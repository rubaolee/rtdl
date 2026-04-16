# Goal 429 Report: v0.7 RT DB Cross-Engine PostgreSQL Correctness Gate

Date: 2026-04-15
Goal:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_429_v0_7_rt_db_cross_engine_postgresql_correctness_gate.md`

## Scope

Close correctness for the first bounded `v0.7` DB kernel family across all
implemented engines against PostgreSQL on Linux.

Target workloads:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

Target engines:

- `cpu_python_reference`
- `cpu`
- `embree`
- `optix`
- `vulkan`
- `postgresql`

## What was implemented

Added a single cross-engine PostgreSQL gate test:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal429_v0_7_rt_db_cross_engine_postgresql_correctness_gate_test.py`

The gate constructs bounded denormalized DB cases and checks row-exact parity
across:

- Python truth
- native/oracle CPU
- Embree
- OptiX
- Vulkan
- PostgreSQL query execution over prepared temporary tables

## Linux authoritative result

Fresh synced checkout:

- `/home/lestat/tmp/rtdl_v0_7_db_vulkan_check`

Host/backend bring-up confirmed in that checkout:

- Embree available
- OptiX rebuilt and available
- Vulkan rebuilt and available
- PostgreSQL available through `dbname=postgres`

Cross-engine correctness gate on `lestat-lx1`:

- `RTDL_POSTGRESQL_DSN="dbname=postgres" python3 -m unittest tests.goal429_v0_7_rt_db_cross_engine_postgresql_correctness_gate_test -v`
- result:
  - `Ran 3 tests`
  - `OK`

## What the gate proves

For the bounded first-wave DB family, the following all agree exactly on Linux:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

Agreement is now established across:

- semantic truth path
- native/oracle CPU path
- all three RT backends
- PostgreSQL baseline

The gate keeps the claim bounded:

- one group key only
- integer-compatible `grouped_sum`
- Goal 416 runtime ceilings still apply
- PostgreSQL remains an external correctness anchor, not an RTDL execution
  backend

## Reading

This goal closes the main correctness question for the first `v0.7` DB family:

- the language/kernel semantics are stable
- the Python and native/oracle paths agree
- Embree, OptiX, and Vulkan all agree with those paths
- PostgreSQL agrees with all of them on the bounded gate cases

So after Goal 429, correctness for the first bounded DB family is no longer a
per-backend claim. It is a cross-engine, PostgreSQL-anchored claim.

## Conclusion

Goal 429 is technically implemented and verified.

The first bounded `v0.7` DB kernel family is now row-exact across:

- Python truth
- native/oracle CPU
- Embree
- OptiX
- Vulkan
- PostgreSQL on Linux

The next goal is Goal 430:

- bounded cross-engine performance comparison against PostgreSQL on Linux
