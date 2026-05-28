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

## Current v2.x Portfolio Snapshot

### Promoted Benchmark Apps

These are the current benchmark apps. They are reconstruction instruments for
RTDL language/runtime design, not broad paper-reproduction claims.
Most performance values below come from the latest internal standard matrix:
`docs/reports/goal2634_full_standard_prepared_contact_pod/summary.md`.
Rows with later app-specific closeout evidence cite that evidence in the
boundary column.

The matrix was collected on an NVIDIA RTX A5000 pod from commit
`56e1f9b230cdef6d803191c8804f192133b4d020`. It is exact-subpath evidence only,
not public whole-app speedup wording.

For a per-app audit of whether each row uses the current optimized path and
where scale/scope evidence is still weak, see
`docs/reports/goal2635_benchmark_app_optimization_validity_audit_2026-05-27.md`.
For the current measured performance report and its overclaiming boundaries,
see
`docs/reports/goal2636_current_benchmark_performance_report_2026-05-27.md`.
For the completed all-benchmark performance diffs including the strengthened
Goal2636 rows, see
`docs/reports/goal2637_all_benchmark_perf_diffs_2026-05-27.md`.
For the current detailed per-app portfolio report including design pressure,
primitive boundaries, non-benchmark demotions, and the latest Barnes-Hut
Goal2642 follow-up, see
`docs/reports/goal2643_all_benchmark_apps_detailed_report_2026-05-27.md`.
For the refreshed current all-benchmark performance comparison after the RayDB
Goal2653 closeout, see
`docs/reports/goal2654_all_benchmark_app_perf_comparison_refresh_2026-05-27.md`.
For the compact combined-app RT-core speedup summary, see
`docs/reports/goal2655_benchmark_rt_core_speedup_summary_2026-05-27.md`.
For the follow-up runner that strengthens the weaker Hausdorff, Spatial
RayJoin, RTNN, Barnes-Hut, and triangle-counting rows, see
`docs/reports/goal2636_strengthened_benchmark_rows_plan_2026-05-27.md`.

| Benchmark app | Entry point | Benchmark contract | Key RTDL primitive/path | Embree sec | OptiX sec | Speedup | Boundary |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| Hausdorff / X-HD-style | `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py` | Hausdorff threshold decision | Prepared fixed-radius threshold | 0.102451 | 0.0311073 | 3.29x | No claim that every Hausdorff input beats every CUDA implementation. |
| Spatial RayJoin-style | `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | Scoped all-backend query summary | Prepared spatial relation / shape-pair route | 0.0203149 | 0.000529638 | 38.4x | Scoped spatial join contracts, not full RayJoin paper reproduction. |
| RT-DBSCAN-style | `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py` | Cluster signature | Fixed-radius rows plus grouped continuation | 20.6102 | 1.62144 | 12.7x | Generic fixed-radius/component contracts; no DBSCAN-native ABI. |
| Robot collision | `examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py` | Prepared collision flags | Prepared 3-D segment/scene any-hit flags | 0.00853798 | 0.00161413 | 5.29x | Static-scene screening, not a planner or exact swept collision solver. |
| RayDB-style grouped aggregate | `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py` | Generated 2M grouped count, steady-state prepared query | Paper-shaped generic ray/triangle grouped i64 reduction | 0.0047154 | 0.0001704 | 27.7x | Goal2652 internal prepared-query evidence on RTX A5000 only; no whole-app, SQL/DBMS, authors-code, or public speedup claim. |
| RayDB-style grouped aggregate | `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py` | Generated 2M grouped sum, steady-state prepared query | Paper-shaped generic ray/triangle grouped i64 reduction | 0.0985329 | 0.0009476 | 104.0x | Goal2652 internal prepared-query evidence on RTX A5000 only; setup, table descriptor, scene build, payload prep, and ray prep are excluded. |
| Barnes-Hut / RT-BarnesHut-style | `examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py` | Node-coverage threshold decision | Same-contract prepared node coverage | 0.0388851 | 0.00855045 | 4.55x | No app-specific force ABI; full hierarchical aggregate-frontier remains future generic primitive work. |
| LibRTS-style spatial index | `examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py` | AABB index count-only | `AABB_INDEX_QUERY_2D` | 20.707 | 0.691477 | 29.9x | Internal benchmark slice, not full mutable LibRTS reproduction. |
| RTNN neighbor search | `scripts/goal2348_rtnn_v2_2_external_runner.py` | Prepared 3-D ranked summary | Fixed-radius neighbor rows plus ranked summary | 0.2638 | 0.00153247 | 172x | Strict same-contract boundary; not a full RTNN paper reproduction. |
| Triangle counting | `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py` | RT-Graph-style RT-2A1 summary | Generic prepared 3-D ray/triangle path | 0.039049 | 0.000364401 | 107x | Graph benchmark slice; larger paper datasets require future segmented/streamed lowering. |
| Bounded contact witness / contact-manifold | `examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py` | Generic AABB broadphase plus bounded witness rows | Prepared `AABB_INDEX_QUERY_2D` plus `COLLECT_K_BOUNDED` | 0.485812 | 0.0184764 | 26.3x | Promoted benchmark for generic bounded witness collection; no native contact/collision ABI and no speedup claim; exact contact interpretation remains Python app logic. |

There are 10 promoted benchmark apps. RayDB-style grouped aggregate has two
standard matrix rows because grouped count and grouped sum are distinct
reduction contracts.

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
| GPU-RMQ learner app | `examples/v2_0/learner_apps/gpu_rmq/` | RMQ hierarchy/RT lowering pressure and generic grouped candidate argmin | Explicitly demoted learner/design-pressure app after Goal2612 |
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
| GPU-RMQ range minimum query | `examples/v2_0/learner_apps/gpu_rmq/rtdl_gpu_rmq_learner_app.py` | learner/design-pressure app for exact compact RMQ rows, hierarchy-style local contracts, paper-style generic closest-hit RT lowering, and the generic grouped candidate argmin primitive | Goal2612 rejects benchmark promotion for the current design: RTDL remains much slower than direct CUDA sparse-query code; keep it outside the benchmark app set |
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
