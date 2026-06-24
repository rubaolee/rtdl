# Handoff: Claude Review Debt For Goal3859-3864 Perf Chain

Please perform a read-only external review of the RTDL Goal3859-3864 chain and write the review to:

`docs/reviews/goal3865_claude_review_goal3859_3864_perf_chain_2026-06-08.md`

## Scope

Review the latest committed chain on `main`:

- Goal3859: RT-DBSCAN Numba grouped-stream promotion.
- Goal3861: LibRTS AABB prepared-query bottleneck characterization.
- Goal3862: LibRTS generic multi-operation prepared AABB query path.
- Goal3864: full 10-app scale refresh after the LibRTS multi-operation path.

Primary artifacts and tests:

- `docs/reports/goal3859_rt_dbscan_numba_grouped_stream_2026-06-08.md`
- `docs/reports/goal3861_librts_prepared_aabb_probe_2026-06-08.md`
- `docs/reports/goal3862_librts_aabb_multi_operation_probe_2026-06-08.md`
- `docs/reports/goal3864_full_scale_after_librts_multi_operation_2026-06-08.md`
- `docs/reports/goal3859_rt_dbscan_numba_grouped_stream_a5000/`
- `docs/reports/goal3861_librts_aabb_prepared_probe_a5000/`
- `docs/reports/goal3862_librts_aabb_multi_operation_streams_a5000/`
- `docs/reports/goal3864_full_scale_after_librts_multi_operation_a5000/`
- `tests/goal3859_rt_dbscan_numba_grouped_stream_test.py`
- `tests/goal3861_librts_prepared_aabb_probe_test.py`
- `tests/goal3862_librts_aabb_multi_operation_probe_test.py`
- `tests/goal3864_full_scale_after_librts_multi_operation_test.py`

Relevant implementation files:

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `src/rtdsl/current_benchmark_scale_profiles.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `src/rtdsl/optix_runtime.py`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_workloads.cpp`

## Questions To Answer

1. Does Goal3859 genuinely promote RT-DBSCAN to a high-performance Numba grouped-stream reference path without app-specific native leakage or hidden CuPy fallback?
2. Are the Goal3859 performance claims correctly bounded by the JSON artifacts, especially the canonical CuPy comparison ratio of about `1.017078x` for the new Numba grouped-stream path versus the prior CuPy grouped-stream path?
3. Does Goal3861 correctly diagnose the LibRTS AABB row as scene/query preparation dominated rather than Python continuation dominated?
4. Is Goal3862 a valid generic/app-agnostic multi-operation AABB prepared-query primitive, and are its limited performance results honestly reported rather than overclaimed?
5. Does Goal3864 provide a clean current 10-app scale snapshot with no public claim-boundary violations?
6. What must remain open for the next engineering step, especially RayJoin representativeness and contract-by-contract baseline quality?

## Review Rules

- This is read-only. Do not edit source files except for writing the review file above.
- Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
- Lead with findings and risks. Be precise about evidence, artifact paths, and any inconsistencies.
- Do not authorize release, broad speedup claims, broad RT-core claims, zero-copy claims, or paper-reproduction claims.
- If you cannot run tests due to environment limits, say so explicitly and rely on static verification plus artifacts.

