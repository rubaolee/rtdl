# Goal1931 - Current All-App v1.8 vs v2.0 Performance Analysis

Status: current-evidence-analysis-external-review-needed

Date: 2026-05-13

This report is the current all-app performance analysis layer on top of Goal1930. It uses existing accepted pod artifacts where they exist and marks the remaining rows as pending or evidence-only controls. It does not authorize v2.0 release and it does not claim every app has a measured v2 speedup.

## Current Table

| App | Class | Partner | Size | v1.8 prepared s | v2 prepared partner s | Ratio | Insight |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `database_analytics` | `control` | pending | pending | pending | pending | pending | The current fast path is a prepared compact-summary native continuation, not a v2 partner tensor continuation. Treat as a control until a true partner columnar scan/grouped-reduction adapter exists. |
| `graph_analytics` | `control` | pending | pending | pending | pending | pending | Visibility can be RT-shaped, but BFS and triangle-count bookkeeping remain graph algorithms. Final analysis must split these rows rather than hiding them under one app name. |
| `service_coverage_gaps` | `positive` | cupy | 16384 | 0.038096 | 0.000228 | 0.005983 | Prepared fixed-radius native work plus partner-owned threshold columns amortize very well at the larger row size. |
| `event_hotspot_screening` | `positive` | cupy | 16384 | 0.094140 | 0.000188 | 0.001998 | Prepared fixed-radius native work plus partner-owned threshold columns amortize very well at the larger row size. |
| `facility_knn_assignment` | `positive` | cupy | 524288 | 1.553787 | 0.000480 | 0.000309 | Repeat-3 fixed-radius pod evidence is seconds-scale on v1.8 and sub-millisecond on the v2 partner threshold path; this is not ranked KNN or full cluster labeling. |
| `road_hazard_screening` | `positive` | cupy | 2048 | 0.004491 | 0.001108 | 0.246651 | Prepared reuse and partner-owned compact outputs matter; row materialization or tiny cases are much less favorable. |
| `segment_polygon_hitcount` | `positive` | torch | 2048 | 0.002544 | 0.000878 | 0.345241 | Prepared reuse and partner-owned compact outputs matter; row materialization or tiny cases are much less favorable. |
| `segment_polygon_anyhit_rows` | `positive` | torch | 1048576 | 7.121871 | 1.582755 | 0.222239 | Goal1940 moves this row out of pending: the 1,048,576-row segment any-hit artifact is seconds-scale and same-contract, with strict row-count parity. |
| `polygon_pair_overlap_area_rows` | `control` | pending | pending | pending | pending | pending | Do not claim full v2 partner acceleration until exact area refinement is a reviewed partner tensor continuation or explicitly accepted as fallback. |
| `polygon_set_jaccard` | `control` | pending | pending | pending | pending | pending | The exact set-union reduction dominates unless moved into a bounded partner continuation. |
| `hausdorff_distance` | `positive` | torch | 524288 | 1.326599 | 0.000368 | 0.000277 | Repeat-3 fixed-radius pod evidence is seconds-scale on v1.8 and sub-millisecond on the v2 partner threshold path; this is not ranked KNN or full cluster labeling. |
| `ann_candidate_search` | `positive` | torch | 524288 | 1.328173 | 0.000350 | 0.000263 | Repeat-3 fixed-radius pod evidence is seconds-scale on v1.8 and sub-millisecond on the v2 partner threshold path; this is not ranked KNN or full cluster labeling. |
| `outlier_detection` | `positive` | cupy | 524288 | 1.357974 | 0.000439 | 0.000323 | Repeat-3 fixed-radius pod evidence is seconds-scale on v1.8 and sub-millisecond on the v2 partner threshold path; this is not ranked KNN or full cluster labeling. |
| `dbscan_clustering` | `positive` | torch | 524288 | 1.337720 | 0.000436 | 0.000326 | Repeat-3 fixed-radius pod evidence is seconds-scale on v1.8 and sub-millisecond on the v2 partner threshold path; this is not ranked KNN or full cluster labeling. |
| `robot_collision_screening` | `positive-subsecond` | cupy | 8388608 | 0.524696 | 0.009835 | 0.018745 | Goal1940 proves exact pose-flag parity and strong ratios through 8,388,608 poses, but the v1.8 baseline remains subsecond, so this is not a seconds-scale whole-app claim. |
| `barnes_hut_force_app` | `positive` | cupy | 524288 | 1.373772 | 0.000418 | 0.000304 | Repeat-3 fixed-radius pod evidence is seconds-scale on v1.8 and sub-millisecond on the v2 partner threshold path; this is not ranked KNN or full cluster labeling. |

## What The Table Says

- The strongest measured v2 rows are the repeat-3 fixed-radius family rows, where v1.8 is seconds-scale and v2 partner threshold decisions are sub-millisecond.
- Segment any-hit now has a seconds-scale same-contract row at 1,048,576 outputs; road-hazard and segment hitcount remain positive compact-output rows.
- Robot collision now has exact pose-flag parity and strong ratios through 8,388,608 poses, but it is marked `positive-subsecond` because the v1.8 baseline is still below one second.
- Database, graph, and exact polygon metrics are intentionally marked as controls/fallbacks. They are important evidence rows, but they are not v2 partner speedup rows until their app continuations move into reviewed partner tensor contracts.

## Release Boundary

This is a performance-analysis scaffold and partial evidence report. Final v2.0 still needs external review of the all-app conclusion, a packaging/source-tree decision, and final release consensus.
