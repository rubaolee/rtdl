# Goal3848: AABB Count Per-Ray Device Accumulation

Date: 2026-06-08

Status: local implementation pending pod timing

## Purpose

Goal3846 identified the generic OptiX `AABB_INDEX_QUERY_2D` count path as the
next plausible large-scale performance target for the LibRTS-style benchmark.
At dense scales the existing count-only path used one global `atomicAdd` per
accepted hit. For large AABB query batches this can mean hundreds of millions
of contended global atomics even when the caller only wants aggregate counts.

The first attempted implementation used an OptiX payload register as a per-ray
hit accumulator. Pod validation rejected that version because it undercounted
the dense 131k stress case, so the final Goal3848 design is more conservative:
use one device counter per launched ray and sum those counters after traversal.

This goal changes the generic count-only kernel behavior:

- count-only launches accumulate accepted hits into a distributed
  `query_hit_counts[payload_idx]` device array instead of one contended global
  counter;
- the host downloads the compact per-ray `uint32` count array and sums it into
  the existing aggregate `size_t` result;
- row-output launches keep the existing row-index atomic path because row
  collection needs stable output slots;
- the native symbol surface remains generic and app-agnostic;
- no LibRTS-specific native symbol or app term is introduced.

## Implementation

Touched file:

- `src/native/optix/rtdl_optix_workloads.cpp`

Key changes:

- `AabbIndexQueryLaunchParams` now includes `query_hit_counts`.
- `__anyhit__aabb_index_count` increments `query_hit_counts + payload_idx`
  when `collect_rows == 0`.
- `sum_device_u32_counts` downloads and sums the compact per-ray counts.
- Row collection still uses `atomicAdd(params.hit_count, 1ULL)` to reserve row
  slots and preserve overflow detection.
- The AABB pipeline payload count stays at `1`.

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
  --repeat 10 --warmup 2
```

Compare the result with Goal3846's `librts_131k_repeat10` baseline:

- `repeat_protocol.query_sec_median`: `0.6460927510634065`
- `repeat_protocol.query_sec_total`: `6.463141920976341`
