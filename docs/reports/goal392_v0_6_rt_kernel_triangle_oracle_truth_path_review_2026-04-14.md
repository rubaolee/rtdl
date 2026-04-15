# Goal 392 Review: v0.6 RT-Kernel Triangle Oracle Truth Path

Date: 2026-04-14
Status: accepted

## Evidence Read

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_392_v0_6_rt_kernel_triangle_oracle_truth_path.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal392_v0_6_rt_kernel_triangle_oracle_truth_path_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal392_v0_6_rt_kernel_triangle_oracle_truth_path_review_2026-04-14.md`
- changed code:
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/oracle/rtdl_oracle_abi.h`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/oracle/rtdl_oracle_api.cpp`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/oracle_runtime.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/runtime.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal390_v0_6_rt_graph_triangle_truth_path_test.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal391_v0_6_rt_graph_bfs_oracle_test.py`
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal392_v0_6_rt_graph_triangle_oracle_test.py`

## Verdict

Goal 392 is accepted.

The corrected RT graph line now has bounded native/oracle truth-path closure
for both opening graph workloads:

- RT-kernel `bfs_discover(...)`
- RT-kernel `triangle_match(...)`

This keeps the current branch honest and materially stronger before any
backend-specific Embree / OptiX / Vulkan work begins.

## External Consensus

Gemini approved the implementation and confirmed:

- the triangle native/oracle ABI is coherent
- CSR and seed validation are correct
- the bounded `u < v < w` contract is preserved
- parity against the Python reference is explicitly tested and achieved

## Verification

- `python3 -m unittest tests.goal392_v0_6_rt_graph_triangle_oracle_test`
  - `Ran 4 tests`
  - `OK`
- `python3 -m unittest tests.goal389_v0_6_rt_graph_bfs_truth_path_test tests.goal390_v0_6_rt_graph_triangle_truth_path_test tests.goal391_v0_6_rt_graph_bfs_oracle_test tests.goal392_v0_6_rt_graph_triangle_oracle_test`
  - `Ran 21 tests`
  - `OK`
- `python3 -m unittest tests.test_core_quality`
  - `Ran 105 tests`
  - `OK`

## Next Dependency

The next correct goal is Goal 393:

- Embree RT graph mapping and first workload closure
