# Goal4917 — Claude Review Amendment Response

Date: 2026-07-03

Review source:

```text
history/internal_docs/claude_review_goal4917_status_and_next_plan_2026-07-03.md
```

Target document amended:

```text
history/internal_docs/goal4917_rayjoin_reproduction_performance_status_and_next_plan_2026-07-03.md
```

## Verdict Accepted

Claude verdict:

```text
approve_with_required_amendments
```

Accepted.

## AM1 — Cold/Hot Arc And Hot-Body Definition

Status: addressed.

Changes made:

- added explicit definition:

  ```text
  Hot Body = prepared-hot query+output body, including LSI/PIP replay,
  reprojection/sorting, app continuation, exact output-chain writer, and file
  summary checks. It excludes cold one-time workspace setup and import/setup
  phases.
  ```

- added the earlier `20.920s query+output` baseline;
- added the corrected arc:

  ```text
  Goal4888 "native traversal dominated" was a cold/unprepared-state conclusion.
  Prepared-hot state is Branch A: materialization/output/session-lifecycle work.
  ```

- recorded that the original `3–8s` hot target has been reached in prepared-hot
  mode:

  ```text
  best prepared-hot query+output body: 3.832s
  ```

## AM2 — Track 1 Is Not RayJoin's Remaining Hot-Path Remedy

Status: addressed.

Changes made:

- added a statement that RayJoin's remaining hot path is writer/output-format
  bound, not traversal-reduce bound;
- clarified that dataflow-to-kernel pushdown remains a long-term language
  investment but is not expected to move the current RayJoin representative
  number;
- clarified that a compiled/native output writer is the only direct RayJoin
  lever, but is likely app-output-specific and must not be smuggled into RTDL
  core.

## AM3 — Australia/SA AuthorOfficial Boundary

Status: addressed.

Changes made:

- updated Section 5.7 status boundary to state that Australia/SA results are
  AuthorOfficial-contract results, not raw-author-byte-equality claims unless a
  per-dataset patch-impact audit proves zero effect.

## Result

Goal4917 now says the sharper conclusion:

```text
The current RayJoin product state is correct, bounded, and useful. The
remaining RayJoin performance gap is output-format bound. Small Python
micro-optimizations should stop. Pushdown compiler work is a separate generic
language track, not a RayJoin hot-path rescue. A compiled output writer would
need a separate app-specific-risk review.
```
