# Goal1005 Post-A5000 Speedup Candidate Audit

Date: 2026-04-26

Goal1005 classifies speedup-claim candidates from the final Goal1004 RTX A5000 v2 artifacts. It does not authorize public speedup claims; it only identifies rows that may deserve later 2-AI public-claim review or rows that should be rejected/kept internal under current evidence.

## Summary

- source final A5000 v2 evidence: `True`
- rows audited: `17`
- candidate rows for later 2-AI public-claim review: `8`
- internal-only rows: `1`
- rejected current public speedup rows: `8`
- public speedup claims authorized here: `0`
- recommendation counts: `{'candidate_for_separate_2ai_public_claim_review': 8, 'reject_current_public_speedup_claim': 8, 'internal_only_margin_or_scale': 1}`

## App/Path Decisions

| App | Path | RTX phase key | RTX phase (s) | Fastest non-OptiX baseline | Ratio | Recommendation |
|---|---|---|---:|---|---:|---|
| `robot_collision_screening` | `prepared_pose_flags` | `prepared_pose_flags_warm_query_sec.median_sec` | 0.000493 | `embree_anyhit_pose_count_or_equivalent_compact_summary` 0.581851 | 1179.643861 | `candidate_for_separate_2ai_public_claim_review` |
| `outlier_detection` | `prepared_fixed_radius_density_summary` | `prepared_optix_warm_query_sec.median_sec` | 0.005828 | `cpu_scalar_threshold_count_oracle` 0.027044 | 4.640074 | `candidate_for_separate_2ai_public_claim_review` |
| `dbscan_clustering` | `prepared_fixed_radius_core_flags` | `prepared_optix_warm_query_sec.median_sec` | 0.003751 | `cpu_scalar_threshold_count_oracle` 0.024832 | 6.620046 | `candidate_for_separate_2ai_public_claim_review` |
| `database_analytics` | `prepared_db_session_sales_risk` | `prepared_session_warm_query_sec.median_sec` | 0.103378 | `embree_compact_summary` 0.061593 | 0.595806 | `reject_current_public_speedup_claim` |
| `database_analytics` | `prepared_db_session_regional_dashboard` | `prepared_session_warm_query_sec.median_sec` | 0.143968 | `embree_compact_summary` 0.127206 | 0.883570 | `reject_current_public_speedup_claim` |
| `service_coverage_gaps` | `prepared_gap_summary` | `scenario.timings_sec.optix_query` | 0.136545 | `embree_summary_path` 0.220048 | 1.611541 | `candidate_for_separate_2ai_public_claim_review` |
| `event_hotspot_screening` | `prepared_count_summary` | `scenario.timings_sec.optix_query` | 0.253894 | `embree_summary_path` 0.256616 | 1.010722 | `internal_only_margin_or_scale` |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `scenario.timings_sec.optix_query_sec` | 0.003131 | `cpu_oracle_same_semantics` 0.071395 | 22.805076 | `candidate_for_separate_2ai_public_claim_review` |
| `road_hazard_screening` | `road_hazard_native_summary_gate` | `timings_sec.optix_query_sec` | 0.172010 | `embree_same_semantics` 0.003571 | 0.020763 | `reject_current_public_speedup_claim` |
| `segment_polygon_hitcount` | `segment_polygon_hitcount_native_experimental` | `timings_sec.optix_query_sec` | 0.003996 | `embree_same_semantics` 0.006826 | 1.708308 | `candidate_for_separate_2ai_public_claim_review` |
| `segment_polygon_anyhit_rows` | `segment_polygon_anyhit_rows_prepared_bounded_gate` | `timings_sec.optix_query_sec` | 0.004701 | `postgis_when_available_for_same_pair_semantics` 0.014249 | 3.030858 | `candidate_for_separate_2ai_public_claim_review` |
| `graph_analytics` | `graph_visibility_edges_gate` | `records.optix_visibility_anyhit.sec` | 2.584184 | `embree_graph_ray_bfs_and_triangle_when_available` 0.567219 | 0.219497 | `reject_current_public_speedup_claim` |
| `hausdorff_distance` | `directed_threshold_prepared` | `scenario.timings_sec.optix_query_sec` | 0.001364 | `cpu_oracle_same_semantics` 0.000022 | 0.016462 | `reject_current_public_speedup_claim` |
| `ann_candidate_search` | `candidate_threshold_prepared` | `scenario.timings_sec.optix_query_sec` | 0.000755 | `cpu_oracle_same_semantics` 0.003667 | 4.857461 | `candidate_for_separate_2ai_public_claim_review` |
| `barnes_hut_force_app` | `node_coverage_prepared` | `scenario.timings_sec.optix_query_sec` | 0.004754 | `cpu_oracle_same_semantics` 0.000699 | 0.147059 | `reject_current_public_speedup_claim` |
| `polygon_pair_overlap_area_rows` | `polygon_pair_overlap_optix_native_assisted_phase_gate` | `phases.optix_candidate_discovery_sec` | 10.052899 | `postgis_when_available_for_same_unit_cell_contract` 0.001471 | 0.000146 | `reject_current_public_speedup_claim` |
| `polygon_set_jaccard` | `polygon_set_jaccard_optix_native_assisted_phase_gate` | `phases.optix_candidate_discovery_sec` | 4.152796 | `embree_native_assisted_candidate_discovery` 0.013214 | 0.003182 | `reject_current_public_speedup_claim` |

## Boundary

Goal1005 classifies speedup-claim candidates from the final Goal1004 RTX A5000 v2 artifacts. It does not authorize public speedup claims; it only identifies rows that may deserve later 2-AI public-claim review or rows that should be rejected/kept internal under current evidence.
