"""Player-driven parameter engine for Jump Probability Cup v4.

This layer converts probable lineups + club/player stats + match context into
model parameters consumed by the v3 statistical model engine.

Design principle:
    player-level production -> team aggregate rates -> distribution parameters.

The generated rows remain transparent CSV rows.  You can audit every forecast by
looking at the generated mu/lambda inputs.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from .sot_gate import context_multiplier_guard, sot_bottom_up_gate


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _float(v: object, default: float = 0.0) -> float:
    if v is None:
        return default
    s = str(v).strip()
    if s == "":
        return default
    return float(s)


def _read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _index_by(rows: List[Dict[str, str]], key: str) -> Dict[str, Dict[str, str]]:
    return {(r.get(key, "") or "").strip(): r for r in rows if (r.get(key, "") or "").strip()}


def _index_match_team(rows: List[Dict[str, str]]) -> Dict[Tuple[str, str], Dict[str, str]]:
    out = {}
    for r in rows:
        m = (r.get("match", "") or "").strip()
        t = (r.get("team", "") or "").strip()
        if m and t:
            out[(m, t)] = r
    return out


def expected_minutes(row: Dict[str, str]) -> float:
    starter_prob = clamp(_float(row.get("starter_prob"), 0.75), 0.0, 1.0)
    minutes_if_start = _float(row.get("minutes_if_start"), 75.0)
    minutes_if_bench = _float(row.get("minutes_if_bench"), 18.0)
    explicit = row.get("expected_minutes", "")
    if str(explicit).strip() != "":
        return clamp(_float(explicit), 0.0, 120.0)
    return clamp(starter_prob * minutes_if_start + (1.0 - starter_prob) * minutes_if_bench, 0.0, 120.0)


def player_role_multiplier(role: str, stat: str) -> float:
    role = (role or "").lower()
    # Conservative default role mapping. Users can override via role_multiplier in player_pool.
    attack_roles = {
        "striker": 1.15,
        "forward": 1.10,
        "winger": 1.08,
        "creator_forward": 1.05,
        "attacking_mid": 1.03,
        "midfielder": 0.95,
        "defensive_mid": 0.78,
        "fullback": 0.72,
        "centerback": 0.45,
        "goalkeeper": 0.05,
    }
    foul_roles = {
        "striker": 0.80,
        "forward": 0.82,
        "winger": 0.85,
        "creator_forward": 0.80,
        "attacking_mid": 0.88,
        "midfielder": 1.00,
        "defensive_mid": 1.18,
        "fullback": 1.12,
        "centerback": 1.05,
        "goalkeeper": 0.10,
    }
    card_roles = {
        "striker": 0.75,
        "forward": 0.78,
        "winger": 0.82,
        "creator_forward": 0.78,
        "attacking_mid": 0.85,
        "midfielder": 1.00,
        "defensive_mid": 1.22,
        "fullback": 1.15,
        "centerback": 1.18,
        "goalkeeper": 0.20,
    }
    if stat in {"shots", "sot", "xg", "xag", "corners", "offsides"}:
        return attack_roles.get(role, 1.0)
    if stat == "fouls":
        return foul_roles.get(role, 1.0)
    if stat == "cards":
        return card_roles.get(role, 1.0)
    return 1.0


class PlayerParameterEngine:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.player_pool = _read_csv(data_dir / "player_pool.csv")
        self.attack = _index_by(_read_csv(data_dir / "player_attacking_stats.csv"), "player")
        self.discipline = _index_by(_read_csv(data_dir / "player_defensive_discipline.csv"), "player")
        self.team_context = _index_match_team(_read_csv(data_dir / "lineup_context.csv"))
        self.match_context = {r.get("match", "").strip(): r for r in _read_csv(data_dir / "match_context.csv")}
        self.referee_context = {r.get("match", "").strip(): r for r in _read_csv(data_dir / "referee_context.csv")}

    def team_players(self, match: str, team: str) -> List[Dict[str, str]]:
        out = []
        for r in self.player_pool:
            if r.get("match", "").strip() == match and r.get("team", "").strip() == team:
                out.append(r)
        return out

    def possession_factor(self, expected_possession: float, stat: str) -> float:
        # Lower possession -> more defending/fouls/cards; higher possession -> more corners/SOT.
        poss = clamp(expected_possession, 25.0, 75.0)
        if stat in {"shots", "sot", "corners", "offsides", "xg"}:
            return clamp(0.75 + 0.50 * (poss / 50.0), 0.75, 1.30)
        if stat in {"fouls", "cards"}:
            return clamp(1.25 - 0.50 * (poss / 50.0), 0.70, 1.25)
        return 1.0

    def aggregate_team(self, match: str, team: str, opponent: Optional[str] = None) -> Dict[str, float]:
        players = self.team_players(match, team)
        ctx = self.team_context.get((match, team), {})
        mctx = self.match_context.get(match, {})
        rctx = self.referee_context.get(match, {})
        possession = _float(ctx.get("expected_possession"), 50.0)
        attack_mult = _float(ctx.get("team_attack_multiplier"), 1.0)
        defense_mult = _float(ctx.get("opponent_defense_multiplier"), 1.0)
        style_corner_mult = _float(ctx.get("corner_style_multiplier"), 1.0)
        high_line_mult = _float(ctx.get("opponent_high_line_multiplier"), 1.0)
        dribble_against_mult = _float(ctx.get("opponent_dribbling_multiplier"), 1.0)
        importance_mult = _float(mctx.get("match_importance_multiplier"), 1.0)
        referee_foul_mult = _float(rctx.get("fouls_multiplier"), 1.0)
        referee_card_mult = _float(rctx.get("cards_multiplier"), 1.0)

        shots = sot = xg = xag = corners = offsides = 0.0
        fouls = cards = fouls_drawn = 0.0
        attack_rating = defense_rating = discipline_rating = 0.0
        minutes_total = 0.0

        for p in players:
            name = p.get("player", "").strip()
            mins = expected_minutes(p) / 90.0
            role = p.get("role", "")
            role_override = _float(p.get("role_multiplier"), 0.0)
            atk = self.attack.get(name, {})
            dis = self.discipline.get(name, {})
            # Role override only for attacking contribution; otherwise use stat-specific role map.
            attack_role_mult = role_override if role_override > 0 else player_role_multiplier(role, "sot")
            shots += mins * _float(atk.get("shots90"), 0.0) * attack_role_mult
            sot += mins * _float(atk.get("sot90"), 0.0) * attack_role_mult
            xg += mins * _float(atk.get("xg90"), 0.0) * attack_role_mult
            xag += mins * _float(atk.get("xag90"), 0.0) * attack_role_mult
            corners += mins * (_float(atk.get("crosses90"), 0.0) * 0.18 + _float(atk.get("key_passes90"), 0.0) * 0.12) * attack_role_mult
            offsides += mins * _float(atk.get("offsides90"), 0.15) * player_role_multiplier(role, "offsides")
            fouls += mins * _float(dis.get("fouls_committed90"), 0.0) * player_role_multiplier(role, "fouls")
            fouls_drawn += mins * _float(dis.get("fouls_drawn90"), 0.0)
            cards += mins * _float(dis.get("cards90"), 0.0) * player_role_multiplier(role, "cards")
            attack_rating += mins * (1.2 * _float(atk.get("xg90"), 0.0) + 0.8 * _float(atk.get("xag90"), 0.0) + 0.15 * _float(atk.get("sca90"), 0.0))
            defense_rating += mins * (_float(dis.get("tackles90"), 0.0) + _float(dis.get("interceptions90"), 0.0) + 0.5 * _float(dis.get("aerial_duels90"), 0.0))
            discipline_rating += mins * (_float(dis.get("fouls_committed90"), 0.0) + 4 * _float(dis.get("cards90"), 0.0))
            minutes_total += mins * 90.0

        # Blend raw player aggregation with context and basic team minimums.
        # IMPORTANT v6 change: preserve bottom-up SOT and expose top-down/context values
        # so the SOT gate can audit and shrink aggressive volume estimates.
        poss_attack = self.possession_factor(possession, "sot")
        poss_def = self.possession_factor(possession, "fouls")

        shots_bottomup_raw = shots
        sot_bottomup_raw = sot
        xg_bottomup_raw = xg
        xag_bottomup_raw = xag

        # WC BASELINE FLOOR (Claude fix + chat audit request): player club stats
        # underestimate WC-level SOT for smaller nations. Floor = 2.5 by default.
        # Expose BOTH raw player-sum AND after-floor for full audit trail.
        sot_bottomup_player_raw = sot_bottomup_raw  # before floor — audit field
        wc_sot_floor = _float(ctx.get("wc_sot_floor"), 2.5)
        if sot_bottomup_raw < wc_sot_floor:
            sot_bottomup_raw = max(sot_bottomup_raw, wc_sot_floor)
        sot_bottomup_after_floor = sot_bottomup_raw  # after floor — audit field

        sot_context_multiplier = attack_mult * defense_mult * poss_attack
        sot_cap = _float(ctx.get("sot_context_multiplier_cap"), 1.65)
        allow_over_cap = str(ctx.get("allow_sot_context_over_cap", "")).strip().lower() in {"1", "true", "yes", "y"}
        sot_guard = context_multiplier_guard(
            sot_bottomup_raw,
            sot_context_multiplier,
            max_multiplier=sot_cap,
            hard_data_override=allow_over_cap,
        )
        sot_uncapped = sot_bottomup_raw * sot_context_multiplier
        sot = sot_guard.capped_mu

        # Shots use the same cap as SOT to keep the shot/SOT structure coherent.
        shots_uncapped = shots_bottomup_raw * sot_context_multiplier
        shots = shots_bottomup_raw * sot_guard.capped_multiplier
        xg = xg_bottomup_raw * sot_guard.capped_multiplier
        xag = xag_bottomup_raw * sot_guard.capped_multiplier

        # Corners are not just player crosses; add attack/territory floor.
        corners = (2.2 + corners) * attack_mult * style_corner_mult * poss_attack
        # Offsides depend heavily on runs in behind + opponent line.
        offsides = (0.25 + offsides) * attack_mult * high_line_mult * poss_attack
        fouls = (4.5 + fouls) * poss_def * dribble_against_mult * referee_foul_mult * importance_mult
        cards = (0.7 + cards) * poss_def * dribble_against_mult * referee_card_mult * importance_mult

        # Goals lambda is anchored later by market if provided; this is player xG proxy.
        xg_proxy = clamp(0.60 * xg + 0.25 * xag + 0.15 * (sot * 0.28), 0.25, 4.50)
        return {
            "shots_mu": clamp(shots, 2.0, 28.0),
            "shots_mu_uncapped": clamp(shots_uncapped, 0.0, 40.0),
            "shots_mu_bottomup_raw": clamp(shots_bottomup_raw, 0.0, 40.0),
            "sot_mu": clamp(sot, 0.5, 12.0),
            "sot_mu_uncapped": clamp(sot_uncapped, 0.0, 20.0),
            "sot_mu_bottomup_raw": clamp(sot_bottomup_raw, 0.0, 20.0),
            "sot_mu_bottomup_player_raw": clamp(sot_bottomup_player_raw, 0.0, 20.0),
            "sot_mu_bottomup_after_floor": clamp(sot_bottomup_after_floor, 0.0, 20.0),
            "sot_wc_floor": wc_sot_floor,
            "sot_wc_floor_applied": int(sot_bottomup_after_floor > sot_bottomup_player_raw),
            "sot_context_multiplier": sot_context_multiplier,
            "sot_context_capped_multiplier": sot_guard.capped_multiplier,
            "sot_context_flag": sot_guard.flag,
            "sot_context_note": sot_guard.note,
            "xg_proxy": xg_proxy,
            "corners_mu": clamp(corners, 1.0, 14.0),
            "offsides_mu": clamp(offsides, 0.05, 6.0),
            "fouls_mu": clamp(fouls, 4.0, 28.0),
            "cards_mu": clamp(cards, 0.2, 7.0),
            "attack_rating": attack_rating,
            "defense_rating": defense_rating,
            "discipline_rating": discipline_rating,
            "minutes_total": minutes_total,
            "expected_possession": possession,
        }

    def gated_sot_mu_from_agg(self, agg: Dict[str, float], q: Optional[Dict[str, str]] = None, prefix: str = "") -> Tuple[float, Dict[str, str]]:
        """Return a SOT mu after the coded SOT gate plus audit columns.

        Uses the uncapped context top-down mu vs raw player bottom-up mu. If context
        multiplier was capped, final mu is also bounded by the capped context mu so
        the gate cannot re-create double-counted team strength.
        """
        q = q or {}
        hard_override = str(q.get(f"{prefix}sot_hard_data_override", q.get("sot_hard_data_override", ""))).strip().lower() in {"1", "true", "yes", "y"}
        mu_topdown = _float(q.get(f"{prefix}sot_mu_topdown", q.get("sot_mu_topdown", "")), _float(agg.get("sot_mu_uncapped"), _float(agg.get("sot_mu"), 1.0)))
        mu_bottomup = _float(q.get(f"{prefix}sot_mu_bottomup", q.get("sot_mu_bottomup", "")), _float(agg.get("sot_mu_bottomup_raw"), _float(agg.get("sot_mu"), 1.0)))
        evidence_score = _float(
            q.get(f"{prefix}sot_evidence_score", q.get("sot_evidence_score", "")),
            None,
        ) if q else None
        gate = sot_bottom_up_gate(
            mu_topdown,
            mu_bottomup,
            hard_data_override=hard_override,
            evidence_score=evidence_score,
        )
        # v7: no silent downward clip.  The old code did
        #     final_mu = min(gate.gated_mu, capped_context_mu) when the context flag was REVIEW,
        # a third one-directional cut stacked on top of the gate shrink and the context cap.
        # The gate is now flag-only, so mu passes through and the flags travel with it in the
        # audit dict for a human to act on.
        final_mu = gate.gated_mu
        audit = {
            f"{prefix}sot_mu_topdown": f"{mu_topdown:.4f}",
            f"{prefix}sot_mu_bottomup": f"{mu_bottomup:.4f}",
            f"{prefix}sot_gate_mu": f"{final_mu:.4f}",
            f"{prefix}sot_gate_divergence": f"{gate.divergence:.4f}",
            f"{prefix}sot_gate_flag": gate.flag,
            f"{prefix}sot_gate_note": gate.note,
            f"{prefix}sot_context_multiplier": f"{_float(agg.get('sot_context_multiplier'), 1.0):.4f}",
            f"{prefix}sot_context_capped_multiplier": f"{_float(agg.get('sot_context_capped_multiplier'), 1.0):.4f}",
            f"{prefix}sot_context_flag": str(agg.get("sot_context_flag", "OK")),
            f"{prefix}sot_context_note": str(agg.get("sot_context_note", "")),
        }
        return clamp(final_mu, 0.05, 12.0), audit

    def market_team_lambda(self, match: str, team: str, fallback: float) -> float:
        ctx = self.match_context.get(match, {})
        key = f"{team}_team_total_xg_market"
        return _float(ctx.get(key), fallback)

    def lambda_goal(self, match: str, team: str, opponent: str) -> float:
        agg = self.aggregate_team(match, team, opponent)
        opp_agg = self.aggregate_team(match, opponent, team)
        fallback = agg["xg_proxy"]
        market_lam = self.market_team_lambda(match, team, fallback)
        # Player attack edge vs opponent defense, intentionally modest.
        player_lam = agg["xg_proxy"] * math.exp(0.04 * (agg["attack_rating"] - opp_agg["defense_rating"] / 15.0))
        # Market anchored: market is still efficient for goals.
        return clamp(0.62 * market_lam + 0.38 * player_lam, 0.2, 4.5)

    def player_sot_inputs(self, match: str, team: str, opponent: str, player: str, q: Optional[Dict[str, str]] = None) -> Dict[str, object]:
        """Build player SOT inputs.

        IMPORTANT SOT v6.1 fix:
        Player SOT props must use the gated team SOT mu when available.
        Otherwise a swollen top-down team SOT estimate can leak into every
        player via team_attack_multiplier and bypass the SOT bottom-up gate.

        aggregate_team still exposes the context-capped top-down and raw
        bottom-up values separately; the downstream gate combines them here.
        """
        q = q or {}
        pool = {r.get("player", "").strip(): r for r in self.team_players(match, team)}
        p = pool.get(player, {})
        atk = self.attack.get(player, {})
        team_agg = self.aggregate_team(match, team, opponent)
        opp_agg = self.aggregate_team(match, opponent, team)

        gated_team_sot_mu, gate_audit = self.gated_sot_mu_from_agg(team_agg, q, prefix="player_team_")
        attack_multiplier = clamp(gated_team_sot_mu / 4.2, 0.75, 1.35)
        opponent_multiplier = clamp(1.05 - 0.015 * (opp_agg["defense_rating"] - 14.0), 0.80, 1.20)
        return {
            "minutes": expected_minutes(p) if p else 60.0,
            "shots_per90": _float(atk.get("shots90"), 1.5),
            "sot_rate": clamp(_float(atk.get("sot90"), 0.45) / max(_float(atk.get("shots90"), 1.5), 0.1), 0.05, 0.80),
            "team_attack_multiplier": attack_multiplier,
            "team_sot_mu_for_player": gated_team_sot_mu,
            "team_sot_gate_divergence_for_player": _float(gate_audit.get("player_team_sot_gate_divergence"), 0.0),
            "team_sot_gate_flag_for_player": gate_audit.get("player_team_sot_gate_flag", ""),
            "role_multiplier": _float(p.get("role_multiplier"), 0.0) or player_role_multiplier(p.get("role", ""), "sot"),
            "opponent_multiplier": opponent_multiplier,
            "set_piece_multiplier": _float(p.get("set_piece_multiplier"), 1.0),
        }

    def build_model_row(self, q: Dict[str, str]) -> Dict[str, str]:
        row = dict(q)
        match = q.get("match", "").strip()
        team = q.get("team", "").strip()
        opponent = q.get("opponent", "").strip()
        player = q.get("player", "").strip()
        family = q.get("model_family", "").strip()

        if family in {"match_poisson_win", "total_goals_poisson_le"}:
            row["lambda_team"] = f"{self.lambda_goal(match, team, opponent):.4f}"
            row["lambda_opp"] = f"{self.lambda_goal(match, opponent, team):.4f}"

        elif family == "relative_nb":
            stat = q.get("stat", "").strip() or "fouls"
            a = self.aggregate_team(match, team, opponent)
            b = self.aggregate_team(match, opponent, team)
            key = {
                "fouls": "fouls_mu",
                "cards": "cards_mu",
                "corners": "corners_mu",
                "sot": "sot_mu",
                "shots": "shots_mu",
                "offsides": "offsides_mu",
            }.get(stat, "fouls_mu")
            if stat == "sot":
                mu_a, audit_a = self.gated_sot_mu_from_agg(a, q, prefix="team_")
                mu_b, audit_b = self.gated_sot_mu_from_agg(b, q, prefix="opp_")
                row["mu_team"] = f"{mu_a:.4f}"
                row["mu_opp"] = f"{mu_b:.4f}"
                row.update(audit_a)
                row.update(audit_b)
            else:
                row["mu_team"] = f"{a[key]:.4f}"
                row["mu_opp"] = f"{b[key]:.4f}"
            row["alpha_team"] = q.get("alpha_team", "") or ("0.28" if stat in {"cards"} else "0.20")
            row["alpha_opp"] = q.get("alpha_opp", "") or ("0.28" if stat in {"cards"} else "0.20")

        elif family == "threshold_nb":
            stat = q.get("stat", "").strip() or "offsides"
            a = self.aggregate_team(match, team, opponent)
            key = {
                "offsides": "offsides_mu",
                "corners": "corners_mu",
                "sot": "sot_mu",
                "shots": "shots_mu",
                "fouls": "fouls_mu",
                "cards": "cards_mu",
            }.get(stat, "offsides_mu")
            if stat == "sot":
                mu_a, audit_a = self.gated_sot_mu_from_agg(a, q, prefix="team_")
                row["mu_team"] = f"{mu_a:.4f}"
                row.update(audit_a)
            else:
                row["mu_team"] = f"{a[key]:.4f}"
            row["alpha_team"] = q.get("alpha_team", "") or "0.22"

        elif family == "player_sot_poisson":
            vals = self.player_sot_inputs(match, team, opponent, player, q)
            for k, v in vals.items():
                if isinstance(v, (int, float)):
                    row[k] = f"{v:.4f}"
                else:
                    row[k] = str(v)

        elif family == "rare_penalty_or_red":
            mctx = self.match_context.get(match, {})
            rctx = self.referee_context.get(match, {})
            team_agg = self.aggregate_team(match, team, opponent) if team and opponent else {"discipline_rating": 1.0}
            opp_agg = self.aggregate_team(match, opponent, team) if team and opponent else {"discipline_rating": 1.0}
            row["penalty_prob"] = q.get("penalty_prob", "") or f"{_float(rctx.get('penalty_prob_base'), _float(mctx.get('penalty_prob_base'), 0.22)):.4f}"
            row["red_card_prob"] = q.get("red_card_prob", "") or f"{_float(rctx.get('red_card_prob_base'), _float(mctx.get('red_card_prob_base'), 0.15)):.4f}"
            row["referee_multiplier"] = q.get("referee_multiplier", "") or f"{_float(rctx.get('rare_event_multiplier'), 1.0):.4f}"
            # Use both teams' discipline profile, but cap effect.
            disc = clamp((team_agg.get("discipline_rating", 1.0) + opp_agg.get("discipline_rating", 1.0)) / 22.0, 0.85, 1.20)
            row["discipline_multiplier"] = q.get("discipline_multiplier", "") or f"{disc:.4f}"
            row["match_importance_multiplier"] = q.get("match_importance_multiplier", "") or f"{_float(mctx.get('match_importance_multiplier'), 1.0):.4f}"
            row["overlap_multiplier"] = q.get("overlap_multiplier", "") or "0.30"

        elif family == "second_half_relative_nb":
            stat = q.get("stat", "").strip() or "sot"
            a = self.aggregate_team(match, team, opponent)
            b = self.aggregate_team(match, opponent, team)
            key = {
                "corners": "corners_mu",
                "sot": "sot_mu",
                "shots": "shots_mu",
                "fouls": "fouls_mu",
                "cards": "cards_mu",
            }.get(stat, "sot_mu")
            # Second-half base share plus game-state scenario blend.
            # If team is expected to be favorite / press, assign a slight 2H bump.
            fav_bump = _float(q.get("second_half_team_bump"), 1.04)
            opp_bump = _float(q.get("second_half_opp_bump"), 0.98)
            # Underdog chasing 2H share (Claude fix #3): a chasing underdog produces
            # more than 50% of their total volume in 2H (pushes forward when losing).
            _chasing_share = _float(q.get("underdog_chasing_2h_share"), 0.56)
            team_2h_share = _float(q.get("team_2h_share"), 0.50)
            opp_2h_share = _float(q.get("opp_2h_share"), 0.50)
            if str(q.get("team_is_chasing_underdog", "")).strip() in {"1", "true", "True"}:
                team_2h_share = _chasing_share
            if str(q.get("opp_is_chasing_underdog", "")).strip() in {"1", "true", "True"}:
                opp_2h_share = _chasing_share
            if stat == "sot":
                mu_a, audit_a = self.gated_sot_mu_from_agg(a, q, prefix="team_")
                mu_b, audit_b = self.gated_sot_mu_from_agg(b, q, prefix="opp_")
                row["mu_team_2h"] = f"{team_2h_share * mu_a * fav_bump:.4f}"
                row["mu_opp_2h"] = f"{opp_2h_share * mu_b * opp_bump:.4f}"
                row["team_2h_share_used"] = f"{team_2h_share:.2f}"
                row["opp_2h_share_used"] = f"{opp_2h_share:.2f}"
                row.update(audit_a)
                row.update(audit_b)
            else:
                row["mu_team_2h"] = f"{team_2h_share * a[key] * fav_bump:.4f}"
                row["mu_opp_2h"] = f"{opp_2h_share * b[key] * opp_bump:.4f}"
            row["alpha_team"] = q.get("alpha_team", "") or "0.30"
            row["alpha_opp"] = q.get("alpha_opp", "") or "0.30"

        return row


def build_generated_input(data_dir: Path, questions_path: Path, output_path: Path) -> None:
    engine = PlayerParameterEngine(data_dir)
    questions = _read_csv(questions_path)
    rows = [engine.build_model_row(q) for q in questions]
    # Union of headers while preserving question columns first.
    headers: List[str] = []
    for r in rows:
        for k in r.keys():
            if k not in headers:
                headers.append(k)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--questions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    build_generated_input(args.data_dir, args.questions, args.output)
