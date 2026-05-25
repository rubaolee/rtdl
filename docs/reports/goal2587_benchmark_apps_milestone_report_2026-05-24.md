# Goal2587 Benchmark Apps Milestone Report

Date: 2026-05-24

Status: internal milestone report. This is a portfolio summary, not a new public
speedup claim and not a release/tag operation.

## Executive Summary

RTDL now has a real benchmark-app portfolio rather than isolated demos. The
benchmarks are used as reconstruction instruments: each app is allowed to cover
only the slice needed to expose missing language/runtime structure, as long as
the claim boundary is explicit.

Current formal research benchmark apps in the working tree:

| App | Current milestone state |
| --- | --- |
| Hausdorff / X-HD-style | Consensus-closed as an exact 2-D projected-point reconstruction app. |
| Spatial RayJoin-style | Consensus-closed as scoped PIP/LSI/overlay-seed spatial benchmark. |
| RT-DBSCAN-style | Consensus-closed as generic fixed-radius graph/component benchmark. |
| Robot collision | Consensus-closed as sampled static-scene feasibility-screening benchmark. |
| RayDB-style | Consensus-closed as deterministic columnar grouped-aggregate benchmark. |
| Barnes-Hut / RT-BarnesHut-style | Closed as hierarchical aggregate-frontier and partner-resident force diagnostic benchmark. |
| LibRTS-style spatial index | Internally publishable with 3-AI consensus for generic AABB-index count-only paths. |
| RTNN neighbor search | Formal front door added for prepared fixed-radius ranked-summary evidence and RTNN diagnostics. |
| Triangle counting | Closed as the only graph research benchmark slice with an accepted limitation: RT-Graph/SIGMETRICS 2025 paper datasets were evaluated, cuGraph is the strongest current end-to-end baseline, RTDL is correct on smaller paper datasets, and largest-dataset scalability is deferred to segmented/streamed lowering. |
| GPU-RMQ | Candidate benchmark front door added for exact range-minimum-query rows, hierarchy-style local contract, and paper-style generic closest-hit RT lowering; native OptiX closest-hit is source-wired, with pod evidence and consensus still pending. |

Continuous Frechet was evaluated and demoted to learner/demo status. It is not
counted as a benchmark app because the current evidence does not support a
serious benchmark claim against optimized CPU C++.

## Claim Boundary

This report authorizes only a milestone summary of already recorded evidence.
It does not authorize:

- broad RT-core speedup wording;
- whole-application speedup wording;
- paper reproduction claims;
- authors-code parity claims except where explicitly described as diagnostic or
  internal count-only evidence;
- external ABI stability claims;
- package-install support.

Each performance row below must still be cited with its exact report, hardware,
dataset, backend, and output contract before use outside internal discussion.

## Benchmark Inventory

| Benchmark | Paper or workload family | RTDL-owned contract | Main language/runtime pressure | Primary evidence |
| --- | --- | --- | --- | --- |
| Hausdorff / X-HD-style | X-HD-style exact Hausdorff distance | Exact 2-D point-set Hausdorff via grouped threshold/witness primitives and partner continuation | Grouped point traversal, scale-aware grouping, threshold search, nearest witness, reduced max-distance continuation | [Goal2129](goal2129_fair_public_hausdorff_a5000_perf_2026-05-16.md), [Goal2529](goal2529_3ai_consensus_finished_benchmark_apps_2026-05-23.md) |
| Spatial RayJoin-style | RayJoin-style spatial join | PIP, LSI, and overlay-seed rows over generic prepared spatial primitives | Prepared closed-shape queries, first-hit/count modes, phase telemetry, generic shape-pair kernel fixes | [Goal2150](goal2150_rayjoin_v2_optix_pod_perf_and_shape_pair_fix_2026-05-16.md), [Goal2297](goal2297_prepared_closed_shape_phase_telemetry_2ai_consensus_2026-05-17.md), [Goal2529](goal2529_3ai_consensus_finished_benchmark_apps_2026-05-23.md) |
| RT-DBSCAN-style | RT-DBSCAN 3-D density clustering | 3-D fixed-radius neighbor search -> core threshold -> radius-graph components | RT count-threshold device columns, adjacency streams, grouped union, explicit plan/explain selection, dense-stream memory control | [Goal2478](goal2478_rt_dbscan_project_completion_2026-05-21.md), [Goal2529](goal2529_3ai_consensus_finished_benchmark_apps_2026-05-23.md) |
| Robot collision | Static-scene robot feasibility screening | Grouped finite 3-D segment any-hit flags against prepared triangle scenes | Reusable prepared static scenes, host/device query-buffer reuse, compact flags, count-only screening, app-vocabulary purity guards | [Goal2491](goal2491_robot_collision_benchmark_app_closeout_2026-05-22.md), [Goal2529](goal2529_3ai_consensus_finished_benchmark_apps_2026-05-23.md) |
| RayDB-style | RayDB-style grouped aggregate query | Predicate-filtered grouped i64 count/sum/min/max/stats over partner-resident columns | Partner-resident column descriptors, grouped i64 dispatcher, fused grouped stats, large same-contract external baselines | [Goal2528](goal2528_raydb_style_benchmark_app_closeout_2026-05-23.md), [Goal2529](goal2529_3ai_consensus_finished_benchmark_apps_2026-05-23.md) |
| Barnes-Hut / RT-BarnesHut-style | PPoPP 2025 RT-BarnesHut | Aggregate tree rows, opening frontier, materialization-pressure accounting, partner-resident 3-D scalar diagnostic | Hierarchical aggregate descriptors, frontier traversal, streamed vector sums, partner-resident force accumulation, rejection of app-specific native force ABI | [Goal2550](goal2550_barnes_hut_final_performance_and_closeout_2026-05-23.md), [Goal2571](goal2571_3ai_consensus_benchmark_app_goal_audit_2026-05-23.md) |
| LibRTS-style spatial index | PPoPP 2025 LibRTS | Generic 2-D AABB index count-only point/range contains/intersects | Prepared AABB query buffers, generic AABB index operation, two-pass range-intersects traversal, authors-code fixture interchange | [Goal2582](goal2582_librts_internal_publish_consensus_2026-05-24.md), [Goal2580](goal2580_librts_optix_aabb_index_native_path_2026-05-24.md), [Goal2581](goal2581_librts_optix_range_intersects_path_2026-05-24.md) |
| RTNN neighbor search | RTNN-style fixed-radius nearest-neighbor search | Prepared 3-D fixed-radius bounded ranked-summary rows; ANN candidate-quality helper | Prepared search-side structures, device-side ranked summary, candidate quality references, density-aware partitioning pressure | [Goal2585](goal2585_rtnn_benchmark_front_door_2026-05-24.md), [Goal2388](goal2388_rtnn_fair_fight_benchmark_2026-05-19.md), [Goal2391](goal2391_rtnn_density_partition_and_grid_baseline_2026-05-19.md) |
| Triangle counting | RT-Graph / SIGMETRICS 2025 triangle-counting workload | Triangle witness rows or compact triangle summary | Raw row views, row-summary adapters, set-intersection-heavy graph contracts, strict Python graph semantics vs native engine boundary, and segmented-lowering pressure from real paper datasets | [Goal2586](goal2586_graph_analytics_benchmark_promotion_2026-05-24.md), [Goal2588](goal2588_rt_graph_triangle_counting_paper_code_intake_2026-05-24.md), [Goal2593](goal2593_rt_graph_paper_dataset_evaluation_2026-05-24.md), [Goal2593 consensus](goal2593_consensus_rt_graph_paper_dataset_2026-05-24.md) |
| GPU-RMQ | GPU-RMQ / range minimum query | Exact compact leftmost-argmin row per inclusive query interval | Hierarchical summaries, partner-resident scans, RT-assisted closest-hit subpaths, and explicit Python+partner+RTDL scheduling | [Goal2594](goal2594_gpu_rmq_benchmark_promotion_plan_2026-05-24.md) |

## Performance Evidence Snapshot

These rows are included to summarize the milestone. They are not new claims.

### Hausdorff / X-HD-style

Goal2129 measured exact 2-D projected Stanford point-set Hausdorff on an RTX
A5000. RTDL/OptiX beat dense all-pairs CuPy at larger public-data sizes, but a
fairer optimized grouped CuPy baseline remained faster for the best tuned
2-D projected-point cases.

Representative conclusion: RTDL can express the exact workflow and useful
pruning, but this benchmark does not support "RT cores beat optimized CUDA" for
the current 2-D projected-point harness.

### Spatial RayJoin-style

Goal2150 showed mixed but useful OptiX evidence on an RTX 4000 Ada pod:

| Workload | Scale | CPU sec | Embree sec | OptiX sec | Narrow interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| PIP | medium | 0.003706 | 0.003642 | 0.002488 | OptiX wins this small scoped row. |
| LSI | medium | 0.022420 | 0.026350 | 0.016080 | OptiX wins this scoped row. |
| Overlay seed | medium | 0.202004 | 0.015115 | 0.019069 | Embree wins; overlay is not the OptiX sweet spot here. |
| PIP | large synthetic | 0.018510 | 0.005658 | 0.014360 | Embree wins this sparse/disjoint synthetic row. |
| LSI | large synthetic | 0.093596 | 0.071418 | 0.065615 | OptiX modestly wins this scoped row. |

Goal2344 also records internal v2.1 evidence that a generic prepared
segment-first-hit / nearest-boundary route improved a same-contract RayJoin PIP
route over v2.0 by up to 72.93x. That remains internal exact-subpath evidence,
not a RayJoin paper reproduction claim.

### RT-DBSCAN-style

Goal2478 closed RT-DBSCAN for the current v2.x scope on clustered3d data.

| Points | Prepared CuPy grid sec | RT-count + prepared CuPy sec | Grouped-stream total sec | Grouped-stream speedup vs CuPy |
| ---: | ---: | ---: | ---: | ---: |
| 32,768 | 0.1597758988 | 0.1429276895 | 0.0408550138 | 3.9108x |
| 65,536 | 0.4676661789 | 0.3734569130 | 0.0990382954 | 4.7221x |
| 131,072 | 1.5541055435 | 1.0094030295 | 0.3172265468 | 4.8990x |

The correct claim is generic: RTDL now has fixed-radius rows, threshold columns,
adjacency streams, and grouped continuation sufficient for the scoped app. This
is not a paper-speedup claim and not a DBSCAN-native ABI.

### Robot Collision

Goal2491 closed the sampled discrete feasibility-screening benchmark on an RTX
4000 Ada pod.

| Mode | Tail median total sec | Correctness |
| --- | ---: | --- |
| CPU reference | 0.3339872658 | reference |
| Embree prepared | 0.0085970387 | matches sampled probe |
| Embree prepared buffers | 0.0001065433 | matches sampled probe |
| OptiX prepared | 0.0062834173 | matches sampled probe |
| OptiX prepared buffers | 0.0001258254 | matches sampled probe |
| OptiX prepared device buffers | 0.0000809059 | matches sampled probe |
| OptiX prepared device count | 0.0000528470 | count matches sampled probe |

The main insight is that repeated query packing and result materialization
dominated the naive prepared path more than traversal. The app forced buffer
reuse and compact result modes.

### RayDB-style

Goal2528 closed the grouped aggregate benchmark on an RTX 4000 Ada pod.
Medians exclude setup/index/descriptor preparation.

| Rows | PostgreSQL indexed ms | DuckDB ms | cuDF ms | RTDL fused full-contract ms |
| ---: | ---: | ---: | ---: | ---: |
| 1,000,000 | 6.241950 | 4.087197 | 42.533734 | 1.601686 |
| 5,000,000 | 43.007387 | 11.630014 | 51.043358 | 1.986026 |
| 10,000,000 | 66.663138 | 19.248983 | 52.286274 | 2.425149 |

All available results matched the shared compact grouped rows. This is a
same-contract grouped aggregate result, not a SQL engine, DBMS, SSB, or RayDB
authors-code comparison.

### Barnes-Hut / RT-BarnesHut-style

Goal2550 closed Barnes-Hut for this phase on an RTX A5000:

| Row | Value |
| --- | ---: |
| RTDL-side partner-resident 32K diagnostic min | 0.502848 ms |
| RTDL-side diagnostic mean | 0.521787 ms |
| Max scalar relative error vs RTDL Python reference | 3.301934e-05 |
| Authors artifact supported `new` mode force min | 5.405 ms |
| Authors artifact supported `new` mode force mean | 5.576 ms |

The authors same-input reload path segfaulted on the pod, so the authors row is
orientation evidence only. No same-contract authors-code speedup is authorized.
The rejected app-specific native OptiX force ABI was removed before final
timing.

### LibRTS-style Spatial Index

Goal2582 accepted the LibRTS-style slice for internal publication. On generated
paper-like small-box fixtures, 1M boxes x 1k queries produced:

| Operation | Authors-code timing | RTDL prepared OptiX warm median | Boundary |
| --- | ---: | ---: | --- |
| Point contains | 0.099 ms | 0.0983 ms | Count-only generated fixture. |
| Range contains | 0.106 ms | 0.0889 ms | Count-only generated fixture. |
| Range intersects | 0.620 ms | 0.4049 ms | Count-only generated fixture. |

Counts matched authors-code evidence for 10k/100k/1M rows. This is internal
generic `AABB_INDEX_QUERY_2D` evidence, not broad public speedup wording and not
full LibRTS reproduction.

### RTNN Neighbor Search

Goal2585 formalized the RTNN front door using Goal2388 evidence:

| Distribution | Points | RTDL prepared OptiX sec | CuPy all-pairs sec | CuPy / RTDL |
| --- | ---: | ---: | ---: | ---: |
| uniform | 65,536 | 0.012051 | 26.004428 | 2157.8x |
| clustered | 65,536 | 0.204774 | 22.450877 | 109.6x |
| shell | 65,536 | 0.006513 | 15.335754 | 2354.7x |

Scale rows:

| Distribution | Points | RTDL sec |
| --- | ---: | ---: |
| uniform | 262,144 | 0.041202 |
| clustered | 262,144 | 2.705786 |
| shell | 262,144 | 0.193032 |

Official RTNN binary rows exist but are diagnostic because the materialization
pipeline is not the same contract. Goal2391 also showed that a stronger CuPy
grid baseline beats current RTDL on dense clustered 262k data, so
density-aware scheduling remains a real runtime target.

### Triangle Counting

Goal2586 promotes only triangle counting as the graph benchmark slice. Goal2588
sets the concrete paper/code target as RT-Graph from SIGMETRICS 2025, while
keeping BFS out of this benchmark. Goal2593 completes same-input paper-dataset
evaluation against RTDL, the authors' `rt_tc`/`bs_tc` binaries where they
completed, and RAPIDS cuGraph.

The accepted closeout boundary is deliberately narrow. RTDL's generic OptiX
2A1 path is correct on `com-dblp`, `com-youtube`, `wiki-Talk`, and
`cit-Patents`; RTDL 1A2 is correct on `com-dblp` and `com-youtube`; larger
datasets expose pre-traversal CUDA OOM in the current unsegmented CuPy lowering.
cuGraph is the strongest current end-to-end baseline on real paper datasets.
No paper-dataset speedup claim is authorized.

BFS and visibility-edge modes remain learner/demo/example surfaces. They are not
part of the benchmark portfolio unless a future goal promotes one of them as a
separate single-contract benchmark.

## Cross-Benchmark Runtime Lessons

The benchmark suite has produced recurring design pressure in five areas:

| Runtime theme | Benchmarks that forced it | Current lesson |
| --- | --- | --- |
| Prepared reusable state | RayJoin, robot collision, LibRTS, RTNN, RT-DBSCAN | Serious workloads need scene/index/query-buffer reuse; one-shot examples hide the real cost model. |
| Compact outputs | Robot collision, RayDB, RTNN, RT-DBSCAN, LibRTS | Flags, counts, ranked summaries, and compact grouped rows are often the right contract; full witness rows are frequently the wrong fast path. |
| Partner-resident continuation | RayDB, RT-DBSCAN, Barnes-Hut, Hausdorff | RTDL should expose generic primitives and let Python/partner code own app continuation when the continuation is not RT traversal. |
| Generic grouped continuation | RT-DBSCAN, RayDB, RTNN | Grouping, bounded streams, and fused reductions are shared behavior, not app-specific engine logic. |
| App-agnostic native boundary | All benchmark apps | Native engines must see generic geometry, columns, prepared handles, queries, flags, counts, summaries, and reductions; app names and app formulas belong outside the engine. |

## Non-Benchmark Boundary

Continuous Frechet was intentionally demoted to learner/demo status after
Goal2583 and Goal2584. The current evidence says:

- correctness is useful;
- RTDL beats a simple Torch CUDA wavefront baseline;
- optimized CPU C++ is still faster across the measured sizes;
- no serious paper/authors-code benchmark target is currently attached.

Therefore it should not be listed with the promoted research benchmark apps
until a future goal identifies a stronger benchmark contract and baseline.

## Portfolio Status

| Category | Apps |
| --- | --- |
| 3-AI consensus-closed benchmark apps | Hausdorff/X-HD, Spatial RayJoin, RT-DBSCAN, Robot collision, RayDB-style |
| Closed bounded benchmark apps after the first consensus wave | Barnes-Hut |
| Internally publishable with 3-AI consensus | LibRTS-style spatial index |
| Formal front door added; strict claim boundary | RTNN |
| Candidate benchmark front door; pod evidence pending | GPU-RMQ |
| Closed bounded benchmark with accepted scalability limitation | Triangle counting |
| Explicitly demoted to learner/demo | Continuous Frechet |

## Recommended Next Milestone

The next milestone should not be "add more app-specific native kernels." The
best next work is to consolidate shared behavior exposed by the benchmark suite:

1. Normalize the benchmark-app catalog so committed docs, front doors, and tests
   match the current inventory.
2. Promote a behavior-first primitive catalog covering prepared state, compact
   outputs, grouped reductions, fixed-radius streams, AABB-index queries, and
   aggregate-frontier traversal.
3. Add stricter rules for benchmark-owned helper code versus engine primitives:
   a helper can live in an app when it expresses app semantics; it can move
   toward runtime only when at least two benchmark apps need the same behavior.
4. Keep external baselines strong. Use authors code when available and
   buildable; otherwise use serious same-contract CPU/CUDA/DB baselines with
   correctness oracles.
5. For triangle counting, scope the target paper and exact output contract
   before adding performance language.

## Sync Note

At the time this report was written, RTNN and graph analytics front doors plus
the Continuous Frechet demotion artifacts are present in the working tree but
not yet necessarily committed. Before external review, run `git status`, ensure
the intended files are tracked, run the relevant unit tests, and commit/push
only after the user approves the sync operation.
