# Goal2588 RT-Graph Triangle-Counting Paper/Code Intake

Date: 2026-05-24

Status: paper/code intake plus local preprocessing oracle complete. Goal2589
adds pod evidence for deterministic same-input correctness and synthetic timing
rows. This report defines the benchmark target and reproduction contract. It
does not authorize a paper reproduction claim or any performance wording.

## Sources

| Source | Value |
| --- | --- |
| Paper | "A Case Study for Ray Tracing Cores: Performance Insights with Breadth-First Search and Triangle Counting in Graphs" |
| Venue | SIGMETRICS 2025 |
| PDF | `https://rubaolee.github.io/paper_pdfs/2025-rtgraph.pdf` |
| Code | `https://github.com/rubaolee/RT-Graph` |
| Local code snapshot | `scratch/external/RT-Graph` |
| Studied commit | `e7675f2e0cd06077c5050da13f455cc0c2320208` |
| Pod evidence | `docs/reports/goal2589_rt_graph_triangle_counting_pod_evidence_2026-05-24.md` |

## Benchmark Boundary

This benchmark should reproduce only the triangle-counting portion of RT-Graph.
BFS remains outside this benchmark, even though the RT-Graph paper also studies
BFS. The benchmark contract is:

```text
input graph -> RT-Graph-style preprocessing -> triangle count
```

The output contract is either exact triangle witness rows or a compact exact
triangle summary. Any RTDL performance comparison must use the same graph input
and the same directed/preprocessed triangle-counting semantics.

## Paper Contract

The paper treats triangle counting as set intersection over neighboring lists.
To avoid redundant counting, the graph is converted into a loop-free directed
graph, then common neighbors are counted.

RT-Graph defines two RT triangle-counting mappings:

| Method | Primitive side | Ray side | Main tradeoff |
| --- | --- | --- | --- |
| RT-1A2 | 2-hop relations | 1-hop relations | More balanced and fast on smaller datasets, but high memory footprint because 2-hop relations can be huge. |
| RT-2A1 | 1-hop relations | compacted 2-hop relations | Lower primitive memory, but high ray miss ratio and slower large-graph behavior. |

The paper also defines binary-search baselines with the same task decomposition:

| Baseline | Matching RT method | Meaning |
| --- | --- | --- |
| BS-1A2 | RT-1A2 | Search 1-hop neighbors among 2-hop neighbors using CUDA binary search, not RT traversal. |
| BS-2A1 | RT-2A1 | Search compacted 2-hop relations among 1-hop neighbors using CUDA binary search, not RT traversal. |

The key paper insight for our benchmark is not simply "RT cores are faster for
triangle counting." The paper reports that RT methods can look strong on small
datasets, but the CUDA binary-search versions of the same decompositions beat
the RT versions in the reported TC study. That makes `bs_tc` an essential
baseline, not an optional fallback.

## Authors-Code Layout

Relevant files in `scratch/external/RT-Graph/tc/`:

| Path | Role |
| --- | --- |
| `rt_tc/main.cpp` | Reads a binary edge file, preprocesses the graph, converts to CSR, builds RT structures, counts triangles. |
| `rt_tc/rt_tc.cpp` | Builds triangle primitives, computes ray origins/values, launches OptiX, reduces counts. |
| `rt_tc/device_programs.cu` | OptiX raygen and any-hit programs for RT-1A2 and RT-2A1. |
| `rt_tc/include/config.h` | Compile-time method selector. Current snapshot defaults to `RTTC_METHOD 1`, meaning RT-2A1. |
| `bs_tc/bs_tc.cu` | CUDA binary-search baselines mirroring the RT decompositions. |
| `bs_tc/main.cu` | Entry point for `bs_tc`. |
| `graph/graph.cpp` | Binary edge reader, degree-oriented preprocessing, duplicate/self-loop removal, CSR conversion. |
| `script/run_rt_tc.sh` | Runs `rt_tc` over SNAP-style datasets. |
| `script/run_bs_tc.sh` | Runs `bs_tc` over SNAP-style datasets. |

The authors build expects CUDA 11.8, OptiX 7.5, GCC 11, and
`OptiX_INSTALL_DIR` pointing at the OptiX include directory.

## Authors-Code Semantics

`Graph::ReadBinaryEdges` reads a binary edge-list file of int32 `(src, dst)`
pairs and compacts arbitrary node IDs into a dense ID range.

`Graph::TCPreprocessing` computes degrees, orients each undirected edge from the
lower-priority endpoint to the higher-priority endpoint using degree and ID,
removes low-degree vertices, sorts edges, and removes duplicate/self-loop edges.
`Graph::ConvertToCSR` then builds the directed CSR adjacency used by both RT and
BS triangle counters.

For RT-2A1, the current default in `config.h`, the code:

- builds one OptiX triangle primitive per directed 1-hop edge;
- enumerates and sorts 2-hop neighbors per source node on the host;
- compacts duplicate `(source, two_hop_neighbor)` rays with an add-value count;
- launches OptiX rays and atomically adds the compacted count on any hit.

For BS-2A1, the code performs the same compacted 2-hop preprocessing, then uses
CUDA binary search over the source node adjacency list instead of OptiX BVH
traversal.

For RT-1A2/BS-1A2, the compile-time selector changes the decomposition so that
1-hop relations probe 2-hop relations.

## RTDL Mapping

Our current RTDL triangle-counting front door is:

```text
examples/v2_0/research_benchmarks/triangle_counting/
```

It currently provides a small deterministic correctness contract over the
existing graph triangle-count feature path. Goal2588 also adds a benchmark-owned
Python RT-Graph preprocessing/oracle path for small fixtures and edge-list
files, plus an id-ascending relabeling adapter that lets the current RTDL CPU
triangle matcher check the same triangle count locally. It does not yet
reproduce large SNAP datasets or authors-code performance rows.

The important local design finding is that current RTDL `triangle_match`
assumes id-ascending witnesses (`u < v < w`), while RT-Graph orients edges by
degree and ID. Those are not the same contract on general graphs. Exact
RT-Graph reproduction therefore needs an orientation-aware graph triangle
contract or a validated relabeling adapter before backend timing is meaningful.
The local adapter sorts surviving vertices by the same orientation key
`(degree, compacted_id)`, so all directed RT-Graph edges become ascending for
RTDL's existing triangle matcher without changing the triangle count.

The first paper-shaped RTDL runtime path is now `rt_graph_2a1_generic_rt`.
It follows the RT-2A1 decomposition from the paper/authors code:

- directed 1-hop edges become generic `Triangle3D` primitives;
- compacted 2-hop relations become generic `Ray3D` probes;
- the 2-hop multiplicity is kept as a Python-side add-value weight;
- RTDL runs the app-name-free generic `ANY_HIT` ray/triangle primitive and
  reduces hit weights into a triangle count.

This is intentionally not a new graph-specific native engine path. It is a
Python+RTDL mapping of the paper's OptiX geometry contract onto the existing
generic ray/triangle primitive.

The second paper-shaped RTDL runtime path is now `rt_graph_1a2_generic_rt`.
It follows the RT-1A2 decomposition from the paper/authors code:

- compacted 2-hop relations become generic `Triangle3D` primitives;
- directed 1-hop relations become generic `Ray3D` probes;
- RTDL uses a generic ray/triangle `HIT_COUNT` contract rather than `ANY_HIT`,
  because one 1-hop probe may intersect multiple 2-hop primitives.

This is also a Python+RTDL mapping of the paper geometry contract. It does not
add graph- or triangle-count-specific semantics to the native engine.

To become an RT-Graph reproduction benchmark, RTDL needs:

1. Authors-code build and run scripts for `bs_tc` and `rt_tc` on a CUDA/OptiX
   pod, including the compile-time method selector for both 1A2 and 2A1.
2. RTDL native OptiX rows for `rt_graph_2a1_generic_rt` and
   `rt_graph_1a2_generic_rt`.
3. Same-input result comparison before timing is trusted.
4. Separate timing rows for preprocessing, build/index time, traversal/kernel
   time, and total time, because the paper distinguishes these costs.

## Claim Boundary

Authorized now:

- Triangle counting is the graph benchmark target.
- RT-Graph/SIGMETRICS 2025 is the paper/code target for this benchmark.
- The authors code and paper contract have been studied.
- A benchmark-owned Python oracle now implements RT-Graph-style dense ID
  compaction, degree/ID edge orientation, low-degree pruning, duplicate/self-loop
  cleanup, CSR construction, and compacted RT-2A1 two-hop rays for fixtures and
  edge-list files.
- A local RTDL CPU adapter check now confirms the same count through the current
  id-ascending triangle matcher after validated relabeling.
- A local RTDL CPU generic ray/triangle check now confirms the RT-2A1
  primitive/ray mapping preserves the oracle count on fixtures.
- A local RTDL CPU generic ray/triangle check now confirms the RT-1A2
  primitive/ray mapping preserves the oracle count on fixtures through per-ray
  hit counts.
- Goal2589 pod evidence confirms authors `bs_tc`, authors `rt_tc`, and RTDL
  OptiX generic 1A2/2A1 mappings return identical counts on deterministic
  same-input fixtures and K4-clique synthetic workloads.
- `bs_tc` must be treated as a first-class baseline because the paper reports
  CUDA binary-search variants beating RT variants under the same decomposition.

Not authorized now:

- Claiming RTDL reproduces RT-Graph authors-code performance.
- Claiming the current CPU `rt_graph_2a1_generic_rt` or
  `rt_graph_1a2_generic_rt` checks are RT-core results.
- Claiming RTDL beats RT-Graph, `bs_tc`, or `rt_tc`.
- Claiming RTDL has a true RT-core triangle-counting speedup.
- Claiming RTDL whole-app performance is competitive with authors code.
  Goal2589 shows the new generic summary traversal is fast, but Python graph
  preprocessing and lowering still dominate whole-app time.
- Claiming BFS as part of this benchmark.
- Adding triangle-count app semantics into the native engine.

## Next Goals

1. Keep the new generic prepared ray/triangle summary mode app-agnostic and
   covered by same-contract tests.
2. Optimize partner/lowering support so RTDL can avoid Python object creation
   and repeated host packing on large graph-derived ray/triangle batches.
3. If external SNAP datasets are needed, run authors `bs_tc`/`rt_tc` and RTDL
   on the same downloaded files with the same preprocessing contract.
4. Seek external review before any performance wording.
