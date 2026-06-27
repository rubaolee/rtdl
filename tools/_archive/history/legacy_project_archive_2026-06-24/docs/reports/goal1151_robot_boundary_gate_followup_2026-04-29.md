# Goal1151 Robot Boundary Gate Follow-Up

Date: 2026-04-29

## Scope

Goal1151 updates two remaining live gates that still expected the robot public-wording boundary to contain the older `100 ms` timing-floor phrase:

- `tests/goal847_active_rtx_claim_review_package_test.py`
- `tests/goal978_rtx_speedup_claim_candidate_audit_test.py`

The current robot state is stricter and more precise:

- `robot_collision_screening / prepared_pose_flags` remains `public_wording_blocked`.
- The boundary is now framed around possible future explicit normalized per-pose review.
- Whole-app robot planning speedup remains outside any wording.

Historical reports that mention the older timing-floor decision are not rewritten.

## Verification

Focused follow-up:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal847_active_rtx_claim_review_package_test tests.goal978_rtx_speedup_claim_candidate_audit_test -v
```

Result: 6 tests OK.

Expanded public RTX gate suite:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal847_active_rtx_claim_review_package_test \
  tests.goal848_v1_rt_core_goal_series_test \
  tests.goal937_ready_rtx_claim_review_packet_test \
  tests.goal939_current_rtx_claim_review_package_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal978_rtx_speedup_claim_candidate_audit_test \
  tests.goal1006_public_rtx_claim_wording_gate_test \
  tests.goal1009_public_rtx_wording_review_packet_test \
  tests.goal1010_public_rtx_readme_wording_test \
  tests.goal1011_rtx_public_wording_matrix_test \
  tests.goal1020_public_docs_rtx_boundary_audit_test \
  tests.goal1024_final_public_surface_audit_test \
  tests.goal1025_pre_cloud_rtx_app_batch_readiness_test \
  tests.goal1044_public_rtx_cloud_policy_sync_test \
  tests.goal1109_v1_rtx_readiness_status_after_baselines_test \
  tests.goal1123_public_wording_review_after_goal1121_test \
  tests.goal1126_robot_normalized_public_wording_review_test -v
```

Result: 60 tests OK.

## Codex Verdict

ACCEPT.

The live gates now check the current source-of-truth robot boundary instead of a superseded timing-floor phrase, without authorizing robot public speedup wording.

## External Review Status

Pending Gemini/Claude review before bounded closure under the project 2-AI rule.

