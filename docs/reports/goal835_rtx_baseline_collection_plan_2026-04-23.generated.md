# Goal835 RTX Baseline Collection Plan

Status: `ok`

This plan is a local baseline checklist. It does not run benchmarks, start cloud, promote deferred apps, or authorize RTX speedup claims.

## Summary

- active entries: `5`
- deferred entries: `3`
- invalid entries: `0`

## Baseline Checklist

| Section | App | Path | Required baselines | Required phases | Claim limit |
|---|---|---|---|---|---|
| active | database_analytics | prepared_db_session_sales_risk | cpu_oracle_compact_summary, embree_compact_summary, postgresql_same_semantics_on_linux_when_available | input_pack_or_table_build, backend_prepare, native_query, copyback_or_materialization, python_summary_postprocess | prepared DB sub-path only; not a DBMS or SQL-engine speedup claim |
| active | database_analytics | prepared_db_session_regional_dashboard | cpu_oracle_compact_summary, embree_compact_summary, postgresql_same_semantics_on_linux_when_available | input_pack_or_table_build, backend_prepare, native_query, copyback_or_materialization, python_summary_postprocess | prepared DB sub-path only; not a DBMS or SQL-engine speedup claim |
| active | outlier_detection | prepared_fixed_radius_density_summary | cpu_scalar_threshold_count_oracle, embree_scalar_or_summary_path, scipy_or_reference_neighbor_baseline_when_used_in_app_report | point_pack, backend_prepare, native_threshold_query, scalar_copyback, python_postprocess | outlier threshold-count or DBSCAN core-count summary only; not row-returning neighbors or full DBSCAN cluster expansion |
| active | dbscan_clustering | prepared_fixed_radius_core_flags | cpu_scalar_threshold_count_oracle, embree_scalar_or_summary_path, scipy_or_reference_neighbor_baseline_when_used_in_app_report | point_pack, backend_prepare, native_threshold_query, scalar_copyback, python_postprocess | outlier threshold-count or DBSCAN core-count summary only; not row-returning neighbors or full DBSCAN cluster expansion |
| active | robot_collision_screening | prepared_pose_flags | cpu_oracle_pose_count, embree_anyhit_pose_count_or_equivalent_compact_summary | pose_and_obstacle_generation, ray_pack, backend_scene_prepare, pose_index_prepare, native_anyhit_query, scalar_copyback, oracle_validation_separate | scalar pose-count collision screening only; not full robot planning, kinematics, CCD, or witness-row output |
| deferred | service_coverage_gaps | prepared_gap_summary | cpu_oracle_summary, embree_summary_path, scipy_baseline_when_available | input_build, optix_prepare, optix_query, python_postprocess | prepared compact summary only; not nearest-row or whole-app speedup |
| deferred | event_hotspot_screening | prepared_count_summary | cpu_oracle_summary, embree_summary_path, scipy_baseline_when_available | input_build, optix_prepare, optix_query, python_postprocess | prepared compact summary only; not nearest-row or whole-app speedup |
| deferred | segment_polygon_hitcount | segment_polygon_hitcount_native_experimental | cpu_python_reference, optix_host_indexed, postgis_when_available | records, strict_pass, strict_failures, status | experimental native hit-count gate only; not pair-row any-hit or road-hazard whole-app speedup |

## Review Rule

A public RTX speedup claim may not be made from a cloud artifact unless the matching row above has same-semantics baseline artifacts, correctness parity, and phase-separated timing.

