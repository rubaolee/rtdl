# Goal753 OptiX Prepared Pose Flags Closure

## Verdict

ACCEPT.

Goal753 promotes the robot collision app from a prepared scalar OptiX summary
only to a prepared pose-level OptiX summary for the app's most common compact
output shape.

## Implemented Surface

New native C ABI:

```text
rtdl_optix_pose_flags_prepared_ray_anyhit_2d_packed(...)
```

It consumes:

- a prepared OptiX 2D any-hit triangle scene;
- a prepared packed 2D ray buffer;
- one pose index per ray;
- a pose-count output width.

It emits:

- one native per-pose collision flag.

The kernel uses idempotent `atomicExch(..., 1u)` because many rays can map to
the same pose and all racing writers store the same value.

## Public App Surface

The robot collision app now accepts:

```bash
--backend optix --optix-summary-mode prepared_pose_flags
```

This mode returns pose-level collision flags without per-ray Python dict row
materialization.

Boundary:

- it does not emit edge-level witnesses or hit-ray IDs;
- use `--optix-summary-mode rows` when witnesses are required;
- it is native OptiX correctness and whole-call evidence on the Linux GTX 1070,
  not RTX RT-core speedup evidence.

## Verification

Mac portable checks:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal701_robot_collision_compact_output_test \
  tests.goal691_optix_robot_summary_profiler_test \
  tests.goal702_robot_collision_profiler_output_modes_test

python3 -m py_compile \
  src/rtdsl/optix_runtime.py \
  examples/rtdl_robot_collision_screening_app.py \
  scripts/goal691_optix_app_phase_profiler.py

git diff --check
```

Result: `24` tests OK locally, with native OptiX tests skipped on macOS where
the OptiX library is unavailable.

Linux native scratch validation on `lestat-lx1`:

```bash
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
  PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal701_robot_collision_compact_output_test \
  tests.goal691_optix_robot_summary_profiler_test \
  tests.goal702_robot_collision_profiler_output_modes_test
```

Result: `24` tests OK, including the native prepared pose-flag test.

## Independent Review

Gemini Flash:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal753_gemini_flash_optix_pose_flags_candidate_review_2026-04-21.md`
- Verdict: ACCEPT.

Windows Codex:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal753_windows_optix_pose_flags_review_2026-04-21.md`
- Verdict: ACCEPT_WITH_NOTES.
- Notes resolved: the native test class has been renamed from `Goal752...` to
  `Goal753...`.

## Release Meaning

RTDL now has two prepared OptiX robot summary modes:

- `prepared_count`: native scalar hit-edge count;
- `prepared_pose_flags`: native pose-level collision flags.

Both are compact app-summary paths. They are not replacements for full
emitted-row mode when an app needs edge witnesses.
