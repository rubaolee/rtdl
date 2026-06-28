# Goal4796-Goal4800 Kernel-First Tutorial Remediation Plan

Date: 2026-06-28

Status: completed locally; external review requested in Goal4800 packet

## Why This Exists

The current tutorial surface improved over the earlier V4 public cleanup, but a
new audit found that not every file under `examples/tutorial_programs/` teaches
RTDL kernel programming. Several files are useful V4 operator-surface examples,
but they teach `plan_operator_request_v4(...)` or `prepare_*_v4(...)` directly
without first teaching the RTDL relation/kernel shape.

That violates the release tutorial standard:

```text
Tutorial programs must teach the RTDL language/relation model first.
V4 operator/runtime APIs may appear only after the user sees what relation or
continuation they execute.
```

## Goal4796 - Freeze The Standard And File Classification

Purpose:

- record the kernel-first tutorial standard;
- classify every tutorial-program file;
- define the acceptance gate for Goals4797-4800.

Outputs:

- this plan;
- an audit table in Goal4800 showing every user-visible tutorial/example file
  and its final classification.

Exit gate:

- every file under `examples/tutorial_programs/` is either:
  - a `core_tutorial_program` with kernel/relation-first teaching; or
  - an `operator_companion` that points to its kernel-first concept tutorial and
    is not presented as the first learning path.

## Goal4797 - Repair Semi-Qualified Relation Tutorials

Purpose:

- strengthen the relation-only app-lowering programs so they explain the
  kernel/relation method before V4 routing.

Target files:

- `aggregate_frontier_rows.py`
- `contact_manifold_lowering.py`
- `hausdorff_distance_recipe.py`
- `measure_phases.py`
- `partner_choices.py`
- `ranked_summary_neighbors.py`
- `raydb_table_to_ray.py`
- `rayjoin_topology_intro.py`
- `robot_collision_lowering.py`
- `triangle_counting_graph_lowering.py`

Required per file:

- a clear `tutorial_classification`;
- a `kernel_first` or `relation_first` explanation;
- a `manual_data_flow`;
- no app-only "call this V4 API and it solves the app" framing.

Exit gate:

- each target file has a relation/kernel-first payload visible in normal output.

## Goal4798 - Reclassify Pure V4 Surface Files As Operator Companions

Purpose:

- stop presenting pure device-array/frontdoor files as standalone language
  tutorials;
- keep them available as useful reference companions after the concept lesson.

Target files:

- `aabb_index_all_ops_count.py`
- `benchmark_app_recipes.py`
- `closest_hit_grouped_argmin_torch_device_arrays.py`
- `custom_predicate_early_exit_planning.py`
- `fixed_radius_torch_device_arrays.py`
- `operator_callback_planning.py`
- `operator_primitives.py`
- `point_group_nearest_witness_torch_device_arrays.py`
- `primitive_grouped_i64_reduction_torch_device_arrays.py`
- `ray_triangle_any_hit_flags_torch_device_arrays.py`
- `ray_triangle_any_hit_weighted_sum_torch_device_arrays.py`
- `v4_frontdoor_quickstart.py`

Required per file:

- an explicit companion classification;
- a pointer to the kernel-first concept tutorial when one exists;
- wording that the file is an execution-surface companion, not the source of the
  programming idea.

Exit gate:

- no pure V4 surface file is described as the first place to learn RTDL.

## Goal4799 - Update User-Facing Tutorial Navigation

Purpose:

- make the public tutorial/readme path match the repaired classification.

Target files:

- `tutorials/current/README.md`
- `examples/tutorial_programs/README.md`
- `docs/public_documentation_map.md`
- any tutorial page that links directly to a pure V4 companion before the
  kernel-first concept page.

Exit gate:

- users see the kernel-first learning ladder first;
- operator companion examples appear only after concept tutorials.

## Goal4800 - Validation And External Review Packet

Purpose:

- run the tutorial examples and public-doc tests;
- produce an audit/review packet for Antigravity or Claude debt.

Required validation:

- public docs tests pass;
- representative tutorial programs run;
- audit confirms every tutorial-program file is classified and no pure V4 file
  is masquerading as the first lesson.

Outputs:

- `tools/_archive/future/v4/tutorial_audits/goal4800_kernel_first_tutorial_completion_audit_2026-06-28.md`
- `tools/_archive/future/v4/reviews/call_for_review_goal4800_kernel_first_tutorial_completion_2026-06-28.md`

Non-goals:

- no V4 performance claim changes;
- no benchmark result changes;
- no POD work;
- no new app-specific kernels.
