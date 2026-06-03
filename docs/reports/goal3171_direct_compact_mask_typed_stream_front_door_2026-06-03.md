# Goal3171 - Direct Compact-Mask Typed-Stream Front Door

Date: 2026-06-03

Status: local validation complete; pod validation pending.

## Purpose

Goal3147 promoted `compact_mask_i64` into the v2.8 typed-stream partner-consumer
front door, but RayJoin and triangle-counting still had to build an empty
segmented row adapter just to express caller-owned `values + mask` columns.

Goal3171 adds a direct caller-column helper:

`execute_compact_mask_typed_stream_partner_columns(...)`

This keeps the existing generic operation and canonical output schema, while
removing the empty-row adapter ceremony from app wrappers.

## What Changed

- Added `rt.execute_compact_mask_typed_stream_partner_columns(...)`.
- The helper accepts `values`, `mask`, explicit `partner`, explicit
  `stream_id`, optional `block_size`, and optional `producer_primitive`.
- The helper publishes a `candidate_stream` typed result-stream contract.
- Because `V28GroupedContinuationPlan` requires a group column, the helper uses
  a schema-only group column:
  - `group_ids:int64`
  - role: `group_key`
  - shape: `(0,)`
  - `required_for_continuation: False`
- The actual partner input mapping remains only:
  - `values -> values`
  - `mask -> mask`
- Added typed-stream semantics for `compact_mask_i64`.
- Migrated RayJoin and triangle-counting compact-mask preview wrappers to the
  direct helper while preserving their v2.6 compatibility function names.

## Boundary

This goal does not promote a native producer, does not replace RT traversal,
does not claim device-resident streams, does not claim true zero-copy, does not
authorize public speedup wording, and does not authorize release packaging.

The helper rejects hidden partner selection and preserves:

- `automatic_partner_selection_allowed: False`
- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `app_specific_engine_logic_allowed: False`

RayJoin and triangle-counting vocabulary remains in the benchmark app wrappers.
The helper itself is a generic compact-mask continuation over typed columns.

## Local Validation

Compile check:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m py_compile `
  src\rtdsl\v2_8_typed_result_stream.py `
  src\rtdsl\v2_8_segmented_typed_stream_adapter.py `
  src\rtdsl\__init__.py `
  examples\v2_0\research_benchmarks\spatial_rayjoin\rtdl_rayjoin_v2_spatial_join_app.py `
  examples\v2_0\research_benchmarks\triangle_counting\rtdl_triangle_counting_benchmark_app.py `
  tests\goal3171_direct_compact_mask_typed_stream_front_door_test.py `
  tests\goal3151_v2_8_benchmark_front_door_adoption_audit_test.py
```

Result: pass.

Regression slice:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3171_direct_compact_mask_typed_stream_front_door_test `
  tests.goal3151_v2_8_benchmark_front_door_adoption_audit_test `
  tests.goal3002_rayjoin_numba_compact_mask_wiring_test `
  tests.goal2999_triangle_counting_numba_compact_mask_wiring_test `
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test `
  tests.goal3147_compact_mask_front_door_test
```

Result: 43 tests pass.
