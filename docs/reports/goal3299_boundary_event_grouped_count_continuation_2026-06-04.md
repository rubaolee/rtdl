# Goal3299 Boundary-Event Grouped Count Continuation

Date: 2026-06-04

Status: pod validated for continuation correctness on commit
`c44e548162567967a15936d1fd430c591c88c403`; not release evidence and not
RayJoin reproduction evidence.

## Purpose

Goal3298 produces generic point/closed-shape boundary-event columns on the
OptiX CUDA device. Goal3299 adds the next generic continuation: count those
events by the `point_id` column while keeping the dense count output on device.

This is intentionally not a RayJoin-specific classifier. It is a reusable
device-resident grouped-count continuation over a typed event stream.

## Implemented Slice

Added:

- `OptixClosedShapeBoundaryEventDeviceColumnOutput.grouped_count_by_point_id_device_columns(...)`

The method uses the existing generic resident columnar grouped-count primitive:

- `rtdl_optix_columnar_device_payload_grouped_count_i64_device_columns_with_capacity`

No new native app-specific kernel was added.

## Boundaries

This goal proves a generic grouped-count continuation over boundary-event
device columns.

It does not encode RayJoin polygon assignment, map-id interpretation, or
simulation-of-simplicity policy.

It does not prove true zero-copy.

It does not authorize release.

It does not authorize public speedup wording.

It does not authorize broad RT-core speedup wording.

It does not authorize RayJoin reproduction.

RayJoin-specific native logic added: false.

## Pod Validation

Validation artifact:

- `docs/reports/goal3299_boundary_event_grouped_count_continuation_pod_2026-06-04.json`

Evidence recorded there:

- pod GPU: NVIDIA RTX A5000;
- CuPy version: `14.1.1`;
- focused live tests: 9 run, 0 skipped, status `pass`;
- boundary-event stream residency: `device_resident_boundary_event_columns`;
- grouped-count output residency: `device_resident_dense_grouped_count_column`;
- dense count result: point `10` count `1`, point `20` count `0`;
- event telemetry: mode `boundary_event_device_columns`, candidate download
  `0.0`, emitted rows `1`;
- grouped count reduction time: `2.1084e-05` seconds.

This validates that a generic resident boundary-event stream can feed a
generic resident grouped-count continuation. It still does not validate
RayJoin polygon assignment, simulation-of-simplicity policy, whole-workload
performance, or release readiness.

## Next Step

The next performance step is a same-slice RayJoin PIP experiment that uses the
resident boundary-event stream plus grouped continuation where the contract is
actually equivalent. If the app requires extra caller interpretation, that
logic must remain outside the native engine.
