# Goal1221 Gemini Review: v0.9.8 Release Action

Date: 2026-05-01
Reviewer: Claude (acting as external-AI reviewer in the RTDL 2-AI consensus role)

## Verdict

`ACCEPT`

## Files Inspected

- `VERSION`
- `README.md`
- `docs/README.md`
- `docs/current_main_support_matrix.md`
- `docs/release_reports/v0_9_8/README.md`
- `docs/release_reports/v0_9_8/release_statement.md`
- `docs/release_reports/v0_9_8/support_matrix.md`
- `docs/release_reports/v0_9_8/audit_report.md`
- `docs/release_reports/v0_9_8/tag_preparation.md`
- `history/COMPLETE_HISTORY.md`
- `history/revision_dashboard.md`
- `docs/reports/goal1220_two_ai_consensus_2026-05-01.md`
- `docs/reports/goal1221_v0_9_8_release_action_2026-05-01.md`
- `tests/goal1221_v0_9_8_release_action_test.py`

## Question-by-Question Findings

### Q1 — Is the VERSION bump to v0.9.8 justified by Goal1220 final authorization?

Yes. `VERSION` reads `v0.9.8`. Goal1220 returned an explicit `ACCEPT` verdict
with the authorized next steps recorded verbatim: "bump `VERSION` from `v0.9.6`
to `v0.9.8`." The Goal1221 release-action report confirms "Bumped `VERSION` from
`v0.9.6` to `v0.9.8`." The test
`test_version_and_public_front_page_are_released_v098` asserts both the
`VERSION` file value and the front-page phrase "The current released version is
`v0.9.8`". No discrepancy found.

### Q2 — Do the release package and live public docs consistently say v0.9.8 is released/current without leaving v0.9.6 as the current public release?

Yes, consistently. Every live pointer checked reads as follows:

- `VERSION`: `v0.9.8`
- `README.md`: "The current released version is `v0.9.8`"; "current released
  version: `v0.9.8`"; release history table entry for `v0.9.8` marked `current
  public release`
- `docs/README.md`: "current released version is `v0.9.8`"; new-user path leads
  with the v0.9.8 release package
- `docs/current_main_support_matrix.md`: "Current public release: `v0.9.8`"
- All four `docs/release_reports/v0_9_8/` files carry `Status: released as
  \`v0.9.8\``
- `history/COMPLETE_HISTORY.md`: `v0.9.8` appears in the Release Tags list and
  the top revision-rounds table shows `released` status for Goal1221
- `history/revision_dashboard.md`: v0.9.8 row is marked `released` at `HEAD`

`v0.9.6` wording is preserved only where it correctly describes the previous
backend-feature release boundary (e.g., the version-history narrative in
README.md, the "`v0.9.6`: previous backend-feature public release" entry). No
surface conflates v0.9.6 with the current release.

### Q3 — Are public RTX/RT-core claims still bounded?

Yes, on all four sub-questions:

**DB full output.** README.md "Still outside public RTX claim review today"
paragraph explicitly lists "SQL/DBMS behavior, default row-materializing DB
output." The v0.9.8 support matrix marks `database_analytics` public speedup
wording `blocked`. The README "Version Status At A Glance" section additionally
states "`database_analytics` and `polygon_set_jaccard` public speedup wording
remain blocked."

**Polygon Jaccard.** Listed as a claim-review candidate with a `--require-rt-core`
flag requirement, but the support matrix explicitly blocks it and the Version
Status section confirms the block. No public speedup claim is made.

**Whole-app speedup.** Every claim-boundary section consistently says the
allowed conclusion is limited to the named traversal/summary sub-path and
explicitly excludes "whole-app speedup, Python post-processing, exact polygon
area/Jaccard refinement, ranked KNN, full DBSCAN cluster expansion, and
graph-system claims." The road-hazard newly reviewed row is bounded to 40k
copies and the prepared native compact-summary sub-path only.

**Backend-flag-only claims.** The "NVIDIA RT-Core Claim Boundary" section of
README.md clearly states "`--backend optix` is not, by itself, a claim that
NVIDIA RT cores accelerated the app" and requires `--require-rt-core` plus
a documented bounded sub-path. This wording is unchanged and correct.

Robot normalized per-pose wording retains its explicit caveat: "not a
same-total-work wall-time claim and not a whole-app robot-planning claim."

**Minor observation (non-blocking).** The `audit_report.md` Flow Audit section
retains a sentence — "This package still requires its own external review and
final maintainer authorization before tag, push, publish, or `VERSION` bump" —
that was accurate at draft time but is now stale relative to the `Status:
released as \`v0.9.8\`` header. Since the status header is the authoritative
release marker and all tests pass, this is a documentation artifact rather than
a substantive error. A future hygiene pass could remove it.

### Q4 — Is it correct that commit/tag/push remain separate operations after this review?

Yes. The Goal1221 release-action report explicitly states: "Commit, tag, and
push are separate git operations and must include only the reviewed release file
set." The tag_preparation.md documents the git commands as a separate step and
notes "tag is created only after the release commit." The test
`test_release_action_report_records_boundary` asserts this sentence is present
verbatim. Current git state (branch `codex/rtx-cloud-run-2026-04-22`, modified
files not yet committed) confirms no tag or push has occurred.

## Summary

All four review questions are satisfied. The VERSION bump is authorized, all
live public pointers are consistent, RTX/RT-core claims remain properly bounded
with DB/Jaccard/whole-app wording blocked, and the commit/tag/push sequence is
correctly deferred. The 39-test suite passes. One stale sentence in
audit_report.md is noted but is not a release blocker.

`ACCEPT`
