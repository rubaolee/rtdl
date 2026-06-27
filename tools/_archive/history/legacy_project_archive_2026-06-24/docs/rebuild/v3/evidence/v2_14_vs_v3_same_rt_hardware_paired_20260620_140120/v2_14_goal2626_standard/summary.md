# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `8384a38376567fe518d89721453eb4433de08312`
- Scale: `standard`
- Case repeat: `1`
- Generated: `2026-06-20T14:09:04+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | node_coverage_prepared_threshold_decision | 0.0289173 | 0.0104044 | 2.78x | {"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"} |
| contact_manifold | generic_aabb_broadphase_collect_k | 0.029919 | 0.0234874 | 1.27x | {"embree": "run_phases.emit_aabb_intersection_pair_rows_2d_median_sec", "optix": "run_phases.emit_aabb_intersection_pair_rows_2d_median_sec"} |
| hausdorff_xhd | hausdorff_threshold_decision | 0.102274 | 0.0404937 | 2.53x | {"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"} |
| librts_spatial_index | aabb_index_all_count_only | 0.0136378 | 0.199243 | 0.0684x | {"embree": "run_phases.query_median_sec", "optix": "run_phases.query_median_sec"} |
| raydb_style | raydb_grouped_count | 0.237497 | 0.000633989 | 375x | {"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_median_sec"} |
| raydb_style | raydb_grouped_sum | 0.238459 | 0.000764076 | 312x | {"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_median_sec"} |
| robot_collision | prepared_collision_flags | 0.0113679 | 0.00227615 | 4.99x | {"embree": "tail_medians.total_run_seconds", "optix": "tail_medians.total_run_seconds"} |
| rt_dbscan | dbscan_cluster_signature | 26.154 | 0.0137046 | 1.91e+03x | {"embree": "elapsed_sec", "optix": "elapsed_sec"} |
| rtnn | prepared_3d_ranked_summary | 0.11489 | 0.104552 | 1.1x | {"embree": "elapsed_median_sec", "optix": "elapsed_median_sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| hausdorff_xhd | hausdorff_embree_threshold | embree | ok | 0.102274 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| hausdorff_xhd | hausdorff_optix_threshold | optix | ok | 0.0404937 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| spatial_rayjoin | spatial_rayjoin_embree_generic | embree | ok | 0.0292882 | workloads.total_elapsed_sec |
| spatial_rayjoin | spatial_rayjoin_optix_prepared_full_route | optix | failed |  | None |
| rt_dbscan | rt_dbscan_embree_fixed_radius_rows | embree | ok | 26.154 | elapsed_sec |
| rt_dbscan | rt_dbscan_optix_grouped_stream | optix | ok | 0.0137046 | elapsed_sec |
| robot_collision | robot_collision_embree_prepared_buffers | embree | ok | 0.0113679 | tail_medians.total_run_seconds |
| robot_collision | robot_collision_optix_prepared_device_buffers | optix | ok | 0.00227615 | tail_medians.total_run_seconds |
| raydb_style | raydb_embree_count | embree | ok | 0.237497 | metadata.timings.query_sec |
| raydb_style | raydb_optix_partner_resident_count | optix | ok | 0.000633989 | metadata.timings.query_median_sec |
| raydb_style | raydb_embree_sum | embree | ok | 0.238459 | metadata.timings.query_sec |
| raydb_style | raydb_optix_partner_resident_sum | optix | ok | 0.000764076 | metadata.timings.query_median_sec |
| barnes_hut | barnes_hut_embree_node_coverage | embree | ok | 0.0289173 | node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec |
| barnes_hut | barnes_hut_optix_node_coverage | optix | ok | 0.0104044 | node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec |
| librts_spatial_index | librts_embree_aabb_index | embree | ok | 0.0136378 | run_phases.query_median_sec |
| librts_spatial_index | librts_optix_aabb_index | optix | ok | 0.199243 | run_phases.query_median_sec |
| rtnn | rtnn_embree_prepared_3d_ranked_summary | embree | ok | 0.11489 | elapsed_median_sec |
| rtnn | rtnn_optix_prepared_3d_ranked_summary | optix | ok | 0.104552 | elapsed_median_sec |
| triangle_counting | triangle_counting_embree_rt_graph_2a1 | embree | ok | 0.0240627 | timing_ms.query_median_ms converted-ms-to-sec |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_partner | optix | failed |  | None |
| contact_manifold | contact_manifold_embree_aabb_broadphase_collect_k | embree | ok | 0.029919 | run_phases.emit_aabb_intersection_pair_rows_2d_median_sec |
| contact_manifold | contact_manifold_optix_aabb_broadphase_collect_k | optix | ok | 0.0234874 | run_phases.emit_aabb_intersection_pair_rows_2d_median_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
