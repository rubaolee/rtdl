# Goal2081 Streaming Witness Page Adapter

Date: 2026-05-15

## Purpose

Goal2079 showed that `segment_polygon_anyhit_rows` is the remaining weak OptiX/RT row in the v1.8-vs-v2.0 table: v2.0 was slower when it materialized full Python witness-row dictionaries. The design issue is not the ray traversal itself. It is the output contract.

Goal2081 adds a v2 app-layer adapter for bounded/streaming exact witness output:

- `segment_polygon_exact_witness_pair_page_optix_partner_columns`
- `segment_polygon_exact_witness_pair_page_optix_prepared_partner_columns`

## Design

The native engine still emits generic ray/primitive candidate witness pairs. This does not add app logic to the native engine.

The new adapter:

1. Calls the existing generic OptiX all-witness path.
2. Exact-filters candidate pairs in the partner layer.
3. Returns a bounded page of partner-owned columns:
   - `witness_ray_ids`
   - `witness_primitive_ids`
4. Avoids full Python row-table materialization for users who can continue in CuPy or Torch.

This is an app-layer continuation over a generic engine primitive, not a custom native segment/polygon kernel.

## Boundary

This is a structural fix for the full-witness output shape, not a release claim. Pod timing is still required before updating the OptiX/RT performance table or making any speedup wording.

Claim boundary:

- `v2_0_release_authorized`: false
- `whole_app_speedup_claim_authorized`: false
- `native_exact_row_semantics_authorized`: false
- `app_exact_row_semantics_authorized`: true
- `full_python_row_table_materialization_avoided`: true

## Verification

Local structural test:

`PYTHONPATH=src;. py -3 -m unittest tests.goal2081_streaming_witness_page_adapter_test`

The test verifies the adapter is public, preserves the generic native contract, exact-filters a fake witness stream, returns a bounded page of witness columns, and records that Python row materialization is avoided.

Pod timing runner:

`PYTHONPATH=src:. python3 scripts/goal2081_streaming_witness_page_perf.py --count 4096 --iterations 5 --partner cupy --output docs/reports/goal2081_streaming_witness_page_perf_pod.json`

The runner compares:

1. v1.8 native OptiX full witness rows.
2. v2.0 partner-column path that still returns full Python rows.
3. v2.0 streaming exact witness page columns.
