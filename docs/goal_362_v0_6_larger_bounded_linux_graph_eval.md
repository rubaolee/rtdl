# Goal 362: v0.6 larger bounded Linux real-data graph evaluation

## Status

Implemented. Measured locally and on Linux with PostgreSQL using the corrected
query/setup timing split.

## Scope

Extends Goal 357 (BFS, 200k directed edges) and Goal 359 (triangle count,
50k canonical undirected edges) to larger bounded slices on SNAP wiki-Talk:

| workload | previous bound | goal 362 bound |
|---|---|---|
| BFS | 200,000 directed edges | 500,000 directed edges |
| triangle count | 50,000 canonical undirected edges | 150,000 canonical undirected edges |

Preserves all constraints from Goal 361 corrected timing contract:
- `postgresql_seconds` = query-only
- `postgresql_setup_seconds` = setup / load / index / analyze

## Dataset

SNAP wiki-Talk directed edge-list (5,021,410 total directed edges).
Both workloads load from `build/graph_datasets/wiki-Talk.txt.gz`.

Transform for triangle count: simple undirected, self-loops dropped, canonical
undirected edges deduplicated.

## Key finding at this scale

BFS Python truth path remains fast (69 ms median at 500k edges).
Triangle count Python truth path is slow (19 s median at 150k canonical edges)
because high-degree vertices in the early wiki-Talk edges make the
merge-intersection count expensive. The C++ oracle (364 ms) is the viable
validation path for triangle count at larger scales. Both workloads report
`oracle_match: true`.

## Honesty boundary

- Bounded: 500k / 150k edges from a 5M-edge dataset.
- Linux PostgreSQL numbers are now real for this slice.
- No full-dataset claim.
- No paper-scale reproduction.

## Files

- `scripts/goal362_wiki_talk_larger_bfs_eval.py`
- `scripts/goal362_wiki_talk_larger_triangle_count_eval.py`
- `tests/goal362_v0_6_wiki_talk_larger_bfs_eval_test.py`
- `tests/goal362_v0_6_wiki_talk_larger_triangle_count_eval_test.py`
- `docs/reports/claude_goal362_v0_6_larger_bounded_linux_graph_eval_2026-04-13.md`
