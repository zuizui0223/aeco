# AECO v1.5 — global butterfly pilot, verified (2026-11-25)

## Actual data, not a fertility surface
The two independent grid samples were stratified before querying GBIF. Six diurnal butterfly families, 2010–2021 HUMAN_OBSERVATION, PRESENT, coordinates and no reported geospatial issue. Species facets and family facets were reconciled, and global Pieridae species keys resolved (702 keys, 7,702,156 search hits). No point records or observer identities redistributed. Counts are live API snapshots, not unique ecological events. The 100 and 200 km samples overlap geographically; do not sum hits as unique. No direct foam contact or mating/fertilization data.

| Outcome | 100 km | 200 km |
|---|---:|---:|
| Eligible frog-frame cells | 8,900 | 2,587 |
| Actual queried cells | 160 | 145 |
| Successful retrievals | 160 | 145 |
| All butterfly hits | 86,695 | 265,745 |
| Species-resolved hits | 82,925 | 254,646 |
| Pieridae hits | 13,388 | 35,874 |
| Zero butterfly hits | 44 | 22 |
| Positive hits but fewer than 50 identified | 75 | 52 |
| >=50 identified hits | 41 | 71 |
| Excluded at overall 95% species-resolution gate | 14 | 34 |
| Excluded at additional Pieridae 95% gate | 1 | 3 |
| Eligible rarefaction to 50 | 26 | 34 |
| Eligible rarefaction to 100 | 20 | 30 |
| Eligible rarefaction (50), sheltered-present stratum | 2 | 4 |

Primary response (fraction of expected species richness after rarefying identified records to 50) is below the predefined minimum of 40 cells at both scales. This is insufficient support, NOT a negative primary test. Do not lower gates after seeing results; preserve exploratory sensitivity separately. The absolute count of butterfly hits hides strongly uneven coverage. At 100 km only two eligible southern extratropical cells, and at 200 km six.

## Secondary observation-record share
200 km, n=71 / 34 spatial blocks, includes frog richness, GPCP annual rain and monthly CV, latitude/longitude, sampling hits and native frog-grid support. Per 10 percentage points of trait-known frogs assigned to a foam category (versus reference while holding other fractions constant):
- exposed-only: -0.5205 outcome percentage points (95% CI -1.0617 to +0.0208; p=.0589)
- sheltered-only: +0.8432 (-0.9276 to +2.6139; p=.3397)
- exposed minus sheltered contrast: -1.3637 (-3.2383 to +0.5110; p=.1484).
- other foam: -1.0715 (-2.0002 to -0.1428; nominal p=.0251); secondary, multiple comparisons, sparse support, not evidence of target mechanism.
CI spatial-block held-out MSE worsened 20.95% after adding foam fractions. Local independent fit reproduced coefficients; GroupKFold tie/version differences gave MSE worsening 18.10%, same direction. A local exploratory additional temperature-adjusted model (same 71 cells) gave exposed -0.5310 pp, contrast -1.3574 pp; both CIs include zero; MSE worsened 21.43%. >=5 known-frog-species sensitivity left only 36 (200 km) and 21 (100 km) cells and is below the threshold.

100 km GPCP was acquired incompletely (HDF error; differing file byte count/hash); recipient outputs were preserved. No climate-complete 100 km model. As a comparable *secondary sensitivity*, using temperature and geography/effort without precipitation on both grids: exposed coefficient +0.2822 pp (CI -1.2752 to +1.8396) at 100 km, -0.2840 pp (-1.0403 to +0.4723) at 200 km. Added foam worsened local spatial-CV MSE by 33.56% and 53.96%, respectively. This is not a full climate adjustment or an independent cross-scale replication.

## Verified reproducibility
200 km successful run https://github.com/zuizui0223/aeco/actions/runs/45585235439/job/139105021587 ; artifact https://github.com/zuizui0223/aeco/actions/runs/45585235439/artifacts/15008981974 ; ZIP digest independently matched API. 100 km successful recipient run https://github.com/zuizui0223/aeco/actions/runs/45585783825/job/139106901385 ; artifact https://github.com/zuizui0223/aeco/actions/runs/45585783825/artifacts/15008049514 ; digest independently matched API.
- [200 km JSON with original CI result and local audit](../results/global_butterfly_v1.5_200km_verified.json)
- [100 km JSON with original CI result and local audit](../results/global_butterfly_v1.5_100km_verified.json)

Original local sampling preview reproduced strata counts but not exact CI cells (32/160 and 34/145 overlaps). Different pandas/numpy versions and group-key representation or RNG suspected; exact cause not isolated. Actual CI selections are now frozen as explicit ix/iy lists and checked via compact JSON SHA256. Actual CI blocks 39/43 for 100/200 km. Do not use local preview coordinates as the analyzed sample. First 100 km attempt had NOAA 429, second 200 km attempt hit GitHub metadata API rate limit. Patch decouples occurrence and climate acquisition, pins verified rasterSp commit and hash, and reuses actual CI keys; replay code change not independently rerun here. Result-only commits skipped CI to avoid redundant retrieval. Exact source files remain in verified artifacts; no claim of a new full-grid census.

## Decision
The original hypothesis is not supported by the available secondary macro proxy, and the primary test is unresolved. No direct recipient fertilization evidence. Next prioritize a global observation-support panel before outcome extraction (select cells using total six-family observation coverage only, not Pieridae share), then species-facet acquisition with audited classification and fixed sample keys. For the main biological mechanism, monthly/behavior-specific recipient data or independent standardized mating data are necessary. Do not keep adding climate variables to force a positive static correlation. Archive failures; retain both grains. 
