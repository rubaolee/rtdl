# Goal 391 Review: v0.6 RT-Kernel BFS Oracle Truth Path

Date: 2026-04-14
Status: accepted

## Evidence Read

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_391_v0_6_rt_kernel_bfs_oracle_truth_path.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal391_v0_6_rt_kernel_bfs_oracle_truth_path_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal391_v0_6_rt_kernel_bfs_oracle_truth_path_review_2026-04-14.md`
- changed code:
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/oracle/rtdl_oracle_abi.h`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/oracle/rtdl_oracle_api.cpp`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/oracle_runtime.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/runtime.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal389_v0_6_rt_graph_bfs_truth_path_test.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal391_v0_6_rt_graph_bfs_oracle_test.py`

## Verdict

Goal 391 is accepted.

The corrected RT graph line now has its first bounded native/oracle execution
step:

- RT-kernel `bfs_discover(...)` works through `rt.run_cpu(...)`
- row parity against `rt.run_cpu_python_reference(...)` is proven on the
  bounded BFS step
- the graph boundary remains honest because `triangle_match(...)` is still
  blocked from the native path

## External Consensus

Gemini accepted the implementation and specifically confirmed:

- the C ABI is clean and consistent with the existing oracle style
- CSR/frontier/visited validation is robust
- deterministic row parity is preserved against the Python reference
- the triangle-count native boundary remains explicit

## Verification

- `python3 -m unittest tests.goal391_v0_6_rt_graph_bfs_oracle_test`
  - `Ran 4 tests`
  - `OK`
- `python3 -m unittest tests.goal389_v0_6_rt_graph_bfs_truth_path_test tests.goal390_v0_6_rt_graph_triangle_truth_path_test tests.goal391_v0_6_rt_graph_bfs_oracle_test`
  - `Ran 17 tests`
  - `OK`
- `python3 -m unittest tests.test_core_quality`
  - `Ran 105 tests`
  - `OK`

## Next Dependency

The next correct coding goal is Goal 392:

- RT-kernel `triangle_count` native/oracle truth-path closure
