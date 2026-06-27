# Goal1109 V1 RTX Readiness Status After Goal1146 Public Wording Promotion

Date: 2026-04-29

Valid: `true`

Supersedes: `docs/reports/goal1109_v1_rtx_readiness_status_after_baselines_2026-04-29.json`

Goal1109 refreshes v1 RTX readiness after Goal1142 same-source RTX intake. It does not run cloud, does not authorize release, and does not create new evidence. After Goal1146, Facility and Barnes-Hut have reviewed bounded public RTX sub-path wording; Robot remains engineering-ready but blocked for public speedup wording.

## Summary

| Metric | Value |
| --- | ---: |
| `row_count` | `3` |
| `engineering_comparison_ready_count` | `1` |
| `public_wording_reviewed_count` | `2` |
| `non_cloud_ready_count` | `0` |
| `blocked_count` | `0` |
| `public_speedup_claim_authorized_count` | `2` |

## Rows

| App | Path | Status | Engineering ratio summary | Next action | Claim authorized |
| --- | --- | --- | --- | --- | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared_recentered` | `public_wording_reviewed` | 80.60x vs CPU oracle using query-phase medians; Goal1146 reviewed narrow prepared coverage-threshold public wording | Keep wording limited to the prepared recentered coverage-threshold query decision; do not claim ranked KNN assignment or whole-app speedup. | `True` |
| `robot_collision_screening` | `prepared_pose_flags` | `engineering_review_ready_needs_public_wording_review` | Robot same-source RTX evidence complete: 4096-pose correctness passed; 64M-pose timing crossed the 100 ms floor at 0.178471s median query. Same-scale public ratio still requires wording review. | Run a public wording review that decides whether the 64M RTX timing can be compared to the 36M chunked Embree native-any-hit baseline, and document any normalization limits. | `False` |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | `public_wording_reviewed` | 240.56x vs Embree using query-phase medians; Goal1146 reviewed narrow prepared node-coverage public wording | Keep wording limited to the prepared depth-8 node-coverage threshold traversal; do not claim opening-rule, force-vector, N-body, or whole-app speedup. | `True` |

## Boundary

Goal1109 refreshes v1 RTX readiness after Goal1142 same-source RTX intake. It does not run cloud, does not authorize release, and does not create new evidence. After Goal1146, Facility and Barnes-Hut have reviewed bounded public RTX sub-path wording; Robot remains engineering-ready but blocked for public speedup wording.
