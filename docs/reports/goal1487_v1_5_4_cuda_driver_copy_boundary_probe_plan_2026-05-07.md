# Goal 1487: v1.5.4 CUDA Driver Copy-Boundary Probe Plan

## Verdict

Accepted as the next pod-efficient step after Goal 1486.

Goal 1486 proved that a real NVIDIA pod can allocate and free device memory through the CUDA Driver API without `nvcc`. Goal 1487 probes the content-copy boundary for RTDL-shaped `int64` rows.

## Purpose

This goal distinguishes allocation-only evidence from content-movement evidence.

For Python+RTDL, ordinary Python data starts in CPU memory. If RTDL moves that content into device memory, the host-to-device transfer must be counted. If RTDL returns content to Python, the device-to-host transfer must also be counted.

## What The Probe Does

The probe uses Python `ctypes` against `libcuda.so.1`:

- allocate device memory with `cuMemAlloc_v2`
- copy RTDL-shaped `int64` rows from host to device with `cuMemcpyHtoD_v2`
- copy rows back with `cuMemcpyDtoH_v2`
- verify roundtrip content equality
- free memory with `cuMemFree_v2`
- attach the result to the v1.5.4 allocation evidence envelope

## Expected Result

Expected on a real NVIDIA pod:

- device allocation succeeds
- device free succeeds
- roundtrip content matches
- host-to-device transfers equals `1`
- device-to-host transfers equals `1`
- `true_zero_copy_evidence_candidate=False`

This is the correct result because explicit content copies are not true zero-copy.

## Claim Boundary

This goal does not authorize:

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
PYTHONPATH=src:. python3 scripts/goal1487_v1_5_4_cuda_driver_copy_boundary_probe.py \
  --json-out docs/reports/goal1487_v1_5_4_cuda_driver_copy_boundary_probe_2026-05-07.json \
  --md-out docs/reports/goal1487_v1_5_4_cuda_driver_copy_boundary_probe_2026-05-07.md
```

## Files

- `scripts/goal1487_v1_5_4_cuda_driver_copy_boundary_probe.py`
- `tests/goal1487_v1_5_4_cuda_driver_copy_boundary_probe_test.py`
- `docs/reports/goal1487_v1_5_4_cuda_driver_copy_boundary_probe_plan_2026-05-07.md`

