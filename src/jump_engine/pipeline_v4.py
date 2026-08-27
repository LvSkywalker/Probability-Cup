"""End-to-end player-driven Jump Probability Cup v4 pipeline.

Usage:
    PYTHONPATH=src python3 -m jump_engine.pipeline_v4 \
      --data-dir data \
      --questions data/questions_player_driven.csv \
      --generated-input data/turkey_paraguay_generated_input_v4.csv \
      --output data/turkey_paraguay_final_v4.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .player_parameter_engine import build_generated_input
from .pipeline import run as run_forecast_pipeline


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--questions", required=True, type=Path)
    parser.add_argument("--generated-input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--apply-caps", action="store_true",
                        help="Opt in to legacy hard caps. Off by default (they hurt Brier).")
    args = parser.parse_args()

    build_generated_input(args.data_dir, args.questions, args.generated_input)
    run_forecast_pipeline(args.generated_input, args.output, apply_caps=args.apply_caps)
