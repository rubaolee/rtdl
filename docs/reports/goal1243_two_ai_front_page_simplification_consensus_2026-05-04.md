# Goal1243 Two-AI Consensus: Front-Page Simplification

Date: 2026-05-04

Participants:
- Codex
- Gemini (`docs/reports/goal1243_gemini_front_page_simplification_review_2026-05-04.md`)

Scope:
- `README.md`
- `docs/v1_0_rtx_app_status.md`
- `tests/goal1010_public_rtx_readme_wording_test.py`
- `tests/goal938_public_rtx_wording_sync_test.py`

## Verdict

`ACCEPT`

Codex and Gemini agree that the README simplification is safe to commit.

## Consensus Basis

- The README now acts as a shorter public landing page rather than a dense
  claim/evidence report.
- Detailed RTX row, ratio, command, and evidence checks remain in
  `docs/v1_0_rtx_app_status.md` and app support docs.
- The README still preserves current release `v0.9.8`, v1.0/v1.5/v2.0
  positioning, Goal748 robot OptiX erratum wording, and Goal1177/Goal1184
  external-review-only boundaries.
- The public wording count remains `12 reviewed` bounded RTX sub-path rows
  after Goal1224.
- Guard tests now match the intended doc structure: compact front-page anchors
  in README, detailed RTX wording checks in the status/support pages.

## Verification

- `PYTHONPATH=src:. python3 -m unittest tests.goal1231_front_page_simplification_test tests.goal1228_v1_0_positioning_docs_test tests.goal1010_public_rtx_readme_wording_test tests.goal938_public_rtx_wording_sync_test tests.goal1179_public_docs_goal1177_boundary_audit_test tests.goal1180_current_release_readiness_window_audit_test tests.goal751_robot_optix_erratum_doc_test tests.goal1221_v0_9_8_release_action_test tests.goal1217_version_marker_current_release_sync_test`
  - Result: `Ran 26 tests`, `OK`.
- `PYTHONPATH=src:. python3 -m unittest $(rg -l "README.md|docs/README.md|v1_0_rtx_app_status|public docs|front page|app_engine_support_matrix|v1_0_app_acceleration_inventory|current released version|Goal1177|Goal1184|Goal1224|Goal748" tests -g '*test.py' | sed 's#/#.#g; s#.py$##')`
  - Result: `Ran 363 tests`, `OK`.

## Boundary

This consensus covers documentation structure and claim-boundary preservation
only. It does not authorize new public speedup wording, does not change the
current released version, and does not require an NVIDIA pod.
