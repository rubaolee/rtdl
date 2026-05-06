# Goal1363 v1.5 Bounded Collection Claim Boundaries

Date: 2026-05-06

## Scope

Hardened the experimental `COLLECT_K_BOUNDED` metadata boundary for the v1.5
Jaccard diagnostic path.

## Implementation

- Extended `validate_v1_5_collect_k_bounded_contracts()` to require claim
  boundary text for diagnostic-only status, no public Jaccard speedup wording,
  no silent candidate truncation, and no score output after overflow.
- Propagated the bounded-collection `claim_boundary` into runtime collection
  metadata from `collect_k_bounded_candidate_pairs()`.
- Added tests for static contract boundaries and runtime collection metadata.

## Boundary

This is metadata hardening only. It does not promote `COLLECT_K_BOUNDED` to a
stable primitive, add public Jaccard speedup wording, change the fail-closed
overflow behavior, or authorize v1.5 release wording.

## Local Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test tests.goal1320_v1_5_jaccard_generic_score_reduction_test
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
Ran 92 tests in 0.016s
OK
```

## Pod Validation

Endpoint:

```text
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Fresh checkout path:

```text
/tmp/rtdl_goal1363/repo
```

Validated commit:

```text
2599d73200ccb4eb0ce30650c42578c77db5b7f7
```

Environment probe:

```text
python: Python 3.12.3
git: git version 2.43.0
```

Focused pod tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test tests.goal1320_v1_5_jaccard_generic_score_reduction_test
```

Result:

```text
Ran 15 tests in 0.003s
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
Ran 92 tests in 6.027s
OK
```
