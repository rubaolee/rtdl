# Goal 459: v0.7 Dry-Run Staging Command Plan

Date: 2026-04-16

## Purpose

Generate an exact, reproducible dry-run staging command plan from the accepted
Goal 458 pre-stage validation gate.

## Scope

The plan must:

- use the Goal 458 include/defer/exclude decisions
- produce grouped `git add --` command lists
- keep `rtdsl_current.tar.gz` excluded by default
- keep the three Goal 457 v0.6 audit-history files deferred by default
- perform no staging

## Non-Goals

- Do not run `git add`.
- Do not commit.
- Do not tag, push, merge, or release.

## Acceptance Criteria

- A script writes a JSON dry-run command plan.
- A Markdown report summarizes the command groups.
- The command plan has zero overlap between include, defer, and exclude sets.
- The command plan records `staging_performed=false`.
- Goal 459 receives 2-AI consensus before closure.
