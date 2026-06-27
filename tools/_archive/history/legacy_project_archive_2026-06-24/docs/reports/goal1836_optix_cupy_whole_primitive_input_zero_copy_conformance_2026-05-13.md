# Goal1836 OptiX CuPy Whole-Primitive Input Zero-Copy Conformance

Date: 2026-05-13
Status: `accept-with-boundary`

## Summary

Goal1836 verifies that the Goal1834 OptiX whole-primitive input zero-copy path
is not Torch-only. The same prepared 2-D ray/triangle any-hit contract now
accepts CuPy CUDA arrays for:

- ray columns: `ids`, `ox`, `oy`, `dx`, `dy`, `tmax`;
- triangle columns: `ids`, `x0`, `y0`, `x1`, `y1`, `x2`, `y2`;
- the contiguous CUDA `float32[N, 6]` AABB tensor in OptiX `OptixAabb` order.

The main compatibility change is stride normalization at the Python boundary.
Torch reports contiguous tensor strides in elements, such as `(1,)` and
`(6, 1)`. CuPy reports contiguous byte strides, such as `(8,)` for a
`float64` column, `(4,)` for a `uint32` column, and `(24, 4)` for the
`float32[:, 6]` AABB matrix. RTDL now accepts both representations while still
rejecting non-contiguous partner buffers.

## Boundary

This authorizes this exact claim:

> The OptiX prepared 2-D ray/triangle any-hit primitive can execute from
> partner-owned CuPy CUDA ray columns, triangle columns, and AABB tensor inputs
> under the same input true zero-copy contract proven for Torch in Goal1834.

This does not authorize:

- v2.0 release readiness;
- broad RT-core speedup;
- whole-app acceleration;
- arbitrary partner acceleration beyond the observed Torch and CuPy CUDA tensor
  contracts;
- a claim that OptiX creates no native acceleration state. GAS output remains
  native OptiX acceleration state.

## Pod Evidence

Hardware validation was run on:

- Host: `ssh root@213.173.108.219 -p 17793`
- GPU: NVIDIA RTX A4500
- Driver: 550.127.05
- CUDA/NVRTC: CUDA 12.4 from `/usr/local/cuda`
- CuPy: 14.0.1 via `cupy-cuda12x`

Artifact:

- `docs/reports/goal1836_optix_cupy_whole_primitive_input_zero_copy_pod_validation.json`

Result:

```json
{
  "goal": "Goal1836",
  "status": "pass",
  "partner": "cupy",
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

Both ray and triangle metadata record `source_protocols: ["cupy"]`.

## Validation

Pod commands:

```text
python3 -m pip install --progress-bar off cupy-cuda12x
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda
PYTHONPATH=src:. python3 scripts/run_goal1828_optix_device_column_pod_validation.py \
  --partner cupy \
  --goal Goal1836 \
  --output docs/reports/goal1836_optix_cupy_whole_primitive_input_zero_copy_pod_validation.json
```

Local static/unit validation covers:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1836_optix_cupy_whole_primitive_input_zero_copy_conformance_test
```

## Verdict

Goal1836 is `accept-with-boundary`. It establishes CuPy conformance for the
current OptiX whole-primitive input zero-copy primitive, but v2.0 release
readiness remains `needs-more-evidence` until the broader partner surface,
documentation, and required release consensus are complete.
