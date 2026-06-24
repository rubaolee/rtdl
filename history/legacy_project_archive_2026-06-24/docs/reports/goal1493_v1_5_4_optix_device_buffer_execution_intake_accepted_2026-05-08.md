# Goal 1493: OptiX Device-Buffer Execution Intake

## Verdict

`goal1493_measured_optix_execution_intake_accepted`

## Scope

- Primitive: `COLLECT_K_BOUNDED`
- Backend: `optix`
- Symbol: `rtdl_optix_collect_k_bounded_i64_device`

## Claim Boundary

Goal1493 accepts measured OptiX device-buffer execution parity and transfer-accounting evidence only. It still does not authorize true zero-copy wording, public speedup wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.

## Accepted Evidence

- Valid count parity: `True`
- Overflow parity: `True`
- Candidate row parity: `True`
- H2D transfers before backend execution: `1`
- D2H transfers after backend execution: `2`
