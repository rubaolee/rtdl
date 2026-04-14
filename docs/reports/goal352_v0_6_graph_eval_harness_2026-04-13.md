# Goal 352 Report: v0.6 Graph Evaluation Harness

Date: 2026-04-13

## Summary

This slice adds a bounded evaluation surface for the opening `v0.6` graph line:

- synthetic CSR graph helpers
- BFS comparison helper
- triangle-count comparison helper
- a Linux-oriented evaluation script

## What was added

- `cycle_graph`, `grid_graph`, and `clique_graph`
- `bfs_baseline_evaluation(...)`
- `triangle_count_baseline_evaluation(...)`
- a JSON-emitting evaluation script for Linux use
- focused tests for graph generation and evaluation-shape behavior

## Current timing contract

The PostgreSQL portion of the harness now reports:

- `postgresql_seconds`
  - query-only timing
- `postgresql_setup_seconds`
  - table preparation / load / index / analyze timing

This replaces the earlier, flawed interpretation where repeated setup and query
work were measured together as if they were a single query-time baseline.

## Methodology Correction (Remediation)

Following the v0.5+v0.6 audit, this harness was remediated to resolve a
high-severity methodology flaw. Previous versions included PostgreSQL
table-preparation overhead (drop/create/ingestion) within the repeat-timed
query window.

Current harness now separates:
- `postgresql_setup_seconds`: one-off ingestion and index-prep time
- `postgresql_seconds`: median time of the actual query execution

## Current boundary

This is a bounded harness for the opening graph line:

- not a paper-reproduction claim
- not an accelerated-backend claim
- not a final benchmark suite
- PostgreSQL query timing and setup timing must be interpreted separately
