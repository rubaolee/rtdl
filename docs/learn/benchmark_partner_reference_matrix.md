# Benchmark Partner Reference Matrix

Status: current v2.x source-tree guidance, with v2.6 Numba work in progress.
This page is a guide for app authors choosing a custom continuation partner. It
does not authorize release wording or broad speedup claims.

The first choice is always the same: if a fused generic RTDL primitive exactly
expresses the answer, use that primitive. Partner code is for the work that is
not fused, not a hidden replacement for the RTDL engine.

Users choose partners explicitly. The matrix recommends reference paths for
benchmark apps; it does not define hidden auto-selection rules.

| Benchmark app | Custom logic pressure | Current RTDL primitive-first path | Recommended custom partner when needed | CuPy role | Numba role | Current best path summary | Evidence boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Hausdorff / X-HD style | exact directed distance from nearest-candidate summaries | OptiX active-frontier exact path for the current app contract | CuPy for CUDA-core baseline; Numba only for selected generic argmax/score-row experiments | strong grouped-grid and RawKernel baseline | correctness and contract evidence; not default winner | active-frontier RTDL/OptiX beats grouped-grid CuPy on reviewed synthetic diversity runs | cite Goal3046/3048 artifacts before publishing |
| Spatial RayJoin | point-in-polygon parity/count, boundary proximity, row-stream filtering | scalar count/parity and first-hit/nearest-boundary style primitives where available | Numba for compact-mask row continuation; CuPy for established CUDA baselines | useful baseline and app-level exact continuation | compact-mask reference for row-stream continuation | primitive-first for scalar answers; Numba only for explicit row continuation | no paper-reproduction claim without RayJoin same-contract evidence |
| RT-DBSCAN | fixed-radius core flags plus component labeling | fixed-radius/core-summary primitives | CuPy today for measured component continuation; Numba is future candidate | prepared grid/components reference | not promoted for component labeling yet | RTDL summaries plus CuPy component continuation for many rows | dense-stream and clustering semantics remain app code |
| RTNN | ranked fixed-radius summaries and candidate-quality probes | prepared fixed-radius ranked summaries | CuPy for CUDA-core all-pairs baseline; Numba only after measured win | baseline rows and quality checks | no promoted default yet | RTDL prepared OptiX summaries are the main path | compare exact contract and dataset scale |
| RayDB-style aggregates | grouped count/sum/min/max/stats | fused columnar grouped reductions when they exactly match | Numba for unfused grouped min/max style custom kernels | conformance and older partner rows | first-class v2.6 custom grouped continuation lane | use primitive-first for fused scalar summaries | do not force partner continuation onto fused primitive rows |
| Triangle counting | scalar triangle count plus optional candidate-row interpretation | native scalar triangle-count primitive | Numba for compact-mask candidate continuation only | optional device geometry setup and baseline summaries | compact-mask continuation reference | scalar primitive remains preferred for scalar answer | app interpretation of candidate rows stays outside engine |
| Barnes-Hut | force-vector continuation after aggregate-frontier collection | aggregate-frontier collect primitive | CuPy for exact force-vector reference | active force-vector partner reference | not promoted yet | primitive collects generic frontier rows; app computes force law | no broad N-body acceleration claim |
| Robot collision | pose batching, collision flag reduction | any-hit/collision-style generic flags where supported | no promoted v2.6 Numba reference yet | possible flag reduction/reference path | future candidate | keep CPU/Embree/OptiX primitive parity first | robotics policy stays app code |
| Contact manifold | bounded contact witness rows and stable witness pages | bounded collect/fail-closed witness primitives | no promoted v2.6 Numba reference yet | possible witness filtering/reference path | future candidate | preserve bounded witness contract first | no arbitrary manifold-generation claim |
| LibRTS-style spatial index | mutable index and point/range query semantics | generic point/range query rows where supported | no promoted v2.6 Numba reference yet | possible app-owned continuation | future candidate | Tier C/no-regression style evidence, not partner-performance row | index mutation policy stays app code |

## How To Use This Matrix

1. Start from the benchmark README and run the primitive-first command.
2. If the app needs unfused continuation, choose the partner listed above only
   when the README or report gives same-contract evidence for your scale.
3. If the matrix says "future candidate," keep that partner experimental until
   you add correctness, timing, and review artifacts.
4. Keep user code honest: app-specific policy and labels can be in Python, but
   the native engine primitive must stay app-agnostic.

For the practical decision guide, read
[Choosing A Partner For Custom Logic](partner_choice_for_custom_logic.md).

The same benchmark recommendations are available as advisory metadata through
`rtdsl.plan_v2_6_partner_choice(...)`. That helper is explanatory only; it does
not auto-select a partner or authorize performance wording.
