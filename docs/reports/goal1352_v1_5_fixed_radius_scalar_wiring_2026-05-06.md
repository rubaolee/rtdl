# Goal1352 v1.5 Fixed-Radius Scalar Wiring

Date: 2026-05-06

## Scope

Wired row-returning fixed-radius threshold-count paths through the v1.5 scalar
reduction helper for `REDUCE_INT(COUNT)`.

## Implementation

- Added an internal threshold-row scalar reduction helper that filters
  `threshold_reached` rows and calls
  `run_generic_scalar_reduction(..., summary_primitive="REDUCE_INT(COUNT)")`.
- Updated direct `run_generic_fixed_radius_count_threshold_2d(...)` to derive
  `threshold_reached_count` from the scalar helper.
- Updated prepared row-returning
  `GenericPreparedFixedRadiusCountThreshold2D.run(...)` to use the same scalar
  helper.
- Preserved existing compatibility keys and row outputs.
- Added scalar reduction metadata to row-returning fixed-radius summaries.

Native scalar `count_threshold_reached(...)` remains a native scalar count path
when available because it intentionally avoids row materialization.

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
Ran 68 tests in 0.310s
OK
```

## Boundary

This is v1.5 contract wiring only. It does not claim native scalar-reduction
acceleration, does not authorize public speedup wording, and does not change
the v1.0 release tag.
