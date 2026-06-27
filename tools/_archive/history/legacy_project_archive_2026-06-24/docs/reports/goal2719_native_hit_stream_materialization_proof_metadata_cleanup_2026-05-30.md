# Goal2719: Native Hit-Stream Materialization-Proof Metadata Cleanup

Date: 2026-05-30
Status: accepted as metadata cleanup with pod smoke

## Purpose

Goal2715 proved the RayDB native OptiX device-column path bypasses host hit-row construction and preserves same device pointers through the Torch carrier. After that run, two metadata layers were still too conservative or too indirect:

- the OptiX native hit-stream producer still constructed handoffs with `native_device_column_output_proven_on_hardware = false`;
- the pod runner did not expose `native_device_column_output_proven_on_hardware` or `removes_host_materialization_bottleneck` at the case level.

Goal2719 cleans up that metadata so the machine-readable evidence matches the executed path.

## Changes

- `src/rtdsl/optix_runtime.py` now marks OptiX hit-stream device-column output as hardware-proven when the native device-column API succeeds and returns CUDA-resident columns.
- `src/rtdsl/hit_stream_handoff.py` now includes direct `native_device_column_output_proven_on_hardware` metadata in gather handoffs and exposes native-output/materialization status in the neutral-buffer summary.
- `scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py` now records:
  - `handoff_native_device_column_output_proven_on_hardware`
  - `handoff_removes_host_materialization_bottleneck`
- The neutral-buffer claim text now distinguishes native device-column proof from true-zero-copy/public-speedup authorization.

## Pod Smoke

Artifact:

`docs/reports/goal2719_pod_artifacts/goal2719_native_output_proven_materialization_removed_smoke_pod_69_30_85_171_2026-05-30.json`

Pod:

- host: `69.30.85.171`
- port: `22167`
- GPU: `NVIDIA RTX A5000, 570.211.01, 24564 MiB`
- commit: `e8ef0816d156675e0da52edc5e586bb94206f919`

The smoke ran one RayDB native-device-column case:

- backend: `paper_rt_optix_device_hit_stream_triton`
- rows: `10000`
- mode: `count`
- correctness: `all_correct = true`

Key evidence:

- `handoff_native_device_column_output_proven_on_hardware = true`
- `handoff_removes_host_materialization_bottleneck = true`
- `host_row_bridge_bypassed = true`
- `handoff_materializes_host_rows_for_bridge = false`
- `neutral_buffer_handoff_summary.native_device_column_output_proven_on_hardware = true`
- `neutral_buffer_handoff_summary.removes_host_materialization_bottleneck = true`
- `torch_carrier_execution.adapter_execution_proven_on_hardware = true`
- `torch_carrier_execution.same_pointer_evidence_observed = true`
- `true_zero_copy_authorized = false`
- `no_public_speedup_claim = true`

## Boundary

This cleanup authorizes the internal statement that the RayDB native OptiX device-column path removes host hit-row materialization for this path. It still does not authorize:

- public true-zero-copy wording;
- broad speedup wording;
- a claim that Torch/Triton is the only or preferred partner for every app;
- a claim that v2.5 is complete across the full benchmark suite.
