# Goal2636 Strengthened Benchmark Rows

This artifact strengthens the weaker Goal2634 rows with scale ladders or larger fixtures.
It is internal engineering evidence only, not public speedup wording.

- Tier: `stress`
- Case repeat: `3`
- Generated: `2026-06-22T13:26:41+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | barnes_hut_node_coverage_bodies_131072 | 0.558796 | 0.306293 | 1.82x | `{"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| barnes_hut | barnes_hut_node_coverage_bodies_32768 | 0.128073 | 0.0723395 | 1.77x | `{"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_16384 | 0.462018 | 0.230272 | 2.01x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_262144 | 10.0065 | 5.41369 | 1.85x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_65536 | 2.52421 | 1.50746 | 1.67x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| rtnn | rtnn_clustered_262144_ranked_summary | 12.5002 | 1.38061 | 9.05x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_clustered_65536_ranked_summary | 0.599021 | 0.16876 | 3.55x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_shell_262144_ranked_summary | 1.62054 | 0.548861 | 2.95x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_shell_65536_ranked_summary | 0.124309 | 0.107554 | 1.16x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_uniform_262144_ranked_summary | 0.465297 | 0.432792 | 1.08x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_uniform_65536_ranked_summary | 0.115646 | 0.105871 | 1.09x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| spatial_rayjoin | rayjoin_lsi_authored_tiled_x2048 | 0.0534668 | 0.000137985 | 387x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| spatial_rayjoin | rayjoin_overlay_seed_authored_tiled_x2048 | 5.12313 | 0.000157773 | 3.25e+04x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| spatial_rayjoin | rayjoin_pip_authored_tiled_x2048 | 0.0459997 | 0.00519592 | 8.85x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| triangle_counting | triangle_count_rt_graph_2a1_cliques_20000 | 0.136631 | 0.00119287 | 115x | `{"embree": "timing_ms.query_median_ms converted-ms-to-sec", "optix": "timing_ms.query_median_ms converted-ms-to-sec"}` |
| triangle_counting | triangle_count_rt_graph_2a1_cliques_80000 | 0.548892 | 0.00157111 | 349x | `{"embree": "timing_ms.query_median_ms converted-ms-to-sec", "optix": "timing_ms.query_median_ms converted-ms-to-sec"}` |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| hausdorff_xhd | hausdorff_embree_threshold_copies_16384 | embree | ok | 0.462018 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_16384 | optix | ok | 0.230272 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_embree_threshold_copies_65536 | embree | ok | 2.52421 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_65536 | optix | ok | 1.50746 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_embree_threshold_copies_262144 | embree | ok | 10.0065 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_262144 | optix | ok | 5.41369 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_exact_grouped_seeded_pruned_points_32768 | optix | ok | 2.57416 | `primary.elapsed_sec` |
| hausdorff_xhd | hausdorff_optix_exact_grouped_seeded_pruned_points_131072 | optix | ok | 2.73867 | `primary.elapsed_sec` |
| spatial_rayjoin | rayjoin_embree_pip_tiled_x2048 | embree | ok | 0.0459997 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_pip_tiled_x2048 | optix | ok | 0.00519592 | `phases_sec.prepared_query_sec` |
| spatial_rayjoin | rayjoin_embree_lsi_tiled_x2048 | embree | ok | 0.0534668 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_lsi_tiled_x2048 | optix | ok | 0.000137985 | `phases_sec.prepared_query_sec` |
| spatial_rayjoin | rayjoin_embree_overlay_seed_tiled_x2048 | embree | ok | 5.12313 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_overlay_seed_tiled_x2048 | optix | ok | 0.000157773 | `phases_sec.prepared_query_sec` |
| rtnn | rtnn_embree_uniform_65536_ranked_summary | embree | ok | 0.115646 | `elapsed_sec` |
| rtnn | rtnn_optix_uniform_65536_ranked_summary | optix | ok | 0.105871 | `elapsed_sec` |
| rtnn | rtnn_embree_clustered_65536_ranked_summary | embree | ok | 0.599021 | `elapsed_sec` |
| rtnn | rtnn_optix_clustered_65536_ranked_summary | optix | ok | 0.16876 | `elapsed_sec` |
| rtnn | rtnn_embree_shell_65536_ranked_summary | embree | ok | 0.124309 | `elapsed_sec` |
| rtnn | rtnn_optix_shell_65536_ranked_summary | optix | ok | 0.107554 | `elapsed_sec` |
| rtnn | rtnn_embree_uniform_262144_ranked_summary | embree | ok | 0.465297 | `elapsed_sec` |
| rtnn | rtnn_optix_uniform_262144_ranked_summary | optix | ok | 0.432792 | `elapsed_sec` |
| rtnn | rtnn_embree_clustered_262144_ranked_summary | embree | ok | 12.5002 | `elapsed_sec` |
| rtnn | rtnn_optix_clustered_262144_ranked_summary | optix | ok | 1.38061 | `elapsed_sec` |
| rtnn | rtnn_embree_shell_262144_ranked_summary | embree | ok | 1.62054 | `elapsed_sec` |
| rtnn | rtnn_optix_shell_262144_ranked_summary | optix | ok | 0.548861 | `elapsed_sec` |
| barnes_hut | barnes_hut_embree_node_coverage_bodies_32768 | embree | ok | 0.128073 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_optix_node_coverage_bodies_32768 | optix | ok | 0.0723395 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_embree_node_coverage_bodies_131072 | embree | ok | 0.558796 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_optix_node_coverage_bodies_131072 | optix | ok | 0.306293 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| triangle_counting | triangle_counting_embree_rt_graph_2a1_cliques_20000 | embree | ok | 0.136631 | `timing_ms.query_median_ms converted-ms-to-sec` |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_cliques_20000 | optix | ok | 0.00119287 | `timing_ms.query_median_ms converted-ms-to-sec` |
| triangle_counting | triangle_counting_embree_rt_graph_2a1_cliques_80000 | embree | ok | 0.548892 | `timing_ms.query_median_ms converted-ms-to-sec` |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_cliques_80000 | optix | ok | 0.00157111 | `timing_ms.query_median_ms converted-ms-to-sec` |

## Boundary

- Hausdorff exact-witness rows are OptiX-only and are not ratioed.
- Spatial RayJoin rows use derived tiled fixtures, but still do not materialize full polygon overlay.
- RTNN rows are distribution-sensitive; clustered rows are the density-risk signal.
- Barnes-Hut rows are node-coverage only, not force aggregation.
- Triangle-counting rows are synthetic RT-2A1 backend-query ladders; paper datasets still require segmented/streamed lowering.
