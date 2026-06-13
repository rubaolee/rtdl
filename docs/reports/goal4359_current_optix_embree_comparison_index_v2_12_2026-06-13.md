# Current OptiX vs Embree Comparison Index

Version: `rtdl.v2_12.current_optix_embree_comparison_index.goal4359.v1`

This is a comparability index, not a speedup table and not a public speedup table.

Goal4341 supersedes the older planning index for the optimized LibRTS AABB same-contract row. Goal4358 now adds Spatial RayJoin LSI/PIP same-stream scalar-count pairs. This current index remains useful for showing which broad registry artifacts should not be compared directly.

| App | OptiX row | Embree CPU row | Existing artifact status | Comparability | Internal ratio scope | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| hausdorff_xhd | `hausdorff_xhd_scale_default_optix_threshold` | `hausdorff_xhd_embree_cpu_directed_summary` | OptiX pass; Embree pass | contract_split_pair_required | `not_authorized` | run the same directed-summary or same threshold-decision contract on both backends at the same point counts, copies, repeat, and warmup |
| spatial_rayjoin | `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | `spatial_rayjoin_pip_count_embree_cpu_generic_kernel` | OptiX pass; Embree pass | same_stream_scalar_count_pairs_available | `internal_same_stream_scalar_count_only_not_public_claim` | use the Goal4358 LSI/PIP scalar-count pairs for internal backend comparison; keep overlay active-count and whole-app wording separate |
| spatial_rayjoin / lsi | `Goal4358 OptiX` | `Goal4358 Embree` | count 8921, match=True | same-stream scalar-count pair | `internal_same_stream_scalar_count_only_not_public_claim` | OptiX 0.336 ms vs Embree 14.539 ms; OptiX/Embree speedup 43.28x |
| spatial_rayjoin / pip | `Goal4358 OptiX` | `Goal4358 Embree` | count 8686, match=True | same-stream scalar-count pair | `internal_same_stream_scalar_count_only_not_public_claim` | OptiX 12.034 ms vs Embree 14.168 ms; OptiX/Embree speedup 1.18x |
| rt_dbscan | `rt_dbscan_optix_numba_scale_default_65536_no_validation` | `rt_dbscan_embree_cpu_prepared_rows` | OptiX pass; Embree pass | contract_split_pair_required | `not_authorized` | run a common fixed-radius neighbor-row or grouped-signature contract with matching validation and continuation policy on both backends |
| robot_collision | `robot_collision_optix_scale_default_1024_no_probe_reference` | `robot_collision_embree_cpu_prepared_buffers` | OptiX pass; Embree pass | same_contract_different_scale_pair_required | `not_authorized` | run the scaled prepared-buffer/device-count contract on both backends with matching repeat, warmup, validation, and summary-only policy |
| contact_manifold | `contact_manifold_optix_scale_default_grid64` | `contact_manifold_embree_cpu_native_collect_k` | OptiX pass; Embree pass | same_contract_different_scale_pair_required | `not_authorized` | run the same grid size, witness capacity, repeat count, and backend contract on both backends |
| raydb_style | `raydb_style_optix_count_scale_default_262k` | `raydb_style_embree_cpu_count_primitive_first` | OptiX pass; Embree pass | same_contract_different_scale_pair_required | `not_authorized` | run identical generated row and group counts on both backends, with summary-only iteration policy held constant |
| barnes_hut | `barnes_hut_numba_scale_default_8192` | `barnes_hut_embree_cpu_node_coverage_prepared` | OptiX pass; Embree pass | contract_split_pair_required | `not_authorized` | choose either exact-force partner continuation or prepared node coverage as the comparison contract, then run that one contract on both sides |
| librts_spatial_index | `librts_spatial_index_optix_scale_default_32768` | `librts_spatial_index_embree_cpu_aabb_index` | OptiX pass; Embree pass | same_contract_different_scale_pair_required | `not_authorized` | run identical box/query counts and operation policy; record whether count validation is enabled on both sides |
| rtnn | `rtnn_prepared_optix_scale_default_65536` | `rtnn_embree_cpu_ann_candidate_quality_reference` | OptiX pass; Embree pass | contract_split_pair_required | `not_authorized` | decide between 2-D ANN candidate quality and 3-D ranked-summary as the paired contract, then run that one contract on both backends |
| triangle_counting | `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | `triangle_counting_embree_cpu_native_summary` | OptiX pass; Embree pass | same_contract_different_scale_pair_required | `not_authorized` | run the same fixture, copy count, repeat, warmup, and output-mode on both backends |

Only the Goal4358 Spatial RayJoin LSI/PIP same-stream scalar-count pairs authorize internal backend ratios from existing artifacts. Every public/release speedup claim flag remains false.
Fresh same-contract paired runs are still required before publishing whole-app or broad benchmark speedups.
