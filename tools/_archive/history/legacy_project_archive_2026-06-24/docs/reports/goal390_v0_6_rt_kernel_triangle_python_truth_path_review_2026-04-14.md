# Goal 390 Review: v0.6 RT-Kernel Triangle Count Python Truth Path

Date: 2026-04-14
Status: accepted

## Evidence Read

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_390_v0_6_rt_kernel_triangle_python_truth_path.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal390_v0_6_rt_kernel_triangle_python_truth_path_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/claude_goal390_v0_6_rt_kernel_triangle_python_truth_path_review_2026-04-14.md`
- changed code:
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/graph_reference.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/runtime.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal390_v0_6_rt_graph_triangle_truth_path_test.py`

## Verdict

Goal 390 is accepted.

The repo now has the second executable bounded RTDL graph-kernel slice:

- logical seed-edge input surface
- graph predicate surface for triangle relation matching
- compile-time preservation of graph-intersect mode/predicate metadata
- executable Python truth-path triangle probe step
- explicit `run_cpu` rejection so native/oracle absence remains honest

## External Consensus

Claude accepted the implementation and did not find a blocking issue.

The only residual note is mild type-coherence debt in `_normalize_records`
because graph inputs return different normalized shapes than record-sequence
inputs. That does not block this bounded slice.

## Verification

- `python3 -m unittest tests.goal390_v0_6_rt_graph_triangle_truth_path_test`
  - `Ran 6 tests`
  - `OK`
- `python3 -m unittest tests.goal389_v0_6_rt_graph_bfs_truth_path_test tests.goal263_v0_5_bounded_knn_rows_surface_test tests.test_core_quality`
  - `Ran 117 tests`
  - `OK`

## Next Dependency

The corrected `v0.6` line now has bounded Python truth-path closure for both:

- RT-kernel `bfs`
- RT-kernel `triangle_count`

The next meaningful step is no longer Python truth design. It is the first
implementation-side move beyond Python truth, likely the first backend-mapping
or native/oracle graph-step closure goal.
