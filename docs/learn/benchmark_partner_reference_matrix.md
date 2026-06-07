# Benchmark Partner Reference Matrix

Status: current v2.10 source-tree guidance.
This page is a guide for app authors choosing a custom continuation partner. It
does not broaden release wording or authorize broad speedup claims.

The first choice is always the same: if a fused generic RTDL primitive exactly
expresses the answer, use that primitive. Partner code is for the work that is
not fused, not a hidden replacement for the RTDL engine.

Users choose partners explicitly. The matrix recommends reference paths for
benchmark apps; it does not define hidden auto-selection rules.

| Benchmark app | Custom logic pressure | Current RTDL primitive-first path | Recommended custom partner when needed | CuPy role | Numba role | Current best path summary | Evidence boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Hausdorff / X-HD style | exact directed distance from nearest-candidate summaries | OptiX active-frontier exact path for the current app contract | CuPy for CUDA-core baseline; Numba for exact continuation/reference experiments | strong grouped-grid and RawKernel baseline | exact continuation reference exists; not default winner | active-frontier RTDL/OptiX is the promoted path for the reviewed app contract | cite Goal3046/3048/3143 artifacts before publishing |
| Spatial RayJoin | point-in-polygon parity/count, boundary proximity, row-stream filtering | scalar count/parity and first-hit/nearest-boundary style primitives where available | Numba for compact-mask and topology-reference continuation; CuPy for dense CUDA baselines | useful dense opponent and app-level exact continuation | no-RawKernel topology and compact-mask references exist | primitive-first for scalar answers; Numba only for explicit row/topology continuation | no paper-reproduction claim without RayJoin same-contract evidence |
| RT-DBSCAN | fixed-radius core flags plus component labeling | fixed-radius/core-summary primitives | Numba prepared grid/component continuation where measured; CuPy remains a baseline | prepared grid/components baseline | measured prepared-repeat component continuation | RTDL/OptiX threshold flags plus Numba prepared component continuation for scale rows | dense-stream and clustering semantics remain app code |
| RTNN | ranked fixed-radius summaries and candidate-quality probes | prepared fixed-radius ranked summaries | no custom partner on the promoted path; CuPy remains the CUDA-core opponent/reference | baseline rows and quality checks | no promoted default because the current path is primitive/aggregate-first | RTDL prepared OptiX summaries are the main path | compare exact contract and dataset scale |
| RayDB-style aggregates | grouped count/sum/min/max/stats | fused columnar grouped reductions when they exactly match | Numba for unfused grouped min/max style custom kernels | conformance and older partner rows | selected generic grouped continuation lane | use primitive-first for fused scalar summaries | do not force partner continuation onto fused primitive rows |
| Triangle counting | scalar triangle count plus optional candidate-row interpretation | native scalar triangle-count primitive | Numba for compact-mask candidate continuation only | optional device geometry setup and baseline summaries | compact-mask continuation reference | scalar primitive remains preferred for scalar answer | app interpretation of candidate rows stays outside engine |
| Barnes-Hut | force-vector continuation after aggregate-frontier collection | aggregate-frontier collect primitive | CuPy for fastest measured exact force-vector path; Numba for no-RawKernel block-reduction reference | active force-vector partner reference, faster overall in current evidence | improved exact-force block-reduction reference exists | primitive collects generic frontier rows; app computes force law | no broad N-body acceleration claim |
| Robot collision | pose batching, collision flag reduction | any-hit/collision-style generic flags where supported | no partner needed on the promoted path | possible optional flag-reference path | not required for the promoted primitive contract | keep CPU/Embree/OptiX primitive parity first | robotics policy stays app code |
| Contact manifold | bounded contact witness rows and stable witness pages | bounded collect/fail-closed witness primitives | no partner needed on the accepted current path | possible optional witness filtering/reference path | not required for the promoted primitive contract | preserve bounded witness contract first | no arbitrary manifold-generation claim |
| LibRTS-style spatial index | mutable index and point/range query semantics | generic point/range query rows where supported | no partner needed on the prepared AABB index path | possible app-owned continuation | not required for the promoted primitive contract | Tier C/no-regression style evidence, not partner-performance row | index mutation policy stays app code |

## How To Use This Matrix

1. Start from the benchmark README and run the primitive-first command.
2. If the app needs unfused continuation, choose the partner listed above only
   when the README or report gives same-contract evidence for your scale.
3. If your app needs a continuation not listed here, keep that partner
   experimental until you add correctness, timing, and review artifacts.
4. Keep user code honest: app-specific policy and labels can be in Python, but
   the native engine primitive must stay app-agnostic.

For the practical decision guide, read
[Choosing A Partner For Custom Logic](partner_choice_for_custom_logic.md).

The current benchmark adequacy recommendations are available as advisory
metadata through `rtdsl.current_benchmark_adequacy()` and
`rtdsl.summarize_current_benchmark_adequacy()`. These helpers are explanatory
only; they do not auto-select a partner or authorize performance wording.
