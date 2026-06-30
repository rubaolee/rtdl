# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `0a2ed76efeab07e79ccad004b978befde0d383db`
- Scale: `standard`
- Case repeat: `3`
- Generated: `2026-05-26T18:47:59+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | node_coverage_candidate_summary | 0.602833 | 1.53632 | 0.392x | {"embree": "process_wall_median_sec", "optix": "process_wall_median_sec"} |
| hausdorff_xhd | hausdorff_threshold_decision | 0.101699 | 0.0318415 | 3.19x | {"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"} |
| raydb_style | raydb_grouped_count | 0.39152 | 1.3316 | 0.294x | {"embree": "process_wall_median_sec", "optix": "process_wall_median_sec"} |
| raydb_style | raydb_grouped_sum | 0.429403 | 1.55514 | 0.276x | {"embree": "process_wall_median_sec", "optix": "process_wall_median_sec"} |
| robot_collision | prepared_collision_flags | 0.00937482 | 0.00147787 | 6.34x | {"embree": "tail_medians.total_run_seconds", "optix": "tail_medians.total_run_seconds"} |
| spatial_rayjoin | rayjoin_all_generic_summary | 0.00105102 | 0.283771 | 0.0037x | {"embree": "workloads.lsi.elapsed_sec", "optix": "workloads.lsi.elapsed_sec"} |
| triangle_counting | triangle_count_summary | 0.599089 | 1.3062 | 0.459x | {"embree": "process_wall_median_sec", "optix": "process_wall_median_sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| hausdorff_xhd | hausdorff_embree_threshold | embree | ok | 0.101699 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| hausdorff_xhd | hausdorff_optix_threshold | optix | ok | 0.0318415 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| spatial_rayjoin | spatial_rayjoin_embree_generic | embree | ok | 0.00105102 | workloads.lsi.elapsed_sec |
| spatial_rayjoin | spatial_rayjoin_optix_generic | optix | ok | 0.283771 | workloads.lsi.elapsed_sec |
| rt_dbscan | rt_dbscan_embree_grouped_stream | embree | unsupported |  | The promoted app front door has no Embree grouped fixed-radius continuation mode; current comparable row is OptiX-only. |
| rt_dbscan | rt_dbscan_optix_grouped_stream | optix | ok | 1.7143 | elapsed_sec |
| robot_collision | robot_collision_embree_prepared_buffers | embree | ok | 0.00937482 | tail_medians.total_run_seconds |
| robot_collision | robot_collision_optix_prepared_device_buffers | optix | ok | 0.00147787 | tail_medians.total_run_seconds |
| raydb_style | raydb_embree_count | embree | ok | 0.39152 | process_wall_median_sec |
| raydb_style | raydb_optix_count | optix | ok | 1.3316 | process_wall_median_sec |
| raydb_style | raydb_embree_sum | embree | ok | 0.429403 | process_wall_median_sec |
| raydb_style | raydb_optix_sum | optix | ok | 1.55514 | process_wall_median_sec |
| barnes_hut | barnes_hut_embree_node_coverage | embree | ok | 0.602833 | process_wall_median_sec |
| barnes_hut | barnes_hut_optix_node_coverage | optix | ok | 1.53632 | process_wall_median_sec |
| librts_spatial_index | librts_embree_aabb_index | embree | unsupported |  | AABB_INDEX_QUERY_2D is currently implemented as generic CPU reference and OptiX native paths; there is no Embree AABB index front door. |
| librts_spatial_index | librts_optix_aabb_index | optix | ok | 0.852479 | elapsed_sec |
| rtnn | rtnn_embree_prepared_3d_ranked_summary | embree | unsupported |  | The promoted RTNN benchmark path is a prepared 3-D OptiX fixed-radius ranked-summary row; no same-contract Embree front door exists. |
| rtnn | rtnn_optix_prepared_3d_ranked_summary | optix | ok | 0.00164372 | elapsed_sec |
| triangle_counting | triangle_counting_embree_summary | embree | ok | 0.599089 | process_wall_median_sec |
| triangle_counting | triangle_counting_optix_summary | optix | ok | 1.3062 | process_wall_median_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
