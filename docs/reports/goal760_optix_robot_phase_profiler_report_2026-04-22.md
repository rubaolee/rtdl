# Goal 760: OptiX Robot Prepared Pose-Flags Phase Profiler Report

Status: implemented and locally verified.

## What Changed

Added a phase-clean profiler for the robot collision prepared OptiX pose-flags
path:

- `/Users/rl2025/rtdl_python_only/scripts/goal760_optix_robot_pose_flags_phase_profiler.py`
- `/Users/rl2025/rtdl_python_only/tests/goal760_optix_robot_pose_flags_phase_profiler_test.py`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal760_robot_pose_flags_phase_profiler_dry_run_2026-04-22.json`

The profiler reports:

- Python fixture/input construction time.
- OptiX prepared scene/BVH setup time.
- OptiX prepared ray-buffer setup time.
- Repeated prepared pose-flag query timing.
- Optional CPU oracle validation time.
- Close/cleanup time.

It has two modes:

- `--mode optix`: future RTX cloud mode using
  `prepare_optix_ray_triangle_any_hit_2d`, `prepare_optix_rays_2d`, and
  `pose_flags_packed`.
- `--mode dry-run`: portable schema/logic validation mode that uses the CPU
  any-hit oracle and makes no native performance claim.

Goal759's RTX cloud manifest was also updated so the robot collision entry uses
this phase profiler instead of raw app CLI timing.

## Claim Boundary

This is a measurement tool, not a speedup claim.

- Local `dry-run` evidence validates only schema, boundaries, and correctness
  plumbing.
- Future `optix` evidence must come from RTX-class hardware with exported
  prepared OptiX any-hit symbols.
- The valid performance target is prepared ray/triangle any-hit pose-flag
  summary timing, not continuous collision detection, full robot kinematics, or
  mesh-engine replacement.

## Verification

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal760_optix_robot_pose_flags_phase_profiler_test

Ran 8 tests in 0.237s
OK
```

Dry-run JSON generation:

```text
PYTHONPATH=src:. python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py \
  --mode dry-run \
  --pose-count 32 \
  --obstacle-count 8 \
  --iterations 2 \
  --output-json docs/reports/goal760_robot_pose_flags_phase_profiler_dry_run_2026-04-22.json
```

Static checks:

```text
python3 -m py_compile \
  scripts/goal759_rtx_cloud_benchmark_manifest.py \
  scripts/goal760_optix_robot_pose_flags_phase_profiler.py \
  tests/goal759_rtx_cloud_benchmark_manifest_test.py \
  tests/goal760_optix_robot_pose_flags_phase_profiler_test.py
git diff --check
```

All passed.

## Consensus

Plan review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal760_gemini_flash_plan_review_2026-04-22.md`
- Verdict: ACCEPT.

Finish review is requested after this report.
