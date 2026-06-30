# Goal 385 Report: v0.6 RT Graph Version Plan

Date: 2026-04-14
Status: drafted

## Summary

The corrected `v0.6` line is defined as an RTDL-kernel graph release aligned
with the SIGMETRICS 2025 graph paper.

This means:

- graph workloads are not a detached runtime add-on
- users must be able to express the graph workloads through RTDL kernels
- the graph execution model must be the ray-tracing-style approach described by
  the paper
- Embree, OptiX, and Vulkan are high-performance backend targets for that same
  RTDL-kernel model

## Why The Earlier Direction Was Wrong

The rolled-back public `v0.6` line was bounded and honest as a workload/runtime
slice, but it did not meet the intended RTDL-product direction:

- it provided graph truth paths and runtime surfaces
- it did not provide RTDL-kernel graph authoring
- it did not define graph lowering through the RTDL kernel model
- it therefore could not honestly claim paper-aligned RT graph execution

That mismatch is already recorded in the public rollback event:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/history/events/v0_6_public_rollback_2026-04-14.md`

## Corrected Version Boundary

The corrected `v0.6` version boundary is:

- initial workloads:
  - `bfs`
  - `triangle_count`
- authoring model:
  - RTDL kernels
- execution model:
  - ray-tracing-style graph traversal/refinement derived from the SIGMETRICS
    2025 direction
- correctness anchors:
  - bounded Python reference
  - bounded oracle/native reference
  - PostgreSQL supporting baseline
- performance targets:
  - Embree
  - OptiX
  - Vulkan

## Required Goal Ladder

The corrected next ladder is:

1. version plan
2. graph kernel-surface design
3. RT graph execution interpretation
4. graph lowering/runtime contract
5. bounded Python/oracle truth-path closure for the RT-kernel form
6. backend-specific RT graph mapping and closure
7. release review/test/doc/audit gates

## Current Verdict

This version plan is the correct restart point for `v0.6` work after the
public rollback to `v0.5`.
