# Goal3189: Pair-Column Grouped Count Continuation

Date: 2026-06-03

## Purpose

Goal3185 added device-resident segment-pair candidate ID columns, and Goal3187
made their traversal producer chunk append into the same output stream.

Goal3189 adds the first generic continuation over those columns: counts candidate rows per `left_id` using the existing OptiX device-column grouped-count primitive.

## Code Changes

- Added Python method:
  `OptixNativeDevicePairColumnOutput.grouped_count_by_left_id(...)`.
- The method describes the resident `left_id` CUDA pointer as a generic
  `_RtdlDevicePayloadField`.
- It calls the existing native ABI:
  `rtdl_optix_columnar_device_payload_grouped_count_i64_with_capacity`.
- It returns host-materialized compact count rows:
  `{"left_id": ..., "count": ...}`.

## Boundary

This is a generic device-column grouped-count continuation. It does not add a new native kernel and it does not add RayJoin-specific native-engine logic.

It does:

- consume the native-owned CUDA `left_id` column from the pair candidate stream,
- count candidate rows per `left_id`,
- fail closed if the candidate stream overflowed,
- fail closed if the caller's `group_capacity` is too small,
- reuse the existing generic device-column grouped-count implementation.

It does not:

- materialize exact intersection witness rows,
- compute final Spatial RayJoin semantics,
- keep the grouped-count result resident on device,
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
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3189_pair_column_grouped_count_continuation_test tests.goal3185_segment_pair_candidate_device_columns_test
```

Initial status: local source validation is expected first. Pod validation should
call `candidate_device_columns(...).grouped_count_by_left_id(...)` on an authored
crossing-segment case and compare counts against the exact row path.
