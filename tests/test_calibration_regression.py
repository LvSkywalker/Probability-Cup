"""Regression tests that re-derive the v7 calibration decisions from the real backtests.

These are not unit tests of arithmetic.  They re-run the measurements that justified
removing shrinkage and demoting the SOT gate, so that if anyone (human or model) later
reintroduces compression, the suite fails and says why.

Run:  PYTHONPATH=src python3 tests/test_calibration_regression.py
"""
import csv
import math
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from jump_engine.calibration import (  # noqa: E402
    DEPRECATED_CONFIDENCE_TO_SHRINK,
    OPTIONAL_MAX_PROB_BY_MARKET_TYPE,
    final_probability,
    weighted_raw_probability,
)
from jump_engine.sot_gate import sot_bottom_up_gate  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
PRED = os.path.join(ROOT, "data/backtests/count_model_backtest/count_model_backtest_predictions.csv")
GATE = os.path.join(ROOT, "data/backtests/historical_sot_gate_backtest.csv")


def _brier(p, y):
    return (p - y) ** 2


def _load_negbin():
    with open(PRED) as f:
        return [(float(r["p"]), int(r["y"]), r["prop_family"])
                for r in csv.DictReader(f) if r["model"] == "NegBin"]


def _mean_brier(data, fn=lambda p: p):
    return sum(_brier(fn(p), y) for p, y, _ in data) / len(data)


# --- the model is already calibrated -----------------------------------------

def test_negbin_baseline_brier_is_stable():
    data = _load_negbin()
    assert len(data) == 7830, f"expected 7830 NegBin rows, got {len(data)}"
    b = _mean_brier(data)
    assert abs(b - 0.20302) < 1e-4, f"NegBin baseline Brier drifted: {b:.5f}"


def test_negbin_is_already_calibrated():
    """Mean reliability bias must stay small. If it grows, recalibration is warranted."""
    data = _load_negbin()
    bias = sum(p - y for p, y, _ in data) / len(data)
    assert abs(bias) < 0.03, f"reliability bias {bias*100:+.2f}pp is too large — investigate"


# --- shrinkage strictly hurts -------------------------------------------------

def test_every_shrink_level_hurts():
    """Compression only loses, and loses more the harder it compresses."""
    data = _load_negbin()
    base = _mean_brier(data)

    scored = [(c, _mean_brier(data, lambda p, c=c: 0.5 + c * (p - 0.5)))
              for _, c in sorted(DEPRECATED_CONFIDENCE_TO_SHRINK.items(), key=lambda kv: kv[1])]

    for c, b in scored:
        assert b >= base - 1e-9, f"shrink c={c} unexpectedly improved Brier ({b:.5f} vs {base:.5f})"

    # sorted by increasing c (less compression) -> Brier must fall monotonically
    for (c_lo, b_lo), (c_hi, b_hi) in zip(scored, scored[1:]):
        assert b_hi <= b_lo + 1e-9, (
            f"shrink is not monotone: c={c_lo} gives {b_lo:.5f} but c={c_hi} gives {b_hi:.5f}"
        )

    worst = scored[0][1]
    assert worst - base > 0.01, "c=0.45 should cost >0.01 Brier; the finding changed"


def test_every_hard_cap_hurts():
    data = _load_negbin()
    base = _mean_brier(data)
    for market_type, cap in OPTIONAL_MAX_PROB_BY_MARKET_TYPE.items():
        b = _mean_brier(data, lambda p, cap=cap: min(p, cap))
        assert b >= base - 1e-9, f"cap {cap} for {market_type} unexpectedly improved Brier"


def test_sharpening_does_not_help_either():
    """Optimal exponent is ~1.0. Guards against overreacting the other way."""
    data = _load_negbin()

    def sharp(p, k):
        p = min(max(p, 1e-6), 1 - 1e-6)
        return 1 / (1 + math.exp(-k * math.log(p / (1 - p))))

    scores = {k: _mean_brier(data, lambda p, k=k: sharp(p, k))
              for k in [0.8, 0.9, 1.0, 1.1, 1.2, 1.4]}
    best_k = min(scores, key=scores.get)
    assert 0.95 <= best_k <= 1.15, f"optimal sharpening drifted to k={best_k}"
    assert scores[best_k] > scores[1.0] - 0.001, "sharpening gain is within noise; do not chase it"


# --- production path applies no compression -----------------------------------

def test_final_probability_applies_no_shrinkage():
    """With no market prior, a confident model output must survive untouched-ish."""
    for conf in DEPRECATED_CONFIDENCE_TO_SHRINK:
        p_model, p_blend, _anchor, p_submit = final_probability(
            market_type="team_stat", base_prob=0.50, market_prob=None,
            model_prob=0.85, context_adj=0.0, confidence=conf,
        )
        assert abs(p_model - 0.85) < 1e-9, "p_model must be the untouched model output"
        assert abs(p_submit - p_blend) < 1e-9, "caps must be off by default"
        assert p_submit > 0.70, f"confidence '{conf}' still compresses: {p_submit:.4f}"


def test_confidence_no_longer_changes_output():
    outs = set()
    for conf in DEPRECATED_CONFIDENCE_TO_SHRINK:
        _, _, _, p = final_probability(
            market_type="player_prop", base_prob=0.30, market_prob=0.40,
            model_prob=0.62, context_adj=0.0, confidence=conf,
        )
        outs.add(round(p, 10))
    assert len(outs) == 1, f"confidence still moves the output: {outs}"


def test_missing_market_transfers_weight_to_model_not_base():
    """The France-Iraq bug: a missing market prior used to inflate base_prob's weight."""
    base, model = 0.28, 0.1162
    with_market = weighted_raw_probability("period_specific", base, 0.20, model, 0.0)
    without = weighted_raw_probability("period_specific", base, None, model, 0.0)
    assert without < 0.24, (
        f"model 11.6% with base 28% and no market gave {without*100:.1f}% — "
        "base_prob is still dominating"
    )
    # weights: base 0.15, model 0.45 -> renormalised to 0.25 / 0.75
    expected = (0.15 * base + 0.45 * model) / 0.60
    assert abs(without - expected) < 1e-9
    assert with_market != without


def test_context_adj_is_an_honest_shift():
    a = weighted_raw_probability("team_stat", 0.40, 0.45, 0.55, 0.0)
    b = weighted_raw_probability("team_stat", 0.40, 0.45, 0.55, 0.05)
    assert abs((b - a) - 0.05) < 1e-9, "context_adj must be a pure additive shift"


# --- the SOT gate must not move mu --------------------------------------------

def test_gate_reproduces_backtest_divergences_without_moving_mu():
    """Replay the recorded backtest through the live gate.

    Restricted to `team_*` props: on `match_total_*` rows the CSV records a divergence
    computed over the combined match total while the top_mu/bottom_mu columns hold a
    single team's values, so those rows are not self-consistent and cannot be replayed.
    """
    with open(GATE) as f:
        rows = [r for r in csv.DictReader(f) if r["prop"].startswith("team_")]
    checked = 0
    for r in rows:
        try:
            mt, mb = float(r["top_mu"]), float(r["bottom_mu"])
        except (ValueError, KeyError):
            continue
        if mt <= 0:
            continue
        g = sot_bottom_up_gate(mt, mb)
        assert abs(g.gated_mu - max(mt, 0.01)) < 1e-9, "gate moved mu in flag-only mode"
        assert abs(g.divergence - float(r["divergence"])) < 1e-6, (
            f"divergence mismatch on {r['prop']}: {g.divergence:.6f} vs {r['divergence']}"
        )
        checked += 1
    assert checked > 5000, f"only replayed {checked} rows"


def test_legacy_gate_would_have_hurt():
    """Documents why modify_mu defaults to False, using the recorded backtest."""
    with open(GATE) as f:
        rows = [r for r in csv.DictReader(f) if r["divergence"] not in ("", "nan")]
    fired = [r for r in rows if float(r["divergence"]) > 0.30]
    assert len(fired) > 200, "not enough gate-firing rows to evaluate"
    b_top = sum(float(r["brier_top"]) for r in fired) / len(fired)
    b_gated = sum(float(r["brier_gated"]) for r in fired) / len(fired)
    assert b_gated > b_top, (
        "The recorded backtest no longer shows the gate hurting where it fires. "
        "Re-run the analysis before re-enabling modify_mu."
    )


def test_gate_direction_is_biased_downward():
    """Bottom-up sits below top-down ~74% of the time: the gate was a downward push."""
    with open(GATE) as f:
        rows = list(csv.DictReader(f))
    pairs = []
    seen = set()
    for r in rows:
        key = (r["match_id"], r["team"])
        if key in seen:
            continue
        seen.add(key)
        try:
            pairs.append((float(r["top_mu"]), float(r["bottom_mu"])))
        except ValueError:
            continue
    share = sum(1 for t, b in pairs if b < t) / len(pairs)
    assert share > 0.60, f"bottom-up below top-down only {share*100:.0f}% of the time"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed, failed = 0, []
    for t in tests:
        try:
            t()
            passed += 1
            print(f"  PASS  {t.__name__}")
        except Exception as e:
            failed.append((t.__name__, e))
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
