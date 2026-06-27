# Goal1221 Gemini Review Request: v0.9.8 Release Action

Date: 2026-05-01

You are reviewing Goal1221 as the required external-AI side of RTDL's
2-AI consensus rule. Please review the saved release-action edits and decide
whether Goal1221 can be accepted.

## Context

Goal1220 already authorized the v0.9.8 release action after Goal1216-1219
release-candidate audit, package review, and final authorization evidence.
Goal1221 performs only the local release-action edits:

- bump `VERSION` from `v0.9.6` to `v0.9.8`
- convert `docs/release_reports/v0_9_8/` from release-prepared to released
  wording
- update live public release pointers in the root README, docs index,
  current-main support matrix, complete history map, and revision dashboard
- preserve older v0.9.6 wording where it is historical or an explicit previous
  backend-feature boundary
- keep commit, tag, and push as separate git operations after review

## Files To Inspect

- `VERSION`
- `README.md`
- `docs/README.md`
- `docs/current_main_support_matrix.md`
- `docs/release_reports/v0_9_8/README.md`
- `docs/release_reports/v0_9_8/release_statement.md`
- `docs/release_reports/v0_9_8/support_matrix.md`
- `docs/release_reports/v0_9_8/audit_report.md`
- `docs/release_reports/v0_9_8/tag_preparation.md`
- `history/COMPLETE_HISTORY.md`
- `history/revision_dashboard.md`
- `docs/reports/goal1220_two_ai_consensus_2026-05-01.md`
- `docs/reports/goal1221_v0_9_8_release_action_2026-05-01.md`
- `tests/goal1221_v0_9_8_release_action_test.py`

## Validation Already Run By Codex

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal532_v0_8_release_authorization_test \
  tests.goal645_v0_9_5_release_package_test \
  tests.goal646_public_front_page_doc_consistency_test \
  tests.goal654_current_main_support_matrix_test \
  tests.goal655_tutorial_example_current_main_consistency_test \
  tests.goal684_v0_9_6_release_level_flow_audit_test \
  tests.goal1022_history_release_drift_audit_test \
  tests.goal1024_final_public_surface_audit_test \
  tests.goal1217_version_marker_current_release_sync_test \
  tests.goal1218_v0_9_8_release_authorization_gate_test \
  tests.goal1219_v0_9_8_release_package_test \
  tests.goal1220_v0_9_8_final_authorization_test \
  tests.goal1221_v0_9_8_release_action_test -v
```

Result: `OK`, 39 tests.

## Review Questions

1. Is the `VERSION` bump to `v0.9.8` justified by Goal1220 final authorization?
2. Do the release package and live public docs consistently say v0.9.8 is
   released/current without leaving v0.9.6 as the current public release?
3. Are public RTX/RT-core claims still bounded, especially for DB full output,
   polygon Jaccard, whole-app speedup, and backend-flag-only claims?
4. Is it correct that commit/tag/push remain separate operations after this
   review, rather than silently bundled into Goal1221?

Please write your verdict as `ACCEPT` or `BLOCK`, with concise reasons and any
required fixes. If you cannot write directly to the repo, return the verdict in
stdout so Codex can save it verbatim into `docs/reports/`.
