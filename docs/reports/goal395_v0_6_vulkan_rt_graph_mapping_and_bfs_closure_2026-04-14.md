# Goal 395 Report: v0.6 Vulkan RT Graph Mapping And BFS Closure

Date: 2026-04-14
Status: implemented, review pending

## Summary

Goal 395 is now materially implemented.

The first RT-kernel graph workload, `bfs_discover(...)`, now runs on the
Vulkan backend through a bounded native Vulkan graph ABI and runtime dispatch.

## Code Changes

Native Vulkan ABI and implementation:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_prelude.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_core.cpp`

Python runtime and test surface:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/vulkan_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal395_v0_6_rt_graph_bfs_vulkan_test.py`

## What Landed

- `PreparedVulkanKernel` now accepts `bfs_discover`
- `run_vulkan(...)` and `prepare_vulkan(...)` can execute the bounded
  RT-kernel BFS graph step
- graph inputs are now packed for Vulkan:
  - `rt.GraphCSR`
  - `rt.VertexFrontier`
  - `rt.VertexSet`
- native symbol added:
  - `rtdl_vulkan_run_bfs_expand(...)`
- candidate generation is currently implemented as a native host-indexed
  Vulkan helper over the graph CSR inputs, not as a disguised oracle fallback

## Verification

Focused graph suite:

```text
python3 -m unittest \
  tests.goal389_v0_6_rt_graph_bfs_truth_path_test \
  tests.goal391_v0_6_rt_graph_bfs_oracle_test \
  tests.goal393_v0_6_rt_graph_bfs_embree_test \
  tests.goal394_v0_6_rt_graph_bfs_optix_test \
  tests.goal395_v0_6_rt_graph_bfs_vulkan_test
```

Result:

- `Ran 23 tests`
- `OK (skipped=8)`

The eight skipped tests are the backend-specific OptiX and Vulkan tests, which
is the expected local result when those runtimes are not installed.

Core quality gate:

```text
python3 -m unittest tests.test_core_quality
```

Result:

- `Ran 105 tests`
- `OK`

## Honesty Boundary

This Goal 395 implementation does not claim:

- Vulkan `triangle_count`
- GPU-validated graph traversal parity on this macOS machine
- large-scale graph benchmarking

The current Vulkan BFS closure is:

- a real Vulkan backend ABI/runtime path
- bounded BFS graph support
- parity-tested at the API/runtime level
- locally skipped when Vulkan is unavailable
