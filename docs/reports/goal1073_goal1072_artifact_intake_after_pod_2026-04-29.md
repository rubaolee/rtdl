# Goal1073 Goal1072 Artifact Intake

Date: 2026-04-28

Overall status: `ready_for_public_wording_review`

This intake checks copied Goal1072 artifacts only. It does not run cloud, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.

## Summary

- expected artifacts: `4`
- present artifacts: `4`
- missing artifacts: `0`
- validation passed: `2`
- timing floor passed: `2`
- timing below floor: `0`
- blocked rows: `0`
- excluded rows: `1`
- public speedup claims authorized: `0`

## Rows

| App | Path | Phase | Artifact | Review status | RTX phase | Reason |
| --- | --- | --- | --- | --- | ---: | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `correctness_validation` | `present` | `validation_passed` | `` | facility_knn_assignment validation artifact proves optix oracle parity |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `large_timing_repeat` | `present` | `timing_floor_passed` | `0.111038` | RTX phase 0.111038s passes timing floor |
| `robot_collision_screening` | `prepared_pose_flags` | `correctness_validation` | `present` | `validation_passed` | `` | robot validation artifact proves optix oracle parity |
| `robot_collision_screening` | `prepared_pose_flags` | `large_timing_repeat` | `present` | `timing_floor_passed` | `0.100071` | RTX phase 0.100071s passes timing floor |

## Excluded Rows

- `barnes_hut_force_app / node_coverage_prepared`: `blocked_contract_reframe_required`; The current Barnes-Hut node-coverage contract builds only four one-level quadtree nodes. The 1M-body pod run produced a 0.004204 s median RT query, so blind body-count scaling mostly measures input construction/packing rather than meaningful RTX traversal.

## Boundary

This intake checks copied Goal1072 artifacts only. It does not run cloud, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.
