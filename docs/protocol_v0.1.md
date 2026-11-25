# AECO v0.1 — frozen pilot protocol (2026-11-25)

## Estimands

Primary direct endpoint: newly initiated copulations per monitored site-hour, not the number of photographs of an already mating pair. Secondary: unique receptive female arrivals/site-hour; male arrivals/site-hour; courtships/site-hour; mating conditional on an encounter. Record flights entering and leaving a standardized patch and its buffer. An increased mating rate within a patch is not necessarily an increase in landscape-wide mating success.

Mechanism chain: randomized cue treatment -> male arrivals -> female arrivals/encounters -> locally initiated copulations. Measure nutrient uptake separately; do not condition on post-treatment male abundance when estimating the total treatment effect. Female avoidance is an explicitly competing hypothesis.

## Stage 0: evidence and source audit

- Recompute published bait-visitor male fraction from Beck 1999: 760/761 pooled across taxa and two locations. Descriptive only; no independent-observation CI or frog effect.
- Public iNaturalist audit: 2015-01-01 through 2025-12-31, wild verifiable observations, Pieridae and Pieris. Candidate streams: mating project, reproductive behavior project, exact observation field values, text searches for mating, puddling and frog/toad. Treat all as retrieval proxies.
- Validate field filters against returned observation-field IDs/values, check taxonomic ancestry, de-duplicate by observation ID, report truncation and query failures. A zero is meaningful only for a successful query and never proves biological absence.
- Pilot sample is capped and ordered deterministically; report query-reported totals separately from validated samples. Candidate sources can overlap; never sum totals.
- Manually adjudicate candidates independently for copulation, courtship, feeding, puddling, roosting, substrate, direct frog evidence, initiation vs already coupled, and confidence. Missing/unannotated is unknown.
- If no direct frog-associated mating record is obtained, retain hypothesis as untested; do not substitute ordinary co-occurrence.

## Stage 1: exploratory association

Only after obtaining adequate reviewed mating events and reviewed nonmating adult controls with usable date and accuracy: match same species and observer-day or observer/season/location blocks. Estimate association with independently recorded frog detections in prespecified distance and time windows; report sensitivity to spatial scale, observer effort and background habitat. A detection is a proxy, absence is not inferred from non-detection. Adjust for water proximity, solar radiation, temperature, host and nectar resources, land cover and accessibility if measured. Place-time blocking; leave-region-out replication. No causal claim.

## Stage 2: causal field experiment

Randomized within-site crossover of damp control, frog-derived noninvasive cue, ion-matched control, and non-frog vertebrate cue. Balance order and weather; washout and separate stations to prevent spillover. Predator presence/cues only in a separate permitted noninvasive experiment. Keep moisture, light, host plants, nectar and patch size comparable. Count unique visitors, sex, courtship and newly initiated copulations with standard video effort and blinded adjudication. Site/block is independent unit. Conduct pilot to estimate variance and determine replication before confirmatory data collection; no assumed power.

Interpretation gates:
- More males alone: resource aggregation only.
- More females and encounters: potential encounter-site mechanism.
- More locally initiated copulations than wet and generic vertebrate controls: evidence of frog-specific local mating-site formation, subject to design.
- Landscape total mating requires monitoring background and displacement.
- Fewer females or no increase in copulations: support avoidance or lack of facilitation; report uncertainty, no forced positive interpretation.

## Data governance

Only openly accessible source metadata and aggregate outputs in public repo. Do not upload exact locations, raw photos, usernames or unrestricted descriptions. Use appropriate permissions and biosecurity for all field materials. Review table is local/private. No claiming systematic literature completeness or confirmed ecological effects from synthetic fixtures.
