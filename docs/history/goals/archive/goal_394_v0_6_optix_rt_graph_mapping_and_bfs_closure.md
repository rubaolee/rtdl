# Goal 394: v0.6 OptiX RT Graph Mapping And BFS Closure

## Objective

Bring the first RTDL graph workload onto the OptiX backend by defining the
bounded OptiX graph mapping and closing the first workload, `bfs`.

## Why This Goal Exists

Goal 393 closed the first RT backend graph slice on Embree. The next backend
step is OptiX, which should be treated as its own graph mapping problem rather
than as an automatic copy of the Embree implementation.

The current OptiX state is:

- real geometry backend coverage exists
- `run_optix(...)` has no graph predicate dispatch
- the native OptiX surface has no graph-specific BFS ABI yet

## Required Outcome

This goal is complete only when the repo contains:

- a bounded OptiX graph ABI for RT-kernel `bfs`
- Python OptiX runtime support for that BFS graph step
- focused tests proving bounded parity versus Python/oracle
- honest documentation of what is truly OptiX-specific in the implementation

## Honesty Boundary

This goal does not claim:

- OptiX `triangle_count`
- Vulkan graph support
- full graph lowering
- large-scale GPU benchmark results

This goal is only the first bounded OptiX graph workload closure.
