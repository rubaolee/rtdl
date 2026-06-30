# Goal 392 Report: v0.6 RT-Kernel Triangle Oracle Truth Path

Date: 2026-04-14
Status: implemented

## Summary

This goal completes the bounded native/oracle truth-path pair for the corrected
RTDL graph line:

- RT-kernel `bfs_discover(...)` now works through `rt.run_cpu(...)`
- RT-kernel `triangle_match(...)` now also works through `rt.run_cpu(...)`

The new native/oracle path supports bounded triangle probing with:

- CSR validation
- seed-edge validation
- `order="id_ascending"` enforcement
- `unique=True` triangle dedupe
- row parity against the Python truth-path step

## Files Changed

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/oracle/rtdl_oracle_abi.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/oracle/rtdl_oracle_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/oracle_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal390_v0_6_rt_graph_triangle_truth_path_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal391_v0_6_rt_graph_bfs_oracle_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal392_v0_6_rt_graph_triangle_oracle_test.py`

## Implemented Behavior

The native/oracle triangle ABI adds:

- graph inputs:
  - CSR `row_offsets`
  - CSR `column_indices`
- probe inputs:
  - seed edges `(u, v)`
- options:
  - ascending-order enforcement
  - uniqueness enforcement
- output rows:
  - `u`
  - `v`
  - `w`

The oracle implementation matches the Python truth-path semantics:

- reject invalid seed vertices
- skip self-edges
- enforce `u < v < w` for the current bounded contract
- dedupe repeated seed-derived triangles when `unique=True`

## Verification

Focused new tests:

- `python3 -m unittest tests.goal392_v0_6_rt_graph_triangle_oracle_test`
  - `Ran 4 tests`
  - `OK`

Focused graph regression:

- `python3 -m unittest tests.goal389_v0_6_rt_graph_bfs_truth_path_test tests.goal390_v0_6_rt_graph_triangle_truth_path_test tests.goal391_v0_6_rt_graph_bfs_oracle_test tests.goal392_v0_6_rt_graph_triangle_oracle_test`
  - `Ran 21 tests`
  - `OK`

Core quality:

- `python3 -m unittest tests.test_core_quality`
  - `Ran 105 tests`
  - `OK`

## Current Boundary

This is not yet:

- graph lowering
- Embree / OptiX / Vulkan graph execution
- large-scale RT backend validation

It is the bounded native/oracle triangle-step closure for the corrected RTDL
graph-kernel line.
