# Goal 420 Report: v0.7 RT DB Conjunctive Scan Native Oracle Truth Path

Date: 2026-04-15
Goal:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_420_v0_7_rt_db_conjunctive_scan_native_oracle_truth_path.md`

## Summary

The bounded `conjunctive_scan` DB kernel now has a real native/oracle path.

Implemented shape:

- native oracle ABI for bounded denormalized table scans
- Python wrapper that encodes:
  - schema fields
  - scalar row values
  - bounded predicate clauses
- `run_cpu(...)` now calls the native oracle library for
  `conjunctive_scan`

## Boundary

This native slice is still bounded:

- it only closes `conjunctive_scan`
- it does not yet close grouped native/oracle kernels
- it is a small scalar-table ABI, not a full DB row engine

## Verification

Focused test:

- `python3 -m unittest tests.goal420_v0_7_rt_db_conjunctive_scan_native_oracle_truth_path_test`

Local result:

- `Ran 3 tests`
- `OK (skipped=1)`

Local evidence now includes:

- native `run_cpu(...)` parity with Python truth path
- native `run_cpu(...)` still works when the Python truth helper is patched to
  fail

Authoritative Linux result on `lestat-lx1` with
`RTDL_POSTGRESQL_DSN="dbname=postgres"`:

- `python3 -B -m unittest tests.goal420_v0_7_rt_db_conjunctive_scan_native_oracle_truth_path_test tests.goal423_v0_7_postgresql_db_correctness_test -v`
  - `Ran 6 tests`
  - `OK`

This proves:

- native oracle `run_cpu(...)` parity with Python truth path
- native oracle `run_cpu(...)` parity with live PostgreSQL on Linux
- Goal 423 PostgreSQL correctness remains green after the native-oracle change
