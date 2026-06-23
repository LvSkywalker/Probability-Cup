# Jump / SportsPredict Probability Cup — Master File

**Version:** Master v4.1  
**Canonical pipeline:** v1.4  
**Last update:** 2026-06-23  
**Purpose:** one-file operational memory for new chats and Claude handoff.

**v4.1 update:** shared CSV discipline and output-divergence protocol added. Cross-checking now happens at the input/data/code layer, not by averaging output probabilities. No model parameters changed.

---

## 0. How to use this file in a new chat

Say:

> Usa `jump_probability_cup_master_v4_1.md` as the canonical project memory. Apply pipeline v1.4: shared CSV before engine run, no crowd pre-match, market-first for liquid props, player checklist, SOT bottom-up/lambda coherence module, global cross-question coherence check, small-sample guard, source-bound rule, dual-engine input/code reconciliation, and final audit before submission.

Then provide the match and the ten questions.

---

## 1. Difference between Master and Pipeline

### Pipeline
The pipeline is the **method specification**:

```text
rules
models
checklists
gates
how to price each prop type
how to audit before submission
```

It answers:

```text
How do we forecast?
```

### Master
The master is the **project memory and operating handbook**:

```text
current canonical pipeline version
how to use the project
lessons learned
postmortems
current sheets
handoff instructions
file structure
Claude protocol
```

It answers:

```text
What have we learned and what is the current state of the project?
```

In short:

```text
Pipeline = rules of the model.
Master = rules + history + lessons + current operating context.
```

---

## 2. Core philosophy

We are not trying to predict football generically. We are assigning calibrated probabilities to binary propositions.

The model has edge when it is disciplined:

```text
market-first for liquid props;
role-first for player props;
bottom-up for SOT volume;
coherence-first across correlated questions;
small-sample guard before aggressive moves;
shared CSV before engine run;
Claude as CSV verifier/data scout/code sanity check, not probability authority;
final_pipeline as submit default.
```

v4.1 clarification:

Cross-checking must happen at the input/data/code layer.

The correct question is not:

```text
Which probability do we like better?
```

The correct question is:

```text
Are both engines using the same verified inputs?
If yes, why do their formulas produce different outputs?
If no, which CSV field or source is wrong?
```

No output averaging.

---

## 3. Current canonical pipeline: v1.4

Major v1.3 additions still active:

```text
1. SOT-1 Bottom-up SOT gate.
2. SOT-2 Lambda coherence check across related SOT questions.
3. SOT-3 Single-match shrinkage.
4. SOT-4 Relative 2H SOT data gate, not hard cap.
5. SOT-5 Player SOT consistency.
6. Global Cross-Question Coherence Check.
7. Global Small-Sample Guard.
8. Symmetric Hard-Data Gate for ChatGPT, Claude, human analyst and any model output.
9. Shared CSV/input set before engine run.
10. Dual-engine reconciliation at data/code layer.
11. No output-level probability averaging.
12. final_pipeline remains submit default.
```

v1.4 does not change model parameters. It changes the validation protocol.

---

## 4. Essential hard rules

### 4.1 Crowd rule

```text
Platform crowd is never a pre-match input.
Crowd is post-start/post-match benchmark only.
```

### 4.2 Coherence rule

```text
The ten probabilities in a sheet must describe one coherent match script.
If one number is incompatible with others, stop and audit it.
```

### 4.3 Small-sample rule

```text
Never make aggressive decisions from very little data.
One match is signal, not baseline.
```

### 4.4 SOT rule

```text
Any SOT volume question requires explicit top-down vs bottom-up reasoning.
Multiple SOT questions require lambda coherence.
```

### 4.5 Player prop rule

```text
Starting XI, minutes and role come before raw averages.
Unknown is not No.
Bench player is not automatically dead: classify the bench type.
```

### 4.6 Claude/Chat rule

```text
No model moves a quote aggressively without hard-data gate.
Convergence is not validation if both models use the same narrative.
```

v4.1 update:

Claude / Chat / second engine cross-checks happen on inputs, not output probabilities.

If Claude and Chat produce different probabilities from the same CSV:

```text
Debug model family, formulas, gates, schema mapping, or implementation.
```

If Claude and Chat produce different probabilities from different CSVs:

```text
Fix the CSV/data/source mismatch and rerun.
```

In neither case is the correct resolution to average the output probabilities.

Rule:

```text
If outputs diverge, reconcile data/code, not probabilities.
```

---

## 4A. Shared CSV / Output-Divergence Hard Rule

### 4A.1 Single source of truth

Before running forecasts, build or confirm a shared CSV/input set.

The shared CSV must contain the inputs actually used by the engine:

```text
- player rates;
- team rates;
- market anchors;
- match context;
- MD box-score data;
- referee data where relevant;
- lineup/role/minutes assumptions;
- source labels.
```

Each key field should be marked:

```text
VERIFIED / ESTIMATED / MISSING
HIGH / MEDIUM / LOW confidence
```

### 4A.2 Cross-checking unit

```text
The unit of cross-validation is the CSV, not the final probability.
```

### 4A.3 Divergence rule

If two engines diverge materially:

```text
Do not average outputs.
Do not submit a midpoint.
Do not move lower for prudence.
Do not move toward narrative convergence.
```

Instead:

```text
1. Check whether both engines used the same CSV.
2. If not, reconcile the data/source mismatch.
3. If yes, debug schema/formula/model implementation.
4. Rerun after correction.
5. Submit final_pipeline.
```

### 4A.4 Output override rule

A final probability may move more than 5 points away from final_pipeline only with explicit hard evidence.

Allowed:

```text
- official lineup;
- confirmed injury/suspension;
- confirmed referee/stat correction;
- verified market-anchor error;
- verified input data error;
- verified CSV/schema bug;
- verified code/formula/model bug.
```

Invalid:

```text
- Claude probability differs;
- Chat probability differs;
- probability feels too aggressive;
- prudence;
- narrative convergence;
- crowd convergence.
```

---

## 5. Model modules used

```text
Market-implied probability model
Dixon-Coles / Poisson style goals model
Event-rate Poisson/Binomial model
SOT bottom-up lambda model
Player prop role/minutes model
Cards/fouls referee-weighted model
Corners territory/crossing model
Offside tactical-volatility model
Brier/RBP postmortem model
```

---

## 6. SOT postmortem MD2 — key lesson

MD2 exposed a systematic leak:

```text
Non-SOT questions: strong positive RBP.
SOT questions: large negative RBP.
```

The problem was not the whole pipeline. The problem was the SOT volume submodel.

Root causes:

```text
1. Top-down SOT lambdas built from one-match data without bottom-up player validation.
2. Relative 2H SOT narrative extrapolations without bottom-up support.
3. Failure to check lambda coherence across correlated SOT questions.
```

Main examples:

```text
Uruguay 6+ SOT at 82%: overbuilt from Uruguay 10 SOT MD1 + Cape Verde 7 SOT conceded vs Spain.
NZ more 2H SOT than Egypt at 63%: narrative + MD1 contrast, no bottom-up.
Tielemans 1+ SOT at 27% hit: variance, not necessarily model error.
```

---

## 7. Lessons learned by category

### Offside
Offside was profitable when grounded in specific tactical/rate evidence. Still volatile; avoid one-match overfitting.

### Fouls
Fouls worked when based on hard data: team foul rates, Ugarte/Bentancur profiles, pressing/transition context.

### Cards
Cards require referee/player/team evidence. Without referee edge, stay prudent.

### Player props
Player checklist works. Benched players must be classified by impact type.

### Corners
Usually more stable; keep tied to territory and crossing/set-piece script.

### Penalty/red card
High variance. Conservative unless referee + box-entry/tackler evidence strongly supports higher pricing.

### SOT
Requires dedicated bottom-up and lambda coherence checks.

---

## 8. Recent postmortems — condensed

### Spain–Saudi
Strong positive result. Pipeline worked because market and match-script were clear, Spain volume was strong, Saudi scoring was low, and player prop Salem was kept low.

### Belgium–Iran
Near flat. Tielemans hit at 27% was variance, not necessarily model error. Cards 2H was slightly overestimated.

### Uruguay–Cape Verde
Main win: Uruguay fouls/cards corrected through hard data. Main loss: Uruguay 6+ SOT overestimated due to top-down one-match lambda and failure to cut after Darwin benched/midfield-packed XI. Cape Verde 2H SOT/goal was underpriced but partly variance.

### New Zealand–Egypt
Main loss: NZ more 2H SOT at 63 was narrative extrapolation without bottom-up validation. Waine bench prop was correctly low; Trezeguet needed more nuanced bench classification.

---

## 9. Current final sheets from latest state

### Uruguay–Cape Verde final submitted / discussed

```text
44
52
38/40
26
61/60
22/26
68
18/20
11/18 depending exact submission timing
82/80 depending exact submission timing
```

Postmortem note: the main structural error was Q10 Uruguay 6+ SOT.

### New Zealand–Egypt final discussed

```text
34
49
63
50
56
16/18
55
48
11
16/11 depending Trezeguet revision
```

Postmortem note: the main structural error was Q3 New Zealand more 2H SOT.

---

## 10. Final pre-submission audit template

```markdown
# Pipeline Audit — [Match]

## Sheet
[10 probabilities]

## 1. Prop classification
[table]

## 2. Market anchors
[match winner / totals / BTTS / available props]

## 3. Lineup and role check
[official or predicted]

## 4. Player Prop Checklist
[for every player]

## 5. SOT Module
Top-down lambdas:
- Team A total SOT:
- Team B total SOT:
- Team A 2H SOT:
- Team B 2H SOT:

Bottom-up lambdas:
- Team A:
- Team B:

Coherence:
- Qx implies:
- Qy implies:
- conflicts:

## 6. Global coherence check
[all question relationships]

## 7. Small-sample guard
[which estimates rely on few data points?]

## 8. Shared CSV / input reconciliation
- Shared CSV used: YES/NO
- Key fields source-labelled: YES/NO
- Estimated or missing fields:
- Claude/second-engine checked inputs: YES/NO
- Any engine divergence >5 points:
- Cause of divergence:
  - data mismatch
  - schema mismatch
  - formula/code mismatch
  - hard evidence not in CSV
  - unresolved
- Rerun after correction: YES/NO

## 9. Claude / red-team divergences
[divergence, evidence type, accepted/rejected]

## 10. Extreme quote justification
[anything >70 or <30]

## 11. Final verdict
Ready / Not ready / Need lineup / Need data
```


---

## 10A. Mandatory Pre-Submission Audit Checklist

**Hard rule:** no final submission without completing this checklist.

The pipeline is the default. Claude, ChatGPT, Gemini and human intuition are challengers, not automatic quote movers.

```text
SHARED CSV → ENGINE OUTPUT → SECOND-ENGINE / CLAUDE INPUT AUDIT → DATA/CODE RECONCILIATION → FINAL_PIPELINE → FINAL DECISION
```

Never skip the audit because an external explanation sounds convincing.

### 1. Run engine first

Before listening to Claude/human intuition, record the engine output.

Required fields:

```text
engine_probability
engine_audit
model_family
key_inputs
```

Rule:

```text
Pipeline is default.
Claude/human is challenger, not authority.
```

### 2. Claude / external input-data divergence audit

For every question where a Claude / human / external model probability is available, do not average outputs.

First ask:

```text
Did both engines use the same CSV?
If no: reconcile CSV/input/source mismatch and rerun.
If yes: debug formula/schema/model implementation.
```

Only after data/code reconciliation may a final probability be accepted.

Thresholds for engine-vs-engine output divergence:

```text
0–5 points: OK / minor review.
6–10 points: INPUT OR FORMULA REVIEW.
>10 points: FULL DEBUG.
>15 points: OUTPUT INVALID until mismatch is explained.
```

Mandatory table:

```text
Question
Engine probability
External probability, if available
Difference
Same CSV? YES/NO
Flag
Divergence cause: data / schema / formula-code / hard evidence / unresolved
Decision
Final probability
```

Rule:

```text
Claude cannot move a quote by output disagreement alone.
Claude can only trigger:
- input correction;
- source correction;
- schema/code review;
- hard-evidence update;
- rerun.
```

### 3. Evidence classification

Every override must classify its evidence:

```text
A. Market hard data
B. Official lineup / confirmed role
C. Referee / official assignment
D. Player historical data, role-adjusted
E. Team tactical hard data
F. Single-match signal
G. Narrative / intuition
```

Rule:

```text
Only A, B, C, D role-adjusted, or strong E can move a quote aggressively.
F and G cannot justify hard override.
```

### 4. Player SOT checklist

For every player SOT prop, complete:

```text
player
starter?
minutes expected
club SOT/90
national/team role
position today
set pieces?
penalties?
free kicks?
corners?
long-shot profile?
main shooter?
main creator?
team SOT mu
player share of team shots/SOT
opponent defensive strength
game-state script
```

Rules:

```text
Unknown is not No.
Club SOT rate cannot override national role unless role is the same.
```

### 5. Team SOT audit

For every team/match SOT prop, record:

```text
mu_topdown
mu_bottomup_player_raw
mu_bottomup_after_floor
wc_floor_applied
gate_divergence
gate_flag
evidence_score
shrink_used
mu_gated
distribution
probability
```

Rules:

```text
If divergence > 30%, REVIEW.
If divergence > 60%, BLOCK / strong REVIEW.
```

### 6. SOT coherence check

If one sheet contains multiple SOT props, produce a lambda coherence table:

```text
mu_A_total
mu_B_total
mu_A_2H
mu_B_2H
P(A 1+ SOT 2H)
P(B 1+ SOT 2H)
P(A 2+ SOT 2H)
P(B 2+ SOT 2H)
P(A X+ total SOT)
P(A more SOT than B)
```

Rule:

```text
All SOT props must speak the same lambda language.
```

### 7. Underdog 2H SOT guard

For any underdog 2H SOT prop, check:

```text
is underdog likely chasing?
2H share used
transition threat
attacking outlets
favorite likely to lower tempo?
garbage-time possibility
```

v6.2 rule:

```text
standard 2H share = 0.50
chasing underdog share ≈ 0.56
```

### 8. Corner profile check

For every corner prop, do not rely on possession only. Complete:

```text
expected possession
field tilt
wide attacks
crossing profile
high press
transition-to-cross profile
opponent build-up pressure
game state
corner mu team A
corner mu team B
```

Rule:

```text
Possession dominance is not the same as corner dominance.
An aggressive / vertical / high-press underdog can generate corners without dominating the ball.
```

### 9. Cards / referee check

For cards props, record:

```text
referee
referee cards/game
red-card tendency
match importance
team foul profiles
pressing/aggression
derby/rivalry/emotional factor
game-state risk
```

Rules:

```text
If referee unknown, do not push too aggressively.
If the engine cards module has a known limitation, use referee + World Cup baseline.
```

### 10. Market-first check

For liquid markets, anchor to devigged market:

```text
match winner
over/under goals
BTTS
main handicaps
```

Rule:

```text
Market beats internal model on liquid questions unless we have hard match-specific data.
```

### 11. Source-bound aggressiveness rule

Every aggressive quote must be inside a source-supported range.

Rule:

```text
If final probability is far outside the independent-source range,
provide hard-data explanation or do not submit the aggressive quote.
```

### 12. Small-sample guard

One match cannot become a full baseline.

Rule:

```text
single-match data = directional signal, not baseline
```

### 13. Context multiplier guard

Record:

```text
attack_mult
defense_mult
possession_factor
script_mult
combined_context_mult
```

v6.2 rule:

```text
combined_context_mult > 1.65 → REVIEW
```

This is a warning, not a hard cap.

### 14. Final override decision label

Each final probability must have one decision label:

```text
ENGINE ACCEPTED
ENGINE + SMALL ADJUSTMENT
MARKET OVERRIDE
CLAUDE OVERRIDE ACCEPTED
CLAUDE OVERRIDE REJECTED
HUMAN OVERRIDE ACCEPTED
SKIP
```

And one short reason.

### 15. Extreme quote justification

For every quote above 70 or below 30, write why it has earned its extremity.

Rule:

```text
Do not submit aggressive probabilities that have not earned their extremity.
```

### 16. Global cross-question coherence check

The whole sheet must imply one coherent match script.

Check:

```text
winner vs goals
winner vs SOT
SOT vs goals
corners vs territory / pressing
cards vs fouls / referee
2H props vs game-state script
```

### 17. Skip / answer decision

For each question, decide:

```text
submit
skip
```

Rule:

```text
If we can articulate a reasoned lean, submit.
If it is pure noise with no edge, skip.
```

### 18. Final sign-off preparation

Before final sign-off, make sure all unresolved hard-review items have been resolved or explicitly blocked.

### 19. Shared CSV / final_pipeline divergence check

Before submission, record:

```text
shared_csv_used: YES/NO
second_engine_used_same_csv: YES/NO/N/A
max_engine_divergence:
divergence_cause:
rerun_after_reconciliation: YES/NO/N/A
```

For every question:

```text
final_pipeline_probability
final_submit_probability
absolute_difference
hard_evidence_if_difference_gt_5
decision
```

Rules:

```text
If abs(final_submit - final_pipeline) > 5, hard evidence is required.
If >8–10 without hard evidence, revert to final_pipeline.
If >15, block unless verified input/code/lineup/referee/market evidence exists.
```

### 20. Final sign-off

Before submission, write:

```text
All mandatory checks completed: YES/NO
Unresolved hard-review items:
Final vector:
Ready / Not ready:
```

If the answer is not `YES`, do not submit.

---

## 11. Claude handoff prompt

```markdown
Use pipeline v1.4. Do not move quotes automatically.

Primary role:
CSV/input verification, source validation, and implementation sanity check.

Do not generate alternative probabilities for averaging.

Before engine run:
1. Check the shared CSV/input table.
2. Flag wrong, stale, missing, estimated, or low-confidence fields.
3. Verify key player/team/referee/market inputs where possible.
4. Check schema/column mapping.
5. Return corrections as field-level changes, not probability changes.

Required correction format:

```text
field_name:
current_value:
proposed_value:
source:
status: VERIFIED / ESTIMATED / MISSING
confidence: HIGH / MEDIUM / LOW
evidence_type:
action: accept / reject / needs research / rerun
```

After engine run:
1. If your engine output differs from Chat/final_pipeline, identify whether the cause is:
   - CSV/input mismatch;
   - schema mismatch;
   - formula/model implementation difference;
   - hard evidence not yet reflected in the CSV.
2. Do not propose an averaged probability.
3. If data or code is corrected, rerun the engine.

For every SOT question, still run:
1. top-down lambda;
2. bottom-up player lambda;
3. lambda coherence across related SOT props;
4. single-match shrinkage check.

For the whole sheet, still run:
1. cross-question coherence check;
2. small-sample guard;
3. source-bound aggressiveness check.
```

---

## 12. Project file structure

```text
jump_probability_cup_full_handoff_v2/
├── 00_master/
│   └── jump_probability_cup_master_v2.md
├── 01_pipeline_versions/
│   ├── jump_cup_forecasting_pipeline_v1_1.md
│   ├── jump_cup_forecasting_pipeline_v1_2.md
│   └── jump_cup_forecasting_pipeline_v1_3.md
├── 02_model_specs/
│   ├── model_pipeline_description.md
│   ├── MODEL_SPEC.md files
│   └── README files
├── 03_data_and_workbooks/
│   ├── forecast workbooks
│   ├── match csvs
│   ├── shared_csv_inputs/
│   └── StatsBomb packages
├── 04_reports/
│   └── generated reports
├── 05_competition_docs/
│   └── scoring/resources PDFs
└── README_FOR_CLAUDE.md
```

---

## 13. MD3 Backtest Lesson — Input Cross-Check, Not Output Averaging

Added: 2026-06-23.

The MD3 postmortem showed a repeatable procedural error:

```text
Cross-checking was happening on output probabilities instead of input data.
```

When two models used different CSVs, different assumptions, or different implementations, output-level compromise introduced noise.

Backtest numbers, MD3 preliminary 4-match sample:

```text
Chat engine puro:                  +20.40 RBP
Submitted, cross-checked outputs:  -31.25 RBP
Delta:                             -51.65 RBP
```

These numbers are not a model-parameter update. They are evidence for a workflow update.

New rule:

```text
Do not cross-check probabilities.
Cross-check data inputs and code implementation.
```

If two engines disagree:

```text
1. Check the CSV.
2. Check the source values.
3. Check schema/column mapping.
4. Check formula/model implementation.
5. Rerun.
6. Submit final_pipeline.
```

Do not submit a compromise probability.

This update does not change model parameters. It only changes the validation protocol.

---

## 14. Golden rule

```text
Do not update because one outcome hurt.
Update only when the reasoning error is repeatable.
Do not submit aggressive probabilities that have not earned their extremity.
```

---

## 15. Critical patch — Final Pipeline Priority Rule

This rule was added after the France–Iraq foul-prop mistake.

```text
SUBMISSION DEFAULT = final_pipeline, not raw_model.
raw_model is diagnostic only.
```

Operational rule:

```text
1. The first vector shown to the user must be the SUBMIT vector.
2. The SUBMIT vector uses final_pipeline by default.
3. raw_model may be shown only in a clearly labeled audit table: RAW MODEL — NON SUBMIT.
4. If Claude/human is rejected, return to final_pipeline, not raw_model.
5. raw_model can replace final_pipeline only if final_pipeline explicitly fails audit.
6. final_pipeline fails audit only for documented reasons:
   - liquid-market cap/shrink error;
   - known model-family bug;
   - wrong base_prob contamination;
   - wrong input data;
   - incoherent output versus mandatory audit checks.
7. For liquid market questions, market-first can override final_pipeline when final_pipeline is visibly capped or under-shrunk.
```

Example: France–Iraq Q2, France more fouls.

```text
raw_model = 21
final_pipeline = 33
Claude = 36
crowd = 34

Correct decision: final_pipeline accepted = 33.
Incorrect decision: raw_model accepted = 21.
```

Lesson:

```text
Rejecting Claude does not imply using raw_model.
The default fallback is final_pipeline.
```

---

## 16. Cross-family coherence patch

This rule was hardened after Argentina–Austria.

```text
No final submission unless cross-family coherence is checked across all props sharing the same match script.
```

Mandatory cross-family checks:

```text
winner ↔ goals
winner ↔ SOT
SOT team ↔ player SOT
SOT ↔ corners
corners ↔ possession / field tilt / pressing / wide attacks
fouls ↔ cards ↔ referee
2H props ↔ expected game state
underdog 2H props ↔ chasing script
```

Argentina–Austria failure:

```text
Sabitzer 1+ SOT: engine 37 vs Claude 13, diff 24 → should have been OVERRIDE BLOCKED.
Austria more corners: engine 34 vs Claude 19, diff 15 → should have been HARD REVIEW.
```

The mistake was not only the individual quote; it was accepting an incoherent story:

```text
Austria alive enough for 2H SOT,
but almost dead for corners and Sabitzer SOT.
```

Correct procedure:

```text
If team output is non-trivial, key player involvement cannot be crushed without role-adjusted evidence.
If underdog pressing/wide/transition profile exists, corner probability cannot be crushed only from possession narrative.
```

---

## 17. Mandatory output format going forward

Every engine answer must start with:

```text
SUBMIT VECTOR — final_pipeline / audited overrides only
```

Then, optionally:

```text
AUDIT TABLE — raw_model, final_pipeline, Claude, crowd, market
RAW MODEL — NON SUBMIT
```

Never send raw_model as the first or main vector.
