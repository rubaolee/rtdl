# Goal 347 Report: v0.6 PostgreSQL Graph Baseline Plan

Date: 2026-04-13

## Summary

This slice defines how PostgreSQL should be used in the opening `v0.6` graph
workload line.

## Decision

PostgreSQL should be used as:

- a bounded external correctness baseline
- a bounded external SQL/database performance baseline

for:

- `bfs`
- `triangle_count`

## Why PostgreSQL is acceptable here

Unlike PostGIS, plain PostgreSQL can represent graphs directly through tables
and SQL:

- BFS:
  - recursive CTEs
- triangle count:
  - edge-table joins / self-joins

That makes PostgreSQL a defensible external graph baseline for bounded cases.

## What PostgreSQL should not be claimed to be

PostgreSQL should not be presented as:

- a graph-specialized engine
- a paper-equivalent system for the SIGMETRICS 2025 graph work
- the primary truth path

The primary truth path remains:

- Python truth path first
- compiled CPU/native RTDL next

## Recommended baseline stack

For the opening `v0.6` graph line:

1. Python truth path
2. compiled CPU/native RTDL baseline
3. PostgreSQL bounded external baseline
4. first accelerated Linux backend later

## Recommendation

Proceed with PostgreSQL as the first external graph baseline for bounded
correctness and bounded timing comparisons in `v0.6`.
