# Goal 353: v0.6 Code Review and Test Gate

## Why this goal exists

The bounded opening `v0.6` graph line now has real code:

- graph truth paths
- PostgreSQL graph baselines
- compiled CPU/native graph baselines
- bounded graph evaluation helpers

Before any broader `v0.6` publish or implementation expansion, this code slice
needs an explicit review-and-test gate.

## Scope

In scope:

- code review of the opening `v0.6` graph code surface
- test review of the focused graph tests and their coverage value
- audit of whether the bounded code-development slice is structurally coherent
- first external review leg via Gemini
- second external review leg via Claude later when available

Out of scope:

- new feature work
- accelerated graph backend implementation
- release packaging

## Exit condition

This goal is complete when the repo has:

- a saved Gemini code-review/test-gate report
- a saved Claude code-review/test-gate report
- a saved Codex consensus note
- an honest verdict on whether the bounded opening `v0.6` code-development
  slice is ready to move from implementation to evaluation/review
