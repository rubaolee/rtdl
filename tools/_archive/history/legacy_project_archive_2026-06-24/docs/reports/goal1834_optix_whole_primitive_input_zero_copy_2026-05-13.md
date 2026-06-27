# Goal1834 OptiX Whole-Primitive Input Zero-Copy

Date: 2026-05-13
Status: `accept-with-boundary`

## Summary

Goal1834 extends Goal1831 from ray-column true zero-copy to whole-primitive
input true zero-copy for the prepared 2-D ray/triangle any-hit primitive.

The new scene contract requires the partner to provide:

- CUDA triangle columns: `ids`, `x0`, `y0`, `x1`, `y1`, `x2`, `y2`;
- a contiguous CUDA `float32[N, 6]` AABB tensor in OptiX `OptixAabb` order:
  `minX`, `minY`, `minZ`, `maxX`, `maxY`, `maxZ`.

With that contract, RTDL no longer launches `pack_triangle2d_device_columns`
for this path and no longer creates an RTDL-owned triangle buffer or AABB staging
buffer. The OptiX intersection program reads partner-owned triangle columns
directly, while OptiX builds its GAS from the partner-owned AABB buffer.

## Boundary

This authorizes this exact claim:

> The OptiX prepared 2-D ray/triangle any-hit primitive can execute from
> partner-owned Torch CUDA ray columns, triangle columns, and AABB tensor inputs
> without RTDL ray/triangle/AABB staging or repacking.

This does not authorize:

- v2.0 release readiness;
- broad RT-core speedup;
- whole-app acceleration;
- arbitrary partner acceleration beyond the observed Torch CUDA tensor contract;
- a claim that OptiX creates no native acceleration state. GAS output remains
  native OptiX acceleration state, as expected for a ray tracing backend.

## Pod Evidence

Hardware validation was run on:

- Host: `ssh root@213.173.108.219 -p 17793`
- GPU: NVIDIA RTX A4500
- Driver: 550.127.05
- CUDA/NVRTC: CUDA 12.4 from `/usr/local/cuda`
- Torch: 2.4.1+cu124

Artifact:

- `docs/reports/goal1834_optix_whole_primitive_input_zero_copy_pod_validation.json`

Result:

```json
{
  "goal": "Goal1834",
  "status": "pass",
  "observed_count": 1,
  "expected_count": 1,
  "claim_boundary": {
    "ray_column_true_zero_copy_observed": true,
    "triangle_scene_true_zero_copy_observed": true,
    "whole_primitive_true_zero_copy_authorized": true,
    "true_zero_copy_authorized": true,
    "rt_core_speedup_claim_authorized": false,
    "v2_0_release_authorized": false
  }
}
```

## Validation

Local and pod validation covered:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1823_optix_partner_device_ray_columns_partial_abi_test \
  tests.goal1826_optix_partner_device_triangle_scene_test \
  tests.goal1828_optix_device_column_pod_validation_packet_test \
  tests.goal1831_optix_ray_column_true_zero_copy_slice_test \
  tests.goal1834_optix_whole_primitive_input_zero_copy_test
```

The OptiX backend was rebuilt on Linux and on the RTX A4500 pod, and exported:

- `rtdl_optix_prepare_ray_anyhit_2d_device_triangle_columns_aabbs`
- `rtdl_optix_count_prepared_ray_anyhit_2d_device_rays`

