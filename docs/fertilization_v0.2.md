# AECO v0.2 — Heterospecific-mediated fertilization opportunity
Date: 2026-11-25. Exploratory; supersedes the primary endpoint of v0.1 for a future confirmatory experiment. No frog-specific effect has been demonstrated.

## Question
Can an organism spatially organize successful within-species reproduction in another animal by creating a predictable mate-encounter site? In Pieridae, mating is an upstream mediator, not equivalent to fertilization. Frogs are a candidate provider, not an established facilitator.

## Reproductive transitions and endpoints
Track known initially unmated females from entry/eclosion over a fixed observation horizon. Include unmated females, females laying zero eggs, and deaths in the assigned-treatment denominator; record loss to follow-up separately, never convert unknown to zero. Distinguish:
1. Arrival and encounter with a compatible male.
2. Copulation initiation and completion.
3. Insemination: eupyrene sperm in the spermatheca (not just a spermatophore); terminal validation on a separate randomized subset if necessary.
4. Egg fertilization: validate an assay for paternal genetic contribution or appropriate sperm/zygote evidence on a subset, with virgin controls and known fertile controls. Early cleavage alone and egg darkening are imperfect proxies.
5. Egg hatch and larval survival: postfertilization outcomes, not direct measurements of fertilization.

Primary biological estimand: proportion of initially unmated females with at least one demonstrably fertilized egg within a fixed horizon, including zeros. Secondary: count of fertilized eggs per assigned female and fraction fertilized among laid eggs; hatching as a separately labeled endpoint. If direct assay not feasible, explicitly change target to realized viable offspring, not fertilization. Do not infer fertilization from photographs, genital contact, or sperm storage alone.

## Competing causal routes
- Spatial facilitation: randomized cue -> male and receptive female spatial overlap -> encounter -> completed mating -> fertilization. Strongest prediction under mate scarcity. Test female attraction/avoidance and landscape-level displacement.
- Physiological facilitation: cue ingestion -> sperm condition/ejaculate allocation -> fertilization conditional on mating. Separate exposure and forced/standardized pairing experiment; not the same mechanism as encounter.
- Predation and harassment: fewer receptive females, interrupted copulations, or mortality -> lower realized fertilization.
- Shared habitat and thermal effects: moisture, temperature, host plants and time affect both site use and fertility.

Use randomized independently replicated enclosed landscape arrays to compare cue locations versus dispersed controls at low and high mate densities; block on developmental temperature and sex ratio, equalize host, nectar, and water resources. Compare wet control, frog-derived cue, generic vertebrate cue, and chemically matched cue. Do not introduce or translocate wild frogs; use appropriate noninvasive materials and permissions. Separate cue intake and spatial layout in a factorial design where feasible; otherwise do not claim a pure spatial mechanism. Track individuals throughout whole array and count locally initiated and completed matings. Stage 1 public observations are feasibility/association only.

## Theory
For K equal patches, male and receptive-female fractions m_i and f_i, random local mixing, equal encounter coefficient and fixed total densities, relative encounters E/E_uniform = K sum_i(m_i f_i). If females remain uniform, male aggregation alone changes no total encounters. Female attraction to the same male-rich patch raises encounters; avoidance lowers them. This idealized result is not a guarantee under movement, search saturation, harassment, unequal patch sizes or heterogeneous encounter rates. See scripts/encounter_model.py and results/encounter_scenarios.json (analytic/synthetic only).

With a finite observation horizon and a first-completed-mating-only approximation, the probability of at least one fertilized egg for a female remaining at patch i is q_i[1-exp(-lambda_i T)], where lambda_i is completed-mating hazard and q_i is conditional probability of confirmed fertilization within the horizon (assuming no time dependence or delays in the simplified model). Weighted by female fractions. Do not multiply a landscape-average hazard and fertility probability under heterogeneity; use patch-specific outcomes. Remating, sperm storage and egg timing require an expanded state-transition model.

## Prior work / independent measurement benchmark
- Watanabe, Wiklund & Bon'no 1998, Entomological Science 1:15–19: in Pieris rapae sperm transfer was concentrated near the end of copulation; incomplete copulation is not reliable evidence of insemination. https://dl.ndl.go.jp/view/prepareDownload?contentNo=1&itemId=info%3Andljp%2Fpid%2F10656061
- Tschudi-Rein & Benz 1990, https://doi.org/10.1093/aesa/83.6.1158 : postcopulatory sperm transport in P. brassicae.
- Wedell 1999, https://doi.org/10.1046/j.1365-2435.1999.00286.x : mating history and allocation of the two sperm morphs in P. rapae.
- Pembury Smith et al. 2025, https://doi.org/10.1111/1365-2656.70026 : male developmental heat stress did not detectably reduce mating success but authors reported 39.2% lower egg production and 97.7% lower hatch-based fertility. Fertilizing sperm production/transfer was disrupted. Not a frog study.
- Open data: https://doi.org/10.5061/dryad.dfn2z35cj (egg_larvae_counts.csv, sperm_counts.csv, copulation_duration_mate.csv and others); README schema verified, download through current web route returned 403; raw data not acquired/analyzed.
- Landmarking and strong Allee thresholds, https://doi.org/10.1007/s12080-015-0254-z : prior theory linking shared landmarks to mate finding and Allee effects. AECO must distinguish heterospecific construction of a landmark and actual fertilization from established general aggregation theory.
- Välimäki & Kaitala 2006, https://doi.org/10.1111/j.2006.0030-1299.14947.x : no direct support for lack of mating opportunities explaining variation in monandry in P. napi; do not assume natural populations are mate limited.

## Decision gates
Male accumulation alone: no evidence for reproductive facilitation. More local copulations alone: no evidence of fertilization gain. More eggs hatching per assigned female: viable-offspring endpoint, not proof of altered fertilization rate. Direct fertilization gain across an entire randomized array versus generic and wet controls: evidence for facilitation under those conditions. Frog-specific and spatial claims require their respective controls. No evidence of an effect is not proof of absence; report uncertainty and design limits.
