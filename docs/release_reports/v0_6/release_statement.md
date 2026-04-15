# RTDL v0.6 Release Statement

Date: 2026-04-15
Status: released as `v0.6.1`

## Statement

RTDL `v0.6` is the corrected RT graph release line for the repository.

It adds the first released RTDL-kernel graph workload family:

- `bfs`
- `triangle_count`

This package is the canonical `v0.6` release report set for:

- `v0.6.1`

## What The v0.6 Line Stands On

The corrected `v0.6` line now has:

- RT graph kernel surface design
- RT graph execution interpretation and lowering contract
- Python truth paths for:
  - `bfs`
  - `triangle_count`
- native CPU/oracle execution for:
  - `bfs`
  - `triangle_count`
- Embree execution for:
  - `bfs`
  - `triangle_count`
- OptiX execution for:
  - `bfs`
  - `triangle_count`
- Vulkan execution for:
  - `bfs`
  - `triangle_count`
- PostgreSQL-backed external correctness anchoring
- large-batch correctness validation on real public graph slices
- large-scale performance evidence on public graph datasets
- internal 3-AI pre-release closure and external independent release check

## What The v0.6 Line Adds

`v0.6` adds:

- the first released graph workload family in RTDL
- an RTDL-kernel graph execution model aligned with the RT graph direction
- a backend story across:
  - CPU/oracle
  - Embree
  - OptiX
  - Vulkan
- PostgreSQL as the supporting external correctness baseline for graph
  workloads

## What The v0.6 Line Does Not Claim

The `v0.6` line does not claim:

- that RTDL graph universally beats specialized graph systems
- that all external comparisons are exact apples-to-apples workload matches
- that the published OptiX numbers are RTX-class RT-core results on the Linux
  benchmark host
- that PostgreSQL is a production RTDL backend

## Relationship To Earlier Releases

Read the repo now as:

- `v0.2.0`: stable workload/package core
- `v0.3.0`: released RTDL-plus-Python bounded application/demo proof
- `v0.4.0`: released nearest-neighbor workload expansion
- `v0.5.0`: released 3D nearest-neighbor and bounded multi-backend expansion
- `v0.6.1`: released corrected RT graph line

## Current Honest Release Boundary

- RTDL can express and execute graph workloads through the RT kernel path
- correctness is closed on the validated bounded and large-batch slices
- OptiX and Vulkan are the main RTDL graph backends going forward
- Linux carries the main correctness/performance validation story
- Windows participates in the bounded validation story
