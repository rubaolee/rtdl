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
| RT-DBSCAN | fixed-radius core flags plus component labeling or compact component signatures | fixed-radius/core-summary primitives, plus grouped-stream component-label front door for app-owned signatures | Use `output_mode="component_signature"` when the user needs cluster-size/noise/core summaries; keep `output_mode="full"` only when per-point Python cluster rows are required. Measure CuPy and Numba explicitly. | direct CUDA-array partner; Goal4445 measures compact device `unique` aggregation and removes Python cluster rows | no-C++ Python-source reference; Goal4445 consumes Numba device columns through CuPy's CUDA array interface for the compact signature path | RTDL/OptiX grouped-stream component labels plus explicit partner signature aggregation; at 2.1M points the full Python row consumer is about 3.05s while compact signature aggregation is about 0.002s | DBSCAN fixture/oracle semantics remain app code; no DBSCAN-native ABI, automatic partner selection, or broad DBSCAN speedup claim; cite Goal4445 for compact signatures and Goal4389 for the older prepared-grid continuation row |
| RayDB-style unfused grouped continuation | grouped min/max/count/sum/avg when not already fused | fused columnar grouped reductions when they exactly match | CuPy for current performance; Numba when no-RawKernel Python-source reference code matters | Goal4266 large-scale same-contract RTX 3090 rows for grouped count/sum/min/max and average-as-sum-plus-count; currently faster than Numba | selected generic grouped continuation lane; correct no-RawKernel reference, currently slower than CuPy in Goal4266 | use primitive-first for fused scalar summaries; use CuPy for current speed on unfused grouped continuations; use Numba for Python-source reference constraints | do not force partner continuation onto fused primitive rows; Goal4266 is partner-continuation evidence only |
| Triangle RT-Graph summary-contract construction | candidate-row / summary-contract interpretation after the scalar answer | generic RT graph relationship-count composition for the scalar answer | CuPy for current large-scale performance; Numba when no-C++ Python-source reference code matters | still fastest at 200K K4 cliques: Goal4444 total `140.671ms` on RT-2A1 and `74.989ms` on RT-1A2 | no longer the M27 Python-contract path; Goal4444 direct-binary summary cuts Numba total to `352.764ms` on RT-2A1 and `397.367ms` on RT-1A2, a `19.96x-23.07x` improvement over M27 | scalar answer stays primitive-first; choose a partner only for explicit RT-Graph summary-contract experiments | app graph construction stays outside engine; no RT-core triangle-count paper claim; remaining debt is fully device-side/segmented construction |
| RTNN resident graph bridge | same-stream compact reduction after prepared ranked-summary graph partials | exact native aggregate path exists separately for float64 backend comparison | CuPy and Numba are both explicit app-bridge partners; keep exact aggregate and float32 graph rows separate | slightly faster measured Goal4443/M47 app-front-door partner at 1M resident search / 65K query batch: 4.988ms median per batch, 4.988s over 1000 repeats | near-parity no-C++ Python-source reference: 5.020ms median per batch, 5.020s over 1000 repeats | use exact native aggregate for same-contract OptiX-vs-Embree; use graph bridge for resident app evidence with both partners visible | no full RTNN paper reproduction, no arbitrary ANN-index speedup, and no automatic exact-vs-float32 selection |
| Barnes-Hut | force-vector continuation after aggregate-frontier collection | aggregate-frontier device-column collect primitive plus fused CPU/Numba app route | Numba for both current routes: fused CPU/Numba is the fastest measured no-C++ app route in Goal4442; Numba is also the fastest measured GPU partner for the prepared OptiX device-column route in Goal4438/4439 | same-contract GPU comparison partner for the prepared aggregate-frontier route; older exact-force rows that favored CuPy stay scoped to their older contract | fastest measured app route is fused CPU/Numba; fastest measured RTDL/OptiX device-column partner is Numba | RTDL/OptiX emits generic frontier device columns and feeds Numba/CuPy partners; Goal4442 shows a fused CPU/Numba partner route avoids frontier materialization and beats the current RT route at tested scales | no broad N-body acceleration claim; no Barnes-Hut RT-core speedup claim; choose route explicitly by purpose |

## Primitive-First Paths

These rows are not CuPy-vs-Numba decisions. Start with the generic RTDL
primitive or composition; add partner code only if your own app needs extra
continuation work not covered by the primitive.

| Benchmark app / contract | Current user path | Partner guidance | Evidence boundary |
| --- | --- | --- | --- |
| Hausdorff / X-HD style | OptiX active-frontier exact path for the current app contract | CuPy remains a CUDA-core baseline; Numba is contract evidence, not the default winner | cite Goal3046/3048/3143 artifacts before publishing |
| RTNN exact aggregate | prepared fixed-radius ranked-summary aggregate | no partner needed for exact float64 aggregate; use the graph bridge row when resident same-stream partner reductions are the target | compare exact contract, precision, and dataset scale; Goal4381/4443 are current large evidence, not paper reproduction |
| RayDB fused count/sum | fused columnar grouped reductions | no partner needed when the fused primitive exactly answers the query | do not force partner continuation onto fused primitive rows |
| Triangle scalar answer | generic RT graph relationship-count composition | no partner needed for the scalar answer; Goal4444 partner evidence applies only to explicit RT-Graph summary-contract experiments | app interpretation of candidate rows stays outside engine; no RT-core triangle-count paper claim |
| Robot collision | generic grouped-segment any-hit flag/count primitive with NumPy vectorized app lowering for large prepared queries | no partner needed on the promoted path; use Goal4446's `lowering_mode="numpy_arrays"` for large timing/summary probes | robotics policy stays app code; no planner, continuous collision, exact solid collision, or true-zero-copy claim |
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
