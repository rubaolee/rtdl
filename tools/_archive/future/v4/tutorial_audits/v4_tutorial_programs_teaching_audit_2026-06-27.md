# V4 Tutorial Teaching Audit

Date: 2026-06-27

This is an internal tutorial-quality audit. It is intentionally not part of
the public first-time user path.

## Standard

A tutorial program is good only if it teaches how a user thinks in RTDL:

- how an app problem becomes an RT-shaped relation;
- how candidate generation, RT traversal, and continuation fit together;
- what RTDL owns and what app code owns;
- which partner is chosen and why;
- what the user would write before opening a full benchmark app.

A tutorial program is weak if it only calls a function that already performs
the whole idea. That style may be valid API documentation, but it is not a
teaching program.

## Overall Verdict

Current tutorial organization is improved. Rewrite pass 1 fixed the largest
concept-level failure: NN, fixed-radius, PIP, ray-hit, and spatial join now show
visible candidate rows, relation rows, and continuations instead of hiding the
lesson inside reference helpers.

The remaining risk is that some advanced surface examples still look like API
smoke examples unless the tutorial path clearly labels them as the second layer
after concept programs.

The right direction is to split tutorial programs into three levels:

1. Concept programs: transparent, tiny, mostly manual data-flow examples.
2. Surface programs: planner and prepare/run/continue examples.
3. App recipes: benchmark and paper-reproduction assembly maps.

## Required Rewrite Direction

Do not delete the existing surface examples. Reclassify them as advanced API
surface examples. Add or rewrite beginner concept examples so they expose the
logic.

Concrete rewrite rules:

- NN must show query points, candidate/search groups, distance calculation,
  nearest-witness row selection, then the V4 surface that accelerates that
  relation.
- PIP must show polygon bounds, candidate filtering, exact containment logic,
  then the AABB/RTDL broadphase surface.
- Ray/triangle must show ray segment, triangle geometry, hit flag meaning, and
  only then the any-hit surface.
- Fixed-radius must show radius checks and relation rows, not only call a
  helper.
- Spatial join must show broadphase pair rows and refinement rows.
- Partner choice must teach why Torch/CuPy/Numba/RTDL native differs, not only
  list statuses.
- Device-array examples must be marked advanced and should not be the first
  teaching path.

## Tutorial Program Audit

| File | Current teaching role | Expected user understanding | Does it teach RTDL thinking? | Does it mislead or merely appease? | Better action |
| --- | --- | --- | --- | --- | --- |
| `examples/tutorial_programs/__init__.py` | Package marker. | None. | Not applicable. | No. It is not a teaching file. | Keep as package marker; do not advertise. |
| `examples/tutorial_programs/hello_world.py` | First import and planner call. | User learns the V4 import and that operators are planned before running. | Yes, for first contact only. | No, but it is only a door opener. | Keep; add a sentence in tutorial docs that this is planning, not execution. |
| `examples/tutorial_programs/v4_frontdoor_quickstart.py` | Release/front-door summary. | User sees current surface count, partners, and next files. | Partial. It orients; it does not teach programming. | Partial risk: it can feel like status output instead of a lesson. | Keep as quickstart, but do not treat it as a concept tutorial. |
| `examples/tutorial_programs/sorting_rows.py` | Relation rows sorted and consumed by nearest/grouped continuations. | User sees relation rows as data and learns continuation by sorting/reducing. | Yes. This is a good small teaching program. | No. It exposes data flow. | Keep; possibly add comments naming relation -> continuation. |
| `examples/tutorial_programs/operator_primitives.py` | Catalog introspection. | User sees surface, primitive, continuation, partner. | Partial. It names concepts but does not show how data enters. | Partial risk: it can become vocabulary dumping. | Keep as reference-like tutorial; pair it after concrete relation examples. |
| `examples/tutorial_programs/partner_choices.py` | Partner planning matrix. | User sees explicit partner choice and deferred combinations. | Partial. Good for boundary learning, weak for why each partner is useful. | No deception, but too status-heavy. | Add small examples explaining Torch=device tensors, CuPy=continuation kernels, Numba=compiled predicate/union, RTDL native=prepared traversal/index. |
| `examples/tutorial_programs/fixed_radius_neighbors.py` | Radius neighbor data-flow example. | User learns candidate checks, neighbor relation rows, and count-threshold continuation. | Yes after rewrite. | No. The loop is visible. | Keep as concept-level program before the Torch device-array surface. |
| `examples/tutorial_programs/nearest_neighbor.py` | NN/nearest-witness data-flow example. | User learns search groups, candidate witness rows, and per-query argmin continuation. | Yes after rewrite. | No. It no longer hides NN behind a helper. | Keep as the required first NN lesson before `point_group_nearest_witness_torch_device_arrays.py`. |
| `examples/tutorial_programs/ray_triangle_hits.py` | Any-hit data-flow example. | User learns ray/primitive candidate hit tests and compact per-ray hit flags. | Yes after rewrite. | No. It shows hit reasons and candidate rows. | Keep as concept-level program before any-hit device-array surfaces. |
| `examples/tutorial_programs/continuation_grouped_sum.py` | Grouped continuation example. | User learns reducing relation rows into app output. | Yes. The loop is visible and app-owned. | No. It teaches the pattern cleanly. | Keep; later connect it to RayDB/Barnes-Hut examples. |
| `examples/tutorial_programs/measure_phases.py` | Measurement phase example. | User learns setup/hot/continuation/validation split with runnable code. | Yes. It shows timing sections directly. | No. | Keep and link from `06_measure_a_program.md`. |
| `examples/tutorial_programs/point_in_polygon.py` | PIP data-flow example. | User learns polygon bounds, candidate point/polygon rows, and exact containment rows. | Yes after rewrite. | No. Candidate filtering and containment are visible. | Keep as spatial concept program before full spatial apps. |
| `examples/tutorial_programs/spatial_join_lsi.py` | Spatial join broadphase plus LSI refinement. | User sees segment bounds, broadphase candidate pairs, and exact intersection rows. | Yes after rewrite. | No. Broadphase and refinement are visible. | Keep as bridge to Spatial RayJoin. |
| `examples/tutorial_programs/operator_callback_planning.py` | Callback boundary planner. | User learns supported fused operator vs deferred callback shapes. | Partial. It explains planner boundaries, not how to program a valid callback. | Partial risk: looks like policy output. | Keep as boundary demo; add separate valid predicate tutorial or enrich `custom_predicate_early_exit_planning.py`. |
| `examples/tutorial_programs/custom_predicate_early_exit_planning.py` | Constrained Numba predicate planning. | User learns pure boolean predicate shape and why unsafe mutation is rejected. | Partial to good after rewrite. It now leads with predicate contract and rejected program shape, though it still carries compact measured context for gates. | Low. It is now mostly programming-oriented. | Keep; later split measured context into a separate non-beginner example if needed. |
| `examples/tutorial_programs/fixed_radius_torch_device_arrays.py` | Advanced device-array surface example. | User learns prepare/run/continue with Torch device columns. | Good as advanced API example, bad as first tutorial. | No if labeled advanced; yes if presented as beginner lesson. | Keep but move after concept-level fixed-radius example. |
| `examples/tutorial_programs/point_group_nearest_witness_torch_device_arrays.py` | Advanced NN device-array surface. | User learns prepared point groups and Torch query columns. | Good as advanced surface, not as NN concept teaching. | Partial risk: if used alone, it hides why point groups exist. | Keep as advanced; pair with rewritten transparent NN concept tutorial. |
| `examples/tutorial_programs/ray_triangle_any_hit_flags_torch_device_arrays.py` | Advanced any-hit device-array surface. | User learns ray/triangle columns and output flags. | Good as API surface example. | No if advanced; weak for concept teaching. | Keep; point beginner users to `ray_triangle_hits.py` first after rewrite. |
| `examples/tutorial_programs/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py` | Advanced any-hit weighted-sum surface. | User learns fused any-hit plus weight continuation. | Good advanced example, but complex. | No if labeled advanced. | Keep; add a simpler conceptual weighted-hit program before it if needed. |
| `examples/tutorial_programs/primitive_grouped_i64_reduction_torch_device_arrays.py` | Advanced grouped primitive reduction. | User learns primitive groups, values, sum/count outputs. | Good advanced example, but dense. | No if advanced. | Keep; add a compact conceptual grouped reduction bridge or link to `continuation_grouped_sum.py`. |
| `examples/tutorial_programs/closest_hit_grouped_argmin_torch_device_arrays.py` | Advanced grouped argmin/closest-hit surface. | User learns grouped argmin device columns. | Good advanced API example, not beginner teaching. | Partial risk if used before relation-row sorting. | Keep; introduce after `sorting_rows.py` and a future conceptual argmin example. |
| `examples/tutorial_programs/aabb_index_all_ops_count.py` | AABB all-ops count example. | User learns point/box queries and count outputs. | Partial. Tiny fixture is visible, but runner does the logic. | Partial. It teaches the API more than AABB thinking. | Add manual point/box containment counts before the runner or create separate AABB concept tutorial. |
| `examples/tutorial_programs/benchmark_app_recipes.py` | 10-app planner recipe map. | User sees each app as relation + operator + continuation. | Partial to good as a map; not enough as construction tutorial. | Partial risk: "planner recipe" can masquerade as "how to implement app." | Keep as map, but each benchmark app needs a small concept tutorial or construction walkthrough before full source. |

## Tutorial Document Audit

| File | Current teaching role | Expected user understanding | Does it teach enough? | Does it mislead or merely appease? | Better action |
| --- | --- | --- | --- | --- | --- |
| `tutorials/current/README.md` | Tutorial index and outcomes. | User sees the learning path. | Partial. It lists goals but does not enforce concept-before-surface order strongly enough. | No, but it overstates readiness of the path. | Reorder into: concepts, surfaces, partners, apps. |
| `tutorials/current/01_first_run.md` | What RTDL is and first command. | User learns RTDL is about RT-shaped relations. | Partial. Needs a clearer "not magic function calls" statement. | No, but thin. | Add "RTDL programs are relation-building programs" framing. |
| `tutorials/current/02_hello_world.md` | Import and planner. | User learns planning one operator. | Good for first contact. | No. | Keep; clarify that planner output is not execution. |
| `tutorials/current/03_sorting_rows.md` | Relation-row continuation. | User learns sorting/top-k/grouped summaries. | Good. | No. | Keep and use as pattern for other concept tutorials. |
| `tutorials/current/04_relations_and_operators.md` | Central relation/operator lesson. | User should learn RTDL's core programming model. | Partial. It lists commands but needs walk-throughs of data flow. | Partial. Current version risks becoming a command index. | Expand with 2-3 worked examples: fixed-radius, NN, ray-hit. |
| `tutorials/current/05_prepare_run_continue.md` | Prepare/run/continue and device arrays. | User should learn execution phases. | Partial. It jumps to dry-run surface examples too fast. | Partial. It may teach "run these files" rather than "why phases exist." | Add a concept-level prepare/run/continue pseudo-example before device arrays. |
| `tutorials/current/06_measure_a_program.md` | Measurement phases and records. | User learns setup/hot/continuation/validation split. | Partial to good. The language is user-facing and not process-heavy, but it lacks a runnable measurement toy. | No clear deception. It is conceptually useful, but too passive. | Add a tiny runnable measurement program or extend an existing tutorial program with timing fields. |
| `tutorials/current/07_benchmark_apps.md` | App recipes. | User should learn how the 10 apps are assembled. | Partial. It is useful as a map but not enough as "write the app" tutorial. | Partial. It can be mistaken for implementation teaching. | Add "mini construction" links for each app: concept program -> operator surface -> full app. |
| `tutorials/current/08_choose_a_partner.md` | Partner choice. | User learns Torch/CuPy/Numba/native roles. | Partial to good. Needs more concrete examples of why one partner is chosen. | No deception, but too abstract. | Add scenario table and direct links to partner-specific tutorial programs. |

## Priority Fix Plan

1. Rewrite `nearest_neighbor.py` first because it is the clearest failure.
2. Rewrite `fixed_radius_neighbors.py`, `point_in_polygon.py`, and
   `ray_triangle_hits.py` to stop using black-box reference helpers as the
   main teaching mechanism.
3. Reframe device-array scripts as advanced surface examples in the README.
4. Expand `04_relations_and_operators.md` into the central concept lesson with
   small, visible data-flow examples.
5. Expand `07_benchmark_apps.md` so each app points to the relevant single-skill
   tutorial before the full app source.
6. Run public tutorial tests after every rewrite.

## One-Sentence Lesson

The public tutorial path must teach users how to decompose a problem into RTDL
relations, primitives, partners, and continuations. If a file only shows a
black-box helper call, it is not yet a tutorial; it is only an API smoke
example.

## Rewrite Pass 1 Record

After this audit, the following concept programs were rewritten from black-box
helper calls into visible data-flow examples:

| File | Original problem | Rewrite result |
| --- | --- | --- |
| `fixed_radius_neighbors.py` | Called `fixed_radius_neighbors_cpu`, hiding candidate checks. | Now shows explicit distance checks, neighbor relation rows, and count-threshold continuation rows. |
| `v4_frontdoor_quickstart.py` | Oriented users but omitted the explicit release-boundary flags required by the catalog gate. | Now keeps the quickstart user-facing while exposing the non-claim boundary fields expected by the release gate. |
| `nearest_neighbor.py` | Called `knn_rows_cpu`, hiding NN logic. | Now shows search groups, candidate witness rows, and per-query argmin nearest rows. |
| `point_in_polygon.py` | Called `pip_cpu`, hiding bounds and exact containment. | Now shows polygon bounds, candidate point/polygon rows, and exact containment rows. |
| `ray_triangle_hits.py` | Called `ray_triangle_any_hit_cpu`, hiding hit tests. | Now shows ray/triangle candidate rows, hit reasons, and per-ray any-hit rows. |
| `spatial_join_lsi.py` | Used helper calls for broadphase/refinement. | Now shows segment bounds, broadphase pair rows, and exact segment-intersection rows. |
| `measure_phases.py` | No runnable measurement tutorial existed. | New file shows setup, hot relation work, continuation, validation, and app output timing fields. |

Remaining distinction:

- Device-array files remain advanced surface examples, not beginner concept
  tutorials.
- `custom_predicate_early_exit_planning.py` still needs a separate teaching
  pass only if we want to remove measured context entirely from beginner output.
- `benchmark_app_recipes.py` remains a map, not a full app-construction
  tutorial.
