# Goal1347 Post-Local-Prep Public Matrix Sync

Date: 2026-05-06

## Scope

Synchronized Goal1133's live public-wording boundary audit with the current
matrix:

- `polygon_pair_overlap_area_rows` now expects `public_wording_reviewed`.
- This matches Goal1263 bounded polygon-pair wording and the current
  `rtdsl.rtx_public_wording_matrix()` state.

## Boundary

This updates an active audit expectation only. It does not change historical
Goal1133 artifacts, public wording text, release state, cloud policy, or backend
implementation.

## Local Validation

- `PYTHONPATH=src:. python3 -m unittest tests.goal1133_post_local_prep_audit_test tests.goal1249_v1_0_release_candidate_audit_test tests.goal1248_v1_0_release_candidate_package_test`
- Result: `OK`, 10 tests.
- `git diff --check`
- Result: `OK`.

## Pod Validation

Pod SSH command:

`ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex`

Validated from Git with `git fetch origin main` and `git reset --hard
origin/main`.

- Pod commit: `8210ef52346b199dd8f275843383ff675dbcf8dc`.
- Pod command: `PYTHONPATH=src:. python3 -m unittest tests.goal848_v1_rt_core_goal_series_test tests.goal1025_pre_cloud_rtx_app_batch_readiness_test tests.goal1051_post_goal1048_followup_plan_test tests.goal1063_pre_pod_local_completion_audit_test tests.goal1125_unresolved_rtx_public_wording_prioritization_test tests.goal1133_post_local_prep_audit_test tests.goal1178_goal1177_public_status_sync_audit_test tests.goal1210_v0_9_8_release_readiness_audit_test tests.goal1216_v0_9_8_release_candidate_audit_test tests.goal1218_v0_9_8_release_authorization_gate_test tests.goal1011_rtx_public_wording_matrix_test tests.goal1010_public_rtx_readme_wording_test tests.goal938_public_rtx_wording_sync_test`
- Pod result: `OK`, 57 tests.
