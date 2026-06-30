# Goal3848: AABB Count Per-Ray Device Accumulation

Date: 2026-06-08

Status: implemented and A5000-validated

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
same smaller counts in-session, supporting the interpretation that the mismatch
was a command/fixture-width mismatch rather than the optimization. The exact
bad-run command transcript was not preserved, so this note is explanatory
rather than release evidence. The accepted validation evidence is the committed
default-width A5000 artifact below, which compares directly against the true
Goal3846 fixture.

## A5000 Validation

Artifact:

- `docs/reports/goal3848_aabb_per_ray_device_a5000/librts_131k_repeat10_per_ray_device_defaults.json`

Validation command used Goal3846's default widths:

```bash
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
python examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py \
  --mode optix_aabb_index --dataset uniform --box-count 131072 \
  --query-count 131072 --seed 2025 --operation all --repeat 10 --warmup 2
```

Results:

| Metric | Goal3846 baseline | Goal3848 per-ray counters | Ratio |
| --- | ---: | ---: | ---: |
| `point_contains` count | 743946470 | 743946470 | exact |
| `range_contains` count | 520904982 | 520904982 | exact |
| `range_intersects` count | 1133035386 | 1133035386 | exact |
| `repeat_protocol.query_sec_median` | 0.646092751 | 0.563984715 | 1.1456x |
| `repeat_protocol.query_sec_total` | 6.463141921 | 5.642192487 | 1.1455x |

Per-operation medians changed as follows:

| Operation | Goal3846 baseline | Goal3848 per-ray counters | Ratio |
| --- | ---: | ---: | ---: |
| `point_contains` | 0.155771718 | 0.133414827 | 1.1676x |
| `range_contains` | 0.165047798 | 0.143535357 | 1.1499x |
| `range_intersects` | 0.325273235 | 0.287034532 | 1.1332x |

The stderr artifact is empty.

## App-Agnostic Boundary

This is a generic primitive improvement for `AABB_INDEX_QUERY_2D`. The benchmark
beneficiary is LibRTS-style spatial indexing, but the engine change is not
LibRTS-specific and does not encode a spatial-library API.

## Claim Boundary

This does not authorize release action, public speedup wording, paper
reproduction claims, or broad RT-core claims. It is internal primitive evidence
pending external review.
