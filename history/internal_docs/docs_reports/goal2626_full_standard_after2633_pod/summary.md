# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `ac0abfb3b47d29d10dab10701838fe530513271f`
- Scale: `standard`
- Case repeat: `1`
- Generated: `2026-05-27T04:20:13+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | node_coverage_prepared_threshold_decision | 0.0350694 | 0.00837431 | 4.19x | {"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"} |
| contact_manifold | native_collect_k_i64 | 0.0112383 | 0.0122115 | 0.92x | {"embree": "native_collect_elapsed_sec", "optix": "native_collect_elapsed_sec"} |
| hausdorff_xhd | hausdorff_threshold_decision | 0.099465 | 0.030408 | 3.27x | {"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"} |
| librts_spatial_index | aabb_index_all_count_only | 20.7959 | 1.0113 | 20.6x | {"embree": "elapsed_sec", "optix": "elapsed_sec"} |
| raydb_style | raydb_grouped_count | 0.1858 | 0.000731998 | 254x | {"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_median_sec"} |
| raydb_style | raydb_grouped_sum | 0.236247 | 0.00403211 | 58.6x | {"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_median_sec"} |
| robot_collision | prepared_collision_flags | 0.00932187 | 0.00260676 | 3.58x | {"embree": "tail_medians.total_run_seconds", "optix": "tail_medians.total_run_seconds"} |
| rt_dbscan | dbscan_cluster_signature | 20.5097 | 1.27554 | 16.1x | {"embree": "elapsed_sec", "optix": "elapsed_sec"} |
| rtnn | prepared_3d_ranked_summary | 0.256645 | 0.011392 | 22.5x | {"embree": "elapsed_sec", "optix": "elapsed_sec"} |
| spatial_rayjoin | rayjoin_all_backend_query_summary | 0.0205852 | 0.000567341 | 36.3x | {"embree": "workloads.total_elapsed_sec", "optix": "prepared_query_total_sec"} |
| triangle_counting | triangle_count_rt_graph_2a1_summary | 0.0383412 | 0.000597202 | 64.2x | {"embree": "timing_ms.query_median_ms converted-ms-to-sec", "optix": "timing_ms.query_median_ms converted-ms-to-sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| hausdorff_xhd | hausdorff_embree_threshold | embree | ok | 0.099465 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| hausdorff_xhd | hausdorff_optix_threshold | optix | ok | 0.030408 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| spatial_rayjoin | spatial_rayjoin_embree_generic | embree | ok | 0.0205852 | workloads.total_elapsed_sec |
| spatial_rayjoin | spatial_rayjoin_optix_prepared_full_route | optix | ok | 0.000567341 | prepared_query_total_sec |
| rt_dbscan | rt_dbscan_embree_fixed_radius_rows | embree | ok | 20.5097 | elapsed_sec |
| rt_dbscan | rt_dbscan_optix_grouped_stream | optix | ok | 1.27554 | elapsed_sec |
| robot_collision | robot_collision_embree_prepared_buffers | embree | ok | 0.00932187 | tail_medians.total_run_seconds |
| robot_collision | robot_collision_optix_prepared_device_buffers | optix | ok | 0.00260676 | tail_medians.total_run_seconds |
| raydb_style | raydb_embree_count | embree | ok | 0.1858 | metadata.timings.query_sec |
| raydb_style | raydb_optix_partner_resident_count | optix | ok | 0.000731998 | metadata.timings.query_median_sec |
| raydb_style | raydb_embree_sum | embree | ok | 0.236247 | metadata.timings.query_sec |
| raydb_style | raydb_optix_partner_resident_sum | optix | ok | 0.00403211 | metadata.timings.query_median_sec |
| barnes_hut | barnes_hut_embree_node_coverage | embree | ok | 0.0350694 | node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec |
| barnes_hut | barnes_hut_optix_node_coverage | optix | ok | 0.00837431 | node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec |
| librts_spatial_index | librts_embree_aabb_index | embree | ok | 20.7959 | elapsed_sec |
| librts_spatial_index | librts_optix_aabb_index | optix | ok | 1.0113 | elapsed_sec |
| rtnn | rtnn_embree_prepared_3d_ranked_summary | embree | ok | 0.256645 | elapsed_sec |
| rtnn | rtnn_optix_prepared_3d_ranked_summary | optix | ok | 0.011392 | elapsed_sec |
| triangle_counting | triangle_counting_embree_rt_graph_2a1 | embree | ok | 0.0383412 | timing_ms.query_median_ms converted-ms-to-sec |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_partner | optix | ok | 0.000597202 | timing_ms.query_median_ms converted-ms-to-sec |
| contact_manifold | contact_manifold_embree_native_collect_k | embree | ok | 0.0112383 | native_collect_elapsed_sec |
| contact_manifold | contact_manifold_optix_native_collect_k | optix | ok | 0.0122115 | native_collect_elapsed_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
