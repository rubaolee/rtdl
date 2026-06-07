# Goal3770 HIPRT Prepared AABB Index Count Queries

Date: 2026-06-07

## Purpose

Goal3770 adds the generic HIPRT prepared `AABB_INDEX_QUERY_2D` count path needed
by the LibRTS spatial-index benchmark lane. It supports three count-only
operations over a prepared 2D axis-aligned bounding-box index:

- `point_contains`
- `range_contains`
- `range_intersects`

The native symbols are:

- `rtdl_hiprt_prepare_aabb_index_2d`
- `rtdl_hiprt_count_prepared_aabb_index_2d`
- `rtdl_hiprt_destroy_prepared_aabb_index_2d`

## Implementation

- Added a generic HIPRT AABB device payload and `RtdlAabbIndexCount2DKernel`.
- Added a prepared HIPRT AABB geometry handle with scalar count queries.
- Added the Python handle `PreparedHiprtAabbIndex2D`.
- Added direct `rt.prepare_hiprt_aabb_index_2d(...)`.
- Added generic dispatch through `rt.prepare_aabb_index_2d(..., backend="hiprt")`
  and `rt.query_aabb_index_2d(..., backend="hiprt")`.
- Added `prepared_aabb_query_2d` to the engine feature matrix.
- Updated the v2.10 AMD/HIPRT parity matrix so `librts_spatial_index` has no
  missing generic HIPRT contract and moves to `ready_for_amd_functional_pod`.

## Boundary

This goal is count-only. It does not add HIPRT row collection for
`AABB_INDEX_QUERY_2D`, does not claim LibRTS whole-app acceleration, and does
not claim AMD hardware validation.

Any validation on the current pod is HIPRT through CUDA/Orochi on NVIDIA
hardware. That is useful functional evidence for the HIPRT code path, but it is
not AMD hardware evidence and does not authorize release, AMD performance,
broad RT-core, whole-app speedup, paper reproduction, or public benchmark
claims.

## Validation Plan

Portable local validation:

```text
PYTHONPATH=src:. python -m unittest \
  tests.goal3770_hiprt_prepared_aabb_index_test \
  tests.goal3753_amd_hiprt_benchmark_parity_plan_test
```

Clean pod validation after commit:

```text
make build-hiprt HIPRT_PREFIX=/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
PYTHONPATH=src:. python3 -m unittest \
  tests.goal3770_hiprt_prepared_aabb_index_test \
  tests.goal3753_amd_hiprt_benchmark_parity_plan_test
```

The pod artifact will be recorded separately after the clean HIPRT build passes.
