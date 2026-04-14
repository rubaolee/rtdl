# Goal 351: v0.6 Triangle Count Oracle Implementation

## Why this goal exists

`v0.6` has a bounded triangle-count truth path in Python. The next code step is
the first compiled RTDL CPU/native implementation for that same contract.

## Scope

In scope:

- native/oracle CSR triangle-count implementation
- Python runtime wrapper for the native triangle-count path
- public export surface
- focused parity tests against the triangle-count truth path

Out of scope:

- generic graph DSL lowering
- accelerated graph backends
- performance claims

## Exit condition

This goal is complete when the repo has:

- a working native/oracle triangle-count implementation for CSR simple graphs
- focused parity tests
- a saved external review
- a saved Codex consensus note
