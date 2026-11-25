# AECO — Heterospecific-mediated mating-site formation

**Status (2026-11-25): exploratory. No demonstrated frog-to-butterfly mating effect.**

## v1.2 — global macroecology of foam reproductive architecture (2026-11-25)

- [Global study design and frozen evidence gates](docs/global_foam_macroecology_v1.2.md)
- [Published 2021 froth/bubble reproductive-mode crosswalk](data/literature/foam_mode_crosswalk_v1.2.csv)
- [Source workbook acquisition and schema audit](scripts/global_foam_traits.py)
- [GitHub Actions acquisition workflow](.github/workflows/global_foam_traits.yml)

Primary scale is now global, with Sado as a possible local validation system. Nunes-de-Almeida et al. (2021) sampled 2,012 anurans and defined modes 44–64 as froth and 65 as bubble. Crosswalk distinguishes potentially exposed versus sheltered and variable placement; exposure is not measured. Publisher directory lists the actual species-level supplementary workbook; web XLSX retrieval unsupported and container DNS failed. No workbook, species count of foam producers, global occurrence panel or raster acquired yet; workflow execution unverified. Global proposal uses 100 km equal-area grid, 50/200 km sensitivity, monthly 2010–2021 panel linked to JRC surface water, frog breeding evidence and Pieridae flight/mating evidence, with independent climate, effort and spatial controls. Co-occurrence and activity overlap are opportunity proxies, not fertilization. Previous macroclimate studies of frog reproductive modes are not novelty; focus on exposed reproductive structures and cross-taxon timing.

## v1.1 — remote-sensing feasibility and Sado nest architecture (2026-11-25)

- [Remote-sensing evidence and design](docs/foam_remote_sensing_v1.1.md)
- [Published five measured fossorial nests](data/literature/sado_foam_dimensions_v1.1.json)
- [Nominal GSD arithmetic](scripts/foam_gsd_benchmark.mjs)
- [Calculated size-versus-resolution results](results/foam_gsd_v1.1.json)
- [Earth Engine exploratory habitat predictor export](scripts/sado_habitat_screen_gee.js)

Miyata et al. (2026) document seven case records of fossorial Z. arboreus nesting on Sado (five measured; one record spans repeated years). The measured short axes are 49–89 mm; at 5 mm GSD four of five span at least ten pixels under full exposure. Satellite and standard aerial imagery are unsuitable for individual nest identification; even close-range optics cannot resolve hidden nests. Satellite products can screen habitat strata; the 2010 Sado egg-mass/forest-cover study and government report already establish a landscape-model precedent. Novelty must concern exposed reproductive architecture and recipient encounters/fertilization. Geometry calculated and checked in JS; no empirical detection accuracy measured. The GEE script requires an authorized project and inland AOI and has not run; direct raster metadata connection failed DNS. No new raw raster/field images or direct butterfly event acquired.

## v1.0 — material accessibility as a reproductive-site gate (2026-11-25)

- [Foam material evidence, physical limits and focused empirical protocol](docs/foam_nest_v1.0.md)
- [Published numerical evidence and missing-parameter ledger](data/literature/foam_material_evidence_v1.0.json)
- [Reproducible numerical benchmark](scripts/foam_material_benchmark.mjs)
- [Calculated results](results/foam_material_benchmark_v1.0.json)
- [Header-only material characterization template](data/templates/foam_material_assay_v1.0.csv)

Shigeri et al. (2021) measured acid-hydrolyzed amino-acid residues of Z. arboreus foam, not accessible free amino acids or sodium. Lee & Lee (2014) directly compared P. rapae with the brush-tipped Polygonia c-aureum: approximate wet-film areal uptake rates 0.239 and 0.454 mm²/s, respectively. Other frog species have measured surface-tension reductions; these do not establish Japanese foam properties or butterfly feeding. A passive capillary illustration explicitly shows why the direction of a surface-tension effect depends on wettability and viscosity. Retain visual landmark, soluble chemistry, physical accessibility and runoff pathways separately. Prioritize matched natural observation and permitted material characterization of confirmed abandoned foam; no active nest manipulation. The primary endpoint remains confirmed fertilization across initially unmated Pieris females. No new target contact, mating, or fertility event verified. Published aggregates were transcribed and arithmetic executed in JavaScript, including sanity checks; the committed Node script was not separately executed. Japanese proteome PDF page screenshot failed to return a verifiable image; table and methods were read in extracted text. No new raw field data or chemical assays acquired.

## v0.9 — stage-dependent use and postdeparture foam legacy (2026-11-25)

- [Focused literature and revised observation protocol](docs/foam_nest_v0.9.md)
- [Published aggregate transcription](data/literature/foam_stage_evidence_v0.9.json)
- [Reproducible arithmetic](scripts/foam_stage_benchmark.mjs)
- [Computed results](results/foam_stage_benchmark_v0.9.json)

Lin et al. (2000) report foam-nest selection by Taiwanese Caiusa coomani females: fresh nests accepted in each of three five-repeat paired assays; a whipped-egg-white mimic elicited hovering in three of five trials but no oviposition. This supports separating approach from substrate acceptance, not a pure visual mechanism or mating/fertilization result. Published embryo mortality among 20 infested nests averaged 92.5% vs 5.3% in 29 uninfested nests (descriptive, not randomized; no stage-specific risk denominators). Toda (2014), p.45, reports Japanese Z. arboreus dry nest residue persisting for 2–3 weeks after larval departure, adding an evidence-based temporal window for residue observations. Prioritize naturally abandoned foam, before/after comparisons, measured visibility and surface wetness, and daylight sampling across the day; never disturb active nests. Arithmetic executed in JavaScript and committed; individual-level data and independently verified butterfly visits remain unavailable. The primary target remains Pieris and confirmed fertilization per initially unmated female, not Caiusa oviposition.

## v0.8 — reported foam-associated insect mating; evidence-gated comparison (2026-11-25)

- [Focused evidence and revised experimental gates](docs/foam_nest_v0.8.md)
- [Source-level visitor event ledger](data/literature/foam_visitor_events_v0.8.csv)
- [Published scorpionfly mating branch counts](data/literature/scorpionfly_mating_branches_v0.8.json)
- [Descriptive calculation script](scripts/scorpionfly_benchmark.py)
- [Recomputed benchmark](results/scorpionfly_benchmark_v0.8.json)

New natural-history sources report a female Episyrphus balteatus licking a dry Zhangixalus arboreus foam nest (June 2023), and both sexes of Panorpa japonica gathering and a copulating pair on a foam nest (June 2024). Same-event media were deduplicated; an independent 2023 blog reports scorpionfly gathering but not mating. These are source descriptions, not independently reviewed footage or controlled evidence of mating-site formation. Published scorpionfly laboratory data describe 27/31 matings in bait-associated branches (40 pairs, no randomized resource or foam contrast). Recipient mating-system dependence is now an explicit hypothesis; retain Pieris as the primary target and Panorpa as a candidate positive comparator, not a substitute. Direct adult Pieridae foam use and confirmed recipient fertilization are still unverified. No original video/individual-level data retrieved; thesis page screenshot failed 429, numeric text and diagram extraction agree. Arithmetic reproduced in JavaScript. No claim of full video verification or Python execution in this update.

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
