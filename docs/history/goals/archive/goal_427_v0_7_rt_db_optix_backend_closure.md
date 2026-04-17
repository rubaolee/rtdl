# Goal 427: v0.7 RT DB OptiX Backend Closure

## Goal

Implement the bounded `v0.7` database-style workload family on OptiX.

## Required outcome

- OptiX supports:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- correctness is shown against:
  - Python truth path
  - native/oracle CPU
  - PostgreSQL where applicable

## Review requirement

This goal requires at least 2-AI consensus before closure.
