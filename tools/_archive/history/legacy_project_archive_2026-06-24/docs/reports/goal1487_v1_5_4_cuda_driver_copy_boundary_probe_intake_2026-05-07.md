# Goal 1487: CUDA Driver Copy-Boundary Probe Intake

## Verdict

Accepted as real NVIDIA copy-boundary evidence for v1.5.4 Python+RTDL managed-buffer work.

This result is intentionally not true-zero-copy evidence. It proves that when RTDL-shaped content originates in host memory and is copied to a device allocation, the transfer boundary is visible and must be counted.

## Pod

- SSH target: `root@213.173.108.6 -p 17339`
- Hostname: `91aee8725935`
- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: `550.127.05`
- CUDA Driver API version observed by probe: `12040`
- Source commit: `20d8553db865885fad75c6737fe221125b137d1c`

## Evidence

The probe used `libcuda.so.1` through Python `ctypes` and performed:

- `cuInit`
- `cuDeviceGetCount`
- `cuDeviceGet`
- `cuDeviceGetName`
- `cuDriverGetVersion`
- `cuCtxCreate_v2`
- `cuMemAlloc_v2`
- `cuMemcpyHtoD_v2`
- `cuMemcpyDtoH_v2`
- `cuMemFree_v2`
- CUDA context destroy

Observed result:

- device allocation performed: `True`
- device free performed: `True`
- device pointer nonzero: `True`
- host-to-device transfers: `1`
- device-to-host transfers: `1`
- device residency observed: `True`
- measured on real NVIDIA: `True`
- content roundtrip verified: `True`
- true-zero-copy evidence candidate: `False`

## Interpretation

Goal 1486 showed allocation-only evidence: a real device allocation/free can have zero content transfers and can be marked as a candidate-only zero-copy evidence shape.

Goal 1487 shows content-copy evidence: when actual RTDL-shaped rows move from Python host memory into device memory and back, transfer counts are nonzero. Therefore this path is correctly not a true-zero-copy candidate.

Together, these two pod results sharpen the v1.5.4 boundary:

- RTDL-owned device allocation can exist on real NVIDIA hardware.
- Python-origin content movement must be counted.
- Allocation-only evidence must not be confused with end-to-end RTDL/OptiX execution.
- Explicit copy-boundary evidence must not be advertised as zero-copy.

## Claim Boundary

This artifact does not authorize:

- public true-zero-copy wording
- public speedup wording
- whole-application claims
- stable primitive promotion
- partner tensor handoff
- release action

## Artifacts

- `docs/reports/goal1487_v1_5_4_cuda_driver_copy_boundary_probe_2026-05-07.json`
- `docs/reports/goal1487_v1_5_4_cuda_driver_copy_boundary_probe_2026-05-07.md`
- `docs/reports/goal1487_v1_5_4_cuda_driver_copy_boundary_probe_intake_2026-05-07.md`

## Next Work

The next step is to design and validate the real RTDL/OptiX handoff point that can consume RTDL-owned device memory, while preserving parity and transfer accounting. This pod is sufficient for CUDA Driver API evidence, but it lacks `nvcc` and a built `librtdl_optix.so`, so native OptiX extension work may require a different image or prebuilt artifact flow.

