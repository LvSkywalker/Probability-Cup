# Changelog — v6 SOT Gate Patch

## Added

- `src/sot_gate.py`
  - `sot_bottom_up_gate()`
  - `sot_threshold_prob()`
  - `sot_threshold_audit()`
  - `sot_relative_2h_audit()`
  - `context_multiplier_guard()`
  - `sot_lambda_coherence_check()`
  - `underdog_sot_variance_guard()`

- `src/sot_backtest_md2.py`
- `data/md2_sot_backtest_cases.csv`
- `reports/md2_sot_gate_backtest.md`
- `reports/md2_sot_gate_backtest.csv`
- `tests/test_sot_gate.py`

## Modified

- `src/player_parameter_engine.py`
  - SOT bottom-up/raw/top-down audit fields added.
  - SOT context multiplier cap added.
  - SOT gate applied to team SOT threshold, relative, and second-half relative models.

## Known limitations

- Backtest is a replay with assumptions, not a real out-of-sample backtest.
- The underdog SOT variance guard is currently a callable warning, not fully integrated into automatic row generation.
- Coherence checks are implemented as general utilities but not yet automatically run across a full match sheet in `pipeline.py`.
- Player SOT props still use Poisson at player level. That may be acceptable for 1+ player SOT but should be reviewed separately.
