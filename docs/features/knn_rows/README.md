# KNN Rows

## Status

Planned public workload line for `v0.4`.

Current implemented boundary:

- public DSL surface: not yet
- lowering: not yet
- Python truth path: not yet
- native CPU/oracle path: not yet
- Embree: not yet
- SciPy `cKDTree` external baseline: planned
- bounded PostGIS helper: planned
- OptiX / Vulkan: not yet

## Purpose

`knn_rows` finds the `k` nearest search points for each query point and emits
one row per accepted neighbor.

Use it when you want:

- deterministic nearest-neighbor row materialization
- candidate-edge generation for graph or clustering pipelines
- a direct top-`k` neighbor surface without explicit radius filtering

## Intended first boundary

The first accepted public boundary is:

- 2D points only
- Euclidean distance only
- one query point set
- one search point set
- one explicit `k`
- row-materialization only

## Contract

### Inputs

- `query_points`
  - role: probe/query side
  - type: 2D points
- `search_points`
  - role: build/search side
  - type: 2D points
- `k`
  - meaning: maximum number of nearest neighbors emitted per query

### Emitted fields

The first public emitted row shape is:

- `query_id`
- `neighbor_id`
- `distance`
- `neighbor_rank`

For the first public contract:

- `query_id` is the non-negative integer id attached to the query-side point
- `neighbor_id` is the non-negative integer id attached to the search-side
  point
- `neighbor_rank` is 1-based within each query row group

The distance field is the Euclidean distance between the query point and the
accepted neighbor point.

## Exact first-release semantics

### Neighbor-selection rule

For each query point:

- compute the Euclidean distance to every search point
- sort candidates by the public ordering rule
- emit only the first `k`

### Ordering rule

Rows for each query point are ordered by:

1. ascending `distance`
2. ascending `neighbor_id`

Across different queries, emitted rows are grouped by ascending `query_id`.

### Rank rule

`neighbor_rank` is assigned after sorting:

- the nearest emitted row has `neighbor_rank = 1`
- the second emitted row has `neighbor_rank = 2`
- and so on up to the number of emitted rows for that query

### Short-result rule

If fewer than `k` search points exist, or fewer than `k` distinct candidates are
available:

- emit all available rows
- do not emit padding rows

### Empty result rule

If a query point has no available search points:

- it emits no rows

### Self-match policy

The first public contract does not suppress self-matches automatically.

If the same physical dataset is supplied on both sides, rows are still driven by
the two explicit inputs. Equal coordinates or equal ids do not suppress a row
unless a later surface adds that behavior explicitly.

## Example kernel shape

Planned kernel shape:

```python
query_points = rt.input("query_points", rt.Points, role="probe")
search_points = rt.input("search_points", rt.Points, role="build")
candidates = rt.traverse(query_points, search_points, accel="bvh")
neighbors = rt.refine(
    candidates,
    predicate=rt.knn_rows(k=8),
)
return rt.emit(neighbors, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])
```

## Best Practices

- keep `query_id` and `neighbor_id` stable and auditable
- choose `k` explicitly rather than relying on an implicit default
- validate deterministic tie cases in the truth path before trusting backend
  acceleration
- use `knn_rows` for row-oriented top-`k` materialization, not summary-only
  distances

## Try

- nearest candidate generation for graph edges
- bounded top-`k` facility matching
- deterministic neighbor materialization before clustering

## Try Not

- treating this as radius filtering
- assuming unlimited neighbors per query
- reading current docs as proof of implementation before the runtime lands

## Limitations

- current status is planned only
- first release scope is 2D only
- first release scope is Euclidean only
- first release scope is row materialization, not aggregate summaries
- first release scope emits at most `k` rows per query after deterministic
  ordering
