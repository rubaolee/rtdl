# Goal 423 Report: v0.7 PostgreSQL DB Correctness For Conjunctive Scan

Date: 2026-04-15
Goal target from sequence:
- PostgreSQL-backed correctness gate for the bounded RT database workload family

This first slice closes the PostgreSQL-backed correctness gate for
`conjunctive_scan`.

## Summary

PostgreSQL is now the real external correctness anchor for the first `v0.7`
database kernel on the Linux validation host.

Implemented baseline surface:

- `build_postgresql_conjunctive_scan_sql(...)`
- `prepare_postgresql_denorm_table(...)`
- `query_postgresql_conjunctive_scan(...)`
- `run_postgresql_conjunctive_scan(...)`

The baseline uses:

- a temp denormalized table
- field indexes for bounded predicate columns
- ordered result rows on `row_id`

## Verification

Local fake-connection correctness band:

- `python3 -m unittest tests.goal423_v0_7_postgresql_db_correctness_test`
  - `Ran 3 tests`
  - `OK (skipped=1)`

Linux live PostgreSQL result on `lestat-lx1` with
`RTDL_POSTGRESQL_DSN="dbname=postgres"`:

- `python3 -B -m unittest tests.goal423_v0_7_postgresql_db_correctness_test`
  - `Ran 3 tests`
  - `OK`

Live parity proved against:

- PostgreSQL
- `run_cpu_python_reference(...)`
- `run_cpu(...)`

## Boundary

This slice closes PostgreSQL-backed correctness for `conjunctive_scan`. It does
not yet cover grouped kernels by itself.
