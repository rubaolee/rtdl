# Call For Review - Goal4942 Device-Column Row-Buffer Handoff

Date: 2026-07-04

## Packet To Review

- `history/internal_docs/goal4942_device_column_row_buffer_handoff_2026-07-04.md`
- `src/rtdsl/device_column_row_buffer.py`
- `tests/goal4942_device_column_row_buffer_handoff_test.py`
- `tests/goal2990_v2_6_neutral_partner_handoff_test.py`
- `src/rtdsl/__init__.py`

## Requested Verdict Label

`approve_goal4942_reuse_first_layer1_device_column_handoff_adapter`

## Review Questions

1. Did Goal4942 correctly reuse the existing v2.5 hit-stream device-column and v2.6 neutral partner handoff assets instead of inventing a new memory system?
2. Is `RtdlDeviceColumnRowBuffer` generic enough for primitive-output named columns, rather than RayJoin or output-chain specific?
3. Does the adapter preserve the correct boundary that it validates the carrier/handoff but does not execute a partner continuation?
4. Does the Numba path correctly go through v2.6 neutral handoff without torch carrier/coercion?
5. Does the host-materialized path fail closed when device residency is required?
6. Is adapting `RtdlHitStreamColumnHandoff(ray_ids, primitive_ids)` into the generic row buffer a valid reuse of the v2.5 line?
7. Are the non-authorization boundaries clear enough: no public speedup, no whole-app speedup, no true-zero-copy claim, no release claim?
8. Is it correct that this closes only the generic carrier/validation gap, while still leaving per-primitive producer gaps for LSI/PIP device-column outputs?
9. Was the small Goal2990 test path update a legitimate maintenance fix after internal reports were moved from `docs/reports` to `history/internal_docs/docs_reports`?
10. Should Goal4942 close with `completed_reuse_first_layer1_device_column_row_buffer_adapter_no_speedup_claim`, or is additional work required before closing?

## Non-Authorization Statement

Approval of this goal must not authorize:

- public performance claims,
- true-zero-copy wording,
- whole-app speedup claims,
- app-specific output schemas in RTDL core,
- RayJoin-specific row-buffer schemas,
- same-stream async continuation claims,
- or any claim that all LSI/PIP producers already emit compatible device columns.
