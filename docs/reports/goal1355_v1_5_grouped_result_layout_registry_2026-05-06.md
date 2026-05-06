# Goal1355 v1.5 Grouped Result Layout Registry

Date: 2026-05-06

## Scope

Addressed Claude's second actionable scalar-reduction follow-up: the
`grouped_threshold_bool` result layout was previously a loose string literal.

## Implementation

- Added `V1_5_GROUPED_THRESHOLD_BOOL_RESULT_LAYOUT`.
- Added `V1_5_GROUPED_REDUCTION_RESULT_LAYOUTS`.
- Validated every grouped reduction contract against the registered result
  layouts.
- Reused the grouped threshold layout constant in the prepared pose-flag
  runtime path.
- Exported the result-layout constants from `rtdsl`.

This does not create a new primitive. Grouped boolean output remains
`REDUCE_INT(COUNT)` with a grouped threshold-bool result layout.

## Local Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1305_v1_5_grouped_reduction_contract_test tests.goal1306_v1_5_robot_pose_flags_generic_migration_test
```

Result:

```text
Ran 10 tests in 0.002s
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
  tests.goal1308_v1_5_polygon_float_sum_contract_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test \
  tests.goal1350_v1_5_generic_scalar_reduction_test
```

Result:

```text
Ran 75 tests in 0.056s
OK
```

## Boundary

This is metadata contract hardening only. It does not authorize public v1.5
release wording, does not claim native scalar-reduction acceleration, and does
not change the v1.0 release tag.

## Pod Validation

Endpoint:

```text
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Fresh checkout path:

```text
/tmp/rtdl_goal1355/repo
```

Validated commit:

```text
49541d7b61615437a87ba948e05b1495d009510c
```

Environment probe:

```text
python: Python 3.12.3
git: git version 2.43.0
```

Focused pod tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1305_v1_5_grouped_reduction_contract_test tests.goal1306_v1_5_robot_pose_flags_generic_migration_test
```

Result:

```text
Ran 10 tests in 0.002s
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
  tests.goal1308_v1_5_polygon_float_sum_contract_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test \
  tests.goal1350_v1_5_generic_scalar_reduction_test
```

Result:

```text
Ran 75 tests in 5.915s
OK
```
