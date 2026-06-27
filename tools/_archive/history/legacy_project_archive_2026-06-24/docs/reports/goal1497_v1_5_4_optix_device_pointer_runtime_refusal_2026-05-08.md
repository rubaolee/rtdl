# Goal 1497: OptiX Device-Pointer Runtime Refusal

## Verdict

`goal1497_optix_device_pointer_runtime_refuses_without_explicit_experimental_opt_in`

## Runtime Surface

- Device symbol: `rtdl_optix_collect_k_bounded_i64_device`
- Host symbol: `rtdl_optix_collect_k_bounded_i64`
- Runtime refused execution: `True`
- Accepted for Goal1493 evidence: `False`

## Claim Boundary

Goal1497 wires Python runtime awareness of the measured OptiX COLLECT_K_BOUNDED device-pointer symbol, but refuses default execution unless the caller explicitly enables the experimental surface. It does not prove true zero-copy and does not authorize public speedup wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
