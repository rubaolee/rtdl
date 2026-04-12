# Goal 262: v0.5 Bounded-Radius KNN Contract Design

Date: 2026-04-11
Status: implemented

## Purpose

Close the paper-consistent KNN contract decision before API code spreads.

## Decision

`v0.5` should add a new explicit predicate:

- `bounded_knn_rows(radius: float, k_max: int)`

instead of mutating the released `knn_rows(k=...)` predicate.

## Why This Is The Right Move

- protects the released `v0.4.0` API from semantic drift
- keeps the paper-aligned contract explicit
- separates:
  - pure KNN ordering
  - radius-bounded neighbor discovery
  - radius-bounded KNN ranking

## Resulting Predicate Family

- `fixed_radius_neighbors(radius, k_max)`
- `knn_rows(k)`
- `bounded_knn_rows(radius, k_max)`

## Next Implementation Meaning

The next code goals can now implement:

- API surface
- lowering
- reference path
- native path

without ambiguity about whether `knn_rows` itself was supposed to change.
