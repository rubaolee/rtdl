# Goal 373 Report: v0.6 bounded cit-Patents triangle-count Linux probe

Date: 2026-04-14

## Summary

This slice records the first bounded Linux `triangle_count` probe on:

- `graphalytics_cit_patents`

using the currently accepted:

- Python truth path
- compiled CPU/oracle path
- PostgreSQL external baseline

## Linux result

Host:
- `lestat-lx1`

| field | value |
| --- | --- |
| dataset | `graphalytics_cit_patents` |
| workload | `triangle_count` |
| graph_transform | `simple_undirected` |
| max_canonical_edges_loaded | `50000` |
| edge_count | `100000` |
| vertex_count | `4692122` |
| python_seconds | `3.606278282997664` |
| oracle_seconds | `0.7714257469633594` |
| postgresql_seconds | `0.011647004052065313` |
| postgresql_setup_seconds | `2.557821645983495` |
| oracle_match | `true` |
| postgresql_match | `true` |

## Interpretation

- the first bounded `cit-Patents` triangle-count slice is parity-clean across
  Python/oracle/PostgreSQL
- at this first bound, Python is still practical enough to remain part of the
  timing picture
- PostgreSQL query time is small relative to Python and oracle, while setup
  time remains materially larger than query time

## Boundary

This is a bounded first Linux probe only:

- not full `cit-Patents` triangle-count closure
- not a larger accepted production bound yet
- not a benchmark claim
- not a paper-scale reproduction claim
