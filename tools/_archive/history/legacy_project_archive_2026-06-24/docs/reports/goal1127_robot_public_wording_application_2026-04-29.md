# Goal1127 Robot Public Wording Application

Date: 2026-04-29

This report applies the Goal1126 three-AI consensus to the current public
surfaces and live audits. It does not add new benchmark evidence, does not start
cloud resources, does not tag or release, and does not authorize any whole-app
speedup claim.

## Applied Decision

Goal1126 accepted exactly one new public wording surface:

`robot_collision_screening / prepared_pose_flags`: RTDL's prepared robot
collision pose-count RTX query sub-path measured 0.178698 s for 64M poses and
917.75x per-pose throughput versus the reviewed 36M chunked Embree any-hit
baseline.

The wording is explicitly normalized per-pose. It is not a same-total-work
wall-time claim and not a whole-app robot-planning claim. Full robot kinematics,
scene construction, ray packing, witness-row output, continuous collision
detection, Python input construction, and whole-app planning speedup remain
outside the wording.

## Updated Surfaces

- `src/rtdsl/app_support_matrix.py`: robot moved to
  `public_wording_reviewed` with Goal1121/Goal1123/Goal1126 evidence and the
  normalized per-pose boundary.
- `README.md`, `docs/v1_0_rtx_app_status.md`,
  `docs/app_engine_support_matrix.md`, `docs/application_catalog.md`,
  `docs/release_facing_examples.md`, and `docs/rtdl_feature_guide.md`: public
  robot wording now matches the accepted normalized language.
- Current audit generators for Goal939, Goal1020, Goal1024, Goal1025, Goal1063,
  Goal1125, Goal947, and Goal848 now reflect the current state: 10 reviewed
  public wording rows, 0 blocked public wording rows, and 6 still-unreviewed
  NVIDIA RTX rows.
- `docs/handoff/REFRESH_LOCAL_2026-04-13.md`: updated so future context
  refreshes carry the current Goal1126 robot boundary instead of the old
  Goal1123 blocked state.

## Current Counts

- NVIDIA-target apps ready for RTX claim review: 16.
- Public wording reviewed rows: 10.
- Public wording blocked rows: 0.
- Public wording not reviewed rows: 6.
- Non-NVIDIA public wording targets: 2.

## Verification

Focused public-surface suite:

`PYTHONPATH=src:. python3 -m unittest tests.goal1010_public_rtx_readme_wording_test tests.goal1011_rtx_public_wording_matrix_test tests.goal947_v1_rtx_app_status_page_test tests.goal848_v1_rt_core_goal_series_test tests.goal939_current_rtx_claim_review_package_test tests.goal1020_public_docs_rtx_boundary_audit_test tests.goal1024_final_public_surface_audit_test tests.goal1025_pre_cloud_rtx_app_batch_readiness_test tests.goal1063_pre_pod_local_completion_audit_test tests.goal1125_unresolved_rtx_public_wording_prioritization_test tests.goal1126_robot_normalized_public_wording_review_test -v`

Result: 43 tests OK.

Compile check:

`python3 -m py_compile scripts/goal939_current_rtx_claim_review_package.py scripts/goal1020_public_docs_rtx_boundary_audit.py scripts/goal1024_final_public_surface_audit.py scripts/goal1025_pre_cloud_rtx_app_batch_readiness.py scripts/goal947_v1_rtx_app_status_page.py scripts/goal1063_pre_pod_local_completion_audit.py scripts/goal1125_unresolved_rtx_public_wording_prioritization.py tests/goal939_current_rtx_claim_review_package_test.py tests/goal1020_public_docs_rtx_boundary_audit_test.py tests/goal1024_final_public_surface_audit_test.py tests/goal1025_pre_cloud_rtx_app_batch_readiness_test.py`

Result: OK.

## Boundary

Historical reports that predate Goal1126 are not rewritten. Their old
`public_wording_blocked` robot decisions are superseded by Goal1126 and this
application report, not retroactively edited.
