# RTDL V4 Tutorial Programs

These scripts are small learning programs. They run from the repository root
with `PYTHONPATH=src:.`.

Start with the concept programs. They show the data flow by hand: candidate
checks, relation rows, and continuation rows. After that, open the advanced
surface programs that use V4 prepare/run APIs and partner device arrays.

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\hello_world.py
py -3 examples\tutorial_programs\v4_frontdoor_quickstart.py
py -3 examples\tutorial_programs\sorting_rows.py
py -3 examples\tutorial_programs\operator_primitives.py
py -3 examples\tutorial_programs\partner_choices.py
py -3 examples\tutorial_programs\fixed_radius_neighbors.py
py -3 examples\tutorial_programs\nearest_neighbor.py
py -3 examples\tutorial_programs\ray_triangle_hits.py
py -3 examples\tutorial_programs\continuation_grouped_sum.py
py -3 examples\tutorial_programs\measure_phases.py
py -3 examples\tutorial_programs\point_in_polygon.py
py -3 examples\tutorial_programs\spatial_join_lsi.py
py -3 examples\tutorial_programs\aggregate_frontier_rows.py
py -3 examples\tutorial_programs\component_union_from_radius.py
py -3 examples\tutorial_programs\ranked_summary_neighbors.py
py -3 examples\tutorial_programs\bounded_witness_collection.py
py -3 examples\tutorial_programs\contact_manifold_lowering.py
py -3 examples\tutorial_programs\triangle_counting_graph_lowering.py
py -3 examples\tutorial_programs\robot_collision_lowering.py
py -3 examples\tutorial_programs\hausdorff_distance_recipe.py
py -3 examples\tutorial_programs\raydb_table_to_ray.py
py -3 examples\tutorial_programs\rayjoin_topology_intro.py
py -3 examples\tutorial_programs\aabb_spatial_index_predicates.py
py -3 examples\tutorial_programs\benchmark_app_recipes.py
py -3 examples\tutorial_programs\operator_callback_planning.py --case complex-callback
py -3 examples\tutorial_programs\fixed_radius_torch_device_arrays.py --dry-run
py -3 examples\tutorial_programs\ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
py -3 examples\tutorial_programs\aabb_index_all_ops_count.py --dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/hello_world.py
PYTHONPATH=src:. python examples/tutorial_programs/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/tutorial_programs/sorting_rows.py
PYTHONPATH=src:. python examples/tutorial_programs/operator_primitives.py
PYTHONPATH=src:. python examples/tutorial_programs/partner_choices.py
PYTHONPATH=src:. python examples/tutorial_programs/fixed_radius_neighbors.py
PYTHONPATH=src:. python examples/tutorial_programs/nearest_neighbor.py
PYTHONPATH=src:. python examples/tutorial_programs/ray_triangle_hits.py
PYTHONPATH=src:. python examples/tutorial_programs/continuation_grouped_sum.py
PYTHONPATH=src:. python examples/tutorial_programs/measure_phases.py
PYTHONPATH=src:. python examples/tutorial_programs/point_in_polygon.py
PYTHONPATH=src:. python examples/tutorial_programs/spatial_join_lsi.py
PYTHONPATH=src:. python examples/tutorial_programs/aggregate_frontier_rows.py
PYTHONPATH=src:. python examples/tutorial_programs/component_union_from_radius.py
PYTHONPATH=src:. python examples/tutorial_programs/ranked_summary_neighbors.py
PYTHONPATH=src:. python examples/tutorial_programs/bounded_witness_collection.py
PYTHONPATH=src:. python examples/tutorial_programs/contact_manifold_lowering.py
PYTHONPATH=src:. python examples/tutorial_programs/triangle_counting_graph_lowering.py
PYTHONPATH=src:. python examples/tutorial_programs/robot_collision_lowering.py
PYTHONPATH=src:. python examples/tutorial_programs/hausdorff_distance_recipe.py
PYTHONPATH=src:. python examples/tutorial_programs/raydb_table_to_ray.py
PYTHONPATH=src:. python examples/tutorial_programs/rayjoin_topology_intro.py
PYTHONPATH=src:. python examples/tutorial_programs/aabb_spatial_index_predicates.py
PYTHONPATH=src:. python examples/tutorial_programs/benchmark_app_recipes.py
PYTHONPATH=src:. python examples/tutorial_programs/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python examples/tutorial_programs/fixed_radius_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/tutorial_programs/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/tutorial_programs/aabb_index_all_ops_count.py --dry-run
```

## Suggested Order

| Program | What it teaches |
| --- | --- |
| `hello_world.py` | Import V4 and ask the planner for one RT-shaped operator. |
| `v4_frontdoor_quickstart.py` | See the current public surface and measured partners. |
| `sorting_rows.py` | Sort relation rows, then continue with nearest or grouped summaries. |
| `operator_primitives.py` | See how operator surfaces map to generic primitives and continuations. |
| `partner_choices.py` | Compare Torch, CuPy, Numba, and RTDL native planning outcomes. |
| `fixed_radius_neighbors.py` | Build a radius-neighbor relation from visible candidate checks. |
| `nearest_neighbor.py` | Build a nearest-witness relation from candidate distances and argmin continuation. |
| `ray_triangle_hits.py` | Build ray/triangle any-hit rows from visible hit tests. |
| `continuation_grouped_sum.py` | Reduce relation rows into grouped app output. |
| `measure_phases.py` | Measure setup, hot relation work, continuation, and validation separately. |
| `point_in_polygon.py` | Use polygon bounds, candidate discovery, and exact containment logic. |
| `spatial_join_lsi.py` | Build broadphase join rows, then refine them with segment intersections. |
| `aggregate_frontier_rows.py` | Build Barnes-Hut-style aggregate frontier rows and grouped vector force output. |
| `component_union_from_radius.py` | Continue radius-neighbor rows into component labels for RTDBSCAN-style clustering. |
| `ranked_summary_neighbors.py` | Turn candidate rows into bounded ranked summaries for RTNN-style apps. |
| `bounded_witness_collection.py` | Keep a bounded number of witnesses per group and report overflow. |
| `contact_manifold_lowering.py` | Connect broadphase shape pairs to bounded contact witnesses. |
| `triangle_counting_graph_lowering.py` | Lower graph two-hop rows into triangle witness counts. |
| `robot_collision_lowering.py` | Lower poses and links into grouped collision queries. |
| `hausdorff_distance_recipe.py` | Compose nearest-witness rows into directed and undirected Hausdorff distance. |
| `raydb_table_to_ray.py` | Lower table predicates into ray/primitive payload rows and grouped aggregates. |
| `rayjoin_topology_intro.py` | Add topology and boundary policy to spatial join candidate rows. |
| `aabb_spatial_index_predicates.py` | Build point/range AABB predicate rows before using the prepared runner. |
| `benchmark_app_recipes.py` | Map the tutorial concepts to the 10 benchmark apps. |

The remaining device-array scripts are advanced surface examples. Use them
after you understand the concept programs.
