# Changelog

## Master v4.1 / Pipeline v1.4 — 2026-06-23

### Added

- Shared CSV discipline before engine runs.
- Dual-engine output-divergence protocol.
- Input/data/code reconciliation rule.
- Claude handoff as CSV/input verifier.
- Mandatory final_pipeline divergence check.
- MD3 postmortem lesson: do not average output probabilities.

### Changed

- Hardened `submit = final_pipeline`.
- Claude/second-engine disagreement now triggers input/code review, not probability compromise.

### Not changed

- No model parameters changed.
- No SOT floors changed.
- No minor-league multipliers changed.
- No player multipliers changed.
- No distributional assumptions changed.

## Pipeline v1.3 — 2026-06-22

### Added

- Bottom-up SOT gate.
- SOT lambda coherence.
- Single-match shrinkage guard.
- Cross-question coherence check.
- Small-sample guard.
- Symmetric hard-data gate.
