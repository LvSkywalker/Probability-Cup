"""CSV-driven model engine.

Reads rows with `model_family` and parameter columns, returns model_prob.
This keeps the forecasting workflow transparent: every model probability can be
traced back to the assumptions in the input CSV.
"""
from __future__ import annotations

from typing import Dict, Optional

from .stat_models import (
    match_win_probability,
    total_goals_le_probability,
    relative_team_stat_probability,
    threshold_team_stat_probability,
    player_sot_probability,
    rare_penalty_or_red_probability,
    second_half_relative_probability,
)


def _f(row: Dict[str, str], key: str, default: Optional[float] = None) -> Optional[float]:
    v = (row.get(key, "") or "").strip()
    if v == "":
        return default
    x = float(v)
    if key.endswith("_prob") and x > 1:
        x /= 100.0
    return x


def _i(row: Dict[str, str], key: str, default: int) -> int:
    v = (row.get(key, "") or "").strip()
    return default if v == "" else int(float(v))


def compute_model_probability(row: Dict[str, str]) -> Optional[float]:
    family = (row.get("model_family", "") or "").strip()
    if family == "":
        return None

    if family == "match_poisson_win":
        return match_win_probability(
            lambda_team=_f(row, "lambda_team", 1.2),
            lambda_opp=_f(row, "lambda_opp", 1.0),
            market_blend=_f(row, "market_prob", None),
            market_weight=_f(row, "model_market_weight", 0.0) or 0.0,
        )

    if family == "total_goals_poisson_le":
        return total_goals_le_probability(
            lambda_team=_f(row, "lambda_team", 1.2),
            lambda_opp=_f(row, "lambda_opp", 1.0),
            threshold=_i(row, "threshold", 2),
        )

    if family == "relative_nb":
        return relative_team_stat_probability(
            mu_team=_f(row, "mu_team", 10.0),
            mu_opp=_f(row, "mu_opp", 10.0),
            alpha_team=_f(row, "alpha_team", 0.18),
            alpha_opp=_f(row, "alpha_opp", 0.18),
        )

    if family == "threshold_nb":
        return threshold_team_stat_probability(
            mu=_f(row, "mu_team", 1.5),
            threshold=_i(row, "threshold", 2),
            alpha=_f(row, "alpha_team", 0.18),
        )

    if family == "player_sot_poisson":
        return player_sot_probability(
            minutes=_f(row, "minutes", 75.0),
            shots_per90=_f(row, "shots_per90", 1.5),
            sot_rate=_f(row, "sot_rate", 0.35),
            team_attack_multiplier=_f(row, "team_attack_multiplier", 1.0),
            role_multiplier=_f(row, "role_multiplier", 1.0),
            opponent_multiplier=_f(row, "opponent_multiplier", 1.0),
            set_piece_multiplier=_f(row, "set_piece_multiplier", 1.0),
        )

    if family == "rare_penalty_or_red":
        return rare_penalty_or_red_probability(
            penalty_prob=_f(row, "penalty_prob", 0.22),
            red_card_prob=_f(row, "red_card_prob", 0.16),
            overlap_multiplier=_f(row, "overlap_multiplier", 0.30),
            referee_multiplier=_f(row, "referee_multiplier", 1.0),
            discipline_multiplier=_f(row, "discipline_multiplier", 1.0),
            match_importance_multiplier=_f(row, "match_importance_multiplier", 1.0),
        )

    if family == "second_half_relative_nb":
        return second_half_relative_probability(
            mu_team_2h=_f(row, "mu_team_2h", 2.5),
            mu_opp_2h=_f(row, "mu_opp_2h", 2.0),
            alpha_team=_f(row, "alpha_team", 0.22),
            alpha_opp=_f(row, "alpha_opp", 0.22),
        )

    raise ValueError(f"Unknown model_family: {family}")
