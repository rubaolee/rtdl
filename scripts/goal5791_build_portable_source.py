#!/usr/bin/env python3
"""Build the deterministic, native-free Goal5791 portable source.

The sole base is Goal5790-A1 portable-source v4.  Its non-self manifest is
fully rehashed before overlay.  Exactly two product files may change, at the
old/new hashes frozen by Goal5791-A1; every other overlay is a Goal5791 or
review-authority document, harness, or test.  The complete successor payload
is scanned for nested containers, executable/device binaries, private state,
and unsafe names before a deterministic source/twin pair is written.

This builder is CPU-only.  It does not build a native, run a GPU, contact Home
or a POD, start a formal worker, or record a performance timing.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import stat
import tarfile
import tempfile
from typing import Mapping


ROOT = Path(__file__).resolve().parents[1]
BASE_SOURCE = ROOT / (
    "history/internal_docs/goal5790_a1_portable_source_v4_20260816.tar.gz"
)
BASE_SOURCE_SHA256 = (
    "fe7cb3ea456b02432339dca6fe51f9bd8b05bfbb373c8f13fa38e3a68907fd1f"
)
BASE_SOURCE_BYTES = 3_266_868
BASE_TREE_SHA256 = (
    "62ff2a310517eed5d3c8ef64d757f714346f211416a6cf7ba5034d9013b24de6"
)
BASE_MANIFEST = (
    "history/internal_docs/goal5790_a1_portable_source_manifest_v4_20260816.json"
)
BASE_MANIFEST_SHA256 = (
    "d538a1ddaa79768feb9c8845077c069e444151d5aa76a59f50bd55922933b9c5"
)
PRESERVED_BASE_MANIFEST_MEMBER = (
    "history/internal_docs/"
    "goal5791_frozen_goal5790_a1_v4_base_manifest_20260817.json"
)
NEW_MANIFEST = (
    "history/internal_docs/goal5791_portable_source_manifest_v1_20260817.json"
)
BUILDER_MEMBER = "scripts/goal5791_build_portable_source.py"
CANONICAL_OUTPUT_PATH = (
    "history/internal_docs/goal5791_portable_source_v26_20260820.tar.gz"
)
CANONICAL_TWIN_PATH = (
    "history/internal_docs/goal5791_portable_source_v26_twin_20260820.tar.gz"
)
CANONICAL_RECEIPT_PATH = (
    "history/internal_docs/goal5791_portable_source_v26_build_receipt_20260820.json"
)
PRODUCT_DELTA = {
    "src/rtdsl/v4_operation_evidence.py": {
        "base_sha256": (
            "55aa2a2752914e393462fe501db8e22af1dcacce628ad09ea4d2d7903ca1c9e6"),
        "successor_sha256": (
            "ff59cba24c7ae188e9f99c3a29a968e0ea83e465033084e81665ee3eff129026"),
    },
    "src/rtdsl/v4_triangle_reduction_device_runtime.py": {
        "base_sha256": (
            "bcaca714158eedafd102d73cb2ad0ec3b4c6efc7ec46fc2303d71c4d327a465e"),
        "successor_sha256": (
            "d045c9ce04e5b77bbb7785191cdd07d7430de97e7ffdd4f5e0c3a60937b6ba00"),
    },
}

# Filled only after the formal worker/evaluator/recount and successor source
# authority are final.  The builder deliberately refuses to run if this map
# and OVERLAY_PATHS differ, so a partially edited candidate cannot be sealed.
OVERLAY_PATHS = (
    "src/rtdsl/v4_operation_evidence.py",
    "src/rtdsl/v4_triangle_reduction_device_runtime.py",
    "scripts/goal5791_build_owner_authority.py",
    "scripts/goal5791_build_pre_pod_bundle.py",
    "scripts/goal5791_build_pretarget_authority.py",
    "scripts/goal5791_cpu_test_gate.py",
    "scripts/goal5791_formal_contract.py",
    "scripts/goal5791_formal_controller.py",
    "scripts/goal5791_formal_evaluate.py",
    "scripts/goal5791_formal_independent_recount.py",
    "scripts/goal5791_formal_worker.py",
    "scripts/goal5791_home_clean_validate.py",
    "scripts/goal5791_home_token_validation.py",
    "scripts/goal5791_independent_home_recount.py",
    "scripts/goal5791_independent_portable_audit.py",
    "scripts/goal5791_open_upload_staging.py",
    "scripts/goal5791_segment_descriptors.py",
    "scripts/goal5791_target_prepare.py",
    "scripts/goal5791_target_producer_probe.py",
    "scripts/goal5791_target_token_smoke.py",
    "scripts/goal5791_trace_record_cost_diagnostic.py",
    "tests/goal5791_data_oracle_authority_test.py",
    "tests/goal5791_formal_contract_test.py",
    "tests/goal5791_formal_evaluator_recount_test.py",
    "tests/goal5791_formal_worker_controller_test.py",
    "tests/goal5791_portable_home_harness_test.py",
    "tests/goal5791_pre_pod_base_budget_audit_test.py",
    "tests/goal5791_pre_worker_zero_claim_freeze_test.py",
    "tests/goal5791_pretimer_execution_token_amendment_test.py",
    "tests/goal5791_segment_descriptors_test.py",
    "tests/goal5791_successor_source_authority_test.py",
    "tests/goal5791_verified_fusion_execution_token_test.py",
    "history/internal_docs/goal5790_a1_owner_returned_external_review_absorption_20260817.json",
    "history/internal_docs/goal5790_a1_postreview_claim_clarification_20260817.md",
    "history/internal_docs/goal5790_a1_home_rejected_program_suite_result_20260816.json",
    "history/internal_docs/goal5790_home_functional_closure_result_20260816.json",
    "history/internal_docs/goal5790_same_source_same_cohort_fusion_ablation_technical_report_20260816.md",
    "history/internal_docs/review_goal5790_a1_home_rejected_program_suite_20260816.md",
    "history/internal_docs/goal5791_amendment_a1_pretimer_fusion_execution_token_result_20260817.json",
    "history/internal_docs/goal5791_amendment_a1_pretimer_fusion_execution_token_technical_report_20260817.md",
    "history/internal_docs/goal5791_amendment_a2_segment_plan_input_token_binding_result_20260817.json",
    "history/internal_docs/goal5791_amendment_a2_segment_plan_input_token_binding_technical_report_20260817.md",
    "history/internal_docs/goal5791_frozen_triangle_data_and_oracle_authority_20260817.json",
    "history/internal_docs/goal5791_owner_authority_request_protocol_20260817.md",
    "history/internal_docs/goal5791_pre_pod_conservative_runtime_budget_20260817.json",
    "history/internal_docs/goal5791_pre_pod_portable_base_and_bundle_audit_20260817.json",
    "history/internal_docs/goal5791_pre_pod_portable_base_and_bundle_audit_20260817.md",
    "history/internal_docs/goal5791_pre_worker_zero_related_work_and_claim_freeze_20260817.json",
    "history/internal_docs/goal5791_pre_worker_zero_related_work_and_claim_freeze_20260817.md",
    "history/internal_docs/goal5791_preregistration_20260817.json",
    "history/internal_docs/goal5791_preregistration_v2_20260817.json",
    "history/internal_docs/goal5791_preregistration_v3_20260817.json",
    "history/internal_docs/goal5791_preregistration_v4_20260817.json",
    "history/internal_docs/goal5791_preregistration_v5_20260818.json",
    "history/internal_docs/goal5791_preregistration_v6_20260819.json",
    "history/internal_docs/goal5791_preregistration_v7_20260819.json",
    "history/internal_docs/goal5791_preregistration_v8_20260820.json",
    "history/internal_docs/goal5791_preregistration_v9_20260820.json",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_20260817.json",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v2_20260817.json",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v3_20260817.json",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v4_20260817.json",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v5_20260818.json",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v6_20260819.json",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v7_20260819.json",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v8_20260820.json",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v9_20260820.json",
    "history/internal_docs/goal5791_successor_source_authority_20260817.json",
    "history/internal_docs/goal5791_successor_source_authority_v2_20260817.json",
    "history/internal_docs/goal5791_v3_prereg_pretarget_terminal_supersession_20260817.md",
    "history/internal_docs/goal5791_v3_prereg_pretarget_terminal_supersession_authority_20260817.json",
    "history/internal_docs/goal5791_v4_successor_lineage_authority_20260817.json",
    "history/internal_docs/goal5791_portable_source_v1_zero_output_terminal_20260817.json",
    "history/internal_docs/goal5791_portable_source_v1_zero_output_terminal_20260817.md",
    "history/internal_docs/goal5791_portable_source_v2_zero_output_terminal_20260817.json",
    "history/internal_docs/goal5791_portable_source_v2_zero_output_terminal_20260817.md",
    "history/internal_docs/goal5791_portable_source_v3_dual_cpu_gate_successor_authority_20260817.json",
    "history/internal_docs/goal5791_portable_source_v3_dual_cpu_gate_successor_authority_20260817.md",
    "history/internal_docs/goal5791_portable_source_v3_zero_output_terminal_20260817.json",
    "history/internal_docs/goal5791_portable_source_v3_zero_output_terminal_20260817.md",
    "history/internal_docs/goal5791_portable_source_v4_clean_failure_diagnostic_successor_authority_20260817.json",
    "history/internal_docs/goal5791_portable_source_v4_clean_failure_diagnostic_successor_authority_20260817.md",
    "history/internal_docs/goal5791_home_v4_s1_zero_lane_python_environment_failure_20260817.log",
    "history/internal_docs/goal5791_home_v4_s1_zero_lane_python_environment_failure_20260817.json",
    "history/internal_docs/goal5791_home_v4_s1_zero_lane_python_environment_failure_20260817.md",
    "history/internal_docs/goal5791_home_v4_s2_zero_lane_source_cache_directory_failure_20260817.log",
    "history/internal_docs/goal5791_home_v4_s2_zero_lane_source_cache_directory_failure_20260817.json",
    "history/internal_docs/goal5791_home_v4_s2_zero_lane_source_cache_directory_failure_20260817.md",
    "history/internal_docs/goal5791_portable_source_v5_build_receipt_20260817.json",
    "history/internal_docs/goal5791_portable_source_v5_independent_audit_20260817.json",
    "history/internal_docs/goal5791_home_v5_s1_ten_lane_recount_schema_failure_20260817.log",
    "history/internal_docs/goal5791_home_v5_s1_ten_lane_recount_schema_failure_20260817.json",
    "history/internal_docs/goal5791_home_v5_s1_ten_lane_recount_schema_failure_20260817.md",
    "history/internal_docs/goal5791_portable_source_v6_build_receipt_20260817.json",
    "history/internal_docs/goal5791_portable_source_v6_independent_audit_20260817.json",
    "history/internal_docs/goal5791_home_v6_s1_evidence_producer_crossbind_failure_20260817.log",
    "history/internal_docs/goal5791_home_v6_s1_evidence_producer_crossbind_failure_20260817.json",
    "history/internal_docs/goal5791_home_v6_s1_evidence_producer_crossbind_failure_20260817.md",
    "history/internal_docs/goal5791_portable_source_v7_build_receipt_20260817.json",
    "history/internal_docs/goal5791_portable_source_v7_independent_audit_20260817.json",
    "history/internal_docs/goal5791_home_v7_s1_trace_alias_audit_failure_20260817.log",
    "history/internal_docs/goal5791_home_v7_s1_trace_alias_audit_failure_20260817.json",
    "history/internal_docs/goal5791_home_v7_s1_trace_alias_audit_failure_20260817.md",
    "history/internal_docs/goal5791_portable_source_v8_build_receipt_20260817.json",
    "history/internal_docs/goal5791_portable_source_v8_independent_audit_20260817.json",
    "history/internal_docs/goal5791_pre_pod_bundle_v1_zero_output_cpu_timeout_field_classifier_failure_20260817.json",
    "history/internal_docs/goal5791_pre_pod_bundle_v1_zero_output_cpu_timeout_field_classifier_failure_20260817.md",
    "history/internal_docs/goal5791_portable_source_v9_build_receipt_20260817.json",
    "history/internal_docs/goal5791_portable_source_v9_independent_audit_20260817.json",
    "history/internal_docs/goal5791_pre_pod_bundle_v2_build_receipt_20260817.json",
    "history/internal_docs/goal5791_pre_pod_bundle_v2_joint_audit_timeout_field_classifier_failure_20260817.json",
    "history/internal_docs/goal5791_pre_pod_bundle_v2_joint_audit_timeout_field_classifier_failure_20260817.md",
    "history/internal_docs/goal5791_cpu_trace_record_cost_diagnostic_20260818.json",
    "history/internal_docs/goal5791_cpu_trace_record_cost_diagnostic_v1_supersession_20260818.json",
    "history/internal_docs/goal5791_cpu_trace_record_cost_diagnostic_v2_20260818.json",
    "history/internal_docs/goal5791_owner_authority_request_protocol_v2_amendment_20260818.md",
    "history/internal_docs/goal5791_owner_returned_external_review_absorption_20260818.json",
    "history/internal_docs/review_goal5791_post_external_review_pre_pod_readiness_20260817.md",
    "history/internal_docs/call_for_review_goal5791_owner_returned_review_absorption_and_local_successor_freeze_20260818.md",
    "history/internal_docs/goal5791_postreview_cgo_scope_and_fallback_clarification_20260819.md",
    "history/internal_docs/goal5791_project_state_review_absorption_and_cgo_scope_decision_20260819.json",
    "history/internal_docs/review_goal5791_project_state_review_absorption_20260819.md",
    "history/internal_docs/call_for_review_goal5791_project_state_review_absorption_20260819.md",
    "history/internal_docs/goal5791_small_relative_claim_gate_and_diagnostic_host_closure_20260819.md",
    "history/internal_docs/goal5791_small_relative_claim_gate_review_absorption_20260819.json",
    "history/internal_docs/call_for_review_goal5791_small_relative_claim_gate_closure_20260819.md",
    "history/internal_docs/goal5791_cgo_theory_positioning_review_absorption_20260819.json",
    "history/internal_docs/goal5791_assume_guarantee_positioning_and_goal5793_acceptance_challenge_20260819.md",
    "history/internal_docs/goal5791_postreview_portable_v11_successor_authority_20260819.json",
    "history/internal_docs/goal5791_postreview_portable_v11_successor_authority_20260819.md",
    "history/internal_docs/goal5791_postreview_portable_v11_identity_error_terminal_20260819.json",
    "history/internal_docs/goal5791_postreview_portable_v11_identity_error_terminal_20260819.md",
    "history/internal_docs/goal5791_postreview_portable_v12_successor_authority_20260819.json",
    "history/internal_docs/goal5791_postreview_portable_v12_successor_authority_20260819.md",
    "history/internal_docs/goal5791_postreview_portable_v12_clean_import_terminal_20260819.json",
    "history/internal_docs/goal5791_postreview_portable_v12_clean_import_terminal_20260819.md",
    "history/internal_docs/goal5791_postreview_portable_v13_successor_authority_20260819.json",
    "history/internal_docs/goal5791_postreview_portable_v13_successor_authority_20260819.md",
    "history/internal_docs/goal5791_postreview_portable_v13_clean_missing_control_terminal_20260819.json",
    "history/internal_docs/goal5791_postreview_portable_v13_clean_missing_control_terminal_20260819.md",
    "history/internal_docs/goal5791_postreview_portable_v14_successor_authority_20260819.json",
    "history/internal_docs/goal5791_postreview_portable_v14_successor_authority_20260819.md",
    "history/internal_docs/goal5791_stage_a_v1_first_entry_zero_output_terminal_20260820.json",
    "history/internal_docs/goal5791_stage_a_v1_first_entry_zero_output_terminal_20260820.md",
    "history/internal_docs/goal5791_stage_a_v2_upload_receipt_contract_terminal_20260820.json",
    "history/internal_docs/goal5791_stage_a_v2_upload_receipt_contract_terminal_20260820.md",
    "history/internal_docs/goal5791_stage_a_v2_failure_evidence_20260820/UPLOAD_STAGING_OPEN_RECEIPT.json",
    "history/internal_docs/goal5791_stage_a_endpoint_record_v15_successor_authority_20260820.json",
    "history/internal_docs/goal5791_stage_a_endpoint_record_v15_successor_authority_20260820.md",
    "history/internal_docs/goal5791_stage_a_v3_capacity_admission_terminal_20260820.json",
    "history/internal_docs/goal5791_stage_a_v3_capacity_admission_terminal_20260820.md",
    "history/internal_docs/goal5791_stage_a_v3_failure_evidence_20260820/UPLOAD_STAGING_OPEN_RECEIPT.json",
    "history/internal_docs/goal5791_stage_a_v4_wheelhouse_root_directory_terminal_20260820.json",
    "history/internal_docs/goal5791_stage_a_v4_wheelhouse_root_directory_terminal_20260820.md",
    "history/internal_docs/goal5791_stage_a_v4_failure_evidence_20260820/PARTIAL_UPLOAD_STAGING_OPEN_RECEIPT.json",
    "history/internal_docs/goal5791_stage_a_archive_root_v16_successor_authority_20260820.json",
    "history/internal_docs/goal5791_stage_a_archive_root_v16_successor_authority_20260820.md",
    "history/internal_docs/goal5791_stage_a_archive_root_v16_final_successor_authority_20260820.json",
    "history/internal_docs/goal5791_stage_a_archive_root_v16_final_successor_authority_20260820.md",
    "history/internal_docs/goal5791_stage_a_v5_dependency_identity_terminal_20260820.json",
    "history/internal_docs/goal5791_stage_a_v5_dependency_identity_terminal_20260820.md",
    "history/internal_docs/goal5791_wheelhouse_v4_dependency_identity_successor_authority_20260820.json",
    "history/internal_docs/goal5791_wheelhouse_v4_dependency_identity_successor_authority_20260820.md",
    "history/internal_docs/goal5791_stage_a_v6_missing_strace_terminal_20260820.json",
    "history/internal_docs/goal5791_stage_a_v6_missing_strace_terminal_20260820.md",
    "history/internal_docs/goal5791_stage_a_v7_postupload_capacity_terminal_20260820.json",
    "history/internal_docs/goal5791_stage_a_v7_postupload_capacity_terminal_20260820.md",
    "history/internal_docs/goal5791_stage_a_v7_failure_evidence_20260820/UPLOAD_STAGING_OPEN_RECEIPT.json",
    "history/internal_docs/goal5791_stage_a_v8_target_producer_observation_terminal_20260820.json",
    "history/internal_docs/goal5791_stage_a_v8_target_producer_observation_terminal_20260820.md",
    "history/internal_docs/goal5791_stage_a_v8_failure_evidence_20260820/TARGET_PTX_PRODUCER_OBSERVATION.json",
    "history/internal_docs/goal5791_portable_source_v17_build_receipt_20260820.json",
    "history/internal_docs/goal5791_portable_source_v17_independent_audit_20260820.json",
    "history/internal_docs/goal5791_stage_a_producer_identity_v18_successor_authority_20260820.json",
    "history/internal_docs/goal5791_stage_a_producer_identity_v18_successor_authority_20260820.md",
    "history/internal_docs/goal5791_stage_a_v9_first_entry_command_serialization_terminal_20260820.json",
    "history/internal_docs/goal5791_stage_a_v9_first_entry_command_serialization_terminal_20260820.md",
    "history/internal_docs/goal5791_stage_a_v10_target_binding_exact_keys_terminal_20260820.json",
    "history/internal_docs/goal5791_stage_a_v10_target_binding_exact_keys_terminal_20260820.md",
    "history/internal_docs/goal5791_portable_source_v18_build_receipt_20260820.json",
    "history/internal_docs/goal5791_portable_source_v18_independent_audit_20260820.json",
    "history/internal_docs/goal5791_stage_a_handoff_schema_v19_successor_authority_20260820.json",
    "history/internal_docs/goal5791_stage_a_handoff_schema_v19_successor_authority_20260820.md",
    "history/internal_docs/goal5791_portable_source_v19_zero_output_interpreter_preflight_terminal_20260820.json",
    "history/internal_docs/goal5791_portable_source_v19_zero_output_interpreter_preflight_terminal_20260820.md",
    "history/internal_docs/goal5791_portable_source_v20_bundled_interpreter_successor_authority_20260820.json",
    "history/internal_docs/goal5791_portable_source_v20_bundled_interpreter_successor_authority_20260820.md",
    "history/internal_docs/goal5791_portable_source_v20_build_receipt_20260820.json",
    "history/internal_docs/goal5791_portable_source_v20_independent_audit_20260820.json",
    "history/internal_docs/goal5791_home_v20_qualification_20260820/RESULT.json",
    "history/internal_docs/goal5791_home_v20_qualification_20260820/FUNCTIONAL_RECOUNT.json",
    "history/internal_docs/goal5791_home_v20_qualification_20260820/HOME_EVIDENCE_INDEPENDENT_AUDIT.json",
    "history/internal_docs/goal5791_home_v20_qualification_20260820/HOME_EVIDENCE_LOCAL_INDEPENDENT_AUDIT.json",
    "history/internal_docs/goal5791_pre_pod_bundle_v9_build_receipt_20260820.json",
    "history/internal_docs/goal5791_pre_pod_bundle_v9_independent_audit_20260820.json",
    "history/internal_docs/goal5791_owner_stage_a_request_v11_20260820.json",
    "history/internal_docs/goal5791_owner_stage_a_authority_v11_20260820.json",
    "history/internal_docs/goal5791_stage_a_v11_empty_numba_cache_directory_terminal_20260820.json",
    "history/internal_docs/goal5791_stage_a_v11_empty_numba_cache_directory_terminal_20260820.md",
    "history/internal_docs/goal5791_portable_source_v21_numba_cache_isolation_successor_authority_20260820.json",
    "history/internal_docs/goal5791_portable_source_v21_numba_cache_isolation_successor_authority_20260820.md",
    "history/internal_docs/goal5791_formal_v1_worker1_numba_source_mutation_terminal_20260820.json",
    "history/internal_docs/goal5791_formal_v1_worker1_numba_source_mutation_terminal_20260820.md",
    "history/internal_docs/goal5791_portable_source_v22_formal_worker_dual_cache_successor_authority_20260820.json",
    "history/internal_docs/goal5791_portable_source_v22_formal_worker_dual_cache_successor_authority_20260820.md",
    "history/internal_docs/goal5791_portable_source_v22_zero_output_historical_contract_assertion_terminal_20260820.json",
    "history/internal_docs/goal5791_portable_source_v22_zero_output_historical_contract_assertion_terminal_20260820.md",
    "history/internal_docs/goal5791_portable_source_v23_historical_contract_assertion_successor_authority_20260820.json",
    "history/internal_docs/goal5791_portable_source_v23_historical_contract_assertion_successor_authority_20260820.md",
    "history/internal_docs/goal5791_pre_pod_bundle_v11_manifest_contract_pin_terminal_20260820.json",
    "history/internal_docs/goal5791_pre_pod_bundle_v11_manifest_contract_pin_terminal_20260820.md",
    "history/internal_docs/goal5791_portable_source_v24_auditor_contract_pin_successor_authority_20260820.json",
    "history/internal_docs/goal5791_portable_source_v24_auditor_contract_pin_successor_authority_20260820.md",
    "history/internal_docs/goal5791_append_only_record_reference_correction_authority_20260820.json",
    "history/internal_docs/goal5791_append_only_record_reference_correction_authority_20260820.md",
    "history/internal_docs/goal5791_paper_outcome_consequence_selection_successor_authority_20260820.json",
    "history/internal_docs/goal5791_paper_outcome_consequence_selection_successor_authority_20260820.md",
    "history/internal_docs/goal5791_portable_source_v25_support_chain_auditor_terminal_20260820.json",
    "history/internal_docs/goal5791_portable_source_v25_support_chain_auditor_terminal_20260820.md",
    "history/internal_docs/reviewer_project_state_and_remaining_work_to_cgo_20260817.md",
    "history/internal_docs/goal5792_unknown_lane_classification_work_authority_20260819.json",
    "history/internal_docs/v4_competitive_cgo_submission_work_plan_after_goal5788_20260816.md",
    "history/internal_docs/self_review_goal5791_amendment_a1_pretimer_fusion_execution_token_20260817.md",
)
EXPECTED_OVERLAY_SHA256: Mapping[str, str] = {
    "src/rtdsl/v4_operation_evidence.py": "ff59cba24c7ae188e9f99c3a29a968e0ea83e465033084e81665ee3eff129026",
    "src/rtdsl/v4_triangle_reduction_device_runtime.py": "d045c9ce04e5b77bbb7785191cdd07d7430de97e7ffdd4f5e0c3a60937b6ba00",
    "scripts/goal5791_build_owner_authority.py": "0d1e27290a0ae1908e5e9eb088aa5e4161039eb4d9ced97be68c0b7e07ecf153",
    "scripts/goal5791_build_pre_pod_bundle.py": "a456d5e527218edc5f46b353149667482073101c397e3fa30a97521117c26f95",
    "scripts/goal5791_build_pretarget_authority.py": "26e8739d953e9b585fcb36420fbad5308ec450c0f29e06341f259e4ecc31f29b",
    "scripts/goal5791_cpu_test_gate.py": "40e627b21bf6fc602442b63cad23e6fae98370a997531a1d4efeb7f89500dd2a",
    "scripts/goal5791_formal_contract.py": "aa1a7189a9afc667d6fc9e5e6088e1f6aa262dabb91325177db3e35b5bb4284c",
    "scripts/goal5791_formal_controller.py": "e2307b8bdb432688637aef6ea06425ba8df1369a3ec43d5837dae006e3bca068",
    "scripts/goal5791_formal_evaluate.py": "b5d545762f79adc8f6844f770f55f2d87e9b7bf953ee3d5ebbf986200010f4af",
    "scripts/goal5791_formal_independent_recount.py": "43d3be5bff769728c2492c808e05a943f6473bca940a39d023f0bf9d585be60c",
    "scripts/goal5791_formal_worker.py": "70d8623047d9f0d82229908cf71d78731a907a29a11b69292f9efbd71140c41b",
    "scripts/goal5791_home_clean_validate.py": "892a84f9695db24aa1078d463de10a18d8a996dd245376aebf524334cae5b5aa",
    "scripts/goal5791_home_token_validation.py": "7fd3c00b4510d29933a0e1b54cba2591ef8b1443e7160f7730d3643cc8daa7a3",
    "scripts/goal5791_independent_home_recount.py": "7928389e0b0a33d95f575093c83141e870cd3a3be10dea623c32a9de768359c9",
    "scripts/goal5791_independent_portable_audit.py": "04e75cb2040e4ba33ebb9956538fda6d7e13a4c5771c38be4c47acb66cce6f60",
    "scripts/goal5791_open_upload_staging.py": "e78d8406f9b4b74ff7a460b0a8b88408e300fff88d4f9442a4206edfbe55de47",
    "scripts/goal5791_segment_descriptors.py": "0fbdbf9d5f8a85eb6ce1308336df3fb192b0eb146abf68907c7cd0580cd4577d",
    "scripts/goal5791_target_prepare.py": "3dd3ac1121df95b2853d07e97a75b16464ec8471e67a366d632f75184ee5c1ce",
    "scripts/goal5791_target_producer_probe.py": "a6b91e66c3d06e947bb86d43bdfeb5478e9b803691d9b6380855244179a0c2e0",
    "scripts/goal5791_target_token_smoke.py": "4d11e0edcee96dde1db54600e64937978bab1c254b0f99d38a2ebf4d93c7ab5d",
    "scripts/goal5791_trace_record_cost_diagnostic.py": "57635bafa0ae0649ff21c4f08ff0c2040f04856cbcb3dd56d32a9fdf64437fc2",
    "tests/goal5791_data_oracle_authority_test.py": "7246fffa0ada39a96753f116409af5cd5f1995ed4a102760fae85fbe219f4951",
    "tests/goal5791_formal_contract_test.py": "87a5148f70c3f86820a4f7380c25cb72a713fe6b55a898f3b6ee9e31302c2ebd",
    "tests/goal5791_formal_evaluator_recount_test.py": "c458c5646ddef1e85bc6e9e0e068b80c5a8ce153b9926c330fcd989264490ad7",
    "tests/goal5791_formal_worker_controller_test.py": "10cbd594116e888062594b2a307ed5bc1e404784f38572975dff8fb4556beede",
    "tests/goal5791_portable_home_harness_test.py": "a6c86d416948a59a2240d18b48086b6f0328abcb18cef8ccac7269cb7c7a44ad",
    "tests/goal5791_pre_pod_base_budget_audit_test.py": "214f7c9bd2d38e849895cc28d97fa51715d745446754f8b2b214957cbd9b7e7e",
    "tests/goal5791_pre_worker_zero_claim_freeze_test.py": "5c0247e11ae4e8c03781eab718e45e3230f9e6f58b7cf3f93e8d895f90c8bdeb",
    "tests/goal5791_pretimer_execution_token_amendment_test.py": "f87c9b82f442c077080ae4bab33c377c5bffce86732a5096b41b18492643ef5e",
    "tests/goal5791_segment_descriptors_test.py": "f03839244a4a809e7d9c7325961b902b44ef9e2fcd65dd80c46301316325457a",
    "tests/goal5791_successor_source_authority_test.py": "eb121c377fad86f4c16b2680022131e9c283a49a67cb52588b7a671ec3009862",
    "tests/goal5791_verified_fusion_execution_token_test.py": "6e5ffd30dacf7433c6a5c34690fb32c2648f333f3a12c52e4a432147ecb14e3c",
    "history/internal_docs/goal5790_a1_owner_returned_external_review_absorption_20260817.json": "e830a626689cc362c8223c70544e28bf97d0aa00086727b901cdcb54677f91eb",
    "history/internal_docs/goal5790_a1_postreview_claim_clarification_20260817.md": "9fc25d0b5bb0bf81551a119066b6c0913178d0c56da54747212677354a92cbff",
    "history/internal_docs/goal5790_a1_home_rejected_program_suite_result_20260816.json": "800707087dcabfd677eff41062215cde22eca94f0d5102ab637eece815160dcf",
    "history/internal_docs/goal5790_home_functional_closure_result_20260816.json": "dfb1190b4c8880f41dcc5bb7c4c8583a9ff7a6eb1e197e711512020c8c89c20a",
    "history/internal_docs/goal5790_same_source_same_cohort_fusion_ablation_technical_report_20260816.md": "bd2954a8ca0460c422dd2a0233f5eb5de0bee9c89693a6ce6edc30ccc65b9868",
    "history/internal_docs/review_goal5790_a1_home_rejected_program_suite_20260816.md": "778c996516c85ab185c8e3be23132794348827ad13f54d774e402fc42f09e9d9",
    "history/internal_docs/goal5791_amendment_a1_pretimer_fusion_execution_token_result_20260817.json": "8d3318461956673417d1a57fb57d66d710ca0e96a49769cbbbe47112f7522b66",
    "history/internal_docs/goal5791_amendment_a1_pretimer_fusion_execution_token_technical_report_20260817.md": "711d0317487951bda5f2cdef59b674855546b0fa0f65b6aa9c3feb56b5769838",
    "history/internal_docs/goal5791_amendment_a2_segment_plan_input_token_binding_result_20260817.json": "60e7fcbdc2ca7b817b76dcd75e283abc0db5b0ac77e59cfede99cb2295a47cfe",
    "history/internal_docs/goal5791_amendment_a2_segment_plan_input_token_binding_technical_report_20260817.md": "2efb890032c8186e6e8a082c2888c5bc640d40519f529310e4c742c965e9b62a",
    "history/internal_docs/goal5791_frozen_triangle_data_and_oracle_authority_20260817.json": "b89496b22266c7953ae5608d998ed395cdde5f5bf0ae2f17ff34a37a8b7df181",
    "history/internal_docs/goal5791_owner_authority_request_protocol_20260817.md": "692ebc743f32245f413329167fe05999f61c0b19c9db2a5f7a745e63dd229a1c",
    "history/internal_docs/goal5791_pre_pod_conservative_runtime_budget_20260817.json": "e1510b9f5f1f22ce213d023828f10561dea6132369ef88e4484288293f439fc5",
    "history/internal_docs/goal5791_pre_pod_portable_base_and_bundle_audit_20260817.json": "38eb0cc50367e65309aab85e8df1b9f9cf28d1922af7e04df5856207d92e0767",
    "history/internal_docs/goal5791_pre_pod_portable_base_and_bundle_audit_20260817.md": "270099233d8349e345540c7d061ae54d0b194d3bc752cfd3393ff4af3b1c937b",
    "history/internal_docs/goal5791_pre_worker_zero_related_work_and_claim_freeze_20260817.json": "4851d3911c1bd124b041b7f656764b4521fc543963f3124625bd1ffae02c54f6",
    "history/internal_docs/goal5791_pre_worker_zero_related_work_and_claim_freeze_20260817.md": "8d8cf5fb3d2d41385e0d4176ff4864b4a3779e63d1db68e9ae0049f12e4b23bc",
    "history/internal_docs/goal5791_preregistration_20260817.json": "40ff35a33ec5598fb22a094fbe2f2fc32e17caabef8923e721e7e1cd6a34bf02",
    "history/internal_docs/goal5791_preregistration_v2_20260817.json": "39be7d1d9fa1dc05efcc3452bdabfe08452251a8e38aea24c3c5fbb00f6ed530",
    "history/internal_docs/goal5791_preregistration_v3_20260817.json": "03a031afbcc6c532a666b7fdc6e426a0a1c66b15d2e5c6abf52b8adf3ef65e86",
    "history/internal_docs/goal5791_preregistration_v4_20260817.json": "af7a099ef15b239d3933a0ac63720ef8f47e3799401881f4407e309be2f42a10",
    "history/internal_docs/goal5791_preregistration_v5_20260818.json": "9368a5eea36d3f7b2f0d149f6c455c4633ae940703310b832fca1101abcb3ce4",
    "history/internal_docs/goal5791_preregistration_v6_20260819.json": "83834d7d4f785fb9ce86f7cbe4d7c12308f6f95a9687cc39408b0d65da5b36ed",
    "history/internal_docs/goal5791_preregistration_v7_20260819.json": "b434f864f11af545a420b4984b7066f54d17d2fd5d4fe8f6cfc0e7ac2fe83cb1",
    "history/internal_docs/goal5791_preregistration_v8_20260820.json": "b53da728fc73a2bcec680bb8be388cfc58fe8bf1ca136915ad2cada3aa61953f",
    "history/internal_docs/goal5791_preregistration_v9_20260820.json": "4878e666695e513e47c2adad65869a1cde2640396b6afdcbcd1f493e8cc1495a",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_20260817.json": "650ca15d5687cd0124302e9c8626e19560b5240afec25628f2fc62a2cb4c5738",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v2_20260817.json": "05d0bf2b93d3dbf12355f6115c25b3dadba75de291e1362410d88a53ff28dab7",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v3_20260817.json": "2ea28b4b4ebdf28d69a99dff29e402188e9b7ec12d9ca5b4553d08c6d37ee4ad",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v4_20260817.json": "2ccd1decc818fbef9a464febeb26cdd0aa1ea12bb8e0266ab9836d0ce4d8a0ac",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v5_20260818.json": "8c82a57b8a8a65ca7dad23ea18d4970c0bf05c67f85a23651233e8e4c2a771d5",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v6_20260819.json": "9444e609ae3ae8e78d2160fa5b8db67163743f5e4d661cfbbef1c8d2e1afeb4b",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v7_20260819.json": "8718865c3e09d11f0273b5c83b50c14a1db1ee7b94c5495b41b3d9aa31b53807",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v8_20260820.json": "27873208bc7b34c62781286b79ac3d5497a305645fb404aa861b35b5a061449f",
    "history/internal_docs/goal5791_pretarget_preexecution_authority_v9_20260820.json": "46fdb549f8397b361871a8dc1d5a6e7d6995903c9e0f1ba60ed2a7804ff0cfc1",
    "history/internal_docs/goal5791_successor_source_authority_20260817.json": "1382ecb3531f642822dac7d477b1034938abb9d665533ce7f44de424cef66965",
    "history/internal_docs/goal5791_successor_source_authority_v2_20260817.json": "d0366794d255e188bb1ad671ea0675f75a36f3ae4b752a377f56dfd45a298fb8",
    "history/internal_docs/goal5791_v3_prereg_pretarget_terminal_supersession_20260817.md": "d7940ad5b60661e0fb138e13fcb093b10ec65fc0e0e30913c879ca61a4f4161c",
    "history/internal_docs/goal5791_v3_prereg_pretarget_terminal_supersession_authority_20260817.json": "37b669dc4333999ebf74b5471a2eca5595f8bec08e73aa7fc18d85c4b86416cc",
    "history/internal_docs/goal5791_v4_successor_lineage_authority_20260817.json": "2be98a59f1fdd95014fc93af14959ccf10d1886bccfed450458f47453bb340a7",
    "history/internal_docs/goal5791_portable_source_v1_zero_output_terminal_20260817.json": "6894ccb2955c013c4cbb986da4f43134402248b7062b47bdf04672951b8f652b",
    "history/internal_docs/goal5791_portable_source_v1_zero_output_terminal_20260817.md": "fd8ab28035a56e65de0d6b6edfba11f36c30116e75b34fbff1fc0fc351179e2b",
    "history/internal_docs/goal5791_portable_source_v2_zero_output_terminal_20260817.json": "95fbc322050cc89ce1b7a8d96e1c8c09959930f36d648d03af63d491e8bd2762",
    "history/internal_docs/goal5791_portable_source_v2_zero_output_terminal_20260817.md": "a36cdaa27eb18443a9c2fc7f73aa5579bd0a5d1054a788f709007bc271af941d",
    "history/internal_docs/goal5791_portable_source_v3_dual_cpu_gate_successor_authority_20260817.json": "923d1a07700d6e218a0ecba3d40b7ee5ed537c9a99370fbe79a5fa9e6e90eac2",
    "history/internal_docs/goal5791_portable_source_v3_dual_cpu_gate_successor_authority_20260817.md": "1e1071bb5b2bc487e7d2ca115046f36b3ce331c167a46bcad17a5436f4e11c79",
    "history/internal_docs/goal5791_portable_source_v3_zero_output_terminal_20260817.json": "b8d160a0299c34fb8f00b737b2865b6394c05a29eacf224c996c696128ce9538",
    "history/internal_docs/goal5791_portable_source_v3_zero_output_terminal_20260817.md": "537d4e0e00727f38b82d5640044df0583e16e7ed2f5aeb994d8c44abe4446ac8",
    "history/internal_docs/goal5791_portable_source_v4_clean_failure_diagnostic_successor_authority_20260817.json": "d0e0db723c47f6c43502d790cf52a097da060b7e6ae57d1473404f9e0a91fab6",
    "history/internal_docs/goal5791_portable_source_v4_clean_failure_diagnostic_successor_authority_20260817.md": "d8949d25bc6592e82431a89957c88a675ca1a8c957bec8455208d2dc6568f188",
    "history/internal_docs/goal5791_home_v4_s1_zero_lane_python_environment_failure_20260817.log": "27334ac5173ce212adf7133419344b9293ad216a4c1767859c60da15f7dd233f",
    "history/internal_docs/goal5791_home_v4_s1_zero_lane_python_environment_failure_20260817.json": "0426b4ac964cf1b46654a878cff9083a33995ab098ccc2cbac25e79b8055cc89",
    "history/internal_docs/goal5791_home_v4_s1_zero_lane_python_environment_failure_20260817.md": "11f28d447b70b66897f2e81200a52f4e790626faca1464018d07fa3e5d93fe50",
    "history/internal_docs/goal5791_home_v4_s2_zero_lane_source_cache_directory_failure_20260817.log": "1e6d04f9c26294da157f50d1dd8b8edad739b8e6d3e3517d9760aa220eb1bd3b",
    "history/internal_docs/goal5791_home_v4_s2_zero_lane_source_cache_directory_failure_20260817.json": "7c4f19fd9fae3f3de692f020ac6903f5a62c210204503d09cc2864540cdaf046",
    "history/internal_docs/goal5791_home_v4_s2_zero_lane_source_cache_directory_failure_20260817.md": "9adf1855c84348866ddadbd4d9e130b31c6baac498d7e02d670d546239d910ff",
    "history/internal_docs/goal5791_portable_source_v5_build_receipt_20260817.json": "21609d38d817b3b5a2de786e419327b26ddaf803b91c295074877b8189412180",
    "history/internal_docs/goal5791_portable_source_v5_independent_audit_20260817.json": "e96896e78d1fe0cc0097b517eb5b5249bb65abae37a7ad6aa55297ba4ce509d5",
    "history/internal_docs/goal5791_home_v5_s1_ten_lane_recount_schema_failure_20260817.log": "a408cffe89a21e0facf91d6aa8bfe2b7d911519213027f313897e7da610b9fb3",
    "history/internal_docs/goal5791_home_v5_s1_ten_lane_recount_schema_failure_20260817.json": "086e8e77aa2f66b2b214b31124097223bf808ec166d074e4243ea286c63632fc",
    "history/internal_docs/goal5791_home_v5_s1_ten_lane_recount_schema_failure_20260817.md": "5f12dd5d58951a4973025729cac3fe624fa494a1f9fa210028c48ec24a9371f3",
    "history/internal_docs/goal5791_portable_source_v6_build_receipt_20260817.json": "ec2b81211ba3eb027f7a0bdc5dfeb4b212d529653e0e6eeb52187465ebbba4a6",
    "history/internal_docs/goal5791_portable_source_v6_independent_audit_20260817.json": "9a791b48ef1b801cede9385f13835c032f149281ed40425af0b6fa9f1eb46942",
    "history/internal_docs/goal5791_home_v6_s1_evidence_producer_crossbind_failure_20260817.log": "5d2c5da543f295a503ad790c7193ee40a2ee0a88fb2c04bd09dd7415d25b42eb",
    "history/internal_docs/goal5791_home_v6_s1_evidence_producer_crossbind_failure_20260817.json": "218605c5cf95db44627042dd5d356f8efea0a2686f4132cfd573e8bf4a5a9747",
    "history/internal_docs/goal5791_home_v6_s1_evidence_producer_crossbind_failure_20260817.md": "ddd1c8073d0445aa93beb8d5afd657afa760aaf3fdaa4a2909c218a30cd12a14",
    "history/internal_docs/goal5791_portable_source_v7_build_receipt_20260817.json": "7c64510078b449e25335c675af6eff5f76632cdc845fd4c255720a6040227188",
    "history/internal_docs/goal5791_portable_source_v7_independent_audit_20260817.json": "0a47ccc2137ce822dffca851ddcabc06d26abb846a503e9a082236fe9c579c65",
    "history/internal_docs/goal5791_home_v7_s1_trace_alias_audit_failure_20260817.log": "c417b9e0214cbd507d4424680589c41e0cbd69a7ae2cc59bf61cedc6b82c7425",
    "history/internal_docs/goal5791_home_v7_s1_trace_alias_audit_failure_20260817.json": "205d0b67ffd470c3e7eeb1f51ff49aa01cda809925c513985023d2289e666dbc",
    "history/internal_docs/goal5791_home_v7_s1_trace_alias_audit_failure_20260817.md": "11dfcb4f092801afb0deb68f7332c3b6e88dfecf55eb0aa7613be93c01f5a868",
    "history/internal_docs/goal5791_portable_source_v8_build_receipt_20260817.json": "15f157ceb501bc8554e959b9f694841795235da78e77955d4e606b84a48f2e59",
    "history/internal_docs/goal5791_portable_source_v8_independent_audit_20260817.json": "770c97a03bef120e339ddb69a483af23209210306cb9d12fa08a38a77e63383a",
    "history/internal_docs/goal5791_pre_pod_bundle_v1_zero_output_cpu_timeout_field_classifier_failure_20260817.json": "2d54ed93a235e10894b2015765733b9611624efbc50cb3680af27e8768d0eb9b",
    "history/internal_docs/goal5791_pre_pod_bundle_v1_zero_output_cpu_timeout_field_classifier_failure_20260817.md": "0d02e7b3ad00aef1807480eb9967dddadf6298b8b6f8c47c40ef6eec327cb0e6",
    "history/internal_docs/goal5791_portable_source_v9_build_receipt_20260817.json": "b5b9f00b907f307ca9c301897f451e71908e7b27f76218f48767c9230c16c4e3",
    "history/internal_docs/goal5791_portable_source_v9_independent_audit_20260817.json": "c6ebc5e638235f23a4dfe6eca6314e801f4bdc6f96337c2cd6108392e82811b0",
    "history/internal_docs/goal5791_pre_pod_bundle_v2_build_receipt_20260817.json": "9e8fa8878fb2bbfed36eb4fb4103144cacf9384c5c02fcef04c25ea56b61f07d",
    "history/internal_docs/goal5791_pre_pod_bundle_v2_joint_audit_timeout_field_classifier_failure_20260817.json": "468bd9c42427d7610dfc9920b03109b868d84c92bad1c711b8e495c208f07086",
    "history/internal_docs/goal5791_pre_pod_bundle_v2_joint_audit_timeout_field_classifier_failure_20260817.md": "67cc0c3dd8d56a9511d738467f4e11fdff393a929833c2c8807af0e08e611d27",
    "history/internal_docs/goal5791_cpu_trace_record_cost_diagnostic_20260818.json": "f6ca8119200c5fcbf9887f2a2ba07f8cc2dfd9c54ca178b1dc2a6474d8a72b54",
    "history/internal_docs/goal5791_cpu_trace_record_cost_diagnostic_v1_supersession_20260818.json": "31d05023966a929596264ec80c5a0315c3d63baf1425876c947340da576a5567",
    "history/internal_docs/goal5791_cpu_trace_record_cost_diagnostic_v2_20260818.json": "8a5d5924b54e0746a1ff83fa92d94c5977764b1b49fde8ac06790365f25436a2",
    "history/internal_docs/goal5791_owner_authority_request_protocol_v2_amendment_20260818.md": "3de2c2fd10898cb3c64ee043f644752a8e40123d526e6f02c773d1dfcd2fbcdd",
    "history/internal_docs/goal5791_owner_returned_external_review_absorption_20260818.json": "31f89ae6d60f53823c2d04398f014b73d76259bd2b464e58d7de564b8f97bc5c",
    "history/internal_docs/review_goal5791_post_external_review_pre_pod_readiness_20260817.md": "331212c140cd67e6eb5ba8b3bf71946b983f0d7b9b54e475be6b185ad06fc502",
    "history/internal_docs/call_for_review_goal5791_owner_returned_review_absorption_and_local_successor_freeze_20260818.md": "b9dcfa4041cfaddf99c00443c0790657deca270d5acbfd0efd0e300138ec18e5",
    "history/internal_docs/goal5791_postreview_cgo_scope_and_fallback_clarification_20260819.md": "7cd8424bb4de07935cca2b8fab889c803a1f44af3fe0886b8ab0e28cf29ae2e9",
    "history/internal_docs/goal5791_project_state_review_absorption_and_cgo_scope_decision_20260819.json": "471018936b4cdcbadd18ab9d58a826c0b18b5c5a2c2f355a5e58f7e7fdf2b3db",
    "history/internal_docs/review_goal5791_project_state_review_absorption_20260819.md": "1b0e8a4d66373f4bef2f05c9ba4344759b54e153f087fb65bb2ca02346d8c2b0",
    "history/internal_docs/call_for_review_goal5791_project_state_review_absorption_20260819.md": "7374e26bc689330dca8e3168e185732bdb960539edfd6dffa166bbfb4de755af",
    "history/internal_docs/goal5791_small_relative_claim_gate_and_diagnostic_host_closure_20260819.md": "f045e824e7abeef121e88d147876e4105d8e7e570360f9ec3360aba5c92510a5",
    "history/internal_docs/goal5791_small_relative_claim_gate_review_absorption_20260819.json": "f8d68cb07821bf1c85c9ff375b9f70c560b5612d136b5bb6de5562321662ffee",
    "history/internal_docs/call_for_review_goal5791_small_relative_claim_gate_closure_20260819.md": "c0e560798639cb9abb50b136ec8448d770bbdbf4433596917e611709e3dc172c",
    "history/internal_docs/goal5791_cgo_theory_positioning_review_absorption_20260819.json": "f99cbf22646d0ec8893ea694459cdcf66ab4e8e9b8cd217d43b095d3cdc3b92a",
    "history/internal_docs/goal5791_assume_guarantee_positioning_and_goal5793_acceptance_challenge_20260819.md": "672fdb360bd0881c8003143b46847f053c8ebdec65f70d49d473433cdab7681e",
    "history/internal_docs/goal5791_postreview_portable_v11_successor_authority_20260819.json": "b24ab821fc899f55c1d73cb0c4aa3a5a08d259a8a7c6eb04217a9f2f1fd1c0fc",
    "history/internal_docs/goal5791_postreview_portable_v11_successor_authority_20260819.md": "fceeb990155c1927664410620f06ae66fa929ff33ad50d826f11686fa47193a6",
    "history/internal_docs/goal5791_postreview_portable_v11_identity_error_terminal_20260819.json": "222ea1cd7c226023f6050267f881ad1d78902cd23bcb44bdce97386d1389266d",
    "history/internal_docs/goal5791_postreview_portable_v11_identity_error_terminal_20260819.md": "3bf5b8fa8d39bd18b668d86638dbc037024705838c0e7d253da931894ed14ab8",
    "history/internal_docs/goal5791_postreview_portable_v12_successor_authority_20260819.json": "f81dc7a2286663109eceb20371b95c6f212aa57af768fc2ae162615743f584bf",
    "history/internal_docs/goal5791_postreview_portable_v12_successor_authority_20260819.md": "85e975eb0ba201b678bec04f78381f5ae4583cd885b08d1f7df49c520034d148",
    "history/internal_docs/goal5791_postreview_portable_v12_clean_import_terminal_20260819.json": "5df6d8883f054dbaed85bd460c431d5f4447c85f430ef94a4f5d4e09755deb8e",
    "history/internal_docs/goal5791_postreview_portable_v12_clean_import_terminal_20260819.md": "3c130247ecfd082edd32f412528cd0392cf9d455761246a4a6b2312c6035dcfd",
    "history/internal_docs/goal5791_postreview_portable_v13_successor_authority_20260819.json": "dfffdad5e9141f9dec258f0e739d073f90ad7bce7e0a565956f9d8536fc03b73",
    "history/internal_docs/goal5791_postreview_portable_v13_successor_authority_20260819.md": "e8054eb5ab99ae83247b7e3efb72a29a29f213fec6fee7f71ac3a7431fbedaf4",
    "history/internal_docs/goal5791_postreview_portable_v13_clean_missing_control_terminal_20260819.json": "ecc21c39d1c9b95d44cc076fac22febe5d32a94244748ba45c2b496011afb410",
    "history/internal_docs/goal5791_postreview_portable_v13_clean_missing_control_terminal_20260819.md": "80ed950f67394c964e8625f909b3d9e5d92941478ced0e53e087b4cd152646d3",
    "history/internal_docs/goal5791_postreview_portable_v14_successor_authority_20260819.json": "6a20c6b5d2a750b46c46e13ff994bb4e528c8a1356ca0e2ec474cb6a45285b65",
    "history/internal_docs/goal5791_postreview_portable_v14_successor_authority_20260819.md": "b7e555a2977f619d1c2609728601d5fee82f0c5597e93f88f56a744c45880c0a",
    "history/internal_docs/goal5791_stage_a_v1_first_entry_zero_output_terminal_20260820.json": "ef9eff34cd3db91eac216e97880c22332d0ce394ca2707464f2ab755dbd9b364",
    "history/internal_docs/goal5791_stage_a_v1_first_entry_zero_output_terminal_20260820.md": "44716628a521b2f48d01c8ca8fa815c35d296240f28eb12bd600ad3b0d40b060",
    "history/internal_docs/goal5791_stage_a_v2_upload_receipt_contract_terminal_20260820.json": "d6e416a4c524b16739358a14f773143dc1aba1ef9b8de6292f05515942e33260",
    "history/internal_docs/goal5791_stage_a_v2_upload_receipt_contract_terminal_20260820.md": "0547679219fc74b43bf1cc63a52842682524c00753eaeb07e06d314ec6991a07",
    "history/internal_docs/goal5791_stage_a_v2_failure_evidence_20260820/UPLOAD_STAGING_OPEN_RECEIPT.json": "c564a0316728356c8331441e0537d6539e12d7d242ae82258e7ad7cd9e6959cc",
    "history/internal_docs/goal5791_stage_a_endpoint_record_v15_successor_authority_20260820.json": "29bea2bc28942d5e3040db58a4bd3b6ba2507058a55d4adb0d2279082f33f938",
    "history/internal_docs/goal5791_stage_a_endpoint_record_v15_successor_authority_20260820.md": "372da96b6626366dfeda2d5aaee49869266981e4c53d880aac0ea558cccce46e",
    "history/internal_docs/goal5791_stage_a_v3_capacity_admission_terminal_20260820.json": "eed3a899f14389e78c83bc2f04140912695ab0b771220878aba5ee1d7718fdf4",
    "history/internal_docs/goal5791_stage_a_v3_capacity_admission_terminal_20260820.md": "1cc5988773110f894723b8dde142cd9dedf231117aa0c986e2e253fbd38100d4",
    "history/internal_docs/goal5791_stage_a_v3_failure_evidence_20260820/UPLOAD_STAGING_OPEN_RECEIPT.json": "50f18f96275b2e8ec8e6624614d01ab47f1281ae7115eee84fac420fbbd8e55a",
    "history/internal_docs/goal5791_stage_a_v4_wheelhouse_root_directory_terminal_20260820.json": "1590233d646f46ca50db905e975317ea6c327850d1aae8c9d3059a9753395796",
    "history/internal_docs/goal5791_stage_a_v4_wheelhouse_root_directory_terminal_20260820.md": "0ef79f3f757fb2f044bd08b959ae09bfa05856139da2be47f830b8b215bbb829",
    "history/internal_docs/goal5791_stage_a_v4_failure_evidence_20260820/PARTIAL_UPLOAD_STAGING_OPEN_RECEIPT.json": "b6e62490cc7baa58e38c46f5920f0c19cbc157f87fcbb402260c102cab4f001a",
    "history/internal_docs/goal5791_stage_a_archive_root_v16_successor_authority_20260820.json": "9ff7f0f3dfa3b3d71df3c08d974fb658db56e402fd2a2ec43019381c3e78395c",
    "history/internal_docs/goal5791_stage_a_archive_root_v16_successor_authority_20260820.md": "670d51bf6c6dad36fdc941e43c080d23e900fbf3344b87a205eef6d65601f213",
    "history/internal_docs/goal5791_stage_a_archive_root_v16_final_successor_authority_20260820.json": "9cf2b12866839d4ee52cc192e9e6cdea1f9c19c252cdf3fbcf28d74a03667abf",
    "history/internal_docs/goal5791_stage_a_archive_root_v16_final_successor_authority_20260820.md": "98820bb60de127ea82b78a7ac56302a82d51127cbd19995e4a7f663401daeea5",
    "history/internal_docs/goal5791_stage_a_v5_dependency_identity_terminal_20260820.json": "90f7d95976ce186a23f16caf6cfb50aba648fc442638bff083b6a7c8da8f2004",
    "history/internal_docs/goal5791_stage_a_v5_dependency_identity_terminal_20260820.md": "81dd3be76cc3b34fa57f74f24a951707f99061b5a2c88f6e940cd3b3a1f95195",
    "history/internal_docs/goal5791_wheelhouse_v4_dependency_identity_successor_authority_20260820.json": "43f056f4ae3b55aedd44a5aab53ea4393880a7251f610faabd4da079ed35a4b3",
    "history/internal_docs/goal5791_wheelhouse_v4_dependency_identity_successor_authority_20260820.md": "ab9fcac764acc6198222b668cf83ff6ec06d76e00d29dd46445c40cc288c129a",
    "history/internal_docs/goal5791_stage_a_v6_missing_strace_terminal_20260820.json": "95c105a71e680a734a4dbda2a9627924b0ccf7dc27aa5cd79441ecca9e7a6ab6",
    "history/internal_docs/goal5791_stage_a_v6_missing_strace_terminal_20260820.md": "faf7791de989f392d2b0397bc08ba840e50a82658ef17d7a5a125ab0b6fe6384",
    "history/internal_docs/goal5791_stage_a_v7_postupload_capacity_terminal_20260820.json": "f65340c47374b1d1de387f8e6581bb36890878450afe3348fc026eea0b3ceb4e",
    "history/internal_docs/goal5791_stage_a_v7_postupload_capacity_terminal_20260820.md": "8613ffe5671f94d8c48d70f2ff5f75b1cdbedebddc468adf3a34601d37caed24",
    "history/internal_docs/goal5791_stage_a_v7_failure_evidence_20260820/UPLOAD_STAGING_OPEN_RECEIPT.json": "83121710746ef4199677b691a64e9eadccd8399a8b249ce98576b8e091535328",
    "history/internal_docs/goal5791_stage_a_v8_target_producer_observation_terminal_20260820.json": "69b000d7ef9ab9335b7db165e9019126d9273e068633620e37b3a396f2ae5b48",
    "history/internal_docs/goal5791_stage_a_v8_target_producer_observation_terminal_20260820.md": "e9a6ddd668edea48c947ae2649ae21f0eb49415a19c4092321353040cef8baf4",
    "history/internal_docs/goal5791_stage_a_v8_failure_evidence_20260820/TARGET_PTX_PRODUCER_OBSERVATION.json": "8fb0b58a26593f98a289dfffd3b16a69753617e1a56bf695f8e10a52ff74037e",
    "history/internal_docs/goal5791_portable_source_v17_build_receipt_20260820.json": "1492f37297652c8e8eaf3718d8ad774feb88c5f1ba232ebf8afcccf10cd9a4f0",
    "history/internal_docs/goal5791_portable_source_v17_independent_audit_20260820.json": "41fdfacd551e488cc1191f6588ba0ab5112177b3d97689dbf1afd3f335128194",
    "history/internal_docs/goal5791_stage_a_producer_identity_v18_successor_authority_20260820.json": "6487315dfd36f6bc84a71b45c7280c3f6766194a4ab3875a28ea7b749cfa8a14",
    "history/internal_docs/goal5791_stage_a_producer_identity_v18_successor_authority_20260820.md": "d8a3f90d291bcf5da0a90818c17a085cfb645c0ccde2667689faf8a89a05d60c",
    "history/internal_docs/goal5791_stage_a_v9_first_entry_command_serialization_terminal_20260820.json": "d6f973af664ef160b5d3c37220da64d132e26682fbf3e5c8f29dca7ce80c009a",
    "history/internal_docs/goal5791_stage_a_v9_first_entry_command_serialization_terminal_20260820.md": "adacf5eca2dc6e901c78d809afe226019d18ea666dcadf5e76a8c29636d745e4",
    "history/internal_docs/goal5791_stage_a_v10_target_binding_exact_keys_terminal_20260820.json": "9c8f9355b0640313e164814ead6c2e1618c25855bc5c4196ff6cc58090d3ab38",
    "history/internal_docs/goal5791_stage_a_v10_target_binding_exact_keys_terminal_20260820.md": "0805a39bbfae3a465166f622541f942a2f32c69d4c5f318338d706250bb4a82b",
    "history/internal_docs/goal5791_portable_source_v18_build_receipt_20260820.json": "6d003af976d53cb253cb39dae0e7e12a595f315a7dbd97580678b03461ca2b0e",
    "history/internal_docs/goal5791_portable_source_v18_independent_audit_20260820.json": "8eec5fbc73b1c4e816e3c47c10232d7261eaa7b52fd7ad719ceddfdfe0db1286",
    "history/internal_docs/goal5791_stage_a_handoff_schema_v19_successor_authority_20260820.json": "7ced91da5085f43b541de0f4b71306c4afccc7c850502dc6acc3b35af7bebaa2",
    "history/internal_docs/goal5791_stage_a_handoff_schema_v19_successor_authority_20260820.md": "9a664aa555a8c9d5500a243d72528eb144454ce8d6cf44a7ae5ad6942e4845ce",
    "history/internal_docs/goal5791_portable_source_v19_zero_output_interpreter_preflight_terminal_20260820.json": "f36a2cc57035edfe975257c3da0ee52623eabebae506d5b3c9aebc83d2b865bc",
    "history/internal_docs/goal5791_portable_source_v19_zero_output_interpreter_preflight_terminal_20260820.md": "53908d27fbd50621aec7307438ecdd3f09434a5964f73a7ef4cc0a731fd76a3a",
    "history/internal_docs/goal5791_portable_source_v20_bundled_interpreter_successor_authority_20260820.json": "a9a179028884f1c8c81181cdda35edbbcc2480059f13972710338b7f54803e40",
    "history/internal_docs/goal5791_portable_source_v20_bundled_interpreter_successor_authority_20260820.md": "ec7abdd1eb8e8664a062dd98c98240316c46b886e39dca566d9c2c133203405e",
    "history/internal_docs/goal5791_portable_source_v20_build_receipt_20260820.json": "72bf532253756965a2aaef54f83ac1d21d9087d15b9efaf96cf474f6a6aef022",
    "history/internal_docs/goal5791_portable_source_v20_independent_audit_20260820.json": "070d5436d4a68a994df29b71df4fc2db8057007ecd21c2e6a34e1ae0986b2807",
    "history/internal_docs/goal5791_home_v20_qualification_20260820/RESULT.json": "96492e6ffd3edafffe512f8f0e25b492515fb202c989d08fda86c63fb11fb96e",
    "history/internal_docs/goal5791_home_v20_qualification_20260820/FUNCTIONAL_RECOUNT.json": "56ebd6f8bba3f387c5f1b29410f78f0c159d1db182c823533504441e9c1ebc7a",
    "history/internal_docs/goal5791_home_v20_qualification_20260820/HOME_EVIDENCE_INDEPENDENT_AUDIT.json": "eeafdacf8f15a59d975ebb046ee27b42727deb169a4082db6ef6f3ea071025c6",
    "history/internal_docs/goal5791_home_v20_qualification_20260820/HOME_EVIDENCE_LOCAL_INDEPENDENT_AUDIT.json": "eeafdacf8f15a59d975ebb046ee27b42727deb169a4082db6ef6f3ea071025c6",
    "history/internal_docs/goal5791_pre_pod_bundle_v9_build_receipt_20260820.json": "c425670ddd537fe0088bd4638d3993518384cc9d191a06a08118640e6b499f17",
    "history/internal_docs/goal5791_pre_pod_bundle_v9_independent_audit_20260820.json": "40de06c089071ad830db49f5c5880b79d48758105ce57f40d03e1001a5e7bec7",
    "history/internal_docs/goal5791_owner_stage_a_request_v11_20260820.json": "c12d010419d6c712914b8db659eff5af3a8600875e30c84194e39ed67390d77e",
    "history/internal_docs/goal5791_owner_stage_a_authority_v11_20260820.json": "26fa9ec3bfc19725fd13d3e86dc3c4d23008bb49747b86d585fce7465d6025da",
    "history/internal_docs/goal5791_stage_a_v11_empty_numba_cache_directory_terminal_20260820.json": "b41f15e7630116173412a0db1bc3bc818d06da17be1ea5ed183e99abf88a1f3a",
    "history/internal_docs/goal5791_stage_a_v11_empty_numba_cache_directory_terminal_20260820.md": "f320cd712e30978a7e02a930e61560e1390dd50c6a9d679d3763d65e5e38097c",
    "history/internal_docs/goal5791_portable_source_v21_numba_cache_isolation_successor_authority_20260820.json": "7623daedbb6561488a9615761e36a74b46a588993c04a84c5ab86e237fbeef8d",
    "history/internal_docs/goal5791_portable_source_v21_numba_cache_isolation_successor_authority_20260820.md": "5c74788dd6ac63a2c199b173a0b3bcd17f3bc8776123490033d6744133b64c1e",
    "history/internal_docs/goal5791_formal_v1_worker1_numba_source_mutation_terminal_20260820.json": "74e3084812ae0b4cd250b5a707bc3f1b8009d0113b2f1b8cd56e652fe9b1f1f4",
    "history/internal_docs/goal5791_formal_v1_worker1_numba_source_mutation_terminal_20260820.md": "bcd8e99ac45df66db0a2c05aa9fe5921c0eaf24530d61dac0d73ba16a4741ba2",
    "history/internal_docs/goal5791_portable_source_v22_formal_worker_dual_cache_successor_authority_20260820.json": "a373fbc7c6f8dcdddf6cff86011810203f579dc55a8ed5120c76405364e1b25b",
    "history/internal_docs/goal5791_portable_source_v22_formal_worker_dual_cache_successor_authority_20260820.md": "1852cccf70f46050a5bee4691f980e0aee0396312dcd3313abe0b0290da0d78e",
    "history/internal_docs/goal5791_portable_source_v22_zero_output_historical_contract_assertion_terminal_20260820.json": "ea99041dd55d6d80498c0198d385c6d1afc9c43f7203bbc7b127f08b00a5f372",
    "history/internal_docs/goal5791_portable_source_v22_zero_output_historical_contract_assertion_terminal_20260820.md": "03e01f858e3625dd45a6dee80577fe1e094da8d89171d40cced6611d6789b2c5",
    "history/internal_docs/goal5791_portable_source_v23_historical_contract_assertion_successor_authority_20260820.json": "33e69578f8a70ddda081fd0e99949f3b122915367b01915919bbcadc040a063b",
    "history/internal_docs/goal5791_portable_source_v23_historical_contract_assertion_successor_authority_20260820.md": "5e597def2c3e8277a9247924b06b257abb813c5828fa4832207a827844ab7199",
    "history/internal_docs/goal5791_pre_pod_bundle_v11_manifest_contract_pin_terminal_20260820.json": "f8d10bb33eebda819af6ae3f779133ccfa0b77d9e00d900fc525d620e1035335",
    "history/internal_docs/goal5791_pre_pod_bundle_v11_manifest_contract_pin_terminal_20260820.md": "c83e9287e2e1d6616afde614a46ecdf0f536d67d417a2d8d0fc357a0a5a1bd20",
    "history/internal_docs/goal5791_portable_source_v24_auditor_contract_pin_successor_authority_20260820.json": "583878f35183ee965e56be20ef6d4614fc68fa0192d2dacf58ae6657d76353be",
    "history/internal_docs/goal5791_portable_source_v24_auditor_contract_pin_successor_authority_20260820.md": "df28d0b26449cd2732d6a361aada72e5ead3d2239e023c17c0ebf6a7e9e8c3a0",
    "history/internal_docs/goal5791_append_only_record_reference_correction_authority_20260820.json": "b21a5728ebc73c2c9c36292817b292a83360b9673ca11112969c7247429288a4",
    "history/internal_docs/goal5791_append_only_record_reference_correction_authority_20260820.md": "dcdc2759ee3bc607f8801e9354b7052b259ec82274300d0ab872bfe7bd4113d0",
    "history/internal_docs/goal5791_paper_outcome_consequence_selection_successor_authority_20260820.json": "b38251247b6408ca3b1b34b51fd8b22c2cc079f80e3f28fb14b124106b5957ac",
    "history/internal_docs/goal5791_paper_outcome_consequence_selection_successor_authority_20260820.md": "582a71d65b11595316626cb69b1fea23acc2637de1bcdd8fce6f92d7c8bab846",
    "history/internal_docs/goal5791_portable_source_v25_support_chain_auditor_terminal_20260820.json": "4a07a409176fbb3ebb01a5241c1d71cfbc2e5d73f95d895f63ca995c1973df40",
    "history/internal_docs/goal5791_portable_source_v25_support_chain_auditor_terminal_20260820.md": "eff0696a24d65c0f5aac36cbb7a2665472dae573011cd1aa1789334ff31e421b",
    "history/internal_docs/reviewer_project_state_and_remaining_work_to_cgo_20260817.md": "c74f3fd4348543dfe5bfa8c84a337160a05bb01eb2847798f0e2cf72f8b3734b",
    "history/internal_docs/goal5792_unknown_lane_classification_work_authority_20260819.json": "465cd43d1fa93a567ac85c53dc210165aa33f95c9a55d6e4064795d4804df9c3",
    "history/internal_docs/v4_competitive_cgo_submission_work_plan_after_goal5788_20260816.md": "b79dfda72bae430a2702210ccfe5d926967630048e350255136f3549ed98f1e7",
    "history/internal_docs/self_review_goal5791_amendment_a1_pretimer_fusion_execution_token_20260817.md": "b360b31b1a1ec0b7a24a20c5f83dac5684c045243ef530900d1c43082180566d",
}

WORKSPACE_CPU_TEST_MODULES = (
    "tests.goal5791_data_oracle_authority_test",
    "tests.goal5791_formal_contract_test",
    "tests.goal5791_formal_evaluator_recount_test",
    "tests.goal5791_formal_worker_controller_test",
    "tests.goal5791_portable_home_harness_test",
    "tests.goal5791_pre_pod_base_budget_audit_test",
    "tests.goal5791_pre_worker_zero_claim_freeze_test",
    "tests.goal5791_pretimer_execution_token_amendment_test",
    "tests.goal5791_segment_descriptors_test",
    "tests.goal5791_successor_source_authority_test",
    "tests.goal5791_verified_fusion_execution_token_test",
)
EXPECTED_WORKSPACE_CPU_TEST_COUNT = 115
CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS = (
    "tests.goal5791_data_oracle_authority_test."
    "Goal5791DataOracleAuthorityTest."
    "test_bundle_manifest_datasets_oracles_and_non_authorization",
    "tests.goal5791_pre_pod_base_budget_audit_test."
    "Goal5791PrePodBaseBudgetAuditTest."
    "test_budget_rebuilds_from_frozen_goal5784_and_goal5785_raw",
    "tests.goal5791_pre_pod_base_budget_audit_test."
    "Goal5791PrePodBaseBudgetAuditTest."
    "test_selected_a1_v4_base_rehashes_and_manifest_recounts",
    "tests.goal5791_pre_pod_base_budget_audit_test."
    "Goal5791PrePodBaseBudgetAuditTest."
    "test_v8_nested_elf_rejection_reproduces",
    "tests.goal5791_pre_worker_zero_claim_freeze_test."
    "Goal5791PreWorkerZeroClaimFreezeTest."
    "test_a1_raw_rejects_prove_five_facade_plus_one_tps",
    "tests.goal5791_pretimer_execution_token_amendment_test."
    "Goal5791PretimerExecutionTokenAmendmentTest."
    "test_selected_base_and_append_only_product_lineage_are_exact",
)
EXPECTED_CLEAN_CPU_TEST_COUNT = 109
CPU_TEST_TIMEOUT_SECONDS = 1_200
CPU_TEST_GATE_MEMBER = "scripts/goal5791_cpu_test_gate.py"
WORKSPACE_CPU_TEST_MODULES_SHA256 = (
    "b22d66d23ed29e80c8184880f09e257246ea21288eb3eca0567adf16506fe766"
)
EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256 = (
    "84b6fd3a5e2f2437784972d15bb5f5f19ddc7999615bd1151eed8e1634fbb171"
)
CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256 = (
    "a7319f38d0eb5ec0ca21db7588a950eb07bc0c86b4c619d68db95d39b3e30245"
)
EXPECTED_CLEAN_CPU_TEST_IDS_SHA256 = (
    "d472d8023717e1e025c5c4dbd66d39158bda156b2cec89084854bb15b28a36f9"
)
CPU_TEST_ENVIRONMENT_CONTRACT = {
    "pythonpath_role": "source_root_src_then_source_root",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONNOUSERSITE": "1",
    "CUDA_VISIBLE_DEVICES": "-1",
    "NUMBA_DISABLE_CUDA": "1",
    "ambient_environment_outside_overrides_is_not_claimed": True,
}

_FORBIDDEN_PARTS = frozenset((".codex", ".git", "__pycache__", "build"))
_FORBIDDEN_SUFFIXES = (
    ".pyc", ".pyo", ".so", ".dll", ".dylib", ".pyd", ".cubin",
    ".ptx", ".o", ".obj", ".a", ".lib", ".exe",
)
_CONTAINER_SUFFIXES = (
    ".tar.gz", ".tgz", ".tar", ".zip", ".7z", ".rar", ".gz",
    ".bz2", ".xz",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_rows(payloads: Mapping[str, bytes]) -> list[dict[str, object]]:
    return [
        {"path": name, "size_bytes": len(data), "sha256": _sha(data)}
        for name, data in sorted(payloads.items())
    ]


def _tree_sha(rows: list[dict[str, object]]) -> str:
    return _sha(json.dumps(
        rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8"))


def _normalized(name: str) -> str:
    pure = PurePosixPath(name)
    parts = tuple(part for part in pure.parts if part not in ("", "."))
    normalized = "/".join(parts)
    if not parts or pure.is_absolute() or ".." in parts \
            or normalized != name.rstrip("/"):
        raise RuntimeError(f"unsafe/noncanonical source member: {name!r}")
    if any(part.casefold() in _FORBIDDEN_PARTS for part in parts):
        raise RuntimeError(f"private/cache source member: {name!r}")
    if normalized.lower().endswith(_FORBIDDEN_SUFFIXES):
        raise RuntimeError(f"prebuilt/binary source member: {name!r}")
    return normalized


def _read_archive(data: bytes) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    folded: set[str] = set()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for member in archive.getmembers():
            name = _normalized(member.name)
            if member.isdir():
                continue
            if name in payloads or name.casefold() in folded:
                raise RuntimeError(f"duplicate/case collision: {name}")
            if not member.isfile() or member.issym() or member.islnk():
                raise RuntimeError(f"unsupported source member: {name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"unreadable source member: {name}")
            payloads[name] = stream.read()
            folded.add(name.casefold())
    return payloads


def _blob_kind(data: bytes) -> str | None:
    signatures = (
        (b"\x7fELF", "ELF"), (b"MZ", "PE"), (b"!<arch>\n", "AR"),
        (b"\xcf\xfa\xed\xfe", "MACHO64_LE"),
        (b"\xfe\xed\xfa\xcf", "MACHO64_BE"),
        (b"\xce\xfa\xed\xfe", "MACHO32_LE"),
        (b"\xfe\xed\xfa\xce", "MACHO32_BE"),
        (b"\x1f\x8b", "GZIP"), (b"PK\x03\x04", "ZIP"),
        (b"PK\x05\x06", "ZIP_EMPTY"), (b"BZh", "BZIP2"),
        (b"\xfd7zXZ\x00", "XZ"),
        (b"7z\xbc\xaf'\x1c", "7ZIP"),
        (b"Rar!\x1a\x07\x00", "RAR4"),
        (b"Rar!\x1a\x07\x01\x00", "RAR5"),
        (b"P\xedU\xba", "CUDA_FATBIN_V1"),
        (b"\xb1CbF", "CUDA_FATBIN_V2"),
    )
    for prefix, kind in signatures:
        if data.startswith(prefix):
            return kind
    if len(data) >= 262 and data[257:262] == b"ustar":
        return "TAR"
    if any(data.startswith(magic) for magic in (
        b"\x42\x0d\x0d\x0a", b"\x33\x0d\x0d\x0a",
        b"\xa7\x0d\x0d\x0a", b"\xcb\x0d\x0d\x0a",
    )):
        return "PYTHON_BYTECODE"
    return None


def _deep_audit(payloads: Mapping[str, bytes]) -> dict[str, object]:
    for name, data in payloads.items():
        if name.lower().endswith(_CONTAINER_SUFFIXES):
            raise RuntimeError(f"nested container suffix remains: {name}")
        kind = _blob_kind(data)
        if kind is not None:
            raise RuntimeError(f"binary/container magic remains: {name}: {kind}")
    return {
        "all_payload_bytes_scanned": True,
        "scanned_payload_count": len(payloads),
        "maximum_nested_container_depth": 0,
        "recognized_container_magic_count": 0,
        "recognized_container_suffix_count": 0,
        "recognized_executable_or_device_binary_magic_count": 0,
        "private_cache_member_count": 0,
    }


def _verify_base(payloads: Mapping[str, bytes]) -> dict[str, object]:
    data = payloads.get(BASE_MANIFEST)
    if data is None or _sha(data) != BASE_MANIFEST_SHA256:
        raise RuntimeError("Goal5790-A1 v4 base manifest drifted")
    value = json.loads(data)
    if value.get("schema") != "rtdl.goal5790_a1.portable_source_manifest.v4" \
            or value.get("source_tree_sha256") != BASE_TREE_SHA256:
        raise RuntimeError("Goal5790-A1 v4 base manifest header drifted")
    rows = value.get("files")
    if not isinstance(rows, list):
        raise RuntimeError("Goal5790-A1 v4 base file rows are absent")
    expected = {
        str(row["path"]): (int(row["size_bytes"]), str(row["sha256"]))
        for row in rows
    }
    actual = {
        name: (len(blob), _sha(blob)) for name, blob in payloads.items()
        if name != BASE_MANIFEST
    }
    if len(rows) != len(expected) or expected != actual \
            or value.get("file_count_excluding_this_manifest") != len(actual) \
            or _tree_sha(_canonical_rows({
                name: blob for name, blob in payloads.items()
                if name != BASE_MANIFEST
            })) != BASE_TREE_SHA256:
        raise RuntimeError("Goal5790-A1 v4 base manifest does not rehash")
    return value


def _archive(payloads: Mapping[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as out:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o755 if name.endswith((".py", ".sh")) else 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                out.addfile(info, io.BytesIO(data))
    return output.getvalue()


def _extract(payloads: Mapping[str, bytes], target: Path) -> None:
    if target.exists() or target.is_symlink():
        raise FileExistsError(target)
    target.mkdir(parents=True)
    for name, data in sorted(payloads.items()):
        path = target.joinpath(*PurePosixPath(name).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def _audit_extracted_exact_set(
    root: Path, expected: Mapping[str, bytes],
) -> dict[str, object]:
    """Reject extra regular files, links, or special nodes after extraction."""

    observed: dict[str, bytes] = {}
    observed_dirs: set[str] = set()
    expected_dirs: set[str] = set()
    for name in expected:
        parent = PurePosixPath(name).parent
        while parent.as_posix() not in ("", "."):
            expected_dirs.add(parent.as_posix())
            parent = parent.parent
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
        reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        if path.is_symlink() or (reparse_flag and attributes & reparse_flag):
            raise RuntimeError(
                f"Goal5791 extracted source contains link/reparse: {relative}")
        if path.is_dir():
            observed_dirs.add(relative)
            continue
        if not path.is_file():
            raise RuntimeError(
                f"Goal5791 extracted source contains special node: {relative}")
        observed[relative] = path.read_bytes()
    if observed != dict(expected) or observed_dirs != expected_dirs:
        raise RuntimeError(
            "Goal5791 extracted file/directory set or bytes drifted: "
            + repr({
                "files": sorted(set(observed) ^ set(expected))[:16],
                "directories": sorted(observed_dirs ^ expected_dirs)[:16],
            })
        )
    return {
        "regular_file_count": len(observed),
        "directory_count_excluding_root": len(observed_dirs),
        "regular_file_set_exact": True,
        "directory_set_exact": True,
        "extra_regular_file_count": 0,
        "extra_directory_count": 0,
        "link_count": 0,
        "reparse_point_count": 0,
        "special_file_count": 0,
    }


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def _path_for_receipt(path: Path) -> str:
    if not path.is_absolute():
        return path.as_posix()
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _regular_file_snapshot(
    path: Path, *, label: str,
) -> tuple[bytes, tuple[int, int, int, int, int, int]]:
    if not path.is_file() or path.is_symlink():
        raise FileNotFoundError(f"Goal5791 {label} absent/not regular: {path}")
    before = path.stat()
    if not stat.S_ISREG(before.st_mode):
        raise RuntimeError(f"Goal5791 {label} is not a regular file: {path}")
    data = path.read_bytes()
    after = path.stat()
    identity = lambda value: (
        value.st_mode, value.st_size, value.st_mtime_ns, value.st_ctime_ns,
        value.st_ino, value.st_dev,
    )
    if identity(before) != identity(after) or len(data) != after.st_size:
        raise RuntimeError(f"Goal5791 {label} changed while read: {path}")
    return data, identity(after)


def _verified_workspace_input_snapshot(
) -> tuple[
    bytes, dict[str, bytes], bytes,
    dict[str, tuple[int, int, int, int, int, int]],
]:
    base_bytes, base_identity = _regular_file_snapshot(
        BASE_SOURCE, label="base source")
    if len(base_bytes) != BASE_SOURCE_BYTES \
            or _sha(base_bytes) != BASE_SOURCE_SHA256:
        raise RuntimeError("Goal5790-A1 portable-source v4 base drifted")
    overlays: dict[str, bytes] = {}
    identities = {"__base_source__": base_identity}
    for name in OVERLAY_PATHS:
        path = ROOT.joinpath(*PurePosixPath(name).parts)
        data, identity = _regular_file_snapshot(
            path, label=f"overlay {name}")
        if _sha(data) != EXPECTED_OVERLAY_SHA256[name]:
            raise RuntimeError(f"Goal5791 overlay drifted: {name}")
        overlays[name] = data
        identities[name] = identity
    builder, builder_identity = _regular_file_snapshot(
        ROOT / BUILDER_MEMBER, label="portable source builder")
    identities[BUILDER_MEMBER] = builder_identity
    return base_bytes, overlays, builder, identities


def _assert_workspace_input_snapshot_unchanged(
    *, base_bytes: bytes, overlays: Mapping[str, bytes], builder: bytes,
    identities: Mapping[str, tuple[int, int, int, int, int, int]],
) -> None:
    observed_base, observed_overlays, observed_builder, observed_identities = (
        _verified_workspace_input_snapshot())
    if observed_base != base_bytes \
            or observed_overlays != dict(overlays) \
            or observed_builder != builder \
            or observed_identities != dict(identities):
        raise RuntimeError(
            "Goal5791 workspace input changed across the full CPU gate")


def _canonical_digest(value: object) -> str:
    return _sha(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8"))


def _validate_cpu_test_gate_result(
    value: object, *, scope: str, require_success: bool = True,
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {
        "schema", "scope", "python_role", "entrypoint",
        "workspace_test_modules", "workspace_test_module_count",
        "workspace_test_modules_sha256", "discovered_workspace_test_ids",
        "discovered_workspace_test_count",
        "discovered_workspace_test_ids_sha256",
        "excluded_external_only_test_ids",
        "excluded_external_only_test_count",
        "excluded_external_only_test_ids_sha256", "selected_test_ids",
        "selected_test_count", "selected_test_ids_sha256",
        "environment_contract", "test_result", "success",
        "outcome_test_ids", "outcome_test_ids_sha256",
        "failure_test_ids", "error_test_ids",
        "failure_exception_summaries", "error_exception_summaries",
        "reported_elapsed_value_count",
        "test_or_scientific_clock_sample_count",
        "registered_performance_timing_count",
        "operational_timeout_watchdog_uses_host_clock",
        "operational_watchdog_clock_not_persisted_or_registered",
    }:
        raise RuntimeError("Goal5791 CPU test gate result shape drifted")
    full_ids = value.get("discovered_workspace_test_ids")
    excluded_ids = value.get("excluded_external_only_test_ids")
    selected_ids = value.get("selected_test_ids")
    if not isinstance(full_ids, list) \
            or not all(isinstance(item, str) and item for item in full_ids) \
            or len(set(full_ids)) != len(full_ids) \
            or not isinstance(excluded_ids, list) \
            or not all(isinstance(item, str) and item for item in excluded_ids) \
            or len(set(excluded_ids)) != len(excluded_ids) \
            or not isinstance(selected_ids, list) \
            or not all(isinstance(item, str) and item for item in selected_ids) \
            or len(set(selected_ids)) != len(selected_ids):
        raise RuntimeError("Goal5791 CPU test gate IDs are malformed")
    expected_clean_ids = [
        item for item in full_ids
        if item not in set(CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS)
    ]
    expected_selected_ids = (
        full_ids if scope == "workspace" else expected_clean_ids)
    expected_selected_count = (
        EXPECTED_WORKSPACE_CPU_TEST_COUNT
        if scope == "workspace" else EXPECTED_CLEAN_CPU_TEST_COUNT)
    expected_selected_sha = (
        EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256
        if scope == "workspace" else EXPECTED_CLEAN_CPU_TEST_IDS_SHA256)
    test_result = value.get("test_result")
    result_keys = (
        "failures", "errors", "skipped", "expectedFailures",
        "unexpectedSuccesses",
    )
    outcome_ids = value.get("outcome_test_ids")
    if not isinstance(outcome_ids, dict) or set(outcome_ids) != set(result_keys) \
            or any(not isinstance(outcome_ids.get(key), list)
                   for key in result_keys):
        raise RuntimeError("Goal5791 CPU test outcome map drifted")
    selected_set = set(selected_ids)
    for key in result_keys:
        ids = outcome_ids[key]
        if ids != sorted(ids) \
                or not all(isinstance(item, str) and item for item in ids) \
                or len(ids) != len(set(ids)) \
                or not set(ids).issubset(selected_set):
            raise RuntimeError("Goal5791 CPU test outcome IDs drifted")
    all_outcome_ids = [
        item for key in result_keys for item in outcome_ids[key]
    ]
    if len(all_outcome_ids) != len(set(all_outcome_ids)):
        raise RuntimeError("Goal5791 CPU test outcome classes overlap")
    failure_summaries = value.get("failure_exception_summaries")
    error_summaries = value.get("error_exception_summaries")

    def validate_summaries(
        summaries: object, *, outcome: str, expected_ids: list[str],
    ) -> bool:
        if not isinstance(summaries, list) or len(summaries) != len(expected_ids):
            return False
        expected_order = sorted(
            summaries,
            key=lambda item: (
                item.get("test_id", ""), item.get("summary", ""))
            if isinstance(item, dict) else ("", ""),
        )
        if summaries != expected_order:
            return False
        observed_ids: list[str] = []
        for item in summaries:
            if not isinstance(item, dict) or set(item) != {
                    "test_id", "outcome", "exception_type", "summary"}:
                return False
            test_id = item.get("test_id")
            exception_type = item.get("exception_type")
            summary = item.get("summary")
            if not isinstance(test_id, str) or not test_id \
                    or item.get("outcome") != outcome \
                    or not isinstance(exception_type, str) \
                    or not exception_type \
                    or not isinstance(summary, str) or len(summary) > 2_048 \
                    or "\n" in summary or "\r" in summary \
                    or re.search(
                        r"(?:[a-z]:/|/(?:tmp|private/tmp|var/tmp)/|"
                        r"/users/[^/]+/appdata/local/temp/)", summary,
                        flags=re.IGNORECASE,
                    ) \
                    or any(part in summary.casefold()
                           for part in ("/.codex/", "/.git/")):
                return False
            observed_ids.append(test_id)
        return observed_ids == expected_ids

    if not isinstance(test_result, dict) \
            or set(test_result) != {"testsRun", *result_keys} \
            or any(type(test_result.get(key)) is not int
                   for key in ("testsRun", *result_keys)) \
            or test_result.get("testsRun") != expected_selected_count \
            or any(test_result.get(key) != len(outcome_ids[key])
                   for key in result_keys) \
            or value.get("failure_test_ids") != outcome_ids["failures"] \
            or value.get("error_test_ids") != outcome_ids["errors"] \
            or value.get("outcome_test_ids_sha256") \
                != _canonical_digest(outcome_ids) \
            or not validate_summaries(
                failure_summaries, outcome="failure",
                expected_ids=outcome_ids["failures"]) \
            or not validate_summaries(
                error_summaries, outcome="error",
                expected_ids=outcome_ids["errors"]):
        raise RuntimeError("Goal5791 CPU test outcome evidence drifted")
    derived_success = all(not outcome_ids[key] for key in result_keys)
    if scope not in {"workspace", "clean"} \
            or value.get("schema") \
                != "rtdl.goal5791.cpu_test_gate_result.v2" \
            or value.get("scope") != scope \
            or value.get("python_role") != "current_interpreter" \
            or value.get("entrypoint") != CPU_TEST_GATE_MEMBER \
            or value.get("workspace_test_modules") \
                != list(WORKSPACE_CPU_TEST_MODULES) \
            or type(value.get("workspace_test_module_count")) is not int \
            or value.get("workspace_test_module_count") \
                != len(WORKSPACE_CPU_TEST_MODULES) \
            or value.get("workspace_test_modules_sha256") \
                != WORKSPACE_CPU_TEST_MODULES_SHA256 \
            or _canonical_digest(list(WORKSPACE_CPU_TEST_MODULES)) \
                != WORKSPACE_CPU_TEST_MODULES_SHA256 \
            or type(value.get("discovered_workspace_test_count")) is not int \
            or value.get("discovered_workspace_test_count") \
                != EXPECTED_WORKSPACE_CPU_TEST_COUNT \
            or len(full_ids) != EXPECTED_WORKSPACE_CPU_TEST_COUNT \
            or _canonical_digest(full_ids) \
                != EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256 \
            or value.get("discovered_workspace_test_ids_sha256") \
                != EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256 \
            or excluded_ids != list(CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS) \
            or type(value.get("excluded_external_only_test_count")) is not int \
            or value.get("excluded_external_only_test_count") != 6 \
            or _canonical_digest(excluded_ids) \
                != CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256 \
            or value.get("excluded_external_only_test_ids_sha256") \
                != CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256 \
            or not set(excluded_ids).issubset(full_ids) \
            or selected_ids != expected_selected_ids \
            or type(value.get("selected_test_count")) is not int \
            or value.get("selected_test_count") != expected_selected_count \
            or value.get("selected_test_ids_sha256") \
                != expected_selected_sha \
            or _canonical_digest(selected_ids) != expected_selected_sha \
            or value.get("environment_contract") \
                != CPU_TEST_ENVIRONMENT_CONTRACT \
            or value.get("success") is not derived_success \
            or (require_success and not derived_success) \
            or any(type(value.get(key)) is not int or value.get(key) != 0
                   for key in (
                       "reported_elapsed_value_count",
                       "test_or_scientific_clock_sample_count",
                       "registered_performance_timing_count")):
        raise RuntimeError("Goal5791 CPU test gate identity/result drifted")
    if value.get("operational_timeout_watchdog_uses_host_clock") is not True \
            or value.get(
                "operational_watchdog_clock_not_persisted_or_registered") \
                is not True:
        raise RuntimeError("Goal5791 CPU gate watchdog disclosure drifted")
    return value


def _cpu_test_gate(root: Path, *, scope: str) -> dict[str, object]:
    env = os.environ.copy()
    env.update({
        "PYTHONPATH": os.pathsep.join((str(root / "src"), str(root))),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "CUDA_VISIBLE_DEVICES": "-1",
        "NUMBA_DISABLE_CUDA": "1",
    })
    helper = root.joinpath(*PurePosixPath(CPU_TEST_GATE_MEMBER).parts)
    if not helper.is_file() or helper.is_symlink():
        raise RuntimeError("Goal5791 CPU test gate helper is absent/not regular")
    command = [
        sys.executable, str(helper), "--root", str(root), "--scope", scope,
    ]
    completed = subprocess.run(
        command, cwd=root, env=env, text=True, encoding="utf-8",
        errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        timeout=CPU_TEST_TIMEOUT_SECONDS, check=False,
    )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    try:
        value = json.loads(lines[-1])
    except (IndexError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            "Goal5791 CPU gate emitted no strict result:\n"
            + completed.stdout[-16000:]) from exc
    validated = _validate_cpu_test_gate_result(
        value, scope=scope, require_success=completed.returncode == 0)
    if completed.returncode:
        if completed.returncode != 1 or validated.get("success") is not False:
            raise RuntimeError(
                f"Goal5791 {scope} CPU gate exit/result drifted: "
                f"returncode={completed.returncode}")
        raise RuntimeError(
            f"Goal5791 {scope} CPU gate failed: "
            f"failure_test_ids={json.dumps(validated['failure_test_ids'])}; "
            f"error_test_ids={json.dumps(validated['error_test_ids'])}; "
            "failure_exception_summaries="
            f"{json.dumps(validated['failure_exception_summaries'], sort_keys=True)}; "
            "error_exception_summaries="
            f"{json.dumps(validated['error_exception_summaries'], sort_keys=True)}")
    return validated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    outputs = (args.output, args.twin, args.receipt)
    if len({path.resolve() for path in outputs}) != 3:
        raise ValueError("Goal5791 outputs must be pairwise distinct")
    if any(path.exists() or path.is_symlink() for path in outputs):
        raise FileExistsError("Goal5791 output already exists")
    expected_outputs = (
        ROOT / CANONICAL_OUTPUT_PATH,
        ROOT / CANONICAL_TWIN_PATH,
        ROOT / CANONICAL_RECEIPT_PATH,
    )
    if tuple(path.resolve() for path in outputs) != tuple(
        path.resolve() for path in expected_outputs
    ):
        raise ValueError(
            "Goal5791 source outputs must use the frozen canonical paths")
    if set(EXPECTED_OVERLAY_SHA256) != set(OVERLAY_PATHS):
        raise RuntimeError("Goal5791 exact overlay hash map is not frozen")

    base_bytes, frozen_overlays, builder, workspace_identities = (
        _verified_workspace_input_snapshot())
    workspace_cpu_gate = _cpu_test_gate(ROOT, scope="workspace")
    _assert_workspace_input_snapshot_unchanged(
        base_bytes=base_bytes, overlays=frozen_overlays, builder=builder,
        identities=workspace_identities)
    base = _read_archive(base_bytes)
    base_manifest = _verify_base(base)
    payloads = dict(base)
    preserved_base_manifest = payloads[BASE_MANIFEST]
    del payloads[BASE_MANIFEST]
    if PRESERVED_BASE_MANIFEST_MEMBER in payloads:
        raise RuntimeError("Goal5791 preserved base manifest path collision")
    payloads[PRESERVED_BASE_MANIFEST_MEMBER] = preserved_base_manifest
    base_product = {
        name: _sha(data) for name, data in payloads.items()
        if name.startswith(("src/", "native/"))
    }
    for name in OVERLAY_PATHS:
        payloads[name] = frozen_overlays[name]
    payloads[BUILDER_MEMBER] = builder

    successor_product = {
        name: _sha(data) for name, data in payloads.items()
        if name.startswith(("src/", "native/"))
    }
    changed_product = sorted(
        set(base_product) | set(successor_product),
        key=str,
    )
    changed_product = [
        name for name in changed_product
        if base_product.get(name) != successor_product.get(name)
    ]
    if changed_product != sorted(PRODUCT_DELTA):
        raise RuntimeError(f"Goal5791 product delta set drifted: {changed_product!r}")
    for name, record in PRODUCT_DELTA.items():
        if base_product.get(name) != record["base_sha256"] \
                or successor_product.get(name) != record["successor_sha256"]:
            raise RuntimeError(f"Goal5791 product old/new hash drifted: {name}")
    for name in payloads:
        _normalized(name)
    if NEW_MANIFEST in payloads:
        raise RuntimeError("Goal5791 non-self manifest path collision")
    deep = _deep_audit(payloads)
    rows = _canonical_rows(payloads)
    tree_sha = _tree_sha(rows)
    manifest = (json.dumps({
        "schema": "rtdl.goal5791.portable_source_manifest.v1",
        "goal": 5791,
        "status": "PORTABLE_SOURCE_FROZEN__HOME_REQUALIFICATION_REQUIRED",
        "base_source_archive_sha256": BASE_SOURCE_SHA256,
        "base_source_manifest_sha256": BASE_MANIFEST_SHA256,
        "base_source_tree_sha256": BASE_TREE_SHA256,
        "base_source_file_count_excluding_manifest": base_manifest[
            "file_count_excluding_this_manifest"],
        "old_source_manifest_removed": BASE_MANIFEST,
        "product_delta_paths": sorted(PRODUCT_DELTA),
        "product_delta": PRODUCT_DELTA,
        "nonproduct_overlay_count_including_builder": (
            len(OVERLAY_PATHS) + 2 - len(PRODUCT_DELTA)),
        "deep_blob_audit": deep,
        "manifest_is_non_self_referential": True,
        "file_count_excluding_this_manifest": len(rows),
        "source_tree_sha256": tree_sha,
        "home_or_target_execution_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "files": rows,
    }, indent=2, sort_keys=True) + "\n").encode("utf-8")
    archive_payloads = {**payloads, NEW_MANIFEST: manifest}
    archive_bytes = _archive(archive_payloads)
    if _read_archive(archive_bytes) != archive_payloads:
        raise RuntimeError("Goal5791 in-memory archive reopen mismatch")

    with tempfile.TemporaryDirectory(prefix="goal5791_source_audit_") as temp:
        extracted = Path(temp) / "source"
        _extract(archive_payloads, extracted)
        extracted_before = _audit_extracted_exact_set(
            extracted, archive_payloads)
        clean_cpu_gate = _cpu_test_gate(extracted, scope="clean")
        extracted_after = _audit_extracted_exact_set(
            extracted, archive_payloads)

    archive_sha = _sha(archive_bytes)
    builder_sha = _sha(builder)
    receipt_value = {
        "schema": "rtdl.goal5791.portable_source_build_receipt.v26",
        "goal": 5791,
        "status": "PASS__DETERMINISTIC_NATIVE_FREE_SOURCE__NO_EXECUTION",
        "base_source_archive_path": BASE_SOURCE.relative_to(ROOT).as_posix(),
        "base_source_archive_sha256": BASE_SOURCE_SHA256,
        "base_source_manifest_sha256": BASE_MANIFEST_SHA256,
        "base_source_tree_sha256": BASE_TREE_SHA256,
        "base_manifest_rehashed": True,
        "preserved_base_manifest_member": PRESERVED_BASE_MANIFEST_MEMBER,
        "preserved_base_manifest_sha256": BASE_MANIFEST_SHA256,
        "output_path": CANONICAL_OUTPUT_PATH,
        "twin_path": CANONICAL_TWIN_PATH,
        "source_archive_sha256": archive_sha,
        "source_archive_bytes": len(archive_bytes),
        "source_twin_sha256": archive_sha,
        "source_twin_byte_identical": True,
        "source_manifest_member": NEW_MANIFEST,
        "source_manifest_sha256": _sha(manifest),
        "source_manifest_non_self_referential": True,
        "source_tree_sha256": tree_sha,
        "source_file_count_excluding_manifest": len(payloads),
        "archive_payload_count_including_manifest": len(archive_payloads),
        "archive_payload_bytes": sum(len(data) for data in archive_payloads.values()),
        "builder_path": BUILDER_MEMBER,
        "builder_sha256": builder_sha,
        "overlay_sha256": {
            **dict(EXPECTED_OVERLAY_SHA256), BUILDER_MEMBER: builder_sha,
        },
        "product_delta": PRODUCT_DELTA,
        "changed_product_file_count": len(changed_product),
        "changed_native_file_count": 0,
        "deep_blob_audit": deep,
        "unsafe_member_count": 0,
        "prebuilt_native_or_device_binary_count": 0,
        "nested_container_count": 0,
        "private_cache_member_count": 0,
        "empty_directory_extract_rehash_passed": True,
        "clean_extraction_exact_set_before_tests": extracted_before,
        "clean_extraction_exact_set_after_tests": extracted_after,
        "cpu_test_gate_helper_member": CPU_TEST_GATE_MEMBER,
        "cpu_test_gate_helper_sha256": _sha(
            payloads[CPU_TEST_GATE_MEMBER]),
        "workspace_cpu_test_gate_result": workspace_cpu_gate,
        "clean_cpu_test_gate_result": clean_cpu_gate,
        "cpu_test_timeout_seconds": CPU_TEST_TIMEOUT_SECONDS,
        "home_or_target_execution_count": 0,
        "gpu_execution_count": 0,
        "pod_execution_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "reported_elapsed_value_count": 0,
        "test_or_scientific_clock_sample_count": 0,
        "operational_timeout_watchdog_uses_host_clock": True,
        "operational_watchdog_clock_not_persisted_or_registered": True,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
        "requires_fresh_home_token_path_qualification": True,
        "requires_separate_owner_target_prepare_authority": True,
        "requires_separate_postprepare_owner_formal_authority": True,
        "performance_or_compiler_fusion_claimed": False,
    }
    receipt = (json.dumps(
        receipt_value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    _write(args.output, archive_bytes)
    _write(args.twin, archive_bytes)
    _write(args.receipt, receipt)
    if args.output.read_bytes() != args.twin.read_bytes():
        raise RuntimeError("Goal5791 on-disk source twin differs")
    print(json.dumps({
        "source_archive_sha256": archive_sha,
        "source_tree_sha256": tree_sha,
        "source_manifest_sha256": _sha(manifest),
        "source_file_count_excluding_manifest": len(payloads),
        "archive_payload_count_including_manifest": len(archive_payloads),
        "archive_payload_bytes": sum(len(data) for data in archive_payloads.values()),
        "workspace_cpu_test_count": workspace_cpu_gate[
            "selected_test_count"],
        "clean_cpu_test_count": clean_cpu_gate["selected_test_count"],
        "source_twin_byte_identical": True,
        "receipt_sha256": _sha(receipt),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
