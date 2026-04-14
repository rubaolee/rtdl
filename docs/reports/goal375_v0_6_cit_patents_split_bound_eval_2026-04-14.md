# Goal 375 Report: v0.6 cit-Patents split-bound Linux evaluation

Date: 2026-04-14

## Summary

This slice executes the next bounded `cit-Patents` Linux step selected in Goal 374:

- `bfs` at `1000000` directed edges
- `triangle_count` at `100000` canonical undirected edges

## Linux results

Host:
- `lestat-lx1`

### BFS

| field | value |
| --- | --- |
| dataset | `graphalytics_cit_patents` |
| workload | `bfs` |
| max_edges_loaded | `1000000` |
| edge_count | `1000000` |
| vertex_count | `5751314` |
| python_seconds | `0.1239954199991189` |
| oracle_seconds | `1.0668449780205265` |
| postgresql_seconds | `0.00032035697950050235` |
| postgresql_setup_seconds | `42.83335640496807` |
| oracle_match | `true` |
| postgresql_match | `true` |

### Triangle count

| field | value |
| --- | --- |
| dataset | `graphalytics_cit_patents` |
| workload | `triangle_count` |
| graph_transform | `simple_undirected` |
| max_canonical_edges_loaded | `100000` |
| edge_count | `200000` |
| vertex_count | `4692122` |
| python_seconds | `3.8491162119898945` |
| oracle_seconds | `0.7847236479865387` |
| postgresql_seconds | `0.02595591504359618` |
| postgresql_setup_seconds | `4.892115190043114` |
| oracle_match | `true` |
| postgresql_match | `true` |

## Interpretation

- parity remains clean across Python/oracle/PostgreSQL for both workloads
- `bfs` still scales comfortably at the larger bound
- `triangle_count` remains practical enough for Python to stay in the timing picture at this bound
- PostgreSQL query time remains tiny for `bfs` and modest for `triangle_count`
- PostgreSQL setup time continues to dominate query time in both cases

## Boundary

This is still a bounded evaluation slice:

- not full `cit-Patents` closure
- not a final accepted production bound
- not a benchmark claim
- not a paper-scale reproduction claim
