# RTDL v0.4 Release Statement

Date: 2026-04-10
Status: prepared for release, tag not created yet

## Statement

RTDL `v0.4` is the nearest-neighbor release line for the repository.

It returns the project focus to non-graphical spatial-query workloads and adds
two new workload families to the public RTDL surface:

- `fixed_radius_neighbors`
- `knn_rows`

This package is the canonical `v0.4` release report set, prepared ahead of the
final user-authorized tag step.

## What The v0.4 Line Stands On

The `v0.4` line now has:

- frozen public contracts for:
  - `fixed_radius_neighbors`
  - `knn_rows`
- public DSL authoring support for both workloads
- Python truth paths for both workloads
- native CPU/oracle execution for both workloads
- Embree execution for both workloads
- OptiX execution for both workloads
- Vulkan execution for both workloads
- optional external baseline helpers for:
  - SciPy `cKDTree`
  - bounded PostGIS comparison paths
- public top-level examples for both workloads
- one bounded scaling note for the nearest-neighbor family
- heavy Linux benchmark evidence comparing CPU, Embree, OptiX, Vulkan, and
  indexed PostGIS
- Goal 229 accelerated boundary-fix evidence restoring full heavy-case parity
- whole-line Gemini and Claude audits plus later post-benchmark follow-up
  evidence clearing the package for final release decision

## What The v0.4 Line Adds

`v0.4` adds:

- the first public nearest-neighbor workload family in RTDL
- a correctness-first multi-backend story for two related workloads across
  CPU/oracle, Embree, OptiX, and Vulkan
- a cleaner research-to-workload bridge through explicit workload/foundation
  documentation
- public first-run examples that no longer depend on internal goal naming

## What The v0.4 Line Does Not Claim

The `v0.4` line does not claim:

- final release-tag completion yet
- a benchmark win over external nearest-neighbor libraries
- that SciPy or PostGIS are required dependencies for ordinary first-run use

## Relationship To Earlier Releases

Read the repo now as:

- `v0.2.0`: stable workload/package core
- `v0.3.0`: released RTDL-plus-Python bounded application/demo proof
- `v0.4`: nearest-neighbor workload expansion on top of the same RTDL core

## Main Public Workload Entry Points

- [rtdl_fixed_radius_neighbors.py](../../../examples/rtdl_fixed_radius_neighbors.py)
- [rtdl_knn_rows.py](../../../examples/rtdl_knn_rows.py)

## Current Honest Release Boundary

- the nearest-neighbor workloads are now running across CPU/oracle, Embree,
  OptiX, and Vulkan
- the heavy Linux benchmark and Goal 229 fix restored full heavy-case
  fixed-radius parity across CPU, Embree, OptiX, Vulkan, and indexed PostGIS
- the repo still remains pre-tag until explicit user-authorized release action
