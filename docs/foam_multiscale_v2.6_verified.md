# AECO V2.6 — multiscale camera-space diagnostic (2026-11-26 JST)

Reuses the 36 photo IDs and 12 species of V2.5. No additional images or independent observations. Both source ZIPs and every individual photo hash checked against the V2.5 masks and receipts. V2.5 input result.json SHA256 4d89a94ebc9802599e5986a6828f7c2f5071e8042e37efd1b4bfedd2c460c687. Raw image sources and licenses remain in the original manifests; no images redistributed in this branch.

## Method
Convert sRGB to linear RGB, then blur the full image by Gaussian kernel (reflect edges, truncate at 3 sigma). Set FWHM/partial target ROI equivalent diameter to 0, 0.125, 0.25, 0.5, 1, 2. Equivalent diameter = 2 sqrt(mask area/pi), not physical width. Retain original masks for target and three contexts (manual, near ring, whole non-ROI); contexts may include actual target or other objects. Recompute median luminance contrast C, median RGB proportion max-minus-min, pixel rank AUC and target luminance IQR. Average photos within species, then weight species equally. At zero blur, 324 C/chroma/AUC checks reproduce prior values to tolerance 1e-10. All 648 photo-by-scale-by-context rows generated. Coarser scales mix pixels across objects; not an optical acuity or distance simulation.

## Results
Manual context, species-balanced C:
| FWHM/ROI diameter | Foam | White flower | Pale fungus | Colored flower | Colored fungus | Nonfoam eggs |
|---:|---:|---:|---:|---:|---:|---:|
|0|.7070|.7123|.7375|.2811|.6226|.1037|
|.125|.6674|.5885|.6925|.1966|.6079|.0919|
|.25|.6331|.5490|.6483|.1674|.5837|.1039|
|.5|.5430|.4778|.5649|.1421|.5002|.0823|
|1|.3304|.2946|.3592|.1082|.3580|.0429|
|2|.0855|.0937|.0969|.0576|.1606|.0166|

At .5, foam retains about 77% of original C; white flower 67%, pale fungus 77%. Foam RGB spread is .0823 at zero and .0765 at .5; colored flowers .4515 to .3609. Equal-weight Euclidean distances from foam group centroid in (C, RGB spread) space: closest group is white flower in 9/18 scale-context conditions and pale fungus in 9/18. Excluding the five previously flagged context-sensitive photos gives 6 and 12. Leave one species out (exclude removal of sole colored fungus species) gives 198 repeated scale-context-species cases; white flower nearest in 118, pale fungus in 80; both closer than all other references in all 198 cases. These counts are repeated diagnostics, not independent biological replicates or p-values. Arbitrary centroid metric, not animal perception or formal equivalence. Same pattern does not establish mimicry, attraction, functional convergence or reproduction.

## Replay
1. Obtain historical V2.4 artifact 15093723498 (run 45771230665) and V2.5 artifact 15095728860 (run 45776020474). Exact ZIP SHA256 in results/foam_multiscale_v2.6_summary.json.
2. Use the original V2.5 local result.json or regenerate an equivalent row-level record with scripts/foam_cross_structure_compare_v2_5.py and the committed V2.4/V2.5 masks.
3. Run python scripts/foam_multiscale_v2_6.py result.json old.zip new.zip --out v26
4. Run python scripts/foam_multiscale_loso_v2_6.py v26/summary.json
Local execution completed, including the leave-one-species-out calculation separately on the generated summary. GitHub replay not separately run. Local output SHA256 receipts saved in the compact summary. No CI claim.

## Interpretation and next gate
The selected foam/white-flower/pale-fungus photographs retain comparable bright low-RGB-spread profiles over moderate image blur, while strong blur erases much of the luminance contrast. The result supports a descriptive camera-space shared-appearance hypothesis, not a floral-specific signal. Shape cannot be measured from partial interior masks. Photographic framing, flash, background, taxa, selection and within-species dependence remain confounded. No calibrated 300–700 nm reflectance, UV, physical size, angular distance, species-specific acuity or measured behavior. Next distinguish visual detection from category recognition with actual reflectance, documented scale, background-controlled stimuli and receptor/acuity models; behavior remains a separate empirical gate. For macro-scale analysis, expand balanced lineages and include nonreproductive pale structures rather than multiplying repeated image conditions.
