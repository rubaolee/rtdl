# Goal 385: v0.6 RT Graph Version Plan

## Objective

Define the corrected `v0.6` line as an RTDL-kernel graph release aligned with
the SIGMETRICS 2025 graph paper, rather than as a standalone graph-runtime
extension.

## Why This Goal Exists

The previous `v0.6` line proved bounded graph workloads and supporting
baselines, but it did not satisfy the intended product direction:

- users must be able to write RTDL kernels for the graph workloads
- graph execution must follow the ray-tracing-style approach from the paper
- Embree, OptiX, and Vulkan must be treated as high-performance RT backend
  targets for that same RTDL-kernel model

The public rollback event already records that the earlier public `v0.6` line
did not meet that bar.

## Required Outcome

This goal is complete only when the repo contains a version plan that makes the
next `v0.6` line explicit:

- `v0.6` is an RTDL-kernel graph line
- initial workloads remain:
  - `bfs`
  - `triangle_count`
- the execution model is the paper-aligned RT approach
- the next dependency is a graph kernel-surface design, not backend closure
- high-performance backends are downstream realizations, not the starting
  definition of the version

## Honesty Boundary

This goal does not claim any of the following are implemented yet:

- RTDL graph kernels
- RT graph lowering
- Embree graph execution
- OptiX graph execution
- Vulkan graph execution

It only defines the correct version boundary and the next design ladder.

## Required Deliverables

- a version-plan report in `docs/reports/`
- a Gemini review handoff and response file
- a Codex closure note after reading the Gemini review
- an internal `v0.6` goal-sequence record that starts from this corrected
  direction
