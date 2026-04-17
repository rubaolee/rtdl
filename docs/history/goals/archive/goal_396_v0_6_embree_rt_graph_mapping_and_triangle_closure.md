# Goal 396: v0.6 Embree RT Graph Mapping And Triangle Closure

## Objective

Bring the second RTDL graph workload onto the Embree backend by defining the
bounded Embree graph mapping and closing `triangle_count`.

## Why This Goal Exists

Goal 393 closed Embree `bfs`. The next missing Embree graph capability is the
RT-kernel `triangle_match(...)` path driven by `graph_intersect`.

The current Embree state before this goal was:

- real geometry backend coverage exists
- Embree graph `bfs` is closed
- the native Embree surface declared `rtdl_embree_run_triangle_probe(...)`
- but there was no implementation or Python runtime dispatch for it

## Required Outcome

This goal is complete only when the repo contains:

- a bounded Embree graph ABI for RT-kernel `triangle_count`
- Python Embree runtime support for that triangle graph step
- focused tests proving bounded parity versus Python/oracle
- honest documentation of what is truly Embree-specific in the implementation

## Honesty Boundary

This goal does not claim:

- OptiX `triangle_count`
- Vulkan `triangle_count`
- full graph lowering
- large-scale graph benchmarking

This goal is only the first bounded Embree graph `triangle_count` closure.
