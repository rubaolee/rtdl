# Goal 355 Report: v0.6 Bounded Linux Graph Evaluation

Date: 2026-04-13

## Summary

This slice records the first bounded Linux evaluation table for the opening
`v0.6` graph workloads.

Host:

- `lestat-lx1`

Backends compared:

- Python truth path
- compiled CPU/native oracle
- PostgreSQL bounded external baseline

## Workload table

| Workload | Graph Family | Vertex Count | Edge Count | Python (s) | Oracle (s) | PostgreSQL Query (s) | PostgreSQL Setup (s) | Oracle Match | PostgreSQL Match |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `bfs` | binary tree | `127` | `126` | `0.000129507` | `0.000216405` | `0.001259607` | `0.012505270` | `true` | `true` |
| `triangle_count` | clique | `24` | `552` | `0.001895895` | `0.000233474` | `0.001078883` | `0.019379521` | `true` | `true` |

## Important boundary

- the bounded PostgreSQL BFS baseline is restricted here to an acyclic graph
  family
- this slice does not claim a safe general cyclic-graph PostgreSQL BFS closure
- this slice does not claim accelerated graph performance

## Interpretation

- the opening `v0.6` graph stack is now parity-clean across:
  - Python truth path
  - compiled CPU/native baseline
  - bounded Linux PostgreSQL baseline
- the earlier combined PostgreSQL timing interpretation for this slice is
  superseded
- query-only PostgreSQL timing is much smaller than setup timing on these
  bounded synthetic cases
- PostgreSQL remains an external SQL/database baseline, not a graph-specialized
  engine claim
