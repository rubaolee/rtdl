# Goal3760 Spatial RayJoin Native-PIP Adequacy Correction

Date: 2026-06-07

## Purpose

The current benchmark adequacy matrix still described `spatial_rayjoin` as if
its recommended PIP scalar-count leg were the older CuPy dense CUDA-core route.
That was stale after the native relation-status corrected scalar-count executor
work.

Goal3760 corrects the source-of-truth matrix to separate three facts:

1. Older cross-size safe-mixed packets still include a CuPy dense PIP leg.
2. The current Goal3713 native-PIP packet replaces that PIP leg with a generic
   RTDL/OptiX resident scalar-count executor on the measured 4096 public-CDB
   packet.
3. CuPy remains an important baseline/opponent and user-selectable partner, but
   it is no longer the only documented route for the PIP scalar-count leg.

## Evidence

Key artifacts:

- `docs/reports/goal3688_rayjoin_native_pip_safe_mixed_composite_a5000/summary.json`
- `docs/reports/goal3713_rayjoin_native_pip_current_composite_a5000/summary.json`
- `docs/reports/goal3737_rayjoin_safe_mixed_executor_cross_size_a5000/summary.json`

Goal3713 evidence:

| Contract | Count/parity | Timing result |
| --- | --- | --- |
| PIP scalar count | `11316`, matches dense all-CuPy baseline | native scalar-count executor is `>2.5x` faster than CuPy PIP leg |
| Current native-PIP composite | all counts match | `268.798x` versus dense all-CuPy same-contract baseline |

Goal3737 evidence remains useful but older for the PIP leg:

- cross-size safe-mixed geomean: `324.324x` versus all-CuPy,
- that packet still labels its PIP route as `recommended_cupy_dense_pip_scalar_count`.

## Matrix Update

The active matrix version is now:

`rtdl.v2_9.benchmark_adequacy_after_goal3760.v1`

The `spatial_rayjoin` row now states:

- current recommended path: RTDL/OptiX resident scalar-count PIP where measured,
  exact RTDL/OptiX prepared segment-pair count for LSI, and RTDL/OptiX
  prepared-left shape-pair active-count executor for overlay active count;
- partner role: CuPy is the dense CUDA-core baseline/opponent and appears in
  older cross-size packets, while Goal3749 covers no-RawKernel Numba topology
  continuation;
- next work: larger native-PIP whole-RayJoin packet refresh and HIPRT parity.

## Boundary

This is a matrix correction, not a release packet. It does not authorize public
speedup wording, whole-app acceleration wording, broad RT-core wording, RayJoin
paper-reproduction wording, RTDL-beats-RayJoin wording, true-zero-copy wording,
automatic partner selection, or app-specific native engine logic.
