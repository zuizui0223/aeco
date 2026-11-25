# AECO — Heterospecific-mediated mating-site formation

**Status (2026-11-25): exploratory. No demonstrated frog-to-butterfly mating effect.**

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
