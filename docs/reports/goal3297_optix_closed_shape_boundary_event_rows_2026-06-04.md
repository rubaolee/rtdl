# Goal3297 OptiX Closed-Shape Boundary-Event Rows

Date: 2026-06-04

Status: implementation in progress; pod validation required before using as
performance evidence.

## Purpose

Goal3296 created the generic contract for point/closed-shape first boundary
crossing events. This goal starts the native OptiX implementation of that
contract.

The important distinction from the existing membership path is:

- membership count answers whether the point/shape predicate is positive;
- boundary-event selection emits the representative boundary event that a
  caller may use for its own classification or grouping.

This follows the RayJoin lesson without copying RayJoin-specific names or
application logic into RTDL.

## Implemented Slice

Added a generic C ABI row:

- `RtdlPointClosedShapeBoundaryEventRow`

Added a prepared OptiX symbol:

- `rtdl_optix_run_prepared_point_closed_shape_first_boundary_crossing_2d`

Added a separate OptiX pipeline:

- `kPointClosedShapeBoundaryEventKernelSrc`
- `__raygen__point_closed_shape_boundary_event_probe`
- `__intersection__point_closed_shape_boundary_event_isect`
- `__anyhit__point_closed_shape_boundary_event_anyhit`

The pipeline traces an upward point ray through the prepared closed-shape AABB
scene, scans the prepared edge range for each intersected shape, and emits
host-materialized generic boundary-event rows:

- `point_id`
- `shape_id`
- `boundary_id`
- `crossing_t`
- `crossing_x`
- `crossing_y`
- `event_kind`

The first implementation uses a two-pass count/write launch so it does not
allocate `point_count * shape_count` rows up front.

## Python Surface

Added methods on `PreparedOptixPointClosedShapeMembership2D`:

- `first_boundary_crossing_raw(points)`
- `first_boundary_crossing(points)`

The returned row view uses the v2.8 typed geometry relation schema from
Goal3296:

- `point_closed_shape_boundary_event_2d_columns`

## Boundaries

This goal produces host-materialized generic boundary-event rows.

It is not device-resident boundary-event columns.

It is not true zero-copy.

It is not a release gate.

It does not authorize release.

It does not authorize public speedup wording.

It does not authorize RT-core speedup wording.

It does not authorize RayJoin reproduction.

RayJoin-specific native logic added: false.

## Required Validation

Before this goal is accepted as implementation evidence:

1. build `librtdl_optix.so` from this commit on a pod;
2. run the focused Goal3297 unit test with `RTDL_OPTIX_LIBRARY` set;
3. run a tiny live parity smoke against
   `rt.point_closed_shape_first_boundary_crossing_2d_cpu`;
4. record the artifact at
   `docs/reports/goal3297_optix_closed_shape_boundary_event_rows_pod_2026-06-04.json`;
5. only then compare against the Goal3294/Goal3295 RayJoin same-slice harness.

## Next Step After Correctness

If the row ABI is correct, the next optimization should add device-resident
boundary-event columns and a grouped/count continuation. The row ABI is a
correctness and schema step, not the final high-performance route.
