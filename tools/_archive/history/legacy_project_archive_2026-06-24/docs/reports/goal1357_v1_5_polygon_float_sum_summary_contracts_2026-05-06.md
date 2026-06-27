# Goal1357 v1.5 Polygon Float-Sum Summary Contracts

Date: 2026-05-06

## Scope

Made polygon and Jaccard `REDUCE_FLOAT(SUM)` runtime metadata explicit while
preserving the integer-parity boundary.

## Implementation

- Added `V1_5_POLYGON_FLOAT_SUM_RESULT_LAYOUTS`.
- Added per-result `summary_contract` metadata for:
  - polygon-pair exact-area summary;
  - polygon-set Jaccard score reduction.
- Recorded `integer_parity_required: True` and
  `scalar_helper_direct_use: False` in those contracts.
- Preserved existing `summary_primitive`, `result_layout`, `dtype`, and
  integer parity output keys.

These paths intentionally do not call the generic scalar reducer directly:
they first require exact integer oracle parity before exposing float64
`REDUCE_FLOAT(SUM)` metadata.

## Local Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1308_v1_5_polygon_float_sum_contract_test tests.goal1320_v1_5_jaccard_generic_score_reduction_test
```

Result:

```text
Ran 9 tests in 0.001s
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
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test \
  tests.goal1320_v1_5_jaccard_generic_score_reduction_test \
  tests.goal1350_v1_5_generic_scalar_reduction_test
```

Result:

```text
Ran 83 tests in 0.024s
OK
```

## Boundary

This is metadata contract hardening only. It does not claim generic polygon
overlay, fused GPU Jaccard, native scalar-reduction acceleration, public
speedup wording, or v1.5 release authorization. The v1.0 release tag remains
unchanged.

## Pod Validation

Endpoint:

```text
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Fresh checkout path:

```text
/tmp/rtdl_goal1357/repo
```

Validated commit:

```text
a1442c42593a817813c20eb831ce49fe2daa6f1c
```

Environment probe:

```text
python: Python 3.12.3
git: git version 2.43.0
```

Focused pod tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1308_v1_5_polygon_float_sum_contract_test tests.goal1320_v1_5_jaccard_generic_score_reduction_test
```

Result:

```text
Ran 9 tests in 0.001s
OK
```

v1.5 primitive slice on pod:

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
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test \
  tests.goal1320_v1_5_jaccard_generic_score_reduction_test \
  tests.goal1350_v1_5_generic_scalar_reduction_test
```

Result:

```text
Ran 83 tests in 5.982s
OK
```
