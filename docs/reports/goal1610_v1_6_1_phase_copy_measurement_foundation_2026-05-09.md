# Goal1610 v1.6.1 Phase/Copy Measurement Foundation

Date: 2026-05-09

## Verdict

Goal1610 starts the `v1.6.1` measurement-foundation track.

The deliverable is a local, source-tree runner that records a standard
phase/copy schema before any new optimization or paid NVIDIA pod run:

- script: `scripts/goal1610_v1_6_1_phase_copy_measurement.py`
- test: `tests/goal1610_v1_6_1_phase_copy_measurement_test.py`
- default smoke artifact:
  `docs/reports/goal1610_v1_6_1_phase_copy_measurement_smoke_2026-05-09.json`

This is a measurement foundation, not a performance claim.

## Why This Exists

The v1.6.x roadmap requires measurement before optimization. Previous OptiX and
collect-k work showed that total time can hide different bottlenecks:

- scene preparation;
- probe/ray packing;
- host/device transfers;
- launch/setup;
- native traversal;
- output transfer;
- Python row materialization;
- validation;
- Python continuation.

Goal1610 provides the common record shape future goals should extend rather
than inventing another one-off profiler.

## Schema

Required phase fields:

- `input_construction_sec`
- `scene_preparation_sec`
- `probe_packing_sec`
- `host_to_device_transfer_sec`
- `launch_sec`
- `traversal_sec`
- `device_to_host_transfer_sec`
- `output_materialization_sec`
- `validation_sec`
- `python_continuation_sec`
- `query_and_materialize_sec`
- `total_wrapper_sec`

Required copy/materialization fields:

- `input_materialization_count`
- `output_materialization_count`
- `host_to_device_copy_count`
- `device_to_host_copy_count`
- `python_row_count`
- `thin_view_count`
- `prepared_buffer_reuse_count`

Fields may be `null` when a local smoke case cannot observe that phase yet.
They must still be present so later Embree/OptiX profilers do not drift.

## Local Smoke Case

The first included case is:

```text
hausdorff_cpu_reference_smoke
```

It runs:

```text
python examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
```

This case is portable and has app-level `run_phases`, so it is useful for local
schema validation without requiring Embree, OptiX, or a pod.

## Claim Boundary

Goal1610 does not authorize:

- public speedup wording;
- whole-app speedup wording;
- broad RTX/GPU wording;
- true zero-copy wording;
- stable `COLLECT_K_BOUNDED` promotion;
- partner tensor handoff claims;
- package-install claims;
- release tags or release action.

## Next Step

Goal1611 should attach this schema to a prepared host-output path so the next
measurement package can compare compatibility rows versus prepared/thin output
without changing public claims.
