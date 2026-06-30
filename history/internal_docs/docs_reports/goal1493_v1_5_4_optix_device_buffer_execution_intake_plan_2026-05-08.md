# Goal 1493: OptiX Device-Buffer Execution Intake Plan

## Verdict

Goal 1493 adds a strict intake validator for the future measured OptiX
device-buffer execution result prepared by Goal 1492.

## Scope

- Source packet: `docs/reports/goal1492_v1_5_4_collect_k_device_buffer_execution_packet_2026-05-08.json`
- Primitive: `COLLECT_K_BOUNDED`
- Target backend: `optix`
- Required native symbol: `rtdl_optix_collect_k_bounded_i64`

## Required Future Evidence

- Real NVIDIA hardware measurement.
- Green Goal 1489 OptiX device-buffer preflight.
- Same candidate rows, valid count, and overflow flag as the Goal 1492 Python reference.
- Explicit host-to-device, device-to-host, and internal-device transfer accounting.
- Allocation-only transfers distinguished from content transfers.

## Claim Boundary

This goal prepares validation only. It does not run OptiX, does not prove true
zero-copy, and does not authorize public speedup wording, whole-app claims,
partner tensor handoff, stable primitive promotion, or release action.
