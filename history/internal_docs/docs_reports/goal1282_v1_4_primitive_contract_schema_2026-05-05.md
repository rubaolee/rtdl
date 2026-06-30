# Goal1282 v1.4 Primitive Contract Schema Normalization

Date: 2026-05-05

Status: local v1.4 schema checkpoint. This is not a pod evidence packet and
does not authorize public RTX wording.

## Change

Added `src/rtdsl/primitive_contract_schema.py`, a small validator for the
`primitive_contract` dictionaries attached in v1.4. The schema enforces:

- required common fields;
- active backend scope fixed to Embree plus OptiX;
- Embree role as `cpu_rt_baseline_and_fallback`;
- OptiX role as `nvidia_rt_target`;
- inactive backends as `compatibility_or_inactive`;
- valid migration statuses;
- non-empty phase-counter and claim-boundary payloads;
- Jaccard remains `optix_still_slower_with_reason` and
  `public_wording_allowed=false`.

Runtime app behavior is unchanged. The validator is currently used by tests to
lock the contract shape before further wrapper refactoring.

## Verification

Focused local verification should include:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1282_v1_4_primitive_contract_schema_test \
  tests.goal1281_v1_4_wrapper_consolidation_status_test \
  tests.goal1280_v1_4_polygon_jaccard_diagnostic_contract_test \
  tests.goal1279_v1_4_polygon_pair_primitive_contract_test \
  tests.goal1278_v1_4_sales_risk_primitive_contract_test \
  tests.goal1276_v1_4_graph_visibility_wrapper_metadata_test
```

Result: 24 tests passed.

Broader v1.4 regression:

```text
PYTHONPATH=src:. python3 -m unittest \
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

Result: 81 tests passed.
