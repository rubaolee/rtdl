# Gemini Handoff: Goal2394 RT-DBSCAN Device-Grid Baseline Review

Please review Goal2394 as an independent Gemini review distinct from Codex.

## Files To Inspect

- `docs/reports/goal2394_rt_dbscan_device_grid_baseline_2026-05-19.md`
- `docs/reports/goal2394_rt_dbscan_device_grid_local_linux/*.json`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/README.md`
- `scripts/goal2392_rt_dbscan_pod_runner.sh`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py`
- `tests/goal2394_rt_dbscan_device_grid_baseline_test.py`

## Context

Goal2393 accepted the initial RT-DBSCAN campaign with boundary and warned that
pod timing should not compare OptiX against a weak host-side continuation.
Codex then added a generic CuPy device-grid 3-D radius-graph component baseline:

```text
radius_graph_components_3d_cupy_grid_partner_columns(...)
```

The benchmark app now has a `partner_cupy_grid_components_3d` mode. Local Linux
GTX 1070 smoke artifacts show:

- `tiny` CuPy grid matches the CPU reference;
- `clustered3d` 512-point CuPy grid matches the CPU reference;
- `clustered3d` 4096-point CuPy grid and host bucket produce the same signature;
- local 4096 CuPy grid is faster than host bucket, but this is not RT-core
  evidence.

## Review Questions

1. Is the new CuPy device-grid path generic enough for RTDL, or does it leak
   DBSCAN/app-specific concepts into the runtime?
2. Are the correctness checks and local artifacts sufficient for this
   implementation slice?
3. Are the claim boundaries correct, especially no RT-core claim from GTX 1070
   and no paper reproduction claim?
4. Is the next gap correctly identified as:
   `OptiX fixed-radius device output -> device-resident grouped/component continuation`?
5. What must be checked on the RTX pod before this can support a serious
   RT-DBSCAN comparison?

## Required Output

Write your review to:

`docs/reviews/goal2395_gemini_review_goal2394_rt_dbscan_device_grid_2026-05-19.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.
