# Goal 1486: v1.5.4 CUDA Driver Allocation Probe Plan

## Verdict

Accepted as the next pod-efficient evidence step after Goal 1485.

Goal 1485 prepared a pod evidence envelope. Goal 1486 adds a real CUDA Driver API allocation probe that does not require `nvcc`.

## Why This Is Needed

The first pod run showed:

- `nvidia-smi` worked
- the GPU was an NVIDIA RTX 4000 Ada Generation
- `nvcc` was not installed

Therefore the next evidence step should avoid CUDA toolkit compilation and use the installed NVIDIA driver directly through `libcuda.so.1`.

## What The Probe Does

The probe uses the CUDA Driver API through Python `ctypes`:

- load `libcuda.so.1`
- call `cuInit`
- call `cuDeviceGetCount`
- call `cuDeviceGet`
- call `cuDeviceGetName`
- call `cuDriverGetVersion`
- create a CUDA context
- call `cuMemAlloc_v2`
- call `cuMemFree_v2`
- destroy the context
- attach the result to the v1.5.4 managed-buffer allocation evidence envelope

## Claim Boundary

This is still candidate evidence only.

Even if `cuMemAlloc_v2` succeeds with zero host/device transfers and observed device residency, the artifact does not authorize:

- public true-zero-copy wording
- public speedup wording
- whole-application claims
- stable primitive promotion
- partner tensor handoff
- release action

## Pod Command

From a clean pod checkout:

```bash
git fetch origin
git reset --hard origin/main
PYTHONPATH=src:. python3 scripts/goal1486_v1_5_4_cuda_driver_allocation_probe.py \
  --json-out docs/reports/goal1486_v1_5_4_cuda_driver_allocation_probe_2026-05-07.json \
  --md-out docs/reports/goal1486_v1_5_4_cuda_driver_allocation_probe_2026-05-07.md
```

## Files

- `scripts/goal1486_v1_5_4_cuda_driver_allocation_probe.py`
- `tests/goal1486_v1_5_4_cuda_driver_allocation_probe_test.py`
- `docs/reports/goal1486_v1_5_4_cuda_driver_allocation_probe_plan_2026-05-07.md`

