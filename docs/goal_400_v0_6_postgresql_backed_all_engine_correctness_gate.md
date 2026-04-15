# Goal 400: v0.6 PostgreSQL-Backed All-Engine Correctness Gate

## Objective

Strengthen the corrected RT-kernel graph line so all engine correctness claims
are also checked against PostgreSQL, not only against Python and native/oracle.

## Why This Goal Exists

Goal 399 established the first bounded integrated engine gate across:

- Python
- native/oracle
- Embree
- OptiX
- Vulkan

But the acceptance bar is higher:

- all engines must also agree with PostgreSQL on bounded graph cases

That makes PostgreSQL the required external correctness anchor for the engine
line, not just an optional supporting baseline.

## Required Outcome

This goal is complete only when the repo contains:

- bounded PostgreSQL graph checks for:
  - `bfs`
  - `triangle_count`
- integrated parity checks showing agreement among:
  - Python
  - native/oracle
  - Embree
  - OptiX
  - Vulkan
  - PostgreSQL
- explicit documentation of what PostgreSQL indexes and SQL paths are used

## Honesty Boundary

This goal does not claim:

- large-scale performance closure
- final benchmark conclusions
- release closure

This goal is the correctness gate that upgrades Goal 399 by requiring
PostgreSQL-backed parity.
