# v1.0 App Acceleration Inventory

Status: current-main v1.0 documentation aid.

This page explains what RTDL accelerates in each public app and what remains
outside the accelerated claim. It is not a release authorization and not a
whole-app speedup table.

The v1.0 architecture intentionally contains app-specific native continuations.
That is acceptable for v1.0 because the goal is to prove the RTDL model against
real app-shaped workloads. These continuations are v1.0 proof machinery, not the
final architecture. They are also technical debt: v1.5 should replace these
app-specific continuations with reviewed generic traversal-plus-reduction
primitives.

## Reading The Table

- `RT-accelerated part`: the traversal or spatial-query phase that can run
  through RTDL's RT-capable backend path.
- `v1.0 native continuation`: app-specific native work used today to avoid
  materializing excessive rows or to compute compact summaries.
- `Still outside`: work that must not be described as RT-core accelerated or as
  a public speedup claim unless a later review explicitly authorizes it.
- `Public wording`: current public RTX wording state. Reviewed means bounded
  sub-path wording only.

## Inventory

| App | RT-accelerated part | v1.0 native continuation | Still outside | Public wording |
| --- | --- | --- | --- | --- |
| `database_analytics` | Prepared DB compact-summary traversal/filter/grouping. | Materialization-free compact DB summaries. | SQL engine behavior, DBMS claims, full dashboard output, row materialization, and broad DB speedup. | Not reviewed. |
| `graph_analytics` | Visibility-edge any-hit and native graph-ray candidate generation. | Native graph section summaries after selected graph sections. | BFS frontier control, triangle set intersection, graph database behavior, distributed analytics, and whole graph-app speedup. | Blocked because current same-contract OptiX evidence is slower than Embree. |
| `apple_rt_demo` | Apple Metal/MPS RT closest-hit and visibility-count demo paths. | Apple-specific native/native-assisted demo handling. | NVIDIA RTX wording and cross-backend RTX speedup claims. | Not a NVIDIA public wording target. |
| `service_coverage_gaps` | Prepared fixed-radius gap-summary traversal. | Covered/uncovered compact summary paths. | Household IDs, clinic IDs, distances, clinic loads, and whole service-coverage optimization. | Reviewed bounded sub-path. |
| `event_hotspot_screening` | Prepared fixed-radius count-summary traversal. | Hotspot count summaries. | Hotspot ID rows, neighbor-pair rows, distances, and whole hotspot analytics. | Reviewed bounded sub-path. |
| `facility_knn_assignment` | Prepared fixed-radius service-coverage decision. | Coverage-threshold decision summaries. | Ranked nearest-depot assignment, fallback choices, facility-location optimization, and whole-app speedup. | Reviewed bounded sub-path. |
| `road_hazard_screening` | Prepared native segment/polygon road-hazard compact-summary traversal. | Compact hazard summary counts. | Full GIS/routing, default app behavior, row output, and whole road-hazard speedup. | Reviewed bounded sub-path. |
| `segment_polygon_hitcount` | Prepared native segment/polygon hit-count traversal. | Compact hit-count summary. | Pair-row output and broad segment/polygon app speedup. | Reviewed bounded sub-path. |
| `segment_polygon_anyhit_rows` | Prepared bounded native segment/polygon pair-row traversal. | Bounded row emitter with overflow metadata. | Unbounded row-volume performance and default app behavior. | Reviewed bounded sub-path. |
| `polygon_pair_overlap_area_rows` | Native-assisted LSI/PIP candidate discovery. | Native C++ exact area continuation after candidate discovery. | Monolithic GPU polygon-area overlay, arbitrary polygon geometry claims, Python setup, and whole polygon-overlap speedup. | Blocked because current same-contract OptiX evidence is slower than Embree. |
| `polygon_set_jaccard` | Native-assisted LSI/PIP candidate discovery. | Native C++ exact set-area/Jaccard continuation after candidate discovery. | Monolithic GPU Jaccard, larger diagnostic chunk failures, arbitrary polygon geometry claims, and whole-app speedup. | Not reviewed. |
| `hausdorff_distance` | Prepared fixed-radius Hausdorff threshold-decision traversal. | Directed-threshold decision continuation. | Exact Hausdorff distance, KNN rows, nearest-neighbor ranking, witness output, and whole-app speedup. | Reviewed bounded sub-path. |
| `ann_candidate_search` | Prepared fixed-radius candidate-coverage decision. | Candidate rerank summaries for selected modes. | Full ANN indexing, FAISS/HNSW/IVF/PQ behavior, nearest-neighbor ranking, recall policy, and whole ANN speedup. | Reviewed bounded sub-path. |
| `outlier_detection` | Prepared fixed-radius scalar density-threshold traversal. | Scalar density/outlier count continuation. | Per-point labels, full anomaly-detection behavior, and row-returning paths. | Reviewed bounded sub-path. |
| `dbscan_clustering` | Prepared fixed-radius scalar core-count traversal. | Scalar core-count/core-flag continuation. | Full DBSCAN cluster expansion, per-point clustering labels, and whole clustering speedup. | Reviewed bounded sub-path. |
| `robot_collision_screening` | Prepared ray/triangle any-hit count or pose-flag traversal. | Prepared count and pose-flag summaries. | Robot kinematics, scene construction, ray packing, witness rows, continuous collision detection, Python input construction, and whole robot-planning speedup. | Reviewed normalized per-pose sub-path wording only. |
| `barnes_hut_force_app` | Prepared fixed-radius Barnes-Hut node-coverage decision. | Native candidate summaries for compact modes. | Opening-rule evaluation, candidate-row output, force-vector reduction, N-body simulation, and whole-app speedup. | Reviewed bounded sub-path. |
| `hiprt_ray_triangle_hitcount` | HIPRT-specific ray/triangle hit-count validation. | HIPRT prepared hit-count path where available. | NVIDIA RTX wording, AMD GPU claims unless separately validated, and broad HIPRT speedup claims. | Not a NVIDIA public wording target. |

## v1.5 Replacement Target

The v1.5 target is not to remove Python orchestration. Python should remain the
control plane. The target is to replace app-specific native continuations with a
small reviewed primitive set such as:

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN|MAX|SUM)`
- `REDUCE_INT(COUNT|SUM)`
- experimental bounded collection where a reviewed output-capacity contract
  exists

That replacement should preserve the v1.0 app boundaries while reducing engine
custom code.
