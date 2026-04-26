# RT Graph Benchmark Handoff

Date: 2026-04-14
Prepared for: Mac Codex continuation

## What this work established

This benchmark phase validated the RTDL `v0.6` graph path as a real RT-kernel graph execution path and exercised it against public graph datasets plus external baselines.

Main conclusions:

- The current graph workloads are lowered into RT-style traversal/intersection kernels.
- The Embree large-batch triangle-count bug was fixed and revalidated.
- Large-scale correctness matched across `cpu`, `embree`, `optix`, `vulkan`, and `postgresql` on the validated slices.
- OptiX and Vulkan were consistently the strongest RTDL graph backends.
- Gunrock was the strongest BFS compute baseline.
- Neo4j GDS was a strong professional baseline for BFS and whole-graph triangle count.

## Key local files

### Main report

- `C:\Users\lestat\Desktop\rtdl_v0_6_rt_check_win_desktop\docs\graph_rt_validation_and_perf_report_2026-04-14.md`

### Embree bug fix

- `C:\Users\lestat\Desktop\rtdl_v0_6_rt_check_win_desktop\src\native\embree\rtdl_embree_api.cpp`

### Embree regression test

- `C:\Users\lestat\Desktop\rtdl_v0_6_rt_check_win_desktop\tests\goal396_v0_6_rt_graph_triangle_embree_test.py`

### Added public dataset specs

- `C:\Users\lestat\Desktop\rtdl_v0_6_rt_check_win_desktop\src\rtdsl\graph_datasets.py`

## Important code facts

The graph RT path is defined at the DSL level in:

- `src/rtdsl/graph_perf.py`

Important kernels:

- `bfs_expand_reference`
  - uses `traverse(..., accel="bvh", mode="graph_expand")`
- `triangle_probe_reference`
  - uses `traverse(..., accel="bvh", mode="graph_intersect")`

This is the main evidence that graph work is being lowered into RT-style traversal/intersection kernels rather than conventional graph-library kernels.

## Embree bug summary

Bug:

- large-batch Embree `triangle_count` was wrong on asymmetric-degree seed cases

Root cause:

- one mark buffer was reused for both seed endpoints

Fix:

- separate mark buffers for `u` and `v`

Regression closure:

- targeted regression test added
- Linux and Windows large-batch reruns matched after sync

## Test environment used

### Linux host

- alias: `lestat-lx1`
- GPU: `NVIDIA GeForce GTX 1070`
- driver: `580.126.09`
- CUDA: `12.0.140`
- Python: `3.12.3`
- PostgreSQL: local and working

Important note:

- GTX 1070 has no RT cores, so current OptiX results are a useful non-RT-core baseline

### External baselines used on Linux

- Gunrock:
  - usable for BFS
  - not trustworthy for triangle count on this host/build
- Neo4j GDS:
  - usable for BFS
  - usable for whole-graph triangle count
  - brought up locally with user-space Java 21 and Neo4j `5.26.24` plus GDS `2.13.4`

## Public datasets covered

- `wiki-Talk`
- `soc-LiveJournal1`
- `com-Orkut`

## Best benchmark anchors

### `soc-LiveJournal1`, 5M edges

RTDL BFS, directed:

- correctness rows: `171940`
- hash: `8a66e01f328909638298b73b8f0404ca52fd784f7e031749abbb07c6a5ce636d`
- Embree: `1.019s`
- OptiX: `0.151s`
- Vulkan: `0.152s`
- PostgreSQL query: `0.329s`

RTDL triangle probe, 5M canonical undirected:

- rows: `34110`
- hash: `ca4fc4f36b453d0f874442e4790772f16274f45b185816386ea8826e0f32158e`
- Embree: `3.518s`
- OptiX: `0.555s`
- Vulkan: `0.552s`
- PostgreSQL query: `100.87s`

Gunrock BFS:

- source vertex: `10009`
- reachable nodes: `1318426`
- GPU mean: `9.56 ms`

Neo4j GDS BFS:

- reached nodes: `1318426`
- compute: `201 ms`, `189 ms`, `154 ms`

Neo4j GDS triangle count:

- global triangles: `5820077`
- compute: `2064 ms`, `1941 ms`, `1947 ms`

### `com-Orkut`, 5M edges

RTDL BFS, directed:

- rows: `233056`
- hash: `189c495665903ef8a63c71dc6cdb2b546f9a3a047f4659ed92d30e58f72e3333`
- Embree: `1.077s`
- OptiX: `0.202s`
- Vulkan: `0.202s`
- PostgreSQL query: `0.575s`

RTDL triangle probe, 5M canonical undirected:

- rows: `94396`
- hash: `9f489eabc954cc450b51e9c71bf1bcdb668eec71738173730d790626db6f3ba9`
- Embree: `3.595s`
- OptiX: `1.869s`
- Vulkan: `1.872s`
- PostgreSQL query: `0.976s`

Gunrock BFS:

- source vertex: `8123`
- reachable nodes: `873200`
- GPU mean: `9.49 ms`

Neo4j GDS BFS:

- reached nodes: `873200`
- compute: `193 ms`, `98 ms`, `88 ms`

Neo4j GDS triangle count:

- global triangles: `15890879`
- compute: `2189 ms`, `1762 ms`, `1698 ms`

## External baseline interpretation

### Gunrock

Use Gunrock only as a BFS baseline from this work.

Do not trust Gunrock triangle count on this machine/build without further debugging. It returned zero even for a tiny hand-built triangle and source inspection suggested a likely setup/algorithm issue in the TC path.

### Neo4j

Neo4j is a good baseline, but remember:

- Neo4j BFS is single-source full BFS
- Neo4j triangle count is whole-graph triangle counting
- RTDL BFS/triangle timings here are bounded workloads

So comparisons are informative but not perfect apples-to-apples.

## Recommended next steps for Mac Codex

Best next options:

1. Produce a shorter executive summary from the full report with a few compact tables.
2. Normalize one closer apples-to-apples comparison:
   - RTDL vs Neo4j on a nearer triangle workload shape, or
   - RTDL vs Gunrock on a nearer BFS workload shape.
3. Plan an RTX rerun:
   - the Linux host used here has no RT cores
   - an RTX-class rerun would test whether OptiX gains materially from real RT hardware on these graph kernels.
4. If more benchmarking is desired, only then consider another dataset such as `Friendster`.

## Suggested quick-start instruction for Mac Codex

Start by reading:

- `C:\Users\lestat\Desktop\rtdl_v0_6_rt_check_win_desktop\docs\graph_rt_validation_and_perf_report_2026-04-14.md`

Then inspect:

- `C:\Users\lestat\Desktop\rtdl_v0_6_rt_check_win_desktop\src\rtdsl\graph_perf.py`
- `C:\Users\lestat\Desktop\rtdl_v0_6_rt_check_win_desktop\src\native\embree\rtdl_embree_api.cpp`
- `C:\Users\lestat\Desktop\rtdl_v0_6_rt_check_win_desktop\tests\goal396_v0_6_rt_graph_triangle_embree_test.py`

## Bottom line

This phase is complete enough to treat as a finished benchmark package.

The most important preserved message is:

- the RT graph path is real
- the backends were validated at scale
- OptiX and Vulkan are the main RTDL graph backends to carry forward
- Gunrock and Neo4j provide credible external context
