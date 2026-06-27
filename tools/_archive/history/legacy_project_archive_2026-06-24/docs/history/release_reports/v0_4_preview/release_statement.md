# RTDL v0.4 Preview Release Statement

Date: 2026-04-10
Status: preview only, not released

## Statement

`v0.4` is currently the active nearest-neighbor development line for RTDL.

It should be read as a correctness-first expansion of the non-graphical spatial
query surface, centered on two new workload families:

- `fixed_radius_neighbors`
- `knn_rows`

This preview is not a release claim yet. It records the intended public package
shape while implementation and review are still underway.

## What The Preview Currently Stands On

The active `v0.4` line already has:

- frozen public workload contracts for:
  - `fixed_radius_neighbors`
  - `knn_rows`
- public DSL authoring support for both workloads
- Python truth paths for both workloads
- native CPU/oracle execution for both workloads
- Embree execution for both workloads
- optional external baseline helpers for:
  - SciPy `cKDTree`
  - bounded PostGIS comparison paths
- clean top-level public examples for both workloads
- one bounded local scaling note for the nearest-neighbor family

## What The Preview Does Not Claim Yet

The active `v0.4` preview does not yet claim:

- a released package or release tag
- a benchmark win against external baselines
- full GPU backend closure
- that SciPy or PostGIS are required local dependencies
- that the nearest-neighbor line is already the stable release baseline

## Relationship To v0.3.0

- `v0.3.0` remains the latest released tag on this repo
- the `v0.3.0` line demonstrated RTDL’s application-style versatility through
  the bounded visual-demo work
- the active `v0.4` line returns the project focus to non-graphical workload
  expansion

## Current Reading Rule

Read the `v0.4` material as:

- an active preview package
- a live development direction
- not a completed release report
