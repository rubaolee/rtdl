# Goal2636 Strengthened Benchmark Rows

This artifact strengthens the weaker Goal2634 rows with scale ladders or larger fixtures.
It is internal engineering evidence only, not public speedup wording.

- Tier: `standard`
- Case repeat: `1`
- Generated: `2026-06-20T06:08:57+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | barnes_hut_node_coverage_bodies_32768 | 0.13223 | 0.0711865 | 1.86x | `{"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| barnes_hut | barnes_hut_node_coverage_bodies_8192 | 0.0284442 | 0.010399 | 2.74x | `{"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_16384 | 0.472846 | 0.233493 | 2.03x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_4096 | 0.100531 | 0.0387298 | 2.6x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_65536 | 2.53201 | 1.55091 | 1.63x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| rtnn | rtnn_clustered_65536_ranked_summary | 0.746337 | 0.171 | 4.36x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_shell_65536_ranked_summary | 0.123412 | 0.106215 | 1.16x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_uniform_65536_ranked_summary | 0.115008 | 0.119889 | 0.959x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| spatial_rayjoin | rayjoin_lsi_authored_tiled_x512 | 0.0449833 | 0.000123091 | 365x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| spatial_rayjoin | rayjoin_overlay_seed_authored_tiled_x512 | 0.360242 | 6.64741e-05 | 5.42e+03x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| spatial_rayjoin | rayjoin_pip_authored_tiled_x512 | 0.0421171 | 0.00185143 | 22.7x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| triangle_counting | triangle_count_rt_graph_2a1_cliques_20000 | 0.137554 | 0.00120419 | 114x | `{"embree": "timing_ms.query_median_ms converted-ms-to-sec", "optix": "timing_ms.query_median_ms converted-ms-to-sec"}` |
| triangle_counting | triangle_count_rt_graph_2a1_cliques_5000 | 0.0247227 | 0.000674885 | 36.6x | `{"embree": "timing_ms.query_median_ms converted-ms-to-sec", "optix": "timing_ms.query_median_ms converted-ms-to-sec"}` |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| hausdorff_xhd | hausdorff_embree_threshold_copies_4096 | embree | ok | 0.100531 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_4096 | optix | ok | 0.0387298 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_embree_threshold_copies_16384 | embree | ok | 0.472846 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_16384 | optix | ok | 0.233493 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_embree_threshold_copies_65536 | embree | ok | 2.53201 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_65536 | optix | ok | 1.55091 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_exact_grouped_seeded_pruned_points_8192 | optix | ok | 4.47765 | `primary.elapsed_sec` |
| hausdorff_xhd | hausdorff_optix_exact_grouped_seeded_pruned_points_32768 | optix | ok | 5.44186 | `primary.elapsed_sec` |
| spatial_rayjoin | rayjoin_embree_pip_tiled_x512 | embree | ok | 0.0421171 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_pip_tiled_x512 | optix | ok | 0.00185143 | `phases_sec.prepared_query_sec` |
| spatial_rayjoin | rayjoin_embree_lsi_tiled_x512 | embree | ok | 0.0449833 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_lsi_tiled_x512 | optix | ok | 0.000123091 | `phases_sec.prepared_query_sec` |
| spatial_rayjoin | rayjoin_embree_overlay_seed_tiled_x512 | embree | ok | 0.360242 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_overlay_seed_tiled_x512 | optix | ok | 6.64741e-05 | `phases_sec.prepared_query_sec` |
| rtnn | rtnn_embree_uniform_65536_ranked_summary | embree | ok | 0.115008 | `elapsed_sec` |
| rtnn | rtnn_optix_uniform_65536_ranked_summary | optix | ok | 0.119889 | `elapsed_sec` |
| rtnn | rtnn_embree_clustered_65536_ranked_summary | embree | ok | 0.746337 | `elapsed_sec` |
| rtnn | rtnn_optix_clustered_65536_ranked_summary | optix | ok | 0.171 | `elapsed_sec` |
| rtnn | rtnn_embree_shell_65536_ranked_summary | embree | ok | 0.123412 | `elapsed_sec` |
| rtnn | rtnn_optix_shell_65536_ranked_summary | optix | ok | 0.106215 | `elapsed_sec` |
| barnes_hut | barnes_hut_embree_node_coverage_bodies_8192 | embree | ok | 0.0284442 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_optix_node_coverage_bodies_8192 | optix | ok | 0.010399 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_embree_node_coverage_bodies_32768 | embree | ok | 0.13223 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_optix_node_coverage_bodies_32768 | optix | ok | 0.0711865 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| triangle_counting | triangle_counting_embree_rt_graph_2a1_cliques_5000 | embree | ok | 0.0247227 | `timing_ms.query_median_ms converted-ms-to-sec` |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_cliques_5000 | optix | ok | 0.000674885 | `timing_ms.query_median_ms converted-ms-to-sec` |
| triangle_counting | triangle_counting_embree_rt_graph_2a1_cliques_20000 | embree | ok | 0.137554 | `timing_ms.query_median_ms converted-ms-to-sec` |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_cliques_20000 | optix | ok | 0.00120419 | `timing_ms.query_median_ms converted-ms-to-sec` |

## Boundary

- Hausdorff exact-witness rows are OptiX-only and are not ratioed.
- Spatial RayJoin rows use derived tiled fixtures, but still do not materialize full polygon overlay.
- RTNN rows are distribution-sensitive; clustered rows are the density-risk signal.
- Barnes-Hut rows are node-coverage only, not force aggregation.
- Triangle-counting rows are synthetic RT-2A1 backend-query ladders; paper datasets still require segmented/streamed lowering.
