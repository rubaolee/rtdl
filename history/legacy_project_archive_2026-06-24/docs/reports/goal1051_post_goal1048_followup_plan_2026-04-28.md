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
| `facility_knn_assignment` | `Goal1048/Goal1058 RTX A5000 evidence remains historical validation context; Goal1135/Goal1136 added changed-path RTX A5000 artifacts from source marker 21fa036881bf9a0c806f69c15727d87b482ccfcf. Goal1146 promoted narrow prepared coverage-threshold public wording only; Goal1164/Goal1165/Goal1166/Goal1177/Goal1184 are follow-up engineering and clean-source batch evidence, not new public wording. ranked KNN assignment, fallback assignment, Python setup, and whole-app speedup remain outside the claim.` | `PYTHONPATH=src:. python examples/rtdl_facility_knn_assignment.py --backend optix --optix-summary-mode coverage_threshold_prepared --require-rt-core` |
| `robot_collision_screening` | `Goal1048/Goal1058 RTX A5000 evidence remains historical validation context; Goal1135/Goal1136 added changed-path RTX A5000 artifacts from source marker 21fa036881bf9a0c806f69c15727d87b482ccfcf. Goal1142 replaced stale-source 64M robot timing with same-source bounded sub-path evidence. Goal1164 exposed large-scale robot timing bottlenecks, Goal1165 removed avoidable CPU validation from prepared timing paths, Goal1166 prepared the next validation/timing pod packet, and Goal1177 accepted the recovered clean-source staged-archive robot timing row as timing-only review input. Goal1184 accepted the newer RTX A4500 robot timing row as timing-only external-review input. Goal1126 accepted explicit normalized per-pose public wording only; this is not a same-total-work wall-time or whole-app robot-planning claim.` | `PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py --backend optix --optix-summary-mode prepared_count` |

## Same-Semantics Review Needed

| App | Claim Scope | Boundary |
| --- | --- | --- |
| `database_analytics` | prepared DB compact-summary traversal/filter/grouping sub-path may enter claim review; no DBMS or SQL-engine speedup claim | DB claims must stay limited to compact-summary prepared sub-paths; no SQL engine, DBMS, full dashboard, row-materializing, or broad whole-app speedup claim is allowed |
| `polygon_set_jaccard` | native-assisted candidate-discovery path only; no full Jaccard speedup claim | exact set-area/Jaccard refinement remains CPU/Python-owned, and larger chunk sizes are diagnostic failures until root-caused |

## Reviewed Rows To Preserve

- `service_coverage_gaps`
- `event_hotspot_screening`
- `facility_knn_assignment`
- `road_hazard_screening`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `hausdorff_distance`
- `ann_candidate_search`
- `outlier_detection`
- `dbscan_clustering`
- `robot_collision_screening`
- `barnes_hut_force_app`

## Next Local Actions

- Create a validation-enabled rerun manifest for facility_knn_assignment and robot_collision_screening.
- Package same-semantics baseline-review packets for public_wording_not_reviewed rows before stronger wording.
- Keep v1.0 app-first custom native paths as golden references for later v1.5 primitive extraction.
- Treat v2.0 compute partnership as future direction only; do not expand v1.0 scope into a magic Python compiler.

## Boundary

This plan does not run cloud, authorize release, or authorize new public speedup wording. It only defines the next local and cloud-batch work.
