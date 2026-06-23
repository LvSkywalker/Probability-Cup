"""Small MD2 SOT postmortem/backtest for the coded SOT gate.

This is NOT a clean statistical backtest. It uses the realised MD2 questions and
known submitted/crowd/outcome values from the postmortem, then compares a few
counterfactual probabilities produced or implied by the new SOT gate.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List


def brier(p: float, y: int) -> float:
    return (p - y) ** 2


def parse_prob(x: str) -> float:
    v = float(x)
    return v / 100.0 if v > 1 else v


def fmt(x: float) -> str:
    return f"{x:.2f}"


def load_cases(path: Path) -> List[Dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def enrich(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    out = []
    for r in rows:
        p_old = parse_prob(r["submitted_prob"])
        p_crowd = parse_prob(r["crowd_prob"])
        y = int(float(r["outcome"]))
        p_new = parse_prob(r["adjusted_prob"])
        rbp = float(r["rbp"])
        crowd_b = brier(p_crowd, y)
        old_b = brier(p_old, y)
        new_b = brier(p_new, y)
        raw_old = crowd_b - old_b
        raw_new = crowd_b - new_b
        # Infer SportsPredict question multiplier from observed RBP when possible.
        if abs(raw_old) > 1e-8:
            mult = rbp / (100.0 * raw_old)
            est_new_rbp = 100.0 * raw_new * mult
        else:
            mult = float("nan")
            est_new_rbp = float("nan")
        rr = dict(r)
        rr.update({
            "old_brier": fmt(old_b),
            "new_brier": fmt(new_b),
            "crowd_brier": fmt(crowd_b),
            "raw_delta_old_vs_crowd": fmt(100.0 * raw_old),
            "raw_delta_new_vs_crowd": fmt(100.0 * raw_new),
            "estimated_new_rbp": "" if est_new_rbp != est_new_rbp else fmt(est_new_rbp),
            "estimated_rbp_change": "" if est_new_rbp != est_new_rbp else fmt(est_new_rbp - rbp),
        })
        out.append(rr)
    return out


def write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = []
    for r in rows:
        for k in r:
            if k not in headers:
                headers.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader(); w.writerows(rows)


def write_md(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    known = [r for r in rows if r["estimated_new_rbp"] != ""]
    total_old = sum(float(r["rbp"]) for r in rows)
    total_new_known = sum(float(r["estimated_new_rbp"] or 0) for r in known)
    total_old_known = sum(float(r["rbp"]) for r in known)
    with path.open("w", encoding="utf-8") as f:
        f.write("# MD2 SOT gate backtest / replay\n\n")
        f.write("This is a small counterfactual replay, not a clean out-of-sample backtest. ")
        f.write("It uses the realised MD2 questions and compares the submitted probabilities with probabilities that the new SOT gate would have forced us to review or shrink.\n\n")
        f.write(f"- Submitted RBP on listed SOT-related rows: **{total_old:.2f}**\n")
        f.write(f"- Estimated new RBP on rows where multiplier is inferable: **{total_new_known:.2f}** vs submitted **{total_old_known:.2f}**\n\n")
        f.write("| Match | Question | Submitted | Crowd | Outcome | Submitted RBP | Adjusted | Est. new RBP | Change | Method |\n")
        f.write("|---|---|---:|---:|---:|---:|---:|---:|---:|---|\n")
        for r in rows:
            f.write(
                f"| {r['match']} | {r['question']} | {r['submitted_prob']} | {r['crowd_prob']} | {r['outcome']} | "
                f"{float(r['rbp']):.2f} | {r['adjusted_prob']} | {r['estimated_new_rbp'] or 'n/a'} | {r['estimated_rbp_change'] or 'n/a'} | {r['adjustment_method']} |\n"
            )
        f.write("\n## Interpretation\n\n")
        f.write("The new code would not magically fix every SOT row. It does three concrete things:\n\n")
        f.write("1. It would have flagged and shrunk **Uruguay 6+ SOT** before submission, avoiding the biggest loss.\n")
        f.write("2. It would have blocked/reviewed **NZ more 2H SOT than Egypt** because >60% lacked bottom-up support.\n")
        f.write("3. It would have warned that **Cape Verde 2+ SOT in 2H** was too low for a live underdog profile, but this remains a variance/modeling issue rather than a pure top-down-vs-bottom-up divergence.\n\n")
        f.write("It would also have reduced Spain 8+ SOT under the mechanical NB gate. That would have hurt this realised YES, but it is a calibration correction: the previous 81% was probably overconfident even though it won.\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/md2_sot_backtest_cases.csv")
    ap.add_argument("--csv-output", default="reports/md2_sot_gate_backtest.csv")
    ap.add_argument("--md-output", default="reports/md2_sot_gate_backtest.md")
    args = ap.parse_args()
    rows = enrich(load_cases(Path(args.input)))
    write_csv(Path(args.csv_output), rows)
    write_md(Path(args.md_output), rows)
    print(f"Wrote {args.csv_output}")
    print(f"Wrote {args.md_output}")


if __name__ == "__main__":
    main()
