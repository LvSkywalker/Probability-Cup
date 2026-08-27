# Jump / SportsPredict Probability Cup — Master File

**Version:** Master v5.0 — final
**Canonical pipeline:** v1.5
**Engine:** v7.0
**Last update:** 2026-08-27
**Status:** competition closed. This is the closing state of the project.

**v5.0 update:** shrinkage and hard caps removed after post-competition testing; the
SOT gate demoted from lambda corrector to input flag. Unlike v1.4, this update *does*
change model behaviour. Evidence: `docs/postmortems/post_competition_conclusions.md`.

Supersedes v4.1, which is kept in this repo as a record of the in-season state.

---

## 0. How to use this file

> Use `jump_probability_cup_master_v5.md` as the canonical project memory. Apply
> pipeline v1.5: shared CSV before engine run, no crowd pre-match, market-first for
> liquid props, player checklist, SOT flag module, global cross-question coherence
> check, small-sample guard, source-bound rule, dual-engine input/code reconciliation,
> and final audit before submission. Never compress an output probability.

---

## 1. Master vs Pipeline

**Pipeline** is the method specification: rules, models, checklists, gates, how to
price each prop type, how to audit before submission. It answers *how do we forecast?*

**Master** is the project memory: canonical versions, lessons learned, postmortems,
handoff instructions, operating context. It answers *what have we learned and what is
the current state?*

---

## 2. Core philosophy

We are not predicting football generically. We are assigning calibrated probabilities
to binary propositions.

```text
market-first for liquid props;
role-first for player props;
bottom-up as a CHECK on SOT volume, never as an automatic correction;
coherence-first across correlated questions;
small-sample guard before aggressive moves;
shared CSV before engine run;
second engine as CSV verifier and code sanity check, not probability authority;
the model output is the forecast — no compression.
```

### 2.1 The v5.0 principle

```text
Apply caution to the DECISION, not to the PROBABILITY.
```

Compressing a number destroys information and cannot be undone downstream. Declining
to answer a question costs nothing. Between v1.2 and v1.4 this project consistently
did the first when it should have done the second.

Concretely:

| Uncertain about... | Wrong response | Right response |
|---|---|---|
| an input value | shrink the output | fix the input, or flag and skip |
| a lambda built on one match | shrink toward a "safer" lambda | flag the input; get more data or skip |
| an aggressive-looking number | cap it | check whether it earned its extremity; if yes, submit it |
| the whole question | submit a hedged midpoint | skip the question |

---

## 3. Canonical pipeline: v1.5

Active modules:

```text
1.  SOT-1 Bottom-up divergence FLAG (does not modify mu).
2.  SOT-2 Lambda coherence check across related SOT questions.
3.  SOT-3 Single-match input warning.
4.  SOT-4 Relative 2H SOT data gate (review threshold, not a cap).
5.  SOT-5 Player SOT consistency check.
6.  Global Cross-Question Coherence Check.
7.  Global Small-Sample Guard.
8.  Symmetric Hard-Data Gate for any model or analyst output.
9.  Shared CSV/input set before engine run.
10. Dual-engine reconciliation at data/code layer.
11. No output-level probability averaging.
12. No output compression of any kind.
```

Removed in v1.5, with evidence:

```text
- confidence-based shrinkage        (delta Brier up to -0.0148, significant)
- hard probability caps             (delta Brier up to -0.0169, significant)
- SOT gate lambda shrinkage         (delta Brier -0.0107, not supported)
- context multiplier hard cap       (never validated)
- the phantom base_prob weighting   (accidental, undocumented)
```

---

## 4. Essential hard rules

### 4.1 Crowd rule
Platform crowd is never a pre-match input. Post-start benchmark only.

### 4.2 Coherence rule
The ten probabilities must describe one coherent match script. If one number is
incompatible with the others, it becomes mandatory-review.

### 4.3 Small-sample rule
One match is signal, not baseline. Never make aggressive decisions from very little
data — and never resolve the discomfort by shrinking the output.

### 4.4 SOT rule
Any SOT volume question requires explicit top-down vs bottom-up reasoning. Divergence
raises a flag for human inspection; it does not move the lambda.

### 4.5 Player prop rule
Starting XI, minutes and role come before raw averages. Unknown is not No. Classify
the bench type.

### 4.6 No-compression rule (v5.0)
```text
No shrinkage. No caps. No prudence haircut.
The model output is the forecast.
If you are not willing to submit it, skip the question — do not move it.
```

### 4.7 Second-engine rule
Cross-checks happen on inputs and code, never on output probabilities. If two engines
disagree, find the data/schema/formula cause. Never submit a midpoint.

---

## 5. Output contract

```text
p_model    pure model output. Untouched by priors, caps or gates.
p_blend    p_model blended with market / base priors.
p_submit   what to submit. Equals p_blend unless caps are explicitly enabled.
```

Every probability must be traceable to one of these. A number that matches none of
them is an override and requires written hard-evidence justification.

---

## 6. Lessons learned

### 6.1 The structural lesson

Every guard added during the season was a reaction to a specific loss, and every one
was individually defensible. Tested together, they cost accuracy — because nobody had
checked the premise underneath all of them. The model was already calibrated
(reliability bias +1.27pp). One table, computed early, would have prevented two
versions of work.

**Check whether the model is calibrated before building machinery to fix it.**

### 6.2 One-directional guards are not guards

All three accidental compressions found in the post-competition review pushed *down*.
A downward error reads as prudence and survives review; an upward error looks like
recklessness and gets caught immediately. That asymmetry in how errors are perceived
is what let them live for two versions.

**Audit specifically for guards that can only ever move one way.**

### 6.3 Don't sprint to the opposite extreme

The same review found that relative props looked like they wanted *sharpening*
(k=1.40–1.60, gains of +0.0014/+0.0022). Both confidence intervals crossed zero on
n=522. Not acted on. The discipline that should have blocked the original error must
also block its mirror image.

### 6.4 By prop family

**SOT** — the MD2 leak was real but misdiagnosed. The problem was a lambda built on a
single match, not the absence of a shrink coefficient. The fix is input validation, not
output correction.

**Fouls** — worked when grounded in hard team/player rates. Ugarte/Bentancur profiles,
pressing and transition context.

**Cards** — require referee evidence. Without a referee edge, stay near base rates.
"Stay near base rates" means choosing a base-rate estimate, not shrinking a computed one.

**Corners** — more stable. Possession dominance is not corner dominance: an aggressive
vertical underdog generates corners without holding the ball.

**Offside** — profitable when grounded in specific tactical/rate evidence. Volatile.

**Penalty/red card** — high variance. The old 0.55 cap on this family was the single
most damaging component of the calibration layer.

**Player props** — the checklist works. Bench players must be classified by impact type.

---

## 7. Postmortems — condensed

**Spain–Saudi.** Strong positive. Market and match-script were clear.

**Belgium–Iran.** Near flat. Tielemans hit at 27% was variance, not model error.

**Uruguay–Cape Verde.** Main win: Uruguay fouls/cards corrected through hard data.
Main loss: Uruguay 6+ SOT at 82%, built from a single-match lambda of 7.5. The v7 flag
would have raised REVIEW on that input — which is where the fix belonged.

**New Zealand–Egypt.** Main loss: NZ more 2H SOT at 63, narrative extrapolation without
bottom-up validation.

**MD3.** Cross-checking on output probabilities instead of input data: Chat engine pure
+20.40 RBP, submitted cross-checked outputs −31.25 RBP. This was the first clear
evidence that compromising at the output layer destroys value; the v5.0 no-compression
rule is the generalisation of it.

---

## 8. Pre-submission audit checklist

```text
1.  Every prop classified?
2.  Market checked for liquid props?
3.  Platform crowd excluded pre-match?
4.  Lineup / news / injuries checked?
5.  Referee checked where relevant?
6.  Player Prop Checklist completed?
7.  SOT divergence flags reviewed — and INPUTS inspected where they fired?
8.  SOT lambda coherence checked if multiple SOT props?
9.  Cross-question coherence check completed?
10. Small-sample guard passed?
11. Shared CSV verified before engine run?
12. Second-engine divergence reconciled at data/code layer, not by averaging?
13. Every quote above 70 or below 30 justified by hard data?
14. Every submitted number traceable to p_model, p_blend, or a written override?
15. NO probability compressed, capped, or hedged toward the middle?
16. For anything you would not submit as-is: skipped rather than moved?
17. Ready to submit?
```

If any answer is No, do not submit.

### 8.1 Evidence classification for overrides

```text
A. Market hard data
B. Official lineup / confirmed role
C. Referee / official assignment
D. Player historical data, role-adjusted
E. Team tactical hard data
F. Single-match signal
G. Narrative / intuition
```

Only A, B, C, D or strong E may move a quote aggressively. F and G cannot.

### 8.2 SOT audit fields

```text
mu_topdown
mu_bottomup
gate_divergence
gate_flag
input_source_of_topdown      <- v5.0: the field that actually mattered
context_multiplier
context_flag
distribution
probability
```

`input_source_of_topdown` is new and is the point of the whole SOT module: if the
top-down lambda came from one match, that is the problem, and no coefficient fixes it.

---

## 9. Skip rule

For each question: submit or skip.

```text
If we can articulate a reasoned lean, submit the honest probability.
If it is noise, skip.
Never submit a compressed probability as a substitute for skipping.
```

---

## 10. Golden rules

```text
Do not update because one outcome hurt.
Update only when the reasoning error is repeatable.
Do not submit aggressive probabilities that have not earned their extremity.
Do not compress probabilities that have.
Check calibration before building machinery to fix it.
Apply caution to the decision, not to the number.
```
