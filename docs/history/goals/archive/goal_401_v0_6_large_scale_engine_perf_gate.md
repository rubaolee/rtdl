# Goal 401: v0.6 Large-Scale Engine Performance Gate

## Objective

Run the first bounded large-scale performance gate for the corrected RT-kernel
graph line across:

- Embree
- OptiX
- Vulkan

using PostgreSQL with good indexes as the indexed external baseline.

## Why This Goal Exists

Correctness and performance must stay separate.

After Goal 400 closes correctness with PostgreSQL-backed parity, the next
requirement is large-scale performance evidence for the RT backends on real
graph workloads.

## Required Outcome

This goal is complete only when the repo contains:

- bounded large real-data runs for:
  - `bfs`
  - `triangle_count`
- backend comparisons across:
  - Embree
  - OptiX
  - Vulkan
  - PostgreSQL
- explicit PostgreSQL indexing details
- honest separation of:
  - query time
  - setup / load / index time

## Honesty Boundary

This goal does not relax correctness requirements.

The corrected RT graph line currently executes one bounded RT-kernel step at a
time, not an end-to-end whole-graph RT runtime.

So this goal is complete when the repo contains large real-data timings for:

- bounded `bfs` expansion steps
- bounded `triangle_count` probe steps

For large-scale development/performance runs:

- PostgreSQL may serve as the required external comparison baseline
- Python and oracle may be skipped for speed, per the current policy

This goal is the performance gate, not the correctness gate.
