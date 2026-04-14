# Goal 362 Report: v0.6 larger bounded Linux real-data graph evaluation

## Summary

This slice extends the current bounded `wiki-Talk` real-data line to a larger
but still clearly bounded Linux evaluation for:
- `bfs`
- `triangle_count`

It preserves the corrected timing contract from Goal 361:
- `postgresql_seconds`
  - query-only
- `postgresql_setup_seconds`
  - setup/load/index/analyze

## Scale chosen

| workload | previous bound | Goal 362 bound | factor |
| --- | ---: | ---: | ---: |
| BFS directed edges loaded | `200000` | `500000` | `2.5x` |
| triangle count canonical undirected edges loaded | `50000` | `150000` | `3x` |

## Linux results

Host:
- `lestat-lx1`

### BFS

| field | value |
| --- | --- |
| dataset | `snap_wiki_talk` |
| workload | `bfs` |
| max_edges_loaded | `500000` |
| vertex_count | `2394381` |
| edge_count | `500000` |
| python_seconds | `0.06200010102475062` |
| oracle_seconds | `0.4794901569839567` |
| postgresql_seconds | `0.000506219977978617` |
| postgresql_setup_seconds | `24.861175783968065` |
| oracle_match | `true` |
| postgresql_match | `true` |

### Triangle count

| field | value |
| --- | --- |
| dataset | `snap_wiki_talk` |
| workload | `triangle_count` |
| graph_transform | `simple_undirected` |
| max_canonical_edges_loaded | `150000` |
| vertex_count | `2394381` |
| edge_count | `300000` |
| python_seconds | `27.710148987011053` |
| oracle_seconds | `0.45065801800228655` |
| postgresql_seconds | `0.6715572610264644` |
| postgresql_setup_seconds | `6.537921606970485` |
| oracle_match | `true` |
| postgresql_match | `true` |

## Interpretation

- parity remains clean across:
  - Python truth path
  - oracle
  - PostgreSQL
- the corrected timing split remains necessary
- BFS PostgreSQL query time stays tiny relative to setup time at this bound
- triangle-count PostgreSQL query time becomes material at this larger bound
- Python triangle-count timing degrades sharply and is no longer a practical
  performance baseline at this scale

## Verification

Local focused additions:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal362_v0_6_wiki_talk_larger_bfs_eval_test \
  tests.goal362_v0_6_wiki_talk_larger_triangle_count_eval_test
Ran 4 tests
OK
```

Linux focused probe:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal362_v0_6_wiki_talk_larger_bfs_eval_test \
  tests.goal362_v0_6_wiki_talk_larger_triangle_count_eval_test
Ran 4 tests
OK
```

## Boundary

This is still a bounded real-data evaluation slice:
- not full `wiki-Talk` closure
- not full dataset benchmarking
- not paper-scale reproduction
- not an accelerated graph-backend claim beyond the current oracle path
