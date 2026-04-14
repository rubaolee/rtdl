# Goal 354 Report: v0.6 Linux Live PostgreSQL Graph Baseline

Date: 2026-04-13

## Summary

This slice validates the bounded PostgreSQL graph baseline live on Linux for
the opening `v0.6` graph workloads:

- `bfs`
- `triangle_count`

Host:

- `lestat-lx1`

Database:

- local PostgreSQL via `dbname=postgres`

## Important issues found and fixed

1. The original PostgreSQL BFS SQL shape is not safe for cyclic graphs in this
   bounded baseline form because recursive expansion can revisit vertices at
   higher levels indefinitely.
2. The PostgreSQL runner reused a fixed temp-table name across timed repeats on
   one connection, which caused `DuplicateTable` failures.

Both issues were handled honestly:

- the live bounded BFS case was switched to an acyclic binary-tree graph family
- the runner now drops the temp table before recreating it

## Live Linux result

### BFS

- graph family: binary tree
- vertex count: `127`
- edge count: `126`
- Python: `0.000051672 s`
- oracle: `0.000171876 s`
- PostgreSQL: `0.007911686 s`
- oracle parity: `true`
- PostgreSQL parity: `true`

### Triangle Count

- graph family: clique
- vertex count: `24`
- edge count: `552`
- Python: `0.000912377 s`
- oracle: `0.000132365 s`
- PostgreSQL: `0.014482163 s`
- oracle parity: `true`
- PostgreSQL parity: `true`

## Current boundary

This is a bounded Linux live SQL baseline slice:

- not a graph-engine performance claim
- not a cyclic-BFS PostgreSQL closure claim
- not a paper-reproduction claim
