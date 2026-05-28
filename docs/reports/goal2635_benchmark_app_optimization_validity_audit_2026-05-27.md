# Goal2635 Benchmark-App Optimization Validity Audit

Date: 2026-05-27

Status: internal engineering audit, not public speedup wording.

## Question

For each promoted benchmark app, review the v2.x goals/docs/reports, understand
what we actually did, and decide whether the current Embree-vs-OptiX/RT test is
optimized enough to be a reasonable and trustworthy performance comparison.

## Method

This audit reviewed the current benchmark catalog, benchmark READMEs, the
Goal2626/Goal2634 matrix runner and artifacts, and the controlling post-v2.0
closeout or gap-closure reports for each promoted benchmark app.

The review is intentionally focused on controlling evidence, not every
historical file line-by-line. Apps with many development reports are judged from
the final closeout, consensus, and later correction reports that supersede
earlier experiments.

Primary shared evidence:

- `docs/application_catalog.md`
- `examples/v2_0/research_benchmarks/README.md`
- `scripts/goal2626_benchmark_embree_optix_baseline.py`
- `docs/reports/goal2626_benchmark_embree_optix_baseline_plan_2026-05-26.md`
- `docs/reports/goal2626_benchmark_embree_optix_stress_addendum_2026-05-26.md`
- `docs/reports/goal2634_gap_closure_and_rt_baseline_2026-05-27.md`
- `docs/reports/goal2634_full_standard_prepared_contact_pod/summary.md`
- `docs/reports/goal2634_full_standard_prepared_contact_pod/summary_slim.json`

Current promoted suite size:

- 10 promoted benchmark apps.
- 11 standard matrix rows because RayDB-style grouped aggregate has separate
  grouped `count` and grouped `sum` contracts.

## Overall Verdict

The current Goal2634 standard matrix is a valid internal exact-subpath baseline:
every promoted benchmark app has both Embree/CPU-fallback and OptiX entries, the
known broken rows were repaired, and the native engine remains app-name-free for
the promoted paths.

It is not yet a uniformly strong final performance baseline for all apps. The
rows are trustworthy only at their stated contract boundary. Several rows still
need larger scale ladders or stronger end-to-end workload coverage before we
should use them as serious "RT beats Embree" evidence for the app as a whole.

## App-by-App Audit

| App | Controlling evidence reviewed | What we did since v2.0 | Current matrix row | Optimization-validity verdict |
| --- | --- | --- | --- | --- |
| Hausdorff / X-HD-style | `hausdorff_xhd/README.md`; `goal2340_hausdorff_v2_1_benchmark_refresh_2026-05-18.md`; current Goal2626/2634 matrix | Refreshed the app front door, added scale-aware grouped traversal defaults, kept native engine app-agnostic through point groups, threshold flags, nearest witnesses, and reductions. Earlier reports contain stronger public-dataset OptiX evidence, but the current matrix row is narrower. | `hausdorff_threshold_decision`; Embree `0.102451s`, OptiX `0.0311073s`, `3.29x`; same metric `query_fixed_radius_threshold_reached_count_sec`. | Trustworthy for a prepared threshold-decision subpath. Not enough by itself for a final serious Hausdorff performance claim because the standard row is short and not the exact witness/full Hausdorff path. Use larger public-dataset reruns before claim wording. |
| Spatial RayJoin-style | `spatial_rayjoin/README.md`; `goal2632_rayjoin_prepared_full_route_2026-05-27.md`; earlier RayJoin closure reports listed in app README | Fixed the immediate matrix gap: prepared OptiX now covers PIP, LSI, and overlay-seed pair-dependency flags through generic point/shape, segment-pair, and shape-pair primitives. No RayJoin-native engine path was added. | `rayjoin_all_backend_query_summary`; Embree `0.0203149s`, OptiX `0.000529638s`, `38.4x`. | Functionally trustworthy but performance-weak. The report itself says the fixture is tiny and overlay-seed is zero-row on that fixture. Needs a larger CDB or scaled synthetic all-route fixture before it can be a serious performance baseline. |
| RT-DBSCAN-style | `rt_dbscan/README.md`; `goal2478_rt_dbscan_project_completion_2026-05-21.md`; current Goal2626/2634 matrix | Built a full RTDL app shape using generic 3-D fixed-radius rows, RT core count/core columns, adjacency streams, grouped-stream continuation, grouped-union all-items/self-query, predicate/same-root culling, and CuPy component continuation. Explicitly rejected DBSCAN-native native ABI. | `dbscan_cluster_signature`; Embree fixed-radius rows `20.6102s`, OptiX grouped stream `1.62144s`, `12.7x`. | Trustworthy as current best generic CPU fallback versus current best OptiX grouped-stream app contract. Caveat: Embree and OptiX use different internal routes, so this is not a pure backend-only primitive microcomparison; it is a same output-contract app comparison. |
| Robot collision | `robot_collision/README.md`; `goal2491_robot_collision_benchmark_app_closeout_2026-05-22.md`; Goal2484-2490 optimization reports by closeout reference; Goal2626 stress addendum | Added grouped finite 3-D segment any-hit flags, prepared static scene reuse, reusable host buffers, OptiX device-resident grouped segment query buffers, compact group flags, count-only screening, and phase telemetry. Native code remains robot/link/pose-free. | `prepared_collision_flags`; Embree prepared buffers `0.00853798s`, OptiX prepared device buffers `0.00161413s`, `5.29x`. | Trustworthy for prepared sampled collision-flag screening. The standard row is short, but stress evidence still shows OptiX faster at larger prepared-query scale. Not a planner, exact solid collision, or swept collision claim. |
| RayDB-style grouped aggregate | `raydb_style/README.md`; `goal2528_raydb_style_benchmark_app_closeout_2026-05-23.md`; `goal2630_raydb_partner_resident_benchmark_path_2026-05-26.md` | Built generic partner-resident column descriptors and grouped i64 reductions: count, sum, min, max, sum_count, fused stats. Fixed the first matrix problem by switching OptiX from host-copy columnar payload to warm device-resident grouped reduction. | `raydb_grouped_count`: Embree `0.222185s`, OptiX partner-resident `0.000793088s`, `280x`; `raydb_grouped_sum`: Embree `0.243746s`, OptiX `0.000977349s`, `249x`. | Trustworthy for the grouped count/sum query subpaths, and supported by larger 1M/5M/10M evidence. Important caveat: this is not RT-core acceleration; it is Python+partner+RTDL device-resident CUDA grouped reduction. |
| Barnes-Hut / RT-BarnesHut-style | `barnes_hut/README.md`; `goal2550_barnes_hut_final_performance_and_closeout_2026-05-23.md`; `goal2633_barnes_hut_same_contract_node_coverage_2026-05-27.md` | Created many generic aggregate-tree/frontier/vector-sum reference contracts, rejected app-specific native inverse-square force math, and later fixed the matrix to compare the same prepared node-coverage threshold decision on Embree and OptiX. | `node_coverage_prepared_threshold_decision`; Embree `0.0388851s`, OptiX `0.00855045s`, `4.55x`. | Trustworthy for node-coverage threshold decision only. Not enough for Barnes-Hut as an app because the full hierarchical aggregate-frontier plus force accumulation is not the measured Embree/OptiX path. Also rerun a scale ladder, because earlier stress evidence found large Barnes-Hut node coverage could favor Embree under an older row. |
| LibRTS-style spatial index | `librts_spatial_index/README.md`; `goal2580_librts_optix_aabb_index_native_path_2026-05-24.md`; `goal2581_librts_optix_range_intersects_path_2026-05-24.md`; `goal2582_librts_internal_publish_consensus_2026-05-24.md` | Implemented generic `AABB_INDEX_QUERY_2D` for point contains, range contains, and range intersects. Added prepared query buffers, query-GAS backward pass for range intersects, exact refinement, duplicate suppression, authors-code evidence, and 3-AI internal publication consensus. | `aabb_index_all_count_only`; Embree/CPU fallback `20.707s`, OptiX `0.691477s`, `29.9x`. | High confidence for count-only AABB query contract. Caveat: the Embree row is a CPU fallback path for the same contract, not necessarily an equally optimized Embree RT traversal. The OptiX side is well justified and authors-code-oriented for prepared query latency. |
| RTNN neighbor search | `rtnn/README.md`; `goal2388_rtnn_fair_fight_benchmark_2026-05-19.md`; `goal2585_rtnn_benchmark_front_door_2026-05-24.md` | Added formal RTNN benchmark front door over generic prepared 3-D fixed-radius ranked summaries. The path avoids full witness materialization when one bounded ranked summary per query is enough. Official RTNN remains diagnostic because its materialization contract differs. | `prepared_3d_ranked_summary`; Embree `0.2638s`, OptiX `0.00153247s`, `172x`. | Trustworthy for the prepared ranked-summary contract, but the standard matrix row is small and uniform. For serious baseline use, rerun distribution ladder from Goal2388, especially clustered density cases and larger point counts. |
| Triangle counting | `triangle_counting/README.md`; `goal2593_rt_graph_paper_dataset_evaluation_2026-05-24.md`; `goal2631_triangle_generic_rt_path_2026-05-26.md` | Promoted only triangle counting, aligned with RT-Graph 2A1/1A2 ideas, added generic `Triangle3D`/`Ray3D` mapping and weighted any-hit/hit-count summaries, and moved graph preprocessing to Python/CuPy partner code. Current largest-paper datasets fail from unsegmented two-hop materialization, not OptiX traversal correctness. | `triangle_count_rt_graph_2a1_summary`; Embree `0.039049s`, OptiX `0.000364401s`, `107x`. | Trustworthy for the synthetic RT-2A1 backend-query subpath. Not sufficient for paper-dataset or end-to-end graph benchmark claims. The next real optimization is segmented/streamed RT-Graph lowering that avoids global two-hop materialization. |
| Bounded contact witness / contact-manifold | `contact_manifold/README.md`; `goal2621_bounded_contact_witness_collect_k_3ai_consensus_2026-05-25.md`; `goal2622_contact_manifold_generic_aabb_discovery_2026-05-25.md`; `goal2623_optix_aabb_intersection_pair_rows_2026-05-25.md`; `goal2623_optix_aabb_intersection_pair_rows_3ai_consensus_2026-05-25.md`; Goal2634 matrix | Promoted stable generic `COLLECT_K_BOUNDED` with exact fail-closed overflow, added generic AABB broadphase rows, added generic OptiX AABB intersection pair rows, documented pre-dedup raw capacity rule, and kept exact triangle refinement/contact interpretation in Python. | `generic_aabb_broadphase_collect_k`; Embree `0.485812s`, OptiX `0.0184764s`, `26.3x`. | Trustworthy for generic AABB row discovery plus bounded collection. Not a full contact-manifold solver claim; exact triangle intersection refinement remains app-owned and outside the primary metric. |

## Current Matrix Adequacy By Class

| Class | Apps | Interpretation |
| --- | --- | --- |
| Strong current exact-subpath baseline | RT-DBSCAN, robot collision, RayDB, LibRTS, contact manifold | Current rows use the optimized path that the app development converged on. The claim boundary is still exact-subpath only. |
| Correct but too small or too scoped for serious final perf wording | Hausdorff, Spatial RayJoin, RTNN, Barnes-Hut, triangle counting | The row is valid, but the current standard workload or metric is not enough to support broad or whole-app performance claims. These need scale ladders, paper-dataset-capable lowering, or larger all-route fixtures. |
| Not an RT-core claim despite OptiX label | RayDB | The OptiX row is a partner-resident CUDA grouped-reduction path. It is important for Python+partner+RTDL, but it should not be counted as RT-core acceleration evidence. |

## Required Follow-Up Before Using This As A Serious Perf Baseline

The following work should happen before the matrix becomes the main baseline for
the next no-C++ partner version.

| App | Required follow-up |
| --- | --- |
| Hausdorff | Rerun a larger current-main threshold/witness scale ladder and keep exact witness runs separate from threshold-decision rows. |
| Spatial RayJoin | Build a larger all-route fixture where PIP, LSI, and overlay-seed all do nontrivial work; current tiny fixture is not enough. |
| RT-DBSCAN | Add the 65k/131k grouped-stream closeout rows to the canonical matrix or expose a `large-dbscan` matrix mode; current standard 8k row is useful but smaller than the final closeout scale. |
| Robot collision | Keep the prepared-query stress row available as an addendum; do not quote process wall or CPU oracle-inclusive timings as backend speedups. |
| RayDB | Keep the large 1M/5M/10M fused stats evidence next to the standard count/sum row; explicitly label the path as partner-resident CUDA, not RT-core. |
| Barnes-Hut | Rerun the current same-contract node-coverage path across a scale ladder; do not use the row as evidence for full aggregate-frontier force acceleration. |
| LibRTS | If the question is specifically Embree-vs-OptiX RT traversal, add a true Embree AABB-index traversal row or label current row as CPU fallback. For app-level CPU-vs-OptiX contract, current row is strong. |
| RTNN | Rerun uniform/clustered/shell distributions and larger point counts under the same current matrix harness; standard uniform-only row under-represents density risk. |
| Triangle counting | Add segmented/streamed lowering before claiming paper-dataset seriousness; current synthetic query subpath is not enough for paper-scale graphs. |
| Contact manifold | Keep the 65k pressure result and pre-dedup capacity rule in the benchmark notes; current standard row is acceptable for primitive-level evidence. |

## Final Position

The current suite is good enough to say:

```text
RTDL has 10 promoted benchmark apps and an internal exact-subpath matrix where
all current benchmark rows have Embree/CPU-fallback and OptiX entries.
The known broken matrix rows were repaired without adding app-specific native
engine logic.
```

The current suite is not enough to say:

```text
RTDL broadly beats Embree or every CPU/GPU implementation for all benchmark apps.
RTDL has full paper-system reproductions for all app papers.
Every current matrix row is second-scale, paper-scale, or end-to-end.
```

The main engineering conclusion is that Goal2634 fixed correctness of the
comparison front doors, but Goal2635 still finds performance-evidence debt in
scale and scope for Hausdorff, Spatial RayJoin, RTNN, Barnes-Hut, and triangle
counting. The next matrix should keep the exact-subpath discipline but add
larger, less toy workloads for those apps.
