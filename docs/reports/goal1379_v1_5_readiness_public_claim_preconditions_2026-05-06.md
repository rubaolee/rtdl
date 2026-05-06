# Goal1379: v1.5 Readiness Public Claim Preconditions

Date: 2026-05-06

Source commit before change: `0833870ae6c3deff2ea72894fed114eb0bf263e7`

## Scope

This goal hardens the internal v1.5 readiness decision so it records the exact
preconditions required before any public v1.5 claim can be considered.

The internal readiness decision remains non-public. It does not authorize:

- public v1.5 release wording
- public speedup wording
- release tag actions
- stable `COLLECT_K_BOUNDED` promotion
- new Vulkan, HIPRT, or Apple RT implementation work before v2.1

## Added Guard

`V1_5_INTERNAL_READINESS_PUBLIC_CLAIM_PRECONDITIONS` is now an exported exact
tuple:

- `exact_subpath_evidence`
- `fresh_git_pod_validation`
- `external_3_ai_consensus`
- `public_wording_review`

`v1_5_internal_readiness_decision()` now exposes:

- `public_claim_preconditions`
- `public_claims_ready: False`

`validate_v1_5_internal_readiness_decision()` requires exact precondition
equality and rejects any decision that marks public claims ready.

## Local Validation

Focused readiness gate:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test
Ran 9 tests in 0.002s
OK
```

v1.5 slice:

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
  tests.goal1359_v1_5_float_min_max_empty_guard_test \
  tests.goal1367_v1_5_internal_readiness_gate_test
Ran 102 tests in 0.032s
OK
```
