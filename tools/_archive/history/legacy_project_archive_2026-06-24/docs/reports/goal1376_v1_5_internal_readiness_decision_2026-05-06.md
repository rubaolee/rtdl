# Goal1376 v1.5 Internal Readiness Decision

## Scope

Add a compact internal readiness decision API that consumes the aggregate v1.5
readiness gate and returns allowed/blocked next actions.

Allowed next actions remain internal:

- continue internal contract hardening
- collect pod validation from Git
- request external review before public claims

Blocked next actions remain explicit:

- public v1.5 release wording
- public speedup wording
- release tag action
- stable `COLLECT_K_BOUNDED` promotion
- new backend implementation before v2.1

## Boundary

This decision is internal/non-public. It does not authorize public v1.5 release
wording, public speedup wording, release tag action, or broad backend work.

## Local Validation

- Focused:
  `PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test`
  - `Ran 9 tests in 0.001s`
  - `OK`
- v1.5 slice:
  `PYTHONPATH=src:. python3 -m unittest tests.goal1282_v1_4_primitive_contract_schema_test tests.goal1287_v1_4_exit_readiness_and_v1_5_blockers_test tests.goal1288_v1_5_generic_anyhit_count_test tests.goal1289_v1_5_graph_visibility_generic_dispatch_test tests.goal1290_v1_5_generic_prepared_anyhit_count_test tests.goal1291_v1_5_embree_prepared_parity_status_test tests.goal1295_v1_5_generic_prepared_scene_session_test tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test tests.goal1304_v1_5_generic_migration_inventory_test tests.goal1305_v1_5_grouped_reduction_contract_test tests.goal1306_v1_5_robot_pose_flags_generic_migration_test tests.goal1307_v1_5_db_compact_summary_generic_migration_test tests.goal1308_v1_5_polygon_float_sum_contract_test tests.goal1309_v1_5_polygon_pair_generic_area_summary_test tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test tests.goal1320_v1_5_jaccard_generic_score_reduction_test tests.goal1350_v1_5_generic_scalar_reduction_test tests.goal1359_v1_5_float_min_max_empty_guard_test tests.goal1367_v1_5_internal_readiness_gate_test`
  - `Ran 102 tests in 0.035s`
  - `OK`

## Pod Validation

- SSH target: `root@213.173.108.215 -p 14800`
- Key: `~/.ssh/id_ed25519_rtdl_codex`
- Source: fresh Git clone from `https://github.com/rubaolee/rtdl.git`
- Commit: `e5bc2080291d79461d3d6dc460e41755218cd946`
- Python: `Python 3.12.3`
- Git: `git version 2.43.0`
- Focused:
  `PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test`
  - `Ran 9 tests in 0.001s`
  - `OK`
- v1.5 slice:
  `PYTHONPATH=src:. python3 -m unittest tests.goal1282_v1_4_primitive_contract_schema_test tests.goal1287_v1_4_exit_readiness_and_v1_5_blockers_test tests.goal1288_v1_5_generic_anyhit_count_test tests.goal1289_v1_5_graph_visibility_generic_dispatch_test tests.goal1290_v1_5_generic_prepared_anyhit_count_test tests.goal1291_v1_5_embree_prepared_parity_status_test tests.goal1295_v1_5_generic_prepared_scene_session_test tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test tests.goal1304_v1_5_generic_migration_inventory_test tests.goal1305_v1_5_grouped_reduction_contract_test tests.goal1306_v1_5_robot_pose_flags_generic_migration_test tests.goal1307_v1_5_db_compact_summary_generic_migration_test tests.goal1308_v1_5_polygon_float_sum_contract_test tests.goal1309_v1_5_polygon_pair_generic_area_summary_test tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test tests.goal1320_v1_5_jaccard_generic_score_reduction_test tests.goal1350_v1_5_generic_scalar_reduction_test tests.goal1359_v1_5_float_min_max_empty_guard_test tests.goal1367_v1_5_internal_readiness_gate_test`
  - `Ran 102 tests in 6.031s`
  - `OK`
