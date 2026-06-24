# Goal 760: OptiX Robot Prepared Pose-Flags Phase Profiler Plan

Status: plan.

## Purpose

Goal759's RTX cloud manifest marks `robot_collision_screening` as the cleanest
current OptiX traversal app candidate, but its cloud command is still an app CLI
command. For a serious RTX claim review, we need phase-clean timing that
separates:

- fixture/input construction
- prepared OptiX scene/BVH setup
- prepared ray-buffer setup
- repeated prepared pose-flag traversal
- optional CPU oracle validation
- close/cleanup

## Proposed Artifact

Add `scripts/goal760_optix_robot_pose_flags_phase_profiler.py`.

The script should support:

- `--mode optix`: use `prepare_optix_ray_triangle_any_hit_2d`,
  `prepare_optix_rays_2d`, and `pose_flags_packed`.
- `--mode dry-run`: portable local mode for CI/test environments without
  OptiX; it exercises the same JSON schema without making native performance
  claims.
- `--pose-count`, `--obstacle-count`, `--iterations`.
- `--skip-validation` for large paid cloud timing after correctness has been
  checked separately.
- `--output-json`.

## Claim Boundary

This profiler is a measurement tool, not a speedup claim.

- `optix` mode can support future RTX claim review only when run on RTX-class
  hardware with exported OptiX prepared any-hit symbols.
- `dry-run` mode is schema/logic validation only.
- Even in `optix` mode, the valid claim is prepared ray/triangle any-hit
  pose-flag summary timing, not continuous robot collision detection or full
  mesh collision engine performance.

## Verification

- Add focused tests that exercise `dry-run` schema and command-line JSON.
- Test that output includes phase fields and the honesty boundary.
- `py_compile`, focused unittest, and `git diff --check`.

## Consensus Request

Reviewer should confirm this is the right next local tool before cloud testing
and that it does not overclaim RTX acceleration by itself.
