# Goal 1494: COLLECT_K_BOUNDED OptiX ABI Classification

## Verdict

`goal1494_collect_k_optix_abi_classified_host_pointer`

## Finding

- Symbol: `rtdl_optix_collect_k_bounded_i64`
- Current API class: `host_pointer_api=True`
- Device-buffer API class: `device_buffer_api=False`
- Accepted for Goal1493 device-buffer execution: `False`

## Required Next Symbol Shape

- Candidate rows: `CUdeviceptr_or_uint64_device_pointer`
- Rows out: `CUdeviceptr_or_uint64_device_pointer`
- Metadata out: `host_or_device_explicit`
- Transfer accounting: `explicit_nonnegative_counters`

## Claim Boundary

Goal1494 classifies the current OptiX COLLECT_K_BOUNDED ABI only. The existing symbol is host-pointer/native-library boundary work, not accepted Goal1493 device-buffer execution evidence. This does not run OptiX, does not prove true zero-copy, and does not authorize public speedup wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
