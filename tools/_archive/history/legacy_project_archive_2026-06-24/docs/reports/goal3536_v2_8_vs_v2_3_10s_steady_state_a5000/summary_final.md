# Goal3536 v2.8 vs v2.3 10s Steady-State Protocol

This is an internal measurement packet. It does not authorize release or public speedup wording.

- Target measured query time per side: `10.0` sec
- Scale: `standard`
- GPU: `NVIDIA RTX A5000, 580.126.09, 24564 MiB`
- Summary: `{"geomean_speedup": 0.9457641417358104, "max_speedup": 1.1870630569403169, "median_speedup": 1.0058954464982628, "min_speedup": 0.4640993084656678, "ratio_count": 11, "row_count": 11, "target_met_by_plan_pair_count": 6}`

## Comparison Rows

| App | Case | v2.3 sec | v2.8 sec | v2.8/v2.3 | Target plan met? |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | barnes_hut_optix_node_coverage | 0.0117182 | 0.0252492 | 0.464x | False/False |
| contact_manifold | contact_manifold_optix_aabb_broadphase_collect_k | 0.0276667 | 0.0233069 | 1.187x | True/True |
| hausdorff_xhd | hausdorff_optix_threshold | 0.0428776 | 0.0433917 | 0.988x | False/False |
| librts_spatial_index | librts_optix_aabb_index | 0.47317 | 0.529358 | 0.894x | False/False |
| raydb_style | raydb_optix_partner_resident_count | 0.000582892 | 0.000599006 | 0.973x | True/True |
| raydb_style | raydb_optix_partner_resident_sum | 0.000787355 | 0.000789243 | 0.998x | True/True |
| robot_collision | robot_collision_optix_prepared_device_buffers | 0.00190233 | 0.00189118 | 1.006x | False/False |
| rt_dbscan | rt_dbscan_optix_grouped_stream | 1.37458 | 1.35629 | 1.013x | True/True |
| rtnn | rtnn_optix_prepared_3d_ranked_summary | 0.00149109 | 0.00141328 | 1.055x | True/True |
| spatial_rayjoin | spatial_rayjoin_optix_prepared_full_route | 0.00052627 | 0.000503196 | 1.046x | False/False |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_partner | 0.000361342 | 0.000354582 | 1.019x | True/True |

## Boundary

- A row is final 10s evidence only when both sides report `target_met_by_plan = true` and the execution succeeds.
- Rows without a repeat knob are reported as partial diagnostics when wrapper repetition would exceed the wall-time guard.
- Setup, packing, and validation are kept out of the primary hot-query metric unless the underlying app exposes only a total metric.
