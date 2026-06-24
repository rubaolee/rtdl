# Goal 1490: v1.5.4 OptiX Dependency Handoff Plan

## Verdict

Accepted as the next local-preparation step after Goal 1489.

The current pod is blocked for deeper RTDL/OptiX device-buffer execution by missing OptiX dependencies. Goal 1490 converts that blocker into a precise handoff with acceptable resolution paths.

## Purpose

Goal 1489 showed the pod has:

- NVIDIA GPU
- CUDA driver
- CUDA prefix
- `nvcc`
- accepted Goal 1488 evidence boundary

It lacks:

- OptiX SDK headers
- `librtdl_optix.so`
- enough OptiX build/runtime evidence for device-buffer execution work

Goal 1490 tells the next operator how to resolve that without guessing.

## Acceptable Resolution Paths

The handoff accepts three paths:

- install or mount OptiX SDK headers, then run `make build-optix`
- provide a compatible prebuilt `librtdl_optix.so`
- use a different OptiX-ready image

After any path, the next operator must rerun Goal 1489 preflight before attempting RTDL/OptiX device-buffer execution.

## Claim Boundary

This is dependency handoff only. It does not install OptiX, does not run RTDL/OptiX backend execution, and does not authorize:

- public true-zero-copy wording
- public speedup wording
- whole-application claims
- stable primitive promotion
- partner tensor handoff
- release action

## Files

- `scripts/goal1490_v1_5_4_optix_dependency_handoff.py`
- `tests/goal1490_v1_5_4_optix_dependency_handoff_test.py`
- `docs/reports/goal1490_v1_5_4_optix_dependency_handoff_plan_2026-05-07.md`

