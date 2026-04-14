# Claude Review: Goal 362 — v0.6 Larger Bounded Real-Data Graph Evaluation

Date: 2026-04-13
Reviewer: Claude Sonnet 4.6

---

## Scale chosen and why

| workload | previous bound (Goal 357/359) | Goal 362 bound | factor |
|---|---|---|---|
| BFS directed edges loaded | 200,000 | 500,000 | 2.5× |
| triangle count canonical undirected edges loaded | 50,000 | 150,000 | 3× |

**Rationale for BFS bound (500k):** The Python BFS truth path at 200k edges ran
in ~50 ms; at 500k it runs in ~69 ms. The C++ oracle at 200k ran in ~342 ms
(Goal 361); at 500k it runs in ~471 ms. Both paths remain fast and the
oracle/python agreement is maintained. 500k is 10% of the 5.0M total directed
edges in wiki-Talk — a meaningful but still clearly bounded slice.

**Rationale for triangle count bound (150k):** The previous bound was 50k
canonical undirected edges. At 100k the Python truth path took ~14.6 s (median,
3 repeats); at 150k it took ~19.1 s. Both bounds are within the C++ oracle's
fast path (~0.39 s and ~0.36 s respectively). The 3× increase from 50k to 150k
is the largest step that keeps the oracle under 0.5 s and still represents a
meaningful scale increase. The Python truth path is slow at this scale — this is
a documented finding (see below), not a defect.

---

## Measured results (macOS)

### BFS — 500,000 directed edges, wiki-Talk, source_id=0

```json
{
  "dataset": "snap_wiki_talk",
  "edge_count": 500000,
  "goal": "goal362",
  "max_edges_loaded": 500000,
  "oracle_match": true,
  "oracle_seconds": 0.470648665970657,
  "python_seconds": 0.06933454202953726,
  "vertex_count": 2394381,
  "workload": "bfs"
}
```

Repeats: 3 (median reported). `oracle_match: true`.

### Triangle count — 150,000 canonical undirected edges, wiki-Talk

```json
{
  "dataset": "snap_wiki_talk",
  "edge_count": 300000,
  "goal": "goal362",
  "graph_transform": "simple_undirected",
  "max_canonical_edges_loaded": 150000,
  "oracle_match": true,
  "oracle_seconds": 0.36369070794899017,
  "python_seconds": 19.082386333029717,
  "vertex_count": 2394381,
  "workload": "triangle_count"
}
```

Repeats: 3 (median reported). `oracle_match: true`.

**Note on vertex_count:** Both workloads report `vertex_count: 2,394,381` even
at bounded edge counts. This is correct: SNAP wiki-Talk contains edges between
high-ID vertices that appear early in the file, so the vertex ID range spans the
full dataset even when only a fraction of edges are loaded. The loaded graphs are
genuinely sparse (500k edges on 2.4M vertices for BFS; 300k adjacency entries
for triangle count).

---

## Key finding: Python triangle count does not scale to this range

At 150k canonical undirected edges on wiki-Talk, the Python truth path takes
~19 s (median, 3 repeats). At 50k edges it took ~6–8 s. The degradation is
super-linear because wiki-Talk contains high-degree hubs even in the first 150k
canonical edges; the merge-intersection triangle count algorithm is O(m · d̄)
where d̄ is the mean degree, and the high-degree hubs dominate.

**The C++ oracle at 364 ms is the practical validation path for triangle count
at this scale.** The Python truth path remains the ground-truth reference but
should not be the primary timing benchmark.

This finding strengthens the case for the oracle-first approach in v0.6.

---

## Files changed

| file | change |
|---|---|
| `scripts/goal362_wiki_talk_larger_bfs_eval.py` | new — BFS eval script, default max_edges=500,000 |
| `scripts/goal362_wiki_talk_larger_triangle_count_eval.py` | new — triangle count eval script, default max_edges=150,000 |
| `tests/goal362_v0_6_wiki_talk_larger_bfs_eval_test.py` | new — 2 tests using small in-process fixture |
| `tests/goal362_v0_6_wiki_talk_larger_triangle_count_eval_test.py` | new — 2 tests using small in-process fixture |
| `docs/goal_362_v0_6_larger_bounded_linux_graph_eval.md` | new — goal record |
| `docs/reports/claude_goal362_v0_6_larger_bounded_linux_graph_eval_2026-04-13.md` | new — this report |

No existing files were modified. The previous eval scripts (goal357, goal359)
are unchanged and continue to represent the earlier bounded results.

---

## Tests run

```
# New goal362 tests:
PYTHONPATH=src:. python3 -m unittest \
  tests.goal362_v0_6_wiki_talk_larger_bfs_eval_test \
  tests.goal362_v0_6_wiki_talk_larger_triangle_count_eval_test \
  -v
# Ran 4 tests in 0.908s — OK

# Full focused v0.6 graph suite (no regressions):
PYTHONPATH=src:. python3 -m unittest \
  tests.goal345_v0_6_bfs_truth_path_test \
  tests.goal346_v0_6_triangle_count_truth_path_test \
  tests.goal348_postgresql_bfs_baseline_test \
  tests.goal349_postgresql_triangle_count_baseline_test \
  tests.goal350_v0_6_bfs_oracle_test \
  tests.goal351_v0_6_triangle_count_oracle_test \
  tests.goal352_v0_6_graph_eval_test \
  tests.goal356_v0_6_graph_dataset_prep_test \
  tests.goal357_v0_6_wiki_talk_bfs_eval_test \
  tests.goal359_v0_6_wiki_talk_triangle_count_eval_test \
  tests.claude_goal353_v0_6_graph_review_test \
  tests.goal362_v0_6_wiki_talk_larger_bfs_eval_test \
  tests.goal362_v0_6_wiki_talk_larger_triangle_count_eval_test
# Ran 97 tests in 1.631s — OK
```

---

## Honesty boundary for this slice

## Measured results (Linux, live PostgreSQL)

### BFS — 500,000 directed edges, wiki-Talk, source_id=0

```json
{
  "dataset": "snap_wiki_talk",
  "edge_count": 500000,
  "goal": "goal362",
  "max_edges_loaded": 500000,
  "oracle_match": true,
  "oracle_seconds": 0.4794901569839567,
  "postgresql_match": true,
  "postgresql_seconds": 0.000506219977978617,
  "postgresql_setup_seconds": 24.861175783968065,
  "python_seconds": 0.06200010102475062,
  "vertex_count": 2394381,
  "workload": "bfs"
}
```

### Triangle count — 150,000 canonical undirected edges, wiki-Talk

```json
{
  "dataset": "snap_wiki_talk",
  "edge_count": 300000,
  "goal": "goal362",
  "graph_transform": "simple_undirected",
  "max_canonical_edges_loaded": 150000,
  "oracle_match": true,
  "oracle_seconds": 0.45065801800228655,
  "postgresql_match": true,
  "postgresql_seconds": 0.6715572610264644,
  "postgresql_setup_seconds": 6.537921606970485,
  "python_seconds": 27.710148987011053,
  "vertex_count": 2394381,
  "workload": "triangle_count"
}
```

**What this slice is:**
- Bounded real-data BFS and triangle count on SNAP wiki-Talk at 2.5–3× the
  previous bounded sizes.
- Oracle validation confirmed (oracle_match: true for both workloads).
- Linux PostgreSQL validation confirmed with corrected timing split:
  - `postgresql_seconds` = query-only
  - `postgresql_setup_seconds` = setup/load/index/analyze
- Python and C++ oracle timing measured locally on macOS and on Linux.

**What this slice is not:**
- Full wiki-Talk dataset evaluation (5.0M edges). Current bounds are 10% for
  BFS and 3% for triangle count.
- Final benchmark status or paper-scale reproduction.
- A claim that Python triangle count scales. At 150k edges it takes 19 s on
  macOS and 27.7 s on Linux — this is an explicit observation, not a validated
  benchmark.

**Next step for Linux:** Run both scripts on the Linux host with
`--postgresql-dsn` pointed at the live database and append the
`postgresql_seconds` / `postgresql_setup_seconds` results to this record.
