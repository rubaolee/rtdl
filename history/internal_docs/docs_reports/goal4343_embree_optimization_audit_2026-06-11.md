# Goal4343: Embree Optimization Audit

Date: 2026-06-11

Status: internal Embree optimization audit; not comparison or release authorization.

## Verdict

LibRTS remains the only fully optimized measured Embree-vs-OptiX pair, but Goal4344 now supplies the five missing Embree scale rows. The remaining Embree campaign blockers are the four apps that still need a contract choice before a serious backend ratio can be reported.

Important stale-evidence note: the full Goal4298 artifact predates the Goal4308 RTNN Embree front door, so the audit combines the historical packet with the Goal4308 RTNN follow-up, the Goal4340 LibRTS optimized summary, and the Goal4344 Embree same-contract scale probe.

## Route Table

| App | Registry Row | Optimization Status | Comparison Readiness | Artifact Status | Next Action |
| --- | --- | --- | --- | --- | --- |
| hausdorff_xhd | `hausdorff_xhd_embree_cpu_directed_summary` | `scaled_threshold_count_route_available` | `same_contract_scale_row_ready` | `goal4344_same_contract_scale_probe_pass` | carry the threshold-count scale row into the internal comparison packet as a query-ratio candidate |
| spatial_rayjoin | `spatial_rayjoin_pip_count_embree_cpu_generic_kernel` | `python_continuation_route_present_contract_split` | `needs_contract_split_before_optimization` | `historical_packet_pass` | choose PIP count, LSI scalar count, or overlay active count before optimizing/running Embree |
| rt_dbscan | `rt_dbscan_embree_cpu_prepared_rows` | `prepared_rows_tiny_python_continuation` | `needs_summary_or_signature_contract_choice` | `historical_packet_pass` | choose fixed-radius neighbor rows or grouped-signature contract, then optimize Embree at scale |
| robot_collision | `robot_collision_embree_cpu_prepared_buffers` | `scaled_prepared_buffer_route_available` | `same_scale_boundary_limited_row_ready` | `goal4344_same_contract_scale_probe_pass` | use traversal-only internal comparison, or run an OptiX prepared-buffer flags row if a clean output-contract ratio is needed |
| contact_manifold | `contact_manifold_embree_cpu_native_collect_k` | `scaled_collect_k_route_available` | `same_contract_scale_row_ready` | `goal4344_same_contract_scale_probe_pass` | carry the collect-k scale row into the internal comparison packet as a query-ratio candidate |
| raydb_style | `raydb_style_embree_cpu_count_primitive_first` | `scaled_primitive_first_grouped_count_available` | `same_scale_boundary_limited_row_ready` | `goal4344_same_contract_scale_probe_pass` | compare native grouped-reduction traversal cautiously, or add a prepared Embree resident row before clean end-to-end ratios |
| barnes_hut | `barnes_hut_embree_cpu_node_coverage_prepared` | `node_coverage_contract_split` | `needs_contract_choice_before_optimization` | `historical_packet_pass` | choose node-coverage or exact-force configured route before optimizing Embree/CPU side |
| librts_spatial_index | `librts_spatial_index_embree_cpu_aabb_index` | `optimized_native_aabb_route_available` | `first_measured_pair_ready` | `optimized_goal4340_summary_available` | scale the optimized native AABB row and keep validation row separate from performance rows |
| rtnn | `rtnn_embree_cpu_ann_candidate_quality_reference` | `embree_front_door_present_contract_split` | `needs_3d_ranked_or_2d_ann_contract_choice` | `current_followup_pass` | decide between current 2-D ANN candidate-quality route and OptiX 3-D ranked-summary contract |
| triangle_counting | `triangle_counting_embree_cpu_native_summary` | `scaled_native_summary_route_available` | `same_contract_scale_row_ready` | `goal4344_same_contract_scale_probe_pass` | carry the RT-Graph 2A1 scale row into the internal comparison packet as a query-ratio candidate |

## Summary

- Optimized measured pair ready: 1
- Embree scale evidence ready: 6
- Boundary-limited scale evidence ready: 2
- Same-contract scale pairs needed: 0
- Contract choices needed: 4
- LibRTS Embree speedup versus old columnar fallback: 3740.9x

## Boundary

Goal4343 audits the current Embree CPU campaign for optimized-comparison readiness. It does not authorize release action, public speedup wording, whole-app acceleration wording, Intel GPU performance wording, broad RT-core wording, paper reproduction wording, automatic partner selection, or app-specific native-engine logic.

Validation status: `accept`.
