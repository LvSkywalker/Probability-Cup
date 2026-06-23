# Jump / SportsPredict Probability Cup — Forecasting Pipeline v1.3

**Status:** canonical operational pipeline  
**Last update:** 2026-06-22  
**Scope:** binary football propositions for Jump Trading Probability Cup / SportsPredict  
**Core update in v1.3:** full SOT volume module, cross-question coherence check, small-sample guard, symmetric hard-data gate.

---

## 0. Version history

### v1.3 — SOT module + global coherence / small-sample gates
- Added **SOT-1 Bottom-up SOT Gate**.
- Added **SOT-2 Lambda Coherence Check** across all correlated SOT questions in the same sheet.
- Added **SOT-3 Single-Match Shrinkage Rule**.
- Added **SOT-4 Relative 2H SOT Data Gate** as a conditional data gate, not a hard cap.
- Added **Global Cross-Question Coherence Check** for every question type.
- Added **Global Small-Sample Guard** for every question type.
- Reframed Claude/Chat as symmetric model inputs: no model can move a quote aggressively without passing the same gate.

### v1.2 — Pre-match crowd removal + source-bound discipline
- Platform crowd removed from pre-match pipeline because it is not visible before match start.
- Crowd retained only for post-start/post-match RBP and benchmarking.
- Added source-bound aggressiveness and data sufficiency rules.

### v1.1 — Data sufficiency + source-bound rule
- Added targeted research requirement for incomplete/stale/generic data.
- Added rule that source convergence confirms direction, not necessarily extremity.

### v1.0 — Operational pipeline
- Formalized v5 baseline, market-first approach, lineup/news checks, player structural checklist, StatsBomb secondary check, Claude cross-check and final audit.

---

## 1. Core principle

The final probability is not a direct average of models. It is a structured, audited forecast:

```text
Final probability =
market / sportsbook prior when liquid
+ v5 internal baseline
+ event-rate and player-rate modules
+ lineup/news/role correction
+ referee correction where relevant
+ tactical/match-script correction
+ coherence check across related questions
+ small-sample guard
+ Claude/other-model red-team check
+ final audit
```

Main hierarchy:

```text
v5 baseline commands the internal process.
Sportsbook/sharp market is the anchor for liquid props.
FootyStats / StatFootball / player aggregates feed v5.
Lineup/news/role can override generic aggregates.
StatsBomb is a secondary tactical-pattern check.
Claude is a data scout and red-team, not an automatic quote mover.
Platform crowd is never a pre-match input.
```

---

## 2. Source hierarchy

1. **Official lineup / official team news**  
   Highest authority for player props, role/minutes and tactical shape.

2. **Sportsbook / sharp market**  
   Strongest prior for liquid events: match winner, totals, BTTS, sometimes corners/cards.

3. **v5 internal model**  
   Team strength, expected script, event priors, player roles, tactical assumptions.

4. **Player/team aggregates**  
   FootyStats, StatFootball, FotMob, club-season player SOT/90, fouls/90, cards/90, corners, offsides.

5. **Match-specific news**  
   Injuries, tactical quotes, referee, weather, motivation, rotation.

6. **StatsBomb/event-level history**  
   Useful for tactical checks and historical event rates; secondary, not automatic.

7. **Claude / other model**  
   Red-team, missing-data finder, overconfidence detector.

8. **Platform crowd**  
   Post-start/post-match only.

---

## 3. Standard workflow for a new match

### Step 1 — Classify all 10 questions
Each prop must be assigned a type:

```text
market-driven
match-script
SOT / shots volume
corners
fouls
cards
offside
penalty/red-card high variance
player SOT
player score/assist
```

### Step 2 — Build v5 baseline
Use market priors, team strength, expected game state, event-rate priors, player roles, and known lineup/news.

### Step 3 — Market-first for liquid props
For match winner, totals and BTTS, devig market odds when available and use as strong prior. Move away only with specific evidence.

### Step 4 — Data collection and missing-information scan
Before any aggressive quote, ask:

```text
Do we have official/predicted lineups?
Do we know the player role?
Do we have market odds?
Do we have player/team event rates?
Do we have enough comparable data?
Is this based on one weird match?
```

### Step 5 — Run type-specific modules
Apply player checklist, SOT module, offside prudence, cards/referee module, fouls/corners module.

### Step 6 — Run global coherence and small-sample gates
Mandatory for **all** question types.

### Step 7 — Claude/red-team cross-check
Ask for missing data, overfitting risk, divergences >10 points, bottom-up disagreement, coherence violations.

### Step 8 — Final audit before submission
No sheet is final until the audit is passed.

---

## 4. Global rule A — Cross-Question Coherence Check

This applies to **every match and every question set**, not only SOT.

A probability sheet is a joint object. The 10 probabilities must tell one coherent story. If one number implies a match script that contradicts another number, stop and investigate.

### 4.1 Examples of coherence checks

```text
High favorite win probability + very low team volume: possible, but requires low-event control script.
High team SOT threshold + low both-teams-SOT probability: check implied lambdas.
High underdog 2H goal probability + very low underdog 2H SOT probability: inconsistent unless goal type is special.
High 4+ cards + low team fouls/cards profiles + lenient referee: likely overpricing.
High team more corners + very low possession/territory: needs transition/cross/set-piece explanation.
High player SOT + low team SOT: only possible if player is a dominant shot-taker.
High offside 2+ + low attacking depth/directness: needs specific runner/high-line evidence.
```

### 4.2 Operational checklist

Before submission, write a short coherence note:

```text
1. What is the expected match script?
2. Which team controls territory?
3. Which team chases in 2H?
4. Which numbers imply high volume?
5. Which numbers imply low volume?
6. Are player props compatible with team props?
7. Are SOT/corners/fouls/cards mutually coherent?
8. Which quote is the most extreme and why?
```

### 4.3 Rule

```text
If one question looks mathematically or narratively incompatible with the rest of the sheet, it is not automatically wrong, but it becomes mandatory-review.
```

---

## 5. Global rule B — Small-Sample Guard

This applies to **all** question types.

Do not make aggressive decisions from very little data. A single match can be informative, but it must not become the baseline unless supported by other evidence.

### 5.1 Small-sample warning signs

```text
Only one previous tournament match.
Only one opponent-specific example.
A historically extreme stat, e.g. 1 foul in a match.
A player role inferred from one lineup.
A tactical claim based on one result.
A rate from non-comparable opponent strength.
A sample from club context transferred directly to national-team context.
```

### 5.2 Correct use of a single match

A single match can be used as:

```text
directional evidence
role evidence
style evidence
warning flag
```

A single match should not be used as:

```text
full lambda
full baseline
sole reason for a >10 point move
sole reason for an aggressive probability
```

### 5.3 Operational rule

```text
If a probability move >8–10 points is based mainly on one match, stop.
Need at least one of:
- bottom-up player/team aggregate confirmation;
- market confirmation;
- official lineup/role news;
- repeated pattern over multiple comparable matches;
- referee/player-specific hard data.
```

---

## 6. Symmetric Hard-Data Gate

This rule applies equally to ChatGPT, Claude, the human analyst, market intuition, and any model output.

No model is allowed to be a quote mover without passing the same gate.

### 6.1 Classify every proposed quote move

```text
Official lineup / role news
Hard player/team data
Market correction
Referee correction
Single-match directional signal
Narrative match-script
Pure intuition
```

### 6.2 Typical move sizes

```text
Official lineup / role news:       8–20 points
Hard player/team data:             8–15 points
Market correction:                 5–15 points
Referee correction:                3–10 points
Single-match directional signal:   3–8 points
Narrative match-script:            2–6 points
Pure intuition:                    0–3 points
```

### 6.3 Rule

```text
If a proposed move is >10 points, it must be supported by hard data, lineup/role news, or market evidence.
Convergence between ChatGPT and Claude is not independent validation if both are using the same narrative.
```

---

## 7. Source-Bound Aggressiveness Rule

If independent sources give a range [a, b], final probability should usually stay within or close to [a, b].

Moving beyond the range is allowed only if there is new match-specific information not captured by the sources.

Examples:

```text
Darwin Núñez benched → player score/assist can be cut sharply.
Uruguay midfield packed → team SOT threshold should be cut.
Ugarte/Bentancur high-foul data → Uruguay more fouls can be boosted.
```

No hard caps. Use data gates.

---

## 8. Player Prop Checklist

Mandatory for every player prop.

```text
1. Starting XI?
2. Expected minutes?
3. Actual role in the current XI?
4. Central or peripheral in attack?
5. Set pieces?
6. Corners/free kicks?
7. Penalties?
8. Captain/top scorer/main creator/main outlet?
9. Shoots from distance?
10. Team attacking volume?
11. Opponent defensive weakness?
12. Bench type if not starting?
```

### 8.1 Unknown is not No
If we do not know whether a player takes set pieces, penalties or is a main outlet, do not automatically treat him as marginal.

### 8.2 Bench-player classification

```text
Type A — Low-impact reserve:       7–12%
Type B — Likely attacking sub:     13–18%
Type C — Star/high-impact sub:     18–25%
```

This applies to score/assist or SOT props depending on role.

Example:

```text
Ben Waine bench profile ≠ Trezeguet bench profile.
Trezeguet can be a high-impact attacking sub; Waine may be a lower-impact reserve if Chris Wood starts.
```

---

## 9. SOT Volume Module v1.3

This is the most important new section.

Post-mortem MD2 showed:

```text
Non-SOT questions: strong positive RBP.
SOT questions: large negative RBP.
```

Therefore, SOT props require extra quantitative rigor.

---

### SOT-1 — Bottom-up gate obbligatorio

For every SOT volume question, estimate two lambdas:

```text
Top-down lambda:
- market/team strength
- prior team SOT rate
- opponent SOT conceded
- expected possession/territory
- match script
- previous match signal, shrunk

Bottom-up lambda:
- sum expected SOT contribution of projected/official starters
- player SOT/90 or SOT/start
- minutes adjustment
- role adjustment
- set-piece/shot-heavy adjustment
- substitution impact where relevant
```

If top-down and bottom-up differ by more than 30%:

```text
Do not submit the aggressive number.
Investigate.
Shrink toward the more conservative estimate unless hard data explains the gap.
```

---

### SOT-2 — Lambda coherence check incrociato

If a sheet contains multiple SOT props, derive explicit lambdas:

```text
Team A total SOT lambda
Team B total SOT lambda
Team A 2H SOT lambda
Team B 2H SOT lambda
Player SOT contributions
```

Then check every SOT question against those lambdas:

```text
P(Team A 6+ total SOT)
P(Both teams 1+ SOT in 2H)
P(Team B 2+ SOT in 2H)
P(Team A more SOT than Team B in 2H)
Player 1+ SOT probability
```

Rule:

```text
If two questions imply incompatible lambdas, the most extreme SOT quote is mandatory-review.
```

---

### SOT-3 — Single-match shrinkage

A single match is signal, not baseline.

Examples:

```text
Uruguay 10 SOT vs Saudi Arabia ≠ Uruguay lambda = 10.
Cape Verde 7 SOT conceded vs Spain ≠ Cape Verde concession lambda = 7.
New Zealand 8 SOT vs Iran ≠ New Zealand 2H SOT dominance baseline.
```

Use MD1 as directional evidence and shrink toward:

```text
player bottom-up rates
team long-run rates
market/team-strength priors
opponent-adjusted expectation
```

---

### SOT-4 — Relative 2H SOT Data Gate, not hard cap

For questions like:

```text
Team A will have more shots on target than Team B in the second half.
```

Do not use hard caps.

Default without bottom-up confirmation:

```text
50 ± 7
```

That means:

```text
43–57 = normal cautious range
58–60 = aggressive but possible
>60 = requires explicit bottom-up confirmation
```

The rule is not:

```text
Never go above 58.
```

The rule is:

```text
Do not go above 60 unless the bottom-up SOT model confirms it.
```

High numbers are allowed if earned by data.

Example:

```text
Spain more 2H SOT than Saudi Arabia at 83% can be valid if bottom-up, market, territory, and lineup all support Spain dominance.
New Zealand more 2H SOT than Egypt at 63% was not valid because it was mainly narrative + MD1 contrast without bottom-up validation.
```

---

### SOT-5 — Player SOT consistency

Player SOT props must be compatible with team SOT lambdas.

Examples:

```text
If team total SOT lambda is low, only structurally central players should be priced high.
If a player is benched, classify bench type before cutting.
If a player has 27% probability, a hit is variance, not necessarily model error.
```

---

## 10. Offside module

Offside is volatile.

Inputs:

```text
team offside rate
opponent defensive line
runner profile
directness/depth passing
match script
lineup attackers
```

Rules:

```text
Do not overfit one offside-heavy match.
2+ offside probabilities above 55 need strong tactical or rate evidence.
Offside can contain edge, but it must be source-grounded.
```

---

## 11. Fouls and cards module

### Fouls
Inputs:

```text
team fouls committed
team fouls suffered
pressing intensity
defensive game state
midfield ball-winners
opponent dribblers/transitions
referee style
```

### Cards
Cards are not identical to fouls. Check:

```text
foul locations
tactical fouls
player yellow-card rates
referee severity
match stakes
expected chasing/defending script
```

Rule:

```text
Without referee/team/player evidence, avoid aggressive 4+ cards or more-cards positions.
```

---

## 12. Corners module

Inputs:

```text
territory
crossing style
wing attacks
favorite pressure
low block opponent
set-piece tendency
```

Corner props are usually more stable than SOT but still require coherence with territory and match script.

---

## 13. Penalty / red-card module

High variance.

Inputs:

```text
referee penalty/red history
box entries
dribbler vs tackler mismatch
team discipline
VAR/tournament context
```

Rule:

```text
Do not push high without referee + tactical evidence.
Default conservative.
```

---

## 14. Model modules

### 14.1 Market-implied probability model
Convert odds to implied probabilities, approximately remove vig, use as strong prior.

### 14.2 Dixon-Coles / Poisson style goals model
Used for scoreline, win/draw/loss, under/over, BTTS. Market-calibrated rather than purely historical.

### 14.3 Event-rate Poisson / Binomial model
Used for SOT, shots, corners, offsides, fouls, cards thresholds.

For threshold `k+` under Poisson lambda:

```text
P(X >= k) = 1 - exp(-lambda) * sum_{i=0}^{k-1} lambda^i / i!
```

For 1+ event:

```text
P(X >= 1) = 1 - exp(-lambda)
```

### 14.4 Player prop model
Uses:

```text
player rate per 90
starting probability
expected minutes
role
team lambda
set pieces/penalties
opponent profile
bench type
```

### 14.5 RBP / Brier postmortem
Used after match to distinguish calibration from bad luck.

---

## 15. Final audit checklist

Before submitting, answer all:

```text
1. v5 baseline produced?
2. Every prop classified?
3. Market checked for liquid props?
4. Platform crowd excluded pre-match?
5. Lineup/news/injuries checked?
6. Referee checked where relevant?
7. Player Prop Checklist completed?
8. SOT bottom-up gate completed for SOT props?
9. SOT lambda coherence check completed if multiple SOT props?
10. Cross-question coherence check completed for all props?
11. Small-sample guard passed?
12. FootyStats/StatFootball/player rates used correctly?
13. StatsBomb used only as secondary tactical check?
14. Claude/other-model divergence understood?
15. Extreme probabilities justified by hard data?
16. Source-bound rule respected?
17. Data sufficiency respected?
18. Scenario coherence checked?
19. Execution checked before adding new rules?
20. Ready to submit?
```

---

## 16. Claude handoff protocol

When sending a sheet to Claude, ask:

```text
1. Identify divergences >10 points.
2. For each divergence, classify your argument:
   - hard data
   - lineup/role
   - market
   - single-match signal
   - narrative
3. Flag any cross-question incoherence.
4. Flag any small-sample overreaction.
5. For SOT questions, request bottom-up and lambda coherence checks.
6. Do not propose aggressive moves without stating the supporting evidence type.
```

---

## 17. Postmortem update process

After each match:

```text
1. Record our probabilities.
2. Record crowd.
3. Record outcomes.
4. Record RBP/Brier.
5. Separate bad luck from bad model.
6. Identify repeatable reasoning errors.
7. Update watchlist or pipeline only if error is structural.
8. Do not update from one low-probability event unless the reasoning was wrong.
```

---

## 18. Anti-overreaction rule

Do not update the pipeline just because a low-probability event happened.

Example:

```text
Tielemans 1+ SOT at 27% hit.
That is not necessarily wrong: a 27% event should happen about one time in four.
```

Update only when the **reasoning process** was wrong, not when an event hurt.

---

## 19. Current canonical version

```text
Current pipeline: v1.3
Main upgrade over v1.2: SOT rigor + global coherence + small-sample guard.
```
