# Goal3298 Closed-Shape Boundary-Event Device Columns

Date: 2026-06-04

Status: pod validated for device-column correctness on commit
`3517d648dcedf62bfae419b21990a84fc91fdfc3`; not release evidence and not
RayJoin reproduction evidence.

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

## Pod Validation

Validation artifact:

- `docs/reports/goal3298_closed_shape_boundary_event_device_columns_pod_2026-06-04.json`

Evidence recorded there:

- pod GPU: NVIDIA RTX A5000;
- CUDA prefix: `/usr/local/cuda-12.8`;
- OptiX prefix: `/root/vendor/optix-sdk`;
- CuPy version: `14.1.1`;
- native build: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk
  CUDA_PREFIX=/usr/local/cuda-12.8`, status `pass`;
- focused live tests: 22 run, 0 skipped, status `pass`;
- live smoke: CuPy readback from the device-resident columns exactly matches
  `rt.point_closed_shape_first_boundary_crossing_2d_cpu`;
- device pointers: all seven output columns nonzero;
- representative event: point `10`, shape `7`, boundary `3`, crossing
  `(0.0, 2.0)`, `crossing_t=2.0`, `event_kind=1`;
- phase telemetry: mode `boundary_event_device_columns`, raw candidates `1`,
  emitted rows `1`, candidate download `0.0`.

This validates the native ABI, Python binding, typed metadata, CuPy
consumer-view path, and small live correctness smoke for resident boundary
columns. It still does not validate grouped continuation or RayJoin same-slice
performance.

## Next Step

If the device-column producer validates, the next useful slice is a generic
device-resident continuation over this stream, such as grouped counts or caller
selected compact summaries. That continuation should still be generic and
should not encode RayJoin-specific map or closest-edge interpretation.
