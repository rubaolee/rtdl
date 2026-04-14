# Goal 337 Report: v0.6 Graph Workloads Version Plan

Date: 2026-04-13

## Summary

This planning slice sets the intended `v0.6` direction after the `v0.5.0`
release. The version should move into graph applications that are explicitly
anchored by the SIGMETRICS 2025 graph case-study paper rather than starting a
new unbounded feature cycle.

The first two candidate `v0.6` workloads are:

- `bfs`
- `triangle_count`

## Evidence used

Primary external anchor:

- Rubao Lee homepage entry for:
  - *A Case Study for Ray Tracing Cores: Performance Insights with
    Breadth-First Search and Triangle Counting in Graphs*
  - SIGMETRICS 2025
  - DOI: `10.1145/3727108`
  - code link: `https://github.com/rubaolee/RT-Graph`

Primary in-repo anchor:

- [future_ray_tracing_directions.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/future_ray_tracing_directions.md)

That repo doc already positions the graph case-study paper as part of the
current research direction beyond spatial join and nearest-neighbor workloads.

## Decision

The next version should be:

- `v0.6`
- theme: graph applications motivated by ray-tracing-core research
- first bounded workloads:
  - breadth-first search
  - triangle counting

## Why this is the correct boundary

It is bounded enough to be defensible:

- two named workloads
- one named paper anchor
- one clear version shift after `v0.5.0`

It is also broad enough to matter:

- it moves RTDL beyond geometry and NN kernels
- it introduces graph-application semantics without pretending to solve all
  graph workloads at once

## Proposed v0.6 goal sequence

1. workload charter for graph applications
2. graph data and layout contract
3. BFS truth path
4. triangle-count truth path
5. first backend closure for BFS
6. first backend closure for triangle count
7. bounded Linux evaluation and paper-correlation review

## Explicit non-claims

This report does not claim:

- that RTDL already reproduces the SIGMETRICS 2025 paper
- that all graph algorithms are now in scope
- that Windows/macOS performance are required for the first `v0.6` slice
- that graph workloads should bypass the existing truth-path discipline

## Current recommendation

Proceed with `v0.6` as a bounded graph-workloads version anchored on:

- `bfs`
- `triangle_count`

Do not start implementation until the plan itself has external review and
Codex consensus saved.
