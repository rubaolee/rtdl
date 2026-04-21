# Revision Round Archive

This directory is not intended to contain one subdirectory for every RTDL goal.
It stores structured revision rounds: selected review, repair, audit, and
release cycles where the project captured copied reports plus a project snapshot
under one immutable round directory.

## Why Goals 66-493 Look Sparse Here

The middle history is not absent. It is split across several archive layers:

- `history/revisions/` records structured revision rounds.
- `docs/history/goals/archive/` records archived goal documents.
- `docs/reports/` records reports, reviews, audits, and release evidence.
- `history/ad_hoc_reviews/` records standalone Codex, Claude, and Gemini
  consensus notes.
- Git commits and tags record exact source-code changes.

For Goals 66-493 specifically, the repository currently has this direct
filename-level coverage:

| Layer | Count |
| --- | ---: |
| Structured per-round revision directories in this folder | 1 |
| Archived goal documents in `docs/history/goals/archive/` | 300 |
| Direct report or ad hoc review artifacts only | 63 |
| No direct goal-id filename hit in the scanned public artifacts | 64 |

The gap visible on GitHub is therefore a presentation/indexing gap, not evidence
that all work between Goal 65 and Goal 493 disappeared.

## Where To Look

- Start at `../README.md` for the history-system overview.
- Use `../COMPLETE_HISTORY.md` for the complete public history map.
- Use `../revision_dashboard.md` for chronological structured rounds.
- Use `../../docs/history/goals/archive/` for archived goal documents.
- Use `../../docs/reports/` for reports and reviews.
- Use `../ad_hoc_reviews/` for standalone consensus and review notes.
- Use `../GOAL_66_493_COVERAGE_AUDIT.md` for the Goal 66-493 gap audit.
- Use `../goal_66_493_coverage.csv` for the per-goal coverage ledger.

## Current Boundary

This README makes the public directory view honest and navigable. It does not
backfill hundreds of structured revision directories. If the project later wants
one visible structured round for every historical goal, that should be a
separate generated backfill goal because it will add many files and must not
rewrite already accepted reports.

## Latest Current-Main Catch-Up

The latest structured current-main catch-up round is Goals658-679:

- `2026-04-20-goal658-679-cross-engine-prepared-visibility-optimization`

It records Apple RT, OptiX, HIPRT, and Vulkan prepared/prepacked
visibility-count optimization work plus the local and Linux release gates. It
is current-main evidence, not a new public release tag and not a retroactive
`v0.9.5` tag claim.
