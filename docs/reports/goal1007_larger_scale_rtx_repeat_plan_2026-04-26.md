# Goal1007 Larger-Scale RTX Repeat Plan

Date: 2026-04-26

Goal1007 prepares larger-scale RTX repeats for held Goal1006 candidates. It does not start cloud resources and does not authorize speedup claims.

## Summary

- status: `ok`
- held candidates: `7`
- targets: `7`
- executable commands: `6`

## Targets

| App | Path | Command? | Reason | Risk note |
|---|---|---:|---|---|
| `robot_collision_screening` | `prepared_pose_flags` | `True` | Increase ray count enough that warm pose-count query should exceed the 100 ms wording floor. | High memory run: 8M poses means 32M packed rays; intended for 24GB+ RTX pods and may need downscaling if VRAM pressure appears. |
| `outlier_detection` | `prepared_fixed_radius_density_summary` | `True` | Raise tiled point count for scalar threshold-count traversal. | Moderate memory run: 3.2M points; if pod memory is tight, reduce copies before changing semantics. |
| `dbscan_clustering` | `prepared_fixed_radius_core_flags` | `False` | Same fixed-radius command emits both outlier and DBSCAN scalar summaries. | No separate command; validate both app records from the shared fixed-radius JSON. |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `True` | Raise facility service-coverage copies for a stable threshold query phase. | Moderate memory run: 3.2M build/query points; validation is skipped for cost control. |
| `segment_polygon_hitcount` | `segment_polygon_hitcount_native_experimental` | `True` | Raise segment/polygon copies for native hitcount traversal while keeping validation skipped for cost control. | Output is scalar hitcount summary, so memory risk is mostly geometry/ray staging. |
| `segment_polygon_anyhit_rows` | `segment_polygon_anyhit_rows_prepared_bounded_gate` | `True` | Raise bounded pair-row copies and capacity; output remains bounded and overflow must stay false. | Bounded output capacity is raised to 131072; any overflow keeps this row out of public wording. |
| `ann_candidate_search` | `candidate_threshold_prepared` | `True` | Raise ANN candidate copies for stable threshold-query timing. | Moderate memory run: 2.4M query/candidate points; validation is skipped for cost control. |

## Boundary

Goal1007 prepares larger-scale RTX repeats for held Goal1006 candidates. It does not start cloud resources and does not authorize speedup claims.
