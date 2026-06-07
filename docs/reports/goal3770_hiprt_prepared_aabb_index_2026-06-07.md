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

## Evidence

Artifact:

`docs/reports/goal3770_hiprt_prepared_aabb_index_a5000.json`

Environment:

- GPU: NVIDIA RTX A5000
- Source commit: `75d19c76`
- Scoped source dirty: `false`
- HIPRT SDK: `/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`
- Backend route: HIPRT through CUDA/Orochi on NVIDIA hardware

Portable local validation passed before the pod commit:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal3770_hiprt_prepared_aabb_index_test \
  tests.goal3753_amd_hiprt_benchmark_parity_plan_test
```

Result:

- 14 tests passed.
- 1 local native-HIPRT test skipped because the Windows library was not loaded.

Clean pod validation from `/root/rtdl_goal3770_clean`:

```text
make build-hiprt HIPRT_PREFIX=/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
PYTHONPATH=src:. python3 -m unittest \
  tests.goal3770_hiprt_prepared_aabb_index_test \
  tests.goal3753_amd_hiprt_benchmark_parity_plan_test
```

Result:

- 14 tests passed.
- 0 tests skipped.
- The clean source commit was `75d19c76`.
- The scoped source status was clean.

Correctness sample:

- Indexed boxes: `3`
- Point queries: `3`
- Box queries: `3`
- CPU counts: `point_contains=3`, `range_contains=1`, `range_intersects=5`
- HIPRT direct counts: `point_contains=3`, `range_contains=1`, `range_intersects=5`
- HIPRT generic-dispatch counts: `point_contains=3`, `range_contains=1`, `range_intersects=5`
- Direct and generic HIPRT counts matched the CPU reference.

## Parity Position

After Goal3770, the `librts_spatial_index` HIPRT row in the v2.10 AMD/HIPRT
parity matrix has no missing generic contracts and is marked
`ready_for_amd_functional_pod`.

The overall parity matrix is now:

- `ready_for_amd_functional_pod`: 4 apps
- `needs_generic_hiprt_extension`: 4 apps
- `compatibility_only_not_amd_perf_ready`: 2 apps
