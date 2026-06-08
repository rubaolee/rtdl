# Goal3848: AABB Count Payload-Local Accumulation

Date: 2026-06-08

Status: local implementation pending pod timing

## Purpose

Goal3846 identified the generic OptiX `AABB_INDEX_QUERY_2D` count path as the
next plausible large-scale performance target for the LibRTS-style benchmark.
At dense scales the existing count-only path used one global `atomicAdd` per
accepted hit. For large AABB query batches this can mean hundreds of millions
of contended global atomics even when the caller only wants aggregate counts.

This goal changes the generic count-only kernel behavior:

- count-only launches accumulate accepted hits in an OptiX payload register per
  ray and perform one aggregate add per ray;
- row-output launches keep the existing row-index atomic path because row
  collection needs stable output slots;
- the native symbol surface remains generic and app-agnostic;
- no LibRTS-specific native symbol or app term is introduced.

## Implementation

Touched file:

- `src/native/optix/rtdl_optix_workloads.cpp`

Key changes:

- `__raygen__aabb_index_query` now passes two payload registers to
  `optixTrace` for count-only launches.
- `trace_aabb_index_segment` now accumulates segment-query hits in payload
  register 1 and performs one aggregate add after traversal returns.
- `__anyhit__aabb_index_count` increments payload register 1 when
  `collect_rows == 0`.
- Row collection still uses `atomicAdd(params.hit_count, 1ULL)` to reserve row
  slots and preserve overflow detection.
- The AABB pipeline payload count is raised from `1` to `2`.

## App-Agnostic Boundary

This is a generic primitive improvement for `AABB_INDEX_QUERY_2D`. The benchmark
beneficiary is LibRTS-style spatial indexing, but the engine change is not
LibRTS-specific and does not encode a spatial-library API.

## Claim Boundary

This does not authorize release action, public speedup wording, paper
reproduction claims, or broad RT-core claims. It is an internal primitive
optimization pending A5000 timing and correctness evidence.

## Next Validation

Run on the A5000 pod after rebuilding `librtdl_optix.so`:

```bash
make build-optix
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
python examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py \
  --mode optix_aabb_index --dataset uniform --box-count 131072 \
  --query-count 131072 --seed 2025 --operation all \
  --query-repeat 10 --query-warmup 2
```

Compare the result with Goal3846's `librts_131k_repeat10` baseline:

- `repeat_protocol.query_sec_median`: `0.6460927510634065`
- `repeat_protocol.query_sec_total`: `6.463141920976341`

