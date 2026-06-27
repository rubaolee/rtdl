# Goal1306: Robot Pose Flags Generic Grouped Reduction Migration

Date: 2026-05-05

## Purpose

Goal1306 migrates `robot_collision_screening / prepared_pose_flags` from an
app-level OptiX summary call to the generic v1.5 grouped reduction wrapper.

This is a local source migration. Pod validation is still required before the
row can move from local generic migration evidence to pod-verified generic
status.

## Contract

The migrated path uses:

```text
input primitive = ANY_HIT
summary primitive = REDUCE_INT(COUNT)
result layout = grouped_threshold_bool
group key = pose index
threshold = 1
```

The boolean flag is the generic grouped count predicate `count > 0`. This
avoids introducing `GROUPED_ANY_BOOL` as a new primitive name and keeps v1.5
inside the accepted primitive set.

## Implementation

Added:

```text
run_generic_prepared_ray_triangle_any_hit_grouped_count_threshold_bool()
GenericPreparedRayTriangleAnyHitScene.grouped_count_threshold_bool()
```

The generic helper prepares the ray/triangle scene, prepares rays, optionally
prepares group indices, and returns grouped threshold flags plus metadata. The
current OptiX backend delegates to the existing prepared pose-index any-hit
path, but the app no longer calls that path directly.

The migration inventory now marks `robot_collision_screening /
prepared_pose_flags` as `local_generic_pending_pod`. It should not be promoted
to `pod_verified_generic` until RTX pod evidence confirms the real OptiX path.

Validation note: the previous scaled-fixture analytic expectation was only
safe for tiny fixtures. Goal1306 uses the CPU ray/triangle oracle whenever
validation is requested; large timing runs should pass `--skip-validation`.

## Boundary

- This is still only the robot collision-screening pose-flag subpath.
- It does not claim whole-app motion planning acceleration.
- It does not authorize public NVIDIA speedup wording.
- Embree grouped output parity remains a later v1.5 implementation step.

## Verification

Planned focused local gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1306_v1_5_robot_pose_flags_generic_migration_test \
  tests.goal953_robot_native_continuation_metadata_test \
  tests.goal1304_v1_5_generic_migration_inventory_test \
  tests.goal1305_v1_5_grouped_reduction_contract_test
```
