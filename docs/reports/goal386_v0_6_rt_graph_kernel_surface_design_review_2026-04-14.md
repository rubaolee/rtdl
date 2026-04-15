# Goal 386 Review: v0.6 RT Graph Kernel Surface Design

Date: 2026-04-14
Status: accepted

## Evidence Read

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_386_v0_6_rt_graph_kernel_surface_design.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal386_v0_6_rt_graph_kernel_surface_design_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal386_v0_6_rt_graph_kernel_surface_design_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/claude_goal386_v0_6_rt_graph_kernel_surface_design_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/rtdl/dsl_reference.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/future_ray_tracing_directions.md`

## Verdict

Goal 386 is accepted.

The design now says the critical technical things explicitly:

- the host owns BFS level iteration and triangle-count batching/reduction
- the RTDL kernel owns one bounded RT search/expand step
- logical graph input remains CSR
- RT encoding and BVH construction are internal execution concerns
- graph work stays inside `input -> traverse -> refine -> emit`

## External Consensus

Gemini accepted the goal as the correct next dependency for a paper-aligned
RTDL graph line.

Claude also accepted it and called out one useful forward note:

- the inherited `precision=\"float_approx\"` decorator value is geometry-oriented
  and should be revisited during the graph lowering goal

That note is valid, but it does not block closure of the design itself.

## Next Dependency

The next correct goal is the RT graph execution interpretation:

- how CSR-backed graph data is encoded into an RT-searchable structure
- how `traverse` actually realizes RT-based neighbor visiting or relation
  search
- how the paper's BFS and triangle-count methods map onto RTDL execution terms
