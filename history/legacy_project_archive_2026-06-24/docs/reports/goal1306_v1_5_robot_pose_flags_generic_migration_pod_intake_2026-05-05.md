# Goal1306 Pod Intake: Robot Pose Flags Generic Grouped Reduction

Date: 2026-05-05

## Source

Goal1306 validates `robot_collision_screening / prepared_pose_flags` on the RTX
pod after migrating the app path to the generic prepared ray/triangle grouped
count-to-boolean helper.

Pod workspace:

```text
/workspace/rtdl_goal1292
```

Copied local files into the pod workspace because the pod checkout was older
than the local branch.

## Evidence

Compact copied artifact:

```text
docs/reports/goal1306_v1_5_robot_pose_flags_generic_migration_pod_results/compact_summary.json
```

| Artifact | Scale | Primitive | Summary | Result layout | Validation |
| --- | --- | --- | --- | --- | --- |
| `robot_pose_flags_generic_validation_512.json` | 512 poses, 2048 rays, 256 triangles | `ANY_HIT` | `REDUCE_INT(COUNT)` | `grouped_threshold_bool` | `matches_oracle=true`, `validation_mode=cpu_oracle` |
| `robot_pose_flags_generic_timing_4096_skip_validation.json` | 4096 poses, 16384 rays, 2048 triangles | `ANY_HIT` | `REDUCE_INT(COUNT)` | `grouped_threshold_bool` | timing only, `validation_mode=skipped` |

The validated 512-pose run returned 427 colliding poses and matched the CPU
oracle. The larger 4096-pose run returned 3968 colliding poses with validation
intentionally skipped to avoid CPU oracle cost.

## Correction

The first 4096-pose attempt used the previous scaled analytic fixture and
reported `matches_oracle=false`. Investigation showed the analytic expectation
was too simplistic for denser scaled layouts. Goal1306 therefore changed
validated pose-flag runs to use the CPU ray/triangle oracle. Large timing runs
must use `--skip-validation`.

## Status

`robot_collision_screening / prepared_pose_flags` is now pod-verified as a
generic v1.5 grouped reduction row:

```text
input primitive = ANY_HIT
summary primitive = REDUCE_INT(COUNT)
result layout = grouped_threshold_bool
```

This remains an exact subpath claim only. It does not claim whole-app collision
planning acceleration and does not authorize public NVIDIA speedup wording.

## Pod Tests

Passed on pod:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1306_v1_5_robot_pose_flags_generic_migration_test \
  tests.goal953_robot_native_continuation_metadata_test \
  tests.goal1304_v1_5_generic_migration_inventory_test \
  tests.goal1305_v1_5_grouped_reduction_contract_test
```

Result: 17 tests OK.
