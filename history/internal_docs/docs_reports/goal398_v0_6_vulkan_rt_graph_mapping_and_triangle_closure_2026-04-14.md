# Goal 398 Report: v0.6 Vulkan RT Graph Mapping And Triangle Closure

Date: 2026-04-14
Status: implemented, review pending

## Summary

Goal 398 is now materially implemented.

The second RT-kernel graph workload, `triangle_match(...)`, now runs on the
Vulkan backend through a bounded native Vulkan graph ABI and runtime dispatch.

## Code Changes

Native Vulkan ABI and implementation:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_prelude.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_core.cpp`

Python runtime and test surface:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/vulkan_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal398_v0_6_rt_graph_triangle_vulkan_test.py`

## What Landed

- `PreparedVulkanKernel` now accepts `triangle_match`
- `run_vulkan(...)` and `prepare_vulkan(...)` can execute the bounded
  RT-kernel triangle probe graph step
- graph inputs are now packed for Vulkan:
  - `rt.EdgeSet`
  - `rt.GraphCSR`
- native symbol added:
  - `rtdl_vulkan_run_triangle_probe(...)`
- candidate generation is currently implemented as a native host-indexed
  Vulkan helper over the graph CSR inputs, not as a disguised oracle fallback

## Verification

Focused graph triangle suite:

```text
python3 -m unittest \
  tests.goal390_v0_6_rt_graph_triangle_truth_path_test \
  tests.goal392_v0_6_rt_graph_triangle_oracle_test \
  tests.goal396_v0_6_rt_graph_triangle_embree_test \
  tests.goal397_v0_6_rt_graph_triangle_optix_test \
  tests.goal398_v0_6_rt_graph_triangle_vulkan_test
```

Result:

- `Ran 22 tests`
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

This Goal 398 implementation does not claim:

- release-grade GPU-validated graph traversal parity on this macOS machine
- large-scale graph benchmarking
- anything beyond the bounded RT-kernel triangle probe step

The current Vulkan triangle closure is:

- a real Vulkan backend ABI/runtime path
- bounded `triangle_count` graph support
- parity-tested at the API/runtime level
- locally skipped when Vulkan is unavailable
