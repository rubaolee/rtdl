# Goal 1490: v1.5.4 OptiX Dependency Handoff

## Verdict

OptiX dependency blocked: `True`.

## Current Pod

Accepted uses:
- `CUDA Driver API allocation probes`
- `CUDA Driver API copy-boundary probes`
- `preflight and diagnostic checks`

Blocked uses:
- `end_to_end_rtdl_optix_device_buffer_execution`
- `native_optix_extension_build_without_optix_headers`
- `public_true_zero_copy_or_speedup_claims`

## Resolution Paths

### install_optix_sdk_headers_then_build

Requires:
- `OptiX SDK root with include/optix.h`
- `CUDA toolkit with nvcc`
- `CUDA driver library`

Commands:

```bash
export OPTIX_PREFIX=/path/to/NVIDIA-OptiX-SDK
export CUDA_PREFIX=/usr/local/cuda
make build-optix OPTIX_PREFIX=$OPTIX_PREFIX CUDA_PREFIX=$CUDA_PREFIX
export RTDL_OPTIX_LIB=$(pwd)/build/librtdl_optix.so
PYTHONPATH=src:. python3 scripts/goal1489_v1_5_4_optix_device_buffer_preflight.py
```

### provide_compatible_prebuilt_librtdl_optix

Requires:
- `prebuilt librtdl_optix.so from the same source commit or documented compatible commit`
- `matching CUDA driver/runtime availability`

Commands:

```bash
export RTDL_OPTIX_LIB=/path/to/librtdl_optix.so
PYTHONPATH=src:. python3 scripts/goal1489_v1_5_4_optix_device_buffer_preflight.py
```

### use_optix_ready_image

Requires:
- `image already contains OptiX SDK headers`
- `image already contains CUDA toolkit and nvcc`
- `repo can build or load librtdl_optix.so`

Commands:

```bash
git fetch origin
git reset --hard origin/main
PYTHONPATH=src:. python3 scripts/goal1489_v1_5_4_optix_device_buffer_preflight.py
```

## Must Rerun

- `PYTHONPATH=src:. python3 scripts/goal1489_v1_5_4_optix_device_buffer_preflight.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal1489_v1_5_4_optix_device_buffer_preflight_test tests.goal1488_v1_5_4_cuda_evidence_boundary_gate_test`

## Claim Boundary

Goal1490 is an OptiX dependency handoff only. It does not install OptiX, does not run RTDL/OptiX backend execution, and does not authorize true zero-copy wording, public speedup wording, whole-app claims, partner tensor handoff, or release action.
