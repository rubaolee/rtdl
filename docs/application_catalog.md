# RTDL Application Catalog

This is the v2.x-facing catalog of runnable RTDL application examples. It keeps
normal users focused on the current architecture: Python application code around
RTDL kernels, with optional partner-owned columns for supported paths.

Older app/version evidence belongs in
[Learner Doc Version Notes](history/learner_doc_version_notes.md)
and the report archive.

Archived scenario-specific DB and Apple RT helpers remain in the repository for
compatibility and audit tests, but users should start from the unified Apple and
database app wrappers listed below.

## Reading Rule

Each app below has two boundaries:

- what RTDL owns;
- what remains Python, partner, or domain-library work.

Do not turn an app row into a broad speedup claim unless the exact backend,
partner, hardware, command shape, output contract, and artifact are cited.

## v2.3 Portfolio Snapshot

### Promoted Benchmark Apps

These are the current benchmark apps. They are reconstruction instruments for
RTDL language/runtime design, not broad paper-reproduction claims.

| Benchmark app | Directory | Benchmark contract | Current v2.3 status |
| --- | --- | --- | --- |
| Hausdorff / X-HD-style | `examples/v2_0/research_benchmarks/hausdorff_xhd/` | Exact Hausdorff distance with grouped threshold/witness and partner continuation paths | Promoted benchmark with bounded evidence; no claim that every Hausdorff input beats every CUDA implementation |
| Spatial RayJoin-style | `examples/v2_0/research_benchmarks/spatial_rayjoin/` | PIP, LSI, and overlay-seed rows over generic prepared spatial primitives | Promoted benchmark for scoped spatial join contracts; not full RayJoin paper reproduction |
| RT-DBSCAN-style | `examples/v2_0/research_benchmarks/rt_dbscan/` | 3-D fixed-radius neighbor search, core thresholding, and component continuation | Promoted benchmark for generic fixed-radius/component contracts; no DBSCAN-native ABI |
| Robot collision | `examples/v2_0/research_benchmarks/robot_collision/` | Static scene plus batched transformed query geometry to compact any-hit flags/counts | Promoted benchmark for prepared static-scene screening; not a planner or exact swept collision solver |
| RayDB-style grouped aggregate | `examples/v2_0/research_benchmarks/raydb_style/` | Predicate-filtered grouped count/sum/min/max/stats over partner-resident columns | Promoted benchmark for columnar grouped reductions; not SQL, SSB, or a DBMS |
| Barnes-Hut / RT-BarnesHut-style | `examples/v2_0/research_benchmarks/barnes_hut/` | Aggregate tree rows, opening frontier, and partner-resident force diagnostics | Promoted benchmark for hierarchical aggregate-frontier pressure; no app-specific force ABI |
| LibRTS-style spatial index | `examples/v2_0/research_benchmarks/librts_spatial_index/` | Generic 2-D AABB point/range contains/intersects count-only paths | Promoted internal benchmark slice; not full mutable LibRTS reproduction |
| RTNN neighbor search | `examples/v2_0/research_benchmarks/rtnn/` | Prepared 3-D fixed-radius bounded ranked-summary rows and ANN candidate-quality helpers | Promoted benchmark front door with strict same-contract boundary; not a full RTNN paper reproduction |
| Triangle counting | `examples/v2_0/research_benchmarks/triangle_counting/` | RT-Graph-style triangle witness rows or compact triangle summary | Promoted graph benchmark slice; larger paper datasets require future segmented/streamed lowering |

### Learner And Example Apps

These are runnable learner, feature, partner, demo, or demoted research apps.
They are useful for teaching and design pressure, but they are not promoted
benchmark claims.

| Learner/example group | Files or directory | What it teaches | Benchmark status |
| --- | --- | --- | --- |
| Getting started | `examples/v2_0/getting_started/rtdl_hello_world.py`, `rtdl_hello_world_backends.py`, `rtdl_feature_quickstart_cookbook.py` | First import, backend choice, and feature recipes | Learner examples |
| Ray query features | `examples/v2_0/features/ray_queries/` | Any-hit, visibility rows, and row reduction basics | Feature examples |
| Neighbor features | `examples/v2_0/features/neighbors/` | Fixed-radius rows and KNN rows | Feature examples |
| Database feature recipes | `examples/v2_0/features/database/` | Conjunctive scan, grouped count, grouped sum | Feature examples |
| Graph feature recipes | `examples/v2_0/features/graph/` | BFS and simple triangle-count feature shapes | Feature examples; promoted graph benchmark is triangle-counting only |
| Spatial feature recipes | `examples/v2_0/features/spatial/` | Segment/polygon hit count, any-hit rows, overlap rows, Jaccard | Feature examples |
| Partner continuation examples | `examples/v2_0/partners/` | NumPy/CuPy/user-owned continuation around RTDL outputs | Partner examples |
| Geospatial apps | `examples/v2_0/apps/geospatial/` | Road hazard, service coverage, hotspot, facility assignment, sales-risk screening | Learner apps |
| ML apps | `examples/v2_0/apps/ml/` | ANN candidate quality, outlier detection, DBSCAN learner path | Learner apps; promoted DBSCAN benchmark is under `research_benchmarks/rt_dbscan/` |
| Analytics apps | `examples/v2_0/apps/analytics/` | Database-style summaries and graph analytics examples | Learner apps; promoted RayDB and triangle-counting benchmarks live under `research_benchmarks/` |
| Robotics app | `examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py` | Pose/link any-hit screening shape | Learner app; promoted benchmark is under `research_benchmarks/robot_collision/` |
| Simulation app | `examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py` | Barnes-Hut node candidate and coverage ideas | Learner app; promoted benchmark is under `research_benchmarks/barnes_hut/` |
| Trajectory app | `examples/v2_0/apps/trajectory/rtdl_continuous_frechet_distance_app.py` | Continuous Frechet broadphase plus learner-owned continuation | Explicitly demoted learner/demo app |
| GPU-RMQ research app | `examples/v2_0/research_benchmarks/gpu_rmq/` | RMQ hierarchy/RT lowering pressure and generic grouped candidate argmin | Explicitly demoted research/learner app after Goal2612 |
| Visual demos | `examples/visual_demo/` | Visual explanation of RT-shaped query work | Demos, not renderer claims |

## Beginner Examples

| Example | File | What it teaches |
| --- | --- | --- |
| Hello world | `examples/v2_0/getting_started/rtdl_hello_world.py` | source-tree import and first output |
| Backend hello world | `examples/v2_0/getting_started/rtdl_hello_world_backends.py` | same app idea through selected runtime backends |
| Feature cookbook | `examples/v2_0/getting_started/rtdl_feature_quickstart_cookbook.py` | compact recipe per public feature |
| Partner any-hit | `examples/v2_0/partners/rtdl_partner_anyhit.py` | first partner-owned column path |

## Spatial And Geometry Apps

| App | File | RTDL role | Boundary |
| --- | --- | --- | --- |
| Segment/polygon hit count | `examples/v2_0/features/spatial/rtdl_segment_polygon_hitcount.py` | candidate traversal and compact counts | not a full GIS engine |
| Segment/polygon any-hit rows | `examples/v2_0/features/spatial/rtdl_segment_polygon_anyhit_rows.py` | exact witness pairs or streaming witness columns where supported | full Python row tables are convenience output, not the fast v2 shape |
| Polygon pair overlap rows | `examples/v2_0/features/spatial/rtdl_polygon_pair_overlap_area_rows.py` | bounded candidate discovery and summary contracts | not arbitrary polygon overlay |
| Polygon set Jaccard | `examples/v2_0/features/spatial/rtdl_polygon_set_jaccard.py` | bounded candidate discovery and summary contracts | not a general GIS/Jaccard engine |
| Road hazard screening | `examples/v2_0/apps/geospatial/rtdl_road_hazard_screening.py` | segment/polygon candidate and priority summaries | no routing or road-network system claim |
| Continuous Frechet distance | `examples/v2_0/apps/trajectory/rtdl_continuous_frechet_distance_app.py` | broadphase free-space candidate discovery | Python or learner-owned C++ owns the Frechet decision/search algorithm; keep this as a learner/demo app, not a benchmark app |

## Proximity And Search Apps

| App | File | RTDL role | Boundary |
| --- | --- | --- | --- |
| Service coverage gaps | `examples/v2_0/apps/geospatial/rtdl_service_coverage_gaps.py` | fixed-radius coverage counts/rows | not a service-optimization product |
| Event hotspot screening | `examples/v2_0/apps/geospatial/rtdl_event_hotspot_screening.py` | fixed-radius density counts/rows | not a full analytics pipeline |
| Facility KNN assignment | `examples/v2_0/apps/geospatial/rtdl_facility_knn_assignment.py` | KNN or threshold coverage rows | richer assignment policies remain app code |
| Hausdorff distance | `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py` | nearest-candidate rows or threshold summaries | exact rich witness extraction is app/partner work unless documented |
| RTNN neighbor search | `examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py` | candidate-subset reranking, coverage summaries, and prepared 3-D ranked neighbor summaries | not a general ANN index or full RTNN paper reproduction |
| Outlier detection | `examples/v2_0/apps/ml/rtdl_outlier_detection_app.py` | radius density rows/counts | final anomaly policy is Python/app code |
| DBSCAN clustering | `examples/v2_0/apps/ml/rtdl_dbscan_clustering_app.py` | core-count/core-flag primitives | cluster expansion remains app/partner graph work |

## Analytical, Graph, And Simulation Apps

| App | File | RTDL role | Boundary |
| --- | --- | --- | --- |
| Database analytics | `examples/v2_0/apps/analytics/rtdl_database_analytics_app.py` | bounded columnar scan/group summaries | not SQL or a DBMS |
| Graph analytics | `examples/v2_0/apps/analytics/rtdl_graph_analytics_app.py` | learner/demo graph app for frontier rows, triangle-style rows/summaries, and visibility edges | not a graph database; the closed research benchmark scope is RT-Graph-style triangle counting only, with Goal2593 documenting the accepted large-paper-dataset segmented/streamed-lowering limitation |
| GPU-RMQ range minimum query | `examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py` | research/learner app for exact compact RMQ rows, hierarchy-style local contracts, paper-style generic closest-hit RT lowering, and the generic grouped candidate argmin primitive | Goal2612 rejects benchmark promotion for the current design: RTDL remains much slower than direct CUDA sparse-query code; keep it as a design-pressure case, not a speedup benchmark |
| Robot collision screening | `examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py` | any-hit pose flags/counts | not a planner or physics simulator |
| Barnes-Hut force approximation | `examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py` | node/body candidate discovery and coverage summaries | force-vector reduction remains app/partner work unless documented |

## Visual Demos

| Demo | File | RTDL role | Boundary |
| --- | --- | --- | --- |
| Hidden star visual demo | `examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py` | ray/triangle query core | RTDL is not a renderer |
| Lit ball demo | `examples/visual_demo/rtdl_lit_ball_demo.py` | query core inside Python presentation | Python owns rendering/presentation |

## v2.x Output Guidance

For performance-oriented v2.x apps, prefer compact or partner-owned outputs:

- flags instead of full witness rows when only yes/no is needed;
- counts instead of pair tables when only totals are needed;
- streaming witness columns instead of Python dictionaries for large witness
  output;
- partner-owned arrays when the next computation will run in PyTorch or CuPy.

Use Python row dictionaries when clarity or inspection matters more than
throughput.

## Read Next

- [App And Example Quickstart](app_example_quickstart.md)
- [Partner Acceleration Boundaries](partner_acceleration_boundaries.md)
- [App Engine Support Matrix](app_engine_support_matrix.md)
- [v2.3 Release Package](release_reports/v2_3/README.md)
