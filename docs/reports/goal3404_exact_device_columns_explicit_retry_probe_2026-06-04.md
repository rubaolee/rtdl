# Goal3404 - Exact Device Columns Explicit Retry Probe

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3403 exposed a generic pair-column capacity-status contract. Goal3404 proves
the intended user recovery path on hardware: callers can run with a bounded
capacity, observe fail-closed overflow, read `retry_capacity_hint`, and
explicitly retry with that capacity.

This is not hidden dispatch or automatic retry. The caller remains in control.

## Evidence

Artifact:
`docs/reports/goal3404_exact_device_columns_explicit_retry_probe_2026-06-04.json`

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit:
`02bd4510a5af994f81a601a75f3f5a467704d985`

| Step | Capacity | Required capacity | Row count | Overflow | Retry hint |
| --- | ---: | ---: | ---: | --- | ---: |
| Initial bounded attempt | 100 | 11316 | 0 | true | 11316 |
| Explicit retry | 11316 | 11316 | 11316 | false | n/a |

The explicit retry stream was device-resident and matched the exact host-refined
row pairs:

| Measure | Value |
| --- | ---: |
| Exact rows | 11316 |
| Retry rows | 11316 |
| Missing exact pairs | 0 |
| Extra pairs | 0 |
| Pairs match | true |

## Boundary

This proves explicit capacity recovery for the existing host-refined exact
device-column bridge. It does not implement automatic retry, chunked streaming
overflow recovery, a device-only exact predicate, true zero-copy, hidden
dispatch, public speedup claims, RT-core speedup claims, RayJoin reproduction
claims, or release authorization.
