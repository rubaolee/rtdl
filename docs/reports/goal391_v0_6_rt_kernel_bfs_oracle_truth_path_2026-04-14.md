# Goal 391 Report: v0.6 RT-Kernel BFS Oracle Truth Path

Date: 2026-04-14
Status: implemented

## Summary

This goal extends the corrected RTDL graph line from Python-only BFS truth-path
execution to the first bounded native/oracle graph step.

The repo now supports:

- `rt.run_cpu(...)` for RT-kernel `bfs_discover(...)`
- bounded CSR/frontier/visited transfer through the native oracle ABI
- row-level parity against `rt.run_cpu_python_reference(...)`

The graph boundary remains explicit:

- BFS is now supported in the native/oracle path
- triangle-count graph kernels are still blocked from `rt.run_cpu(...)`

## Files Changed

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/oracle/rtdl_oracle_abi.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/oracle/rtdl_oracle_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/oracle_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal389_v0_6_rt_graph_bfs_truth_path_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal391_v0_6_rt_graph_bfs_oracle_test.py`

## Implemented Behavior

The new native/oracle behavior adds a narrow BFS expansion ABI:

- graph inputs:
  - CSR `row_offsets`
  - CSR `column_indices`
- probe inputs:
  - frontier `(vertex_id, level)` rows
  - visited vertex IDs
- output rows:
  - `src_vertex`
  - `dst_vertex`
  - `level`

The native path preserves the same bounded semantics as the Python reference:

- CSR validation
- frontier vertex validation
- visited filtering
- same-step dedupe
- deterministic sort by:
  - `level`
  - `dst_vertex`
  - `src_vertex`

## Verification

Focused new tests:

- `python3 -m unittest tests.goal391_v0_6_rt_graph_bfs_oracle_test`
  - `Ran 4 tests`
  - `OK`

Focused graph regression:

- `python3 -m unittest tests.goal389_v0_6_rt_graph_bfs_truth_path_test tests.goal390_v0_6_rt_graph_triangle_truth_path_test tests.goal391_v0_6_rt_graph_bfs_oracle_test`
  - `Ran 17 tests`
  - `OK`

Core quality:

- `python3 -m unittest tests.test_core_quality`
  - `Ran 105 tests`
  - `OK`

## Current Boundary

This is not yet:

- native/oracle RT-kernel `triangle_count`
- graph lowering
- Embree / OptiX / Vulkan graph execution

It is the first honest bounded native/oracle execution step for the corrected
RTDL graph-kernel line.
