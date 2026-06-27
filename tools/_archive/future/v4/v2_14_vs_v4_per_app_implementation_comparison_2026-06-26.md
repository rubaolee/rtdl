# V2.14 vs V4 Per-App Implementation Comparison

Date: 2026-06-26

Status: `pre_execution_design_context_for_goal4723`

Purpose: explain, before running the next V4 benchmark-closure work, how V2.14
and V4 implement each of the 10 promoted benchmark apps, what they share, what
actually differs, and what design risks must be controlled.

This document is intentionally implementation-facing. It is not a release claim
and it does not authorize performance wording.

## Executive Summary

The central fact is uncomfortable but clarifying:

> V2.14 already had a primitive or explicit partner route for all 10 benchmark
> apps.

Therefore V4 cannot honestly win by merely moving old work behind a cleaner
front door. For an existing benchmark app to support a V4 performance claim,
V4 must prove one of two things:

1. a generic runtime/operator lever absent from V2.14, or
2. a material same-primitive improvement over the V2.14 app route under a
   frozen same-hardware protocol.

Anything else is productization, usability, or boundary cleanup. Those can be
valuable, but they are not app-level performance wins.

## Sources

- V2.14 per-app primitive audit:
  `future/v4/evidence/v4_goal4672_v2_14_per_app_primitive_audit_2026-06-25.json`
- Current V4 route binding after Hausdorff/RTNN updates:
  `future/v4/evidence/v4_goal4662_app_route_binding_after_hausdorff_rtnn_2026-06-25.json`
- Current V4 status:
  `docs/current_v4_status.md`
- App-level benchmark analysis:
  `future/v4/evidence/v4_goal4669_app_level_benchmark_analysis_2026-06-25.json`
- Complete 10-app closure plan:
  `future/v4/v4_goals_4723_4733_complete_10_app_app_level_benchmark_closure_2026-06-26.md`

## Design Lens

V2.14 style:

- primitive-first or explicitly mixed partner routes;
- many app routes already knew which OptiX/RTDL primitive or CuPy/Numba partner
  path to use;
- strong expert-toolbox behavior, but less unified product surface.

V4 intended style:

- one Python eDSL/operator-pushdown front door;
- generic operator catalog and planner;
- fail-closed behavior for unsupported routes;
- fused generic continuation operators are allowed;
- app-identity kernels are not allowed.

The allowed V4 abstraction rule:

> The engine may contain generic continuation operators such as count,
> threshold, grouped reduction, component union, nearest witness, AABB query,
> aggregate frontier, or constrained predicate early-exit. It must not contain
> "DBSCAN kernel", "Barnes-Hut kernel", "RayJoin kernel", or other app-identity
> kernels as public V4 features.

## App Matrix

| App | V2.14 implementation class | Current V4 implementation class | Current app-level state |
| --- | --- | --- | --- |
| `rt_dbscan` | mixed explicit RT + CuPy/Numba route | full V4 fused-operator route | measured modest gain |
| `raydb_style` | primitive-first grouped reductions | full V4 operator route | measured regression |
| `triangle_counting` | primitive-first graph/any-hit composition | full V4 weighted-sum/grouped route | fast vs V2.14, regression vs V3 |
| `librts_spatial_index` | prepared AABB query primitive | full V4 AABB all-ops/count route | measured parity |
| `hausdorff_xhd` | nearest-witness primitive plus grouped max continuation | full V4 official route | one true V4 app candidate win |
| `robot_collision` | prepared any-hit collision primitive | partial any-hit flag coverage | no complete app row |
| `contact_manifold` | bounded contact-witness collect primitive | partial nearest-witness coverage | no complete app row |
| `rtnn` | prepared ranked-summary aggregate | candidate ranked-summary route, then deferred | measured parity/slower |
| `spatial_rayjoin` | mixed explicit relation/topology route | no V4 app route | blocker |
| `barnes_hut` | aggregate-frontier membership + partner continuation | aggregate-frontier subprobe only | no complete app row |

## 1. RTDBSCAN

Common structure:

- Both versions depend on fixed-radius neighbor discovery and a component/union
  continuation.
- Both are mixed RT-core plus general GPU work: traversal produces candidate or
  neighborhood information; a continuation groups/merges components.

V2.14 implementation:

- Mixed explicit RT-DBSCAN route.
- Uses prepared RT-core count-threshold in 3D.
- Uses grouped-stream CuPy/Numba-style continuation paths and direct-status
  variants.
- V2.14 already had the essential primitive contract:
  fixed-radius count-threshold device columns plus grouped component labels.

Current V4 implementation:

- Route is bound to generic V4 surfaces:
  `v4_fixed_radius_count_threshold_2d_device_arrays` and
  `v4_fixed_radius_graph_component_union_3d_device_arrays`.
- V4 exposes this through the planner/front door instead of an app-specific
  route choice.

Current result:

- V4/V2.14 hot: `1.086x`.
- This is a modest runtime gain, below formal high-performance bar.

Design consideration:

- RTDBSCAN is not a clean "new V4 primitive" win because V2.14 already had the
  count-threshold plus grouped-union family.
- A future win needs a genuinely better generic grouped-union/runtime lever,
  not a DBSCAN-specific kernel.

## 2. RayDB-Style

Common structure:

- Both versions use ray/triangle traversal and grouped primitive reductions.
- The core abstraction is columnar grouped reduction over hit or primitive
  relationships.

V2.14 implementation:

- Primitive-first RTDL/OptiX grouped count/sum reduction route.
- V2.14 measured route includes
  `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D` and the native prepared
  grouped-i64 reduction symbol.

Current V4 implementation:

- Route is bound to V4 grouped-i64, grouped-argmin, and any-hit operator
  surfaces.
- V4 adds catalog/planner boundaries and measured operator surface records.

Current result:

- V4/V2.14 hot: `0.974x`.
- This is a regression against the no-regression floor.

Design consideration:

- V4 grouped-i64 productization is useful, but not a new app-level speed source
  by itself because V2.14 already had the primitive-first path.
- Goal4723 must either prove a real same-primitive improvement or record this
  row as regression.

## 3. Triangle Counting

Common structure:

- Both versions express triangle/counting-style work through generic RT graph or
  ray/triangle any-hit composition.
- Both rely on weighted any-hit or grouped reduction style primitives.

V2.14 implementation:

- Primitive-first generic RT graph relationship-count composition.
- Serious V2.14 row already used an OptiX weighted any-hit sum primitive with a
  CuPy partner continuation.

Current V4 implementation:

- Uses V4 ray/triangle any-hit weighted-sum plus grouped-i64 surfaces.
- The V4 surface is cleaner and better documented, but much of the primitive
  family already existed in the V2.14 path.

Current result:

- V4/V2.14 hot: `4.055x`.
- V4/V3.0.2 hot: `0.948x`.

Design consideration:

- The V4/V2.14 number alone is misleading. The V2 delta reflects historical
  route evolution, while V4 regresses versus V3.0.2.
- This row must not be sold as a clean new V4 win unless the V3 regression is
  explained/fixed under the same app protocol.

## 4. LibRTS Spatial Index

Common structure:

- Both versions depend on prepared AABB spatial-index query primitives.
- This is a backend-bound prepared-query workload.

V2.14 implementation:

- Prepared RTDL/OptiX AABB spatial-index query primitive.
- V2.14 already had `aabb_index_query_2d` style prepared-session primitive
  coverage.

Current V4 implementation:

- V4 exposes `v4_aabb_index_query_2d_all_ops_count_prepared_runner`.
- The V4 operator-level scorecard can show large wins versus Embree or slower
  controls, but the app-level denominator is V2.14's prepared AABB route.

Current result:

- V4/V2.14 hot: `1.003x`.
- V4/V2.14 primary wall: `1.049x`.

Design consideration:

- App-level parity is expected because V2.14 already had the relevant prepared
  primitive.
- V4 value here is catalog clarity and bounded operator support, not a broad
  new speed source.

## 5. Hausdorff XHD

Common structure:

- Both versions solve directed nearest-witness / max-nearest-distance style
  work.
- Both combine RT-shaped nearest witness search with a continuation that
  selects the maximum or summary result.

V2.14 implementation:

- Route table records RTDL/OptiX active-frontier nearest-witness plus grouped
  max continuation.
- The Goal4669 V2.14 denominator row used Embree directed-summary style
  evidence, so denominator provenance must stay visible.

Current V4 implementation:

- Official V4 route exists through generic point-group nearest-witness plus a
  Torch or CuPy global argmax continuation.
- Requires coordinate-normalized correctness handling for the 1M exactness
  boundary.

Current result:

- V4/V2.14 hot: `201581.860x`, but this is a denominator outlier because the
  Goal4669 V2.14 row used an Embree directed-summary route.
- V4/V2.14 primary wall: `114.824x`.
- V4/V3.0.2 hot: `2.546x`.

Design consideration:

- This is a current app-level V4 candidate, but the raw V2.14 hot ratio must not
  be used as a normal headline speedup. The readable same-family speed signal is
  V4/V3.0.2 hot at `2.546x`.
- It is still one app row, not proof that all benchmark apps are faster.
- The denominator and correctness-boundary details must be reported openly: the
  1,048,576 points/side coordinate-normalized row is a correctness-boundary
  probe, not a speed claim.

## 6. Robot Collision

Common structure:

- Both versions center on any-hit collision flags and scalar collision counts.
- The natural generic primitive is prepared any-hit flag/count over collision
  geometry.

V2.14 implementation:

- Prepared RTDL/OptiX any-hit flag primitive.
- The V2.14 audit says device-buffer modes already existed.
- No partner was needed for the primary primitive.

Current V4 implementation:

- V4 has partial any-hit flag coverage through generic ray/triangle any-hit
  surfaces.
- There is not yet a complete app-level V4 route recorded for robot collision.

Current result:

- No complete app-level V4/V2.14 row yet.

Design consideration:

- Robot collision is not a clean V4 win target unless V4 proves material
  same-primitive improvement over V2.14 or adds a reusable generic runtime
  lever.
- Partial any-hit coverage cannot be counted as a full app result.

## 7. Contact Manifold

Common structure:

- Both versions involve witness/contact collection under bounded output
  constraints.
- The hard part is not just nearest witness; it is bounded, fail-closed contact
  witness collection with correct output semantics.

V2.14 implementation:

- Prepared bounded contact-witness collect primitive.
- No external partner was required for the primary route.

Current V4 implementation:

- V4 has partial nearest-witness coverage.
- No complete contact-manifold V4 app route is currently recorded.

Current result:

- No complete app-level V4/V2.14 row yet.

Design consideration:

- A V4 win requires a generic contact/witness collect operator or a materially
  faster bounded collect-k route.
- Reusing nearest-witness alone is insufficient because it does not cover the
  complete contact-manifold contract.

## 8. RTNN

Common structure:

- Both versions use fixed-radius/ranked nearest summary style aggregation.
- The relevant primitive family is ranked-summary/top-k or nearest aggregate,
  not just raw nearest witness.

V2.14 implementation:

- Prepared RTDL/OptiX fixed-radius ranked-summary aggregate.
- V2.14 already had the essential ranked-summary primitive family.

Current V4 implementation:

- V4 candidate `v4_fixed_radius_ranked_summary_3d_prepared_runner` was built
  and validated as a runtime-executed route.
- Goal4678 deferred it out of the current candidate front door because serious
  scale performance did not move the app-level bar.

Current result:

- 262,144 points: V4/V2.14 hot about `0.999x`.
- 1,048,576 points: V4/V2.14 hot about `0.994x`.

Design consideration:

- This is a good example of "runtime executed" not being enough.
- V4 wrappers/productization do not support a speed claim when V2.14 already
  had the primitive and serious-scale timing is parity/slower.

## 9. Spatial RayJoin

Common structure:

- The workload needs relation/topology primitives: point/shape batches,
  segment-pair exact counts, and shape-pair active counts.
- The route naturally mixes RT-style spatial traversal and partner/general GPU
  continuation logic.

V2.14 implementation:

- Mixed explicit RayJoin route from fixed-Numba-toolchain evidence.
- Primitive contract included prepared point/closed-shape batch count,
  segment-pair exact count, and shape-pair active count.

Current V4 implementation:

- Current V4 has no complete app route for Spatial RayJoin.
- No silent fallback to V2/V3 is authorized.

Current result:

- No complete app-level V4/V2.14 row yet.

Design consideration:

- This is a major V4 route gap.
- A valid V4 path must be a generic relation-topology operator family, not a
  Spatial-RayJoin-specific native kernel.

## 10. Barnes-Hut

Common structure:

- Both versions need aggregate-frontier membership and force/vector
  continuation.
- This is a multi-stage residency-sensitive workload: traversal/frontier output
  must feed vector accumulation efficiently.

V2.14 implementation:

- RTDL/OptiX membership primitive plus explicit force-vector partner
  continuation.
- V2.14 policy recorded CuPy as fastest with Numba reference.

Current V4 implementation:

- V4 has aggregate-frontier device-column evidence and a measured subroute:
  `v4_aggregate_frontier_device_columns_2d_prepared_runner`.
- That subprobe removes a V2.14 host-frontier bottleneck, but it is not a
  complete Barnes-Hut app route.

Current result:

- No complete app-level V4/V2.14 row yet.
- Aggregate-frontier subprobe: large V4/V2.14 speedup, but V4/V3.0.2 hot ratio
  about `0.998x`; therefore it is not a clean V4-over-V3 app win.

Design consideration:

- Barnes-Hut cannot be solved by app identity. The acceptable V4 target is a
  generic aggregate-tree weighted-vector primitive/workflow.
- The existing subprobe must not be used as a full app result.

## Cross-App Design Conclusions

1. V2.14 is a strong denominator.
   It already had primitive or explicit partner routes for all 10 apps.

2. V4's clean front door is valuable but insufficient.
   Usability, planner discipline, docs, and fail-closed behavior matter, but
   they do not automatically create app-level speedups.

3. The next benchmark work must close missing app rows, not add more operator
   rows.
   Operator rows are useful only when they are routed through complete app
   workflows.

4. The five incomplete app rows have different meanings:
   - `robot_collision`: likely same-primitive improvement/no-go.
   - `contact_manifold`: missing full bounded contact/witness route.
   - `rtnn`: measured candidate route is parity/slower.
   - `spatial_rayjoin`: no V4 relation-topology route.
   - `barnes_hut`: aggregate-frontier subprobe exists, full generic aggregate
     workflow missing.

5. Final V4 release must be gated on a complete 10-app matrix.
   Rows may be wins, parity, regressions, or explicit blockers. What is not
   acceptable is leaving rows vague.

## How This Directs Goals4723-4733

- Goal4723 must freeze a full 10-app protocol using this comparison as context.
- Goal4724 must audit route gaps for the five incomplete apps before POD spend.
- Goals4725-4729 must produce full app rows or explicit no-go rows.
- Goal4730 must run the complete same-hardware protocol only after the route
  and blocker statuses are frozen.
- Goal4731/4732 must publish the complete table, not only the operator catalog.

## Non-Authorization

This document does not authorize final V4 tag, broad V4 speedup wording,
whole-application speedups, all-benchmark speedups, arbitrary callback support,
raw OptiX callbacks, C ABI, embedding, non-Python host bindings, app-specific
native kernels, or using operator/subprobe evidence as complete app-level
evidence.
