"""Calibration utilities for Jump Probability Cup forecasts.

v7 principle — NO SHRINKAGE.
-----------------------------
Shrinkage and hard caps were removed in v7 after a backtest on the project's own
data (7830 NegBin predictions, cluster bootstrap over 261 matches) showed they
degrade accuracy monotonically:

    shrink c=0.45   delta Brier -0.0148   CI95 [-0.0183, -0.0113]   significant
    shrink c=0.60   delta Brier -0.0081   CI95 [-0.0106, -0.0055]   significant
    shrink c=0.75   delta Brier -0.0034   CI95 [-0.0050, -0.0018]   significant
    shrink c=0.92   delta Brier -0.0005   CI95 [-0.0010, +0.0000]   neutral
    cap 0.55        delta Brier -0.0169   CI95 [-0.0212, -0.0125]   significant
    cap 0.68        delta Brier -0.0041   CI95 [-0.0057, -0.0025]   significant
    cap 0.74        delta Brier -0.0017   CI95 [-0.0025, -0.0008]   significant

The reason is simple: the NegBin model is already calibrated (mean bias +1.27pp
across the reliability curve).  Compressing an already-calibrated forecast can
only lose.  The optimal sharpening exponent on the same data was k = 1.05, i.e.
"leave it alone".

See tests/test_calibration_regression.py, which re-derives these numbers and
fails if anyone reintroduces compression.

What is left:
    - weighted_raw_probability: an honest blend of market / model / base priors.
    - evidence_anchor: retained as a DIAGNOSTIC reference point only.  It no
      longer moves the output.
    - apply_market_caps: retained but OFF by default.  Opt in explicitly.

Note on `p_model`: the pipeline now reports the pure model output separately from
the market-blended one.  Any downstream consumer that needs the model's own opinion
— rather than a number already pulled toward the market — should read p_model.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

# Retained for reference and for the regression test.  NOT used in production.
DEPRECATED_CONFIDENCE_TO_SHRINK: Dict[str, float] = {
    "low": 0.45,
    "medium_low": 0.60,
    "medium": 0.75,
    "medium_high": 0.85,
    "high": 0.92,
    "very_high": 1.00,
}

# Opt-in only.  Every one of these measurably hurt Brier on the project backtest.
OPTIONAL_MAX_PROB_BY_MARKET_TYPE: Dict[str, float] = {
    "match_outcome": 0.82,
    "goals": 0.78,
    "team_stat": 0.74,
    "player_prop": 0.68,
    "rare_event": 0.55,
    "period_specific": 0.70,
}

WEIGHTS_BY_MARKET_TYPE: Dict[str, Dict[str, float]] = {
    "match_outcome": {"market": 0.60, "model": 0.20, "base": 0.05},
    "goals": {"market": 0.50, "model": 0.25, "base": 0.10},
    "team_stat": {"market": 0.20, "model": 0.50, "base": 0.10},
    "player_prop": {"market": 0.20, "model": 0.35, "base": 0.20},
    "rare_event": {"market": 0.20, "model": 0.20, "base": 0.45},
    "period_specific": {"market": 0.20, "model": 0.45, "base": 0.15},
}

NOISY_TYPES = {"player_prop", "rare_event", "period_specific"}


def clamp(p: float, lo: float = 0.01, hi: float = 0.99) -> float:
    return max(lo, min(hi, p))


def brier(prob: float, outcome: int) -> float:
    if outcome not in (0, 1):
        raise ValueError("outcome must be 0 or 1")
    return (prob - outcome) ** 2


def relative_points(prob: float, outcome: int, field_avg_brier: float, multiplier: float = 1.0) -> float:
    return (field_avg_brier - brier(prob, outcome)) * 100.0 * multiplier


def weighted_raw_probability(
    market_type: str,
    base_prob: float,
    market_prob: float | None,
    model_prob: float | None,
    context_adj: float = 0.0,
) -> float:
    """Blend the priors that actually exist, then apply context as an honest shift.

    v7 fix — two silent shrinkage channels removed:

    1. The old code had a fourth "context" source equal to `base_prob + context_adj`.
       With context_adj = 0 that term was simply extra weight on base_prob.  For
       player_prop this pushed base_prob's effective weight from 0.20 to 0.45.
    2. The old code substituted base_prob whenever market_prob or model_prob was
       missing, silently stacking even more weight onto the hand-typed base_prob.
       In the France-Iraq example that gave base_prob 55% of the total weight, and
       a model output of 11.6% was reported as 22.

    Now: missing sources are dropped and the remaining weights are renormalised,
    so a missing market prior transfers weight to the *model*, not to base_prob.
    context_adj is added afterwards as an explicit additive shift.
    """
    weights = WEIGHTS_BY_MARKET_TYPE.get(market_type, WEIGHTS_BY_MARKET_TYPE["team_stat"])
    parts: List[Tuple[float, float]] = [(weights["base"], base_prob)]
    if market_prob is not None:
        parts.append((weights["market"], market_prob))
    if model_prob is not None:
        parts.append((weights["model"], model_prob))

    total_w = sum(w for w, _ in parts)
    if total_w <= 0:
        blended = base_prob
    else:
        blended = sum(w * p for w, p in parts) / total_w
    return clamp(blended + context_adj)


def evidence_anchor(market_type: str, base_prob: float, market_prob: float | None) -> float:
    """DIAGNOSTIC ONLY as of v7.  Reported for audit; does not move the output."""
    if market_prob is None:
        return clamp(base_prob)
    if market_type in {"match_outcome", "goals"}:
        return clamp(0.80 * market_prob + 0.20 * base_prob)
    if market_type == "rare_event":
        return clamp(0.80 * base_prob + 0.20 * market_prob)
    if market_type in {"player_prop", "period_specific"}:
        return clamp(0.50 * base_prob + 0.50 * market_prob)
    return clamp(0.60 * market_prob + 0.40 * base_prob)


def apply_market_caps(prob: float, market_type: str) -> float:
    """Opt-in only.  Measurably harmful on the project backtest — see module docstring."""
    cap = OPTIONAL_MAX_PROB_BY_MARKET_TYPE.get(market_type)
    return prob if cap is None else clamp(min(prob, cap))


def final_probability(
    market_type: str,
    base_prob: float,
    market_prob: float | None,
    model_prob: float | None,
    context_adj: float,
    confidence: str = "medium",
    evidence_score: float | None = None,
    apply_caps: bool = False,
) -> Tuple[float, float, float, float]:
    """Return (p_model, p_blend, anchor_diagnostic, p_submit).

    p_model  the pure statistical model output, untouched by priors, caps or gates.
    p_blend  model blended with market/base priors.
    anchor   diagnostic reference point only.
    p_submit what to submit.  Equals p_blend unless apply_caps is explicitly set.

    `confidence` and `evidence_score` are accepted for CSV compatibility and audit
    logging.  As of v7 they no longer alter the probability.
    """
    p_model = clamp(model_prob) if model_prob is not None else None
    p_blend = weighted_raw_probability(market_type, base_prob, market_prob, model_prob, context_adj)
    anchor = evidence_anchor(market_type, base_prob, market_prob)
    p_submit = apply_market_caps(p_blend, market_type) if apply_caps else p_blend
    return (p_model if p_model is not None else p_blend), p_blend, anchor, p_submit


def red_team_flags(
    market_type: str,
    final_prob: float,
    expected_field_prob: float | None = None,
    evidence_score: float | None = None,
    model_prob: float | None = None,
    market_prob: float | None = None,
) -> List[str]:
    """Warnings for the human.  These never modify a probability."""
    flags: List[str] = []
    e = 0.5 if evidence_score is None else evidence_score
    if market_type in NOISY_TYPES and abs(final_prob - 0.5) > 0.15 and e < 0.75:
        flags.append("Noisy market with strong probability: verify lineup/game-state sensitivity.")
    if market_type == "rare_event" and final_prob > 0.38:
        flags.append("Rare event probability is high: check base rate, referee and narrative bias.")
    if (final_prob > 0.72 or final_prob < 0.28) and e < 0.75:
        flags.append("Extreme forecast without high evidence score: verify assumptions.")
    if expected_field_prob is not None and abs(final_prob - expected_field_prob) < 0.02:
        flags.append("Near expected field: little relative edge unless your probability is more accurate.")
    if model_prob is not None and market_prob is not None and abs(model_prob - market_prob) > 0.12:
        flags.append("Model/market disagreement >12pp: investigate before submitting.")
    return flags
