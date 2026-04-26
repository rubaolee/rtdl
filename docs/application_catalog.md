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

## NVIDIA RT-Core Claim-Sensitive Runs

Use `--require-rt-core` when a script or benchmark is intended to make a real
NVIDIA RT-core claim. The flag is deliberately stricter than `--backend optix`:
it fails before backend dispatch unless the selected app mode is a documented
bounded OptiX traversal path with a narrow claim scope.

Current paths ready for RTX claim review:

| App | Claim-sensitive command shape | Current claim scope |
| --- | --- | --- |
| Database analytics | `--backend optix --output-mode compact_summary --require-rt-core` | prepared compact DB traversal/filter/grouping summary with materialization-free native continuation only; no SQL engine, DBMS, full dashboard, or row-materializing speedup claim |
| Graph analytics | `--backend optix --scenario visibility_edges --require-rt-core` | graph visibility-edge filtering plus native graph-ray candidate-generation sub-paths only; not whole graph-system speedup |
| Service coverage gaps | `--backend optix --optix-summary-mode gap_summary_prepared --require-rt-core` | prepared scalar covered/uncovered count only; household IDs require rows or Embree summary mode |
| Event hotspot screening | `--backend optix --optix-summary-mode count_summary_prepared --require-rt-core` | prepared scalar hotspot count only; hotspot IDs require rows or Embree summary mode |
| Facility KNN assignment | `--backend optix --optix-summary-mode coverage_threshold_prepared --require-rt-core` | scalar service-radius coverage decision only; ranked nearest-depot assignment and uncovered-ID witnesses remain outside the claim |
| Road hazard screening | `--backend optix --output-mode summary --optix-mode native --require-rt-core` | prepared road-hazard compact summary only; no GIS/routing or default-app speedup claim |
| Segment/polygon hit count | Goal933 prepared profiler | prepared native compact hit-count traversal only; no broad segment/polygon speedup claim |
| Segment/polygon any-hit rows | Goal934 prepared profiler | prepared bounded pair-row traversal only; no unbounded row-volume speedup claim |
| Polygon pair overlap rows | `--backend optix --require-rt-core` | native-assisted LSI/PIP candidate discovery plus native C++ exact area continuation; no monolithic GPU polygon-area speedup claim |
| Polygon set Jaccard | `--backend optix --require-rt-core` | native-assisted LSI/PIP candidate discovery plus native C++ exact set-area/Jaccard continuation; no monolithic GPU Jaccard speedup claim |
| Hausdorff distance | `--backend optix --optix-summary-mode directed_threshold_prepared --require-rt-core` | prepared Hausdorff <= radius decision only; no exact-distance speedup claim |
| ANN candidate search | `--backend optix --optix-summary-mode candidate_threshold_prepared --require-rt-core` | prepared scalar candidate-coverage decision only; no ANN index, ranking, or uncovered-query witness speedup claim |
| Outlier detection | `--backend optix --optix-summary-mode rt_count_threshold_prepared --output-mode density_count` | prepared scalar fixed-radius density-threshold count; per-point outlier labels require `density_summary` |
| DBSCAN clustering | `--backend optix --optix-summary-mode rt_core_flags_prepared --output-mode core_count` | prepared scalar core count only; per-point core flags require `core_flags` and Python cluster expansion remains host-side |
| Robot collision screening | `--backend optix --optix-summary-mode prepared_count` or `prepared_pose_flags` | prepared any-hit count or pose flags; witness rows remain outside the compact claim |
| Barnes-Hut force approximation | `--backend optix --optix-summary-mode node_coverage_prepared --require-rt-core` | prepared node-coverage decision only; no force-vector or opening-rule speedup claim |

These rows are claim-review candidates, not release authorization and not
automatic speedup claims. The support matrix and current claim-review package
define the exact scope. Still outside public NVIDIA RT-core claims: SQL/DBMS
behavior, row-materializing DB output, full GIS/routing behavior, unbounded
segment/polygon pair-row output, exact Hausdorff distance, ANN index/ranking,
Barnes-Hut opening-rule/force reduction, and broad whole-app speedup.
The machine-readable public wording source is
`rtdsl.rtx_public_wording_matrix()` via the
[App Engine Support Matrix](app_engine_support_matrix.md) and
[v1.0 RTX App Status](v1_0_rtx_app_status.md). In particular,
`robot_collision_screening / prepared_pose_flags` is a real bounded RT-core
path but remains blocked for public RTX speedup wording until the 100 ms
evidence gate is cleared and reviewed.

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
| Service coverage gaps | `examples/rtdl_service_coverage_gaps.py` | households plus clinic locations become uncovered household IDs in row/Embree-summary modes or scalar covered/uncovered counts in OptiX prepared mode | radius spatial join with `fixed_radius_neighbors`; compact OptiX gap-summary path uses scalar threshold-count continuation |
| Event hotspot screening | `examples/rtdl_event_hotspot_screening.py` | events become hotspot event IDs in row/Embree-summary modes or scalar hotspot count in OptiX prepared mode | radius self-join with `fixed_radius_neighbors`; compact OptiX count-summary path uses scalar threshold-count continuation |
| Facility KNN assignment | `examples/rtdl_facility_knn_assignment.py` | customers plus depots become nearest depot assignments or a scalar service-radius coverage decision | KNN spatial join with `knn_rows`; optional OptiX `coverage_threshold_prepared` maps the coverage-decision form to scalar fixed-radius traversal and reports native threshold-count continuation |
| Road hazard screening | `examples/rtdl_road_hazard_screening.py` | road segments plus hazard polygons become per-road hit counts | segment/polygon spatial join |
| Segment/polygon hit count | `examples/rtdl_segment_polygon_hitcount.py` | segments plus polygons become per-segment intersection counts | direct segment/polygon join |
| Segment/polygon any-hit rows | `examples/rtdl_segment_polygon_anyhit_rows.py` | segments plus polygons become intersecting segment/polygon pairs | direct segment/polygon join |
| Polygon-pair overlap rows | `examples/rtdl_polygon_pair_overlap_area_rows.py` | polygon pairs become overlap-area rows | bounded polygon/polygon overlap join |
| Polygon-set Jaccard | `examples/rtdl_polygon_set_jaccard.py` | polygon sets become Jaccard-similarity rows | bounded polygon-set overlap join |

The polygon-pair overlap and polygon-set Jaccard apps expose Embree
native-assisted mode: Embree performs positive candidate discovery through
segment-intersection and point-in-polygon kernels, then native C++ exact
grid-cell continuation computes the released area/Jaccard rows. This avoids
full overlay-matrix materialization and removes Python exact-refinement loops
from the native-assisted app path, but it is not a monolithic GPU or Embree
area-overlay kernel.

External comparison scripts for indexed SQL/GIS baselines live under
`docs/sql/`, including the v0.4 app comparisons and v0.2 PostGIS geometry
workloads. PostGIS is an external baseline and correctness/performance anchor,
not an RTDL backend.

## Paper-Derived And App-Building Examples

These examples show RTDL kernels embedded inside Python applications. They use
the ITRE model: input, traverse, refine, emit.

| App | File | What data becomes | RTDL role |
| --- | --- | --- | --- |
| Hausdorff distance | `examples/rtdl_hausdorff_distance_app.py` | two point sets become nearest-neighbor rows, one directed Hausdorff distance, or a Hausdorff <= radius decision | emit KNN rows and reduce max distance in Python; optional Embree `directed_summary` keeps directed max reduction native and reports native continuation; optional OptiX `directed_threshold_prepared` maps the decision form to fixed-radius traversal and reports native continuation |
| ANN candidate search | `examples/rtdl_ann_candidate_app.py` | queries plus a Python-selected candidate subset become nearest rows, native C++ rerank summaries, recall metrics, or a scalar candidate-coverage decision | exact KNN over candidate subsets; compact rerank summaries use native C++ continuation for row/query/rank counts while Python still owns exact quality comparison; optional OptiX `candidate_threshold_prepared` maps the coverage-decision form to scalar fixed-radius traversal |
| Outlier detection | `examples/rtdl_outlier_detection_app.py` | points become neighbor rows, density counts, outlier labels, or scalar outlier counts | radius-neighbor rows plus Python thresholding; optional OptiX `rt_count_threshold_prepared` with `density_count` emits only scalar threshold/outlier counts, while `density_summary` keeps per-point labels |
| DBSCAN clustering | `examples/rtdl_dbscan_clustering_app.py` | points become neighbor rows, core counts, core flags, or cluster labels | radius-neighbor rows plus Python expansion; optional OptiX `rt_core_flags_prepared` with `core_count` emits only scalar core counts, while `core_flags` keeps per-point labels and full cluster expansion remains outside the native path |
| Robot collision screening | `examples/rtdl_robot_collision_screening_app.py` | robot link rays plus obstacle triangles become pose collision flags | any-hit rows plus `rt.reduce_rows(any)`; compact row-output modes reduce payload size, while prepared OptiX count/pose-flag modes report native continuation and avoid per-ray row materialization |
| Barnes-Hut force approximation | `examples/rtdl_barnes_hut_force_app.py` | bodies plus tree nodes become candidate rows, native C++ candidate summaries, a node-coverage decision, and approximate force vectors | candidate generation; compact candidate summaries use native C++ continuation while Python still owns opening-rule evaluation and force reduction; optional OptiX `node_coverage_prepared` maps the node-coverage decision to fixed-radius traversal |

## Spatial Join App Summary Modes

Some spatial apps expose optional Embree summary modes when the app needs only
compact answers instead of all emitted neighbor rows.

| App | Summary mode | What it returns | Boundary |
| --- | --- | --- | --- |
| `examples/rtdl_database_analytics_app.py` | `--output-mode summary` with `--copies N` | regional dashboard and sales-risk aggregate summaries over repeated deterministic DB fixtures | scales bounded DB kernels for Embree characterization while omitting full row lists from JSON |
| `examples/rtdl_graph_analytics_app.py` | `--output-mode summary` with `--copies N` | BFS discovery counts and triangle-count summaries over repeated deterministic graph fixtures | scales the public graph app for Embree characterization while omitting full discovery/triangle rows from JSON; top-level metadata propagates native continuation from graph sub-sections |
| `examples/rtdl_service_coverage_gaps.py` | `--embree-summary-mode gap_summary`; OptiX `--optix-summary-mode gap_summary_prepared` | Embree covered/uncovered household summary rows or OptiX scalar covered/uncovered counts | OptiX scalar mode omits household ids, clinic ids, distances, and clinic-load counts |
| `examples/rtdl_event_hotspot_screening.py` | `--embree-summary-mode count_summary`; OptiX `--optix-summary-mode count_summary_prepared` | Embree neighbor-count rows plus hotspot flags or OptiX scalar hotspot count | OptiX scalar mode omits hotspot event ids, neighbor-pair rows, and distances |
| `examples/rtdl_facility_knn_assignment.py` | `--output-mode primary_assignments` / `summary`; OptiX `--optix-summary-mode coverage_threshold_prepared` | primary depot assignments, depot-load summaries, or a scalar service-coverage decision | KNN modes use K=1 and omit K=3 fallback choices; OptiX threshold mode does not claim ranked assignment or uncovered-customer witnesses |
| `examples/rtdl_hausdorff_distance_app.py` | `--embree-result-mode directed_summary` | directed Hausdorff distance and witness summaries | omits full KNN rows |
| `examples/rtdl_ann_candidate_app.py` | `--output-mode rerank_summary` / `quality_summary`; OptiX `--optix-summary-mode candidate_threshold_prepared` | native C++ candidate-rerank summaries, compact recall/distance metrics, or a scalar candidate-coverage decision | separates RTDL candidate-subset KNN reranking from Python exact full-set quality comparison; OptiX threshold mode does not claim full ANN indexing, ranking, or uncovered-query witnesses |
| `examples/rtdl_robot_collision_screening_app.py` | `--output-mode hit_count` / `pose_flags`; OptiX `--optix-summary-mode prepared_count` / `prepared_pose_flags` | hit-edge counts or pose collision flags | row-output modes omit full witness rows; prepared OptiX modes report native continuation and avoid per-ray row materialization |
| `examples/rtdl_segment_polygon_anyhit_rows.py` | `--output-mode segment_counts` / `segment_flags` | one hit-count or any-hit flag row per segment | omits polygon ids and pair rows |
| `examples/rtdl_road_hazard_screening.py` | `--output-mode priority_segments` / `summary` | priority road ids and counts | omits full per-road hit-count rows from the JSON payload |
| `examples/rtdl_polygon_pair_overlap_area_rows.py` | `--output-mode summary` | aggregate overlap-pair count and total areas | omits full per-pair area rows; Embree/OptiX app paths use positive LSI/PIP candidate discovery |
| `examples/rtdl_barnes_hut_force_app.py` | `--output-mode candidate_summary` / `force_summary`; OptiX `--optix-summary-mode node_coverage_prepared` | native C++ candidate-generation summaries, force-reduction summaries, or a node-coverage decision | separates RTDL candidate generation from Python Barnes-Hut opening-rule/force reduction; OptiX threshold mode does not claim opening-rule or force-vector acceleration |

## DB-Style App Examples

The primary DB app is unified. The bounded v0.7 DB line demonstrates
analytical row workloads without claiming to be a DBMS.

| App | File | What data becomes | Boundary |
| --- | --- | --- | --- |
| Unified database analytics | `examples/rtdl_database_analytics_app.py` | order tables become regional dashboard rows and sales-risk summaries | primary DB app entry point; materialization-free compact DB summary runs report native continuation |
| Conjunctive scan | `examples/rtdl_db_conjunctive_scan.py` | rows plus predicates become matching row IDs | bounded filter primitive |
| Grouped count | `examples/rtdl_db_grouped_count.py` | filtered rows become grouped counts | bounded aggregate primitive |
| Grouped sum | `examples/rtdl_db_grouped_sum.py` | filtered rows become grouped sums | bounded aggregate primitive |

`examples/rtdl_database_analytics_app.py` is the preferred user-facing DB app
because it unifies the regional dashboard and sales-risk screening scenarios.
The older scenario-specific files remain runnable compatibility helpers for
historical tests and imports, but they are retired from the public app catalog.
The unified app also supports `--copies N --output-mode summary` for scalable
Embree characterization while keeping the default small full-output fixture.
For DB native-continuation metadata, only materialization-free compact summary
paths report `native_continuation_active`; full output, summary output, or
fallback compact paths that still materialize grouped rows remain explicitly
outside the native-continuation claim.

## Graph App Examples

The primary graph app is unified over the two released v0.6.1 graph kernels.

| App | File | What data becomes | Boundary |
| --- | --- | --- | --- |
| Unified graph analytics | `examples/rtdl_graph_analytics_app.py` | graph inputs become BFS discovery rows and triangle rows, then optional native C++ summaries | primary graph app entry point |
| BFS one-step example | `examples/rtdl_graph_bfs.py` | frontier vertices become discovered vertices, then optional native C++ discovery summaries | bounded graph traversal primitive |
| Triangle-count example | `examples/rtdl_graph_triangle_count.py` | seed edges become triangle rows, then optional native C++ triangle summaries | bounded graph intersection primitive |

This is a graph-kernel app surface, not a graph database or distributed graph
analytics system. The unified app also supports
`--copies N --output-mode summary` for scalable Embree characterization:
the default remains the small row-emitting tutorial fixture, while summary
mode repeats the deterministic BFS and triangle fixtures and sends emitted rows
through the native C++ oracle continuation to return compact counts instead of
full emitted rows.

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
