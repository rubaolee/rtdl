# Goal1861 - Segment/Polygon Hitcount Device Count Columns

Status: pass-with-boundary

Date: 2026-05-13

## Scope

Goal1861 adds:

`rtdsl.segment_polygon_hitcount_optix_partner_device_count_columns(...)`

This is the device-column successor to the Goal1859 row adapter. It calls the
generic OptiX bounded all-witness contract, where native output is only
ray/primitive candidate witness IDs. Goal2000 found that this contract must not
be described as exact segment/polygon rows by itself: the app adapter must
filter candidates against the app geometry before materializing hit counts.
After that exact-filter step, the adapter returns partner-owned:

- `segment_ids`
- `hit_counts`

The adapter does not add a segment/polygon/count semantic to the native engine.

## Claim Boundary

The intended metadata boundary is:

- `native_engine_row_contract: generic_ray_primitive_candidate_witness_pairs`
- `app_count_materialization: partner_columns_from_host_exact_filter`
- `app_count_host_materialization: true`
- `whole_app_true_zero_copy_authorized: false`
- `v2_0_release_authorized: false`
- `whole_app_speedup_claim_authorized: false`

This is still useful because the adapter returns a columnar partner-facing
result, but it is not true whole-app zero-copy until the exact candidate filter
moves to partner-side GPU code. It is still not a v2.0 release gate or a public
speedup claim.

## Pod Smoke

Pod smoke validation was run on the RTX A4500 pod. Artifact:

`docs/reports/goal1861_segment_polygon_hitcount_device_count_columns_pod_smoke.json`

Both CuPy and Torch produced device-count columns that validate to:

```text
segment_ids = [101, 102, 103]
hit_counts = [2, 2, 0]
```

The historical artifact preserves the earlier device-output boundary. Goal2000
supersedes the stronger zero-copy wording for exact segment/polygon semantics:

- `app_count_materialization: partner_columns_from_host_exact_filter`
- `app_count_host_materialization: true`
- `whole_app_true_zero_copy_authorized: false`
- `v2_0_release_authorized: false`
- `whole_app_speedup_claim_authorized: false`

## Boundary

The counting step currently applies an exact host-side segment/triangle filter
to generic `(ray_id, primitive_id)` candidates, then materializes compact counts
back into partner columns. This preserves the app-agnostic native engine
contract, but broad performance and true-zero-copy claims remain blocked until
the exact filter is partner-side GPU code and measured on the RTX pod against
the same v1.8 app contract.
