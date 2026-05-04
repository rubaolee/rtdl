# Goal1253 v1.0 Release Action

Date: 2026-05-04

## Summary

VERDICT: RELEASE ACTION COMPLETE PENDING TAG

This goal performs the authorized v1.0 release action after Goal1252 final
authorization and two-AI consensus.

## Changes

- Updated `VERSION` from `v0.9.8` to `v1.0`.
- Updated the root front page and docs index to identify `v1.0` as the current
  released version.
- Converted `docs/release_reports/v1_0/` from draft release-candidate wording
  to released v1.0 wording.
- Updated release-surface and version-marker tests so they enforce the released
  v1.0 state instead of the prior candidate state.
- Preserved the historical `v0.9.8` release package as an older release
  package.

## Verification

Focused release-action suite:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1248_v1_0_release_candidate_package_test \
  tests.goal1249_v1_0_release_candidate_audit_test \
  tests.goal1250_v1_0_release_surface_doc_audit_test \
  tests.goal1217_version_marker_current_release_sync_test \
  tests.goal1221_v0_9_8_release_action_test \
  tests.goal646_public_front_page_doc_consistency_test \
  tests.goal654_current_main_support_matrix_test

Ran 24 tests in 0.163s

OK
```

Pre-release full local discovery from Goal1251:

```text
Ran 2422 tests in 166.940s

OK (skipped=196)
```

## Boundary

This release action does not authorize new public speedup wording, whole-app
speedup wording, broad all-app NVIDIA RT-core speedup wording, or a claim that
app-specific native continuations have already been removed. The released v1.0
scope remains the app-shaped RTDL proof release documented in
`docs/release_reports/v1_0/`.

## Next Step

Commit this release action, then create the annotated `v1.0` tag on the
release-action commit.
