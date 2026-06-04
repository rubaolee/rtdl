# Goal3329: OptiX Device Pair-Column CuPy Adapter

Date: 2026-06-04

Status: generic adapter ergonomics. This does not authorize release, public speedup, true zero-copy, or app-specific engine claims.

## Purpose

Goals 3327-3328 used generic point/closed-shape device pair columns to diagnose RayJoin CDB count mismatches. That probe had to manually wrap `left_ids_device_ptr` and `right_ids_device_ptr` with CuPy `UnownedMemory` because `OptixNativeDevicePairColumnOutput` did not expose the same public CuPy adapter shape already available on richer boundary-event streams.

Goal3329 adds that missing generic convenience:

- `OptixNativeDevicePairColumnOutput.as_cupy_columns()`

It returns a dictionary keyed by the output's `field_names`, such as `point_id` and `shape_id` for point/closed-shape membership candidate columns.

## Boundary

The helper wraps already-produced native device columns. It does not:

- create a new native primitive,
- change traversal/filter semantics,
- add RayJoin-specific behavior,
- authorize true zero-copy claims for the broader pipeline,
- keep arrays valid after the owning native output is closed.

The method is deliberately generic because `OptixNativeDevicePairColumnOutput` is used for id-pair streams, not for one application.

## Validation

Local tests confirm:

- the public method exists,
- it uses the output's declared `field_names`,
- it preserves the existing false `true_zero_copy_authorized` boundary,
- it retains overflow/device-pointer guards before wrapping.

Pod execution is not required for this narrow Python adapter change, but the method is directly motivated by the A5000 Goal3327 diagnostic path.
