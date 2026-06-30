# Goal1288 v1.5 Generic ANY_HIT/COUNT_HITS Slice

Date: 2026-05-05

Status: first local v1.5 implementation slice. This is not a public release
gate, not pod evidence, and not public RTX wording authorization.

## Change

Added an app-name-free generic primitive surface:

- `run_generic_ray_triangle_any_hit(...)`
- `run_generic_ray_triangle_any_hit_count(...)`

The slice supports raw ray/triangle `ANY_HIT` rows and aggregate
`COUNT_HITS`. CPU is available as the local oracle. Embree and OptiX are the
active native dispatch targets. Vulkan, HIPRT, and Apple RT are rejected for
this v1.5 generic surface because they remain frozen for new implementation
work before v2.1.

## Boundary

This does not yet replace app wrappers. It is the first narrow generic surface
needed before graph visibility can move from v1.4 metadata wrappers toward
v1.5 generic traversal-plus-reduction execution. Performance evidence still
requires a later NVIDIA pod packet.

## Verification

Focused generic primitive test:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1288_v1_5_generic_anyhit_count_test
```

Result: 5 tests passed.

Combined v1.5/v1.4 regression:

```text
PYTHONPATH=src:. python3 -m unittest \
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

Result: 105 tests passed.
