# Goal 262: v0.5 Bounded-Radius KNN Contract Design

## Purpose

Define the paper-consistent bounded-radius KNN public contract for `v0.5`
without destabilizing the released `v0.4.0` nearest-neighbor surface.

## Current Constraint

The released public surface has:

- `fixed_radius_neighbors(radius=..., k_max=...)`
- `knn_rows(k=...)`

That is useful and correct for `v0.4.0`.

It does not directly expose the paper-style contract where both:

- search radius
- maximum returned neighbors

are part of the same KNN-style predicate.

## Design Decision

`v0.5` should add a new explicit predicate instead of mutating the released
`knn_rows(k=...)` contract in place.

Proposed name:

- `bounded_knn_rows(radius: float, k_max: int)`

## Why A New Predicate Is Better

### 1. Protects released `v0.4.0`

`knn_rows(k=...)` is already released and documented. Changing its meaning would
create silent semantic drift.

### 2. Keeps families distinct

- `fixed_radius_neighbors(radius, k_max)`
  - radius-bounded neighbor discovery
  - no neighbor rank field today
- `knn_rows(k)`
  - pure nearest-order rows
  - no radius filter
- `bounded_knn_rows(radius, k_max)`
  - nearest-order rows within a radius bound
  - explicit rank-bearing bounded KNN family

### 3. Makes paper-consistency claims honest

The new paper-aligned semantics become additive and explicit, not retroactive.

## Proposed Output Contract

`bounded_knn_rows` should emit rows with:

- `query_id`
- `neighbor_id`
- `distance`
- `neighbor_rank`

Ordering:

- rows grouped by ascending `query_id`
- within each query:
  - ascending `neighbor_rank`
  - which is assigned by ascending `(distance, neighbor_id)`

Filtering:

- only neighbors with `distance <= radius`
- emit at most `k_max` rows per query

## Relationship To Existing Predicates

`bounded_knn_rows` is not a synonym for `fixed_radius_neighbors`.

The difference is semantic and output-oriented:

- `fixed_radius_neighbors` is a radius-bounded neighbor family
- `bounded_knn_rows` is a radius-bounded KNN ranking family

This distinction matters for paper alignment and for downstream code that wants
explicit nearest-neighbor rank fields.

## Non-Goals

This goal does not itself implement:

- API code
- lowering
- reference execution
- native backend execution

It closes the public contract decision first.

## Success Condition

This goal is successful if the repo has a saved, reviewed design agreement that:

- preserves released `knn_rows(k)`
- introduces a new explicit bounded-radius KNN predicate
- defines the row semantics clearly enough for the next implementation goals
