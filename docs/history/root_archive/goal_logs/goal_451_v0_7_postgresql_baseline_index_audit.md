# Goal 451: v0.7 PostgreSQL Baseline Index Audit

Date: 2026-04-16

## Purpose

Audit the PostgreSQL baseline used for v0.7 DB performance claims.

Goal 450 used PostgreSQL temp tables with B-tree indexes on `row_id` and each
predicate field plus `ANALYZE`. This goal checks whether that baseline should be
described as naive, indexed, or fully tuned by comparing it against no-index and
composite/covering index variants.

## Scope

- Linux only.
- PostgreSQL only.
- Bounded v0.7 DB workloads:
  - conjunctive scan
  - grouped count
  - grouped sum
- Row count: configurable, default 200,000.
- Repeats: configurable, default 10.
- Evidence:
  - setup timing
  - query timing
  - total repeated timing
  - row hashes
  - `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` summary

## Non-Goals

- No arbitrary SQL support.
- No claim that RTDL is a DBMS.
- No release authorization.
- No staging, commit, tag, push, or merge.
