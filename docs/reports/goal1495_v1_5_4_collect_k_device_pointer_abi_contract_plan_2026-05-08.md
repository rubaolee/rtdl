# Goal 1495: COLLECT_K_BOUNDED Device-Pointer ABI Contract Plan

## Verdict

Goal 1495 defines the future native ABI shape needed after Goal 1494 showed
that the current OptiX collect-k symbol is host-pointer based.

## Scope

- Primitive: `COLLECT_K_BOUNDED`
- Existing host symbol: `rtdl_optix_collect_k_bounded_i64`
- Proposed device symbol: `rtdl_optix_collect_k_bounded_i64_device`

## Contract Intent

The proposed device symbol must receive RTDL-owned CUDA device pointers for the
candidate rows and bounded output rows. It must return host metadata for emitted
count and overflow, and it must expose transfer-accounting counters.

This keeps the future implementation separate from the existing host-pointer ABI
and lets Goal 1493 intake distinguish true device-buffer evidence from current
native-library host-buffer parity.

## Claim Boundary

This goal defines the ABI contract only. It does not implement the native
symbol, does not run OptiX, does not prove true zero-copy, and does not authorize
public speedup wording, whole-app claims, partner tensor handoff, stable
primitive promotion, or release action.
