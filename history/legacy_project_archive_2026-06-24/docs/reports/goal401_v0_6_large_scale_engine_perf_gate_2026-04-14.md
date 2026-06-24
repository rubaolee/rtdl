# Goal 401 Report: v0.6 Large-Scale Engine Performance Gate

Date: 2026-04-14
Status: implemented, review pending

## Summary

Goal 401 is implemented as the first bounded large-scale performance gate for
the corrected RT-kernel graph line.

This goal follows Goal 400:

- Goal 400 = PostgreSQL-backed correctness
- Goal 401 = bounded large-scale engine performance

## Required Performance Surface

Backends:

- Embree
- OptiX
- Vulkan
- PostgreSQL

Workloads:

- `bfs`
- `triangle_count`

## PostgreSQL Requirement

PostgreSQL must use good indexes, and the report must separate:

- query time
- setup/load/index time

## Data Requirement

Large-scale runs must move beyond micro-graphs and use bounded large graph
data that is meaningful for engine comparison.

## Implementation Added

New files:

- `src/rtdsl/graph_datasets.py`
- `src/rtdsl/graph_perf.py`
- `scripts/goal401_large_scale_rt_graph_perf.py`
- `tests/goal401_v0_6_large_scale_engine_perf_gate_test.py`

Updated:

- `src/rtdsl/__init__.py`

## What The Harness Measures

This harness measures the corrected RT graph line honestly:

- one bounded `bfs` expand step on a large real-data graph slice
- one bounded `triangle_count` probe step on a large real-data graph slice

This is not yet a claim of end-to-end whole-graph RT execution.

For the RT backends:

- prepare time is measured once through `prepare_embree(...)`,
  `prepare_optix(...)`, `prepare_vulkan(...)` plus `bind(...)`
- execution time is measured from repeated `Prepared*Execution.run()` calls

For PostgreSQL:

- setup time includes temp-table load, index creation, and `ANALYZE`
- query time is measured separately

## PostgreSQL Indexing Used

From `src/rtdsl/graph_postgresql.py`:

- graph edge table:
  - `(src)`
  - `(dst)`
  - `(src, dst)`
- BFS temp tables:
  - frontier `(vertex_id)`
  - visited `(vertex_id)`
- triangle temp table:
  - seed edges `(u, v)`

## Verification

Local:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal401_v0_6_large_scale_engine_perf_gate_test -v
# Ran 7 tests — OK

PYTHONPATH=src:. python3 -m unittest \
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
  tests.goal400_v0_6_postgresql_graph_correctness_test -v
# Ran 51 tests — OK (skipped on unavailable local backends)
```

Linux `lestat-lx1` fresh sync:

```bash
cd /home/lestat/tmp/rtdl_v0_6_rt_check
PYTHONPATH=src:. python3 -m unittest discover -s tests \
  -p "goal401_v0_6_large_scale_engine_perf_gate_test.py" -v
# Ran 7 tests — OK

make build-vulkan
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc

PYTHONPATH=src:. RTDL_POSTGRESQL_DSN="dbname=postgres" python3 \
  scripts/goal401_large_scale_rt_graph_perf.py \
  --dataset /home/lestat/work/rtdl_v06_graph_probe/build/graph_datasets/wiki-Talk.txt.gz \
  --dataset-name snap_wiki_talk \
  --workload bfs \
  --max-edges 1000000 \
  --frontier-size 4096 \
  --source-id 0 \
  --repeats 3 \
  --postgresql-dsn "dbname=postgres"

PYTHONPATH=src:. RTDL_POSTGRESQL_DSN="dbname=postgres" python3 \
  scripts/goal401_large_scale_rt_graph_perf.py \
  --dataset /home/lestat/work/rtdl_v06_graph_stage/build/graph_datasets/cit-Patents.txt.gz \
  --dataset-name graphalytics_cit_patents \
  --workload triangle_count \
  --max-edges 100000 \
  --seed-count 8192 \
  --repeats 3 \
  --postgresql-dsn "dbname=postgres"
```

## Measured Results

### BFS Step Performance

Dataset:

- `snap_wiki_talk`
- first `1,000,000` directed edges loaded
- actual frontier batch used: `1,884` expandable vertices

```json
{
  "dataset": "snap_wiki_talk",
  "edge_count": 1000000,
  "embree_available": true,
  "embree_prepare_seconds": 0.43921319500077516,
  "embree_seconds": 0.6687887600855902,
  "frontier_size": 1884,
  "max_edges_loaded": 1000000,
  "optix_available": true,
  "optix_prepare_seconds": 0.43626449001021683,
  "optix_seconds": 0.47295012103859335,
  "postgresql_seconds": 1.2444212369155139,
  "postgresql_setup_seconds": 36.560594053938985,
  "vertex_count": 2394381,
  "vulkan_available": true,
  "vulkan_prepare_seconds": 0.4364068900467828,
  "vulkan_seconds": 0.47580938693135977,
  "workload": "bfs"
}
```

### Triangle Probe Performance

Dataset:

- `graphalytics_cit_patents`
- first `100,000` canonical undirected edges loaded
- actual seed batch used: `8,192` canonical edges

```json
{
  "dataset": "graphalytics_cit_patents",
  "edge_count": 200000,
  "embree_available": true,
  "embree_prepare_seconds": 0.6451302459463477,
  "embree_seconds": 0.052159475977532566,
  "graph_transform": "simple_undirected",
  "max_canonical_edges_loaded": 100000,
  "optix_available": true,
  "optix_prepare_seconds": 0.6372530059888959,
  "optix_seconds": 0.004164474899880588,
  "postgresql_seconds": 0.004445821978151798,
  "postgresql_setup_seconds": 8.719684956944548,
  "seed_count": 8192,
  "vertex_count": 4692122,
  "vulkan_available": true,
  "vulkan_prepare_seconds": 0.6507506290217862,
  "vulkan_seconds": 0.004779421957209706,
  "workload": "triangle_count"
}
```

## Findings

- The corrected RT graph line now has real large-data Linux performance
  evidence on:
  - Embree
  - OptiX
  - Vulkan
  - PostgreSQL
- PostgreSQL setup/index cost is materially larger than query cost for both
  workloads, so the query/setup split remains necessary.
- On this bounded BFS step, OptiX and Vulkan are faster than Embree and faster
  than PostgreSQL query time, but PostgreSQL setup dominates the full external
  baseline cost.
- On this bounded triangle probe step, OptiX, Vulkan, and PostgreSQL query
  time are all in the same low-millisecond range, while Embree is slower and
  PostgreSQL setup still dominates total external-baseline cost.

## Honesty Boundary

This goal closes the first bounded large-data performance gate for the corrected
RT-kernel graph line.

What it is:

- bounded large real-data RT-kernel step performance
- Linux live evidence for:
  - Embree
  - OptiX
  - Vulkan
  - PostgreSQL
- explicit PostgreSQL setup/query split

What it is not:

- a claim of end-to-end whole-graph RT BFS execution
- a claim of end-to-end whole-graph RT triangle-count execution
- a final release gate
