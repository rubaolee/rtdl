# Goal3403 - Pair Column Capacity Status Contract

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3400 proved that exact device-column streams fail closed when a caller gives
too small a `max_rows` bound. Goal3401 fixed the misleading successful-capacity
metadata. Goal3403 makes the recovery path explicit and generic: every
`OptixNativeDevicePairColumnOutput` now exposes a capacity-status contract with
the bounded capacity, produced row count, required capacity, overflow flag, and
retry hint.

This is intentionally not hidden dispatch. The runtime reports what happened;
the caller chooses whether to retry with the required capacity.

## Contract

The new metadata shape is:

```text
capacity
row_count
required_capacity
overflowed
overflow_policy = fail_closed
retry_capacity_hint
partial_result_returned
```

Successful streams must satisfy:

```text
required_capacity <= capacity
overflowed = false
```

Overflowed streams must satisfy:

```text
row_count = 0
required_capacity > capacity
overflowed = true
retry_capacity_hint = required_capacity
```

## Evidence

Local tests:

```text
py -3 -m unittest tests.goal3403_pair_column_capacity_status_contract_test
```

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit:
`8bdc8a647bc4e126d43f7eeccc71d774f156a00d`

The pod artifacts were refreshed from the tracked Goal3403 contract:

| Probe | Capacity | Required capacity | Retry hint | Overflow |
| --- | ---: | ---: | ---: | --- |
| 4096-chain exact stream | 11316 | 11316 | n/a | false |
| Full `br_county.cdb` exact stream | 47262 | 47262 | n/a | false |
| Forced `max_rows=100` overflow | 100 | 11316 | 11316 | true |

The overflow artifact is refreshed by
`scripts/goal3400_exact_device_columns_overflow_probe.py` and records the same
status fields at top level.

## Boundary

This is a capacity-planning and fail-closed recovery contract. It does not
implement automatic retry, chunked execution, streaming overflow recovery,
device-only exact predicates, true zero-copy, hidden dispatch, public speedup
claims, RT-core speedup claims, RayJoin reproduction claims, or release
authorization.
