# Goal 445: v0.7 High-Level Prepared DB Columnar Default

## Goal

Make the high-level prepared kernel API use columnar prepared DB dataset transfer
for DB workloads.

## Required Outcome

- `prepare_embree(kernel).bind(...)` uses columnar DB dataset transfer for the
  bounded DB workload family.
- `prepare_optix(kernel).bind(...)` uses columnar DB dataset transfer for the
  bounded DB workload family.
- `prepare_vulkan(kernel).bind(...)` uses columnar DB dataset transfer for the
  bounded DB workload family.
- Direct prepared dataset APIs keep backward-compatible row-transfer defaults:
  - `prepare_embree_db_dataset(..., transfer="row")`
  - `prepare_optix_db_dataset(..., transfer="row")`
  - `prepare_vulkan_db_dataset(..., transfer="row")`
- Prove correctness for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`

## Review Requirement

This goal requires at least 2-AI consensus before closure.
