# AECO V2.2 — nest-level thermal transfer (2026-11-26 JST)

Source: Ichioka & Kajimura (2024), DOI 10.1002/ece3.10926; CC BY 4.0 Figshare file 41534736, DOI 10.6084/m9.figshare.23667387.v1. Raw SHA256 f15f470e06a05ddd0de4ac1954e16517741463951a2b0eb6657a2ef8c8b77176. Original study already established nighttime insulation and hatching differences. All ten experimental nests originally arboreal, five moved to ground. Internal sensor ~5 cm deep, air sensor ~10 cm above nest.

Successful run https://github.com/zuizui0223/aeco/actions/runs/45719017207, job 139572321436, source commit 71276fb3d5aa21be904897ec7f3f385559d7caa3. Artifact https://github.com/zuizui0223/aeco/actions/runs/45719017207/artifacts/15071725666. ZIP SHA256 a3b14f673f9e72319a4f50a09fc1aa211e7041b3323ae0de9278f406858b30e0 independently verified. Recomputed nest-weighted contrasts, daily contrasts, held-out MSE and egg denominators from aggregate CSVs locally; not a separate raw-data reread. Initial run 45718941067 failed because of Unicode sheet prefix, fixed before successful run.

| Indicator | Tree | Ground |
|---|---:|---:|
| Paired temperature records | 1929 | 1964 |
| Nests | 5 | 5 |
| All-time mean Tin−Tout (C), equal nests | -0.38834 | +0.23679 |
| Night 18–06 clock (C) | +0.11961 | +0.83914 |
| Day 06–18 clock (C) | -0.98450 | -0.40024 |
| Within-nest descriptive Tin~Tout slope | 0.71375 | 0.61719 |
| SD ratio adjacent 15-min increments | 0.62401 | 0.43770 |
| Complete nest-days | 14 | 13 |
| Full-day min(Tin)−min(Tout) (C) | +0.20929 | +1.17733 |
| Full-day max(Tin)−max(Tout) (C) | -2.49571 | -1.38267 |
| Outside-minus-inside daily range (C) | 2.705 | 2.560 |

Complete days require >=80/96 slots and >=16/24 per fixed six-hour sector (27/57 nest-days, 4 tree and 5 ground nests represented). Simultaneous comparison: 1581 timestamps, 20 calendar days, 18 positive days, mean ground-minus-tree offset +0.58654 C with equal day weighting. Common ambient bins 14–16,16–18,18–20,20–22,22–24 C all have positive ground-minus-tree offset, +1.0357,+1.3956,+0.5179,+0.5348,+0.2036 C. Different nest ages, dates and habitat conditions remain; descriptive only.

## Leave-one-nest-out temperature calibration
Fit same-placement Tin=a+b(Tout−18), weighting training nests equally, evaluate held-out temperatures within training ambient min/max; compare Tin=Tout.

| Group | Test records | Excluded outside support | Baseline RMSE | Model RMSE | MSE gain | Improved nests |
|---|---:|---:|---:|---:|---:|---:|
| Tree | 1701 | 228 | .89537 | .92619 | -7.00% | 3/5 |
| Ground | 1736 | 228 | 1.06010 | 1.00880 | +9.44% | 4/5 |

No universal transfer function. Internal temperature is not surface temperature or surface moisture, and coarse climate grids are not nest-adjacent air. No global application.

## Hatching
Egg and nest sheets reconciled: nine outcome nests, 3597 eggs, dead/live labels. Tree 1256/1801; ground 1706/1796. Equal-nest fractions 67.86% versus 95.03%, +27.17 pp. Excluding tree nest 6 (reported maggots) gives 83.45% versus 95.03%, +11.58 pp. Predation-destroyed tree nest 12 has missing egg count/outcome; excluded, not imputed zero. No egg-level independent inference, thermal mediation, or initial fertilization measurement.

## Decision
The local physical pattern is asymmetric warming/cooling, not greater thermal buffering in every dimension. Local out-of-nest static calibration not consistently predictive; do not transfer coefficients to global SDMs. No no-foam control, postdeparture residue lifetime, external surface wetness/area, direct Pieridae visitation/mating/fertilization. Seek longitudinal surface persistence and weather observations before estimating accessible structure dynamics. Previous V1.8 nonreplication unchanged. Stacked PR #8 unmerged.
