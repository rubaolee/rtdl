# Goal 398: v0.6 Vulkan RT Graph Mapping And Triangle Closure

## Objective

Bring the second RTDL graph workload onto the Vulkan backend by defining the
bounded Vulkan graph mapping and closing `triangle_count`.

## Why This Goal Exists

Goal 395 closed Vulkan `bfs`. The next missing Vulkan graph capability is the
RT-kernel `triangle_match(...)` path driven by `graph_intersect`.

The current Vulkan state is:

- real geometry backend coverage exists
- Vulkan graph `bfs` is closed
- there is no native Vulkan graph triangle ABI or runtime dispatch yet

## Required Outcome

This goal is complete only when the repo contains:

- a bounded Vulkan graph ABI for RT-kernel `triangle_count`
- Python Vulkan runtime support for that triangle graph step
- focused tests proving bounded parity versus Python/oracle
- honest documentation of what is truly Vulkan-specific in the implementation

## Honesty Boundary

This goal does not claim:

- release-grade large-scale GPU benchmarking
- full graph lowering
- anything beyond the bounded RT-kernel `triangle_count` step

This goal is only the first bounded Vulkan graph `triangle_count` closure.
