# Public Documentation Map

The current V4 documentation path is deliberately short.

## First-Time User Path

1. [Project README](../README.md)
2. [Docs index](README.md)
3. [V4 release notes](v4_release_notes.md)
4. [Current V4 status](current_v4_status.md)
5. [Operator catalog](learn/operator_catalog.md)
6. [Partner choice](learn/partner_choice.md)
7. [Tutorials](../tutorials/current/README.md)
8. [Runnable examples](../examples/README.md)
9. [Benchmark apps](../examples/benchmark_apps/README.md)
10. [App-level benchmark summary](app_level_benchmark_summary.md)

## Quick Check Path

The quick-check path includes both language-layer lessons and V4 runtime-surface
checks. A tutorial program has a V4 operator surface only when its output or
lesson names that surface explicitly.

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\hello_world.py
py -3 examples\tutorial_programs\sorting_rows.py
py -3 examples\tutorial_programs\operator_primitives.py
py -3 examples\tutorial_programs\fixed_radius_neighbors.py --mode both
py -3 examples\tutorial_programs\nearest_neighbor.py --mode both
py -3 examples\tutorial_programs\aabb_spatial_index_predicates.py --mode both
py -3 examples\tutorial_programs\partner_choices.py --mode both
py -3 examples\tutorial_programs\measure_phases.py --mode both
py -3 examples\tutorial_programs\ray_triangle_hits.py --mode both
py -3 examples\tutorial_programs\continuation_grouped_sum.py --mode both
py -3 examples\tutorial_programs\point_in_polygon.py --mode both
py -3 examples\tutorial_programs\spatial_join_lsi.py --mode both
py -3 examples\tutorial_programs\component_union_from_radius.py --mode both
py -3 examples\tutorial_programs\bounded_witness_collection.py --mode both
py -3 examples\tutorial_programs\aggregate_frontier_rows.py --mode both
py -3 examples\tutorial_programs\ranked_summary_neighbors.py --mode both
py -3 examples\tutorial_programs\contact_manifold_lowering.py --mode both
py -3 examples\tutorial_programs\triangle_counting_graph_lowering.py --mode both
py -3 examples\tutorial_programs\robot_collision_lowering.py --mode both
py -3 examples\tutorial_programs\raydb_table_to_ray.py --mode both
py -3 examples\tutorial_programs\hausdorff_distance_recipe.py --mode both
py -3 examples\tutorial_programs\rayjoin_topology_intro.py
py -3 examples\tutorial_programs\benchmark_app_recipes.py
py -3 examples\tutorial_programs\v4_frontdoor_quickstart.py
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/hello_world.py
PYTHONPATH=src:. python examples/tutorial_programs/sorting_rows.py
PYTHONPATH=src:. python examples/tutorial_programs/operator_primitives.py
PYTHONPATH=src:. python examples/tutorial_programs/fixed_radius_neighbors.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/nearest_neighbor.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/aabb_spatial_index_predicates.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/partner_choices.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/measure_phases.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/ray_triangle_hits.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/continuation_grouped_sum.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/point_in_polygon.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/spatial_join_lsi.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/component_union_from_radius.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/bounded_witness_collection.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/aggregate_frontier_rows.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/ranked_summary_neighbors.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/contact_manifold_lowering.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/triangle_counting_graph_lowering.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/robot_collision_lowering.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/raydb_table_to_ray.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/hausdorff_distance_recipe.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/rayjoin_topology_intro.py
PYTHONPATH=src:. python examples/tutorial_programs/benchmark_app_recipes.py
PYTHONPATH=src:. python examples/tutorial_programs/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python scripts/v4_catalog_regression_gate.py --mode dry-run
```
