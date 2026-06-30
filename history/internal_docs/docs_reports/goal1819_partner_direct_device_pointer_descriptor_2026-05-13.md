# Goal1819: Partner Direct Device-Pointer Descriptor

Status: `accept-with-boundary`

Date: 2026-05-13

## Scope

Goal1819 begins the first hard blocker in the strict v2.0 birth gate: direct
device-pointer handoff. It adds a public descriptor-only API that can observe a
partner-owned CUDA pointer from PyTorch, CuPy, or generic DLPack-style tensors.

This is not native execution and not true zero-copy evidence.

## Public API

```python
handoff = rt.prepare_direct_device_pointer_handoff(tensor)
metadata = handoff.to_metadata()
```

The returned `RtdlDevicePointerHandoff` records:

- `data_ptr`;
- `device_type` and `device_id`;
- `dtype`;
- `shape` and `strides`;
- `byte_offset`;
- `access_mode`;
- `stream_handle`;
- `source_protocol`;
- `transfer_mode = "device_descriptor_only"`;
- `direct_device_pointer_observed = True`;
- `direct_device_handoff_authorized = False`;
- `true_zero_copy_authorized = False`.

## Boundaries

The API rejects:

- CPU tensors;
- missing or zero CUDA pointers;
- non-zero stream handles;
- any attempt to set `direct_device_handoff_authorized = True`;
- any attempt to set `true_zero_copy_authorized = True`.

The partner protocol contract now records:

```text
direct_device_handoff_status = "descriptor_only_claims_blocked"
```

## Why This Matters

The previous partner path could validate partner descriptors only as part of
host staging. Goal1819 separates pointer observation from host staging so the
next v2.0 slices can build a native OptiX execution path around an explicit
device-pointer contract.

## What Remains

This goal does not satisfy the strict v2.0 blocker yet. The release gate still
requires:

- native OptiX execution from the device descriptor;
- stream and lifetime rules with real CUDA synchronization evidence;
- measured artifacts proving whether hidden host copies occur;
- 3-AI consensus before any true zero-copy or direct-handoff public claim.
