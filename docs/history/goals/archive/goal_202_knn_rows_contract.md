# Goal 202: KNN Rows Contract

Date: 2026-04-10
Status: planned

## Goal

Freeze the second public `v0.4` workload contract:

- `knn_rows`

This goal is about semantics, not implementation.

## Why this goal exists

After `fixed_radius_neighbors`, the next workload in the same family should be
the direct K-nearest-neighbor row surface.

That workload is close enough to the fixed-radius line that it would be easy to
blur the two semantics during implementation. RTDL needs one exact public
contract first, so later CPU, Embree, and baseline work can be judged against a
stable definition.

## Required result

This goal is complete when the repo contains:

- a feature home for `knn_rows`
- an explicit row contract
- an explicit ranking and tie policy
- an explicit short-result rule when fewer than `k` neighbors exist
- an honest note about what is and is not promised in the first release
- `2+` AI review confirming the contract is sharp enough to implement

## Non-goals

This goal does not:

- add DSL code
- add runtime code
- add examples or tests
- claim backend support

It only freezes the second public contract in the nearest-neighbor family.
