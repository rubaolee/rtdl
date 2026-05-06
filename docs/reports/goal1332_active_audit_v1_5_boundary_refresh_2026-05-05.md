# Goal1332 Active Audit v1.5 Boundary Refresh

Date: 2026-05-05

## Scope

Refresh active audit, manifest, and support/status wording so current-main
surfaces no longer require stale pre-pod v1.5 phrasing or stale Goal1224 row
counts.

Historical reports and release artifacts are intentionally unchanged unless an
active audit explicitly checks them as released v1.0 records.

## Changes

- Updated `docs/app_engine_support_matrix.md` to record 13 reviewed public
  wording rows after Goal1263.
- Updated `docs/v1_1_optix_status.md` next-work wording so v1.2/v1.5 text is a
  current roadmap boundary, not stale "should replace" language.
- Updated `scripts/goal1229_current_main_v1_0_readiness_audit.py` and
  `scripts/goal1250_v1_0_release_surface_doc_audit.py` required phrases to
  match the current front page and internally pod-verified v1.5 generic
  primitive boundary.
- Updated `scripts/goal759_rtx_cloud_benchmark_manifest.py` polygon-pair and
  Jaccard comparable metric scopes to describe backend-neutral native summary
  plumbing instead of old native C++ continuation phrasing.

## Boundary

- v1.0 remains the current public release.
- This does not authorize public v1.5 release wording.
- Public speedup wording still requires reviewed exact-subpath evidence and
  the appropriate consensus level.
- Vulkan, HIPRT, and Apple RT remain out of active implementation scope before
  v2.1.

## Local Validation

- `PYTHONPATH=src:. python3 -m unittest tests.goal1250_v1_0_release_surface_doc_audit_test tests.goal1229_current_main_v1_0_readiness_audit_test tests.goal759_rtx_cloud_benchmark_manifest_test tests.goal687_app_engine_support_matrix_test tests.goal938_public_rtx_wording_sync_test tests.goal1010_public_rtx_readme_wording_test`
  - 38 tests OK.
- `PYTHONPATH=src:. python3 -m unittest $(find tests -maxdepth 1 -name 'goal13*_test.py' -exec basename {} .py \; | sed 's/^/tests./')`
  - 76 tests OK.
- `git diff --check`
  - clean.

## Pod Validation

Pending after push.
