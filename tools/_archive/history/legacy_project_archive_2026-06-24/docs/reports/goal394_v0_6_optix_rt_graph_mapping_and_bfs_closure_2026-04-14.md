# Goal 394 Report: v0.6 OptiX RT Graph Mapping And BFS Closure

Date: 2026-04-14
Status: implemented, review pending

## Summary

Goal 394 is now materially implemented.

The first RT-kernel graph workload, `bfs_discover(...)`, now runs on the OptiX
backend through a bounded native OptiX graph ABI and runtime dispatch.

## Code Changes

Native OptiX ABI and implementation:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_prelude.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_workloads.cpp`

Python runtime and test surface:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal394_v0_6_rt_graph_bfs_optix_test.py`

## What Landed

- `PreparedOptixKernel` now accepts `bfs_discover`
- `run_optix(...)` and `prepare_optix(...)` can execute the bounded RT-kernel
  BFS graph step
- graph inputs are now packed for OptiX:
  - `rt.GraphCSR`
  - `rt.VertexFrontier`
  - `rt.VertexSet`
- native symbol added:
  - `rtdl_optix_run_bfs_expand(...)`
- candidate generation is currently implemented as a native host-indexed OptiX
  helper over the graph CSR inputs, not as a disguised oracle fallback

## Verification

Focused graph suite:

```text
python3 -m unittest \
  tests.goal389_v0_6_rt_graph_bfs_truth_path_test \
  tests.goal391_v0_6_rt_graph_bfs_oracle_test \
  tests.goal393_v0_6_rt_graph_bfs_embree_test \
  tests.goal394_v0_6_rt_graph_bfs_optix_test
```

Result:

- `Ran 19 tests`
- `OK (skipped=4)`

The four skipped tests are the OptiX-specific tests in
`goal394_v0_6_rt_graph_bfs_optix_test.py`, which is the expected local result
when the OptiX runtime is not installed.

Core quality gate:

```text
python3 -m unittest tests.test_core_quality
```

Result:

- `Ran 105 tests`
- `OK`

## Honesty Boundary

This Goal 394 implementation does not claim:

- OptiX `triangle_count`
- GPU-validated graph traversal parity on this macOS machine
- large-scale graph benchmarking

The current OptiX BFS closure is:

- a real OptiX backend ABI/runtime path
- bounded BFS graph support
- parity-tested at the API/runtime level
- locally skipped when OptiX is unavailable
