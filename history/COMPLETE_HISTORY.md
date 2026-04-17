# RTDL Complete History Map

Date: 2026-04-16
Status: generated

This page answers the question a new visitor will ask: "Where is the full RTDL
history?"

Short answer: the repository now has a complete public map over the preserved
history artifacts, but `history/` is an index and archive, not a verbatim
conversation transcript. The exact code evolution remains in git commits and
tags; the reasoning, reviews, audits, and release evidence are preserved in the
files indexed here.

## What Is Recorded

- Structured revision rounds: `70`
- Archived files in `history/history.db`: `788`
- External report snapshots: `180`
- Project snapshots: `608`
- Tracked `docs/reports/` artifacts: `1443`
- Tracked `history/ad_hoc_reviews/` artifacts: `657`
- Tracked AI handoff files: `372`
- Tracked release tags: `8`

## How To Read The History

Use these layers together:

1. Start with `README.md` for the current released surface.
2. Read `docs/README.md` for the public documentation map.
3. Read `docs/release_reports/<version>/` for release statements, support
   matrices, audits, and tag preparation.
4. Read `history/revision_dashboard.md` for the chronological revision-round
   table.
5. Read `history/revisions/<round>/metadata.txt` and its snapshots for a
   specific archived round.
6. Read `history/ad_hoc_reviews/` for standalone Codex/Claude/Gemini consensus
   memos and review notes.
7. Read `docs/reports/` for the full report and review corpus.
8. Use git commits and tags for exact source-code diffs.

## Release Tags

- `v0.1.0`
- `v0.2.0`
- `v0.3.0`
- `v0.4.0`
- `v0.5.0`
- `v0.6.0`
- `v0.6.1`
- `v0.7.0`

## Current Top Revision Rounds

| Version | Date | Status | Round | Result | Archive |
| --- | --- | --- | --- | --- | --- |
| `v0.7.0` | 2026-04-16 | `complete-consensus` | Goal495 Complete History Map | `COMPLETE` | `2026-04-16-goal495-complete-history-map` |
| `v0.7.0` | 2026-04-16 | `complete-consensus` | Goal494 History Revisions Refresh After v0.7 Release | `COMPLETE` | `2026-04-16-goal494-history-revisions-refresh` |
| `v0.7.0` | 2026-04-16 | `complete-consensus` | Goal493 Post-v0.7 Public Surface 3C Audit | `COMPLETE` | `2026-04-16-goal493-post-v0-7-public-surface-3c` |
| `v0.7.0` | 2026-04-16 | `released` | v0.7.0 Release Action | `RELEASED` | `2026-04-16-v0-7-release-action` |
| `v0.7.0` | 2026-04-16 | `complete-consensus` | v0.7 Goals 488-492 Release-Readiness Catch-up | `COMPLETE` | `2026-04-16-v0-7-goals488-492-catchup` |
| `v0.7` | 2026-04-16 | `active-hold` | v0.7 Current Release-Hold State | `HOLD` | `2026-04-16-v0-7-current-hold` |
| `v0.6.1` | 2026-04-15 | `complete` | v0.6.1 Closure Catch-up | `COMPLETE` | `2026-04-15-v0-6-closure` |
| `v0.5` | 2026-04-14 | `complete` | v0.5 Closure Catch-up | `COMPLETE` | `2026-04-14-v0-5-closure` |
| `v0.4` | 2026-04-12 | `complete` | v0.4 Closure Catch-up | `COMPLETE` | `2026-04-12-v0-4-closure` |
| `v0.3` | 2026-04-09 | `complete` | v0.2/v0.3 Closure Catch-up | `COMPLETE` | `2026-04-09-v0-2-v0-3-closure` |
| `v0.1` | 2026-04-04 | `complete-consensus` | Goal 65 Vulkan OptiX Linux Comparison | `Goal 65 accepted under Codex+Gemini consensus: Vulkan runs on Linux but remains provisional; OptiX stays the accepted GPU backend` | `2026-04-04-goal-65-vulkan-optix-linux-comparison` |
| `v0.1` | 2026-04-04 | `complete-consensus` | Goal 64 Submission-Ready Paper Package | `Goal 64 accepted under Codex+Gemini fallback because Claude was unavailable` | `2026-04-04-goal-64-submission-ready-paper-package` |

## Tracked File Categories

| Category | Count |
| --- | ---: |
| `ad_hoc_review_or_consensus` | 657 |
| `ai_handoff` | 372 |
| `example` | 66 |
| `feature_doc` | 13 |
| `front_page` | 1 |
| `history_index` | 3 |
| `history_support` | 4 |
| `live_goal_doc` | 61 |
| `other` | 479 |
| `release_report` | 49 |
| `report_or_review` | 1443 |
| `script` | 116 |
| `source` | 76 |
| `structured_history_archive` | 1229 |
| `test` | 199 |
| `tutorial` | 9 |

## Boundaries

- This page does not claim that every chat message or terminal line is
  preserved.
- It does claim that the repo-visible evidence is now discoverable through a
  stable map: release reports, goal reports, external reviews, handoffs,
  consensus notes, structured revision rounds, and git tags/commits.
- Some old periods are represented by catch-up revision rounds plus the
  underlying reports, rather than one revision directory per micro-goal.
- Historical records are not rewritten to look current. Newer repair rounds are
  appended when earlier indexes become stale.

## Machine Artifacts

- JSON inventory: `/Users/rl2025/rtdl_python_only/docs/reports/goal495_complete_history_map_2026-04-16.json`
- CSV file inventory: `/Users/rl2025/rtdl_python_only/docs/reports/goal495_complete_history_file_inventory_2026-04-16.csv`
- Report: `/Users/rl2025/rtdl_python_only/docs/reports/goal495_complete_history_map_2026-04-16.md`
