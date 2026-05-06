# Goal1356 v1.5 DB Summary Contract Metadata

Date: 2026-05-06

## Scope

Hardened generic DB compact-summary metadata so each request explicitly maps to
its stable v1.5 summary primitive and result layout.

## Implementation

- Added `V1_5_DB_COMPACT_SUMMARY_RESULT_LAYOUTS`.
- Added per-operation DB summary contracts:
  - `conjunctive_scan_count` -> `COUNT_HITS`,
    `scalar_int64_hit_count`;
  - `grouped_count_summary` -> `REDUCE_INT(COUNT)`,
    `grouped_int64_count_map`;
  - `grouped_sum_summary` -> `REDUCE_INT(SUM)`,
    `grouped_int64_sum_map`.
- Added `summary_contracts` to
  `run_generic_db_compact_summary_batch(...)`.
- Preserved the existing `summary_primitives` compatibility key.
- Exported the DB compact-summary result-layout registry from `rtdsl`.

This is metadata contract hardening only; DB compact-summary execution remains
delegated to the prepared dataset native path.

## Local Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1307_v1_5_db_compact_summary_generic_migration_test
```

Result:

```text
Ran 3 tests in 0.001s
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
  tests.goal1350_v1_5_generic_scalar_reduction_test
```

Result:

```text
Ran 78 tests in 0.039s
OK
```

## Boundary

This does not claim SQL behavior, DBMS behavior, row materialization-free
speedup, native scalar-reduction acceleration, or public v1.5 release wording.
The v1.0 release tag remains unchanged.
