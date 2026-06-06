# Goal3536 v2.8 vs v2.3 10s Steady-State Protocol

This is an internal measurement packet. It does not authorize release or public speedup wording.

- Target measured query time per side: `10.0` sec
- Scale: `standard`
- GPU: `NVIDIA RTX A5000, 580.126.09, 24564 MiB`
- Summary: `{"geomean_speedup": 1.016536624799562, "max_speedup": 1.2195277885128637, "median_speedup": 0.9938217804455728, "min_speedup": 0.9442693792475817, "observed_target_miss_count": 0, "observed_target_misses": [], "ratio_count": 11, "row_count": 11, "target_met_by_observed_pair_count": 11, "target_met_by_plan_pair_count": 11}`

## Comparison Rows

| App | Case | v2.3 sec | v2.8 sec | v2.8/v2.3 | Target plan met? | Target observed met? |
| --- | --- | ---: | ---: | ---: | --- | --- |
| barnes_hut | barnes_hut_optix_node_coverage | 0.00812398 | 0.00817448 | 0.994x | True/True | True/True |
| contact_manifold | contact_manifold_optix_aabb_broadphase_collect_k | 0.0281399 | 0.0230744 | 1.220x | True/True | True/True |
| hausdorff_xhd | hausdorff_optix_threshold | 0.0317706 | 0.0311612 | 1.020x | True/True | True/True |
| librts_spatial_index | librts_optix_aabb_index | 0.000752487 | 0.000758727 | 0.992x | True/True | True/True |
| raydb_style | raydb_optix_partner_resident_count | 0.000571252 | 0.000587386 | 0.973x | True/True | True/True |
| raydb_style | raydb_optix_partner_resident_sum | 0.000748903 | 0.000793103 | 0.944x | True/True | True/True |
| robot_collision | robot_collision_optix_prepared_device_buffers | 0.00189056 | 0.00191426 | 0.988x | True/True | True/True |
| rt_dbscan | rt_dbscan_optix_grouped_stream | 0.0125921 | 0.0126274 | 0.997x | True/True | True/True |
| rtnn | rtnn_optix_prepared_3d_ranked_summary | 0.00153289 | 0.00144445 | 1.061x | True/True | True/True |
| spatial_rayjoin | spatial_rayjoin_optix_prepared_full_route | 0.000179248 | 0.000181246 | 0.989x | True/True | True/True |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_partner | 0.000362574 | 0.000352157 | 1.030x | True/True | True/True |

## Boundary

- A row is final 10s evidence only when both sides report `target_met_by_plan = true` and the execution succeeds.
- Rows without a repeat knob are reported as partial diagnostics when wrapper repetition would exceed the wall-time guard.
- Setup, packing, and validation are kept out of the primary hot-query metric unless the underlying app exposes only a total metric.
