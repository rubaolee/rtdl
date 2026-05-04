# Goal1248 v1.0 Release Candidate Package

Date: 2026-05-04

## Purpose

Prepare a draft `v1.0` release-candidate package without changing the current
released version marker or authorizing a tag.

## Files Added

- `docs/release_reports/v1_0/README.md`
- `docs/release_reports/v1_0/release_statement.md`
- `docs/release_reports/v1_0/support_matrix.md`
- `docs/release_reports/v1_0/audit_report.md`
- `docs/release_reports/v1_0/tag_preparation.md`
- `tests/goal1248_v1_0_release_candidate_package_test.py`

## Files Updated

- `docs/README.md` now links the v1.0 release-candidate package from the
  release package section.

## Boundary

The package is explicitly marked:

> Status: draft release candidate for `v1.0`; not released.

The current released version remains `v0.9.8`. This goal does not update
`VERSION`, does not authorize a tag, and does not promote any blocked or
not-reviewed app row into public speedup wording.

## v1.0 Positioning

The package defines `v1.0` as the app-shaped RTDL proof release candidate:

- current docs and examples show a Python-facing RTDL authoring path;
- the app inventory records `18` app rows;
- current NVIDIA RTX public wording remains bounded to `12` reviewed sub-path
  rows;
- v1.0 still accepts app-specific native continuations where needed;
- v1.5 is the generic primitive cleanup target;
- v2.0 is the later end-to-end performance architecture.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1248_v1_0_release_candidate_package_test
Ran 4 tests in 0.004s
OK

PYTHONPATH=src:. python3 -m unittest \
  tests.goal646_public_front_page_doc_consistency_test \
  tests.goal1230_v1_0_app_acceleration_inventory_test \
  tests.goal947_v1_rtx_app_status_page_test
Ran 12 tests in 0.352s
OK
```

An initial `python` invocation failed because this shell does not provide a
`python` executable. The tests were rerun successfully with `python3`.

## Remaining Before v1.0 Release

- External-AI review of this release-candidate package.
- Codex consensus report after external review.
- Final release-candidate audit and agreed release-surface test gate.
- Full local discovery or approved release-equivalent gate.
- Final authorization before changing `VERSION` or tagging.

No immediate pod is required unless the release scope changes to add new public
speedup wording for a blocked or not-reviewed app row.
