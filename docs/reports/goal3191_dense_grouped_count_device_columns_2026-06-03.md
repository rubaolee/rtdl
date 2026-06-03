# Goal3191: Dense Grouped-Count Device Columns

Date: 2026-06-03

## Purpose

Goal3189 proved a first continuation over Goal3185/3187 segment-pair candidate
device columns, but the result was still compact host-materialized rows.

Goal3191 adds a generic dense direct-address grouped-count result so a caller can
keep the dense `count[group_id]` column resident on CUDA after grouping.

## Code Changes

- Added native ABI struct:
  `RtdlNativeDeviceGroupedCountI64Columns`.
- Added native ABI:
  `rtdl_optix_columnar_device_payload_grouped_count_i64_device_columns_with_capacity`.
- Added release ABI:
  `rtdl_optix_release_device_grouped_count_i64_columns`.
- Reused the existing device-column grouped-count CUDA kernel and factored its
  module initialization into `ensure_device_column_grouped_i64_pipeline()`.
- Added Python output owner:
  `OptixNativeDeviceGroupedCountI64Output`.
- Added Python continuation:
  `OptixNativeDevicePairColumnOutput.grouped_count_by_left_id_device_columns(...)`.

## Boundary

This is a generic dense grouped-count continuation. It does not add app-specific native logic and it does not add a new RayJoin path.

It does:

- reuse the existing grouped-count kernel,
- consume a generic int64-compatible device column as the group key,
- keep the dense `count[group_id]` column resident on CUDA,
- expose optional CuPy wrapping through `cp.cuda.UnownedMemory`,
- fail closed when keys exceed the caller's direct-address capacity.

Goal3191 reuses the existing grouped-count kernel.
Goal3191 keeps the dense `count[group_id]` column resident on CUDA.

It does not:

- compact the dense device counts into resident sparse rows,
- materialize exact intersection witness rows,
- compute final Spatial RayJoin semantics,
- prove true zero-copy,
- prove a public speedup,
- authorize release.

The capacity contract remains direct-address: `group_capacity` must exceed the maximum non-negative group key unless the caller remaps sparse keys before grouping.
Plainly: group_capacity must exceed the maximum non-negative group key.

Boundary flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Validation

Local validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3191_dense_grouped_count_device_columns_test tests.goal3189_pair_column_grouped_count_continuation_test tests.goal3187_segment_pair_candidate_chunked_append_test tests.goal3185_segment_pair_candidate_device_columns_test
```

Initial status: local source validation is expected first. Pod validation should
rebuild the OptiX library, run the focused tests, call
`candidate_device_columns(...).grouped_count_by_left_id_device_columns(...)` on
the authored crossing-segment case, wrap the returned dense counts with CuPy,
and compare the non-zero entries with the exact row path.
