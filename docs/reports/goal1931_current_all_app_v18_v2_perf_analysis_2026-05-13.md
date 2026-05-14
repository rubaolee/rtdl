# Goal1931 - Current All-App v1.8 vs v2.0 Performance Analysis

Status: current-evidence-analysis-external-review-needed

Date: 2026-05-13

This report is the current all-app performance analysis layer on top of Goal1930. It uses existing accepted pod artifacts where they exist and marks the remaining rows as pending or evidence-only controls. It does not authorize v2.0 release and it does not claim every app has a measured v2 speedup.

## Current Table

| App | Class | Partner | Size | v1.8 prepared s | v2 prepared partner s | Ratio | Insight |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `database_analytics` | `positive` | cupy | 100000 | 5.002953 | 1.023833 | 0.204646 | Goal1957/1956 RawKernel evidence is fast, but the reusable engine debt is a general partner grouped-scan/reduction adapter instead of app-local DB code. |
| `graph_analytics` | `positive-bounded` | cupy | 1000 | 18.060916 | 0.000054 | 0.000003 | Goal1972 removes the closed-form graph shortcut and uses generic partner metric-table reductions; this is still not a broad graph traversal acceleration claim. |
| `service_coverage_gaps` | `positive` | cupy | 16384 | 0.038096 | 0.000228 | 0.005983 | Prepared fixed-radius native work plus partner-owned threshold columns amortize very well at the larger row size. |
| `event_hotspot_screening` | `positive` | cupy | 16384 | 0.094140 | 0.000188 | 0.001998 | Prepared fixed-radius native work plus partner-owned threshold columns amortize very well at the larger row size. |
| `facility_knn_assignment` | `positive-bounded-exact` | cupy | 512 | 0.101372 | 0.004628 | 0.045649 | Goal1978 upgrades facility KNN from a service-coverage threshold proxy to exact K=3 ranked nearest-depot rows through generic partner top-k point-column algebra; this is not an RT-core claim. |
| `road_hazard_screening` | `positive` | cupy | 2048 | 0.004491 | 0.001108 | 0.246651 | Prepared reuse and partner-owned compact outputs matter; row materialization or tiny cases are much less favorable. |
| `segment_polygon_hitcount` | `positive` | torch | 2048 | 0.002544 | 0.000878 | 0.345241 | Prepared reuse and partner-owned compact outputs matter; row materialization or tiny cases are much less favorable. |
| `segment_polygon_anyhit_rows` | `positive` | torch | 1048576 | 7.121871 | 1.582755 | 0.222239 | Goal1940 moves this row out of pending: the 1,048,576-row segment any-hit artifact is seconds-scale and same-contract, with strict row-count parity. |
| `polygon_pair_overlap_area_rows` | `positive-bounded` | cupy | 2048 | 0.279780 | 0.081689 | 0.291976 | Goal1969 reverses the polygon control rows by using a compact CuPy extent candidate table; this is still bounded to the authored axis-aligned control app and is not an arbitrary polygon overlay or OptiX RT-core claim. |
| `polygon_set_jaccard` | `positive-bounded` | cupy | 2048 | 0.233212 | 0.065533 | 0.281000 | Goal1969 reverses the polygon control rows by using a compact CuPy extent candidate table; this is still bounded to the authored axis-aligned control app and is not an arbitrary polygon overlay or OptiX RT-core claim. |
| `hausdorff_distance` | `positive-bounded-exact` | cupy | 512 | 0.325964 | 0.002686 | 0.008241 | Goal1975 upgrades Hausdorff from a fixed-radius threshold proxy to exact partner-reference directed Hausdorff via min-distance then max-distance reductions; the CPU baseline is limited to a small exact row and this is not an RT-core claim. |
| `ann_candidate_search` | `positive` | torch | 524288 | 1.328173 | 0.000350 | 0.000263 | Repeat-3 fixed-radius pod evidence is seconds-scale on v1.8 and sub-millisecond on the v2 partner threshold path; this is not ranked KNN or full cluster labeling. |
| `outlier_detection` | `positive` | cupy | 524288 | 1.357974 | 0.000439 | 0.000323 | Repeat-3 fixed-radius pod evidence is seconds-scale on v1.8 and sub-millisecond on the v2 partner threshold path; this is not ranked KNN or full cluster labeling. |
| `dbscan_clustering` | `positive` | torch | 524288 | 1.337720 | 0.000436 | 0.000326 | Repeat-3 fixed-radius pod evidence is seconds-scale on v1.8 and sub-millisecond on the v2 partner threshold path; this is not ranked KNN or full cluster labeling. |
| `robot_collision_screening` | `positive-subsecond` | cupy | 8388608 | 0.524696 | 0.009835 | 0.018745 | Goal1940 proves exact pose-flag parity and strong ratios through 8,388,608 poses, but the v1.8 baseline remains subsecond, so this is not a seconds-scale whole-app claim. |
| `barnes_hut_force_app` | `positive` | cupy | 524288 | 1.373772 | 0.000418 | 0.000304 | Repeat-3 fixed-radius pod evidence is seconds-scale on v1.8 and sub-millisecond on the v2 partner threshold path; this is not ranked KNN or full cluster labeling. |

## What The Table Says

- The strongest measured v2 rows are the repeat-3 fixed-radius family rows, where v1.8 is seconds-scale and v2 partner threshold decisions are sub-millisecond.
- Segment any-hit now has a seconds-scale same-contract row at 1,048,576 outputs; road-hazard and segment hitcount remain positive compact-output rows.
- Robot collision now has exact pose-flag parity and strong ratios through 8,388,608 poses, but it is marked `positive-subsecond` because the v1.8 baseline is still below one second.
- Database remains a bounded control/fallback row. Graph and the two polygon control rows now have positive bounded v2 evidence after Goal1972 and Goal1969, but their claims stay narrow.
- Hausdorff now has an exact partner-reference row after Goal1975, so the table prefers that semantic match over the faster but weaker fixed-radius threshold proxy.
- Facility KNN now has an exact partner-reference K=3 top-k row after Goal1978, so the table no longer treats service coverage as the best semantic representative for that app.

## Release Boundary

This is a performance-analysis scaffold and partial evidence report. Final v2.0 still needs external review of the all-app conclusion, a packaging/source-tree decision, and final release consensus.
