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

- Structured revision rounds: `94`
- Archived files in `history/history.db`: `1006`
- External report snapshots: `193`
- Project snapshots: `813`
- Tracked `docs/reports/` artifacts: `1523`
- Tracked `history/ad_hoc_reviews/` artifacts: `681`
- Tracked AI handoff files: `396`
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
| `v0.8` | 2026-04-17 | `accepted` | Goal519 RT workload universe roadmap | `docs/reports/goal519_rt_workload_universe_from_2603_28771_2026-04-17.md` | `goal519-rt-workload-universe` |
| `v0.8` | 2026-04-17 | `accepted` | Goal518 v0.8 final local release audit | `docs/reports/goal518_v0_8_final_local_release_audit_2026-04-17.md` | `goal518-v0-8-final-local-release-audit` |
| `v0.8` | 2026-04-17 | `accepted` | Goal517 ITRE app programming model | `docs/reports/goal517_itre_app_programming_model_2026-04-17.md` | `goal517-itre-app-programming-model` |
| `v0.8` | 2026-04-17 | `accepted` | Goal516 Linux full public command validation | `docs/reports/goal516_linux_full_public_command_validation_2026-04-17.md` | `goal516-linux-full-public-command-validation` |
| `v0.8` | 2026-04-17 | `accepted` | Goal515 public docs command truth | `docs/reports/goal515_public_docs_command_truth_closure_2026-04-17.md` | `goal515-public-docs-command-truth` |
| `v0.8` | 2026-04-17 | `accepted` | Goal514 tutorial/example harness refresh | `docs/reports/goal514_tutorial_example_harness_refresh_2026-04-17.md` | `goal514-tutorial-example-harness-refresh` |
| `v0.8` | 2026-04-17 | `accepted` | Goal513 public example smoke gate | `docs/reports/goal513_public_example_smoke_gate_2026-04-17.md` | `goal513-public-example-smoke-gate` |
| `v0.8` | 2026-04-17 | `accepted` | Goal512 public documentation smoke audit | `docs/reports/goal512_public_doc_smoke_audit_2026-04-17.md` | `goal512-public-doc-smoke-audit` |
| `v0.8` | 2026-04-17 | `accepted` | Goal511 feature guide v0.8 refresh | `docs/reports/goal511_feature_guide_v08_refresh_2026-04-17.md` | `goal511-feature-guide-v08-refresh` |
| `v0.8` | 2026-04-17 | `accepted` | Goal510 Goal509 public documentation follow-through | `docs/reports/goal510_goal509_public_doc_followthrough_2026-04-17.md` | `goal510-goal509-public-doc-followthrough` |
| `v0.8` | 2026-04-17 | `accepted` | Goal509 robot and Barnes-Hut Linux performance evidence | `docs/reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md` | `goal509-robot-barnes-linux-perf` |
| `v0.8.0` | 2026-04-17 | `complete-consensus` | Goal508 Hausdorff Performance Public Doc Refresh | `COMPLETE` | `2026-04-17-goal508-hausdorff-perf-public-doc-refresh` |

## Tracked File Categories

| Category | Count |
| --- | ---: |
| `ad_hoc_review_or_consensus` | 681 |
| `ai_handoff` | 396 |
| `example` | 70 |
| `feature_doc` | 13 |
| `front_page` | 1 |
| `history_index` | 3 |
| `history_support` | 4 |
| `live_goal_doc` | 61 |
| `other` | 482 |
| `release_report` | 49 |
| `report_or_review` | 1523 |
| `script` | 121 |
| `source` | 76 |
| `structured_history_archive` | 1461 |
| `test` | 216 |
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
