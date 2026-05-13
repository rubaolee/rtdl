# Goal1927 - Robot Collision Partner Pose-Flags Adapter

Status: adapter-ready-pod-needed

Date: 2026-05-13

## Purpose

Goal1924's Family B includes `robot_collision_screening`. v1.8 already has a
prepared OptiX ray/triangle pose-flags path, but the v2.0 all-app matrix needs
the app summary to stay in the partner layer after RTDL produces generic
ray/primitive any-hit results.

Goal1927 adds that app-layer adapter:

`robot_collision_pose_flags_optix_prepared_partner_device_columns`

## Contract

The native engine contract remains generic:

`generic_ray_primitive_any_hit_flags`

The app-specific work is outside the engine:

1. caller supplies partner-owned ray columns and pose-index columns;
2. prepared OptiX writes one generic any-hit flag per ray into a partner-owned
   `ray_any_hit_flags` output column;
3. Torch/CuPy reduces ray flags by pose index into a partner-owned
   `pose_collision_flags` output column.

This is the v2.0 pattern we want for app rows that do real work on RT results:
RTDL performs the generic RT query; partner tensor operations perform the app
summary without host row materialization.

## Boundaries

This adapter does not authorize v2.0 release.

It does not claim whole-app acceleration. It only prepares the
`robot_collision_screening` same-contract v2 path for the final all-app matrix.

It does not introduce ad-hoc CUDA/Triton kernels. The app reduction is written
with the selected partner's tensor operations, consistent with the v2.0 scope.

## Next Pod Work

The next runner should compare:

- v1.8 prepared OptiX `pose_flags` / `pose_count` timing from
  `scripts/goal760_optix_robot_pose_flags_phase_profiler.py`;
- v2.0 prepared partner `robot_collision_pose_flags_optix_prepared_partner_device_columns`;
- Torch and CuPy partner paths;
- parity on small validation rows and timing on packed-array rows.

The pod artifact must record source commit, GPU, partner versions, per-phase
timing, parity, and claim boundary flags.
