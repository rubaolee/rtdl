# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `56e1f9b230cdef6d803191c8804f192133b4d020`
- Scale: `standard`
- Case repeat: `1`
- Generated: `2026-05-27T04:42:50+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | node_coverage_prepared_threshold_decision | 0.0388851 | 0.00855045 | 4.55x | {"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"} |
| contact_manifold | generic_aabb_broadphase_collect_k | 0.485812 | 0.0184764 | 26.3x | {"embree": "run_phases.emit_aabb_intersection_pair_rows_2d_median_sec", "optix": "run_phases.emit_aabb_intersection_pair_rows_2d_median_sec"} |
| hausdorff_xhd | hausdorff_threshold_decision | 0.102451 | 0.0311073 | 3.29x | {"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"} |
| librts_spatial_index | aabb_index_all_count_only | 20.707 | 0.691477 | 29.9x | {"embree": "elapsed_sec", "optix": "elapsed_sec"} |
| raydb_style | raydb_grouped_count | 0.222185 | 0.000793088 | 280x | {"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_median_sec"} |
| raydb_style | raydb_grouped_sum | 0.243746 | 0.000977349 | 249x | {"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_median_sec"} |
| robot_collision | prepared_collision_flags | 0.00853798 | 0.00161413 | 5.29x | {"embree": "tail_medians.total_run_seconds", "optix": "tail_medians.total_run_seconds"} |
| rt_dbscan | dbscan_cluster_signature | 20.6102 | 1.62144 | 12.7x | {"embree": "elapsed_sec", "optix": "elapsed_sec"} |
| rtnn | prepared_3d_ranked_summary | 0.2638 | 0.00153247 | 172x | {"embree": "elapsed_sec", "optix": "elapsed_sec"} |
| spatial_rayjoin | rayjoin_all_backend_query_summary | 0.0203149 | 0.000529638 | 38.4x | {"embree": "workloads.total_elapsed_sec", "optix": "prepared_query_total_sec"} |
| triangle_counting | triangle_count_rt_graph_2a1_summary | 0.039049 | 0.000364401 | 107x | {"embree": "timing_ms.query_median_ms converted-ms-to-sec", "optix": "timing_ms.query_median_ms converted-ms-to-sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| hausdorff_xhd | hausdorff_embree_threshold | embree | ok | 0.102451 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| hausdorff_xhd | hausdorff_optix_threshold | optix | ok | 0.0311073 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| spatial_rayjoin | spatial_rayjoin_embree_generic | embree | ok | 0.0203149 | workloads.total_elapsed_sec |
| spatial_rayjoin | spatial_rayjoin_optix_prepared_full_route | optix | ok | 0.000529638 | prepared_query_total_sec |
| rt_dbscan | rt_dbscan_embree_fixed_radius_rows | embree | ok | 20.6102 | elapsed_sec |
| rt_dbscan | rt_dbscan_optix_grouped_stream | optix | ok | 1.62144 | elapsed_sec |
| robot_collision | robot_collision_embree_prepared_buffers | embree | ok | 0.00853798 | tail_medians.total_run_seconds |
| robot_collision | robot_collision_optix_prepared_device_buffers | optix | ok | 0.00161413 | tail_medians.total_run_seconds |
| raydb_style | raydb_embree_count | embree | ok | 0.222185 | metadata.timings.query_sec |
| raydb_style | raydb_optix_partner_resident_count | optix | ok | 0.000793088 | metadata.timings.query_median_sec |
| raydb_style | raydb_embree_sum | embree | ok | 0.243746 | metadata.timings.query_sec |
| raydb_style | raydb_optix_partner_resident_sum | optix | ok | 0.000977349 | metadata.timings.query_median_sec |
| barnes_hut | barnes_hut_embree_node_coverage | embree | ok | 0.0388851 | node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec |
| barnes_hut | barnes_hut_optix_node_coverage | optix | ok | 0.00855045 | node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec |
| librts_spatial_index | librts_embree_aabb_index | embree | ok | 20.707 | elapsed_sec |
| librts_spatial_index | librts_optix_aabb_index | optix | ok | 0.691477 | elapsed_sec |
| rtnn | rtnn_embree_prepared_3d_ranked_summary | embree | ok | 0.2638 | elapsed_sec |
| rtnn | rtnn_optix_prepared_3d_ranked_summary | optix | ok | 0.00153247 | elapsed_sec |
| triangle_counting | triangle_counting_embree_rt_graph_2a1 | embree | ok | 0.039049 | timing_ms.query_median_ms converted-ms-to-sec |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_partner | optix | ok | 0.000364401 | timing_ms.query_median_ms converted-ms-to-sec |
| contact_manifold | contact_manifold_embree_aabb_broadphase_collect_k | embree | ok | 0.485812 | run_phases.emit_aabb_intersection_pair_rows_2d_median_sec |
| contact_manifold | contact_manifold_optix_aabb_broadphase_collect_k | optix | ok | 0.0184764 | run_phases.emit_aabb_intersection_pair_rows_2d_median_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
