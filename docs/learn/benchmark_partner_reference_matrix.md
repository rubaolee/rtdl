# Benchmark Partner Reference Matrix

Status: current v2.14 closeout guidance.
This page is a guide for app authors choosing a custom continuation partner. It
does not broaden release wording or authorize broad speedup claims.

The first choice is always the same: if a fused generic RTDL primitive exactly
expresses the answer, use that primitive. Partner code is for the work that is
not fused, not a hidden replacement for the RTDL engine.

For any benchmark-app claim that needs partner continuation, RTDL requires two
partner lines before stronger wording: the current best-performance partner for
that contract, and a Numba implementation. Numba is required because it gives
users a Python-source, no-C++/CUDA-kernel-writing path. This does not mean Numba
must win; it means Numba must be measured as the accessibility/reference path.

Users choose partners explicitly. The tables below separate two cases:

- **Partner-needed continuations**: the app still has custom work after RTDL
  emits generic outputs.
- **Primitive-first paths**: the current recommended app path does not need a
  CuPy-vs-Numba decision.

## Partner-Needed Continuations

Use this table only when your program really has custom continuation logic after
the RTDL primitive. If a row says that the primitive answers the query, skip this
table and use the primitive-first table instead.

| Benchmark app / contract | Custom logic pressure | Current RTDL primitive-first path | Recommended custom partner when needed | CuPy role | Numba role | Current best path summary | Evidence boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Spatial RayJoin | point-in-polygon parity/count, boundary proximity, row-stream filtering | scalar count/parity and first-hit/nearest-boundary style primitives where available | Numba for scalar-count and topology-reference continuation; CuPy for dense CUDA baselines | useful dense opponent and app-level exact continuation; still fastest on the one-shot bounded public-CDB PIP scalar-count row | Goal3834/3838 no-RawKernel scalar-count coverage for PIP, LSI, and overlay; compact-mask/topology references also exist | primitive-first for LSI/overlay scalar answers, where RTDL/OptiX is about `260x` faster than dense partners; resident repeated PIP uses the prepared batch executor at about `0.024ms/request` for batch 100; one-shot bounded public-CDB PIP remains contract-specific | no paper-reproduction claim without RayJoin same-contract evidence |
| RT-DBSCAN | fixed-radius core flags plus component labeling | fixed-radius/core-summary primitives | Numba prepared grid/component continuation for the current prepared-grid contract; CuPy remains the same-contract opponent | measured prepared-grid opponent; at 524K RT+CuPy is 10.662s and pure CuPy is 22.341s | current best measured path for this contract; at 524K RT+Numba is 8.900s and pure Numba is 20.244s; no RawKernel required | RTDL/OptiX threshold flags plus Numba prepared component continuation for scale rows; signatures match CuPy at all Goal4389 scales | dense-stream and clustering semantics remain app code; cite Goal4389 before publishing |
| RayDB-style unfused grouped continuation | grouped min/max/count/sum/avg when not already fused | fused columnar grouped reductions when they exactly match | CuPy for current performance; Numba when no-RawKernel Python-source reference code matters | Goal4266 large-scale same-contract RTX 3090 rows for grouped count/sum/min/max and average-as-sum-plus-count; currently faster than Numba | selected generic grouped continuation lane; correct no-RawKernel reference, currently slower than CuPy in Goal4266 | use primitive-first for fused scalar summaries; use CuPy for current speed on unfused grouped continuations; use Numba for Python-source reference constraints | do not force partner continuation onto fused primitive rows; Goal4266 is partner-continuation evidence only |
| Triangle candidate-row compaction | candidate-row interpretation after the scalar answer | generic RT graph relationship-count composition for the scalar answer | CuPy for current compact-mask performance; Numba when no-RawKernel Python-source reference code matters | Goal4266 large-scale same-contract compact-mask row; currently much faster than Numba | compact-mask continuation reference; correct no-RawKernel path, currently slower than CuPy in Goal4266 | scalar answer stays primitive-first; choose a partner only for explicit candidate-row compaction | app interpretation of candidate rows stays outside engine; no RT-core triangle-count claim; Goal4266 is partner-continuation evidence only |
| Barnes-Hut | force-vector continuation after aggregate-frontier collection | aggregate-frontier device-column collect primitive | Numba for the prepared aggregate-frontier weighted-vector app route measured in Goal4436/Goal4438 and exposed in Goal4439; CuPy remains a required same-contract comparison partner | same-contract comparison partner for the prepared aggregate-frontier route; older exact-force rows that favored CuPy stay scoped to their older contract | current fastest measured partner for the prepared aggregate-frontier device-column route, and the no-C++ Python-source route | RTDL/OptiX emits generic frontier device columns; Numba fuses contribution math and grouped accumulation on device; CuPy remains measured but slower on this contract; Goal4441 CPU/Embree host+Numba baselines show the remaining debt is frontier collection and host materialization | no broad N-body acceleration claim; no RT-core speedup claim from partner-only or host-baseline comparisons |

## Primitive-First Paths

These rows are not CuPy-vs-Numba decisions. Start with the generic RTDL
primitive or composition; add partner code only if your own app needs extra
continuation work not covered by the primitive.

| Benchmark app / contract | Current user path | Partner guidance | Evidence boundary |
| --- | --- | --- | --- |
| Hausdorff / X-HD style | OptiX active-frontier exact path for the current app contract | CuPy remains a CUDA-core baseline; Numba is contract evidence, not the default winner | cite Goal3046/3048/3143 artifacts before publishing |
| RTNN | prepared fixed-radius ranked summaries | no custom partner on the promoted path; CuPy remains the CUDA-core opponent/reference | compare exact contract and dataset scale; Goal3820 is front-door evidence, not paper reproduction |
| RayDB fused count/sum | fused columnar grouped reductions | no partner needed when the fused primitive exactly answers the query | do not force partner continuation onto fused primitive rows |
| Triangle scalar answer | generic RT graph relationship-count composition | no partner needed for the scalar answer; use Numba only for candidate-row compaction | app interpretation of candidate rows stays outside engine; no RT-core triangle-count claim |
| Robot collision | generic any-hit/collision flag primitive where supported | no partner needed on the promoted path | robotics policy stays app code |
| Contact manifold | bounded collect and fail-closed witness primitives | no partner needed on the accepted current path | no arbitrary manifold-generation claim |
| LibRTS-style spatial index | generic point/range query rows where supported | no partner needed on the prepared AABB index path | index mutation policy stays app code |

## How To Use This Matrix

1. Start from the benchmark README and run the primitive-first command.
2. If the app needs unfused continuation, choose the partner listed above only
   when the README or report gives same-contract evidence for your scale.
3. For partner-dependent benchmark claims, measure both the best-performance
   partner and Numba on the same contract, data, repeat protocol, and oracle.
4. If your app needs a continuation not listed here, keep that partner
   experimental until you add correctness, timing, and review artifacts.
5. Keep user code honest: app-specific policy and labels can be in Python, but
   the native engine primitive must stay app-agnostic.

For CuPy-vs-Numba decisions, prefer decision-grade rows like Goal4266: both
partners must use the same contract, the same repeat count, CPU-oracle
validation, and more than one second of aggregate hot time. Subsecond rows are
useful for smoke tests, not for user-facing partner recommendations.

For the practical decision guide, read
[Choosing A Partner For Custom Logic](partner_choice_for_custom_logic.md).

The current benchmark adequacy recommendations are available as advisory
metadata through `rtdsl.current_benchmark_adequacy()` and
`rtdsl.summarize_current_benchmark_adequacy()`. These helpers are explanatory
only; they do not auto-select a partner or authorize performance wording.

For a direct Numba-reference lookup, use
`rtdsl.v2_6_numba_reference_index()`. It returns one row per benchmark app with
the current Numba role, whether a custom partner is required for the reference
path, and whether any CuPy-only custom-continuation gap remains. This helper is
also advisory only; it never selects a partner for the user.

For parity expectations behind those Numba references, use
`rtdsl.v2_6_numba_parity_expectations()`. It names the oracle or tolerance that
must be checked for each current Numba reference row and keeps pending items,
such as RT-DBSCAN blocked-mode A5000 timing, explicit.
