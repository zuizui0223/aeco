# AECO v1.7 — completed observation-support census (2026-11-25)

All nine jobs of run https://github.com/zuizui0223/aeco/actions/runs/45599848032 succeeded. Final artifact https://github.com/zuizui0223/aeco/actions/runs/45599848032/artifacts/15015695860 SHA256 3cc7ae47c8b2b6ece1afeb17ee6be0160eeba10ca37fc4104e69027887469717. Verified all four coverage shards, both annual shards, and the final ZIP locally; reproduced 408 keys and previous-sample flags, total counts, and annual common-year support. [Machine-readable result](../results/global_foam_coverage_v1.7_verified_summary.json). [Pre-outcome taxonomy/placement audit](foam_coverage_v1.7_preoutcome_audit.md). Draft PR #3 remains stacked on unmerged PR #2.

| Coverage | All | Previously sampled | New |
|---|---:|---:|---:|
| Candidate cells | 408 | 53 | 355 |
| Both API queries succeeded | 408 | 53 | 355 |
| Taxonomy below 80% | 12 | 6 | 6 |
| Taxonomy passed but any group <30 dated hits | 365 | 41 | 324 |
| All four groups >=30 + taxonomy | 31 | 6 | 25 |
| All four groups >=72 (necessary annual condition) | 9 | 0 | 9 |
| >=6 common years, each group >=12 dated hits/year | 0 | 0 | 0 |
| >=6 common years, each group >=24 dated hits/year | 0 | 0 | 0 |

Month range 1,12 and years 2010–2021. Search hits: E 16,274, S 7,639, Pieridae 10,949, other butterflies 155,002. Counts are not unique events or biological activity. The 12 Madagascar cells have no accepted E keys: source-taxonomy coverage failure, not observed absence; zero sums in their empty E mappings are arithmetic placeholders excluded by taxonomy gate. Annual queries for all nine candidates succeeded and matched total counts. Common-year counts with >=12 hits per group/year: 0 years (3 cells), 1 year (3), 2 years (2), 3 years (1). Maximum 3 years. The 20-cell/5-block threshold is already impossible at annual candidate stage (9 cells/4 blocks) and the annual test has no qualifying cells. No monthly phases queried in v1.7; no climate-anomaly or temporal effect fit. This is failure of observation support, not a negative effect estimate.

The 25 previously unsampled cells passing total support in five South American blocks have been frozen in [pooled-month candidate JSON](../results/global_foam_coverage_v1.7_frozen_pooled_month_candidates.json) before querying their monthly profiles. Block allocation 4,2,2,13,4. This is a targeted diagnostic of v1.6 pooled-month pattern, chosen after annual support failed but not from new phase outcomes. All 25 must be retained, no cherry-picking; verify index counts, >=2 nonzero months and temporal support in each group, compare identical statistic D(+1)-D(-1) with block-balanced estimates and leave-one-block-out sensitivity; do not relax gate after seeing direction. Shared blocks and climate/effort confounding preclude independent continental replication or causal claims. Original provisional mode classes retained; conservative no-ground/uncertain Microhylidae sensitivity separate. No new direct mating or fertilization evidence.

## Independent reproductive-activity source identified
Forti et al. (2022), Diversity and Distributions, https://doi.org/10.1111/ddi.13610, manually categorized Brazilian iNaturalist evidence (8,478 all observations; Fig.3 reports 546 vocalization, 119 amplexus, 24 eggs/nests, 43 tadpoles; behavior categories may overlap). Published data https://doi.org/10.5281/zenodo.6811407, TableS2.xlsx (repository MD5 1da34c8eda2252cfb2bb12a4e9055555), CC BY 4.0. Workbook download attempted, failed in current container; not yet acquired or inspected. It could validate the relationship between ordinary observations and actual reproductive behavior in the region, not independent of iNaturalist/GBIF, not a paired butterfly mating dataset. Preserve IDs/source provenance and aggregate outputs only; do not redistribute sensitive coordinates. Do not infer actual foam from eggs/nests categories. 
