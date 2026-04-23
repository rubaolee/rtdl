# Goal 768: Robot Native Pose-Count Summary

Date: 2026-04-23

## Purpose

Goal 765 showed that the RTX A5000 robot collision benchmark already has a fast prepared OptiX traversal phase, but the app-level path still pays unnecessary host-side work when the benchmark only needs a scalar collision summary. Goals 766 and 767 removed per-ray Python object construction and repeated pose-index uploads. Goal 768 adds the next local optimization before another paid cloud run: a native OptiX scalar colliding-pose count path.

## Change

Added a new prepared OptiX ABI:

- `rtdl_optix_count_poses_prepared_ray_anyhit_2d_prepared_indices`

Added the Python method:

- `PreparedOptixRayTriangleAnyHit2D.pose_count_prepared_indices(...)`

Updated the robot phase profiler:

- `scripts/goal760_optix_robot_pose_flags_phase_profiler.py`
- new CLI option: `--result-mode pose_flags|pose_count`
- `pose_count` mode requires `--mode optix --input-mode packed_arrays --skip-validation`

Updated the RTX cloud manifest:

- `docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json`
- the robot command now uses `--input-mode packed_arrays --result-mode pose_count --skip-validation`

## Implementation Notes

The native kernel remains the prepared ray/triangle any-hit path. For scalar pose-count mode, the kernel atomically marks a per-pose flag and increments a device-side count only on the first hit for each pose. The host downloads one scalar count instead of converting and returning a full pose-flag tuple.

This does not change the public correctness contract for pose flags. The scalar path is a benchmark/app-summary optimization after pose-flag correctness has already been established.

## Verification

Focused local verification on macOS:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal760_optix_robot_pose_flags_phase_profiler_test \
  tests.goal761_rtx_cloud_run_all_test \
  tests.goal762_rtx_cloud_artifact_report_test \
  tests.goal763_rtx_cloud_bootstrap_check_test

Ran 29 tests in 0.672s
OK (skipped=6)
```

Additional checks:

```text
python3 -m py_compile src/rtdsl/optix_runtime.py scripts/goal760_optix_robot_pose_flags_phase_profiler.py scripts/goal759_rtx_cloud_benchmark_manifest.py
git diff --check
```

Both passed.

## Boundary

This is local preparation for the next RTX pod batch. The Mac cannot validate the native OptiX symbol because it does not have the Linux RTX OptiX build/runtime environment. No new RTX speedup claim is authorized until the cloud host rebuilds `librtdl_optix.so`, reruns Goal 763, reruns Goal 761, and Goal 762 records the updated artifacts.

