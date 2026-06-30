# Goal1284 v1.4 Primitive Contract Inventory

Date: 2026-05-05

Status: local v1.4 inventory gate. This is not a pod evidence packet and does
not authorize public RTX wording.

## Change

RTDL now exposes a v1.4 primitive contract inventory helper:

- `v1_4_primitive_contract_inventory()`
- `validate_v1_4_primitive_contract_inventory()`

The inventory covers the four current supported v1.4 app rows:

- `graph_analytics.visibility_edges`
- `database_analytics.sales_risk`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

For each row, the active v1.4 backend scope is Embree plus OptiX only. The
inventory also includes frozen-before-v2.1 backend probes for Vulkan, HIPRT,
and Apple RT and asserts they remain inactive compatibility entries.

## Boundary

This is a registry and validation gate only. It does not change execution,
does not add new backend work, does not request pod evidence, and does not
change public wording. Jaccard remains diagnostic with
`public_wording_allowed=false`.

## Verification

Focused inventory gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1284_v1_4_primitive_contract_inventory_test
```

Result: 4 tests passed.

Focused v1.4 contract set:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1284_v1_4_primitive_contract_inventory_test \
  tests.goal1283_v1_4_runtime_contract_validation_test \
  tests.goal1282_v1_4_primitive_contract_schema_test \
  tests.goal1281_v1_4_wrapper_consolidation_status_test \
  tests.goal1280_v1_4_polygon_jaccard_diagnostic_contract_test \
  tests.goal1279_v1_4_polygon_pair_primitive_contract_test \
  tests.goal1278_v1_4_sales_risk_primitive_contract_test \
  tests.goal1276_v1_4_graph_visibility_wrapper_metadata_test
```

Result: 32 tests passed.

Broader v1.4 regression:

```text
PYTHONPATH=src:. python3 -m unittest \
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

Result: 89 tests passed.
