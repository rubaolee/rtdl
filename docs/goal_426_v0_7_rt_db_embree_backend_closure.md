# Goal 426: v0.7 RT DB Embree Backend Closure

## Goal

Implement the first RT backend for the bounded `v0.7` database-style workload
family on Embree.

## Required outcome

- Embree supports:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- correctness is shown against:
  - Python truth path
  - native/oracle CPU
  - PostgreSQL where applicable

## Review requirement

This goal requires at least 2-AI consensus before closure.

## Boundary

- keep the same bounded workload family
- do not expand to SQL or DBMS claims
- reuse the current RTDL kernel surface rather than inventing new syntax
