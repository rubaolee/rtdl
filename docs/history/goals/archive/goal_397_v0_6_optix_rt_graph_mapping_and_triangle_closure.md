# Goal 397: v0.6 OptiX RT Graph Mapping And Triangle Closure

## Objective

Bring the second RTDL graph workload onto the OptiX backend by defining the
bounded OptiX graph mapping and closing `triangle_count`.

## Why This Goal Exists

Goal 394 closed OptiX `bfs`. The next missing OptiX graph capability is the
RT-kernel `triangle_match(...)` path driven by `graph_intersect`.

The current OptiX state is:

- real geometry backend coverage exists
- OptiX graph `bfs` is closed
- there is no native OptiX graph triangle ABI or runtime dispatch yet

## Required Outcome

This goal is complete only when the repo contains:

- a bounded OptiX graph ABI for RT-kernel `triangle_count`
- Python OptiX runtime support for that triangle graph step
- focused tests proving bounded parity versus Python/oracle
- honest documentation of what is truly OptiX-specific in the implementation

## Honesty Boundary

This goal does not claim:

- Vulkan `triangle_count`
- full graph lowering
- large-scale graph benchmarking

This goal is only the first bounded OptiX graph `triangle_count` closure.
