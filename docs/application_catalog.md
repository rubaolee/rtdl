# RTDL Application Catalog

This page is the public inventory of runnable RTDL application examples.
It answers two practical questions for users:

- Which complete app-shaped examples exist today?
- Which examples are spatial joins or spatial-join-like workloads?

The boundary is important: RTDL owns traversal, candidate discovery,
refinement, and row emission. Python owns application orchestration,
post-processing, policy decisions, and presentation. These examples are not
full GIS, database, robotics, clustering, or simulation systems.

For app-level support across CPU/Python, Embree, OptiX, Vulkan, HIPRT, and
Apple RT, see the [App Engine Support Matrix](app_engine_support_matrix.md).

## Spatial Join And Proximity Apps

Yes, RTDL has spatial join apps. The current public surface includes both
direct spatial joins and app-level proximity joins.

| App | File | What data becomes | RTDL feature shape |
| --- | --- | --- | --- |
| Service coverage gaps | `examples/rtdl_service_coverage_gaps.py` | households plus clinic locations become uncovered household IDs | radius spatial join with `fixed_radius_neighbors` |
| Event hotspot screening | `examples/rtdl_event_hotspot_screening.py` | events become hotspot event IDs after an event/event radius self-join | radius self-join with `fixed_radius_neighbors` |
| Facility KNN assignment | `examples/rtdl_facility_knn_assignment.py` | customers plus depots become nearest depot assignments | KNN spatial join with `knn_rows` |
| Road hazard screening | `examples/rtdl_road_hazard_screening.py` | road segments plus hazard polygons become per-road hit counts | segment/polygon spatial join |
| Segment/polygon hit count | `examples/rtdl_segment_polygon_hitcount.py` | segments plus polygons become per-segment intersection counts | direct segment/polygon join |
| Segment/polygon any-hit rows | `examples/rtdl_segment_polygon_anyhit_rows.py` | segments plus polygons become intersecting segment/polygon pairs | direct segment/polygon join |
| Polygon-pair overlap rows | `examples/rtdl_polygon_pair_overlap_area_rows.py` | polygon pairs become overlap-area rows | bounded polygon/polygon overlap join |
| Polygon-set Jaccard | `examples/rtdl_polygon_set_jaccard.py` | polygon sets become Jaccard-similarity rows | bounded polygon-set overlap join |

External comparison scripts for indexed SQL/GIS baselines live under
`docs/sql/`, including the v0.4 app comparisons and v0.2 PostGIS geometry
workloads. PostGIS is an external baseline and correctness/performance anchor,
not an RTDL backend.

## Paper-Derived And App-Building Examples

These examples show RTDL kernels embedded inside Python applications. They use
the ITRE model: input, traverse, refine, emit.

| App | File | What data becomes | RTDL role |
| --- | --- | --- | --- |
| Hausdorff distance | `examples/rtdl_hausdorff_distance_app.py` | two point sets become nearest-neighbor rows and one directed Hausdorff distance | emit KNN rows, reduce max distance in Python |
| ANN candidate search | `examples/rtdl_ann_candidate_app.py` | queries plus a Python-selected candidate subset become nearest rows and recall metrics | exact KNN over candidate subsets |
| Outlier detection | `examples/rtdl_outlier_detection_app.py` | points become neighbor rows, density counts, and outlier labels | radius-neighbor rows plus Python thresholding |
| DBSCAN clustering | `examples/rtdl_dbscan_clustering_app.py` | points become neighbor rows, core counts, and cluster labels | radius-neighbor rows plus Python expansion |
| Robot collision screening | `examples/rtdl_robot_collision_screening_app.py` | robot link rays plus obstacle triangles become pose collision flags | any-hit rows plus `rt.reduce_rows(any)` |
| Barnes-Hut force approximation | `examples/rtdl_barnes_hut_force_app.py` | bodies plus tree nodes become candidate rows and approximate force vectors | candidate generation; Python force reduction |

## DB-Style App Examples

The primary DB app is unified. The bounded v0.7 DB line demonstrates
analytical row workloads without claiming to be a DBMS.

| App | File | What data becomes | Boundary |
| --- | --- | --- | --- |
| Unified database analytics | `examples/rtdl_database_analytics_app.py` | order tables become regional dashboard rows and sales-risk summaries | primary DB app entry point |
| Sales risk screening | `examples/rtdl_sales_risk_screening.py` | orders plus predicates become risky order IDs, grouped counts, and grouped revenue | bounded DB kernels inside app logic |
| Regional order dashboard | `examples/rtdl_v0_7_db_app_demo.py` | a denormalized order table becomes scan and grouped JSON results | app-level prepared dataset demo |
| DB kernel-form demo | `examples/rtdl_v0_7_db_kernel_app_demo.py` | the same order workload becomes explicit RTDL kernel-form rows | kernel syntax demonstration |
| Conjunctive scan | `examples/rtdl_db_conjunctive_scan.py` | rows plus predicates become matching row IDs | bounded filter primitive |
| Grouped count | `examples/rtdl_db_grouped_count.py` | filtered rows become grouped counts | bounded aggregate primitive |
| Grouped sum | `examples/rtdl_db_grouped_sum.py` | filtered rows become grouped sums | bounded aggregate primitive |

`examples/rtdl_database_analytics_app.py` is the preferred user-facing DB app
because it unifies the regional dashboard and sales-risk screening scenarios.
The older scenario-specific files remain runnable compatibility examples.

## Graph App Examples

The primary graph app is unified over the two released v0.6.1 graph kernels.

| App | File | What data becomes | Boundary |
| --- | --- | --- | --- |
| Unified graph analytics | `examples/rtdl_graph_analytics_app.py` | graph inputs become BFS discovery rows and triangle rows | primary graph app entry point |
| BFS one-step example | `examples/rtdl_graph_bfs.py` | frontier vertices become discovered vertices | bounded graph traversal primitive |
| Triangle-count example | `examples/rtdl_graph_triangle_count.py` | seed edges become triangle rows | bounded graph intersection primitive |

This is a graph-kernel app surface, not a graph database or distributed graph
analytics system.

## Visibility And Ray Query Examples

| Example | File | What data becomes | Boundary |
| --- | --- | --- | --- |
| Any-hit blocker rows | `examples/rtdl_ray_triangle_any_hit.py` | rays plus triangles become `{ray_id, any_hit}` rows | bounded yes/no blocker primitive |
| Visibility rows | `examples/rtdl_visibility_rows.py` | observers, targets, and blockers become visibility rows | standard-library line-of-sight helper |
| Unified Apple RT demo | `examples/rtdl_apple_rt_demo_app.py` | Apple RT closest-hit and visibility-count scenarios become one app JSON result | primary Apple RT demo entry point |
| Apple RT visibility count | `examples/rtdl_apple_rt_visibility_count.py` | repeated 2D rays plus blockers become one scalar blocked-ray count | scenario-specific prepared/prepacked Apple RT count path |
| Apple RT closest hit | `examples/rtdl_apple_rt_closest_hit.py` | 3D rays plus triangles become nearest-hit rows | scenario-specific Apple Metal/MPS RT closest-hit slice |
| HIPRT hit count | `examples/rtdl_hiprt_ray_triangle_hitcount.py` | 3D rays plus triangles become per-ray hit counts | Linux HIPRT SDK path |

## Beginner And Reference Examples

Use these first when learning the language surface:

- `examples/rtdl_hello_world.py`
- `examples/rtdl_hello_world_backends.py`
- `examples/rtdl_feature_quickstart_cookbook.py`
- `examples/rtdl_fixed_radius_neighbors.py`
- `examples/rtdl_knn_rows.py`
- `examples/rtdl_graph_bfs.py`
- `examples/rtdl_graph_triangle_count.py`
- `examples/rtdl_reduce_rows.py`

Files under `examples/reference/`, `examples/generated/`, and
`examples/internal/` are preserved for tests, fixtures, generated artifacts, or
auditability. They are not the recommended public starting point.

## Honesty Boundary

- Spatial-join examples are bounded examples, not a full GIS engine.
- DB examples are bounded analytical kernels, not SQL, transactions, indexes,
  query planning, or a DBMS.
- App examples intentionally combine RTDL and Python. If an app uses Python for
  orchestration or reduction, that is the intended programming model unless a
  native backend helper is explicitly documented.
- Backend support and native/assisted/fallback status are defined in
  `docs/features/engine_support_matrix.md`.
