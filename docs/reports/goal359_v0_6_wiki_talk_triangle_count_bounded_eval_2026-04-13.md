# Goal 359 Report: v0.6 wiki-Talk triangle-count bounded eval

## Delivered

- explicit real-data transform in code:
  - `load_snap_simple_undirected_graph(...)`
- bounded eval script:
  - `scripts/goal359_wiki_talk_triangle_count_eval.py`
- focused tests:
  - `tests/goal356_v0_6_graph_dataset_prep_test.py`
  - `tests/goal359_v0_6_wiki_talk_triangle_count_eval_test.py`

## Real-data transform

The first real-data triangle-count slice does **not** run directly on the directed `wiki-Talk` edge list.

Instead it uses this bounded simple-graph transform:
- read the SNAP edge list
- drop self-loops
- canonicalize each edge as `(min(src, dst), max(src, dst))`
- dedupe canonical edges
- materialize a simple undirected CSR graph

This keeps the `triangle_count` contract aligned with the current `v0.6` truth path:
- simple graph
- sorted neighbor lists
- no self-loops

## Local result

Command:

```text
python3 scripts/goal359_wiki_talk_triangle_count_eval.py --dataset build/graph_datasets/wiki-Talk.txt.gz --max-edges 50000 --repeats 1
```

Observed result:

| field | value |
| --- | --- |
| dataset | `snap_wiki_talk` |
| graph_transform | `simple_undirected` |
| max_canonical_edges_loaded | `50000` |
| vertex_count | `2394381` |
| edge_count | `100000` |
| python_seconds | `7.674925082945265` |
| oracle_seconds | `0.2656803749850951` |
| oracle_match | `true` |

## Linux result

Host:
- `lestat-lx1`

Command:

```text
python3 scripts/goal359_wiki_talk_triangle_count_eval.py --dataset build/graph_datasets/wiki-Talk.txt.gz --max-edges 50000 --repeats 3 --postgresql-dsn "dbname=postgres"
```

Observed result:

| field | value |
| --- | --- |
| dataset | `snap_wiki_talk` |
| graph_transform | `simple_undirected` |
| max_canonical_edges_loaded | `50000` |
| vertex_count | `2394381` |
| edge_count | `100000` |
| python_seconds | `13.751628719968721` |
| oracle_seconds | `0.40168821497354656` |
| postgresql_seconds | `0.23782865999964997` |
| postgresql_setup_seconds | `3.2653968860395253` |
| oracle_match | `true` |
| postgresql_match | `true` |

## Verification

```text
python3 -m unittest tests.goal356_v0_6_graph_dataset_prep_test tests.goal359_v0_6_wiki_talk_triangle_count_eval_test
Ran 5 tests
OK
```

Linux focused probe:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal356_v0_6_graph_dataset_prep_test tests.goal359_v0_6_wiki_talk_triangle_count_eval_test
Ran 5 tests
OK
```

## Boundary

This is the first bounded real-data `triangle_count` slice only.

It does **not** claim:
- full `wiki-Talk` closure
- large-scale graph benchmarking
- direct SIGMETRICS paper reproduction
- graph-native external-engine comparison beyond bounded PostgreSQL
- earlier combined PostgreSQL timing for this slice is superseded by the split
  query/setup measurement
