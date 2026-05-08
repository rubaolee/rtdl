# Goal 1497: OptiX Device-Pointer Runtime Refusal

## Verdict

`goal1497_optix_device_pointer_runtime_refuses_unimplemented_execution`

## Runtime Surface

- Device symbol: `rtdl_optix_collect_k_bounded_i64_device`
- Host symbol: `rtdl_optix_collect_k_bounded_i64`
- Runtime refused execution: `True`
- Accepted for Goal1493 evidence: `False`

## Claim Boundary

Goal1497 wires Python runtime awareness of the reserved OptiX COLLECT_K_BOUNDED device-pointer symbol, but refuses execution until a measured native implementation exists. It does not run OptiX, does not prove true zero-copy, and does not authorize public speedup wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
