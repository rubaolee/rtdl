# Goal5043 - Public DeviceColumnBuffer Contract

Date: 2026-07-05

Status: completed public contract implementation

Exit label:

```text
completed_public_device_column_buffer_contract
```

## Purpose

Goal5043 turns the existing v2.14.2 row-buffer substrate into a public v2.14.4 `DeviceColumnBuffer` contract without promoting the old internal adapter names.  This is the first actual v2.14.4 API consolidation step after the Goal5042 inventory.

## Files Changed

- `src/rtdsl/device_column_row_buffer.py`
- `src/rtdsl/__init__.py`
- `tests/goal5043_public_device_column_buffer_contract_test.py`

Related documentation carried forward:

- `history/internal_docs/goal5042_existing_asset_inventory_and_api_mapping_2026-07-05.md`
- `history/internal_docs/claude_review_goal5042_asset_inventory_and_api_mapping_2026-07-05.md`

## What Was Implemented

### Public Symbols

New public exports:

```text
DEVICE_COLUMN_BUFFER_CONTRACT_VERSION
DEVICE_COLUMN_BUFFER_API_MATURITY
DEVICE_COLUMN_BUFFER_CLAIM_BOUNDARY
DEVICE_COLUMN_BUFFER_OWNER_LIFETIME_STATES
DeviceColumnBuffer
describe_device_column_buffer_contract
device_column_buffer
device_column_buffer_from_row_buffer
```

Existing internal substrate names remain importable for compatibility but are still not in `rt.__all__`:

```text
RtdlDeviceColumnRowBuffer
prepare_device_column_row_buffer
device_column_row_buffer_from_native_pair_columns
device_column_row_buffer_from_point_location_id_columns
```

This prevents v2.14.4 from accidentally publishing the old experimental adapter surface.

### Public Wrapper

`DeviceColumnBuffer` wraps `RtdlDeviceColumnRowBuffer` and exposes:

- `columns`
- `row_count`
- `column_count`
- `producer`
- `source_mode`
- `materializes_host_rows_for_bridge`
- `producer_consumer_stream_ordering`
- `device_resident_candidate`
- `close()`
- context-manager lifetime
- `to_metadata()`
- `plan_partner_handoff(...)`
- `prepare_partner_handoff(...)`

### Four-State Stream Ordering Preserved

The public contract preserves the existing richer vocabulary:

```text
not_proven
same_stream
producer_event_waited_by_consumer
host_synchronized_before_consumer
```

It does not downgrade this to the weaker `synchronized/event_ordered/unknown` vocabulary rejected in the review.

### Device Residency Is Derived, Not Declared

The public metadata records:

```text
device_resident_candidate
materializes_host_rows_for_bridge
residency_self_declared = false
```

Residency is derived from the underlying column interfaces and host-materialization metadata.  App flags or CLI flags cannot self-certify residency.

### Lifetime

`DeviceColumnBuffer` supports:

```text
borrowed
owned_close_on_buffer_close
no_close_required
```

Owned owners are closed exactly once through `close()` or context-manager exit.  Borrowed owners are not closed by the buffer.

## What Was Not Implemented

- No new native code.
- No RayJoin app changes.
- No public `device_group_by`.
- No `device_order_by` work yet.
- No performance claim.
- No true-zero-copy wording.

## Verification

Command:

```powershell
$env:PYTHONPATH="src"; py -3 -m unittest tests.goal5043_public_device_column_buffer_contract_test tests.goal4942_device_column_row_buffer_handoff_test tests.goal4943_lsi_pip_device_column_producer_audit_test
```

Result:

```text
Ran 17 tests in 0.023s
OK
```

Environment note:

- `python` command was unavailable due to the Windows app execution alias.
- `pytest` was not installed in the local `py -3` interpreter.
- The standard-library `unittest` run above passed with `PYTHONPATH=src`.
- `py -3` printed `Could not find platform independent libraries <prefix>`, but the tests imported and executed successfully.

## Claim Boundary

Authorized:

- public `DeviceColumnBuffer` contract exists;
- public wrapper preserves the existing four-state stream-ordering vocabulary;
- public wrapper derives device-residency from metadata;
- public wrapper can plan/prepare partner handoff through the existing v2.6 neutral path;
- old experimental row-buffer adapter names remain internal with respect to `__all__`.

Not authorized:

- `device_group_by` public readiness;
- broad device-columnar performance claims;
- true-zero-copy public wording;
- RayJoin performance claims;
- native ABI rename completion.

## Next Goal

Proceed to:

```text
Goal5044 - Public Prepared Session / Query-Batch Contract
```

Goal5044 should make regime labels and prepare/query-batch metadata a public concept while preserving the fresh/replay/query-many distinctions from v2.14.3.
