# Goal 396 Report: v0.6 Embree RT Graph Mapping And Triangle Closure

Date: 2026-04-14
Status: implemented, review pending

## Summary

Goal 396 is now materially implemented.

The second RT-kernel graph workload, `triangle_match(...)`, now runs on the
Embree backend through a bounded native Embree graph ABI and runtime dispatch.

## Code Changes

Native Embree ABI and implementation:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_scene.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_api.cpp`

Python runtime and test surface:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/embree_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal396_v0_6_rt_graph_triangle_embree_test.py`

## What Landed

- `PreparedEmbreeKernel` now accepts `triangle_match`
- `run_embree(...)` and `prepare_embree(...)` can execute the bounded
  RT-kernel triangle probe graph step
- graph inputs are now packed for Embree:
  - `rt.EdgeSet`
  - `rt.GraphCSR`
- native symbol now used:
  - `rtdl_embree_run_triangle_probe(...)`
- candidate generation is Embree-specific:
  - graph edges are encoded as Embree point-query primitives keyed by source vertex
  - each seed edge issues two point queries, one for each endpoint
  - the returned neighbor sets are intersected under the RT-kernel triangle semantics

## Verification

Focused graph triangle suite:

```text
python3 -m unittest \
  tests.goal390_v0_6_rt_graph_triangle_truth_path_test \
  tests.goal392_v0_6_rt_graph_triangle_oracle_test \
  tests.goal396_v0_6_rt_graph_triangle_embree_test
```

Result:

- `Ran 14 tests`
- `OK`

Core quality gate:

```text
python3 -m unittest tests.test_core_quality
```

Result:

- `Ran 105 tests`
- `OK`

## Honesty Boundary

This Goal 396 implementation does not claim:

- OptiX `triangle_count`
- Vulkan `triangle_count`
- large-scale graph benchmarking

The current Embree triangle closure is:

- a real Embree backend ABI/runtime path
- bounded `triangle_count` graph support
- parity-tested against Python/oracle
- implemented through Embree point-query candidate generation rather than oracle fallback
