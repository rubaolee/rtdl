# Goal2077 Complete v1.8/v2.0 Performance Tables

Date: 2026-05-15

Status: `embree-v18-v2-complete-table-evidence`

Goal2077 fills the Embree v1.8-way cells that had previously been left blank, especially `database_analytics` and `graph_analytics`, by measuring current-tree v1.8-style Python+RTDL+Embree commands. The v2 Embree cells are measured with the current Embree CPU evidence command for the same app row.

## Boundary

- This is evidence-only local Linux wall-clock timing, not public release wording.
- The table has no `n/a` cells when `all_cells_filled` is true.
- Some v2 Embree rows currently reuse the same public Embree app surface because the distinct CPU-partner continuation is not yet implemented for that app.
- OptiX/RT rows still require fresh pod timing for new Goal2075 polygon changes.

## Embree Table

- scale: `evidence`
- all cells filled: `True`

| App | Scale | v1.8-way Embree sec | v2 Embree/CPU-partner sec | v2/v1.8 | Evidence note |
| --- | --- | ---: | ---: | ---: | --- |
| `database_analytics` | copies=4000 | 0.624328 | 0.623253 | 0.998x | filled by re-implementing/running the v1.8 Python+RTDL Embree path in the current tree; no distinct v2 CPU partner DB adapter claim |
| `graph_analytics` | scenario=all copies=2000 | 0.448031 | 0.448262 | 1.001x | filled by measuring the complete graph app instead of leaving split graph rows or blank cells; reusable v2 graph partner primitive remains future work |
| `service_coverage_gaps` | copies=2000 | 0.383810 | 0.385865 | 1.005x | threshold/proxy semantics only; not exact ranked KNN, full DBSCAN, or force-vector accumulation |
| `event_hotspot_screening` | copies=2000 | 0.462037 | 0.460492 | 0.997x | threshold/proxy semantics only; not exact ranked KNN, full DBSCAN, or force-vector accumulation |
| `facility_knn_assignment` | copies=2000 | 1.038575 | 1.039533 | 1.001x | threshold/proxy semantics only; not exact ranked KNN, full DBSCAN, or force-vector accumulation |
| `road_hazard_screening` | copies=2000 | 0.358194 | 0.358267 | 1.000x | same Embree evidence cell; v2 GPU partner speedup is an OptiX/CuPy result, not an Embree CPU claim |
| `segment_polygon_hitcount` | copies=1024 | 0.393747 | 0.394920 | 1.003x | same Embree evidence cell; compact count is the desired v2 shape but this local row is CPU Embree |
| `segment_polygon_anyhit_rows` | copies=1024 capacity=16384 | 0.417826 | 0.419203 | 1.003x | full row materialization remains the weak output shape; no compact-count substitution in this row |
| `polygon_pair_overlap_area_rows` | copies=5000 | 2.422751 | 1.029965 | 0.425x | filled as evidence for the bounded/streaming candidate-summary direction; not arbitrary polygon overlay |
| `polygon_set_jaccard` | copies=1000 | 1.844188 | 0.383534 | 0.208x | filled as evidence for the bounded/streaming candidate-summary direction; not arbitrary polygon overlay |
| `hausdorff_distance` | copies=2000 | 1.271810 | 1.306289 | 1.027x | exact directed summary, not a GPU partner threshold proxy in this Embree table |
| `ann_candidate_search` | copies=2000 | 0.752987 | 0.746997 | 0.992x | candidate coverage/rerank summary only; not a general ANN index claim |
| `outlier_detection` | copies=2000 | 0.377554 | 0.373912 | 0.990x | threshold/proxy semantics only; not exact ranked KNN, full DBSCAN, or force-vector accumulation |
| `dbscan_clustering` | copies=2000 | 0.378293 | 0.377832 | 0.999x | core-count only; full cluster expansion remains app/partner graph work |
| `robot_collision_screening` | poses=2000 obstacles=512 | 35.723054 | 35.676529 | 0.999x | pose flags/count only; no whole-planner acceleration claim |
| `barnes_hut_force_app` | body-count=50000 | 1.022868 | 1.020987 | 0.998x | node coverage only; force-vector reduction remains outside this row |

## OptiX/RT Table

- all cells filled: `True`
- source: existing NVIDIA pod artifacts; polygon rows are pre-Goal2075 and need fresh pod timing for the new generic AABB candidate-summary path.

| App | Scale | v1.8 OptiX/RT sec | v2 OptiX/RT+partner sec | v2/v1.8 | Evidence note |
| --- | --- | ---: | ---: | ---: | --- |
| `database_analytics` | copies=4096 | 0.300836 | 0.074904 | 0.249x | app-wall Python+RTDL vs Python+CuPy+RTDL; not absolutely fair, but user-approved v2 app comparison |
| `graph_analytics` | copies=512 | 5.206507 | 0.000121 | 0.000x | app-wall Python+RTDL vs Python+CuPy+RTDL; not absolutely fair, but user-approved v2 app comparison |
| `service_coverage_gaps` | size=16384 partner=cupy | 0.038096 | 0.000228 | 0.006x | prepared fixed-radius count/threshold output; compact partner-owned columns |
| `event_hotspot_screening` | size=16384 partner=cupy | 0.094140 | 0.000188 | 0.002x | prepared fixed-radius count/threshold output; compact partner-owned columns |
| `facility_knn_assignment` | query=16384 search=16384 partner=cupy | 0.040198 | 0.000328 | 0.008x | prepared fixed-radius threshold/proxy row; richer exact semantics remain bounded as documented |
| `road_hazard_screening` | roads=12288 hazards=18432 partner=cupy | 0.029205 | 0.002496 | 0.085x | prepared reusable witness output plus partner priority flags |
| `segment_polygon_hitcount` | rows=131072 capacity=67108864 partner=cupy | 0.452884 | 0.002772 | 0.006x | compact partner-owned count columns; strongest segment/polygon v2 shape |
| `segment_polygon_anyhit_rows` | rows=4096 capacity=16777216 partner=cupy | 0.105058 | 0.164098 | 1.562x | full witness rows; correct but slower than v1.8 native rows |
| `polygon_pair_overlap_area_rows` | copies=3072 partner=cupy candidate_backend=optix | 0.492970 | 0.641490 | 1.301x | pre-Goal2075 pod timing; fresh pod timing required for the new bounded generic AABB source path |
| `polygon_set_jaccard` | copies=3072 partner=cupy candidate_backend=optix | 0.395736 | 0.378481 | 0.956x | pre-Goal2075 pod timing; fresh pod timing required for the new bounded generic AABB source path |
| `hausdorff_distance` | query=16384 search=16384 partner=cupy | 0.040002 | 0.000288 | 0.007x | prepared fixed-radius threshold/proxy row; richer exact semantics remain bounded as documented |
| `ann_candidate_search` | query=16384 search=16384 partner=cupy | 0.039402 | 0.000266 | 0.007x | prepared fixed-radius threshold/proxy row; richer exact semantics remain bounded as documented |
| `outlier_detection` | query=16384 search=16384 partner=cupy | 0.034903 | 0.000275 | 0.008x | prepared fixed-radius threshold/proxy row; richer exact semantics remain bounded as documented |
| `dbscan_clustering` | query=16384 search=16384 partner=cupy | 0.035026 | 0.000277 | 0.008x | prepared fixed-radius threshold/proxy row; richer exact semantics remain bounded as documented |
| `robot_collision_screening` | poses=65536 obstacles=8192 partner=cupy | 0.006289 | 0.000528 | 0.084x | prepared generic any-hit flags to partner-owned pose flags |
| `barnes_hut_force_app` | query=16384 search=16384 partner=cupy | 0.034574 | 0.000315 | 0.009x | prepared fixed-radius threshold/proxy row; richer exact semantics remain bounded as documented |

## Table Interpretation

- Embree is CPU RT evidence on local Linux. Several rows intentionally use the same v1.8-way Embree app surface for v2 until a distinct CPU-partner continuation exists; those cells are filled as evidence, not as a speedup claim.
- OptiX/RT is where v2 partner-owned compact outputs show the strongest gains. Full witness-row materialization and pre-Goal2075 polygon timing remain bounded.
- No row authorizes v2.0 release, all-app speedup, broad RT-core speedup, or arbitrary polygon overlay.
