# Goal1365 v1.5 Inventory Public Boundary Guard

Date: 2026-05-06

## Scope

Hardened the v1.5 migration inventory so every row carries an explicit public
wording/speedup boundary.

## Implementation

- Updated shorter v1.5 inventory boundaries to include `no public speedup
  wording`.
- Extended `_validate_v1_5_generic_migration_inventory_rows()` to reject rows
  whose boundary text does not block public wording.
- Added regression tests for both valid inventory rows and malformed boundary
  text.

## Boundary

This is inventory metadata hardening only. It does not authorize public v1.5
release wording, public speedup wording, release packages, tags, or backend
implementation outside Embree and OptiX.

## Local Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1304_v1_5_generic_migration_inventory_test tests.goal1359_v1_5_float_min_max_empty_guard_test tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test
```

Result:

```text
Ran 13 tests in 0.001s
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
Ran 93 tests in 0.042s
OK
```
