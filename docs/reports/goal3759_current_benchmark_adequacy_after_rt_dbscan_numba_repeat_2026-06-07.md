# Goal3759 Current Benchmark Adequacy After RT-DBSCAN Numba Repeat Evidence

Date: 2026-06-07

Source of truth: `rtdl.v2_9.benchmark_adequacy_after_goal3762.v1`

## Purpose

Goal3758 changed the RT-DBSCAN status from "Numba support exists" to "Numba is
measured on the prepared-repeat contract." This report is the current
reader-facing adequacy refresh after that evidence. It does not rewrite older
goal reports; it points to the current matrix and keeps the release boundary
explicit.

## Current Matrix

| Benchmark app | Current adequacy | Recommended path | Partner role | Next major direction |
| --- | --- | --- | --- | --- |
| `hausdorff_xhd` | adequate | RTDL/OptiX nearest-witness primitives plus grouped max continuation | Numba exact reference exists; promoted RT path is primitive-first | HIPRT nearest-witness and grouped-max parity |
| `spatial_rayjoin` | strong | Mixed route with current native-PIP cross-size evidence: RTDL/OptiX resident scalar-count PIP, RTDL/OptiX exact LSI count, RTDL/OptiX overlay active-count | CuPy is the dense CUDA-core baseline/opponent; Goal3749 covers no-RawKernel topology reference | HIPRT segment-pair and shape-pair parity; non-dense baseline policy for larger sizes where dense all-CuPy OOMs |
| `rt_dbscan` | strong | RTDL/OptiX fixed-radius threshold flags plus app-owned component continuation | Numba is now the measured high-performance no-RawKernel prepared-repeat reference | HIPRT fixed-radius grouped-stream parity |
| `robot_collision` | strong | Prepared RTDL/OptiX any-hit flags or scalar device-count | no partner needed for the promoted prepared path | AMD functional row validation, then HIPRT prepared-buffer parity |
| `contact_manifold` | adequate | Prepared bounded witness collection primitive | no partner needed on the accepted current path | HIPRT bounded-witness parity |
| `raydb_style` | adequate | Primitive-first RTDL/OptiX grouped count/sum reductions | no partner recommended for fused scalar reductions | HIPRT grouped i64 count/sum parity |
| `barnes_hut` | adequate | RTDL/OptiX membership plus explicit partner exact-force/vector continuation | CuPy remains fastest; Numba is the improved no-RawKernel block-reduction reference | HIPRT membership parity or deeper hierarchical vector primitive design |
| `librts_spatial_index` | adequate | Prepared generic AABB index query primitive | no partner needed | HIPRT AABB query parity |
| `rtnn` | adequate | Prepared RTDL/OptiX fixed-radius ranked-summary aggregate | no partner on the promoted path; CuPy grid remains the opponent/reference | HIPRT ranked-summary mapping |
| `triangle_counting` | adequate | Generic RT graph summary primitive | no partner needed on the fastest primitive row | HIPRT graph-summary primitive parity |

## RT-DBSCAN Update

Goal3758 A5000 prepared-repeat evidence:

| Points | Numba vs prepared CuPy grid | OptiX+Numba vs prepared CuPy grid | OptiX+Numba vs Numba grid |
| ---: | ---: | ---: | ---: |
| 4,096 | 1.131x | 0.956x | 0.845x |
| 65,536 | 1.153x | 1.367x | 1.185x |
| 131,072 | 1.106x | 1.748x | 1.581x |

The interpretation is scale-dependent and intentionally bounded:

- At small scale, the mixed OptiX+Numba route is slower because launch and
  occupancy costs dominate.
- At 65k and 131k points, RT-core threshold flags plus Numba prepared
  continuation become the stronger path.
- This is prepared-repeat component-labeling evidence, not a whole DBSCAN
  paper-reproduction claim.

## Barnes-Hut Update

Goal3762 replaces the first Numba exact-force loop from Goal3746 with a
512-thread block-per-source target-stride reduction. Clean A5000 evidence at
source commit `afda1b83`:

| Bodies | CuPy RawKernel median sec | Numba block-reduce median sec | Numba vs CuPy |
| ---: | ---: | ---: | ---: |
| 1,024 | 0.005063 | 0.005922 | 0.855x |
| 2,048 | 0.009919 | 0.010402 | 0.954x |
| 4,096 | 0.019897 | 0.020210 | 0.985x |
| 8,192 | 0.039565 | 0.040361 | 0.980x |
| 16,384 | 0.079204 | 0.102273 | 0.774x |

This improves the Numba no-RawKernel reference from a serial-style force loop
to a parallel reduction structure. It still does not beat the hand-written
CuPy RawKernel overall, so Barnes-Hut remains adequate with boundary rather
than strong.

## Boundary

This report does not authorize release action, public speedup wording,
whole-app acceleration wording, broad RT-core wording, true-zero-copy wording,
automatic partner selection, paper reproduction wording, or app-specific native
engine logic.
