# Goal2720: RayDB Prepared Device Hit-Stream Steady-State Path

Date: 2026-05-30
Status: accepted as pod smoke evidence with claim boundary

## Purpose

Goal2715 and Goal2719 proved that the RayDB-style v2.5 OptiX path can return native device hit-stream columns and hand them through the Torch/Triton carrier without building host hit rows. The remaining performance issue was cold-path overhead: every timed invocation rebuilt app-owned table payload columns, prepared the OptiX scene, and paid one-time setup costs before measuring traversal plus continuation.

Goal2720 adds a prepared steady-state backend for the same generic contract:

`paper_rt_optix_device_hit_stream_triton_prepared`

The prepared path keeps native code app-agnostic. It prepares the app-owned workload, typed payload columns, and static OptiX triangle scene once, then measures repeated query, native hit-stream, typed-payload gather, and Triton continuation iterations.

## Implementation

- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py` registers the prepared backend.
- The prepared backend reuses:
  - `prepare_paper_rt_encoded_table_descriptor`
  - `prepare_typed_payload_columns`
  - `rt.prepare_optix_static_triangle_scene_3d`
- Each steady-state iteration calls:
  - `prepared_scene.ray_triangle_hit_stream_device_columns`
  - `rt.gather_typed_payload_columns_for_hit_stream`
  - the existing Triton continuation
- `scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py` recognizes the prepared backend and lets the app perform internal warmup/repeat timing, so the reported median is a steady-state per-iteration median rather than an outer cold-run median.

## Pod Smoke

Artifact:

`docs/reports/goal2720_pod_artifacts/goal2720_raydb_prepared_device_hit_stream_smoke_pod_69_30_85_171_2026-05-30.json`

Pod:

- host: `69.30.85.171`
- port: `22167`
- GPU: `NVIDIA RTX A5000, 570.211.01, 24564 MiB`
- commit: `051b15be95349a0674be1ca001fa4c72cec9b760`
- repeats: `3`
- warmup: `1`

Focused pod tests passed before the smoke:

`tests.goal2720_raydb_prepared_device_hit_stream_steady_state_test`

`tests.goal2685_device_resident_hit_stream_handoff_test`

`tests.goal2710_raydb_native_device_hit_stream_path_test`

Result: `23` tests passed.

## Results

| Rows | Mode | Unprepared median sec | Prepared median sec | Prepared speedup |
| ---: | --- | ---: | ---: | ---: |
| 10000 | count | 0.027641 | 0.005005 | 5.522x |
| 10000 | sum | 0.128689 | 0.027570 | 4.668x |
| 100000 | count | 0.176325 | 0.007366 | 23.938x |
| 100000 | sum | 0.602112 | 0.116064 | 5.188x |

All prepared cases reported:

- `matches_cpu_reference = true`
- `prepared_steady_state = true`
- `prepared_payload_columns_reused = true`
- `prepared_optix_scene_reused = true`
- `native_device_column_path_used = true`
- `native_device_hit_stream_columns_ready = true`
- `host_row_bridge_bypassed = true`
- `handoff_materializes_host_rows_for_bridge = false`
- `handoff_native_device_column_output_proven_on_hardware = true`
- `handoff_removes_host_materialization_bottleneck = true`
- `torch_carrier_same_pointer_evidence_observed = true`
- `true_zero_copy_authorized = false`

## Interpretation

The prepared path shows that the v2.5 typed primitive payload and native hit-stream design has a useful steady-state execution mode. The measured win comes from removing repeated app-owned setup from the timed loop:

- static scene preparation is reused;
- typed payload column preparation is reused;
- the native OptiX hit-stream call still produces device columns;
- the continuation still gathers payload through the partner carrier;
- no host hit-row bridge is introduced.

This is the right measurement boundary for repeated RayDB-style queries against stable data. It is not a replacement for cold whole-app timing, and it is not evidence that every RTDL app automatically gets the same ratio.

## Boundary

This goal authorizes the internal statement that the prepared RayDB-style v2.5 path is faster than the unprepared v2.5 device hit-stream path on the recorded RTX A5000 smoke cases.

It does not authorize:

- public true-zero-copy wording;
- broad RT-core speedup wording;
- RayDB paper reproduction claims;
- a claim that prepared steady-state timing replaces cold whole-app timing;
- a claim that v2.5 is complete across all benchmark apps.
