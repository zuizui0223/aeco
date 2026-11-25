# AECO v1.4 — global range panel, verified (2026-11-25)

## Verified source provenance and spatial output

- Raw 2021 trait workbook SHA256 `3ec2b6ab0d457cf6bcd4bcbabd7bf51aa2ea3f1ec898d297f1f68a46a883b964`.
- rasterSp `amphibians_dist.rda`, pinned source ref `8c007900ceb2679f8aee04aec4d936648df5191b`, SHA256 `f197cff80d0de3f9b3b7e524540903db429a549c4dea2d5d462079cfac478f84`. Documentation: https://rdrr.io/github/RS-eco/rasterSp/man/amphibians_dist.html ; IUCN 2017-derived 0.5 degree distribution. Actual object has 797,577 unique valid species-cell rows, 6,393 amphibian species, 52,710 native grid cells. Data version older than the 2021 trait taxonomy; derived range maps, not abundance or direct occurrences. No raw range redistribution in the repository.
- Verified first run https://github.com/zuizui0223/aeco/actions/runs/45583806934 (frog-range job 139100156586); second run https://github.com/zuizui0223/aeco/actions/runs/45583960209 (frog-range job 139100687268) exactly reproduces spatial summaries.
- Spatial artifact https://github.com/zuizui0223/aeco/actions/runs/45583960209/artifacts/15006794984 includes pooled 100 km and 200 km cells and summary; artifact availability may expire.

## Exact name coverage

| Class | Source | Mapped | Unmatched |
|---|---:|---:|---:|
| Potentially exposed froth | 187 | 148 | 39 |
| Sheltered froth | 33 | 31 | 2 |
| Variable froth | 26 | 25 | 1 |
| Mixed froth | 7 | 7 | 0 |
| Bubble only | 2 | 2 | 0 |
| No documented froth or bubble | 1755 | 1485 | 270 |
| Total | 2010 | 1698 | 312 |

211/253 strict froth mapped, 145,826 matched native species-cell rows. Exposed-only exact match fraction 79.1%, sheltered-only 93.9%; differential missingness is a limitation, not a biological result. Synonyms not filled silently; no absent-species imputation. Treat taxonomy updates separately.

## Equal-area gridding

EPSG:6933, native 0.5-degree cell centers assigned to fixed projected squares. Not exact polygon rasterization, not true occupancy probabilities, and not a complete world land grid. Counts restricted to trait-matched species; the 100/200 km outcomes are repeated summaries of the same data.

| Quantity | 100 km | 200 km |
|---|---:|---:|
| Cells with known-trait species | 8900 | 2587 |
| Any strict froth | 4718 | 1395 |
| Potentially exposed-only species present | 4473 | 1341 |
| Sheltered-only species present | 1650 | 457 |
| Both classes present | 1510 | 436 |
| Max strict-froth richness | 17 | 18 |
| Max exposed-only richness | 12 | 14 |
| Max sheltered-only richness | 9 | 9 |

1510/1650 = 91.52% of sheltered-class cells also have exposed-class species; 436/457 = 95.40% at 200 km. These are overlap of mapped potential traits, not observed co-nesting or actual accessible foam surface. Overlap motivates compositional comparisons rather than exposed-presence versus absence. Within-family exposed/sheltered species counts: Leptodactylidae 38/17, Microhylidae 16/13, Rhacophoridae 91/1, Limnodynastidae 3/0. Strong taxonomic imbalance cautions against pooled exposure effects. No direct causal inference.

## Recipient and rainfall sources

Pinkert et al. country-level butterfly checklist (DOI 10.48600/mol-1sr2-nh14; https://doi.org/10.1111/geb.13475) acquired: 87,506 rows, SHA256 ed34ad7991e8a4e8cef0c337a2c8aa88b3b6d0863e13ce1d7dbf57a85a06ee32. Actual columns geomid, scientificname, iso3, verbatimscientificname, source. No family column or grid-level coordinates; cannot create Pieridae gridded richness directly. Source artifact https://github.com/zuizui0223/aeco/actions/runs/45583806934/artifacts/15006878491. Daru 10,372 species range archive (https://doi.org/10.5061/dryad.bzkh189h9) range request failed HTTP 403; no individual grids downloaded. Do not inflate country presence into local occupancy.

NOAA GPCP v2.3 monthly 2.5 degree, https://psl.noaa.gov/thredds/catalog/Datasets/gpcp/catalog.html, DOI 10.7289/V56971M6: source acquired with SHA256 f82d867432102665f9203ba01ef367c68463a37b81c23917f940dd1d8ccb8027. First two runs failed on time decoding/epoch format. Latest code corrects the non-zero-padded epoch and checks all 144 months for 2010–2021. Do not claim climate results without the successful outcome; subsequent verification will be recorded separately.

## Next analysis gate
Use recipient species/family taxonomy and georeferenced observations or range polygons; define effort and spatial blocks, never use butterfly country checklists as 100 km occupancy. Range overlap is only potential exposure, not breeding phenology, mating or fertility. For environmental analysis, retain native GPCP resolution and distinguish range-climate descriptions from a new trait-evolution result. No claim of a frog-mediated reproductive effect.
