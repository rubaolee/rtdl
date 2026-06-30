# Goal 395: v0.6 Vulkan RT Graph Mapping And BFS Closure

## Objective

Bring the first RTDL graph workload onto the Vulkan backend by defining the
bounded Vulkan graph mapping and closing the first workload, `bfs`.

## Why This Goal Exists

Goal 394 closes the first bounded OptiX graph slice. The next backend step is
Vulkan, which should be treated as its own graph mapping problem rather than as
an automatic copy of the Embree or OptiX implementation.

The current Vulkan state is:

- real geometry backend coverage exists
- `run_vulkan(...)` had no graph predicate dispatch
- the native Vulkan surface had no graph-specific BFS ABI yet

## Required Outcome

This goal is complete only when the repo contains:

- a bounded Vulkan graph ABI for RT-kernel `bfs`
- Python Vulkan runtime support for that BFS graph step
- focused tests proving bounded parity versus Python/oracle
- honest documentation of what is truly Vulkan-specific in the implementation

## Honesty Boundary

This goal does not claim:

- Vulkan `triangle_count`
- full graph lowering
- large-scale GPU benchmark results

This goal is only the first bounded Vulkan graph workload closure.
