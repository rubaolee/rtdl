# Goal1291 v1.5 Embree Prepared Parity Status

Date: 2026-05-05

Status: local v1.5 parity status artifact. This is not pod evidence and does
not authorize public RTX wording.

## Finding

OptiX now has an app-name-free prepared raw ray/triangle `ANY_HIT` plus
`COUNT_HITS` helper through `run_generic_prepared_ray_triangle_any_hit_count`.

Embree has native direct ray any-hit and hit-count dispatch, but the current
generic prepared surface does not yet expose an equivalent scene/probe split:

- OptiX prepared semantics: build scene once, prepare rays once, repeat count
  queries.
- Embree prepared status: blocked until we implement a scene/probe split or
  explicitly accept a weaker fallback contract.

## Backend Status

| Backend | v1.5 prepared status | Role |
|---|---|---|
| OptiX | implemented | NVIDIA RT target |
| Embree | blocked pending scene/probe split | CPU RT baseline and fallback |
| Vulkan | frozen before v2.1 | compatibility/inactive |
| HIPRT | frozen before v2.1 | compatibility/inactive |
| Apple RT | frozen before v2.1 | compatibility/inactive |

## What Unblocks Embree Parity

Embree parity can be unblocked by one of two reviewed options:

- Preferred: add a generic Embree prepared ray/triangle any-hit count helper
  with build-scene-once and probe-many semantics comparable to OptiX.
- Fallback: define and review a weaker Embree prepared-execution contract that
  reuses packed inputs but does not claim scene/probe parity.

The preferred option is cleaner for v1.5 because it keeps Embree as the
same-contract CPU RT baseline for NVIDIA RT timing.

## Boundary

This status does not change runtime behavior. It documents why v1.5 prepared
parity is not complete and prevents accidental claims that OptiX prepared
count already has a same-contract Embree prepared baseline.

## Verification

Focused status test:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1291_v1_5_embree_prepared_parity_status_test
```

Result: 4 tests passed.

Combined v1.5/v1.4 regression:

```text
PYTHONPATH=src:. python3 -m unittest \
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

Result: 116 tests passed.
