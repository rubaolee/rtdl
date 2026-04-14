# Goal 341: v0.6 Triangle Count Truth Path

## Why this goal exists

After BFS, the next bounded graph workload from the `v0.6` charter is:

- `triangle_count`

The next step is to define the first truth-path boundary clearly enough that
implementation can begin without ambiguity around graph assumptions or count
semantics.

## Scope

In scope:

- define the first bounded `triangle_count` truth-path surface
- specify the expected count semantics
- specify the graph assumptions needed for deterministic truth-path work

Out of scope:

- backend acceleration
- performance claims
- graph ingestion generalization

## Exit condition

This goal is complete when the repo has:

- a saved triangle-count truth-path report
- a saved external review
- a saved Codex consensus note
