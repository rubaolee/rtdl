# Goal 350: v0.6 BFS Oracle Implementation

## Why this goal exists

`v0.6` has a bounded BFS truth path in Python. The next code step is the first
compiled RTDL CPU/native implementation for that same contract.

## Scope

In scope:

- native/oracle CSR BFS implementation
- Python runtime wrapper for the native BFS path
- public export surface
- focused parity tests against the BFS truth path

Out of scope:

- generic graph DSL lowering
- accelerated graph backends
- performance claims

## Exit condition

This goal is complete when the repo has:

- a working native/oracle BFS implementation for CSR single-source BFS
- focused parity tests
- a saved external review
- a saved Codex consensus note
