# Goal1221 v0.9.8 Release Action

Date: 2026-05-01

## Purpose

Goal1221 performs the local release-action edits authorized by Goal1220.

## Changes

- Bumped `VERSION` from `v0.9.6` to `v0.9.8`.
- Converted `docs/release_reports/v0_9_8/` from release-prepared wording to
  released `v0.9.8` wording.
- Updated the root README, docs index, current-main support matrix, complete
  history map, and revision dashboard so live public pointers identify
  `v0.9.8` as the current public release.
- Preserved `v0.9.6` wording only where it remains historical or explicitly
  describes the previous backend-feature release boundary.
- Updated release package, public-doc drift, and release-action tests to
  validate released status.

## Boundary

This report records local release-action edits. Commit, tag, and push are
separate git operations and must include only the reviewed release file set.

## Validation

Run:

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
