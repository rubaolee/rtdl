# Goal1831 OptiX Ray-Column True Zero-Copy Slice

Date: 2026-05-13
Status: `accept-with-boundary`

## Summary

Goal1831 converts the narrow OptiX partner ray-column execution path from
GPU-resident repacking to ray-side true zero-copy.

Before this goal, `rtdl_optix_count_prepared_ray_anyhit_2d_device_rays` accepted
Torch-owned CUDA columns but launched an intermediate CUDA kernel,
`pack_ray2d_device_columns`, to copy/convert those columns into an RTDL-owned
`GpuRay` array before OptiX launch.

After this goal, the prepared any-hit count path launches a specialized OptiX
raygen that reads these partner-owned columns directly:

- `ids`
- `ox`
- `oy`
- `dx`
- `dy`
- `tmax`

No RTDL-owned ray buffer is allocated for this path, and the old
`pack_ray2d_device_columns` kernel is no longer used by the device-ray count
entrypoint.

## Claim Boundary

The authorized claim is intentionally narrow:

> OptiX prepared any-hit count can read partner-owned Torch CUDA ray columns
> directly from device memory without ray-side staging or ray-side repacking.

The following claims remain blocked:

- whole-primitive true zero-copy, because the prepared triangle scene still uses
  RTDL-owned native triangle/AABB layout construction before OptiX GAS build;
- broad RT-core speedup, because this is a transfer-layout correctness slice,
  not a performance study;
- whole-app acceleration;
- arbitrary PyTorch/CuPy acceleration, until both partner families have pod
  evidence for the same contract;
- v2.0 release readiness.

Python metadata therefore records:

- `ray_columns_true_zero_copy_authorized: True`
- `triangle_scene_true_zero_copy_authorized: False`
- `true_zero_copy_authorized: False`

The last field remains false to prevent readers from interpreting the whole
primitive as true zero-copy.

## Implementation Notes

Native changes:

- Added a specialized `RayAnyHitCountDeviceRayColumnsLaunchParams` layout.
- Added `g_rayanyhit_count_device_ray_columns`.
- Added `ray_anyhit_count_device_ray_columns_kernel_source_2d()`, which derives
  from the existing 2-D any-hit count kernel and replaces `params.rays[idx]`
  loads with `load_ray_column(idx)`.
- Rewired `count_prepared_ray_anyhit_2d_device_rays_optix()` so it launches the
  specialized OptiX pipeline directly from partner device pointers.

Python changes:

- Updated `pack_optix_ray_any_hit_2d_device_ray_inputs()` metadata from
  `device_columns_gpu_pack` to `device_ray_columns_zero_copy`.
- Preserved the existing public method
  `PreparedOptixRayTriangleAnyHit2D.count_device_rays(ray_columns)`.

## Validation

Local static/runtime-adjacent validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal1831_optix_ray_column_true_zero_copy_slice_test \
  tests.goal1828_optix_device_column_pod_validation_packet_test \
  tests.goal1823_optix_partner_device_ray_columns_partial_abi_test
```

Pod validation was completed on:

- Host: `ssh root@213.173.108.219 -p 17793`
- GPU: NVIDIA RTX A4500
- Driver: 550.127.05
- CUDA/NVRTC: CUDA 12.4 from `/usr/local/cuda`
- Torch: 2.4.1+cu124
- Commit: `4b43f229ed0d7324ff3a714b8f037c4d2a456ee6`

Command:

```text
PYTHONPATH=src:. python3 scripts/run_goal1828_optix_device_column_pod_validation.py \
  --goal Goal1831 \
  --output docs/reports/goal1831_optix_ray_column_true_zero_copy_pod_validation.json
```

Artifact:

- `docs/reports/goal1831_optix_ray_column_true_zero_copy_pod_validation.json`

Result:

```json
{
  "goal": "Goal1831",
  "status": "pass",
  "device": "NVIDIA RTX A4500",
  "observed_count": 1,
  "expected_count": 1,
  "claim_boundary": {
    "direct_device_column_execution_observed": true,
    "ray_column_true_zero_copy_observed": true,
    "whole_primitive_true_zero_copy_authorized": false,
    "true_zero_copy_authorized": false,
    "rt_core_speedup_claim_authorized": false,
    "v2_0_release_authorized": false
  }
}
```
