# Goal 196: Fixed-Radius Neighbors Contract

Date: 2026-04-09
Status: completed

## Result

The first public `v0.4` workload contract is now frozen:

- `fixed_radius_neighbors`

The contract is documented as a planned `v0.4` feature and is sharp enough for
implementation goals to target without silently redefining semantics later.

## Final contract

### Public purpose

`fixed_radius_neighbors` finds all search points within a radius of each query
point and emits one row per accepted neighbor.

### First-release boundary

- 2D points only
- Euclidean distance only
- explicit `radius`
- explicit `k_max`
- row-materialization only

### Public emitted fields

- `query_id`
- `neighbor_id`
- `distance`

For the first public contract:

- `query_id` is the non-negative integer id carried by the query-side point
- `neighbor_id` is the non-negative integer id carried by the search-side point

### Deterministic ordering

Rows are ordered by:

1. ascending `query_id`
2. within each query, ascending `distance`
3. then ascending `neighbor_id`

### Boundary and tie rule

- `distance <= radius` counts as a neighbor
- equal-distance ties are broken by `neighbor_id`

### Overflow rule

If a query has more than `k_max` eligible neighbors:

- sort using the public ordering rule
- emit only the first `k_max`
- emit no extra overflow marker row

### Empty-query rule

If a query point has no eligible neighbors:

- it emits no rows

## Clarifications added during review

After external review, two small documentation clarifications were folded in:

- the example kernel no longer implies unexplained `exact=False` semantics
- the source/type of `query_id` and `neighbor_id` is now stated explicitly

## Why these choices were made

### Why row materialization, not summaries

This keeps the first public workload clearly distinct from later summary
variants like:

- `nearest_distance`
- neighbor counts within radius

### Why `fixed_radius_neighbors` before `knn_rows`

The row semantics are easier to explain and audit:

- explicit radius
- explicit truncation
- deterministic tie rule

That makes it the right first public contract in the family.

### Why no overflow marker row

It keeps the row shape small and stable.

If users later need explicit truncation metadata, that should be a later
surface addition, not a silent complication in the first contract.

## Repo changes in this goal

- added the planned feature home:
  - [fixed_radius_neighbors/README.md](/Users/rl2025/rtdl_python_only/docs/features/fixed_radius_neighbors/README.md)
- added the goal file:
  - [goal_196_fixed_radius_neighbors_contract.md](/Users/rl2025/rtdl_python_only/docs/goal_196_fixed_radius_neighbors_contract.md)

## Review questions

The review for this goal should answer:

- Is the contract sharp enough to implement?
- Are ordering and tie rules deterministic enough?
- Is the `k_max` overflow rule honest and usable?
- Is the planned-only status clear enough that users are not misled?
