# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: ``
- Scale: `standard`
- Case repeat: `1`
- Generated: `2026-06-20T14:19:43+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | node_coverage_prepared_threshold_decision | 0.0281065 | 0.0103854 | 2.71x | {"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"} |
| contact_manifold | generic_aabb_broadphase_collect_k | 0.0298087 | 0.0237424 | 1.26x | {"embree": "run_phases.emit_aabb_intersection_pair_rows_2d_median_sec", "optix": "run_phases.emit_aabb_intersection_pair_rows_2d_median_sec"} |
| hausdorff_xhd | hausdorff_threshold_decision | 0.101819 | 0.0391708 | 2.6x | {"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"} |
| librts_spatial_index | aabb_index_all_count_only | 0.0113064 | 0.177699 | 0.0636x | {"embree": "run_phases.query_median_sec", "optix": "run_phases.query_median_sec"} |
| raydb_style | raydb_grouped_count | 0.247182 | 0.00065995 | 375x | {"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_median_sec"} |
| raydb_style | raydb_grouped_sum | 0.237683 | 0.000661816 | 359x | {"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_median_sec"} |
| robot_collision | prepared_collision_flags | 0.0113328 | 0.00221325 | 5.12x | {"embree": "tail_medians.total_run_seconds", "optix": "tail_medians.total_run_seconds"} |
| rt_dbscan | dbscan_cluster_signature | 26.1053 | 0.0139415 | 1.87e+03x | {"embree": "elapsed_sec", "optix": "elapsed_sec"} |
| rtnn | prepared_3d_ranked_summary | 0.114486 | 0.104158 | 1.1x | {"embree": "elapsed_median_sec", "optix": "elapsed_median_sec"} |
| spatial_rayjoin | rayjoin_all_backend_query_summary | 0.0342377 | 1.07156 | 0.032x | {"embree": "workloads.total_elapsed_sec", "optix": "prepared_query_total_sec"} |
| triangle_counting | triangle_count_rt_graph_2a1_summary | 0.0245235 | 0.000549182 | 44.7x | {"embree": "timing_ms.query_median_ms converted-ms-to-sec", "optix": "timing_ms.query_median_ms converted-ms-to-sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| hausdorff_xhd | hausdorff_embree_threshold | embree | ok | 0.101819 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| hausdorff_xhd | hausdorff_optix_threshold | optix | ok | 0.0391708 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| spatial_rayjoin | spatial_rayjoin_embree_generic | embree | ok | 0.0342377 | workloads.total_elapsed_sec |
| spatial_rayjoin | spatial_rayjoin_optix_prepared_full_route | optix | ok | 1.07156 | prepared_query_total_sec |
| rt_dbscan | rt_dbscan_embree_fixed_radius_rows | embree | ok | 26.1053 | elapsed_sec |
| rt_dbscan | rt_dbscan_optix_grouped_stream | optix | ok | 0.0139415 | elapsed_sec |
| robot_collision | robot_collision_embree_prepared_buffers | embree | ok | 0.0113328 | tail_medians.total_run_seconds |
| robot_collision | robot_collision_optix_prepared_device_buffers | optix | ok | 0.00221325 | tail_medians.total_run_seconds |
| raydb_style | raydb_embree_count | embree | ok | 0.247182 | metadata.timings.query_sec |
| raydb_style | raydb_optix_partner_resident_count | optix | ok | 0.00065995 | metadata.timings.query_median_sec |
| raydb_style | raydb_embree_sum | embree | ok | 0.237683 | metadata.timings.query_sec |
| raydb_style | raydb_optix_partner_resident_sum | optix | ok | 0.000661816 | metadata.timings.query_median_sec |
| barnes_hut | barnes_hut_embree_node_coverage | embree | ok | 0.0281065 | node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec |
| barnes_hut | barnes_hut_optix_node_coverage | optix | ok | 0.0103854 | node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec |
| librts_spatial_index | librts_embree_aabb_index | embree | ok | 0.0113064 | run_phases.query_median_sec |
| librts_spatial_index | librts_optix_aabb_index | optix | ok | 0.177699 | run_phases.query_median_sec |
| rtnn | rtnn_embree_prepared_3d_ranked_summary | embree | ok | 0.114486 | elapsed_median_sec |
| rtnn | rtnn_optix_prepared_3d_ranked_summary | optix | ok | 0.104158 | elapsed_median_sec |
| triangle_counting | triangle_counting_embree_rt_graph_2a1 | embree | ok | 0.0245235 | timing_ms.query_median_ms converted-ms-to-sec |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_partner | optix | ok | 0.000549182 | timing_ms.query_median_ms converted-ms-to-sec |
| contact_manifold | contact_manifold_embree_aabb_broadphase_collect_k | embree | ok | 0.0298087 | run_phases.emit_aabb_intersection_pair_rows_2d_median_sec |
| contact_manifold | contact_manifold_optix_aabb_broadphase_collect_k | optix | ok | 0.0237424 | run_phases.emit_aabb_intersection_pair_rows_2d_median_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
