# Goal1351 v1.5 ANY_HIT Count Scalar Wiring

Date: 2026-05-06

## Scope

Wired `run_generic_ray_triangle_any_hit_count(...)` through the v1.5 scalar
reduction helper added in Goal1350. The wrapper still exposes the same
compatibility keys (`hit_count`, `row_count`, optional `rows`) while adding
explicit scalar reduction metadata for the stable `COUNT_HITS` summary
primitive.

## Implementation

- Replaced the wrapper-local inline `sum(any_hit)` with
  `run_generic_scalar_reduction(..., summary_primitive="COUNT_HITS")`.
- Preserved existing wrapper output behavior.
- Added `scalar_reduction` metadata containing the stable primitive name,
  result layout, dtype, input field, and bounded claim boundary.
- Added a focused test proving the any-hit count wrapper delegates to the
  scalar reduction surface.

## Local Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1288_v1_5_generic_anyhit_count_test tests.goal1350_v1_5_generic_scalar_reduction_test
```

Result:

```text
Ran 12 tests in 0.001s
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
  tests.goal1304_v1_5_generic_migration_inventory_test \
  tests.goal1306_v1_5_robot_pose_flags_generic_migration_test \
  tests.goal1308_v1_5_polygon_float_sum_contract_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test \
  tests.goal1350_v1_5_generic_scalar_reduction_test
```

Result:

```text
Ran 61 tests in 0.022s
OK
```

## Boundary

This is local contract wiring only. It does not claim native backend
acceleration for scalar reduction, does not authorize public speedup wording,
and does not change the v1.0 release tag.

## Pod Validation

Endpoint:

```text
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Fresh checkout path:

```text
/tmp/rtdl_goal1351/repo
```

Validated commit:

```text
536f492a473f84cc83f4d8fb41b027d375d0295f
```

Environment probe:

```text
hostname: 4fc0b98845a6
python: Python 3.12.3
git: git version 2.43.0
```

Focused pod tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1288_v1_5_generic_anyhit_count_test tests.goal1350_v1_5_generic_scalar_reduction_test
```

Result:

```text
Ran 12 tests in 0.002s
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
  tests.goal1304_v1_5_generic_migration_inventory_test \
  tests.goal1306_v1_5_robot_pose_flags_generic_migration_test \
  tests.goal1308_v1_5_polygon_float_sum_contract_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test \
  tests.goal1350_v1_5_generic_scalar_reduction_test
```

Result:

```text
Ran 61 tests in 5.845s
OK
```
