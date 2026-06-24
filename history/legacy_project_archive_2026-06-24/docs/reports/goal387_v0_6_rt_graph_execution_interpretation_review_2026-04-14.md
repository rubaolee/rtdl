# Goal 387 Review: v0.6 RT Graph Execution Interpretation

Date: 2026-04-14
Status: accepted

## Evidence Read

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_387_v0_6_rt_graph_execution_interpretation.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal387_v0_6_rt_graph_execution_interpretation_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal387_v0_6_rt_graph_execution_interpretation_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/claude_goal387_v0_6_rt_graph_execution_interpretation_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/future_ray_tracing_directions.md`

## Verdict

Goal 387 is accepted.

The design now states the execution meaning clearly enough to support the next
goal:

- logical CSR input remains the public graph contract
- runtime derives RT-searchable relation encoding plus acceleration structure
- RT traversal is the candidate-generation engine
- hits mean different graph candidates depending on workload mode:
  - `graph_expand`
  - `graph_intersect`
- host code owns outer BFS and batching loops
- kernel code owns bounded RT search steps plus refine/emit semantics

## External Consensus

Gemini approved the interpretation and confirmed it satisfies the required
mapping from Goal 386 kernel surface to an RT execution model.

Claude also accepted it after two targeted fixes:

- add paper-anchored wording for each workload mode
- make clear that `rt.bfs_discover(...)` and `rt.triangle_match(...)` are
  proposed public graph-surface predicates, not hidden aliases

Those fixes are now reflected in the report.

## Next Dependency

The next correct goal is Goal 388:

- graph lowering and runtime contract for the RT-kernel form

That goal must decide how the design surfaces from Goals 386 and 387 become a
real lowering/runtime boundary without collapsing back into detached graph
helpers.
