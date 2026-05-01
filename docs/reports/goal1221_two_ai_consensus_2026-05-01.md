# Goal1221 Two-AI Consensus: v0.9.8 Release Action

Date: 2026-05-01

## Verdict

`ACCEPT`

Goal1221 is accepted by Codex plus external-AI review.

## Review Trail

- Codex implemented the local release-action edits and validated the focused
  release/public-surface suite.
- Gemini 2.5 Flash was attempted for the external review but returned repeated
  `MODEL_CAPACITY_EXHAUSTED` / HTTP 429 capacity errors.
- Claude CLI was then used as the external-AI reviewer permitted by the RTDL
  2-AI rule. Claude wrote:
  `docs/reports/goal1221_gemini_v0_9_8_release_action_review_2026-05-01.md`.
- Claude verdict: `ACCEPT`.

## Accepted Scope

- `VERSION` is bumped to `v0.9.8`.
- `docs/release_reports/v0_9_8/` is released, not release-prepared.
- Live public docs now identify `v0.9.8` as the current public release.
- `v0.9.6` remains only as historical or previous backend-feature boundary
  wording.
- Public RTX/RT-core claims remain bounded; DB full output and polygon Jaccard
  public speedup wording remain blocked.
- Commit, tag, and push remain separate git operations and must stage only the
  reviewed release file set.

## Validation

Focused release/public-surface suite:

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

Post-review hygiene rerun after removing one stale draft sentence from the
v0.9.8 audit report:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1219_v0_9_8_release_package_test \
  tests.goal1220_v0_9_8_final_authorization_test \
  tests.goal1221_v0_9_8_release_action_test \
  tests.goal1024_final_public_surface_audit_test -v
```

Result: `OK`, 11 tests.

## Boundary

This consensus accepts Goal1221 local release-action edits. It does not itself
perform git commit, git tag, push, upload, package publication, or any cloud
benchmark run.
