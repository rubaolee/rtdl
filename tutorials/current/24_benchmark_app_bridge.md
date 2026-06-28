# Benchmark App Bridge

The 10 benchmark apps are not the first V4 tutorial. They are a check that the
small RTDL V4 concepts compose.

Run:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/benchmark_app_recipes.py
```

## How To Read The Bridge

Each benchmark app is described as a small plan:

```text
app idea
  -> operator request
  -> explicit partner
  -> input row shape
  -> continuation or output shape
```

Open the full app source only after you can identify those pieces. If an app
uses a continuation, ask which tutorial program taught that continuation. If an
app uses a partner, ask which partner contract it relies on.

## Prerequisite Map

| Benchmark app | Read these tutorial programs first | Main RTDL concept |
| --- | --- | --- |
| RTDBSCAN | `fixed_radius_neighbors.py`, `component_union_from_radius.py` | Radius rows plus component continuation. |
| RTNN | `nearest_neighbor.py`, `ranked_summary_neighbors.py` | Nearest witness and bounded ranked summary. |
| Triangle counting | `ray_triangle_hits.py`, `triangle_counting_graph_lowering.py`, `continuation_grouped_sum.py` | Witness rows plus grouped integer reduction. |
| Robot collision | `ray_triangle_hits.py`, `robot_collision_lowering.py` | Hit rows grouped into pose collision flags. |
| RayDB-style query | `raydb_table_to_ray.py`, `continuation_grouped_sum.py` | Payload-preserving hit rows and grouped aggregation. |
| LibRTS spatial index | `aabb_spatial_index_predicates.py` | AABB broadphase predicate rows. |
| Contact manifold | `aabb_spatial_index_predicates.py`, `bounded_witness_collection.py`, `contact_manifold_lowering.py` | Broadphase pairs plus bounded witnesses. |
| Spatial RayJoin | `spatial_join_lsi.py`, `rayjoin_topology_intro.py` | LSI rows plus topology/boundary policy. |
| Barnes-Hut | `aggregate_frontier_rows.py`, `continuation_grouped_sum.py` | Aggregate-frontier rows plus weighted continuation. |
| Hausdorff | `nearest_neighbor.py`, `hausdorff_distance_recipe.py` | Directed nearest-witness composition. |

This table is the bridge from small RTDL features to larger apps. It is not a
promise that every app has a special V4 kernel. The app is composed from the
generic relation and continuation pieces.

## What This Is Not

This bridge is not a shortcut around learning RTDL. It is an index that connects
the concept programs to the full benchmark apps.

Next: [Benchmark app examples](../../examples/benchmark_apps/README.md)

After benchmark apps, see also
[Paper reproduction examples](../../examples/paper_reproduction/README.md).
