# Goal 202: KNN Rows Contract

Date: 2026-04-10
Status: completed

## Result

The second public `v0.4` workload contract is now frozen:

- `knn_rows`

The contract is documented as a planned `v0.4` feature and is sharp enough for
later DSL, truth-path, and backend goals to target without redefining semantics
during implementation.

## Final contract

### Public purpose

`knn_rows` finds the `k` nearest search points for each query point and emits
one row per accepted neighbor.

### First-release boundary

- 2D points only
- Euclidean distance only
- explicit `k`
- row-materialization only

### Public emitted fields

- `query_id`
- `neighbor_id`
- `distance`
- `neighbor_rank`

For the first public contract:

- `query_id` is the non-negative integer id carried by the query-side point
- `neighbor_id` is the non-negative integer id carried by the search-side point
- `neighbor_rank` is 1-based within each query group

### Deterministic ordering

Rows are ordered by:

1. ascending `query_id`
2. within each query, ascending `distance`
3. then ascending `neighbor_id`

### Tie and rank rule

- equal-distance ties are broken by `neighbor_id`
- `neighbor_rank` is assigned after applying that ordering

### Short-result rule

If fewer than `k` neighbors exist for a query:

- emit all available rows
- emit no padding rows

### Empty-query rule

If a query point has no available neighbors:

- it emits no rows

## Why these choices were made

### Why include `neighbor_rank`

Unlike `fixed_radius_neighbors`, KNN is fundamentally about ordered top-`k`
selection. Exposing `neighbor_rank` makes that order explicit in the row shape
instead of forcing users to reconstruct it from row position.

### Why `knn_rows` after `fixed_radius_neighbors`

The fixed-radius line closed the simpler radius-filtering semantics first. That
lets `knn_rows` build on a stable nearest-neighbor family rather than defining
both contracts at once.

### Why no radius in the first KNN contract

The first KNN surface should stay distinct from the fixed-radius surface. Hybrid
radius-plus-KNN behavior can be a later extension if needed.

## Repo changes in this goal

- added the planned feature home:
  - [knn_rows/README.md](/Users/rl2025/rtdl_python_only/docs/features/knn_rows/README.md)
- added the goal file:
  - [goal_202_knn_rows_contract.md](/Users/rl2025/rtdl_python_only/docs/goal_202_knn_rows_contract.md)

## Review questions

The review for this goal should answer:

- Is the contract sharp enough to implement?
- Is the ordering and rank policy deterministic enough?
- Is the short-result rule honest and usable?
- Is the planned-only status clear enough that users are not misled?
