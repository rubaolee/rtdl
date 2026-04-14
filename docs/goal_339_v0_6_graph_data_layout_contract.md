# Goal 339: v0.6 Graph Data / Layout Contract

## Why this goal exists

The version boundary and workload charter are now set. The next dependency is
to define the graph data contract tightly enough that truth-path implementation
for `bfs` and `triangle_count` can begin without hidden ambiguity.

## Scope

In scope:

- define the initial graph representation for `v0.6`
- define what layout/materialization assumptions are allowed
- define what should remain application-owned versus RTDL-owned
- define the first implementation-critical contract details needed by:
  - `bfs`
  - `triangle_count`

Out of scope:

- implementing graph workloads
- claiming performance
- choosing every future graph encoding

## Exit condition

This goal is complete when the repo has:

- a saved graph data/layout contract report
- a saved external review
- a saved Codex consensus note

Then BFS and triangle-count truth-path work can start from an explicit contract.
