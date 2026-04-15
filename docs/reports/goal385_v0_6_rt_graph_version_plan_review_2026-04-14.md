# Goal 385 Review: v0.6 RT Graph Version Plan

Date: 2026-04-14
Status: accepted

## Evidence Read

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_385_v0_6_rt_graph_version_plan.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal385_v0_6_rt_graph_version_plan_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal385_v0_6_rt_graph_version_plan_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/history/events/v0_6_public_rollback_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/future_ray_tracing_directions.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/rtdl/dsl_reference.md`

## Verdict

Goal 385 is accepted.

The version boundary is now technically coherent:

- `v0.6` is redefined as an RTDL-kernel graph line
- the initial workload pair remains:
  - `bfs`
  - `triangle_count`
- the paper-aligned RT execution model is treated as the defining contract
- backend work is correctly pushed downstream until the kernel and execution
  semantics exist

## Why This Closure Is Valid

The public rollback event established that the earlier `v0.6` line was honest
but mis-scoped. Goal 385 corrects that mistake without pretending the missing RT
graph pieces already exist.

Gemini independently reached the same conclusion and accepted the pivoted
direction.

## Next Dependency

The next correct goal is Goal 386:

- define the RT graph kernel surface users actually write

Without that, there is still no honest claim that RTDL can express the graph
workloads from the paper.
