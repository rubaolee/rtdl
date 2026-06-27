# Goal1931 - Current All-App v1.8 vs v2.0 Performance Analysis

Status: current-evidence-analysis-final-pod-batch-needed

Date: 2026-05-13

This report is the current all-app performance analysis layer on top of Goal1930. It uses existing accepted pod artifacts where they exist and marks the remaining rows as pending or evidence-only controls. It does not authorize v2.0 release and it does not claim every app has a measured v2 speedup.

## Current Table

| App | Class | Partner | Size | v1.8 prepared s | v2 prepared partner s | Ratio | Insight |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `database_analytics` | `control` | pending | pending | pending | pending | pending | The current fast path is a prepared compact-summary native continuation, not a v2 partner tensor continuation. Treat as a control until a true partner columnar scan/grouped-reduction adapter exists. |
| `graph_analytics` | `control` | pending | pending | pending | pending | pending | Visibility can be RT-shaped, but BFS and triangle-count bookkeeping remain graph algorithms. Final analysis must split these rows rather than hiding them under one app name. |
| `service_coverage_gaps` | `positive` | cupy | 16384 | 0.038096 | 0.000228 | 0.005983 | Prepared fixed-radius native work plus partner-owned threshold columns amortize very well at the larger row size. |
| `event_hotspot_screening` | `positive` | cupy | 16384 | 0.094140 | 0.000188 | 0.001998 | Prepared fixed-radius native work plus partner-owned threshold columns amortize very well at the larger row size. |
| `facility_knn_assignment` | `pending-pod` | pending | pending | pending | pending | pending | The honest row is coverage/threshold. Ranked KNN ordering is outside this adapter. |
| `road_hazard_screening` | `positive` | cupy | 2048 | 0.004491 | 0.001108 | 0.246651 | Prepared reuse and partner-owned compact outputs matter; row materialization or tiny cases are much less favorable. |
| `segment_polygon_hitcount` | `positive` | torch | 2048 | 0.002544 | 0.000878 | 0.345241 | Prepared reuse and partner-owned compact outputs matter; row materialization or tiny cases are much less favorable. |
| `segment_polygon_anyhit_rows` | `pending-pod` | pending | pending | pending | pending | pending | This is row-output materialization, so it may lag compact count/flag rows even though the native RT discovery is generic. |
| `polygon_pair_overlap_area_rows` | `control` | pending | pending | pending | pending | pending | Do not claim full v2 partner acceleration until exact area refinement is a reviewed partner tensor continuation or explicitly accepted as fallback. |
| `polygon_set_jaccard` | `control` | pending | pending | pending | pending | pending | The exact set-union reduction dominates unless moved into a bounded partner continuation. |
| `hausdorff_distance` | `pending-pod` | pending | pending | pending | pending | pending | This is a thresholded nearest-candidate workload. Exact directed Hausdorff max-distance remains a different app continuation. |
| `ann_candidate_search` | `pending-pod` | pending | pending | pending | pending | pending | The row tests candidate coverage, not arbitrary nearest-neighbor indexing. |
| `outlier_detection` | `pending-pod` | pending | pending | pending | pending | pending | The v2 output should be compact flags/counts; host materialized row lists would erase much of the point. |
| `dbscan_clustering` | `pending-pod` | pending | pending | pending | pending | pending | Only the RTDL neighbor/core test is accelerated; transitive cluster labeling is not yet a partner graph algorithm. |
| `robot_collision_screening` | `pending-pod` | pending | pending | pending | pending | pending | The important correctness check is exact pose-flag parity, not just colliding-pose count parity. |
| `barnes_hut_force_app` | `pending-pod` | pending | pending | pending | pending | pending | This covers spatial node coverage, not a full Barnes-Hut force-vector GPU solver. |

## What The Table Says

- The strongest measured v2 rows are prepared fixed-radius and prepared compact output rows, where native work is reused and the app result stays in partner-owned columns.
- Segment/polygon and road-hazard become convincing at larger rows; small rows remain setup-bound and must be described as mixed.
- The six additional fixed-radius-family apps and robot collision now have local harnesses, but they still need current RTX pod timing before they can move from `pending-pod` to measured.
- Database, graph, and exact polygon metrics are intentionally marked as controls/fallbacks. They are important evidence rows, but they are not v2 partner speedup rows until their app continuations move into reviewed partner tensor contracts.

## Release Boundary

This is a performance-analysis scaffold and partial evidence report. Final v2.0 still needs the current pod batch for pending rows, external review of the all-app conclusion, and final release consensus.
