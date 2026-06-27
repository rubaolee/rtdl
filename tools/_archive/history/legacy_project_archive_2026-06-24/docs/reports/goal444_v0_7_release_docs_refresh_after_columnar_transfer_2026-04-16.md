# Goal 444: v0.7 Release Docs Refresh After Columnar Transfer

Date: 2026-04-16

## Verdict

Goal 444 is implemented and ready for external review.

The release-facing v0.7 docs now reflect the accepted columnar prepared DB
dataset transfer work from Goals 440-442 and the refreshed columnar
repeated-query performance gate from Goal 443.

## Files Updated

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/release_statement.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/audit_report.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/support_matrix.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/tag_preparation.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/features/db_workloads/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/tutorials/db_workloads.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_facing_examples.md`

## Changes Made

- Replaced stale statements that final columnar/binary ingestion was not closed.
- Replaced stale statements that table ingestion still used the compatibility
  ctypes row path for the current RT prepared dataset performance story.
- Updated current performance evidence from Goal 437 to Goal 443.
- Updated support-matrix performance numbers to the Goal 443 columnar gate:
  - `conjunctive_scan`: best RTDL total 1.035639 s vs PostgreSQL 10.371679 s
  - `grouped_count`: best RTDL total 0.881182 s vs PostgreSQL 12.346080 s
  - `grouped_sum`: best RTDL total 0.924547 s vs PostgreSQL 10.513986 s
- Added explicit prepared dataset API examples with `transfer="columnar"`.
- Preserved the DBMS boundary:
  - no arbitrary SQL
  - no PostgreSQL-style storage/indexing/transactions/optimizer/concurrency
  - no claim that RTDL replaces PostgreSQL
- Preserved branch status:
  - active bounded v0.7 branch line
  - still not tagged as the next mainline release

## Stale-Wording Check

Command:

```text
rg -n "compatibility ctypes|compatibility encoding|table ingestion still|final columnar|large-table ingestion is not closed|Goal 437|row ingestion path|row-struct compatibility|current compatibility" README.md docs/README.md docs/quick_tutorial.md docs/release_facing_examples.md docs/tutorials docs/features docs/release_reports/v0_7
```

Result:

```text
no matches
```

## Boundary

Goal 444 is documentation-only. It does not change runtime behavior, test
coverage, or release status. It aligns release-facing language with the already
accepted implementation/performance gates.
