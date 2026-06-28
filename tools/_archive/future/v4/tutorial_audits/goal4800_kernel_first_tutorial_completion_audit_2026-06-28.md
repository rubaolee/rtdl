# Goal4800 Kernel-First Tutorial Completion Audit

Date: 2026-06-28

Status: local completion complete; external review requested.

## Goal Chain

- Goal4796: recorded the kernel-first tutorial standard and acceptance criteria.
- Goal4797: strengthened semi-qualified relation tutorials with visible
  relation/kernel programming metadata.
- Goal4798: reclassified V4-only runtime/front-door examples as operator
  companions, not core first lessons.
- Goal4799: updated public tutorial/readme ordering so users see kernel-first
  lessons before V4 runtime surfaces.
- Goal4800: added classification guard tests, ran all tutorial programs, and
  prepared the external review request.

## What Changed

The tutorial-program surface is now split into four explicit categories:

1. Core kernel-first programs that contain real `@rt.kernel` examples.
2. Core relation-first programs that teach manual data flow and kernel
   programming method even when they are not literal `@rt.kernel` scripts.
3. Operator companions that are useful after the concept lesson, and now say
   they are not first lessons.
4. One vocabulary map that explains relation rows, operators, and continuation
   classes without claiming to be an execution program.

This keeps the V4 operator API as the execution/runtime layer rather than the
first teaching model.

## File-By-File Audit

| File | Final classification | Audit result |
| --- | --- | --- |
| `hello_world.py` | core kernel-first | Contains `@rt.kernel`; remains the first runnable lesson. |
| `sorting_rows.py` | core kernel-first | Contains `@rt.kernel`; teaches RTDL lowering for sorting rows; no false V4 sorting claim. |
| `fixed_radius_neighbors.py` | core kernel-first | Contains `@rt.kernel`; teaches fixed-radius rows before V4 mode. |
| `nearest_neighbor.py` | core kernel-first | Contains `@rt.kernel`; teaches nearest-witness rows before V4 mode. |
| `aabb_spatial_index_predicates.py` | core kernel-first | Contains `@rt.kernel`; teaches broadphase predicates before prepared AABB route. |
| `point_in_polygon.py` | core kernel-first | Contains `@rt.kernel`; teaches point/polygon containment rows. |
| `spatial_join_lsi.py` | core kernel-first | Contains `@rt.kernel`; teaches LSI-style spatial join rows. |
| `ray_triangle_hits.py` | core kernel-first | Contains `@rt.kernel`; teaches any-hit rows before V4 route. |
| `continuation_grouped_sum.py` | core kernel-first | Contains `@rt.kernel`; teaches relation rows plus grouped continuation. |
| `component_union_from_radius.py` | core kernel-first | Contains `@rt.kernel`; teaches radius rows into component union. |
| `bounded_witness_collection.py` | core kernel-first | Contains `@rt.kernel`; teaches witness collection and overflow validation. |
| `operator_primitives.py` | core concept map | Marked `core_concept_map_not_execution_program`; no longer masquerades as a kernel example. |
| `aggregate_frontier_rows.py` | core relation-first | Added `core_tutorial_program_relation_first` and `kernel_programming_method`. |
| `contact_manifold_lowering.py` | core relation-first | Added `core_tutorial_program_relation_first` and `kernel_programming_method`. |
| `hausdorff_distance_recipe.py` | core relation-first | Added `core_tutorial_program_relation_first` and `kernel_programming_method`. |
| `measure_phases.py` | core relation-first | Added `core_tutorial_program_relation_first` and `kernel_programming_method`. |
| `partner_choices.py` | core relation-first | Added `core_tutorial_program_relation_first`; partner choice now follows known relation shape. |
| `ranked_summary_neighbors.py` | core relation-first | Added `core_tutorial_program_relation_first` and `kernel_programming_method`. |
| `raydb_table_to_ray.py` | core relation-first | Added `core_tutorial_program_relation_first` and `kernel_programming_method`. |
| `rayjoin_topology_intro.py` | core relation-first | Added `core_tutorial_program_relation_first` and topology-oriented method metadata. |
| `robot_collision_lowering.py` | core relation-first | Added `core_tutorial_program_relation_first` and `kernel_programming_method`. |
| `triangle_counting_graph_lowering.py` | core relation-first | Added `core_tutorial_program_relation_first` and `kernel_programming_method`. |
| `v4_frontdoor_quickstart.py` | operator companion | Marked `operator_companion_after_kernel_first_lesson`, `not_first_lesson`, and `kernel_first_requirement`. |
| `benchmark_app_recipes.py` | operator companion | Marked as post-concept app recipe bridge, not a first lesson. |
| `operator_callback_planning.py` | operator companion | Marked as callback boundary companion after ray-hit and continuation lessons. |
| `custom_predicate_early_exit_planning.py` | operator companion | Marked as constrained predicate companion after ray-hit lesson. |
| `fixed_radius_torch_device_arrays.py` | operator companion | Points to `fixed_radius_neighbors.py` before device-array route. |
| `point_group_nearest_witness_torch_device_arrays.py` | operator companion | Points to nearest/ranked-summary concept lessons first. |
| `ray_triangle_any_hit_flags_torch_device_arrays.py` | operator companion | Points to `ray_triangle_hits.py` first. |
| `ray_triangle_any_hit_weighted_sum_torch_device_arrays.py` | operator companion | Points to ray-hit, grouped-sum, and RayDB concept lessons first. |
| `primitive_grouped_i64_reduction_torch_device_arrays.py` | operator companion | Points to triangle-counting and grouped-sum concept lessons first. |
| `closest_hit_grouped_argmin_torch_device_arrays.py` | operator companion | Points to bounded-witness and contact-manifold concept lessons first. |
| `aabb_index_all_ops_count.py` | operator companion | Points to `aabb_spatial_index_predicates.py` first. |

## Navigation Audit

Updated user-facing order in:

- `README.md`
- `examples/README.md`
- `examples/tutorial_programs/README.md`
- `tutorials/current/01_first_run.md`
- `tutorials/current/02_hello_world.md`
- `tutorials/current/04_relations_and_operators.md`
- `docs/public_documentation_map.md`
- `docs/current_v4_status.md`
- `docs/learn/source_tree_doctor.md`

The current order is now:

```text
hello_world -> sorting_rows -> relation/kernel tutorials -> partner/runtime
choices -> V4 frontdoor/device-array companions
```

## Validation

Commands run:

```powershell
py -3 -m unittest tests.v4_goal4800_kernel_first_tutorial_classification_test
```

Result:

```text
Ran 6 tests in 0.029s
OK
```

Full tutorial program smoke:

```text
tutorial_program_smoke_passed=33
```

Public/V4 regression group:

```powershell
py -3 -m unittest tests.v4_goal4800_kernel_first_tutorial_classification_test tests.v4_goal4640_public_docs_cleanup_test tests.v4_goal4643_publication_decision_test tests.v4_goal4774_release_packaging_audit_test tests.v4_rayjoin_section57_public_entry_test
```

Result:

```text
Ran 32 tests in 90.385s
OK
```

Note: this Windows Python environment prints `Could not find platform
independent libraries <prefix>` before many runs; the commands still exit 0.

## Remaining Boundary

This audit did not change any V4 performance claim, benchmark result, POD
result, partner support claim, or release tag. It only repaired tutorial
classification and learning order.
