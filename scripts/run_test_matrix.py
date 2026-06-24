#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


TEST_GROUPS: dict[str, tuple[str, ...]] = {
    "unit": (
        "tests.baseline_contracts_test",
        "tests.dsl_negative_test",
        "tests.goal10_workloads_test",
        "tests.goal15_compare_test",
        "tests.goal17_prepared_runtime_test",
        "tests.goal18_result_mode_test",
        "tests.goal19_compare_test",
        "tests.goal22_reproduction_test",
        "tests.goal23_reproduction_test",
        "tests.goal28b_staging_test",
        "tests.goal28c_conversion_test",
        "tests.goal28d_execution_test",
        "tests.goal30_precision_abi_test",
        "tests.goal31_lsi_gap_closure_test",
        "tests.goal32_lsi_sort_sweep_test",
        "tests.goal36_performance_test",
        "tests.goal40_native_oracle_test",
        "tests.paper_reproduction_test",
        "tests.report_smoke_test",
        "tests.rtdsl_language_test",
        "tests.rtdsl_py_test",
        "tests.rtdsl_ray_query_test",
        "tests.rtdsl_simulator_test",
        "tests.section_5_6_scalability_test",
        "tests.test_core_quality",
    ),
    "integration": (
        "tests.baseline_integration_test",
        "tests.cpu_embree_parity_test",
        "tests.evaluation_test",
        "tests.goal44_optix_benchmark_test",
        "tests.optix_embree_interop_test",
        "tests.rtdsl_embree_test",
        "tests.rtdsl_vulkan_test",
    ),
    "system": (
        "tests.goal34_performance_test",
        "tests.goal35_blockgroup_waterbodies_test",
        "tests.goal37_lkau_pkau_test",
        "tests.goal38_feasibility_test",
        "tests.goal43_optix_validation_test",
        "tests.goal45_optix_county_zipcode_test",
        "tests.goal47_optix_goal41_large_checks_test",
        "tests.goal50_postgis_ground_truth_test",
        "tests.goal54_lkau_pkau_four_system_test",
    ),
    "v3_rebuild": (
        "tests.v3_rebuild_reset_test",
        "tests.v3_rebuild_evidence_classification_test",
        "tests.v3_rebuild_spatial_rayjoin_route_test",
        "tests.v3_rebuild_tutorial_surface_test",
        "tests.v3_negative_route_explanation_test",
        "tests.v3_claim_grade_all_benchmarks_test",
        "tests.v3_paired_v2_v3_benchmark_test",
        "tests.v3_gpu_python_env_gate_script_test",
        "tests.v3_optix_hardware_gate_test",
        "tests.v3_release_wording_gate_test",
        "tests.v3_phoenix_next_engine_work_queue_test",
        "tests.v3_phoenix_next_dominant_hotpath_selection_test",
        "tests.v3_phoenix_prepared_execution_session_runner_test",
        "tests.v3_phoenix_install_reproducibility_gate_test",
        "tests.v3_phoenix_secondary_platform_gate_test",
        "tests.v3_phoenix_release_surface_breadth_gate_test",
        "tests.v3_phoenix_objective_conformance_gate_test",
        "tests.v3_phoenix_major_performance_mandate_gate_test",
        "tests.v3_phoenix_serious_v2x_paired_analysis_test",
        "tests.v3_phoenix_release_gap_ledger_test",
        "tests.v3_phoenix_external_verdict_intake_test",
        "tests.v3_phoenix_m30_m33_review_bundle_gate_test",
        "tests.v3_phoenix_prepared_session_surface_ledger_gate_test",
        "tests.v3_phoenix_m35_focused_gap_ledger_test",
        "tests.v3_phoenix_m36_grouped_reduction_core_node_gate_test",
        "tests.v3_phoenix_m37_adapter_metadata_contract_test",
        "tests.v3_phoenix_m37_component_union_core_node_gate_test",
        "tests.v3_phoenix_m38_component_union_focused_pod_protocol_test",
        "tests.v3_phoenix_m39_component_union_harness_test",
        "tests.v3_phoenix_m41_grouped_reduction_harness_test",
        "tests.v3_phoenix_review_debt_and_completion_gate_test",
        "tests.v3_phoenix_m49_current_blocker_queue_gate_test",
        "tests.v3_phoenix_m50_spatial_runner_fail_closed_gate_test",
        "tests.v3_phoenix_m51_librts_authorized_runbook_gate_test",
        "tests.v3_phoenix_m52_pod_surface_audit_gate_test",
        "tests.v3_phoenix_m53_open_debt_backfill_gate_test",
        "tests.v3_phoenix_m54_librts_authorization_packet_gate_test",
        "tests.v3_phoenix_m55_librts_authorized_pod_intake_gate_test",
        "tests.v3_phoenix_m56_librts_set_b_metadata_diagnosis_test",
        "tests.v3_phoenix_m57_librts_rerun_authorization_packet_gate_test",
        "tests.v3_phoenix_m58_librts_authorized_rerun_intake_gate_test",
        "tests.v3_phoenix_m59_librts_yellow_open_decision_gate_test",
        "tests.v3_phoenix_m60_step2_set_a_selection_gate_test",
        "tests.v3_phoenix_m61_topology_stream_gap_ledger_test",
        "tests.v3_phoenix_m62_topology_stream_contract_gate_test",
        "tests.v3_phoenix_m63_topology_stream_m3_phase_bridge_gate_test",
        "tests.v3_phoenix_m64_topology_stream_step3_audit_gate_test",
        "tests.v3_phoenix_m65_topology_stream_step3_audit_negative_hardening_gate_test",
        "tests.v3_phoenix_m66_topology_stream_pod_authorization_non_go_gate_test",
        "tests.v3_phoenix_m67_barnes_hut_phase_structure_pre_audit_gate_test",
        "tests.v3_phoenix_m68_next_set_a_family_selection_gate_test",
        "tests.v3_phoenix_m69_rtnn_phase_shape_bridge_audit_gate_test",
        "tests.v3_phoenix_m70_rtnn_focused_protocol_gate_test",
        "tests.v3_phoenix_m71_rtnn_local_harness_dry_run_gate_test",
        "tests.v3_phoenix_m70_m71_claude_backfill_packet_gate_test",
        "tests.v3_phoenix_m70_m71_claude_backfill_intake_test",
        "tests.v3_phoenix_m70_m71_goal_completion_audit_test",
        "tests.v3_phoenix_m70_m71_final_3ai_consensus_test",
        "tests.v3_phoenix_release_readiness_gate_test",
        "tests.v3_public_docs_rebuild_surface_test",
        "tests.v3_phoenix_user_facing_performance_dossier_test",
        "tests.v3_phoenix_route_capability_map_test",
        "tests.v3_phoenix_m4_grouped_continuation_packet_test",
        "tests.v3_phoenix_m4_grouped_continuation_evidence_test",
        "tests.v3_phoenix_m10_same_stream_accounting_interpretation_test",
        "tests.v3_rayjoin_pip_missing_author_test",
        "tests.v3_phoenix_m5_topology_packet_test",
        "tests.v3_phoenix_m5_topology_intake_test",
        "tests.v3_phoenix_m5_topology_evidence_test",
        "tests.v3_phoenix_m6_barnes_hut_intake_test",
        "tests.v3_phoenix_m6_barnes_hut_evidence_test",
        "tests.v3_phoenix_barnes_hut_vector_accumulation_contract_test",
        "tests.v3_phoenix_barnes_hut_same_basis_wall_time_no_go_test",
        "tests.v3_phoenix_barnes_hut_fused_partner_m7_candidate_test",
        "tests.v3_phoenix_raydb_m28_evidence_test",
        "tests.v3_phoenix_raydb_grouped_reduction_redo_alignment_test",
        "tests.v3_phoenix_triangle_prepared_graph_intake_test",
        "tests.v3_phoenix_triangle_prepared_graph_tutorial_candidate_test",
        "tests.v3_phoenix_triangle_prepared_graph_80000_m7_final_review_packet_test",
        "tests.v3_phoenix_rtnn_ranked_summary_intake_test",
        "tests.v3_phoenix_rtnn_ranked_summary_wall_time_boundary_test",
        "tests.v3_phoenix_rtnn_m112_reconciliation_test",
        "tests.v3_phoenix_rtnn_full_batch_float32_same_contract_runner_test",
        "tests.v3_phoenix_optix_cubin_cache_test",
        "tests.v3_phoenix_rtnn_cubin_cache_evidence_test",
        "tests.v3_phoenix_rtnn_self_query_aggregate_test",
        "tests.v3_phoenix_rtnn_self_query_graph_evidence_test",
        "tests.v3_phoenix_rtnn_lazy_exact_prepare_test",
        "tests.v3_phoenix_rtnn_self_query_evidence_test",
        "tests.v3_phoenix_rtnn_lazy_exact_prepare_evidence_test",
        "tests.v3_phoenix_rtnn_column_source_residency_gap_test",
        "tests.v3_phoenix_rtnn_npz_cubin_cache_evidence_test",
        "tests.v3_phoenix_rtnn_prepared_repeat50_amortization_evidence_test",
        "tests.v3_phoenix_rtnn_prepared_repeat50_review_gate_test",
        "tests.v3_phoenix_rtnn_full_batch_float32_pod_evidence_test",
        "tests.v3_phoenix_rtnn_full_batch_float32_review_gate_test",
        "tests.v3_phoenix_aabb_cpu_reference_oracle_test",
        "tests.v3_phoenix_aabb_candidate_stream_m7_feasibility_test",
        "tests.v3_phoenix_aabb_candidate_stream_32768_m7_final_review_packet_test",
        "tests.v3_phoenix_aabb_prepared_query_cache_test",
        "tests.v3_phoenix_aabb_query_cache_evidence_test",
        "tests.v3_phoenix_aabb_native_query_handle_evidence_test",
        "tests.v3_phoenix_aabb_raw_oracle_evidence_test",
        "tests.v3_phoenix_aabb_native_query_handle_stability_evidence_test",
        "tests.v3_phoenix_aabb_native_query_handle_row_wording_gate_test",
        "tests.v3_phoenix_aabb_native_query_handle_review_gate_test",
        "tests.v3_phoenix_aabb_prepare_reuse_contract_test",
        "tests.v3_phoenix_aabb_prepare_reuse_pod_runner_test",
        "tests.v3_phoenix_aabb_prepare_reuse_serious_pod_evidence_test",
        "tests.v3_phoenix_aabb_prepare_reuse_scale_evidence_test",
        "tests.v3_phoenix_aabb_prepare_reuse_overhead_gate_test",
        "tests.v3_phoenix_hausdorff_threshold_summary_boundary_test",
        "tests.v3_phoenix_robot_collision_flag_stream_boundary_test",
        "tests.v3_phoenix_contact_manifold_broadphase_boundary_test",
        "tests.v3_phoenix_m7_row_classification_packet_test",
        "tests.v3_phoenix_grouped_reduction_m7_feasibility_test",
        "tests.v3_phoenix_grouped_reduction_m7_rerun_packet_test",
        "tests.v3_phoenix_grouped_reduction_m7_pod_evidence_test",
        "tests.v3_phoenix_grouped_reduction_prepared_query_contract_test",
        "tests.v3_phoenix_grouped_reduction_scalar_broadcast_optimization_test",
        "tests.v3_phoenix_grouped_reduction_device_column_candidate_test",
        "tests.v3_phoenix_grouped_reduction_device_column_pod_evidence_test",
        "tests.v3_phoenix_grouped_reduction_device_column_m7_final_review_packet_test",
        "tests.v3_phoenix_grouped_reduction_sum_m7_candidate_wording_test",
        "tests.v3_phoenix_grouped_reduction_sum_262144_m7_final_review_packet_test",
        "tests.v3_phoenix_spatial_rayjoin_m7_feasibility_test",
        "tests.v3_phoenix_spatial_rayjoin_topology_stream_contract_test",
        "tests.v3_phoenix_spatial_rayjoin_m3_gap_analysis_test",
        "tests.v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner_test",
        "tests.v3_phoenix_spatial_rayjoin_exact_executor_intake_test",
        "tests.v3_phoenix_spatial_rayjoin_relation_status_corrected_no_go_test",
        "tests.v3_phoenix_spatial_rayjoin_relation_status_exact_f64_intake_test",
        "tests.v3_phoenix_spatial_rayjoin_relation_status_exact_f64_adverse_subset_test",
        "tests.v3_phoenix_spatial_rayjoin_relation_status_exact_f64_review_gate_test",
        "tests.v3_phoenix_spatial_rayjoin_hotpath_probe_no_go_test",
        "tests.v3_phoenix_spatial_overlay_active_count_full_scale_candidate_test",
        "tests.v3_phoenix_spatial_active_p0_closure_gate_test",
        "tests.v3_phoenix_spatial_relation_status_prefilter_zero_experiment_test",
        "tests.v3_phoenix_spatial_squared_boundary_equivalence_test",
        "tests.v3_phoenix_spatial_relation_status_squared_boundary_candidate_test",
        "tests.v3_phoenix_spatial_topology_stream_redo_alignment_test",
        "tests.v3_phoenix_spatial_relation_status_count_only_no_diagnostics_no_go_test",
        "tests.v3_phoenix_rtdbscan_m7_feasibility_test",
        "tests.v3_phoenix_rtdbscan_same_contract_rerun_test",
        "tests.v3_phoenix_rtdbscan_continuation_bottleneck_no_go_test",
        "tests.v3_phoenix_rtdbscan_component_signature_optimization_test",
        "tests.v3_phoenix_rtdbscan_component_signature_optimization_packet_test",
        "tests.v3_phoenix_rtdbscan_component_union_redo_alignment_test",
    ),
    "v3_current": (
        "tests.goal4508_v3_0_m112_rtnn_clean_target_closeout_test",
        "tests.goal4509_v3_0_m113_prepared_graph_chunk_executor_test",
        "tests.goal4510_v3_0_m114_rtdbscan_clean_target_audit_test",
        "tests.goal4511_v3_0_m115_triangle_clean_target_audit_test",
        "tests.goal4512_v3_0_m116_barnes_hut_clean_target_audit_test",
        "tests.goal4513_v3_0_m117_primitive_app_clean_target_audit_test",
        "tests.goal4514_v3_0_m118_rayjoin_mixed_explicit_clean_target_audit_test",
        "tests.goal4515_v3_0_m119_all_benchmark_app_clean_target_closeout_test",
        "tests.goal4516_v3_0_m120_prepared_graph_chunk_adoption_gate_test",
        "tests.goal4517_v3_0_m121_aggregate_tree_fused_rt_native_contract_test",
        "tests.goal4518_v3_0_m122_barnes_hut_device_column_rtcore_boundary_test",
        "tests.goal4519_v3_0_m123_rtdbscan_chunk_handle_gate_test",
        "tests.goal4520_v3_0_m124_rtdbscan_chunk_handle_smoke_test",
        "tests.goal4521_v3_0_m125_triangle_unique_count_gate_test",
        "tests.goal4522_v3_0_m126_route_adequacy_consistency_test",
        "tests.goal4523_v3_0_m127_barnes_hut_rt_native_symbol_gap_test",
        "tests.goal4524_v3_0_m128_benchmark_implementation_queue_test",
        "tests.goal4525_v3_0_m129_barnes_hut_rt_native_python_wrapper_gate_test",
        "tests.goal4526_v3_0_m130_barnes_hut_rt_native_fail_closed_abi_test",
        "tests.goal4527_v3_0_m131_barnes_hut_rt_native_traversal_semantic_gate_test",
        "tests.goal4528_v3_0_m132_rtdbscan_prepared_graph_capture_test",
        "tests.goal4530_v3_0_m133_triangle_device_key_payload_merge_test",
        "tests.goal4531_v3_0_m134_triangle_weighted_replay_graph_capture_test",
        "tests.goal4533_v3_0_m135_v3_claim_scope_closeout_test",
        "tests.goal4534_v3_0_m136_v3_current_app_completion_gate_test",
        "tests.goal4535_v3_0_m137_v3_completion_readiness_audit_test",
        "tests.goal4536_v3_0_m138_v3_internal_completion_packet_test",
        "tests.goal4537_v3_0_completion_review_request_test",
        "tests.goal4538_v3_0_m139_v3_completion_review_consensus_test",
        "tests.goal4539_v3_0_m140_triangle_capture_mode_audit_test",
        "tests.goal4540_v3_0_m141_triangle_non_graph_stream_closure_gate_test",
        "tests.goal4541_v3_0_m142_barnes_hut_current_route_closure_gate_test",
        "tests.goal4542_v3_0_m143_post_closure_surface_audit_test",
        "tests.goal4543_v3_0_m144_major_performance_target_refresh_test",
        "tests.goal4544_v3_0_m145_app_author_strategy_doc_test",
        "tests.goal4547_v3_0_m148_source_tree_doctor_v3_matrix_hint_test",
        "tests.goal4548_v3_0_m149_legacy_full_runner_repair_test",
    ),
    "v0_2_local": (
        "tests.goal110_baseline_runner_backend_test",
        "tests.goal110_segment_polygon_hitcount_semantics_test",
        "tests.goal111_generate_only_mvp_test",
        "tests.goal113_generate_only_maturation_test",
        "tests.goal116_segment_polygon_backend_audit_test",
        "tests.goal118_segment_polygon_linux_large_perf_test",
        "tests.goal128_segment_polygon_anyhit_postgis_test",
        "tests.goal129_generate_only_second_workload_test",
    ),
    "v0_2_linux": (
        "tests.goal110_segment_polygon_hitcount_closure_test",
        "tests.goal114_segment_polygon_postgis_test",
    ),
}

# After the 2026-06-24 V3 cleanup, the default V3 gate is the clean current
# user surface. Historical rebuild/evidence milestone tests remain importable in
# the repository, but they are no longer the default V3 user-facing matrix.
_V3_CURRENT_SURFACE_GROUP = (
    "tests.v3_rebuild_reset_test",
    "tests.v3_rebuild_tutorial_surface_test",
    "tests.v3_public_docs_rebuild_surface_test",
    "tests.v3_release_wording_gate_test",
    "tests.goal4278_source_tree_doctor_test",
)
TEST_GROUPS["v3_current_surface"] = _V3_CURRENT_SURFACE_GROUP
TEST_GROUPS["v3_rebuild"] = _V3_CURRENT_SURFACE_GROUP


def build_env() -> dict[str, str]:
    env = os.environ.copy()
    pythonpath_key = next((key for key in env if key.upper() == "PYTHONPATH"), "PYTHONPATH")
    entries = [str(ROOT / "src"), str(ROOT)]
    existing = env.get(pythonpath_key)
    if existing:
        entries.append(existing)
    env[pythonpath_key] = os.pathsep.join(entries)
    return env


def group_modules(name: str) -> tuple[str, ...]:
    if name == "full":
        return TEST_GROUPS["unit"] + TEST_GROUPS["integration"] + TEST_GROUPS["system"]
    if name == "v0_2_full":
        return TEST_GROUPS["v0_2_local"] + TEST_GROUPS["v0_2_linux"]
    return TEST_GROUPS[name]


def run_group(name: str) -> dict[str, object]:
    modules = group_modules(name)
    cp = subprocess.run(
        [sys.executable, "-m", "unittest", *modules],
        cwd=str(ROOT),
        env=build_env(),
        text=True,
        capture_output=True,
        check=False,
    )
    output = cp.stdout
    if cp.stderr:
        output = (output + ("\n" if output else "") + cp.stderr).strip()
    return {
        "group": name,
        "command": sys.executable + " -m unittest " + " ".join(modules),
        "module_count": len(modules),
        "returncode": cp.returncode,
        "ok": cp.returncode == 0,
        "output": output,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the RTDL test matrix by group.")
    choices = tuple(TEST_GROUPS.keys()) + ("full", "v0_2_full")
    parser.add_argument(
        "--group",
        choices=choices,
        default="full",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path to write the matrix payload as JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = run_group(args.group)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
