# Windows Codex Handoff: Corrected RT v0.6 Continuation

Start by updating from Git, then verify that you are actually on the corrected
RT graph line before doing any new work.

## Required first steps

1. Fetch the latest Git state from origin.
2. Check whether the corrected RT branch/commit you need is actually present.
3. If the corrected RT branch is not present from Git, stop and report that
   you need the latest staged bundle/worktree snapshot instead of continuing
   from an older public branch.

Do **not** silently continue from the rolled-back public `v0.5` line.

## Current project intent

You are continuing the corrected RT `v0.6` graph line, not the older rolled-back
standalone graph-runtime line.

Target model:

- RTDL kernels express the graph workloads
- execution follows the SIGMETRICS 2025 RT graph approach
- correctness anchor is:
  - CPU/oracle truth
  - PostgreSQL external truth
- high-performance backends are:
  - Embree
  - OptiX
  - Vulkan

## Current correctness/performance state

Known current report:

- `docs/reports/v0_6_rt_graph_correctness_and_performance_report_2026-04-14.md`

Most important current finding:

- `bfs` large-batch parity is clean:
  - Windows Embree matches Linux PostgreSQL exactly
- `triangle_count` large-batch parity is **not** clean:
  - Windows CPU truth matches Linux PostgreSQL
  - Windows Embree matches Linux Embree
  - therefore the bug is in the Embree triangle path itself

## Immediate next goal

Open and continue the next goal as:

- large-batch Embree triangle correctness regression

Required work:

1. Reproduce the large-batch triangle mismatch on the corrected RT branch.
2. Localize the missing/incorrect rows in the Embree triangle path.
3. Fix the Embree triangle implementation.
4. Re-run parity against:
   - Windows CPU/oracle truth
   - Linux PostgreSQL truth
5. Save results back into the repo as a bounded goal/report/review chain.

## Likely fix surfaces

Inspect first:

- `src/native/embree/rtdl_embree_api.cpp`
- `src/native/embree/rtdl_embree_scene.cpp`
- `src/rtdsl/embree_runtime.py`

## Important operating rule

If Git does not contain the corrected RT branch state you need, stop and say so.
Do not continue from an older public branch just because it is available.
Do not commit or push from Windows yet. Finish the current version work first,
then make a deliberate Git decision.
