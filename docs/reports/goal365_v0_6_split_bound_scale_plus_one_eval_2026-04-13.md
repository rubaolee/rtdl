# Goal 365 Report: v0.6 split-bound scale-plus-one Linux graph evaluation

## Summary

This slice advances the split-bound `wiki-Talk` line by one more bounded step:

- BFS:
  - `1500000` directed edges
- triangle count:
  - `250000` canonical undirected edges

The split keeps the evaluation useful without letting triangle count collapse
into an unbounded Python timing exercise.

## Linux results

Host:
- `lestat-lx1`

### BFS

| field | value |
| --- | --- |
| dataset | `snap_wiki_talk` |
| workload | `bfs` |
| max_edges_loaded | `1500000` |
| vertex_count | `2394381` |
| edge_count | `1500000` |
| python_seconds | `0.09003346302779391` |
| oracle_seconds | `0.6294806849909946` |
| postgresql_seconds | `0.0005864349659532309` |
| postgresql_setup_seconds | `63.54525600600755` |
| oracle_match | `true` |
| postgresql_match | `true` |

### Triangle count

| field | value |
| --- | --- |
| dataset | `snap_wiki_talk` |
| workload | `triangle_count` |
| graph_transform | `simple_undirected` |
| max_canonical_edges_loaded | `250000` |
| vertex_count | `2394381` |
| edge_count | `500000` |
| python_seconds | `41.29946040402865` |
| oracle_seconds | `0.5279242940014228` |
| postgresql_seconds | `2.244469935016241` |
| postgresql_setup_seconds | `12.479064457991626` |
| oracle_match | `true` |
| postgresql_match | `true` |

## Interpretation

- parity remains clean across Python/oracle/PostgreSQL
- BFS still scales comfortably at this bound
- triangle count is still correct, but Python timing is now firmly in
  truth-preserving-only territory
- PostgreSQL query time for triangle count continues to rise materially while
  BFS query time remains tiny relative to setup time

## Boundary

This is still a bounded evaluation slice:
- not full `wiki-Talk` closure
- not a final benchmark
- not paper-scale reproduction
- not a claim that Python triangle count is a practical timing baseline here
