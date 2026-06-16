# Triangle Counting Benchmark

This benchmark promotes only the graph triangle-counting slice into the
research-benchmark tree.

The target paper/code for this benchmark is RT-Graph from SIGMETRICS 2025:
"A Case Study for Ray Tracing Cores: Performance Insights with Breadth-First
Search and Triangle Counting in Graphs." The authors code is
`https://github.com/rubaolee/RT-Graph`; the local intake report records the
studied commit and the triangle-counting reproduction plan.

The broader graph analytics app remains a learner/demo app under
`examples/current/apps/analytics/rtdl_graph_analytics_app.py`. Its BFS and
visibility-edge modes are useful examples, but they are intentionally not part
of this benchmark. Keeping the benchmark to one operation makes correctness,
baselines, and claim boundaries easier to review.

## Contract

| Contract | RTDL role | Boundary |
| --- | --- | --- |
| RT-Graph-style triangle counting | Triangle witness rows or compact triangle summary over a graph fixture | not BFS, shortest path, visibility edges, graph database, or distributed graph analytics |

The RT-Graph triangle-counting contract uses a loop-free directed graph after
degree/order preprocessing. It counts common neighbors through set-intersection
work: RT-Graph implements RT-1A2 and RT-2A1 by mapping 1-hop or 2-hop relations
to OptiX triangle primitives and rays, plus `bs_tc` CUDA binary-search baselines
with the same task decomposition.

## Commands

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode scope
PYTHONPATH=src:. python examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode run --backend cpu_python_reference --copies 2 --output-mode summary
PYTHONPATH=src:. python examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode rt_graph_contract --fixture degree_oriented_two_triangles
PYTHONPATH=src:. python examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode rt_graph_rtdl_adapter --fixture degree_oriented_two_triangles --backend cpu_python_reference
PYTHONPATH=src:. python examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode rt_graph_2a1_generic_rt --fixture degree_oriented_two_triangles --backend cpu
PYTHONPATH=src:. python examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode rt_graph_1a2_generic_rt --fixture degree_oriented_two_triangles --backend cpu
PYTHONPATH=src:. python examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode rt_graph_2a1_generic_rt --edge-file build/goal2588_rt_graph/k4_cliques_10000.edge --edge-format binary --backend optix --detail summary
PYTHONPATH=src:. python examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode rt_graph_2a1_generic_rt --edge-file build/goal2588_rt_graph/k4_cliques_10000.edge --edge-format binary --backend optix --detail summary --partner cupy
PYTHONPATH=src:. python examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode rt_graph_2a1_segmented_generic_rt --edge-file build/goal2588_rt_graph/k4_cliques_10000.edge --edge-format binary --backend optix --detail summary --partner cupy --segment-max-two-hop-rows 1000000
PYTHONPATH=src:. python examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode rt_graph_1a2_generic_rt --edge-file build/goal2588_rt_graph/k4_cliques_10000.edge --edge-format binary --backend optix --detail summary --partner cupy
PYTHONPATH=src:. python examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode run --backend optix --output-mode summary --optix-graph-mode native --copies 128 --repeat 2 --warmup 1
PYTHONPATH=src:. python examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py --mode command_plan
```

## Current Evidence Boundary

Current evidence includes RT-Graph authors-code, RAPIDS cuGraph, and RTDL
same-input runs on the paper TC datasets listed in the RT-Graph README. The
stronger paper-dataset matrix supersedes the earlier synthetic K4-only
closeout.

The current RTDL graph triangle feature assumes id-ascending triangle witnesses.
RT-Graph instead orients edges by degree and ID. That means exact RT-Graph
reproduction needs either an orientation-aware graph contract or a validated
relabeling adapter. This benchmark now includes the relabeling adapter for local
CPU correctness; native/backend timing still needs a same-contract gate.

The first paper-shaped RTDL path is `rt_graph_2a1_generic_rt`: it maps RT-2A1
directed 1-hop edges to generic `Triangle3D` primitives and compacted 2-hop
relations to generic `Ray3D` probes with add-value weights. This follows the
paper/authors-code geometry shape while staying inside app-name-free RTDL
ray/triangle primitives. Current local evidence is CPU correctness only.

The second paper-shaped path is `rt_graph_1a2_generic_rt`: it maps RT-1A2
compacted 2-hop relations to generic `Triangle3D` primitives and directed
1-hop edges to generic `Ray3D` probes. This path needs per-ray hit counts,
because one 1-hop probe can intersect multiple 2-hop primitives. Current local
evidence is CPU correctness only.

Goal2589 adds pod evidence that both generic RTDL mappings match authors
`bs_tc`/`rt_tc` counts on deterministic same-input fixtures and synthetic K4
workloads. The first row-returning OptiX path was performance-negative, so the
runtime now includes app-agnostic 3-D ray/triangle scalar summary paths for
weighted any-hit and hit-count sums. Those paths remove row materialization from
the benchmark; remaining whole-app cost is dominated by Python graph
preprocessing and lowering.

The optional `--partner cupy` path moves app-owned RT-Graph summary-contract
construction to CuPy for binary edge-list inputs. This is the intended
Python+partner+RTDL split: graph preprocessing remains outside the native RTDL
engine, while the engine still sees generic rays, triangles, weights, and scalar
summary primitives.

Goal4444 refreshes the optional `--partner numba` path. The old M27 Numba row
used `cpu_contract_then_numba_device_upload`, which made the Numba comparison
mostly a Python contract-construction timing. The current Numba path reads the
binary edge list directly, builds the compact CSR/two-hop summary with
vectorized array operations, and uploads Numba CUDA device columns. On the
200,000-K4-clique synthetic row this cuts Numba total time by `19.96x-23.07x`
versus M27 while keeping the same OptiX summary primitive and oracle signature.
CuPy remains the current large-scale performance route; the Numba row is now a
fairer no-C++ Python-source reference, not a broad paper-speedup claim.

For the synthetic app-summary route, prefer passing `--optix-graph-mode native`
when you want the current native summary timing path. The default `auto` mode is
conservative and may report the host-indexed fallback. Even with explicit
`native`, the current app still reports `rt_core_accelerated=false` and
`triangle_count_rt_core_claim_authorized=false`; use it as internal route
evidence, not as a public RT-core triangle-count claim.

Goal2593 paper-dataset evidence shows:

- RTDL 2A1 is correct on `com-dblp`, `com-youtube`, `wiki-Talk`, and
  `cit-Patents`.
- RTDL 1A2 is correct on `com-dblp` and `com-youtube`, but runs out of GPU
  memory on `wiki-Talk` and `cit-Patents`.
- Both RTDL paths run out of memory on `com-lj`, `soc-LiveJournal1`, and
  `com-orkut` because the current CuPy lowering globally materializes large
  two-hop relations.
- cuGraph is currently the best end-to-end baseline on the real paper datasets
  that completed.
- Authors' `rt_tc` and `bs_tc` remain important paper-code baselines. Their
  pure count kernels are very fast, but their full pipelines are dominated by
  preprocessing and graph-to-RT/GPU construction on this pod.

Therefore the app is closed with a documented limitation: it is a bounded
RT-Graph triangle-counting benchmark, not a full paper-system reproduction and
not a paper-dataset speedup claim. The next RTDL target is segmented/streamed
RT-Graph lowering that preserves the generic engine contract while avoiding
global two-hop materialization.

Goal4461 adds the first explicit segmented RT-2A1 route for that target. It
builds a CuPy directed CSR, estimates two-hop row counts, prepares one generic
OptiX 3-D triangle scene, then lowers duplicate two-hop rays in bounded
segments with unit weights. On the 200,000-K4-clique pod row it matched the
generated 800,000-triangle oracle with 1,200,000 directed edge triangles,
800,000 duplicate two-hop rays, four segments, and
`two_hop_summary_materialized=false`. This is internal route evidence, not a
triangle-counting RT-core speedup claim.

Goal4462 applies that route to the real `com-lj` paper dataset that previously
failed both RTDL 2A1 and 1A2 with a 7,429,851,776-byte CUDA allocation failure.
The segmented route matched the expected 177,820,130 triangles with 33,895,259
directed edge triangles, 928,731,472 duplicate two-hop rays, 186 segments, and
`global_two_hop_summary_materialized=false`. This is a correctness and
scalability milestone, not refreshed public speedup wording.

Primary paper-dataset report:

- `docs/reports/goal2593_rt_graph_paper_dataset_evaluation_2026-05-24.md`
- `docs/reports/goal4461_v3_0_m65_triangle_segmented_2a1_2026-06-16.md`
- `docs/reports/goal4462_v3_0_m66_triangle_segmented_com_lj_2026-06-16.md`

## Engine Boundary

No graph-specific native ABI is added by this benchmark wrapper. Graph
semantics remain in Python app code. The engine-facing contract stays generic:
graph rows, compact row summaries, and app-agnostic row-summary continuation.

BFS, visibility edges, shortest path, and whole graph analytics stay in learner
or demo examples unless a later goal promotes one of them as its own single-
contract benchmark.
