# Call For Review: Goal4949 RayJoin Hot-Path Remeasure

Date: 2026-07-04

Please review:

- `history/internal_docs/goal4949_rayjoin_hot_path_remeasure_2026-07-04.md`
- `history/internal_docs/goal4949_rayjoin_hot_path_remeasure_artifact_2026-07-04.json`

## Context

Goal4947 and Goal4948 proved the generic device-column row-buffer -> Numba continuation connector on both RayJoin LSI pair columns and a non-RayJoin ray/triangle hit stream.

Claude's prior review correctly warned that the next measurement must use a real RayJoin hot-path continuation, not demo operators such as equality masks or segmented counts.

Goal4949 therefore reran the RayJoin Section 5.7 public County x Soil sample with:

1. baseline `section57_overlay.py`
2. Numba variant `section57_overlay_numba.py`

Both routes were byte-equal to the author answer.

## Requested Verdict Label

Use one of:

- `approve_goal4949_measurement_current_layer2_helper_not_promoted`
- `approve_with_required_amendments`
- `fail_redo_goal4949`

## Review Questions

1. Did Goal4949 use a real RayJoin Section 5.7 public-sample workload rather than a toy connector probe?
2. Do the artifacts prove both baseline and Numba variant remained byte-equal to the author answer?
3. Is the conclusion correct that the current Numba app-layer helper is not a performance win?
4. Does the phase table justify saying prepared-hot PIP traversal is not the bottleneck on this sample?
5. Does the evidence justify rejecting the current Numba writer path as an optimization candidate?
6. Is it correct that the next Layer 2 target, if continued, must be reprojection/sort rather than demo operators or the current writer wrapper?
7. Is the report careful not to claim broad RayJoin / whole-app / full Section 5.7 speedup?
8. Should Goal4949 close with label `completed_measurement__current_layer2_helper_not_performance_win__next_target_reprojection_sort_or_layer3`?
