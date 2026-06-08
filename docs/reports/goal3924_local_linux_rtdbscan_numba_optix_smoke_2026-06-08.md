# Goal3924 Local Linux RTDBSCAN Numba OptiX Smoke

Date: 2026-06-08

## Purpose

Goal3924 verifies that the local Linux development machine can run the current
RTDBSCAN OptiX + Numba grouped-stream paths after rebuilding the native OptiX
library. This keeps local development useful while waiting for the next A5000
pod, and avoids spending pod time on stale-library or missing-symbol failures.

This is functional readiness evidence only. The local machine uses a GTX 1070,
so the timings are not release performance evidence and do not authorize
benchmark-speedup claims.

## Local Platform

- Host: `192.168.1.20`
- Repo: `/home/lestat/work/rtdl_codex_local_check`
- GPU: `NVIDIA GeForce GTX 1070`
- OptiX include path: `/home/lestat/vendor/optix-dev/include`
- Rebuilt library: `/home/lestat/work/rtdl_codex_local_check/build/librtdl_optix.so`
- Numba: installed in the user site with CUDA support

## Commands Run

Native rebuild:

```bash
cd /home/lestat/work/rtdl_codex_local_check
make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev
```

Unblocked grouped-stream Numba column-signature smoke:

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIBRARY=/home/lestat/work/rtdl_codex_local_check/build/librtdl_optix.so \
python3 examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py \
  --mode optix_rt_core_grouped_stream_numba_column_signature_3d \
  --dataset clustered3d \
  --point-count 1024 \
  --repeat 1 \
  --warmup 0 \
  --grouped-union-query-block-size 256 \
  --no-validation
```

Blocked grouped-stream Numba column-signature smoke:

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIBRARY=/home/lestat/work/rtdl_codex_local_check/build/librtdl_optix.so \
python3 examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py \
  --mode optix_rt_core_grouped_stream_blocked_numba_column_signature_3d \
  --dataset clustered3d \
  --point-count 1024 \
  --repeat 1 \
  --warmup 0 \
  --grouped-union-query-block-size 256 \
  --no-validation
```

## Observed Results

Both smoke runs completed successfully after the native library rebuild.

| Mode | Result | Notes |
| --- | --- | --- |
| `optix_rt_core_grouped_stream_numba_column_signature_3d` | pass | Loaded the rebuilt OptiX library and produced a stable column signature. |
| `optix_rt_core_grouped_stream_blocked_numba_column_signature_3d` | pass | Exercised the blocked query-range path with `grouped_union_query_block_count = 4`. |

The small run emitted a Numba low-occupancy warning because `point-count=1024`
only launches a tiny grid. That warning is expected for a smoke test and does
not affect the next-pod performance plan.

## Boundary

This goal does not create release performance evidence, promote the blocked
RTDBSCAN path as a default, authorize public speedup claims, authorize broad
RT-core claims, authorize true-zero-copy wording, or claim RT-DBSCAN paper
reproduction.

The required A5000 evidence remains the Goal3923 combined next-pod queue:

- Goal3913 RayJoin shared loaded-case subprobe timing.
- Goal3920 RTDBSCAN unblocked versus blocked Numba timing.

## Validation

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3924_local_linux_rtdbscan_numba_optix_smoke_test
```

Expected: all tests pass.
