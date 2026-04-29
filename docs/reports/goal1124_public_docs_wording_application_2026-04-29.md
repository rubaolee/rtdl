# Goal1124 Public Docs Wording Application

Date: 2026-04-29

## Scope

Goal1124 applies the accepted Goal1123 public wording decision to the live
matrix, public docs, and public-surface audit scripts.

This goal does not authorize release, whole-app speedup claims, default-mode
claims, or public robot speedup wording.

## Applied Decisions

- `facility_knn_assignment / coverage_threshold_prepared_recentered` is now
  `public_wording_reviewed` with narrow wording for the prepared facility
  coverage-threshold RTX query sub-path only.
- `barnes_hut_force_app / node_coverage_prepared_rich` is now
  `public_wording_reviewed` with narrow wording for the prepared Barnes-Hut
  node-coverage RTX query sub-path only.
- `robot_collision_screening / prepared_pose_flags` remains
  `public_wording_blocked`. Goal1121 cleared the 100 ms timing floor, but
  Goal1123 kept public ratio wording blocked until a same-scale or explicitly
  accepted normalized baseline review exists.

## Files Updated

- `src/rtdsl/app_support_matrix.py`
- `README.md`
- `docs/rtdl_feature_guide.md`
- `docs/v1_0_rtx_app_status.md`
- `docs/app_engine_support_matrix.md`
- `docs/release_facing_examples.md`
- `docs/handoff/REFRESH_LOCAL_2026-04-13.md`
- `scripts/goal947_v1_rtx_app_status_page.py`
- `scripts/goal1020_public_docs_rtx_boundary_audit.py`
- `scripts/goal1024_final_public_surface_audit.py`
- `scripts/goal1063_pre_pod_local_completion_audit.py`
- focused tests for the same public wording and audit surfaces

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1010_public_rtx_readme_wording_test tests.goal1011_rtx_public_wording_matrix_test tests.goal1123_public_wording_review_after_goal1121_test tests.goal947_v1_rtx_app_status_page_test tests.goal848_v1_rt_core_goal_series_test tests.goal939_current_rtx_claim_review_package_test tests.goal1063_pre_pod_local_completion_audit_test tests.goal1109_v1_rtx_readiness_status_after_baselines_test -v
```

Result: 35 tests OK.

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1020_public_docs_rtx_boundary_audit_test tests.goal1024_final_public_surface_audit_test tests.goal515_public_command_truth_audit_test -v
```

Result: 5 tests OK.

```text
rg -n "larger RTX repeats stayed below|below the 100 ms public-review timing floor|Goal1008 keeps public speedup wording blocked|facility_knn_assignment.*public_wording_blocked|facility.*speedup wording remains blocked|timing-floor/baseline review" README.md docs/*.md docs/handoff/REFRESH_LOCAL_2026-04-13.md docs/release_facing_examples.md docs/rtdl_feature_guide.md docs/app_engine_support_matrix.md docs/v1_0_rtx_app_status.md src/rtdsl/app_support_matrix.py tests scripts/goal947_v1_rtx_app_status_page.py scripts/goal1020_public_docs_rtx_boundary_audit.py scripts/goal1024_final_public_surface_audit.py scripts/goal1063_pre_pod_local_completion_audit.py
```

Result: no matches.

## Boundary

The update only applies wording already accepted by Goal1123. It keeps the
public RTX claim surface bounded to named prepared query sub-paths and keeps
robot speedup wording blocked.
