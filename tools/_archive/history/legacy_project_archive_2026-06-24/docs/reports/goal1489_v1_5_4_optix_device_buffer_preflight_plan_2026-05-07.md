# Goal 1489: v1.5.4 OptiX Device-Buffer Preflight Plan

## Verdict

Accepted as local preparation for the next OptiX-backed Python+RTDL managed-buffer milestone.

This goal does not require the current pod unless we want to prove that the current pod is blocked for deeper OptiX work. It defines a precise preflight so future pod time is not wasted.

## Purpose

Goal 1488 established the CUDA evidence boundary:

- allocation-only evidence can be candidate-only zero-copy evidence
- explicit Python-origin content movement must be counted
- neither result proves end-to-end RTDL/OptiX device-buffer execution

Goal 1489 prepares the environment gate for that missing end-to-end step.

## Required Checks

The preflight checks:

- source tree cleanliness
- accepted Goal 1488 evidence boundary
- `nvidia-smi`
- CUDA driver library
- CUDA prefix
- `nvcc`
- OptiX headers
- `librtdl_optix.so` or enough build toolchain to produce it
- existing RTDL OptiX library path

## Expected Current Pod Outcome

The current pod is expected to fail the full preflight because it has:

- NVIDIA driver and `libcuda.so.1`
- no `nvcc`
- no discovered OptiX SDK headers
- no built `librtdl_optix.so`

That is a useful result: it means the pod should not be used for native OptiX integration unless a prebuilt library or build toolchain is provided.

## Claim Boundary

This preflight does not run backend execution and does not authorize:

- public true-zero-copy wording
- public speedup wording
- whole-application claims
- stable primitive promotion
- partner tensor handoff
- release action

## Files

- `scripts/goal1489_v1_5_4_optix_device_buffer_preflight.py`
- `tests/goal1489_v1_5_4_optix_device_buffer_preflight_test.py`
- `docs/reports/goal1489_v1_5_4_optix_device_buffer_preflight_plan_2026-05-07.md`

