# AECO v2.0 — reported breeding calendars and genus-composition diagnostic (2026-11-26 JST)

## Source and execution
Forti et al. (2022), DOI 10.1111/ddi.13610, Table S2 (https://doi.org/10.5281/zenodo.6811407), CC BY 4.0, checksum matches the v1.9 source. The article reports 80 publications, 760 species-location breeding reports and 4039 species-location-month data points. Methods section 2.2 confirms that months are months with evidence of breeding; no observation-effort or negative-month denominator is supplied in the workbook. PDF screenshot retrieval failed (cache miss); methods were read in the extracted text. Source trait workbook pinned to the v1.3 SHA256. [CI run](https://github.com/zuizui0223/aeco/actions/runs/45657627552), job 139358477967 completed successfully; [artifact](https://github.com/zuizui0223/aeco/actions/runs/45657627552/artifacts/15042962788) ZIP SHA256 f90cc63e4b7fba6aa06664d92767c6c84dd96c1c157c88847e1cee45cab6aec6 independently verified. All five available study-balanced contrasts and their signs reproduced locally from the 92 aggregate contrast rows. Raw workbook processed in CI; no independent local row-level reread. [Verified JSON](../results/forti_calendar_v2.0_verified_summary.json). Draft PR #6 stacked on #5; not merged.

## Data audit
760 rows, 251 checked names (427 original name strings), 79 normalized citation strings (do not equate this mechanically with independent publications), 4039 recorded one-month flags, matching the paper's total. 752 complete binary rows, of which 4 all-zero rows; 8 incomplete rows; 5 exact-calendar duplicate rows excluded, leaving 743. Exact source name and family match: 468/760 rows before quality exclusions; 459/743 retained. Four name-matched rows fail family check. Exact normalized municipality available in 735 source rows; the simple decimal-coordinate parser yielded zero valid pairs, so no coordinate-level comparison or location-specific climate adjustment was possible. Source links are not used as unique study IDs because both many links per citation and multiple citations per link occur. Full month coverage per survey is not verified; unreported months are not confirmed biological absence.

## Species-balanced descriptive summary
| Original exposure class | Rows | Species | Mean reported months | Mean R |
|---|---:|---:|---:|---:|
| Potentially exposed | 55 | 13 | 4.5264 | .6992 |
| Sheltered | 47 | 12 | 4.4826 | .7213 |
| Strict exposed (no ground) | 52 | 10 | 4.7843 | .6995 |
| Mixed | 13 | 3 | 5.3429 | .6092 |
| Variable | 8 | 2 | 6.6667 | .4974 |
| No documented foam/bubble | 336 | 88 | 6.1423 | .5278 |

Strict exposed overlaps the original exposed class, not an independent group. Record means computed within species before averaging equally across species. The variable and mixed groups are especially sparse. No pooled group difference is phylogenetically or climate-adjusted.

## Paired contrasts (exposed minus sheltered)
All E and S matched records in this literature subset belong to Leptodactylidae. Average distinct calendars per species within a study/unit, species equally weighted by class, then weight studies equally. Primary same citation + municipality. Reported-month contrast, not true reproductive season duration.

| Analysis | Studies | E/S species | Delta months | Descriptive bootstrap 95% interval | Positive/negative/zero |
|---|---:|---:|---:|---|---|
| Same study and municipality | 25 | 11/12 | +0.3780 | [-0.3600, 1.1347] | 14/10/1 |
| Exclude ground from E | 24 | 9/12 | +0.4424 | [-0.3194, 1.2160] | 14/9/1 |
| Same study only | 26 | 11/12 | +0.3635 | [-0.3609, 1.0904] | 14/10/2 |
| Same study, municipality and genus | 11 | 2/6 | -1.2727 | [-2.4091, 0] | 2/8/1 |
| >=2 species each per study/municipality | 6 | 9/9 | +0.3750 | [-0.6111, 1.3611] | 4/2/0 |

Within-genus comparison only contains Leptodactylus: E L. latrans, L. macrosternum; S six species. The prespecified descriptive-support threshold requires >=10 studies AND >=5 species per group, so the within-genus comparison fails the species gate. Repeated species/shared sites and sampling designs limit bootstrap independence; intervals descriptive only. Leave-one-study-out ranges: primary +0.2410 to +0.5188; strict +0.3022 to +0.5920; within-genus -1.7000 to -0.9500.

### Post-outcome composition diagnostic
The 11 studies with a within-genus contrast also have the pooled-genera municipality contrast. Restricting the latter to exactly those same study IDs yields +0.098485 months (7/11 positive), while within-genus yields -1.272727 months (2/11 positive). Pooled minus within mean +1.371212, positive in 6 studies, tied in 5, negative in none. Remaining 14 studies in primary pooled analysis: +0.597619 months. Thus study selection alone does not account for the sign reversal. Changing which genera/species enter the contrast also changes it; not an identified causal decomposition. No claim of a genus-adjusted general negative effect. A publication/municipality may pool ponds or years.

## Decision
The hypothesis that exposed-foam species breed for longer is not robustly supported. A weak pooled positive contrast persists after excluding ground, but intervals span zero and the within-genus contrast reverses under very sparse exposure-species support. The result is useful as a falsification of a simple duration assumption, not proof of equivalence or absence of heterospecific effects. Do not feed a positive trait-specific duration multiplier into the butterfly model. Preserve the previous v1.8 primary nonreplication and v1.9 proxy-quality limitation. Next prioritize repairing source coordinate formats transparently and obtaining genuinely comparable exposed/sheltered within-lineage reproductive calendars or actual nest persistence data. No new climate or butterfly analysis, no direct nest area, actual lifetime, mating or fertilization estimate.
