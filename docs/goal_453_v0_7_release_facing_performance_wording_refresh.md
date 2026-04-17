# Goal 453: v0.7 Release-Facing Performance Wording Refresh

Date: 2026-04-16

## Purpose

Refresh public and release-facing v0.7 DB performance wording after Goal 452.

Goal 452 changed the canonical performance comparison from the original
single-column indexed PostgreSQL baseline to the best PostgreSQL modes tested in
Goal 451. The docs must now separate query-only and total-time claims.

## Scope

- README front-page wording.
- DB workload feature page.
- DB workload tutorial.
- v0.7 release statement.
- v0.7 support matrix.
- v0.7 audit report.
- v0.7 tag-preparation note.

## Acceptance Criteria

- Goal 452 is cited as the canonical performance comparison.
- Goal 450 is preserved as historical indexed-baseline evidence.
- Query-only results are described as mixed.
- Total setup-plus-10-query results are described as favoring RTDL in the
  measured Linux evidence.
- No doc claims exhaustive PostgreSQL tuning, arbitrary SQL, or DBMS behavior.
