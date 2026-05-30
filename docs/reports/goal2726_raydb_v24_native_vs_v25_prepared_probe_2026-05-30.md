# Goal2726: RayDB v2.4 Native vs v2.5 Prepared Diagnostic Probe

Date: 2026-05-30
Status: accepted as diagnostic pod evidence with release-claim boundary

## Purpose

Goal2720 and Goal2722 proved that the prepared RayDB-style v2.5 device hit-stream path is much faster than the unprepared v2.5 path once the app-owned workload, typed payload columns, and static OptiX scene are reused.

Goal2726 adds a same-hardware diagnostic comparison against the older `paper_rt_optix` RayDB-style native grouped-reduction path. The purpose is narrow:

- confirm the prepared v2.5 path is not merely beating an artificially weak unprepared v2.5 baseline;
- inspect whether the old native path still spends most time outside RT traversal;
- keep the public claim boundary explicit until a truly fair prepared-vs-prepared same-contract opponent exists.

## Artifact

`docs/reports/goal2726_pod_artifacts/goal2726_raydb_v24_native_vs_v25_prepared_probe_pod_69_30_85_171_2026-05-30.json`

Pod:

- host: `69.30.85.171`
- port: `22167`
- GPU: `NVIDIA RTX A5000, 570.211.01, 24564 MiB`
- commit: `bbb882cb83df3cd642004a934ca58bd5bc4d1c26`
- repeats: `3`
- warmup: `1`
- group count: `256`

## Results

| Rows | Mode | Existing `paper_rt_optix` median sec | v2.5 prepared median sec | Diagnostic ratio |
| ---: | --- | ---: | ---: | ---: |
| 250000 | count | 0.733122 | 0.011452 | 64.018x |
| 250000 | sum | 2.875404 | 0.273448 | 10.515x |
| 1000000 | count | 2.522323 | 0.007360 | 342.722x |
| 1000000 | sum | 2.755282 | 0.263002 | 10.476x |

All cases reported `matches_cpu_reference = true`.

The existing `paper_rt_optix` cases reported:

- `rt_core_accelerated = true`
- native symbol `rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction`
- phase contract `rtdl.partner.v2.4`
- no device hit-stream handoff metadata
- no true-zero-copy authorization

The v2.5 prepared cases reported:

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

The old native path is RT-core accelerated, but its recorded phase timings show that RT traversal is not the bottleneck. For example, at one million rows:

- count: `rt_traversal = 0.000207s`, while `query_preparation + materialization` is about `0.499s`;
- sum: `rt_traversal = 0.001905s`, while `query_preparation + materialization` is about `1.245s`.

That is exactly the pressure v2.5 is meant to relieve: keep generic RT traversal, but expose typed device-resident hit-stream columns so the partner continuation can consume the stream without forcing a host row bridge.

The large count ratio is especially high because the hit stream is sparse and the prepared path pays mostly native hit-stream launch, carrier handoff, and partner continuation. The sum cases are heavier because they still gather and reduce value-carrying payload columns, but they still improve by about `10.5x` against this diagnostic old path.

## Boundary

This goal does not authorize a public v2.5 speedup claim over v2.4 or v2.0. The comparison is useful but asymmetric:

- `paper_rt_optix` is an existing older native grouped-reduction path, not a prepared steady-state same-contract opponent;
- the v2.5 row is explicitly prepared and reuses app-owned workload, typed payload columns, and OptiX scene setup;
- the result is a diagnostic probe for direction, not final release parity evidence;
- true-zero-copy wording remains unauthorized, even though same-pointer Torch carrier evidence was observed for the adapter.

The next fair-comparison goal should either add a prepared old-path opponent or document why the old path cannot express the v2.5 typed hit-stream contract without becoming v2.5 itself.

