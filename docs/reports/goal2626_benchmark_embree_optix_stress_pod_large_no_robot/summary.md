# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `11da92848a30be3a71d76ac58d8f53b1c8621ba7`
- Scale: `large`
- Case repeat: `1`
- Generated: `2026-05-26T19:11:31+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | node_coverage_candidate_summary | 0.949983 | 1.76206 | 0.539x | {"embree": "process_wall_median_sec", "optix": "process_wall_median_sec"} |
| hausdorff_xhd | hausdorff_threshold_decision | 0.399736 | 0.370397 | 1.08x | {"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"} |
| triangle_counting | triangle_count_summary | 0.915364 | 1.56583 | 0.585x | {"embree": "process_wall_median_sec", "optix": "process_wall_median_sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| hausdorff_xhd | hausdorff_embree_threshold | embree | ok | 0.399736 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| hausdorff_xhd | hausdorff_optix_threshold | optix | ok | 0.370397 | run_phases.query_fixed_radius_threshold_reached_count_sec |
| rt_dbscan | rt_dbscan_embree_grouped_stream | embree | unsupported |  | The promoted app front door has no Embree grouped fixed-radius continuation mode; current comparable row is OptiX-only. |
| rt_dbscan | rt_dbscan_optix_grouped_stream | optix | ok | 2.14414 | elapsed_sec |
| barnes_hut | barnes_hut_embree_node_coverage | embree | ok | 0.949983 | process_wall_median_sec |
| barnes_hut | barnes_hut_optix_node_coverage | optix | ok | 1.76206 | process_wall_median_sec |
| librts_spatial_index | librts_embree_aabb_index | embree | unsupported |  | AABB_INDEX_QUERY_2D is currently implemented as generic CPU reference and OptiX native paths; there is no Embree AABB index front door. |
| librts_spatial_index | librts_optix_aabb_index | optix | ok | 2.31278 | elapsed_sec |
| rtnn | rtnn_embree_prepared_3d_ranked_summary | embree | unsupported |  | The promoted RTNN benchmark path is a prepared 3-D OptiX fixed-radius ranked-summary row; no same-contract Embree front door exists. |
| rtnn | rtnn_optix_prepared_3d_ranked_summary | optix | ok | 0.0102268 | elapsed_sec |
| triangle_counting | triangle_counting_embree_summary | embree | ok | 0.915364 | process_wall_median_sec |
| triangle_counting | triangle_counting_optix_summary | optix | ok | 1.56583 | process_wall_median_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
