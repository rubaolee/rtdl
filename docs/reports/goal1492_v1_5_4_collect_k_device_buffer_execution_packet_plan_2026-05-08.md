# Goal 1492: v1.5.4 COLLECT_K_BOUNDED Device-Buffer Execution Packet Plan

## Verdict

Accepted as local preparation for the first future RTDL/OptiX device-buffer execution run.

This packet does not run OptiX. It prepares the fixture, expected reference result, parity requirements, and transfer-accounting skeleton for the first run after Goal 1489 preflight becomes green.

## Fixture

Candidate rows:

- `(2, 20)`
- `(1, 10)`
- `(2, 20)`
- `(3, 30)`

Capacity: `3`

Expected reference result:

- valid count: `3`
- overflowed: `False`
- candidate rows: `((1, 10), (2, 20), (3, 30))`

The duplicate `(2, 20)` is intentionally included so the execution result must preserve the existing deduplication and lexicographic ordering contract.

## Required Future Execution

The future OptiX-ready run must provide:

- backend: `optix`
- symbol: `rtdl_optix_collect_k_bounded_i64`
- RTDL-owned device-resident `int64` input rows
- bounded RTDL-owned result buffer
- same-contract parity JSON
- transfer-accounting summary

## Current Status

The packet is blocked on the current pod because Goal 1489 reported missing OptiX SDK headers and missing `librtdl_optix.so`.

## Claim Boundary

This packet does not authorize:

- public true-zero-copy wording
- public speedup wording
- whole-application claims
- stable primitive promotion
- partner tensor handoff
- release action

## Files

- `scripts/goal1492_v1_5_4_collect_k_device_buffer_execution_packet.py`
- `tests/goal1492_v1_5_4_collect_k_device_buffer_execution_packet_test.py`
- `docs/reports/goal1492_v1_5_4_collect_k_device_buffer_execution_packet_plan_2026-05-08.md`

