# Goal 455: v0.7 Post-454 Packaging Manifest Refresh

Date: 2026-04-16
Author: Codex
Status: Accepted with 2-AI consensus

## Verdict

The v0.7 DB package boundary should be refreshed to include Goals 450-454 before
any future staging decision. This remains a non-destructive manifest update; no
staging, commit, tag, push, merge, or release action is authorized.

## Current Worktree Shape

Observed on 2026-04-16:

- `git status --short` entries: 207.
- Top-level distribution:
  - `README.md`: 1
  - `docs`: 149
  - `history`: 22
  - `scripts`: 13
  - `src`: 13
  - `tests`: 8
  - `rtdsl_current.tar.gz`: 1

The archive `rtdsl_current.tar.gz` is not part of the source package manifest
and should not be staged by default.

## Already Established Package Core

Goal 448/449 already captured the core v0.7 DB columnar package:

- runtime/native source changes under `src/`
- tests for Goals 432, 434-436, 440-442, and 445
- scripts through Goal 443 and Goal 449
- release-facing docs
- goal/report/handoff/consensus trail through Goal 449

Goal 455 keeps that boundary and extends it with Goals 450-454.

## Additions Since Goal 449

### Goal 450: Linux Correctness And Performance Refresh

Include:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_450_v0_7_linux_correctness_and_performance_refresh.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/handoff/GOAL450_SINGLE_SENTENCE_EXTERNAL_REVIEW_REQUEST_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/linux_correctness_db_sweep_with_postgresql_2026-04-16.log`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/linux_perf_goal443_columnar_repeated_query_2026-04-16.log`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal450_columnar_repeated_query_perf_linux_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal450_v0_7_linux_correctness_and_performance_refresh_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal450_v0_7_linux_correctness_and_performance_refresh_review_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal450_external_review_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal450-v0_7-linux-correctness-and-performance-refresh.md`

### Goal 451: PostgreSQL Baseline Index Audit

Include:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_451_v0_7_postgresql_baseline_index_audit.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal451_postgresql_baseline_index_audit.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/handoff/GOAL451_SINGLE_SENTENCE_EXTERNAL_REVIEW_REQUEST_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal451_postgresql_baseline_index_audit_linux_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal451_v0_7_postgresql_baseline_index_audit_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal451_v0_7_postgresql_baseline_index_audit_review_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal451_external_review_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal451-v0_7-postgresql-baseline-index-audit.md`

### Goal 452: RTDL vs Best-Tested PostgreSQL Rebase

Include:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_452_v0_7_rtdl_vs_best_tested_postgresql_perf_rebase.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal452_rtdl_vs_best_tested_postgresql_perf_rebase.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/handoff/GOAL452_SINGLE_SENTENCE_EXTERNAL_REVIEW_REQUEST_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal452_rtdl_vs_best_tested_postgresql_perf_rebase_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal452_v0_7_rtdl_vs_best_tested_postgresql_perf_rebase_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal452_v0_7_rtdl_vs_best_tested_postgresql_perf_rebase_review_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal452_external_review_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal452_external_review_status_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal452_external_review_gemini_attempt_overbroad_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal452-v0_7-rtdl-vs-best-tested-postgresql-perf-rebase.md`

The overbroad Gemini attempt is preserved as invalid review history and must not
be counted as consensus.

### Goal 453: Release-Facing Performance Wording Refresh

Include:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_453_v0_7_release_facing_performance_wording_refresh.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/handoff/GOAL453_SINGLE_SENTENCE_EXTERNAL_REVIEW_REQUEST_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal453_v0_7_release_facing_performance_wording_refresh_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal453_v0_7_release_facing_performance_wording_refresh_review_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal453_external_review_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal453-v0_7-release-facing-performance-wording-refresh.md`

Also include the release-facing docs changed by this goal:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/features/db_workloads/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/tutorials/db_workloads.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_facing_examples.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/release_statement.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/support_matrix.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/audit_report.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/tag_preparation.md`

### Goal 454: Post-Wording Evidence Package Validation

Include:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_454_v0_7_post_wording_evidence_package_validation.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal454_post_wording_evidence_package_validation.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/handoff/GOAL454_SINGLE_SENTENCE_EXTERNAL_REVIEW_REQUEST_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal454_post_wording_evidence_package_validation_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal454_v0_7_post_wording_evidence_package_validation_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal454_v0_7_post_wording_evidence_package_validation_review_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal454_external_review_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal454-v0_7-post-wording-evidence-package-validation.md`

## Exclude By Default

Exclude from any source staging/package action unless the user explicitly asks:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/rtdsl_current.tar.gz`

Rationale: it is an archive artifact, not source, tests, scripts, docs, or
consensus evidence.

## Recommended Safe Staging Split

If the user later approves staging, use this split:

1. Runtime and executable validation assets:
   - `src/`
   - `tests/`
   - `scripts/`
2. Goal docs, reports, handoffs, and consensus evidence:
   - `docs/goal_*`
   - `docs/handoff/*`
   - `docs/reports/goal*`
   - `docs/reports/linux_*`
   - `history/ad_hoc_reviews/*`
3. Public and release-facing docs:
   - `README.md`
   - `docs/README.md`
   - `docs/features/README.md`
   - `docs/features/db_workloads/README.md`
   - `docs/tutorials/db_workloads.md`
   - `docs/release_facing_examples.md`
   - `docs/release_reports/v0_7/*`
   - `docs/history/goals/v0_7_goal_sequence_2026-04-15.md`

Do not include `rtdsl_current.tar.gz` in any of those source/doc staging groups.

## Current Hold Conditions

- Do not merge to main.
- Do not tag a release.
- Do not stage or commit until the user explicitly approves.
- Treat Goal 452 as canonical performance wording.
- Treat Goal 450 as historical indexed-baseline evidence.
- Preserve invalid review attempts as history only, not consensus.

## Conclusion

The v0.7 DB package manifest is ready for a future user-approved staging
decision, but this goal does not perform or authorize that action.

## External Review

External review:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal455_external_review_2026-04-16.md`

Verdict: ACCEPT.

Consensus record:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal455-v0_7-post-454-packaging-manifest-refresh.md`
