# Goal1008 Large-Repeat RTX Artifact Intake

Date: 2026-04-26

Goal1008 is an artifact-intake gate for Goal1007 RTX A5000 larger repeats. It can clear the 100 ms timing-floor concern for separate public-wording review, but it does not authorize any public speedup claim.

## Summary

- rows audited: `7`
- timing-floor-cleared rows: `6`
- still-held rows: `1`
- public speedup claims authorized here: `0`
- minimum phase duration for public-wording review: `0.1` s
- status counts: `{'still_below_public_review_timing_floor': 1, 'timing_floor_cleared_for_separate_2ai_public_wording_review': 6}`

## Decisions

| App | Path | Chosen artifact | RTX phase (s) | Goal1006 ratio | Status |
|---|---|---|---:|---:|---|
| `robot_collision_screening` | `prepared_pose_flags` | `goal1007_robot_pose_flags_dense_obstacles_large_rtx.json` | 0.014177 | 1179.643861 | `still_below_public_review_timing_floor` |
| `outlier_detection` | `prepared_fixed_radius_density_summary` | `goal1007_outlier_dbscan_x35_large_rtx.json` | 0.122348 | 4.640074 | `timing_floor_cleared_for_separate_2ai_public_wording_review` |
| `dbscan_clustering` | `prepared_fixed_radius_core_flags` | `goal1007_outlier_dbscan_x35_large_rtx.json` | 0.122921 | 6.620046 | `timing_floor_cleared_for_separate_2ai_public_wording_review` |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `goal1007_facility_service_coverage_x4_large_rtx.json` | 0.157368 | 22.805076 | `timing_floor_cleared_for_separate_2ai_public_wording_review` |
| `segment_polygon_hitcount` | `segment_polygon_hitcount_native_experimental` | `goal1007_segment_polygon_hitcount_large_rtx.json` | 0.146860 | 1.708308 | `timing_floor_cleared_for_separate_2ai_public_wording_review` |
| `segment_polygon_anyhit_rows` | `segment_polygon_anyhit_rows_prepared_bounded_gate` | `goal1007_segment_polygon_anyhit_rows_large_rtx.json` | 0.192639 | 3.030858 | `timing_floor_cleared_for_separate_2ai_public_wording_review` |
| `ann_candidate_search` | `candidate_threshold_prepared` | `goal1007_ann_candidate_coverage_x4_large_rtx.json` | 0.105215 | 4.857461 | `timing_floor_cleared_for_separate_2ai_public_wording_review` |

## Current Public Wording Source-Of-Truth

Release-facing wording must follow `rtdsl.rtx_public_wording_matrix()`, not this intake gate alone.

- `robot_collision_screening / prepared_pose_flags` current status: `public_wording_blocked` — The prepared ray/triangle any-hit scalar pose-count path is a real RT-core path, but larger RTX repeats stayed below the 100 ms public-review timing floor.

## Boundary

- A cleared timing floor means the row is eligible for separate 2-AI public-wording review.
- It does not authorize front-page or release-note speedup wording by itself.
- The wording remains limited to prepared RTX query/native sub-paths, not whole-app speedups.

