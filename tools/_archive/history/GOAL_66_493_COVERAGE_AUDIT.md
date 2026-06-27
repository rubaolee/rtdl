# Goal 66-493 History Coverage Audit

Date: 2026-04-19

This audit explains why `history/revisions/` appears sparse between Goal 65 and Goal 493 on GitHub.

## Summary

- Goals audited: `66-493` (`428` goal numbers)
- Structured per-round revision directories in `history/revisions/`: `1`
- Goal documents preserved in `docs/history/goals/archive/` but not as per-goal revision directories: `300`
- Report/review-only direct goal artifacts: `63`
- No direct goal-id artifact found by filename scan: `64`

## Root Cause

The repo has two historical layers. `history/revisions/` is a structured revision-round archive, not a complete one-directory-per-goal ledger. Most Goals 66-493 were preserved in `docs/history/goals/archive/`, `docs/reports/`, and `history/ad_hoc_reviews/`. The GitHub directory listing for `history/revisions/` did not explain that, making it look like the middle history was missing.

## Coverage By Layer

| Layer | Count | Meaning |
| --- | ---: | --- |
| `history/revisions/` structured rounds | 1 | Goals with explicit per-round snapshot directories |
| `docs/history/goals/archive/` | 300 | Goals preserved as archived goal docs, not structured revision directories |
| `docs/reports/` or `history/ad_hoc_reviews/` only | 63 | Goals with reports/reviews but no archived goal doc detected |
| no direct filename hit | 64 | Goal numbers not directly found by filename scan; may be folded into catch-up/release rounds or absent |

## Important Ranges

- Structured revision-round hits in this interval: `493`
- Report/review-only direct hits: `237, 423-424, 432-475, 477-492`
- No direct filename hit: `162, 183, 188, 221, 235, 301-309, 337-384, 425, 476`

## Machine-Readable Ledger

The full per-goal coverage ledger is in `history/goal_66_493_coverage.csv`.

Each row records whether a goal has a structured revision directory, archived goal doc, report/review artifact, or no direct goal-id filename hit.

## Fix Applied

The public `history/revisions/README.md` now explains that `history/revisions/` is selective and points readers to the complete history map, dashboard, goal archive, reports, and this coverage ledger. This directly addresses the misleading GitHub directory view.

## Remaining Follow-Up

If we want one visible structured round for every historical goal, the next action is a generated backfill pass that creates compact catch-up revision directories for missing ranges. That should be done as a separate goal because it will add hundreds of files and should not rewrite existing accepted archives.
