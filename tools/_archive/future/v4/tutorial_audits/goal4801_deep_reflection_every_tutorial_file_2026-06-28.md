# Goal4801 Deep Reflection: Every Current Tutorial File

Date: 2026-06-28

Scope:

- `tutorials/current/*.md`
- `examples/tutorial_programs/*.py`
- `examples/tutorial_programs/README.md`

This audit asks three questions for every tutorial file:

1. Is this file reasonable in the current V4 tutorial path?
2. What is missing or weak?
3. How should it improve?

## Overall Judgment

The tutorial system is now directionally correct: it starts from RTDL kernel and
relation thinking, separates V4 runtime/operator surfaces from first lessons,
and keeps benchmark apps as a composition check rather than the first teaching
unit.

It is not yet in its best possible teaching state.

The main weakness is uneven depth. Lessons 01-14 are mostly real tutorials with
commands, kernel shape, visible flow, V4 mapping, and next step. Lessons 15-24
are much thinner. They are acceptable as bridge notes, but not yet as strong
teaching chapters. The runnable programs are better than the markdown in many
places: several Python files print the data flow clearly, while their matching
markdown page only summarizes it.

The next improvement should not be another architecture debate. It should be a
teaching-quality pass that expands thin markdown chapters into the same
standard pattern used by lessons 05-14.

## Standard For A Best-State Tutorial File

A current tutorial file is best-state only if it has:

- a clear lesson purpose;
- a runnable command;
- a small input example;
- the RTDL kernel/relation mental model;
- visible output rows or expected output;
- a "what the user owns" section;
- V4 mapping only after the relation is clear;
- one concrete next step;
- no internal process wording;
- no claim that a companion/front-door API is the programming model.

## Markdown Tutorial Audit

| File | Reasonable? | Missing or weak | Improvement |
| --- | --- | --- | --- |
| `tutorials/current/README.md` | Yes. It correctly states the learning path and separates language-layer lessons from runtime lessons. | It is a long capability list, not a diagnostic guide. It does not mark which lessons are full tutorials versus bridge notes. | Add a small stage map: Foundations, Relations, Continuations, App lowerings, Runtime surfaces. Mark 15-24 as advanced bridge lessons unless expanded. |
| `tutorials/current/01_first_run.md` | Yes. It gives the right first mental model and no longer pushes the V4 front door too early. | It is conceptual and short. It does not show the actual row emitted by hello world. | Add one tiny output-row sketch before linking to lesson 02. |
| `tutorials/current/02_hello_world.md` | Yes. This is a real first lesson and now uses the original simple hello-world spirit. | It still has a compact kernel snippet but does not fully connect the two triangles per rectangle to the emitted hit count. | Add a two-row mini table: rectangle id, triangles hit, label selected. |
| `tutorials/current/03_sorting_rows.md` | Yes. It teaches sorting as RTDL lowering, not as a black-box sort API. | The geometric transformation is still mentally demanding. It could use one diagram or table mapping value to segment and hit count. | Add a worked 4-value example before the full command. |
| `tutorials/current/04_relations_and_operators.md` | Yes. This is the key philosophical bridge: kernel first, V4 second. | It mixes `operator_primitives.py`, `fixed_radius_neighbors.py`, and `v4_frontdoor_quickstart.py`; a beginner may still run front door before understanding output. | Add an explicit "stop here if rows are unclear" check before the V4 front-door command. |
| `tutorials/current/05_fixed_radius_neighbors.md` | Yes. Strong tutorial shape: question, kernel mode, visible flow, V4 mode, both modes, user ownership. | Needs a small visual coordinate example for users new to radius search. | Add a two-query, four-point sketch or table directly in the markdown. |
| `tutorials/current/06_nearest_witness.md` | Yes. Strong tutorial and good contrast with fixed radius. | It should spell out tie-break behavior in the nearest-witness result. | Add a tie case and expected winner rule. |
| `tutorials/current/07_aabb_predicates.md` | Yes. Good broadphase lesson. | It does not strongly enough distinguish broadphase candidates from final app truth. | Add a "candidate is not answer" warning with one false-positive AABB example. |
| `tutorials/current/08_point_in_polygon.md` | Yes. Good RTDL lowering lesson with rows and V4 mapping. | The point-in-polygon parity idea may be too implicit. | Add a short odd/even crossing explanation and expected rows. |
| `tutorials/current/09_line_segment_intersection_spatial_join.md` | Yes. Good LSI and spatial join bridge. | It ends with a prose "Next: later lessons..." instead of a normal link. | Convert the next step into links to ray/triangle hits and grouped continuations. |
| `tutorials/current/10_ray_triangle_hits.md` | Yes. Core RT relation tutorial. | Could better explain why this is a generic primitive used by many apps. | Add a small "same hit rows, different app meanings" table. |
| `tutorials/current/11_grouped_continuations.md` | Yes. Important and mostly clear. | It ends with a prose future pointer instead of a normal next link. It also needs a clearer boundary between hit rows and grouped output. | Add a before/after row table and link to component union. |
| `tutorials/current/12_component_union_from_radius.md` | Yes. Strong continuation lesson. | The union-find concept is assumed. | Add a tiny two-edge component example. |
| `tutorials/current/13_bounded_witness_collection.md` | Yes. Strong bounded-output lesson. | Overflow validation is mentioned but could be more concrete. | Add an example where `k=2` and three witnesses exist, showing overflow flag. |
| `tutorials/current/14_aggregate_frontier_rows.md` | Mostly yes. It is honest that aggregate frontier is not an `@rt.kernel` predicate. | It ends with a broad pointer instead of a normal next link. It also needs clearer input/output table for the weighted continuation. | Add a frontier row table and link to ranked summary neighbors. |
| `tutorials/current/15_ranked_summary_neighbors.md` | Partly. It is coherent but thin. | No visible output, no command output snippet, no exercise, no link back to nearest-witness lesson. | Expand to the 05-14 template with input rows, ranked rows, and top-k output. |
| `tutorials/current/16_contact_manifold_lowering.md` | Partly. Correct boundary: RTDL teaches row pipeline, not physics. | Too short for a hard concept. No concrete candidate/witness rows. | Add a toy pair with two witnesses, kept witness, and overflow state. |
| `tutorials/current/17_graph_triangle_counting_lowering.md` | Partly. Correctly avoids app-specific kernel framing. | It explains row types but does not show a complete mini graph result. | Add a three-edge triangle example and grouped count output. |
| `tutorials/current/18_robot_collision_lowering.md` | Partly. Correctly keeps robot semantics outside RTDL. | Too short and easy to read as "just any-hit again." | Add a two-pose example with link segment rows and pose collision flags. |
| `tutorials/current/19_raydb_table_to_ray.md` | Partly. Good payload-preservation idea. | Missing concrete table rows and resulting hit payload rows. | Add a small table with `customer_id`, `amount`, primitive hit, and grouped sum. |
| `tutorials/current/20_hausdorff_composition.md` | Partly. Correctly explains exact witness versus threshold decision. | Too terse for a composition lesson. | Add two directed passes with concrete distances and final max. |
| `tutorials/current/21_partner_choice_device_arrays.md` | Partly. Correctly says partner is execution policy, not meaning. | Needs a clearer decision tree for Torch versus CuPy versus Numba versus native. | Add "choose partner when..." table and one rejected-partner example. |
| `tutorials/current/22_measurement_phases.md` | Partly. Concept is right. | It is close to a checklist, not a tutorial. No sample phase numbers. | Add a fake but clearly labeled timing table to teach interpretation. |
| `tutorials/current/23_callback_planning_boundary.md` | Partly. Boundary is correct and important. | Needs clearer examples of how to rewrite an action-shaped callback into rows plus continuation. | Add one rejected custom action and its decomposed RTDL form. |
| `tutorials/current/24_benchmark_app_bridge.md` | Partly. Correctly says benchmark apps are composition checks, not first tutorials. | Too short to prove the learning path can build the apps. | Add a 10-app table mapping each app to prerequisite tutorial programs. |
| `examples/tutorial_programs/README.md` | Yes. It now clearly separates core kernel-first path from operator companions. | The core command list is long and intimidating. | Add a short "minimum path" of 5 commands before the full path. |

## Tutorial Program Audit

| File | Reasonable? | Missing or weak | Improvement |
| --- | --- | --- | --- |
| `examples/tutorial_programs/__init__.py` | Yes as package marker, but it is not a tutorial. | Could be mistaken by file-count audits as a tutorial file. | Exclude it explicitly in audit tests and docs, as already done. |
| `examples/tutorial_programs/hello_world.py` | Yes. It is the right first executable: small, visual, kernel-first. | Could expose the intermediate emitted row more visibly for readers who only run it. | Add optional `--explain` output later, not required for current release. |
| `examples/tutorial_programs/sorting_rows.py` | Yes. It is valuable because it teaches non-obvious RTDL lowering. | It is easy to misunderstand as a production sort. It already states no V4 sort claim, but could print a smaller default case. | Keep current warning; consider defaulting to fewer values in beginner mode. |
| `examples/tutorial_programs/operator_primitives.py` | Yes as vocabulary map, not as execution lesson. | It is abstract and may feel like catalog output. | Add one "read this after sorting" sentence in output or README. |
| `examples/tutorial_programs/fixed_radius_neighbors.py` | Yes. Strong dual-mode program. | Good enough. Minor improvement: print a tiny coordinate diagram in visible mode. | Optional visual-only improvement. |
| `examples/tutorial_programs/nearest_neighbor.py` | Yes. Strong dual-mode program. | Needs explicit tie-break in output. | Add tie-break field if a tie example is introduced. |
| `examples/tutorial_programs/aabb_spatial_index_predicates.py` | Yes. Real kernel and useful predicate lesson. | Broadphase versus final predicate could be more explicit in output. | Add one false-positive candidate row if not already present. |
| `examples/tutorial_programs/point_in_polygon.py` | Yes. Real kernel and useful spatial primitive. | Parity/crossing reasoning could be more visible. | Add `crossing_count` in visible payload if feasible. |
| `examples/tutorial_programs/spatial_join_lsi.py` | Yes. Real kernel and good spatial join primer. | Needs to make topology/boundary policy handoff more explicit. | Cross-link output to `rayjoin_topology_intro.py`. |
| `examples/tutorial_programs/rayjoin_topology_intro.py` | Yes as relation-first topology companion. | It has no actual kernel and is thinner than LSI. | Add more explicit before/after topology rows. |
| `examples/tutorial_programs/partner_choices.py` | Yes. Correctly teaches partner as policy after relation shape. | It may still feel like planner API first. | Add a relation-name field before each partner plan. |
| `examples/tutorial_programs/ray_triangle_hits.py` | Yes. Strong generic any-hit lesson. | Could show app interpretations of same rows. | Add optional visible examples: collision, triangle count, RayDB. |
| `examples/tutorial_programs/continuation_grouped_sum.py` | Yes. Critical continuation lesson. | It should make "rows before continuation" impossible to miss. | Add separate printed sections for raw hit rows and grouped result. |
| `examples/tutorial_programs/measure_phases.py` | Yes as measurement concept program. | It is relation-first but not a kernel program; needs concrete numbers or phase rows. | Add a sample phase table in output. |
| `examples/tutorial_programs/component_union_from_radius.py` | Yes. Strong bridge from rows to components. | Union-find is assumed. | Add a small `edges -> labels` explanation in visible payload. |
| `examples/tutorial_programs/bounded_witness_collection.py` | Yes. Important bounded-output lesson. | Overflow semantics should be more explicit. | Add a test case where overflow is true. |
| `examples/tutorial_programs/aggregate_frontier_rows.py` | Mostly yes. It honestly explains the relation shape and runtime gap. | It contains a real `@rt.kernel` marker in helper text/classification context but says aggregate frontier is not exposed as predicate. That is subtle. | Make the output wording even clearer: relation-first tutorial, not a literal aggregate-frontier kernel surface. |
| `examples/tutorial_programs/ranked_summary_neighbors.py` | Partly. Useful relation-first program. | No real kernel, and ranked summary is planner-deferred. | Keep it, but expand output with concrete ranked rows and state that it is capability teaching, not measured V4 surface. |
| `examples/tutorial_programs/contact_manifold_lowering.py` | Partly. Correct relation-first scope. | Too many physics terms with little concrete row output. | Add toy shape-pair and witness rows. |
| `examples/tutorial_programs/triangle_counting_graph_lowering.py` | Yes. It explains the important triangle-counting lowering. | It is relation-first, not kernel-decorated. That is acceptable but should stay explicit. | Add one markdown cross-reference to grouped continuations. |
| `examples/tutorial_programs/robot_collision_lowering.py` | Partly. Correctly avoids teaching robot planning. | Needs more row details to avoid seeming like "call any_hit." | Add pose/link rows and per-pose reduction rows to output. |
| `examples/tutorial_programs/raydb_table_to_ray.py` | Partly. Good payload-preservation lesson. | Needs a clearer SQL/table-to-ray analogy in output. | Add table input rows and resulting grouped aggregate rows. |
| `examples/tutorial_programs/hausdorff_distance_recipe.py` | Partly. Correct composition, but thin. | It needs exact witness versus threshold examples. | Add both outputs side by side. |
| `examples/tutorial_programs/benchmark_app_recipes.py` | Yes as bridge, not first lesson. | Long output may overwhelm. It lists planner-level surfaces but not prerequisite tutorial names per step. | Add `learn_first` field per recipe step. |
| `examples/tutorial_programs/v4_frontdoor_quickstart.py` | Yes as operator companion. | Still tempting as a first copied command because it is named quickstart. | Consider renaming in V4.1 or adding stronger first-line output: "not first lesson." |
| `examples/tutorial_programs/operator_callback_planning.py` | Yes as boundary lesson. | Needs a rewrite example for complex callback. | Print a suggested decomposition shape for `complex-callback`. |
| `examples/tutorial_programs/custom_predicate_early_exit_planning.py` | Yes as narrow V4 companion. | Could be mistaken as broad callback support if read casually. | Keep `not_claimed`; add one sentence that arbitrary Python callbacks are not supported. |
| `examples/tutorial_programs/fixed_radius_torch_device_arrays.py` | Yes as device-array companion. | It is useful but not beginner-friendly. | Add a concise mapping from kernel fields to device-array columns. |
| `examples/tutorial_programs/point_group_nearest_witness_torch_device_arrays.py` | Yes as device-array companion. | Needs clearer relation to nearest-witness tutorial output fields. | Add a field mapping table in payload. |
| `examples/tutorial_programs/ray_triangle_any_hit_flags_torch_device_arrays.py` | Yes as device-array companion. | Needs clear link from hit rows to flags. | Add field mapping from `ray_id, triangle_id, hit` to output flag. |
| `examples/tutorial_programs/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py` | Yes as companion for fused hit plus continuation. | It may look like a magic weighted-sum API. | Add explicit "unfused logical steps" before the prepared call. |
| `examples/tutorial_programs/primitive_grouped_i64_reduction_torch_device_arrays.py` | Yes as companion. | Needs clearer grouped-reduction precondition: offsets/groups must be valid. | Add group-offset invariant in output. |
| `examples/tutorial_programs/closest_hit_grouped_argmin_torch_device_arrays.py` | Yes as companion. | Needs clearer `argmin` tie and invalid group behavior. | Add tie/empty group boundary in payload. |
| `examples/tutorial_programs/aabb_index_all_ops_count.py` | Yes as companion. | "all ops count" may be opaque. | Add a short explanation of which AABB predicates are counted. |

## Cross-File Gaps

| Gap | Why It Matters | Fix |
| --- | --- | --- |
| Thin lessons 15-24 | A user can pass early lessons but not have enough scaffolding for app-lowering concepts. | Expand 15-24 to match the 05-14 template. |
| Some "Next" pointers are prose, not links | The path feels less polished and easier to lose. | Normalize every markdown lesson to one linked `Next:` line. |
| Device-array companions need field maps | Users see `prepare_*_v4(...)` and may not know how it corresponds to kernel rows. | Add "kernel fields -> device-array columns -> output fields" table to each companion. |
| Benchmark bridge lacks prerequisite map | Users need to know which small lessons compose into each benchmark app. | Add a 10-app prerequisite table in lesson 24 and/or `benchmark_app_recipes.py`. |
| Runtime API name `v4_frontdoor_quickstart.py` still sounds first | It can undermine the kernel-first ordering. | Consider renaming to `v4_frontdoor_after_kernel.py` in a future compatibility-safe cleanup. |

## Immediate Priority Order

1. Expand `24_benchmark_app_bridge.md` with a 10-app prerequisite table.
2. Expand thin lessons 15-20 with concrete input rows and expected output.
3. Add device-array field maps to companion scripts.
4. Normalize all `Next:` links.
5. Add one optional `--explain` mode to the most important beginner scripts:
   `hello_world.py`, `sorting_rows.py`, `fixed_radius_neighbors.py`.

## Final Self-Reflection

Is the tutorial path reasonable now?

Yes, as a release candidate path. It is no longer fundamentally misleading in
the way the earlier V4-only API tutorials were. It teaches kernel and relation
thinking first.

Is it best-state?

No. It is structurally correct but uneven. The beginning is strong, the middle
is acceptable, and the later app-lowering bridge is too compressed.

What must not happen next?

Do not replace the thin lessons with more `plan_operator_request_v4(...)`
examples. That would recreate the original problem. The right improvement is
more visible rows, more small inputs, clearer continuations, and better
prerequisite mapping from tutorial concepts to benchmark apps.
