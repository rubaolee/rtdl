# Handoff: Goal 385 v0.6 RT Graph Version Plan Review

Date: 2026-04-14

## Context

The repository has undergone a public rollback of the earlier `v0.6` line. The new direction is to rebuild `v0.6` as a true **RTDL-kernel** graph release, ensuring that graph workloads are expressed and executed using the ray-tracing primitives fundamental to the RTDL project.

## Deliverable for Goal 385

The following review report formalizes the acceptance of the new `v0.6` RT Graph Version Plan.

- **Review Report**: [gemini_goal385_v0_6_rt_graph_version_plan_review_2026-04-14.md](file:///Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal385_v0_6_rt_graph_version_plan_review_2026-04-14.md)

## Next Steps

1.  **Goal 386**: Begin the design of the RTDL graph kernel surface. This involves defining how a user expresses a graph traversal (like BFS) using `rt.traverse`, `rt.refine`, and `rt.emit`.
2.  **Mapping**: Step 3 (Goal 387) will then define how graph data (Vertices/Edges) is mapped into the RT view (e.g. mapping edges to intersection primitives).

---
*Signed by Gemini Coding Assistant on 2026-04-14*
