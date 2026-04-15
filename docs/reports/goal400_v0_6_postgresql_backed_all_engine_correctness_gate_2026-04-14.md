# Goal 400 Report: v0.6 PostgreSQL-Backed All-Engine Correctness Gate

Date: 2026-04-14
Status: implemented, review pending

## Summary

Goal 400 redefines the corrected `v0.6` correctness bar.

Goal 399 remains valid as the first bounded multi-backend integration gate, but
it is no longer the final correctness gate because PostgreSQL-backed parity is
now required for all engines.

## Required Comparison Surface

For bounded graph cases, the following must agree:

- Python truth path
- native/oracle
- Embree
- OptiX
- Vulkan
- PostgreSQL

for both:

- `bfs`
- `triangle_count`

## PostgreSQL Requirement

PostgreSQL must be used as the external correctness anchor for this gate.

The gate must document:

- the SQL path used for `bfs`
- the SQL path used for `triangle_count`
- the indexes used
- any setup/query split if timing is reported

## What Landed

New PostgreSQL graph baseline module:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/graph_postgresql.py`

New focused tests:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal400_v0_6_postgresql_graph_correctness_test.py`

Public exports updated:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`

## PostgreSQL SQL Paths

Bounded BFS step:

- `build_postgresql_bfs_expand_sql(...)`
- one-step frontier expansion
- visited filtering
- `DISTINCT ON (dst_vertex)` dedupe to match the RT-kernel `bfs_discover(..., dedupe=True)` semantics
- final row order:
  - `ORDER BY level, dst_vertex, src_vertex`

Bounded triangle step:

- `build_postgresql_triangle_probe_sql(...)`
- one-step triangle probe from seed edges
- relational common-neighbor join:
  - `edges(u -> w)` joined with `edges(v -> w)`
- canonical ordering:
  - `u < v < w`
- final row order:
  - `ORDER BY u, v, w`

## PostgreSQL Indexes

Graph edge table indexes:

- `CREATE INDEX rtdl_graph_edges_tmp_src_idx ON rtdl_graph_edges_tmp (src)`
- `CREATE INDEX rtdl_graph_edges_tmp_dst_idx ON rtdl_graph_edges_tmp (dst)`
- `CREATE INDEX rtdl_graph_edges_tmp_src_dst_idx ON rtdl_graph_edges_tmp (src, dst)`

BFS input indexes:

- `CREATE INDEX rtdl_frontier_tmp_vertex_idx ON rtdl_frontier_tmp (vertex_id)`
- `CREATE INDEX rtdl_visited_tmp_vertex_idx ON rtdl_visited_tmp (vertex_id)`

Triangle input indexes:

- `CREATE INDEX rtdl_edge_seeds_tmp_uv_idx ON rtdl_edge_seeds_tmp (u, v)`

All temp tables are analyzed before query execution.

## Verification

Local focused PostgreSQL graph suite:

```text
python3 -m unittest tests.goal400_v0_6_postgresql_graph_correctness_test
```

Result:

- `Ran 6 tests`
- `OK (skipped=2)`

Local integrated graph + PostgreSQL suite:

```text
python3 -m unittest \
  tests.goal389_v0_6_rt_graph_bfs_truth_path_test \
  tests.goal390_v0_6_rt_graph_triangle_truth_path_test \
  tests.goal391_v0_6_rt_graph_bfs_oracle_test \
  tests.goal392_v0_6_rt_graph_triangle_oracle_test \
  tests.goal393_v0_6_rt_graph_bfs_embree_test \
  tests.goal394_v0_6_rt_graph_bfs_optix_test \
  tests.goal395_v0_6_rt_graph_bfs_vulkan_test \
  tests.goal396_v0_6_rt_graph_triangle_embree_test \
  tests.goal397_v0_6_rt_graph_triangle_optix_test \
  tests.goal398_v0_6_rt_graph_triangle_vulkan_test \
  tests.goal400_v0_6_postgresql_graph_correctness_test
```

Result:

- `Ran 51 tests`
- `OK (skipped=18)`

Linux PostgreSQL-focused suite on `lestat-lx1`:

```text
RTDL_POSTGRESQL_DSN="dbname=postgres" python3 -m unittest \
  tests.goal400_v0_6_postgresql_graph_correctness_test
```

Result:

- `Ran 6 tests`
- `OK`

Linux integrated graph + PostgreSQL suite on `lestat-lx1`:

```text
RTDL_POSTGRESQL_DSN="dbname=postgres" python3 -m unittest \
  tests.goal389_v0_6_rt_graph_bfs_truth_path_test \
  tests.goal390_v0_6_rt_graph_triangle_truth_path_test \
  tests.goal391_v0_6_rt_graph_bfs_oracle_test \
  tests.goal392_v0_6_rt_graph_triangle_oracle_test \
  tests.goal393_v0_6_rt_graph_bfs_embree_test \
  tests.goal394_v0_6_rt_graph_bfs_optix_test \
  tests.goal395_v0_6_rt_graph_bfs_vulkan_test \
  tests.goal396_v0_6_rt_graph_triangle_embree_test \
  tests.goal397_v0_6_rt_graph_triangle_optix_test \
  tests.goal398_v0_6_rt_graph_triangle_vulkan_test \
  tests.goal400_v0_6_postgresql_graph_correctness_test
```

Result:

- `Ran 51 tests`
- `OK`

Linux live backend state during this run:

- `optix_version = (9, 0, 0)`
- `vulkan_version = (0, 1, 0)`
- availability:
  - Embree `True`
  - OptiX `True`
  - Vulkan `True`

## Gate Result

Goal 400 now upgrades the corrected graph line from:

- Python/oracle/all-engine bounded parity

to:

- Python/oracle/all-engine/PostgreSQL bounded parity

for both:

- `bfs`
- `triangle_count`

## Honesty Boundary

Goal 400 establishes the PostgreSQL-backed correctness gate.

It does not yet establish:

- large-scale performance closure
- final benchmark conclusions
- release closure

That remains Goal 401 and later.
