# AI Checker Review: Goals 415-416 RT DB Execution And Lowering

Date: 2026-04-15
Reviewer: independent AI checker
Inputs:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_415_v0_7_rt_db_execution_interpretation.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal415_v0_7_rt_db_execution_interpretation_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_416_v0_7_rt_db_lowering_runtime_contract.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal416_v0_7_rt_db_lowering_runtime_contract_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal412_rt_db_workload_analysis_for_next_version_2026-04-15.md`

## Verdict

Mostly sound after patching.

## Main findings

- Goal 415 is honest about the current non-RT engines.
- Goal 416 is a bounded RT lowering direction that stays aligned with the
  RTScan/RayDB candidate-discovery model.
- The earlier ambiguity around “bounded” needed operational ceilings; that is
  now corrected with explicit limits on:
  - rows per RT job
  - candidate rows per RT job
  - grouped-job cardinality
- `grouped_sum` needed exact numeric semantics for later cross-backend parity;
  that is now corrected by limiting first-wave parity to exact integer sums.

## Residual note

- The remaining risk is implementation difficulty, not conceptual honesty.
  Backend work must preserve the stated fallback/decomposition behavior instead
  of silently widening the contract later.

## Recommendation

Accept Goals 415 and 416 as the bounded design basis for Embree-first DB
backend work.
