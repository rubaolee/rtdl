# Goal 766: Robot Packed Input Optimization

Date: 2026-04-23

## Verdict

`IMPLEMENTED_LOCALLY_NEEDS_RTX_RERUN`

Goal765 showed that the RTX A5000 OptiX traversal path for robot collision is already fast (`0.240423s` median warm query for 800k edge rays), while app-side input construction and ray-buffer preparation dominate the total path. Goal766 therefore targets the measured bottleneck rather than the OptiX traversal kernel.

## Change Summary

- Added `rtdsl.pack_rays_2d_from_arrays(...)` for fast 2D ray packing from array-like inputs.
- Updated `PreparedOptixRayTriangleAnyHit2D.pose_flags_packed(...)` so NumPy `uint32` pose-index arrays can be passed without converting 800k indices into a Python tuple first.
- Added `--input-mode packed_arrays` to `scripts/goal760_optix_robot_pose_flags_phase_profiler.py`.
- Updated the RTX cloud manifest robot command to use:

```bash
python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py \
  --mode optix \
  --pose-count 200000 \
  --obstacle-count 1024 \
  --iterations 10 \
  --input-mode packed_arrays \
  --skip-validation \
  --output-json docs/reports/goal759_robot_pose_flags_phase_rtx.json
```

## Design Boundary

This is an app-path optimization, not a new language feature. It preserves the existing RTDL/OptiX prepared ray-triangle any-hit semantics and only changes how generated robot rays and pose-index buffers are marshaled into the existing runtime.

`packed_arrays` mode is intentionally restricted to `mode=optix` and `--skip-validation`. Correctness validation remains the job of Goal763 focused native tests and `python_objects` oracle runs. This avoids mixing a large CPU oracle into clean RTX performance timing.

## Expected Impact

The main expected improvement is lower Python-side construction time for large generated robot sweeps:

- fewer per-ray `Ray2D` Python objects;
- no per-ray `ray_metadata` dictionary;
- no 800k-element Python tuple conversion for pose indices;
- direct packed C ABI records for `prepare_optix_rays_2d(...)`.

This should reduce the Goal765 robot phases:

- `python_input_construction_sec`: previously `3.038428s`;
- `optix_prepare_rays_sec`: previously `1.893762s`, partly due to Python object/packing overhead before GPU upload;
- warm query median should remain comparable unless pose-index upload/conversion was a large part of each query.

## Verification

Focused local verification passed:

```text
Ran 26 tests in 1.726s
OK (skipped=5)
```

Covered test groups:

- `tests.goal671_optix_prepared_anyhit_count_test`
- `tests.goal759_rtx_cloud_benchmark_manifest_test`
- `tests.goal760_optix_robot_pose_flags_phase_profiler_test`
- `tests.goal761_rtx_cloud_run_all_test`
- `tests.goal762_rtx_cloud_artifact_report_test`
- `tests.goal763_rtx_cloud_bootstrap_check_test`

Additional checks:

- `python3 -m py_compile src/rtdsl/optix_runtime.py scripts/goal760_optix_robot_pose_flags_phase_profiler.py`
- `git diff --check`

Local Python 3.14 did not have NumPy installed, so the new NumPy-specific portable test was skipped locally. The project requirement remains `numpy>=1.26`, and the RTX cloud image used by the Goal765 pipeline supports the benchmark scripts that depend on NumPy.

## Required Next Step

Rerun the Goal761/Goal762 cloud pipeline on the stopped RTX A5000 pod after restarting it. The expected comparison is Goal765 `python_objects` robot timing versus Goal766 `packed_arrays` robot timing.

Do not claim a robot app speedup until the cloud rerun confirms the phase reduction and the artifact report is reviewed.
