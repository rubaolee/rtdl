# Goal 715: Embree Fixed-Radius Summary Optimization

Date: 2026-04-21

## Scope

Goal715 addresses the main fixed-radius app bottleneck observed in Goal714: apps such as outlier detection and DBSCAN often use RTDL fixed-radius traversal only to derive density/core flags, but the default backend path emits all bounded neighbor rows, copies them into Python dictionaries, and then reduces them in Python.

This goal adds a narrower Embree-native summary primitive:

- `rtdl_embree_run_fixed_radius_count_threshold`
- `rt.fixed_radius_count_threshold_2d_embree(...)`

The primitive emits `{query_id, neighbor_count, threshold_reached}` summary rows instead of `{query_id, neighbor_id, distance}` neighbor rows. Positive thresholds permit capped counting for density/core predicates.

## Code Changes

- Added `RtdlFixedRadiusCountRow` and `rtdl_embree_run_fixed_radius_count_threshold` to the Embree native ABI.
- Added an Embree point-query callback mode for fixed-radius count/threshold summaries.
- Avoided neighbor-row materialization, per-query distance sorting, and final row sorting in the summary path.
- Used squared-distance checks and query-radius shrink on threshold reached.
- Exposed `rt.fixed_radius_count_threshold_2d_embree(...)` in Python.
- Added opt-in app modes:
  - `examples/rtdl_outlier_detection_app.py --backend embree --embree-summary-mode rt_count_threshold`
  - `examples/rtdl_dbscan_clustering_app.py --backend embree --embree-summary-mode rt_core_flags`

## Correctness Result

Focused test:

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal715_embree_fixed_radius_summary_test
Ran 3 tests in 3.664s
OK
```

The tests verify source/export presence and app-level oracle parity for the new Embree summary modes. In summary mode, neighbor-row emission is zero and output flags still match the brute-force oracle.

## Local Native Timing

Command:

```text
PYTHONPATH=src:. python3 scripts/goal715_embree_fixed_radius_summary_perf.py --copies 512,2048,8192,32768 --repeats 3 --warmups 1 --output docs/reports/goal715_embree_fixed_radius_summary_perf_local_2026-04-21.json
```

Result summary on this macOS host:

| copies | outlier summary vs rows | DBSCAN summary vs rows |
| ---: | ---: | ---: |
| 512 | 0.928x | 1.063x |
| 2048 | 0.902x | 1.071x |
| 8192 | 0.919x | 1.111x |
| 32768 | 0.856x | 1.043x |

## Interpretation

The optimization is correctness-useful and API-useful, but only performance-useful for denser fixed-radius summaries in this local fixture. DBSCAN improves modestly because row emission is heavier than one capped core-flag row per query. Outlier detection is slower because the fixture is sparse: the row path emits only about 2.5 rows per query, while the summary path still pays Embree point-query traversal and emits one row per query.

This is not a broad Embree performance-win claim. The honest conclusion is:

- `rt_count_threshold` / `rt_core_flags` are the right app-facing primitives for density/core predicates.
- The current Embree point-query implementation does not yet guarantee speedup for sparse neighborhoods.
- Future performance work should focus on prepared/reused scenes, denser fixtures, and native app-specific summary kernels where Python output volume dominates.

## Status

Goal715 is implemented and locally validated. Release-facing docs should describe it as an optional summary/count path, not as a universal speedup.
