# Goal3173 - Direct Bounded-Collect Typed-Stream Front Door

Date: 2026-06-03

Status: local and pod validation complete.

## Purpose

Goal3171 gave compact-mask continuation a direct v2.8 caller-column front
door. Goal3173 does the same for generic bounded collection:
`execute_bounded_collect_typed_stream_partner_columns(...)`.

The operation is intentionally generic. It consumes caller-supplied partner
columns:

- `group_ids`
- `item_ids`

and executes `bounded_collect_finalize_i64` with `group_count`, `k`, and an
optional `total_row_capacity`. The canonical output schema is:

- `group_ids`
- `item_ids`
- `row_offsets`

## Boundary

The helper models fail-closed overflow for bounded per-group item collection.
It does not define contact, collision, spatial, or app-specific semantics.
Apps may interpret the item IDs as witnesses, but the v2.8 front door only sees
generic groups and items.

The helper requires an explicit user-selected partner and uses caller-supplied partner columns. It does not hide row materialization or choose a partner.

The helper continues to enforce:

- `automatic_partner_selection_allowed: False`
- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `app_specific_engine_logic_allowed: False`

It does not promote a native producer, prove device-resident typed streams, or
authorize release wording.

## Validation

Focused local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3173_direct_bounded_collect_typed_stream_front_door_test `
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test
```

Result: 23 tests passed locally.

Focused pod validation:

```bash
cd /root/rtdl_goal3151
git fetch origin main
git reset --hard origin/main
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  /root/venvs/rtdl_goal3154/bin/python -m unittest \
  tests.goal3173_direct_bounded_collect_typed_stream_front_door_test \
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test
```

Pod result: commit `97be9d1d`, 23 tests passed.
