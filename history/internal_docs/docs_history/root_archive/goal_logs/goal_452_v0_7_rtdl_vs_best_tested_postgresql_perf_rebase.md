# Goal 452: v0.7 RTDL vs Best-Tested PostgreSQL Performance Rebase

Date: 2026-04-16

## Purpose

Rebase v0.7 DB performance comparisons from the Goal 450 single-column indexed
PostgreSQL baseline to the best PostgreSQL index mode tested in Goal 451.

## Scope

- Use existing Linux evidence from:
  - Goal 450 RTDL columnar repeated-query gate.
  - Goal 451 PostgreSQL no-index/single-column/composite/covering audit.
- Compare:
  - RTDL median query time versus PostgreSQL best tested median query time.
  - RTDL prepare-plus-10-query total versus PostgreSQL best tested setup-plus-10-query total.
- Preserve correctness by requiring matching workload row hashes between Goal
  450 and Goal 451.

## Non-Goals

- No new Linux benchmark run unless evidence compatibility fails.
- No arbitrary SQL claim.
- No DBMS claim.
- No release authorization.
- No staging, commit, tag, push, or merge.
