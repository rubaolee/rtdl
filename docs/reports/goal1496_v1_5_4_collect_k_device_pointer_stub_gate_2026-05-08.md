# Goal 1496: COLLECT_K_BOUNDED Device-Pointer Stub Gate

## Verdict

`goal1496_collect_k_device_pointer_stub_fail_closed`

## Stub

- Symbol: `rtdl_optix_collect_k_bounded_i64_device`
- Signature present: `True`
- Implementation present: `True`
- Fail-closed stub present: `True`
- Accepted for Goal1493 device-buffer execution: `False`

## Claim Boundary

Goal1496 reserves the proposed OptiX COLLECT_K_BOUNDED device-pointer ABI as a fail-closed native stub only. It does not implement device execution, does not run OptiX, does not prove true zero-copy, and does not authorize public speedup wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
