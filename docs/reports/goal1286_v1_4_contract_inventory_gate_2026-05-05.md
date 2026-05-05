# Goal1286 v1.4 Contract Inventory Gate

Date: 2026-05-05

Status: local v1.4 CI/operator gate. This is not a pod evidence packet and
does not authorize public RTX wording.

## Change

Added `scripts/goal1286_v1_4_contract_inventory_gate.py`, a JSON gate for the
Goal1285 v1.4 contract inventory snapshot. The gate fails if:

- active v1.4 backends drift away from Embree plus OptiX;
- Vulkan, HIPRT, or Apple RT are promoted before v2.1;
- contract counts drift from the expected v1.4 surface;
- Jaccard stops being diagnostic;
- public RTX wording is accidentally marked authorized.

## Boundary

This gate validates a local inventory artifact only. It does not execute app
workloads, does not collect pod evidence, does not promote frozen backends, and
does not authorize public speedup wording.

## Verification

Gate artifact:

```text
docs/reports/goal1286_v1_4_contract_inventory_gate_2026-05-05.json
```

Gate result: `valid=true`, `failure_count=0`, `checked_contract_count=20`.

Focused gate test:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1286_v1_4_contract_inventory_gate_test
```

Result: 4 tests passed.

Artifact gate command:

```text
PYTHONPATH=src:. python3 scripts/goal1286_v1_4_contract_inventory_gate.py \
  docs/reports/goal1285_v1_4_contract_inventory_export_2026-05-05.json \
  --output-json docs/reports/goal1286_v1_4_contract_inventory_gate_2026-05-05.json
```

Result: exit code 0.

Broader v1.4 regression:

```text
PYTHONPATH=src:. python3 -m unittest \
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

Result: 95 tests passed.
