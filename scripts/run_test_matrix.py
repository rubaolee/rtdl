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
        "tests.goal4545_v3_0_m146_source_tree_doctor_refresh_test",
        "tests.goal4547_v3_0_m148_source_tree_doctor_v3_matrix_hint_test",
        "tests.goal4548_v3_0_m149_legacy_full_runner_repair_test",
        "tests.goal4549_v3_0_m150_embeddability_strategy_intake_test",
        "tests.goal4550_v3_0_m151_c_abi_draft_test",
        "tests.goal4551_v3_0_m152_c_abi_header_compile_smoke_test",
        "tests.goal4552_v3_0_m153_c_abi_stub_library_test",
        "tests.goal4553_v3_0_m154_c_abi_c_client_smoke_test",
        "tests.goal4554_v3_0_m155_c_abi_makefile_build_target_test",
        "tests.goal4555_v3_0_m156_c_abi_header_boundary_refresh_test",
        "tests.goal4556_v3_0_m157_c_abi_exported_symbol_audit_test",
        "tests.goal4557_v3_0_m158_c_abi_fail_closed_query_entrypoints_test",
        "tests.goal4558_v3_0_m159_c_abi_host_aabb2_query_proof_test",
        "tests.goal4559_v3_0_m160_c_abi_example_client_test",
        "tests.goal4560_v3_0_m161_c_abi_embedding_readme_test",
        "tests.goal4561_v3_0_m162_c_abi_aabb2_contract_doc_test",
        "tests.goal4562_v3_0_m163_embeddability_status_refresh_test",
        "tests.goal4563_v3_0_m164_c_abi_aabb2_negative_runtime_test",
        "tests.goal4564_v3_0_m165_c_abi_source_tree_doctor_surface_test",
        "tests.goal4565_v3_0_m166_c_abi_stability_policy_test",
        "tests.goal4566_v3_0_m167_c_abi_symbol_manifest_test",
        "tests.goal4567_v3_0_m168_c_abi_aabb2_layout_validation_test",
        "tests.goal4568_v3_0_m169_zero_copy_interop_contract_test",
        "tests.goal4569_v3_0_m170_embeddability_progress_gate_test",
        "tests.goal4570_v3_0_m171_c_abi_ownership_threading_contract_test",
        "tests.goal4571_v3_0_m172_c_abi_aabb2_result_ordering_contract_test",
        "tests.goal4572_v3_0_m173_c_abi_doctor_docs_surface_test",
        "tests.goal4573_v3_0_m174_c_abi_backend_runtime_fail_closed_test",
        "tests.goal4574_v3_0_m175_c_abi_patch_version_refresh_test",
        "tests.goal4575_v3_0_m176_c_abi_version_negotiation_test",
        "tests.goal4576_v3_0_m177_c_abi_staging_bundle_test",
        "tests.goal4577_v3_0_m178_c_abi_pkg_config_stage_test",
        "tests.goal4578_v3_0_m179_c_abi_capability_queries_test",
        "tests.goal4579_v3_0_m180_c_abi_direct_link_example_test",
        "tests.goal4580_v3_0_m181_embeddability_readiness_packet_test",
        "tests.goal4581_v3_0_m182_c_abi_python_ctypes_example_test",
        "tests.goal4582_v3_0_m183_c_abi_python_ctypes_aabb2_query_test",
        "tests.goal4583_v3_0_m184_embeddability_readiness_refresh_test",
        "tests.goal4584_v3_0_m185_source_tree_doctor_ctypes_surface_test",
        "tests.goal4585_v3_0_m186_c_abi_staging_inventory_refresh_test",
        "tests.goal4586_v3_0_m187_c_abi_pkg_config_relocatable_stage_test",
        "tests.goal4587_v3_0_m188_c_abi_stage_archive_test",
        "tests.goal4588_v3_0_m189_source_tree_doctor_stage_archive_test",
        "tests.goal4589_v3_0_m190_embeddability_shipping_readiness_refresh_test",
        "tests.goal4590_v3_0_m191_embeddability_architecture_status_refresh_test",
        "tests.goal4591_v3_0_m192_c_abi_host_external_runtime_gate_test",
        "tests.goal4592_v3_0_m193_c_abi_cuda_buffer_metadata_gate_test",
        "tests.goal4593_v3_0_m194_python_ctypes_cuda_metadata_bridge_test",
        "tests.goal4594_v3_0_m195_embeddability_metadata_readiness_refresh_test",
        "tests.goal4595_v3_0_m196_c_abi_prefix_stage_test",
        "tests.goal4596_v3_0_m197_source_tree_doctor_prefix_stage_test",
        "tests.goal4597_v3_0_m198_prefix_stage_python_ctypes_smoke_test",
        "tests.goal4598_v3_0_m199_embeddability_architecture_prefix_status_test",
        "tests.goal4599_v3_0_m200_python_ctypes_layout_audit_test",
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
    parser.add_argument(
        "--group",
        choices=(
            "unit",
            "integration",
            "system",
            "full",
            "v3_current",
            "v0_2_local",
            "v0_2_linux",
            "v0_2_full",
        ),
        default="full",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = run_group(args.group)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
