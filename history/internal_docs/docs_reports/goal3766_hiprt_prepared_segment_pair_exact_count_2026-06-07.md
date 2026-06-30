# Goal3766 HIPRT Prepared Segment-Pair Exact Count

Date: 2026-06-07

## Purpose

Goal3766 closes the first RayJoin-shaped HIPRT parity gap without adding
RayJoin-specific native logic. The new contract is a generic prepared
right-side 2D segment scene plus a scalar exact-count query over left-side 2D
segments.

The new native symbols are:

- `rtdl_hiprt_prepare_segment_pair_intersection`
- `rtdl_hiprt_count_prepared_segment_pair_intersection`
- `rtdl_hiprt_destroy_prepared_segment_pair_intersection`

The Python-facing prepared handle is:

- `prepare_hiprt_segment_pair_intersection_2d`
- `PreparedHiprtSegmentPairIntersection2D.count(left_segments)`

## Implementation

- Added `PreparedSegmentPairIntersection2D` to retain the right-side segment
  payload, AABB geometry, HIPRT function table, and lazily compiled count
  kernel.
- Added `RtdlSegmentPairIntersectionCount2DKernel`, which traverses the
  prepared right-side geometry for each left segment and atomically accumulates
  the exact hit count.
- Added the C ABI prepare/count/destroy trio.
- Added the Python prepared handle and context-manager lifecycle.
- Added `prepared_segment_pair_exact_count_2d` to the engine feature matrix.
- Updated the v2.10 AMD/HIPRT parity matrix: `spatial_rayjoin` no longer lists
  `prepared_segment_pair_exact_count` as missing, but it remains blocked on
  `prepared_shape_pair_active_count` and AMD hardware evidence.

## Evidence

Artifact:

`docs/reports/goal3766_hiprt_prepared_segment_pair_exact_count_a5000.json`

Environment:

- GPU: NVIDIA RTX A5000
- Source commit: `6968b19c`
- Scoped source dirty: `false`
- HIPRT SDK: `/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`
- Backend route: HIPRT through CUDA/Orochi on NVIDIA hardware

Clean validation from `/root/rtdl_goal3766_clean`:

```text
make build-hiprt HIPRT_PREFIX=/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
python3 -m unittest \
  tests.goal3766_hiprt_prepared_segment_pair_count_test \
  tests.goal3765_hiprt_prepared_grouped_anyhit_flags_test \
  tests.goal674_hiprt_prepared_anyhit_2d_test \
  tests.goal3753_amd_hiprt_benchmark_parity_plan_test
```

Result:

- 23 tests passed.
- The clean source commit was `6968b19c`.
- The scoped source status was clean.

Correctness sample:

- HIPRT row path count: `3`
- HIPRT prepared scalar count: `3`
- Match: `true`

## Boundary

This is functional NVIDIA CUDA/Orochi HIPRT evidence. It is not AMD hardware
evidence and does not authorize release, AMD performance, broad RT-core,
whole-app speedup, paper reproduction, or public benchmark claims.

`spatial_rayjoin` remains in `needs_generic_hiprt_extension` because the fast
route still needs prepared shape-pair active-count parity and actual AMD pod
validation.

## Next Step

The next HIPRT parity target should be `prepared_shape_pair_active_count`: a
generic prepared shape-pair active-count/summary contract, still app-agnostic,
so the RayJoin parity lane can move from partial prepared-count support toward
the same higher-level route shape used by OptiX.
