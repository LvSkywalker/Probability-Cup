"""Statistical model layer for the Jump Probability Cup pipeline.

Each function outputs a decimal probability in [0,1].  The goal is not to be a
perfect closed-form soccer model on day one; it is to replace manual `model_prob`
with auditable model-generated probabilities that can be improved over time.
"""
from __future__ import annotations

from distributions import (
    clamp,
    poisson_ge,
    poisson_match_probs,
    poisson_total_le,
    prob_a_greater_b_nb,
    negbin_ge,
)


def match_win_probability(lambda_team: float, lambda_opp: float, market_blend: float | None = None, market_weight: float = 0.0) -> float:
    model, _, _ = poisson_match_probs(lambda_team, lambda_opp)
    if market_blend is None or market_weight <= 0:
        return model
    return clamp((1 - market_weight) * model + market_weight * market_blend)


def total_goals_le_probability(lambda_team: float, lambda_opp: float, threshold: int = 2) -> float:
    return poisson_total_le(lambda_team, lambda_opp, threshold)


def relative_team_stat_probability(mu_team: float, mu_opp: float, alpha_team: float = 0.18, alpha_opp: float = 0.18) -> float:
    """P(team stat > opponent stat), e.g. Paraguay fouls > Turkey fouls."""
    return prob_a_greater_b_nb(mu_team, mu_opp, alpha_team, alpha_opp)


def threshold_team_stat_probability(mu: float, threshold: int, alpha: float = 0.18) -> float:
    """P(team stat >= threshold), e.g. Turkey offsides >= 2."""
    return negbin_ge(threshold, mu, alpha)


def player_sot_probability(
    minutes: float,
    shots_per90: float,
    sot_rate: float,
    team_attack_multiplier: float = 1.0,
    role_multiplier: float = 1.0,
    opponent_multiplier: float = 1.0,
    set_piece_multiplier: float = 1.0,
) -> float:
    """P(player records 1+ shot on target) using a minutes-adjusted Poisson rate."""
    lam = (
        max(minutes, 0.0) / 90.0
        * max(shots_per90, 0.0)
        * clamp(sot_rate, 0.01, 0.99)
        * max(team_attack_multiplier, 0.01)
        * max(role_multiplier, 0.01)
        * max(opponent_multiplier, 0.01)
        * max(set_piece_multiplier, 0.01)
    )
    return clamp(1.0 - pow(2.718281828459045, -lam))


def rare_penalty_or_red_probability(
    penalty_prob: float,
    red_card_prob: float,
    overlap_multiplier: float = 0.30,
    referee_multiplier: float = 1.0,
    discipline_multiplier: float = 1.0,
    match_importance_multiplier: float = 1.0,
) -> float:
    """P(penalty OR red card), anchored to base rates.

    overlap_multiplier is the fraction of independent overlap to subtract. It prevents
    double-counting while acknowledging that penalties and reds are not mutually exclusive.
    """
    pen = clamp(penalty_prob * referee_multiplier * match_importance_multiplier)
    red = clamp(red_card_prob * referee_multiplier * discipline_multiplier * match_importance_multiplier)
    overlap = overlap_multiplier * pen * red
    return clamp(pen + red - overlap)


def second_half_relative_probability(mu_team_2h: float, mu_opp_2h: float, alpha_team: float = 0.22, alpha_opp: float = 0.22) -> float:
    """P(team 2H stat > opponent 2H stat).  Higher alpha reflects game-state volatility."""
    return prob_a_greater_b_nb(mu_team_2h, mu_opp_2h, alpha_team, alpha_opp, max_count=60)
