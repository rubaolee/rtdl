# Goal2636 Strengthened Benchmark Rows

This artifact strengthens the weaker Goal2634 rows with scale ladders or larger fixtures.
It is internal engineering evidence only, not public speedup wording.

- Tier: `stress`
- Case repeat: `1`
- Generated: `2026-05-27T05:54:14+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | barnes_hut_node_coverage_bodies_131072 | 0.385655 | 0.304904 | 1.26x | `{"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| barnes_hut | barnes_hut_node_coverage_bodies_32768 | 0.110231 | 0.0374388 | 2.94x | `{"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_16384 | 0.369679 | 0.164627 | 2.25x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_262144 | 7.31725 | 4.63951 | 1.58x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_65536 | 1.69796 | 1.01777 | 1.67x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| rtnn | rtnn_clustered_262144_ranked_summary | 14.9944 | 1.37452 | 10.9x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_clustered_65536_ranked_summary | 2.11638 | 0.0933383 | 22.7x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_shell_262144_ranked_summary | 9.3538 | 0.186924 | 50x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_shell_65536_ranked_summary | 0.866792 | 0.00552687 | 157x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_uniform_262144_ranked_summary | 3.15816 | 0.00990457 | 319x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_uniform_65536_ranked_summary | 0.262757 | 0.00226594 | 116x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| spatial_rayjoin | rayjoin_lsi_authored_tiled_x2048 | 0.0356758 | 0.000455981 | 78.2x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| spatial_rayjoin | rayjoin_overlay_seed_authored_tiled_x2048 | 3.78287 | 0.897468 | 4.22x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| spatial_rayjoin | rayjoin_pip_authored_tiled_x2048 | 0.0349485 | 0.000510602 | 68.4x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| triangle_counting | triangle_count_rt_graph_2a1_cliques_20000 | 0.101853 | 0.000703277 | 145x | `{"embree": "timing_ms.query_median_ms converted-ms-to-sec", "optix": "timing_ms.query_median_ms converted-ms-to-sec"}` |
| triangle_counting | triangle_count_rt_graph_2a1_cliques_80000 | 0.403863 | 0.000867688 | 465x | `{"embree": "timing_ms.query_median_ms converted-ms-to-sec", "optix": "timing_ms.query_median_ms converted-ms-to-sec"}` |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| hausdorff_xhd | hausdorff_embree_threshold_copies_16384 | embree | ok | 0.369679 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_16384 | optix | ok | 0.164627 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_embree_threshold_copies_65536 | embree | ok | 1.69796 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_65536 | optix | ok | 1.01777 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_embree_threshold_copies_262144 | embree | ok | 7.31725 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_262144 | optix | ok | 4.63951 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_exact_grouped_seeded_pruned_points_32768 | optix | ok | 1.41121 | `primary.elapsed_sec` |
| hausdorff_xhd | hausdorff_optix_exact_grouped_seeded_pruned_points_131072 | optix | ok | 1.34782 | `primary.elapsed_sec` |
| spatial_rayjoin | rayjoin_embree_pip_tiled_x2048 | embree | ok | 0.0349485 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_prepared_pip_tiled_x2048 | optix | ok | 0.000510602 | `phases_sec.prepared_query_sec` |
| spatial_rayjoin | rayjoin_embree_lsi_tiled_x2048 | embree | ok | 0.0356758 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_prepared_lsi_tiled_x2048 | optix | ok | 0.000455981 | `phases_sec.prepared_query_sec` |
| spatial_rayjoin | rayjoin_embree_overlay_seed_tiled_x2048 | embree | ok | 3.78287 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_prepared_overlay_seed_tiled_x2048 | optix | ok | 0.897468 | `phases_sec.prepared_query_sec` |
| rtnn | rtnn_embree_uniform_65536_ranked_summary | embree | ok | 0.262757 | `elapsed_sec` |
| rtnn | rtnn_optix_uniform_65536_ranked_summary | optix | ok | 0.00226594 | `elapsed_sec` |
| rtnn | rtnn_embree_clustered_65536_ranked_summary | embree | ok | 2.11638 | `elapsed_sec` |
| rtnn | rtnn_optix_clustered_65536_ranked_summary | optix | ok | 0.0933383 | `elapsed_sec` |
| rtnn | rtnn_embree_shell_65536_ranked_summary | embree | ok | 0.866792 | `elapsed_sec` |
| rtnn | rtnn_optix_shell_65536_ranked_summary | optix | ok | 0.00552687 | `elapsed_sec` |
| rtnn | rtnn_embree_uniform_262144_ranked_summary | embree | ok | 3.15816 | `elapsed_sec` |
| rtnn | rtnn_optix_uniform_262144_ranked_summary | optix | ok | 0.00990457 | `elapsed_sec` |
| rtnn | rtnn_embree_clustered_262144_ranked_summary | embree | ok | 14.9944 | `elapsed_sec` |
| rtnn | rtnn_optix_clustered_262144_ranked_summary | optix | ok | 1.37452 | `elapsed_sec` |
| rtnn | rtnn_embree_shell_262144_ranked_summary | embree | ok | 9.3538 | `elapsed_sec` |
| rtnn | rtnn_optix_shell_262144_ranked_summary | optix | ok | 0.186924 | `elapsed_sec` |
| barnes_hut | barnes_hut_embree_node_coverage_bodies_32768 | embree | ok | 0.110231 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_optix_node_coverage_bodies_32768 | optix | ok | 0.0374388 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_embree_node_coverage_bodies_131072 | embree | ok | 0.385655 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_optix_node_coverage_bodies_131072 | optix | ok | 0.304904 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| triangle_counting | triangle_counting_embree_rt_graph_2a1_cliques_20000 | embree | ok | 0.101853 | `timing_ms.query_median_ms converted-ms-to-sec` |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_cliques_20000 | optix | ok | 0.000703277 | `timing_ms.query_median_ms converted-ms-to-sec` |
| triangle_counting | triangle_counting_embree_rt_graph_2a1_cliques_80000 | embree | ok | 0.403863 | `timing_ms.query_median_ms converted-ms-to-sec` |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_cliques_80000 | optix | ok | 0.000867688 | `timing_ms.query_median_ms converted-ms-to-sec` |

## Boundary

- Hausdorff exact-witness rows are OptiX-only and are not ratioed.
- Spatial RayJoin rows use derived tiled fixtures, but still do not materialize full polygon overlay.
- RTNN rows are distribution-sensitive; clustered rows are the density-risk signal.
- Barnes-Hut rows are node-coverage only, not force aggregation.
- Triangle-counting rows are synthetic RT-2A1 backend-query ladders; paper datasets still require segmented/streamed lowering.
