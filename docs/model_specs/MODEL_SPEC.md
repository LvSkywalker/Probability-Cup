# Model specification

## Why this model layer exists

The contest scores relative Brier, so we need calibrated probabilities that can still be aggressive when the evidence supports it.  V3 separates two steps:

1. **Statistical probability**: estimate the event probability from an explicit model.
2. **Calibration / winner mode**: shrink only when evidence is weak or the market is noisy.

## Model families

### Match outcome / goals

Independent Poisson goals:

- Team goals ~ Poisson(lambda_team)
- Opponent goals ~ Poisson(lambda_opp)

Then compute:

- P(team wins)
- P(total goals <= threshold)

This can later be upgraded to Dixon-Coles with correlation correction.

### Relative team stats

Negative Binomial:

- X_team ~ NB(mu_team, alpha_team)
- X_opp ~ NB(mu_opp, alpha_opp)

with variance:

Var[X] = mu + alpha * mu^2

Then compute P(X_team > X_opp).

This is used for fouls, cards, corners, SOT and similar team-stat markets.

### Threshold team stats

Negative Binomial threshold probability:

P(X >= k)

Used for offside/corner/card thresholds.

### Player props

Minutes-adjusted Poisson:

lambda_player = minutes/90 * shots_per90 * SOT_rate * multipliers

Then:

P(1+ SOT) = 1 - exp(-lambda_player)

### Rare events

Penalty-or-red is modeled as a union:

P(PEN or RED) = P(PEN) + P(RED) - overlap

Then apply referee, discipline and match-importance multipliers.  It remains base-rate anchored.

## Winner-mode calibration

The calibration layer combines base, market, model and context.  Then it computes an evidence anchor and shrink coefficient.

High `evidence_score` permits less shrinkage and wider caps.  Low evidence compresses back to market/base rates.  Rare events remain constrained because the field tends to overestimate dramatic events.
