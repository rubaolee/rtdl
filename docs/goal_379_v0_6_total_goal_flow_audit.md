# Goal 379: v0.6 total goal-flow audit

## Why this goal exists

The `v0.6` line has accumulated a long goal ladder. Before release, we need one
strict audit that checks whether the line is structurally sound as a process
artifact, not only as code and docs.

## Scope

In scope:

- audit the `v0.6` goals for flow correctness
- verify that major goals have:
  - bounded scope
  - saved review artifacts
  - saved Codex consensus
  - honest closure language
- identify missing or suspicious closure points

Out of scope:

- new implementation work
- release tagging

## Required audit targets

At minimum, this gate should cover the `v0.6` ladder from:

- Goal 337 through the current active release-prep goals

## Exit condition

This goal is complete when the repo has:

- a saved total goal-flow audit report
- at least one external review
- a saved Codex consensus note
- an honest verdict on whether the `v0.6` goal ladder is release-correct enough
