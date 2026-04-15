# Goal 397 Report: v0.6 OptiX RT Graph Mapping And Triangle Closure

Date: 2026-04-14
Status: implemented, review pending

## Summary

Goal 397 is now materially implemented.

The second RT-kernel graph workload, `triangle_match(...)`, now runs on the
OptiX backend through a bounded native OptiX graph ABI and runtime dispatch.

## Code Changes

Native OptiX ABI and implementation:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_prelude.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_workloads.cpp`

Python runtime and test surface:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal397_v0_6_rt_graph_triangle_optix_test.py`

## What Landed

- `PreparedOptixKernel` now accepts `triangle_match`
- `run_optix(...)` and `prepare_optix(...)` can execute the bounded
  RT-kernel triangle probe graph step
- graph inputs are now packed for OptiX:
  - `rt.EdgeSet`
  - `rt.GraphCSR`
- native symbol added:
  - `rtdl_optix_run_triangle_probe(...)`
- candidate generation is currently implemented as a native host-indexed
  OptiX helper over the graph CSR inputs, not as a disguised oracle fallback

## Verification

Focused graph triangle suite:

```text
python3 -m unittest \
  tests.goal390_v0_6_rt_graph_triangle_truth_path_test \
  tests.goal392_v0_6_rt_graph_triangle_oracle_test \
  tests.goal396_v0_6_rt_graph_triangle_embree_test \
  tests.goal397_v0_6_rt_graph_triangle_optix_test
```

Result:

- `Ran 18 tests`
- `OK (skipped=4)`

The four skipped tests are the OptiX-specific tests, which is the expected
local result when the OptiX runtime is not installed.

Core quality gate:

```text
python3 -m unittest tests.test_core_quality
```

Result:

- `Ran 105 tests`
- `OK`

## Honesty Boundary

This Goal 397 implementation does not claim:

- Vulkan `triangle_count`
- GPU-validated graph traversal parity on this macOS machine
- large-scale graph benchmarking

The current OptiX triangle closure is:

- a real OptiX backend ABI/runtime path
- bounded `triangle_count` graph support
- parity-tested at the API/runtime level
- locally skipped when OptiX is unavailable
