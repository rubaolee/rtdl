# Goal1350 v1.5 Generic Scalar Reduction

Date: 2026-05-06

## Scope

Added an app-name-free v1.5 scalar reduction helper for the stable summary
primitive names:

- `COUNT_HITS`
- `REDUCE_FLOAT(MIN)`
- `REDUCE_FLOAT(MAX)`
- `REDUCE_FLOAT(SUM)`
- `REDUCE_INT(COUNT)`
- `REDUCE_INT(SUM)`

This is a backend-neutral Python contract helper over already-emitted rows. It
does not change `rt.reduce_rows(...)`, does not claim native backend
acceleration, and does not authorize public speedup wording.

## Implementation

- Added `rt.run_generic_scalar_reduction(...)`.
- Added exported primitive declaration
  `rt.V1_5_GENERIC_SCALAR_REDUCTION_PRIMITIVES`.
- Enforced strict primitive-name validation so pseudo-primitives such as
  grouped boolean flags are rejected.
- Defined explicit scalar result layouts and dtype metadata.
- Kept empty-input identities bounded:
  - counts return `0`;
  - sums return `0` or `0.0`;
  - float min/max fail closed because they have no implicit identity.
- Rejected mismatched primitive shapes, including value fields on count
  primitives and non-integer payloads for `REDUCE_INT(SUM)`.

## Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1350_v1_5_generic_scalar_reduction_test tests.goal644_reduce_rows_standard_library_test
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
Ran 60 tests in 0.031s
OK
```

## Boundary

This closes a local v1.5 contract gap only. Native Embree/OptiX scalar
reduction validation remains separate evidence work and should be run on a pod
only when collecting backend evidence.
