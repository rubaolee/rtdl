# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `8384a38376567fe518d89721453eb4433de08312`
- Scale: `large`
- Case repeat: `3`
- Generated: `2026-06-22T10:19:58+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | node_coverage_prepared_threshold_decision | 0.134177 | 0.0423665 | 3.17x | {"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"} |
| contact_manifold | generic_aabb_broadphase_collect_k | 0.0838748 | 0.0575376 | 1.46x | {"embree": "run_phases.emit_aabb_intersection_pair_rows_2d_median_sec", "optix": "run_phases.emit_aabb_intersection_pair_rows_2d_median_sec"} |
| hausdorff_xhd | hausdorff_threshold_decision | 0.571787 | 0.277334 | 2.06x | {"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"} |
| librts_spatial_index | aabb_index_all_count_only | 0.0244974 | 0.222862 | 0.11x | {"embree": "run_phases.query_median_sec", "optix": "run_phases.query_median_sec"} |
| raydb_style | raydb_grouped_count | 0.257125 | 0.000630513 | 408x | {"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_median_sec"} |
| raydb_style | raydb_grouped_sum | 0.24802 | 0.00067148 | 369x | {"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_median_sec"} |
| robot_collision | prepared_collision_flags | 0.0723999 | 0.00853574 | 8.48x | {"embree": "tail_medians.total_run_seconds", "optix": "tail_medians.total_run_seconds"} |
| rt_dbscan | dbscan_cluster_signature | 113.815 | 0.0381233 | 2.99e+03x | {"embree": "elapsed_sec", "optix": "elapsed_sec"} |
| rtnn | prepared_3d_ranked_summary | 0.464964 | 0.423937 | 1.1x | {"embree": "elapsed_median_sec", "optix": "elapsed_median_sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| hausdorff_xhd | hausdorff_embree_threshold | embree | ok | 0.571787 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| hausdorff_xhd | hausdorff_optix_threshold | optix | ok | 0.277334 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| spatial_rayjoin | spatial_rayjoin_embree_generic | embree | ok | 0.0355704 | workloads.total_elapsed_sec |
| spatial_rayjoin | spatial_rayjoin_optix_prepared_full_route | optix | failed |  | None |
| rt_dbscan | rt_dbscan_embree_fixed_radius_rows | embree | ok | 113.815 | elapsed_sec |
| rt_dbscan | rt_dbscan_optix_grouped_stream | optix | ok | 0.0381233 | elapsed_sec |
| robot_collision | robot_collision_embree_prepared_buffers | embree | ok | 0.0723999 | tail_medians.total_run_seconds |
| robot_collision | robot_collision_optix_prepared_device_buffers | optix | ok | 0.00853574 | tail_medians.total_run_seconds |
| raydb_style | raydb_embree_count | embree | ok | 0.257125 | metadata.timings.query_sec |
| raydb_style | raydb_optix_partner_resident_count | optix | ok | 0.000630513 | metadata.timings.query_median_sec |
| raydb_style | raydb_embree_sum | embree | ok | 0.24802 | metadata.timings.query_sec |
| raydb_style | raydb_optix_partner_resident_sum | optix | ok | 0.00067148 | metadata.timings.query_median_sec |
| barnes_hut | barnes_hut_embree_node_coverage | embree | ok | 0.134177 | node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec |
| barnes_hut | barnes_hut_optix_node_coverage | optix | ok | 0.0423665 | node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec |
| librts_spatial_index | librts_embree_aabb_index | embree | ok | 0.0244974 | run_phases.query_median_sec |
| librts_spatial_index | librts_optix_aabb_index | optix | ok | 0.222862 | run_phases.query_median_sec |
| rtnn | rtnn_embree_prepared_3d_ranked_summary | embree | ok | 0.464964 | elapsed_median_sec |
| rtnn | rtnn_optix_prepared_3d_ranked_summary | optix | ok | 0.423937 | elapsed_median_sec |
| triangle_counting | triangle_counting_embree_rt_graph_2a1 | embree | ok | 0.137709 | timing_ms.query_median_ms converted-ms-to-sec |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_partner | optix | failed |  | None |
| contact_manifold | contact_manifold_embree_aabb_broadphase_collect_k | embree | ok | 0.0838748 | run_phases.emit_aabb_intersection_pair_rows_2d_median_sec |
| contact_manifold | contact_manifold_optix_aabb_broadphase_collect_k | optix | ok | 0.0575376 | run_phases.emit_aabb_intersection_pair_rows_2d_median_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
