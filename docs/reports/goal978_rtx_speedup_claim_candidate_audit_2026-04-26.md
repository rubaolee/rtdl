# Goal978 RTX Speedup Claim Candidate Audit

Date: 2026-04-26

Goal978 classifies RTX speedup-claim candidates after Goal836 reached 50/50 baseline readiness. It does not authorize public speedup claims; it only selects rows for later 2-AI claim review or identifies rows that need timing repair or rejection.

## Summary

- rows audited: `17`
- candidate rows for later 2-AI public-claim review: `7`
- rows needing timing repair: `0`
- public speedup claims authorized here: `0`
- recommendation counts: `{'candidate_for_separate_2ai_public_claim_review': 7, 'reject_current_public_speedup_claim': 9, 'internal_only_margin_or_scale': 1}`

## App/Path Decisions

| App | Path | RTX phase (s) | Fastest non-OptiX baseline | Ratio | Recommendation |
| --- | --- | ---: | --- | ---: | --- |
| `robot_collision_screening` | `prepared_pose_flags` | 0.000367 | `embree_anyhit_pose_count_or_equivalent_compact_summary` 0.581851 | 1585.066368 | `candidate_for_separate_2ai_public_claim_review` |
| `outlier_detection` | `prepared_fixed_radius_density_summary` | 0.005078 | `cpu_scalar_threshold_count_oracle` 0.027044 | 5.325816 | `candidate_for_separate_2ai_public_claim_review` |
| `dbscan_clustering` | `prepared_fixed_radius_core_flags` | 0.000853 | `cpu_scalar_threshold_count_oracle` 0.024832 | 29.128064 | `candidate_for_separate_2ai_public_claim_review` |
| `database_analytics` | `prepared_db_session_sales_risk` | 0.100171 | `embree_compact_summary` 0.061593 | 0.614881 | `reject_current_public_speedup_claim` |
| `database_analytics` | `prepared_db_session_regional_dashboard` | 0.135571 | `embree_compact_summary` 0.127206 | 0.938299 | `reject_current_public_speedup_claim` |
| `service_coverage_gaps` | `prepared_gap_summary` | 0.215130 | `embree_summary_path` 0.220048 | 1.022860 | `internal_only_margin_or_scale` |
| `event_hotspot_screening` | `prepared_count_summary` | 0.326126 | `embree_summary_path` 0.256616 | 0.786862 | `reject_current_public_speedup_claim` |
| `facility_knn_assignment` | `coverage_threshold_prepared` | 0.000585 | `cpu_oracle_same_semantics` 0.071395 | 121.980502 | `candidate_for_separate_2ai_public_claim_review` |
| `road_hazard_screening` | `road_hazard_native_summary_gate` | 0.182339 | `embree_same_semantics` 0.003571 | 0.019586 | `reject_current_public_speedup_claim` |
| `segment_polygon_hitcount` | `segment_polygon_hitcount_native_experimental` | 0.004443 | `embree_same_semantics` 0.006826 | 1.536281 | `candidate_for_separate_2ai_public_claim_review` |
| `segment_polygon_anyhit_rows` | `segment_polygon_anyhit_rows_prepared_bounded_gate` | 0.003625 | `postgis_when_available_for_same_pair_semantics` 0.014249 | 3.930470 | `candidate_for_separate_2ai_public_claim_review` |
| `graph_analytics` | `graph_visibility_edges_gate` | 1.583060 | `embree_graph_ray_bfs_and_triangle_when_available` 0.567219 | 0.358306 | `reject_current_public_speedup_claim` |
| `hausdorff_distance` | `directed_threshold_prepared` | 0.001217 | `cpu_oracle_same_semantics` 0.000022 | 0.018452 | `reject_current_public_speedup_claim` |
| `ann_candidate_search` | `candidate_threshold_prepared` | 0.000632 | `cpu_oracle_same_semantics` 0.003667 | 5.805503 | `candidate_for_separate_2ai_public_claim_review` |
| `barnes_hut_force_app` | `node_coverage_prepared` | 0.001540 | `cpu_oracle_same_semantics` 0.000699 | 0.453908 | `reject_current_public_speedup_claim` |
| `polygon_pair_overlap_area_rows` | `polygon_pair_overlap_optix_native_assisted_phase_gate` | 3.513415 | `postgis_when_available_for_same_unit_cell_contract` 0.001471 | 0.000419 | `reject_current_public_speedup_claim` |
| `polygon_set_jaccard` | `polygon_set_jaccard_optix_native_assisted_phase_gate` | 3.642833 | `embree_native_assisted_candidate_discovery` 0.013214 | 0.003627 | `reject_current_public_speedup_claim` |

## Detail

### robot_collision_screening / prepared_pose_flags

- recommendation: `candidate_for_separate_2ai_public_claim_review`
- reason: RTX query/native phase is at least 20% faster than every timed non-OptiX same-semantics baseline; separate 2-AI review is still required.
- public speedup authorized: `False`
- warning: RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence.

### outlier_detection / prepared_fixed_radius_density_summary

- recommendation: `candidate_for_separate_2ai_public_claim_review`
- reason: RTX query/native phase is at least 20% faster than every timed non-OptiX same-semantics baseline; separate 2-AI review is still required.
- public speedup authorized: `False`
- warning: RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence.

### dbscan_clustering / prepared_fixed_radius_core_flags

- recommendation: `candidate_for_separate_2ai_public_claim_review`
- reason: RTX query/native phase is at least 20% faster than every timed non-OptiX same-semantics baseline; separate 2-AI review is still required.
- public speedup authorized: `False`
- warning: RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence.

### database_analytics / prepared_db_session_sales_risk

- recommendation: `reject_current_public_speedup_claim`
- reason: RTX is slower than the fastest non-OptiX same-semantics baseline in current evidence.
- public speedup authorized: `False`

### database_analytics / prepared_db_session_regional_dashboard

- recommendation: `reject_current_public_speedup_claim`
- reason: RTX is slower than the fastest non-OptiX same-semantics baseline in current evidence.
- public speedup authorized: `False`

### service_coverage_gaps / prepared_gap_summary

- recommendation: `internal_only_margin_or_scale`
- reason: RTX is not slower than the fastest baseline, but the margin is below the 20% candidate threshold.
- public speedup authorized: `False`

### event_hotspot_screening / prepared_count_summary

- recommendation: `reject_current_public_speedup_claim`
- reason: RTX is slower than the fastest non-OptiX same-semantics baseline in current evidence.
- public speedup authorized: `False`

### facility_knn_assignment / coverage_threshold_prepared

- recommendation: `candidate_for_separate_2ai_public_claim_review`
- reason: RTX query/native phase is at least 20% faster than every timed non-OptiX same-semantics baseline; separate 2-AI review is still required.
- public speedup authorized: `False`
- warning: RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence.

### road_hazard_screening / road_hazard_native_summary_gate

- recommendation: `reject_current_public_speedup_claim`
- reason: RTX is slower than the fastest non-OptiX same-semantics baseline in current evidence.
- public speedup authorized: `False`

### segment_polygon_hitcount / segment_polygon_hitcount_native_experimental

- recommendation: `candidate_for_separate_2ai_public_claim_review`
- reason: RTX query/native phase is at least 20% faster than every timed non-OptiX same-semantics baseline; separate 2-AI review is still required.
- public speedup authorized: `False`
- warning: RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence.

### segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate

- recommendation: `candidate_for_separate_2ai_public_claim_review`
- reason: RTX query/native phase is at least 20% faster than every timed non-OptiX same-semantics baseline; separate 2-AI review is still required.
- public speedup authorized: `False`
- warning: RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence.

### graph_analytics / graph_visibility_edges_gate

- recommendation: `reject_current_public_speedup_claim`
- reason: RTX is slower than the fastest non-OptiX same-semantics baseline in current evidence.
- public speedup authorized: `False`
- warning: cpu_python_reference_visibility_edges lacks comparable timing
- warning: cpu_python_reference_bfs lacks comparable timing
- warning: cpu_python_reference_triangle_count lacks comparable timing

### hausdorff_distance / directed_threshold_prepared

- recommendation: `reject_current_public_speedup_claim`
- reason: RTX is slower than the fastest non-OptiX same-semantics baseline in current evidence.
- public speedup authorized: `False`
- warning: RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence.

### ann_candidate_search / candidate_threshold_prepared

- recommendation: `candidate_for_separate_2ai_public_claim_review`
- reason: RTX query/native phase is at least 20% faster than every timed non-OptiX same-semantics baseline; separate 2-AI review is still required.
- public speedup authorized: `False`
- warning: RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence.

### barnes_hut_force_app / node_coverage_prepared

- recommendation: `reject_current_public_speedup_claim`
- reason: RTX is slower than the fastest non-OptiX same-semantics baseline in current evidence.
- public speedup authorized: `False`
- warning: RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence.

### polygon_pair_overlap_area_rows / polygon_pair_overlap_optix_native_assisted_phase_gate

- recommendation: `reject_current_public_speedup_claim`
- reason: RTX is slower than the fastest non-OptiX same-semantics baseline in current evidence.
- public speedup authorized: `False`

### polygon_set_jaccard / polygon_set_jaccard_optix_native_assisted_phase_gate

- recommendation: `reject_current_public_speedup_claim`
- reason: RTX is slower than the fastest non-OptiX same-semantics baseline in current evidence.
- public speedup authorized: `False`
