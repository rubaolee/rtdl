# Goal 355: v0.6 Bounded Linux Graph Evaluation

## Why this goal exists

The bounded opening `v0.6` graph line now has:

- Python truth paths
- compiled CPU/native graph baselines
- bounded PostgreSQL graph baselines
- a live Linux PostgreSQL baseline result

The next step is to capture one bounded Linux evaluation slice cleanly.

## Scope

In scope:

- one bounded Linux evaluation table for:
  - `bfs`
  - `triangle_count`
- compare:
  - Python truth path
  - compiled CPU/native oracle
  - PostgreSQL baseline
- preserve the current graph-family restrictions honestly

Out of scope:

- accelerated graph backends
- large-scale graph benchmarks
- paper-reproduction claims

## Exit condition

This goal is complete when the repo has:

- a saved bounded Linux graph-evaluation report
- a saved external review
- a saved Codex consensus note
