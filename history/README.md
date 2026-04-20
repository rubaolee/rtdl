# History Archive

This directory is the revision archive for RTDL.

If you are asking whether RTDL has a full public history, start here:

- [Complete History Map](COMPLETE_HISTORY.md)
- [Revision Dashboard](revision_dashboard.md)
- [Goal 66-493 Coverage Audit](GOAL_66_493_COVERAGE_AUDIT.md)
- [Goal 66-493 Coverage CSV](goal_66_493_coverage.csv)

The complete history map explains how to trace preserved evidence across
structured revision rounds, release reports, ad hoc review notes, handoff files,
git tags, and git commits.

It is designed around two layers:

1. A central SQLite database
   `history/history.db`

   This stores normalized metadata for revision rounds, events, and archived files.

2. Immutable per-round file archives
   `history/revisions/<round-slug>/`

   Each round directory stores the actual copied files for that review or revision cycle.

   Important boundary: this is a structured round archive, not a one-directory-
   per-goal ledger. Many historical goals are represented by goal archive files,
   reports, ad hoc reviews, and git commits rather than by a dedicated directory
   under `history/revisions/`.

There is also a manager-facing summary file:

3. Human-readable revision dashboard
   `history/revision_dashboard.html`

   This is a single self-contained HTML file with inline styles. It keeps one row per round so someone can quickly scan version, status, review outcome, revision outcome, and final result without querying SQLite.

4. GitHub-readable markdown companion
   `history/revision_dashboard.md`

   This mirrors the same round summary in Markdown so it can be read directly on GitHub without opening the HTML file.

5. Ad hoc review notes
   `history/ad_hoc_reviews/`

   This stores accepted standalone review memos and consensus notes that are
   intentionally kept outside the per-round archive layout.

## Why This Layout

The database is good for:

- querying all past revision rounds,
- tracking which files changed in each round,
- recording commits, dates, actors, and summaries,
- storing structured manager-facing status fields for each round,
- keeping the archive searchable without scanning the filesystem.

The filesystem archive is good for:

- preserving the original review reports,
- preserving the exact project files associated with a revision round,
- keeping artifacts readable without special tooling,
- avoiding binary blobs for every archived file inside the database.

This hybrid layout is more practical than:

- storing only ad hoc markdown logs,
- storing file contents only inside SQLite,
- or relying only on git history for cross-agent review records.

## Directory Layout

- `history/history.db`
  Central SQLite index.
- `history/schema.sql`
  Schema used to initialize the database.
- `history/scripts/register_revision_round.sh`
  Helper script to register a new round and archive files into the database plus filesystem.
- `history/revision_dashboard.html`
  Single-file HTML dashboard for managers and quick project status reviews.
- `history/revision_dashboard.md`
  Markdown summary of the same dashboard data for GitHub reading.
- `history/ad_hoc_reviews/`
  Standalone review memos and consensus notes that were accepted without being
  folded into a dedicated per-round `history/revisions/<round-slug>/` archive.
- `history/revisions/<round-slug>/metadata.txt`
  Human-readable round summary.
- `history/revisions/<round-slug>/external_reports/`
  Copies of external review/revision reports.
- `history/revisions/<round-slug>/project_snapshot/`
  Copies of RTDL repository files that were revised or discussed in that round.

## Database Tables

- `revision_rounds`
  One row per review/revision cycle.
- `revision_events`
  Ordered events inside a round, such as original report, rebuttal, agreement, implementation, and follow-up review.
- `revision_round_status`
  One structured status row per round for quick reporting fields such as version, review summary, revision summary, and final result.
- `archived_files`
  One row per copied file, including source path, archive path, category, and checksum.

## Recommended Workflow

1. Create or identify a revision round slug.
2. Archive external review reports into `external_reports/`.
3. Archive the relevant RTDL project files into `project_snapshot/`.
4. Insert round metadata and file metadata into `history.db`.
5. Regenerate `revision_dashboard.html` and `revision_dashboard.md` from the database.
6. Keep the archive immutable after the round is closed.

## Current State

This archive began with the March 29, 2026 review-and-revision cycle and now
contains later rounds through the `v0.9.5` release and post-release
fresh-checkout verification, plus the Goals650-656 current-main any-hit,
documentation, and full-test catch-up:

- language/runtime bring-up
- Embree validation and RayJoin-style reproduction work
- OptiX bring-up and bounded real-data validation
- full-project audits, documentation rewrites, and backend comparison notes
- `v0.7.0` release-readiness, release action, and post-release public-surface
  3C audit records
- `v0.8.0` app-building release records
- `v0.9.0` HIPRT / closest-hit release records
- `v0.9.1` Apple Metal/MPS RT closest-hit release records
- `v0.9.4` Apple RT compatibility, HIPRT/Apple documentation, and release-gate
  repair records
- `v0.9.5` bounded any-hit, visibility-row, emitted-row reduction,
  post-release front-page refresh, and fresh-checkout verification records
- Goals650-656 current-main native/native-assisted any-hit backend work,
  current-main support matrix, tutorial/example boundary refresh, and
  post-doc-refresh full local test evidence
- ad hoc review memos and consensus notes that complement the structured rounds

Goal629 added an explicit audit for the misleading public gap between Goal 65
and Goal 493. The short answer is that `history/revisions/` is sparse by design,
while most middle goals are preserved in `docs/history/goals/archive/`,
`docs/reports/`, and `history/ad_hoc_reviews/`.

The immutable rule still applies:

- do not rewrite accepted historical reports
- do not rewrite archived per-round snapshots
- only update live guide/index material such as this file when the archive
  structure or workflow description changes
