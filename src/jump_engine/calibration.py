"""Calibration utilities for Jump Probability Cup forecasts.

V3 winner-mode principle:
- A proper scoring rule says the best forecast is our true probability estimate.
- Therefore, we do NOT become aggressive just to be different from the field.
- We reduce shrinkage when evidence is strong, and keep strong shrinkage when the
  model is noisy, data-poor, or narrative-driven.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

CONFIDENCE_TO_SHRINK: Dict[str, float] = {
    "low": 0.45,
    "medium_low": 0.60,
    "medium": 0.75,
    "medium_high": 0.85,
    "high": 0.92,
    "very_high": 1.00,
}

# Normal-mode soft caps: protect against overconfidence when evidence is not strong.
MAX_PROB_BY_MARKET_TYPE: Dict[str, float] = {
    "match_outcome": 0.82,
    "goals": 0.78,
    "team_stat": 0.74,
    "player_prop": 0.68,
    "rare_event": 0.55,
    "period_specific": 0.70,
}

# Winner-mode caps: used only when evidence_score is high.  Rare events remain capped
# because their base rates are low and narratives often inflate them.
WINNER_MAX_PROB_BY_MARKET_TYPE: Dict[str, float] = {
    "match_outcome": 0.78,
    "goals": 0.75,
    "team_stat": 0.82,
    "player_prop": 0.75,
    "rare_event": 0.55,
    "period_specific": 0.74,
}

WEIGHTS_BY_MARKET_TYPE: Dict[str, Dict[str, float]] = {
    "match_outcome": {"market": 0.60, "model": 0.20, "base": 0.05, "context": 0.15},
    "goals": {"market": 0.50, "model": 0.25, "base": 0.10, "context": 0.15},
    "team_stat": {"market": 0.20, "model": 0.50, "base": 0.10, "context": 0.20},
    "player_prop": {"market": 0.20, "model": 0.35, "base": 0.20, "context": 0.25},
    "rare_event": {"market": 0.20, "model": 0.20, "base": 0.45, "context": 0.15},
    "period_specific": {"market": 0.20, "model": 0.45, "base": 0.15, "context": 0.20},
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
    weights = WEIGHTS_BY_MARKET_TYPE.get(market_type, WEIGHTS_BY_MARKET_TYPE["team_stat"])
    mkt = base_prob if market_prob is None else market_prob
    mdl = base_prob if model_prob is None else model_prob
    ctx = clamp(base_prob + context_adj)
    raw = (
        weights["market"] * mkt
        + weights["model"] * mdl
        + weights["base"] * base_prob
        + weights["context"] * ctx
    )
    return clamp(raw)


def evidence_anchor(market_type: str, base_prob: float, market_prob: float | None) -> float:
    if market_prob is None:
        return clamp(base_prob)
    if market_type in {"match_outcome", "goals"}:
        return clamp(0.80 * market_prob + 0.20 * base_prob)
    if market_type == "rare_event":
        return clamp(0.80 * base_prob + 0.20 * market_prob)
    if market_type in {"player_prop", "period_specific"}:
        return clamp(0.50 * base_prob + 0.50 * market_prob)
    return clamp(0.60 * market_prob + 0.40 * base_prob)


def adaptive_shrink_coeff(confidence: str, evidence_score: float | None) -> float:
    base = CONFIDENCE_TO_SHRINK.get(confidence, CONFIDENCE_TO_SHRINK["medium"])
    if evidence_score is None:
        return base
    e = clamp(evidence_score, 0.0, 1.0)
    # Evidence upgrades shrinkage only when it is genuinely strong.  Below 0.5,
    # we do not let it inflate confidence.
    evidence_coeff = 0.50 + 0.50 * e
    return clamp(max(base, evidence_coeff), 0.35, 1.0)


def apply_shrinkage(raw_prob: float, confidence: str, anchor_prob: float, evidence_score: float | None = None) -> float:
    c = adaptive_shrink_coeff(confidence, evidence_score)
    return clamp(anchor_prob + c * (raw_prob - anchor_prob))


def apply_market_caps(prob: float, market_type: str, evidence_score: float | None = None, winner_mode: bool = True) -> float:
    e = 0.0 if evidence_score is None else clamp(evidence_score, 0.0, 1.0)
    caps = WINNER_MAX_PROB_BY_MARKET_TYPE if (winner_mode and e >= 0.72) else MAX_PROB_BY_MARKET_TYPE
    cap = caps.get(market_type)
    if cap is None:
        return prob
    return clamp(min(prob, cap))


def final_probability(
    market_type: str,
    base_prob: float,
    market_prob: float | None,
    model_prob: float | None,
    context_adj: float,
    confidence: str,
    evidence_score: float | None = None,
    winner_mode: bool = True,
) -> Tuple[float, float, float, float, float]:
    raw = weighted_raw_probability(market_type, base_prob, market_prob, model_prob, context_adj)
    anchor = evidence_anchor(market_type, base_prob, market_prob)
    coeff = adaptive_shrink_coeff(confidence, evidence_score)
    shrunk = apply_shrinkage(raw, confidence, anchor, evidence_score)
    final = apply_market_caps(shrunk, market_type, evidence_score, winner_mode)
    return raw, anchor, coeff, shrunk, final


def red_team_flags(
    market_type: str,
    final_prob: float,
    expected_field_prob: float | None = None,
    evidence_score: float | None = None,
    model_prob: float | None = None,
    market_prob: float | None = None,
) -> List[str]:
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
