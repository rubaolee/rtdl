# RTDL V4 Tutorial Structure And Content Plan

This plan defines the tutorial structure to build after the auditable goals. It
is a design plan, not a claim that the current tutorials already satisfy it.

## Ground Rules

1. First audit existing tutorial programs and reuse them when they already teach
   the right RTDL concept.
2. Do not replace a working old tutorial blindly.
3. A tutorial must show the lowering from user problem to RTDL relation,
   operator, continuation, and output.
4. A tutorial must not be a hidden `do_everything()` wrapper.
5. Benchmark apps and paper reproduction apps are exams, not basic lessons.

## Public Example Categories

The public `examples/` tree should have three clear categories:

| Category | Purpose | User expectation |
| --- | --- | --- |
| `examples/tutorial_programs/` | Small concept programs | Learn one RTDL idea at a time |
| `examples/benchmark_apps/` | The 10 standard benchmark apps | See full benchmark workloads |
| `examples/paper_reproduction/` | Paper-specific reproduction workloads | Reproduce external paper workloads under explicit contracts |

Tutorials should link primarily to `examples/tutorial_programs/`. Benchmark and
paper examples should link back to the concept programs they depend on.

## Tutorial Lesson Ladder

### 00. What RTDL Is

Content:
- RTDL expresses queries as relations over geometric or ray-traversal candidates.
- RT cores help generate candidate/hit rows.
- Continuations reduce, rank, group, or refine those rows.
- Partners such as Torch, CuPy, and Numba are explicit choices, not hidden magic.

Runnable program:
- none required, or `hello_world.py`.

User should learn:
- RTDL is not "call OptiX directly".
- RTDL is not a general CPU algorithm replacement.
- RTDL is useful when the problem can be lowered to traversal plus continuation.

### 01. First RTDL Kernel

Program:
- `hello_world.py`

Content:
- Declare ray and triangle inputs.
- Traverse candidate ray/triangle pairs.
- Refine candidates with a hit predicate.
- Emit result rows.
- Let ordinary Python map the result row to `hello, world`.

Lowering taught:
- Input geometry -> traverse -> refine -> emit rows -> Python program result.

Must not:
- Hide the RTDL kernel behind a one-line app wrapper.

### 02. Relation Rows

Program:
- `v4_frontdoor_quickstart.py` or a dedicated relation-row example.

Content:
- Explain query id, candidate id, hit facts, distance facts, weights, and output
  rows.
- Show that RTDL work is often row production plus continuation.

Lowering taught:
- Objects or rays -> candidate/hit relation rows.

### 03. Sorting, Rank, And Top-K

Program:
- `sorting_rows.py`

Content:
- Teach sorting as the original Goal97 ray-hit sorting demo.
- Encode each nonnegative integer as a horizontal probe segment and a vertical
  key segment.
- Segment-intersection hit count becomes a rank signal.
- Python reconstructs stable ascending and descending order from RTDL rows.

Lowering taught:
- Values -> segment geometry.
- Probe/key segment pairs -> intersection hit rows.
- Hit rows -> hit counts -> stable sorted output.

Must say explicitly:
- Opaque Python comparators belong to ordinary CPU/GPU sort.
- Do not replace this with a planner/catalog demo.
- Do not claim this is a general sorting library.

### 04. Fixed-Radius Neighbors

Program:
- `fixed_radius_neighbors.py`

Content:
- Explain query points, indexed points, radius, neighbor rows.
- Show candidate generation and count/row output.

Lowering taught:
- Points + radius -> neighbor relation rows.

Apps prepared:
- RTDBSCAN, RTNN, component union.

### 05. Nearest Neighbor / Nearest Witness

Program:
- `nearest_neighbor.py`

Content:
- Explain nearest as candidate rows plus distance facts plus argmin
  continuation.
- Show query ids, candidate ids, distances, nearest witness rows.

Lowering taught:
- Query points -> candidate rows -> distance/witness facts -> nearest row per
  query.

Must not:
- Only call a black-box `nearest_neighbor()` helper.

Apps prepared:
- RTNN, Hausdorff, contact witness patterns.

### 06. Partner Choice

Program:
- `partner_choices.py`

Content:
- Show the same operator request with different partners.
- Explain when RTDL native, Torch, CuPy, and Numba are appropriate.
- State unsupported/deferred combinations honestly.

Lowering taught:
- Operator intent is stable; partner is execution policy.

### 07. AABB Index Predicates

Program:
- `aabb_spatial_index_predicates.py`

Content:
- Explain boxes, point containment, range containment, range intersection.
- Show predicate-specific relation rows.

Lowering taught:
- Spatial predicate -> AABB candidate rows -> count or row summaries.

Apps prepared:
- LibRTS spatial index, broadphase collision, spatial joins.

### 08. Point In Polygon

Program:
- `point_in_polygon.py`

Content:
- Explain point query, polygon boundary representation, hit/winding or
  containment facts.
- Keep polygon algorithm details minimal; focus on RTDL relation shape.

Lowering taught:
- Points + polygon boundary -> hit/containment rows -> point classification.

Apps prepared:
- Spatial RayJoin PIP, RayJoin paper reproduction support.

### 09. Line Segment Intersection / Spatial Join

Program:
- `spatial_join_lsi.py`

Content:
- Explain segments, AABB broadphase, candidate pairs, exact refinement.
- RTDL accelerates candidate relation generation; app logic owns exact predicate
  if needed.

Lowering taught:
- Segment sets -> AABB rows -> candidate pair rows -> exact intersection rows.

Apps prepared:
- Spatial RayJoin LSI, polygon overlay building blocks.

### 10. Ray/Triangle Hits

Program:
- `ray_triangle_hits.py`

Content:
- Explain rays, triangle scene, any-hit rows, closest-hit rows, hit flags.

Lowering taught:
- Ray stream + triangle scene -> hit relation rows -> flag/count/witness
  continuation.

Apps prepared:
- Triangle counting, RayDB-style queries, robot collision.

### 11. Grouped Continuations

Program:
- `continuation_grouped_sum.py`

Content:
- Explain group id, value, grouped sum/count/min/max.
- Show continuation after candidate rows, not as a separate unrelated trick.

Lowering taught:
- Relation rows -> group-by continuation -> summarized rows.

Apps prepared:
- Triangle counting, RayDB-style grouped queries, weighted reductions.

### 12. Component Union

Program:
- `component_union_from_radius.py`

Content:
- Explain how neighbor rows become graph edges.
- Explain union/component continuation.

Lowering taught:
- Neighbor relation rows -> graph edges -> connected components.

Apps prepared:
- RTDBSCAN-style clustering.

### 13. Aggregate Frontier

Program:
- `aggregate_frontier_rows.py`

Content:
- Explain aggregate tree traversal, frontier rows, weighted continuation.
- Show why frontier residency matters without exposing old internal process
  language.

Lowering taught:
- Body/tree query -> frontier rows -> grouped weighted vector continuation.

Apps prepared:
- Barnes-Hut.

### 14. Ranked Summary

Program:
- `ranked_summary_neighbors.py`

Content:
- Explain top-k/ranked summaries over neighbor rows.
- State current release boundary if a surface is not promoted.

Lowering taught:
- Candidate rows -> sort/rank within group -> top-k summary.

Apps prepared:
- RTNN and recommendation-style outputs.

### 15. Bounded Witness Collection

Program:
- `bounded_witness_collection.py`

Content:
- Explain collecting a bounded number of witnesses per query.
- Show output limits and correctness boundaries.

Lowering taught:
- Hit rows -> bounded per-query witness rows.

Apps prepared:
- Contact manifold, collision/contact witnesses.

### 16. Contact Manifold Lowering

Program:
- `contact_manifold_lowering.py`

Content:
- Explain broadphase rows, contact candidate rows, witness continuation.
- Keep physics-specific details out of the basic lesson.

Lowering taught:
- Object pairs -> broadphase candidates -> witness rows.

### 17. Triangle Counting Lowering

Program:
- `triangle_counting_graph_lowering.py`

Content:
- Explain graph motif search as ray/triangle or pair/hit relation construction.
- Show where RTDL produces hit/flag/count rows.

Lowering taught:
- Graph/query structure -> RT hit relation -> grouped count.

### 18. Robot Collision Lowering

Program:
- `robot_collision_lowering.py`

Content:
- Explain robot motion or segment sets as collision queries.
- Show hit flags, not a full robotics simulator.

Lowering taught:
- Motion/collision candidates -> any-hit flags -> safe/unsafe summary.

### 19. RayDB Table-To-Ray

Program:
- `raydb_table_to_ray.py`

Content:
- Explain table rows becoming rays and scene rows.
- Show any-hit, weighted sum, and grouped continuation choices.

Lowering taught:
- Table query -> ray stream -> hit rows -> database-style summary.

### 20. Measurement Phases

Program:
- `measure_phases.py`

Content:
- Explain setup, prepare, hot traversal, continuation, validation, and
  materialization.
- Teach users not to mix benchmark timing with tutorial timing.

Lowering taught:
- A program is measured as phases, not one unexplained wall-clock number.

### 21. Callback Planning Boundary

Programs:
- `operator_callback_planning.py`
- `custom_predicate_early_exit_planning.py`

Content:
- Explain what can be planned as a known operator/continuation.
- Explain what is deferred when the user asks for arbitrary action-shaped
  callback logic.

Lowering taught:
- Recognized operator -> planned V4 path.
- Arbitrary action callback -> explicit unsupported/deferred boundary.

## Benchmark-App Bridge

After the concept lessons, provide a bridge table:

| Benchmark app | Required concepts |
| --- | --- |
| RTDBSCAN | fixed-radius neighbors, component union, measurement phases |
| RTNN | fixed-radius neighbors, nearest witness, ranked summary |
| Triangle counting | ray/triangle hits, grouped continuation |
| Robot collision | ray/triangle hits, bounded witness/flag summary |
| RayDB-style | table-to-ray, any-hit, grouped reductions |
| LibRTS spatial index | AABB index predicates |
| Contact manifold | AABB broadphase, closest witness, bounded collection |
| Spatial RayJoin | AABB spatial join, LSI, PIP |
| Barnes-Hut | aggregate frontier, grouped weighted continuation |
| Hausdorff XHD | nearest witness, threshold/fixed-radius checks |

## Paper-Reproduction Bridge

Paper reproduction apps should not be tutorials. They should list prerequisites:

| Paper workload | Required RTDL concepts | Extra contract |
| --- | --- | --- |
| RT-BarnesHut | aggregate frontier, grouped weighted continuation, measurement phases | author-code comparison contract |
| RayJoin Section 5.7 Polygon Overlay | AABB spatial join, LSI, PIP, measurement phases | exact CDB inputs, author binaries, 8/8 pair completion |

## Per-File Audit Record

Each tutorial program should receive one audit row:

| File | Concept | Lowering shown | RTDL operator | Continuation | Output | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| `sorting_rows.py` | rank/sort lowering | items -> predecessor rows | AABB/range or ordered relation | grouped count -> rank | sorted rows | pending audit |
| `nearest_neighbor.py` | nearest witness | queries -> candidates | point-group nearest | argmin/ranked | nearest rows | pending audit |

This table should be completed for every tutorial program before claiming the
tutorial surface is release-quality.

## Final Gate

The tutorial surface is complete only when:

1. Every required concept has a runnable program.
2. Every program shows the lowering, not only a wrapper call.
3. Every tutorial command passes locally.
4. Public docs link to the correct examples.
5. Benchmark and paper apps can be mapped back to prerequisite concepts.
6. A reviewer can pick an unfamiliar workload and identify which RTDL concepts
   apply without reading internal history.
