# Goal 450: v0.7 Linux Correctness And Performance Refresh

Date: 2026-04-16

## Purpose

Refresh the Linux correctness and performance evidence for the current v0.7 DB
columnar state.

## Scope

- Sync the current worktree to `lestat-lx1`.
- Confirm PostgreSQL is available.
- Confirm Embree, OptiX, and Vulkan backend runtime availability.
- Run the v0.7 DB correctness sweep with `RTDL_POSTGRESQL_DSN=dbname=postgres`.
- Run the PostgreSQL-inclusive columnar repeated-query performance gate.
- Write local evidence and a report.

## Non-Goals

- No staging.
- No commit.
- No tag.
- No merge to main.
- No new performance claim outside the measured Linux setup.
