# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `84b1ed3dbc19415342d884850532c909e1814987`
- Scale: `standard`
- Case repeat: `1`
- Generated: `2026-05-26T23:37:06+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | node_coverage_candidate_summary | 0.61465 | 1.41422 | 0.435x | {"embree": "process_wall_median_sec", "optix": "process_wall_median_sec"} |
| contact_manifold | native_collect_k_i64 | 0.0127979 | 0.0117202 | 1.09x | {"embree": "native_collect_elapsed_sec", "optix": "native_collect_elapsed_sec"} |
| hausdorff_xhd | hausdorff_threshold_decision | 0.0956386 | 0.0301328 | 3.17x | {"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"} |
| librts_spatial_index | aabb_index_all_count_only | 21.161 | 0.680997 | 31.1x | {"embree": "elapsed_sec", "optix": "elapsed_sec"} |
| robot_collision | prepared_collision_flags | 0.00958579 | 0.00147287 | 6.51x | {"embree": "tail_medians.total_run_seconds", "optix": "tail_medians.total_run_seconds"} |
| rt_dbscan | dbscan_cluster_signature | 21.0626 | 1.63278 | 12.9x | {"embree": "elapsed_sec", "optix": "elapsed_sec"} |
| rtnn | prepared_3d_ranked_summary | 0.27916 | 0.00162952 | 171x | {"embree": "elapsed_sec", "optix": "elapsed_sec"} |
| spatial_rayjoin | rayjoin_all_generic_summary | 0.0215456 | 1.04091 | 0.0207x | {"embree": "workloads.total_elapsed_sec", "optix": "workloads.total_elapsed_sec"} |
| triangle_counting | triangle_count_summary | 0.612414 | 1.49616 | 0.409x | {"embree": "process_wall_median_sec", "optix": "process_wall_median_sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| hausdorff_xhd | hausdorff_embree_threshold | embree | ok | 0.0956386 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| hausdorff_xhd | hausdorff_optix_threshold | optix | ok | 0.0301328 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| spatial_rayjoin | spatial_rayjoin_embree_generic | embree | ok | 0.0215456 | workloads.total_elapsed_sec |
| spatial_rayjoin | spatial_rayjoin_optix_generic | optix | ok | 1.04091 | workloads.total_elapsed_sec |
| rt_dbscan | rt_dbscan_embree_fixed_radius_rows | embree | ok | 21.0626 | elapsed_sec |
| rt_dbscan | rt_dbscan_optix_grouped_stream | optix | ok | 1.63278 | elapsed_sec |
| robot_collision | robot_collision_embree_prepared_buffers | embree | ok | 0.00958579 | tail_medians.total_run_seconds |
| robot_collision | robot_collision_optix_prepared_device_buffers | optix | ok | 0.00147287 | tail_medians.total_run_seconds |
| raydb_style | raydb_embree_count | embree | failed |  | None |
| raydb_style | raydb_optix_count | optix | failed |  | None |
| raydb_style | raydb_embree_sum | embree | failed |  | None |
| raydb_style | raydb_optix_sum | optix | failed |  | None |
| barnes_hut | barnes_hut_embree_node_coverage | embree | ok | 0.61465 | process_wall_median_sec |
| barnes_hut | barnes_hut_optix_node_coverage | optix | ok | 1.41422 | process_wall_median_sec |
| librts_spatial_index | librts_embree_aabb_index | embree | ok | 21.161 | elapsed_sec |
| librts_spatial_index | librts_optix_aabb_index | optix | ok | 0.680997 | elapsed_sec |
| rtnn | rtnn_embree_prepared_3d_ranked_summary | embree | ok | 0.27916 | elapsed_sec |
| rtnn | rtnn_optix_prepared_3d_ranked_summary | optix | ok | 0.00162952 | elapsed_sec |
| triangle_counting | triangle_counting_embree_summary | embree | ok | 0.612414 | process_wall_median_sec |
| triangle_counting | triangle_counting_optix_summary | optix | ok | 1.49616 | process_wall_median_sec |
| contact_manifold | contact_manifold_embree_native_collect_k | embree | ok | 0.0127979 | native_collect_elapsed_sec |
| contact_manifold | contact_manifold_optix_native_collect_k | optix | ok | 0.0117202 | native_collect_elapsed_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
