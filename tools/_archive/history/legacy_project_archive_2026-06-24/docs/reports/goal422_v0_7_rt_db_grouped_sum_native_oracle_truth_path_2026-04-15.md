# Goal 422 Report: v0.7 RT DB Grouped Sum Native Oracle Truth Path

Date: 2026-04-15
Goal:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_422_v0_7_rt_db_grouped_sum_native_oracle_truth_path.md`

## Summary

The bounded single-group-key `grouped_sum` DB kernel now has a real
native/oracle path.

## Boundary

- this native grouped slice supports exactly one group key
- multi-group-key grouped queries still fall back to the Python helper
- string group keys are encoded to stable integer codes before the native call
  and decoded afterward

## Verification

Focused test:

- `python3 -m unittest tests.goal422_v0_7_rt_db_grouped_sum_native_oracle_truth_path_test`

Local result:

- `Ran 3 tests`
- `OK (skipped=1)`

Local evidence now includes:

- native `run_cpu(...)` parity with Python truth path
- native `run_cpu(...)` still works when the Python grouped-sum helper is
  patched to fail

Authoritative Linux result on `lestat-lx1` with
`RTDL_POSTGRESQL_DSN="dbname=postgres"`:

- `python3 -B -m unittest tests.goal420_v0_7_rt_db_conjunctive_scan_native_oracle_truth_path_test tests.goal421_v0_7_rt_db_grouped_count_native_oracle_truth_path_test tests.goal422_v0_7_rt_db_grouped_sum_native_oracle_truth_path_test tests.goal423_v0_7_postgresql_db_correctness_test tests.goal424_v0_7_postgresql_db_grouped_correctness_test -v`
  - `Ran 17 tests`
  - `OK`

This proves:

- native oracle `run_cpu(...)` parity with Python truth path
- native oracle `run_cpu(...)` parity with live PostgreSQL on Linux for
  bounded single-key `grouped_sum`
