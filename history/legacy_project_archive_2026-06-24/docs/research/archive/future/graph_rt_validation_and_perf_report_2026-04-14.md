# RT Graph Validation And Performance Report

Date: 2026-04-14

## Scope

This report summarizes the graph-workload validation and benchmarking phase for the RTDL `v0.6` graph path, with emphasis on the ray-tracing-kernel implementation of:

- BFS expansion
- Triangle counting / triangle probe

The work covered:

- correctness validation after an Embree triangle-count bug fix
- large-scale Linux benchmarking across RTDL backends
- Windows Embree-only confirmation
- external baseline comparisons against Gunrock and Neo4j GDS
- real public graph datasets beyond the original `wiki-Talk` slice

The main intent was to answer four questions:

1. Does the current RT graph path actually execute graph operations through RT-style traversal/intersection kernels?
2. Are the RTDL backends correct at large scale after the Embree fix?
3. How does performance scale on real public datasets?
4. How does the RTDL path compare with a specialist GPU graph library and a professional graph database?

## Executive Summary

The RT graph path is working end to end.

- The graph workloads in this version are lowered through RT-style BVH traversal/intersection kernels, not conventional graph-library kernels.
- The Embree large-batch triangle-count regression was fixed and revalidated.
- Large-scale correctness held across `cpu`, `embree`, `optix`, `vulkan`, and `postgresql` on the tested public dataset slices.
- OptiX and Vulkan consistently outperformed Embree on the RTDL graph workloads.
- Gunrock remained the fastest BFS compute baseline.
- Neo4j GDS was a strong whole-graph baseline, especially for triangle counting.

The strongest overall result is that the RTDL OptiX/Vulkan graph path is real, correct on the tested workloads, and competitive enough to be interesting on large public graph slices, even though it is not faster than specialized graph systems on every workload shape.

Important interpretation note:

- the Linux benchmark GPU used in this report is a GTX 1070, which has no RT cores
- therefore the OptiX timings here are useful non-RT-core OptiX baselines, not
  RTX-class RT-core acceleration results

## Test Environment

### Linux benchmark host

- Host: `lestat-lx1`
- OS family: Ubuntu Linux
- Python: `3.12.3`
- CUDA toolkit: `12.0.140`
- GCC/G++: `13.3.0`
- CMake: `3.28.3`
- PostgreSQL: available locally
- GPU: `NVIDIA GeForce GTX 1070`
- Driver: `580.126.09`
- VRAM: `8192 MiB`

Important hardware note:

- this GPU has no RT cores
- so the OptiX results in this report should not be interpreted as RT-core
  hardware acceleration results

### Windows validation host

- Windows desktop host used for Embree fix implementation and local Embree confirmation
- Windows reruns were intentionally limited to the local Embree path where requested

## RT Graph Path Confirmation

This version does use RT-style graph execution rather than a conventional graph-library implementation.

At the DSL layer:

- `bfs_expand_reference` uses `traverse(..., accel="bvh", mode="graph_expand")`
- `triangle_probe_reference` uses `traverse(..., accel="bvh", mode="graph_intersect")`

That means graph expansion and graph intersection are lowered into RT acceleration-structure traversal behavior, then executed by the prepared RT backends:

- Embree
- OptiX
- Vulkan RT

This is better described as "graph workloads mapped onto RT traversal/intersection kernels" than literally "plain graphics ray-triangle tests," but the essential claim holds: this version is exercising the RT kernel path for graph operations.

## Embree Triangle Regression

### Problem

Large-batch Embree `triangle_count` was returning incorrect results on the `wiki-Talk` triangle slice. The failure reproduced as:

- `py/cpu`: `10256` rows
- `embree`: `2832` rows

### Root cause

The native Embree triangle probe reused a single mark buffer for both seed endpoints. In asymmetric-degree cases, shared neighbors from one endpoint could be overwritten and lost before the intersection pass.

### Fix

The Embree path was changed to maintain separate mark buffers for `u` and `v`, preserving the smaller-side optimization while fixing the intersection logic.

### Regression coverage

A targeted regression test was added for the asymmetric-degree case that had been slipping through.

## Validation Methodology

### RTDL correctness

Correctness was established with row-count and SHA-256 row-hash comparisons across:

- CPU reference
- Embree
- OptiX
- Vulkan
- PostgreSQL baseline

For BFS, the compared row shape was:

- `(src_vertex, dst_vertex, level)`

For triangle workloads, the compared row shape was:

- `(u, v, w)`

### Workload shapes

Two graph-workload families were used:

- BFS expansion:
  - bounded frontier batch
  - typical parameters: `frontier_size=4096`, `source_id=0`
- Triangle probe:
  - bounded canonical seed-edge batch
  - typical parameters: `seed_count=8192`

These RTDL workloads are not identical to the external baselines:

- Gunrock BFS is single-source full BFS
- Neo4j GDS BFS is single-source full BFS
- Neo4j GDS triangle count is whole-graph `triangleCount`

So comparisons should be interpreted as "related baseline context" rather than strict apples-to-apples equivalence unless explicitly normalized.

### Public datasets used

- `wiki-Talk`
- `soc-LiveJournal1`
- `com-Orkut`

All are public SNAP datasets.

## Integrated Correctness Closure

### Linux integrated unit suite

The Linux integrated correctness suite with PostgreSQL enabled remained green:

- `51` tests
- status: `OK`

This suite was useful, but it did not catch the large-batch Embree triangle regression by itself. The stronger closure signal came from the row-hash large-batch validations described below.

## Dataset Results

## 1. `wiki-Talk`

### `wiki-Talk` BFS, directed, `1M` edges

Large-scale correctness matched across:

- `py`
- `cpu`
- `embree`
- `optix`
- `vulkan`
- `postgresql`

Result:

- rows: `575436`
- hash: `be440f7d3a81d47c2100dace4f70ad32eba7dd5aa35b8785c1675b2cb443b375`

Linux RTDL perf:

- Embree: `0.676s`
- OptiX: `0.478s`
- Vulkan: `0.479s`
- PostgreSQL query: `1.248s`
- PostgreSQL setup: `36.64s`

OptiX target-window tuned run on the same slice:

- OptiX: `5.368s`
- Vulkan: `5.197s`
- Embree: `7.439s`
- PostgreSQL query: `1.421s`
- PostgreSQL setup: `43.91s`

### `wiki-Talk` triangle, undirected, nonzero slice

After the Embree fix, correctness matched across:

- `py`
- `cpu`
- `embree`
- `optix`
- `vulkan`
- `postgresql`

On the large nonzero validation slice:

- rows: `10256`
- hash: `afb242ded6f36a7fe68ee3c423ab946a44f31ddf75e80947594eaeaa3176bebf`

Linux RTDL perf on the larger nonzero triangle slice:

- Embree: `2.338s`
- OptiX: `1.196s`
- Vulkan: `1.197s`
- PostgreSQL query: `1.120s`
- PostgreSQL setup: `84.42s`

### `wiki-Talk` external baselines

Gunrock BFS, source vertex `1764`:

- reachable nodes: `573110`
- GPU mean: `5.174 ms`
- wall mean: `0.478s`

Neo4j GDS BFS:

- same source vertex family, reached nodes: `573110`
- compute: `83 ms`, `53 ms`, `52 ms`
- directed projection: `969 ms`

Neo4j GDS whole-graph triangle count:

- global triangles: `2362984`
- compute: `1930 ms`, `1772 ms`, `1769 ms`
- undirected projection: `365 ms`

## 2. `soc-LiveJournal1`

### `soc-LiveJournal1` BFS, directed, `1M` edges

Correctness matched across:

- `cpu`
- `embree`
- `optix`
- `vulkan`
- `postgresql`

Result:

- rows: `171940`
- hash: `8a66e01f328909638298b73b8f0404ca52fd784f7e031749abbb07c6a5ce636d`

Linux RTDL perf:

- Embree: `0.297s`
- OptiX: `0.139s`
- Vulkan: `0.139s`
- PostgreSQL query: `0.316s`
- PostgreSQL setup: `36.61s`

### `soc-LiveJournal1` triangle, simple-undirected, `1M` canonical edges

Correctness matched across:

- `cpu`
- `embree`
- `optix`
- `vulkan`
- `postgresql`

Result:

- rows: `3856`
- hash: `7aa9f35e4aa013718053c67dfe2ab6dc4900dca6087eb7898b99c2e4c5794cf4`

Linux RTDL perf:

- Embree: `1.388s`
- OptiX: `0.0885s`
- Vulkan: `0.0906s`
- PostgreSQL query: `26.58s`
- PostgreSQL setup: `76.15s`

### `soc-LiveJournal1` BFS, directed, `5M` edges

Correctness matched across:

- `cpu`
- `embree`
- `optix`
- `vulkan`
- `postgresql`

Result:

- rows: `171940`
- hash: `8a66e01f328909638298b73b8f0404ca52fd784f7e031749abbb07c6a5ce636d`

Interpretation:

- the bounded frontier still sat in the same early region of the graph
- increasing tail edges did not materially change this one-step BFS workload

Linux RTDL perf:

- Embree: `1.019s`
- OptiX: `0.151s`
- Vulkan: `0.152s`
- PostgreSQL query: `0.329s`
- PostgreSQL setup: `188.71s`

### `soc-LiveJournal1` triangle, simple-undirected, `5M` canonical edges

Correctness matched across:

- `cpu`
- `embree`
- `optix`
- `vulkan`
- `postgresql`

Result:

- rows: `34110`
- hash: `ca4fc4f36b453d0f874442e4790772f16274f45b185816386ea8826e0f32158e`

Linux RTDL perf:

- Embree: `3.518s`
- OptiX: `0.555s`
- Vulkan: `0.552s`
- PostgreSQL query: `100.87s`
- PostgreSQL setup: `374.27s`

Interpretation:

- the larger triangle-heavy slice changed the workload substantially
- bounded triangle output grew from `3856` to `34110`
- PostgreSQL degraded sharply

### `soc-LiveJournal1` external baselines

Gunrock BFS, `1M` directed slice, source `10009`:

- reachable nodes: `481590`
- GPU mean: `6.33 ms`
- wall mean: `0.538s`

Neo4j GDS BFS, `1M` directed slice:

- same source vertex family
- reached nodes: `481590`
- compute: `74 ms`, `52 ms`, `51 ms`
- projection: `1013 ms`

Neo4j GDS whole-graph triangle count, `1M` simple-undirected slice:

- global triangles: `368037`
- compute: `586 ms`, `522 ms`, `472 ms`
- projection: `1276 ms`

Gunrock BFS, `5M` directed slice, source `10009`:

- reachable nodes: `1318426`
- GPU mean: `9.56 ms`
- wall mean: `1.632s`

Neo4j GDS BFS, `5M` directed slice:

- same source vertex family
- reached nodes: `1318426`
- compute: `201 ms`, `189 ms`, `154 ms`
- directed projection: `1592 ms`

Neo4j GDS whole-graph triangle count, `5M` simple-undirected slice:

- global triangles: `5820077`
- compute: `2064 ms`, `1941 ms`, `1947 ms`
- undirected projection: `828 ms`

## 3. `com-Orkut`

### `com-Orkut` BFS, directed, `1M` edges

Correctness matched across:

- `cpu`
- `embree`
- `optix`
- `vulkan`
- `postgresql`

Result:

- rows: `230634`
- hash: `1b904d459941af9b717b0f18613a694c5f5633fffc36a4e9953786238db28c60`

Linux RTDL perf:

- Embree: `0.388s`
- OptiX: `0.195s`
- Vulkan: `0.197s`
- PostgreSQL query: `1.057s`
- PostgreSQL setup: `42.22s`

### `com-Orkut` triangle, simple-undirected, `1M` canonical edges

Correctness matched across:

- `cpu`
- `embree`
- `optix`
- `vulkan`
- `postgresql`

Result:

- rows: `94183`
- hash: `f327a143d2a860d371c58a66466407f3b544de820420190d3aa4b2abfd55fd63`

Linux RTDL perf:

- Embree: `2.243s`
- OptiX: `1.831s`
- Vulkan: `1.850s`
- PostgreSQL query: `1.005s`
- PostgreSQL setup: `81.71s`

Interpretation:

- `com-Orkut` is already much heavier than `LiveJournal` on bounded triangle output at only `1M` canonical edges

### `com-Orkut` BFS, directed, `5M` edges

Correctness matched across:

- `cpu`
- `embree`
- `optix`
- `vulkan`
- `postgresql`

Result:

- rows: `233056`
- hash: `189c495665903ef8a63c71dc6cdb2b546f9a3a047f4659ed92d30e58f72e3333`

Linux RTDL perf:

- Embree: `1.077s`
- OptiX: `0.202s`
- Vulkan: `0.202s`
- PostgreSQL query: `0.575s`
- PostgreSQL setup: `211.80s`

### `com-Orkut` triangle, simple-undirected, `5M` canonical edges

Correctness matched across:

- `cpu`
- `embree`
- `optix`
- `vulkan`
- `postgresql`

Result:

- rows: `94396`
- hash: `9f489eabc954cc450b51e9c71bf1bcdb668eec71738173730d790626db6f3ba9`

Linux RTDL perf:

- Embree: `3.595s`
- OptiX: `1.869s`
- Vulkan: `1.872s`
- PostgreSQL query: `0.976s`
- PostgreSQL setup: `404.16s`

Interpretation:

- OptiX and Vulkan land naturally in the useful `~1.87s` band on this heavier triangle workload

### `com-Orkut` external baselines

Gunrock BFS, `1M` directed slice, source `8160`:

- reachable nodes: `84997`
- GPU mean: `4.69 ms`
- wall mean: `0.452s`

Neo4j GDS BFS, `1M` directed slice:

- same source vertex family
- reached nodes: `84997`
- compute: `34 ms`, `19 ms`, `16 ms`
- directed projection: `1018 ms`

Neo4j GDS whole-graph triangle count, `1M` simple-undirected slice:

- global triangles: `3232240`
- compute: `514 ms`, `440 ms`, `432 ms`
- undirected projection: `315 ms`

Gunrock BFS, `5M` directed slice, source `8123`:

- reachable nodes: `873200`
- GPU mean: `9.49 ms`
- wall mean: `1.542s`

Neo4j GDS BFS, `5M` directed slice:

- same source vertex family
- reached nodes: `873200`
- compute: `193 ms`, `98 ms`, `88 ms`
- directed projection: `1441 ms`

Neo4j GDS whole-graph triangle count, `5M` simple-undirected slice:

- global triangles: `15890879`
- compute: `2189 ms`, `1762 ms`, `1698 ms`
- undirected projection: `686 ms`

## Windows Embree Confirmation

Windows was used for the Embree fix and local confirmation, not for the full Linux-scale external-baseline matrix.

### Windows `wiki-Talk` BFS, Embree only

- `py/cpu/embree` matched
- rows: `575436`
- hash: `be440f7d3a81d47c2100dace4f70ad32eba7dd5aa35b8785c1675b2cb443b375`

Perf:

- prepare: `0.779s`
- execute: `1.257s`

### Windows `wiki-Talk` triangle, Embree only

- `py/cpu/embree` matched after the fix
- rows: `10256`
- hash: `afb242ded6f36a7fe68ee3c423ab946a44f31ddf75e80947594eaeaa3176bebf`

Perf:

- prepare: `0.480s`
- execute: `1.372s`

## External Baseline Summary

### Gunrock

Status:

- usable and trustworthy for BFS on this Linux host
- not trustworthy for triangle count on this host/build

Observed issue:

- Gunrock `tc` returned zero even for a tiny hand-built triangle
- source inspection suggested a likely frontier-initialization problem in the current TC example path on this setup

Decision:

- Gunrock was kept as a BFS-only external GPU baseline
- Gunrock triangle count was excluded

### Neo4j GDS

Status:

- usable and stable on Linux after local user-space setup
- strong baseline for:
  - single-source BFS
  - whole-graph triangle count

Practical notes:

- required a local Java 21 runtime
- used local Neo4j `5.26.24`
- used GDS plugin `2.13.4`
- imports were done with offline `neo4j-admin database import full`

## Interpretation

### Correctness

The strongest result of this phase is correctness closure across the RTDL backends after the Embree fix.

On the tested large public slices:

- `cpu`
- `embree`
- `optix`
- `vulkan`
- `postgresql`

all matched on the validated row-hash checks for BFS and triangle workloads.

### RTDL backend behavior

OptiX and Vulkan were consistently the strongest RTDL backends on the graph workloads.

Embree:

- remained correct after the fix
- was usually slower than OptiX and Vulkan
- sometimes landed in the same rough one-off wall-clock ballpark as Neo4j projection plus compute, but that does not mean the workloads are directly comparable

### BFS positioning

For BFS, Gunrock remained the fastest compute baseline.

Typical pattern:

- Gunrock BFS compute: a few milliseconds
- Neo4j GDS BFS compute: tens to low hundreds of milliseconds
- RTDL OptiX BFS: usually a few tenths of a second on the bounded frontier workload

So RTDL BFS works and can be reasonably fast, but it is not a specialized BFS engine.

### Triangle positioning

For triangle-heavy graphs:

- RTDL bounded triangle probes on OptiX/Vulkan became quite interesting
- Neo4j whole-graph triangle count remained a strong professional baseline
- PostgreSQL ranged from acceptable to extremely slow depending on dataset and workload shape

The most useful nuance is workload shape:

- RTDL triangle timings here are bounded seed-edge probes
- Neo4j triangle timings are whole-graph counts

That means the results are informative, but not a strict apples-to-apples winner table.

### Dataset progression

`soc-LiveJournal1` was a good scaling bridge:

- realistic social graph
- meaningful nonzero triangle workloads
- clean `1M` to `5M` scaling story

`com-Orkut` was a stronger triangle stress case:

- heavier triangle structure
- larger bounded triangle outputs
- more demanding for RTDL triangle workloads

## Main Conclusions

1. The current version does use the RT graph path. Graph workloads are lowered into RT-style traversal/intersection kernels and executed by Embree, OptiX, and Vulkan.
2. The Embree triangle-count regression is fixed. Large-batch correctness now matches the other backends on the validated public slices.
3. RTDL OptiX and Vulkan are the most important RTDL graph backends going forward. They consistently outperformed Embree on the tested graph workloads.
4. Gunrock is the right external BFS baseline on this host. It remained the fastest BFS compute engine in the comparison set.
5. Neo4j GDS is the right professional graph-system baseline in this environment. It provided stable, credible BFS and triangle-count baselines.
6. The RTDL path is not universally faster than specialized graph systems, but it is fast enough on real public graphs to be technically meaningful, especially given that it is executing the RT-kernel graph path rather than a purpose-built graph engine.

## Recommended Next Phase

The current benchmarking phase is complete enough to stop testing and move to packaging.

Best next steps:

1. turn this report into a shorter publishable summary with 2-3 headline tables
2. normalize one apples-to-apples comparison, especially RTDL vs Neo4j on a closer triangle workload shape
3. preserve the current results as the baseline benchmark package for the RT graph line
