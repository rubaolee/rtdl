# Goal1290 v1.5 Generic Prepared ANY_HIT/COUNT_HITS

Date: 2026-05-05

Status: local v1.5 prepared-primitive slice. This is not pod evidence and does
not authorize public RTX wording.

## Change

Added `run_generic_prepared_ray_triangle_any_hit_count(...)`, an app-name-free
prepared raw ray/triangle `ANY_HIT` plus `COUNT_HITS` helper for repeated
queries. The graph visibility prepared-count compatibility wrapper now delegates
to this generic helper while preserving its existing JSON shape:

- graph wrapper output still returns `blocked_count`;
- phase counter names are preserved;
- `visibility_query_repeats` still controls repeated prepared queries.

## Boundary

This is an OptiX-focused prepared generic surface for the current NVIDIA
performance work. Embree prepared parity and public performance evidence remain
future work. Vulkan, HIPRT, and Apple RT remain frozen before v2.1.

## Verification

Focused prepared-generic and affected v1.4 guard tests:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1290_v1_5_generic_prepared_anyhit_count_test \
  tests.goal1275_v1_4_first_wrapper_slice_plan_test
```

Result: 8 tests passed.

Combined v1.5/v1.4 regression:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1290_v1_5_generic_prepared_anyhit_count_test \
  tests.goal1289_v1_5_graph_visibility_generic_dispatch_test \
  tests.goal1288_v1_5_generic_anyhit_count_test \
  tests.goal1287_v1_4_exit_readiness_and_v1_5_blockers_test \
  tests.goal1286_v1_4_contract_inventory_gate_test \
  tests.goal1285_v1_4_contract_inventory_export_test \
  tests.goal1284_v1_4_primitive_contract_inventory_test \
  tests.goal1283_v1_4_runtime_contract_validation_test \
  tests.goal1282_v1_4_primitive_contract_schema_test \
  tests.goal1281_v1_4_wrapper_consolidation_status_test \
  tests.goal1280_v1_4_polygon_jaccard_diagnostic_contract_test \
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

Result: 112 tests passed.
