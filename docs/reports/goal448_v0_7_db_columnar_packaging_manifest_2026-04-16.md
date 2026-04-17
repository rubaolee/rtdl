# Goal 448: v0.7 DB Columnar Packaging Manifest

Date: 2026-04-16
Author: Codex
Status: Accepted with 2-AI consensus

## Verdict

The v0.7 DB columnar block has a coherent package boundary through Goal 447,
but it must remain unstaged and unmerged until the user explicitly approves a
packaging action.

This manifest is an inventory and staging recommendation, not a release action.

## Current Worktree Shape

Observed from `git status --short` and `git diff --stat` on
2026-04-16:

- Top-level changed entries: 142.
- Tracked modified files: 25.
- Untracked files/directories: 117.
- Tracked diffstat: 25 files changed, 3909 insertions, 53 deletions.
- Top-level distribution: `README.md` 1, `docs` 102, `history` 15,
  `scripts` 9, `src` 13, `tests` 8.

No staging, commit, tag, push, or main merge was performed for this goal.

## Runtime And Native Source Manifest

These files form the implementation surface for the v0.7 DB prepared dataset
and columnar-transfer block:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_prelude.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_prelude.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_workloads.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_core.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_prelude.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/db_perf.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/embree_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/vulkan_runtime.py`

Packaging status: include.

## Test Manifest

These tests are part of the package because they prove correctness,
prepared-dataset behavior, columnar transfer parity, and high-level columnar
defaults:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal432_v0_7_rt_db_phase_split_perf_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal434_v0_7_embree_native_prepared_db_dataset_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal435_v0_7_optix_native_prepared_db_dataset_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal436_v0_7_vulkan_native_prepared_db_dataset_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal440_v0_7_embree_columnar_prepared_db_dataset_transfer_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal441_v0_7_optix_columnar_prepared_db_dataset_transfer_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal442_v0_7_vulkan_columnar_prepared_db_dataset_transfer_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal445_v0_7_high_level_prepared_db_columnar_default_test.py`

Packaging status: include.

## Script Manifest

These scripts generate or summarize the accepted DB prepared-dataset and
PostgreSQL comparison evidence:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal432_db_phase_split_perf_gate.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal434_embree_native_prepared_db_dataset_perf_gate.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal435_optix_native_prepared_db_dataset_perf_gate.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal436_vulkan_native_prepared_db_dataset_perf_gate.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal437_repeated_query_db_perf_summary.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal440_embree_columnar_transfer_perf_gate.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal441_optix_columnar_transfer_perf_gate.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal442_vulkan_columnar_transfer_perf_gate.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal443_columnar_repeated_query_perf_gate.py`

Packaging status: include.

## Release-Facing Documentation Manifest

These files should be included because they expose the current v0.7 DB feature
state to users or maintainers:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/features/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/features/db_workloads/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/quick_tutorial.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/tutorials/db_workloads.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_facing_examples.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/audit_report.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/release_statement.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/support_matrix.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/tag_preparation.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/history/goals/v0_7_goal_sequence_2026-04-15.md`

Packaging status: include.

## Goal, Handoff, Report, And Consensus Manifest

The package should preserve the goal files, handoff files, reports, external
reviews, and Codex consensus notes for Goals 432 through 448.

Primary evidence anchors:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal443_columnar_repeated_query_perf_linux_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal443_v0_7_columnar_repeated_query_perf_gate_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal446_post_columnar_db_regression_linux_2026-04-16.log`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal446_v0_7_post_columnar_db_regression_sweep_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal447_v0_7_db_columnar_packaging_readiness_audit_2026-04-16.md`

Consensus anchors:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal440-v0_7-embree-columnar-prepared-db-dataset-transfer.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal441-v0_7-optix-columnar-prepared-db-dataset-transfer.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal442-v0_7-vulkan-columnar-prepared-db-dataset-transfer.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal443-v0_7-columnar-repeated-query-perf-gate.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal444-v0_7-release-docs-refresh-after-columnar-transfer.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal445-v0_7-high-level-prepared-db-columnar-default.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal446-v0_7-post-columnar-db-regression-sweep.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal447-v0_7-db-columnar-packaging-readiness-audit.md`

Packaging status: include current goal/review/consensus trail.

## Preserved But Not Valid Consensus

The following file is intentionally preserved as a review-trail artifact but
must not be counted as acceptance evidence:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal445_external_review_gemini_attempt_invalid_2026-04-16.md`

The valid Goal 445 review is:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal445_external_review_2026-04-16.md`

The invalid-attempt status note is:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal445_external_review_status_2026-04-16.md`

Packaging recommendation: preserve these files together if preserving the full
review trail; otherwise exclude the invalid attempt from release-facing bundles.

## Hold Conditions

- Do not merge to main yet.
- Do not tag a release yet.
- Do not stage or commit until the user approves a packaging action.
- External tester report intake remains active under Goal 439.
- Goal 446 is a focused post-columnar DB regression sweep, not a full release
  test across the entire repository.
- Performance claims must continue to cite Goal 443 for PostgreSQL-inclusive
  Linux evidence.

## Recommended Staging Strategy

Preferred safe split if the user approves staging later:

1. Runtime, tests, and perf scripts:
   source changes under `src/`, tests under `tests/`, scripts under `scripts/`.
2. Goal evidence and consensus trail:
   `docs/goal_*`, `docs/handoff/*`, `docs/reports/goal43*`,
   `docs/reports/goal44*`, and `history/ad_hoc_reviews/*goal43*/*goal44*`
   as applicable.
3. Release-facing docs:
   `README.md`, tutorial files, feature docs, and `docs/release_reports/v0_7/*`.

Single-commit alternative if the user wants one reviewable package:

- `Add v0.7 DB columnar prepared dataset gates`

## External Review

External review:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal448_external_review_2026-04-16.md`

Verdict: ACCEPT.

Consensus record:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal448-v0_7-db-columnar-packaging-manifest.md`

## Conclusion

The package boundary is explicit enough to support the next packaging decision.
The correct next action is user choice: either keep developing on v0.7, stage a
bounded package, or wait for additional external tester reports.
