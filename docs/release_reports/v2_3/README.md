# RTDL v2.3 Release Package

Status: released source-tree Python+partner+RTDL app-portfolio boundary.

Version marker: `v2.3`

Release date: 2026-05-25

## Release Statement

RTDL v2.3 is the app-portfolio cleanup release on top of the current v2.x
Python+partner+RTDL language boundary. It publishes the current benchmark-app
set, the learner/example app set, and the boundary decisions from the latest
benchmark wave.

The release is source-tree based. Use it from a checkout with
`PYTHONPATH=src:.`. It is not a package-install release, not a broad RT-core
speedup claim, not a whole-application speedup claim, and not a claim that RTDL
optimizes arbitrary PyTorch or CuPy programs.

## What v2.3 Includes

- A cleaned current app catalog with separate benchmark and learner/example
  tables.
- Ten promoted benchmark apps used as RTDL language/runtime reconstruction
  instruments.
- Explicit demotion of Continuous Frechet and GPU-RMQ to learner/design-pressure
  status after performance evidence did not support benchmark promotion.
- Generic OptiX grouped candidate argmin/finalize support extracted from the
  GPU-RMQ study without adding RMQ-specific native-engine logic.
- Current docs updated from stale release wording to the v2.3 app-portfolio
  release boundary.

## Promoted Benchmark Apps

| Benchmark app | Directory | Benchmark contract | Release boundary |
| --- | --- | --- | --- |
| Hausdorff / X-HD-style | `examples/v2_0/research_benchmarks/hausdorff_xhd/` | Exact Hausdorff distance with grouped threshold/witness and partner continuation paths | Bounded evidence only; not every Hausdorff input beats CUDA |
| Spatial RayJoin-style | `examples/v2_0/research_benchmarks/spatial_rayjoin/` | PIP, LSI, and overlay-seed rows over generic prepared spatial primitives | Scoped spatial join contracts; not full RayJoin paper reproduction |
| RT-DBSCAN-style | `examples/v2_0/research_benchmarks/rt_dbscan/` | 3-D fixed-radius neighbor search, core thresholding, and component continuation | Generic fixed-radius/component benchmark; no DBSCAN-native ABI |
| Robot collision | `examples/v2_0/research_benchmarks/robot_collision/` | Static scene plus batched transformed query geometry to compact any-hit flags/counts | Prepared static-scene screening; not a planner or exact swept collision solver |
| RayDB-style grouped aggregate | `examples/v2_0/research_benchmarks/raydb_style/` | Paper-shaped generated grouped count/sum prepared-query paths plus historical grouped columnar paths | Current RT-core evidence is prepared-query only; not SQL, SSB, DBMS, authors-code, or whole-app speedup |
| Barnes-Hut / RT-BarnesHut-style | `examples/v2_0/research_benchmarks/barnes_hut/` | Aggregate tree rows, opening frontier, and partner-resident force diagnostics | Hierarchical aggregate-frontier pressure; no app-specific force ABI |
| LibRTS-style spatial index | `examples/v2_0/research_benchmarks/librts_spatial_index/` | Generic 2-D AABB point/range contains/intersects count-only paths | Internal benchmark slice; not full mutable LibRTS reproduction |
| RTNN neighbor search | `examples/v2_0/research_benchmarks/rtnn/` | Prepared 3-D fixed-radius bounded ranked-summary rows and ANN candidate-quality helpers | Same-contract benchmark front door; not full RTNN paper reproduction |
| Triangle counting | `examples/v2_0/research_benchmarks/triangle_counting/` | RT-Graph-style triangle witness rows or compact triangle summary | Graph benchmark slice; large paper datasets need segmented/streamed lowering |
| Bounded contact witness / contact-manifold | `examples/v2_0/research_benchmarks/contact_manifold/` | Generic AABB broadphase plus bounded witness collection | Validates `COLLECT_K_BOUNDED`; no contact/collision native ABI |

## Learner And Example Apps

| Learner/example group | Files or directory | What it teaches | Release boundary |
| --- | --- | --- | --- |
| Getting started | `examples/v2_0/getting_started/` | Hello world, backend choice, feature cookbook | Learner examples |
| Ray query features | `examples/v2_0/features/ray_queries/` | Any-hit, visibility rows, row reductions | Feature examples |
| Neighbor features | `examples/v2_0/features/neighbors/` | Fixed-radius rows and KNN rows | Feature examples |
| Database feature recipes | `examples/v2_0/features/database/` | Conjunctive scan, grouped count, grouped sum | Feature examples |
| Graph feature recipes | `examples/v2_0/features/graph/` | BFS and simple triangle-count feature shapes | Feature examples; benchmark graph scope is triangle counting only |
| Spatial feature recipes | `examples/v2_0/features/spatial/` | Segment/polygon, overlap, and Jaccard feature rows | Feature examples |
| Partner continuation examples | `examples/v2_0/partners/` | NumPy/CuPy/user-owned continuation around RTDL outputs | Partner examples |
| Geospatial apps | `examples/v2_0/apps/geospatial/` | Road hazard, service coverage, hotspot, facility assignment, sales-risk screening | Learner apps |
| ML apps | `examples/v2_0/apps/ml/` | ANN candidate quality, outlier detection, DBSCAN learner path | Learner apps |
| Analytics apps | `examples/v2_0/apps/analytics/` | Database-style summaries and graph analytics examples | Learner apps |
| Robotics app | `examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py` | Pose/link any-hit screening shape | Learner app |
| Simulation app | `examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py` | Barnes-Hut candidate and coverage ideas | Learner app |
| Trajectory app | `examples/v2_0/apps/trajectory/rtdl_continuous_frechet_distance_app.py` | Continuous Frechet broadphase plus learner-owned continuation | Demoted learner/demo app |
| GPU-RMQ learner app | `examples/v2_0/learner_apps/gpu_rmq/` | RMQ hierarchy/RT lowering pressure and generic grouped candidate argmin | Demoted learner/design-pressure app |
| Visual demos | `examples/visual_demo/` | Visual explanation of RT-shaped query work | Demos, not renderer claims |

## What v2.3 Does Not Claim

- No package metadata, PyPI artifact, or install command is published.
- No universal speedup claim is made for backend flags such as `--backend optix`.
- No arbitrary PyTorch/CuPy acceleration claim is made.
- No whole-application speedup claim is made for the benchmark portfolio.
- No paper-reproduction claim is made unless a specific report says so for a
  specific subpath.
- No GPU-RMQ benchmark promotion is claimed; Goal2612 demotes it.
- No Continuous Frechet benchmark promotion is claimed; Goal2583/2584 demote it.

## Evidence

- [Application Catalog](../../application_catalog.md)
- [v2.3 benchmark-app performance appendix](benchmark_app_performance.md)
- [v2.3 benchmark-app performance 3-AI consensus](benchmark_app_performance_3ai_consensus.md)
- [v2.4/v2.5 partner roadmap proposal](../../reports/goal2657_v2_4_v2_5_partner_roadmap_2026-05-27.md)
- [Goal2583 Continuous Frechet benchmark promotion decision](../../reports/goal2583_continuous_frechet_benchmark_promotion_2026-05-24.md)
- [Goal2584 Continuous Frechet baseline results](../../reports/goal2584_continuous_frechet_gpu_cpu_baseline_results_2026-05-24.md)
- [Goal2587 benchmark-app milestone report](../../reports/goal2587_benchmark_apps_milestone_report_2026-05-24.md)
- [Goal2593 triangle-counting paper-dataset evaluation](../../reports/goal2593_rt_graph_paper_dataset_evaluation_2026-05-24.md)
- [Goal2593 triangle-counting consensus](../../reports/goal2593_consensus_rt_graph_paper_dataset_2026-05-24.md)
- [Goal2612 GPU-RMQ demotion evidence](../../reports/goal2612_gpu_rmq_grouped_candidate_argmin_vs_cuda_2026-05-25.md)

## Minimal Smoke Commands

```bash
PYTHONPATH=src:. python examples/v2_0/getting_started/rtdl_hello_world.py
PYTHONPATH=src:. python examples/v2_0/learner_apps/gpu_rmq/rtdl_gpu_rmq_learner_app.py --mode scope
PYTHONPATH=src:. python -m unittest tests.goal2613_v2_3_app_portfolio_release_test
```

## Release Boundary

RTDL v2.3 is ready as an internal/public source-tree release for the current
app portfolio. It makes the benchmark suite cleaner by separating promoted
benchmark apps from learner/example apps. It does not widen performance claims
beyond the exact reviewed artifacts.
