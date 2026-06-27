# Goal1283 v1.4 Runtime Contract Validation

Date: 2026-05-05

Status: local v1.4 schema hardening checkpoint. This is not a pod evidence
packet and does not authorize public RTX wording.

## Change

The v1.4 `primitive_contract` attach helpers now validate contracts before
attaching them to app payloads:

- graph visibility;
- sales-risk DB;
- polygon-pair;
- polygon-set Jaccard diagnostic.

The imports are local inside attach helpers to avoid circular module imports.
Runtime outputs are unchanged when contracts are valid; invalid contract shapes
now fail early instead of silently entering app JSON.

## Boundary

This is schema hardening only. It does not change backend execution, does not
request pod evidence, does not touch Vulkan/HIPRT/Apple RT implementation, and
does not change public wording status.

## Verification

Focused local verification:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1283_v1_4_runtime_contract_validation_test \
  tests.goal1282_v1_4_primitive_contract_schema_test \
  tests.goal1281_v1_4_wrapper_consolidation_status_test \
  tests.goal1280_v1_4_polygon_jaccard_diagnostic_contract_test \
  tests.goal1279_v1_4_polygon_pair_primitive_contract_test \
  tests.goal1278_v1_4_sales_risk_primitive_contract_test \
  tests.goal1276_v1_4_graph_visibility_wrapper_metadata_test
```

Result: 28 tests passed.

Broader v1.4 regression:

```text
PYTHONPATH=src:. python3 -m unittest \
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

Result: 85 tests passed.
