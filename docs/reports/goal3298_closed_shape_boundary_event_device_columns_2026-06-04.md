# Goal3298 Closed-Shape Boundary-Event Device Columns

Date: 2026-06-04

Status: local implementation slice; pod validation required before using as
performance or residency evidence.

## Purpose

Goal3297 proved the generic point/closed-shape first-boundary-event contract
through host-materialized OptiX rows. Goal3298 moves the same contract one step
closer to the RayJoin-style fast path by producing the boundary-event stream as
device-resident columns.

The implementation remains generic. It exposes point, shape, boundary, crossing
coordinate, and event-kind columns. It does not expose RayJoin-specific edge
selection names, map semantics, polygon assignment policy, or paper-system
logic.

## Implemented Slice

Added a native device-column carrier:

- `RtdlNativeClosedShapeBoundaryEventDeviceColumns`

Added prepared OptiX symbols:

- `rtdl_optix_prepared_point_closed_shape_first_boundary_crossing_device_columns_2d`
- `rtdl_optix_release_point_closed_shape_boundary_event_device_columns_2d`

The existing generic boundary-event OptiX kernel now supports two output modes:

- host row output from Goal3297;
- device-resident structure-of-arrays output from Goal3298.

Device columns:

- `point_id`
- `shape_id`
- `boundary_id`
- `crossing_t`
- `crossing_x`
- `crossing_y`
- `event_kind`

Telemetry mode:

- `boundary_event_device_columns` (`7`)

## Python Surface

Added:

- `PreparedOptixPointClosedShapeMembership2D.first_boundary_crossing_device_columns(...)`
- `OptixClosedShapeBoundaryEventDeviceColumnOutput`

The output wrapper reports v2.8 typed geometry-relation metadata with CUDA
column pointers and offers `as_cupy_columns()` for caller-selected partner
continuation. CuPy is a consumer convenience, not hidden dispatch and not a
required partner choice.

## Boundaries

This goal produces device-resident boundary-event columns.

It does not yet add the grouped/count continuation over those columns.

It does not prove true zero-copy.

It does not authorize release.

It does not authorize public speedup wording.

It does not authorize broad RT-core speedup wording.

It does not authorize RayJoin reproduction.

RayJoin-specific native logic added: false.

## Required Pod Validation

Before this goal is accepted as implementation evidence:

1. build `librtdl_optix.so` from this commit on a pod;
2. run `tests.goal3298_closed_shape_boundary_event_device_columns_test` with
   `RTDL_OPTIX_LIBRARY` set;
3. validate the device columns against
   `rt.point_closed_shape_first_boundary_crossing_2d_cpu`;
4. record the pod artifact at
   `docs/reports/goal3298_closed_shape_boundary_event_device_columns_pod_2026-06-04.json`.

## Next Step

If the device-column producer validates, the next useful slice is a generic
device-resident continuation over this stream, such as grouped counts or caller
selected compact summaries. That continuation should still be generic and
should not encode RayJoin-specific map or closest-edge interpretation.
