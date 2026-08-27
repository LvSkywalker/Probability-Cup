# Jump / SportsPredict Probability Cup — Forecasting Pipeline v1.5

**Status:** canonical, final
**Engine:** v7.0
**Last update:** 2026-08-27
**Core update in v1.5:** all output compression removed. The SOT gate becomes an input
flag. Unlike v1.4, **this version does change model behaviour.**

Evidence: `docs/postmortems/post_competition_conclusions.md`
Enforced by: `tests/test_calibration_regression.py`

---

## 0. Version history

### v1.5 — No-compression pipeline
- Removed confidence-based shrinkage (Δ Brier up to −0.0148, significant).
- Removed hard probability caps from the default path (Δ Brier up to −0.0169).
- SOT gate no longer modifies lambda; it flags divergent inputs.
- Context multiplier guard warns instead of clipping.
- Removed two accidental compression channels in the prior blend, and one downward
  clip in the parameter engine.
- Added the `p_model` / `p_blend` / `p_submit` output contract.
- Added the skip-don't-shrink rule.

### v1.4 — Shared CSV and output-divergence protocol
Shared CSV before engine run; second-engine cross-check reframed as input/data/code
verification; no output averaging. Procedural only.

### v1.3 — SOT module + global coherence / small-sample gates
Added the bottom-up SOT gate, lambda coherence, single-match shrinkage, relative 2H
data gate, global coherence and small-sample guards.

### v1.2 — Pre-match crowd removal + source-bound discipline
### v1.1 — Data sufficiency + source-bound rule
### v1.0 — Operational pipeline

---

## 1. Core principle

```text
Final probability =
    market / sportsbook prior when liquid
  + internal model output
  + event-rate and player-rate modules
  + lineup / news / role correction applied to INPUTS
  + referee correction applied to INPUTS
  + coherence check across related questions
  + small-sample guard
  + red-team check
  + final audit
```

Note what is absent: no shrink step, no cap step, no prudence step. Corrections are
applied to **inputs**, before the model runs. Once the model has spoken, the number
stands or the question is skipped.

### 1.1 The v1.5 rule

```text
Apply caution to the decision, not to the probability.
```

Compression is irreversible and invisible downstream. Skipping is free.

---

## 2. Source hierarchy

1. Official lineup / team news — highest authority for player props and roles.
2. Sportsbook / sharp market — strongest prior for liquid events.
3. Internal model — team strength, expected script, event priors.
4. Player/team aggregates — club-season rates per 90.
5. Match-specific news — injuries, tactics, referee, weather, rotation.
6. Event-level history — tactical checks, secondary.
7. Second model — red-team, missing-data finder.
8. Platform crowd — post-start only.

---

## 3. Workflow

### Step 0 — Shared CSV preparation
Single source of truth for player rates, team event rates, match context, market
anchors, referee data, lineup assumptions, and box-score data. Each field labelled:

```text
field_name | value | source | VERIFIED/ESTIMATED/MISSING | HIGH/MEDIUM/LOW | notes
```

If a key field is missing or low confidence, the options are: research it, use an
explicit conservative *input*, mark the question hard-review, or **skip it**. Producing
a hedged output is not on the list.

### Step 1 — Classify all 10 questions
market-driven / match-script / SOT volume / corners / fouls / cards / offside /
penalty-red / player SOT / player score-assist.

### Step 2 — Build the baseline
Market priors, team strength, expected game state, event-rate priors, roles, news.

### Step 3 — Market-first for liquid props
Devig match winner, totals, BTTS. Move away only with specific evidence.

### Step 4 — Missing-information scan
```text
Do we have lineups? Do we know the role? Do we have market odds?
Do we have event rates? Enough comparable data?
Is this built on one weird match?
```

### Step 5 — Type-specific modules
Player checklist, SOT module, offside, cards/referee, fouls, corners.

### Step 6 — Global coherence and small-sample gates
Mandatory for all question types.

### Step 7 — Second-engine cross-check on inputs
Check for stale/wrong values, rate mismatches, referee errors, role mismatches, schema
bugs, coherence violations. If outputs diverge, find the data/code cause. Never average.

### Step 8 — Final audit
Master v5.0 section 8.

---

## 4. Global rule A — Cross-question coherence

The ten probabilities are a joint object and must tell one story.

```text
High favourite win + very low team volume: needs a low-event control script.
High team SOT threshold + low both-teams-SOT: check implied lambdas.
High underdog 2H goal + very low underdog 2H SOT: inconsistent.
High 4+ cards + lenient referee + low foul profiles: likely overpriced.
High team more corners + very low territory: needs a transition/cross explanation.
High player SOT + low team SOT: only if the player is a dominant shot-taker.
```

If a number is incompatible with the rest of the sheet, it is mandatory-review — which
means *investigate it*, not *move it toward the others*.

---

## 5. Global rule B — Small-sample guard

Warning signs: one tournament match; one opponent-specific example; a historically
extreme stat; a role inferred from one lineup; a rate from non-comparable opposition;
club context transferred directly to national-team context.

A single match is directional evidence, role evidence, style evidence, a warning flag.
It is **not** a lambda, a baseline, or grounds for a >10 point move.

```text
If a probability move >8-10 points rests mainly on one match, stop.
Required: bottom-up confirmation, market confirmation, official role news,
a repeated pattern, or player/referee hard data.
```

**v1.5 clarification.** The correct response to a small-sample input is to fix or
distrust the *input*. It is not to compute a probability from the bad input and then
shrink it — that was the v1.3 error, and it measurably lost accuracy.

---

## 6. Symmetric hard-data gate

Applies equally to every model and every analyst.

| Evidence type | Move size |
|---|---|
| Official lineup / role news | 8–20 points |
| Hard player/team data | 8–15 points |
| Market correction | 5–15 points |
| Referee correction | 3–10 points |
| Single-match directional signal | 3–8 points |
| Narrative match-script | 2–6 points |
| Pure intuition | 0–3 points |

Any move >10 points needs hard data, lineup news, or market evidence. Convergence
between two models is not independent validation if both use the same narrative.

---

## 7. Output-divergence protocol

```text
The unit of cross-validation is the CSV, not the final probability.
```

| Engine-vs-engine divergence | Action |
|---|---|
| 0–2 points | OK |
| 3–5 points | minor review |
| 6–10 points | mandatory input/formula review |
| >10 points | full debug before submission |
| >15 points | output invalid until explained |

Never resolve disagreement by submitting the midpoint. Find the data, schema or formula
difference, fix it, rerun.

---

## 8. Output contract

```text
p_model    pure model output, untouched
p_blend    p_model blended with market/base priors
p_submit   what to submit; equals p_blend unless caps explicitly enabled
```

Valid reasons to submit something other than `p_submit`:

```text
official lineup change; confirmed injury/suspension; confirmed referee correction;
verified market-anchor error; verified input data error; verified schema bug;
verified formula/model bug.
```

Invalid reasons:

```text
another model differs; the number feels too high or too low; prudence;
narrative convergence; crowd convergence; fear of being aggressive.
```

---

## 9. Player prop checklist

```text
1. Starting XI?          7. Penalties?
2. Expected minutes?     8. Captain / top scorer / main creator / outlet?
3. Role in this XI?      9. Shoots from distance?
4. Central or peripheral? 10. Team attacking volume?
5. Set pieces?           11. Opponent defensive weakness?
6. Corners / free kicks? 12. Bench type if not starting?
```

**Unknown is not No.** Bench classification:

```text
Type A — low-impact reserve:    7-12%
Type B — likely attacking sub: 13-18%
Type C — star / high-impact:   18-25%
```

---

## 10. SOT volume module v1.5

The MD2 post-mortem showed SOT props leaking heavily while non-SOT props scored well.
v1.3 responded with a lambda-shrinking gate. Post-competition testing found that gate
unsupported: where it fired, Δ Brier −0.0107, CI95 [−0.0265, +0.0050], and leaning
further on bottom-up made things monotonically worse.

The real failure was never the absence of a shrink coefficient. It was a top-down
lambda of 7.5 built on **one match**.

### SOT-1 — Bottom-up divergence flag

Estimate both lambdas:

```text
Top-down: market/team strength, prior team SOT rate, opponent SOT conceded,
          expected territory, match script, previous-match signal.
Bottom-up: sum of projected starters' SOT contributions, minutes-adjusted,
          role-adjusted, set-piece adjusted.
```

If they differ by more than 30%:

```text
DO NOT shrink the lambda.
Ask instead: where did the top-down number come from?
  - built on one match?          -> the input is the problem. Fix or skip.
  - stale player rates?          -> fix the CSV and rerun.
  - lineup assumption wrong?     -> fix and rerun.
  - genuinely divergent, both sound? -> submit the top-down, note the flag.
```

Record `input_source_of_topdown`. That field, not the divergence, is the point.

### SOT-2 — Lambda coherence
Derive team total, team 2H, and player contributions, then check every SOT prop against
them. All SOT props on a sheet must speak the same lambda language. Incompatible pairs
are mandatory-review.

### SOT-3 — Single-match input warning
A single match is not a lambda. This is now an input warning, not an output shrink.

### SOT-4 — Relative 2H SOT data gate
No caps. Default without bottom-up confirmation: 50 ± 7.

```text
43-57  normal cautious range
58-60  aggressive but possible
>60    permitted, but requires bottom-up confirmation
```

High numbers are allowed when earned. Spain more 2H SOT than Saudi Arabia at 83% was
valid. New Zealand at 63% was not — narrative plus a one-match contrast.

### SOT-5 — Player SOT consistency
Player props must be compatible with team lambdas. A benched player is classified, not
crushed. A 27% prop that hits is variance, not necessarily model error.

---

## 11. Other modules

**Offside** — team offside rate, opponent line height, runner profile, directness,
script, attackers. Do not overfit one offside-heavy match. 2+ above 55 needs strong
tactical evidence.

**Fouls** — team fouls committed/suffered, pressing intensity, defensive game state,
ball-winners, opponent dribblers, referee style.

**Cards** — foul locations, tactical fouls, player yellow rates, referee severity,
stakes, chasing script. Without referee evidence, choose a base-rate estimate; do not
compute an aggressive one and then cut it.

**Corners** — territory, crossing style, wing attacks, low block, set-piece tendency.
Possession dominance is not corner dominance.

**Penalty / red card** — high variance. Referee history, box entries, dribbler-vs-tackler
mismatch, discipline. Base-rate anchored. The old 0.55 cap on this family was the most
damaging single component of the v6.2 calibration layer.

---

## 12. Model layer

**Market-implied** — convert odds, remove vig, use as prior.

**Goals** — Poisson / Dixon-Coles style, market-calibrated.

**Event counts** — Negative Binomial with `Var = mu + alpha*mu^2`, alpha ≈ 0.18–0.22
(0.30 for period props). NegBin beat Poisson, COM-Poisson, Weibull-Count and Bivariate
NB on a 301-match rolling backtest.

```text
NegBin       Brier 0.2030
BivarNB      Brier 0.2032
COM-Poisson  Brier 0.2038
Poisson      Brier 0.2057
WeibullCount Brier 0.2065
```

Do not compute SOT thresholds in Poisson by hand: on mu=7.5, Poisson gives 76% where
NegBin gives 62%. A systematic ~13-point upward bias.

**Player props** — rate per 90, starting probability, expected minutes, role, team
lambda, set pieces, opponent, bench type.

**Postmortem** — Brier / RBP, to separate calibration from luck.

---

## 13. Anti-overreaction rule

Do not update the pipeline because a low-probability event happened. A 27% event should
happen about one time in four. Update only when the **reasoning process** was wrong.

This applies to v1.5 itself. The changes here were made because a reasoning error was
repeatable and repeated three times — compressing an output to compensate for
uncertainty about an input — not because a matchday hurt.

---

## 14. Postmortem update process

```text
1. Record our probabilities.      5. Separate bad luck from bad model.
2. Record crowd.                  6. Identify repeatable reasoning errors.
3. Record outcomes.               7. Update only if the error is structural.
4. Record RBP/Brier.              8. Re-run the regression tests.
```

Step 8 is new in v1.5: `tests/test_calibration_regression.py` re-derives the evidence
behind this pipeline from the raw backtests. If a future change reintroduces
compression, the suite fails and names the finding it contradicts.
