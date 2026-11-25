# AECO v1.8 — verified pooled-month replication, 26 November 2026 JST

All four jobs of [run 45643302160](https://github.com/zuizui0223/aeco/actions/runs/45643302160) succeeded after correcting a floating-point equality assertion in the synthetic pre-outcome test. [Final artifact](https://github.com/zuizui0223/aeco/actions/runs/45643302160/artifacts/15034899366), SHA256 a94a670b44b0eb6dc99a4b2998dc099d619456fa0f7e21b54a0f77851345ecf7. All three shard archive digests independently matched API metadata; final archive and members verified; recomputed primary and sensitivity means independently from monthly counts using overlap = 1 - L1 distance / 2. [Verified machine-readable result](../results/global_foam_replication_v1.8_verified_summary.json). PR #4 remains draft, stacked, unmerged.

## Frozen design
All 25 previously unsampled, coverage-qualified 200 km cells from v1.7 retained, 5 South American blocks. Exact taxon keys from the v1.7 artifact; 19 E keys and 16 S keys, all prior five-cell E/S keys contained in new sample. No cell overlap, three shared geographic blocks. Same 2010–2021 month-resolved GBIF human observations, original provisional exposure classification. 25/25 cells retrieved, expected dated-hit counts and monthly butterfly partition all match; no attrition. E 11357, S 3680, Pieridae 3963, other five butterfly families 53929. Counts are search hits, not unique events. D(lag)=overlap(E,P)-overlap(E,B)-overlap(S,P)+overlap(S,B), moving frog curves by lag. Primary D(+1)-D(-1), equal block weights, exploratory support gate >=20 cells and >=5 blocks.

## Results
| Outcome | Cells / blocks | Block-balanced mean | Positive blocks |
|---|---:|---:|---:|
| v1.6 exploratory discovery | 5 / 3 | +0.051384 | 3/3 |
| v1.8 primary | 25 / 5 | +0.002330 | 3/5 |
| >=50 records each sensitivity | 16 / 5 | +0.021150 | 5/5 |
| <=80% dominant frog species sensitivity | 10 / 2 | -0.063326 | 1/2 |
| >=2 observed species per frog group | 19 / 3 | -0.001190 | 1/3 |
| Secondary D0 | 25 / 5 | -0.015138 | 0/5 |
| Secondary D(+1) | 25 / 5 | +0.014323 | 4/5 |
| Secondary D(-1) | 25 / 5 | +0.011993 | 4/5 |
| Secondary D(+1)-D0 | 25 / 5 | +0.029461 | 5/5 |

Primary cell-balanced mean -0.002750; descriptive block bootstrap interval [-0.014611,+0.018645]. Leave-one-block-out [-0.004023,+0.009834], changes sign. Exact sign-flip diagnostic two-sided p=.8125, one-sided .40625, conditional on independent symmetric block effects (not assured); 5 blocks imply only 32 sign patterns. The original +.0514 is not reproduced in magnitude. Secondary plus-one versus zero is positive in all blocks; reverse-lag also positive. Higher-count subset is positive in every block but has only 16 cells, and species-dominance restrictions do not sustain positive direction. The all-positive five-block diagnostic has two-sided p=.0625, not a confirmatory result. No directional hypothesis support; do not infer no biological effect. No post-outcome thresholds promoted. No annual, climate/observer effort or species-level correction; pooled months, provisional placement classes, shared taxa and geography. No direct foam exposure, mating or fertility observations.

## Next gate
Prioritize direct reproductive-behavior source (Forti et al. dataset identified in v1.7), compare actual frog breeding evidence to ordinary observation profiles, and audit species-level foam placement before further cross-taxon analysis. Avoid additional threshold searches or a causal interpretation of month-shift symmetry. Retain conditional secondary patterns as candidates only.
