# Goal1838 OptiX Partner-Owned Output Flags Zero-Copy

Date: 2026-05-13
Status: `accept-with-boundary`

## Summary

Goal1838 extends the Goal1834/Goal1836 OptiX prepared 2-D ray/triangle
any-hit path from input-only true zero-copy to partner-owned output as well.

The new native entry point:

- `rtdl_optix_write_prepared_ray_anyhit_2d_device_flags`

reads partner-owned ray columns and partner-owned triangle columns, uses the
borrowed partner AABB tensor for OptiX GAS construction, and writes one
`uint32` any-hit flag per ray directly into a partner-owned CUDA output vector.

This removes the host scalar output path for this exact primitive mode. The
validation script now supports `--output-flags`, which allocates either a Torch
or CuPy CUDA output vector, calls `scene.write_device_any_hit_flags(...)`, and
then reads the flags back only for test assertion.

## Boundary

This authorizes this exact claim:

> The OptiX prepared 2-D ray/triangle any-hit primitive can read partner-owned
> Torch or CuPy CUDA input columns and write per-ray any-hit flags into a
> partner-owned Torch or CuPy CUDA output vector without RTDL-owned input or
> output staging buffers.

This does not authorize:

- v2.0 release readiness;
- broad RT-core speedup;
- whole-app acceleration;
- arbitrary partner acceleration beyond the observed Torch/CuPy CUDA tensor
  contract;
- a claim that OptiX creates no native acceleration state. GAS output remains
  native OptiX acceleration state.

## Pod Evidence

Hardware validation was run on:

- Host: `ssh root@213.173.108.219 -p 17793`
- GPU: NVIDIA RTX A4500
- Driver: 550.127.05
- CUDA/NVRTC: CUDA 12.4 from `/usr/local/cuda`
- Torch: 2.4.1+cu124
- CuPy: 14.0.1 via `cupy-cuda12x`

Artifacts:

- `docs/reports/goal1838_optix_partner_owned_output_flags_pod_validation.json`
- `docs/reports/goal1838_optix_partner_owned_output_flags_torch_pod_validation.json`

CuPy result:

```json
{
  "goal": "Goal1838",
  "status": "pass",
  "partner": "cupy",
  "observed_flags": [1, 0],
  "observed_count": 1,
  "expected_count": 1,
  "claim_boundary": {
    "ray_column_true_zero_copy_observed": true,
    "triangle_scene_true_zero_copy_observed": true,
    "output_flags_true_zero_copy_observed": true,
    "true_zero_copy_authorized": true,
    "rt_core_speedup_claim_authorized": false,
    "v2_0_release_authorized": false
  }
}
```

Torch result matches the same `[1, 0]` flags and records
`source_protocols: ["torch"]` in the output metadata.

## Validation

Pod commands:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda
PYTHONPATH=src:. python3 scripts/run_goal1828_optix_device_column_pod_validation.py \
  --partner cupy \
  --goal Goal1838 \
  --output-flags \
  --output docs/reports/goal1838_optix_partner_owned_output_flags_pod_validation.json
PYTHONPATH=src:. python3 scripts/run_goal1828_optix_device_column_pod_validation.py \
  --partner torch \
  --goal Goal1838-Torch \
  --output-flags \
  --output docs/reports/goal1838_optix_partner_owned_output_flags_torch_pod_validation.json
```

Local static/unit validation covers:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1838_optix_partner_owned_output_flags_zero_copy_test
```

## Verdict

Goal1838 is `accept-with-boundary`. It closes the first input-plus-output
zero-copy slice for one OptiX primitive and both v2.0 partners, but v2.0 release
readiness remains `needs-more-evidence` until the broader partner surface,
documentation, performance boundaries, and required release consensus are
complete.
