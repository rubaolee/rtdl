# Call For Review: Goal5301 X-HD Non-Graphics Dataset Provenance

Date: 2026-07-09

Please strictly review Goal5301.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5301_non_graphics_dataset_provenance_matrix_2026-07-09.json
tests/goal5301_xhd_non_graphics_dataset_provenance_test.py
history/internal_docs/goal5301_xhd_non_graphics_dataset_provenance_result_2026-07-09.md
```

Relevant prior evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_dataset_provenance_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5297_dataset_acquisition_manifest_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5288_figure5_timing_denominator_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5295_figures7_8_10_pod_dataset_availability_2026-07-09.json
```

## Scope

Goal5301 is a provenance/status goal, not a performance or implementation goal.

It should answer whether the non-graphics X-HD full-paper inputs are ready for execution, and what the next concrete target should be.

## Expected Findings To Check

1. Exact paper input status still requires file/hash provenance or deterministic author-script regeneration, not just count/Gini/statistical matching.
2. BraTS is correctly classified as registration/license gated and absent from local/POD assets.
3. Census/TIGER-like public geographic inputs are correctly identified as the highest-priority non-graphics next target, but not yet executable until product/year/layer/WKT conversion are resolved.
4. OSM Lakes/Parks/All Nodes are correctly deferred until snapshot/extract/filter/conversion decisions exist.
5. The current POD is correctly classified as not the blocker, because `/local/storage/shared/HDDatasets` is absent and the issue is dataset provenance/acquisition.
6. The report does not claim full X-HD paper reproduction, exact non-graphics dataset recovery, non-graphics correctness, Figure reproduction, or any performance ratio.
7. `Goal5302_census_tiger_public_source_resolution_plan` is the correct next goal, rather than writing more RTDL route code or running POD comparisons immediately.

## Questions For Reviewer

1. Does the matrix accurately preserve the exact-dataset rule from prior X-HD reviews?
2. Are BraTS, Census/TIGER, and OSM classified with the right blockers and priorities?
3. Is the decision to prioritize Census/TIGER over BraTS/OSM justified by the evidence?
4. Is the decision not to use POD for this goal correct?
5. Does the claim boundary prevent Level-B public reconstructions from being mislabeled as exact-paper input recovery?
6. Are the tests sufficient for a provenance/status goal?
7. Should Goal5301 close with `completed_non_graphics_dataset_provenance_matrix__census_tiger_next`?

## Requested Verdict Label

```text
approve_goal5301_non_graphics_dataset_provenance__census_tiger_next
```
