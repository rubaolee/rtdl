# Goal 338 Report: v0.6 Graph Workload Charter

Date: 2026-04-13

## Summary

This charter defines the first bounded graph workloads for `v0.6`:

- `bfs`
- `triangle_count`

These workloads are selected because they are explicitly named by the
SIGMETRICS 2025 graph case-study paper and together form a reasonable opening
application slice for RTDL beyond nearest-neighbor and geometry kernels.

## Workload intent

### `bfs`

Intent:

- express frontier-based breadth-first traversal over graph data

Initial truth-path expectations:

- deterministic traversal results for a fixed source set and graph encoding
- row/output semantics should be defined clearly before backend claims

### `triangle_count`

Intent:

- express graph-local triangle counting over a bounded graph representation

Initial truth-path expectations:

- deterministic count semantics
- explicit handling of duplicate counting conventions before backend claims

## Language/runtime boundary

The initial `v0.6` graph slice should still follow the RTDL positioning:

- RTDL remains a language/runtime core
- graph applications are bounded workloads built on that core
- Python can still own surrounding application logic and orchestration

This charter does **not** claim:

- a general graph DSL
- all graph algorithms
- full paper reproduction

## Platform boundary

- Linux:
  - first performance platform
- Windows:
  - correctness-first
- macOS:
  - correctness-first

## Backend boundary

The first implementation sequence should keep the same discipline used in
`v0.5`:

1. truth path
2. first bounded native/runtime path
3. accelerated backend path
4. bounded performance review

## Recommendation

Accept this charter as the starting point for the first implementation goals in
`v0.6`.
