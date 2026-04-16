# Goal 428: v0.7 RT DB Vulkan Backend Closure

## Goal

Implement the bounded `v0.7` database-style workload family on Vulkan.

## Required outcome

- Vulkan supports:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- correctness is shown against:
  - Python truth path
  - native/oracle CPU
  - PostgreSQL where applicable

## Review requirement

This goal requires at least 2-AI consensus before closure.
