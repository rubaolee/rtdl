# Goal 1496: COLLECT_K_BOUNDED Device-Pointer Stub Gate

## Verdict

`goal1496_collect_k_device_pointer_dynamic_row_width_guarded`

## Implementation Guard

- Symbol: `rtdl_optix_collect_k_bounded_i64_device`
- Signature present: `True`
- Implementation present: `True`
- Implementation markers present: `True`
- Hidden host content buffer absent: `True`
- Accepted for Goal1493 device-buffer execution: `False`

## Claim Boundary

Goal1496 guards the OptiX COLLECT_K_BOUNDED device-pointer implementation shape. It is not accepted as Goal1493 device-buffer execution evidence until measured on an OptiX-ready NVIDIA pod and passed through Goal1493 intake. It does not prove true zero-copy and does not authorize public speedup wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
