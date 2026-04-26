# Goal1030 Local RTX Baseline Manifest

Date: 2026-04-26

This is a local baseline command manifest. It does not execute benchmarks, does not authorize speedup claims, and does not replace same-semantics review.

## Summary

- entries: `17`
- status_counts: `{'baseline_partial': 13, 'baseline_ready': 4}`

## Matrix

| App | RTX Path | Local Status | Command Count | Reason |
|---|---|---|---:|---|
| `robot_collision_screening` | `prepared_pose_flags` | `baseline_partial` | 2 | CPU and Embree app paths exist, but exact prepared-pose semantics need phase extraction. |
| `outlier_detection` | `prepared_fixed_radius_density_summary` | `baseline_ready` | 3 | CPU, Embree prepared threshold, and real SciPy cKDTree threshold-count paths are exposed; this Mac currently lacks SciPy, so SciPy is an optional local dependency gap until installed. |
| `dbscan_clustering` | `prepared_fixed_radius_core_flags` | `baseline_ready` | 3 | CPU, Embree prepared core-count, and real SciPy cKDTree threshold-count paths are exposed; this Mac currently lacks SciPy, so SciPy is an optional local dependency gap until installed. |
| `database_analytics:sales_risk` | `prepared_db_session_sales_risk` | `baseline_partial` | 2 | CPU and Embree compact summaries are local; PostgreSQL indexed baseline is Linux/PostgreSQL-gated. |
| `database_analytics:regional_dashboard` | `prepared_db_session_regional_dashboard` | `baseline_partial` | 2 | CPU and Embree compact summaries are local; PostgreSQL indexed baseline is Linux/PostgreSQL-gated. |
| `service_coverage_gaps` | `prepared_gap_summary` | `baseline_ready` | 3 | CPU, Embree summary, and SciPy paths are exposed by the app CLI; this Mac currently lacks SciPy, so SciPy is an optional local dependency gap until installed. |
| `event_hotspot_screening` | `prepared_count_summary` | `baseline_ready` | 3 | CPU, Embree summary, and SciPy paths are exposed by the app CLI; this Mac currently lacks SciPy, so SciPy is an optional local dependency gap until installed. |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `baseline_partial` | 3 | CPU/Embree/SciPy app paths exist, but coverage-threshold phase parity needs a dedicated extractor. |
| `road_hazard_screening` | `road_hazard_native_summary_gate` | `baseline_partial` | 2 | CPU and Embree compact summaries are local; PostGIS same-semantics baseline is Linux/PostGIS-gated. |
| `segment_polygon_hitcount` | `segment_polygon_hitcount_native_experimental` | `baseline_partial` | 2 | CPU and Embree hit-count paths are local; PostGIS same-semantics baseline is Linux/PostGIS-gated. |
| `segment_polygon_anyhit_rows` | `segment_polygon_anyhit_rows_prepared_bounded_gate` | `baseline_partial` | 2 | CPU and Embree compact outputs are local; bounded pair-row capacity and PostGIS parity need Linux review. |
| `graph_analytics` | `graph_visibility_edges_gate` | `baseline_partial` | 4 | CPU and Embree graph paths are local when GEOS/native oracle dependencies are present; visibility/BFS/triangle claims must stay separated. |
| `hausdorff_distance` | `directed_threshold_prepared` | `baseline_partial` | 2 | CPU and Embree exact summaries exist, but threshold-decision parity needs dedicated extraction. |
| `ann_candidate_search` | `candidate_threshold_prepared` | `baseline_partial` | 3 | CPU/Embree/SciPy app summaries exist, but candidate-threshold parity needs dedicated extraction. |
| `barnes_hut_force_app` | `node_coverage_prepared` | `baseline_partial` | 2 | CPU/Embree candidate summaries exist, but node-coverage threshold parity needs dedicated extraction. |
| `polygon_pair_overlap_area_rows` | `polygon_pair_overlap_optix_native_assisted_phase_gate` | `baseline_partial` | 2 | CPU and Embree summary paths are local; PostGIS same-semantics unit-cell baseline is Linux/PostGIS-gated. |
| `polygon_set_jaccard` | `polygon_set_jaccard_optix_native_assisted_phase_gate` | `baseline_partial` | 2 | CPU and Embree paths are local; PostGIS same-semantics unit-cell baseline is Linux/PostGIS-gated. |

## Commands

### `robot_collision_screening`

```bash
PYTHONPATH=src:. python3 examples/rtdl_robot_collision_screening_app.py --backend cpu --output-mode pose_flags --pose-count 200000 --obstacle-count 1024
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_robot_collision_screening_app.py --backend embree --output-mode pose_flags --pose-count 200000 --obstacle-count 1024
```

### `outlier_detection`

```bash
PYTHONPATH=src:. python3 examples/rtdl_outlier_detection_app.py --backend cpu --copies 20000 --output-mode density_count
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_outlier_detection_app.py --backend embree --copies 20000 --output-mode density_count --embree-summary-mode rt_count_threshold_prepared
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_outlier_detection_app.py --backend scipy --copies 20000 --output-mode density_count
```

### `dbscan_clustering`

```bash
PYTHONPATH=src:. python3 examples/rtdl_dbscan_clustering_app.py --backend cpu --copies 20000 --output-mode core_count
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_dbscan_clustering_app.py --backend embree --copies 20000 --output-mode core_count --embree-summary-mode rt_core_flags_prepared
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_dbscan_clustering_app.py --backend scipy --copies 20000 --output-mode core_count
```

### `database_analytics:sales_risk`

```bash
PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py --backend cpu --scenario sales_risk --copies 20000 --iterations 10 --output-mode compact_summary --strict
```

```bash
PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies 20000 --iterations 10 --output-mode compact_summary --strict
```

### `database_analytics:regional_dashboard`

```bash
PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py --backend cpu --scenario regional_dashboard --copies 20000 --iterations 10 --output-mode compact_summary --strict
```

```bash
PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario regional_dashboard --copies 20000 --iterations 10 --output-mode compact_summary --strict
```

### `service_coverage_gaps`

```bash
PYTHONPATH=src:. python3 examples/rtdl_service_coverage_gaps.py --backend cpu --copies 20000
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_service_coverage_gaps.py --backend embree --copies 20000 --embree-summary-mode gap_summary
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_service_coverage_gaps.py --backend scipy --copies 20000
```

### `event_hotspot_screening`

```bash
PYTHONPATH=src:. python3 examples/rtdl_event_hotspot_screening.py --backend cpu --copies 20000
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_event_hotspot_screening.py --backend embree --copies 20000 --embree-summary-mode count_summary
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_event_hotspot_screening.py --backend scipy --copies 20000
```

### `facility_knn_assignment`

```bash
PYTHONPATH=src:. python3 examples/rtdl_facility_knn_assignment.py --backend cpu --copies 20000 --output-mode summary
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_facility_knn_assignment.py --backend embree --copies 20000 --output-mode summary
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_facility_knn_assignment.py --backend scipy --copies 20000 --output-mode summary
```

### `road_hazard_screening`

```bash
PYTHONPATH=src:. python3 examples/rtdl_road_hazard_screening.py --backend cpu --copies 20000 --output-mode summary
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_road_hazard_screening.py --backend embree --copies 20000 --output-mode summary
```

### `segment_polygon_hitcount`

```bash
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu --copies 256
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_hitcount.py --backend embree --copies 256
```

### `segment_polygon_anyhit_rows`

```bash
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu --copies 256 --output-mode rows --output-capacity 4096
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_anyhit_rows.py --backend embree --copies 256 --output-mode rows --output-capacity 4096
```

### `graph_analytics`

```bash
PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py --backend cpu --scenario visibility_edges --copies 20000 --output-mode summary
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py --backend embree --scenario visibility_edges --copies 20000 --output-mode summary
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py --backend embree --scenario bfs --copies 20000 --output-mode summary
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py --backend embree --scenario triangle_count --copies 20000 --output-mode summary
```

### `hausdorff_distance`

```bash
PYTHONPATH=src:. python3 examples/rtdl_hausdorff_distance_app.py --backend cpu --copies 20000 --embree-result-mode directed_summary
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_hausdorff_distance_app.py --backend embree --copies 20000 --embree-result-mode directed_summary
```

### `ann_candidate_search`

```bash
PYTHONPATH=src:. python3 examples/rtdl_ann_candidate_app.py --backend cpu --copies 20000 --output-mode quality_summary
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_ann_candidate_app.py --backend embree --copies 20000 --output-mode quality_summary
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_ann_candidate_app.py --backend scipy --copies 20000 --output-mode quality_summary
```

### `barnes_hut_force_app`

```bash
PYTHONPATH=src:. python3 examples/rtdl_barnes_hut_force_app.py --backend cpu --body-count 200000 --output-mode candidate_summary
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_barnes_hut_force_app.py --backend embree --body-count 200000 --output-mode candidate_summary
```

### `polygon_pair_overlap_area_rows`

```bash
PYTHONPATH=src:. python3 examples/rtdl_polygon_pair_overlap_area_rows.py --backend cpu --copies 20000 --output-mode summary
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_polygon_pair_overlap_area_rows.py --backend embree --copies 20000 --output-mode summary
```

### `polygon_set_jaccard`

```bash
PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py --backend cpu --copies 20000
```

```bash
PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py --backend embree --copies 20000
```

