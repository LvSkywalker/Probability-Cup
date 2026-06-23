"""Real-data ingestion helpers for Jump Probability Cup v5.

This module converts exported public football-data tables into the CSV schema
expected by the player-driven parameter engine:

    data/player_attacking_stats.csv
    data/player_defensive_discipline.csv

Primary intended source: FBref exported tables.
It is deliberately file-based: export/download the source CSVs yourself, then run
this script. This avoids brittle live scraping and makes every input auditable.
"""
from __future__ import annotations

import argparse
import csv
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


def norm_name(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def fnum(v: object, default: float = 0.0) -> float:
    if v is None:
        return default
    s = str(v).strip().replace("%", "")
    if s == "" or s.lower() in {"nan", "none"}:
        return default
    try:
        return float(s)
    except ValueError:
        return default


def read_csv_flexible(path: Path) -> List[Dict[str, str]]:
    """Read FBref-like CSV exports, skipping repeated header rows."""
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    clean = []
    for r in rows:
        player = (r.get("Player") or r.get("player") or "").strip()
        if not player or player.lower() in {"player", "rk"}:
            continue
        clean.append(r)
    return clean


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def load_mapping(path: Path) -> Dict[str, Dict[str, str]]:
    rows = read_csv_flexible(path) if path.exists() else []
    if not rows and path.exists():
        with path.open("r", newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    out = {}
    for r in rows:
        internal = (r.get("player") or "").strip()
        source_name = (r.get("fbref_player") or internal).strip()
        if internal:
            out[norm_name(internal)] = {**r, "fbref_player": source_name}
    return out


def build_lookup(files: Iterable[Path]) -> Dict[str, List[Dict[str, str]]]:
    lookup: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for fp in files:
        for r in read_csv_flexible(fp):
            player = (r.get("Player") or r.get("player") or "").strip()
            if player:
                rr = dict(r)
                rr["__source_file"] = fp.name
                lookup[norm_name(player)].append(rr)
    return lookup


def pick_row(candidates: List[Dict[str, str]], preferred_squad: str = "") -> Optional[Dict[str, str]]:
    if not candidates:
        return None
    preferred_squad = norm_name(preferred_squad)
    if preferred_squad:
        exact = [r for r in candidates if norm_name(r.get("Squad") or r.get("squad") or "") == preferred_squad]
        if exact:
            candidates = exact
    # Prefer highest minutes/90s when duplicated across comps.
    return max(candidates, key=lambda r: fnum(r.get("90s") or r.get("90") or r.get("Min"), 0.0))


def per90_from_total(total: float, nineties: float) -> float:
    if nineties <= 0:
        return 0.0
    return total / nineties


def build_attacking_stats(data_dir: Path) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    """Return player_attacking_stats rows + audit rows."""
    raw = data_dir / "raw" / "fbref"
    shooting = build_lookup(raw.glob("*shoot*.csv"))
    standard = build_lookup(raw.glob("*standard*.csv"))
    passing = build_lookup(list(raw.glob("*passing*.csv")) + list(raw.glob("*gca*.csv")))
    misc = build_lookup(raw.glob("*misc*.csv"))
    mapping = load_mapping(data_dir / "player_mapping.csv")

    player_pool_rows = []
    with (data_dir / "player_pool.csv").open("r", newline="", encoding="utf-8") as f:
        player_pool_rows = list(csv.DictReader(f))

    out, audit = [], []
    for p in player_pool_rows:
        internal = p.get("player", "").strip()
        mp = mapping.get(norm_name(internal), {})
        src_name = mp.get("fbref_player", internal).strip()
        preferred_squad = mp.get("club") or p.get("club", "")
        key = norm_name(src_name)
        shoot = pick_row(shooting.get(key, []), preferred_squad)
        std = pick_row(standard.get(key, []), preferred_squad)
        pas = pick_row(passing.get(key, []), preferred_squad)
        mi = pick_row(misc.get(key, []), preferred_squad)
        n90 = fnum((shoot or std or {}).get("90s"), fnum((std or {}).get("90"), 0.0))
        shots90 = fnum((shoot or {}).get("Sh/90"), per90_from_total(fnum((shoot or {}).get("Sh"), 0.0), n90))
        sot90 = fnum((shoot or {}).get("SoT/90"), per90_from_total(fnum((shoot or {}).get("SoT"), 0.0), n90))
        sot_rate = fnum((shoot or {}).get("SoT%"), 0.0) / 100.0 if fnum((shoot or {}).get("SoT%"), 0.0) > 1.0 else fnum((shoot or {}).get("SoT%"), 0.0)
        if sot_rate <= 0 and shots90 > 0:
            sot_rate = sot90 / shots90
        xg90 = fnum((shoot or std or {}).get("xG"), 0.0)
        npxg90 = fnum((shoot or std or {}).get("npxG"), xg90)
        xag90 = fnum((std or pas or {}).get("xAG"), fnum((std or {}).get("xA"), 0.0))
        # If FBref row uses totals, convert by 90s for selected columns when values look too large.
        if n90 > 0 and xg90 > 2.5:
            xg90 = xg90 / n90
        if n90 > 0 and npxg90 > 2.5:
            npxg90 = npxg90 / n90
        if n90 > 0 and xag90 > 2.5:
            xag90 = xag90 / n90
        key_passes90 = fnum((pas or {}).get("KP"), 0.0)
        if n90 > 0 and key_passes90 > 15:
            key_passes90 = key_passes90 / n90
        sca90 = fnum((pas or std or {}).get("SCA90"), fnum((pas or {}).get("SCA"), 0.0))
        if n90 > 0 and sca90 > 20:
            sca90 = sca90 / n90
        prog_carries90 = fnum((std or {}).get("PrgC"), 0.0)
        if n90 > 0 and prog_carries90 > 20:
            prog_carries90 = prog_carries90 / n90
        box_touches90 = fnum((mi or {}).get("Att Pen"), 0.0)
        if n90 > 0 and box_touches90 > 20:
            box_touches90 = box_touches90 / n90
        crosses90 = fnum((mi or pas or {}).get("Crs"), 0.0)
        if n90 > 0 and crosses90 > 20:
            crosses90 = crosses90 / n90
        offsides90 = fnum((mi or {}).get("Off"), 0.0)
        if n90 > 0 and offsides90 > 6:
            offsides90 = offsides90 / n90
        out.append({
            "player": internal,
            "shots90": round(shots90, 3),
            "sot90": round(sot90, 3),
            "sot_rate": round(max(0.0, min(1.0, sot_rate)), 3),
            "xg90": round(xg90, 3),
            "npxg90": round(npxg90, 3),
            "xag90": round(xag90, 3),
            "key_passes90": round(key_passes90, 3),
            "sca90": round(sca90, 3),
            "progressive_carries90": round(prog_carries90, 3),
            "box_touches90": round(box_touches90, 3),
            "crosses90": round(crosses90, 3),
            "offsides90": round(offsides90, 3),
        })
        audit.append({
            "player": internal,
            "fbref_player": src_name,
            "matched_shooting": bool(shoot),
            "matched_standard": bool(std),
            "matched_passing": bool(pas),
            "matched_misc": bool(mi),
            "source_shooting": (shoot or {}).get("__source_file", ""),
            "source_standard": (std or {}).get("__source_file", ""),
            "source_passing": (pas or {}).get("__source_file", ""),
            "source_misc": (mi or {}).get("__source_file", ""),
        })
    return out, audit


def build_discipline_stats(data_dir: Path) -> List[Dict[str, object]]:
    raw = data_dir / "raw" / "fbref"
    misc = build_lookup(raw.glob("*misc*.csv"))
    defense = build_lookup(raw.glob("*defense*.csv"))
    standard = build_lookup(raw.glob("*standard*.csv"))
    mapping = load_mapping(data_dir / "player_mapping.csv")
    with (data_dir / "player_pool.csv").open("r", newline="", encoding="utf-8") as f:
        player_pool_rows = list(csv.DictReader(f))
    out = []
    for p in player_pool_rows:
        internal = p.get("player", "").strip()
        mp = mapping.get(norm_name(internal), {})
        src_name = mp.get("fbref_player", internal).strip()
        preferred_squad = mp.get("club") or p.get("club", "")
        key = norm_name(src_name)
        mi = pick_row(misc.get(key, []), preferred_squad)
        de = pick_row(defense.get(key, []), preferred_squad)
        std = pick_row(standard.get(key, []), preferred_squad)
        n90 = fnum((mi or de or std or {}).get("90s"), 0.0)
        fls = fnum((mi or {}).get("Fls"), 0.0)
        fld = fnum((mi or {}).get("Fld"), 0.0)
        crdy = fnum((std or mi or {}).get("CrdY"), 0.0)
        crdr = fnum((std or mi or {}).get("CrdR"), 0.0)
        tackles = fnum((de or {}).get("Tkl"), 0.0)
        interceptions = fnum((de or {}).get("Int"), 0.0)
        aerial = fnum((mi or {}).get("Won"), 0.0) + fnum((mi or {}).get("Lost"), 0.0)
        out.append({
            "player": internal,
            "fouls_committed90": round(per90_from_total(fls, n90), 3),
            "fouls_drawn90": round(per90_from_total(fld, n90), 3),
            "cards90": round(per90_from_total(crdy + 2.0 * crdr, n90), 3),
            "tackles90": round(per90_from_total(tackles, n90), 3),
            "interceptions90": round(per90_from_total(interceptions, n90), 3),
            "aerial_duels90": round(per90_from_total(aerial, n90), 3),
        })
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data", help="Pipeline data directory")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    data_dir = Path(args.data_dir)
    attacking, audit = build_attacking_stats(data_dir)
    discipline = build_discipline_stats(data_dir)
    if not args.dry_run:
        write_csv(data_dir / "player_attacking_stats.csv", attacking, [
            "player","shots90","sot90","sot_rate","xg90","npxg90","xag90","key_passes90","sca90","progressive_carries90","box_touches90","crosses90","offsides90"
        ])
        write_csv(data_dir / "player_defensive_discipline.csv", discipline, [
            "player","fouls_committed90","fouls_drawn90","cards90","tackles90","interceptions90","aerial_duels90"
        ])
        write_csv(data_dir / "derived" / "player_source_audit.csv", audit, [
            "player","fbref_player","matched_shooting","matched_standard","matched_passing","matched_misc","source_shooting","source_standard","source_passing","source_misc"
        ])
    print(f"Built attacking rows: {len(attacking)}")
    print(f"Built discipline rows: {len(discipline)}")
    missing = [r for r in audit if not (r['matched_shooting'] or r['matched_standard'] or r['matched_misc'])]
    print(f"Players with no FBref match at all: {len(missing)}")
    if missing[:10]:
        print("First missing:", ", ".join(r['player'] for r in missing[:10]))


if __name__ == "__main__":
    main()
