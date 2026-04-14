# Goal 349: v0.6 PostgreSQL Triangle Count Baseline Implementation

## Why this goal exists

After the PostgreSQL BFS baseline, the next external graph baseline is:

- triangle count

## Scope

In scope:

- add PostgreSQL SQL builder for bounded triangle count
- add temp-table prep reuse for graph edges
- add focused tests with a fake PostgreSQL connection

Out of scope:

- live database benchmarking
- backend acceleration
- broader graph-database claims

## Exit condition

This goal is complete when the repo has:

- PostgreSQL triangle-count baseline code
- focused tests
- a saved external review
- a saved Codex consensus note
