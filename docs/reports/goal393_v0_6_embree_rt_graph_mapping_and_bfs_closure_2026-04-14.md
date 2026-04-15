# Goal 393 Report: v0.6 Embree RT Graph Mapping And BFS Closure

Date: 2026-04-14
Status: implemented

## Summary

This goal brings the first RTDL graph workload onto the Embree backend:

- RT-kernel `bfs_discover(...)` now runs through `rt.run_embree(...)`
- candidate generation is Embree-specific
- row parity is preserved against both Python and native/oracle bounded truth
  paths

## Files Changed

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_scene.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/embree_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal393_v0_6_rt_graph_bfs_embree_test.py`

## Implemented Behavior

The bounded Embree mapping used here is:

- each outgoing graph edge is represented as an Embree point-query primitive
  keyed by its source vertex
- each frontier vertex issues an Embree point query at that source-vertex
  coordinate
- the Embree point-query callback materializes candidate neighbor rows
- visited filtering and same-step dedupe happen inside the Embree callback state

This is intentionally narrow, but it is genuinely Embree-specific candidate
generation rather than a relabeled CPU fallback.

The new public surface supports:

- `rt.run_embree(...)` for RT-kernel BFS
- `rt.prepare_embree(...)` for RT-kernel BFS

## Verification

Focused Embree graph tests:

- `python3 -m unittest tests.goal393_v0_6_rt_graph_bfs_embree_test`
  - `Ran 4 tests`
  - `OK`

Focused BFS regression:

- `python3 -m unittest tests.goal393_v0_6_rt_graph_bfs_embree_test tests.goal389_v0_6_rt_graph_bfs_truth_path_test tests.goal391_v0_6_rt_graph_bfs_oracle_test`
  - `Ran 15 tests`
  - `OK`

Core quality:

- `python3 -m unittest tests.test_core_quality`
  - `Ran 105 tests`
  - `OK`

## Current Boundary

This is not yet:

- Embree `triangle_count`
- graph lowering
- OptiX graph support
- Vulkan graph support

It is the first honest bounded Embree graph workload closure for the corrected
RTDL graph line.
