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

- Structured revision rounds: `104`
- Archived files in `history/history.db`: `1084`
- External report snapshots: `193`
- Project snapshots: `891`
- Tracked `docs/reports/` artifacts: `1558`
- Tracked `history/ad_hoc_reviews/` artifacts: `691`
- Tracked AI handoff files: `406`
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
| `v0.8` | 2026-04-18 | `accepted` | Goal529 v0.8 Linux post-doc-refresh validation | `accepted` | `2026-04-18-goal529-v0_8-linux-post-doc-refresh-validation` |
| `v0.8` | 2026-04-18 | `accepted` | Goal528 v0.8 post-doc-refresh local audit | `accepted` | `2026-04-18-goal528-v0_8-post-doc-refresh-local-audit` |
| `v0.8` | 2026-04-18 | `accepted` | Goal527 examples and capability boundary refresh | `accepted` | `2026-04-18-goal527-examples-and-capability-boundary-refresh` |
| `v0.8` | 2026-04-18 | `accepted` | Goal526 v0.8 public doc stale app-count cleanup | `accepted` | `2026-04-18-goal526-v0_8-public-doc-stale-app-count-cleanup` |
| `v0.8` | 2026-04-18 | `accepted` | Goal525 v0.8 proximity performance doc refresh | `accepted` | `2026-04-18-goal525-v0_8-proximity-perf-doc-refresh` |
| `v0.8` | 2026-04-17 | `accepted` | Goal524 v0.8 Stage-1 proximity Linux performance | `docs/reports/goal524_v0_8_stage1_proximity_linux_perf_2026-04-17.md` | `goal524-stage1-proximity-linux-perf` |
| `v0.8` | 2026-04-17 | `accepted` | Goal523 v0.8 Linux public command validation | `docs/reports/goal523_v0_8_linux_public_command_validation_2026-04-17.md` | `goal523-linux-public-command-validation` |
| `v0.8` | 2026-04-17 | `accepted` | Goal522 v0.8 scope-refreshed final local audit | `docs/reports/goal522_v0_8_scope_refreshed_final_local_audit_2026-04-17.md` | `goal522-v0-8-scope-refreshed-local-audit` |
| `v0.8` | 2026-04-17 | `accepted` | Goal521 v0.8 workload scope decision matrix | `docs/reports/goal521_v0_8_workload_scope_decision_matrix_2026-04-17.md` | `goal521-v0-8-workload-scope` |
| `v0.8` | 2026-04-17 | `accepted` | Goal520 v0.8 Stage-1 proximity apps | `docs/reports/goal520_v0_8_stage1_proximity_apps_2026-04-17.md` | `goal520-stage1-proximity-apps` |
| `v0.8` | 2026-04-17 | `accepted` | Goal519 RT workload universe roadmap | `docs/reports/goal519_rt_workload_universe_from_2603_28771_2026-04-17.md` | `goal519-rt-workload-universe` |
| `v0.8` | 2026-04-17 | `accepted` | Goal518 v0.8 final local release audit | `docs/reports/goal518_v0_8_final_local_release_audit_2026-04-17.md` | `goal518-v0-8-final-local-release-audit` |

## Tracked File Categories

| Category | Count |
| --- | ---: |
| `ad_hoc_review_or_consensus` | 691 |
| `ai_handoff` | 406 |
| `example` | 73 |
| `feature_doc` | 13 |
| `front_page` | 1 |
| `history_index` | 3 |
| `history_support` | 4 |
| `live_goal_doc` | 61 |
| `other` | 482 |
| `release_report` | 49 |
| `report_or_review` | 1558 |
| `script` | 122 |
| `source` | 76 |
| `structured_history_archive` | 1548 |
| `test` | 221 |
| `tutorial` | 11 |

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
