# Goal 1392 - v1.5 Readiness Decision Validator Refactor

Date: 2026-05-06

## Scope

Refactored the internal v1.5 readiness decision validator into focused private helper checks.

This is a no-contract-change hardening step:

- The public decision payload remains unchanged.
- The exported constants remain unchanged.
- The readiness decision fingerprint contract remains unchanged.
- Public v1.5 release wording, public speedup wording, release tag actions, and claim-grade evidence remain blocked.

## Local Validation

Command:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test
```

Result:

```text
Ran 9 tests in 0.001s

OK
```

Command:

```sh
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
```

Result:

```text
Ran 102 tests in 0.035s

OK
```

## Fresh Git Pod Validation

Pod command:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
  root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex \
  'git clone --depth 1 https://github.com/rubaolee/rtdl.git /tmp/rtdl_goal1392/repo && ...'
```

Environment:

```text
commit: 700967f9741d5903d4f916e78ed2cfe310654154
python: Python 3.12.3
git: git version 2.43.0
```

Results:

```text
tests.goal1367_v1_5_internal_readiness_gate_test
Ran 9 tests in 0.002s

OK

v1.5 readiness slice
Ran 102 tests in 5.882s

OK
```
