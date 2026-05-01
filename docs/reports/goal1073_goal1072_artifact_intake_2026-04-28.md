# Goal1073 Goal1072 Artifact Intake

Date: 2026-04-28

Overall status: `needs_cloud_artifacts`

This intake checks copied Goal1072 artifacts only. It does not run cloud, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.

## Summary

- expected artifacts: `4`
- present artifacts: `0`
- missing artifacts: `4`
- validation passed: `0`
- timing floor passed: `0`
- timing below floor: `0`
- blocked rows: `0`
- excluded rows: `1`
- public speedup claims authorized: `0`

## Rows

| App | Path | Phase | Artifact | Review status | RTX phase | Reason |
| --- | --- | --- | --- | --- | ---: | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `correctness_validation` | `missing` | `needs_cloud_artifact` | `` | expected Goal1072 artifact has not been copied back from the pod |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `large_timing_repeat` | `missing` | `needs_cloud_artifact` | `` | expected Goal1072 artifact has not been copied back from the pod |
| `robot_collision_screening` | `prepared_pose_flags` | `correctness_validation` | `missing` | `needs_cloud_artifact` | `` | expected Goal1072 artifact has not been copied back from the pod |
| `robot_collision_screening` | `prepared_pose_flags` | `large_timing_repeat` | `missing` | `needs_cloud_artifact` | `` | expected Goal1072 artifact has not been copied back from the pod |

## Excluded Rows

- `barnes_hut_force_app / node_coverage_prepared`: `blocked_contract_reframe_required`; The current Barnes-Hut node-coverage contract builds only four one-level quadtree nodes. The 1M-body pod run produced a 0.004204 s median RT query, so blind body-count scaling mostly measures input construction/packing rather than meaningful RTX traversal.

## Boundary

This intake checks copied Goal1072 artifacts only. It does not run cloud, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.
