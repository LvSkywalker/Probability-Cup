# Research Log — Count Models for SOT Pipeline

**Project:** Jump Probability Cup / SportsPredict  
**Purpose:** Improve the SOT/count-event module beyond simple Poisson and current Negative Binomial.  
**Status:** Research backlog, not production.  
**Current production baseline:** Top-down SOT model + bottom-up gate + Negative Binomial threshold probabilities + lambda coherence checks.

---

## 1. Why this research log exists

The MD2 postmortem showed that the general pipeline is strong, but the SOT module had a systematic leak:

- non-SOT props performed strongly;
- SOT props produced most of the negative RBP;
- the largest losses came from overconfident SOT volume estimates;
- manual Poisson-style calculations were not consistent with the engine.

The current fix is:

1. Use Negative Binomial instead of manual Poisson for SOT thresholds.
2. Validate top-down SOT estimates with bottom-up player SOT estimates.
3. Trigger the SOT gate only when top-down and bottom-up diverge materially.
4. Run lambda coherence checks when several SOT questions are present in the same sheet.

This research log tracks candidate models that may improve the SOT/count module further.

---

## 2. Models to compare

We want to compare:

1. Poisson
2. Negative Binomial
3. Conway-Maxwell-Poisson / COM-Poisson
4. Weibull Count Model
5. Bivariate Negative Binomial
6. Current hybrid pipeline: top-down + bottom-up gate + Negative Binomial

---

## 3. Evaluation target

The target is not simply predicting total SOT. We care about the probability of contest questions such as:

- team 1+ SOT in 2H;
- team 2+ SOT in 2H;
- team 6+ SOT total;
- match 8+ total SOT;
- team A more SOT than team B in 2H;
- both teams 1+ SOT in 2H;
- player 1+ SOT.

The model should be judged on probability calibration, not just point forecasts.

Preferred metrics:

```text
Brier score
Log loss
Calibration curve
RBP vs crowd when available
Hit rate only as secondary
Tail calibration for high thresholds
```

---

## 4. Baseline 1 — Poisson

### Idea

The Poisson model assumes:

```text
X ~ Poisson(lambda)
```

where X is the SOT count.

### Strengths

- Simple.
- Interpretable.
- Easy to fit.
- Good first approximation for low-count events.

### Weaknesses

- Mean equals variance.
- Usually too rigid for football counts.
- Poor at handling overdispersion.
- Can become overconfident in tails.
- Assumes constant event intensity unless modified.

### Use in pipeline

Poisson should remain a diagnostic baseline only. It should not be used manually for final SOT threshold probabilities.

### Research question

Does Poisson ever beat Negative Binomial on low thresholds such as 1+ or 2+ SOT?

---

## 5. Baseline 2 — Negative Binomial

### Idea

The Negative Binomial allows variance greater than the mean:

```text
X ~ NegBin(mu, alpha)
```

where alpha controls overdispersion.

### Strengths

- Handles overdispersion.
- Better tail behavior than Poisson.
- Already compatible with current SOT engine.
- Good default for team/match SOT thresholds.

### Weaknesses

- Still mostly a static count model.
- Does not directly model timing of events.
- Does not model correlation between the two teams unless extended.
- 2H split needs additional assumptions.

### Current role

Production model for SOT threshold probabilities, after top-down/bottom-up validation.

### Research question

Can we improve its alpha calibration by competition, team strength, match state, or threshold type?

---

## 6. Candidate 1 — COM-Poisson

### Idea

The Conway-Maxwell-Poisson distribution generalizes Poisson and can handle both:

```text
overdispersion
underdispersion
```

It has two parameters:

```text
lambda = rate-like parameter
nu = dispersion parameter
```

When:

```text
nu = 1  -> Poisson
nu < 1  -> overdispersed
nu > 1  -> underdispersed
```

### Why it may help

Some football count variables may be overdispersed, while others may be underdispersed depending on tactical constraints.

For example:

- total SOT may be overdispersed;
- certain player SOT props may be zero-inflated or structurally constrained;
- elite-favorite SOT may be less variable than underdog SOT.

### Strengths

- More flexible than Poisson.
- Can model underdispersion, which Negative Binomial cannot.
- Useful diagnostic against assuming all counts are overdispersed.

### Weaknesses

- Harder to fit.
- Normalizing constant can be computationally expensive.
- Less interpretable.
- May overfit on small samples.
- Requires reliable implementation.

### Where to test

```text
team total SOT
match total SOT
player SOT
corners maybe later
```

### Success criterion

COM-Poisson is useful only if it improves calibration materially over Negative Binomial without becoming unstable.

---

## 7. Candidate 2 — Weibull Count Model

### Idea

Instead of modeling the final count directly, model waiting times between SOT events.

If inter-arrival times follow a Weibull distribution, then the number of events in 90 minutes becomes a Weibull count process.

### Why it may help

SOT arrivals are not necessarily constant over time.

Football has temporal effects:

```text
favorite scores early and manages
underdog chases in 2H
late game opens up
substitutions increase/decrease attacking rate
fatigue changes defensive quality
```

Weibull can model non-constant hazard:

```text
shape k > 1  -> event hazard increases over time
shape k < 1  -> event hazard decreases over time
shape k = 1  -> exponential waiting times, Poisson-like
```

### Strengths

- Natural for timing and 2H questions.
- Better suited for second-half SOT props.
- Can model increasing/decreasing event intensity.
- Useful for underdog chasing scripts.

### Weaknesses

- Needs event timestamps.
- Harder to estimate from match-level aggregates.
- Can overfit badly on small samples.
- May need team-level or state-level pooling.

### Where to test

Most relevant:

```text
team 1+ SOT in 2H
team 2+ SOT in 2H
relative 2H SOT
both teams 1+ SOT in 2H
2H more goals / shots style props
```

Less relevant:

```text
simple full-match total SOT thresholds
```

### Proposed role

Not a replacement for Negative Binomial at first.

Better role:

```text
Negative Binomial for full-match SOT volume
Weibull/temporal model for splitting volume across 1H/2H and game-state adjustment
```

### Research question

Does a Weibull temporal model improve 2H SOT calibration versus a simple 50/50 split or 55/45 chasing adjustment?

---

## 8. Candidate 3 — Bivariate Negative Binomial

### Idea

Model both teams' SOT counts jointly:

```text
(X_home, X_away)
```

rather than independently.

### Why it may help

Several contest props depend on both teams:

```text
both teams 1+ SOT in 2H
team A more SOT than team B
match total SOT
relative 2H SOT
```

The two teams' SOT counts are not independent. They depend on the same match script.

Example:

- open game -> both teams can produce more SOT;
- one-sided control -> favorite SOT high, underdog SOT low;
- red card -> one team increases, other decreases;
- early goal -> trailing team may increase SOT.

### Strengths

- Captures correlation.
- Better coherence between related SOT props.
- Helps avoid inconsistent sheets.
- Useful for relative SOT and both-team SOT questions.

### Weaknesses

- More complex.
- Needs enough joint observations.
- Correlation may be match-script dependent, not constant.
- Requires careful parameterization.

### Possible constructions

#### Shared Gamma frailty model

```text
lambda_A = team-specific component + shared match-tempo factor
lambda_B = team-specific component + shared match-tempo factor
```

This induces positive correlation through shared tempo.

#### Copula approach

Fit marginal Negative Binomial distributions and connect them with a copula.

#### Hierarchical match-state model

Model latent tempo and dominance:

```text
tempo_factor
dominance_factor
game_state_factor
```

Then generate both SOT counts conditionally.

### Where to test

Most relevant:

```text
A more SOT than B
both teams 1+ SOT
match total SOT
relative 2H SOT
```

### Research question

Does bivariate NB improve coherence and Brier score on joint/relative SOT props compared with independent NB marginals?

---

## 9. Current hybrid production model

### Structure

The current production approach should remain:

```text
1. Top-down mu estimate
2. Bottom-up player mu estimate
3. Divergence gate
4. Negative Binomial probability
5. Lambda coherence check
6. Audit trail
```

### Important property

The gate is conditional.

It does not always shrink.

```text
If top-down and bottom-up agree:
    use main model
If they diverge:
    REVIEW / shrink / investigate
```

### Why keep it

The hybrid model directly addresses the MD2 failure mode:

- Uruguay 6+ SOT overconfidence;
- New Zealand 2H relative SOT narrative overreach;
- manual Poisson errors;
- inconsistent lambda assumptions across a sheet.

---

## 10. Backtest design

### Data needed

Minimum:

```text
match ID
date
competition
team A
team B
final SOT A
final SOT B
first-half SOT A
first-half SOT B
second-half SOT A
second-half SOT B
lineups
player SOT rates
event timestamps if testing Weibull
odds / market if available
contest questions and outcomes if available
```

### Historical data sources

Possible:

```text
StatsBomb open data
FBref / Stathead style aggregates
FotMob match stats
Sofascore match stats
FootyStats / StatFootball
club season data for players
manual contest logs from SportsPredict
```

### Rolling backtest

Use only past data to predict future matches.

```text
for each match in chronological order:
    train/estimate using matches before current date
    generate probabilities for SOT props
    score Brier/log loss
```

### Prop generation

Generate synthetic contest props:

```text
team 2+ SOT
team 3+ SOT
team 4+ SOT
team 5+ SOT
team 6+ SOT
match 7+ SOT
match 8+ SOT
match 9+ SOT
team A more SOT than team B
both teams 1+ SOT
```

For 2H if timestamps or half splits exist:

```text
team 1+ SOT 2H
team 2+ SOT 2H
relative 2H SOT
both teams 1+ SOT 2H
```

---

## 11. Model comparison table to fill

| Model | Full-match team SOT | Match total SOT | 2H SOT | Relative SOT | Player SOT | Pros | Cons | Status |
|---|---:|---:|---:|---:|---:|---|---|---|
| Poisson | TBD | TBD | TBD | TBD | TBD | simple | rigid | baseline |
| Negative Binomial | TBD | TBD | TBD | TBD | TBD | overdispersion | static | production |
| COM-Poisson | TBD | TBD | TBD | TBD | TBD | handles over/underdispersion | harder fit | research |
| Weibull Count | TBD | TBD | TBD | TBD | weak | temporal hazard | needs timestamps | research |
| Bivariate NB | TBD | TBD | TBD | strong | weak | joint coherence | complex | research |
| Hybrid Gate + NB | TBD | TBD | TBD | TBD | TBD | practical + auditable | needs data quality | production candidate |

---

## 12. Acceptance criteria

A candidate model should enter production only if it satisfies:

```text
1. Improves Brier/log loss on rolling backtest.
2. Improves or preserves calibration.
3. Does not introduce unstable extreme probabilities.
4. Has interpretable audit output.
5. Handles missing data gracefully.
6. Beats current hybrid model on the prop family it targets.
```

Important:

```text
A model does not need to beat every other model on every prop.
```

Possible final allocation:

```text
Negative Binomial:
    full-match SOT thresholds

Weibull temporal model:
    2H SOT split / timing

Bivariate NB:
    relative SOT / both-team SOT

Hybrid gate:
    safety layer across all SOT props
```

---

## 13. Immediate next experiments

### Experiment A — COM-Poisson vs Negative Binomial

Goal:

```text
Compare calibration on full-match team and match SOT thresholds.
```

Key question:

```text
Does COM-Poisson improve because some SOT counts are underdispersed?
```

### Experiment B — Weibull Count for 2H SOT

Goal:

```text
Use SOT timestamps to estimate whether SOT hazard changes over time.
```

Key question:

```text
Does Weibull improve relative 2H SOT and team 2H SOT props?
```

### Experiment C — Bivariate NB for joint SOT

Goal:

```text
Model team A and team B SOT jointly.
```

Key question:

```text
Does it improve both-teams-1+ and relative-SOT props?
```

### Experiment D — Hybrid gate ablation

Compare:

```text
NB only
NB + bottom-up gate
NB + coherence check
NB + gate + coherence
NB + gate + coherence + underdog 2H adjustment
```

---

## 14. Practical implementation notes

Start simple.

Do not put all experimental models into production at once.

Recommended order:

```text
1. Lock current NB + SOT gate.
2. Run historical backtests.
3. Implement bivariate NB for joint SOT props.
4. Implement Weibull Count only if timestamp data is reliable.
5. Test COM-Poisson as diagnostic competitor.
```

---

## 15. Current recommendation

Current production remains:

```text
Negative Binomial + top-down/bottom-up conditional gate + coherence checks.
```

Research backlog:

```text
1. Bivariate Negative Binomial for joint and relative SOT.
2. Weibull Count for temporal / 2H SOT.
3. COM-Poisson for dispersion diagnostics.
4. Poisson only as benchmark baseline.
```

Do not replace the current pipeline until a candidate wins on rolling backtest.
