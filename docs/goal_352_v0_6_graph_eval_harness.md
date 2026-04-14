# Goal 352: v0.6 Graph Evaluation Harness

## Why this goal exists

The opening `v0.6` graph line now has:

- Python truth paths
- compiled CPU/native baselines
- bounded PostgreSQL baselines

It still needs one bounded runnable evaluation surface that compares those
layers coherently.

## Scope

In scope:

- bounded synthetic graph helpers
- bounded BFS/triangle-count evaluation helpers
- one Linux-oriented script that emits a comparison summary
- focused tests for the new helpers

Out of scope:

- live paper-dataset reproduction
- accelerated graph backends
- broad performance claims

## Exit condition

This goal is complete when the repo has:

- a working bounded graph evaluation harness
- focused tests
- a saved external review
- a saved Codex consensus note
