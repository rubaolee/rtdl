# Goal 216: OptiX Fixed-Radius Neighbors

## Objective

Close `fixed_radius_neighbors` on OptiX for `v0.4`.

This goal is part of the reopened GPU-required `v0.4` bar:

- `fixed_radius_neighbors` must support:
  - `cpu`
  - `embree`
  - `optix`
  - `vulkan`
- `knn_rows` must support:
  - `cpu`
  - `embree`
  - `optix`
  - `vulkan`

## Scope

Bounded to the OptiX backend for `fixed_radius_neighbors`.

Accepted work in this goal:

- OptiX native ABI support
- OptiX Python runtime support
- row-level contract parity against CPU/Python reference
- authored and fixture tests
- Linux OptiX validation

Not in scope:

- `knn_rows` OptiX
- Vulkan implementation
- performance optimization beyond correctness-first viability

## Contract

The OptiX path must preserve the public `fixed_radius_neighbors` contract:

- emitted fields:
  - `query_id`
  - `neighbor_id`
  - `distance`
- emitted rows must satisfy:
  - `distance <= radius`
- per-query ordering:
  - ascending `distance`
  - then ascending `neighbor_id`
- global grouping:
  - ascending `query_id`
- truncation:
  - per-query truncate to `k_max` after the public ordering rule

## Implementation Direction

Use the existing OptiX/CUDA helper family as the closest implementation base.

Specifically:

- mirror the current OptiX `point_nearest_segment` helper style
- add a correctness-first GPU-parallel helper for `fixed_radius_neighbors`
- avoid overclaiming BVH/RT-core optimization until parity is proven

## Closure Bar

This goal is only closable when:

1. authored-case row parity against `cpu_python_reference` is green
2. fixture-case row parity against `cpu_python_reference` is green
3. raw-mode row shape is correct
4. baseline runner `optix` backend works for the workload
5. Linux OptiX validation is green
6. `2+` AI review is saved
