# Goal 369 Report: v0.6 first bounded cit-Patents BFS Linux evaluation

Date: 2026-04-13

## Summary

This slice runs the first bounded Linux BFS evaluation on:
- `graphalytics_cit_patents`

using the current:
- Python truth path
- compiled CPU/oracle path
- PostgreSQL baseline

## Linux result

Host:
- `lestat-lx1`

| field | value |
| --- | --- |
| dataset | `graphalytics_cit_patents` |
| workload | `bfs` |
| max_edges_loaded | `500000` |
| edge_count | `500000` |
| vertex_count | `5340014` |
| python_seconds | `0.10589127999264747` |
| oracle_seconds | `0.9401946720317937` |
| postgresql_seconds | `0.0003507979563437402` |
| postgresql_setup_seconds | `23.093791443970986` |
| oracle_match | `true` |
| postgresql_match | `true` |

## Important dataset boundary

The raw SNAP `cit-Patents` edge list used for this bounded run exposes a larger
vertex-ID range than the Graphalytics family hint:

- Graphalytics family hint:
  - `3774768`
- observed bounded raw-ID vertex range in this run:
  - `5340014`

This is not a runtime correctness bug. It means the raw edge list is not tightly
renumbered to the Graphalytics family hint, so the current bounded loader
preserves a sparse higher-ID range when early edges touch high-ID vertices.

## Interpretation

- parity is clean across Python/oracle/PostgreSQL
- BFS remains practical on this second real dataset family
- PostgreSQL query time is tiny relative to setup time here as well
- the raw-ID-range observation must remain explicit in future `cit-Patents`
  reports so we do not overstate direct comparability to a renumbered packaged
  graph

## Boundary

This is a bounded first Linux `cit-Patents` BFS slice:

- not full `cit-Patents` closure
- not triangle-count closure
- not a benchmark claim
- not a paper-scale reproduction claim
