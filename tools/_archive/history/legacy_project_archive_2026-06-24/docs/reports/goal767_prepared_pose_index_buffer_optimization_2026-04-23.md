# Goal 767: Prepared Pose-Index Buffer Optimization

Date: 2026-04-23

## Verdict

`IMPLEMENTED_LOCALLY_NEEDS_NATIVE_OPTIX_BUILD_AND_RTX_RERUN`

Goal766 removed avoidable Python ray-object construction for the large robot cloud benchmark. Goal767 continues the same batching strategy by moving pose-index buffers into a prepared GPU-resident handle so repeated pose-flag queries no longer upload the same 800k pose-index array every iteration.

## Change Summary

New Python API:

- `rtdsl.prepare_optix_pose_indices_2d(pose_indices)`
- `rtdsl.OptixPoseIndexBuffer`
- `PreparedOptixRayTriangleAnyHit2D.pose_flags_prepared_indices(prepared_rays, prepared_pose_indices, pose_count=...)`

New native C ABI:

- `rtdl_optix_prepare_pose_indices_2d`
- `rtdl_optix_pose_flags_prepared_ray_anyhit_2d_prepared_indices`
- `rtdl_optix_destroy_prepared_pose_indices_2d`

Profiler integration:

- `scripts/goal760_optix_robot_pose_flags_phase_profiler.py` now prepares pose indices once when `--input-mode packed_arrays` is selected.
- The phase report now includes `optix_prepare_pose_indices_sec`.
- Warm query timing now uses GPU-resident prepared rays and GPU-resident prepared pose indices.

## Why This Matters

Goal765 showed the robot flagship path is promising but still host/interface heavy:

- warm prepared pose flags: `0.240423s`;
- Python input construction: `3.038428s`;
- ray-buffer preparation: `1.893762s`.

Goal766 targeted Python input construction and ray packing. Goal767 targets repeated pose-index upload/conversion inside the warm query loop. Together they form a batched optimization set worth one future RTX cloud rerun.

## Boundary

This is still the same RTDL any-hit traversal feature. It does not add new semantics and does not change correctness rules. It is a prepared-buffer optimization for repeated app execution.

No public speedup claim is allowed until:

- the native OptiX library is rebuilt successfully on the RTX pod;
- Goal763 focused native tests pass with the new symbols;
- Goal761/Goal762 are rerun using the updated manifest;
- an independent review confirms phase interpretation.

## Local Verification

Focused local verification passed:

```text
Ran 29 tests in 0.779s
OK (skipped=6)
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

## Next Pod Run Should Validate

When the pod is used again, run the normal bootstrap first:

```bash
PYTHONPATH=src:. python3 scripts/goal763_rtx_cloud_bootstrap_check.py \
  --output-json docs/reports/goal763_rtx_cloud_bootstrap_check_runpod_goal767.json
```

Then run the cloud benchmark pipeline:

```bash
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --output-json docs/reports/goal761_rtx_cloud_run_all_summary_runpod_goal767.json
```

The key comparison is against Goal765:

- robot `python_input_construction_sec`: `3.038428s`;
- robot `optix_prepare_rays_sec`: `1.893762s`;
- robot warm query median: `0.240423s`.

The desired outcome is lower input/preparation time and possibly lower warm query time if pose-index upload was material.
