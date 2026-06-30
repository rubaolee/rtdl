# RayJoin Section 5.7 Overlay 8/8 Summary

Dataset root: `artifacts/goal4806_section57_arcgis_full_us_20260630/dataset`
Selected implementations: `rtdl_optix`

Timing caveat: Paper Table 4 values are historical reference numbers. Local author_rt rows are measured process wall times. RTDL rows are warm-cache medians under the selected protocol.

Correctness caveat: Raw overlay-output digest matches are byte-level checks for runs that requested --assemble-overlay-output. They are stronger than count-only checks, but they are not a substitute for a geometry/topology equivalence proof when output order or format intentionally differs.

## Coverage

| Metric | Value |
|---|---:|
| overlay_pairs_total | 1 |
| overlay_pairs_selected_implementations_complete | 1 |
| overlay_pairs_selected_implementations_incomplete | 0 |
| overlay_pairs_full_control_complete | 0 |
| overlay_pairs_full_control_incomplete | 1 |
| overlay_pairs_complete | 0 |
| overlay_pairs_incomplete | 1 |

## Matrix

| Pair | Paper RayJoin Processing (Preprocess) | Local Author RT Process | RTDL OptiX Total | RTDL Embree Total | V4+Numba Total | V4+Numba Status | RTDL LSI Count Match | OptiX Raw Output = Author | Embree Raw Output = Author | OptiX Raw Output = Embree | Selected Complete | Full Control Complete |
|---|---:|---:|---:|---:|---:|---|---|---|---|---|---:|---:|
| Block x Water | 0.23 (0.12) |  | 367.231680 |  |  | `` |  |  |  |  | True | False |
