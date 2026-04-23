# Goal838 Local RTX Baseline Collection Manifest

This is a local collection manifest only. It does not run heavy benchmarks, write valid baseline artifacts, start cloud, or authorize speedup claims.

## Summary

- collector_needed: `4`
- deferred_until_app_gate_active: `9`
- linux_postgresql_required: `2`
- local_command_ready: `6`
- optional_dependency_or_reference_required: `2`

## Actions

| Status | App | Path | Baseline | Scale | Artifact |
|---|---|---|---|---|---|
| local_command_ready | database_analytics | prepared_db_session_sales_risk | cpu_oracle_compact_summary | {"copies": 20000, "iterations": 10} | docs/reports/goal835_baseline_database_analytics_prepared_db_session_sales_risk_cpu_oracle_compact_summary_2026-04-23.json |
| local_command_ready | database_analytics | prepared_db_session_sales_risk | embree_compact_summary | {"copies": 20000, "iterations": 10} | docs/reports/goal835_baseline_database_analytics_prepared_db_session_sales_risk_embree_compact_summary_2026-04-23.json |
| linux_postgresql_required | database_analytics | prepared_db_session_sales_risk | postgresql_same_semantics_on_linux_when_available | {"copies": 20000, "iterations": 10} | docs/reports/goal835_baseline_database_analytics_prepared_db_session_sales_risk_postgresql_same_semantics_on_linux_when_available_2026-04-23.json |
| local_command_ready | database_analytics | prepared_db_session_regional_dashboard | cpu_oracle_compact_summary | {"copies": 20000, "iterations": 10} | docs/reports/goal835_baseline_database_analytics_prepared_db_session_regional_dashboard_cpu_oracle_compact_summary_2026-04-23.json |
| local_command_ready | database_analytics | prepared_db_session_regional_dashboard | embree_compact_summary | {"copies": 20000, "iterations": 10} | docs/reports/goal835_baseline_database_analytics_prepared_db_session_regional_dashboard_embree_compact_summary_2026-04-23.json |
| linux_postgresql_required | database_analytics | prepared_db_session_regional_dashboard | postgresql_same_semantics_on_linux_when_available | {"copies": 20000, "iterations": 10} | docs/reports/goal835_baseline_database_analytics_prepared_db_session_regional_dashboard_postgresql_same_semantics_on_linux_when_available_2026-04-23.json |
| collector_needed | outlier_detection | prepared_fixed_radius_density_summary | cpu_scalar_threshold_count_oracle | {"copies": 20000, "iterations": 10} | docs/reports/goal835_baseline_outlier_detection_prepared_fixed_radius_density_summary_cpu_scalar_threshold_count_oracle_2026-04-23.json |
| local_command_ready | outlier_detection | prepared_fixed_radius_density_summary | embree_scalar_or_summary_path | {"copies": 20000, "iterations": 10} | docs/reports/goal835_baseline_outlier_detection_prepared_fixed_radius_density_summary_embree_scalar_or_summary_path_2026-04-23.json |
| optional_dependency_or_reference_required | outlier_detection | prepared_fixed_radius_density_summary | scipy_or_reference_neighbor_baseline_when_used_in_app_report | {"copies": 20000, "iterations": 10} | docs/reports/goal835_baseline_outlier_detection_prepared_fixed_radius_density_summary_scipy_or_reference_neighbor_baseline_when_used_in_app_report_2026-04-23.json |
| collector_needed | dbscan_clustering | prepared_fixed_radius_core_flags | cpu_scalar_threshold_count_oracle | {"copies": 20000, "iterations": 10} | docs/reports/goal835_baseline_dbscan_clustering_prepared_fixed_radius_core_flags_cpu_scalar_threshold_count_oracle_2026-04-23.json |
| local_command_ready | dbscan_clustering | prepared_fixed_radius_core_flags | embree_scalar_or_summary_path | {"copies": 20000, "iterations": 10} | docs/reports/goal835_baseline_dbscan_clustering_prepared_fixed_radius_core_flags_embree_scalar_or_summary_path_2026-04-23.json |
| optional_dependency_or_reference_required | dbscan_clustering | prepared_fixed_radius_core_flags | scipy_or_reference_neighbor_baseline_when_used_in_app_report | {"copies": 20000, "iterations": 10} | docs/reports/goal835_baseline_dbscan_clustering_prepared_fixed_radius_core_flags_scipy_or_reference_neighbor_baseline_when_used_in_app_report_2026-04-23.json |
| collector_needed | robot_collision_screening | prepared_pose_flags | cpu_oracle_pose_count | {"iterations": 10, "obstacle_count": 1024, "pose_count": 200000} | docs/reports/goal835_baseline_robot_collision_screening_prepared_pose_flags_cpu_oracle_pose_count_2026-04-23.json |
| collector_needed | robot_collision_screening | prepared_pose_flags | embree_anyhit_pose_count_or_equivalent_compact_summary | {"iterations": 10, "obstacle_count": 1024, "pose_count": 200000} | docs/reports/goal835_baseline_robot_collision_screening_prepared_pose_flags_embree_anyhit_pose_count_or_equivalent_compact_summary_2026-04-23.json |
| deferred_until_app_gate_active | service_coverage_gaps | prepared_gap_summary | cpu_oracle_summary |  | docs/reports/goal835_baseline_service_coverage_gaps_prepared_gap_summary_cpu_oracle_summary_2026-04-23.json |
| deferred_until_app_gate_active | service_coverage_gaps | prepared_gap_summary | embree_summary_path |  | docs/reports/goal835_baseline_service_coverage_gaps_prepared_gap_summary_embree_summary_path_2026-04-23.json |
| deferred_until_app_gate_active | service_coverage_gaps | prepared_gap_summary | scipy_baseline_when_available |  | docs/reports/goal835_baseline_service_coverage_gaps_prepared_gap_summary_scipy_baseline_when_available_2026-04-23.json |
| deferred_until_app_gate_active | event_hotspot_screening | prepared_count_summary | cpu_oracle_summary |  | docs/reports/goal835_baseline_event_hotspot_screening_prepared_count_summary_cpu_oracle_summary_2026-04-23.json |
| deferred_until_app_gate_active | event_hotspot_screening | prepared_count_summary | embree_summary_path |  | docs/reports/goal835_baseline_event_hotspot_screening_prepared_count_summary_embree_summary_path_2026-04-23.json |
| deferred_until_app_gate_active | event_hotspot_screening | prepared_count_summary | scipy_baseline_when_available |  | docs/reports/goal835_baseline_event_hotspot_screening_prepared_count_summary_scipy_baseline_when_available_2026-04-23.json |
| deferred_until_app_gate_active | segment_polygon_hitcount | segment_polygon_hitcount_native_experimental | cpu_python_reference |  | docs/reports/goal835_baseline_segment_polygon_hitcount_segment_polygon_hitcount_native_experimental_cpu_python_reference_2026-04-23.json |
| deferred_until_app_gate_active | segment_polygon_hitcount | segment_polygon_hitcount_native_experimental | optix_host_indexed |  | docs/reports/goal835_baseline_segment_polygon_hitcount_segment_polygon_hitcount_native_experimental_optix_host_indexed_2026-04-23.json |
| deferred_until_app_gate_active | segment_polygon_hitcount | segment_polygon_hitcount_native_experimental | postgis_when_available |  | docs/reports/goal835_baseline_segment_polygon_hitcount_segment_polygon_hitcount_native_experimental_postgis_when_available_2026-04-23.json |

## Ready Local Commands

### database_analytics / prepared_db_session_sales_risk / cpu_oracle_compact_summary

```bash
python3 scripts/goal756_db_prepared_session_perf.py --backend cpu --scenario sales_risk --copies 20000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal835_baseline_database_analytics_prepared_db_session_sales_risk_cpu_oracle_compact_summary_2026-04-23.raw.json
```

### database_analytics / prepared_db_session_sales_risk / embree_compact_summary

```bash
python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies 20000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal835_baseline_database_analytics_prepared_db_session_sales_risk_embree_compact_summary_2026-04-23.raw.json
```

### database_analytics / prepared_db_session_regional_dashboard / cpu_oracle_compact_summary

```bash
python3 scripts/goal756_db_prepared_session_perf.py --backend cpu --scenario regional_dashboard --copies 20000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal835_baseline_database_analytics_prepared_db_session_regional_dashboard_cpu_oracle_compact_summary_2026-04-23.raw.json
```

### database_analytics / prepared_db_session_regional_dashboard / embree_compact_summary

```bash
python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario regional_dashboard --copies 20000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal835_baseline_database_analytics_prepared_db_session_regional_dashboard_embree_compact_summary_2026-04-23.raw.json
```

### outlier_detection / prepared_fixed_radius_density_summary / embree_scalar_or_summary_path

```bash
python3 scripts/goal715_embree_fixed_radius_summary_perf.py --copies 20000 --repeats 10 --warmups 1 --output docs/reports/goal835_baseline_outlier_detection_prepared_fixed_radius_density_summary_embree_scalar_or_summary_path_2026-04-23.raw.json
```

### dbscan_clustering / prepared_fixed_radius_core_flags / embree_scalar_or_summary_path

```bash
python3 scripts/goal715_embree_fixed_radius_summary_perf.py --copies 20000 --repeats 10 --warmups 1 --output docs/reports/goal835_baseline_dbscan_clustering_prepared_fixed_radius_core_flags_embree_scalar_or_summary_path_2026-04-23.raw.json
```

