# Goal 424 Report: v0.7 PostgreSQL DB Correctness For Grouped Count And Grouped Sum

Date: 2026-04-15
Goal target from sequence:
- PostgreSQL-backed correctness gate for the bounded RT database workload family

This second slice extends the PostgreSQL-backed correctness gate to:

- `grouped_count`
- `grouped_sum`

## Summary

The first `v0.7` grouped database kernels now share the same external
correctness anchor as `conjunctive_scan`.

Implemented baseline surface:

- `build_postgresql_grouped_count_sql(...)`
- `query_postgresql_grouped_count(...)`
- `run_postgresql_grouped_count(...)`
- `build_postgresql_grouped_sum_sql(...)`
- `query_postgresql_grouped_sum(...)`
- `run_postgresql_grouped_sum(...)`

The grouped PostgreSQL path uses:

- the same bounded temp denormalized-table load
- grouped SQL aggregation with ordered grouped rows
- parity checks against both Python truth and `run_cpu(...)`

## Verification

Local grouped PostgreSQL band:

- `python3 -m unittest tests.goal424_v0_7_postgresql_db_grouped_correctness_test`
  - `Ran 5 tests`
  - `OK (skipped=1)`

Linux live PostgreSQL grouped band on `lestat-lx1` with
`RTDL_POSTGRESQL_DSN="dbname=postgres"`:

- `python3 -B -m unittest tests.goal424_v0_7_postgresql_db_grouped_correctness_test`
  - `Ran 5 tests`
  - `OK`

Authoritative full Linux bounded DB band:

- `python3 -B -m unittest tests.goal417_v0_7_rt_db_conjunctive_scan_truth_path_test tests.goal418_v0_7_rt_db_grouped_count_truth_path_test tests.goal419_v0_7_rt_db_grouped_sum_truth_path_test tests.goal423_v0_7_postgresql_db_correctness_test tests.goal424_v0_7_postgresql_db_grouped_correctness_test`
  - `Ran 19 tests`
  - `OK`

Live parity proved for grouped kernels against:

- PostgreSQL
- `run_cpu_python_reference(...)`
- `run_cpu(...)`

## Boundary

This gives the first `v0.7` kernel family a real PostgreSQL-backed correctness
gate. It still does not claim backend execution on Embree, OptiX, or Vulkan.
