# Goal1354 Claude Review Follow-up Contract Locks

Date: 2026-05-06

## Scope

Captured Claude's external review of the v1.5 scalar-reduction wiring and
locked the highest-priority contract ambiguity it identified.

Claude review file:

```text
docs/reports/goal1354_claude_scalar_reduction_review_2026-05-06.md
```

Claude verdict:

```text
ACCEPT
```

## Follow-up Decision

`GenericPreparedFixedRadiusCountThreshold2D.count_threshold_reached(...)` has
two intentionally different cases:

- native scalar fast path: backend exposes `count_threshold_reached(...)`, no
  row materialization, no `scalar_reduction` metadata sub-dict;
- rows-only fallback: backend materializes threshold rows, then RTDL derives
  `threshold_reached_count` via `run_generic_scalar_reduction(...)` and emits
  `scalar_reduction` metadata.

The contract is now locked by tests rather than implicit behavior.

## Additional Test Locks

Also added two low-cost assertions from Claude's actionable-gap list:

- direct fixed-radius row summaries distinguish outer `row_count` from scalar
  threshold count;
- `scalar_reduction` metadata intentionally strips the reduced `result` value.

## Local Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test tests.goal1350_v1_5_generic_scalar_reduction_test
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
  tests.goal1306_v1_5_robot_pose_flags_generic_migration_test \
  tests.goal1308_v1_5_polygon_float_sum_contract_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test \
  tests.goal1350_v1_5_generic_scalar_reduction_test
```

Result:

```text
Ran 69 tests in 0.024s
OK
```
