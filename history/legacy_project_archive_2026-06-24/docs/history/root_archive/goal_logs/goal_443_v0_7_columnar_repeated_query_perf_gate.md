# Goal 443: v0.7 Columnar Repeated-Query Performance Gate

## Goal

Refresh the cross-backend repeated-query DB performance gate after Embree,
OptiX, and Vulkan all gained native columnar prepared DB dataset transfer.

## Required Outcome

- Keep Goal 437 as historical row-transfer evidence.
- Add a new Linux performance artifact that measures:
  - Embree with `transfer="columnar"`
  - OptiX with `transfer="columnar"`
  - Vulkan with `transfer="columnar"`
  - PostgreSQL setup/query on Linux
- Use the bounded DB workload family:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- Report prepare/setup once, median query, total repeated time, and correctness
  hash equality.
- Preserve the claim boundary:
  - RTDL is not PostgreSQL
  - RTDL is not a DBMS
  - this is a bounded in-memory workload-kernel comparison

## Review Requirement

This goal requires at least 2-AI consensus before closure.
