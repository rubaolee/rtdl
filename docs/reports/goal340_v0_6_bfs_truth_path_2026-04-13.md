# Goal 340 Report: v0.6 BFS Truth Path

Date: 2026-04-13

## Summary

This slice defines the intended opening truth-path contract for `bfs` in
`v0.6`.

## Input assumptions

- graph layout:
  - CSR
- vertex IDs:
  - `uint32_t`
- graph type:
  - simple graph
- frontier input:
  - materialized list of source vertex IDs

## Initial BFS truth semantics

The opening truth path should prioritize determinism and explicitness over
performance.

Recommended initial outputs:

- visited vertex IDs
- BFS level / depth per visited vertex

Recommended opening boundary:

- single-source BFS first
- multi-source BFS later if needed

Determinism rule:

- visited rows should be emitted ordered by:
  - BFS level ascending
  - vertex ID ascending within each level

Invalid-source rule:

- if the source vertex ID is out of bounds, the truth path should raise a
  contract error rather than silently returning an empty traversal

## Why this is the right first truth path

It is small enough to verify carefully and broad enough to support the graph
direction of `v0.6`.

It also fits the existing RTDL discipline:

- truth path first
- backend claims later

## Recommendation

Proceed with a single-source CSR BFS truth path as the first `v0.6`
implementation workload.
