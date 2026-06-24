# Goal1060 Post-Goal1058 Speedup Candidate Audit

Date: 2026-04-28

Goal1060 compares accepted Goal1058 RTX A5000 artifact phases against existing same-semantics baselines. It does not authorize public speedup wording; candidate rows still require separate 2-AI public wording review.

## Summary

- valid: `True`
- rows audited: `11`
- candidate rows for later 2-AI public wording review: `3`
- public speedup claims authorized here: `0`
- recommendation counts: `{'candidate_for_separate_2ai_public_claim_review': 3, 'reject_current_public_speedup_claim': 8}`

## Decisions

| App | Path | RTX phase key | RTX phase (s) | Fastest baseline | Ratio | Recommendation | Current public wording |
| --- | --- | --- | ---: | --- | ---: | --- | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `scenario.timings_sec.optix_query_sec` | 0.001211 | `cpu_oracle_same_semantics` 0.071395 | 58.962816 | `candidate_for_separate_2ai_public_claim_review` | `public_wording_blocked` |
| `robot_collision_screening` | `prepared_pose_flags` | `prepared_pose_flags_warm_query_sec.median_sec` | 0.002990 | `embree_anyhit_pose_count_or_equivalent_compact_summary` 0.581851 | 194.588792 | `candidate_for_separate_2ai_public_claim_review` | `public_wording_blocked` |
| `database_analytics` | `prepared_db_session_sales_risk` | `prepared_session_warm_query_sec.median_sec` | 0.101725 | `embree_compact_summary` 0.061593 | 0.605485 | `reject_current_public_speedup_claim` | `public_wording_not_reviewed` |
| `database_analytics` | `prepared_db_session_regional_dashboard` | `prepared_session_warm_query_sec.median_sec` | 0.138423 | `embree_compact_summary` 0.127206 | 0.918964 | `reject_current_public_speedup_claim` | `public_wording_not_reviewed` |
| `graph_analytics` | `graph_visibility_edges_gate` | `records.optix_visibility_anyhit.sec` | 1.316055 | `embree_graph_ray_bfs_and_triangle_when_available` 0.567219 | 0.431000 | `reject_current_public_speedup_claim` | `public_wording_not_reviewed` |
| `event_hotspot_screening` | `prepared_count_summary` | `scenario.timings_sec.optix_query` | 0.165999 | `embree_summary_path` 0.256616 | 1.545891 | `candidate_for_separate_2ai_public_claim_review` | `public_wording_not_reviewed` |
| `road_hazard_screening` | `road_hazard_native_summary_gate` | `timings_sec.optix_query_sec` | 0.097398 | `embree_same_semantics` 0.003571 | 0.036668 | `reject_current_public_speedup_claim` | `public_wording_not_reviewed` |
| `polygon_pair_overlap_area_rows` | `polygon_pair_overlap_optix_native_assisted_phase_gate` | `phases.optix_candidate_discovery_sec` | 2.407473 | `postgis_when_available_for_same_unit_cell_contract` 0.001471 | 0.000611 | `reject_current_public_speedup_claim` | `public_wording_not_reviewed` |
| `polygon_set_jaccard` | `polygon_set_jaccard_optix_native_assisted_phase_gate` | `phases.optix_candidate_discovery_sec` | 2.613548 | `embree_native_assisted_candidate_discovery` 0.013214 | 0.005056 | `reject_current_public_speedup_claim` | `public_wording_not_reviewed` |
| `hausdorff_distance` | `directed_threshold_prepared` | `scenario.timings_sec.optix_query_sec` | 0.003918 | `cpu_oracle_same_semantics` 0.000022 | 0.005733 | `reject_current_public_speedup_claim` | `public_wording_not_reviewed` |
| `barnes_hut_force_app` | `node_coverage_prepared` | `scenario.timings_sec.optix_query_sec` | 0.001782 | `cpu_oracle_same_semantics` 0.000699 | 0.392413 | `reject_current_public_speedup_claim` | `public_wording_not_reviewed` |

## Boundary

Goal1060 compares accepted Goal1058 RTX A5000 artifact phases against existing same-semantics baselines. It does not authorize public speedup wording; candidate rows still require separate 2-AI public wording review.

