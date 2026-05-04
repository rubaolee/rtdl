# Goal1248 Two-AI Consensus: v1.0 Release Candidate Package

Date: 2026-05-04

## Scope

This consensus covers the draft `v1.0` release-candidate package only:

- `docs/release_reports/v1_0/README.md`
- `docs/release_reports/v1_0/release_statement.md`
- `docs/release_reports/v1_0/support_matrix.md`
- `docs/release_reports/v1_0/audit_report.md`
- `docs/release_reports/v1_0/tag_preparation.md`
- `docs/README.md` release-package links
- `tests/goal1248_v1_0_release_candidate_package_test.py`

It does not release `v1.0`, does not update `VERSION`, does not authorize a
tag, and does not promote blocked or not-reviewed app rows into public speedup
wording.

## External-AI Review

Gemini first returned `REQUEST_CHANGES` because the support-matrix labels used
friendly phase names that did not exactly match the source-of-truth reviewed
rows in `docs/v1_0_rtx_app_status.md`. The valid findings were:

- avoid describing `facility_knn_assignment` as KNN when the reviewed sub-path
  is `coverage_threshold_prepared_recentered`;
- avoid describing `service_coverage_gaps` as nearest-service when the reviewed
  sub-path is `prepared_gap_summary`;
- align all reviewed support-matrix phase names to
  `docs/v1_0_rtx_app_status.md`;
- remove duplicate current-release wording from `docs/README.md`;
- update the new test expectations.

After fixes, Gemini re-reviewed and returned `VERDICT: ACCEPT`.

Review files:

- `docs/reports/goal1248_gemini_v1_0_release_candidate_package_review_2026-05-04.md`
- `docs/reports/goal1248_gemini_v1_0_release_candidate_package_rereview_2026-05-04.md`

## Codex Review

Codex accepts the fixed package:

- All five package files are marked `Status: draft release candidate for
  v1.0; not released.`
- The current released version remains `v0.9.8`.
- The support matrix uses exact reviewed phase names from
  `docs/v1_0_rtx_app_status.md`.
- The package keeps v1.0 as a foundation/proof release, v1.5 as generic
  primitive cleanup, and v2.0 as the later end-to-end performance architecture.
- No broad whole-app or all-app RT-core speedup claim is introduced.
- No pod is required unless the release scope changes to add new public speedup
  wording for blocked or not-reviewed rows.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1248_v1_0_release_candidate_package_test
Ran 4 tests in 0.001s
OK

PYTHONPATH=src:. python3 -m unittest \
  tests.goal646_public_front_page_doc_consistency_test \
  tests.goal1230_v1_0_app_acceleration_inventory_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal1217_version_marker_current_release_sync_test
Ran 14 tests in 0.280s
OK
```

## Consensus Verdict

ACCEPT.

Goal1248 is complete as a v1.0 release-candidate package-preparation step. The
next v1.0 work is final release-candidate audit, release-surface test gate, full
local discovery or approved release-equivalent gate, final external review, and
explicit authorization before changing `VERSION` or tagging.
