# Post-Competition Conclusions

**Date:** 2026-08-27
**Status:** final review of the Jump / SportsPredict Probability Cup engine
**Result:** engine v7.0. Shrinkage and hard caps removed; SOT gate demoted to a flag.

This is the closing document of the competition. It goes back over the calibration
layer with the benefit of a finished season and enough data to test it properly,
and reaches an uncomfortable conclusion: **most of the machinery added during the
competition to make forecasts safer was making them worse.**

Everything here is reproducible from data already in this repository:

```bash
PYTHONPATH=src python3 tests/test_calibration_regression.py
```

---

## 1. Summary

During the Cup, after a bad matchday, the instinct was always the same: add a guard.
A shrink coefficient. A probability cap. A gate that pulls an aggressive lambda back
toward a more conservative one. Each was individually reasonable and each was added
in response to a real loss.

Tested together against the project's own backtests, they cost accuracy — every one
of them, in the same direction, monotonically. The root cause is a single fact that
was never checked at the time:

> The Negative Binomial model was already calibrated. Mean reliability bias +1.27pp.

An already-calibrated forecast has nothing to gain from compression. Every guard
built on top of it could only subtract.

The lesson is not "never be careful". It is that **caution has to be applied to the
decision, not to the probability**. Compressing the number destroys information;
declining to answer a question costs nothing. The Cup engine spent two versions doing
the first when it should have been doing the second.

---

## 2. Method

Two datasets already in the repository:

- `data/backtests/count_model_backtest/count_model_backtest_predictions.csv`
  7830 NegBin predictions with outcomes, across 261 matches.
- `data/backtests/historical_sot_gate_backtest.csv`
  8127 synthetic SOT props with top-down and gated probabilities recorded side by side.

Significance by **cluster bootstrap over matches**, 3000 resamples. Rows inside a
match are correlated — several thresholds per team-match — so a naive bootstrap over
rows would badly overstate significance. This matters: it is the same mistake, in
statistical form, as treating one match as a baseline.

Neither dataset contains market prices. See section 8 for what that rules out.

---

## 3. The model was already calibrated

| Bin | n | mean p | observed | gap |
|---|---|---|---|---|
| 10–20% | 465 | 16.5% | 17.4% | −0.9pp |
| 20–30% | 900 | 25.1% | 22.1% | +3.0pp |
| 30–40% | 1300 | 35.3% | 32.5% | +2.8pp |
| 40–50% | 1405 | 44.3% | 42.3% | +2.1pp |
| 50–60% | 972 | 55.1% | 54.8% | +0.3pp |
| 60–70% | 925 | 65.0% | 66.1% | −1.0pp |
| 70–80% | 794 | 74.4% | 73.4% | +1.0pp |
| 80–90% | 1011 | 84.8% | 83.7% | +1.1pp |

Mean bias **+1.27pp**. This single table explains every result that follows.

It also explains why the problem was invisible during the season: the engine was not
producing wild numbers that needed taming. It was producing good numbers that were
then being tamed.

---

## 4. Shrinkage — removed

| Transform | Δ Brier | CI95 | Verdict |
|---|---|---|---|
| shrink c=0.45 (`low`) | −0.0148 | [−0.0183, −0.0113] | significant |
| shrink c=0.60 (`medium_low`) | −0.0081 | [−0.0106, −0.0055] | significant |
| shrink c=0.75 (`medium`) | −0.0034 | [−0.0050, −0.0018] | significant |
| shrink c=0.92 (`high`) | −0.0005 | [−0.0010, +0.0000] | neutral |
| cap 0.55 (`rare_event`) | −0.0169 | [−0.0212, −0.0125] | significant |
| cap 0.68 (`player_prop`) | −0.0041 | [−0.0057, −0.0025] | significant |
| cap 0.74 (`team_stat`) | −0.0017 | [−0.0025, −0.0008] | significant |

Perfectly monotone: the harder the compression, the larger the loss. No exceptions.

Testing the opposite direction, `p' = sigmoid(k·logit(p))`, the optimal exponent was
**k = 1.05** — statistically indistinguishable from "leave it alone".

The single most damaging component was the `rare_event` cap at 0.55, which touched
3302 of 7830 rows. It was introduced because rare-event props felt dangerous. They
were not; the model handled them, and the cap removed its ability to say so.

---

## 5. Three silent compressions nobody had noticed

Beyond the explicit shrink coefficient, the calibration layer contained three further
one-directional cuts that were never intentional design decisions:

**5.1 The phantom context weight.** `weighted_raw_probability` blended four sources,
the fourth being `context_adj + base_prob`. When `context_adj` was 0 — the normal
case — that term was simply *extra weight on base_prob*. On player props this pushed
base_prob's effective weight from a declared 0.20 to an actual 0.45.

**5.2 The base_prob substitution.** When `market_prob` or `model_prob` was missing,
the old code substituted `base_prob` and kept the weight. Combined with 5.1, a row
with no market price gave a hand-typed number 55% of the total weight.

The clearest example, from the France–Iraq sheet, Q1:

| | |
|---|---|
| NegBin model output | **11.6%** |
| `base_prob`, typed by hand | 28% |
| submitted | **22** |

The model's opinion was overruled by a guess, silently, with no flag and no audit
trail. Whatever else the engine got right, this row was never really a model output.

**5.3 A third clip in the parameter engine.** `player_parameter_engine.aggregate_team`
ended with `final_mu = min(gate.gated_mu, capped_context_mu)` — a downward-only
minimum stacked on top of the gate shrink and the context cap. Three independent cuts
in the same direction, compounding.

None of these were decisions. They were accidents that happened to point the same way,
and because they always pointed *down*, they were never conspicuous — a forecast that
comes out lower than expected reads as prudence, not as a bug.

---

## 6. The SOT gate — kept, but demoted to a flag

The SOT gate was the flagship fix after the MD2 post-mortem, written to prevent a
repeat of Uruguay 6+ SOT (submitted 82%, outcome NO). Its own backtest does not
support it.

| Sample | Δ Brier (gated − top-down) | CI95 |
|---|---|---|
| all rows | −0.0018 | [−0.0059, +0.0021] |
| divergence >30% | −0.0107 | [−0.0265, +0.0050] |
| divergence >30%, ≥2021 | −0.0161 | [−0.0334, +0.0017] |

Point estimate consistently negative, confidence interval always crossing zero:
**no evidence it helps**, and no solid evidence it hurts either. It was never
validated.

Isolating the estimators on `team_sot` props where the gate fires gives a perfectly
monotone ordering:

| Estimator | Brier |
|---|---|
| top-down only | 0.1963 |
| 50/50 average | 0.2018 |
| gate (shrink 0.65 toward bottom-up) | 0.2086 |
| bottom-up only | 0.2342 |

The more weight on bottom-up, the worse the forecast. The gate's founding premise —
that the player bottom-up is the more trustworthy estimate — is false on this data.

It was also systematically directional: bottom-up sits below top-down in **74%** of
cases. What was documented as a symmetric "coherence check" was in practice a
constant downward push on lambda.

**Why it was kept anyway.** In this backtest the top-down estimator is a *rolling
multi-match* model — already decent. The Uruguay failure came from a top-down built
on a **single match** (10 SOT vs Saudi Arabia). The backtest contains no such row, so
it cannot test the scenario the gate was actually written for.

That distinction is the useful conclusion: **divergence is a good detector of a rotten
input, and a bad corrector of a lambda.** The gate now reports divergence and an
OK/REVIEW/BLOCK flag, and leaves mu alone. When it fires, a human looks at where the
top-down number came from. That is what would have saved the Uruguay sheet — not the
0.65 shrink coefficient, but somebody noticing that a lambda of 7.5 rested on one game.

---

## 7. A finding deliberately not acted on

Relative props ("A more than B") looked like they wanted the *opposite* of shrinkage:

| Family | optimal k | Δ Brier | CI95 |
|---|---|---|---|
| `relative_2h` | 1.40 | +0.0014 | [−0.0010, +0.0039] |
| `relative_total` | 1.60 | +0.0022 | [−0.0015, +0.0060] |

Sharpening, not compressing. Tempting — and both intervals cross zero, on n=522.

This is exactly the shape of the reasoning that produced the Uruguay error: an
attractive number on a small sample, with a plausible story attached. It was not
acted on, and `test_sharpening_does_not_help_either` now fails if anyone tries.

Recording a rejected finding matters as much as recording an accepted one. The
temptation after discovering "shrinkage was wrong" is to sprint to the opposite
extreme, and the same discipline that should have blocked the original mistake has to
block its mirror image.

---

## 8. What this does not establish

The backtests contain **no market prices**, and they are proxy backtests on synthetic
props built from a tournament-only event archive.

So: these results show the calibration layer was destroying accuracy the model already
had. They do **not** show the model is good in absolute terms, that it would have won
the Cup with these settings, or that it would beat a priced market. A measured harm was
removed. No edge was measured.

The old Master rule stands, and applies to this document too:

> Do not update because one outcome hurt. Update only when the reasoning error is
> repeatable.

The reasoning error here is repeatable and was repeated three times: compressing an
output to compensate for uncertainty about an input.

---

## 9. Changes made in v7.0

1. Shrinkage removed from the production path. `confidence` and `evidence_score` are
   still read and logged for audit, but no longer alter any probability.
2. Hard caps off by default, opt-in via `--apply-caps`.
3. The phantom context weight and the base_prob substitution removed. Missing sources
   are dropped and the remaining weights renormalised, so a missing market prior
   transfers weight to the **model**, not to a hand-typed number. `context_adj` is now
   an honest additive shift.
4. Output split into `p_model` / `p_blend` / `p_submit`, so the model's own opinion is
   never silently conflated with a market-blended one.
5. SOT gate: `modify_mu=False` by default. Reports divergence and a flag. Legacy
   behaviour reachable via `modify_mu=True`.
6. `context_multiplier_guard` warns instead of clipping.
7. The third downward clip in `player_parameter_engine` removed.
8. Imports converted to proper relative package imports; the package runs as
   `python3 -m jump_engine.pipeline`.
9. `tests/test_calibration_regression.py` re-derives every number in this document
   from the raw backtests and fails if compression is reintroduced.

### Effect on the France–Iraq example sheet

| Q | Market type | p_model | v6.2 | v7 | Δ |
|---|---|---|---|---|---|
| 1 | period_specific | 11.6% | 22 | 16 | −6 |
| 2 | team_stat | 21.4% | 33 | 25 | −8 |
| 3 | period_specific | 69.9% | 54 | 63 | +9 |
| 6 | match_outcome | 88.3% | 78 | **88** | +10 |
| 9 | period_specific | 81.1% | 74 | **80** | +6 |

Q6 and Q9 were sitting *exactly* on the old caps — 0.78 for `match_outcome`, 0.74 for
`period_specific`. They were not forecasts; they were the cap value. Q2 is the
France–Iraq foul prop discussed in the Master file, where `raw_model` was 21 and
`final_pipeline` 33.

---

## 10. Data quality note

In `historical_sot_gate_backtest.csv`, the `match_total_*` rows record a divergence
computed over the combined match total while the `top_mu` / `bottom_mu` columns hold a
single team's values. Those rows are not self-consistent and cannot be replayed through
the gate. The `team_*` rows reproduce exactly (6020/6020), and the estimator analysis in
section 6 was restricted to `team_sot` props for this reason.

---

## 11. What generalises

For anyone reading this repository as a case study rather than a codebase, three
things transfer:

**Check whether your model is calibrated before you build machinery to fix it.**
One reliability table, computed early, would have prevented two versions of work.

**Guards that only ever push one direction are not guards.** All three accidental
compressions here pushed down. Downward errors disguise themselves as prudence, so
they survive review in a way that upward errors never do.

**Apply caution to the decision, not to the number.** A forecast should be your honest
estimate. If you are not confident enough to act on it, decline to act — do not
quietly move the estimate toward the middle and act on that instead. Those two are not
the same thing, and only the first one is recoverable.
