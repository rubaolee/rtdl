# Goal 409 Report: Repo-Wide File Status Audit

Date: 2026-04-15

## Scope

This goal performs a repository-wide file status audit for the released
`v0.6.1` line.

The audit must eventually classify every tracked file for:

- role
- status
- correctness
- freshness
- dead/misleading content
- action recommendation

## Shared audit artifact

The per-file ledger for this goal is:

- [goal409_repo_file_status_ledger_2026-04-15.csv](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal409_repo_file_status_ledger_2026-04-15.csv)

## Current first-pass ledger state

The ledger is generated directly from `git ls-files` so the checker, verifier,
and final-proof reviewers all operate on the same tracked-file universe.

Current tracked-file count at ledger generation time:

- `3986`

Current corrected status split after checker-driven heuristic refinement:

- `3480` historical
- `371` live
- `135` transitional
- `0` unclear

Current category split:

- `1735` history
- `1077` report
- `404` doc
- `282` handoff
- `168` test
- `77` script
- `58` example
- `53` source
- `44` release_doc
- `35` tracked_build_artifact
- `20` native_source
- `16` generated
- `6` tutorial
- `5` repo_root
- `4` app
- `2` schema

Release-doc split inside the ledger:

- `5` live current-release files under `docs/release_reports/v0_6/`
- `39` historical release-report files from older releases or previews

Other corrected structural splits:

- `347` of `404` `doc`-category files are now historical rather than live
- `67` goal-named scripts are transitional rather than live
- `12` goal-named source files are transitional rather than live
- `5` goal-named internal examples are transitional rather than live

## Audit method for the first pass

1. enumerate all tracked files
2. assign a category from path
3. assign a role from category
4. assign a first-pass status:
   - live
   - historical
   - transitional
   - unclear
5. assign a first-pass statement for:
   - correctness status
   - content freshness
   - dead/misleading-content risk
   - action recommendation
6. use checker/verifier/final-proof review to challenge the heuristic ledger
7. keep the ledger as the per-file record even where the conclusion is
   intentionally conservative

## Corrections already forced by review

The checker phase materially changed the first-pass picture.

Most important corrections already reflected in the ledger:

1. `VERSION` is still `v0.4.0`, so the ledger now treats it as a high-risk
   front-door version marker rather than a generic "inspect further" root file
2. archival documentation previously overclassified as live now moves to
   `historical`, including:
   - `docs/history/**`
   - `docs/archive/**`
   - `docs/wiki_drafts/**`
   - `docs/engineering/handoffs/**`
   - `docs/current_milestone_qa.md`
   - `docs/goal_*.md`
3. goal-scoped source, script, and internal-example files now move from blanket
   `live` to `transitional`
4. `requirements.txt` is now explicitly classified as a live dependency manifest

## Main first-pass risk bands

The first pass already shows where the repo-wide audit pressure belongs:

1. tracked build artifacts in `build/`
2. generated surfaces under `generated/`
3. live docs, tutorials, and examples that can drift from the released line
4. transitional goal-scoped engineering files that may be bounded support or
   dead scaffolding
5. live implementation and test surfaces under `src/`, `src/native/`, `tests/`,
   `apps/`, and `schemas/`
6. archival material that is acceptable only if it stays clearly archival and
   is not surfaced as the live contract

## What this first pass does not claim

This report does not claim that every file has already been manually
line-reviewed.

The first-pass ledger is a concrete repo-wide classification baseline, not the
final proof by itself. The checker/verifier/final-proof chain must still judge:

- whether the heuristics are materially correct
- whether important stale or misleading files were missed
- whether the tracked-artifact and generated-content slices need stronger action
- whether the live documentation/example surface is honestly represented

## Current status

The checker, verifier, and final-proof chain is now complete.

That means Goal 409 is:

- closed as a repo-wide file-status audit
- accepted as the authoritative per-file inventory and risk map
- not a claim of cleanup completion or full manual line review

## Follow-up

The next work should build on this ledger rather than re-enumerate the repo
from scratch:

1. fix the stale `VERSION` front-door file
2. review the live surfaces by subsystem
3. resolve the transitional goal-scoped and artifact-heavy slices
4. use the ledger as the authoritative per-file cleanup tracker
