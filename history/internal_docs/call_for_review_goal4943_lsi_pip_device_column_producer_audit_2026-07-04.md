# Call For Review - Goal4943 LSI/PIP Device-Column Producer Audit

Date: 2026-07-04

## Packet To Review

- `history/internal_docs/goal4943_lsi_pip_device_column_producer_audit_2026-07-04.md`
- `src/rtdsl/device_column_row_buffer.py`
- `src/rtdsl/__init__.py`
- `tests/goal4942_device_column_row_buffer_handoff_test.py`
- `tests/goal4943_lsi_pip_device_column_producer_audit_test.py`

## Requested Verdict Label

`approve_goal4943_lsi_adapter_and_pip_gap_record`

## Review Questions

1. Does the report correctly identify that LSI already has a Python-visible native device-column producer through `PreparedOptixSegmentPairIntersector2D.candidate_device_columns(...)` and `OptixNativeDevicePairColumnOutput`?
2. Is `device_column_row_buffer_from_native_pair_columns(...)` a generic pair-column adapter rather than a RayJoin-specific shortcut?
3. Does the LSI adapter correctly carry only generic `left_id/right_id` columns into `RtdlDeviceColumnRowBuffer` and v2.6 neutral handoff?
4. Does the packet avoid claiming that full exact LSI witness rows are device-resident?
5. Does the report correctly identify that PIP has native device count/write symbols but lacks a Python-visible pointer carrier?
6. Is it correct to classify PIP as `native_symbols_present_python_pointer_carrier_missing` rather than complete Layer 1 producer support?
7. Are tests sufficient to make the LSI/PIP audit machine-checkable without requiring a live OptiX runtime?
8. Are the non-authorization boundaries preserved: no speedup claim, no true-zero-copy claim, no full RayJoin pipeline claim, no claim that all LSI/PIP producers are complete?
9. Should Goal4943 close with `completed_lsi_producer_adapter__pip_pointer_carrier_gap_recorded`?
10. Should the next goal be the PIP pointer-carrier gap, or is additional LSI work required first?

## Non-Authorization Statement

Approval of this goal must not authorize:

- full RayJoin hot-path residency,
- full LSI exact witness row device residency,
- PIP producer completion,
- public speedup wording,
- true-zero-copy wording,
- same-stream async continuation,
- or app-specific schema promotion into RTDL core.
