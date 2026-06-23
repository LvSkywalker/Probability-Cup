"""Expected CSV schema for the forecasting pipeline."""
REQUIRED_COLUMNS = [
    "question_id",
    "match",
    "raw_question",
    "market_type",
    "base_prob",
    "market_prob",
    "model_prob",
    "context_adj",
    "confidence",
    "expected_field_prob",
]

MARKET_TYPES = [
    "match_outcome",
    "goals",
    "team_stat",
    "player_prop",
    "rare_event",
    "period_specific",
]

CONFIDENCE_LEVELS = [
    "low",
    "medium_low",
    "medium",
    "medium_high",
    "high",
    "very_high",
]
