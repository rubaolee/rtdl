# Goal3768 HIPRT Fixed-Radius Threshold Count

Date: 2026-06-07

## Purpose

Goal3768 adds a generic HIPRT prepared fixed-radius scalar threshold-count
primitive for 3D point workloads. Given a prepared search-point set and a query
batch, it counts how many query points have at least `threshold` neighbors
inside the prepared radius, without materializing neighbor rows.

The new native symbol is:

`rtdl_hiprt_count_prepared_fixed_radius_threshold_reached_3d`

The Python-facing method is:

`PreparedHiprtFixedRadiusNeighbors3D.count_threshold_reached(query_points, threshold=...)`

## Implementation

- Added `RtdlFixedRadiusThresholdReachedCount3DKernel`.
- Added a lazy `threshold_count_kernel` field to `PreparedFixedRadiusNeighbors3D`.
- Added a C ABI scalar count function over the existing prepared fixed-radius
  handle.
- Added the Python method used by generic prepared fixed-radius sessions.
- Added `fixed_radius_threshold_reached_count_3d` to the engine feature matrix.
- Updated the v2.10 AMD/HIPRT parity matrix to record RT-DBSCAN progress while
  preserving the remaining `fixed_radius_grouped_stream_flags` blocker.

## Evidence

Artifact:

`docs/reports/goal3768_hiprt_fixed_radius_threshold_count_a5000.json`

Environment:

- GPU: NVIDIA RTX A5000
- Source commit: `522d3e2a`
- Scoped source dirty: `false`
- HIPRT SDK: `/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`
- Backend route: HIPRT through CUDA/Orochi on NVIDIA hardware

Clean validation from `/root/rtdl_goal3768_clean`:

```text
make build-hiprt HIPRT_PREFIX=/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
python3 -m unittest \
  tests.goal3768_hiprt_fixed_radius_threshold_count_test \
  tests.goal566_hiprt_prepared_nn_test \
  tests.goal3753_amd_hiprt_benchmark_parity_plan_test
```

Result:

- 13 tests passed.
- The clean source commit was `522d3e2a`.
- The scoped source status was clean.

Correctness sample:

- Threshold: `3`
- Expected threshold-reaching query count from prepared rows: `3`
- HIPRT prepared scalar threshold count: `3`
- Match: `true`

## Boundary

This is a scalar threshold-count primitive, not full RT-DBSCAN acceleration.
It does not provide per-query grouped/core flags, component labeling, or
cluster expansion. The `rt_dbscan` parity row therefore remains
`needs_generic_hiprt_extension` with `fixed_radius_grouped_stream_flags` still
missing.

This is NVIDIA CUDA/Orochi HIPRT evidence, not AMD hardware evidence. It does
not authorize release, AMD performance, broad RT-core, whole-app speedup, paper
reproduction, or public benchmark claims.

## Next Step

The next RT-DBSCAN HIPRT target should be a generic per-query fixed-radius flag
stream or compact core-flag output, followed by a partner/runtime continuation
for component labeling. That would be the real contract needed to move
`rt_dbscan` toward AMD functional pod readiness.
