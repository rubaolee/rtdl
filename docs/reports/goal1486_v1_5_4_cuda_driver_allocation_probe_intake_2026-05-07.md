# Goal 1486: CUDA Driver Allocation Probe Intake

## Verdict

Accepted as candidate-only v1.5.4 Python+RTDL managed-buffer allocation evidence.

This is the first pod-backed evidence in this sequence that performs a real NVIDIA driver allocation call through `cuMemAlloc_v2` and a matching `cuMemFree_v2`.

## Pod

- SSH target: `root@213.173.108.6 -p 17339`
- Hostname: `91aee8725935`
- OS: Linux `6.8.0-40-generic`
- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: `550.127.05`
- CUDA driver API version observed by probe: `12040`
- Python: `3.10.12`
- Source commit: `92c601c3a58eb95decddadc2faecc56bc1b88bcd`

## Evidence

Goal 1485 ran the prepared pod evidence packet and confirmed:

- `nvidia-smi` was available
- `nvcc` was not available
- the packet path generated artifacts on the pod

Goal 1486 then ran the stronger CUDA Driver API probe and confirmed:

- `libcuda.so.1` loaded
- `cuInit` succeeded
- device discovery succeeded
- `cuCtxCreate_v2` succeeded
- `cuMemAlloc_v2` succeeded for the RTDL managed-buffer allocation probe size
- the returned device pointer was nonzero
- `cuMemFree_v2` succeeded
- recorded host-to-device transfer count was `0`
- recorded device-to-host transfer count was `0`
- device residency was observed for the allocation-only probe
- the evidence envelope marked `true_zero_copy_evidence_candidate=True`

## Claim Boundary

This remains candidate evidence only.

It does not authorize:

- public true-zero-copy wording
- public speedup wording
- whole-application claims
- stable primitive promotion
- partner tensor handoff
- release action

The result proves that this pod can perform an RTDL-owned CUDA driver allocation/free path without `nvcc`. It does not yet prove end-to-end OptiX query execution using RTDL-managed device-resident buffers.

## Artifacts

- `docs/reports/goal1485_v1_5_4_managed_buffer_pod_results_2026-05-07/goal1485_pod_environment.log`
- `docs/reports/goal1485_v1_5_4_managed_buffer_pod_results_2026-05-07/goal1485_managed_buffer_pod_evidence.log`
- `docs/reports/goal1485_v1_5_4_managed_buffer_pod_results_2026-05-07/goal1485_managed_buffer_pod_evidence_2026-05-07.json`
- `docs/reports/goal1485_v1_5_4_managed_buffer_pod_results_2026-05-07/goal1485_managed_buffer_pod_evidence_2026-05-07.md`
- `docs/reports/goal1486_v1_5_4_cuda_driver_allocation_probe_2026-05-07.json`
- `docs/reports/goal1486_v1_5_4_cuda_driver_allocation_probe_2026-05-07.md`
- `docs/reports/goal1486_v1_5_4_cuda_driver_allocation_probe_intake_2026-05-07.md`

## Next Work

The next evidence step should connect this allocation evidence to an actual RTDL/OptiX data path. The target is no longer just proving that CUDA allocation works; it is proving that RTDL-managed device-resident buffers can be used by the relevant backend path while preserving parity and recording transfer counts.

