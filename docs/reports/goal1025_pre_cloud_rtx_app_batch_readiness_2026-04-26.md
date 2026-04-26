# Goal1025 Pre-Cloud RTX App Batch Readiness

Date: 2026-04-26

This pre-cloud audit checks readiness coverage only. It does not run cloud, tag, release, or authorize public RTX speedup claims.

## Summary

- valid: `True`
- public apps: `18`
- active manifest entries: `8`
- deferred manifest entries: `9`
- missing NVIDIA targets: `0`
- unexpected non-NVIDIA manifest targets: `0`
- public wording reviewed apps: `7`
- public wording blocked apps: `['robot_collision_screening']`
- RTX hardware precondition present: `True`
- manifest blocks speedup claims: `True`

## Cloud Policy

Do not start a paid pod for one app. The next pod should run the manifest as one consolidated active+deferred regression/tuning batch after local checks are clean.

## App Rows

| App | Readiness | Maturity | Public wording | Manifest buckets | Paths |
|---|---|---|---|---|---:|
| `database_analytics` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_not_reviewed` | `active` | 2 |
| `graph_analytics` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_not_reviewed` | `deferred` | 1 |
| `apple_rt_demo` | `exclude_from_rtx_app_benchmark` | `not_nvidia_rt_core_target` | `not_nvidia_public_wording_target` | `` | 0 |
| `service_coverage_gaps` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_reviewed` | `active` | 1 |
| `event_hotspot_screening` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_not_reviewed` | `active` | 1 |
| `facility_knn_assignment` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_reviewed` | `active` | 1 |
| `road_hazard_screening` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_not_reviewed` | `deferred` | 1 |
| `segment_polygon_hitcount` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_reviewed` | `deferred` | 1 |
| `segment_polygon_anyhit_rows` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_reviewed` | `deferred` | 1 |
| `polygon_pair_overlap_area_rows` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_not_reviewed` | `deferred` | 1 |
| `polygon_set_jaccard` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_not_reviewed` | `deferred` | 1 |
| `hausdorff_distance` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_not_reviewed` | `deferred` | 1 |
| `ann_candidate_search` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_reviewed` | `deferred` | 1 |
| `outlier_detection` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_reviewed` | `active` | 1 |
| `dbscan_clustering` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_reviewed` | `active` | 1 |
| `robot_collision_screening` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_blocked` | `active` | 1 |
| `barnes_hut_force_app` | `ready_for_rtx_claim_review` | `rt_core_ready` | `public_wording_not_reviewed` | `deferred` | 1 |
| `hiprt_ray_triangle_hitcount` | `exclude_from_rtx_app_benchmark` | `not_nvidia_rt_core_target` | `not_nvidia_public_wording_target` | `` | 0 |

## Duplicate Commands

- `prepared_fixed_radius_density_summary, prepared_fixed_radius_core_flags` reuse one command; runner may reuse duplicate command output in one paid session.

## Boundary

This pre-cloud audit checks readiness coverage only. It does not run cloud, tag, release, or authorize public RTX speedup claims.

