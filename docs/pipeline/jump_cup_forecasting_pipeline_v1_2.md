# Jump Cup Forecasting Pipeline — v1.2

**Status:** operational  
**Last update:** 2026-06-21  
**Purpose:** reduce overconfidence, pattern overfitting, and execution risk in Jump Cup / SportsPredict probability submissions.

---

## Changelog

### v1.2 — Pre-Match Crowd Removal
- Removed **Platform Crowd** from the pre-match operational pipeline because it is not visible before match start.
- Kept crowd only as a **post-start / post-match evaluation benchmark**, not as a pre-submission input.
- Updated market check, final submission table, execution checklist, and one-line summary accordingly.

### v1.1 — Data Sufficiency + Source-Bound Rule
- Added **Data Sufficiency Rule**: if data is incomplete, stale, or too generic, perform targeted research before finalizing aggressive/player-specific probabilities.
- Added **Source-Bound Aggressiveness Rule**: convergence across sources confirms direction, but normally should not push the final probability beyond the most extreme independent source unless new match-specific information exists.
- Added final checklist items: data quality/specificity check and source-bound check.

### v1.0 — Operational Pipeline
- Formalized v5 baseline, market/crowd distinction, lineup/news checks, player structural checklist, StatsBomb secondary tactical check, Claude cross-check, and final execution checklist.
- Added explicit anti-Bacuna rule: low team volume is not enough to price a player SOT very low unless set pieces/status/main-outlet role are actively excluded.

---

# 1. Core Principle

Final probability should be built as:

```text
Final probability =
v5 baseline
+ sportsbook market correction
+ lineup/news correction
+ player structural-status correction
+ StatsBomb tactical-pattern adjustment
+ Claude / cross-check sanity check
+ controlled aggressiveness
```

Main hierarchy:

```text
v5 commands.
FootyStats feeds v5.
Sportsbook estimates true probability for liquid props.
Lineup/news and structural player role decide player props.
StatsBomb checks tactical patterns only after v5.
Claude checks overconfidence and alternative theses.
Platform crowd is used only after it becomes visible / post-match as an evaluation benchmark.
```

---

# 2. Build v5 Baseline

Start from v5 before secondary pattern checks.

v5 uses team strength, match script, expected possession/territory, shots and shots on target, corners, fouls, cards, offsides, player role and usage, game-state logic, FootyStats / StatFootball aggregates, and market priors where relevant.

FootyStats / StatFootball is not a late brake. It feeds the v5 baseline.

Useful FootyStats / StatFootball inputs:

```text
team shots
team shots on target
team corners
team fouls
team cards
team offsides
player shots
player shots on target
player minutes / usage
team attacking and defensive tendencies
```

Output:

```text
v5 baseline probabilities
```

---

# 3. Classify Every Prop

## A. Market-driven props

Examples:

```text
match winner
3+ goals
over/under
BTTS
team scores
team total goals
```

Sportsbook market is the main external anchor for true probability.

## B. Match-script props

Examples:

```text
team more fouls
team more SOT in second half
team corners
team second-half scoring
territorial dominance props
low-possession team props
```

This is where edge often lives.

## C. Player props

Examples:

```text
Kubo 1+ SOT
Bacuna 1+ SOT
Gakpo 1+ SOT
Skhiri 1+ SOT
Gyokeres 1+ SOT
```

Player props require a structural player check. Generic position is not enough.

## D. High-variance event props

Examples:

```text
penalty OR red card
red card
penalty awarded
4+ cards
team more cards
```

Need referee + match context before aggressive movement.

## E. Offside props

Examples:

```text
team 2+ offsides
opponent caught offside 2+ times
```

Offside can contain edge, but is volatile. Small samples should not dominate.

---

# 4. Market Check

Before the match starts, platform crowd is not visible. Therefore, it is not part of the pre-match decision pipeline.

## A. Sportsbook market

Used to estimate true probability.

Check when available:

```text
1X2
over/under
BTTS
team totals
handicap
corner markets
card markets
```

Rule:

```text
Sportsbook = true-probability anchor for liquid props.
```

## B. Platform crowd

Platform crowd is not visible pre-match, so it cannot be used for pre-submission positioning.

It is used only:

```text
after the match starts, if visible
after the match, for RBP/post-mortem evaluation
```

Rule:

```text
No pre-match probability should depend on crowd if crowd is not visible.
Crowd is an evaluation benchmark, not a pre-match data input.
```

---

# 5. Lineup, News, Injuries, Referee

Before submission, check:

```text
starting XI
absences
suspensions
formation
actual role
expected minutes
referee
motivation/table context
rotation risk
```

Especially important for player props, cards, penalty/red, SOT, corners, and second-half props.

---

# 6. Mandatory Player Prop Checklist

No player prop can be finalized without this checklist.

```text
PLAYER PROP CHECKLIST

Player:
Team:
Prop:

1. Starting XI?
Yes / No / Unknown

2. Expected minutes?
90 / 70-80 / sub risk / unknown

3. Actual role?
Striker / winger / attacking midfielder / CM / DM / fullback / defender / unknown

4. Set pieces?
Corners: Yes / No / Unknown
Free kicks: Yes / No / Unknown
Penalties: Yes / No / Unknown

5. Structural status?
Captain: Yes / No / Unknown
Top scorer / main scorer: Yes / No / Unknown
Primary creator: Yes / No / Unknown
Primary attacking outlet: Yes / No / Unknown
Shoots from distance: Yes / No / Unknown

6. Team attacking volume?
High / medium / low

7. Does structural status override team volume?
Yes / No / Unknown

8. Final player-prop probability:
```

Core rule:

```text
Unknown is not No.
```

To price a player SOT very low, we need:

```text
low team volume
+ generic/non-attacking player role
+ no set pieces
+ no captain/main outlet status
+ no meaningful shot history
```

Failure case:

```text
Bacuna = midfielder in weak low-volume team -> 15%
```

Correct logic:

```text
Bacuna = captain + set pieces + primary outlet + scorer profile
-> cannot be treated as 1/11 of team attacking volume
```

---

# 7. StatsBomb Tactical-Pattern Check

StatsBomb is secondary to v5/FootyStats.

Use it for team/match tactical mechanisms, not player props.

Good uses:

```text
low-possession team commits more fouls?
territorial dominance creates corner pressure?
high line causes opponent offsides?
dominated team struggles to produce 2H SOT?
```

Indicative adjustments:

```text
small sample: ±3-5 points
medium pattern: ±5-7 points
robust pattern: ±8-10 points
```

If StatsBomb conflicts with v5/FootyStats:

```text
v5/FootyStats wins by default
```

unless StatsBomb has large sample, clear mechanism, and strong consistency.

---

# 8. Claude / External Cross-Check

Claude is used to detect alternative theses, ignored market sources, lineup/injury issues, overconfidence, and incoherent narratives.

If Claude diverges, ask:

```text
Why does it diverge?
```

Possible bases:

```text
market-based
lineup-based
injury-based
tactical
statistical
narrative
```

Market/lineup/news-based divergence gets more weight than pure narrative divergence.

---

# 9. Internal Scenario Coherence

Before submitting, ask:

```text
Do the probabilities imply a coherent football scenario?
Or are we combining incompatible claims?
```

Extreme quotes must be explicitly justified.

---

# 10. Controlled Aggressiveness

We avoid hard “never” rules. Instead:

```text
Higher extremity requires stronger evidence.
```

## Favorite win very high

Requires very high sportsbook, no finishing/rotation concerns, and strong mismatch.

## Offside 2+ high

Requires high v5 baseline, supporting FootyStats, vertical lineup, opponent high line, and no major sportsbook/market brake.

## Player SOT very low

Requires low team volume, player not structurally central, no set pieces, no captain/main outlet status, and no shot profile.

## Cards / penalty / red

Requires strict referee, nervous match, foul-prone teams, stakes/duels/transitions.

---

# 11. Addendum — Source-Bound Aggressiveness Rule

When multiple independent sources point in the same direction, convergence increases confidence in the direction, but it does not automatically justify moving beyond the most aggressive individual source.

Rule:

```text
If v5, FootyStats, StatsBomb, Claude, sportsbook, and/or other visible sources all point in the same direction, the final probability should normally remain within the range implied by those sources.
```

The final probability should not exceed the most extreme independent source on the same side unless there is new match-specific information not already included in those sources.

Valid new match-specific information:

```text
confirmed starting XI changes
key injury/news
unexpected tactical setup
player role change
set-piece responsibility confirmed
referee assignment
weather/pitch condition
must-win or rotation context
```

Insufficient reasons to exceed the source range:

```text
several sources agree in the same direction
a generic historical pattern confirms the idea
a small-sample StatsBomb pattern supports the thesis
Claude and v5 are directionally aligned
the narrative feels coherent
```

Interpretation:

```text
Convergence confirms direction.
It does not automatically license extra extremity.
```

Failure case:

```text
Germany–Ivory Coast offside props.

Several sources agreed that offside risk was elevated, but final probabilities moved beyond the strongest individual estimate. Convergence was treated as permission to become more extreme, instead of confirmation inside a bounded range.
```

---

# 12. Addendum — Data Sufficiency Rule

If available data for a prop is incomplete, stale, generic, or not specific enough, perform targeted web research before finalizing the probability.

This is mandatory especially for player props, lineup-dependent props, referee/cards props, penalty/red props, aggressive or contrarian quotes, any probability far from sportsbook/available anchors, and any quote based on a thin narrative.

Rule:

```text
If data quality is weak, do not compensate with confidence.
Research first, then price.
```

For player props:

```text
Generic role + team volume is not sufficient if structural status is unknown.
Unknown is not No.
```

---

# 13. Final Submission Table

Before submission, each prop should have:

```text
final probability
category
main reason
risk
sportsbook/available anchor
anchor gap
confidence
```

Recommended format:

```text
Q1:
Probability:
Category:
Main reason:
Anchor:
Gap:
Risk:
Confidence:
```

---

# 14. Final Execution Checklist

Before submission, answer explicitly.

```text
FINAL EXECUTION CHECKLIST

1. v5 baseline produced?
Yes / No

2. Every prop classified?
Yes / No

3. Sportsbook market checked for liquid props?
Yes / No / Not available

4. Platform crowd excluded from pre-match inputs unless actually visible?
Yes / No

5. Lineup, news, and injuries checked?
Yes / No

6. Referee checked for cards/penalty/red?
Yes / No / Not relevant

7. Player Prop Checklist completed for every player prop?
Yes / No / No player props

8. FootyStats used inside v5, not as late overreaction?
Yes / No

9. StatsBomb, if used, treated as secondary pattern check?
Yes / No / Not used

10. Claude/cross-check divergences understood?
Yes / No / Not available

11. Extreme probabilities justified explicitly?
Yes / No / No extreme probabilities

12. Source-Bound Aggressiveness Rule respected?
Yes / No

13. Data Sufficiency Rule respected?
Yes / No

14. Sheet implies a coherent football scenario?
Yes / No

15. Did we check execution before adding new rules?
Yes / No

16. Ready to submit?
Yes / No
```

If an important answer is “No”, do not submit yet.

---

# 15. Post-Mortem After Every Match

Record:

```text
our probability
crowd probability
outcome
RBP
Brier score
category
reason for hit/miss
```

Main post-mortem question:

```text
Did we follow the pipeline?
```

Only after that:

```text
Do we need a new rule?
```

Most failures should first be treated as execution failures, not missing-rule failures.

---

# One-Line Summary

```text
v5 builds the baseline.
FootyStats feeds v5.
Sportsbook estimates truth.
Crowd is used only as post-start/post-match evaluation benchmark.
Lineup and structural player role decide player props.
StatsBomb checks tactical patterns only after v5.
Claude checks overconfidence.
Aggression requires convergence but stays source-bound unless new match-specific evidence exists.
Every submission ends with an execution checklist.
```
