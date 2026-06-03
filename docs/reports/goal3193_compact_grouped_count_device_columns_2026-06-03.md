# Goal3193: Compact Grouped-Count Device Columns

Date: 2026-06-03

## Purpose

Goal3191 kept dense direct-address `count[group_id]` results resident on CUDA.
That is useful for dense keys, but partner continuations often want only the
active groups.

Goal3193 adds compact grouped-count device columns: `group_key[]` and `count[]`
stay resident on CUDA, while a small row count scalar is materialized on host so
Python knows the valid prefix length.

## Code Changes

- Added native ABI struct:
  `RtdlNativeDeviceGroupedCountI64CompactColumns`.
- Added native ABI:
  `rtdl_optix_columnar_device_payload_grouped_count_i64_compact_device_columns_with_capacity`.
- Added release ABI:
  `rtdl_optix_release_device_grouped_count_i64_compact_columns`.
- Reused the existing grouped-count kernel.
- Added only a generic compact-count-columns kernel that converts dense
  `count[group_id]` into compact SoA columns.
- Added Python output owner:
  `OptixNativeDeviceGroupedCountI64CompactOutput`.
- Added Python continuation:
  `OptixNativeDevicePairColumnOutput.grouped_count_by_left_id_compact_device_columns(...)`.

## Boundary

This is a generic compact grouped-count continuation. It does not add app-specific native logic and it does not add a new RayJoin path.

It does:

- reuse the existing grouped-count kernel,
- add only a generic compact-count-columns kernel,
- keep `group_key[] and count[] stay resident on CUDA`,
- expose optional CuPy wrapping through `cp.cuda.UnownedMemory`,
- materialize the row count scalar on host,
- fail closed when keys exceed the caller's direct-address capacity.

Goal3193 reuses the existing grouped-count kernel.
Goal3193 adds only a generic compact-count-columns kernel.
For the compact output, group_key[] and count[] stay resident on CUDA.
The row count scalar is materialized on host.

It does not:

- materialize compact group/count columns on host except for validation,
- materialize exact intersection witness rows,
- compute final Spatial RayJoin semantics,
- prove true zero-copy,
- prove a public speedup,
- authorize release.

Boundary flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Validation

Local validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3193_compact_grouped_count_device_columns_test tests.goal3191_dense_grouped_count_device_columns_test tests.goal3189_pair_column_grouped_count_continuation_test tests.goal3187_segment_pair_candidate_chunked_append_test tests.goal3185_segment_pair_candidate_device_columns_test
```

Initial status: local source validation is expected first. Pod validation should
rebuild the OptiX library, run the focused tests, call
`candidate_device_columns(...).grouped_count_by_left_id_compact_device_columns(...)`
on the authored crossing-segment case, wrap the returned compact columns with
CuPy, and compare the `(group_key, count)` pairs with the exact row path.
