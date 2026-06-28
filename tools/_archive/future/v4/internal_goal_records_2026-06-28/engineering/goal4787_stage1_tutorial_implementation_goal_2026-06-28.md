# Goal4787: Stage 1 Tutorial Implementation Goal

Date: 2026-06-28

Status: proposed. Do not begin implementation until this file receives external
review approval.

## Objective

Turn the accepted Goal4786 backlog into an implementation-ready tutorial plan.
The plan must list every intended output file, explain the purpose of each
file, and define the future goal sequence that will implement the Stage 1
tutorial ladder.

This is not a tutorial-writing goal. It is the control document for the tutorial
writing work that follows.

## Product Rule

RTDL tutorials must teach the language and programming model. They must not
teach each benchmark app as an app-specific recipe first.

The learner path is:

1. Learn small RTDL concepts.
2. Combine those concepts.
3. Use the 10 benchmark apps as Stage 2 exams.

Every tutorial must show the lowering:

`user problem -> RTDL relation rows -> operator/traversal -> continuation -> output`

If a file only calls a one-shot helper and does not explain the lowering, it is
not an acceptable tutorial.

## Inputs Already Accepted

| Source | Purpose |
| --- | --- |
| `docs/engineering/goal4786_stage1_tutorial_backlog_for_benchmark_apps_2026-06-28.md` | Accepted topic backlog and benchmark-app coverage matrix. |
| `docs/reviews/antigravity_goal4786_stage1_tutorial_backlog_review_2026-06-28.md` | External approval that the backlog is valid as a Stage 1 plan. |
| `docs/engineering/goal4784_restore_original_hello_world_kernel_2026-06-28.md` | Completed first tutorial topic: original RTDL hello-world kernel. |
| `docs/engineering/goal4785_restore_goal97_sorting_tutorial_2026-06-28.md` | Completed second tutorial topic: Goal97 ray-hit sorting. |

## Goal-Level Decision Check

1. Am I being stupid by turning a teaching problem into a paperwork problem?
   - No, if this file only freezes the implementation contract and then stops.
     Yes, if I keep producing process files instead of writing tutorials after
     approval.
2. What would make this goal stupid?
   - Failing to list exact output files, failing to inherit old working
     examples, or letting a reviewer approve vague intent instead of a concrete
     file plan.
3. Is there a better path?
   - Yes: write a strict file-by-file implementation target, get one external
     review, then implement the tutorials in bounded consecutive goals.
4. What is the next real action after approval?
   - Start Goal4788 with the first unfinished language topic, inspect the old
     materials, rewrite the current tutorial/program if needed, run it on Linux,
     and request review before closure.

## Public Tutorial Document Outputs

The public tutorial path should become a clean sequence under
`tutorials/current/`. Existing files may be rewritten in place when the filename
already matches the concept. Older mismatched pages should be moved to history
or replaced by the new sequence so the user sees only one current path.

| Output file | Purpose | Status |
| --- | --- | --- |
| `tutorials/current/README.md` | Public tutorial index. It must list the final lesson order and link only to current V4 tutorial pages. | Update required. |
| `tutorials/current/01_first_run.md` | Teach what RTDL is: traversal rows, RT-shaped relations, continuations, explicit partners. | Existing file; audit and polish only. |
| `tutorials/current/02_hello_world.md` | First RTDL kernel: input geometry, traverse, refine, emit rows, then ordinary Python output. | Completed by Goal4784; keep and final-audit. |
| `tutorials/current/03_sorting_rows.md` | Goal97 sorting lesson: values -> segment geometry -> intersection rows -> hit counts -> stable sorted order. | Completed by Goal4785; keep and final-audit. |
| `tutorials/current/04_relations_and_operators.md` | Teach relation rows, operator surfaces, query ids, candidate ids, payloads, and output rows. | Rewrite required. |
| `tutorials/current/05_fixed_radius_neighbors.md` | Teach radius-neighbor relation rows and threshold/count outputs. | New or rename from stale page. |
| `tutorials/current/06_nearest_witness.md` | Teach nearest/argmin as candidate distance rows plus continuation. | New. |
| `tutorials/current/07_aabb_predicates.md` | Teach point/range/box predicates and AABB spatial-index rows. | New. |
| `tutorials/current/08_point_in_polygon.md` | Teach polygon containment as RTDL rows and boundary policy. | New. |
| `tutorials/current/09_line_segment_intersection_spatial_join.md` | Teach broadphase pair rows plus exact line-segment intersection refinement. | New. |
| `tutorials/current/10_ray_triangle_hits.md` | Teach ray streams, triangle scenes, any-hit rows, closest-hit rows, and hit flags. | New. |
| `tutorials/current/11_grouped_continuations.md` | Teach group-by count/sum/min/max/weighted continuations over emitted rows. | New. |
| `tutorials/current/12_component_union.md` | Teach neighbor rows -> graph edges -> component labels. | New. |
| `tutorials/current/13_bounded_witness_collection.md` | Teach bounded per-query witnesses and overflow boundaries. | New. |
| `tutorials/current/14_aggregate_frontier_weighted_vector.md` | Teach aggregate frontier rows and grouped weighted vector continuation. | New. |
| `tutorials/current/15_contact_manifold_lowering.md` | Teach contact broadphase candidates, closest witness rows, and bounded contact output without teaching a full physics engine. | New. |
| `tutorials/current/16_graph_triangle_counting_lowering.md` | Teach graph motif lowering into RTDL hit/count rows. | New. |
| `tutorials/current/17_robot_collision_lowering.md` | Teach collision candidates and any-hit flags without teaching full robotics. | New. |
| `tutorials/current/18_raydb_table_to_ray.md` | Teach table rows -> ray payloads -> hit rows -> grouped database-style outputs. | New. |
| `tutorials/current/19_hausdorff_composition.md` | Teach Hausdorff as nearest-witness rows plus directed/symmetric reductions. | New. |
| `tutorials/current/20_partner_choice_device_arrays.md` | Teach explicit Torch/CuPy/Numba/RTDL-native partner choice and device-array bridge boundaries. | New or rewrite from `08_choose_a_partner.md`. |
| `tutorials/current/21_measurement_phases.md` | Teach setup, prepare, hot traversal, continuation, validation, and materialization. | New or rewrite from `06_measure_a_program.md`. |
| `tutorials/current/22_callback_planning_boundary.md` | Teach recognized operators vs arbitrary action-shaped callbacks and what V4.0 defers. | New. |
| `tutorials/current/23_benchmark_app_bridge.md` | Map the Stage 1 concepts to the 10 benchmark apps. This is the Stage 2 doorway, not an app tutorial. | Rewrite from `07_benchmark_apps.md`. |

The current files `05_prepare_run_continue.md`, `06_measure_a_program.md`,
`07_benchmark_apps.md`, `08_choose_a_partner.md`, and
`09_benchmark_harness_protocol.md` must either be rewritten into the new lesson
names above or moved into the history archive during implementation. They
should not remain as competing current-path pages.

## Public Tutorial Program Outputs

Every program below must either be audited as already good or rewritten so it
teaches the matching concept. Each program must run on Linux with
`PYTHONPATH=src:.`.

| Output file | Purpose | Related tutorial page |
| --- | --- | --- |
| `examples/tutorial_programs/README.md` | Public index of tutorial programs, commands, and concept order. | All pages. |
| `examples/tutorial_programs/hello_world.py` | First RTDL kernel. | `02_hello_world.md` |
| `examples/tutorial_programs/sorting_rows.py` | Goal97 ray-hit sorting and rank from hit rows. | `03_sorting_rows.md` |
| `examples/tutorial_programs/operator_primitives.py` | Relation rows and generic operator surfaces. | `04_relations_and_operators.md` |
| `examples/tutorial_programs/v4_frontdoor_quickstart.py` | Quick orientation to the V4 public surface, only if it does not hide the concept. | `04_relations_and_operators.md` |
| `examples/tutorial_programs/fixed_radius_neighbors.py` | Radius-neighbor relation rows. | `05_fixed_radius_neighbors.md` |
| `examples/tutorial_programs/nearest_neighbor.py` | Nearest witness rows. | `06_nearest_witness.md` |
| `examples/tutorial_programs/ranked_summary_neighbors.py` | Ranked/top-k continuation over candidate rows. | `06_nearest_witness.md` |
| `examples/tutorial_programs/aabb_spatial_index_predicates.py` | AABB point/range/intersection predicate rows. | `07_aabb_predicates.md` |
| `examples/tutorial_programs/aabb_index_all_ops_count.py` | Advanced AABB prepared surface/count bridge. | `07_aabb_predicates.md` |
| `examples/tutorial_programs/point_in_polygon.py` | Point-in-polygon row shape and boundary policy. | `08_point_in_polygon.md` |
| `examples/tutorial_programs/spatial_join_lsi.py` | Broadphase pair rows and line-segment-intersection refinement. | `09_line_segment_intersection_spatial_join.md` |
| `examples/tutorial_programs/rayjoin_topology_intro.py` | Topology/boundary policy for spatial joins. | `09_line_segment_intersection_spatial_join.md` |
| `examples/tutorial_programs/ray_triangle_hits.py` | Ray/triangle hit rows and hit flags. | `10_ray_triangle_hits.md` |
| `examples/tutorial_programs/continuation_grouped_sum.py` | Grouped reductions over emitted rows. | `11_grouped_continuations.md` |
| `examples/tutorial_programs/component_union_from_radius.py` | Component union continuation from neighbor rows. | `12_component_union.md` |
| `examples/tutorial_programs/bounded_witness_collection.py` | Bounded witness collection and overflow. | `13_bounded_witness_collection.md` |
| `examples/tutorial_programs/aggregate_frontier_rows.py` | Aggregate frontier rows and weighted vector continuation. | `14_aggregate_frontier_weighted_vector.md` |
| `examples/tutorial_programs/contact_manifold_lowering.py` | Contact manifold lowering from broadphase candidates to closest/bounded witness rows. | `15_contact_manifold_lowering.md` |
| `examples/tutorial_programs/triangle_counting_graph_lowering.py` | Graph-to-RT lowering for triangle counting. | `16_graph_triangle_counting_lowering.md` |
| `examples/tutorial_programs/robot_collision_lowering.py` | Collision candidate rows and hit-flag summary. | `17_robot_collision_lowering.md` |
| `examples/tutorial_programs/raydb_table_to_ray.py` | Table rows as ray payloads and grouped query outputs. | `18_raydb_table_to_ray.md` |
| `examples/tutorial_programs/hausdorff_distance_recipe.py` | Hausdorff composition from nearest witness rows. | `19_hausdorff_composition.md` |
| `examples/tutorial_programs/partner_choices.py` | Explicit partner selection and boundaries. | `20_partner_choice_device_arrays.md` |
| `examples/tutorial_programs/fixed_radius_torch_device_arrays.py` | Device-array bridge for radius-neighbor rows. | `20_partner_choice_device_arrays.md` |
| `examples/tutorial_programs/point_group_nearest_witness_torch_device_arrays.py` | Device-array bridge for nearest witness rows. | `20_partner_choice_device_arrays.md` |
| `examples/tutorial_programs/ray_triangle_any_hit_flags_torch_device_arrays.py` | Device-array bridge for any-hit flags. | `20_partner_choice_device_arrays.md` |
| `examples/tutorial_programs/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py` | Device-array bridge for ray/triangle weighted-sum continuation. | `20_partner_choice_device_arrays.md` |
| `examples/tutorial_programs/primitive_grouped_i64_reduction_torch_device_arrays.py` | Device-array bridge for grouped integer reduction. | `20_partner_choice_device_arrays.md` |
| `examples/tutorial_programs/closest_hit_grouped_argmin_torch_device_arrays.py` | Device-array bridge for closest-hit grouped argmin. | `20_partner_choice_device_arrays.md` |
| `examples/tutorial_programs/measure_phases.py` | Phase measurement and benchmark hygiene. | `21_measurement_phases.md` |
| `examples/tutorial_programs/operator_callback_planning.py` | Recognized operator vs arbitrary callback planning. | `22_callback_planning_boundary.md` |
| `examples/tutorial_programs/custom_predicate_early_exit_planning.py` | Custom predicate and early-exit planning boundary. | `22_callback_planning_boundary.md` |
| `examples/tutorial_programs/benchmark_app_recipes.py` | Stage 2 bridge from tutorial concepts to the 10 benchmark apps. | `23_benchmark_app_bridge.md` |

## Audit And Validation Outputs

These are engineering records, not first-time user documents.

| Output file | Purpose |
| --- | --- |
| `docs/engineering/goal4788_stage1_tutorial_file_audit_2026-06-28.md` | Per-file audit row for each tutorial page and program: should exist, content verdict, old material inherited, action taken. |
| `docs/engineering/goal4788_stage1_tutorial_linux_validation_2026-06-28.md` | Linux command log summary for all tutorial programs after the first implementation batch. |
| `docs/engineering/goal4788_stage1_tutorial_link_validation_2026-06-28.md` | Link and index validation for `tutorials/current/README.md`, tutorial pages, and `examples/tutorial_programs/README.md`. |
| `docs/reviews/call_for_review_goal4788_stage1_tutorial_batch_2026-06-28.md` | External review request for the first implementation batch after approval. |
| `docs/reviews/antigravity_goal4788_stage1_tutorial_batch_review_2026-06-28.md` | Antigravity review result for the first implementation batch. |

Later batches may produce equivalent `goal4789`, `goal4790`, etc. audit and
review files if the work is split across multiple implementation goals.

## Future Implementation Goal Sequence

These future goals are proposed only after Goal4787 receives approval.

| Future goal | Scope | Required outputs |
| --- | --- | --- |
| Goal4788 | Foundation cleanup: relation rows, fixed-radius, nearest witness. | Pages 04-06; relevant programs audited/rewritten; README links updated for these lessons; Linux validation; Antigravity review. |
| Goal4789 | Spatial primitives: AABB, point-in-polygon, line-segment intersection/spatial join. | Pages 07-09; relevant programs audited/rewritten; Linux validation; review. |
| Goal4790 | Ray and continuation core: ray/triangle hits, grouped continuations, component union, bounded witnesses. | Pages 10-13; relevant programs audited/rewritten; Linux validation; review. |
| Goal4791 | App-lowering concepts: aggregate frontier, contact manifold, graph triangle counting, robot collision, RayDB, Hausdorff. | Pages 14-19; relevant programs audited/rewritten; Linux validation; review. |
| Goal4792 | Partner, measurement, callback boundaries, benchmark bridge. | Pages 20-23; device-array bridge programs audited; benchmark bridge rewritten; Linux validation; review. |
| Goal4793 | Full tutorial surface audit. | Every user-visible tutorial and tutorial program has an audit row; links pass; stale pages moved to history; review. |

This sequence is intentionally grouped by concept family. It is not one
goal per file because that would create process churn; it is also not one giant
goal because that would hide mistakes until too late.

## External Review Questions For Goal4787

The reviewer must answer:

1. Are the output files explicit enough to make implementation auditable?
2. Are hello world and sorting preserved instead of replaced?
3. Does the plan avoid app-specific teaching before language concepts?
4. Does the plan force old-material inspection before rewriting?
5. Are the tutorial page filenames coherent and user-facing?
6. Are any required benchmark-app prerequisites missing?
7. Are any planned files unnecessary or harmful?
8. Is the proposed Goal4788-Goal4793 batching appropriate, or should it be
   split differently?
9. Does the plan include sufficient Linux validation and external review gates?
10. May implementation begin after this plan is approved?

## Non-Authorization

Approval of Goal4787 does not mean the tutorial surface is complete. It only
authorizes starting Goal4788 under this file contract.
