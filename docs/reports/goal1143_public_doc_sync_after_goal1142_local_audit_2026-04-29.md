# Goal1143 Public Doc Sync After Goal1142 Local Audit

Date: 2026-04-29

Status: `LOCAL_AUDIT_PASS_EXTERNAL_REVIEW_PENDING`

Goal1143 updates the public RTX wording surface after Goal1142 superseded the
older facility, robot, and Barnes-Hut public-speedup evidence with same-source
current-window artifacts.

## Decision

The public docs now hold public speedup wording for:

- `facility_knn_assignment / coverage_threshold_prepared_recentered`
- `robot_collision_screening / prepared_pose_flags`
- `barnes_hut_force_app / node_coverage_prepared_rich`

These rows still have current Goal1142 RTX evidence, but they are not restored
to reviewed public speedup wording until an external AI review accepts the
Goal1142 replacement packet. This is stricter than the historical Goal1123 and
Goal1126 wording and preserves the project rule that changed public claims need
Codex plus Claude or Gemini.

## Files Synced

- `README.md`
- `docs/v1_0_rtx_app_status.md`
- `docs/app_engine_support_matrix.md`
- `docs/application_catalog.md`
- `docs/release_facing_examples.md`
- `docs/rtdl_feature_guide.md`
- `src/rtdsl/app_support_matrix.py`
- Goal1109, Goal1123, Goal1126, Goal947, Goal1020, and Goal1024 generator/test
  surfaces

## Local Verification

Commands executed:

```bash
PYTHONPATH=src:. python3 scripts/goal1020_public_docs_rtx_boundary_audit.py
PYTHONPATH=src:. python3 scripts/goal1024_final_public_surface_audit.py
PYTHONPATH=src:. python3 -m unittest tests.goal515_public_command_truth_audit_test tests.goal1020_public_docs_rtx_boundary_audit_test tests.goal1024_final_public_surface_audit_test -v
PYTHONPATH=src:. python3 -m unittest tests.goal947_v1_rtx_app_status_page_test tests.goal939_current_rtx_claim_review_package_test tests.goal1010_public_rtx_readme_wording_test tests.goal1011_rtx_public_wording_matrix_test tests.goal1109_v1_rtx_readiness_status_after_baselines_test tests.goal1123_public_wording_review_after_goal1121_test tests.goal1126_robot_normalized_public_wording_review_test tests.goal1020_public_docs_rtx_boundary_audit_test tests.goal1024_final_public_surface_audit_test -v
```

Observed results:

- Goal1020 public docs RTX boundary audit: `valid: True`, `7` docs checked,
  `0` failing docs.
- Goal1024 final public surface audit: `valid: True`, `13` files checked,
  `0` missing files, `0` failing phrase docs.
- Public command and boundary audit tests: `5` tests OK.
- Focused RTX public wording/status suite: `35` tests OK.

## Boundary

This goal is locally audited only. It does not close Goal1142 and does not
authorize the three held public RTX speedup wording rows. Closure still requires
an external Claude or Gemini ACCEPT review followed by a Codex consensus report.
