# RTDL v2.13 Row-Scoped RT-Core vs Embree CPU Comparison

Status: release-facing row-scoped comparison; not broad speedup wording.

Post-Goal4378 bridge note: this v2.13 table remains a row-scoped RTDL
OptiX-vs-Embree CPU comparison. It must not be read as author-hot-compute parity
for RayJoin. Goal4376 adds better RayJoin overlay OptiX rows, but those rows
show near author process wall under a cached/preprocessed application-wall
protocol, not equality with the RayJoin authors' specialized C++/CUDA/OptiX hot
processing path. v2.14 is the next formal cleanup and benchmark-app boost
release target.

| App | Status | Directional readout | Contract | Allowed wording |
| --- | --- | ---: | --- | --- |
| barnes_hut | `ready_row_scoped_prepared_phase_wording` | OptiX 2.71x faster | `prepared_fixed_radius_node_coverage_threshold_decision` | For `barnes_hut` under `prepared_fixed_radius_node_coverage_threshold_decision`, the row-scoped RTDL OptiX prepared measurement is 2.71x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Keep the prepared-query/row-scoped contract in the sentence. |
| contact_manifold | `ready_row_scoped_prepared_phase_wording` | OptiX 1.24x faster | `generic_aabb_broadphase_contact_candidates_2d_grid16384` | For `contact_manifold` under `generic_aabb_broadphase_contact_candidates_2d_grid16384`, the row-scoped RTDL OptiX prepared measurement is 1.24x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Keep the prepared-query/row-scoped contract in the sentence. |
| hausdorff_xhd | `ready_row_scoped_prepared_phase_wording` | OptiX 2.53x faster | `directed_threshold_prepared_fixed_radius_count` | For `hausdorff_xhd` under `directed_threshold_prepared_fixed_radius_count`, the row-scoped RTDL OptiX prepared measurement is 2.53x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Keep the prepared-query/row-scoped contract in the sentence. |
| librts_spatial_index | `ready_row_scoped_prepared_phase_wording` | OptiX 259.89x faster | `generic_prepared_aabb_index_query_2d_all_ops` | For `librts_spatial_index` under `generic_prepared_aabb_index_query_2d_all_ops`, the row-scoped RTDL OptiX prepared measurement is 259.89x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Keep the prepared-query/row-scoped contract in the sentence. |
| raydb_style | `ready_row_scoped_prepared_phase_wording` | OptiX 12.13x faster | `prepared_ray_triangle_grouped_i64_reduction_count` | For `raydb_style` under `prepared_ray_triangle_grouped_i64_reduction_count`, the row-scoped RTDL OptiX prepared measurement is 12.13x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Keep the prepared-query/row-scoped contract in the sentence. |
| robot_collision | `ready_traversal_phase_only_wording` | OptiX 9.29x faster | `prepared_triangle_scene_grouped_segment_any_hit_flags` | For `robot_collision` under `prepared_triangle_scene_grouped_segment_any_hit_flags`, the row-scoped RTDL OptiX prepared measurement is 9.29x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Word this only as a traversal-phase result, not as a full hot-loop or app speedup. |
| rt_dbscan | `ready_with_explicit_output_surface_caveat` | OptiX 8.00x faster | `fixed_radius_core_flags_plus_numba_column_signature` | For `rt_dbscan` under `fixed_radius_core_flags_plus_numba_column_signature`, the row-scoped RTDL OptiX prepared measurement is 8.00x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Include the output-surface caveat from the packet; do not present it as a pure backend swap. |
| rtnn | `blocked_not_rt_core_neighbor_search_claim` | OptiX 1.09x faster | `prepared_3d_fixed_radius_ranked_summary_raw` | Do not publish RTNN as an RT-core neighbor-search speedup. Keep it as engineering evidence until the release has an end-to-end RTNN claim boundary that reviewers explicitly approve. |
| spatial_rayjoin_lsi | `ready_row_scoped_prepared_phase_wording` | OptiX 3.51x faster | `public_cdb_lsi_count` | For `spatial_rayjoin_lsi` under `public_cdb_lsi_count`, the row-scoped RTDL OptiX prepared measurement is 3.51x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Keep the prepared-query/row-scoped contract in the sentence. |
| spatial_rayjoin_pip | `ready_row_scoped_embree_faster_wording` | Embree 1.06x faster | `public_cdb_pip_count` | For `spatial_rayjoin_pip` under `public_cdb_pip_count`, the row-scoped Embree CPU prepared measurement is 1.06x faster per iteration than the RTDL OptiX prepared measurement for this scoped protocol. Publish this as a near-parity or Embree-faster row, not as an RT-core speedup. |
| triangle_counting | `ready_row_scoped_prepared_phase_wording` | OptiX 39.54x faster | `rt_graph_2a1_generic_ray_triangle_any_hit` | For `triangle_counting` under `rt_graph_2a1_generic_ray_triangle_any_hit`, the row-scoped RTDL OptiX prepared measurement is 39.54x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Keep the prepared-query/row-scoped contract in the sentence. |

## PIP Reading

PIP is deliberately mixed: the refreshed human-scale public CDB slice is near parity and slightly Embree-faster, while Goal4368 shows the stricter full same-stream exact prepared-points executor is 3.22x faster on OptiX than Embree and still 7.28x slower than RayJoin RT. Do not collapse those facts into a broad RT-core or RTDL-beats-RayJoin claim.

## Blocked Wording

- Do not say RT cores make every benchmark app faster.
- Do not say these are whole-application speedups.
- Do not say RTDL reproduces the RayJoin paper.
- Do not say RTDL beats RayJoin as a whole system.
- Do not say RTDL hot compute matches the RayJoin authors' specialized
  C++/CUDA/OptiX hot path.
- Do not say RTNN is an RT-core neighbor-search speedup.
- Do not say partner selection is automatic or universally Numba-based.
- Do not say Intel GPU or AMD GPU performance is covered by this packet.

Validation status: `accept`.
