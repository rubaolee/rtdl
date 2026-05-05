# Goal1295 v1.5 Generic Prepared Scene Session

Date: 2026-05-05

## Decision

Add an app-name-free prepared scene session for generic ray/triangle `ANY_HIT`
plus `COUNT_HITS`.

The Goal1294 pod evidence showed that OptiX repeated any-hit/count queries are
fast, while scene preparation dominates. The next local v1.5 step is therefore
to expose a reusable scene boundary so callers can amortize scene preparation
across ray batches.

## Implementation

- `prepare_generic_ray_triangle_any_hit_scene(...)` returns a context-managed
  reusable prepared scene.
- `GenericPreparedRayTriangleAnyHitScene.count(...)` runs one ray batch against
  the prepared scene with repeated query timing and `COUNT_HITS` output.
- Existing `run_generic_prepared_ray_triangle_any_hit_count(...)` now delegates
  through the session API, preserving one-shot behavior while sharing the same
  contract.
- Backend scope remains OptiX-focused for prepared generic sessions. Vulkan,
  HIPRT, and Apple RT remain frozen before v2.1.

## Boundary

This is internal v1.5 primitive API work. It does not authorize public speedup
wording, whole-app claims, public release claims, or new Vulkan/HIPRT/Apple RT
implementation before v2.1.

## Verification

Passed:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1295_v1_5_generic_prepared_scene_session_test \
  tests.goal1290_v1_5_generic_prepared_anyhit_count_test \
  tests.goal1291_v1_5_embree_prepared_parity_status_test \
  tests.goal1288_v1_5_generic_anyhit_count_test
```

Result: 18 tests OK.

```bash
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/generic_primitives.py \
  src/rtdsl/__init__.py
```

Result: OK.

Broader v1.5/v1.4 focused regression also passed:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1295_v1_5_generic_prepared_scene_session_test \
  tests.goal1292_v1_5_generic_optix_evidence_packet_test \
  tests.goal1291_v1_5_embree_prepared_parity_status_test \
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

Result: 125 tests OK.
