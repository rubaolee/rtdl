# Goal836 RTX Baseline Readiness Gate

Status: `needs_baselines`

This readiness gate only inspects local baseline evidence. It does not run benchmarks, start cloud resources, promote deferred apps, or authorize RTX speedup claims.

## Summary

- rows checked: `8`
- required baseline artifacts: `23`
- valid artifacts: `12`
- missing artifacts: `11`
- invalid artifacts: `0`

## Row Readiness

| Section | App | Path | Status | Missing | Invalid | Valid |
|---|---|---|---|---:|---:|---:|
| active | database_analytics | prepared_db_session_sales_risk | ok | 0 | 0 | 3 |
| active | database_analytics | prepared_db_session_regional_dashboard | ok | 0 | 0 | 3 |
| active | outlier_detection | prepared_fixed_radius_density_summary | needs_baselines | 1 | 0 | 2 |
| active | dbscan_clustering | prepared_fixed_radius_core_flags | needs_baselines | 1 | 0 | 2 |
| active | robot_collision_screening | prepared_pose_flags | ok | 0 | 0 | 2 |
| deferred | service_coverage_gaps | prepared_gap_summary | needs_baselines | 3 | 0 | 0 |
| deferred | event_hotspot_screening | prepared_count_summary | needs_baselines | 3 | 0 | 0 |
| deferred | segment_polygon_hitcount | segment_polygon_hitcount_native_experimental | needs_baselines | 3 | 0 | 0 |

## Missing Or Invalid Baselines

### outlier_detection / prepared_fixed_radius_density_summary

- `scipy_or_reference_neighbor_baseline_when_used_in_app_report`: `missing` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_outlier_detection_prepared_fixed_radius_density_summary_scipy_or_reference_neighbor_baseline_when_used_in_app_report_2026-04-23.json`
- error: artifact file is missing

### dbscan_clustering / prepared_fixed_radius_core_flags

- `scipy_or_reference_neighbor_baseline_when_used_in_app_report`: `missing` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_dbscan_clustering_prepared_fixed_radius_core_flags_scipy_or_reference_neighbor_baseline_when_used_in_app_report_2026-04-23.json`
- error: artifact file is missing

### service_coverage_gaps / prepared_gap_summary

- `cpu_oracle_summary`: `missing` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_service_coverage_gaps_prepared_gap_summary_cpu_oracle_summary_2026-04-23.json`
- error: artifact file is missing
- `embree_summary_path`: `missing` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_service_coverage_gaps_prepared_gap_summary_embree_summary_path_2026-04-23.json`
- error: artifact file is missing
- `scipy_baseline_when_available`: `missing` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_service_coverage_gaps_prepared_gap_summary_scipy_baseline_when_available_2026-04-23.json`
- error: artifact file is missing

### event_hotspot_screening / prepared_count_summary

- `cpu_oracle_summary`: `missing` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_event_hotspot_screening_prepared_count_summary_cpu_oracle_summary_2026-04-23.json`
- error: artifact file is missing
- `embree_summary_path`: `missing` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_event_hotspot_screening_prepared_count_summary_embree_summary_path_2026-04-23.json`
- error: artifact file is missing
- `scipy_baseline_when_available`: `missing` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_event_hotspot_screening_prepared_count_summary_scipy_baseline_when_available_2026-04-23.json`
- error: artifact file is missing

### segment_polygon_hitcount / segment_polygon_hitcount_native_experimental

- `cpu_python_reference`: `missing` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_segment_polygon_hitcount_segment_polygon_hitcount_native_experimental_cpu_python_reference_2026-04-23.json`
- error: artifact file is missing
- `optix_host_indexed`: `missing` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_segment_polygon_hitcount_segment_polygon_hitcount_native_experimental_optix_host_indexed_2026-04-23.json`
- error: artifact file is missing
- `postgis_when_available`: `missing` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_segment_polygon_hitcount_segment_polygon_hitcount_native_experimental_postgis_when_available_2026-04-23.json`
- error: artifact file is missing

## Release Rule

An RTX speedup claim package is incomplete while this gate reports `needs_baselines`.

