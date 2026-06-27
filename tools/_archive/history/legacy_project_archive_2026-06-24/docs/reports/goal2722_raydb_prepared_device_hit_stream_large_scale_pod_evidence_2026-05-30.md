# Goal2722: RayDB Prepared Device Hit-Stream Large-Scale Pod Evidence

Date: 2026-05-30
Status: accepted as large-scale pod evidence with claim boundary

## Purpose

Goal2720 introduced the prepared RayDB-style v2.5 backend and validated it on a small RTX A5000 smoke grid. Goal2722 extends that evidence to larger row counts while keeping the same measurement boundary:

- native OptiX emits device hit-stream columns;
- typed payload columns are gathered through the Torch/Triton carrier;
- app-owned workload, typed payload, and static scene preparation are reused;
- the timed value is steady-state query/handoff/continuation per iteration;
- true-zero-copy and broad speedup claims remain unauthorized.

## Artifact

`docs/reports/goal2722_pod_artifacts/goal2722_raydb_prepared_device_hit_stream_large_pod_69_30_85_171_2026-05-30.json`

Pod:

- host: `69.30.85.171`
- port: `22167`
- GPU: `NVIDIA RTX A5000, 570.211.01, 24564 MiB`
- commit: `4f84fed87f841198505eae09d9c409ae546a6d26`
- repeats: `3`
- warmup: `1`
- group count: `256`

## Results

| Rows | Mode | Unprepared median sec | Prepared median sec | Prepared speedup |
| ---: | --- | ---: | ---: | ---: |
| 250000 | count | 0.478994 | 0.007322 | 65.416x |
| 250000 | sum | 1.499727 | 0.262664 | 5.710x |
| 1000000 | count | 1.912957 | 0.009095 | 210.336x |
| 1000000 | sum | 2.699901 | 0.256470 | 10.527x |

All cases reported `matches_cpu_reference = true`. All prepared cases reported:

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

The large-scale result strengthens the same lesson as Goal2720: repeated RayDB-style queries need a prepared execution contract. The unprepared path rebuilds app-owned workload/payload state inside each measured call, so it is a poor steady-state opponent once the scene and typed payload are stable. The prepared path removes those repeated setup costs from the timing loop while preserving the generic RTDL boundary.

The count cases show very large ratios because the hit stream is sparse and the steady-state prepared count path mostly pays a small native hit-stream call, carrier handoff, and Triton continuation. The sum cases remain slower than count because they still exercise the value-carrying payload path and a heavier native call, but they still improve materially once preparation is reused.

## Boundary

This goal authorizes an internal, same-path statement: on the recorded RTX A5000 large-scale cases, the prepared RayDB-style v2.5 path is faster than the unprepared v2.5 device hit-stream path.

It does not authorize:

- true-zero-copy wording;
- broad RT-core speedup wording;
- RayDB paper reproduction claims;
- whole-app speedup claims;
- claims about apps whose continuation shape is not a grouped scalar reduction;
- treating prepared steady-state timing as a replacement for cold whole-app timing.
