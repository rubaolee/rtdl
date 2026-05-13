# Goal1828 - OptiX Device-Column Pod Validation Packet

## Status

`ready-for-pod`

Goal1828 prepares the RTX validation command for the Goal1823/Goal1826
device-column path. It does not claim hardware success yet.

## Command

```bash
PYTHONPATH=src:. python3 scripts/run_goal1828_optix_device_column_pod_validation.py \
  --output docs/reports/goal1828_optix_device_column_pod_validation.json
```

Prerequisites:

- CUDA-capable RTX pod.
- Built `build/librtdl_optix.so` from current `main`.
- PyTorch with `torch.cuda.is_available() == True`.
- `RTDL_OPTIX_LIB` set if the built library is not in the default RTDL search path.

## What It Proves

The harness builds partner-owned CUDA columns for a tiny ray/triangle any-hit
case, prepares the triangle scene from device columns, executes ray counting
from device columns, and checks the expected aggregate count.

If it passes on an RTX pod, it proves narrow device-column execution for the
prepared 2-D ray/primitive any-hit path.

## What It Does Not Prove

- true zero-copy,
- broad RT-core speedup,
- whole-application acceleration,
- arbitrary PyTorch/CuPy acceleration,
- package-install readiness,
- v2.0 release readiness.

Those remain governed by Goal1814 until separate reviewed evidence closes or
explicitly removes each blocker.
