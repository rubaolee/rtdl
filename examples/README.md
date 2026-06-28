# RTDL Examples

This directory has three current entrypoints. They are meant to coexist:
tutorial programs teach the language one concept at a time, benchmark apps show
the promoted 10-app suite, and paper-reproduction apps track paper-oriented
work separately.

| Path | What to use it for |
| --- | --- |
| `tutorial_programs/` | Small runnable programs for learning the current RTDL/V4 language path. Some teach language-layer lowering; some also expose V4 runtime surfaces. Start here. |
| `benchmark_apps/` | The 10 benchmark apps used to evaluate RTDL. |
| `paper_reproduction/` | Paper-oriented app entrypoints and notes. |

## Start Here

The first programs teach the RTDL language layer. A tutorial program has a V4
runtime/operator surface only when it explicitly names one.

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\hello_world.py
py -3 examples\tutorial_programs\sorting_rows.py
py -3 examples\tutorial_programs\fixed_radius_neighbors.py --mode both
py -3 examples\tutorial_programs\nearest_neighbor.py --mode both
py -3 examples\tutorial_programs\aabb_spatial_index_predicates.py --mode both
py -3 examples\tutorial_programs\partner_choices.py --mode both
py -3 examples\tutorial_programs\point_in_polygon.py --mode both
py -3 examples\tutorial_programs\spatial_join_lsi.py --mode both
py -3 examples\tutorial_programs\ray_triangle_hits.py --mode both
py -3 examples\tutorial_programs\continuation_grouped_sum.py --mode both
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
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/hello_world.py
PYTHONPATH=src:. python examples/tutorial_programs/sorting_rows.py
PYTHONPATH=src:. python examples/tutorial_programs/fixed_radius_neighbors.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/nearest_neighbor.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/aabb_spatial_index_predicates.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/partner_choices.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/point_in_polygon.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/spatial_join_lsi.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/ray_triangle_hits.py --mode both
PYTHONPATH=src:. python examples/tutorial_programs/continuation_grouped_sum.py --mode both
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
```

## Learn the Benchmark Apps

The bridge program is
[tutorial_programs/benchmark_app_recipes.py](tutorial_programs/benchmark_app_recipes.py).
It explains how each app is built from V4 relations, operators, partners, and
continuations before you open the full app source.

The full benchmark app sources are in `benchmark_apps/`.

## Paper Reproduction

Paper-oriented app entrypoints live in `paper_reproduction/`. They are separate
from the 10-app benchmark suite so users can tell ordinary benchmark apps from
paper-specific reproduction work.
