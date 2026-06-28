# RTDL V4 Tutorial Programs

These scripts are small learning programs in the V4 release path. They run from
the repository root with `PYTHONPATH=src:.`.

Some programs are RTDL language-layer lessons. They teach kernel/relation
lowering and may have no V4 operator surface. Other programs also have a
`--mode v4` mapping to a current V4 runtime/operator surface. Do not infer a V4
runtime claim unless the program explicitly prints one.

Start with the kernel programs. They show how a problem becomes RTDL inputs,
traversal, refinement, emitted rows, and continuation rows. After that, inspect
the V4 mode for the same concept. V4 operator/runtime calls are execution
surface checks, not replacements for the RTDL language model.

## Core Kernel-First Path

These are the programs to read first. They teach the RTDL programming model:
geometry or table inputs become candidate rows, refinement turns candidates into
relation rows, and continuations turn relation rows into application output.

Minimum path:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/hello_world.py
PYTHONPATH=src:. python examples/tutorial_programs/sorting_rows.py
PYTHONPATH=src:. python examples/tutorial_programs/fixed_radius_neighbors.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/ray_triangle_hits.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/continuation_grouped_sum.py --mode both
```

After that, use the full path below.

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\hello_world.py
py -3 examples\tutorial_programs\sorting_rows.py
py -3 examples\tutorial_programs\operator_primitives.py
py -3 examples\tutorial_programs\fixed_radius_neighbors.py --mode both
py -3 examples\tutorial_programs\nearest_neighbor.py --mode both
py -3 examples\tutorial_programs\aabb_spatial_index_predicates.py --mode both
py -3 examples\tutorial_programs\point_in_polygon.py --mode both
py -3 examples\tutorial_programs\spatial_join_lsi.py --mode both
py -3 examples\tutorial_programs\rayjoin_topology_intro.py
py -3 examples\tutorial_programs\partner_choices.py --mode both
py -3 examples\tutorial_programs\ray_triangle_hits.py --mode both
py -3 examples\tutorial_programs\continuation_grouped_sum.py --mode both
py -3 examples\tutorial_programs\measure_phases.py --mode both
py -3 examples\tutorial_programs\component_union_from_radius.py --mode both
py -3 examples\tutorial_programs\bounded_witness_collection.py --mode both
py -3 examples\tutorial_programs\aggregate_frontier_rows.py --mode both
py -3 examples\tutorial_programs\ranked_summary_neighbors.py --mode both
py -3 examples\tutorial_programs\contact_manifold_lowering.py --mode both
py -3 examples\tutorial_programs\triangle_counting_graph_lowering.py --mode both
py -3 examples\tutorial_programs\robot_collision_lowering.py --mode both
py -3 examples\tutorial_programs\raydb_table_to_ray.py --mode both
py -3 examples\tutorial_programs\hausdorff_distance_recipe.py --mode both
py -3 examples\tutorial_programs\benchmark_app_recipes.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/hello_world.py
PYTHONPATH=src:. python examples/tutorial_programs/sorting_rows.py
PYTHONPATH=src:. python examples/tutorial_programs/operator_primitives.py
PYTHONPATH=src:. python examples/tutorial_programs/fixed_radius_neighbors.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/nearest_neighbor.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/aabb_spatial_index_predicates.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/point_in_polygon.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/spatial_join_lsi.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/rayjoin_topology_intro.py
PYTHONPATH=src:. python examples/tutorial_programs/partner_choices.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/ray_triangle_hits.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/continuation_grouped_sum.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/measure_phases.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/component_union_from_radius.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/bounded_witness_collection.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/aggregate_frontier_rows.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/ranked_summary_neighbors.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/contact_manifold_lowering.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/triangle_counting_graph_lowering.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/robot_collision_lowering.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/raydb_table_to_ray.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/hausdorff_distance_recipe.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/benchmark_app_recipes.py
```

## Suggested Order

| Program | What it teaches |
| --- | --- |
| `hello_world.py` | Write the first RTDL kernel: input geometry, traverse, refine, emit rows, then print `hello, world`. |
| `sorting_rows.py` | Convert nonnegative integers into segment-intersection hits, then use hit counts as rank. This is a language-layer lesson with no V4 sorting operator surface. |
| `operator_primitives.py` | Read the vocabulary map: relation rows, operator surfaces, and continuation classes. This is not a kernel execution example. |
| `fixed_radius_neighbors.py --mode both` | First run the RTDL kernel for radius-neighbor rows, then inspect the V4 execution surface. |
| `nearest_neighbor.py --mode both` | First run the RTDL kernel for nearest-witness rows, then inspect the V4 execution surface. |
| `aabb_spatial_index_predicates.py --mode both` | Learn broadphase relation rows, then inspect the prepared V4 AABB route. |
| `point_in_polygon.py --mode both` | First run the RTDL kernel for point/polygon containment rows, then inspect the V4 broadphase surface. |
| `spatial_join_lsi.py --mode both` | First run the RTDL kernel for segment-intersection rows, then inspect the V4 broadphase surface. |
| `rayjoin_topology_intro.py` | Add topology and boundary policy to spatial join candidate rows. |
| `partner_choices.py --mode both` | Compare Torch, CuPy, Numba, and RTDL native planning outcomes after the relation shape is known. |
| `ray_triangle_hits.py --mode both` | First run the RTDL kernel for ray/triangle any-hit rows, then inspect the V4 execution surface. |
| `continuation_grouped_sum.py --mode both` | First run the RTDL kernel that emits hit-count rows, then reduce them with grouped continuations and inspect V4 surfaces. |
| `measure_phases.py --mode both` | Measure setup, hot relation work, continuation, and validation separately. |
| `component_union_from_radius.py --mode both` | First run the RTDL fixed-radius kernel, then continue neighbor rows into component labels and inspect the V4 Numba surface. |
| `bounded_witness_collection.py --mode both` | First run a witness-row kernel, then keep bounded witnesses with overflow validation and inspect the V4 grouped-argmin surface. |
| `aggregate_frontier_rows.py --mode both` | Learn aggregate-frontier relation rows and weighted vector continuation, then inspect the V4 prepared frontier and CuPy continuation surfaces. |
| `ranked_summary_neighbors.py --mode both` | Turn candidate rows into bounded ranked summaries for RTNN-style apps. |
| `contact_manifold_lowering.py --mode both` | Connect broadphase shape pairs to bounded contact witnesses. |
| `triangle_counting_graph_lowering.py --mode both` | Lower graph two-hop rows into triangle witness counts. |
| `robot_collision_lowering.py --mode both` | Lower poses and links into grouped collision queries. |
| `raydb_table_to_ray.py --mode both` | Lower table predicates into ray/primitive payload rows and grouped aggregates. |
| `hausdorff_distance_recipe.py --mode both` | Compose nearest-witness rows into directed and undirected Hausdorff distance. |
| `benchmark_app_recipes.py` | Map the tutorial concepts to the 10 benchmark apps. |

## Operator Companion Path

Run these only after the core path. They show how the same relation and
continuation ideas enter the V4 runtime/front-door API, device-array routes,
partner choices, and callback boundary. They are not first lessons, and they are
not meant to hide application logic behind one magic call.

The file `v4_frontdoor_quickstart.py` keeps its historical name, but in this
tutorial path it is not the first quickstart. Treat it as an operator-surface
check after you have run the kernel-first lessons.

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\v4_frontdoor_quickstart.py
py -3 examples\tutorial_programs\operator_callback_planning.py --case complex-callback
py -3 examples\tutorial_programs\custom_predicate_early_exit_planning.py
py -3 examples\tutorial_programs\fixed_radius_torch_device_arrays.py --dry-run
py -3 examples\tutorial_programs\point_group_nearest_witness_torch_device_arrays.py --dry-run
py -3 examples\tutorial_programs\ray_triangle_any_hit_flags_torch_device_arrays.py --dry-run
py -3 examples\tutorial_programs\ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
py -3 examples\tutorial_programs\primitive_grouped_i64_reduction_torch_device_arrays.py --dry-run
py -3 examples\tutorial_programs\closest_hit_grouped_argmin_torch_device_arrays.py --dry-run
py -3 examples\tutorial_programs\aabb_index_all_ops_count.py --dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/tutorial_programs/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python examples/tutorial_programs/custom_predicate_early_exit_planning.py
PYTHONPATH=src:. python examples/tutorial_programs/fixed_radius_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/tutorial_programs/point_group_nearest_witness_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/tutorial_programs/ray_triangle_any_hit_flags_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/tutorial_programs/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/tutorial_programs/primitive_grouped_i64_reduction_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/tutorial_programs/closest_hit_grouped_argmin_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/tutorial_programs/aabb_index_all_ops_count.py --dry-run
```

## Advanced Surface Bridge

| Advanced program | Concept program to read first | What becomes device-array backed |
| --- | --- | --- |
| `v4_frontdoor_quickstart.py` | `hello_world.py`, `sorting_rows.py`, one relation tutorial | Generic operator request, partner choice, and planned surface. |
| `operator_callback_planning.py` | `ray_triangle_hits.py`, `continuation_grouped_sum.py` | Callback classification and rewrite guidance. |
| `custom_predicate_early_exit_planning.py` | `ray_triangle_hits.py` | Constrained pure boolean predicate early exit. |
| `fixed_radius_torch_device_arrays.py` | `fixed_radius_neighbors.py` | Radius-neighbor rows and threshold counts. |
| `point_group_nearest_witness_torch_device_arrays.py` | `nearest_neighbor.py`, `ranked_summary_neighbors.py` | Nearest witness rows and argmin output columns. |
| `ray_triangle_any_hit_flags_torch_device_arrays.py` | `ray_triangle_hits.py` | Ray/triangle hit rows and any-hit flags. |
| `ray_triangle_any_hit_weighted_sum_torch_device_arrays.py` | `ray_triangle_hits.py`, `continuation_grouped_sum.py` | Hit rows plus fused weighted-sum continuation. |
| `primitive_grouped_i64_reduction_torch_device_arrays.py` | `triangle_counting_graph_lowering.py`, `continuation_grouped_sum.py` | Primitive payload rows plus per-group count/sum output. |
| `closest_hit_grouped_argmin_torch_device_arrays.py` | `bounded_witness_collection.py`, `contact_manifold_lowering.py` | Candidate hit rows plus per-group closest witness. |
| `aabb_index_all_ops_count.py` | `aabb_spatial_index_predicates.py` | AABB predicate rows plus operation counts. |
