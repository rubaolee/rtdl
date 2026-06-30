# Goal 196: Fixed-Radius Neighbors Contract

Date: 2026-04-09
Status: planned

## Goal

Freeze the first public `v0.4` workload contract:

- `fixed_radius_neighbors`

This goal is about semantics, not implementation.

## Why this goal exists

The `v0.4` milestone is now defined as a nearest-neighbor workload release.

Before any backend work starts, RTDL needs one exact public contract for the
first workload in that family. The contract must be stable enough that later
implementation goals can be judged against it rather than silently redefining
the feature during coding.

## Required result

This goal is complete when the repo contains:

- a feature home for `fixed_radius_neighbors`
- an explicit row contract
- an explicit ordering and tie policy
- an explicit overflow policy for `k_max`
- an honest note about what is and is not promised in the first release
- `2+` AI review confirming the contract is sharp enough to implement

## Non-goals

This goal does not:

- add DSL code
- add runtime code
- add examples or tests
- claim backend support

It only freezes the first public contract.
