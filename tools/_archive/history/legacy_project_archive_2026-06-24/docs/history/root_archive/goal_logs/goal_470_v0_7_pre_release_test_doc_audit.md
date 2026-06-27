# Goal 470: v0.7 Pre-Release Full Test, Doc Refresh, And Audit

Date opened: 2026-04-16

## Purpose

Create a current pre-release checkpoint for the bounded `v0.7` DB line after
Goal 469.

This goal covers the recurring version requirements:

- full test evidence
- release-facing documentation refresh
- pre-release audit evidence

## Scope

In scope:

- run full local unittest discovery
- fix release-blocking local harness failures surfaced by full discovery
- run focused Linux v0.7 DB/PostgreSQL/native backend validation from a synced
  current worktree
- refresh release-facing v0.7 reports through Goal 470
- mechanically validate the release-facing doc/audit package
- keep no-stage/no-tag/no-merge status

Out of scope:

- staging or committing
- tagging or releasing
- merging to main
- claiming a new RT-core performance result from the GTX 1070 Linux host

## Acceptance Bar

- local full unittest discovery passes
- Linux focused v0.7 DB/PostgreSQL/native validation passes
- release-facing docs mention the current Goal 469/470 state and keep the DBMS
  and release-hold boundaries explicit
- mechanical doc/audit script reports `valid: true`
- external AI review is requested; closure is pending if Claude/Gemini are
  unavailable before the user's review window
