# Goal754 OptiX Robot Pose-Flags Performance Plan

## Purpose

Goal753 added a native prepared OptiX pose-flag summary path for the robot
collision app. Goal754 should measure that path at scaled app sizes and compare
it against the existing robot performance modes.

## Required Comparisons

Measure deterministic robot fixtures at multiple scales:

- Embree row output;
- OptiX row output;
- OptiX prepared scalar hit-edge count;
- OptiX prepared pose flags.

The important question is not only "which backend is fastest" but which output
contract removes Python row materialization:

- row modes produce per-ray dictionaries;
- `prepared_count` produces one scalar;
- `prepared_pose_flags` produces one flag per pose.

## Implementation Plan

1. Extend `scripts/goal748_optix_robot_scaled_perf.py` with an
   `optix_prepared_pose_flags` backend mode.
2. Reuse the existing scaled fixture generator from
   `examples/rtdl_robot_collision_screening_app.py`.
3. Derive one pose index per ray from the existing deterministic ray metadata.
4. Use `rt.prepare_optix_ray_triangle_any_hit_2d(...)`,
   `rt.prepare_optix_rays_2d(...)`, and
   `prepared_scene.pose_flags_packed(...)`.
5. Validate correctness against CPU oracle pose flags when oracle mode is
   enabled.
6. For large no-oracle runs, compare backend summary counts for internal
   consistency and label the evidence as no-oracle when applicable.
7. Record preparation time separately from execute time:
   - scene preparation;
   - ray preparation;
   - native execution;
   - summary materialization.

## Honesty Boundary

The available Linux host has a GTX 1070, which has no NVIDIA RT cores. Goal754
can produce native OptiX traversal correctness and whole-call timing evidence.
It cannot produce RTX RT-core speedup evidence.

No public speedup claim should be made until the same harness runs on RTX-class
hardware.

## Acceptance Criteria

- Focused portable tests pass on macOS.
- Native Linux OptiX validation passes on `lestat-lx1`.
- The report includes clear tables for correctness and timing.
- Gemini or Windows review plus Codex review reaches at least 2-AI consensus.
