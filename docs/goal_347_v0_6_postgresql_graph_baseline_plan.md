# Goal 347: v0.6 PostgreSQL Graph Baseline Plan

## Why this goal exists

The first `v0.6` graph truth paths now exist. The next question is whether
PostgreSQL should be part of the correctness and performance baseline story for
the opening graph workloads.

This goal answers that at the planning level before SQL implementation work
starts.

## Scope

In scope:

- define whether PostgreSQL is an honest baseline for:
  - `bfs`
  - `triangle_count`
- define how PostgreSQL should be positioned:
  - correctness baseline
  - bounded performance baseline
- define what PostgreSQL should explicitly **not** be claimed to be

Out of scope:

- implementing PostgreSQL queries
- claiming PostgreSQL performance leadership
- claiming paper-equivalent graph-engine behavior

## Exit condition

This goal is complete when the repo has:

- a saved PostgreSQL graph-baseline planning report
- a saved external review
- a saved Codex consensus note
