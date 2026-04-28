# Goal1051 Post-Goal1048 Follow-Up Plan

Date: 2026-04-28

Valid: `True`

This plan does not run cloud, authorize release, or authorize new public speedup wording. It only defines the next local and cloud-batch work.

## Policy

Do not start paid cloud per app. Use one batched pod only after local manifest, validation commands, source commit traceability, and artifact copy-out paths are ready.

## Inputs

- `docs/reports/gemini_v1_0_project_foundational_review_2026-04-27.md`
- `docs/reports/gemini_v2_0_architectural_direction_compute_partnership_2026-04-27.md`
- `docs/reports/goal1050_two_ai_consensus_2026-04-28.md`
- `docs/v1_0_rtx_app_status.md`
- `docs/app_engine_support_matrix.md`

## Diagnostic Reruns

| App | Why | Command |
| --- | --- | --- |
| `facility_knn_assignment` | `Goal1058 RTX A5000 diagnostic rerun validated facility coverage with oracle parity. Public speedup wording remains blocked until a separate baseline/timing wording review authorizes a bounded sub-path claim.` | `PYTHONPATH=src:. python examples/rtdl_facility_knn_assignment.py --backend optix --optix-summary-mode coverage_threshold_prepared --require-rt-core` |
| `robot_collision_screening` | `Goal1058 RTX A5000 diagnostic rerun validated robot pose flags with oracle parity. Public speedup wording remains blocked because the claim-review path still needs timing-floor/baseline review.` | `PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py --backend optix --optix-summary-mode prepared_count` |

## Same-Semantics Review Needed

| App | Claim Scope | Boundary |
| --- | --- | --- |
| `database_analytics` | prepared DB compact-summary traversal/filter/grouping sub-path may enter claim review; no DBMS or SQL-engine speedup claim | DB claims must stay limited to compact-summary prepared sub-paths; no SQL engine, DBMS, full dashboard, row-materializing, or broad whole-app speedup claim is allowed |
| `graph_analytics` | bounded graph visibility any-hit plus native BFS/triangle graph-ray candidate-generation sub-paths may enter claim review; no whole-app graph speedup claim | Goal929 covers bounded graph RT sub-paths only; CPU-side frontier bookkeeping, triangle set-intersection, shortest-path, graph database, distributed analytics, and whole-app graph-system acceleration remain outside the claim |
| `road_hazard_screening` | prepared native road-hazard summary traversal sub-path may enter claim review; no full GIS/routing or default-app speedup claim | claim is limited to the prepared compact road-hazard summary gate; default public app behavior, full GIS/routing, and broad road-hazard speedup remain outside the claim |
| `polygon_pair_overlap_area_rows` | native-assisted candidate-discovery path only; no full polygon-area speedup claim | exact area refinement remains CPU/Python-owned; only candidate discovery may enter claim review |
| `polygon_set_jaccard` | native-assisted candidate-discovery path only; no full Jaccard speedup claim | exact set-area/Jaccard refinement remains CPU/Python-owned, and larger chunk sizes are diagnostic failures until root-caused |
| `hausdorff_distance` | prepared Hausdorff <= radius decision sub-path may enter claim review; no exact-distance speedup claim | exact Hausdorff distance, KNN-row output, nearest-neighbor ranking, and whole-app speedup remain outside the claim |
| `barnes_hut_force_app` | prepared Barnes-Hut node-coverage decision sub-path may enter claim review; no force-vector or opening-rule speedup claim | Barnes-Hut opening-rule evaluation, candidate-row output, force-vector reduction, N-body simulation, and whole-app speedup remain outside the claim |

## Reviewed Rows To Preserve

- `service_coverage_gaps`
- `event_hotspot_screening`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `ann_candidate_search`
- `outlier_detection`
- `dbscan_clustering`

## Next Local Actions

- Create a validation-enabled rerun manifest for facility_knn_assignment and robot_collision_screening.
- Package same-semantics baseline-review packets for public_wording_not_reviewed rows before stronger wording.
- Keep v1.0 app-first custom native paths as golden references for later v1.5 primitive extraction.
- Treat v2.0 compute partnership as future direction only; do not expand v1.0 scope into a magic Python compiler.

## Boundary

This plan does not run cloud, authorize release, or authorize new public speedup wording. It only defines the next local and cloud-batch work.
