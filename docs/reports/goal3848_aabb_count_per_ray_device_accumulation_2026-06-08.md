# Goal3848: AABB Count Per-Ray Device Accumulation

Date: 2026-06-08

Status: implemented; pod validation pending final artifact sync

## Purpose

Goal3846 identified the generic OptiX `AABB_INDEX_QUERY_2D` count path as a
real large-scale performance target for the LibRTS-style benchmark. At dense
scale the prior count-only implementation used one global
`atomicAdd(params.hit_count, 1ULL)` per accepted hit. That is correct, but the
131k stress probe showed seconds-level hot work:

- baseline counts: `point_contains=743946470`,
  `range_contains=520904982`, `range_intersects=1133035386`;
- baseline `repeat_protocol.query_sec_median`: `0.6460927510634065`;
- baseline `repeat_protocol.query_sec_total`: `6.463141920976341`.

Goal3848 replaces the single global count hot spot with distributed per-ray
device counters for count-only AABB queries.

## Implementation

Touched file:

- `src/native/optix/rtdl_optix_workloads.cpp`

Key changes:

- `AabbIndexQueryLaunchParams` now includes `query_hit_counts`.
- Count-only exact accepted hits are counted inside
  `__intersection__aabb_index_exact` with
  `atomicAdd(params.query_hit_counts + qidx, 1u)`.
- Count-only intersection programs return without calling
  `optixReportIntersection`, so they avoid row-slot any-hit logic.
- `sum_device_u32_counts` downloads and sums the compact per-ray count array
  into the existing aggregate `size_t` result.
- Row collection still reports intersections into `__anyhit__aabb_index_count`,
  where `atomicAdd(params.hit_count, 1ULL)` reserves row slots and preserves
  overflow detection.
- The native symbol surface remains generic and app-agnostic.

## Validation Note

An initial validation rerun accidentally used the README smoke widths
(`--max-box-width 0.005 --max-query-width 0.005`) instead of Goal3846's default
wide fixture. That produced much smaller counts:

- `point_contains=107557`
- `range_contains=11870`
- `range_intersects=428116`

Rerunning the restored global path with those same narrow widths produced the
same smaller counts, proving the mismatch was the command, not the optimization.
The final validation must compare against the true Goal3846 default-width
fixture.

## App-Agnostic Boundary

This is a generic primitive improvement for `AABB_INDEX_QUERY_2D`. The benchmark
beneficiary is LibRTS-style spatial indexing, but the engine change is not
LibRTS-specific and does not encode a spatial-library API.

## Claim Boundary

This does not authorize release action, public speedup wording, paper
reproduction claims, or broad RT-core claims. It is internal primitive evidence
pending a committed A5000 artifact and external review.

