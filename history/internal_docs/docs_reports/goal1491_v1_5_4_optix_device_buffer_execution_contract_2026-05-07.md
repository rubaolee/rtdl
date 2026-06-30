# Goal 1491: v1.5.4 OptiX Device-Buffer Execution Contract

## Verdict

Accepted as a contract gate for the next Python+RTDL managed-buffer milestone.

The contract is currently blocked by Goal 1489 preflight because the current pod lacks OptiX SDK headers and `librtdl_optix.so`.

## First Target

The first end-to-end RTDL/OptiX device-buffer execution target should be `COLLECT_K_BOUNDED`.

Reason:

- the app-generic `int64` row ABI already exists
- the Embree and OptiX native symbols already exist
- fail-closed overflow semantics are already specified
- parity requirements are compact and mechanically checkable
- result transfer accounting is easier to audit than a larger app-shaped workload

Required native symbols:

- `rtdl_embree_collect_k_bounded_i64`
- `rtdl_optix_collect_k_bounded_i64`

## Required Contract

Input memory contract:

- RTDL-owned device-resident `int64` candidate rows
- explicit row width
- explicit candidate count
- explicit owner/lifetime metadata

Output memory contract:

- bounded RTDL-owned result buffer
- `valid_count_out`
- `overflowed_out`
- fail-closed overflow behavior

Parity must preserve:

- same candidate rows
- same row width
- same capacity
- same valid count
- same overflow flag
- same deduplicated lexicographic rows

Transfer accounting must record:

- host-to-device transfers before backend execution
- device-to-host transfers after backend execution
- internal device transfers, if any
- allocation-only transfers separately from content transfers

## Claim Boundary

This contract does not run OptiX, does not prove true zero-copy, and does not authorize:

- public true-zero-copy wording
- public speedup wording
- whole-application claims
- stable primitive promotion
- partner tensor handoff
- release action

## Files

- `src/rtdsl/v1_5_4_device_zero_copy_boundary.py`
- `src/rtdsl/__init__.py`
- `tests/goal1491_v1_5_4_optix_device_buffer_execution_contract_test.py`
- `docs/reports/goal1491_v1_5_4_optix_device_buffer_execution_contract_2026-05-07.md`

