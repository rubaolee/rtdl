# Goal4342: NVIDIA RT-Core Optimization Closeout Audit

Date: 2026-06-11

Status: internal optimization closeout audit; not comparison or release authorization.

## Verdict

No obvious remaining high-leverage OptiX/RT-core implementation optimization is visible in the current ten-app campaign evidence. The next work should move to the Embree optimization campaign, while preserving the comparison boundaries below.

Surprise findings:

- No obvious high-leverage OptiX/RT-core implementation optimization remains in the current campaign.
- Barnes-Hut's current NVIDIA scale row is a Numba partner route, not a pure RT-core row.
- Most rows remain smoke/internal timing evidence rather than decision-grade public speedup evidence.

## Route Table

| App | Row | Route Class | Optimization Status | Floor Status | Comparison Use | Remaining RT-Core Work |
| --- | --- | --- | --- | --- | --- | --- |
| hausdorff_xhd | `hausdorff_xhd_scale_default_optix_threshold` | `pure_rtdl_optix_rt_core` | `closed_internal_evidence` | `smoke_scale_or_internal_not_claim_grade` | `pure_rtdl_candidate_after_same_contract_embree_pair` | none_obvious |
| spatial_rayjoin | `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | `rtdl_optix_plus_numba_configured_route` | `closed_configured_route` | `smoke_scale_or_internal_not_claim_grade` | `configured_route_only` | none_obvious_for_current_mixed_route |
| rt_dbscan | `rt_dbscan_optix_numba_scale_default_65536_no_validation` | `rtdl_optix_plus_numba_configured_route` | `closed_configured_route` | `smoke_scale_or_internal_not_claim_grade` | `configured_route_only` | none_obvious_for_current_grouped_stream_route |
| robot_collision | `robot_collision_optix_scale_default_1024_no_probe_reference` | `pure_rtdl_optix_rt_core` | `closed_floor_met` | `floor_met_internal_evidence_only` | `pure_rtdl_candidate_after_same_contract_embree_pair` | none_obvious |
| contact_manifold | `contact_manifold_optix_scale_default_grid64` | `pure_rtdl_optix_collect_k_experimental` | `closed_internal_evidence_collect_k_checkpointed` | `smoke_scale_or_internal_not_claim_grade` | `pure_rtdl_candidate_after_same_contract_embree_pair` | none_before_v2_5_collect_k_checkpoint |
| raydb_style | `raydb_style_optix_count_scale_default_262k` | `pure_rtdl_optix_rt_core` | `closed_floor_met` | `floor_met_internal_evidence_only` | `pure_rtdl_candidate_after_same_contract_embree_pair` | none_obvious |
| barnes_hut | `barnes_hut_numba_scale_default_8192` | `numba_partner_only_current_scale_row` | `not_a_pure_rt_core_row` | `smoke_scale_or_internal_not_claim_grade` | `configured_route_only_or_requires_new_pure_rtdl_contract` | no_current_pure_rt_core_route_to_optimize_for_this_row |
| librts_spatial_index | `librts_spatial_index_optix_scale_default_32768` | `pure_rtdl_optix_rt_core` | `closed_internal_evidence` | `smoke_scale_or_internal_not_claim_grade` | `pure_rtdl_candidate_after_same_contract_embree_pair` | none_obvious |
| rtnn | `rtnn_prepared_optix_scale_default_65536` | `pure_rtdl_optix_rt_core` | `closed_internal_evidence` | `smoke_scale_or_internal_not_claim_grade` | `pure_rtdl_candidate_after_same_contract_embree_pair` | none_obvious |
| triangle_counting | `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | `pure_rtdl_optix_rt_core` | `closed_internal_evidence` | `smoke_scale_or_internal_not_claim_grade` | `pure_rtdl_candidate_after_same_contract_embree_pair` | none_obvious |

## Boundary

Goal4342 closes the current NVIDIA RT-core optimization audit with boundaries. It does not authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, paper reproduction wording, true-zero-copy wording, automatic partner selection, or app-specific native-engine logic. It is also not the final OptiX-vs-Embree comparison.

Validation status: `accept`.
