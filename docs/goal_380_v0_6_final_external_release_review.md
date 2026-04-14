# Goal 380: v0.6 final external release review

## Why this goal exists

Goals `377-379` closed the internal pre-release ladder:
- total code review and test
- total doc review and verification
- total goal-flow audit

That is enough to move into the actual release-decision chain. Before `v0.6.0`
is made, the prepared release package should receive one final bounded external
review as a release-facing artifact rather than as an implementation-side goal.

## Scope

In scope:

- review the prepared `v0.6` release package as a release-facing surface
- check the front door, docs index, release statement, support matrix, audit
  report, and tag-preparation note
- confirm the package is coherent and honestly bounded for `v0.6.0`
- identify any remaining release-blocking defects

Out of scope:

- new graph implementation work
- new dataset bring-up
- broad repo cleanup unrelated to the `v0.6` release surface

## Exit condition

This goal is complete when the repo has:

- a saved external release-review artifact
- a saved internal review note
- a saved Codex consensus note
- an honest verdict on whether the current `v0.6` package is ready to move into
  final release decision and tag-making
