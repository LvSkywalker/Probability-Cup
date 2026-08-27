# Changelog

## Engine v7.0 / Master v5.0 / Pipeline v1.5 — 2026-08-27 — FINAL

Post-competition review. Evidence:
[`docs/postmortems/post_competition_conclusions.md`](docs/postmortems/post_competition_conclusions.md).
Enforced by `tests/test_calibration_regression.py`.

Unlike v1.4, this release **does** change model behaviour.

### Removed

- **Shrinkage**, entirely. Every level tested degraded Brier monotonically on the
  project's own backtest (c=0.75: −0.0034, CI95 [−0.0050, −0.0018], significant;
  c=0.45: −0.0148). The NegBin model was already calibrated: mean reliability bias
  +1.27pp. Testing the opposite direction gave an optimal sharpening exponent of
  k=1.05 — indistinguishable from "leave it alone".
- **Hard probability caps** from the default path. Retained as opt-in `--apply-caps`.
  The `rare_event` cap at 0.55 alone touched 3302/7830 rows and cost −0.0169 Brier,
  the single most damaging component of the calibration layer.
- The phantom `context` weight in `weighted_raw_probability`, which silently equalled
  `base_prob` whenever `context_adj` was 0 — pushing base_prob's effective weight from
  a declared 0.20 to an actual 0.45 on player props.
- The `base_prob` substitution for missing market/model priors. Combined with the
  above, a row with no market price gave a hand-typed number 55% of total weight.
- A third one-directional clip in `player_parameter_engine.aggregate_team`.

### Changed

- **SOT gate is now a flag, not a corrector.** `modify_mu=False` by default. It reports
  divergence and OK/REVIEW/BLOCK; it does not move mu. No evidence it ever helped:
  where it fired, Δ Brier −0.0107, CI95 [−0.0265, +0.0050]. Bottom-up sat below
  top-down in 74% of cases, making a documented "coherence check" a systematic downward
  push. Legacy behaviour available via `modify_mu=True`.
- `context_multiplier_guard` warns instead of clipping (`enforce_cap=False`).
- Pipeline output split into `p_model` / `p_blend` / `p_submit`.
- `confidence` and `evidence_score` no longer alter any probability. Retained for audit.
- Imports converted to proper relative package imports. Runs as
  `PYTHONPATH=src python3 -m jump_engine.pipeline`.

### Added

- `docs/postmortems/post_competition_conclusions.md` — full evidence and the
  generalisable lessons.
- `docs/master/jump_probability_cup_master_v5.md` — final master. v4.1 kept as a record
  of the in-season state.
- `docs/pipeline/jump_cup_forecasting_pipeline_v1_5.md` — no-compression pipeline.
- `tests/test_calibration_regression.py` — re-derives every finding from the raw
  backtests and fails if compression is reintroduced. Includes a test that blocks
  over-correcting in the opposite direction.
- `run_tests.sh`, `requirements.txt` (standard library only).

### Deliberately not acted on

Relative props looked like they wanted *sharpening* (k=1.40 for `relative_2h`, 1.60 for
`relative_total`; gains +0.0014/+0.0022). Both CIs crossed zero on n=522 — the same
small-sample pattern that produced the original Uruguay error. Not acted on, and now
locked out by `test_sharpening_does_not_help_either`.

### Not changed

- Distributions, NegBin parameterisation, alpha values.
- Player parameter engine aggregation logic.
- Source hierarchy, coherence checks, small-sample guard, audit discipline.

### Known limitation

The backtests contain no market prices and are proxy backtests on synthetic props built
from a tournament-only event archive. These results show the calibration layer was
destroying accuracy the model already had. They do not establish that the model is good
in absolute terms.

## Master v4.1 / Pipeline v1.4 — 2026-06-23

### Added

- Shared CSV discipline before engine runs.
- Dual-engine output-divergence protocol.
- Input/data/code reconciliation rule.
- Mandatory final_pipeline divergence check.
- MD3 postmortem lesson: do not average output probabilities.

### Changed

- Second-engine disagreement now triggers input/code review, not probability compromise.

### Not changed

- No model parameters changed.

## Pipeline v1.3 — 2026-06-22

### Added

- Bottom-up SOT gate.
- SOT lambda coherence.
- Single-match shrinkage guard.
- Cross-question coherence check.
- Small-sample guard.
- Symmetric hard-data gate.
