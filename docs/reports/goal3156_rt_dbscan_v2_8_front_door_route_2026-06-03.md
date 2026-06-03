# Goal3156 RT-DBSCAN v2.8 Front-Door Route

Date: 2026-06-03

Verdict: `accept-with-boundary`

## Purpose

Goal3155 added the reusable v2.8 fixed-radius graph component front door. Goal3156 routes the RT-DBSCAN benchmark app's grouped-stream execution branch through that front door while preserving the app's existing benchmark mode labels and app-owned policy.

This keeps the important separation:

- RTDL runtime front door: fixed-radius graph component continuation.
- Benchmark app policy: radius choice, component threshold choice, signature comparison, and benchmark mode naming.
- Native engine: generic fixed-radius grouped union, no app-specific logic.

## What Changed

| File | Operation |
| --- | --- |
| `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py` | Replaced the grouped-stream branch's direct lower-adapter calls with `rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d(...)` and `rt.fixed_radius_graph_component_labels_3d_v2_8(...)`. |
| `tests/goal3156_rt_dbscan_v2_8_front_door_route_test.py` | Added regression coverage proving the grouped-stream branch uses the v2.8 front door while preserving old mode labels and non-authorizing metadata. |

## Compatibility

The existing mode labels remain intact:

- `optix_rt_core_grouped_stream_cupy_components_3d`
- `optix_rt_core_grouped_stream_cupy_column_signature_3d`
- `optix_rt_core_grouped_stream_blocked_cupy_components_3d`
- `optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d`

This avoids breaking old benchmark scripts while moving the implementation to the cleaner v2.8 API.

## Boundary

This goal does not make a new public speed claim and does not promote a v2.8 release:

- no hidden dispatcher
- no automatic partner selection
- no app-specific native engine logic
- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

The benchmark app still owns its DBSCAN-specific semantics. The reusable front door only exposes fixed-radius graph component labels.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3156_rt_dbscan_v2_8_front_door_route_test tests.goal3155_fixed_radius_graph_component_front_door_test tests.goal2457_generic_grouped_stream_continuation_implementation_test tests.goal2459_grouped_stream_threshold_capped_core_flags_test tests.goal2461_grouped_stream_self_query_device_path_test tests.goal2478_rt_dbscan_project_completion_test
```

Result: 28 tests passed.

Pod validation should run a focused RT-DBSCAN grouped-stream probe from a clean checkout to verify the app branch still produces matching signatures through the v2.8 front door.
