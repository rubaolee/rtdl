# Goal1070 Goal1068 Artifact Intake

Date: 2026-04-28

Overall status: `timing_floor_not_met`

This intake checks copied Goal1068 artifacts only. It does not run cloud, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.

## Summary

- expected artifacts: `6`
- present artifacts: `6`
- missing artifacts: `0`
- validation passed: `3`
- timing floor passed: `0`
- timing below floor: `3`
- blocked rows: `0`
- public speedup claims authorized: `0`

## Rows

| App | Path | Phase | Artifact | Review status | RTX phase | Reason |
| --- | --- | --- | --- | --- | ---: | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `correctness_validation` | `present` | `validation_passed` | `` | facility_knn_assignment validation artifact proves optix oracle parity |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `large_timing_repeat` | `present` | `timing_below_floor` | `0.034053` | RTX phase 0.034053s is below 0.100s floor |
| `robot_collision_screening` | `prepared_pose_flags` | `correctness_validation` | `present` | `validation_passed` | `` | robot validation artifact proves optix oracle parity |
| `robot_collision_screening` | `prepared_pose_flags` | `large_timing_repeat` | `present` | `timing_below_floor` | `0.015967` | RTX phase 0.015967s is below 0.100s floor |
| `barnes_hut_force_app` | `node_coverage_prepared` | `correctness_validation` | `present` | `validation_passed` | `` | barnes_hut_force_app validation artifact proves optix oracle parity |
| `barnes_hut_force_app` | `node_coverage_prepared` | `large_timing_repeat` | `present` | `timing_below_floor` | `0.004204` | RTX phase 0.004204s is below 0.100s floor |

## Boundary

This intake checks copied Goal1068 artifacts only. It does not run cloud, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.
