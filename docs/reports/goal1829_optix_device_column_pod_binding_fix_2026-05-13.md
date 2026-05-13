# Goal1829 OptiX Device-Column Pod Binding Fix

Date: 2026-05-13
Status: `accept-with-boundary`

## Summary

Goal1828 reached a real RTX pod and exposed a Python binding bug rather than a native OptiX kernel bug: the new partner device-column symbols were exported and linked, but `ctypes` did not register their `argtypes` / `restype`. As a result, the prepared device-ray path received a corrupted `size_t` count and failed with:

```text
RuntimeError: partner device ray column count exceeds uint32_t launch limit
```

Goal1829 fixes that boundary by registering the two new OptiX symbols in `src/rtdsl/optix_runtime.py`:

- `rtdl_optix_prepare_ray_anyhit_2d_device_triangles`
- `rtdl_optix_count_prepared_ray_anyhit_2d_device_rays`

The fix is intentionally narrow: it does not widen the v2.0 claim surface and does not rename or alter the native ABI.

## Pod Evidence

Hardware validation was run on an RTX pod with:

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 550.127.05
- Python: 3.12.3
- Torch: 2.8.0+cu128
- OptiX SDK headers: `/root/vendor/optix-sdk/include`
- CUDA/NVRTC runtime selected for this driver: Ubuntu CUDA 12.0 libraries from `/usr/lib/x86_64-linux-gnu`

The validation artifact is committed at:

- `docs/reports/goal1828_optix_device_column_pod_validation.json`

Key artifact fields:

```json
{
  "status": "pass",
  "observed_count": 1,
  "expected_count": 1,
  "device": "NVIDIA RTX 4000 Ada Generation",
  "claim_boundary": {
    "direct_device_column_execution_observed": true,
    "true_zero_copy_authorized": false,
    "rt_core_speedup_claim_authorized": false,
    "v2_0_release_authorized": false
  }
}
```

## Boundary

This is the first narrow pod proof that the OptiX partner path can accept Torch-owned CUDA columns for both rays and triangles and execute the prepared any-hit primitive through RTDL's native OptiX backend.

It is not a v2.0 release proof. The following claims remain blocked:

- true zero-copy, because the current path still GPU-packs partner columns into RTDL-owned native layouts;
- broad RT-core speedup, because this is a correctness proof on a tiny primitive packet, not a performance study;
- whole-app acceleration, because only the prepared ray/triangle any-hit primitive is covered;
- arbitrary PyTorch/CuPy acceleration, because only Torch CUDA columns were observed on pod;
- package-install readiness, because the pod needed explicit CUDA/driver library selection.

## Validation

Local regression:

```text
PYTHONPATH=src;. py -3 -m py_compile src\rtdsl\optix_runtime.py
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal1828_optix_device_column_pod_validation_packet_test \
  tests.goal1826_optix_partner_device_triangle_scene_test \
  tests.goal1823_optix_partner_device_ray_columns_partial_abi_test
```

Result: 13 tests passed.

Pod validation:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/lib/cuda
PYTHONPATH=src:. python3 scripts/run_goal1828_optix_device_column_pod_validation.py \
  --output docs/reports/goal1828_optix_device_column_pod_validation.json
```

Result: `status: pass`, `observed_count: 1`, `expected_count: 1`.

