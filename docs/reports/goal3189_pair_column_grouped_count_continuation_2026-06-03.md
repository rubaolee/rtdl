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

The reused grouped-count primitive uses direct-address key capacity. For this
first continuation, `group_capacity` must exceed the maximum non-negative
`left_id` key unless the caller remaps sparse IDs before grouping.

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
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3189_pair_column_grouped_count_continuation_test tests.goal3187_segment_pair_candidate_chunked_append_test tests.goal3185_segment_pair_candidate_device_columns_test
```

Status: local source validation passed.

Pod validation artifact:

- `docs/reports/goal3189_pod_pair_column_grouped_count_continuation_2026-06-03.json`
- Commit under test: `2a33da90`
- Focused pod tests: passed.
- Authored live smoke: 16 horizontal left segments crossed 4 vertical right
  segments.
- Exact row path produced 64 rows.
- Device candidate columns produced 64 candidate rows and 64 candidate events.
- `grouped_count_by_left_id(group_capacity=300)` produced 16 compact count
  rows.
- `all_match_exact_rows: true`
- Negative probe: `group_capacity=64` failed closed because left IDs `200..215`
  exceed the direct-address key capacity.
