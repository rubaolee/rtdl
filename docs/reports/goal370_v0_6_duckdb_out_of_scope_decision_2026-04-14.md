# Goal 370 Report: v0.6 DuckDB out-of-scope baseline decision

Date: 2026-04-14

## Summary

The detailed audit recommended adding DuckDB as a fallback graph baseline.

For this project line, that recommendation is intentionally declined.

## Decision

For `v0.6`, the SQL/database baseline remains:

- PostgreSQL

DuckDB is explicitly:

- considered
- not adopted
- out of scope for the current `v0.6` line

## Why this is the right decision

### 1. PostgreSQL is already real in the current graph line

The project already has bounded PostgreSQL baseline support for:

- `bfs`
- `triangle_count`

and that support is already exercised in the current Linux evaluation line.

### 2. DuckDB is not needed for correctness

Current correctness anchors are:

- Python truth path
- native/oracle parity
- PostgreSQL bounded external baseline

DuckDB does not close a correctness gap that is currently blocking the line.

### 3. Adding DuckDB would expand scope rather than close a defect

At this point, DuckDB would be:

- an additional convenience baseline
- not a required remediation for the graph workload line

That makes it a scope-expansion choice, not a missing-core-fix.

## Approved baseline stack

For the current `v0.6` graph line:

1. Python truth path
2. compiled CPU/native RTDL oracle
3. PostgreSQL bounded external SQL baseline
4. accelerated backend work later, if chosen

## Audit resolution

The DuckDB audit finding is resolved as follows:

- the project acknowledges the recommendation
- the project intentionally declines it for the current scope
- the absence of DuckDB is not treated as an open blocking defect

## Boundary

This decision does not claim:

- DuckDB is a bad idea in general
- DuckDB can never be added later
- PostgreSQL is a graph-specialized engine

It only says:

- DuckDB is not part of the bounded `v0.6` plan
- PostgreSQL is the chosen SQL baseline for this line
