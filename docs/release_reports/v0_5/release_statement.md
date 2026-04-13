# RTDL v0.5 Release Statement

Date: 2026-04-13
Status: release package prepared for `v0.5.0`

## Statement

RTDL `v0.5` is the 3D nearest-neighbor and multi-backend expansion line for the
repository.

It extends the released nearest-neighbor surface with:

- `bounded_knn_rows`
- 3D point nearest-neighbor support for:
  - `fixed_radius_neighbors`
  - `bounded_knn_rows`
  - `knn_rows`

This package is the canonical `v0.5` release report set for the intended
`v0.5.0` release.

## What The v0.5 Line Stands On

The `v0.5` line now has:

- frozen public NN contracts for:
  - `fixed_radius_neighbors`
  - `bounded_knn_rows`
  - `knn_rows`
- 2D and 3D public workload support for the NN trio
- Python truth paths for the active NN trio
- native CPU/oracle execution for the active NN trio
- Embree execution for the active NN trio
- OptiX execution for the active NN trio
- Vulkan execution for the active NN trio
- real KITTI raw-data validation on Linux
- PostGIS-backed external correctness/timing anchoring for the real-data line
- bounded Windows and local macOS Embree correctness verification
- saved pre-release, collaborator, public-doc, and final external-review audit
  closure

## What The v0.5 Line Adds

`v0.5` adds:

- the first released 3D nearest-neighbor line in RTDL
- the public `bounded_knn_rows` workload
- a Linux large-scale backend story across:
  - CPU/oracle
  - Embree
  - OptiX
  - Vulkan
- a clearer separation between:
  - truth path
  - accelerated RTDL backends
  - external correctness/timing anchors

## What The v0.5 Line Does Not Claim

The `v0.5` line does not claim:

- that Windows or local macOS carry the same large-scale performance story as
  Linux
- that PostGIS is a production RTDL backend
- that cuNSearch is part of the main released runtime surface
- that Vulkan has the same cross-platform maturity as the Linux primary line

## Relationship To Earlier Releases

Read the repo now as:

- `v0.2.0`: stable workload/package core
- `v0.3.0`: released RTDL-plus-Python bounded application/demo proof
- `v0.4.0`: released nearest-neighbor workload expansion
- `v0.5.0`: released 3D nearest-neighbor and bounded multi-backend expansion

## Current Honest Release Boundary

- the active NN trio is now running across Python truth, CPU/oracle, Embree,
  OptiX, and Vulkan on Linux
- Linux carries the large-scale performance evidence for the 3D NN line
- Windows and local macOS are bounded correctness platforms in the `v0.5`
  release story
- PostGIS remains an external correctness/timing anchor
- the final external review round is closed cleanly enough to proceed with
  release packaging
