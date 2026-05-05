# Goal1279 v1.4 Polygon-Pair Primitive Contract Metadata

Date: 2026-05-05

Status: local v1.4 implementation checkpoint. This is not public RTX wording.

## Change

`polygon_pair_overlap_area_rows` now attaches a `primitive_contract` payload.
For Embree and OptiX native-assisted modes, the contract records:

- candidate discovery primitive: `ANY_HIT`;
- future exact-area aggregation primitive: `REDUCE_FLOAT(SUM)`;
- future area primitive status: deferred until the generic float-reduction
  contract exists;
- exact area continuation: app-specific native C++;
- Goal1270 candidate/positive-pair diagnostic split preserved;
- Embree as `cpu_rt_baseline_and_fallback`;
- OptiX as `nvidia_rt_target`.

The change is metadata only. It does not alter candidate discovery, exact area
continuation, rows, summaries, phase counters, or native continuation labels.

## Boundary

This contract covers only native RT candidate discovery for polygon pairs. It
does not claim a generic polygon overlay engine, does not claim generic area
reduction, and does not authorize public whole-app speedup wording.

## Verification

Focused local verification should include:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1279_v1_4_polygon_pair_primitive_contract_test \
  tests.goal713_polygon_overlap_embree_app_test \
  tests.goal1131_polygon_app_phase_contract_test \
  tests.goal1274_v1_3_primitive_contract_test
```

Result: 20 tests passed.

Combined v1.4 focused regression:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1279_v1_4_polygon_pair_primitive_contract_test \
  tests.goal1278_v1_4_sales_risk_primitive_contract_test \
  tests.goal1276_v1_4_graph_visibility_wrapper_metadata_test \
  tests.goal1275_v1_4_first_wrapper_slice_plan_test \
  tests.goal1274_v1_3_primitive_contract_test \
  tests.goal713_polygon_overlap_embree_app_test \
  tests.goal1131_polygon_app_phase_contract_test \
  tests.goal954_database_native_continuation_contract_test \
  tests.goal1128_embree_db_compact_summary_contract_test \
  tests.goal1156_db_compact_summary_batch_contract_test \
  tests.goal889_graph_visibility_optix_gate_test \
  tests.goal814_graph_optix_rt_core_honesty_gate_test
```

Result: 71 tests passed.
