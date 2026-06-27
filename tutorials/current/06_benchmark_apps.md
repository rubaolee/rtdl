# Build the Benchmark Apps

This tutorial shows how the 10 benchmark apps are built from the current V4
front door. The apps look different, but they reuse a small set of RT-shaped
relations and continuation operators.

The repeated pattern is:

1. describe the relation that RT cores should traverse;
2. choose the generic V4 operator surface;
3. choose an explicit measured partner;
4. keep the app-specific meaning outside the operator;
5. validate the result against the app reference.

The snippets below are runnable planner examples. They do not allocate GPU
memory. They teach which V4 surface you would use before moving to the full
benchmark script.

```python
import rtdsl.v4 as rt


def show(name, plan):
    print(name, plan.status, plan.api_surface)


show("ray/triangle any-hit", rt.plan_operator_request_v4("any_hit", partner="torch"))
```

You can run the full recipe list as one command:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\benchmark_app_recipes.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/benchmark_app_recipes.py
```

## 1. Neighborhood Apps

RTDBSCAN and RTNN both start with "which points are near this point?" The app
logic differs after that relation is formed.

### RTDBSCAN

RTDBSCAN needs fixed-radius neighbor evidence and a connected-component style
continuation.

```python
import rtdsl.v4 as rt

neighbor_count = rt.plan_operator_request_v4("fixed_radius", partner="torch")
component_union = rt.plan_operator_request_v4("component_union", partner="numba")

print(neighbor_count.api_surface)
print(component_union.api_surface)
```

Full workload source:
`examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`

### RTNN

RTNN uses a neighbor or nearest-witness relation, then ranks or summarizes the
candidate set.

```python
import rtdsl.v4 as rt

nearest = rt.plan_operator_request_v4("point_group_nearest", partner="torch")
ranked = rt.plan_operator_request_v4("ranked_summary", partner="rtdl_native")

print(nearest.status, nearest.api_surface)
print(ranked.status, ranked.guidance)
```

Full workload source:
`examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`

## 2. Ray/Triangle Apps

Triangle counting, robot collision, and RayDB-style summaries all lower part of
their work to ray/triangle hits. The app meaning is different; the RT relation
is shared.

### Triangle Counting

Triangle counting lowers graph contracts to ray/triangle relations and then
uses a compact grouped summary.

```python
import rtdsl.v4 as rt

hit_flags = rt.plan_operator_request_v4("any_hit", partner="torch")
primitive_counts = rt.plan_operator_request_v4("grouped_i64", partner="torch")

print(hit_flags.api_surface)
print(primitive_counts.api_surface)
```

Full workload source:
`examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`

### Robot Collision

Robot collision asks whether a link path intersects an obstacle primitive.

```python
import rtdsl.v4 as rt

collision_flags = rt.plan_operator_request_v4("any_hit", partner="torch")

print(collision_flags.status)
print(collision_flags.api_surface)
```

Full workload source:
`examples/current/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py`

### RayDB-Style Summaries

RayDB-style workloads use hit rows as a relation and summarize them by group.

```python
import rtdsl.v4 as rt

hit_flags = rt.plan_operator_request_v4("any_hit", partner="torch")
weighted_sum = rt.plan_operator_request_v4("weighted_sum", partner="torch")
grouped_sum = rt.plan_operator_request_v4("grouped_sum", partner="cupy")

print(hit_flags.api_surface)
print(weighted_sum.api_surface)
print(grouped_sum.status, grouped_sum.api_surface)
```

Full workload source:
`examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`

## 3. Spatial Index Apps

LibRTS spatial index, Contact manifold, and Spatial RayJoin use broadphase
candidate discovery before app-specific refinement.

### LibRTS Spatial Index

The spatial index app uses AABB-style operations for point, box, and overlap
queries.

```python
import rtdsl.v4 as rt

aabb_ops = rt.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")

print(aabb_ops.status)
print(aabb_ops.api_surface)
```

Full workload source:
`examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`

### Contact Manifold

Contact manifold first finds broadphase candidates, then keeps exact contact
refinement as explicit app logic.

```python
import rtdsl.v4 as rt

broadphase = rt.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
closest = rt.plan_operator_request_v4("closest_hit_argmin", partner="torch")

print(broadphase.api_surface)
print(closest.api_surface)
```

Full workload source:
`examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py`

### Spatial RayJoin

Spatial RayJoin builds candidate shape pairs or point-location rows, then
performs join refinement.

```python
import rtdsl.v4 as rt

candidate_pairs = rt.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
hit_flags = rt.plan_operator_request_v4("any_hit", partner="torch")

print(candidate_pairs.api_surface)
print(hit_flags.api_surface)
```

Full workload source:
`examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`

## 4. Aggregate and Witness Apps

Barnes-Hut and Hausdorff are useful because they show the difference between a
route that produces a compact decision and a route that produces a witness or
frontier for later work.

### Barnes-Hut

Barnes-Hut builds an aggregate frontier, then applies a weighted vector
continuation.

```python
import rtdsl.v4 as rt

frontier = rt.plan_operator_request_v4("aggregate_frontier", partner="rtdl_native")
weighted_sum = rt.plan_operator_request_v4("grouped_sum", partner="cupy")

print(frontier.status, frontier.api_surface)
print(weighted_sum.status, weighted_sum.api_surface)
```

Full workload source:
`examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`

### Hausdorff XHD

The threshold route asks whether a distance threshold is exceeded. The exact
nearest-witness route returns the nearest witness and is a richer V3/V4
capability.

```python
import rtdsl.v4 as rt

threshold_decision = rt.plan_operator_request_v4("fixed_radius", partner="torch")
nearest_witness = rt.plan_operator_request_v4("point_group_nearest", partner="torch")

print(threshold_decision.api_surface)
print(nearest_witness.api_surface)
```

Full workload source:
`examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`

## 5. Custom Predicate Workflow

V4.0 supports a constrained custom predicate early-exit workflow: the callback
is a pure boolean Numba device predicate, and RTDL owns the early-exit action.
Arbitrary Python actions, shared-state mutation, dynamic allocation, and
variable-length output are intentionally rejected in V4.0.

```python
import rtdsl.v4 as rt

accepted = rt.plan_operator_request_v4(
    "custom_predicate_early_exit",
    partner="numba",
    callback_shape="pure_boolean_numba_cabi_device_function",
    numba_device_function=True,
)

rejected = rt.plan_operator_request_v4(
    "custom_predicate_early_exit",
    partner="numba",
    callback_shape="custom_action",
    mutates_shared_state=True,
)

print(accepted.status, accepted.api_surface)
print(rejected.status)
```

Try it:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\custom_predicate_early_exit_planning.py
```

## 6. Running Small V4 Examples

Start with these dry-run examples before running the full app matrix:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\v4_frontdoor_quickstart.py
py -3 examples\v4\fixed_radius_torch_device_arrays.py --dry-run
py -3 examples\v4\ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
py -3 examples\v4\aabb_index_all_ops_count.py --dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/v4/fixed_radius_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/aabb_index_all_ops_count.py --dry-run
```

## User Rule

Use V4 as the current system. The V4 front door selects inherited routes when
they are the right implementation for a task.
V4 includes the mature routes from V2.14 and V3.0.2 and adds the current
operator front door. When a route is inherited, the app source can still use it
through the current benchmark entrypoint. When a route is a V4 operator surface,
name the surface, partner, denominator, and scale when discussing performance.
