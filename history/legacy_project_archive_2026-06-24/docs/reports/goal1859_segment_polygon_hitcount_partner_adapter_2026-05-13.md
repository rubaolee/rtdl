# Goal1859 - Segment/Polygon Hitcount Partner Column Adapter

Status: pass-with-boundary

Date: 2026-05-13

## Scope

Goal1859 adds:

`rtdsl.segment_polygon_hitcount_optix_partner_columns(...)`

This is the second app-level v2.0 OptiX partner adapter. It accepts
caller-supplied PyTorch/CuPy CUDA columns for segment rays, polygon triangles,
and triangle AABBs. It reuses the generic bounded all-witness native contract
and materializes one `{"segment_id", "hit_count"}` row per input segment in
Python.

The native engine still emits only generic ray/primitive witness pairs. It does
not see `segment_polygon_hitcount` semantics, app row names, or app counting
policy.

## Pod Smoke

Pod smoke validation was run on the RTX A4500 pod with the corrected
all-witness native library. Artifact:

`docs/reports/goal1859_segment_polygon_hitcount_partner_adapter_pod_smoke.json`

Both CuPy and Torch produced:

```text
[
  {"segment_id": 101, "hit_count": 2},
  {"segment_id": 102, "hit_count": 2},
  {"segment_id": 103, "hit_count": 0}
]
```

Both artifacts preserve:

- `native_engine_row_contract: generic_ray_primitive_witness_pairs`
- `app_count_materialization: python_from_generic_witness_pairs`
- `app_count_host_materialization: true`
- `true_zero_copy_authorized: true`
- `whole_app_true_zero_copy_authorized: false`
- `exact_row_semantics_authorized: true`
- `v2_0_release_authorized: false`
- `whole_app_speedup_claim_authorized: false`

## Boundary

This proves a second app-level adapter shape, not a release gate. Counting is
currently materialized in Python from generic witness IDs. A future compact
count-output adapter may reduce host materialization, but that would be a new
goal and must preserve the same app-agnostic native boundary.
