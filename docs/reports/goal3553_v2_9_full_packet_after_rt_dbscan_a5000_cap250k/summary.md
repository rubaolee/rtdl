# Goal3536 v2.8 vs v2.3 10s Steady-State Protocol

This is an internal measurement packet. It does not authorize release or public speedup wording.

- Target measured query time per side: `10.0` sec
- Scale: `standard`
- GPU: `NVIDIA RTX A5000, 580.126.09, 24564 MiB`
- Summary: `{"geomean_speedup": 1.0002932332576768, "max_speedup": 1.0947997017495046, "median_speedup": 0.9986491650650922, "min_speedup": 0.8458128919830225, "observed_target_miss_count": 0, "observed_target_misses": [], "ratio_count": 11, "row_count": 11, "target_met_by_observed_pair_count": 11, "target_met_by_plan_pair_count": 11}`

## Comparison Rows

| App | Case | v2.3 sec | v2.8 sec | v2.8/v2.3 | Target plan met? | Target observed met? |
| --- | --- | ---: | ---: | ---: | --- | --- |
| barnes_hut | barnes_hut_optix_node_coverage | 0.0082955 | 0.00808242 | 1.026x | True/True | True/True |
| contact_manifold | contact_manifold_optix_aabb_broadphase_collect_k | 0.0232914 | 0.0275373 | 0.846x | True/True | True/True |
| hausdorff_xhd | hausdorff_optix_threshold | 0.0336996 | 0.0307815 | 1.095x | True/True | True/True |
| librts_spatial_index | librts_optix_aabb_index | 0.000750912 | 0.000750632 | 1.000x | True/True | True/True |
| raydb_style | raydb_optix_partner_resident_count | 0.000586916 | 0.000537366 | 1.092x | True/True | True/True |
| raydb_style | raydb_optix_partner_resident_sum | 0.000750821 | 0.000751837 | 0.999x | True/True | True/True |
| robot_collision | robot_collision_optix_prepared_device_buffers | 0.00187188 | 0.00191219 | 0.979x | True/True | True/True |
| rt_dbscan | rt_dbscan_optix_grouped_stream | 0.0126433 | 0.0126609 | 0.999x | True/True | True/True |
| rtnn | rtnn_optix_prepared_3d_ranked_summary | 0.00131119 | 0.00137186 | 0.956x | True/True | True/True |
| spatial_rayjoin | spatial_rayjoin_optix_prepared_full_route | 0.000191489 | 0.000181905 | 1.053x | True/True | True/True |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_partner | 0.000349659 | 0.000355497 | 0.984x | True/True | True/True |

## Boundary

- A row is final 10s evidence only when both sides report `target_met_by_plan = true` and the execution succeeds.
- Rows without a repeat knob are reported as partial diagnostics when wrapper repetition would exceed the wall-time guard.
- Setup, packing, and validation are kept out of the primary hot-query metric unless the underlying app exposes only a total metric.
