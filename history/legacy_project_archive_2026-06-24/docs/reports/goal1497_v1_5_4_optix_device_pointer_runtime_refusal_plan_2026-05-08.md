# Goal 1497: OptiX Device-Pointer Runtime Refusal Plan

## Verdict

Goal 1497 adds Python runtime awareness of the reserved
`rtdl_optix_collect_k_bounded_i64_device` symbol while refusing to execute it
until a measured native implementation exists.

## Scope

- Runtime file: `src/rtdsl/optix_runtime.py`
- Device symbol: `rtdl_optix_collect_k_bounded_i64_device`
- Host symbol: `rtdl_optix_collect_k_bounded_i64`

## Intent

Python+RTDL now has a stable name for the future OptiX device-pointer path, but
the runtime keeps it fail-closed. This avoids accidental Goal 1493 acceptance
before real native device execution exists and is measured on an OptiX-ready
NVIDIA system.

## Claim Boundary

This goal wires runtime awareness and refusal only. It does not run OptiX, does
not prove true zero-copy, and does not authorize public speedup wording,
whole-app claims, partner tensor handoff, stable primitive promotion, or release
action.
