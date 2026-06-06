# Goal3536 v2.8 vs v2.3 10s Steady-State Protocol

This is an internal measurement packet. It does not authorize release or public speedup wording.

- Target measured query time per side: `10.0` sec
- Scale: `standard`
- GPU: `NVIDIA RTX A5000, 580.126.09, 24564 MiB`
- Summary: `{"geomean_speedup": 1.0014497930916755, "max_speedup": 1.0644694427535752, "median_speedup": 1.0002807279109598, "min_speedup": 0.9548167674661263, "ratio_count": 11, "row_count": 11, "target_met_by_plan_pair_count": 11}`

## Comparison Rows

| App | Case | v2.3 sec | v2.8 sec | v2.8/v2.3 | Target plan met? |
| --- | --- | ---: | ---: | ---: | --- |
| barnes_hut | barnes_hut_optix_node_coverage | 0.00808992 | 0.00829876 | 0.975x | True/True |
| contact_manifold | contact_manifold_optix_aabb_broadphase_collect_k | 0.0275905 | 0.0276496 | 0.998x | True/True |
| hausdorff_xhd | hausdorff_optix_threshold | 0.0317885 | 0.0318784 | 0.997x | True/True |
| librts_spatial_index | librts_optix_aabb_index | 0.00076028 | 0.000750563 | 1.013x | True/True |
| raydb_style | raydb_optix_partner_resident_count | 0.000591503 | 0.000590944 | 1.001x | True/True |
| raydb_style | raydb_optix_partner_resident_sum | 0.000789793 | 0.000789572 | 1.000x | True/True |
| robot_collision | robot_collision_optix_prepared_device_buffers | 0.00188892 | 0.00183312 | 1.030x | True/True |
| rt_dbscan | rt_dbscan_optix_grouped_stream | 1.36516 | 1.42976 | 0.955x | True/True |
| rtnn | rtnn_optix_prepared_3d_ranked_summary | 0.00141039 | 0.00132497 | 1.064x | True/True |
| spatial_rayjoin | spatial_rayjoin_optix_prepared_full_route | 0.000179395 | 0.00017814 | 1.007x | True/True |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_partner | 0.000350908 | 0.000358337 | 0.979x | True/True |

## Boundary

- A row is final 10s evidence only when both sides report `target_met_by_plan = true` and the execution succeeds.
- Rows without a repeat knob are reported as partial diagnostics when wrapper repetition would exceed the wall-time guard.
- Setup, packing, and validation are kept out of the primary hot-query metric unless the underlying app exposes only a total metric.
