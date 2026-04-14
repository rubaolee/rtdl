# Goal 364 Report: v0.6 split-bound next-scale Linux graph evaluation

## Summary

This slice takes the next bounded real-data scale step after Goal 362 using
different bounds per workload:

- BFS:
  - `1000000` directed edges
- triangle count:
  - `200000` canonical undirected edges

The split is intentional. It keeps BFS growing while preventing triangle count
from turning into an unbounded “wait on Python” exercise.

## Linux results

Host:
- `lestat-lx1`

### BFS

| field | value |
| --- | --- |
| dataset | `snap_wiki_talk` |
| workload | `bfs` |
| max_edges_loaded | `1000000` |
| vertex_count | `2394381` |
| edge_count | `1000000` |
| python_seconds | `0.07623101898934692` |
| oracle_seconds | `0.5533416690304875` |
| postgresql_seconds | `0.0005816569901071489` |
| postgresql_setup_seconds | `48.80130802403437` |
| oracle_match | `true` |
| postgresql_match | `true` |

### Triangle count

| field | value |
| --- | --- |
| dataset | `snap_wiki_talk` |
| workload | `triangle_count` |
| graph_transform | `simple_undirected` |
| max_canonical_edges_loaded | `200000` |
| vertex_count | `2394381` |
| edge_count | `400000` |
| python_seconds | `32.56798675400205` |
| oracle_seconds | `0.49230242701014504` |
| postgresql_seconds | `1.0997799409669824` |
| postgresql_setup_seconds | `9.061798089998774` |
| oracle_match | `true` |
| postgresql_match | `true` |

## Interpretation

- parity remains clean across Python/oracle/PostgreSQL
- BFS still scales comfortably at this bound
- triangle count does not break, but Python timing is now clearly impractical as
  a performance baseline
- oracle remains a practical validation path
- PostgreSQL query time is now material for triangle count and still tiny for
  BFS

## Verification

Linux runs:

```text
python3 scripts/goal362_wiki_talk_larger_bfs_eval.py --dataset build/graph_datasets/wiki-Talk.txt.gz --max-edges 1000000 --repeats 3 --postgresql-dsn "dbname=postgres"
python3 scripts/goal362_wiki_talk_larger_triangle_count_eval.py --dataset build/graph_datasets/wiki-Talk.txt.gz --max-edges 200000 --repeats 3 --postgresql-dsn "dbname=postgres"
```

## Boundary

This is still a bounded evaluation slice:
- not full `wiki-Talk` closure
- not final benchmark status
- not paper-scale reproduction
- not a claim that Python triangle count remains a practical timing baseline
