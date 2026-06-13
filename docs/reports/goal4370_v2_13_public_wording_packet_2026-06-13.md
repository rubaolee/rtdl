# Goal4370 v2.13 Public Wording Packet

Status: accepted row-scoped wording packet; broad speedup wording remains blocked.

## Summary

| Field | Value |
| --- | --- |
| Validation | `accept` |
| Rows reviewed | 11 |
| Row-scoped wording authorized | 10 |
| Blocked rows | 1 |
| Zero unexplained rows | True |
| Broad RT-core wording authorized | False |
| Whole-app speedup wording authorized | False |
| Prepare AMD GPU now | False |

## Allowed Portfolio Wording

RTDL v2.13 has row-scoped evidence that selected prepared OptiX/RT-core paths can outperform same-contract or explicitly caveated Embree CPU baselines across the promoted benchmark suite. Each published sentence must name the benchmark row, contract, speedup direction, and caveat.

## Row Wording Table

| App | Status | Speedup | Allowed wording |
| --- | --- | ---: | --- |
| barnes_hut | `ready_row_scoped_prepared_phase_wording` | 2.76x | For `barnes_hut` under `prepared_fixed_radius_node_coverage_threshold_decision`, the row-scoped RTDL OptiX prepared measurement is 2.76x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Keep the prepared-query/row-scoped contract in the sentence. |
| contact_manifold | `ready_row_scoped_prepared_phase_wording` | 1.27x | For `contact_manifold` under `generic_aabb_broadphase_contact_candidates_2d_grid16384`, the row-scoped RTDL OptiX prepared measurement is 1.27x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Keep the prepared-query/row-scoped contract in the sentence. |
| hausdorff_xhd | `ready_row_scoped_prepared_phase_wording` | 2.49x | For `hausdorff_xhd` under `directed_threshold_prepared_fixed_radius_count`, the row-scoped RTDL OptiX prepared measurement is 2.49x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Keep the prepared-query/row-scoped contract in the sentence. |
| librts_spatial_index | `ready_row_scoped_prepared_phase_wording` | 69.32x | For `librts_spatial_index` under `generic_prepared_aabb_index_query_2d_all_ops`, the row-scoped RTDL OptiX prepared measurement is 69.32x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Keep the prepared-query/row-scoped contract in the sentence. |
| raydb_style | `ready_row_scoped_prepared_phase_wording` | 11.38x | For `raydb_style` under `prepared_ray_triangle_grouped_i64_reduction_count`, the row-scoped RTDL OptiX prepared measurement is 11.38x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Keep the prepared-query/row-scoped contract in the sentence. |
| robot_collision | `ready_traversal_phase_only_wording` | 9.87x | For `robot_collision` under `prepared_triangle_scene_grouped_segment_any_hit_flags`, the row-scoped RTDL OptiX prepared measurement is 9.87x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Word this only as a traversal-phase result, not as a full hot-loop or app speedup. |
| rt_dbscan | `ready_with_explicit_output_surface_caveat` | 9x | For `rt_dbscan` under `fixed_radius_core_flags_plus_numba_column_signature`, the row-scoped RTDL OptiX prepared measurement is 9.00x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Include the output-surface caveat from the packet; do not present it as a pure backend swap. |
| rtnn | `blocked_not_rt_core_neighbor_search_claim` | 201.31x | Do not publish RTNN as an RT-core neighbor-search speedup. Keep it as engineering evidence until Embree and OptiX expose the same native ranked-summary surface. |
| spatial_rayjoin_lsi | `ready_with_explicit_output_surface_caveat` | 640.93x | For `spatial_rayjoin_lsi` under `public_cdb_lsi_count`, the row-scoped RTDL OptiX prepared measurement is 640.93x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Include the output-surface caveat from the packet; do not present it as a pure backend swap. |
| spatial_rayjoin_pip | `ready_with_explicit_output_surface_caveat` | 5.57x | For `spatial_rayjoin_pip` under `public_cdb_pip_count`, the row-scoped RTDL OptiX prepared measurement is 5.57x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Include the output-surface caveat from the packet; do not present it as a pure backend swap. |
| triangle_counting | `ready_row_scoped_prepared_phase_wording` | 42.16x | For `triangle_counting` under `rt_graph_2a1_generic_ray_triangle_any_hit`, the row-scoped RTDL OptiX prepared measurement is 42.16x faster per iteration than the best measured Embree CPU row for the same scoped contract/protocol. Keep the prepared-query/row-scoped contract in the sentence. |

## Blocked Wording

- Do not say RT cores make every benchmark app faster.
- Do not say these are whole-application speedups.
- Do not say RTDL reproduces the RayJoin paper.
- Do not say RTDL beats RayJoin as a whole system.
- Do not say RTNN is an RT-core neighbor-search speedup.
- Do not say partner selection is automatic or universally Numba-based.
- Do not say Intel GPU or AMD GPU performance is covered by this packet.

## AMD GPU Decision

Prepare AMD GPU now: `False`.

Prepare AMD GPU after v2.13 is closed/tagged, not before the NVIDIA-vs-Embree packet is frozen.

The NVIDIA RT-core versus Embree CPU story is now packetized; AMD should be a separate v2.14-style matrix, not mixed into v2.13 closeout.

Validation status: `accept`.
