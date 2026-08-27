# Jump Probability Cup Forecasting Engine

A structured football-prop forecasting framework built for binary prediction-market
questions in the Jump / SportsPredict Probability Cup.

The competition is over. This repository is its closing state, including a
post-competition review that overturned two versions' worth of the project's own
design decisions — see **[Post-Competition Conclusions](docs/postmortems/post_competition_conclusions.md)**.

The project combines:

- market-first forecasting for liquid football markets;
- event-rate models for corners, fouls, cards, offsides, and rare events;
- player-level role/minutes modelling;
- bottom-up shots-on-target validation;
- cross-question coherence checks;
- mandatory pre-submission audit;
- post-match RBP/Brier postmortem analysis;
- shared CSV / dual-engine validation protocol.

## Competition result

Jump Trading Probability Cup on SportsPredict, 2026 — 293 settled forecasts.

| | |
|---|---|
| Italy | **#2** on the platform's country leaderboard |
| Politecnico di Milano | **#1** on the university leaderboard |
| Austria vs Jordan | **#1 of 686** on the match leaderboard — 9 of 10 forecasts beat the crowd |
| England vs Croatia | **#6 of 743** on the match leaderboard — 10 of 10 beat the crowd |
| Crowd benchmark | **+2.0** RBP per forecast |

## Headline finding

The calibration layer added during the season to make forecasts *safer* was making
them *worse*. Every compression level tested degraded Brier monotonically, because the
underlying Negative Binomial model was already calibrated (mean reliability bias
+1.27pp) and had nothing to gain from being compressed.

| Transform | Δ Brier | CI95 |
|---|---|---|
| shrink c=0.45 | −0.0148 | [−0.0183, −0.0113] |
| shrink c=0.75 | −0.0034 | [−0.0050, −0.0018] |
| cap 0.55 (`rare_event`) | −0.0169 | [−0.0212, −0.0125] |
| cap 0.68 (`player_prop`) | −0.0041 | [−0.0057, −0.0025] |

Cluster bootstrap over 261 matches, 7830 predictions. Reproduce with `./run_tests.sh`.

The generalisable lesson:

```text
Apply caution to the decision, not to the probability.
Check whether your model is calibrated before building machinery to fix it.
```

## Current Canonical Versions

| Component | Version |
|---|---|
| Master | v5.0 (final) |
| Pipeline | v1.5 |
| Engine | v7.0 |

v1.5 removes all output compression. Unlike v1.4, it **does** change model behaviour.

## Output contract

```text
p_model    pure model output. Untouched by priors, caps or gates.
p_blend    p_model blended with market / base priors.
p_submit   what to submit. Equals p_blend unless caps are explicitly enabled.
```

## Repository Structure

```text
docs/
  master/          Project memory and operating handbook (v5.0 current, v4.1 archived)
  pipeline/        Forecasting pipeline versions (v1.5 current)
  model_specs/     Engine/model specifications
  competition/     Final competition results
  postmortems/     Backtests, conclusions and lessons learned
  reports/         Match reports and notes

src/jump_engine/   Core engine code
tests/             Unit and regression tests

data/
  examples/        Runnable example inputs
  backtests/       Historical backtest data
  shared_csv_inputs/

outputs/
  examples/        Example engine outputs
```

## Quickstart

Standard library only — nothing to install.

```bash
# reproduce every number in the post-competition review
./run_tests.sh

# forecast a real sheet: the France-Iraq questions from the competition
PYTHONPATH=src python3 -m jump_engine.pipeline \
    --input data/examples/france_iraq_input.csv \
    --output outputs/france_iraq.csv
```

Output, with the engine's own opinion alongside the submitted number:

```text
Q1:  16  (p_model 11.6%)  At halftime, will Iraq have more corner kicks than France?
Q2:  25  (p_model 21.4%)  Will France commit more fouls than Iraq?
Q6:  88  (p_model 88.3%)  Will France win the match?
Q9:  80  (p_model 81.1%)  Will France score in the first half?
```

Under v6.2, Q6 and Q9 came out as 78 and 74 — sitting exactly on the old hard caps for
`match_outcome` and `period_specific`. They were not forecasts; they were the cap value.

## Workflow

1. Build or verify a shared CSV/input set.
2. Run the engine on the shared CSV.
3. Run the second-engine check on the same CSV.
4. If outputs diverge, reconcile data/schema/formula/code.
5. Rerun after correction.
6. Apply the mandatory audit checklist.

Do not average output probabilities.

## Hard Rules

```text
Platform crowd is never a pre-match input.
No shrinkage. No hard caps. The model output is the forecast.
The SOT gate flags divergent inputs; it never moves mu.
Corrections apply to inputs, before the model runs.
If you would not submit a number as-is, skip the question - do not move it.
No output averaging.
No aggressive probability without source-backed justification.
```

## License

MIT — see [LICENSE](LICENSE).

## Status

Competition closed. Archived as a case study.
