# Goal 458: v0.7 Pre-Stage Validation Gate

Date: 2026-04-16

## Purpose

Validate the intended v0.7 DB staging set before any staging command is run.

## Scope

Generate a stage-plan artifact from the current worktree and verify:

- include candidates are source, tests, scripts, release-facing docs, goal docs,
  handoffs, reports, or consensus history
- `rtdsl_current.tar.gz` is excluded by default
- the three Goal 457 v0.6 audit-history files are deferred by default
- closed goals from 432-438 and 440-457 have required evidence
- Goal 439 is represented as an open external-tester intake gate, not a closed
  goal

## Non-Goals

- Do not stage files.
- Do not commit files.
- Do not tag, push, merge, or release.

## Acceptance Criteria

- A script writes a JSON stage plan and a Markdown report.
- The stage plan records include, defer, and exclude lists.
- The stage plan validates closed-goal evidence coverage.
- The stage plan preserves the no-stage/no-release boundary.
- Goal 458 receives 2-AI consensus before closure.
