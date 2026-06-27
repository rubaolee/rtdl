# Goal1246 Two-AI Consensus: Front-Page Diet

Date: 2026-05-04

Participants:
- Codex
- Claude (`docs/reports/goal1246_claude_front_page_diet_review_2026-05-04.md`)

Scope:
- `README.md`
- `docs/README.md`
- `docs/application_catalog.md`
- `docs/release_facing_examples.md`
- `scripts/goal1020_public_docs_rtx_boundary_audit.py`
- `scripts/goal1179_public_docs_goal1177_boundary_audit.py`
- `scripts/goal1180_current_release_readiness_window_audit.py`
- `scripts/goal1185_goal1184_public_status_sync_audit.py`
- affected public-doc guard tests

## Verdict

`ACCEPT`

Codex and Claude agree that the front-page diet is safe to commit.

## Consensus Basis

- The root README is now a true landing page: it drops from 191 lines to 114
  lines in the first diet pass and is `117` lines in the final patch after
  adding compact navigation links required by existing public-doc guards.
- Detailed Goal1177, Goal748, Goal509, v0.8, v0.9.5, and fixed-radius summary
  guardrails remain in second-level docs, status pages, release-facing example
  docs, and tests.
- `README.md` keeps only compact public claim boundaries: `--backend optix` is
  not a public RT-core claim, reviewed rows are bounded sub-path wording, and
  support matrix/inventory pages are authoritative.
- The Goal1179/Goal1180 audit scripts no longer treat the root README as a
  historical Goal1177 boundary surface, which matches the new front-page role.
- Goal1020 and Goal1185 audits also no longer treat the root README as the
  detailed historical RTX-boundary/status-sync ledger.
- No new NVIDIA RTX public speedup wording, backend maturity claim, or release
  authorization is introduced.

## Verification

- `PYTHONPATH=src:. python3 -m unittest tests.goal1231_front_page_simplification_test tests.goal1232_public_doc_map_test tests.goal1228_v1_0_positioning_docs_test tests.goal645_v0_9_5_release_package_test tests.goal532_v0_8_release_authorization_test tests.goal506_public_entry_v08_alignment_test tests.goal510_app_perf_doc_refresh_test tests.goal700_fixed_radius_summary_public_doc_test tests.goal1010_public_rtx_readme_wording_test tests.goal751_robot_optix_erratum_doc_test tests.goal1179_public_docs_goal1177_boundary_audit_test tests.goal1180_current_release_readiness_window_audit_test tests.goal1217_version_marker_current_release_sync_test tests.goal1221_v0_9_8_release_action_test`
  - Result: `Ran 43 tests`, `OK`.
- `PYTHONPATH=src:. python3 -m unittest tests.goal1231_front_page_simplification_test tests.goal1232_public_doc_map_test tests.goal1228_v1_0_positioning_docs_test tests.goal645_v0_9_5_release_package_test tests.goal532_v0_8_release_authorization_test tests.goal506_public_entry_v08_alignment_test tests.goal510_app_perf_doc_refresh_test tests.goal700_fixed_radius_summary_public_doc_test tests.goal1010_public_rtx_readme_wording_test tests.goal751_robot_optix_erratum_doc_test tests.goal1179_public_docs_goal1177_boundary_audit_test tests.goal1180_current_release_readiness_window_audit_test tests.goal1217_version_marker_current_release_sync_test tests.goal1221_v0_9_8_release_action_test tests.goal1020_public_docs_rtx_boundary_audit_test tests.goal1185_goal1184_public_status_sync_audit_test tests.goal531_v0_8_release_candidate_public_links_test tests.goal938_public_rtx_wording_sync_test`
  - Result: `Ran 55 tests`, `OK`.
- `PYTHONPATH=src:. python3 -m unittest $(rg -l "README.md|front page|public docs|release_facing_examples|Goal1177|Goal748|Goal509|v0\\.8|v0\\.9\\.5|rt_count_threshold_prepared|rt_core_flags_prepared|current released version|v1_0_rtx_app_status" tests -g '*test.py' | sed 's#/#.#g; s#.py$##')`
  - Result: `Ran 345 tests`, `OK (skipped=2)`.

## Boundary

This consensus covers README slimming and public-doc guard relocation only. It
does not release v1.0, does not change the current released version, does not
authorize new public speedup wording, and does not require an NVIDIA pod.
