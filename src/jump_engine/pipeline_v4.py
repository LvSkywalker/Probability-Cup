"""End-to-end player-driven Jump Probability Cup v4 pipeline.

Usage:
    python src/pipeline_v4.py \
      --data-dir data \
      --questions data/questions_player_driven.csv \
      --generated-input data/turkey_paraguay_generated_input_v4.csv \
      --output data/turkey_paraguay_final_v4.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

from player_parameter_engine import build_generated_input
from pipeline import run as run_forecast_pipeline


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--questions", required=True, type=Path)
    parser.add_argument("--generated-input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--safe-mode", action="store_true")
    args = parser.parse_args()

    build_generated_input(args.data_dir, args.questions, args.generated_input)
    run_forecast_pipeline(args.generated_input, args.output, winner_mode=not args.safe_mode)
