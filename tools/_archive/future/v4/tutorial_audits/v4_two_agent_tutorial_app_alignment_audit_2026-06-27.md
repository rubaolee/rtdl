# V4 Two-Agent Tutorial/App Alignment Audit

Date: 2026-06-27

This is an internal teaching-quality audit. It is not part of the public
first-time user path.

## Purpose

The user asked for two independent learners:

- one learner studies benchmark apps and paper-reproduction apps from the
  application side;
- one learner studies the grassroots tutorial materials from the beginner side;
- then the two learners align by dialogue;
- every gap means the teaching material is not yet comprehensive enough.

This file records the complete audit result and the dialogue details.

## Agents

| Role | Agent | Scope |
| --- | --- | --- |
| Application Learner | Boole (`019f0ba2-db3e-72f1-80d8-b37f8033e14b`) | `examples/benchmark_apps`, `examples/paper_reproduction`, public app wrappers, and archived harnesses exposed by wrappers. |
| Tutorial Learner | Locke (`019f0ba3-07d7-76a3-ad07-fcace6e14efa`) | `README.md`, `tutorials/current`, `examples/tutorial_programs`, `docs/learn`, public example README files. |

Both agents were read-only. No files were edited by either sub-agent.

## High-Level Result

Both agents agree:

Current V4 tutorials are strong enough to teach:

- planner probes;
- relation-row thinking;
- simple pure-Python relation/continuation prototypes;
- dry-run surface discovery;
- basic partner selection;
- a planner-level recipe map for all ten benchmark apps.

Current V4 tutorials are not yet strong enough to teach a user to build the
full benchmark apps or paper-reproduction apps end to end without opening full
app/harness source and inferring missing pieces.

This is not mainly a wording problem. It is a missing executable-teaching
problem: app lowering, continuation contracts, harness protocol, and
paper-scope behavior are not yet taught deeply enough.

## Application Learner Findings

The Application Learner studied:

- `examples/benchmark_apps/README.md`
- `examples/paper_reproduction/README.md`
- all ten `examples/benchmark_apps/*/v4_app.py`
- `examples/benchmark_apps/_support/v4_public_entry.py`
- `src/rtdsl/_example_support/benchmark_harness_compat.py`
- archived harnesses exposed by the public wrappers under
  `tools/_archive/history/v4_0_benchmark_harness_archive_2026-06-27/examples/benchmark_apps`
- tutorial/app recipe links that the app directories expose.

### Application Map

| App | Concept | Operator / Primitive / Partner Surface | User Prerequisites |
| --- | --- | --- | --- |
| RTDBSCAN | Density clustering from fixed-radius neighbor graph, then component merge. | Public map says `fixed_radius` + `component_union`, partners `torch`, `numba`; harness uses fixed-radius rows/count-threshold, CuPy/Numba component continuations, prepared OptiX variants. | DBSCAN core/border/noise semantics, union-find/component signatures, device columns, validation by canonical component sizes. |
| RTNN | Nearest/ranked neighbor evidence. | `point_group_nearest` + `ranked_summary`, partners `torch`, `rtdl_native`; harness uses ranked prepared runner paths. | kNN/ranked summaries, batching, prepared-session reuse, checksum-style validation. |
| Triangle Counting | Lower graph triangles to ray/triangle evidence and grouped counts. | `any_hit` + `grouped_i64`, partners `torch`, `cupy`, `numba`; harness maps graph contracts to generic ray/triangle weighted or hit-count summaries. | Graph orientation/witnesses, ray/triangle lowering, grouped integer reductions, oracle count comparison. |
| Robot Collision | Sampled link/pose geometry to compact collision flags. | `any_hit`, partners `torch`, `rtdl_native`; harness uses transformed 2D link triangles, prepared static triangle scenes, grouped segment any-hit flags. | Triangle intersection, pose/link lowering, grouped query flags, sampled-vs-continuous collision contract. |
| RayDB-style | Encode table predicates as rays/primitives, then grouped aggregates. | `any_hit`, `weighted_sum`, `grouped_sum`, partners `torch`, `cupy`; harness uses primitive grouped reductions and V4 device grouped reductions. | Columnar query encoding, primitive payloads, deduplication, grouped count/sum/min/max semantics. |
| LibRTS Spatial Index | AABB point/range containment and intersection counts. | `aabb_index_query`, partner `rtdl_native`; harness runs point_contains/range_contains/range_intersects and prepared AABB sessions. | AABB predicates, prepared query sets, WKT fixtures, mutable index pressure points. |
| Contact Manifold | AABB broadphase candidate discovery, exact triangle refinement, bounded witness collection. | Public map says `aabb_index_query` + `closest_hit_argmin`, partners `rtdl_native`, `torch`; archived harness uses `AABB_INDEX_QUERY_2D` plus `COLLECT_K_BOUNDED` rows. | Broadphase/narrowphase split, triangle contact witnesses, row-capacity/overflow behavior. |
| Spatial RayJoin | PIP, line-segment intersection, overlay seed joins from spatial datasets. | `aabb_index_query` + `any_hit`, partners `rtdl_native`, `torch`; harness uses PIP kernels, prepared OptiX point/shape and segment-pair paths, compact-mask Numba continuations. | Spatial join semantics, CDB-like datasets, topology streams, prepared OptiX routes, PIP boundary handling. |
| Barnes-Hut | Aggregate frontier over spatial tree, then weighted vector force sum. | `aggregate_frontier` + `grouped_sum`, partners `rtdl_native`, `cupy`; harness uses bucketized aggregate trees, aggregate-frontier rows/device columns, CuPy/Numba weighted vector continuations. | Barnes-Hut opening criterion, tree/frontier rows, vector reductions, tolerance validation. |
| Hausdorff XHD | Threshold or exact nearest-witness distance between point sets. | `fixed_radius` + `point_group_nearest`, partner `torch`; harness also exposes CuPy/OpenMP baselines and grouped/adaptive nearest-witness methods. | Directed/undirected Hausdorff, nearest-distance argmax, threshold search, numeric tolerances. |

### Paper-Reproduction Apps

| Paper-reproduction app | Current behavior | Dependency |
| --- | --- | --- |
| RT-BarnesHut | `examples/paper_reproduction/rt_barneshut.py` forwards to archived `barnes_hut`. | Depends on Barnes-Hut aggregate-frontier and vector-continuation concepts. |
| RayJoin | `examples/paper_reproduction/rayjoin.py` forwards to archived `spatial_rayjoin`. | Depends on Spatial RayJoin topology, boundary, PIP/LSI, and prepared route concepts. |

### Application-Side Tutorial Dependency Summary

The tutorial ladder teaches the shared skeleton: describe relation, plan
operator, prepare, run, continue. Exact app recipe concepts are centralized in
`tutorials/current/07_benchmark_apps.md` and
`examples/tutorial_programs/benchmark_app_recipes.py`.

The one-skill scripts cover fixed-radius rows, nearest witness, any-hit flags,
grouped sum, PIP AABB broadphase, and spatial join broadphase/refinement.

Application-side conclusion:

The tutorials are enough to understand the planner-level shape of all ten apps.
They are not enough to independently write the full harness-level apps.

## Tutorial Learner Findings

The Tutorial Learner studied:

- `README.md`
- `docs/public_documentation_map.md`
- `docs/learn/README.md`
- `docs/learn/operator_catalog.md`
- `docs/learn/partner_choice.md`
- `docs/learn/performance_wording.md`
- `docs/learn/source_tree_doctor.md`
- `tutorials/current/README.md`
- `tutorials/current/01_first_run.md` through `08_choose_a_partner.md`
- `examples/README.md`
- `examples/tutorial_programs/README.md`
- all public `examples/tutorial_programs/*.py`
- `examples/benchmark_apps/README.md`
- `examples/paper_reproduction/README.md`

### Ordered Concepts Learned

1. RTDL V4 is a Python eDSL/operator-pushdown surface for reusable RT-core GPU
   operators, with `import rtdsl.v4 as rtdl_v4` as the front door.
2. The mental model is relation first: describe RT-shaped work, choose a
   partner, plan, prepare, run, and continue.
3. First runnable skill is planner inquiry, not GPU execution.
4. Relation rows can be sorted and continued into nearest-witness or grouped
   summaries.
5. Operators are generic surfaces, not app names.
6. Planning reveals support, partner, API surface, and the next prepare function
   to inspect.
7. Prepare/run/continue is the real execution shape, with dry-run examples
   before real CUDA arrays.
8. Measurement should split setup, hot relation work, continuation, and
   validation.
9. Benchmark apps are recipes over relation/operator/partner/continuation/
   validation, not unrelated one-off kernels.
10. Partner choice is explicit: Torch, CuPy, Numba, or RTDL native.

### What A Learner Can Implement From Current Tutorials

| Tutorial Stage | What a learner can implement |
| --- | --- |
| First run | Run front-door checks and read release/catalog metadata. |
| Hello world | Build planner-only scripts that ask whether an operator/partner is supported. |
| Sorting rows | Implement pure-Python row sorting, nearest-by-query, and grouped weight sums. |
| Relations/operators | Model fixed-radius neighbors, nearest witness, ray/triangle any-hit, grouped sum, PIP broadphase, and spatial join broadphase as visible row pipelines. |
| Prepare/run/continue | Adapt advanced device-array examples if already comfortable with Torch CUDA device columns and prepare/session APIs. |
| Measurement | Build a small measurement record and avoid broad performance overclaims. |
| Benchmark recipes | Choose planner-level recipes for the 10 benchmark apps, but not implement full app logic from scratch. |
| Partner choice | Reject unsupported callback shapes and keep arbitrary mutation/dynamic output outside traversal. |

Tutorial-side conclusion:

A new learner can build planner probes, pure-Python relation/continuation
prototypes, small dry-run surface checks, and scoped adaptations of tutorial
device-array examples.

They cannot confidently build full benchmark apps or paper reproductions
end-to-end without opening the full app sources and inferring missing domain
logic, input contracts, harness behavior, and validation methodology.

## Dialogue Transcript

### Round 1: Application Learner Cross-Examines Tutorial Learner

**Q1. Barnes-Hut / RT-BarnesHut**

Required app-level concept: building an `aggregate_frontier`, interpreting
aggregate/exact frontier rows, then applying weighted vector force
continuation.

Current tutorial location: `tutorials/current/07_benchmark_apps.md` Barnes-Hut
recipe and `05_prepare_run_continue.md` planner dry-run pattern.

Proof needed: show a runnable tutorial or tutorial-derived sequence that
teaches aggregate tree/frontier row construction before opening
`examples/benchmark_apps/barnes_hut/*`. If the only evidence is a planner call
to `aggregate_frontier`, mark GAP.

**Q2. RTDBSCAN**

Required app-level concept: `component_union` over fixed-radius neighbor/core
rows, including cluster-label/signature validation.

Current tutorial location: `fixed_radius_neighbors.py`,
`07_benchmark_apps.md` RTDBSCAN recipe, `08_choose_a_partner.md` partner
examples.

Proof needed: identify where a learner sees runnable component-union behavior,
not just `plan_operator_request_v4("component_union")`. If no tutorial emits
components from neighbor rows, mark GAP.

**Q3. RTNN**

Required app-level concept: ranked summary over bounded fixed-radius/nearest
candidate rows, including k/radius/top-k validation.

Current tutorial location: `nearest_neighbor.py`, `sorting_rows.py`,
`benchmark_app_recipes.py`.

Proof needed: show that tutorials teach `ranked_summary` as a runnable
continuation with expected input/output rows. If they only teach nearest argmin
and planner probing, mark GAP.

**Q4. Contact Manifold**

Required app-level concept: AABB broadphase candidate rows plus bounded
contact/witness collection; public map says `closest_hit_argmin`, archived
harness uses `COLLECT_K_BOUNDED`.

Current tutorial location: `point_in_polygon.py`, `spatial_join_lsi.py`,
`07_benchmark_apps.md` Contact Manifold recipe.

Proof needed: explain whether tutorials teach `closest_hit_argmin` or
`collect_k_bounded` sufficiently to build bounded witness capacity, overflow,
and validation behavior. If not, mark GAP.

**Q5. Spatial RayJoin / RayJoin Paper Wrapper**

Required app-level concept: CDB dataset loading, PIP/LSI/overlay workloads,
topology rows, boundary modes, owner-face/side filtering.

Current tutorial location: `point_in_polygon.py`, `spatial_join_lsi.py`,
`07_benchmark_apps.md` Spatial RayJoin recipe.

Proof needed: show where tutorials teach RayJoin-specific topology and boundary
policies rather than only simple AABB candidate-pair refinement. If absent,
mark GAP.

**Q6. RayDB-Style Query**

Required app-level concept: table-to-ray encoding, primitive payload columns,
deduplication, grouped count/sum/min/max over hit streams.

Current tutorial location: `continuation_grouped_sum.py`,
`ray_triangle_hits.py`, `07_benchmark_apps.md` RayDB-style recipe.

Proof needed: demonstrate a tutorial path that converts relational/table
predicates into ray/primitive workloads and payload columns. If tutorials only
show generic hit rows plus grouped sum, mark GAP.

**Q7. Hausdorff XHD**

Required app-level concept: directed Hausdorff as nearest-per-source followed
by max/min-distance summary; undirected composition; threshold search.

Current tutorial location: `nearest_neighbor.py`, `fixed_radius_neighbors.py`,
`sorting_rows.py`, `07_benchmark_apps.md` Hausdorff recipe.

Proof needed: show tutorial material that teaches directed/undirected
Hausdorff composition and threshold-search control flow. If only nearest
witness and fixed radius are covered, mark GAP.

**Q8. Robot Collision**

Required app-level concept: dynamic pose/link geometry lowering into grouped
ray/segment/triangle queries, compact link/pose flags,
sampled-vs-continuous collision contract.

Current tutorial location: `ray_triangle_hits.py`, `07_benchmark_apps.md`
Robot Collision recipe.

Proof needed: show where tutorials teach transforming app geometry into grouped
query primitives and validating compact collision flags. If they only teach
static ray/triangle any-hit, mark GAP.

**Q9. Triangle Counting**

Required app-level concept: graph-to-ray/triangle lowering,
orientation/witness policy, grouped integer reduction against graph oracle.

Current tutorial location: `ray_triangle_hits.py`,
`continuation_grouped_sum.py`, `07_benchmark_apps.md` Triangle Counting
recipe.

Proof needed: prove the tutorials teach the graph lowering contract, not merely
any-hit and grouped reduction separately. If the graph mapping must be inferred
from app source, mark GAP.

**Q10. LibRTS Spatial Index**

Required app-level concept: AABB point/range contains/intersects, prepared
query sets, WKT fixture inputs, mutation scenario pressure.

Current tutorial location: `point_in_polygon.py`, `spatial_join_lsi.py`,
`05_prepare_run_continue.md`, `07_benchmark_apps.md`.

Proof needed: distinguish what is teachable from tutorials: basic AABB
predicates may be sufficient, but prepared query sets, WKT fixtures, and
mutation behavior likely are not. Mark partial or GAP per sub-concept.

**Q11. All Benchmark Apps Using Harness Mode**

Required app-level concept: prepared-session cache/reuse, warmup/repeat
measurement, capacity probing, overflow handling, validation skip/compare
policies.

Current tutorial location: `06_measure_a_program.md`,
`05_prepare_run_continue.md`.

Proof needed: show tutorial coverage of these harness behaviors with runnable
examples. If measurement is only phase-label guidance and dry-run calls, mark
GAP.

**Q12. Paper Reproduction Wrappers**

Required app-level concept: reproducing paper-oriented routes through archived
harnesses, including paper-scope caveats and non-reproduction boundaries.

Current tutorial location: `examples/paper_reproduction/README.md`,
`07_benchmark_apps.md`.

Proof needed: show that public tutorials teach how to understand these wrappers
beyond "forward to harness." If the learner must open archived full app sources
to understand paper behavior, mark GAP.

### Round 2: Tutorial Learner Answers

| Q | Area | Tutorial Learner Verdict | Reason |
| --- | --- | --- | --- |
| 1 | Barnes-Hut / RT-BarnesHut | GAP | Tutorial gives only concept and planner recipe for `aggregate_frontier` + `grouped_sum`; no runnable aggregate tree/frontier row construction. |
| 2 | RTDBSCAN component union | GAP | Fixed-radius neighbor rows are visible, but component-union behavior is only planned/listed; no tutorial emits components or labels from neighbor/core rows. |
| 3 | RTNN ranked summary | GAP | Nearest-witness argmin is taught, but `ranked_summary` is only a planner recipe and is not clearly present in the public request-name catalog. |
| 4 | Contact bounded witnesses | GAP | `closest_hit_argmin` surface is visible, but bounded witness capacity, overflow handling, and `COLLECT_K_BOUNDED` behavior are not taught. |
| 5 | Spatial RayJoin topology policies | GAP | Tutorials teach simple AABB candidate-pair refinement and line-segment intersection, not CDB loading, topology rows, boundary modes, owner-face/side filtering, or RayJoin policy behavior. |
| 6 | RayDB-style query | GAP | Path shows generic hit rows, weighted sum, grouped sum, and primitive grouped-i64 reduction, but not table-to-ray predicate encoding, payload schema, dedup, or database aggregate semantics. |
| 7 | Hausdorff XHD composition | GAP | Path covers fixed-radius threshold and nearest-witness primitives, but not directed/undirected composition, max/min-distance summary, or threshold-search control flow. |
| 8 | Robot collision lowering | GAP | Tutorials show static ray/triangle any-hit and planner recipe for collision flags, but not dynamic pose/link lowering, grouped link/pose queries, sampled-vs-continuous contract, or compact flag validation. |
| 9 | Triangle graph lowering | GAP | Tutorial states graph structure is lowered to ray/triangle hit tests, but does not teach graph-to-ray/triangle contract, orientation/witness policy, or graph-oracle validation. |
| 10 | LibRTS spatial index | Partial | Basic AABB point/range predicates are covered by a tiny all-ops fixture. WKT fixture inputs and mutation pressure are not taught; prepared query sets are only tiny-fixture partial. |
| 11 | Benchmark harness mode | GAP | Measurement docs teach phase labels and some examples do warmup-style first run, but not harness cache/reuse, repeat strategy, capacity probing, overflow, or validation policy. |
| 12 | Paper reproduction wrappers | GAP | Public path says paper entrypoints exist and forward to corresponding implementations; it does not teach paper routes, archived harness behavior, paper-scope caveats, or non-reproduction boundaries. |

### Round 3: Application Learner Adjudication

| Q | Area | Tutorial Verdict | Application Adjudication |
| --- | --- | --- | --- |
| 1 | Barnes-Hut aggregate frontier | GAP | Accept. Planner mention is not enough to teach aggregate tree/frontier rows plus vector continuation. |
| 2 | RTDBSCAN `component_union` | GAP | Accept. Fixed-radius rows are covered; component union and cluster-signature validation are not taught runnable-first. |
| 3 | RTNN `ranked_summary` | GAP | Accept. Nearest argmin is covered; ranked/bounded summaries are a different continuation. |
| 4 | Contact bounded witnesses | GAP | Accept. Public recipe and harness diverge enough that `closest_hit_argmin` / bounded witness collection needs explicit teaching. |
| 5 | Spatial RayJoin topology policies | GAP | Accept. Simple spatial join does not teach CDB/topology/boundary/owner-face policy. |
| 6 | RayDB table-to-ray / payloads | GAP | Accept. Grouped sum tutorials do not cover predicate encoding, payload columns, or dedup. |
| 7 | Hausdorff composition | GAP | Accept. NN and fixed-radius concepts are primitives, not the directed/undirected Hausdorff algorithm. |
| 8 | Robot collision lowering | GAP | Accept. Static any-hit does not teach pose/link-to-query lowering or grouped compact flags. |
| 9 | Triangle graph lowering | GAP | Accept. Ray hits and grouped reductions are covered separately; graph-to-geometry contract is missing. |
| 10 | LibRTS | Partial | Accept. Basic AABB predicates are teachable; prepared query sets, WKT, mutation behavior are not. |
| 11 | Harness mode behavior | GAP | Accept. Current measurement docs are phase vocabulary, not harness protocol. |
| 12 | Paper wrappers | GAP | Accept. Wrappers only forward to archived harnesses; paper-scope behavior is not publicly learnable without source spelunking. |

## Gap Matrix

| Priority | Gap | Blocks |
| --- | --- | --- |
| P0 | No runnable `aggregate_frontier` tutorial. | Barnes-Hut and RT-BarnesHut understanding. |
| P0 | No runnable `component_union` tutorial from neighbor/core rows. | RTDBSCAN authoring. |
| P0 | No runnable `ranked_summary` / bounded ranked continuation tutorial. | RTNN authoring. |
| P0 | No bounded witness / `collect_k_bounded` tutorial. | Contact manifold authoring and capacity/overflow understanding. |
| P0 | No app-lowering tutorials for graph-to-geometry, robot pose/link lowering, Hausdorff composition, RayDB table-to-ray, RayJoin topology. | User cannot derive full benchmark apps from grassroots material. |
| P0 | No benchmark harness protocol tutorial. | User cannot understand serious app measurement, validation, repeats, capacity, overflow, or `--run-harness`. |
| P1 | Paper reproduction wrappers lack scope/methodology docs. | User can locate wrappers but not understand paper-oriented route behavior. |
| P1 | LibRTS advanced behavior not taught. | WKT fixtures, mutation pressure, richer prepared query sets remain unclear. |
| P1 | Input contracts are scattered across scripts. | Users must inspect code to know columns, dtypes, ownership, and outputs. |

## Required Remediation

### Must Fix Before Public Docs Are Truly Good Enough

1. Add runnable concept tutorials for missing operators/continuations:
   `aggregate_frontier`, `component_union`, `ranked_summary`,
   `closest_hit_argmin` or `collect_k_bounded`.
2. Add app-lowering tutorials for Triangle Counting, Robot Collision,
   Hausdorff, RayDB-style, and RayJoin.
3. Add a benchmark harness tutorial covering prepared sessions, warmup/repeat,
   validation, overflow/capacity, and what `--run-harness` means.
4. Add paper-wrapper docs for RT-BarnesHut and RayJoin explaining scope,
   routed app, supported claims, and what is intentionally not reproduced.

### Needed New Tutorial Programs / Docs

| Proposed file | Purpose |
| --- | --- |
| `examples/tutorial_programs/aggregate_frontier_rows.py` | Body points + aggregate cells -> frontier rows -> grouped vector sum. |
| `examples/tutorial_programs/component_union_from_radius.py` | Neighbor rows -> core flags -> component labels/signature. |
| `examples/tutorial_programs/ranked_summary_neighbors.py` | Candidate rows -> bounded top-k/ranked summary. |
| `examples/tutorial_programs/bounded_witness_collection.py` | Candidate rows -> bounded witness collection and overflow validation. |
| `examples/tutorial_programs/triangle_counting_graph_lowering.py` | Graph edges -> rays/triangles -> grouped triangle count. |
| `examples/tutorial_programs/robot_collision_lowering.py` | Poses/links/obstacles -> grouped any-hit flags. |
| `examples/tutorial_programs/hausdorff_distance_recipe.py` | Directed nearest witnesses -> max-min distance -> undirected result; optional threshold search. |
| `examples/tutorial_programs/raydb_table_to_ray.py` | Columnar records + predicate -> rays/primitives/payloads -> grouped aggregate. |
| `examples/tutorial_programs/rayjoin_topology_intro.py` | PIP/LSI/overlay concepts, boundary policy, topology rows. |
| `tutorials/current/09_benchmark_harness_protocol.md` | Prepared-session cache, warmup/repeat, capacity/overflow, validation modes. |
| `examples/paper_reproduction/paper_reproduction_scope.md` | RT-BarnesHut and RayJoin wrapper behavior and scope boundaries. |

### Later Advanced Docs

1. LibRTS WKT fixtures, mutation pressure, and prepared-query reuse after the
   basic AABB tutorial.
2. RayJoin CDB/topology/boundary modes after a simpler RayJoin lowering
   tutorial exists.
3. RayDB min/max/avg and additional partner continuation variants after
   table-to-ray and primitive payload basics.
4. Barnes-Hut optimized prepared OptiX/CuPy/Numba routes after aggregate
   frontier and vector continuation basics.

## Final Alignment Conclusion

The two-agent dialogue fully aligns: current V4 public tutorials are clean and
much better than the earlier black-box examples, but they are not yet complete
teaching material for the benchmark and paper-reproduction suite. The remaining
work is concrete: add executable app-lowering tutorials, missing continuation
tutorials, harness protocol documentation, and paper-reproduction scope docs.

Until those are added, the tutorial path should be described as teaching the
V4 programming model and planner-level app recipes, not as fully teaching users
to independently write every benchmark and paper-reproduction app end to end.
