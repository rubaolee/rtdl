# Goal2636 Strengthened Benchmark Rows

This artifact strengthens the weaker Goal2634 rows with scale ladders or larger fixtures.
It is internal engineering evidence only, not public speedup wording.

- Tier: `standard`
- Case repeat: `1`
- Generated: `2026-06-20T05:30:37+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | barnes_hut_node_coverage_bodies_32768 | 0.127416 | 0.0499207 | 2.55x | `{"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| barnes_hut | barnes_hut_node_coverage_bodies_8192 | 0.0284851 | 0.0104785 | 2.72x | `{"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_16384 | 0.566952 | 0.278613 | 2.03x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_4096 | 0.104422 | 0.0411352 | 2.54x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_65536 | 2.49315 | 1.62892 | 1.53x | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| rtnn | rtnn_clustered_65536_ranked_summary | 0.721944 | 0.174328 | 4.14x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_shell_65536_ranked_summary | 0.122697 | 0.108155 | 1.13x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_uniform_65536_ranked_summary | 0.114011 | 0.108734 | 1.05x | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| spatial_rayjoin | rayjoin_lsi_authored_tiled_x512 | 0.0389572 | 9.14782e-05 | 426x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| spatial_rayjoin | rayjoin_overlay_seed_authored_tiled_x512 | 0.366381 | 6.39334e-05 | 5.73e+03x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| spatial_rayjoin | rayjoin_pip_authored_tiled_x512 | 0.0430664 | 0.00182209 | 23.6x | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| hausdorff_xhd | hausdorff_embree_threshold_copies_4096 | embree | ok | 0.104422 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_4096 | optix | ok | 0.0411352 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_embree_threshold_copies_16384 | embree | ok | 0.566952 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_16384 | optix | ok | 0.278613 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_embree_threshold_copies_65536 | embree | ok | 2.49315 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_threshold_copies_65536 | optix | ok | 1.62892 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| hausdorff_xhd | hausdorff_optix_exact_grouped_seeded_pruned_points_8192 | optix | ok | 1.93685 | `primary.elapsed_sec` |
| hausdorff_xhd | hausdorff_optix_exact_grouped_seeded_pruned_points_32768 | optix | ok | 2.94047 | `primary.elapsed_sec` |
| spatial_rayjoin | rayjoin_embree_pip_tiled_x512 | embree | ok | 0.0430664 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_pip_tiled_x512 | optix | ok | 0.00182209 | `phases_sec.prepared_query_sec` |
| spatial_rayjoin | rayjoin_embree_lsi_tiled_x512 | embree | ok | 0.0389572 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_lsi_tiled_x512 | optix | ok | 9.14782e-05 | `phases_sec.prepared_query_sec` |
| spatial_rayjoin | rayjoin_embree_overlay_seed_tiled_x512 | embree | ok | 0.366381 | `elapsed_sec` |
| spatial_rayjoin | rayjoin_optix_promoted_overlay_seed_tiled_x512 | optix | ok | 6.39334e-05 | `phases_sec.prepared_query_sec` |
| rtnn | rtnn_embree_uniform_65536_ranked_summary | embree | ok | 0.114011 | `elapsed_sec` |
| rtnn | rtnn_optix_uniform_65536_ranked_summary | optix | ok | 0.108734 | `elapsed_sec` |
| rtnn | rtnn_embree_clustered_65536_ranked_summary | embree | ok | 0.721944 | `elapsed_sec` |
| rtnn | rtnn_optix_clustered_65536_ranked_summary | optix | ok | 0.174328 | `elapsed_sec` |
| rtnn | rtnn_embree_shell_65536_ranked_summary | embree | ok | 0.122697 | `elapsed_sec` |
| rtnn | rtnn_optix_shell_65536_ranked_summary | optix | ok | 0.108155 | `elapsed_sec` |
| barnes_hut | barnes_hut_embree_node_coverage_bodies_8192 | embree | ok | 0.0284851 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_optix_node_coverage_bodies_8192 | optix | ok | 0.0104785 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_embree_node_coverage_bodies_32768 | embree | ok | 0.127416 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| barnes_hut | barnes_hut_optix_node_coverage_bodies_32768 | optix | ok | 0.0499207 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| triangle_counting | triangle_counting_embree_rt_graph_2a1_cliques_5000 | embree | ok | 0.0250783 | `timing_ms.query_median_ms converted-ms-to-sec` |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_cliques_5000 | optix | failed | n/a | `run` |
| triangle_counting | triangle_counting_embree_rt_graph_2a1_cliques_20000 | embree | ok | 0.134602 | `timing_ms.query_median_ms converted-ms-to-sec` |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_cliques_20000 | optix | failed | n/a | `run` |

## Boundary

- Hausdorff exact-witness rows are OptiX-only and are not ratioed.
- Spatial RayJoin rows use derived tiled fixtures, but still do not materialize full polygon overlay.
- RTNN rows are distribution-sensitive; clustered rows are the density-risk signal.
- Barnes-Hut rows are node-coverage only, not force aggregation.
- Triangle-counting rows are synthetic RT-2A1 backend-query ladders; paper datasets still require segmented/streamed lowering.
