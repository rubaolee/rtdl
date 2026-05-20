# Goal2461: Grouped-Stream Self-Query Device Path

Date: 2026-05-20

Status: implementation plus RTX A5000 pod evidence complete; external review pending.

## Purpose

Goal2457 made RT-DBSCAN's dense over-budget continuation use a generic OptiX
grouped-union primitive instead of materializing a giant directed adjacency
stream. Goal2459 then removed unnecessary exact-degree work by threshold-capping
core flags at `min_neighbors`.

One avoidable cost remained: the grouped-union pass is a self-radius graph, but
the Python binding still repacked the prepared search rows as host query rows
and uploaded them on every grouped pass. Goal2461 removes that cost without
adding DBSCAN-specific native code.

## Implementation

Added a generic OptiX native ABI:

- `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs`

This ABI reuses the prepared fixed-radius 3D search buffer as the query buffer,
sets `query_index_offset=0`, and writes into the existing generic device
workspaces:

- `predicate_flags`
- `parent_out`
- `fallback_candidate_out`

The existing host-query ABI remains available for non-self query batches:

- `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs`

Python now exposes:

- `PreparedOptixFixedRadiusCountThreshold3D.apply_device_grouped_union_self(...)`

The RT-DBSCAN grouped-stream adapter now calls the self-query method and reports:

- `native_engine_row_contract=generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces`
- `native_execution_path=prepared_rt_core_grouped_union_3d_self_query`
- `query_source=prepared_search_points_self_query_device`
- `transfer_mode=prepared_device_search_points_self_grouped_union_workspaces`

The native ABI and metadata remain generic fixed-radius/grouped-continuation
language. No DBSCAN-native ABI was added.

## Pod Evidence

Pod command:

`ssh -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod -p 22055 root@69.30.85.177`

Environment:

- GPU: NVIDIA RTX A5000
- Driver: 570.211.01
- Repository: `/root/rtdl_goal2457`
- Base commit: `c98acbc1`
- OptiX SDK: `/root/vendor/optix-sdk`
- CUDA prefix: `/usr/local/cuda-12`
- OptiX library: `/root/rtdl_goal2457/build/librtdl_optix.so`

Build:

`make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12`

Result: success.

## Performance Delta

Same clustered3d data shape and seed as Goal2459. Times below are steady-state
tail medians from repeats 2 and 3, after the first run paid module/pipeline
setup costs.

| Points | Goal2459 tail median sec | Goal2461 tail median sec | Improvement |
| ---: | ---: | ---: | ---: |
| 32,768 | 0.072831 | 0.029680 | 2.454x |
| 65,536 | 0.218252 | 0.095882 | 2.276x |

Goal2461 native metadata confirmed the new path on both rows:

- `native_symbol=rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs`
- `transfer_mode=prepared_device_search_points_self_grouped_union_workspaces`
- `query_source=prepared_search_points_self_query_device`

The planned 65,536-point benchmark still selects
`optix_rt_core_grouped_stream_cupy_components_3d`; its measured elapsed time in
this pod process was `0.536025s`, versus `0.578006s` in the Goal2459 artifact.
The planned one-shot row includes app setup and first-run costs, so the cleaner
steady-state evidence is the prepared repeat table above.

## Correctness

The tiny RT-DBSCAN validation smoke matched the CPU reference.

The repeated clustered3d runs produced stable component signatures for both
32,768 and 65,536 point rows.

## Tests

Local Windows:

`PYTHONPATH=src;. py -3 -m unittest tests.goal2461_grouped_stream_self_query_device_path_test tests.goal2459_grouped_stream_threshold_capped_core_flags_test tests.goal2457_generic_grouped_stream_continuation_implementation_test tests.goal2455_generic_grouped_stream_continuation_design_test tests.goal2437_rt_dbscan_explicit_continuation_planner_test tests.goal2453_rt_dbscan_planner_budget_pod_smoke_test`

Result: 22 tests OK.

Local Windows syntax:

`py -3 -m py_compile src\rtdsl\optix_runtime.py src\rtdsl\partner_adapters.py examples\v2_0\research_benchmarks\rt_dbscan\rtdl_rt_dbscan_benchmark_app.py`

Result: OK.

Pod:

`PYTHONPATH=src:. python3 -m unittest tests.goal2461_grouped_stream_self_query_device_path_test tests.goal2437_rt_dbscan_explicit_continuation_planner_test`

Result: 9 tests OK.

## Artifacts

- `docs/reports/goal2461_grouped_stream_self_query_pod/summary.json`
- `docs/reports/goal2461_grouped_stream_self_query_pod/clustered3d_32768_grouped_stream_self_query.json`
- `docs/reports/goal2461_grouped_stream_self_query_pod/clustered3d_65536_grouped_stream_self_query.json`
- `docs/reports/goal2461_grouped_stream_self_query_pod/tiny.json`
- `docs/reports/goal2461_grouped_stream_self_query_pod/planned_65536.json`

## Boundary

This is not a DBSCAN-specific engine feature. It is a generic prepared
fixed-radius self-query grouped continuation path.

This does not authorize a paper-reproduction claim, a release claim, or a broad
RT-core speedup claim. It is evidence that one generic grouped-stream bottleneck
was removed and that the RT-DBSCAN benchmark can exploit the new generic
self-query path.

The remaining bottleneck is the grouped-union pass itself, especially global
atomic pressure. The next design target should be a generic segmented/blocked
continuation primitive, not an app-specific DBSCAN native endpoint.
