# RTDL V4 Tutorial Programs

These scripts are small learning programs. They run from the repository root
with `PYTHONPATH=src:.`. Start with the first four if you are new to RTDL;
then use the operator examples to connect the ideas to the benchmark apps.

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
py -3 examples\tutorial_programs\point_in_polygon.py
py -3 examples\tutorial_programs\spatial_join_lsi.py
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
PYTHONPATH=src:. python examples/tutorial_programs/point_in_polygon.py
PYTHONPATH=src:. python examples/tutorial_programs/spatial_join_lsi.py
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
| `fixed_radius_neighbors.py` | Build a radius-neighbor relation. |
| `nearest_neighbor.py` | Build a nearest-witness relation for NN-style work. |
| `ray_triangle_hits.py` | Build ray/triangle any-hit rows. |
| `continuation_grouped_sum.py` | Reduce relation rows into grouped app output. |
| `point_in_polygon.py` | Use candidate discovery plus exact containment logic. |
| `spatial_join_lsi.py` | Build broadphase join rows, then refine them with segment intersections. |
| `benchmark_app_recipes.py` | Map the tutorial concepts to the 10 benchmark apps. |

The remaining scripts show individual operator surfaces and partner choices.
They are intentionally smaller than full benchmark apps.
