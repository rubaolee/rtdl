# Goal1222 v0.9.8 Release Commit Staging Inventory

Date: 2026-05-01

## Purpose

This inventory prevents an unsafe `git add -A` before the v0.9.8 release commit
and tag. The worktree contains many unrelated or earlier-goal dirty files, so
the release commit must be staged deliberately.

## Current Release-Action State

- Goal1221 local release-action edits are accepted by two-AI consensus.
- `VERSION` is `v0.9.8`.
- `docs/release_reports/v0_9_8/` is released, not release-prepared.
- Live public docs identify `v0.9.8` as the current public release.
- `v0.9.8` tag does not exist yet.
- Commit, tag, and push have not been performed.

## Reviewed v0.9.8 Release-Flow File Set

Tracked modified files directly touched by the v0.9.8 release action:

- `VERSION`
- `README.md`
- `docs/README.md`
- `docs/current_main_support_matrix.md`
- `history/COMPLETE_HISTORY.md`
- `history/revision_dashboard.md`
- `scripts/goal1022_history_release_drift_audit.py`
- `scripts/goal1024_final_public_surface_audit.py`
- `tests/goal1022_history_release_drift_audit_test.py`
- `tests/goal532_v0_8_release_authorization_test.py`
- `tests/goal645_v0_9_5_release_package_test.py`
- `tests/goal646_public_front_page_doc_consistency_test.py`
- `tests/goal654_current_main_support_matrix_test.py`
- `tests/goal655_tutorial_example_current_main_consistency_test.py`
- `tests/goal684_v0_9_6_release_level_flow_audit_test.py`

New v0.9.8 release-flow files:

- `docs/release_reports/v0_9_8/README.md`
- `docs/release_reports/v0_9_8/release_statement.md`
- `docs/release_reports/v0_9_8/support_matrix.md`
- `docs/release_reports/v0_9_8/audit_report.md`
- `docs/release_reports/v0_9_8/tag_preparation.md`
- `docs/handoff/GOAL1216_CLAUDE_V0_9_8_RELEASE_CANDIDATE_AUDIT_REVIEW_REQUEST_2026-05-01.md`
- `docs/handoff/GOAL1217_GEMINI_VERSION_MARKER_SYNC_REVIEW_REQUEST_2026-05-01.md`
- `docs/handoff/GOAL1218_GEMINI_V0_9_8_RELEASE_AUTHORIZATION_GATE_REVIEW_REQUEST_2026-05-01.md`
- `docs/handoff/GOAL1219_GEMINI_V0_9_8_RELEASE_PACKAGE_REVIEW_REQUEST_2026-05-01.md`
- `docs/handoff/GOAL1220_GEMINI_V0_9_8_FINAL_AUTHORIZATION_REVIEW_REQUEST_2026-05-01.md`
- `docs/handoff/GOAL1221_GEMINI_V0_9_8_RELEASE_ACTION_REVIEW_REQUEST_2026-05-01.md`
- `docs/reports/goal1216_claude_v0_9_8_release_candidate_audit_review_2026-05-01.md`
- `docs/reports/goal1216_two_ai_consensus_2026-05-01.md`
- `docs/reports/goal1216_v0_9_8_release_candidate_audit_2026-05-01.json`
- `docs/reports/goal1216_v0_9_8_release_candidate_audit_2026-05-01.md`
- `docs/reports/goal1217_gemini_version_marker_sync_review_2026-05-01.md`
- `docs/reports/goal1217_two_ai_consensus_2026-05-01.md`
- `docs/reports/goal1217_version_marker_current_release_sync_2026-05-01.md`
- `docs/reports/goal1218_gemini_v0_9_8_release_authorization_gate_review_2026-05-01.md`
- `docs/reports/goal1218_two_ai_consensus_2026-05-01.md`
- `docs/reports/goal1218_v0_9_8_release_authorization_gate_2026-05-01.json`
- `docs/reports/goal1218_v0_9_8_release_authorization_gate_2026-05-01.md`
- `docs/reports/goal1219_external_review_pending_2026-05-01.md`
- `docs/reports/goal1219_gemini_v0_9_8_release_package_review_2026-05-01.md`
- `docs/reports/goal1219_two_ai_consensus_2026-05-01.md`
- `docs/reports/goal1219_v0_9_8_release_package_2026-05-01.md`
- `docs/reports/goal1220_gemini_v0_9_8_final_authorization_review_2026-05-01.md`
- `docs/reports/goal1220_two_ai_consensus_2026-05-01.md`
- `docs/reports/goal1220_v0_9_8_final_authorization_2026-05-01.md`
- `docs/reports/goal1221_gemini_v0_9_8_release_action_review_2026-05-01.md`
- `docs/reports/goal1221_two_ai_consensus_2026-05-01.md`
- `docs/reports/goal1221_v0_9_8_release_action_2026-05-01.md`
- `scripts/goal1216_v0_9_8_release_candidate_audit.py`
- `scripts/goal1218_v0_9_8_release_authorization_gate.py`
- `tests/goal1216_v0_9_8_release_candidate_audit_test.py`
- `tests/goal1217_version_marker_current_release_sync_test.py`
- `tests/goal1218_v0_9_8_release_authorization_gate_test.py`
- `tests/goal1219_v0_9_8_release_package_test.py`
- `tests/goal1220_v0_9_8_final_authorization_test.py`
- `tests/goal1221_v0_9_8_release_action_test.py`

## Dirty-Worktree Risk

The repository also contains many other modified and untracked files from
Goals1135-1208 and related RTX work, including source/runtime files under
`src/`, example files under `examples/`, many scripts, many tests, and many
reports. These must not be swept into the release commit accidentally.

## Recommended Next Step

Do not run `git add -A`.

Before tagging `v0.9.8`, choose one of these release strategies:

- **Conservative release-doc tag:** stage only the reviewed v0.9.8 release-flow
  file set listed above, commit it, and tag that commit. This is safe for docs
  and release evidence, but it does not capture the broader dirty source work.
- **Full current-work release tag:** first audit and stage the prior RTX
  source/docs/tests/reports that the v0.9.8 public status depends on, then
  commit and tag. This is more complete but needs a larger staging audit.

## Boundary

This is an inventory only. It does not stage, commit, tag, push, or publish.
