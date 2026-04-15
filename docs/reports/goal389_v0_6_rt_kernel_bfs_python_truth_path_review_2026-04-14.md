# Goal 389 Review: v0.6 RT-Kernel BFS Python Truth Path

Date: 2026-04-14
Status: accepted

## Evidence Read

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_389_v0_6_rt_kernel_bfs_python_truth_path.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal389_v0_6_rt_kernel_bfs_python_truth_path_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/claude_goal389_v0_6_rt_kernel_bfs_python_truth_path_review_2026-04-14.md`
- changed code:
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/layout_types.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/ir.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/api.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/graph_reference.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/runtime.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal389_v0_6_rt_graph_bfs_truth_path_test.py`

## Verdict

Goal 389 is accepted.

The repo now has a real bounded RTDL graph-kernel execution slice:

- logical graph input surface
- graph predicate surface for BFS expansion
- compile-time preservation of graph mode/predicate metadata
- executable Python truth-path BFS expansion step
- explicit `run_cpu` rejection so native/oracle absence is honest

## External Consensus

Claude accepted the implementation and called out one real issue:

- `run_cpu` needed a clear graph-kernel boundary error

That fix is now present and covered by the test suite.

## Verification

- `python3 -m unittest tests.goal389_v0_6_rt_graph_bfs_truth_path_test`
  - `Ran 7 tests`
  - `OK`
- `python3 -m unittest tests.goal263_v0_5_bounded_knn_rows_surface_test tests.test_core_quality`
  - `Ran 110 tests`
  - `OK`

## Next Dependency

The next correct coding goal is Goal 390:

- RT-kernel `triangle_count` Python truth-path closure
