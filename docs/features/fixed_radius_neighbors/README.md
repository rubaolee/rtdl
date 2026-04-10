# Fixed-Radius Neighbors

## Status

Active public workload line for `v0.4`.

Current implemented boundary:

- public DSL surface: yes
- lowering: yes
- Python truth path: yes
- native CPU/oracle path: yes
- Embree: yes
- OptiX / Vulkan: not yet

## Purpose

`fixed_radius_neighbors` finds all search points within a given radius of each
query point and emits one row per accepted neighbor pair.

Use it when you want:

- radius-based neighborhood screening
- local point-density style row materialization
- bounded neighborhood joins over point sets

## Intended first boundary

The first accepted public boundary is:

- 2D points only
- Euclidean distance only
- one query point set
- one search point set
- one explicit radius `r`
- one explicit neighbor cap `k_max`

## Contract

### Inputs

- `query_points`
  - role: probe/query side
  - type: 2D points
- `search_points`
  - role: build/search side
  - type: 2D points
- `radius`
  - meaning: inclusive Euclidean search radius
- `k_max`
  - meaning: maximum emitted neighbors per query row group

### Emitted fields

The first public emitted row shape is:

- `query_id`
- `neighbor_id`
- `distance`

For the first public contract:

- `query_id` is the non-negative integer id attached to the query-side point
- `neighbor_id` is the non-negative integer id attached to the search-side
  point

The distance field is the Euclidean distance between the query point and the
accepted neighbor point.

## Exact first-release semantics

### Radius rule

A search point is eligible if:

- `distance <= radius`

Boundary-distance points count as neighbors.

### Self-match policy

The first public contract does not assume self-matches by default.

If the same physical dataset is supplied on both sides, rows are still driven by
the two explicit inputs. Whether a query point and a search point happen to have
equal coordinates does not suppress the row automatically.

### Ordering rule

Rows for each query point are ordered by:

1. ascending `distance`
2. ascending `neighbor_id`

This is the public deterministic tie rule.

Across different queries, emitted rows are grouped by ascending `query_id`.

### Overflow rule

If more than `k_max` search points satisfy the radius rule for one query point,
the runtime emits only the first `k_max` rows under the public ordering rule.

So the first release contract is:

- truncate after ordering
- do not emit an overflow marker row
- do not promise total-neighbor counts beyond emitted rows

### Empty result rule

If a query point has no neighbors within the radius:

- it emits no rows

The first release contract is row-materialization only. It does not emit
zero-count summary rows.

## Example kernel shape

Current kernel shape:

```python
query_points = rt.input("query_points", rt.Points, role="probe")
search_points = rt.input("search_points", rt.Points, role="build")
candidates = rt.traverse(query_points, search_points, accel="bvh")
neighbors = rt.refine(
    candidates,
    predicate=rt.fixed_radius_neighbors(radius=0.5, k_max=16),
)
return rt.emit(neighbors, fields=["query_id", "neighbor_id", "distance"])
```

## Best Practices

- keep `query_id` and `neighbor_id` stable and auditable
- choose `k_max` explicitly rather than relying on an implicit default
- validate deterministic tie cases in the Python reference path first
- use this workload for row-oriented neighborhood materialization, not summary
  aggregation

## Try

- neighborhood screening around facilities
- local density row materialization for event points
- candidate-edge generation for later clustering or graph building

## Try Not

- using this as a count-only workload
- assuming unlimited neighbors per query
- treating this as KNN without an explicit radius rule
- reading current docs as proof of implementation before the runtime lands

## Limitations

- current accelerated closure is Embree only
- first release scope is 2D only
- first release scope is Euclidean only
- first release scope is row materialization, not aggregate summaries
- first release scope truncates to `k_max` after deterministic ordering
