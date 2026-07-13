# Claude Review - Goal5043 Public DeviceColumnBuffer Contract

Date: 2026-07-05

Verdict:

```text
approve_goal5043_public_device_column_buffer_contract
```

## Summary

Claude reviewed `DeviceColumnBuffer`, the export boundary, the tests, and the supporting report.  The implementation was approved as a clean public wrapper over the existing `RtdlDeviceColumnRowBuffer` substrate, without promoting old internal adapter names.

## Verified Claims

- `DeviceColumnBuffer` composes an `RtdlDeviceColumnRowBuffer`; it does not create a fifth columnar surface.
- Public exports are limited to the clean v2.14.4 API names.  Old adapter names remain importable but absent from `rt.__all__`.
- The four-state stream-ordering vocabulary is preserved:

```text
not_proven
same_stream
producer_event_waited_by_consumer
host_synchronized_before_consumer
```

- Device residency is derived from source mode, `materializes_host_rows_for_bridge`, and actual column interfaces; there is no settable self-declared residency flag.
- Metadata keeps the claim boundary closed:

```text
public_speedup_claim_authorized = false
whole_app_speedup_claim_authorized = false
true_zero_copy_claim_authorized = false
app_specific_schema_allowed = false
residency_self_declared = false
```

- Lifetime behavior is correct: owned owners are closed exactly once, borrowed owners are not closed by the buffer, and context-manager exit is idempotent.
- Partner handoff reuses the existing v2.6 neutral path and fails closed for host-materialized buffers.
- The six Goal5043 tests cover public exports, old-name boundary, stream ordering, residency derivation, host-materialized rejection, lifetime close behavior, and invalid-state failures.

## Process Caveat

Claude could not execute tests in its own sandbox because the mounted copies of large files appeared truncated, causing a spurious import/syntax issue.  Direct source inspection showed the real files were complete.  This was treated as a sandbox sync artifact, not a code defect.  The report's documented local run remains:

```text
Ran 17 tests in 0.021s
OK
```

## Closeout

Goal5043 may close as:

```text
completed_public_device_column_buffer_contract
```

Next authorized goal:

```text
Goal5044 - Public Prepared Session / Query-Batch Contract
```
