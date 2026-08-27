# Model Pipeline Overview

A plain-language description of how the engine turns match data into a probability.
No executable code here — see `src/jump_engine/` for that.

Current as of engine v7.0. An earlier version of this document described shrinkage and
field-bias exploitation as features; both were removed after post-competition testing.
See [Post-Competition Conclusions](../postmortems/post_competition_conclusions.md).

---

## 1. Question classification

Every question is labelled, because the relevant statistics and the appropriate
distribution differ by event type:

- **Match outcome / goals** — "Turkey win", "total goals ≤ 2"
- **Team stats** — "more fouls", "more cards", "2+ offsides"
- **Player props** — "Enciso 1+ shot on target"
- **Rare events** — "penalty or red card"
- **Period props** — "more shots on target in the second half", "second-half corners"

## 2. Base rate and market

Each category has a **base rate**: how often the event happens in general (for example
~30% for a penalty or red card in a match). Where credible **market odds** exist (1X2,
over/under), the vig-free implied probability becomes the reference anchor. Without
odds, the base rate is the anchor.

## 3. Statistical model

- **Match outcome / goals** — Poisson (or Dixon-Coles where possible) on expected
  goals. Lambdas estimated from average xG with attack/defence corrections.
- **Team stats** — **Negative Binomial**, `Var = mu + alpha*mu^2`, alpha ≈ 0.18–0.22.
  Fouls, cards, corners, shots and offsides are all overdispersed relative to Poisson,
  and using Poisson for them produces a systematic upward bias in the tail — roughly
  13 points at mu = 7.5, threshold 6.
- **Player props** — Poisson on `(expected minutes / 90) × (shots per 90) ×
  (on-target rate)`, adjusted for role, set pieces and opponent.
- **Rare events** — base-rate model with referee, style and match-importance
  adjustments.
- **Period props** — Negative Binomial with higher dispersion (alpha ≈ 0.30) to reflect
  game-state variance.

Model selection was tested on a 301-match rolling backtest:

| Model | Brier |
|---|---|
| **NegBin** | **0.2030** |
| BivarNB | 0.2032 |
| COM-Poisson | 0.2038 |
| Poisson | 0.2057 |
| WeibullCount | 0.2065 |

## 4. Contextual adjustments

Applied to **inputs**, before the model runs:

- **Expected lineups** — key starters, shape, expected minutes
- **Referee** — average cards and penalties awarded
- **Match importance** — must-win, knockout, possible game management
- **Weather** — wind and rain can affect corner and shot counts

The ordering matters. Corrections belong on the input side. Once the model has run, the
output is the forecast.

## 5. No output compression

Earlier versions compressed the raw probability toward the anchor as a function of data
quality, and shaded estimates to exploit expected field bias. Both were removed in v7.0.

Testing on the project's own backtests found that every level of compression degraded
Brier monotonically, because the Negative Binomial model was already calibrated — mean
reliability bias +1.27pp. The operating rule is now:

```text
Apply caution to the decision, not to the probability.
```

If a forecast is not one you would submit as-is, skip the question. Do not move the
number and submit that instead.

## 6. Red team and correlated risk

Before finalising, an explicit check on what could invalidate the forecast: late
injuries, an early goal changing the corner and foul script, weather.

Correlation is checked too. Two props on the same match — "more corners" and "more
second-half shots on target" for the same team — depend on the same match script, and
the sheet as a whole must describe one coherent story.

## 7. Producing the final probability

The model output, the base rate and the market anchor are combined in a weighted blend
whose weights depend on question type. Sources that are missing are dropped and the
remaining weights renormalised, so an absent market prior transfers weight to the
model rather than to a hand-entered base rate.

The pipeline reports three numbers, never conflated:

```text
p_model    pure model output, untouched
p_blend    p_model blended with market / base priors
p_submit   what to submit
```

## 8. Auditability

Every generated parameter is written to the output CSV: the lambdas and mus, the
divergence flags, the multipliers, the blend components. Any forecast can be traced
back to the assumptions that produced it, which is what made the post-competition
review possible at all.
