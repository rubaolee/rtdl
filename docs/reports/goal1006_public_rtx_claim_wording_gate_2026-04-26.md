# Goal1006 Public RTX Claim Wording Gate

Date: 2026-04-26

Goal1006 is a wording gate. It does not authorize public speedup claims. It only identifies which Goal1005 candidates are mature enough to send to a separate 2-AI public wording review.

## Summary

- rows audited: `17`
- public-review-ready query-phase rows: `1`
- public speedup claims authorized here: `0`
- minimum phase duration for public speedup wording: `0.1` s
- minimum ratio for public speedup wording: `1.2`
- status counts: `{'candidate_but_needs_larger_scale_repeat': 7, 'not_public_speedup_candidate': 9, 'public_review_ready_query_phase_claim': 1}`

## Decisions

| App | Path | RTX phase (s) | Ratio | Status |
|---|---|---:|---:|---|
| `robot_collision_screening` | `prepared_pose_flags` | 0.000493 | 1179.643861 | `candidate_but_needs_larger_scale_repeat` |
| `outlier_detection` | `prepared_fixed_radius_density_summary` | 0.005828 | 4.640074 | `candidate_but_needs_larger_scale_repeat` |
| `dbscan_clustering` | `prepared_fixed_radius_core_flags` | 0.003751 | 6.620046 | `candidate_but_needs_larger_scale_repeat` |
| `database_analytics` | `prepared_db_session_sales_risk` | 0.103378 | 0.595806 | `not_public_speedup_candidate` |
| `database_analytics` | `prepared_db_session_regional_dashboard` | 0.143968 | 0.883570 | `not_public_speedup_candidate` |
| `service_coverage_gaps` | `prepared_gap_summary` | 0.136545 | 1.611541 | `public_review_ready_query_phase_claim` |
| `event_hotspot_screening` | `prepared_count_summary` | 0.253894 | 1.010722 | `not_public_speedup_candidate` |
| `facility_knn_assignment` | `coverage_threshold_prepared` | 0.003131 | 22.805076 | `candidate_but_needs_larger_scale_repeat` |
| `road_hazard_screening` | `road_hazard_native_summary_gate` | 0.172010 | 0.020763 | `not_public_speedup_candidate` |
| `segment_polygon_hitcount` | `segment_polygon_hitcount_native_experimental` | 0.003996 | 1.708308 | `candidate_but_needs_larger_scale_repeat` |
| `segment_polygon_anyhit_rows` | `segment_polygon_anyhit_rows_prepared_bounded_gate` | 0.004701 | 3.030858 | `candidate_but_needs_larger_scale_repeat` |
| `graph_analytics` | `graph_visibility_edges_gate` | 2.584184 | 0.219497 | `not_public_speedup_candidate` |
| `hausdorff_distance` | `directed_threshold_prepared` | 0.001364 | 0.016462 | `not_public_speedup_candidate` |
| `ann_candidate_search` | `candidate_threshold_prepared` | 0.000755 | 4.857461 | `candidate_but_needs_larger_scale_repeat` |
| `barnes_hut_force_app` | `node_coverage_prepared` | 0.004754 | 0.147059 | `not_public_speedup_candidate` |
| `polygon_pair_overlap_area_rows` | `polygon_pair_overlap_optix_native_assisted_phase_gate` | 10.052899 | 0.000146 | `not_public_speedup_candidate` |
| `polygon_set_jaccard` | `polygon_set_jaccard_optix_native_assisted_phase_gate` | 4.152796 | 0.003182 | `not_public_speedup_candidate` |

## Allowed Public Wording Candidates

### service_coverage_gaps / prepared_gap_summary

On the recorded RTX A5000 run, the bounded `service_coverage_gaps / prepared_gap_summary` query phase was 1.61x faster than the fastest same-semantics non-OptiX baseline for the measured sub-path. This is not a whole-app speedup claim.

## Boundary

- No row is authorized for front-page wording by this gate alone.
- Rows under 100 ms are intentionally held for larger-scale repeat evidence.
- Whole-app speedups remain disallowed unless a future audit measures whole-app same-semantics timing.
