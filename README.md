# AECO — Heterospecific-mediated mating-site formation

**Status (2026-11-25): exploratory. No demonstrated frog-to-butterfly mating effect.**

## v0.7 — foam as a fertilization environment; field observation gate (2026-11-25)

- [Focused evidence review and noninvasive pilot protocol](docs/foam_nest_v0.7.md)
- [Published aggregate and zero-detection calculations](scripts/foam_exposure.py)
- [Calculated results](results/foam_exposure_v0.7.json)
- [Header-only observation data template](data/templates/foam_observation_v0.7.csv)

Muto & Kubota (2009) directly investigated sperm locomotion in the viscous foam-nest fertilization environment of Zhangixalus arboreus. This supports the provider-side concept; the proposed butterfly encounter effect remains untested. Byrne et al. (2026) found an association between male participation and nest volume in the African Chiromantis xerampelina, not a transferable Japanese estimate. The 134-nest summary is recalculated, with a discrepancy between reported failure count and printed percentage explicitly retained. Raw workbook download returned 403 and container DNS failure. Forest-edge Pieris melete is the priority candidate alongside P. rapae, based on published habitat and seasonal ranges, not verified co-use of nests. The next gate is standardized matched noninvasive filming of naturally formed nests and controls, with validated detection and clustered sampling. No direct adult Pieridae foam contact, mating, or fertilization evidence obtained. The local calculation script ran and its arithmetic was independently reproduced; the template contains no observations.

## v0.6 — foam nests as reproductive architecture (2026-11-25)

- [Foam-nest literature and gated field/experimental protocol](docs/foam_nest_v0.6.md)
- [Published placement and nest-date table transcription](data/literature/foam_nest_placement_tables_v0.6.json)
- [Descriptive benchmark script](scripts/foam_nest_benchmark.py)
- [Recalculated frog-nest results](results/foam_nest_benchmark_v0.6.json)

The focal provider is now the frog foam nest, particularly Zhangixalus arboreus, not generic frog presence or carrion. Natural records show 17/132 ground nests (2019: 15/65; 2020: 2/67). A separate experimental table gives a median 13 days between discovery and the reported hatching/collapse monitoring endpoint (9 nests; not post-abandonment persistence). Compare visual/UV landmark, measured chemical resource, age-dependent cue, social attraction and diversion/risk mechanisms. Do not assume foam is a female-wing mimic or that proteins imply attraction. Prioritize noninvasive matched observations and inert visual/chemistry controls; the final endpoint remains confirmed fertilization across initially unmated females. No direct foam-to-Pieridae link demonstrated and no raw Figshare or verified new butterfly data acquired. No active nest manipulation is proposed.

## v0.5 — direct resource-use evidence and published aggregate benchmark (2026-11-25)

- [Evidence interpretation and revised field priority](docs/frog_link_v0.5.md)
- [Source-level frog/butterfly interaction ledger](data/literature/frog_interaction_events_v0.5.csv)
- [Boggs & Dau 2004 table transcription](data/literature/boggs_dau_2004_tables.json)
- [Descriptive benchmark code](scripts/substrate_benchmark.py)
- [Recalculated aggregate results](results/substrate_benchmark_v0.5.json)

Downes (1973) documented six butterfly species from a frog carcass and qualitatively increased visits after vertebrate carrion additions to puddles. The named frog-carcass consumers were Lycaenidae and Nymphalidae, not Pieridae. Two further photographic sources record frog-carcass use by Nymphalidae. These are not systematic prevalence data. Boggs & Dau (2004) documented both sexes of the Colorado Pieris taxon at mud and carnivore dung; table weights imply 7/74 female visitors. Feeding fractions among observed butterflies were 66/79 on salt versus 4/36 on pooled other substrates. These are descriptive published aggregates, not frog treatment effects or direct mating/fertilization data. The female visitor sex ratio is not the fraction of the female population using a patch. Prioritize observation of naturally occurring frog-associated substrates; retain non-pierid comparator taxa and require direct Pieridae use before causal mating experiments. PDF screenshot verification failed; text and table transcriptions were cross-checked. No raw field dataset or verified workflow output acquired in v0.5.

## v0.4 — frog-generated reproductive patches (2026-11-25)

- [Frog-specific evidence audit, mechanism gates, and field protocol](docs/frog_link_v0.4.md)
- [Competing-risk model](scripts/frog_competing_risk.py)
- [35 illustrative scenarios](results/frog_competing_risk_v0.4.csv)

Prioritize direct adult Pieridae contact with frog-generated substrates: naturally spent foam nests (especially Zhangixalus arboreus), excretion-conditioned wet margins, and opportunistic carrion observations. The literature supports frog-mediated nutrient heterogeneity and some adult butterfly predation; it does not demonstrate that frog substrates attract Pieridae or facilitate their mating or fertilization. Frog reproductive construction is a candidate temporally persistent cue, not a proven mechanism. The model distinguishes a hypothetical persistent cue from contemporaneous loss risk, with no empirical parameter calibration. No new raw data acquired; the amphibian Dryad DOI is identified but failed to resolve through the current access route. v0.4 is a targeted evidence review and model extension, not a completed empirical validation.

## v0.3 — coverage thresholds and female mobility (2026-11-25)

- [Theory, literature constraints, and empirical gate](docs/fertilization_v0.3.md)
- [Exact two-state model](scripts/fertilization_thresholds.py)
- [100 calculated scenarios](results/fertilization_thresholds_v0.3.csv)
- [Conditional hatch benchmark acquisition and schema audit](scripts/benchmark_pieris.py)
- [GitHub Actions benchmark](.github/workflows/fertility_benchmark.yml)

The cumulative first-mating hazard must be distributed among females, not just increased in total. Under constant postmating success and no remating, heterogeneity in cumulative hazard lowers coverage at fixed mean (Jensen inequality). Female switching reduces the simulated hotspot occupancy threshold. This is conditional theory, not evidence for frogs. Dryad raw file access remains blocked locally; the added workflow has not been verified as completed. The benchmark measures hatch among postcopulatory records only.

## v0.2 — fertilization-centered extension (2026-11-25)

The primary biological question is now **heterospecific-mediated fertilization opportunity**, not just mating-site formation. Track the proportion of initially unmated females producing at least one confirmed fertilized egg within a fixed horizon. Copulation, insemination, fertilization and hatch are distinct endpoints. The v0.1 observational audit remains useful for upstream mechanism discovery only.

- [Fertilization protocol and evidence](docs/fertilization_v0.2.md)
- [Analytic toy model](scripts/encounter_model.py)
- [Calculated theoretical scenarios](results/encounter_scenarios.json)

The model predicts that male aggregation with uniform receptive female distribution leaves the total expected encounter rate unchanged under local linear mixing, but lowers first-mating coverage under saturation. Even higher total encounters can coexist with lower realized fertilization coverage. These are conditional mathematical predictions, not frog or butterfly field results. Open Pieris napi thermal reproduction data are identified (Dryad DOI 10.5061/dryad.dfn2z35cj), but raw files were not retrieved through the current web route (403). No new empirical fertility effect is claimed.

## Question

Can frogs or frog-derived resources organize where pierid butterflies encounter potential mates, independently of changing their physiological reproductive capacity?

Primary model: Pieridae (especially Pieris) and Anura. A frog-specific effect is a stronger claim than general attraction to wet soil or vertebrate-derived material. Spatial encounter effects are distinct from sodium effects on courtship vigor or spermatophore quality.

## Competing hypotheses

- H1 resource: frog-derived material attracts butterflies to a site.
- H2 social: initial male aggregation recruits further conspecific males.
- H3 encounter: receptive female arrival and locally initiated courtship/copulation increase; apparent local enrichment may instead reflect displacement from elsewhere.
- H4 avoidance: females avoid male crowding or frogs, so male aggregation does not increase, or reduces, mating.
- H0 shared habitat: moisture, illumination, host plants, nectar, season and observer effort account for co-occurrence.
- H5 indirect: frogs alter the distribution of prey or predators rather than acting as a direct cue.

## First evidence audit

Beck et al. (1999, Oecologia, doi:10.1007/s004420050770) reported 227 and 534 butterflies attracted to baits in two Bornean communities. All except one were male (760/761 overall, 99.87%; multiple families pooled). Their decoy experiments supported visual attraction in Pieridae and Papilionidae. This is NOT a Pieris-specific sex ratio or frog experiment.

Lamie et al. (2025, doi:10.1093/aesa/saaf007) explicitly propose testing whether puddling aggregations attract females like a lek, and discuss female avoidance. The untested link is a heterospecific causal contribution to the site and encounter process, not the concept of puddling as a potential mating site.

Hirota & Obara (2000, doi:10.2108/zsj.17.323; doi:10.2108/zsj.17.1081) document time allocation and thermal constraints on mate searching in Japanese Pieris rapae crucivora. Hirota et al. (2001, doi:10.2108/zsj.18.475) document effects of female post-emergence behavior.

## Validation sequence

1. Audit behavioral-record availability. Confirm copulation, puddling and substrate by independent review of descriptions and imagery; retain unknowns.
2. Match candidate mating records to reviewed nonmating activities of the same species, observer, date/season and habitat. Unannotated is not nonmating. Frog detections are proxies only, and non-detection is not absence.
3. Randomized blocked field trials of wet substrate, frog-derived cue, mineral-matched cue, non-frog vertebrate cue, and an independent predator-presence treatment. Use noninvasive materials, appropriate permits and biosecurity; no wildlife translocation.
4. Measure female arrivals and locally initiated copulations per effort, male arrivals, courtships, unique individuals, departure, and background encounter rates. Independent site/block is the replication unit.

The public repo is for protocols, code, aggregate output and source links. Do not publish precise locations, images, or unlicensed observation text. No co-occurrence, candidate label, or synthetic test is evidence of a causal mating-site effect.
