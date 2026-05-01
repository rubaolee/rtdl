# Goal1152 Public Surface Wording Sync

Date: 2026-04-30

## Scope

Goal1152 fixes release-facing wording that still implied all three Goal1121/Goal1123/Goal1126 public speedup lines were blocked after Goal1142. That became stale after Goal1146:

- `facility_knn_assignment / coverage_threshold_prepared_recentered` is reviewed and public-wording authorized within the bounded Goal1146 scope.
- `barnes_hut_force_app / node_coverage_prepared_rich` is reviewed and public-wording authorized within the bounded Goal1146 scope.
- `robot_collision_screening / prepared_pose_flags` remains blocked for public speedup wording.

This goal updates current public/docs surfaces only. Historical reports are not rewritten.

## Changes

- Updated `scripts/goal947_v1_rtx_app_status_page.py` so generated status prose says Goal1146 re-promoted facility and Barnes-Hut while robot remains blocked.
- Removed the stale robot `917.75x` reviewed-wording row from the status-page reviewed-wording constant.
- Regenerated `docs/v1_0_rtx_app_status.md`.
- Updated the cloud-policy paragraph in `docs/app_engine_support_matrix.md`.
- Regenerated current public command and boundary audit artifacts.

## Verification

Focused public-doc/status tests:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal515_public_command_truth_audit_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal1020_public_docs_rtx_boundary_audit_test \
  tests.goal1024_final_public_surface_audit_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal1010_public_rtx_readme_wording_test \
  tests.goal1011_rtx_public_wording_matrix_test \
  tests.goal1044_public_rtx_cloud_policy_sync_test -v
```

Result: 29 tests OK.

Stale-wording scan over current public surfaces:

```text
rg -n "keeping those three|three public speedup lines blocked|rtx_phase_sec\": \"0\\.178698\"|ratio\": \"917\\.75x\"|robot_collision_screening.*public_wording_reviewed|Goal1123 accepted narrow public wording|Goal1121 robot timing crossed" README.md docs/*.md scripts src tests docs/reports/goal947_v1_rtx_app_status_2026-04-25.json docs/reports/goal939_current_rtx_claim_review_package_2026-04-25.json docs/reports/goal1046_pre_cloud_rtx_app_batch_readiness_2026-04-27.json docs/reports/goal515_public_command_truth_audit_2026-04-17.json
```

Result: no matches.

## Codex Verdict

ACCEPT.

The current public surfaces now match Goal1146 and the live `rtdsl.rtx_public_wording_matrix()` state: facility and Barnes-Hut have bounded reviewed wording; robot remains blocked.

## External Review Status

Pending Gemini/Claude review before bounded closure under the project 2-AI rule.

