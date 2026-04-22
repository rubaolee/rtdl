# RTDL Application Catalog

This page is the public inventory of runnable RTDL application examples.
It answers two practical questions for users:

- Which complete app-shaped examples exist today?
- Which examples are spatial joins or spatial-join-like workloads?

The boundary is important: RTDL owns traversal, candidate discovery,
refinement, and row emission. Python owns application orchestration,
post-processing, policy decisions, and presentation. These examples are not
full GIS, database, robotics, clustering, or simulation systems.

RTDL owns the accelerated core only when the app routes that core through an
RTDL backend traversal, BVH, point-query, ray-query, or native spatial-query
primitive. Python orchestration is expected, but Python-only post-processing
must not be described as backend acceleration. In particular, `--backend optix`
is not by itself a NVIDIA RT-core claim; that claim requires a measured OptiX
traversal path on RTX-class hardware.

For app-level support across CPU/Python, Embree, OptiX, Vulkan, HIPRT, and
Apple RT, see the [App Engine Support Matrix](app_engine_support_matrix.md).

The original RTDL root spatial workloads are still first-class:
[LSI](features/lsi/README.md) turns segment sets into segment-intersection
rows, and [PIP](features/pip/README.md) turns point/polygon inputs into
containment rows. Current Embree evidence is recorded in
[Goal 742](reports/goal742_lsi_pip_root_workload_refresh_2026-04-21.md); the
polygon apps below reuse these root primitives for candidate discovery before
application-specific refinement or reduction.

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

The polygon-pair overlap and polygon-set Jaccard apps expose Embree
native-assisted mode: Embree performs positive candidate discovery through
segment-intersection and point-in-polygon kernels, then CPU/Python exact
grid-cell area refinement computes the released area/Jaccard rows. This avoids
full overlay-matrix materialization inside the apps, but it is not a fully
native Embree area-overlay kernel.

External comparison scripts for indexed SQL/GIS baselines live under
`docs/sql/`, including the v0.4 app comparisons and v0.2 PostGIS geometry
workloads. PostGIS is an external baseline and correctness/performance anchor,
not an RTDL backend.

## Paper-Derived And App-Building Examples

These examples show RTDL kernels embedded inside Python applications. They use
the ITRE model: input, traverse, refine, emit.

| App | File | What data becomes | RTDL role |
| --- | --- | --- | --- |
| Hausdorff distance | `examples/rtdl_hausdorff_distance_app.py` | two point sets become nearest-neighbor rows and one directed Hausdorff distance | emit KNN rows, reduce max distance in Python; optional Embree `directed_summary` keeps directed max reduction native |
| ANN candidate search | `examples/rtdl_ann_candidate_app.py` | queries plus a Python-selected candidate subset become nearest rows and recall metrics | exact KNN over candidate subsets; compact rerank summaries expose the RTDL/Embree slice separately from Python exact quality comparison |
| Outlier detection | `examples/rtdl_outlier_detection_app.py` | points become neighbor rows, density counts, and outlier labels | radius-neighbor rows plus Python thresholding; optional OptiX `rt_count_threshold_prepared` uses prepared traversal and Embree `rt_count_threshold_prepared` uses prepared CPU BVH traversal to emit one density-threshold summary row per query |
| DBSCAN clustering | `examples/rtdl_dbscan_clustering_app.py` | points become neighbor rows, core counts, and cluster labels | radius-neighbor rows plus Python expansion; optional OptiX `rt_core_flags_prepared` uses prepared traversal and Embree `rt_core_flags_prepared` uses prepared CPU BVH traversal to emit core flags only, not full cluster expansion |
| Robot collision screening | `examples/rtdl_robot_collision_screening_app.py` | robot link rays plus obstacle triangles become pose collision flags | any-hit rows plus `rt.reduce_rows(any)`; compact output modes and scaled fixtures expose Embree any-hit performance without full witness rows |
| Barnes-Hut force approximation | `examples/rtdl_barnes_hut_force_app.py` | bodies plus tree nodes become candidate rows and approximate force vectors | candidate generation; compact candidate summaries expose the RTDL/Embree slice separately from Python force reduction |

## Spatial Join App Summary Modes

Some spatial apps expose optional Embree summary modes when the app needs only
compact answers instead of all emitted neighbor rows.

| App | Summary mode | What it returns | Boundary |
| --- | --- | --- | --- |
| `examples/rtdl_database_analytics_app.py` | `--output-mode summary` with `--copies N` | regional dashboard and sales-risk aggregate summaries over repeated deterministic DB fixtures | scales bounded DB kernels for Embree characterization while omitting full row lists from JSON |
| `examples/rtdl_graph_analytics_app.py` | `--output-mode summary` with `--copies N` | BFS discovery counts and triangle-count summaries over repeated deterministic graph fixtures | scales the public graph app for Embree characterization while omitting full discovery/triangle rows from JSON |
| `examples/rtdl_service_coverage_gaps.py` | `--embree-summary-mode gap_summary` | covered/uncovered household summary rows | omits clinic ids, distances, and clinic-load counts |
| `examples/rtdl_event_hotspot_screening.py` | `--embree-summary-mode count_summary` | one neighbor-count row per event plus hotspot flags | omits neighbor-pair rows and distances |
| `examples/rtdl_facility_knn_assignment.py` | `--output-mode primary_assignments` / `summary` | primary depot assignments or depot-load summaries | uses K=1 and omits K=3 fallback choices |
| `examples/rtdl_hausdorff_distance_app.py` | `--embree-result-mode directed_summary` | directed Hausdorff distance and witness summaries | omits full KNN rows |
| `examples/rtdl_ann_candidate_app.py` | `--output-mode rerank_summary` / `quality_summary` | candidate-rerank summaries or compact recall/distance metrics | separates RTDL candidate-subset KNN reranking from Python exact full-set quality comparison |
| `examples/rtdl_robot_collision_screening_app.py` | `--output-mode hit_count` / `pose_flags` | hit-edge counts or pose collision flags | omits full witness rows; Embree still uses native any-hit row path internally |
| `examples/rtdl_segment_polygon_anyhit_rows.py` | `--output-mode segment_counts` / `segment_flags` | one hit-count or any-hit flag row per segment | omits polygon ids and pair rows |
| `examples/rtdl_road_hazard_screening.py` | `--output-mode priority_segments` / `summary` | priority road ids and counts | omits full per-road hit-count rows from the JSON payload |
| `examples/rtdl_polygon_pair_overlap_area_rows.py` | `--output-mode summary` | aggregate overlap-pair count and total areas | omits full per-pair area rows; Embree app path uses positive LSI/PIP candidate discovery |
| `examples/rtdl_barnes_hut_force_app.py` | `--output-mode candidate_summary` / `force_summary` | candidate-generation summaries or force-reduction summaries | separates RTDL candidate generation from Python Barnes-Hut force reduction |

## DB-Style App Examples

The primary DB app is unified. The bounded v0.7 DB line demonstrates
analytical row workloads without claiming to be a DBMS.

| App | File | What data becomes | Boundary |
| --- | --- | --- | --- |
| Unified database analytics | `examples/rtdl_database_analytics_app.py` | order tables become regional dashboard rows and sales-risk summaries | primary DB app entry point |
| Conjunctive scan | `examples/rtdl_db_conjunctive_scan.py` | rows plus predicates become matching row IDs | bounded filter primitive |
| Grouped count | `examples/rtdl_db_grouped_count.py` | filtered rows become grouped counts | bounded aggregate primitive |
| Grouped sum | `examples/rtdl_db_grouped_sum.py` | filtered rows become grouped sums | bounded aggregate primitive |

`examples/rtdl_database_analytics_app.py` is the preferred user-facing DB app
because it unifies the regional dashboard and sales-risk screening scenarios.
The older scenario-specific files remain runnable compatibility helpers for
historical tests and imports, but they are retired from the public app catalog.
The unified app also supports `--copies N --output-mode summary` for scalable
Embree characterization while keeping the default small full-output fixture.

## Graph App Examples

The primary graph app is unified over the two released v0.6.1 graph kernels.

| App | File | What data becomes | Boundary |
| --- | --- | --- | --- |
| Unified graph analytics | `examples/rtdl_graph_analytics_app.py` | graph inputs become BFS discovery rows and triangle rows | primary graph app entry point |
| BFS one-step example | `examples/rtdl_graph_bfs.py` | frontier vertices become discovered vertices | bounded graph traversal primitive |
| Triangle-count example | `examples/rtdl_graph_triangle_count.py` | seed edges become triangle rows | bounded graph intersection primitive |

This is a graph-kernel app surface, not a graph database or distributed graph
analytics system. The unified app also supports
`--copies N --output-mode summary` for scalable Embree characterization:
the default remains the small row-emitting tutorial fixture, while summary
mode repeats the deterministic BFS and triangle fixtures and returns compact
counts instead of full emitted rows.

## Visibility And Ray Query Examples

| Example | File | What data becomes | Boundary |
| --- | --- | --- | --- |
| Any-hit blocker rows | `examples/rtdl_ray_triangle_any_hit.py` | rays plus triangles become `{ray_id, any_hit}` rows | bounded yes/no blocker primitive |
| Visibility rows | `examples/rtdl_visibility_rows.py` | observers, targets, and blockers become visibility rows | standard-library line-of-sight helper |
| Unified Apple RT demo | `examples/rtdl_apple_rt_demo_app.py` | Apple RT closest-hit and visibility-count scenarios become one app JSON result | primary Apple RT demo entry point |
| HIPRT hit count | `examples/rtdl_hiprt_ray_triangle_hitcount.py` | 3D rays plus triangles become per-ray hit counts | Linux HIPRT SDK path |

The older Apple RT closest-hit and visibility-count scenario files remain
runnable compatibility helpers, but users should start from the unified Apple
RT demo app.

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
- The optional OptiX summary modes in the outlier and DBSCAN apps are bounded
  fixed-radius prototypes. They do not imply KNN, Hausdorff, ANN, Barnes-Hut,
  or general clustering acceleration.
- Backend support and native/assisted/fallback status are defined in
  `docs/features/engine_support_matrix.md`.
