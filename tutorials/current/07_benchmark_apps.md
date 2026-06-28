# Build the Benchmark Apps

The 10 benchmark apps are not 10 unrelated special cases. They are examples of
the same V4 programming style:

1. name the RT-shaped relation;
2. choose a generic operator;
3. choose a partner;
4. keep app meaning in normal Python;
5. validate the result.

Run the recipe program first:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\point_in_polygon.py
py -3 examples\tutorial_programs\spatial_join_lsi.py
py -3 examples\tutorial_programs\aggregate_frontier_rows.py
py -3 examples\tutorial_programs\component_union_from_radius.py
py -3 examples\tutorial_programs\ranked_summary_neighbors.py
py -3 examples\tutorial_programs\bounded_witness_collection.py
py -3 examples\tutorial_programs\triangle_counting_graph_lowering.py
py -3 examples\tutorial_programs\robot_collision_lowering.py
py -3 examples\tutorial_programs\hausdorff_distance_recipe.py
py -3 examples\tutorial_programs\raydb_table_to_ray.py
py -3 examples\tutorial_programs\rayjoin_topology_intro.py
py -3 examples\tutorial_programs\benchmark_app_recipes.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/point_in_polygon.py
PYTHONPATH=src:. python examples/tutorial_programs/spatial_join_lsi.py
PYTHONPATH=src:. python examples/tutorial_programs/aggregate_frontier_rows.py
PYTHONPATH=src:. python examples/tutorial_programs/component_union_from_radius.py
PYTHONPATH=src:. python examples/tutorial_programs/ranked_summary_neighbors.py
PYTHONPATH=src:. python examples/tutorial_programs/bounded_witness_collection.py
PYTHONPATH=src:. python examples/tutorial_programs/triangle_counting_graph_lowering.py
PYTHONPATH=src:. python examples/tutorial_programs/robot_collision_lowering.py
PYTHONPATH=src:. python examples/tutorial_programs/hausdorff_distance_recipe.py
PYTHONPATH=src:. python examples/tutorial_programs/raydb_table_to_ray.py
PYTHONPATH=src:. python examples/tutorial_programs/rayjoin_topology_intro.py
PYTHONPATH=src:. python examples/tutorial_programs/benchmark_app_recipes.py
```

The concept scripts are small tutorial programs for ideas that appear inside
the full apps: radius-neighbor rows, NN witness rows, broadphase candidate
discovery, exact containment, ray-hit flags, and join refinement. The recipes
below are copy-paste runnable planner examples. They teach the shape of each
app before you open the full app source.

The app-lowering scripts add the bridge from a single concept to a full
benchmark app:

| App idea | Program to run first |
| --- | --- |
| Barnes-Hut aggregate frontier | `examples/tutorial_programs/aggregate_frontier_rows.py` |
| RTDBSCAN components | `examples/tutorial_programs/component_union_from_radius.py` |
| RTNN ranked summaries | `examples/tutorial_programs/ranked_summary_neighbors.py` |
| Contact witnesses | `examples/tutorial_programs/bounded_witness_collection.py` |
| Triangle counting | `examples/tutorial_programs/triangle_counting_graph_lowering.py` |
| Robot collision | `examples/tutorial_programs/robot_collision_lowering.py` |
| Hausdorff XHD | `examples/tutorial_programs/hausdorff_distance_recipe.py` |
| RayDB-style query | `examples/tutorial_programs/raydb_table_to_ray.py` |
| Spatial RayJoin | `examples/tutorial_programs/rayjoin_topology_intro.py` |

## Common Helper

Each recipe uses the same helper.

```python
import rtdsl.v4 as rt


def choose(operator, partner):
    plan = rt.plan_operator_request_v4(operator, partner=partner)
    print(operator, partner, plan.status, plan.api_surface)
    return plan
```

## 1. RTDBSCAN

RTDBSCAN clusters points by density. In RTDL terms, it first asks for a
fixed-radius neighbor relation, then merges points that are density-connected.

```python
import rtdsl.v4 as rt

neighbors = rt.plan_operator_request_v4("fixed_radius", partner="torch")
components = rt.plan_operator_request_v4("component_union", partner="numba")

print(neighbors.api_surface)
print(components.api_surface)
```

App structure:

- input: point columns and a radius;
- RT relation: points within radius;
- continuation: component union;
- validation: cluster labels match the reference.

Current V4 entry:
`examples/benchmark_apps/rt_dbscan/v4_app.py`

## 2. RTNN

RTNN asks for nearest-neighbor evidence. The RTDL part is the nearest-witness
relation; the app decides how to rank or summarize the witnesses.

```python
import rtdsl.v4 as rt

nearest = rt.plan_operator_request_v4("point_group_nearest", partner="torch")
ranked = rt.plan_operator_request_v4("ranked_summary", partner="rtdl_native")

print(nearest.api_surface)
print(ranked.status)
```

App structure:

- input: query points and reference points;
- RT relation: nearest witness per query or group;
- continuation: ranked summary;
- validation: nearest IDs and distances match the reference.

Current V4 entry:
`examples/benchmark_apps/rtnn/v4_app.py`

## 3. Triangle Counting

Triangle counting turns graph structure into geometric hit tests. RTDL handles
the any-hit relation and grouped integer reduction; the app owns the graph
meaning.

```python
import rtdsl.v4 as rt

hits = rt.plan_operator_request_v4("any_hit", partner="torch")
counts = rt.plan_operator_request_v4("grouped_i64", partner="torch")

print(hits.api_surface)
print(counts.api_surface)
```

App structure:

- input: graph-derived rays and triangle primitives;
- RT relation: ray/triangle hit flags;
- continuation: grouped integer counts;
- validation: triangle counts match the graph reference.

Current V4 entry:
`examples/benchmark_apps/triangle_counting/v4_app.py`

## 4. Robot Collision

Robot collision asks whether a motion segment intersects an obstacle primitive.
This is an any-hit question with robotics data around it.

```python
import rtdsl.v4 as rt

collision = rt.plan_operator_request_v4("any_hit", partner="torch")

print(collision.status)
print(collision.api_surface)
```

App structure:

- input: robot link paths and obstacle primitives;
- RT relation: any collision hit;
- continuation: one collision flag per motion query;
- validation: collision flags match the reference.

Current V4 entry:
`examples/benchmark_apps/robot_collision/v4_app.py`

## 5. RayDB-Style Query

A RayDB-style app treats hits as a relation, then runs a database-like summary
over the relation.

```python
import rtdsl.v4 as rt

hits = rt.plan_operator_request_v4("any_hit", partner="torch")
weighted = rt.plan_operator_request_v4("weighted_sum", partner="torch")
grouped = rt.plan_operator_request_v4("grouped_sum", partner="cupy")

print(hits.api_surface)
print(weighted.api_surface)
print(grouped.api_surface)
```

App structure:

- input: ray table, primitive table, and value columns;
- RT relation: hit rows;
- continuation: weighted or grouped summary;
- validation: query result matches the relational reference.

Current V4 entry:
`examples/benchmark_apps/raydb_style/v4_app.py`

## 6. LibRTS Spatial Index

The spatial index app is about AABB-style predicates: point queries, box
queries, and overlap counts.

```python
import rtdsl.v4 as rt

aabb = rt.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")

print(aabb.status)
print(aabb.api_surface)
```

App structure:

- input: AABB min/max columns and query columns;
- RT relation: candidate boxes or overlap counts;
- continuation: compact count or row summary;
- validation: index answers match the reference.

Current V4 entry:
`examples/benchmark_apps/librts_spatial_index/v4_app.py`

## 7. Contact Manifold

Contact manifold starts with broadphase candidate discovery. It then refines
candidate pairs into closest witnesses or contact data.

```python
import rtdsl.v4 as rt

broadphase = rt.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
closest = rt.plan_operator_request_v4("closest_hit_argmin", partner="torch")

print(broadphase.api_surface)
print(closest.api_surface)
```

App structure:

- input: shape bounds and candidate primitives;
- RT relation: broadphase pairs and closest-hit witnesses;
- continuation: contact-specific refinement;
- validation: contact candidates match the reference.

Current V4 entry:
`examples/benchmark_apps/contact_manifold/v4_app.py`

## 8. Spatial RayJoin

Spatial RayJoin builds candidate pairs, then refines those pairs with RT
predicates.

```python
import rtdsl.v4 as rt

pairs = rt.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
hits = rt.plan_operator_request_v4("any_hit", partner="torch")

print(pairs.api_surface)
print(hits.api_surface)
```

App structure:

- input: two spatial relations;
- RT relation: candidate pair or hit predicate;
- continuation: join refinement;
- validation: joined rows match the reference.

Current V4 entry:
`examples/benchmark_apps/spatial_rayjoin/v4_app.py`

## 9. Barnes-Hut

Barnes-Hut uses a tree-like aggregate frontier. RTDL builds the frontier; the
continuation computes a weighted vector contribution.

```python
import rtdsl.v4 as rt

frontier = rt.plan_operator_request_v4("aggregate_frontier", partner="rtdl_native")
weighted = rt.plan_operator_request_v4("grouped_sum", partner="cupy")

print(frontier.api_surface)
print(weighted.api_surface)
```

App structure:

- input: body positions, masses, and aggregate cell columns;
- RT relation: aggregate frontier per body;
- continuation: weighted vector sum;
- validation: force or contribution vectors match the reference tolerance.

Current V4 entry:
`examples/benchmark_apps/barnes_hut/v4_app.py`

## 10. Hausdorff XHD

Hausdorff-style distance can be written as a threshold decision or as an exact
nearest-witness problem.

```python
import rtdsl.v4 as rt

threshold = rt.plan_operator_request_v4("fixed_radius", partner="torch")
witness = rt.plan_operator_request_v4("point_group_nearest", partner="torch")

print(threshold.api_surface)
print(witness.api_surface)
```

App structure:

- input: two point sets;
- RT relation: threshold neighbor or nearest witness;
- continuation: max/min distance summary;
- validation: distance result matches the reference.

Current V4 entry:
`examples/benchmark_apps/hausdorff_xhd/v4_app.py`

## One-Page Map

| App | Main RTDL relation | Main continuation | Typical partner |
| --- | --- | --- | --- |
| RTDBSCAN | fixed-radius neighbors | component union | Torch + Numba |
| RTNN | nearest witness | ranked summary | Torch + RTDL native |
| Triangle counting | ray/triangle any-hit | grouped integer count | Torch |
| Robot collision | ray/triangle any-hit | collision flags | Torch |
| RayDB-style | hit relation | weighted/grouped summary | Torch + CuPy |
| LibRTS spatial index | AABB query | count summary | RTDL native |
| Contact manifold | AABB candidates | closest-hit argmin | RTDL native + Torch |
| Spatial RayJoin | candidate pairs | join refinement | RTDL native + Torch |
| Barnes-Hut | aggregate frontier | weighted vector sum | RTDL native + CuPy |
| Hausdorff XHD | threshold or witness | distance summary | Torch |

Next: [Choose a Partner](08_choose_a_partner.md)

