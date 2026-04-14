# Goal 348: v0.6 PostgreSQL BFS Baseline Implementation

## Why this goal exists

The PostgreSQL graph-baseline plan is closed. The next step is to implement the
first PostgreSQL graph baseline:

- BFS

## Scope

In scope:

- add PostgreSQL SQL builder for bounded BFS
- add temp-table prep and query helpers
- add focused tests with a fake PostgreSQL connection

Out of scope:

- live database benchmarking
- backend acceleration
- triangle-count PostgreSQL baseline

## Exit condition

This goal is complete when the repo has:

- PostgreSQL BFS baseline code
- focused tests
- a saved external review
- a saved Codex consensus note
