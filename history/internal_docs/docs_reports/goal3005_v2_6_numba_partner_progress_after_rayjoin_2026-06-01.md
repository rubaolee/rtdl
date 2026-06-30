# Goal3005: v2.6 Numba Partner Progress After RayJoin

## Position

v2.6 is now an internal development lane for first-class, user-selected Numba partner support. It is not a release lane yet.

The design rule remains:

> Users choose the partner. RTDL provides high-performance, generic, app-agnostic primitives and honest reference implementations for supported partners.

Triton remains paused for recommended paths because v2.5 same-contract evidence showed it was not the right default for the fused benchmark paths. Numba is the current first-class partner lane.

## Completed Numba Evidence

| Goal | Scope | Evidence | Status |
| --- | --- | --- | --- |
| Goal2990 | Neutral CuPy/Numba handoff contract | Local tests | accepted as N-0 foundation |
| Goal2993 | Numba neutral handoff on L4 | L4 pod artifact | conformance pass |
| Goal2994 | RayDB-style count/sum Numba continuation | L4 pod artifact | conformance pass |
| Goal2995 | RayDB-style count/sum/min/max/avg-as-sum-count | L4 pod artifact | conformance pass |
| Goal2997 | Generic `compact_mask_i64` | L4 pod artifact | conformance pass |
| Goal2999 | Triangle-counting compact-mask app wiring | Local tests | prepared |
| Goal3000 | Triangle-counting compact-mask app wiring | L4 pod artifact | conformance pass |
| Goal3001 | Gemini review of Goal2999/3000 | External review | `accept-with-boundary` |
| Goal3002 | RayJoin compact-mask app wiring | Local tests | prepared |
| Goal3003 | RayJoin compact-mask app wiring across `pip`, `lsi`, `overlay_seed` | L4 pod artifact | conformance pass |
| Goal3004 | Gemini review of Goal3002/3003 | External review | `accept-with-boundary` |

## Generic Primitives Demonstrated

| Primitive | Partner | App Surfaces |
| --- | --- | --- |
| `segmented_count_i64` | Numba | RayDB-style scalar grouped aggregate |
| `segmented_sum_f64` | Numba | RayDB-style scalar grouped aggregate |
| `segmented_min_f64` | Numba | RayDB-style scalar grouped aggregate |
| `segmented_max_f64` | Numba | RayDB-style scalar grouped aggregate |
| `compact_mask_i64` | Numba | Triangle-counting witness rows, RayJoin row streams |

## Toolchain Lesson

The L4 pod exposed a real deployment issue: when `numba-cuda` is installed into a `--target` directory, Python does not automatically process `_numba_cuda_redirector.pth`. Without that redirector, `from numba import cuda` can resolve to the legacy in-tree Numba CUDA module and fail on driver/toolkit PTX compatibility.

RTDL now explicitly activates `_numba_cuda_redirector` in the generic Numba continuation helper and in pod runners before importing `numba.cuda`.

## Claim Boundary

None of this authorizes:

- v2.6 release;
- public speedup wording;
- Numba speedup wording;
- RT-core speedup wording;
- whole-app speedup wording;
- true-zero-copy wording;
- automatic partner selection;
- app-specific native-engine logic;
- RayJoin paper-reproduction or `RTDL beats RayJoin` claims.

## Next Useful Work

1. Pick the next benchmark app where Numba can do real generic continuation work.
2. Prefer app surfaces that reuse existing primitives before adding new primitives.
3. Add performance comparisons only after same-contract baselines and claim boundaries are defined.
4. Keep the pod toolchain recipe: use the `numba-cuda` redirector path, L4/modern NVIDIA GPU, and source-clean artifacts from Git.
