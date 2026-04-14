# Goal 354: v0.6 Linux Live PostgreSQL Graph Baseline

## Why this goal exists

`v0.6` now has:

- Python truth paths
- compiled CPU/native graph baselines
- bounded PostgreSQL graph baseline code

The next bounded evaluation step is to prove that the PostgreSQL baseline runs
live on Linux and matches the bounded RTDL graph results on a real database.

## Scope

In scope:

- Linux live PostgreSQL validation for BFS and triangle count
- one bounded evaluation table
- documenting any SQL or runner issues found during the live pass

Out of scope:

- large-scale graph benchmarking
- paper-reproduction claims
- accelerated graph backends

## Exit condition

This goal is complete when the repo has:

- a saved Linux live PostgreSQL graph-baseline report
- a saved external review
- a saved Codex consensus note
