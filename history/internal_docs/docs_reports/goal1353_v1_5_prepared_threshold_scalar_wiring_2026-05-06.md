# Goal1353 v1.5 Prepared Threshold Scalar Wiring

Date: 2026-05-06

## Scope

Finished scalar-reduction wiring for remaining row/flag-based prepared
`REDUCE_INT(COUNT)` paths in `generic_primitives.py`.

## Implementation

- Added shared scalar-reduction metadata extraction for generic summaries.
- Wired prepared grouped pose flags through
  `run_generic_scalar_reduction(..., summary_primitive="REDUCE_INT(COUNT)")`.
- Wired the rows-only fallback path in
  `GenericPreparedFixedRadiusCountThreshold2D.count_threshold_reached(...)`
  through the same scalar helper.
- Preserved native scalar `count_threshold_reached(...)` when the prepared
  backend exposes it directly; that path intentionally avoids row
  materialization.
- Removed remaining inline threshold-row counting in `generic_primitives.py`
  for row/flag fallback paths.

## Local Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1306_v1_5_robot_pose_flags_generic_migration_test tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test tests.goal1350_v1_5_generic_scalar_reduction_test
```

Result:

```text
Ran 17 tests in 0.002s
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
Ran 69 tests in 0.029s
OK
```

## Boundary

This is v1.5 contract wiring only. It does not claim native scalar-reduction
acceleration, does not authorize public speedup wording, and does not change
the v1.0 release tag.

## Pod Validation

Endpoint:

```text
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Fresh checkout path:

```text
/tmp/rtdl_goal1353/repo
```

Validated commit:

```text
56c6258b7abe8381316bc78892c0427c8d0602ae
```

Environment probe:

```text
python: Python 3.12.3
git: git version 2.43.0
```

Focused pod tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1306_v1_5_robot_pose_flags_generic_migration_test tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test tests.goal1350_v1_5_generic_scalar_reduction_test
```

Result:

```text
Ran 17 tests in 0.003s
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
  tests.goal1306_v1_5_robot_pose_flags_generic_migration_test \
  tests.goal1308_v1_5_polygon_float_sum_contract_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test \
  tests.goal1350_v1_5_generic_scalar_reduction_test
```

Result:

```text
Ran 69 tests in 6.014s
OK
```
