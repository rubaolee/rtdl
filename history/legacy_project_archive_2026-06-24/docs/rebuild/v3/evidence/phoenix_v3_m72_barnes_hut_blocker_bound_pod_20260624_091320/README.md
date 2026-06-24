# Phoenix V3 Barnes-Hut Runner Parity Focused POD A/B

Status: `barnes_hut_runner_parity_pod_ab_collected_not_release`.

- body counts: `[32768, 65536, 131072]`
- repeat/warmup/samples: `11` / `3` / `5`
- runner vs existing fused-control geomean: `0.9997602284020717`
- historical OptiX over runner geomean: `12.75587197083642`
- runner/control output equivalence rows: `[{'body_count': 32768, 'contribution_count_match': True, 'checksum_force_x_match': True, 'checksum_force_y_match': True, 'equivalence_pass': True, 'existing_fused_control_checksum_force_x_median': -4733.575645891869, 'runner_checksum_force_x_median': -4733.575645891869, 'existing_fused_control_checksum_force_y_median': 46717.65234663497, 'runner_checksum_force_y_median': 46717.65234663497, 'existing_fused_control_contribution_row_count_median': 12006704.0, 'runner_contribution_row_count_median': 12006704.0}, {'body_count': 65536, 'contribution_count_match': True, 'checksum_force_x_match': True, 'checksum_force_y_match': True, 'equivalence_pass': True, 'existing_fused_control_checksum_force_x_median': -1297.4488795657612, 'runner_checksum_force_x_median': -1297.4488795657612, 'existing_fused_control_checksum_force_y_median': 579.165983783949, 'runner_checksum_force_y_median': 579.165983783949, 'existing_fused_control_contribution_row_count_median': 21121461.0, 'runner_contribution_row_count_median': 21121461.0}, {'body_count': 131072, 'contribution_count_match': True, 'checksum_force_x_match': True, 'checksum_force_y_match': True, 'equivalence_pass': True, 'existing_fused_control_checksum_force_x_median': -172371.86169971953, 'runner_checksum_force_x_median': -172371.86169971953, 'existing_fused_control_checksum_force_y_median': 408209.6098493129, 'runner_checksum_force_y_median': 408209.6098493129, 'existing_fused_control_contribution_row_count_median': 47961371.0, 'runner_contribution_row_count_median': 47961371.0}]`
- scorecard blocker: `{'id': 'set_a_barnes_hut_app_geomean_0_844x', 'set': 'A', 'app': 'barnes_hut', 'metric': 'set_a_app_geomean_v3_vs_v2_14', 'current_value': 0.8441965065233041, 'source': 'docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md', 'target': 'move_toward_or_above_parity', 'route_kind': 'trunk_fix_candidate'}`
- incumbent route declaration: `{'baseline_variant': 'existing_app_front_door_fused_numba_cuda_control', 'baseline_mode': 'fused_frontier_force_sum_bucketized_numba_cuda', 'candidate_variant': 'runner_prepared_execution_fused_numba_cuda', 'candidate_mode': 'prepared_execution_fused_vector_sum_numba_cuda', 'historical_reference_variant': 'historical_prepared_optix_frontier_numba_reference', 'historical_reference_mode': 'prepared_aggregate_frontier_weighted_vector_optix', 'body_counts': [32768, 65536, 131072], 'theta': 0.5, 'bucket_size': 32, 'max_depth': 32, 'query_repeat': 11, 'warmup': 3, 'samples': 5, 'same_pod_session_required': True, 'scorecard_row_id': 'set_a_barnes_hut_app_geomean_0_844x', 'scorecard_current_value': 0.8441965065233041, 'scorecard_source': 'docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md', 'prior_evidence_reference': 'docs/rebuild/v3/evidence/phoenix_v3_barnes_hut_runner_parity_pod_ab_fixed_20260622_182718/summary.json'}`
- M72 blocker metadata ready: `True`
- runner parity with existing fused partner: `True`
- runner Step-3 residency audit ready: `True`
- step-1 replacement candidate: `True`
- skip-historical smoke only: `False`

The primary control is the existing app-front-door fused Numba CUDA route.
The prepared OptiX frontier route is included only as a historical no-go reference.
If the historical leg is skipped, the packet is smoke-only and cannot become
a Step-1 replacement candidate.
This packet authorizes no release, broad V3-over-V2 wording, true-zero-copy wording,
wrapper-is-faster wording, or all-app rerun.
