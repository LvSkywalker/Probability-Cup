# Jump Probability Cup Forecasting Engine

A structured football-prop forecasting framework built for binary prediction-market questions in the Jump / SportsPredict Probability Cup.

The project combines:

- market-first forecasting for liquid football markets;
- event-rate models for corners, fouls, cards, offsides, and rare events;
- player-level role/minutes modelling;
- bottom-up shots-on-target modelling;
- cross-question coherence checks;
- mandatory pre-submission audit;
- post-match RBP/Brier postmortem analysis;
- shared CSV / dual-engine validation protocol.

## Current Canonical Versions

| Component | Version |
|---|---|
| Master | v4.1 |
| Pipeline | v1.4 |
| Engine/code layer | v6.2 |

Pipeline v1.4 is a procedural update. It does not change model parameters.

Core rule:

```text
Cross-check inputs and code, not output probabilities.
```

Submit rule:

```text
submit = final_pipeline
```

## Repository Structure

```text
docs/
  master/          Project memory and operating handbook
  pipeline/        Forecasting pipeline versions
  model_specs/     Engine/model specifications
  postmortems/     Backtests and lessons learned
  reports/         Match reports and notes

src/jump_engine/   Core engine code

tests/             Unit tests

data/
  examples/        Example match inputs
  backtests/       Historical backtest data
  shared_csv_inputs/

outputs/
  examples/        Example engine outputs
```

## Workflow

1. Build or verify a shared CSV/input set.
2. Run the engine on the shared CSV.
3. Run second-engine / Claude check only on the same CSV.
4. If outputs diverge, reconcile data/schema/formula/code.
5. Rerun after correction.
6. Submit `final_pipeline`.
7. Apply the mandatory audit checklist.

Do not average output probabilities.

## Hard Rules

```text
Platform crowd is never a pre-match input.
raw_model is diagnostic only.
final_pipeline is the default submit vector.
No output averaging.
No prudence haircut without hard evidence.
No aggressive probability without source-backed justification.
```

## Status

Active research/prototype project.
