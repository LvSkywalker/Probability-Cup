# Historical SOT Gate Backtest

Dataset: StatsBomb key events archive in current project. Rolling pre-match style using previous matches only inside the archive. This is a proxy backtest, not a betting-market backtest.

- Team-match rows: 602
- Synthetic SOT props: 8127
- Modern subset props (date >= 2021): 5886

## Overall

| Sample | N | Brier top-down | Brier gated | Delta Brier | LogLoss top-down | LogLoss gated | Delta LogLoss |

| All | 8127 | 0.2016 | 0.2034 | -0.0018 | 0.5884 | 0.5933 | -0.0050 |

| Modern >=2021 | 5886 | 0.2006 | 0.2045 | -0.0039 | 0.5857 | 0.5959 | -0.0102 |


Positive delta means gated model improved.


## By prop type — all

| prop                   |   n |   brier_top |   brier_gated |   delta |   logloss_top |   logloss_gated |   delta_ll |
|:-----------------------|----:|------------:|--------------:|--------:|--------------:|----------------:|-----------:|
| match_total_sot_12plus | 301 |      0.1623 |        0.1547 |  0.0076 |        0.5065 |          0.4896 |     0.0169 |
| match_total_sot_11plus | 301 |      0.1883 |        0.1816 |  0.0067 |        0.5619 |          0.5478 |     0.0142 |
| match_total_sot_10plus | 301 |      0.2205 |        0.2144 |  0.0062 |        0.6316 |          0.6215 |     0.0101 |
| match_total_sot_9plus  | 301 |      0.2446 |        0.2424 |  0.0023 |        0.6805 |          0.6789 |     0.0016 |
| team_sot_6plus         | 602 |      0.2003 |        0.1989 |  0.0014 |        0.5925 |          0.5921 |     0.0004 |
| team_sot_8plus         | 602 |      0.1048 |        0.1046 |  0.0001 |        0.3607 |          0.3606 |     0.0001 |
| team_sot_7plus         | 602 |      0.1602 |        0.1606 | -0.0003 |        0.5012 |          0.5052 |    -0.0039 |
| team_sot_5plus         | 602 |      0.2388 |        0.2392 | -0.0004 |        0.6726 |          0.6750 |    -0.0023 |
| team_sot_h2_1plus      | 602 |      0.1282 |        0.1304 | -0.0023 |        0.4209 |          0.4285 |    -0.0076 |
| team_more_sot_h2       | 602 |      0.2299 |        0.2330 | -0.0031 |        0.6511 |          0.6581 |    -0.0071 |
| team_sot_4plus         | 602 |      0.2511 |        0.2547 | -0.0036 |        0.6961 |          0.7043 |    -0.0082 |
| team_sot_h2_3plus      | 602 |      0.2326 |        0.2368 | -0.0042 |        0.6597 |          0.6705 |    -0.0108 |
| team_sot_h2_2plus      | 602 |      0.2388 |        0.2431 | -0.0043 |        0.6705 |          0.6793 |    -0.0088 |
| match_total_sot_8plus  | 301 |      0.2532 |        0.2585 | -0.0053 |        0.6982 |          0.7101 |    -0.0119 |
| team_sot_3plus         | 602 |      0.1991 |        0.2054 | -0.0063 |        0.5845 |          0.5986 |    -0.0140 |
| match_total_sot_7plus  | 301 |      0.2237 |        0.2334 | -0.0097 |        0.6368 |          0.6554 |    -0.0185 |
| match_total_sot_6plus  | 301 |      0.1831 |        0.1940 | -0.0109 |        0.5501 |          0.5726 |    -0.0225 |


## By prop type — modern >=2021

| prop                   |   n |   brier_top |   brier_gated |   delta |   logloss_top |   logloss_gated |   delta_ll |
|:-----------------------|----:|------------:|--------------:|--------:|--------------:|----------------:|-----------:|
| match_total_sot_12plus | 218 |      0.1579 |        0.1525 |  0.0054 |        0.4958 |          0.4843 |     0.0115 |
| match_total_sot_10plus | 218 |      0.2181 |        0.2130 |  0.0051 |        0.6281 |          0.6209 |     0.0072 |
| match_total_sot_11plus | 218 |      0.1833 |        0.1795 |  0.0038 |        0.5511 |          0.5437 |     0.0074 |
| match_total_sot_9plus  | 218 |      0.2462 |        0.2445 |  0.0017 |        0.6859 |          0.6859 |     0.0000 |
| team_sot_8plus         | 436 |      0.1018 |        0.1022 | -0.0004 |        0.3484 |          0.3508 |    -0.0024 |
| team_sot_6plus         | 436 |      0.1927 |        0.1941 | -0.0014 |        0.5729 |          0.5802 |    -0.0072 |
| team_sot_7plus         | 436 |      0.1576 |        0.1601 | -0.0026 |        0.4921 |          0.5024 |    -0.0103 |
| team_sot_5plus         | 436 |      0.2315 |        0.2343 | -0.0028 |        0.6568 |          0.6644 |    -0.0076 |
| team_sot_h2_1plus      | 436 |      0.1351 |        0.1388 | -0.0037 |        0.4384 |          0.4509 |    -0.0125 |
| team_more_sot_h2       | 436 |      0.2263 |        0.2307 | -0.0044 |        0.6429 |          0.6532 |    -0.0102 |
| team_sot_4plus         | 436 |      0.2471 |        0.2531 | -0.0060 |        0.6873 |          0.7009 |    -0.0136 |
| team_sot_h2_2plus      | 436 |      0.2394 |        0.2455 | -0.0061 |        0.6713 |          0.6838 |    -0.0125 |
| team_sot_h2_3plus      | 436 |      0.2316 |        0.2382 | -0.0065 |        0.6572 |          0.6740 |    -0.0168 |
| match_total_sot_8plus  | 218 |      0.2563 |        0.2639 | -0.0076 |        0.7060 |          0.7229 |    -0.0169 |
| team_sot_3plus         | 436 |      0.2030 |        0.2113 | -0.0084 |        0.5939 |          0.6127 |    -0.0188 |
| match_total_sot_6plus  | 218 |      0.1916 |        0.2060 | -0.0144 |        0.5723 |          0.6023 |    -0.0300 |
| match_total_sot_7plus  | 218 |      0.2304 |        0.2452 | -0.0149 |        0.6532 |          0.6835 |    -0.0303 |


## Notes

- The top-down model is a rolling team-for/opponent-against SOT model.

- The gated model adds starter bottom-up SOT rates from previous starts, divergence review shrinkage, and context multiplier cap.

- Because StatsBomb has only tournament matches, player bottom-up is sparse. This makes the test conservative/noisy.
