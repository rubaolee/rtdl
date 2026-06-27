# Goal2636 Strengthened Benchmark Rows

This artifact strengthens the weaker Goal2634 rows with scale ladders or larger fixtures.
It is internal engineering evidence only, not public speedup wording.

- Tier: `stress`
- Case repeat: `3`
- Generated: `2026-06-23T11:49:11+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | barnes_hut_node_coverage_bodies_131072 | 0.561161 | 0.28753 | 1.95x | `{"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| barnes_hut | barnes_hut_node_coverage_bodies_32768 | 0.133277 | 0.0718509 | 1.85x | `{"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_16384 | 0.472202 | 0.23227 | 2.03x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_262144 | 9.83366 | 5.4103 | 1.82x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_65536 | 2.52339 | 1.5957 | 1.58x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| rtnn | rtnn_clustered_262144_ranked_summary | 13.1314 | 1.37977 | 9.52x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_clustered_65536_ranked_summary | 0.696721 | 0.16984 | 4.1x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_shell_262144_ranked_summary | 1.63495 | 0.547537 | 2.99x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_shell_65536_ranked_summary | 0.124321 | 0.105338 | 1.18x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_uniform_262144_ranked_summary | 0.465589 | 0.424924 | 1.1x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_uniform_65536_ranked_summary | 0.114226 | 0.103875 | 1.1x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| spatial_rayjoin | rayjoin_lsi_authored_tiled_x2048 | 0.0511847 | 0.00012216 | 419x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| spatial_rayjoin | rayjoin_pip_authored_tiled_x2048 | 0.049956 | 0.00516102 | 9.68x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| triangle_counting | triangle_count_rt_graph_2a1_cliques_20000 | 0.137969 | 0.00119827 | 115x | `{"embree": "timing_ms.query_median_ms converted-ms-to-sec", "optix": "timing_ms.query_median_ms converted-ms-to-sec"}` |
| triangle_counting | triangle_count_rt_graph_2a1_cliques_80000 | 0.542197 | 0.00156777 | 346x | `{"embree": "timing_ms.query_median_ms converted-ms-to-sec", "optix": "timing_ms.query_median_ms converted-ms-to-sec"}` |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| hausdorff_xhd | hausdorff_embree_threshold_copies_16384 | embree | ok | 0.472202 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_16384 | optix | ok | 0.23227 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_embree_threshold_copies_65536 | embree | ok | 2.52339 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_65536 | optix | ok | 1.5957 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_embree_threshold_copies_262144 | embree | ok | 9.83366 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_262144 | optix | ok | 5.4103 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_exact_grouped_seeded_pruned_points_32768 | optix | ok | 3.45376 | `primary.elapsed_sec` |
| hausdorff_xhd | hausdorff_optix_exact_grouped_seeded_pruned_points_131072 | optix | ok | 3.4443 | `primary.elapsed_sec` |
| spatial_rayjoin | rayjoin_embree_pip_tiled_x2048 | embree | ok | 0.049956 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_pip_tiled_x2048 | optix | ok | 0.00516102 | `phases_sec.prepared_query_sec` |
| spatial_rayjoin | rayjoin_embree_lsi_tiled_x2048 | embree | ok | 0.0511847 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_lsi_tiled_x2048 | optix | ok | 0.00012216 | `phases_sec.prepared_query_sec` |
| spatial_rayjoin | rayjoin_embree_overlay_seed_tiled_x2048 | embree | ok | 5.02671 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_overlay_seed_tiled_x2048 | optix | failed | n/a | `run` |
| rtnn | rtnn_embree_uniform_65536_ranked_summary | embree | ok | 0.114226 | `elapsed_sec` |
| rtnn | rtnn_optix_uniform_65536_ranked_summary | optix | ok | 0.103875 | `elapsed_sec` |
| rtnn | rtnn_embree_clustered_65536_ranked_summary | embree | ok | 0.696721 | `elapsed_sec` |
| rtnn | rtnn_optix_clustered_65536_ranked_summary | optix | ok | 0.16984 | `elapsed_sec` |
| rtnn | rtnn_embree_shell_65536_ranked_summary | embree | ok | 0.124321 | `elapsed_sec` |
| rtnn | rtnn_optix_shell_65536_ranked_summary | optix | ok | 0.105338 | `elapsed_sec` |
| rtnn | rtnn_embree_uniform_262144_ranked_summary | embree | ok | 0.465589 | `elapsed_sec` |
| rtnn | rtnn_optix_uniform_262144_ranked_summary | optix | ok | 0.424924 | `elapsed_sec` |
| rtnn | rtnn_embree_clustered_262144_ranked_summary | embree | ok | 13.1314 | `elapsed_sec` |
| rtnn | rtnn_optix_clustered_262144_ranked_summary | optix | ok | 1.37977 | `elapsed_sec` |
| rtnn | rtnn_embree_shell_262144_ranked_summary | embree | ok | 1.63495 | `elapsed_sec` |
| rtnn | rtnn_optix_shell_262144_ranked_summary | optix | ok | 0.547537 | `elapsed_sec` |
| barnes_hut | barnes_hut_embree_node_coverage_bodies_32768 | embree | ok | 0.133277 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_optix_node_coverage_bodies_32768 | optix | ok | 0.0718509 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_embree_node_coverage_bodies_131072 | embree | ok | 0.561161 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_optix_node_coverage_bodies_131072 | optix | ok | 0.28753 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| triangle_counting | triangle_counting_embree_rt_graph_2a1_cliques_20000 | embree | ok | 0.137969 | `timing_ms.query_median_ms converted-ms-to-sec` |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_cliques_20000 | optix | ok | 0.00119827 | `timing_ms.query_median_ms converted-ms-to-sec` |
| triangle_counting | triangle_counting_embree_rt_graph_2a1_cliques_80000 | embree | ok | 0.542197 | `timing_ms.query_median_ms converted-ms-to-sec` |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_cliques_80000 | optix | ok | 0.00156777 | `timing_ms.query_median_ms converted-ms-to-sec` |

## Boundary

- Hausdorff exact-witness rows are OptiX-only and are not ratioed.
- Spatial RayJoin rows use derived tiled fixtures, but still do not materialize full polygon overlay.
- RTNN rows are distribution-sensitive; clustered rows are the density-risk signal.
- Barnes-Hut rows are node-coverage only, not force aggregation.
- Triangle-counting rows are synthetic RT-2A1 backend-query ladders; paper datasets still require segmented/streamed lowering.
