# Goal 374: v0.6 cit-Patents split-bound scale plan

## Why this goal exists

The `cit-Patents` line now has:

- first bounded Linux BFS result
- first bounded Linux triangle-count probe

The next bounded step is to decide how to scale the two workloads without
pretending they should advance at the same rate.

## Scope

In scope:

- use existing Linux measurements to choose the next bounded `cit-Patents`
  scale step
- define separate next bounds for:
  - `bfs`
  - `triangle_count`
- keep the decision honest and evidence-driven

Out of scope:

- running the next larger `cit-Patents` evaluations
- changing workload semantics
- adding new baselines or backends

## Exit condition

This goal is complete when the repo has:

- a saved scale-decision report
- a saved external review
- a saved Codex consensus note
