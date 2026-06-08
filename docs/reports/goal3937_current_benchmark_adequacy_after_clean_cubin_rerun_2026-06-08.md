# Goal3937 Current Benchmark Adequacy After Clean CUBIN Rerun

Date: 2026-06-08

## Purpose

Goal3937 moves the machine-readable current benchmark adequacy pointer forward after the Goal3933/3936 OptiX CUBIN repair chain.

This is a project-level status update, not another app-specific tuning pass. The important design point is:

- users choose partners explicitly;
- RTDL recommends primitive-first when a fused generic primitive wins;
- Numba is the no-RawKernel reference partner when custom scalar logic wins;
- slow or bounded candidates are not promoted just because they are more RT-shaped.

## What Changed

- `CURRENT_BENCHMARK_ADEQUACY_VERSION` now points to `rtdl.v2_10.benchmark_adequacy_after_goal3936.v1`.
- The `spatial_rayjoin` adequacy row now cites the clean Goal3936 post-commit rerun.
- The RayJoin current scale-profile row now lists Goal3936 as evidence.
- The row explicitly records the current mixed route:
  - PIP one-shot: Numba preferred on the bounded public-CDB slice.
  - PIP repeated requests: RTDL/OptiX prepared batch executor.
  - LSI scalar count: RTDL/OptiX prepared segment-pair count.
  - Overlay active count: RTDL/OptiX prepared shape-pair active count.
- RTDBSCAN blocked grouped-stream mode remains unpromoted because the clean queue confirms it is slower than the unblocked mode.

## Current RayJoin Evidence From Goal3936

| Contract | Current Reading |
| --- | --- |
| Source hygiene | clean `main` checkout, commit `cd7fa65f`, empty `source_dirty` |
| PIP one-shot | RTDL/OptiX is `0.247x` versus Numba; choose Numba for this bounded scalar count |
| PIP repeated requests | RTDL/OptiX prepared batch executor is `0.155315ms/request` at 100 requests |
| LSI scalar count | RTDL/OptiX is `252.436x` versus Numba |
| Overlay active count | RTDL/OptiX is `202.372x` versus Numba |

## Boundary

This does not authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, true-zero-copy wording, automatic partner selection, RayJoin paper reproduction, RTDBSCAN paper reproduction, or app-specific native-engine logic.

The conclusion is narrower and more useful: current RTDL is becoming a language/runtime with explicit high-performance route choices. The next major performance work should continue at the primitive/runtime level rather than micro-tuning individual apps.
