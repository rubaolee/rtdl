# History Archive

This directory is the revision archive for RTDL.

It is designed around two layers:

1. A central SQLite database
   `history/history.db`

   This stores normalized metadata for revision rounds, events, and archived files.

2. Immutable per-round file archives
   `history/revisions/<round-slug>/`

   Each round directory stores the actual copied files for that review or revision cycle.

There is also a manager-facing summary file:

3. Human-readable revision dashboard
   `history/revision_dashboard.html`

   This is a single self-contained HTML file with inline styles. It keeps one row per round so someone can quickly scan version, status, review outcome, revision outcome, and final result without querying SQLite.

4. GitHub-readable markdown companion
   `history/revision_dashboard.md`

   This mirrors the same round summary in Markdown so it can be read directly on GitHub without opening the HTML file.

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

## Current Seeded Round

This archive is seeded with the March 29, 2026 review-and-revision cycle covering:

- the original Gemini verification report,
- the Codex revision note,
- the Gemini review log and final revised report,
- and the RTDL project changes that implemented the accepted revisions.
