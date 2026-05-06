# Goal1358 v1.5 Float-Sum Layout Registry Alignment

Date: 2026-05-06

## Scope

Aligned static polygon float-sum contracts with runtime polygon/Jaccard
`summary_contract` metadata.

## Implementation

- Moved `V1_5_POLYGON_FLOAT_SUM_RESULT_LAYOUTS` into
  `float_reduction_contracts.py`, where static `REDUCE_FLOAT(SUM)` contracts
  are defined.
- Updated `validate_v1_5_float_sum_reduction_contracts()` to reject unknown
  polygon float-sum result layouts.
- Reused the same exported registry in runtime polygon summary metadata.
- Added tests confirming static contracts and runtime polygon-pair summaries
  use registered layouts and preserve the integer-parity boundary.

## Local Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1308_v1_5_polygon_float_sum_contract_test tests.goal1309_v1_5_polygon_pair_generic_area_summary_test tests.goal1320_v1_5_jaccard_generic_score_reduction_test
```

Result:

```text
Ran 13 tests in 0.002s
OK
```

v1.5 primitive slice:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1282_v1_4_primitive_contract_schema_test \
  tests.goal1287_v1_4_exit_readiness_and_v1_5_blockers_test \
  tests.goal1288_v1_5_generic_anyhit_count_test \
  tests.goal1289_v1_5_graph_visibility_generic_dispatch_test \
  tests.goal1290_v1_5_generic_prepared_anyhit_count_test \
  tests.goal1291_v1_5_embree_prepared_parity_status_test \
  tests.goal1295_v1_5_generic_prepared_scene_session_test \
  tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test \
  tests.goal1304_v1_5_generic_migration_inventory_test \
  tests.goal1305_v1_5_grouped_reduction_contract_test \
  tests.goal1306_v1_5_robot_pose_flags_generic_migration_test \
  tests.goal1307_v1_5_db_compact_summary_generic_migration_test \
  tests.goal1308_v1_5_polygon_float_sum_contract_test \
  tests.goal1309_v1_5_polygon_pair_generic_area_summary_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test \
  tests.goal1320_v1_5_jaccard_generic_score_reduction_test \
  tests.goal1350_v1_5_generic_scalar_reduction_test
```

Result:

```text
Ran 87 tests in 0.031s
OK
```

## Boundary

This is metadata contract hardening only. It does not claim generic polygon
overlay, fused GPU Jaccard, native scalar-reduction acceleration, public
speedup wording, or v1.5 release authorization. The v1.0 release tag remains
unchanged.
