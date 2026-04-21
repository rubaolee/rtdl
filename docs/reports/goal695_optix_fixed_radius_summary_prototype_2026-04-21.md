# Goal 695: OptiX Fixed-Radius Summary Prototype

**Date:** 2026-04-21
**Implementer:** Codex
**Precondition:** Goal694 3-AI consensus accepted only the fixed-radius subset of Gemini's OptiX RT-core redesign.

## Scope

This goal implements the first narrow action from Goal694:

- fixed-radius count/threshold summaries for outlier detection;
- fixed-radius core-flag summaries for DBSCAN;
- OptiX first, with no change to Hausdorff, ANN/KNN, or Barnes-Hut.

## Native Surface

Added a new OptiX C ABI:

```c
rtdl_optix_run_fixed_radius_count_threshold(
    query_points,
    query_count,
    search_points,
    search_count,
    radius,
    threshold,
    rows_out,
    row_count_out,
    error_out,
    error_size)
```

It emits one `RtdlFixedRadiusCountRow` per query:

- `query_id`
- `neighbor_count`
- `threshold_reached`

`threshold == 0` requests full counts. A positive threshold allows the OptiX any-hit program to call `optixTerminateRay()` once the count reaches the threshold.

## RT-Core Mapping

The new kernel uses the Goal694 2.5D construction:

- every target point becomes a custom primitive AABB spanning `(x +/- radius, y +/- radius, z +/- radius)`;
- every query point fires a vertical ray from `(qx, qy, -radius)` in `+z`;
- the OptiX intersection program accepts a primitive only when `dx*dx + dy*dy <= radius*radius`;
- the any-hit program increments the count and optionally terminates at the threshold.

This is a true OptiX traversal path in source shape: it uses `optixTrace`, a custom intersection program, an any-hit program, and `optixTerminateRay`. It is not a wrapper around the existing CUDA-through-OptiX neighbor-row kernel.

## App Wiring

`examples/rtdl_outlier_detection_app.py` now has:

```bash
python examples/rtdl_outlier_detection_app.py --backend optix --optix-summary-mode rt_count_threshold
```

This mode returns density labels from native threshold summaries instead of materializing every neighbor row. Because thresholded counts are intentionally truncated for non-outliers, `matches_oracle` compares the outlier labels against the oracle, not full neighbor counts.

`examples/rtdl_dbscan_clustering_app.py` now has:

```bash
python examples/rtdl_dbscan_clustering_app.py --backend optix --optix-summary-mode rt_core_flags
```

This mode returns DBSCAN core flags only. It intentionally does not perform full cluster expansion, because cluster expansion still needs neighborhood connectivity and is not part of the Goal694 fixed-radius-count prototype.

## Boundaries

This goal does not change public app performance classifications yet. Outlier detection and DBSCAN remain `cuda_through_optix` until the new native function is built and measured on Linux/RTX-class hardware.

This goal does not claim:

- KNN/ANN acceleration;
- Hausdorff acceleration;
- Barnes-Hut acceleration;
- broad OptiX RT-core speedup;
- correctness on arbitrary boundary-tolerance datasets before Linux native parity testing.

## Verification

Added `tests/goal695_optix_fixed_radius_summary_test.py`.

The test suite verifies:

- outlier app summary mode consumes threshold rows and avoids neighbor-row materialization;
- DBSCAN app summary mode consumes threshold rows and reports core flags without pretending to do clustering expansion;
- native source contains the intended OptiX traversal programs and ABI symbols.

Local macOS `make build-optix` was attempted and could not run because this machine does not have the OptiX SDK at `/opt/optix/include/optix.h`. Native Linux build/performance validation is still required before changing support classifications or making speed claims.
