# Goal 393: v0.6 Embree RT Graph Mapping And BFS Closure

## Objective

Bring the first RTDL graph workload onto the Embree backend by defining the
bounded Embree graph mapping and closing the first workload, `bfs`, without
pretending the existing Embree geometry path is already graph-capable.

## Why This Goal Exists

Goals 389-392 established the bounded RT-kernel graph line through:

- Python truth-path `bfs`
- Python truth-path `triangle_count`
- native/oracle `bfs`
- native/oracle `triangle_count`

The next step is not another CPU-like fallback. It is the first actual RT
backend step for the corrected graph line.

The current Embree state is:

- real geometry-native backend coverage exists
- `run_embree(...)` dispatch has no graph predicates
- the native Embree surface in
  `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_prelude.h`
  has no graph ABI yet

## Required Outcome

This goal is complete only when the repo contains:

- a bounded Embree graph ABI for RT-kernel `bfs`
- Python Embree runtime support for that BFS graph step
- focused tests proving bounded parity versus Python/oracle
- honest documentation of what is truly Embree-specific in the implementation

## Honesty Boundary

This goal does not claim:

- full graph lowering
- Embree `triangle_count`
- OptiX or Vulkan graph support
- paper-scale performance results

This goal is only the first bounded Embree graph workload closure, and it must
be explicitly RT-approach aligned rather than a renamed CPU loop.
