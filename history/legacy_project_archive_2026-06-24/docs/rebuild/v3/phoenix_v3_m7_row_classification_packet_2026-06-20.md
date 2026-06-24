# Phoenix V3 M7 Row Classification Packet

Status: M7 classification packet, not release authorization.

## Verdict

This packet classifies the current Phoenix V3 candidate evidence after the focused M4/M5/M6, RayDB, Triangle, RTNN, grouped_sum, AABB, RTDBSCAN, Hausdorff, and Robot Collision final-review closures.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
Phoenix M7-qualified release rows: 12
```

The result is deliberately strict: 5 original route-map rows (AABB, RTDBSCAN component_union, Triangle, Hausdorff threshold_summary, and Robot Collision collision_flag_stream) and 7 supplemental rows (grouped_sum plus AABB native query-handle plus RTNN prepared repeat50 plus Barnes-Hut fused partner rows) are now M7-qualified and row-scoped; all other rows remain internal, blocked, or candidate evidence. V3 release remains unauthorized.

## Why This Exists

Phoenix V3 must not repeat the earlier failure mode where internal technical progress was mistaken for user-facing release proof.
The packet turns each current performance row into one of two states: M7-qualified release row, or not M7-qualified with explicit blockers.

## Focused Evidence Snapshot

| Evidence | Status | M7 rows | Release reading |
| --- | --- | ---: | --- |
| M4 grouped continuation | `internal_m4_evidence_not_release_evidence` | 0 | internal component/continuation evidence only |
| M5 topology | `internal-author-complete` | 0 | RayJoin author RT is faster than RTDL OptiX, so no RTDL-beats-RayJoin claim |
| M6 Barnes-Hut | `internal_m6_route_parity_evidence` | 0 | fused Numba CUDA is fastest; prepared OptiX is route-parity evidence |
| RayDB grouped reduction | `ok` | 0 | hot-query evidence only; not end-to-end DB timing |
| Triangle prepared graph | `internal_triangle_prepared_graph_candidate_not_m7` | 1 | exact 80,000-clique non-graph stream row only; not graph DB or paper reproduction |
| RTNN ranked summary | `internal_rtnn_ranked_summary_candidate_not_m7` | 0 | hot rows win, wall timing regresses |

## Supplemental Final Review Packets

These packets were created after the route-map classification. They can add row-scoped M7-qualified rows without authorizing a V3 release.

| Packet | Candidate | Local reading | External review | Consensus | M7 rows |
| --- | --- | --- | --- | --- | ---: |
| `docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.json` | `grouped_reduction_sum_scalar_broadcast_repeat100_262144` | `m7_qualified_row_scoped_after_claude_codex_consensus` | `claude_approved` | `claude_codex_consensus_complete` | 1 |
| `docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.json` | `grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups; grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups` | `m7_row_evidence_scoped_not_release_after_claude_codex_consensus` | `claude_external_approve_with_required_fixes_p1_applied_2026-06-22` | `claude_codex_consensus_complete_after_subagent_gap_supersession_2026-06-22` | 2 |
| `docs/rebuild/v3/phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2026-06-21.json` | `aabb_candidate_stream_all_count_only_float32_32768` | `m7_qualified_row_scoped_after_claude_codex_consensus` | `claude_approved_after_p0_wording_fix` | `claude_codex_consensus_complete` | 1 |
| `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.json` | `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50; aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50` | `m7_qualified_row_scoped_after_claude_codex_consensus` | `claude_approve_with_conditions` | `claude_codex_consensus_complete_approve_two_row_scoped_m7_rows` | 2 |
| `docs/rebuild/v3/phoenix_v3_rtnn_prepared_repeat50_review_gate_2026-06-21.json` | `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02` | `m7_qualified_row_scoped_after_claude_codex_consensus` | `claude_approve_with_conditions` | `claude_codex_consensus_complete_approve_one_row_scoped_m7` | 1 |
| `docs/rebuild/v3/phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.json` | `aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped` | `m7_qualified_row_scoped_after_claude_amendments_and_codex_consensus` | `claude_approve_with_amendments` | `claude_codex_consensus_complete_approve_one_row_scoped_m7_with_amendments` | 1 |
| `docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.json` | `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream` | `m7_qualified_row_scoped_after_claude_refresh_and_codex_consensus` | `claude_reviewed_approved_with_amendments_2026-06-21` | `claude_codex_consensus_complete` | 1 |
| `docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_repeat5_rtx_evidence_2026-06-21.json` | `hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped` | `m7_qualified_row_scoped_after_p0_repair_and_claude_codex_consensus` | `claude_approved_after_p0_repair_and_scene_prepare_wording` | `claude_codex_consensus_complete` | 1 |
| `docs/rebuild/v3/phoenix_v3_robot_collision_flag_stream_no_probe_paired_rtx_evidence_2026-06-21.json` | `collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped` | `m7_qualified_row_scoped_after_claude_p1_amendments_and_codex_consensus` | `claude_approved_with_p1_amendments_resolved` | `claude_codex_consensus_complete` | 1 |

## Capability Classification

| Capability | Review status | Rows | M7 rows | Main blocker |
| --- | --- | ---:| ---:| --- |
| `aabb_candidate_stream` | `one_route_map_row_m7_qualified_row_scoped` | 2 | 1 | `remaining_aabb_rows_not_m7` |
| `aggregate_frontier` | `accepted_internal_m6_route_parity_not_m7` | 2 | 0 | `prepared_optix_not_fastest_route` |
| `collision_flag_stream` | `claude_codex_m7_qualified_row_scoped` | 1 | 1 | `do_not_generalize_to_full_robot_planning_exact_or_continuous_collision_v2_or_zero_copy` |
| `component_union` | `claude_codex_m7_qualified_row_scoped` | 1 | 1 | `do_not_generalize_to_full_dbscan_rt_dbscan_paper_v2_or_noisy_datasets` |
| `grouped_reduction` | `accepted_internal_grouped_reduction_not_m7` | 2 | 0 | `hot_query_only_not_end_to_end_application_timing` |
| `point_location_topology_stream` | `accepted_internal_m5_author_complete_not_m7` | 3 | 0 | `rayjoin_author_rt_faster_than_rtdl_optix` |
| `prepared_graph_chunk` | `one_triangle_route_map_row_m7_qualified_after_claude_refresh` | 2 | 1 | `remaining_triangle_rows_not_m7` |
| `ranked_summary` | `accepted_internal_rtnn_candidate_not_m7` | 3 | 0 | `wall_timing_optix_slower_than_embree_for_all_three_distributions` |
| `threshold_summary` | `one_large_row_m7_qualified_row_scoped` | 3 | 1 | `remaining_threshold_summary_rows_not_phase_total_wins` |

## Capability M7 Count Summary

- Three exact `aabb_candidate_stream` rows are M7-qualified.
- One exact `aggregate_frontier` row is M7-qualified.
- One exact `collision_flag_stream` row is M7-qualified.
- One exact `component_union` row is M7-qualified.
- Three exact `grouped_reduction` rows are M7-qualified.
- One exact `prepared_graph_chunk` row is M7-qualified.
- One exact `ranked_summary` row is M7-qualified.
- One exact `threshold_summary` row is M7-qualified.

## Capability Scope Notes

- `vector_accumulation`: `covered_by_amended_fused_partner_m7_row_rt_native_future_research`. Claude and Codex now allow exactly one amended M7 milestone row for the generic aggregate-tree fused weighted-vector Numba CUDA partner route. This covers the aggregate_frontier/vector_accumulation breadth gap for the narrow row-scoped partner contract only. It does not complete RT-native Barnes-Hut, RT-core acceleration, whole-app Barnes-Hut, paper reproduction, broad V3-over-V2, or release readiness. RT-native hierarchical traversal remains future research and still requires a reviewed subtree-skip-preserving design before any RT-core wording.

## Row Classification

| App | Row | Capability | Class | Leading blocker |
| --- | --- | --- | --- | --- |
| `spatial_rayjoin` | `rayjoin_overlay_seed_authored_tiled_x2048` | `point_location_topology_stream` | `not_m7_qualified` | `rayjoin_author_rt_faster_than_rtdl_optix` |
| `rt_dbscan` | `dbscan_cluster_signature` | `component_union` | `m7_qualified_release_row` | `none` |
| `librts_spatial_index` | `aabb_index_all_count_only_large_32768` | `aabb_candidate_stream` | `m7_qualified_release_row` | `none` |
| `spatial_rayjoin` | `rayjoin_lsi_authored_tiled_x2048` | `point_location_topology_stream` | `not_m7_qualified` | `rayjoin_author_rt_faster_than_rtdl_optix` |
| `raydb_style` | `raydb_grouped_count` | `grouped_reduction` | `not_m7_qualified` | `hot_query_only_not_end_to_end_application_timing` |
| `raydb_style` | `raydb_grouped_sum` | `grouped_reduction` | `not_m7_qualified` | `hot_query_only_not_end_to_end_application_timing` |
| `triangle_counting` | `triangle_count_rt_graph_2a1_cliques_80000` | `prepared_graph_chunk` | `m7_qualified_release_row` | `none` |
| `triangle_counting` | `triangle_count_rt_graph_2a1_cliques_20000` | `prepared_graph_chunk` | `not_m7_qualified` | `synthetic_k4_clique_ladder_not_paper_dataset` |
| `spatial_rayjoin` | `rayjoin_pip_authored_tiled_x2048` | `point_location_topology_stream` | `not_m7_qualified` | `rayjoin_author_rt_faster_than_rtdl_optix` |
| `robot_collision` | `prepared_collision_flags` | `collision_flag_stream` | `m7_qualified_release_row` | `none` |
| `rtnn` | `rtnn_clustered_65536_ranked_summary` | `ranked_summary` | `not_m7_qualified` | `wall_timing_optix_slower_than_embree_for_all_three_distributions` |
| `hausdorff_xhd` | `hausdorff_threshold_copies_16384` | `threshold_summary` | `not_m7_qualified` | `smaller_threshold_summary_rows_not_phase_total_wins` |
| `barnes_hut` | `barnes_hut_node_coverage_bodies_32768` | `aggregate_frontier` | `not_m7_qualified` | `prepared_optix_not_fastest_route` |
| `barnes_hut` | `barnes_hut_node_coverage_bodies_131072` | `aggregate_frontier` | `not_m7_qualified` | `prepared_optix_not_fastest_route` |
| `hausdorff_xhd` | `hausdorff_threshold_copies_262144` | `threshold_summary` | `m7_qualified_release_row` | `none` |
| `hausdorff_xhd` | `hausdorff_threshold_copies_65536` | `threshold_summary` | `not_m7_qualified` | `smaller_threshold_summary_rows_not_phase_total_wins` |
| `contact_manifold` | `generic_aabb_broadphase_collect_k` | `aabb_candidate_stream` | `not_m7_qualified` | `wall_timing_optix_slower_than_embree` |
| `rtnn` | `rtnn_shell_65536_ranked_summary` | `ranked_summary` | `not_m7_qualified` | `wall_timing_optix_slower_than_embree_for_all_three_distributions` |
| `rtnn` | `rtnn_uniform_65536_ranked_summary` | `ranked_summary` | `not_m7_qualified` | `wall_timing_optix_slower_than_embree_for_all_three_distributions` |

## M7 Row IDs

- `component_union_clustered3d_65536_524288_repeat5_row_scoped`: `component_union` / `rt_dbscan`.
- `aabb_candidate_stream_all_count_only_float32_32768`: `aabb_candidate_stream` / `librts_spatial_index`.
- `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream`: `prepared_graph_chunk` / `triangle_counting`.
- `collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped`: `collision_flag_stream` / `robot_collision`.
- `hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped`: `threshold_summary` / `hausdorff_xhd`.

## Next M7 Promotion Candidates

- None from current evidence. Reopen only after a generic-engine change.

## Next Engine Work Queue

Status: `generic_engine_work_queue_closed_not_release`.

Source: `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`.

Active Phoenix P0 items:


Future research, not active Phoenix P0:

- `barnes_hut_vector_accumulation_frontier_shape`
- `spatial_rayjoin_topology_stream_author_gap`

Do not promote more rows from old evidence. The aggregate_frontier/vector_accumulation breadth gap is now closed only for the amended Numba CUDA partner M7 milestone row. Spatial topology-stream remains future research, not current release scope. AABB native query-handle is now closed as two supplemental M7 rows, and RTNN prepared repeat50 is closed as one supplemental M7 row. RT-native Barnes-Hut/vector accumulation remains future research, not an active Phoenix P0.

## Optimization-Required Reopen Queue

- None in this classification packet. Continue through `phoenix_v3_next_generic_engine_work_queue_2026-06-21`.

## Goal-Level Decision Audit

Decision: count the two reviewed grouped-reduction device-column rows, the two reviewed AABB native-query-handle rows, the one reviewed RTNN prepared-repeat50 row, and the one reviewed Barnes-Hut fused-partner row as supplemental M7 rows while keeping the packet non-release

1. Was I foolish?

   No. This updates the global row count only after external/2-AI review, P1 wording/provenance conditions, exact-row boundaries, and Claude's Barnes-Hut amendments.

2. If yes, what actions made the decision foolish?

   It would be foolish to treat the new rows as a V3 release, call the Embree/device-column ratios pure backend-only, turn the 218.248x cold-prepare phase ratio into headline wording, present RTNN repeat50 as a one-shot nearest-neighbor win, or headline the Barnes-Hut 13.591x OptiX no-go comparison.

3. Was there another path?

   Leave the rows pending after Claude approval. That would avoid changing the global count but would freeze reviewed generic-engine improvements.

4. Can I now try a different path that actually solves the problem?

   Regenerate classification/docs/tests, keep release authorization false, and leave Spatial topology-stream as the remaining breadth blocker.
