# Goal4775 - V4 Release Staging Manifest

Status: `release_staging_manifest_created__pathspec_ready__tag_still_requires_clean_commit`

## Summary

- dirty file entries from `git status -uall`: `1938`
- stage for V4 release commit: `961`
- exclude from V4 release commit: `438`
- hold V3 history out of V4 tag: `302`
- manual review required: `0`
- pathspec ready: `true`
- direct git tag allowed now: `false`
- clean release commit required before tag: `true`
- POD required for this manifest: `false`
- Claude required for this manifest: `false`

## Bucket Counts

| Bucket | Count |
| --- | ---: |
| `exclude_from_v4_release_commit` | `438` |
| `hold_review_debt_not_v4_tag` | `237` |
| `hold_v3_history_not_v4_tag` | `302` |
| `stage_for_v4_release_commit` | `961` |

## Pathspec

- generated pathspec file: `C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/v4_goal4775_release_stage_pathspec_2026-06-27.txt`
- use only after the release owner agrees this exact staging set is the desired V4.0 tag content

## Required Stage Paths

- `README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `future/v4/README.md`
- `future/v4/V4_CURRENT_AGENT_REFRESH_RUNBOOK_2026-06-25.md`
- `future/v4/reviews/v4_gemini_full_coverage_review_debt_for_antigravity_2026-06-27.md`
- `future/v4/reviews/antigravity_v4_gemini_full_coverage_review_2026-06-27.md`
- `future/v4/v4_goal4773_antigravity_review_intake_and_release_owner_status_2026-06-27.md`
- `future/v4/evidence/v4_goal4774_release_packaging_audit_2026-06-27.json`
- `future/v4/v4_goal4774_release_packaging_audit_2026-06-27.md`
- `future/v4/evidence/v4_goal4775_release_staging_manifest_2026-06-27.json`
- `future/v4/v4_goal4775_release_staging_manifest_2026-06-27.md`
- `future/v4/v4_goal4775_release_stage_pathspec_2026-06-27.txt`
- `src/rtdsl/v4_goal4773_release_authorization_status.py`
- `src/rtdsl/v4_goal4774_release_packaging_audit.py`
- `src/rtdsl/v4_goal4775_release_staging_manifest.py`
- `scripts/v4_goal4775_release_staging_manifest.py`
- `tests/v4_goal4773_release_authorization_status_test.py`
- `tests/v4_goal4774_release_packaging_audit_test.py`
- `tests/v4_goal4775_release_staging_manifest_test.py`

## V3 History Held Out

These paths are not staged for the V4 public tag. They can remain as workspace history
or be archived separately, but they must not be silently bundled into the V4 release commit.

- `scripts/phoenix_v3_m5_remote_run.sh`
- `scripts/phoenix_v3_serious_paired_v2x_runner.sh`
- `scripts/phoenix_v3_serious_v2x_paired_analysis.py`
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
- `scripts/run_claude_phoenix_v3_m51_librts_authorized_runbook_review_2026_06_23.ps1`
- `scripts/run_claude_phoenix_v3_m52_pod_surface_audit_review_2026_06_23.ps1`
- `scripts/run_claude_phoenix_v3_m53_open_debt_backfill_review_2026_06_23.ps1`
- `scripts/run_claude_phoenix_v3_m70_m71_backfill_2026_06_24.ps1`
- `scripts/run_claude_phoenix_v3_review_debt_backfill_2026_06_23.ps1`
- `scripts/run_phoenix_v3_m70_m71_post_claude_local_validation_2026_06_24.ps1`
- `scripts/v3_claim_grade_all_benchmarks.py`
- `scripts/v3_gpu_python_env_gate.py`
- `scripts/v3_install_gpu_pod_env.sh`
- `scripts/v3_optix_hardware_gate.py`
- `scripts/v3_phoenix_aabb_cpu_reference_oracle.py`
- `scripts/v3_phoenix_aabb_native_query_handle_evidence.py`
- `scripts/v3_phoenix_aabb_native_query_handle_review_gate.py`
- `scripts/v3_phoenix_aabb_native_query_handle_row_wording_gate.py`
- `scripts/v3_phoenix_aabb_native_query_handle_stability_evidence.py`
- `scripts/v3_phoenix_aabb_prepare_reuse_contract.py`
- `scripts/v3_phoenix_aabb_prepare_reuse_overhead_gate.py`
- `scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py`
- `scripts/v3_phoenix_aabb_prepare_reuse_scale_evidence.py`
- `scripts/v3_phoenix_aabb_prepare_reuse_serious_pod_evidence.py`
- `scripts/v3_phoenix_aabb_query_cache_evidence.py`
- `scripts/v3_phoenix_aabb_raw_oracle_evidence.py`
- `scripts/v3_phoenix_barnes_hut_blocker_intake.py`
- `scripts/v3_phoenix_barnes_hut_fused_partner_m7_candidate.py`
- `scripts/v3_phoenix_barnes_hut_runner_parity_pod_ab.py`
- `scripts/v3_phoenix_barnes_hut_same_basis_wall_time_no_go.py`
- `scripts/v3_phoenix_barnes_hut_t1_phase_residency_probe.py`
- `scripts/v3_phoenix_barnes_hut_vector_accumulation_contract.py`
- `scripts/v3_phoenix_component_union_m38_pod_ab.py`
- `scripts/v3_phoenix_external_verdict_intake.py`
- `scripts/v3_phoenix_grouped_reduction_device_column_candidate.py`
- `scripts/v3_phoenix_grouped_reduction_device_column_m7_final_review_packet.py`
- `scripts/v3_phoenix_grouped_reduction_device_column_pod_evidence.py`
- `scripts/v3_phoenix_grouped_reduction_m41_local_harness.py`
- `scripts/v3_phoenix_grouped_reduction_m7_feasibility.py`
- `scripts/v3_phoenix_grouped_reduction_m7_rerun_packet.py`
- `scripts/v3_phoenix_grouped_reduction_prepared_query_contract.py`
- `scripts/v3_phoenix_grouped_reduction_sum_m7_candidate_wording.py`
- `scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py`
- `scripts/v3_phoenix_hausdorff_threshold_summary_rerun.py`
- `scripts/v3_phoenix_hausdorff_threshold_summary_stability.py`
- `scripts/v3_phoenix_install_reproducibility_gate.py`
- `scripts/v3_phoenix_m21_all_app_protocol_gate.py`
- `scripts/v3_phoenix_m29_barnes_hut_surface_classification.py`
- `scripts/v3_phoenix_m47_librts_stability_protocol.py`
- `scripts/v3_phoenix_m5_topology_intake.py`
- `scripts/v3_phoenix_m61_topology_stream_gap_ledger.py`
- `scripts/v3_phoenix_m67_barnes_hut_phase_structure_pre_audit.py`
- `scripts/v3_phoenix_m68_next_set_a_family_selection.py`
- `scripts/v3_phoenix_m69_rtnn_phase_shape_bridge_audit.py`
- `scripts/v3_phoenix_m6_barnes_hut_intake.py`
- `scripts/v3_phoenix_m70_m71_claude_backfill_intake.py`
- `scripts/v3_phoenix_m70_m71_final_3ai_consensus.py`
- `scripts/v3_phoenix_m70_m71_goal_completion_audit.py`
- `scripts/v3_phoenix_m70_rtnn_focused_protocol.py`
- `scripts/v3_phoenix_m71_rtnn_local_harness_dry_run_gate.py`
- `scripts/v3_phoenix_m7_row_classification_packet.py`
- `scripts/v3_phoenix_major_performance_mandate_gate.py`
- `scripts/v3_phoenix_next_engine_work_queue.py`
- `scripts/v3_phoenix_objective_conformance_gate.py`
- `scripts/v3_phoenix_prepared_session_surface_ledger_gate.py`
- `scripts/v3_phoenix_rayjoin_legacy_materialization_audit.py`
- `scripts/v3_phoenix_rayjoin_point_location_runner_pod_ab.py`
- `scripts/v3_phoenix_release_gap_ledger.py`
- `scripts/v3_phoenix_release_readiness_gate.py`
- ... `222` more

## Excluded Raw Or External Artifacts

- `dist/goal4722_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl`
- `dist/goal4758_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl`
- `external/RT-BarnesHut-author/`
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
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/pod_run.pid`
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/timed_sample01_embree.stderr.txt`
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/timed_sample01_optix.stderr.txt`
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/timed_sample02_embree.stderr.txt`
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/timed_sample02_optix.stderr.txt`
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/timed_sample03_embree.stderr.txt`
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/timed_sample03_optix.stderr.txt`
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/timed_sample04_embree.stderr.txt`
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/timed_sample04_optix.stderr.txt`
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/timed_sample05_embree.stderr.txt`
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/timed_sample05_optix.stderr.txt`
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/validation_embree.stderr.txt`
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/validation_optix.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/k4_32768.edgebin`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v2_14_librts_spatial_index.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v2_14_raydb_style.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v2_14_rt_dbscan.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v2_14_rt_dbscan_parity.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v2_14_triangle_counting.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v3_0_2_librts_spatial_index.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v3_0_2_raydb_style.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v3_0_2_rt_dbscan.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v3_0_2_rt_dbscan_parity.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v3_0_2_triangle_counting.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v4_current_librts_spatial_index.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v4_current_raydb_style.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v4_current_rt_dbscan.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v4_current_rt_dbscan_parity.stderr.txt`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/raw/v4_current_triangle_counting.stderr.txt`
- `future/v4/evidence/v4_goal4658_rtdbscan_route_lever_20260625/raw/v4_cupy_parity.stderr.txt`
- `future/v4/evidence/v4_goal4658_rtdbscan_route_lever_20260625/raw/v4_cupy_serious.stderr.txt`
- `future/v4/evidence/v4_goal4658_rtdbscan_route_lever_20260625/raw/v4_numba_parity.stderr.txt`
- `future/v4/evidence/v4_goal4658_rtdbscan_route_lever_20260625/raw/v4_numba_serious.stderr.txt`
- `future/v4/evidence/v4_goal4659_hausdorff_v4_route_20260625/v3_0_2_optix_device_max_numba_copies16384.json`
- `future/v4/evidence/v4_goal4669_serious_20260625/k4_32768.edgebin`
- `future/v4/evidence/v4_goal4669_serious_20260625/pid`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v2_14_hausdorff_xhd.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v2_14_librts_spatial_index.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v2_14_raydb_style.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v2_14_rt_dbscan.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v2_14_rt_dbscan_parity.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v2_14_triangle_counting.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v3_0_2_hausdorff_xhd.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v3_0_2_librts_spatial_index.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v3_0_2_raydb_style.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v3_0_2_rt_dbscan.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v3_0_2_rt_dbscan_parity.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v3_0_2_triangle_counting.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v4_current_hausdorff_xhd.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v4_current_hausdorff_xhd_correctness_1m.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v4_current_librts_spatial_index.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v4_current_raydb_style.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v4_current_rt_dbscan.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v4_current_rt_dbscan_parity.stderr.txt`
- `future/v4/evidence/v4_goal4669_serious_20260625/raw/v4_current_triangle_counting.stderr.txt`
- `future/v4/evidence/v4_goal4670_rtdbscan_diag_20260625/v4_blocked_grouped_stream_negative_probe.stderr.txt`
- `future/v4/evidence/v4_goal4670_rtdbscan_diag_20260625/v4_cupy_column_signature_historical_route.stderr.txt`
- `future/v4/evidence/v4_goal4670_rtdbscan_diag_20260625/v4_declared_all_items_direct_status.stderr.txt`
- `future/v4/evidence/v4_goal4670_rtdbscan_diag_20260625/v4_default_numba_signature.stderr.txt`
- `future/v4/evidence/v4_goal4670_rtdbscan_diag_20260625/v4_direct_side_effect_no_culling_probe.stderr.txt`
- `future/v4/evidence/v4_goal4670_rtdbscan_diag_20260625/v4_direct_side_effect_probe.stderr.txt`
- `future/v4/evidence/v4_goal4670_rtdbscan_diag_20260625/v4_measured_all_true_direct_status.stderr.txt`
- `future/v4/evidence/v4_goal4670_rtdbscan_diag_20260625/v4_no_same_root_culling_negative_probe.stderr.txt`
- `future/v4/evidence/v4_goal4676_serious_2026-06-25/v2_14_correctness.stderr.txt`
- `future/v4/evidence/v4_goal4676_serious_2026-06-25/v2_14_serious.stderr.txt`
- ... `358` more

## Goal-Level Decision Audit

1. 我是否愚蠢了？没有继续 `git add .`，这是正确的；但 Goal4774 的候选分桶过宽，若直接使用会愚蠢。
2. 如果是，我做了哪些动作使决策愚蠢？把所有 `tests/`、`scripts/` 粗略视为候选，会把 V3 Phoenix 历史混进 V4 tag。
3. 是否有别的路径避免卡在坏思路？有：逐文件展开 `git status -uall`，把 V3 history、raw logs、external/build artifacts 独立排除。
4. 是否可以尝试不同路径真正解决问题？可以，下一步只用这份 pathspec 做可审 staging，不直接打 tag。

## Next Step

Run the manifest tests and full V4 tests. If they pass, the release owner can inspect
the generated pathspec before any staging or commit. A public V4.0 tag still requires
a clean release commit; this file does not create the tag.
