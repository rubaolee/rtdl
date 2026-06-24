# Goal1122 Post-Goal1121 Readiness Refresh Report

Date: 2026-04-29

## Scope

Goal1122 refreshes the v1 RTX readiness status after Goal1121 copied back current-source RTX A5000 artifacts and closed them with 2-AI consensus.

This is a documentation/status refresh only. It does not run cloud, authorize release, change public wording, or authorize public RTX speedup claims.

## Change

The readiness generator now records that the same-source RTX rerun has happened:

- `facility_knn_assignment / coverage_threshold_prepared_recentered` is now `engineering_review_ready_needs_public_wording_review`.
- `robot_collision_screening / prepared_pose_flags` is now `engineering_review_ready_needs_public_wording_review`.
- `barnes_hut_force_app / node_coverage_prepared_rich` is now `engineering_review_ready_needs_public_wording_review`.

The refreshed status points at Goal1121 artifacts and consensus instead of saying the next action is a future same-source RTX rerun.

## Evidence Summary

| App | Current-source RTX evidence | Query median | Status |
| --- | --- | ---: | --- |
| `facility_knn_assignment` | `facility_recentered_coverage_threshold_2_5m_optix_validation.json` | `0.103119` | engineering-review ready |
| `robot_collision_screening` | `robot_prepared_pose_flags_validation.json` and `robot_prepared_pose_flags_64m_timing_goal1121.json` | `0.178698` for 64M timing | engineering-review ready |
| `barnes_hut_force_app` | `barnes_hut_depth8_4096_validation.json` and `barnes_hut_depth8_20m_timing.json` | `0.240634` for 20M timing | engineering-review ready |

## Ratio Notes

Facility and Barnes-Hut now use the Goal1121 current-source RTX query medians in the readiness text:

- Facility: `87.24x` vs CPU oracle and `289.05x` vs Embree using query-phase medians.
- Barnes-Hut: `222.19x` vs Embree using query-phase medians.

Robot is intentionally not converted into a public ratio in this refresh. The 64M RTX timing row is reviewable and crosses the timing floor, but the public wording review must decide how to normalize the 64M RTX row against the 36M chunked Embree baseline before any ratio is made public.

## Verification

```text
PYTHONPATH=src:. python3 scripts/goal1109_v1_rtx_readiness_status_after_baselines.py
```

Result:

```text
{"blocked_count": 0, "engineering_comparison_ready_count": 3, "non_cloud_ready_count": 0, "public_speedup_claim_authorized_count": 0, "row_count": 3, "valid": true}
```

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1109_v1_rtx_readiness_status_after_baselines_test -v
```

Result: 3 tests OK.

## Boundary

No public speedup claim is authorized. The new status means the three current RTX evidence rows are ready for separate public wording review, not that README/front-page wording can already quote speedups.
