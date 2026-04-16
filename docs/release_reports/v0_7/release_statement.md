# RTDL v0.7 Branch Statement

Date: 2026-04-15
Status: active bounded branch line, not yet tagged as the next mainline release

## Statement

RTDL `v0.7` is the bounded DB-style analytical workload line on the
`codex/v0_7_rt_db` branch.

It adds the first bounded RTDL database-kernel family:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

This package is the canonical branch report set for the current `v0.7` DB
line.

## What The v0.7 Line Stands On

The bounded `v0.7` line now has:

- DB kernel surface design
- RT DB execution interpretation and lowering contract
- Python truth paths for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- native CPU/oracle execution for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- Embree execution for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- OptiX execution for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- Vulkan execution for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- PostgreSQL-backed correctness anchoring on Linux
- cross-engine correctness closure on Linux across:
  - Python truth
  - native/oracle CPU
  - Embree
  - OptiX
  - Vulkan
  - PostgreSQL
- bounded Linux performance evidence with PostgreSQL included

## What The v0.7 Line Adds

`v0.7` adds:

- the first bounded DB-style analytical kernel family in RTDL
- an RT DB execution model aligned with the accepted RT lowering contract
- a backend story across:
  - CPU/oracle
  - Embree
  - OptiX
  - Vulkan
- PostgreSQL as the external correctness and performance baseline on Linux

## What The v0.7 Line Does Not Claim

The `v0.7` line does not claim:

- that RTDL is a DBMS
- that RTDL executes arbitrary SQL
- that the first bounded DB kernels cover arbitrary joins, transactions, or
  multi-group-key grouped queries
- that any current RT backend beats warm-query PostgreSQL
- that the current branch line has already replaced the repository's last tagged
  mainline release

## Relationship To Earlier Releases

Read the repo now as:

- `v0.2.0`: stable workload/package core
- `v0.3.0`: released RTDL-plus-Python bounded application/demo proof
- `v0.4.0`: released nearest-neighbor workload expansion
- `v0.5.0`: released 3D nearest-neighbor and bounded multi-backend expansion
- `v0.6.1`: released corrected RT graph line
- `v0.7`: active bounded DB branch line

## Current Honest Boundary

- RTDL can express and execute a first bounded DB-style analytical workload
  family through the RT kernel path
- correctness is closed across Python, native/oracle CPU, Embree, OptiX,
  Vulkan, and PostgreSQL on Linux
- Linux carries the main correctness/performance validation story for this line
- this branch line is release-gated but not yet the new tagged mainline release
