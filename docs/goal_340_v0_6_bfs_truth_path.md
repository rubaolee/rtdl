# Goal 340: v0.6 BFS Truth Path

## Why this goal exists

Goals 337 through 339 established:

- the `v0.6` version boundary
- the first graph workload charter
- the initial graph data/layout contract

The next correct step is the first truth path:

- `bfs`

## Scope

In scope:

- define the first bounded `bfs` truth-path surface
- specify expected outputs and semantics
- define the first correctness target for CSR-based BFS

Out of scope:

- backend acceleration
- performance claims
- triangle-count implementation

## Exit condition

This goal is complete when the repo has:

- a saved BFS truth-path report
- a saved external review
- a saved Codex consensus note

Then the first `v0.6` implementation work can start from a stable BFS truth
contract.
