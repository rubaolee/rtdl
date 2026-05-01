# Goal762 RTX Cloud Artifact Report

## Verdict

Status: `ok`.

This report checks cloud artifacts and summarizes phase metrics. It does not authorize RTX speedup claims; claims require human/AI review of correctness, phase separation, hardware metadata, and comparison baselines.

## Run Metadata

- summary_path: `/workspace/rtdl/docs/reports/goal761_rtx_cloud_run_all_summary.json`
- runner_status: `ok`
- dry_run: `False`
- git_head: `914122ecd2f2c73f6a51ec2d5b04ca3d575d5681`
- failure_count: `0`

## Artifact Table

| App | Path | Runner | Artifact | Input/prep pack (s) | Warm query median (s) | Postprocess median (s) | Validation / oracle (s) | Non-claim |
|---|---|---:|---:|---:|---:|---:|---:|---|
| robot_collision_screening | prepared_pose_flags | ok | ok | 0.004536 | 0.000493 |  | 0.000000 | not continuous collision detection, full robot kinematics, or mesh-engine replacement |
| outlier_detection | prepared_fixed_radius_density_summary | ok | ok | 0.347474 | 0.005828 | 0.000000 | 0.000000 | not per-point outlier labels, row-output neighbors, KNN, Hausdorff, ANN, Barnes-Hut, anomaly-detection-system, or whole-app RTX speedup claim |
| dbscan_clustering | prepared_fixed_radius_core_flags | ok | ok | 0.332053 | 0.003751 | 0.000000 | 0.000000 | not per-point core flags, not a full DBSCAN clustering, KNN, Hausdorff, ANN, Barnes-Hut, or whole-app RTX speedup claim |
| database_analytics | prepared_db_session_sales_risk | ok | ok | 0.899371 | 0.103378 | 0.000013 |  | not a SQL engine claim and not a broad RTX RT-core app speedup claim |
| database_analytics | prepared_db_session_regional_dashboard | ok | ok | 1.099113 | 0.143968 | 0.000004 |  | not a SQL engine claim and not a broad RTX RT-core app speedup claim |
| service_coverage_gaps | prepared_gap_summary | ok | ok | 0.221375 | 0.136545 | 0.000007 |  | not a whole-app service coverage speedup claim and not a nearest-clinic row-output claim |
| event_hotspot_screening | prepared_count_summary | ok | ok | 0.205787 | 0.253894 | 0.000006 |  | not a whole-app hotspot-screening speedup claim and not a neighbor-row output claim |
| facility_knn_assignment | coverage_threshold_prepared | ok | ok | 0.259724 | 0.003131 | 0.000001 | 0.000000 | not a ranked nearest-depot, KNN fallback-assignment, or facility-location optimizer claim |
| road_hazard_screening | road_hazard_native_summary_gate | ok | ok | 0.352265 | 0.172010 | 0.000001 | 1.776709 | not default public road-hazard behavior and not a full GIS/routing speedup claim |
| segment_polygon_hitcount | segment_polygon_hitcount_native_experimental | ok | ok | 0.021605 | 0.003996 | 0.000001 | 0.028015 | not default public app behavior and not a row-returning any-hit claim |
| segment_polygon_anyhit_rows | segment_polygon_anyhit_rows_prepared_bounded_gate | ok | ok | 0.075734 | 0.004701 |  | 0.000001 | not default public app behavior and not an unbounded pair-row performance claim |
| graph_analytics | graph_visibility_edges_gate | ok | ok |  | 2.584184 |  |  | not shortest-path, graph database, distributed graph analytics, or whole-app graph-system acceleration; BFS visited/frontier bookkeeping and triangle set-intersection remain outside RT traversal |
| hausdorff_distance | directed_threshold_prepared | ok | ok | 0.275634 | 0.001364 | 0.000002 | 0.000106 | not an exact Hausdorff distance, KNN-row, or nearest-neighbor ranking speedup claim |
| ann_candidate_search | candidate_threshold_prepared | ok | ok | 0.225219 | 0.000755 | 0.000001 | 0.010705 | not a full ANN index, nearest-neighbor ranking, FAISS/HNSW/IVF/PQ, or recall-optimizer claim |
| barnes_hut_force_app | node_coverage_prepared | ok | ok | 0.392012 | 0.004754 | 0.000003 | 0.164744 | not a Barnes-Hut opening-rule, force-vector reduction, or N-body solver speedup claim |
| polygon_pair_overlap_area_rows | polygon_pair_overlap_optix_native_assisted_phase_gate | ok | ok | 0.000000 | 10.052899 | 3.674281 |  | not a monolithic GPU polygon-area kernel and not a full app RTX speedup claim |
| polygon_set_jaccard | polygon_set_jaccard_optix_native_assisted_phase_gate | ok | ok | 0.000000 | 4.152796 | 5.891413 |  | not a monolithic GPU Jaccard kernel and not a full app RTX speedup claim |

## Baseline Review Contracts

| App | Path | Status | Comparable metric scope | Claim limit |
|---|---|---:|---|---|
| robot_collision_screening | prepared_pose_flags | ok | prepared scalar colliding-pose count for the same poses, edges, obstacles, and iteration policy | scalar pose-count collision screening only; not full robot planning, kinematics, CCD, or witness-row output |
| outlier_detection | prepared_fixed_radius_density_summary | ok | prepared fixed-radius scalar threshold-count/core-count result with identical radius, threshold, fixture, and copies | outlier threshold-count or DBSCAN core-count summary only; not row-returning neighbors or full DBSCAN cluster expansion |
| dbscan_clustering | prepared_fixed_radius_core_flags | ok | prepared fixed-radius scalar threshold-count/core-count result with identical radius, threshold, fixture, and copies | outlier threshold-count or DBSCAN core-count summary only; not row-returning neighbors or full DBSCAN cluster expansion |
| database_analytics | prepared_db_session_sales_risk | ok | compact_summary prepared DB query result for the same scenario/copies/iterations | prepared DB sub-path only; not a DBMS or SQL-engine speedup claim |
| database_analytics | prepared_db_session_regional_dashboard | ok | compact_summary prepared DB query result for the same scenario/copies/iterations | prepared DB sub-path only; not a DBMS or SQL-engine speedup claim |
| service_coverage_gaps | prepared_gap_summary | ok | prepared compact fixed-radius summary for the same generated households/events/facilities and radius | prepared compact summary only; not nearest-row or whole-app speedup |
| event_hotspot_screening | prepared_count_summary | ok | prepared compact fixed-radius summary for the same generated households/events/facilities and radius | prepared compact summary only; not nearest-row or whole-app speedup |
| facility_knn_assignment | coverage_threshold_prepared | ok | same app/path semantics for facility_knn_assignment:coverage_threshold_prepared | bounded sub-path only |
| road_hazard_screening | road_hazard_native_summary_gate | ok | prepared road-hazard native OptiX summary result on the same copies and priority-threshold semantics | experimental prepared road-hazard summary gate only; not default public app behavior or full GIS/routing speedup |
| segment_polygon_hitcount | segment_polygon_hitcount_native_experimental | ok | prepared segment/polygon hit-count result on the same dataset and output count semantics | experimental prepared hit-count gate only; not pair-row any-hit or road-hazard whole-app speedup |
| segment_polygon_anyhit_rows | segment_polygon_anyhit_rows_prepared_bounded_gate | ok | strict bounded segment/polygon pair-row result on the same dataset and output capacity | experimental native bounded pair-row gate only; not default public app behavior and not unbounded row-volume performance |
| graph_analytics | graph_visibility_edges_gate | ok | strict graph visibility-edge, native BFS graph-ray, and native triangle-count graph-ray row-digest results for the same copies semantics | bounded graph RT sub-paths only: visibility any-hit plus BFS/triangle candidate generation; not shortest-path, graph database, distributed graph analytics, or whole-app graph-system acceleration |
| hausdorff_distance | directed_threshold_prepared | ok | same app/path semantics for hausdorff_distance:directed_threshold_prepared | bounded sub-path only |
| ann_candidate_search | candidate_threshold_prepared | ok | same app/path semantics for ann_candidate_search:candidate_threshold_prepared | bounded sub-path only |
| barnes_hut_force_app | node_coverage_prepared | ok | same app/path semantics for barnes_hut_force_app:node_coverage_prepared | bounded sub-path only |
| polygon_pair_overlap_area_rows | polygon_pair_overlap_optix_native_assisted_phase_gate | ok | native-assisted OptiX LSI/PIP candidate-discovery phase plus native C++ exact area continuation | native-assisted candidate-discovery plus native exact continuation path only; no full app RTX speedup claim without same-semantics review |
| polygon_set_jaccard | polygon_set_jaccard_optix_native_assisted_phase_gate | ok | native-assisted OptiX LSI/PIP candidate-discovery phase plus native C++ exact Jaccard continuation | native-assisted candidate-discovery plus native exact continuation path only; no full app RTX speedup claim without same-semantics review |

## Required Review

- Confirm the machine is RTX-class and `nvidia-smi` metadata matches the intended cloud resource.
- Confirm all `artifact_status` cells are `ok` before interpreting timings.
- Compare against explicit baselines separately; this report intentionally does not compute public speedup claims.
- Keep DB, fixed-radius summary, and robot pose-flag claim scopes separate.
