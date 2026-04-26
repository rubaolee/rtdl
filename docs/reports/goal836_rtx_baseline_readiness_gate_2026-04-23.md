# Goal836 RTX Baseline Readiness Gate

Status: `ok`

This readiness gate only inspects local baseline evidence. It does not run benchmarks, start cloud resources, promote deferred apps, or authorize RTX speedup claims.

## Summary

- rows checked: `17`
- required baseline artifacts: `50`
- valid artifacts: `50`
- missing artifacts: `0`
- invalid artifacts: `0`

## Row Readiness

| Section | App | Path | Status | Missing | Invalid | Valid |
|---|---|---|---|---:|---:|---:|
| active | database_analytics | prepared_db_session_sales_risk | ok | 0 | 0 | 3 |
| active | database_analytics | prepared_db_session_regional_dashboard | ok | 0 | 0 | 3 |
| active | outlier_detection | prepared_fixed_radius_density_summary | ok | 0 | 0 | 3 |
| active | dbscan_clustering | prepared_fixed_radius_core_flags | ok | 0 | 0 | 3 |
| active | robot_collision_screening | prepared_pose_flags | ok | 0 | 0 | 2 |
| active | service_coverage_gaps | prepared_gap_summary | ok | 0 | 0 | 3 |
| active | event_hotspot_screening | prepared_count_summary | ok | 0 | 0 | 3 |
| active | facility_knn_assignment | coverage_threshold_prepared | ok | 0 | 0 | 2 |
| deferred | graph_analytics | graph_visibility_edges_gate | ok | 0 | 0 | 7 |
| deferred | road_hazard_screening | road_hazard_native_summary_gate | ok | 0 | 0 | 3 |
| deferred | segment_polygon_hitcount | segment_polygon_hitcount_native_experimental | ok | 0 | 0 | 3 |
| deferred | hausdorff_distance | directed_threshold_prepared | ok | 0 | 0 | 2 |
| deferred | ann_candidate_search | candidate_threshold_prepared | ok | 0 | 0 | 2 |
| deferred | barnes_hut_force_app | node_coverage_prepared | ok | 0 | 0 | 2 |
| deferred | segment_polygon_anyhit_rows | segment_polygon_anyhit_rows_prepared_bounded_gate | ok | 0 | 0 | 3 |
| deferred | polygon_pair_overlap_area_rows | polygon_pair_overlap_optix_native_assisted_phase_gate | ok | 0 | 0 | 3 |
| deferred | polygon_set_jaccard | polygon_set_jaccard_optix_native_assisted_phase_gate | ok | 0 | 0 | 3 |

## Missing Or Invalid Baselines

## Release Rule

An RTX speedup claim package is incomplete while this gate reports `needs_baselines`.
