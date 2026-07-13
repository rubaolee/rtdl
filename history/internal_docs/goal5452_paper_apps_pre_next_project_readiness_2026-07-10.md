# Goal5452 - Paper Apps Pre-Next-Project Readiness

Date: 2026-07-10

## Objective

Close the repository-level documentation, status, regression, and handoff work
for the four existing paper reproduction apps before a fifth paper project is
opened.

## Work Completed

1. Audited the user-facing README and current manifest status for RayJoin,
   RT-BarnesHut, RT-DBSCAN, and X-HD.
2. Removed stale scaffold wording for RT-DBSCAN and X-HD.
3. Updated RayJoin from the v2.14.3 `0.755s` prepared evidence to the final
   v2.14.4 `0.328842s` six-batch prepared-binary result and retained its
   semantic-boundary caveat.
4. Updated the RT-BarnesHut manifest from an older POD result to the final
   Goal5080/5083 phase-boundary packet.
5. Updated the X-HD data status and manifest to the externally approved
   Goal5451 same-input directed-HDResult closeout.
6. Added `Paper-reproduction-apps/paper_app_status_snapshot.json` as the
   machine-readable portfolio source of current scoped status.
7. Added a regression test that requires all four apps, their review evidence,
   their bounded claim boundary, and selected final numbers to remain aligned.

## Current Portfolio

| App | Honest completed scope | Performance position | Explicitly not claimed |
| --- | --- | --- | --- |
| RayJoin | Sections 5.2, 5.3, bounded 5.7 | Prepared binary top4 six-batch `0.328842s`; `1.76x` slower than bounded AuthorOfficial core phases | all-input or semantic whole-app parity |
| RT-BarnesHut | bounded prepared-state same-input force output | narrow kernel lower; broader envelope `2.53x` slower | independent tree construction or full paper |
| RT-DBSCAN | bounded AuthorOfficial plus representative synthetic partition gates | diagnostics only; no ratio authorized | exact paper preprocessing, arbitrary DBSCAN acceleration, full paper |
| X-HD | seven-case same-input directed HDResult, externally approved | denominators remain separate; no ratio authorized | exact paper bytes, all figures, author RT-core equivalence, performance parity |

## Architectural Result

The portfolio continues to enforce one ownership rule:

```text
RTDL core owns generic spatial/dataflow capabilities.
Paper apps own paper-specific inputs, wrappers, comparators, tolerances,
formatting, workload policy, and claim boundaries.
```

The four apps have extracted reusable system capabilities in device-columnar
prepared pipelines, aggregate-hierarchy traversal/reduction, fixed-radius
count-threshold queries, and nearest-witness/max-nearest reduction. None of the
current scoped closeouts requires an app-identity primitive in RTDL core.

## Exit Condition

Goal5452 is complete when:

- the portfolio snapshot test and focused app regressions pass;
- public documentation contains no stale scaffold/current-status conflict;
- durable memory records that X-HD is closed at its approved scope;
- the worktree is committed and clean.

This goal does not authorize a new paper app, a new performance claim, or an
upgrade from scoped reproduction to full-paper reproduction.

## Verification

```text
portfolio status and manifest tests: 4 OK
RayJoin v2.14.4 API/release-boundary tests: 43 OK, 1 skipped
RT-BarnesHut contract/genericity/rope tests: 76 OK, 1 skipped
RT-DBSCAN AuthorOfficial/partition/warm-loop tests: 13 OK
X-HD generic-nearest/independent-consumer/Goal5451 tests: 12 OK
total: 148 OK, 2 environment-conditional skips
```

All edited JSON files pass `python -m json.tool`. The public paper-app surface
contains none of the stale current-state phrases audited by this goal.

## External Review Status

The first external review returned `approve_with_required_amendments`. Its
required RayJoin review-evidence correction and both non-blocking hardening
suggestions were implemented in
`goal5452_review_amendment_response_2026-07-10.md`.

Current review status:

```text
required_amendments_implemented__external_reverification_pending
```
