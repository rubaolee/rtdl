# Codex Review: Goal 413 v0.7 RT DB Workload Scope And Goal Ladder

Date: 2026-04-15
Goal:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_413_v0_7_rt_db_workload_scope_and_goal_ladder.md`

Artifacts reviewed:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/history/goals/v0_7_goal_sequence_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal413_v0_7_rt_db_workload_scope_and_goal_ladder_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal412_rt_db_workload_analysis_for_next_version_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal413_v0_7_rt_db_workload_scope_and_goal_ladder_review_2026-04-15.md`

## Verdict

Accept.

## Reasoning

The version boundary is correct.

`v0.6.1` is already a released and coherent graph-workload line. The accepted
database-style direction changes the workload family enough that it should open
as a new bounded line rather than a patch or silent continuation.

The planning scope is also correctly bounded:

- denormalized analytical data
- scan/filter kernels
- grouped aggregate kernels
- offline/amortized encoding and BVH build

And the rejected scope is explicit enough to keep the line honest:

- no DBMS claim
- no online joins as first-class RT workloads
- no transactions / OLTP
- no arbitrary relational operator closure

The first kernel family is appropriately narrow:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

That is a realistic opening implementation slice rather than a speculative
kitchen-sink surface.

The ladder is ordered correctly from semantics to truth path to external
evidence and public exposure.

## Closure judgment

Goal 413 is complete and can close as the planning anchor for the `v0.7` line.
