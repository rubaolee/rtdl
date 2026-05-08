# Goal 1500: OptiX Device COLLECT_K_BOUNDED Measurement

## Verdict

`goal1500_measured_optix_device_collect_k_packet`

## Scope

- Backend: `optix`
- Symbol: `rtdl_optix_collect_k_bounded_i64_device`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `6f953c4434147abd29b9c88dda1f72f14b23b233`

## Parity

- Candidate rows: `True`
- Valid count: `True`
- Overflow flag: `True`

## Transfer Accounting

- H2D setup transfers before backend execution: `1`
- D2H metadata transfers after backend execution: `2`
- Internal device transfers: `0`

## Claim Boundary

This is measured device-pointer execution evidence for the Goal1492 packet only. It does not authorize true zero-copy wording, public speedup wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
