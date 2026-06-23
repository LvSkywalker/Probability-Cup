# Count Model Backtest — Poisson vs NB vs COM-Poisson vs Weibull Count vs Bivariate NB

## Scope

- Matches parsed: **301**

- Prediction rows: **39150**

- Backtest starts after **80 prior team-match observations**.

- Data: StatsBomb event archive available in project. SOT = Goal, Saved, Saved To Post.

- This is a **proxy rolling backtest** on synthetic SOT props, not a direct SportsPredict contest replay.


## Overall results

| model        |    n |   brier |   logloss |   avg_p |   event_rate |
|:-------------|-----:|--------:|----------:|--------:|-------------:|
| NegBin       | 7830 |  0.2030 |    0.5926 |  0.5128 |       0.5001 |
| BivarNB      | 7830 |  0.2032 |    0.5930 |  0.5092 |       0.5001 |
| COM-Poisson  | 7830 |  0.2038 |    0.5944 |  0.5185 |       0.5001 |
| Poisson      | 7830 |  0.2057 |    0.6020 |  0.5381 |       0.5001 |
| WeibullCount | 7830 |  0.2065 |    0.6072 |  0.5267 |       0.5001 |


## Brier by prop family

| prop_family    |   BivarNB |   COM-Poisson |   NegBin |   Poisson |   WeibullCount |
|:---------------|----------:|--------------:|---------:|----------:|---------------:|
| both_1plus_2h  |    0.2132 |        0.2144 |   0.2130 |    0.2224 |         0.2236 |
| match_total    |    0.2061 |        0.2069 |   0.2060 |    0.2092 |         0.2100 |
| relative_2h    |    0.2308 |        0.2340 |   0.2306 |    0.2294 |         0.2299 |
| relative_total |    0.2337 |        0.2331 |   0.2335 |    0.2311 |         0.2315 |
| team_2h        |    0.1994 |        0.2006 |   0.1992 |    0.2017 |         0.1999 |
| team_total     |    0.1929 |        0.1928 |   0.1927 |    0.1961 |         0.1981 |


## Main takeaways

- **both_1plus_2h**: best proxy model = **NegBin** (Brier 0.2130).

- **match_total**: best proxy model = **NegBin** (Brier 0.2060).

- **relative_2h**: best proxy model = **Poisson** (Brier 0.2294).

- **relative_total**: best proxy model = **Poisson** (Brier 0.2311).

- **team_2h**: best proxy model = **NegBin** (Brier 0.1992).

- **team_total**: best proxy model = **NegBin** (Brier 0.1927).


## Interpretation

- Negative Binomial remains a strong production baseline for static SOT counts.

- Bivariate NB is most useful for joint/relative props; this simple shared-tempo implementation often helps there but needs better calibration.

- Weibull Count is a plausible temporal candidate, but the current global-shape renewal proxy is not enough to declare it superior for 2H props. It needs score-state/timestamp calibration.

- COM-Poisson is useful as a dispersion diagnostic, but this fixed-nu proxy does not clearly beat NB. A fully fitted hierarchical COM-Poisson may perform differently.

- Poisson is kept as a baseline only; it can be competitive on some low thresholds but is not safe for aggressive tails.


## Production recommendation

Keep current production as **Negative Binomial + conditional SOT gate + lambda coherence checks**. Treat Weibull Count, COM-Poisson and Bivariate NB as research modules until they win cleanly on rolling backtests for their target prop family.


## Limitations

- No market odds, no club-season player bottom-up data, no official lineups in this proxy run.

- COM-Poisson uses a rough fixed dispersion parameter from rolling empirical dispersion.

- Weibull Count uses global shape = 1.12 and renewal simulation; no game-state conditioning yet.

- Bivariate NB uses a simple shared Gamma tempo factor.
