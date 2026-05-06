# Goal1366 v1.5 Inventory Remaining-Work Boundary

Date: 2026-05-06

## Scope

Made remaining app-specific work explicit in v1.5 migration inventory
boundaries.

## Implementation

- Updated inventory rows with non-empty `remaining_app_specific_work` so their
  `boundary` text names the remaining app-specific continuations.
- Extended `_validate_v1_5_generic_migration_inventory_rows()` to reject rows
  that hide or omit remaining work from the boundary.
- Added tests for valid boundary text and malformed remaining-work boundaries.

## Boundary

This is inventory metadata hardening only. It does not mark remaining
app-specific continuations as generic, authorize public speedup wording,
authorize public v1.5 release wording, or change the v1.0 release tag.

## Local Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1304_v1_5_generic_migration_inventory_test tests.goal1287_v1_4_exit_readiness_and_v1_5_blockers_test
```

Result:

```text
Ran 11 tests in 0.002s
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
Ran 93 tests in 0.033s
OK
```
