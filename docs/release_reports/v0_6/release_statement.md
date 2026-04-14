# RTDL v0.6 Release Statement

Date: 2026-04-14
Status: released as `v0.6.0`

## Statement

RTDL `v0.6` is the graph-workload expansion line for the repository.

It extends the released RTDL surface beyond the nearest-neighbor line with the
first bounded graph application workloads:

- `bfs`
- `triangle_count`

This package is the canonical `v0.6.0` release-facing report set for the current
graph-workload line.

## What The v0.6 Line Stands On

The `v0.6` line now has:

- a bounded graph-workload charter
- a graph data/layout contract
- Python truth paths for:
  - `bfs`
  - `triangle_count`
- native CPU/oracle execution for:
  - `bfs`
  - `triangle_count`
- PostgreSQL bounded external baseline support for:
  - `bfs`
  - `triangle_count`
- bounded Linux graph evaluation on synthetic graphs
- bounded real-data Linux evaluation on:
  - `wiki-Talk`
  - `cit-Patents`
- explicit support for Partial CSR and large sparse vertex-ID ranges
- saved audit and external-review material for the opening graph correctness line

## What The v0.6 Line Adds

`v0.6` adds:

- the first graph-workload line in RTDL
- a bounded correctness/runtime story for:
  - `bfs`
  - `triangle_count`
- a PostgreSQL-backed external SQL baseline for graph workloads
- bounded real-data graph evaluation on Linux

## What The v0.6 Line Does Not Claim

The `v0.6` line does not claim:

- a general graph DSL redesign
- full graph-backend closure beyond Python/oracle/PostgreSQL
- graph-specialized external engine parity
- benchmark or paper-scale closure
- identical maturity across Linux, Windows, and local macOS

## Relationship To Earlier Releases

Read the repo now as:

- `v0.2.0`: stable workload/package core
- `v0.3.0`: released RTDL-plus-Python bounded application/demo proof
- `v0.4.0`: released nearest-neighbor workload expansion
- `v0.5.0`: released 3D nearest-neighbor and bounded multi-backend expansion
- `v0.6.0`: released graph-workload expansion

## Current Honest Release Boundary

- the active graph pair is:
  - `bfs`
  - `triangle_count`
- Linux carries the primary correctness/evaluation story for the new graph line
- PostgreSQL is the chosen external SQL baseline for the graph line
- the graph line is released under an intentionally bounded contract and should
  not be presented as full graph-system closure
