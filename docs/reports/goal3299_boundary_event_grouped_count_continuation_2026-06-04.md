# Goal3299 Boundary-Event Grouped Count Continuation

Date: 2026-06-04

Status: local implementation slice; pod validation required before using as
continuation evidence.

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

## Required Pod Validation

Before this goal is accepted as implementation evidence:

1. build `librtdl_optix.so` from current main on a pod;
2. run `tests.goal3299_boundary_event_grouped_count_continuation_test` with
   `RTDL_OPTIX_LIBRARY` set;
3. confirm a device-resident boundary-event stream feeds a device-resident
   grouped-count output;
4. record
   `docs/reports/goal3299_boundary_event_grouped_count_continuation_pod_2026-06-04.json`.

## Next Step

The next performance step is a same-slice RayJoin PIP experiment that uses the
resident boundary-event stream plus grouped continuation where the contract is
actually equivalent. If the app requires extra caller interpretation, that
logic must remain outside the native engine.
