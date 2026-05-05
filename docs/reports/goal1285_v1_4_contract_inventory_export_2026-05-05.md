# Goal1285 v1.4 Contract Inventory Export

Date: 2026-05-05

Status: local v1.4 operator/CI utility. This is not a pod evidence packet and
does not authorize public RTX wording.

## Change

Added `scripts/goal1285_v1_4_contract_inventory_export.py`, a lightweight JSON
exporter for the v1.4 primitive contract inventory. It validates the inventory
first, then prints or writes a JSON artifact with:

- active v1.4 backend set: Embree plus OptiX;
- frozen-before-v2.1 backend set: Vulkan, HIPRT, Apple RT;
- total, active, and frozen contract counts;
- the full contract records for the four current supported v1.4 app rows.

## Boundary

The exporter runs locally and does not execute app workloads, native backends,
or pod benchmarks. It is intended for operator visibility and CI checks only.
It preserves `public_wording_authorized=false`.

## Artifact

Generated inventory snapshot:

```text
docs/reports/goal1285_v1_4_contract_inventory_export_2026-05-05.json
```

## Verification

Focused exporter test:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1285_v1_4_contract_inventory_export_test
```

Result: 2 tests passed.

Broader v1.4 regression:

```text
PYTHONPATH=src:. python3 -m unittest \
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

Result: 91 tests passed.
