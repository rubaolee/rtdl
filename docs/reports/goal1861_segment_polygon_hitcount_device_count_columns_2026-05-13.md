# Goal1861 - Segment/Polygon Hitcount Device Count Columns

Status: pass-with-boundary

Date: 2026-05-13

## Scope

Goal1861 adds:

`rtdsl.segment_polygon_hitcount_optix_partner_device_count_columns(...)`

This is the device-column successor to the Goal1859 row adapter. It still calls
the same generic OptiX bounded all-witness contract, where native output is only
ray/primitive witness IDs. The app-specific hit-count aggregation is then done
with partner GPU tensor operations in PyTorch or CuPy, returning partner-owned:

- `segment_ids`
- `hit_counts`

The adapter does not add a segment/polygon/count semantic to the native engine.

## Claim Boundary

The intended metadata boundary is:

- `native_engine_row_contract: generic_ray_primitive_witness_pairs`
- `app_count_materialization: partner_gpu_from_generic_witness_pairs`
- `app_count_host_materialization: false`
- `whole_app_true_zero_copy_authorized: true`
- `v2_0_release_authorized: false`
- `whole_app_speedup_claim_authorized: false`

This is stronger than Goal1859 because the app count output is no longer
materialized as Python rows. It is still not a v2.0 release gate or a public
speedup claim.

## Pod Smoke

Pod smoke validation was run on the RTX A4500 pod. Artifact:

`docs/reports/goal1861_segment_polygon_hitcount_device_count_columns_pod_smoke.json`

Both CuPy and Torch produced device-count columns that validate to:

```text
segment_ids = [101, 102, 103]
hit_counts = [2, 2, 0]
```

The artifact preserves the device-output boundary:

- `app_count_materialization: partner_gpu_from_generic_witness_pairs`
- `app_count_host_materialization: false`
- `whole_app_true_zero_copy_authorized: true`
- `v2_0_release_authorized: false`
- `whole_app_speedup_claim_authorized: false`

## Boundary

The counting step currently uses partner tensor primitives to map generic
`ray_id` witnesses back to compact input-segment positions, deduplicate
`(segment_position, primitive_id)` witness pairs, and count unique primitive hits
per input segment. This preserves non-contiguous segment IDs without using raw
application IDs as composite-key multipliers. That is acceptable as a
Python+partner+RTDL app adapter, but broad performance claims remain blocked
until it is measured on the RTX pod against the same v1.8 app contract and
reviewed.
