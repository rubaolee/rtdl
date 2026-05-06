# Goal1359 v1.5 Float Min/Max Empty-Input Guard

Date: 2026-05-06

## Scope

Locked the current v1.5 boundary for `REDUCE_FLOAT(MIN)` and
`REDUCE_FLOAT(MAX)` before any primitive API wires them into an app migration
path.

## Implementation

- Added a migration guard confirming current v1.5 inventory rows do not use
  `REDUCE_FLOAT(MIN)` or `REDUCE_FLOAT(MAX)`.
- Added explicit negative-path coverage that empty input for
  `REDUCE_FLOAT(MIN)` and `REDUCE_FLOAT(MAX)` raises `ValueError` with a
  no-identity message.
- Kept `REDUCE_FLOAT(SUM)` empty input as the only current float reduction
  identity, returning `0.0`.

## Boundary

This is contract hardening only. It does not add a float-min/max traversal
primitive, native backend acceleration, public speedup wording, or v1.5 release
authorization. A future primitive using `REDUCE_FLOAT(MIN)` or
`REDUCE_FLOAT(MAX)` must add integration-level coverage for empty traversal
outputs before it is marked migrated.

## Local Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1359_v1_5_float_min_max_empty_guard_test tests.goal1350_v1_5_generic_scalar_reduction_test tests.goal1304_v1_5_generic_migration_inventory_test
```

Result:

```text
Ran 15 tests in 0.001s
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
  tests.goal1350_v1_5_generic_scalar_reduction_test \
  tests.goal1359_v1_5_float_min_max_empty_guard_test
```

Result:

```text
Ran 90 tests in 0.038s
OK
```

## Pod Validation

Endpoint:

```text
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Fresh checkout path:

```text
/tmp/rtdl_goal1359/repo
```

Validated commit:

```text
5b9f27d946addc25908bcf200eb28681a82191d6
```

Environment probe:

```text
python: Python 3.12.3
git: git version 2.43.0
```

Focused pod tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1359_v1_5_float_min_max_empty_guard_test tests.goal1350_v1_5_generic_scalar_reduction_test tests.goal1304_v1_5_generic_migration_inventory_test
```

Result:

```text
Ran 15 tests in 0.002s
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
  tests.goal1309_v1_5_polygon_pair_generic_area_summary_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test \
  tests.goal1320_v1_5_jaccard_generic_score_reduction_test \
  tests.goal1350_v1_5_generic_scalar_reduction_test \
  tests.goal1359_v1_5_float_min_max_empty_guard_test
```

Result:

```text
Ran 90 tests in 6.015s
OK
```
