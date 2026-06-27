# V4 Universe Audit Snapshot

Date: 2026-06-27

Status: `pass_with_known_local_debris`

## Counts

- tracked files: `27672`
- untracked files: `977`
- public current files scanned: `31`

## Tracked Buckets

- `audit_provenance`: `1171`
- `current_code_or_gate`: `4313`
- `history_archive`: `22045`
- `other_tracked`: `112`
- `public_current`: `31`

## Tracked Documentation Buckets

- `audit_provenance`: `559`
- `current_code_or_gate`: `3`
- `history_archive`: `14342`
- `other_tracked`: `8`
- `public_current`: `19`

## Tracked Code Buckets

- `audit_provenance`: `13`
- `current_code_or_gate`: `4301`
- `history_archive`: `328`
- `other_tracked`: `94`
- `public_current`: `12`

## Public Surface Findings

- none

## Untracked Buckets

- `local_build_output`: `2`
- `local_external_checkout`: `1`
- `local_paper_reproduction_patch`: `3`
- `local_raw_v4_evidence`: `329`
- `local_review_helper`: `1`
- `local_v3_phoenix_review_helper`: `18`
- `local_v3_phoenix_script_debris`: `105`
- `local_v3_phoenix_test_debris`: `179`
- `local_v4_review_working_record`: `339`

## Untracked Samples

### `local_build_output`
- `dist/goal4722_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl`
- `dist/goal4758_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl`
### `local_external_checkout`
- `external/RT-BarnesHut-author/`
### `local_paper_reproduction_patch`
- `tools/rtbarneshut_author_force_checksum_audit.patch`
- `tools/rtbarneshut_author_modern_cuda_build.patch`
- `tools/rtbarneshut_author_single_gpu_device0.patch`
### `local_raw_v4_evidence`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/author_1m_stdout.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/author_checkout_diff.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/author_synthetic25m_stderr.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/author_synthetic25m_stdout.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/author_treelogy_10m_stdout.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4769_author_phase_print_false_10m_stderr.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4769_author_phase_print_false_10m_stdout.txt`
- `future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/pid`
- `future/v4/evidence/v4_goal4636_threshold_summary_pod_gate_2026-06-25/legacy_app_front_door_prepared_optix.stderr.txt`
- `future/v4/evidence/v4_goal4636_threshold_summary_pod_gate_2026-06-25/productized_prepared_execution_runner.stderr.txt`
- `future/v4/evidence/v4_goal4636_threshold_summary_pod_gate_2026-06-25/same_contract_embree.stderr.txt`
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25.tgz`
### `local_review_helper`
- `write_review.py`
### `local_v3_phoenix_review_helper`
- `scripts/run_claude_phoenix_v3_aggregate_review_after_surface_integrity_2026_06_22.ps1`
- `scripts/run_claude_phoenix_v3_core_gaps_status_review_2026_06_22.ps1`
- `scripts/run_claude_phoenix_v3_m30_m33_bundle_review_2026_06_23.ps1`
- `scripts/run_claude_phoenix_v3_m43_grouped_reduction_review_2026_06_23.ps1`
- `scripts/run_claude_phoenix_v3_m44_goal_completion_audit_review_2026_06_23.ps1`
- `scripts/run_claude_phoenix_v3_m44_scorecard_sync_review_2026_06_23.ps1`
- `scripts/run_claude_phoenix_v3_m45_barnes_hut_reaudit_review_2026_06_23.ps1`
- `scripts/run_claude_phoenix_v3_m46_librts_watch_rows_review_2026_06_23.ps1`
- `scripts/run_claude_phoenix_v3_m47_librts_stability_protocol_review_2026_06_23.ps1`
- `scripts/run_claude_phoenix_v3_m48_librts_harness_execution_safety_review_2026_06_23.ps1`
- `scripts/run_claude_phoenix_v3_m49_current_blocker_queue_review_2026_06_23.ps1`
- `scripts/run_claude_phoenix_v3_m50_spatial_topology_runner_fail_closed_review_2026_06_23.ps1`
### `local_v3_phoenix_script_debris`
- `scripts/phoenix_v3_m5_remote_run.sh`
- `scripts/phoenix_v3_serious_paired_v2x_runner.sh`
- `scripts/phoenix_v3_serious_v2x_paired_analysis.py`
- `scripts/v3_claim_grade_all_benchmarks.py`
- `scripts/v3_gpu_python_env_gate.py`
- `scripts/v3_install_gpu_pod_env.sh`
- `scripts/v3_optix_hardware_gate.py`
- `scripts/v3_phoenix_aabb_cpu_reference_oracle.py`
- `scripts/v3_phoenix_aabb_native_query_handle_evidence.py`
- `scripts/v3_phoenix_aabb_native_query_handle_review_gate.py`
- `scripts/v3_phoenix_aabb_native_query_handle_row_wording_gate.py`
- `scripts/v3_phoenix_aabb_native_query_handle_stability_evidence.py`
### `local_v3_phoenix_test_debris`
- `tests/v3_claim_grade_all_benchmarks_test.py`
- `tests/v3_gpu_python_env_gate_script_test.py`
- `tests/v3_negative_route_explanation_test.py`
- `tests/v3_optix_hardware_gate_test.py`
- `tests/v3_paired_v2_v3_benchmark_test.py`
- `tests/v3_phoenix_aabb_candidate_stream_32768_m7_final_review_packet_test.py`
- `tests/v3_phoenix_aabb_candidate_stream_m7_feasibility_test.py`
- `tests/v3_phoenix_aabb_cpu_reference_oracle_test.py`
- `tests/v3_phoenix_aabb_native_query_handle_evidence_test.py`
- `tests/v3_phoenix_aabb_native_query_handle_review_gate_test.py`
- `tests/v3_phoenix_aabb_native_query_handle_row_wording_gate_test.py`
- `tests/v3_phoenix_aabb_native_query_handle_stability_evidence_test.py`
### `local_v4_review_working_record`
- `future/v4/reviews/antigravity_prompt_v4_goal4720_4722_release_candidate_review_2026-06-26.txt`
- `future/v4/reviews/antigravity_v4_goal4616_status_ledger_completion_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4617_grouped_i64_completion_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4617_grouped_i64_promotion_decision_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4617_grouped_i64_promotion_decision_review_retry_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4618_point_group_completion_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4618_point_group_promotion_decision_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4621_catalog_hardening_completion_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4622_tier3_callback_protocol_completion_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4623_development_state_decision_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4624_development_state_naming_cleanup_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4625_design_status_and_next_goals_amended_review_2026-06-24.stderr.txt`

## Interpretation

Public V4 current surface must be clean. history/ is archival. future/ is audit provenance. Known untracked raw evidence and old Phoenix/V3 debris are local workspace cleanup items, not public V4 files.
