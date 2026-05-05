# Goal1274 v1.3 Primitive ABI And Lowering Contract Draft

Date: 2026-05-05

Status: draft for external review. This is not final consensus and does not
authorize v1.4/v1.5 implementation, public wording, release gates, tags, or new
backend scope.

## Purpose

v1.3 turns the v1.2 evidence into contracts before native refactoring. The goal
is to define what v1.5 must expose as generic traversal-plus-reduction
primitives, what each current app row lowers to, and what parity/performance
gates must pass before app-specific native continuations can be retired.

The contract follows the accepted Goal1255 roadmap and Goal1273 validated pod
findings:

- active engineering scope is Embree plus OptiX;
- NVIDIA RT performance is the top priority;
- Vulkan, HIPRT, and Apple RT stay frozen for new implementation work before
  v2.1;
- v1.5 is a generic traversal-plus-reduction primitive release, not a universal
  compute engine;
- public speedup wording still requires a separate exact-sub-path wording
  packet and required external review.

## Primitive Set

The stable v1.5 primitive target is:

| Primitive | Result shape | Required dtype contract | Determinism and parity rule | v1.5 status |
| --- | --- | --- | --- | --- |
| `ANY_HIT` | one boolean or `uint8` flag per probe item | boolean-compatible scalar; no witness rows required | exact parity for hit/no-hit against CPU oracle and Embree/OptiX same-contract baselines | stable target |
| `COUNT_HITS` | one integer count per probe item or one aggregate count | `uint32` for bounded counts, `uint64` when documented scale can exceed `uint32` | exact integer parity; overflow behavior must be explicit | stable target |
| `REDUCE_FLOAT(MIN)` | scalar or grouped float output | `float32` or `float64` declared per plan | tolerance-based parity with declared absolute/relative tolerance and NaN policy | stable target |
| `REDUCE_FLOAT(MAX)` | scalar or grouped float output | `float32` or `float64` declared per plan | tolerance-based parity with declared absolute/relative tolerance and NaN policy | stable target |
| `REDUCE_FLOAT(SUM)` | scalar or grouped float output | `float32` or `float64` declared per plan | tolerance-based parity; reduction order and accepted tolerance must be declared | stable target |
| `REDUCE_INT(COUNT)` | scalar or grouped integer output | `uint32`, `uint64`, or signed integer if inputs require it | exact integer parity; grouping key schema must be declared | stable target |
| `REDUCE_INT(SUM)` | scalar or grouped integer output | signedness and width declared per plan | exact integer parity unless overflow policy explicitly narrows it | stable target |
| `COLLECT_K_BOUNDED` | bounded witness rows or ids per probe/group | fixed-width ids plus optional payload fields | exact membership/order policy must be declared; allowed only with a hard `k` ceiling | experimental after scalar primitives are stable |

`REDUCE` is deliberately split by dtype and operation. A single untyped
`REDUCE` bucket is not precise enough for ABI review because it hides result
shape, tolerance, overflow, grouping, and determinism requirements.

`REDUCE_FLOAT(SUM)` may later expose compensated summation policies such as
Kahan-style accumulation, but v1.3 only requires the plan to declare the chosen
reduction order, dtype, and tolerance. `COLLECT_K_BOUNDED` must declare what
happens when matches exceed `k`: truncation with deterministic order, explicit
overflow status, or hard failure.

## ABI Contract

Every generic primitive plan must declare:

| Field | Requirement |
| --- | --- |
| `primitive` | one of the stable primitive names above, or `COLLECT_K_BOUNDED` as experimental |
| `backend` | `embree` or `optix` for active v1.3/v1.4 work |
| `build_layout` | native-ready build buffer schema, including geometry kind and field dtypes |
| `probe_layout` | native-ready probe/ray/query buffer schema, including field dtypes |
| `predicate` | hit predicate or comparison predicate used by traversal |
| `result_layout` | scalar, per-probe, grouped, or bounded-row result schema |
| `group_key_layout` | required for grouped reductions; absent for scalar/per-probe primitives |
| `precision_policy` | exact integer, float approximate, float tolerance, and NaN policy |
| `overflow_policy` | required for integer counts/sums and bounded collection capacity |
| `prepared_state` | whether scene/build data, probe buffers, or both are reusable |
| `phase_counters` | required timing counters for traversal, prepare, copyback, reduction, and output packing |
| `claim_boundary` | exact sub-path covered and excluded phases |
| `retained_scale_range` | retained correctness/performance scales covered by the plan; prevents cherry-picked single-point promotion |

For floating reductions, `precision_policy` must state minimum NaN behavior:
whether NaN inputs are rejected, propagated, ignored as identity, or handled by
an app-specific rule. The rule must be the same across CPU oracle, Embree, and
OptiX for the same contract.

The ABI must support two execution shapes:

- `one_shot`: build/prepare plus query plus output in one call;
- `prepared`: reusable build state and optionally reusable probe buffers, with
  repeated query timing exposed separately.

Prepared execution is mandatory for v1.5 review because Goal1273 shows that
the graph any-hit query itself is fast while preparation and packing can
dominate total time.

`prepared_state` must specify which state is immutable and reusable: build
geometry/BVH, probe/ray buffers, both, or neither. If build geometry is frozen,
the plan must state whether the BVH can be reused across all queries and which
inputs are allowed to vary.

## Backend Parity Contract

Embree and OptiX must expose the same logical contract for each stable
primitive before v1.5 promotion:

| Gate | Requirement |
| --- | --- |
| correctness | CPU oracle, Embree, and OptiX produce equivalent results under the declared parity rule |
| tolerance | floating reductions use declared absolute/relative tolerance, not bit-exact parity by default |
| status payload | outputs include backend, primitive, mode, scale, status, and parity fields |
| phase payload | outputs include prepare, traversal/query, copyback, reduction/continuation, and output pack timings where applicable |
| failure payload | unsupported backends fail with explicit `unsupported` or `blocked` status, not silent fallback |
| public boundary | positive public wording remains false until a separate reviewed wording packet accepts the exact sub-path |

## Per-App Lowering Matrix

| App row | Current v1.2 evidence | v1.3 lowering target | Still app-specific or excluded work | Migration gate |
| --- | --- | --- | --- | --- |
| `graph_analytics.visibility_edges` | Goal1272: OptiX total and prepared repeat beat Embree; repeated any-hit query mean is tens of microseconds | `ANY_HIT` for visibility predicate; `COUNT_HITS` or `REDUCE_INT(COUNT)` for summary count | BFS, triangle counting, graph database analytics, frontier bookkeeping, and graph reductions remain outside this row | prepared scene/probe reuse contract plus parity and phase counters on Embree and OptiX |
| `database_analytics.sales_risk` | Goal1272: OptiX warm-query median beats Embree at 100k and 300k under compact-summary contract | `COUNT_HITS` or `REDUCE_INT(COUNT)` over numeric predicate traversal | SQL engine behavior, DBMS integration, broad database analytics, grouped DB workloads, and row-materializing output remain outside claim | zero row-materialization, native counter export, same-contract warm-query parity |
| `polygon_pair_overlap_area_rows` | Goal1272: OptiX candidate discovery beats Embree; positive-pair parity true; conservative candidate upper-bound mismatch remains explicit | `ANY_HIT`/candidate discovery plus later `REDUCE_FLOAT(SUM)` if exact area aggregation is generalized | exact polygon area continuation remains app-specific until generic float reduction/refinement contract exists | preserve Goal1270 diagnostic split and prove result-shape parity |
| `polygon_set_jaccard` | Goal1272: chunk `1024` is correctness-safe but OptiX remains slower than Embree | `ANY_HIT` plus experimental `COLLECT_K_BOUNDED`, later `REDUCE_FLOAT(SUM)` for scoring | chunk policy, pair collection, and exact/native continuation remain diagnostic until bounded collection is stable | keep as `optix_still_slower_with_reason`; do not promote public wording |

## Migration Gates

No app-specific native continuation should be retired until all relevant gates
pass:

| Gate | Required before retirement |
| --- | --- |
| contract gate | primitive ABI declares input, output, dtype, tolerance, overflow, grouping, and prepared-state contract |
| parity gate | CPU oracle, Embree, and OptiX pass declared parity on retained scales |
| phase gate | report separates prepare, traversal, reduction/continuation, copyback, and output packing |
| performance gate | generic primitive is at least performance-neutral against app-specific continuation, or an accepted overhead is documented |
| wording gate | public docs still state exact sub-path boundaries and excluded phases |
| review gate | key architecture changes receive required Gemini and Claude review before final consensus |

For v1.4 migration planning, "performance-neutral" means the generic primitive
median is no worse than 10% slower than the app-specific continuation on the
retained scale range, unless a separate reviewed decision explicitly accepts a
larger overhead because the generic path removes app-specific maintenance risk.

## Public Wording Contract

v1.3 may draft public wording candidates, but it does not authorize them. Any
candidate must use this form:

```text
RTDL accelerates <exact prepared/native sub-path> for <app/workload> under
<backend/mode>, with <evidence/report>. This is not a whole-app speedup claim
and does not include <excluded phases>.
```

Forbidden wording remains:

- whole-app graph/DB/GIS acceleration unless whole-app evidence exists;
- broad "RT cores accelerate databases/graphs/polygons" claims;
- using `--backend optix` alone as proof of RT-core acceleration;
- treating v1.2 internal intake as public release evidence;
- expanding Jaccard wording while it remains `optix_still_slower_with_reason`.

## v1.4 Readiness Criteria

v1.4 can start compatibility-wrapper migration only after v1.3 consensus
accepts:

- the primitive names and dtype/result-shape contracts;
- the per-app lowering matrix;
- the backend parity and tolerance rules;
- the migration gates;
- the public wording boundary.

Until then, v1.4 native refactoring should not begin.

## Boundary

This is a draft contract for review. It is not implementation permission, not
public wording, and not a release package. Because v1.3 defines architecture
and migration gates, final acceptance is a key goal and requires 3-AI consensus
unless the user explicitly classifies it lower.
