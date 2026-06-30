# Goal3918 RT-DBSCAN Blocked Numba Grouped-Stream Modes

Date: 2026-06-08

## Purpose

The RT-DBSCAN grouped-stream path already had blocked range modes for CuPy and unblocked modes for Numba. Goal3918 adds the missing Numba blocked range mode names so future A5000 probes can test the same generic blocked grouped-stream primitive with the Numba partner.

## Change

`examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py` now accepts:

- `optix_rt_core_grouped_stream_blocked_numba_components_3d`
- `optix_rt_core_grouped_stream_blocked_numba_column_signature_3d`

These modes reuse the existing generic `prepare_v2_8_fixed_radius_graph_component_continuation_3d(...)` path with:

- `partner="numba"`;
- `strategy="grouped_stream"`;
- `grouped_union_query_block_size=<explicit block size>`;
- native contract `generic_prepared_fixed_radius_grouped_union_3d_self_range_device_workspaces`.

## Boundary

This is a benchmark-app mode-surface addition over an existing generic primitive. It does not add DBSCAN-specific native engine logic, does not make the mode a default route, and does not authorize release, paper-reproduction, whole-app speedup, broad RT-core speedup, or true-zero-copy claims.

## Validation

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3918_rt_dbscan_blocked_numba_grouped_stream_modes_test tests.goal3898_rt_dbscan_numba_segmented_count_signature_test tests.goal3859_rt_dbscan_numba_grouped_stream_test
```

Expected result: all tests pass.

## Next Pod Step

Run a focused A5000 probe comparing:

- `optix_rt_core_grouped_stream_numba_column_signature_3d`
- `optix_rt_core_grouped_stream_blocked_numba_column_signature_3d`

using the same dataset/point count/repeat/warmup protocol. Only promote the blocked Numba route if it wins timing and preserves signature stability.
