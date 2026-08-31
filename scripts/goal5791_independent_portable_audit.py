#!/usr/bin/env python3
"""Independent stdlib audit for frozen Goal5791 source or pre-POD bundle."""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tarfile
import tempfile


SOURCE_MANIFEST = (
    "history/internal_docs/goal5791_portable_source_manifest_v1_20260817.json"
)
SOURCE_SCHEMA = "rtdl.goal5791.portable_source_manifest.v1"
BUNDLE_SCHEMA = "rtdl.goal5791.pre_pod_bundle.v3"
HOME_EVIDENCE_SCHEMA = "rtdl.goal5791.home_token_evidence_manifest.v1"
BASE_SOURCE_SHA256 = (
    "fe7cb3ea456b02432339dca6fe51f9bd8b05bfbb373c8f13fa38e3a68907fd1f"
)
BASE_SOURCE_MANIFEST_SHA256 = (
    "d538a1ddaa79768feb9c8845077c069e444151d5aa76a59f50bd55922933b9c5"
)
BASE_SOURCE_TREE_SHA256 = (
    "62ff2a310517eed5d3c8ef64d757f714346f211416a6cf7ba5034d9013b24de6"
)
BASE_SOURCE_FILE_COUNT = 729
BASE_SOURCE_ARCHIVE_PATH = (
    "history/internal_docs/goal5790_a1_portable_source_v4_20260816.tar.gz"
)
HISTORICAL_V4_SOURCE_OUTPUT_PATH = (
    "history/internal_docs/goal5791_portable_source_v4_20260817.tar.gz"
)
HISTORICAL_V4_SOURCE_TWIN_PATH = (
    "history/internal_docs/goal5791_portable_source_v4_twin_20260817.tar.gz"
)
HISTORICAL_V16_SOURCE_OUTPUT_PATH = (
    "history/internal_docs/goal5791_portable_source_v16_20260820.tar.gz"
)
HISTORICAL_V16_SOURCE_TWIN_PATH = (
    "history/internal_docs/goal5791_portable_source_v16_twin_20260820.tar.gz"
)
HISTORICAL_V16_SOURCE_RECEIPT_PATH = (
    "history/internal_docs/goal5791_portable_source_v16_build_receipt_20260820.json"
)
CANONICAL_SOURCE_OUTPUT_PATH = (
    "history/internal_docs/goal5791_portable_source_v26_20260820.tar.gz"
)
CANONICAL_SOURCE_TWIN_PATH = (
    "history/internal_docs/goal5791_portable_source_v26_twin_20260820.tar.gz"
)
V1_ZERO_OUTPUT_TERMINAL_MEMBER = (
    "history/internal_docs/"
    "goal5791_portable_source_v1_zero_output_terminal_20260817.json"
)
V1_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER = (
    "history/internal_docs/"
    "goal5791_portable_source_v1_zero_output_terminal_20260817.md"
)
V1_TERMINAL_BUILDER_SHA256 = (
    "f0e9c9ca0496cb00ef7a810a1af453fe954cf7e279e8bf7b4bdc6e67ae1082f7"
)
V2_ZERO_OUTPUT_TERMINAL_MEMBER = (
    "history/internal_docs/"
    "goal5791_portable_source_v2_zero_output_terminal_20260817.json"
)
V2_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER = (
    "history/internal_docs/"
    "goal5791_portable_source_v2_zero_output_terminal_20260817.md"
)
V2_ZERO_OUTPUT_TERMINAL_SHA256 = (
    "95fbc322050cc89ce1b7a8d96e1c8c09959930f36d648d03af63d491e8bd2762"
)
V2_ZERO_OUTPUT_TERMINAL_REPORT_SHA256 = (
    "a36cdaa27eb18443a9c2fc7f73aa5579bd0a5d1054a788f709007bc271af941d"
)
V2_ZERO_OUTPUT_TERMINAL_INTERNAL_SHA256 = (
    "9315dfb29f9c2814b3baa324ab72b4aa9074fe74da656edfdc17a2751cdb7949"
)
DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_MEMBER = (
    "history/internal_docs/"
    "goal5791_portable_source_v3_dual_cpu_gate_successor_authority_20260817.json"
)
DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_REPORT_MEMBER = (
    "history/internal_docs/"
    "goal5791_portable_source_v3_dual_cpu_gate_successor_authority_20260817.md"
)
DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_FILE_SHA256 = (
    "923d1a07700d6e218a0ecba3d40b7ee5ed537c9a99370fbe79a5fa9e6e90eac2"
)
DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_SHA256 = (
    "944c9fee277737ac7aa3ddc40ea3358e34a00b54175ca06f079654c5a335af21"
)
DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_REPORT_SHA256 = (
    "1e1071bb5b2bc487e7d2ca115046f36b3ce331c167a46bcad17a5436f4e11c79"
)
V3_CPU_TEST_GATE_HELPER_SHA256 = (
    "38ba5a158c1c6be580c9f30c52156c8ca21742aadb06cccfd74a1b08d8471fdd"
)
HISTORICAL_V3_FORMAL_CONTRACT_FILE_SHA256 = (
    "bf2c3bf108acedb03245368f739d4ee81678b8279b745351736568635ef10d64"
)
HISTORICAL_V3_FORMAL_CONTRACT_SHA256 = (
    "9296e5d5fbffa18cff05fd745218d091c52cf6febd0c6d347156c435beadf5b3"
)
HISTORICAL_V3_WORKSPACE_CPU_TEST_COUNT = 112
HISTORICAL_V3_CLEAN_CPU_TEST_COUNT = 106
HISTORICAL_V3_WORKSPACE_CPU_TEST_IDS_SHA256 = (
    "3fbc3cc1166ff1d8523c9d5c61e20d62ecbef09c98769ca7f89cbd0b5bfe5caa"
)
HISTORICAL_V3_CLEAN_CPU_TEST_IDS_SHA256 = (
    "d6ee66ab065c34507fcb5886ed130a83c9772978f869cce08ab33d7d7d641bdb"
)
V4_CPU_TEST_GATE_HELPER_SHA256 = (
    "2fa6364c55099baf164a7bf8879a552c48d976103efd19ec7ad5ddd4a4d30656"
)
HISTORICAL_V4_WORKSPACE_CPU_TEST_COUNT = 112
HISTORICAL_V4_CLEAN_CPU_TEST_COUNT = 106
HISTORICAL_V4_WORKSPACE_CPU_TEST_IDS_SHA256 = (
    "3fbc3cc1166ff1d8523c9d5c61e20d62ecbef09c98769ca7f89cbd0b5bfe5caa"
)
HISTORICAL_V4_CLEAN_CPU_TEST_IDS_SHA256 = (
    "d6ee66ab065c34507fcb5886ed130a83c9772978f869cce08ab33d7d7d641bdb"
)
V3_ZERO_OUTPUT_TERMINAL_MEMBER = (
    "history/internal_docs/"
    "goal5791_portable_source_v3_zero_output_terminal_20260817.json"
)
V3_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER = (
    "history/internal_docs/"
    "goal5791_portable_source_v3_zero_output_terminal_20260817.md"
)
V3_ZERO_OUTPUT_TERMINAL_SHA256 = (
    "b8d160a0299c34fb8f00b737b2865b6394c05a29eacf224c996c696128ce9538"
)
V3_ZERO_OUTPUT_TERMINAL_INTERNAL_SHA256 = (
    "0713dfd43feecff11428a1a75db2cef40ef485c395b1933d9c08f0c840d741d2"
)
V3_ZERO_OUTPUT_TERMINAL_REPORT_SHA256 = (
    "537d4e0e00727f38b82d5640044df0583e16e7ed2f5aeb994d8c44abe4446ac8"
)
V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_MEMBER = (
    "history/internal_docs/"
    "goal5791_portable_source_v4_clean_failure_diagnostic_successor_authority_20260817.json"
)
V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_REPORT_MEMBER = (
    "history/internal_docs/"
    "goal5791_portable_source_v4_clean_failure_diagnostic_successor_authority_20260817.md"
)
V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_FILE_SHA256 = (
    "d0e0db723c47f6c43502d790cf52a097da060b7e6ae57d1473404f9e0a91fab6"
)
V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_SHA256 = (
    "d34bd31f9d5dc8a3214c2510b59369399fb81d4ee39f5641270f4fb44b106282"
)
V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_REPORT_SHA256 = (
    "d8949d25bc6592e82431a89957c88a675ca1a8c957bec8455208d2dc6568f188"
)
STAGE_A_V15_SUCCESSOR_AUTHORITY_MEMBER = (
    "history/internal_docs/"
    "goal5791_stage_a_endpoint_record_v15_successor_authority_20260820.json"
)
STAGE_A_V15_SUCCESSOR_AUTHORITY_REPORT_MEMBER = (
    "history/internal_docs/"
    "goal5791_stage_a_endpoint_record_v15_successor_authority_20260820.md"
)
STAGE_A_V15_SUCCESSOR_AUTHORITY_FILE_SHA256 = (
    "29bea2bc28942d5e3040db58a4bd3b6ba2507058a55d4adb0d2279082f33f938"
)
STAGE_A_V15_SUCCESSOR_AUTHORITY_SHA256 = (
    "7abe6b029a1112eba8e836067ac605a42adef90489fc063046080381c5d9dc38"
)
STAGE_A_V15_SUCCESSOR_AUTHORITY_REPORT_SHA256 = (
    "372da96b6626366dfeda2d5aaee49869266981e4c53d880aac0ea558cccce46e"
)
STAGE_A_V16_SUCCESSOR_AUTHORITY_MEMBER = (
    "history/internal_docs/"
    "goal5791_stage_a_archive_root_v16_successor_authority_20260820.json"
)
STAGE_A_V16_SUCCESSOR_AUTHORITY_REPORT_MEMBER = (
    "history/internal_docs/"
    "goal5791_stage_a_archive_root_v16_successor_authority_20260820.md"
)
STAGE_A_V16_SUCCESSOR_AUTHORITY_FILE_SHA256 = (
    "9ff7f0f3dfa3b3d71df3c08d974fb658db56e402fd2a2ec43019381c3e78395c"
)
STAGE_A_V16_SUCCESSOR_AUTHORITY_SHA256 = (
    "075821cda269fbde977110686c6e69925888e6ece4f299e6f7664dd83ff61578"
)
STAGE_A_V16_SUCCESSOR_AUTHORITY_REPORT_SHA256 = (
    "670d51bf6c6dad36fdc941e43c080d23e900fbf3344b87a205eef6d65601f213"
)
STAGE_A_V16_FINAL_AUTHORITY_MEMBER = (
    "history/internal_docs/"
    "goal5791_stage_a_archive_root_v16_final_successor_authority_20260820.json"
)
STAGE_A_V16_FINAL_AUTHORITY_REPORT_MEMBER = (
    "history/internal_docs/"
    "goal5791_stage_a_archive_root_v16_final_successor_authority_20260820.md"
)
STAGE_A_V16_FINAL_AUTHORITY_FILE_SHA256 = (
    "9cf2b12866839d4ee52cc192e9e6cdea1f9c19c252cdf3fbcf28d74a03667abf"
)
STAGE_A_V16_FINAL_AUTHORITY_SHA256 = (
    "964a0e64d958af9b8d52afaf8be81c78f0d87218956858c09b9e29781f33f80e"
)
STAGE_A_V16_FINAL_AUTHORITY_REPORT_SHA256 = (
    "98820bb60de127ea82b78a7ac56302a82d51127cbd19995e4a7f663401daeea5"
)
STAGE_A_V1_TERMINAL_MEMBER = (
    "history/internal_docs/"
    "goal5791_stage_a_v1_first_entry_zero_output_terminal_20260820.json"
)
STAGE_A_V2_TERMINAL_MEMBER = (
    "history/internal_docs/"
    "goal5791_stage_a_v2_upload_receipt_contract_terminal_20260820.json"
)
STAGE_A_V2_OPEN_RECEIPT_MEMBER = (
    "history/internal_docs/goal5791_stage_a_v2_failure_evidence_20260820/"
    "UPLOAD_STAGING_OPEN_RECEIPT.json"
)
CPU_TEST_GATE_MEMBER = "scripts/goal5791_cpu_test_gate.py"
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
EXPECTED_WORKSPACE_CPU_TEST_COUNT = 115
EXPECTED_CLEAN_CPU_TEST_COUNT = 109
CPU_TEST_TIMEOUT_SECONDS = 1200
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
FORMAL_CONTRACT_FILE_SHA256 = (
    "aa1a7189a9afc667d6fc9e5e6088e1f6aa262dabb91325177db3e35b5bb4284c"
)
FORMAL_CONTRACT_SHA256 = (
    "37e2752293b78041409ff946a6402479ec9c31d8173579a967ccb32c0cfc41ae"
)
SCHEDULE_SHA256 = (
    "4b6d119cc6bd8b5f0639c11642745accde4a7bfc26bf758a6f1c24cd9e7af58d"
)
FORMAL_WORKER_FILE_SHA256 = (
    "70d8623047d9f0d82229908cf71d78731a907a29a11b69292f9efbd71140c41b"
)
FORMAL_CONTROLLER_FILE_SHA256 = (
    "e2307b8bdb432688637aef6ea06425ba8df1369a3ec43d5837dae006e3bca068"
)
FORMAL_EVALUATE_FILE_SHA256 = (
    "b5d545762f79adc8f6844f770f55f2d87e9b7bf953ee3d5ebbf986200010f4af"
)
FORMAL_INDEPENDENT_RECOUNT_FILE_SHA256 = (
    "43d3be5bff769728c2492c808e05a943f6473bca940a39d023f0bf9d585be60c"
)
PAPER_OUTCOME_CONSEQUENCE_CONTRACT_SHA256 = (
    "8c9119f854f603ef9ac2898b0c92f2510b171d968c86eaf9a7f19fb34e3c518c"
)
TRACE_INSTRUMENTATION_CONTRACT_SHA256 = (
    "c79d398defe077a5d4016fb9f68243b423ae10b26da5d659c6686c38edb3f993"
)
PREREGISTRATION_V9_MEMBER = (
    "history/internal_docs/goal5791_preregistration_v9_20260820.json"
)
PREREGISTRATION_V9_FILE_SHA256 = (
    "4878e666695e513e47c2adad65869a1cde2640396b6afdcbcd1f493e8cc1495a"
)
PREREGISTRATION_V9_SHA256 = (
    "bef873db5c29a5d33cf22fad1d2dcda320ca41eda12b227b63a071134d63cfaf"
)
PRETARGET_V9_MEMBER = (
    "history/internal_docs/"
    "goal5791_pretarget_preexecution_authority_v9_20260820.json"
)
PRETARGET_V9_FILE_SHA256 = (
    "46fdb549f8397b361871a8dc1d5a6e7d6995903c9e0f1ba60ed2a7804ff0cfc1"
)
PRETARGET_V9_SHA256 = (
    "277087a9f1a2c1042e9a27d474d51d1679e583760b99716aaeb10d634d073a44"
)
APPEND_ONLY_CORRECTION_AUTHORITY_MEMBER = (
    "history/internal_docs/"
    "goal5791_append_only_record_reference_correction_authority_20260820.json"
)
APPEND_ONLY_CORRECTION_AUTHORITY_REPORT_MEMBER = (
    "history/internal_docs/"
    "goal5791_append_only_record_reference_correction_authority_20260820.md"
)
APPEND_ONLY_CORRECTION_AUTHORITY_FILE_SHA256 = (
    "b21a5728ebc73c2c9c36292817b292a83360b9673ca11112969c7247429288a4"
)
APPEND_ONLY_CORRECTION_AUTHORITY_SHA256 = (
    "a9ce2e3e08bf87a39c5a61709c545ab303cd924ce9b6cfd492f5da419a93a9a0"
)
APPEND_ONLY_CORRECTION_AUTHORITY_REPORT_SHA256 = (
    "dcdc2759ee3bc607f8801e9354b7052b259ec82274300d0ab872bfe7bd4113d0"
)
PAPER_OUTCOME_SUCCESSOR_AUTHORITY_MEMBER = (
    "history/internal_docs/"
    "goal5791_paper_outcome_consequence_selection_"
    "successor_authority_20260820.json"
)
PAPER_OUTCOME_SUCCESSOR_AUTHORITY_REPORT_MEMBER = (
    "history/internal_docs/"
    "goal5791_paper_outcome_consequence_selection_"
    "successor_authority_20260820.md"
)
PAPER_OUTCOME_SUCCESSOR_AUTHORITY_FILE_SHA256 = (
    "b38251247b6408ca3b1b34b51fd8b22c2cc079f80e3f28fb14b124106b5957ac"
)
PAPER_OUTCOME_SUCCESSOR_AUTHORITY_SHA256 = (
    "a0daac974c0955403f5f371e1529979e49e1caf0d05e6f1bb4840f69863528b7"
)
PAPER_OUTCOME_SUCCESSOR_AUTHORITY_REPORT_SHA256 = (
    "582a71d65b11595316626cb69b1fea23acc2637de1bcdd8fce6f92d7c8bab846"
)
PREREGISTRATION_V8_MEMBER = (
    "history/internal_docs/goal5791_preregistration_v8_20260820.json"
)
PREREGISTRATION_V8_FILE_SHA256 = (
    "b53da728fc73a2bcec680bb8be388cfc58fe8bf1ca136915ad2cada3aa61953f"
)
PREREGISTRATION_V8_SHA256 = (
    "55854d2ba06bf89993bd8a20cd390a266dd8141c708d8045b5d6dba99bb2dd37"
)
PRETARGET_V8_MEMBER = (
    "history/internal_docs/"
    "goal5791_pretarget_preexecution_authority_v8_20260820.json"
)
PRETARGET_V8_FILE_SHA256 = (
    "27873208bc7b34c62781286b79ac3d5497a305645fb404aa861b35b5a061449f"
)
PRETARGET_V8_SHA256 = (
    "741920a234153fb888d20de543f4fb9e89b411fb91433b7d4fa8b0eee49d5ab9"
)
OWNER_REVIEW_ABSORPTION_MEMBER = (
    "history/internal_docs/review_goal5791_project_state_review_absorption_"
    "20260819.md"
)
OWNER_REVIEW_ABSORPTION_FILE_SHA256 = (
    "1b0e8a4d66373f4bef2f05c9ba4344759b54e153f087fb65bb2ca02346d8c2b0"
)
SMALL_RELATIVE_ABSORPTION_MEMBER = (
    "history/internal_docs/"
    "goal5791_small_relative_claim_gate_review_absorption_20260819.json"
)
SMALL_RELATIVE_ABSORPTION_FILE_SHA256 = (
    "f8d68cb07821bf1c85c9ff375b9f70c560b5612d136b5bb6de5562321662ffee"
)
SMALL_RELATIVE_ABSORPTION_SHA256 = (
    "df4740c9f655accfe20c9eafca903247d1a9fc9a27efa9fb869b95c54afd1446"
)
CORRECTION_FORMAL_V1_TERMINAL_MEMBER = (
    "history/internal_docs/"
    "goal5791_formal_v1_worker1_numba_source_mutation_terminal_20260820.json"
)
CORRECTION_FORMAL_V1_TERMINAL_FILE_SHA256 = (
    "74e3084812ae0b4cd250b5a707bc3f1b8009d0113b2f1b8cd56e652fe9b1f1f4"
)
CORRECTION_FORMAL_V1_TERMINAL_SHA256 = (
    "dc5e0a74d512b24737938f77845faa9abce0e959afded562c4d03e307e6d5180"
)
V25_SUPPORT_CHAIN_TERMINAL_MEMBER = (
    "history/internal_docs/"
    "goal5791_portable_source_v25_support_chain_auditor_terminal_20260820.json"
)
V25_SUPPORT_CHAIN_TERMINAL_REPORT_MEMBER = (
    "history/internal_docs/"
    "goal5791_portable_source_v25_support_chain_auditor_terminal_20260820.md"
)
V25_SUPPORT_CHAIN_TERMINAL_FILE_SHA256 = (
    "4a07a409176fbb3ebb01a5241c1d71cfbc2e5d73f95d895f63ca995c1973df40"
)
V25_SUPPORT_CHAIN_TERMINAL_SHA256 = (
    "94c82ad21004a6972911a275b4182873d97e17b8fd239efd8519bac82f509071"
)
V25_SUPPORT_CHAIN_TERMINAL_REPORT_SHA256 = (
    "eff0696a24d65c0f5aac36cbb7a2665472dae573011cd1aa1789334ff31e421b"
)
TOKEN_AMENDMENT_PREDECESSOR_SHA256 = (
    "8d832bcc0c8e93d4b288d84f7eeaec36a109cd6cdfad922f9e61e5e39be4d4ca"
)
SOURCE_AUTHORITY_MEMBER = (
    "history/internal_docs/goal5791_successor_source_authority_v2_20260817.json"
)
A1_RESULT_MEMBER = (
    "history/internal_docs/"
    "goal5791_amendment_a1_pretimer_fusion_execution_token_result_20260817.json"
)
A2_RESULT_MEMBER = (
    "history/internal_docs/"
    "goal5791_amendment_a2_segment_plan_input_token_binding_result_20260817.json"
)
V4_LINEAGE_AUTHORITY_MEMBER = (
    "history/internal_docs/"
    "goal5791_v4_successor_lineage_authority_20260817.json"
)
EXPECTED_EXTERNAL_UPLOADS = {
    "data_bundle_sha256": (
        "f186cd28a5ae767f968eaa1372cd66285934be430bceb77ff14c6cf94e33e6eb"),
    "wheelhouse_sha256": (
        "d0c0f75365a78792cf0c2f548e0bdd144f0ad7175e0d8f83efcf335eb3b311f3"),
    "optix_headers_sha256": (
        "7fae86ce3dca2fbc2a47be075f02465cf6ee9d9eafd204234f2882fbdeebee54"),
}
BASE_SOURCE_MANIFEST_MEMBER = (
    "history/internal_docs/goal5790_a1_portable_source_manifest_v4_20260816.json"
)
PRESERVED_BASE_MANIFEST_MEMBER = (
    "history/internal_docs/"
    "goal5791_frozen_goal5790_a1_v4_base_manifest_20260817.json"
)
SOURCE_MANIFEST_KEYS = frozenset({
    "schema", "goal", "status", "base_source_archive_sha256",
    "base_source_manifest_sha256", "base_source_tree_sha256",
    "base_source_file_count_excluding_manifest", "old_source_manifest_removed",
    "product_delta_paths", "product_delta",
    "nonproduct_overlay_count_including_builder", "deep_blob_audit",
    "manifest_is_non_self_referential", "file_count_excluding_this_manifest",
    "source_tree_sha256", "home_or_target_execution_count",
    "formal_worker_count", "registered_performance_timing_count", "files",
})
_HOME_ZERO_COUNT_KEYS = frozenset((
    "elapsed_value_count",
    "clock_sample_count",
    "reported_elapsed_value_count",
    "test_or_scientific_clock_sample_count",
    "registered_performance_timing_count",
))
_HOME_TRUE_OPERATIONAL_CLOCK_KEYS = frozenset((
    "operational_timeout_watchdog_uses_host_clock",
    "operational_watchdog_clock_not_persisted_or_registered",
))
_SOURCE_OPERATIONAL_TIMEOUT_FIELDS = {
    "cpu_test_timeout_seconds": 1_200,
}
_HOME_FALSE_OBSERVATION_KEYS = frozenset((
    "elapsed_values_recorded",
    "home_performance_observation_created",
    "home_performance_diagnostic_used",
    "registered_performance_timing_created",
    "performance_or_compiler_fusion_claimed",
    "performance_or_timing_claimed",
    "variant_selected_from_app_dataset_result_or_timing",
    "timing_or_duration_recorded",
    "performance_claimed",
    "performance_observation_created",
    "compiler_fusion_performance_demonstrated",
    "registered_performance_result_created",
    "home_timing_used_for_claim",
    "performance_evidence_included",
    "target_performance_observation",
    "evidence_hashing_or_serialization_inside_registered_timer",
    "registered_timing",
))
_HOME_TIMER_CONTRACT = {
    "schema": "rtdl.goal5791.home_zero_elapsed_observation.v1",
    "elapsed_value_count": 0,
    "clock_sample_count": 0,
    "home_performance_observation_created": False,
    "home_performance_diagnostic_used": False,
    "token_admission_before_device_geometry": True,
    "device_iterator_closed_before_evidence_seal": True,
}
_HOME_FORBIDDEN_OBSERVATION_KEY_TOKENS = (
    "elapsed", "clock", "duration", "timing", "timer", "timestamp",
    "monotonic", "perf_counter", "process_time", "wall_time", "latency",
    "throughput", "benchmark", "performance",
)
_HOME_FORBIDDEN_OBSERVATION_KEY_SUFFIXES = (
    "_started_ns", "_ended_ns", "_start_ns", "_end_ns",
    "_seconds", "_milliseconds", "_microseconds", "_nanoseconds",
)
HOME_FUNCTIONAL_CLOSURE_KEYS = frozenset("""
schema status execution_source_archive_sha256 execution_source_tree_sha256
source_manifest_sha256 native_library_sha256
target_materialization_receipt_sha256 target_materialization_evidence_sha256
home_evidence_sha256 home_evidence_twin_sha256 home_evidence_twin_byte_identical
home_evidence_manifest_sha256 home_evidence_independent_audit_sha256
home_evidence_payload_count gpu home_machine_authority ptx_producer_toolchain_files
ptx_producer_observation home_qualification_dependency_identity
home_qualification_identity_is_not_cross_environment_reproducibility
ptx_producer_open_audit ptx_program_identity_sha256
home_functional_lane_count small_lane_count bounded_real_lane_count exact_lane_count
behavioral_true_optix_lane_count token_only_lane_count fresh_parent_pid_count
operation_receipt_count successful_operation_event_count_by_variant
event_count_per_receipt all_tokens_admitted_in_preparation
fresh_private_cupy_cache_per_lane cache_policy cache_policy_sha256 cold_definition
cold_claim_excludes operating_system_page_cache_controlled_or_dropped
operating_system_page_cache_scope cuda_driver_jit_cache_controlled_or_isolated
optix_disk_cache_controlled_or_isolated
round_major_abba_is_uncontrolled_cache_mitigation_not_control
independent_simple_undirected_oracle_recomputed_from_raw_edges
independently_recounted_inputs legacy_execution_path_used
exact_source_and_native_preserved_before_first_lane
source_manifest_payloads_read_only_before_first_lane
source_manifest_fully_rehashed_after_functional_lanes
source_exact_set_before_first_lane
source_exact_set_and_all_tree_paths_read_only_after_lanes formal_worker_count
registered_performance_timing_count elapsed_value_count clock_sample_count
home_performance_observation_created home_performance_diagnostic_used
performance_or_compiler_fusion_claimed pod_used prebuilt_target_native_used
private_codex_dependency_used
formal_worker_environment_contract_sha256 home_locale_matches_formal_environment_contract
source_admission_policy_sha256
""".split())
HOME_EXTERNAL_EVIDENCE_HASH_KEYS = frozenset({
    "home_evidence_sha256", "home_evidence_twin_sha256",
    "home_evidence_twin_byte_identical", "home_evidence_manifest_sha256",
    "home_evidence_independent_audit_sha256",
})
HOME_EVIDENCE_BOUND_CLOSURE_KEYS = (
    HOME_FUNCTIONAL_CLOSURE_KEYS - HOME_EXTERNAL_EVIDENCE_HASH_KEYS
)
SHARED_FREEZE_MEMBER = (
    "history/internal_docs/goal5789_contract_evidence_20260816/"
    "GOAL5789_GOAL5790_SHARED_CONTRACT_FREEZE.json"
)
HOME_AUTHORITY_MEMBER = (
    "history/internal_docs/goal5790_frozen_home_machine_authority_20260816.json"
)
HOME_QUALIFICATION_DEPENDENCY_IDENTITY = {
    "python": "3.12.3",
    "numba": "0.65.1",
    "numpy": "2.4.4",
    "cupy": "14.0.1",
    "llvmlite": "0.47.0",
}
HOME_PTX_PRODUCER_OBSERVATION_KEYS = frozenset({
    "schema", "python", "numba", "numpy", "llvmlite", "cupy",
    "cuda_home", "cuda_path", "numba_selected_nvvm_by",
    "numba_selected_nvvm_path", "numba_selected_nvvm_sha256",
    "numba_selected_libdevice_by", "numba_selected_libdevice_path",
    "numba_selected_libdevice_sha256", "numba_probe_ptx_sha256",
    "numba_probe_ptx_directives", "loaded_nvvm_paths",
    "cupy_nvrtc_runtime_version", "nvrtc_probe_source_sha256",
    "nvrtc_probe_output", "loaded_nvrtc_family_paths",
    "elapsed_values_recorded", "application_input_used",
    "registered_performance_timing_created",
})
SOURCE_RECEIPT_KEYS = frozenset("""
schema goal status base_source_archive_path base_source_archive_sha256
base_source_manifest_sha256 base_source_tree_sha256 base_manifest_rehashed
preserved_base_manifest_member preserved_base_manifest_sha256 output_path twin_path
source_archive_sha256 source_archive_bytes source_twin_sha256
source_twin_byte_identical source_manifest_member source_manifest_sha256
source_manifest_non_self_referential source_tree_sha256
source_file_count_excluding_manifest archive_payload_count_including_manifest
archive_payload_bytes builder_path builder_sha256 overlay_sha256 product_delta
changed_product_file_count changed_native_file_count deep_blob_audit
unsafe_member_count prebuilt_native_or_device_binary_count nested_container_count
private_cache_member_count empty_directory_extract_rehash_passed
  clean_extraction_exact_set_before_tests clean_extraction_exact_set_after_tests
  cpu_test_gate_helper_member cpu_test_gate_helper_sha256
  workspace_cpu_test_gate_result clean_cpu_test_gate_result
  cpu_test_timeout_seconds
  home_or_target_execution_count gpu_execution_count
pod_execution_count formal_worker_count registered_performance_timing_count
reported_elapsed_value_count test_or_scientific_clock_sample_count
operational_timeout_watchdog_uses_host_clock
operational_watchdog_clock_not_persisted_or_registered
home_performance_observation_created
home_performance_diagnostic_used requires_fresh_home_token_path_qualification
requires_separate_owner_target_prepare_authority
requires_separate_postprepare_owner_formal_authority
performance_or_compiler_fusion_claimed
""".split())
BUNDLE_MANIFEST_KEYS = frozenset("""
schema goal status manifest_is_non_self_referential source_archive_sha256
source_tree_sha256 source_manifest_sha256 source_build_receipt_file_sha256
source_independent_audit_file_sha256 home_functional_closure_file_sha256
home_evidence_sha256 home_evidence_twin_sha256
home_evidence_independent_audit_file_sha256 home_evidence_manifest_sha256
home_functional_recount_sha256
home_independent_recount_reexecuted_and_byte_identical
formal_contract_file_sha256 formal_contract_sha256 schedule_sha256
token_amendment_sha256 token_amendment_chain_sha256 external_uploads
payload_count_excluding_manifest payload_bytes_excluding_manifest
source_is_only_nested_container source_deep_container_depth
contains_real_scale_data contains_wheelhouse contains_optix_headers
contains_prebuilt_target_native contains_owner_prepare_authority
contains_owner_formal_authority formal_worker_count_executed
registered_performance_timing_count elapsed_value_count clock_sample_count
home_performance_observation_created home_performance_diagnostic_used payloads
""".split())
HOME_EVIDENCE_MANIFEST_KEYS = frozenset("""
schema goal status manifest_is_non_self_referential
execution_source_archive_sha256 execution_source_tree_sha256
source_manifest_sha256 native_library_sha256 functional_recount_sha256
exact_lane_count behavioral_true_optix_lane_count token_only_lane_count
payload_count_excluding_manifest payload_bytes_excluding_manifest
formal_worker_count registered_performance_timing_count elapsed_value_count
clock_sample_count home_performance_observation_created
home_performance_diagnostic_used pod_used home_functional_facts files
""".split())
HOME_RECOUNT_KEYS = frozenset("""
schema status execution_source_archive_sha256 execution_source_tree_sha256
native_library_sha256 raw_lane_count raw_lane_sha256 independently_recounted_inputs
independent_simple_undirected_oracle_recomputed_from_raw_edges exact_lane_count
behavioral_true_optix_lane_count token_only_lane_count
target_materialization_receipt_sha256 ptx_program_identity_sha256
fresh_parent_pid_count operation_receipt_count successful_operation_event_count
successful_launch_count raygen_invocation_count operation_receipt_count_by_variant
successful_operation_event_count_by_variant event_count_per_receipt
prepared_lane_count prepared_neutral_off_then_on_prewarm_count cache_policy_sha256
cold_definition cold_claim_excludes operating_system_page_cache_controlled_or_dropped
operating_system_page_cache_scope cuda_driver_jit_cache_controlled_or_isolated
optix_disk_cache_controlled_or_isolated formal_worker_count
registered_performance_timing_count performance_or_compiler_fusion_claimed
elapsed_value_count clock_sample_count home_performance_observation_created
home_performance_diagnostic_used product_or_execution_route_imported
controller_worker_evaluator_or_formal_recount_imported
""".split())
HOME_EVIDENCE_AUDIT_KEYS = frozenset("""
schema goal status kind archive_sha256 archive_bytes evidence_manifest_sha256
payload_count_including_manifest source native_library_sha256 raw_lane_count
independent_input_count maximum_nested_container_depth formal_worker_count
registered_performance_timing_count elapsed_value_count clock_sample_count
home_performance_observation_created home_performance_diagnostic_used
clean_extraction twin_sha256 twin_byte_identical
implementation_imports_primary_builder home_or_target_execution_count
pod_execution_count
""".split())
PRODUCT_DELTA = {
    "src/rtdsl/v4_operation_evidence.py": (
        "ff59cba24c7ae188e9f99c3a29a968e0ea83e465033084e81665ee3eff129026"),
    "src/rtdsl/v4_triangle_reduction_device_runtime.py": (
        "d045c9ce04e5b77bbb7785191cdd07d7430de97e7ffdd4f5e0c3a60937b6ba00"),
}
PRODUCT_DELTA_RECORDS = {
    "src/rtdsl/v4_operation_evidence.py": {
        "base_sha256": (
            "55aa2a2752914e393462fe501db8e22af1dcacce628ad09ea4d2d7903ca1c9e6"),
        "successor_sha256": PRODUCT_DELTA[
            "src/rtdsl/v4_operation_evidence.py"],
    },
    "src/rtdsl/v4_triangle_reduction_device_runtime.py": {
        "base_sha256": (
            "bcaca714158eedafd102d73cb2ad0ec3b4c6efc7ec46fc2303d71c4d327a465e"),
        "successor_sha256": PRODUCT_DELTA[
            "src/rtdsl/v4_triangle_reduction_device_runtime.py"],
    },
}
EXPECTED_SOURCE_OVERLAY_PATHS = frozenset({
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
    "history/internal_docs/goal5791_v3_prereg_pretarget_terminal_supersession_authority_20260817.json",
    "history/internal_docs/goal5791_v3_prereg_pretarget_terminal_supersession_20260817.md",
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
})
OUTER_HARNESS_TO_SOURCE = {
    "HARNESS/CLEAN_VALIDATE.py": "scripts/goal5791_home_clean_validate.py",
    "HARNESS/HOME_TOKEN_WORKER.py": "scripts/goal5791_home_token_validation.py",
    "HARNESS/HOME_INDEPENDENT_RECOUNT.py": (
        "scripts/goal5791_independent_home_recount.py"),
    "HARNESS/INDEPENDENT_PORTABLE_AUDIT.py": (
        "scripts/goal5791_independent_portable_audit.py"),
    "HARNESS/TARGET_PREPARE.py": "scripts/goal5791_target_prepare.py",
    "HARNESS/TARGET_PRODUCER_PROBE.py": (
        "scripts/goal5791_target_producer_probe.py"),
    "HARNESS/OPEN_UPLOAD_STAGING.py": (
        "scripts/goal5791_open_upload_staging.py"),
    "HARNESS/OWNER_AUTHORITY_BUILDER.py": (
        "scripts/goal5791_build_owner_authority.py"),
    "HARNESS/FORMAL_CONTROLLER.py": "scripts/goal5791_formal_controller.py",
    "HARNESS/FORMAL_WORKER.py": "scripts/goal5791_formal_worker.py",
    "HARNESS/EVALUATE.py": "scripts/goal5791_formal_evaluate.py",
    "HARNESS/INDEPENDENT_RECOUNT.py": (
        "scripts/goal5791_formal_independent_recount.py"),
}
OUTER_TO_SOURCE_AUTHORITY_MEMBERS = {
    "CLAIM_AND_RELATED_WORK_FREEZE.json": (
        "history/internal_docs/"
        "goal5791_pre_worker_zero_related_work_and_claim_freeze_20260817.json"
    ),
    "EXPECTED_VALUE_AND_FALLBACK.json": (
        "history/internal_docs/"
        "goal5790_preregistered_expected_value_and_fallback_20260816.json"
    ),
    "PREREGISTRATION.json": (
        PREREGISTRATION_V9_MEMBER
    ),
    "PRETARGET_PREEXECUTION_AUTHORITY.json": (
        PRETARGET_V9_MEMBER
    ),
    "RUNTIME_BUDGET.json": (
        "history/internal_docs/"
        "goal5791_pre_pod_conservative_runtime_budget_20260817.json"
    ),
    "OWNER_AUTHORITY_REQUEST_PROTOCOL.md": (
        "history/internal_docs/"
        "goal5791_owner_authority_request_protocol_20260817.md"
    ),
}
BUNDLE_FIXED_PAYLOAD_MEMBERS = frozenset({
    "SOURCE.tar.gz",
    "SOURCE_BASE_AND_OVERLAY_AUTHORITY.json",
    "SOURCE_INDEPENDENT_AUDIT.json",
    "CLAIM_AND_RELATED_WORK_FREEZE.json",
    "SEMANTIC_PHYSICAL_VARIANT_SUCCESSOR_AUTHORITY.json",
    "EXPECTED_VALUE_AND_FALLBACK.json",
    "PREREGISTRATION.json",
    "PRETARGET_PREEXECUTION_AUTHORITY.json",
    "RUNTIME_BUDGET.json",
    "OWNER_AUTHORITY_REQUEST_PROTOCOL.md",
    "HOME_FUNCTIONAL_CLOSURE.json",
    "HOME_EVIDENCE_MANIFEST.json",
    "HOME_EVIDENCE_INDEPENDENT_AUDIT.json",
    "HOME_FUNCTIONAL_RECOUNT.json",
    "README.md",
})
EXPECTED_BUNDLE_PAYLOAD_MEMBERS = (
    BUNDLE_FIXED_PAYLOAD_MEMBERS | frozenset(OUTER_HARNESS_TO_SOURCE)
)
EXPECTED_BUNDLE_OUTER_MEMBERS = (
    EXPECTED_BUNDLE_PAYLOAD_MEMBERS | {"BUNDLE_MANIFEST.json"}
)
EXPECTED_HOME_RAW_MEMBERS = frozenset({
    "RAW/bounded_real__cit-Patents__bounded_smoke__fusion_off.json",
    "RAW/bounded_real__cit-Patents__bounded_smoke__fusion_on.json",
    "RAW/bounded_real__com-dblp__bounded_smoke__fusion_off.json",
    "RAW/bounded_real__com-dblp__bounded_smoke__fusion_on.json",
    "RAW/bounded_real__soc-LiveJournal1__bounded_smoke__fusion_off.json",
    "RAW/bounded_real__soc-LiveJournal1__bounded_smoke__fusion_on.json",
    "RAW/small__four_vertex_clique__cold__fusion_off.json",
    "RAW/small__four_vertex_clique__cold__fusion_on.json",
    "RAW/small__four_vertex_clique__prepared__fusion_off.json",
    "RAW/small__four_vertex_clique__prepared__fusion_on.json",
})
EXPECTED_HOME_INPUT_MEMBERS = frozenset({
    "INPUTS/bounded_real__cit-Patents.edge",
    "INPUTS/bounded_real__com-dblp.edge",
    "INPUTS/bounded_real__soc-LiveJournal1.edge",
    "INPUTS/small__four_vertex_clique.edge",
})
EXPECTED_TARGET_EVIDENCE_MEMBERS = frozenset({
    "EXECUTION_SOURCE.tar.gz",
    "TARGET_NATIVE/librtdl_optix.so",
    "TARGET_PROGRAM_INSPECTION.json",
    "SOURCE_MANIFEST.json",
    "SHARED_CONTRACT_FREEZE.json",
    "HOME_MACHINE_AUTHORITY.json",
    "PTX_PRODUCER_OPENAT_TRACE.log",
    "PTX_PRODUCER_OBSERVATION.json",
})
TARGET_AUTHORITY_KEYS = frozenset("""
schema shared_contract_freeze_sha256 execution_source_archive_sha256
execution_source_tree_sha256 callback_ir_sha256 callback_authority_nonce
contract_sha256 abi_sha256 provider_identity program_bundle_identity
composed_program_sha256 cupy_version fusion_on_downstream_operation_recipe
fusion_off_downstream_operation_recipe
fusion_on_downstream_operation_recipe_sha256
fusion_off_downstream_operation_recipe_sha256 native_library_sha256
native_payload_sha256 target_identity_sha256 materializer_source_sha256
source_manifest_sha256 evidence_archive_sha256 materialization_nonce
actual_native_rehashed_from_preserved_payload
actual_source_tree_recounted_from_preserved_archive
cross_target_native_byte_reproducibility_claimed receipt_sha256
""".split())
TARGET_INSPECTION_KEYS = frozenset("""
schema provider_identity program_bundle_identity callback_ir_sha256
callback_authority_nonce contract_sha256 abi_sha256 composed_program_sha256
native_library_sha256 target_identity_sha256
fusion_on_downstream_operation_recipe fusion_off_downstream_operation_recipe
fusion_on_downstream_operation_recipe_sha256
fusion_off_downstream_operation_recipe_sha256 cupy_version
application_worker_executed optix_launch_executed
registered_performance_timing_created home_machine_authority
home_machine_authority_sha256 ptx_producer_toolchain
ptx_producer_observation ptx_program_identity ptx_program_identity_sha256
goal5791_token_api_present
""".split())
FORBIDDEN_PARTS = frozenset((".codex", ".git", "__pycache__", "build"))
FORBIDDEN_SUFFIXES = (
    ".pyc", ".pyo", ".so", ".dll", ".dylib", ".pyd", ".cubin",
    ".ptx", ".o", ".obj", ".a", ".lib", ".exe",
)
CONTAINER_SUFFIXES = (
    ".tar.gz", ".tgz", ".tar", ".zip", ".7z", ".rar", ".gz",
    ".bz2", ".xz",
)


class IndependentPortableAuditError(RuntimeError):
    pass


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _digest(value: object) -> str:
    return _sha_bytes(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8"))


def _strict_json_bytes(data: bytes, label: str) -> dict[str, object]:
    def pairs(rows):
        value = {}
        for key, item in rows:
            if key in value:
                raise IndependentPortableAuditError(
                    f"duplicate JSON key in {label}: {key}")
            value[key] = item
        return value

    try:
        value = json.loads(
            data.decode("utf-8"), object_pairs_hook=pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                IndependentPortableAuditError(
                    f"non-finite JSON constant in {label}: {token}")),
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise IndependentPortableAuditError(
            f"cannot parse strict JSON: {label}") from exc
    if not isinstance(value, dict):
        raise IndependentPortableAuditError(f"expected JSON object: {label}")
    return value


def _require_goal_5791(value: dict[str, object], *, label: str) -> None:
    if type(value.get("goal")) is not int or value.get("goal") != 5791:
        raise IndependentPortableAuditError(f"{label} Goal identity drifted")


def _frozen_cpu_test_gate_contract(
    *, builder_bytes: bytes, helper_bytes: bytes,
) -> dict[str, object]:
    names = frozenset({
        "WORKSPACE_CPU_TEST_MODULES", "EXPECTED_WORKSPACE_CPU_TEST_COUNT",
        "CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS",
        "EXPECTED_CLEAN_CPU_TEST_COUNT", "CPU_TEST_TIMEOUT_SECONDS",
        "CPU_TEST_GATE_MEMBER", "WORKSPACE_CPU_TEST_MODULES_SHA256",
        "EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256",
        "CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256",
        "EXPECTED_CLEAN_CPU_TEST_IDS_SHA256",
        "CPU_TEST_ENVIRONMENT_CONTRACT",
    })
    builder = _literal_contract_values(builder_bytes, names)
    helper_names = frozenset({
        "SCHEMA", "WORKSPACE_CPU_TEST_MODULES",
        "EXPECTED_WORKSPACE_CPU_TEST_COUNT",
        "CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS",
        "EXPECTED_CLEAN_CPU_TEST_COUNT", "WORKSPACE_CPU_TEST_MODULES_SHA256",
        "EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256",
        "CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256",
        "EXPECTED_CLEAN_CPU_TEST_IDS_SHA256", "ENVIRONMENT_CONTRACT",
    })
    helper = _literal_contract_values(helper_bytes, helper_names)
    expected = {
        "WORKSPACE_CPU_TEST_MODULES": WORKSPACE_CPU_TEST_MODULES,
        "EXPECTED_WORKSPACE_CPU_TEST_COUNT": EXPECTED_WORKSPACE_CPU_TEST_COUNT,
        "CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS": (
            CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS),
        "EXPECTED_CLEAN_CPU_TEST_COUNT": EXPECTED_CLEAN_CPU_TEST_COUNT,
        "CPU_TEST_TIMEOUT_SECONDS": CPU_TEST_TIMEOUT_SECONDS,
        "CPU_TEST_GATE_MEMBER": CPU_TEST_GATE_MEMBER,
        "WORKSPACE_CPU_TEST_MODULES_SHA256": (
            WORKSPACE_CPU_TEST_MODULES_SHA256),
        "EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256": (
            EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256),
        "CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256": (
            CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256),
        "EXPECTED_CLEAN_CPU_TEST_IDS_SHA256": (
            EXPECTED_CLEAN_CPU_TEST_IDS_SHA256),
        "CPU_TEST_ENVIRONMENT_CONTRACT": CPU_TEST_ENVIRONMENT_CONTRACT,
    }
    expected_helper = {
        "SCHEMA": "rtdl.goal5791.cpu_test_gate_result.v2",
        "WORKSPACE_CPU_TEST_MODULES": WORKSPACE_CPU_TEST_MODULES,
        "EXPECTED_WORKSPACE_CPU_TEST_COUNT": EXPECTED_WORKSPACE_CPU_TEST_COUNT,
        "CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS": (
            CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS),
        "EXPECTED_CLEAN_CPU_TEST_COUNT": EXPECTED_CLEAN_CPU_TEST_COUNT,
        "WORKSPACE_CPU_TEST_MODULES_SHA256": (
            WORKSPACE_CPU_TEST_MODULES_SHA256),
        "EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256": (
            EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256),
        "CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256": (
            CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256),
        "EXPECTED_CLEAN_CPU_TEST_IDS_SHA256": (
            EXPECTED_CLEAN_CPU_TEST_IDS_SHA256),
        "ENVIRONMENT_CONTRACT": CPU_TEST_ENVIRONMENT_CONTRACT,
    }
    if builder != expected or helper != expected_helper \
            or len(WORKSPACE_CPU_TEST_MODULES) != 11 \
            or len(CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS) != 6 \
            or len(set(CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS)) != 6 \
            or _digest(list(WORKSPACE_CPU_TEST_MODULES)) \
                != WORKSPACE_CPU_TEST_MODULES_SHA256 \
            or _digest(list(CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS)) \
                != CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256:
        raise IndependentPortableAuditError(
            "portable CPU test gate frozen contract drifted")
    return expected


def _validate_cpu_test_gate_result(
    value: object, *, scope: str,
) -> None:
    keys = {
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
    }
    if not isinstance(value, dict) or set(value) != keys:
        raise IndependentPortableAuditError(
            "portable CPU test gate result exact keys drifted")
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
        raise IndependentPortableAuditError(
            "portable CPU test gate ID shape drifted")
    clean_ids = [
        item for item in full_ids
        if item not in set(CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS)
    ]
    expected_selected = full_ids if scope == "workspace" else clean_ids
    expected_count = (
        EXPECTED_WORKSPACE_CPU_TEST_COUNT
        if scope == "workspace" else EXPECTED_CLEAN_CPU_TEST_COUNT)
    expected_digest = (
        EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256
        if scope == "workspace" else EXPECTED_CLEAN_CPU_TEST_IDS_SHA256)
    expected_result = {
        "testsRun": expected_count,
        "failures": 0,
        "errors": 0,
        "skipped": 0,
        "expectedFailures": 0,
        "unexpectedSuccesses": 0,
    }
    result = value.get("test_result")
    empty_outcomes = {
        "failures": [], "errors": [], "skipped": [],
        "expectedFailures": [], "unexpectedSuccesses": [],
    }
    if scope not in {"workspace", "clean"} \
            or value.get("schema") \
                != "rtdl.goal5791.cpu_test_gate_result.v2" \
            or value.get("scope") != scope \
            or value.get("python_role") != "current_interpreter" \
            or value.get("entrypoint") != CPU_TEST_GATE_MEMBER \
            or value.get("workspace_test_modules") \
                != list(WORKSPACE_CPU_TEST_MODULES) \
            or type(value.get("workspace_test_module_count")) is not int \
            or value.get("workspace_test_module_count") != 11 \
            or value.get("workspace_test_modules_sha256") \
                != WORKSPACE_CPU_TEST_MODULES_SHA256 \
            or type(value.get("discovered_workspace_test_count")) is not int \
            or value.get("discovered_workspace_test_count") \
                != EXPECTED_WORKSPACE_CPU_TEST_COUNT \
            or len(full_ids) != EXPECTED_WORKSPACE_CPU_TEST_COUNT \
            or _digest(full_ids) != EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256 \
            or value.get("discovered_workspace_test_ids_sha256") \
                != EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256 \
            or excluded_ids != list(CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS) \
            or type(value.get("excluded_external_only_test_count")) is not int \
            or value.get("excluded_external_only_test_count") != 6 \
            or _digest(excluded_ids) \
                != CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256 \
            or value.get("excluded_external_only_test_ids_sha256") \
                != CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256 \
            or not set(excluded_ids).issubset(full_ids) \
            or len(clean_ids) != EXPECTED_CLEAN_CPU_TEST_COUNT \
            or _digest(clean_ids) != EXPECTED_CLEAN_CPU_TEST_IDS_SHA256 \
            or selected_ids != expected_selected \
            or type(value.get("selected_test_count")) is not int \
            or value.get("selected_test_count") != expected_count \
            or value.get("selected_test_ids_sha256") != expected_digest \
            or _digest(selected_ids) != expected_digest \
            or value.get("environment_contract") \
                != CPU_TEST_ENVIRONMENT_CONTRACT \
            or not isinstance(result, dict) \
            or set(result) != set(expected_result) \
            or any(type(result.get(key)) is not int for key in expected_result) \
            or result != expected_result \
            or value.get("outcome_test_ids") != empty_outcomes \
            or value.get("outcome_test_ids_sha256") != _digest(empty_outcomes) \
            or value.get("failure_test_ids") != [] \
            or value.get("error_test_ids") != [] \
            or value.get("failure_exception_summaries") != [] \
            or value.get("error_exception_summaries") != [] \
            or value.get("success") is not True \
            or any(type(value.get(key)) is not int or value.get(key) != 0
                   for key in (
                       "reported_elapsed_value_count",
                       "test_or_scientific_clock_sample_count",
                       "registered_performance_timing_count")):
        raise IndependentPortableAuditError(
            "portable CPU test gate result identity/count drifted")
    if value.get("operational_timeout_watchdog_uses_host_clock") is not True \
            or value.get(
                "operational_watchdog_clock_not_persisted_or_registered") \
                is not True:
        raise IndependentPortableAuditError(
            "portable CPU test gate watchdog disclosure drifted")


def _validate_source_receipt_governance(
    receipt: dict[str, object], *, builder_bytes: bytes, helper_bytes: bytes,
) -> None:
    _frozen_cpu_test_gate_contract(
        builder_bytes=builder_bytes, helper_bytes=helper_bytes)
    _require_goal_5791(receipt, label="portable source receipt")
    if receipt.get("base_source_archive_path") != BASE_SOURCE_ARCHIVE_PATH \
            or receipt.get("output_path") != CANONICAL_SOURCE_OUTPUT_PATH \
            or receipt.get("twin_path") != CANONICAL_SOURCE_TWIN_PATH \
            or receipt.get("schema") \
                != "rtdl.goal5791.portable_source_build_receipt.v26" \
            or receipt.get("cpu_test_gate_helper_member") \
                != CPU_TEST_GATE_MEMBER \
            or receipt.get("cpu_test_gate_helper_sha256") \
                != _sha_bytes(helper_bytes) \
            or type(receipt.get("cpu_test_timeout_seconds")) is not int \
            or receipt.get("cpu_test_timeout_seconds") \
                != CPU_TEST_TIMEOUT_SECONDS \
            or type(receipt.get("reported_elapsed_value_count")) is not int \
            or receipt.get("reported_elapsed_value_count") != 0 \
            or type(receipt.get(
                "test_or_scientific_clock_sample_count")) is not int \
            or receipt.get("test_or_scientific_clock_sample_count") != 0 \
            or receipt.get(
                "operational_timeout_watchdog_uses_host_clock") is not True \
            or receipt.get(
                "operational_watchdog_clock_not_persisted_or_registered") \
                is not True:
        raise IndependentPortableAuditError(
            "portable source receipt governance/CPU gate binding drifted")
    _validate_cpu_test_gate_result(
        receipt.get("workspace_cpu_test_gate_result"), scope="workspace")
    _validate_cpu_test_gate_result(
        receipt.get("clean_cpu_test_gate_result"), scope="clean")


def _validate_v1_zero_output_terminal(payloads: dict[str, bytes]) -> None:
    value = _strict_json_bytes(
        payloads[V1_ZERO_OUTPUT_TERMINAL_MEMBER],
        V1_ZERO_OUTPUT_TERMINAL_MEMBER,
    )
    if set(value) != {
        "attempt_identity", "authorization", "failure", "goal",
        "observed_at", "output_facts", "schema", "status",
        "successor_policy", "terminal_authority_sha256",
        "zero_execution_facts",
    }:
        raise IndependentPortableAuditError(
            "portable-source v1 terminal authority keys drifted")
    unsigned = dict(value)
    claimed = unsigned.pop("terminal_authority_sha256", None)
    expected_outputs = {
        "build_receipt": {
            "exists": False,
            "path": (
                "history/internal_docs/"
                "goal5791_portable_source_v1_build_receipt_20260817.json"),
            "sha256": None, "size_bytes": None,
        },
        "source_archive": {
            "exists": False,
            "path": (
                "history/internal_docs/"
                "goal5791_portable_source_v1_20260817.tar.gz"),
            "sha256": None, "size_bytes": None,
        },
        "source_twin": {
            "exists": False,
            "path": (
                "history/internal_docs/"
                "goal5791_portable_source_v1_twin_20260817.tar.gz"),
            "sha256": None, "size_bytes": None,
        },
    }
    if claimed != _digest(unsigned) \
            or value.get("schema") \
                != "rtdl.goal5791.portable_source_v1_zero_output_terminal.v1" \
            or value.get("goal") != 5791 \
            or value.get("status") \
                != "TERMINAL_ZERO_OUTPUT__CPU_SUITE_TIMEOUT_BEFORE_PUBLICATION" \
            or value.get("observed_at") != "2026-08-17T11:26:09-04:00" \
            or value.get("attempt_identity") != {
                "base_source_archive_sha256": BASE_SOURCE_SHA256,
                "builder_file_sha256": V1_TERMINAL_BUILDER_SHA256,
                "builder_path": "scripts/goal5791_build_portable_source.py",
                "cpu_test_module_count": 11,
                "cpu_test_timeout_seconds": 600,
                "expected_cpu_test_count": 111,
            } \
            or value.get("failure") != {
                "claim_111_tests_passed": False,
                "exception_class": "subprocess.TimeoutExpired",
                "exception_message": (
                    "clean-extracted unittest command timed out after 600 seconds"),
                "failure_stage": (
                    "clean_extracted_cpu_suite_before_any_canonical_output_write"),
                "full_suite_stdout_available": False,
                "number_of_tests_completed_known": False,
                "test_assertion_outcome_known": False,
            } \
            or value.get("output_facts") != expected_outputs \
            or value.get("successor_policy") != {
                "only_distinct_v2_canonical_paths_may_be_used": True,
                "successor_cpu_test_timeout_seconds": 1200,
                "successor_requires_fresh_hash_and_hostile_review_before_build": True,
                "v1_may_never_be_retried_or_selected": True,
            } \
            or value.get("authorization") != {
                "authorizes_bundle_build": False,
                "authorizes_candidate_selection": False,
                "authorizes_formal_worker_zero": False,
                "authorizes_home_execution": False,
                "authorizes_pod_connection": False,
                "authorizes_registered_timing": False,
                "authorizes_retry_of_v1": False,
                "authorizes_stage_a": False,
                "authorizes_stage_b": False,
                "authorizes_target_prepare": False,
            } \
            or value.get("zero_execution_facts") != {
                "bundle_created": False,
                "formal_worker_count": 0,
                "home_execution_count": 0,
                "pod_connection_count": 0,
                "registered_performance_timing_count": 0,
                "source_candidate_created": False,
                "target_prepare_execution_count": 0,
            }:
        raise IndependentPortableAuditError(
            "portable-source v1 zero-output terminal lineage drifted")


def _validate_v2_zero_output_terminal(payloads: dict[str, bytes]) -> None:
    raw = payloads[V2_ZERO_OUTPUT_TERMINAL_MEMBER]
    report = payloads[V2_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER]
    value = _strict_json_bytes(raw, V2_ZERO_OUTPUT_TERMINAL_MEMBER)
    unsigned = dict(value)
    claimed = unsigned.pop("terminal_authority_sha256", None)
    failure_pairs = tuple(
        (item.get("test_id"), item.get("missing_relative_path"))
        for item in value.get("failure_cases", [])
        if isinstance(item, dict)
    )
    expected_pairs = (
        (
            "tests.goal5791_data_oracle_authority_test."
            "Goal5791DataOracleAuthorityTest."
            "test_bundle_manifest_datasets_oracles_and_non_authorization",
            "history/internal_docs/goal5784_targeted_data_bundle_v1_20260814.tar.gz",
        ),
        (
            "tests.goal5791_portable_home_harness_test."
            "Goal5791PortableHomeHarnessTest."
            "test_target_pre_root_source_audit_is_pure_memory",
            "history/internal_docs/goal5790_a1_portable_source_v4_20260816.tar.gz",
        ),
        (
            "tests.goal5791_pre_pod_base_budget_audit_test."
            "Goal5791PrePodBaseBudgetAuditTest."
            "test_budget_rebuilds_from_frozen_goal5784_and_goal5785_raw",
            "history/internal_docs/goal5784_a3_v5_raw_preservation_20260815.tar.gz",
        ),
        (
            "tests.goal5791_pre_pod_base_budget_audit_test."
            "Goal5791PrePodBaseBudgetAuditTest."
            "test_selected_a1_v4_base_rehashes_and_manifest_recounts",
            "history/internal_docs/goal5790_a1_portable_source_v4_20260816.tar.gz",
        ),
        (
            "tests.goal5791_pre_pod_base_budget_audit_test."
            "Goal5791PrePodBaseBudgetAuditTest."
            "test_v8_nested_elf_rejection_reproduces",
            "history/internal_docs/goal5790_portable_source_v8_20260816.tar.gz",
        ),
        (
            "tests.goal5791_pre_worker_zero_claim_freeze_test."
            "Goal5791PreWorkerZeroClaimFreezeTest."
            "test_a1_raw_rejects_prove_five_facade_plus_one_tps",
            "history/internal_docs/goal5790_a1_home_s3_execution_evidence_staging_20260816/controller/RAW/builtin_triangle__checked_u64_overflow__v1__product_admission_reject.json",
        ),
        (
            "tests.goal5791_pre_worker_zero_claim_freeze_test."
            "Goal5791PreWorkerZeroClaimFreezeTest."
            "test_p3_wording_and_bounded_anti_circularity_reconstruct",
            "history/internal_docs/goal5790_a1_home_s3_execution_evidence_staging_20260816/pre_run/AUDIT/PRE_RUN_SOURCE/src/rtdsl/v4_semantic_physical_admission.py",
        ),
        (
            "tests.goal5791_pretimer_execution_token_amendment_test."
            "Goal5791PretimerExecutionTokenAmendmentTest."
            "test_selected_base_and_append_only_product_lineage_are_exact",
            "history/internal_docs/goal5790_a1_portable_source_v4_20260816.tar.gz",
        ),
        (
            "tests.goal5791_pre_worker_zero_claim_freeze_test."
            "Goal5791PreWorkerZeroClaimFreezeTest."
            "test_every_controlling_predecessor_rehashes",
            "history/internal_docs/v4_competitive_cgo_submission_work_plan_after_goal5788_20260816.md",
        ),
    )
    output_facts = value.get("output_facts")
    if _sha_bytes(raw) != V2_ZERO_OUTPUT_TERMINAL_SHA256 \
            or _sha_bytes(report) != V2_ZERO_OUTPUT_TERMINAL_REPORT_SHA256 \
            or set(value) != {
                "attempt_identity", "authorization", "failure_cases", "goal",
                "terminal_record_created_at", "output_facts", "schema", "status",
                "suite_outcome", "successor_policy", "terminal_authority_sha256",
                "zero_execution_facts",
            } \
            or claimed != V2_ZERO_OUTPUT_TERMINAL_INTERNAL_SHA256 \
            or claimed != _digest(unsigned) \
            or value.get("schema") \
                != "rtdl.goal5791.portable_source_v2_zero_output_terminal.v1" \
            or value.get("goal") != 5791 \
            or value.get("status") \
                != "TERMINAL_ZERO_OUTPUT__CLEAN_SOURCE_SUITE_FAILED_BEFORE_PUBLICATION" \
            or value.get("suite_outcome") != {
                "error_count": 8, "failure_count": 1,
                "reported_test_count": 112,
                "reported_unittest_seconds": 639.576,
                "result": "FAILED", "timeout_expired": False,
            } \
            or failure_pairs != expected_pairs \
            or not isinstance(output_facts, dict) \
            or set(output_facts) != {"build_receipt", "source_archive", "source_twin"} \
            or any(not isinstance(item, dict) or item.get("exists") is not False
                   or item.get("sha256") is not None
                   or item.get("size_bytes") is not None
                   for item in output_facts.values()) \
            or not isinstance(value.get("authorization"), dict) \
            or any(item is not False
                   for item in value["authorization"].values()) \
            or value.get("zero_execution_facts") != {
                "bundle_created": False, "formal_worker_count": 0,
                "home_execution_count": 0, "pod_connection_count": 0,
                "registered_performance_timing_count": 0,
                "source_candidate_created": False,
                "target_prepare_execution_count": 0,
            }:
        raise IndependentPortableAuditError(
            "portable-source v2 zero-output terminal lineage drifted")


def _validate_dual_cpu_gate_successor_authority(
    payloads: dict[str, bytes],
) -> None:
    raw = payloads[DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_MEMBER]
    report = payloads[DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_REPORT_MEMBER]
    value = _strict_json_bytes(raw, DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_MEMBER)
    unsigned = dict(value)
    claimed = unsigned.pop("authority_sha256", None)
    # Historical v3 froze helper-v1 and the five then-current formal files at
    # these same lexical paths.  A post-review successor intentionally carries
    # newer bytes; those current bytes are bound by the successor authority and
    # receipt, not retroactively substituted into this append-only v3 record.
    helper_sha = V3_CPU_TEST_GATE_HELPER_SHA256
    formal = {
        "scripts/goal5791_formal_contract.py": (
            HISTORICAL_V3_FORMAL_CONTRACT_FILE_SHA256),
        "scripts/goal5791_formal_controller.py": (
            "e6335afb12728c873af2299228f2a969b105d68295cb318345628b2385aa3e5c"),
        "scripts/goal5791_formal_evaluate.py": (
            "2f6807096c937ebf59b200cb7cd010fc44446e994bf032f0b1cd923e1bc418be"),
        "scripts/goal5791_formal_independent_recount.py": (
            "b69b90c7c65705eb09b9e67559c3171c3d0a8b6baddbc63b62601c608c3ec2f8"),
        "scripts/goal5791_formal_worker.py": (
            "7f566594356d4fe5abb4d28eb78ebf99298d1782d30ab6bc18bc86c6e407b020"),
    }
    gate = value.get("test_gate")
    if _sha_bytes(raw) != DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_FILE_SHA256 \
            or _sha_bytes(report) \
                != DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_REPORT_SHA256 \
            or set(value) != {
                "authority_sha256", "authorization", "builder_binding",
                "formal_frozen_source_sha256", "formal_identity", "goal",
                "recorded_date", "resolution", "schema", "status", "test_gate",
                "v2_terminal", "work_plan", "zero_execution_facts",
            } \
            or claimed != DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_SHA256 \
            or claimed != _digest(unsigned) \
            or value.get("schema") \
                != "rtdl.goal5791.portable_source_v3_dual_cpu_gate_successor_authority.v1" \
            or value.get("goal") != 5791 \
            or value.get("status") \
                != "PREEXECUTION_DUAL_CPU_GATE_SUCCESSOR__NO_BUILD_AUTHORIZATION" \
            or value.get("formal_frozen_source_sha256") != formal \
            or value.get("formal_identity") != {
                "formal_contract_sha256": HISTORICAL_V3_FORMAL_CONTRACT_SHA256,
                "schedule_sha256": SCHEDULE_SHA256,
            } \
            or value.get("builder_binding") != {
                "final_v3_builder_is_bound_by_source_receipt_manifest_and_external_source_sha256": True,
                "final_v3_builder_sha256_is_not_embedded_here_to_avoid_builder_authority_hash_cycle": True,
                "predecessor_reviewed_builder_sha256": (
                    "78f66756f9f410c7e24d822e8c0de8e15a745801a2f54af85b13522e08d4ab1c"),
            } \
            or value.get("resolution") != {
                "clean_gate_coverage_is_not_reduced": True,
                "portable_authority_assertions_are_folded_into_existing_included_resign_test": True,
                "v2_minimum_107_was_a_nonbinding_recommendation_that_assumed_one_new_test_method": True,
                "v3_adds_no_test_method_and_preserves_the_same_workspace_flatten_of_112": True,
            } \
            or not isinstance(gate, dict) \
            or gate.get("workspace_test_modules") \
                != list(WORKSPACE_CPU_TEST_MODULES) \
            or gate.get("workspace_test_module_count") != 11 \
            or gate.get("workspace_test_modules_sha256") \
                != WORKSPACE_CPU_TEST_MODULES_SHA256 \
            or gate.get("workspace_discovered_test_count") \
                != HISTORICAL_V3_WORKSPACE_CPU_TEST_COUNT \
            or gate.get("workspace_discovered_test_ids_sha256") \
                != HISTORICAL_V3_WORKSPACE_CPU_TEST_IDS_SHA256 \
            or gate.get("clean_external_only_excluded_test_ids") \
                != list(CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS) \
            or gate.get("clean_external_only_excluded_test_count") != 6 \
            or gate.get("clean_external_only_excluded_test_ids_sha256") \
                != CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256 \
            or gate.get("clean_selected_test_count") \
                != HISTORICAL_V3_CLEAN_CPU_TEST_COUNT \
            or gate.get("clean_selected_test_ids_sha256") \
                != HISTORICAL_V3_CLEAN_CPU_TEST_IDS_SHA256 \
            or gate.get("cpu_test_gate_helper_path") != CPU_TEST_GATE_MEMBER \
            or gate.get("cpu_test_gate_helper_sha256") != helper_sha \
            or gate.get("timeout_seconds_per_gate") != 1200 \
            or gate.get(
                "operational_timeout_watchdog_uses_host_clock") is not True \
            or gate.get(
                "operational_watchdog_clock_not_persisted_or_registered") \
                is not True \
            or type(gate.get("reported_elapsed_value_count")) is not int \
            or gate.get("reported_elapsed_value_count") != 0 \
            or type(gate.get(
                "test_or_scientific_clock_sample_count")) is not int \
            or gate.get("test_or_scientific_clock_sample_count") != 0 \
            or gate.get("gpu_disabled_environment") \
                != CPU_TEST_ENVIRONMENT_CONTRACT \
            or value.get("v2_terminal") != {
                "file_sha256": V2_ZERO_OUTPUT_TERMINAL_SHA256,
                "internal_sha256": V2_ZERO_OUTPUT_TERMINAL_INTERNAL_SHA256,
                "path": V2_ZERO_OUTPUT_TERMINAL_MEMBER,
                "report_file_sha256": V2_ZERO_OUTPUT_TERMINAL_REPORT_SHA256,
                "report_path": V2_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER,
                "source_archive_twin_and_receipt_outputs_absent": True,
                "terminal_and_never_retried_or_selected": True,
            } \
            or value.get("work_plan") != {
                "bytes": 14622,
                "path": (
                    "history/internal_docs/"
                    "v4_competitive_cgo_submission_work_plan_after_goal5788_20260816.md"),
                "sha256": (
                    "b79dfda72bae430a2702210ccfe5d926967630048e350255136f3549ed98f1e7"),
            } \
            or not isinstance(value.get("authorization"), dict) \
            or any(item is not False
                   for item in value["authorization"].values()) \
            or value.get("zero_execution_facts") != {
                "bundle_created": False, "formal_worker_count": 0,
                "home_execution_count": 0, "pod_connection_count": 0,
                "registered_performance_timing_count": 0,
                "source_candidate_created": False,
                "target_prepare_execution_count": 0,
            }:
        raise IndependentPortableAuditError(
            "portable-source v3 dual CPU-gate successor authority drifted")


def _validate_v3_zero_output_terminal(payloads: dict[str, bytes]) -> None:
    raw = payloads[V3_ZERO_OUTPUT_TERMINAL_MEMBER]
    report = payloads[V3_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER]
    value = _strict_json_bytes(raw, V3_ZERO_OUTPUT_TERMINAL_MEMBER)
    unsigned = dict(value)
    claimed = unsigned.pop("terminal_authority_sha256", None)
    clean = value.get("clean_gate_observation")
    output_facts = value.get("output_facts_after_failure")
    if _sha_bytes(raw) != V3_ZERO_OUTPUT_TERMINAL_SHA256 \
            or _sha_bytes(report) != V3_ZERO_OUTPUT_TERMINAL_REPORT_SHA256 \
            or claimed != V3_ZERO_OUTPUT_TERMINAL_INTERNAL_SHA256 \
            or claimed != _digest(unsigned) \
            or set(value) != {
                "attempt_identity", "authorization", "clean_gate_observation",
                "failure", "goal", "output_facts_after_failure",
                "recorded_date", "schema", "status",
                "terminal_authority_sha256", "zero_execution_facts",
            } \
            or type(value.get("goal")) is not int or value.get("goal") != 5791 \
            or value.get("schema") \
                != "rtdl.goal5791.portable_source_v3_zero_output_terminal.v1" \
            or value.get("status") \
                != "TERMINAL_ZERO_OUTPUT__CLEAN_CPU_GATE_ONE_FAILURE_BEFORE_PUBLICATION" \
            or value.get("failure") != {
                "builder_failure_line_at_execution": 822,
                "exception_class": "RuntimeError",
                "failure_phase": "clean_cpu_test_gate",
                "process_exit_code": 1,
                "timeout_expired": False,
                "workspace_gate_passed_by_control_flow_before_clean_gate": True,
                "workspace_gate_result_not_persisted_because_no_receipt_was_published": True,
            } \
            or not isinstance(clean, dict) \
            or clean.get("clean_selected_test_count") \
                != HISTORICAL_V3_CLEAN_CPU_TEST_COUNT \
            or clean.get("clean_selected_test_ids_sha256") \
                != HISTORICAL_V3_CLEAN_CPU_TEST_IDS_SHA256 \
            or clean.get("result") != {
                "errors": 0, "expectedFailures": 0, "failures": 1,
                "skipped": 0, "testsRun": 106, "unexpectedSuccesses": 0,
            } \
            or clean.get("success") is not False \
            or clean.get("failure_test_id_recorded_by_v3_helper") is not False \
            or clean.get("failure_traceback_recorded_by_v3_helper") is not False \
            or clean.get("named_failure_test_id") is not None \
            or clean.get("named_failure_traceback") is not None \
            or clean.get("no_failure_identity_or_cause_is_inferred") is not True \
            or not isinstance(output_facts, dict) \
            or set(output_facts) != {
                "source_archive", "source_build_receipt", "source_twin"} \
            or any(not isinstance(item, dict)
                   or item.get("exists") is not False
                   or item.get("sha256") is not None
                   or item.get("size_bytes") is not None
                   for item in output_facts.values()) \
            or not isinstance(value.get("authorization"), dict) \
            or any(item is not False
                   for item in value["authorization"].values()) \
            or value.get("zero_execution_facts") != {
                "bundle_created": False, "formal_worker_count": 0,
                "home_execution_count": 0, "pod_connection_count": 0,
                "registered_performance_timing_count": 0,
                "reported_elapsed_value_count": 0,
                "source_candidate_created": False,
                "target_prepare_execution_count": 0,
                "test_or_scientific_clock_sample_count": 0,
            }:
        raise IndependentPortableAuditError(
            "portable-source v3 zero-output terminal lineage drifted")


def _validate_v4_clean_failure_successor_authority(
    payloads: dict[str, bytes],
) -> None:
    raw = payloads[V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_MEMBER]
    report = payloads[V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_REPORT_MEMBER]
    value = _strict_json_bytes(
        raw, V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_MEMBER)
    unsigned = dict(value)
    claimed = unsigned.pop("authority_sha256", None)
    missing = [
        {
            "bytes": 9906,
            "path": "history/internal_docs/goal5790_home_functional_closure_result_20260816.json",
            "sha256": "dfb1190b4c8880f41dcc5bb7c4c8583a9ff7a6eb1e197e711512020c8c89c20a",
        },
        {
            "bytes": 11384,
            "path": "history/internal_docs/goal5790_same_source_same_cohort_fusion_ablation_technical_report_20260816.md",
            "sha256": "bd2954a8ca0460c422dd2a0233f5eb5de0bee9c89693a6ce6edc30ccc65b9868",
        },
        {
            "bytes": 23062,
            "path": "history/internal_docs/goal5790_a1_home_rejected_program_suite_result_20260816.json",
            "sha256": "800707087dcabfd677eff41062215cde22eca94f0d5102ab637eece815160dcf",
        },
        {
            "bytes": 14500,
            "path": "history/internal_docs/review_goal5790_a1_home_rejected_program_suite_20260816.md",
            "sha256": "778c996516c85ab185c8e3be23132794348827ad13f54d774e402fc42f09e9d9",
        },
    ]
    diagnostic = value.get("temporary_v3_diagnostic")
    helper = value.get("test_gate_successor")
    if _sha_bytes(raw) != V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_FILE_SHA256 \
            or _sha_bytes(report) \
                != V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_REPORT_SHA256 \
            or claimed != V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_SHA256 \
            or claimed != _digest(unsigned) \
            or set(value) != {
                "authority_sha256", "authorization", "builder_binding",
                "canonical_v4_outputs", "goal",
                "missing_controlling_predecessors", "recorded_date",
                "resolution", "schema", "status",
                "temporary_v3_diagnostic", "test_gate_successor",
                "v3_terminal", "zero_execution_facts",
            } \
            or type(value.get("goal")) is not int or value.get("goal") != 5791 \
            or value.get("schema") \
                != "rtdl.goal5791.portable_source_v4_clean_failure_diagnostic_successor_authority.v1" \
            or value.get("status") \
                != "PREEXECUTION_V4_CLEAN_FAILURE_SUCCESSOR__NO_BUILD_AUTHORIZATION" \
            or value.get("canonical_v4_outputs") != {
                "receipt": "history/internal_docs/goal5791_portable_source_v4_build_receipt_20260817.json",
                "source": HISTORICAL_V4_SOURCE_OUTPUT_PATH,
                "twin": HISTORICAL_V4_SOURCE_TWIN_PATH,
            } \
            or value.get("builder_binding") != {
                "final_v4_builder_is_bound_by_source_receipt_manifest_and_external_source_sha256": True,
                "final_v4_builder_sha256_is_not_embedded_here_to_avoid_builder_authority_hash_cycle": True,
                "terminal_v3_builder_sha256": (
                    "25f5e96fbbc1dd36893ac40aaad644bf4af6316203b17440380d099a524244ec"),
            } \
            or value.get("resolution") != {
                "all_four_missing_controlling_predecessors_are_exact_v4_overlays": True,
                "clean_external_only_excluded_test_ids_unchanged": True,
                "clean_selected_test_count_remains_106": True,
                "failing_controlling_predecessor_test_is_not_excluded_or_renamed": True,
                "workspace_discovered_test_count_remains_112": True,
            } \
            or value.get("missing_controlling_predecessors") != missing \
            or any(len(payloads[item["path"]]) != item["bytes"]
                   or _sha_bytes(payloads[item["path"]]) != item["sha256"]
                   for item in missing) \
            or value.get("v3_terminal") != {
                "file_sha256": V3_ZERO_OUTPUT_TERMINAL_SHA256,
                "internal_sha256": V3_ZERO_OUTPUT_TERMINAL_INTERNAL_SHA256,
                "path": V3_ZERO_OUTPUT_TERMINAL_MEMBER,
                "report_file_sha256": V3_ZERO_OUTPUT_TERMINAL_REPORT_SHA256,
                "report_path": V3_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER,
                "source_archive_twin_and_receipt_outputs_absent": True,
                "terminal_and_never_retried_or_selected": True,
            } \
            or _sha_bytes(payloads[V3_ZERO_OUTPUT_TERMINAL_MEMBER]) \
                != V3_ZERO_OUTPUT_TERMINAL_SHA256 \
            or _sha_bytes(payloads[V3_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER]) \
                != V3_ZERO_OUTPUT_TERMINAL_REPORT_SHA256 \
            or not isinstance(diagnostic, dict) \
            or diagnostic.get("candidate_archive_payload_count_including_manifest") != 795 \
            or diagnostic.get("candidate_source_tree_sha256") \
                != "5fdf0a8ca987c4dc8584e873a35c85f7158d5532864682c66eed1d985bb1e1bc" \
            or diagnostic.get("clean_selected_test_count") \
                != HISTORICAL_V4_CLEAN_CPU_TEST_COUNT \
            or diagnostic.get("clean_selected_test_ids_sha256") \
                != HISTORICAL_V4_CLEAN_CPU_TEST_IDS_SHA256 \
            or diagnostic.get("failure_test_ids") != [
                "tests.goal5791_pre_worker_zero_claim_freeze_test.Goal5791PreWorkerZeroClaimFreezeTest.test_every_controlling_predecessor_rehashes"] \
            or diagnostic.get("error_test_ids") != [] \
            or diagnostic.get("failure_exception_summaries") != [{
                "exception_type": "builtins.AssertionError",
                "outcome": "failure",
                "summary": "False is not true : <SOURCE_ROOT>/history/internal_docs/goal5790_home_functional_closure_result_20260816.json",
                "test_id": "tests.goal5791_pre_worker_zero_claim_freeze_test.Goal5791PreWorkerZeroClaimFreezeTest.test_every_controlling_predecessor_rehashes",
            }] \
            or diagnostic.get("error_exception_summaries") != [] \
            or diagnostic.get("result") != {
                "errors": 0, "expectedFailures": 0, "failures": 1,
                "skipped": 0, "testsRun": 106, "unexpectedSuccesses": 0,
            } \
            or diagnostic.get("other_selected_tests_passed") != 105 \
            or diagnostic.get("exact_set_before") \
                != diagnostic.get("exact_set_after") \
            or diagnostic.get("exact_set_before") != {
                "directory_count_excluding_root": 56,
                "directory_set_exact": True, "extra_directory_count": 0,
                "extra_regular_file_count": 0, "link_count": 0,
                "regular_file_count": 795, "regular_file_set_exact": True,
                "reparse_point_count": 0, "special_file_count": 0,
            } \
            or diagnostic.get("temporary_diagnostic_was_not_a_candidate_build_or_retry") is not True \
            or diagnostic.get("temporary_tree_cleanup_completed") is not True \
            or not isinstance(helper, dict) \
            or helper.get("cpu_test_gate_helper_path") != CPU_TEST_GATE_MEMBER \
            or helper.get("cpu_test_gate_helper_schema") \
                != "rtdl.goal5791.cpu_test_gate_result.v2" \
            or helper.get("cpu_test_gate_helper_sha256") \
                != V4_CPU_TEST_GATE_HELPER_SHA256 \
            or helper.get("successful_gate_empty_outcome_test_ids_sha256") \
                != _digest({
                    "failures": [], "errors": [], "skipped": [],
                    "expectedFailures": [], "unexpectedSuccesses": []}) \
            or helper.get("successful_gate_requires_all_five_outcome_id_lists_empty") is not True \
            or helper.get("successful_gate_requires_failure_and_error_summaries_empty") is not True \
            or helper.get("workspace_discovered_test_count") \
                != HISTORICAL_V4_WORKSPACE_CPU_TEST_COUNT \
            or helper.get("workspace_discovered_test_ids_sha256") \
                != HISTORICAL_V4_WORKSPACE_CPU_TEST_IDS_SHA256 \
            or helper.get("workspace_test_module_count") != 11 \
            or helper.get("workspace_test_modules_sha256") \
                != WORKSPACE_CPU_TEST_MODULES_SHA256 \
            or helper.get("clean_external_only_excluded_test_count") != 6 \
            or helper.get("clean_external_only_excluded_test_ids_sha256") \
                != CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256 \
            or helper.get("clean_selected_test_count") \
                != HISTORICAL_V4_CLEAN_CPU_TEST_COUNT \
            or helper.get("clean_selected_test_ids_sha256") \
                != HISTORICAL_V4_CLEAN_CPU_TEST_IDS_SHA256 \
            or not isinstance(value.get("authorization"), dict) \
            or any(item is not False
                   for item in value["authorization"].values()) \
            or value.get("zero_execution_facts") != {
                "bundle_created": False, "formal_worker_count": 0,
                "home_execution_count": 0, "pod_connection_count": 0,
                "registered_performance_timing_count": 0,
                "source_candidate_created": False,
                "target_prepare_execution_count": 0,
            }:
        raise IndependentPortableAuditError(
            "portable-source v4 clean-failure successor authority drifted")


def _validate_stage_a_v15_successor_authority(
    payloads: dict[str, bytes],
) -> None:
    raw = payloads[STAGE_A_V15_SUCCESSOR_AUTHORITY_MEMBER]
    report = payloads[STAGE_A_V15_SUCCESSOR_AUTHORITY_REPORT_MEMBER]
    value = _strict_json_bytes(raw, STAGE_A_V15_SUCCESSOR_AUTHORITY_MEMBER)
    unsigned = dict(value)
    claimed = unsigned.pop("authority_sha256", None)
    expected_lineage = {
        "v1_first_entry_terminal_file_sha256": (
            "ef9eff34cd3db91eac216e97880c22332d0ce394ca2707464f2ab755dbd9b364"),
        "v1_first_entry_terminal_internal_sha256": (
            "e62626cea174f57717c349af09308e3878bb4936be95fe543a5ece21e58bb43b"),
        "v1_first_entry_terminal_path": STAGE_A_V1_TERMINAL_MEMBER,
        "v2_open_receipt_file_sha256": (
            "c564a0316728356c8331441e0537d6539e12d7d242ae82258e7ad7cd9e6959cc"),
        "v2_open_receipt_internal_sha256": (
            "bdcd1b07fec1fab3be42082ae6da83a9b69a7239a1e317605a1c5fa1d9a2d23d"),
        "v2_open_receipt_path": STAGE_A_V2_OPEN_RECEIPT_MEMBER,
        "v2_terminal_file_sha256": (
            "d6e416a4c524b16739358a14f773143dc1aba1ef9b8de6292f05515942e33260"),
        "v2_terminal_internal_sha256": (
            "7b1f7cf41141a337c6bb77ad6e2be1ef802b761be16fa97a06c6b97e85be5594"),
        "v2_terminal_path": STAGE_A_V2_TERMINAL_MEMBER,
        "v2_upload_staging_remains_preserved_read_only": True,
        "v2_target_materialization_was_never_created": True,
    }
    if _sha_bytes(raw) != STAGE_A_V15_SUCCESSOR_AUTHORITY_FILE_SHA256 \
            or _sha_bytes(report) \
                != STAGE_A_V15_SUCCESSOR_AUTHORITY_REPORT_SHA256 \
            or claimed != STAGE_A_V15_SUCCESSOR_AUTHORITY_SHA256 \
            or claimed != _digest(unsigned) \
            or set(value) != {
                "authorization", "authority_sha256", "canonical_outputs",
                "date", "decision", "exact_successor_delta",
                "failed_stage_a_lineage", "goal", "predecessor", "schema",
                "status", "successor_invariants",
            } \
            or value.get("schema") \
                != "rtdl.goal5791.stage_a_endpoint_record_v15_successor_authority.v1" \
            or value.get("goal") != 5791 \
            or value.get("status") \
                != "FROZEN_LOCAL_SOURCE_HOME_BUNDLE_REPAIR_POLICY__NOT_STAGE_A_OR_STAGE_B_AUTHORITY" \
            or value.get("decision") \
                != "BUILD_ONE_V15_SUCCESSOR_WITH_ENDPOINT_RECORD_CONTRACT_REPAIR" \
            or value.get("canonical_outputs") != {
                "receipt": "history/internal_docs/goal5791_portable_source_v15_build_receipt_20260820.json",
                "source": "history/internal_docs/goal5791_portable_source_v15_20260820.tar.gz",
                "twin": "history/internal_docs/goal5791_portable_source_v15_twin_20260820.tar.gz",
            } \
            or value.get("predecessor") != {
                "v14_build_receipt_file_sha256": "799e1f0466e5b88343d6d81b49bac37faa1579412e3c6c584b98864893d24085",
                "v14_build_receipt_path": "history/internal_docs/goal5791_portable_source_v14_build_receipt_20260819.json",
                "v14_source_file_sha256": "67e708a93b5a58fcf60d74aa1384b566c5f34cab16c1a285f531fe685c6eeba2",
                "v14_source_path": "history/internal_docs/goal5791_portable_source_v14_20260819.tar.gz",
                "v14_twin_file_sha256": "67e708a93b5a58fcf60d74aa1384b566c5f34cab16c1a285f531fe685c6eeba2",
                "v14_twin_path": "history/internal_docs/goal5791_portable_source_v14_twin_20260819.tar.gz",
            } \
            or value.get("failed_stage_a_lineage") != expected_lineage \
            or _sha_bytes(payloads[STAGE_A_V1_TERMINAL_MEMBER]) \
                != expected_lineage["v1_first_entry_terminal_file_sha256"] \
            or _sha_bytes(payloads[STAGE_A_V2_TERMINAL_MEMBER]) \
                != expected_lineage["v2_terminal_file_sha256"] \
            or _sha_bytes(payloads[STAGE_A_V2_OPEN_RECEIPT_MEMBER]) \
                != expected_lineage["v2_open_receipt_file_sha256"] \
            or value.get("exact_successor_delta") != {
                "mechanical_test": "The staging helper endpoint record must equal target_prepare._pod_endpoint_identity_record for the same user, host, and port.",
                "new_staging_helper_sha256": _sha_bytes(
                    payloads["scripts/goal5791_open_upload_staging.py"]),
                "old_staging_helper_sha256": "367d2bc07368c5bb8c1b36b1d19ff58e69c088537a8c30de38410b3373913e47",
                "predecessor_target_prepare_sha256": "fb61ca150601ea773120529ed43230e1f9b818a15f958716dc121538ad7dd1e5",
                "repair": "Add the canonical identity_sha256 derived from {ssh_user,host,port} to the staging helper endpoint record.",
                "scientific_product_file_delta_count": 0,
                "target_prepare_functional_logic_delta_count": 0,
                "target_prepare_successor_changes_only_the_required_trusted_auditor_sha256_pin_and_source_receipt_schema": True,
            } \
            or value.get("successor_invariants") != {
                "clean_test_count": 106,
                "clean_test_ids_sha256": "d6ee66ab065c34507fcb5886ed130a83c9772978f869cce08ab33d7d7d641bdb",
                "formal_contract_sha256": "d3ef76c08127ce296f0bd42732fd9af2998f718fccf38fbe99615d08c59075b1",
                "product_source_delta_count": 0,
                "schedule_sha256": "4b6d119cc6bd8b5f0639c11642745accde4a7bfc26bf758a6f1c24cd9e7af58d",
                "test_id_delta_count": 0,
                "worker_count": 96,
                "workspace_test_count": 112,
                "workspace_test_ids_sha256": "3fbc3cc1166ff1d8523c9d5c61e20d62ecbef09c98769ca7f89cbd0b5bfe5caa",
            } \
            or not isinstance(value.get("authorization"), dict) \
            or value["authorization"].get(
                "authorizes_one_local_portable_source_v15_build") is not True \
            or value["authorization"].get(
                "authorizes_home_functional_only_qualification") is not True \
            or value["authorization"].get(
                "authorizes_native_free_bundle_build") is not True \
            or any(value["authorization"].get(name) is not False for name in (
                "authorizes_formal_worker_zero", "authorizes_performance_claim",
                "authorizes_publication_or_submission",
                "authorizes_registered_timing", "authorizes_stage_a",
                "authorizes_stage_b",
            )):
        raise IndependentPortableAuditError(
            "Stage-A endpoint-record v15 successor authority drifted")


def _validate_stage_a_v16_successor_authority(
    payloads: dict[str, bytes],
) -> None:
    raw = payloads[STAGE_A_V16_SUCCESSOR_AUTHORITY_MEMBER]
    report = payloads[STAGE_A_V16_SUCCESSOR_AUTHORITY_REPORT_MEMBER]
    value = _strict_json_bytes(raw, STAGE_A_V16_SUCCESSOR_AUTHORITY_MEMBER)
    unsigned = dict(value)
    claimed = unsigned.pop("authority_sha256", None)
    lineage = value.get("failed_stage_a_lineage")
    delta = value.get("exact_successor_delta")
    if _sha_bytes(raw) != STAGE_A_V16_SUCCESSOR_AUTHORITY_FILE_SHA256 \
            or _sha_bytes(report) \
                != STAGE_A_V16_SUCCESSOR_AUTHORITY_REPORT_SHA256 \
            or claimed != STAGE_A_V16_SUCCESSOR_AUTHORITY_SHA256 \
            or claimed != _digest(unsigned) \
            or set(value) != {
                "authorization", "authority_sha256", "canonical_outputs",
                "date", "decision", "exact_successor_delta",
                "failed_stage_a_lineage", "goal", "predecessor", "schema",
                "status", "successor_invariants",
            } \
            or value.get("schema") \
                != "rtdl.goal5791.stage_a_archive_root_v16_successor_authority.v1" \
            or value.get("goal") != 5791 \
            or value.get("status") \
                != "FROZEN_LOCAL_SOURCE_HOME_BUNDLE_REPAIR_POLICY__NOT_STAGE_A_OR_STAGE_B_AUTHORITY" \
            or value.get("decision") \
                != "BUILD_ONE_V16_SUCCESSOR_WITH_LEGAL_ROOT_DIRECTORY_ARCHIVE_REPAIR" \
            or value.get("canonical_outputs") != {
                "receipt": HISTORICAL_V16_SOURCE_RECEIPT_PATH,
                "source": HISTORICAL_V16_SOURCE_OUTPUT_PATH,
                "twin": HISTORICAL_V16_SOURCE_TWIN_PATH,
            } \
            or not isinstance(delta, dict) \
            or delta.get("old_target_prepare_sha256") \
                != "82189a24ab512eafc4518c9ecaecb487c6b0e3937ceea57b86f027b37441ecda" \
            or delta.get("new_target_prepare_sha256") \
                != "2c73d75774b64508dbc1f0197e5f64584a1e358e8da82dfd6a79a8322273bad0" \
            or delta.get("old_portable_harness_test_sha256") \
                != "60ffd58e10f8ca47490320908dd85f4e58a1b27606f9a69c1782d6f4f483a29f" \
            or delta.get("new_portable_harness_test_sha256") \
                != "449fe9f79670efff8d9b8d7ad80d3092f687ffd9292406392948b81bd4bcc2ca" \
            or delta.get("scientific_product_file_delta_count") != 0 \
            or delta.get("test_id_delta_count") != 0 \
            or not isinstance(lineage, dict) \
            or _sha_bytes(payloads[
                "history/internal_docs/goal5791_stage_a_v3_capacity_admission_terminal_20260820.json"
            ]) != lineage.get("v3_terminal_file_sha256") \
            or _sha_bytes(payloads[
                "history/internal_docs/goal5791_stage_a_v3_failure_evidence_20260820/UPLOAD_STAGING_OPEN_RECEIPT.json"
            ]) != lineage.get("v3_open_receipt_file_sha256") \
            or _sha_bytes(payloads[
                "history/internal_docs/goal5791_stage_a_v4_wheelhouse_root_directory_terminal_20260820.json"
            ]) != lineage.get("v4_terminal_file_sha256") \
            or _sha_bytes(payloads[
                "history/internal_docs/goal5791_stage_a_v4_failure_evidence_20260820/PARTIAL_UPLOAD_STAGING_OPEN_RECEIPT.json"
            ]) != lineage.get("v4_open_receipt_file_sha256") \
            or value.get("successor_invariants") != {
                "clean_test_count": 106,
                "clean_test_ids_sha256": "d6ee66ab065c34507fcb5886ed130a83c9772978f869cce08ab33d7d7d641bdb",
                "formal_contract_sha256": "d3ef76c08127ce296f0bd42732fd9af2998f718fccf38fbe99615d08c59075b1",
                "product_source_delta_count": 0,
                "schedule_sha256": "4b6d119cc6bd8b5f0639c11642745accde4a7bfc26bf758a6f1c24cd9e7af58d",
                "test_id_delta_count": 0,
                "worker_count": 96,
                "workspace_test_count": 112,
                "workspace_test_ids_sha256": "3fbc3cc1166ff1d8523c9d5c61e20d62ecbef09c98769ca7f89cbd0b5bfe5caa",
            } \
            or value.get("authorization") != {
                "authorizes_formal_worker_zero": False,
                "authorizes_home_functional_only_qualification": True,
                "authorizes_native_free_bundle_build": True,
                "authorizes_one_local_portable_source_v16_build": True,
                "authorizes_performance_claim": False,
                "authorizes_publication_or_submission": False,
                "authorizes_registered_timing": False,
                "authorizes_stage_a": False,
                "authorizes_stage_b": False,
            }:
        raise IndependentPortableAuditError(
            "Stage-A archive-root v16 successor authority drifted")


def _validate_stage_a_v16_final_authority(
    payloads: dict[str, bytes],
) -> None:
    raw = payloads[STAGE_A_V16_FINAL_AUTHORITY_MEMBER]
    report = payloads[STAGE_A_V16_FINAL_AUTHORITY_REPORT_MEMBER]
    value = _strict_json_bytes(raw, STAGE_A_V16_FINAL_AUTHORITY_MEMBER)
    unsigned = dict(value)
    claimed = unsigned.pop("authority_sha256", None)
    policy = value.get("exact_successor_policy")
    lineage = value.get("predecessor_and_failure_lineage")
    if _sha_bytes(raw) != STAGE_A_V16_FINAL_AUTHORITY_FILE_SHA256 \
            or _sha_bytes(report) != STAGE_A_V16_FINAL_AUTHORITY_REPORT_SHA256 \
            or claimed != STAGE_A_V16_FINAL_AUTHORITY_SHA256 \
            or claimed != _digest(unsigned) \
            or set(value) != {
                "authorization", "authority_sha256", "canonical_outputs",
                "date", "decision", "exact_successor_policy", "goal",
                "predecessor_and_failure_lineage", "schema", "status",
                "successor_invariants",
            } \
            or value.get("schema") \
                != "rtdl.goal5791.stage_a_archive_root_v16_final_successor_authority.v1" \
            or value.get("goal") != 5791 \
            or value.get("status") \
                != "FINAL_LOCAL_SOURCE_HOME_BUNDLE_REPAIR_POLICY__NOT_STAGE_A_OR_STAGE_B_AUTHORITY" \
            or value.get("decision") \
                != "FINALIZE_ONE_V16_SUCCESSOR_WITH_NONCIRCULAR_SOURCE_RECEIPT_BINDING" \
            or value.get("canonical_outputs") != {
                "receipt": HISTORICAL_V16_SOURCE_RECEIPT_PATH,
                "source": HISTORICAL_V16_SOURCE_OUTPUT_PATH,
                "twin": HISTORICAL_V16_SOURCE_TWIN_PATH,
            } \
            or not isinstance(policy, dict) \
            or policy.get("allowed_executable_delta_paths") != [
                "scripts/goal5791_build_portable_source.py",
                "scripts/goal5791_build_pre_pod_bundle.py",
                "scripts/goal5791_independent_portable_audit.py",
                "scripts/goal5791_target_prepare.py",
                "tests/goal5791_portable_home_harness_test.py",
            ] \
            or policy.get("final_executable_hashes_bound_by_source_manifest_and_build_receipt") is not True \
            or policy.get("preliminary_authority_new_file_hashes_are_noncontrolling") is not True \
            or policy.get("product_source_delta_count") != 0 \
            or policy.get("formal_contract_or_schedule_delta_count") != 0 \
            or policy.get("test_id_delta_count") != 0 \
            or not isinstance(lineage, dict) \
            or _sha_bytes(payloads[STAGE_A_V16_SUCCESSOR_AUTHORITY_MEMBER]) \
                != lineage.get("preliminary_v16_authority_file_sha256") \
            or lineage.get("preliminary_v16_authority_internal_sha256") \
                != STAGE_A_V16_SUCCESSOR_AUTHORITY_SHA256 \
            or value.get("successor_invariants") != {
                "clean_test_count": 106,
                "clean_test_ids_sha256": "d6ee66ab065c34507fcb5886ed130a83c9772978f869cce08ab33d7d7d641bdb",
                "formal_contract_sha256": "d3ef76c08127ce296f0bd42732fd9af2998f718fccf38fbe99615d08c59075b1",
                "schedule_sha256": "4b6d119cc6bd8b5f0639c11642745accde4a7bfc26bf758a6f1c24cd9e7af58d",
                "worker_count": 96,
                "workspace_test_count": 112,
                "workspace_test_ids_sha256": "3fbc3cc1166ff1d8523c9d5c61e20d62ecbef09c98769ca7f89cbd0b5bfe5caa",
            } \
            or value.get("authorization") != {
                "authorizes_formal_worker_zero": False,
                "authorizes_home_functional_only_qualification": True,
                "authorizes_native_free_bundle_build": True,
                "authorizes_one_local_portable_source_v16_build": True,
                "authorizes_performance_claim": False,
                "authorizes_publication_or_submission": False,
                "authorizes_registered_timing": False,
                "authorizes_stage_a": False,
                "authorizes_stage_b": False,
            }:
        raise IndependentPortableAuditError(
            "Stage-A archive-root v16 final successor authority drifted")


def _literal_contract_values(
    source: bytes, requested: frozenset[str],
) -> dict[str, object]:
    """Read frozen literal contract constants without importing/executing it."""

    try:
        tree = ast.parse(source.decode("utf-8"))
    except (UnicodeError, SyntaxError) as exc:
        raise IndependentPortableAuditError(
            "formal contract is not parseable UTF-8 Python") from exc
    nodes: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            nodes[node.targets[0].id] = node.value
        elif isinstance(node, ast.AnnAssign) \
                and isinstance(node.target, ast.Name) \
                and node.value is not None:
            nodes[node.target.id] = node.value
    values: dict[str, object] = {}

    def evaluate(node: ast.AST) -> object:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.List):
            return [evaluate(item) for item in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(evaluate(item) for item in node.elts)
        if isinstance(node, ast.Dict):
            return {
                evaluate(key): evaluate(value)
                for key, value in zip(node.keys, node.values, strict=True)
            }
        if isinstance(node, ast.Name):
            return resolve(node.id)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return evaluate(node.left) + evaluate(node.right)  # type: ignore[operator]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -evaluate(node.operand)  # type: ignore[operator]
        raise IndependentPortableAuditError(
            f"non-literal frozen contract expression: {ast.dump(node)}")

    def resolve(name: str) -> object:
        if name not in values:
            node = nodes.get(name)
            if node is None:
                raise IndependentPortableAuditError(
                    f"frozen contract constant is absent: {name}")
            values[name] = evaluate(node)
        return values[name]

    return {name: resolve(name) for name in requested}


def _expected_source_set_receipt(
    source_payloads: dict[str, bytes], *, read_only: bool,
) -> dict[str, object]:
    directories: set[str] = set()
    for name in source_payloads:
        parent = PurePosixPath(name).parent
        while parent.as_posix() not in ("", "."):
            directories.add(parent.as_posix())
            parent = parent.parent
    return {
        "regular_file_count": len(source_payloads),
        "directory_count_excluding_root": len(directories),
        "regular_file_set_exact": True,
        "directory_set_exact": True,
        "extra_regular_file_count": 0,
        "extra_directory_count": 0,
        "link_count": 0,
        "reparse_point_count": 0,
        "special_file_count": 0,
        "all_tree_paths_without_write_bits": read_only,
    }


def _validate_home_ptx_producer_observation(
    observation: dict[str, object], *, home_authority: dict[str, object],
) -> None:
    """Reconstruct the exact frozen Home producer observation contract."""

    directives = observation.get("numba_probe_ptx_directives")
    nvrtc_paths = sorted((
        str(home_authority["cuda_nvrtc_resolved_path"]),
        str(home_authority["cuda_nvrtc_builtins_resolved_path"]),
    ))
    toolkit = str(home_authority["cuda_toolkit_resolved_path"])
    if set(observation) != HOME_PTX_PRODUCER_OBSERVATION_KEYS \
            or observation.get("schema") \
                != "rtdl.goal5790.home_ptx_producer_observation.v1" \
            or any(observation.get(name) != value for name, value in (
                HOME_QUALIFICATION_DEPENDENCY_IDENTITY.items())) \
            or observation.get("cuda_home") != toolkit \
            or observation.get("cuda_path") != toolkit \
            or observation.get("numba_selected_nvvm_by") != "CUDA_HOME" \
            or observation.get("numba_selected_nvvm_path") \
                != home_authority["cuda_nvvm_resolved_path"] \
            or observation.get("numba_selected_nvvm_sha256") \
                != home_authority["cuda_nvvm_sha256"] \
            or observation.get("numba_selected_libdevice_by") != "CUDA_HOME" \
            or observation.get("numba_selected_libdevice_path") \
                != home_authority["cuda_libdevice_resolved_path"] \
            or observation.get("numba_selected_libdevice_sha256") \
                != home_authority["cuda_libdevice_sha256"] \
            or observation.get("loaded_nvvm_paths") \
                != [home_authority["cuda_nvvm_resolved_path"]] \
            or observation.get("cupy_nvrtc_runtime_version") \
                != home_authority["cuda_nvrtc_runtime_version"] \
            or observation.get("loaded_nvrtc_family_paths") != nvrtc_paths \
            or observation.get("nvrtc_probe_output") != 5790 \
            or observation.get("elapsed_values_recorded") is not False \
            or observation.get("application_input_used") is not False \
            or observation.get(
                "registered_performance_timing_created") is not False \
            or not isinstance(directives, dict) \
            or set(directives) != {"version", "target", "address_size"} \
            or directives.get("target") != "sm_61" \
            or directives.get("address_size") != "64" \
            or not isinstance(directives.get("version"), str) \
            or not directives.get("version") \
            or any(
                not isinstance(observation.get(name), str)
                or re.fullmatch(
                    r"[0-9a-f]{64}", str(observation.get(name))) is None
                for name in (
                    "numba_probe_ptx_sha256", "nvrtc_probe_source_sha256",
                )
            ):
        raise IndependentPortableAuditError(
            "Home PTX producer observation exact contract drifted")


def _validate_home_trace_producer_opens(
    trace: bytes, *, expected_producers: set[str],
) -> dict[str, object]:
    successful: set[str] = set()
    for line in trace.decode("utf-8", errors="strict").splitlines():
        match = re.search(
            r'openat\([^,]+,\s*"([^"]+)".*\)\s+=\s+([0-9]+)', line)
        if match and match.group(1).startswith("/"):
            successful.add(str(PurePosixPath(match.group(1))))

    def producer_binary(path: str) -> bool:
        name = PurePosixPath(path).name
        return bool(
            re.fullmatch(r"libnvrtc(?:-builtins)?\.so(?:\..+)?", name)
            or re.fullmatch(r"libnvvm\.so(?:\..+)?", name)
            or (name.startswith("libdevice") and name.endswith(".bc"))
        )

    producer_opens = {path for path in successful if producer_binary(path)}
    missing = expected_producers - producer_opens
    extra = producer_opens - expected_producers

    def is_loader_version_alias(path: str) -> bool:
        candidate = PurePosixPath(path)
        return any(
            candidate.parent == expected.parent
            and expected.name.startswith(candidate.name + ".")
            for expected in map(PurePosixPath, expected_producers)
        )

    foreign = {path for path in extra if not is_loader_version_alias(path)}
    if missing or foreign:
        raise IndependentPortableAuditError(
            "Home trace producer-open exact/alias set drifted")
    return {
        "successful_exact_producer_opens": sorted(expected_producers),
        "foreign_successful_producer_opens": [],
        "trace_sha256": _sha_bytes(trace),
    }


def _validate_home_functional_facts(
    facts: object, *, source_summary: dict[str, object],
    source_payloads: dict[str, bytes], evidence_payloads: dict[str, bytes],
    target_evidence: dict[str, bytes], target_authority: dict[str, object],
    inspection: dict[str, object], recount: dict[str, object],
) -> dict[str, object]:
    if not isinstance(facts, dict) \
            or set(facts) != HOME_EVIDENCE_BOUND_CLOSURE_KEYS:
        raise IndependentPortableAuditError(
            "Home evidence-bound functional facts exact key set drifted")
    _reject_home_performance_observations(
        facts, label="home_functional_facts")
    source_home_authority = source_payloads.get(HOME_AUTHORITY_MEMBER)
    source_shared_freeze = source_payloads.get(SHARED_FREEZE_MEMBER)
    if source_home_authority is None or source_shared_freeze is None \
            or target_evidence.get("HOME_MACHINE_AUTHORITY.json") \
                != source_home_authority \
            or target_evidence.get("SHARED_CONTRACT_FREEZE.json") \
                != source_shared_freeze:
        raise IndependentPortableAuditError(
            "Home target evidence/source authority bytes drifted")
    home_authority = _strict_json_bytes(
        source_home_authority, HOME_AUTHORITY_MEMBER)
    home_unsigned = dict(home_authority)
    home_claimed = home_unsigned.pop("receipt_sha256", None)
    if home_claimed != _digest(home_unsigned) \
            or facts.get("home_machine_authority") != home_authority \
            or inspection.get("home_machine_authority") != home_authority \
            or inspection.get("home_machine_authority_sha256") != home_claimed:
        raise IndependentPortableAuditError(
            "Home machine authority seal/cross-binding drifted")
    observation = _strict_json_bytes(
        target_evidence["PTX_PRODUCER_OBSERVATION.json"],
        "PTX_PRODUCER_OBSERVATION.json",
    )
    _validate_home_ptx_producer_observation(
        observation, home_authority=home_authority)
    if facts.get("ptx_producer_observation") != observation \
            or inspection.get("ptx_producer_observation") != observation:
        raise IndependentPortableAuditError(
            "Home PTX producer observation cross-binding drifted")
    ptx_files: dict[str, object] = {}
    for stem in (
        "cuda_nvrtc", "cuda_nvrtc_builtins", "cuda_nvvm", "cuda_libdevice",
    ):
        for suffix in ("resolved_path", "sha256"):
            key = f"{stem}_{suffix}"
            ptx_files[key] = home_authority[key]
    expected_gpu = ", ".join(str(home_authority[name]) for name in (
        "gpu_name", "gpu_uuid", "driver_version", "compute_capability",
    ))
    trace = target_evidence["PTX_PRODUCER_OPENAT_TRACE.log"]
    expected_producers = {
        str(home_authority[f"{stem}_resolved_path"])
        for stem in (
            "cuda_nvrtc", "cuda_nvrtc_builtins", "cuda_nvvm", "cuda_libdevice",
        )
    }
    expected_open_audit = _validate_home_trace_producer_opens(
        trace, expected_producers=expected_producers)
    formal = _literal_contract_values(
        source_payloads["scripts/goal5791_formal_contract.py"],
        frozenset({
            "CACHE_POLICY", "SOURCE_ADMISSION_POLICY",
            "FORMAL_WORKER_ENVIRONMENT_CONTRACT",
        }),
    )
    cache = formal["CACHE_POLICY"]
    if not isinstance(cache, dict):
        raise IndependentPortableAuditError("frozen cache policy is not a dict")
    ptx_identity = inspection.get("ptx_program_identity")
    expected_static = {
        "schema": "rtdl.goal5791.home_token_functional_closure.v1",
        "status": "PASS__10_OF_10_TOKEN_ONLY_EXACT_BEHAVIORAL_TRUE_OPTIX",
        "execution_source_archive_sha256": source_summary["archive_sha256"],
        "execution_source_tree_sha256": source_summary["source_tree_sha256"],
        "source_manifest_sha256": source_summary["source_manifest_sha256"],
        "native_library_sha256": _sha_bytes(
            evidence_payloads["TARGET_NATIVE/librtdl_optix.so"]),
        "target_materialization_receipt_sha256": target_authority.get(
            "receipt_sha256"),
        "target_materialization_evidence_sha256": _sha_bytes(
            evidence_payloads["TARGET_MATERIALIZATION_EVIDENCE.tar.gz"]),
        "home_evidence_payload_count": len(evidence_payloads),
        "gpu": expected_gpu,
        "home_machine_authority": home_authority,
        "ptx_producer_toolchain_files": ptx_files,
        "ptx_producer_observation": observation,
        "home_qualification_dependency_identity": (
            HOME_QUALIFICATION_DEPENDENCY_IDENTITY),
        "home_qualification_identity_is_not_cross_environment_reproducibility": True,
        "ptx_producer_open_audit": expected_open_audit,
        "ptx_program_identity_sha256": _digest(ptx_identity),
        "home_functional_lane_count": 10,
        "small_lane_count": 4,
        "bounded_real_lane_count": 6,
        "exact_lane_count": recount.get("exact_lane_count"),
        "behavioral_true_optix_lane_count": recount.get(
            "behavioral_true_optix_lane_count"),
        "token_only_lane_count": recount.get("token_only_lane_count"),
        "fresh_parent_pid_count": recount.get("fresh_parent_pid_count"),
        "operation_receipt_count": recount.get("operation_receipt_count"),
        "successful_operation_event_count_by_variant": recount.get(
            "successful_operation_event_count_by_variant"),
        "event_count_per_receipt": {"fusion_on": 2, "fusion_off": 7},
        "all_tokens_admitted_in_preparation": True,
        "fresh_private_cupy_cache_per_lane": True,
        "cache_policy": cache,
        "cache_policy_sha256": _digest(cache),
        "cold_definition": cache["cold_definition"],
        "cold_claim_excludes": cache["cold_claim_excludes"],
        "operating_system_page_cache_controlled_or_dropped": cache[
            "operating_system_page_cache_controlled_or_dropped"],
        "operating_system_page_cache_scope": cache[
            "operating_system_page_cache_scope"],
        "cuda_driver_jit_cache_controlled_or_isolated": cache[
            "cuda_driver_jit_cache_controlled_or_isolated"],
        "optix_disk_cache_controlled_or_isolated": cache[
            "optix_disk_cache_controlled_or_isolated"],
        "round_major_abba_is_uncontrolled_cache_mitigation_not_control": cache[
            "round_major_abba_is_uncontrolled_cache_mitigation_not_control"],
        "independent_simple_undirected_oracle_recomputed_from_raw_edges": (
            recount.get(
                "independent_simple_undirected_oracle_recomputed_from_raw_edges")),
        "independently_recounted_inputs": recount.get(
            "independently_recounted_inputs"),
        "legacy_execution_path_used": False,
        "exact_source_and_native_preserved_before_first_lane": True,
        "source_manifest_payloads_read_only_before_first_lane": True,
        "source_manifest_fully_rehashed_after_functional_lanes": True,
        "source_exact_set_before_first_lane": _expected_source_set_receipt(
            source_payloads, read_only=False),
        "source_exact_set_and_all_tree_paths_read_only_after_lanes": (
            _expected_source_set_receipt(source_payloads, read_only=True)),
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
        "performance_or_compiler_fusion_claimed": False,
        "pod_used": False,
        "prebuilt_target_native_used": False,
        "private_codex_dependency_used": False,
        "formal_worker_environment_contract_sha256": _digest(
            formal["FORMAL_WORKER_ENVIRONMENT_CONTRACT"]),
        "home_locale_matches_formal_environment_contract": True,
        "source_admission_policy_sha256": _digest(
            formal["SOURCE_ADMISSION_POLICY"]),
    }
    for key, expected in expected_static.items():
        if facts.get(key) != expected:
            raise IndependentPortableAuditError(
                f"Home functional fact drifted: {key}")
    if {
        name: observation.get(name)
        for name in HOME_QUALIFICATION_DEPENDENCY_IDENTITY
    } != HOME_QUALIFICATION_DEPENDENCY_IDENTITY:
        raise IndependentPortableAuditError(
            "Home qualification dependency identity drifted")
    return facts


def _validate_target_inspection(
    inspection: dict[str, object], *, home_authority: dict[str, object],
    source_payloads: dict[str, bytes],
) -> None:
    target_sha = inspection.get("target_identity_sha256")
    cupy_version = inspection.get("cupy_version")
    if not isinstance(target_sha, str) \
            or re.fullmatch(r"[0-9a-f]{64}", target_sha) is None \
            or not isinstance(cupy_version, str) or not cupy_version:
        raise IndependentPortableAuditError(
            "Home target/cupy recipe identity drifted")
    reducer_values = _literal_contract_values(
        source_payloads["src/rtdsl/v4_checked_u64_device_reduction.py"],
        frozenset({"_WEIGHTED_REDUCTION_SOURCE"}),
    )
    reducer_source = reducer_values["_WEIGHTED_REDUCTION_SOURCE"]
    if not isinstance(reducer_source, str):
        raise IndependentPortableAuditError(
            "checked-U64 reducer source literal is absent")
    recipes = {
        "fusion_on": {
            "schema": "rtdl.v4.checked_u64_downstream_operation_identity.v1",
            "variant": "fusion_on",
            "target_identity_sha256": target_sha,
            "cupy_version": cupy_version,
            "implementation": {
                "kind": "compiler_owned_rawkernel_recipe",
                "entry": "rtdl_v4_checked_u64_weighted_reduce",
                "source_sha256": _sha_bytes(reducer_source.encode("utf-8")),
                "options": ["-std=c++11"],
                "opaque_partner_kernel_binary_claimed": False,
            },
        },
        "fusion_off": {
            "schema": "rtdl.v4.checked_u64_downstream_operation_identity.v1",
            "variant": "fusion_off",
            "target_identity_sha256": target_sha,
            "cupy_version": cupy_version,
            "implementation": {
                "kind": "trusted_cupy_operation_graph",
                "operations": [
                    "cp.max(weights)", "maximum_weight.item()",
                    "cp.sum(weights,dtype=cp.uint64)", "weight_sum.item()",
                    "values*weights",
                    "cp.sum(weighted_product,dtype=cp.uint64)",
                    "weighted_sum.item()",
                ],
                "opaque_partner_kernel_binary_claimed": False,
            },
        },
    }
    for variant, recipe in recipes.items():
        if inspection.get(f"{variant}_downstream_operation_recipe") != recipe \
                or inspection.get(
                    f"{variant}_downstream_operation_recipe_sha256") \
                    != _digest(recipe):
            raise IndependentPortableAuditError(
                f"Home {variant} exact operation recipe drifted")
    expected_toolchain = {
        field: home_authority[field] for field in (
            "cuda_nvrtc_resolved_path", "cuda_nvrtc_sha256",
            "cuda_nvrtc_builtins_resolved_path",
            "cuda_nvrtc_builtins_sha256", "cuda_nvrtc_runtime_version",
            "cuda_nvvm_resolved_path", "cuda_nvvm_sha256",
            "cuda_libdevice_resolved_path", "cuda_libdevice_sha256",
            "cuda_toolkit_resolved_path",
        )
    }
    if inspection.get("ptx_producer_toolchain") != expected_toolchain \
            or inspection.get("program_bundle_identity") \
                != "v4_builtin_triangle_checked_reduction_composed":
        raise IndependentPortableAuditError(
            "Home PTX producer toolchain/program bundle drifted")
    identity = inspection.get("ptx_program_identity")
    if not isinstance(identity, dict) or set(identity) != {
        "schema", "wrapper", "ordered_leaves", "composed",
        "composer_leaf_bindings",
        "wrapper_leaf_composed_directive_equality_verified",
    } or identity.get("schema") != "rtdl.goal5790.ptx_program_identity.v1" \
            or identity.get(
                "wrapper_leaf_composed_directive_equality_verified") is not True:
        raise IndependentPortableAuditError(
            "Home PTX program identity structure drifted")
    wrapper = identity.get("wrapper")
    composed = identity.get("composed")
    leaves = identity.get("ordered_leaves")
    bindings = identity.get("composer_leaf_bindings")
    if not isinstance(wrapper, dict) or not isinstance(composed, dict) \
            or not isinstance(leaves, list) or not leaves \
            or not isinstance(bindings, list) or len(bindings) != len(leaves):
        raise IndependentPortableAuditError(
            "Home PTX wrapper/leaf identity shape drifted")
    common = composed.get("directives")
    observation = inspection.get("ptx_producer_observation")
    if not isinstance(observation, dict) \
            or not isinstance(common, dict) \
            or set(common) != {"version", "target", "address_size"} \
            or common.get("target") != "sm_61" \
            or common.get("address_size") != "64" \
            or wrapper.get("directives") != common \
            or composed.get("ptx_sha256") \
                != inspection.get("composed_program_sha256") \
            or observation.get("numba_probe_ptx_directives") != common:
        raise IndependentPortableAuditError(
            "Home PTX common directive/composed identity drifted")
    for index, leaf in enumerate(leaves):
        if not isinstance(leaf, dict) or set(leaf) != {
            "role", "abi_name", "ptx_sha256", "directives",
        } or leaf.get("directives") != common \
                or bindings[index] != [leaf.get("role"), leaf.get("abi_name")]:
            raise IndependentPortableAuditError(
                "Home PTX leaf/composer identity drifted")


def _reject_home_performance_observations(
    value: object, *, label: str,
) -> None:
    """Reject re-signed Home payloads that add any clock/elapsed evidence."""

    if isinstance(value, dict):
        for key, item in value.items():
            folded = key.casefold()
            if key in _HOME_ZERO_COUNT_KEYS:
                if type(item) is not int or item != 0:
                    raise IndependentPortableAuditError(
                        f"Home observation count is not exact zero: {label}.{key}")
            elif key in _HOME_FALSE_OBSERVATION_KEYS:
                if item is not False:
                    raise IndependentPortableAuditError(
                        f"Home observation marker is not false: {label}.{key}")
            elif key in _HOME_TRUE_OPERATIONAL_CLOCK_KEYS:
                if item is not True:
                    raise IndependentPortableAuditError(
                        f"operational watchdog disclosure is not true: "
                        f"{label}.{key}")
            elif key in _SOURCE_OPERATIONAL_TIMEOUT_FIELDS:
                if type(item) is not int \
                        or item != _SOURCE_OPERATIONAL_TIMEOUT_FIELDS[key]:
                    raise IndependentPortableAuditError(
                        f"source operational timeout binding drifted: "
                        f"{label}.{key}")
            elif key == "overlay_sha256" \
                    and label == "SOURCE_BASE_AND_OVERLAY_AUTHORITY.json":
                if not isinstance(item, dict) or not item \
                        or any(
                            not isinstance(path, str) or not path
                            or not isinstance(digest, str) or len(digest) != 64
                            or any(ch not in "0123456789abcdef" for ch in digest)
                            for path, digest in item.items()
                        ):
                    raise IndependentPortableAuditError(
                        "source overlay digest map shape drifted")
                continue
            elif key == "timer_contract_sha256":
                if item != _digest(_HOME_TIMER_CONTRACT):
                    raise IndependentPortableAuditError(
                        f"Home zero-observation contract digest drifted: "
                        f"{label}.{key}")
            elif any(token in folded
                     for token in _HOME_FORBIDDEN_OBSERVATION_KEY_TOKENS) \
                    or folded.endswith(
                        _HOME_FORBIDDEN_OBSERVATION_KEY_SUFFIXES):
                raise IndependentPortableAuditError(
                    f"Home performance/clock field is forbidden: {label}.{key}")
            _reject_home_performance_observations(
                item, label=f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_home_performance_observations(
                item, label=f"{label}[{index}]")


def _require_exact_bundle_member_set(payloads: dict[str, bytes]) -> None:
    actual = set(payloads)
    if actual != EXPECTED_BUNDLE_OUTER_MEMBERS:
        raise IndependentPortableAuditError(
            "bundle outer membership is not the frozen exact set: "
            f"missing={sorted(EXPECTED_BUNDLE_OUTER_MEMBERS - actual)!r}, "
            f"extra={sorted(actual - EXPECTED_BUNDLE_OUTER_MEMBERS)!r}"
        )


def _name(value: str, *, source: bool) -> str:
    pure = PurePosixPath(value)
    parts = tuple(part for part in pure.parts if part not in ("", "."))
    normalized = "/".join(parts)
    if not parts or pure.is_absolute() or ".." in parts \
            or normalized != value.rstrip("/"):
        raise IndependentPortableAuditError(
            f"unsafe/noncanonical archive member: {value!r}")
    if source and (any(part.casefold() in FORBIDDEN_PARTS for part in parts)
                   or normalized.lower().endswith(FORBIDDEN_SUFFIXES)):
        raise IndependentPortableAuditError(
            f"private/binary source member: {value!r}")
    return normalized


def _archive(data: bytes, *, label: str, source: bool) -> dict[str, bytes]:
    values: dict[str, bytes] = {}
    folded: set[str] = set()
    try:
        context = tarfile.open(fileobj=io.BytesIO(data), mode="r:gz")
    except (tarfile.TarError, OSError) as exc:
        raise IndependentPortableAuditError(
            f"cannot open gzip tar: {label}") from exc
    with context as opened:
        for member in opened.getmembers():
            name = _name(member.name, source=source)
            if member.isdir():
                raise IndependentPortableAuditError(
                    f"directory archive member is forbidden: {name}")
            if name in values or name.casefold() in folded:
                raise IndependentPortableAuditError(
                    f"duplicate/casefold archive collision: {name}")
            if not member.isfile() or member.issym() or member.islnk():
                raise IndependentPortableAuditError(
                    f"link/special archive member: {name}")
            stream = opened.extractfile(member)
            if stream is None:
                raise IndependentPortableAuditError(
                    f"unreadable archive member: {name}")
            values[name] = stream.read()
            folded.add(name.casefold())
    return values


def _blob_kind(data: bytes) -> str | None:
    for prefix, label in (
        (b"\x7fELF", "ELF"), (b"MZ", "PE"), (b"!<arch>\n", "AR"),
        (b"\xcf\xfa\xed\xfe", "MACHO64_LE"),
        (b"\xfe\xed\xfa\xcf", "MACHO64_BE"),
        (b"\xce\xfa\xed\xfe", "MACHO32_LE"),
        (b"\xfe\xed\xfa\xce", "MACHO32_BE"),
        (b"\x1f\x8b", "GZIP"), (b"PK\x03\x04", "ZIP"),
        (b"PK\x05\x06", "ZIP_EMPTY"), (b"BZh", "BZIP2"),
        (b"\xfd7zXZ\x00", "XZ"), (b"7z\xbc\xaf'\x1c", "7ZIP"),
        (b"Rar!\x1a\x07\x00", "RAR4"),
        (b"Rar!\x1a\x07\x01\x00", "RAR5"),
        (b"P\xedU\xba", "CUDA_FATBIN"), (b"\xb1CbF", "CUDA_FATBIN"),
    ):
        if data.startswith(prefix):
            return label
    if len(data) >= 262 and data[257:262] == b"ustar":
        return "TAR"
    if any(data.startswith(magic) for magic in (
        b"\x42\x0d\x0d\x0a", b"\x33\x0d\x0d\x0a",
        b"\xa7\x0d\x0d\x0a", b"\xcb\x0d\x0d\x0a",
    )):
        return "PYTHON_BYTECODE"
    return None


def _validate_elf_shared_object(data: bytes) -> None:
    if len(data) < 64 or data[:4] != b"\x7fELF" \
            or data[4] != 2 or data[5] != 1 or data[6] != 1 \
            or int.from_bytes(data[16:18], "little") != 3 \
            or int.from_bytes(data[18:20], "little") != 62:
        raise IndependentPortableAuditError(
            "Home native is not a little-endian ELF64 x86-64 shared object")


def _rows(payloads: dict[str, bytes]) -> list[dict[str, object]]:
    return [
        {"path": name, "size_bytes": len(data), "sha256": _sha_bytes(data)}
        for name, data in sorted(payloads.items())
    ]


def _manifest_rehash(
    payloads: dict[str, bytes], manifest_name: str, schema: str,
    row_key: str,
) -> dict[str, object]:
    manifest_data = payloads.get(manifest_name)
    if manifest_data is None:
        raise IndependentPortableAuditError(f"manifest absent: {manifest_name}")
    value = _strict_json_bytes(manifest_data, manifest_name)
    rows = value.get(row_key)
    if value.get("schema") != schema or not isinstance(rows, list):
        raise IndependentPortableAuditError("manifest schema/rows drifted")
    actual_payloads = {
        name: data for name, data in payloads.items() if name != manifest_name
    }
    expected = {
        str(row["path"]): (int(row["size_bytes"]), str(row["sha256"]))
        for row in rows
    }
    actual = {
        name: (len(data), _sha_bytes(data))
        for name, data in actual_payloads.items()
    }
    if len(expected) != len(rows) or expected != actual:
        raise IndependentPortableAuditError("manifest payload rehash drifted")
    return value


def _extract_and_audit(
    payloads: dict[str, bytes], destination: Path,
) -> dict[str, object]:
    destination.mkdir()
    for name, data in sorted(payloads.items()):
        path = destination.joinpath(*PurePosixPath(name).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    expected_dirs: set[str] = set()
    for name in payloads:
        parent = PurePosixPath(name).parent
        while parent.as_posix() not in ("", "."):
            expected_dirs.add(parent.as_posix())
            parent = parent.parent
    files: dict[str, tuple[int, str]] = {}
    directories: set[str] = set()
    for path in destination.rglob("*"):
        relative = path.relative_to(destination).as_posix()
        info = path.lstat()
        reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        if path.is_symlink() or (
            reparse and getattr(info, "st_file_attributes", 0) & reparse
        ):
            raise IndependentPortableAuditError(
                f"clean extraction contains link/reparse: {relative}")
        if path.is_dir():
            directories.add(relative)
        elif path.is_file():
            files[relative] = (path.stat().st_size, _sha(path))
        else:
            raise IndependentPortableAuditError(
                f"clean extraction contains special node: {relative}")
    expected_files = {
        name: (len(data), _sha_bytes(data)) for name, data in payloads.items()
    }
    if files != expected_files or directories != expected_dirs:
        raise IndependentPortableAuditError(
            "clean-extraction exact file/directory set drifted")
    return {
        "regular_file_count": len(files),
        "directory_count_excluding_root": len(directories),
        "regular_file_set_exact": True,
        "directory_set_exact": True,
        "link_reparse_or_special_count": 0,
    }


def _in_memory_exact_set(payloads: dict[str, bytes]) -> dict[str, object]:
    """Reconstruct the exact-set summary without creating filesystem nodes."""

    directories: set[str] = set()
    for name in payloads:
        parent = PurePosixPath(name).parent
        while parent.as_posix() not in ("", "."):
            directories.add(parent.as_posix())
            parent = parent.parent
    return {
        "regular_file_count": len(payloads),
        "directory_count_excluding_root": len(directories),
        "regular_file_set_exact": True,
        "directory_set_exact": True,
        "link_reparse_or_special_count": 0,
    }


def _rehash_self_sealed_support(
    payloads: dict[str, bytes], *, path: str, file_sha256: str,
    seal_field: str, seal_sha256: str, label: str,
) -> dict[str, object]:
    raw = payloads.get(path)
    if raw is None or _sha_bytes(raw) != file_sha256:
        raise IndependentPortableAuditError(
            f"{label} support file identity drifted")
    value = _strict_json_bytes(raw, path)
    unsigned = dict(value)
    claimed = unsigned.pop(seal_field, None)
    if claimed != seal_sha256 or _digest(unsigned) != seal_sha256:
        raise IndependentPortableAuditError(
            f"{label} support internal seal drifted")
    return value


def _validate_v25_terminal_for_v26(payloads: dict[str, bytes]) -> None:
    raw = payloads.get(V25_SUPPORT_CHAIN_TERMINAL_MEMBER)
    report = payloads.get(V25_SUPPORT_CHAIN_TERMINAL_REPORT_MEMBER)
    if raw is None or report is None \
            or _sha_bytes(raw) != V25_SUPPORT_CHAIN_TERMINAL_FILE_SHA256 \
            or _sha_bytes(report) \
                != V25_SUPPORT_CHAIN_TERMINAL_REPORT_SHA256:
        raise IndependentPortableAuditError(
            "v25 support-chain terminal exact bytes drifted")
    value = _strict_json_bytes(raw, V25_SUPPORT_CHAIN_TERMINAL_MEMBER)
    unsigned = dict(value)
    claimed = unsigned.pop("terminal_sha256", None)
    artifact = value.get("immutable_v25_artifact")
    reproduction = value.get("hostile_reproduction")
    matrix = value.get("artifact_hostile_matrix")
    finding = value.get("p1_finding")
    successor = value.get("required_v26_successor")
    authorization = value.get("authorization")
    if set(value) != {
        "artifact_hostile_matrix", "authorization", "baseline_artifact_audit",
        "date", "goal", "hostile_reproduction", "immutable_v25_artifact",
        "p1_finding", "required_v26_successor", "schema", "status",
        "terminal_sha256",
    } or value.get("schema") \
            != "rtdl.goal5791.portable_source_v25_support_chain_auditor_terminal.v1" \
            or value.get("goal") != 5791 \
            or value.get("status") \
                != "TERMINAL__FIXED_AUDITOR_ACCEPTED_RESIGNED_SUPPORT_CHAIN_DRIFT__NO_HOME_OR_EXTERNAL_EXECUTION" \
            or claimed != V25_SUPPORT_CHAIN_TERMINAL_SHA256 \
            or _digest(unsigned) != V25_SUPPORT_CHAIN_TERMINAL_SHA256 \
            or not isinstance(authorization, dict) \
            or len(authorization) != 10 \
            or any(item is not False for item in authorization.values()) \
            or not isinstance(artifact, dict) \
            or artifact.get("source_file_sha256") \
                != "c1a8d91af1ceba544849f1ec8b161d5eb9967238f2fa6abffae794e88447677b" \
            or artifact.get("build_receipt_file_sha256") \
                != "43fab5f2eacdd295fb9bcc13eaf13399d64669b8749c9d4c467001ba90cf909f" \
            or artifact.get("independent_audit_file_sha256") \
                != "881a11f85424a7422d5dd57f5d355be8d9c12558226da3a6d4bb25f3e3c8524c" \
            or artifact.get("workspace_cpu_test_count") != 115 \
            or artifact.get("clean_cpu_test_count") != 109 \
            or any(type(artifact.get(field)) is not int
                   or artifact.get(field) != 0 for field in (
                       "home_or_target_execution_count", "gpu_execution_count",
                       "pod_execution_count", "formal_worker_count",
                       "registered_performance_timing_count",
                   )) \
            or not isinstance(reproduction, dict) \
            or reproduction.get("fixed_auditor_perform_clean_extraction_false_accepted") \
                is not True \
            or reproduction.get("original_file_sha256") \
                != PREREGISTRATION_V8_FILE_SHA256 \
            or reproduction.get("original_internal_sha256") \
                != PREREGISTRATION_V8_SHA256 \
            or reproduction.get("forged_archive_sha256") \
                != "1d7c35a13782f5c61eb8b7196a1d4021bbf6b62b2c0f7e85ed25021405d7ddfe" \
            or not isinstance(matrix, dict) \
            or matrix.get("attack_count") != 17 \
            or matrix.get("rejected_attack_count") != 15 \
            or matrix.get("accepted_attack_count") != 2 \
            or matrix.get("accepted_surface_is_exactly_the_missing_v8_preregistration_and_pretarget_actual_file_internal_crossbind_family") \
                is not True \
            or not isinstance(finding, dict) \
            or finding.get("v25_is_a_terminal_noncandidate") is not True \
            or not isinstance(successor, dict) \
            or successor.get("source_receipt_schema") \
                != "rtdl.goal5791.portable_source_build_receipt.v26" \
            or successor.get("must_rehash_all_paper_authority_archive_resident_path_file_bindings") \
                is not True \
            or successor.get("must_rehash_correction_authority_archive_resident_support_bindings") \
                is not True \
            or successor.get("must_keep_workspace_and_clean_test_identities_at_115_and_109") \
                is not True:
        raise IndependentPortableAuditError(
            "v25 support-chain terminal authority drifted")


def _validate_v25_governance_successors(payloads: dict[str, bytes]) -> None:
    """Bind the append-only record correction and the v9 paper successor."""

    exact_file_hashes = {
        APPEND_ONLY_CORRECTION_AUTHORITY_MEMBER:
            APPEND_ONLY_CORRECTION_AUTHORITY_FILE_SHA256,
        APPEND_ONLY_CORRECTION_AUTHORITY_REPORT_MEMBER:
            APPEND_ONLY_CORRECTION_AUTHORITY_REPORT_SHA256,
        PAPER_OUTCOME_SUCCESSOR_AUTHORITY_MEMBER:
            PAPER_OUTCOME_SUCCESSOR_AUTHORITY_FILE_SHA256,
        PAPER_OUTCOME_SUCCESSOR_AUTHORITY_REPORT_MEMBER:
            PAPER_OUTCOME_SUCCESSOR_AUTHORITY_REPORT_SHA256,
        PREREGISTRATION_V8_MEMBER: PREREGISTRATION_V8_FILE_SHA256,
        PRETARGET_V8_MEMBER: PRETARGET_V8_FILE_SHA256,
        PREREGISTRATION_V9_MEMBER: PREREGISTRATION_V9_FILE_SHA256,
        PRETARGET_V9_MEMBER: PRETARGET_V9_FILE_SHA256,
        OWNER_REVIEW_ABSORPTION_MEMBER:
            OWNER_REVIEW_ABSORPTION_FILE_SHA256,
        SMALL_RELATIVE_ABSORPTION_MEMBER:
            SMALL_RELATIVE_ABSORPTION_FILE_SHA256,
        CORRECTION_FORMAL_V1_TERMINAL_MEMBER:
            CORRECTION_FORMAL_V1_TERMINAL_FILE_SHA256,
        V25_SUPPORT_CHAIN_TERMINAL_MEMBER:
            V25_SUPPORT_CHAIN_TERMINAL_FILE_SHA256,
        V25_SUPPORT_CHAIN_TERMINAL_REPORT_MEMBER:
            V25_SUPPORT_CHAIN_TERMINAL_REPORT_SHA256,
    }
    if any(name not in payloads or _sha_bytes(payloads[name]) != expected
           for name, expected in exact_file_hashes.items()):
        raise IndependentPortableAuditError(
            "v25 governance successor exact file identity drifted")

    _validate_v25_terminal_for_v26(payloads)

    correction = _strict_json_bytes(
        payloads[APPEND_ONLY_CORRECTION_AUTHORITY_MEMBER],
        APPEND_ONLY_CORRECTION_AUTHORITY_MEMBER,
    )
    correction_unsigned = dict(correction)
    correction_claimed = correction_unsigned.pop("authority_sha256", None)
    correction_authorization = correction.get("authorization")
    if set(correction) != {
        "authority_sha256", "authorization", "corrections",
        "current_artifact_nonmutation", "date", "goal",
        "preserved_formal_v1_terminal_truth", "required_interpretation",
        "schema", "scope", "status",
    } or correction.get("schema") \
            != "rtdl.goal5791.append_only_record_reference_correction_authority.v1" \
            or correction.get("goal") != 5791 \
            or correction.get("status") \
                != "APPEND_ONLY_RECORD_REFERENCE_CORRECTION__NO_ARTIFACT_OR_EXECUTION_CHANGE" \
            or correction_claimed != APPEND_ONLY_CORRECTION_AUTHORITY_SHA256 \
            or _digest(correction_unsigned) \
                != APPEND_ONLY_CORRECTION_AUTHORITY_SHA256 \
            or not isinstance(correction_authorization, dict) \
            or len(correction_authorization) != 13 \
            or any(value is not False
                   for value in correction_authorization.values()):
        raise IndependentPortableAuditError(
            "v25 append-only correction authority drifted")

    corrections = correction.get("corrections")
    expected_correction_resident_support = {
        "path": CORRECTION_FORMAL_V1_TERMINAL_MEMBER,
        "file_sha256": CORRECTION_FORMAL_V1_TERMINAL_FILE_SHA256,
        "internal_seal_field": "terminal_sha256",
        "internal_seal": CORRECTION_FORMAL_V1_TERMINAL_SHA256,
    }
    if not isinstance(corrections, list) or len(corrections) != 2 \
            or not isinstance(corrections[0], dict) \
            or corrections[0].get("immutable_predecessor_record") \
                != expected_correction_resident_support:
        raise IndependentPortableAuditError(
            "v25 correction authority resident support map drifted")
    _rehash_self_sealed_support(
        payloads,
        path=CORRECTION_FORMAL_V1_TERMINAL_MEMBER,
        file_sha256=CORRECTION_FORMAL_V1_TERMINAL_FILE_SHA256,
        seal_field="terminal_sha256",
        seal_sha256=CORRECTION_FORMAL_V1_TERMINAL_SHA256,
        label="v25 correction formal-v1 terminal",
    )

    _rehash_self_sealed_support(
        payloads,
        path=SMALL_RELATIVE_ABSORPTION_MEMBER,
        file_sha256=SMALL_RELATIVE_ABSORPTION_FILE_SHA256,
        seal_field="absorption_sha256",
        seal_sha256=SMALL_RELATIVE_ABSORPTION_SHA256,
        label="v25 small-relative predecessor absorption",
    )
    preregistration_v8 = _rehash_self_sealed_support(
        payloads,
        path=PREREGISTRATION_V8_MEMBER,
        file_sha256=PREREGISTRATION_V8_FILE_SHA256,
        seal_field="preregistration_sha256",
        seal_sha256=PREREGISTRATION_V8_SHA256,
        label="v25 preregistration v8",
    )
    pretarget_v8 = _rehash_self_sealed_support(
        payloads,
        path=PRETARGET_V8_MEMBER,
        file_sha256=PRETARGET_V8_FILE_SHA256,
        seal_field="authority_sha256",
        seal_sha256=PRETARGET_V8_SHA256,
        label="v25 pretarget v8",
    )
    if preregistration_v8.get("status") \
            != "FROZEN_PRETARGET__NOT_EXECUTION_AUTHORITY" \
            or pretarget_v8.get("status") \
                != "FROZEN_PRETARGET_INPUT_AUTHORITIES__NOT_EXECUTION_AUTHORITY":
        raise IndependentPortableAuditError(
            "v25 immutable v8 support disposition drifted")

    preregistration = _strict_json_bytes(
        payloads[PREREGISTRATION_V9_MEMBER], PREREGISTRATION_V9_MEMBER)
    preregistration_unsigned = dict(preregistration)
    preregistration_claimed = preregistration_unsigned.pop(
        "preregistration_sha256", None)
    if preregistration_claimed != PREREGISTRATION_V9_SHA256 \
            or _digest(preregistration_unsigned) != PREREGISTRATION_V9_SHA256 \
            or preregistration.get("formal_contract_source_sha256") \
                != FORMAL_CONTRACT_FILE_SHA256 \
            or preregistration.get("formal_contract_sha256") \
                != FORMAL_CONTRACT_SHA256 \
            or preregistration.get("schedule_sha256") != SCHEDULE_SHA256 \
            or any(preregistration.get(key) is not False for key in (
                "authorizes_formal_worker_zero", "authorizes_pod",
                "authorizes_registered_timing", "authorizes_target_prepare",
                "goal5791_target_timing_observed",
            )) \
            or type(preregistration.get("formal_worker_count_executed")) \
                is not int \
            or preregistration.get("formal_worker_count_executed") != 0 \
            or type(preregistration.get(
                "registered_performance_timing_count")) is not int \
            or preregistration.get("registered_performance_timing_count") != 0:
        raise IndependentPortableAuditError(
            "v25 preregistration v9 identity or authorization drifted")

    pretarget = _strict_json_bytes(
        payloads[PRETARGET_V9_MEMBER], PRETARGET_V9_MEMBER)
    pretarget_unsigned = dict(pretarget)
    pretarget_claimed = pretarget_unsigned.pop("authority_sha256", None)
    if pretarget_claimed != PRETARGET_V9_SHA256 \
            or _digest(pretarget_unsigned) != PRETARGET_V9_SHA256 \
            or pretarget.get("formal_contract_sha256") \
                != FORMAL_CONTRACT_SHA256 \
            or pretarget.get("schedule_sha256") != SCHEDULE_SHA256 \
            or pretarget.get("target_materialization_binding") is not None \
            or pretarget.get("authorization") != {
                "authorizes_formal_workers": False,
                "authorizes_pod": False,
                "authorizes_registered_timing": False,
                "authorizes_target_prepare": False,
            } \
            or type(pretarget.get("formal_worker_count")) is not int \
            or pretarget.get("formal_worker_count") != 0 \
            or type(pretarget.get("registered_performance_timing_count")) \
                is not int \
            or pretarget.get("registered_performance_timing_count") != 0:
        raise IndependentPortableAuditError(
            "v25 pretarget v9 identity or authorization drifted")

    successor = _strict_json_bytes(
        payloads[PAPER_OUTCOME_SUCCESSOR_AUTHORITY_MEMBER],
        PAPER_OUTCOME_SUCCESSOR_AUTHORITY_MEMBER,
    )
    successor_unsigned = dict(successor)
    successor_claimed = successor_unsigned.pop("authority_sha256", None)
    expected_formal = {
        "formal_contract_path": "scripts/goal5791_formal_contract.py",
        "formal_contract_file_sha256": FORMAL_CONTRACT_FILE_SHA256,
        "formal_contract_sha256": FORMAL_CONTRACT_SHA256,
        "formal_worker_path": "scripts/goal5791_formal_worker.py",
        "formal_worker_file_sha256": FORMAL_WORKER_FILE_SHA256,
        "formal_controller_path": "scripts/goal5791_formal_controller.py",
        "formal_controller_file_sha256": FORMAL_CONTROLLER_FILE_SHA256,
        "formal_evaluate_path": "scripts/goal5791_formal_evaluate.py",
        "formal_evaluate_file_sha256": FORMAL_EVALUATE_FILE_SHA256,
        "formal_independent_recount_path": (
            "scripts/goal5791_formal_independent_recount.py"),
        "formal_independent_recount_file_sha256": (
            FORMAL_INDEPENDENT_RECOUNT_FILE_SHA256),
        "schedule_sha256": SCHEDULE_SHA256,
        "paper_outcome_consequence_contract_sha256": (
            PAPER_OUTCOME_CONSEQUENCE_CONTRACT_SHA256),
        "trace_instrumentation_contract_sha256": (
            TRACE_INSTRUMENTATION_CONTRACT_SHA256),
        "formal_worker_count": 96,
        "statistical_row_count": 6,
        "joint_test_count": 57,
        "joint_test_seconds": 675.529,
        "joint_test_status": "PASS",
    }
    expected_preexecution = {
        "preregistration_path": PREREGISTRATION_V9_MEMBER,
        "preregistration_file_sha256": PREREGISTRATION_V9_FILE_SHA256,
        "preregistration_sha256": PREREGISTRATION_V9_SHA256,
        "pretarget_path": PRETARGET_V9_MEMBER,
        "pretarget_file_sha256": PRETARGET_V9_FILE_SHA256,
        "pretarget_authority_sha256": PRETARGET_V9_SHA256,
        "formal_worker_count_executed": 0,
        "registered_performance_timing_count": 0,
        "target_materialization_binding_present": False,
    }
    expected_cpu_identity = {
        "test_module_count": 11,
        "test_modules_sha256": WORKSPACE_CPU_TEST_MODULES_SHA256,
        "workspace_test_id_count": EXPECTED_WORKSPACE_CPU_TEST_COUNT,
        "workspace_test_ids_sha256": EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256,
        "excluded_external_history_test_id_count": 6,
        "excluded_external_history_test_ids_sha256": (
            CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256),
        "clean_test_id_count": EXPECTED_CLEAN_CPU_TEST_COUNT,
        "clean_test_ids_sha256": EXPECTED_CLEAN_CPU_TEST_IDS_SHA256,
    }
    expected_finding = {
        "owner_returned_review_path": OWNER_REVIEW_ABSORPTION_MEMBER,
        "owner_returned_review_file_sha256":
            OWNER_REVIEW_ABSORPTION_FILE_SHA256,
        "finding": (
            "A_ROW_LOCAL_SMALL_RELATIVE_RULE_WAS_FROZEN_BUT_THE_DYNAMIC_"
            "PAPER_OUTCOME_BRANCH_DID_NOT_REQUIRE_OR_REBUILD_THAT_RULE"),
        "predecessor_absorption_path": SMALL_RELATIVE_ABSORPTION_MEMBER,
        "predecessor_absorption_file_sha256":
            SMALL_RELATIVE_ABSORPTION_FILE_SHA256,
        "predecessor_absorption_sha256": SMALL_RELATIVE_ABSORPTION_SHA256,
        "predecessor_p1_closed_status_is_limited_to_row_level_gate_fields":
            True,
        "predecessor_did_not_close_dynamic_branch_selection": True,
        "outcome_directed_post_worker_zero_repair_allowed": False,
    }
    expected_v8 = {
        "formal_contract_file_sha256":
            "fa56a67ba80413f09f4d32dea2e25c5838fad17dde2e94535c7d1271c2cce0f1",
        "formal_contract_sha256":
            "52647441ce4fec3533f56e2770b11d2443109e4cbf084d6f8acb0bd48111a828",
        "formal_worker_file_sha256": FORMAL_WORKER_FILE_SHA256,
        "formal_controller_file_sha256":
            "ee0c5e68e48d12d892bca852c57eb7ed776ceda0cbf76e33f3830b946fc61ad8",
        "formal_evaluate_file_sha256":
            "e6a3ba95f4c1af560e3995448beba4e11ace5dc7e30189930ec318a1d538d83c",
        "formal_independent_recount_file_sha256":
            "1a6a79186e80421b0f35f9daa7649acb18db51d3658f1e2b737359e01b3144d3",
        "preregistration_path": PREREGISTRATION_V8_MEMBER,
        "preregistration_file_sha256": PREREGISTRATION_V8_FILE_SHA256,
        "preregistration_sha256": PREREGISTRATION_V8_SHA256,
        "pretarget_path": PRETARGET_V8_MEMBER,
        "pretarget_file_sha256": PRETARGET_V8_FILE_SHA256,
        "pretarget_authority_sha256": PRETARGET_V8_SHA256,
        "disposition": (
            "IMMUTABLE_HISTORICAL_PREDECESSOR__NOT_CURRENT_STAGE_A_OR_STAGE_B_"
            "CANDIDATE"),
    }
    expected_paper_resident_file_hashes = {
        OWNER_REVIEW_ABSORPTION_MEMBER:
            OWNER_REVIEW_ABSORPTION_FILE_SHA256,
        SMALL_RELATIVE_ABSORPTION_MEMBER:
            SMALL_RELATIVE_ABSORPTION_FILE_SHA256,
        APPEND_ONLY_CORRECTION_AUTHORITY_MEMBER:
            APPEND_ONLY_CORRECTION_AUTHORITY_FILE_SHA256,
        PREREGISTRATION_V8_MEMBER: PREREGISTRATION_V8_FILE_SHA256,
        PRETARGET_V8_MEMBER: PRETARGET_V8_FILE_SHA256,
        "scripts/goal5791_formal_contract.py": FORMAL_CONTRACT_FILE_SHA256,
        "scripts/goal5791_formal_worker.py": FORMAL_WORKER_FILE_SHA256,
        "scripts/goal5791_formal_controller.py": FORMAL_CONTROLLER_FILE_SHA256,
        "scripts/goal5791_formal_evaluate.py": FORMAL_EVALUATE_FILE_SHA256,
        "scripts/goal5791_formal_independent_recount.py":
            FORMAL_INDEPENDENT_RECOUNT_FILE_SHA256,
        PREREGISTRATION_V9_MEMBER: PREREGISTRATION_V9_FILE_SHA256,
        PRETARGET_V9_MEMBER: PRETARGET_V9_FILE_SHA256,
    }
    successor_authorization = successor.get("authorization")
    correction_link = successor.get("append_only_record_correction")
    if set(successor) != {
        "append_only_record_correction", "authority_sha256", "authorization",
        "date", "finding_and_absorption", "goal",
        "historical_v24_home_v24_bundle_v12", "immutable_v8_predecessor",
        "paper_outcome_mechanical_policy", "portable_cpu_gate_successor_identity",
        "schema", "scope_and_claim_boundary", "status", "v9_formal_freeze",
        "v9_preexecution_freeze",
    } or successor.get("schema") \
            != "rtdl.goal5791.paper_outcome_consequence_selection_successor_authority.v1" \
            or successor.get("goal") != 5791 \
            or successor.get("status") \
                != "P1_CLOSED__V9_LOCAL_PRETARGET_FREEZE__NO_EXECUTION_AUTHORITY" \
            or successor_claimed != PAPER_OUTCOME_SUCCESSOR_AUTHORITY_SHA256 \
            or _digest(successor_unsigned) \
                != PAPER_OUTCOME_SUCCESSOR_AUTHORITY_SHA256 \
            or not isinstance(successor_authorization, dict) \
            or len(successor_authorization) != 10 \
            or any(value is not False
                   for value in successor_authorization.values()) \
            or correction_link != {
                "path": APPEND_ONLY_CORRECTION_AUTHORITY_MEMBER,
                "file_sha256": APPEND_ONLY_CORRECTION_AUTHORITY_FILE_SHA256,
                "authority_sha256": APPEND_ONLY_CORRECTION_AUTHORITY_SHA256,
                "formal_v1_single_timing_remains_permanently_ineligible": True,
                "historical_checkpoint_receipt_reference_is_corrected_without_rewriting_predecessor": True,
            } \
            or successor.get("finding_and_absorption") != expected_finding \
            or successor.get("immutable_v8_predecessor") != expected_v8 \
            or successor.get("v9_formal_freeze") != expected_formal \
            or successor.get("v9_preexecution_freeze") \
                != expected_preexecution \
            or successor.get("portable_cpu_gate_successor_identity") \
                != expected_cpu_identity \
            or len(expected_paper_resident_file_hashes) != 12 \
            or any(path not in payloads
                   or _sha_bytes(payloads[path]) != expected
                   for path, expected
                   in expected_paper_resident_file_hashes.items()):
        raise IndependentPortableAuditError(
            "v25 paper-outcome successor authority drifted")


def _frozen_builder_overlay_contract(
    builder_bytes: bytes,
) -> tuple[tuple[str, ...], dict[str, str], str, str]:
    try:
        tree = ast.parse(builder_bytes.decode("utf-8"))
    except (UnicodeError, SyntaxError) as exc:
        raise IndependentPortableAuditError(
            "portable source builder is not parseable UTF-8 Python") from exc
    assignments: dict[str, object] = {}
    for node in tree.body:
        target_name: str | None = None
        value_node: ast.AST | None = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            target_name = node.targets[0].id
            value_node = node.value
        elif isinstance(node, ast.AnnAssign) \
                and isinstance(node.target, ast.Name):
            target_name = node.target.id
            value_node = node.value
        if target_name in {
            "OVERLAY_PATHS", "EXPECTED_OVERLAY_SHA256", "BUILDER_MEMBER",
            "PRESERVED_BASE_MANIFEST_MEMBER",
        } and value_node is not None:
            try:
                assignments[target_name] = ast.literal_eval(value_node)
            except (ValueError, TypeError) as exc:
                raise IndependentPortableAuditError(
                    f"builder frozen literal cannot be decoded: {target_name}"
                ) from exc
    overlay_paths = assignments.get("OVERLAY_PATHS")
    overlay_hashes = assignments.get("EXPECTED_OVERLAY_SHA256")
    builder_member = assignments.get("BUILDER_MEMBER")
    preserved_member = assignments.get("PRESERVED_BASE_MANIFEST_MEMBER")
    if not isinstance(overlay_paths, tuple) \
            or not all(isinstance(item, str) for item in overlay_paths) \
            or len(set(overlay_paths)) != len(overlay_paths) \
            or not isinstance(overlay_hashes, dict) \
            or set(overlay_hashes) != set(overlay_paths) \
            or not all(isinstance(key, str) and isinstance(value, str)
                       and len(value) == 64
                       and all(character in "0123456789abcdef"
                               for character in value)
                       for key, value in overlay_hashes.items()) \
            or not isinstance(builder_member, str) \
            or not isinstance(preserved_member, str):
        raise IndependentPortableAuditError(
            "portable builder overlay contract drifted")
    if set(overlay_paths) != EXPECTED_SOURCE_OVERLAY_PATHS:
        raise IndependentPortableAuditError(
            "portable builder overlay path set differs from trusted auditor")
    return overlay_paths, overlay_hashes, builder_member, preserved_member


def audit_source(
    data: bytes, *, perform_clean_extraction: bool = True,
) -> dict[str, object]:
    payloads = _archive(data, label="source", source=True)
    manifest = _manifest_rehash(
        payloads, SOURCE_MANIFEST, SOURCE_SCHEMA, "files")
    without_manifest = {
        name: blob for name, blob in payloads.items() if name != SOURCE_MANIFEST
    }
    expected_deep = {
        "all_payload_bytes_scanned": True,
        "scanned_payload_count": len(without_manifest),
        "maximum_nested_container_depth": 0,
        "recognized_container_magic_count": 0,
        "recognized_container_suffix_count": 0,
        "recognized_executable_or_device_binary_magic_count": 0,
        "private_cache_member_count": 0,
    }
    required_members = {
        "scripts/goal5791_build_portable_source.py",
        CPU_TEST_GATE_MEMBER,
        "scripts/goal5791_independent_portable_audit.py",
        "scripts/goal5791_independent_home_recount.py",
        "scripts/goal5791_home_clean_validate.py",
        "scripts/goal5791_target_prepare.py",
        "scripts/goal5791_formal_contract.py",
        "scripts/goal5791_formal_worker.py",
        "scripts/goal5791_formal_controller.py",
        "scripts/goal5791_formal_evaluate.py",
        "scripts/goal5791_formal_independent_recount.py",
        PREREGISTRATION_V9_MEMBER,
        PRETARGET_V9_MEMBER,
        ("history/internal_docs/"
         "goal5791_v4_successor_lineage_authority_20260817.json"),
        V1_ZERO_OUTPUT_TERMINAL_MEMBER,
        V1_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER,
        V2_ZERO_OUTPUT_TERMINAL_MEMBER,
        V2_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER,
        DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_MEMBER,
        DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_REPORT_MEMBER,
        ("history/internal_docs/"
         "v4_competitive_cgo_submission_work_plan_after_goal5788_20260816.md"),
        *PRODUCT_DELTA,
    }
    builder_bytes = without_manifest.get(
        "scripts/goal5791_build_portable_source.py")
    if builder_bytes is None:
        raise IndependentPortableAuditError("portable source builder is absent")
    overlay_paths, overlay_hashes, builder_member, preserved_member = (
        _frozen_builder_overlay_contract(builder_bytes))
    helper_bytes = without_manifest.get(CPU_TEST_GATE_MEMBER)
    if helper_bytes is None:
        raise IndependentPortableAuditError(
            "portable CPU test gate helper is absent")
    _frozen_cpu_test_gate_contract(
        builder_bytes=builder_bytes, helper_bytes=helper_bytes)
    if builder_member != "scripts/goal5791_build_portable_source.py" \
            or preserved_member != PRESERVED_BASE_MANIFEST_MEMBER:
        raise IndependentPortableAuditError(
            "portable builder/preserved-base path drifted")
    preserved_base = without_manifest.get(preserved_member)
    if preserved_base is None or _sha_bytes(preserved_base) \
            != BASE_SOURCE_MANIFEST_SHA256:
        raise IndependentPortableAuditError(
            "frozen Goal5790-A1 base manifest bytes drifted")
    base_manifest = _strict_json_bytes(
        preserved_base, PRESERVED_BASE_MANIFEST_MEMBER)
    base_rows_raw = base_manifest.get("files")
    if not isinstance(base_rows_raw, list):
        raise IndependentPortableAuditError("frozen base manifest rows are absent")
    try:
        base_rows = {
            str(row["path"]): (int(row["size_bytes"]), str(row["sha256"]))
            for row in base_rows_raw
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise IndependentPortableAuditError(
            "frozen base manifest row shape drifted") from exc
    if base_manifest.get("schema") \
            != "rtdl.goal5790_a1.portable_source_manifest.v4" \
            or len(base_rows) != len(base_rows_raw) \
            or len(base_rows) != BASE_SOURCE_FILE_COUNT \
            or base_manifest.get("source_tree_sha256") != BASE_SOURCE_TREE_SHA256:
        raise IndependentPortableAuditError("frozen base manifest identity drifted")
    base_canonical_rows = [
        {"path": name, "size_bytes": size, "sha256": sha}
        for name, (size, sha) in sorted(base_rows.items())
    ]
    if _digest(base_canonical_rows) != BASE_SOURCE_TREE_SHA256:
        raise IndependentPortableAuditError("frozen base manifest tree drifted")
    actual_rows = {
        name: (len(blob), _sha_bytes(blob))
        for name, blob in without_manifest.items()
    }
    overlay_set = set(overlay_paths)
    expected_added = (
        (overlay_set - set(base_rows)) | {builder_member, preserved_member}
    )
    actual_added = set(actual_rows) - set(base_rows)
    actual_removed = set(base_rows) - set(actual_rows)
    changed_base = {
        name for name in set(base_rows) & set(actual_rows)
        if base_rows[name] != actual_rows[name]
    }
    expected_file_count = len(base_rows) + len(expected_added)
    expected_nonproduct_overlay_count = (
        len(overlay_paths) + 2 - len(PRODUCT_DELTA)
    )
    if actual_added != expected_added or actual_removed \
            or changed_base != set(PRODUCT_DELTA) \
            or any(actual_rows.get(name, (None, None))[1] != sha
                   for name, sha in overlay_hashes.items()) \
            or any(actual_rows.get(name) != base_rows[name]
                   for name in set(base_rows) - set(PRODUCT_DELTA)):
        raise IndependentPortableAuditError(
            "portable source is not exact frozen base plus exact overlay")
    if set(manifest) != SOURCE_MANIFEST_KEYS \
            or manifest.get("goal") != 5791 \
            or manifest.get("status") \
                != "PORTABLE_SOURCE_FROZEN__HOME_REQUALIFICATION_REQUIRED" \
            or manifest.get("base_source_archive_sha256") \
                != BASE_SOURCE_SHA256 \
            or manifest.get("base_source_manifest_sha256") \
                != BASE_SOURCE_MANIFEST_SHA256 \
            or manifest.get("base_source_tree_sha256") \
                != BASE_SOURCE_TREE_SHA256 \
            or manifest.get("base_source_file_count_excluding_manifest") \
                != BASE_SOURCE_FILE_COUNT \
            or manifest.get("old_source_manifest_removed") \
                != BASE_SOURCE_MANIFEST_MEMBER \
            or manifest.get("manifest_is_non_self_referential") is not True \
            or manifest.get("file_count_excluding_this_manifest") \
                != expected_file_count \
            or len(without_manifest) \
                != expected_file_count \
            or manifest.get("nonproduct_overlay_count_including_builder") \
                != expected_nonproduct_overlay_count \
            or manifest.get("deep_blob_audit") != expected_deep \
            or type(manifest.get("home_or_target_execution_count")) is not int \
            or manifest.get("home_or_target_execution_count") != 0 \
            or type(manifest.get("formal_worker_count")) is not int \
            or manifest.get("formal_worker_count") != 0 \
            or type(manifest.get("registered_performance_timing_count")) is not int \
            or manifest.get("registered_performance_timing_count") != 0 \
            or not required_members.issubset(without_manifest) \
            or manifest.get("source_tree_sha256") != _digest(_rows(without_manifest)) \
            or manifest.get("product_delta_paths") != sorted(PRODUCT_DELTA) \
            or manifest.get("product_delta") != PRODUCT_DELTA_RECORDS \
            or any(_sha_bytes(without_manifest[name]) != sha
                   for name, sha in PRODUCT_DELTA.items()):
        raise IndependentPortableAuditError("source tree/product delta drifted")
    _validate_v1_zero_output_terminal(without_manifest)
    _validate_v2_zero_output_terminal(without_manifest)
    _validate_dual_cpu_gate_successor_authority(without_manifest)
    _validate_v3_zero_output_terminal(without_manifest)
    _validate_v4_clean_failure_successor_authority(without_manifest)
    _validate_stage_a_v15_successor_authority(without_manifest)
    _validate_stage_a_v16_successor_authority(without_manifest)
    _validate_stage_a_v16_final_authority(without_manifest)
    _validate_v25_governance_successors(without_manifest)
    for name, blob in without_manifest.items():
        if name.lower().endswith(CONTAINER_SUFFIXES) \
                or _blob_kind(blob) is not None:
            raise IndependentPortableAuditError(
                f"nested binary/container in source: {name}")
    exact = _in_memory_exact_set(payloads)
    result = {
        "archive_sha256": _sha_bytes(data),
        "archive_bytes": len(data),
        "source_tree_sha256": manifest["source_tree_sha256"],
        "source_manifest_sha256": _sha_bytes(payloads[SOURCE_MANIFEST]),
        "payload_count_including_manifest": len(payloads),
        "maximum_nested_container_depth": 0,
        "recognized_binary_or_container_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
        # In the target's pre-root path this is the same exact-set fact rebuilt
        # from already-admitted regular archive members, not a claim that the
        # target wrote or extracted any file before root authorization.
        "clean_extraction": exact,
    }
    if perform_clean_extraction:
        with tempfile.TemporaryDirectory(
            prefix="goal5791_independent_source_",
        ) as temp:
            observed = _extract_and_audit(payloads, Path(temp) / "source")
        if observed != exact:
            raise IndependentPortableAuditError(
                "source clean extraction differs from in-memory exact set")
    return result


def _validate_bundle_manifest(
    *, manifest: dict[str, object], payloads: dict[str, bytes],
    source_payloads: dict[str, bytes], source_summary: dict[str, object],
) -> None:
    a2 = _strict_json_bytes(
        source_payloads[A2_RESULT_MEMBER], A2_RESULT_MEMBER)
    a2_sha = a2.get("canonical_content_sha256")
    if not isinstance(a2_sha, str):
        raise IndependentPortableAuditError(
            "Goal5791 A2 canonical digest is absent")
    payload_rows = _rows({
        name: blob for name, blob in payloads.items()
        if name != "BUNDLE_MANIFEST.json"
    })
    zero_fields = {
        "formal_worker_count_executed": 0,
        "registered_performance_timing_count": 0,
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
    }
    if set(manifest) != BUNDLE_MANIFEST_KEYS \
            or manifest.get("schema") != BUNDLE_SCHEMA \
            or manifest.get("goal") != 5791 \
            or manifest.get("status") \
                != "FROZEN_PRE_POD_PACKET__SEPARATE_OWNER_AUTHORITIES_REQUIRED" \
            or manifest.get("manifest_is_non_self_referential") is not True \
            or manifest.get("payloads") != payload_rows \
            or manifest.get("payload_count_excluding_manifest") \
                != len(payload_rows) \
            or manifest.get("payload_bytes_excluding_manifest") \
                != sum(int(row["size_bytes"]) for row in payload_rows) \
            or manifest.get("source_archive_sha256") \
                != source_summary["archive_sha256"] \
            or manifest.get("source_tree_sha256") \
                != source_summary["source_tree_sha256"] \
            or manifest.get("source_manifest_sha256") \
                != source_summary["source_manifest_sha256"] \
            or manifest.get("source_build_receipt_file_sha256") \
                != _sha_bytes(payloads["SOURCE_BASE_AND_OVERLAY_AUTHORITY.json"]) \
            or manifest.get("source_independent_audit_file_sha256") \
                != _sha_bytes(payloads["SOURCE_INDEPENDENT_AUDIT.json"]) \
            or manifest.get("home_functional_closure_file_sha256") \
                != _sha_bytes(payloads["HOME_FUNCTIONAL_CLOSURE.json"]) \
            or manifest.get("home_evidence_independent_audit_file_sha256") \
                != _sha_bytes(payloads["HOME_EVIDENCE_INDEPENDENT_AUDIT.json"]) \
            or manifest.get("home_evidence_manifest_sha256") \
                != _sha_bytes(payloads["HOME_EVIDENCE_MANIFEST.json"]) \
            or manifest.get("home_functional_recount_sha256") \
                != _sha_bytes(payloads["HOME_FUNCTIONAL_RECOUNT.json"]) \
            or manifest.get(
                "home_independent_recount_reexecuted_and_byte_identical") is not True \
            or manifest.get("formal_contract_file_sha256") \
                != FORMAL_CONTRACT_FILE_SHA256 \
            or _sha_bytes(source_payloads["scripts/goal5791_formal_contract.py"]) \
                != FORMAL_CONTRACT_FILE_SHA256 \
            or manifest.get("formal_contract_sha256") \
                != FORMAL_CONTRACT_SHA256 \
            or manifest.get("schedule_sha256") != SCHEDULE_SHA256 \
            or manifest.get("token_amendment_sha256") != a2_sha \
            or manifest.get("token_amendment_chain_sha256") \
                != _digest([TOKEN_AMENDMENT_PREDECESSOR_SHA256, a2_sha]) \
            or manifest.get("external_uploads") != EXPECTED_EXTERNAL_UPLOADS \
            or manifest.get("source_is_only_nested_container") is not True \
            or manifest.get("source_deep_container_depth") != 0 \
            or any(manifest.get(name) is not False for name in (
                "contains_real_scale_data", "contains_wheelhouse",
                "contains_optix_headers", "contains_prebuilt_target_native",
                "contains_owner_prepare_authority",
                "contains_owner_formal_authority",
            )) \
            or any(manifest.get(key) != value
                   for key, value in zero_fields.items()):
        raise IndependentPortableAuditError(
            "bundle manifest exact trusted binding drifted")


def _validate_bundle_source_chain(
    *, payloads: dict[str, bytes], bundle_manifest: dict[str, object],
    source_data: bytes, source_payloads: dict[str, bytes],
    source_summary: dict[str, object],
) -> None:
    receipt = _strict_json_bytes(
        payloads["SOURCE_BASE_AND_OVERLAY_AUTHORITY.json"],
        "SOURCE_BASE_AND_OVERLAY_AUTHORITY.json",
    )
    _reject_home_performance_observations(
        receipt, label="SOURCE_BASE_AND_OVERLAY_AUTHORITY.json")
    if set(receipt) != SOURCE_RECEIPT_KEYS:
        raise IndependentPortableAuditError(
            "portable source receipt exact key set drifted")
    builder_bytes = source_payloads["scripts/goal5791_build_portable_source.py"]
    overlay_paths, overlay_hashes, builder_member, preserved_member = (
        _frozen_builder_overlay_contract(builder_bytes))
    manifest_bytes = source_payloads[SOURCE_MANIFEST]
    manifest = _strict_json_bytes(manifest_bytes, SOURCE_MANIFEST)
    expected_overlay = {
        name: _sha_bytes(source_payloads[name]) for name in overlay_paths
    }
    expected_overlay[builder_member] = _sha_bytes(source_payloads[builder_member])
    directory_names: set[str] = set()
    for name in source_payloads:
        parent = PurePosixPath(name).parent
        while parent.as_posix() not in ("", "."):
            directory_names.add(parent.as_posix())
            parent = parent.parent
    exact_set = {
        "regular_file_count": len(source_payloads),
        "directory_count_excluding_root": len(directory_names),
        "regular_file_set_exact": True,
        "directory_set_exact": True,
        "extra_regular_file_count": 0,
        "extra_directory_count": 0,
        "link_count": 0,
        "reparse_point_count": 0,
        "special_file_count": 0,
    }
    helper_bytes = source_payloads[CPU_TEST_GATE_MEMBER]
    _validate_source_receipt_governance(
        receipt, builder_bytes=builder_bytes, helper_bytes=helper_bytes)
    if receipt.get("schema") \
            != "rtdl.goal5791.portable_source_build_receipt.v26" \
            or receipt.get("status") \
                != "PASS__DETERMINISTIC_NATIVE_FREE_SOURCE__NO_EXECUTION" \
            or receipt.get("base_source_archive_sha256") != BASE_SOURCE_SHA256 \
            or receipt.get("base_source_manifest_sha256") \
                != BASE_SOURCE_MANIFEST_SHA256 \
            or receipt.get("base_source_tree_sha256") != BASE_SOURCE_TREE_SHA256 \
            or receipt.get("base_manifest_rehashed") is not True \
            or receipt.get("preserved_base_manifest_member") \
                != preserved_member \
            or receipt.get("preserved_base_manifest_sha256") \
                != BASE_SOURCE_MANIFEST_SHA256 \
            or receipt.get("source_archive_sha256") != _sha_bytes(source_data) \
            or receipt.get("source_archive_bytes") != len(source_data) \
            or receipt.get("source_twin_sha256") != _sha_bytes(source_data) \
            or receipt.get("source_twin_byte_identical") is not True \
            or receipt.get("source_manifest_member") != SOURCE_MANIFEST \
            or receipt.get("source_manifest_sha256") != _sha_bytes(manifest_bytes) \
            or receipt.get("source_manifest_non_self_referential") is not True \
            or receipt.get("source_tree_sha256") != manifest["source_tree_sha256"] \
            or receipt.get("source_file_count_excluding_manifest") \
                != len(source_payloads) - 1 \
            or receipt.get("archive_payload_count_including_manifest") \
                != len(source_payloads) \
            or receipt.get("archive_payload_bytes") \
                != sum(len(blob) for blob in source_payloads.values()) \
            or receipt.get("builder_path") != builder_member \
            or receipt.get("builder_sha256") != _sha_bytes(builder_bytes) \
            or receipt.get("overlay_sha256") != expected_overlay \
            or receipt.get("product_delta") != PRODUCT_DELTA_RECORDS \
            or receipt.get("changed_product_file_count") != 2 \
            or receipt.get("changed_native_file_count") != 0 \
            or receipt.get("deep_blob_audit") != manifest["deep_blob_audit"] \
            or receipt.get("unsafe_member_count") != 0 \
            or receipt.get("prebuilt_native_or_device_binary_count") != 0 \
            or receipt.get("nested_container_count") != 0 \
            or receipt.get("private_cache_member_count") != 0 \
            or receipt.get("empty_directory_extract_rehash_passed") is not True \
            or receipt.get("clean_extraction_exact_set_before_tests") != exact_set \
            or receipt.get("clean_extraction_exact_set_after_tests") != exact_set \
            or receipt.get("cpu_test_gate_helper_member") \
                != CPU_TEST_GATE_MEMBER \
            or receipt.get("cpu_test_gate_helper_sha256") \
                != _sha_bytes(helper_bytes) \
            or receipt.get("cpu_test_timeout_seconds") \
                != CPU_TEST_TIMEOUT_SECONDS \
            or any(type(receipt.get(key)) is not int or receipt[key] != 0
                   for key in (
                        "home_or_target_execution_count", "gpu_execution_count",
                        "pod_execution_count", "formal_worker_count",
                        "registered_performance_timing_count",
                        "reported_elapsed_value_count",
                        "test_or_scientific_clock_sample_count")) \
            or receipt.get(
                "operational_timeout_watchdog_uses_host_clock") is not True \
            or receipt.get(
                "operational_watchdog_clock_not_persisted_or_registered") \
                is not True \
            or any(receipt.get(key) is not False for key in (
                "home_performance_observation_created",
                "home_performance_diagnostic_used",
                "performance_or_compiler_fusion_claimed")) \
            or any(receipt.get(key) is not True for key in (
                "requires_fresh_home_token_path_qualification",
                "requires_separate_owner_target_prepare_authority",
                "requires_separate_postprepare_owner_formal_authority")):
        raise IndependentPortableAuditError(
            "portable source receipt/content cross-binding drifted")
    if bundle_manifest.get("source_build_receipt_file_sha256") \
            != _sha_bytes(payloads["SOURCE_BASE_AND_OVERLAY_AUTHORITY.json"]):
        raise IndependentPortableAuditError(
            "bundle/source receipt file binding drifted")
    source_audit = _strict_json_bytes(
        payloads["SOURCE_INDEPENDENT_AUDIT.json"],
        "SOURCE_INDEPENDENT_AUDIT.json",
    )
    _reject_home_performance_observations(
        source_audit, label="SOURCE_INDEPENDENT_AUDIT.json")
    _require_goal_5791(source_audit, label="independent source audit")
    expected_clean_extraction = {
        "regular_file_count": len(source_payloads),
        "directory_count_excluding_root": len(directory_names),
        "regular_file_set_exact": True,
        "directory_set_exact": True,
        "link_reparse_or_special_count": 0,
    }
    summary_without_clean_extraction = {
        key: value for key, value in source_summary.items()
        if key != "clean_extraction"
    }
    expected_audit_keys = set(summary_without_clean_extraction) | {
        "clean_extraction",
        "schema", "goal", "status", "kind", "twin_sha256",
        "twin_byte_identical", "implementation_imports_primary_builder",
        "home_or_target_execution_count", "pod_execution_count",
    }
    if set(source_audit) != expected_audit_keys \
            or source_audit.get("schema") \
                != "rtdl.goal5791.independent_portable_audit.v1" \
            or source_audit.get("status") \
                != "PASS__INDEPENDENT_DEEP_ARCHIVE_AND_TWIN_AUDIT" \
            or source_audit.get("kind") != "source" \
            or source_audit.get("goal") != 5791 \
            or source_audit.get("twin_sha256") != _sha_bytes(source_data) \
            or source_audit.get("twin_byte_identical") is not True \
            or source_audit.get("implementation_imports_primary_builder") is not False \
            or source_audit.get("home_or_target_execution_count") != 0 \
            or source_audit.get("pod_execution_count") != 0 \
            or source_audit.get("clean_extraction") \
                != expected_clean_extraction \
            or (
                "clean_extraction" in source_summary
                and source_summary["clean_extraction"]
                    != expected_clean_extraction
            ) \
            or any(source_audit.get(key) != value
                   for key, value in summary_without_clean_extraction.items()) \
            or bundle_manifest.get("source_independent_audit_file_sha256") \
                != _sha_bytes(payloads["SOURCE_INDEPENDENT_AUDIT.json"]):
        raise IndependentPortableAuditError(
            "bundle independent source-audit chain drifted")


def _validate_bundle_home_chain(
    *, payloads: dict[str, bytes], bundle_manifest: dict[str, object],
    home: dict[str, object], source_summary: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    evidence_manifest = _strict_json_bytes(
        payloads["HOME_EVIDENCE_MANIFEST.json"],
        "HOME_EVIDENCE_MANIFEST.json",
    )
    evidence_audit = _strict_json_bytes(
        payloads["HOME_EVIDENCE_INDEPENDENT_AUDIT.json"],
        "HOME_EVIDENCE_INDEPENDENT_AUDIT.json",
    )
    recount = _strict_json_bytes(
        payloads["HOME_FUNCTIONAL_RECOUNT.json"],
        "HOME_FUNCTIONAL_RECOUNT.json",
    )
    for label, value in (
        ("HOME_EVIDENCE_MANIFEST.json", evidence_manifest),
        ("HOME_EVIDENCE_INDEPENDENT_AUDIT.json", evidence_audit),
        ("HOME_FUNCTIONAL_RECOUNT.json", recount),
    ):
        _reject_home_performance_observations(value, label=label)
    if set(evidence_manifest) != HOME_EVIDENCE_MANIFEST_KEYS \
            or set(evidence_audit) != HOME_EVIDENCE_AUDIT_KEYS \
            or set(recount) != HOME_RECOUNT_KEYS:
        raise IndependentPortableAuditError(
            "bundle Home evidence chain exact key set drifted")
    facts = evidence_manifest.get("home_functional_facts")
    if not isinstance(facts, dict) \
            or set(facts) != HOME_EVIDENCE_BOUND_CLOSURE_KEYS \
            or any(home.get(key) != value for key, value in facts.items()):
        raise IndependentPortableAuditError(
            "bundle Home closure differs from evidence-bound functional facts")
    evidence_rows = evidence_manifest.get("files")
    if not isinstance(evidence_rows, list):
        raise IndependentPortableAuditError("Home evidence manifest rows absent")
    expected_evidence_names = (
        EXPECTED_HOME_RAW_MEMBERS | EXPECTED_HOME_INPUT_MEMBERS | {
            "EXECUTION_SOURCE.tar.gz",
            "TARGET_NATIVE/librtdl_optix.so",
            "TARGET_MATERIALIZATION_AUTHORITY.json",
            "TARGET_MATERIALIZATION_EVIDENCE.tar.gz",
            "TARGET_PROGRAM_INSPECTION.json",
            "SOURCE_MANIFEST.json",
            "FUNCTIONAL_RECOUNT.json",
        }
    )
    try:
        evidence_row_map = {
            str(row["path"]): (int(row["size_bytes"]), str(row["sha256"]))
            for row in evidence_rows
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise IndependentPortableAuditError(
            "Home evidence manifest row shape drifted") from exc
    raw_sha = recount.get("raw_lane_sha256")
    if not isinstance(raw_sha, dict):
        raise IndependentPortableAuditError("Home recount raw SHA map absent")
    expected_raw_basenames = {
        name.removeprefix("RAW/") for name in EXPECTED_HOME_RAW_MEMBERS
    }
    if set(evidence_row_map) != expected_evidence_names \
            or len(evidence_row_map) != len(evidence_rows) \
            or set(raw_sha) != expected_raw_basenames \
            or any(evidence_row_map[f"RAW/{name}"][1] != sha
                   for name, sha in raw_sha.items()):
        raise IndependentPortableAuditError(
            "Home evidence/recount exact member identity drifted")
    zero_fields = {
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
    }
    if evidence_manifest.get("schema") != HOME_EVIDENCE_SCHEMA \
            or evidence_manifest.get("status") \
                != "PASS__10_OF_10_TOKEN_ONLY_HOME_EVIDENCE" \
            or evidence_manifest.get("manifest_is_non_self_referential") is not True \
            or evidence_manifest.get("execution_source_archive_sha256") \
                != source_summary["archive_sha256"] \
            or evidence_manifest.get("execution_source_tree_sha256") \
                != source_summary["source_tree_sha256"] \
            or evidence_manifest.get("source_manifest_sha256") \
                != source_summary["source_manifest_sha256"] \
            or evidence_manifest.get("native_library_sha256") \
                != home.get("native_library_sha256") \
            or evidence_manifest.get("functional_recount_sha256") \
                != _sha_bytes(payloads["HOME_FUNCTIONAL_RECOUNT.json"]) \
            or evidence_manifest.get("payload_count_excluding_manifest") \
                != len(evidence_rows) \
            or evidence_manifest.get("payload_bytes_excluding_manifest") \
                != sum(size for size, _ in evidence_row_map.values()) \
            or evidence_manifest.get("pod_used") is not False \
            or any(evidence_manifest.get(key) != value
                   for key, value in zero_fields.items()):
        raise IndependentPortableAuditError(
            "Home evidence manifest/source chain drifted")
    if evidence_audit.get("schema") \
            != "rtdl.goal5791.independent_portable_audit.v1" \
            or evidence_audit.get("status") \
                != "PASS__INDEPENDENT_DEEP_ARCHIVE_AND_TWIN_AUDIT" \
            or evidence_audit.get("kind") != "home-evidence" \
            or evidence_audit.get("archive_sha256") \
                != home.get("home_evidence_sha256") \
            or evidence_audit.get("twin_sha256") \
                != home.get("home_evidence_twin_sha256") \
            or evidence_audit.get("twin_byte_identical") is not True \
            or evidence_audit.get("evidence_manifest_sha256") \
                != _sha_bytes(payloads["HOME_EVIDENCE_MANIFEST.json"]) \
            or evidence_audit.get("source") != source_summary \
            or evidence_audit.get("native_library_sha256") \
                != home.get("native_library_sha256") \
            or evidence_audit.get("raw_lane_count") != 10 \
            or evidence_audit.get("independent_input_count") != 4 \
            or evidence_audit.get("maximum_nested_container_depth") != 2 \
            or evidence_audit.get("implementation_imports_primary_builder") is not False \
            or evidence_audit.get("home_or_target_execution_count") != 0 \
            or evidence_audit.get("pod_execution_count") != 0 \
            or any(evidence_audit.get(key) != value
                   for key, value in zero_fields.items()):
        raise IndependentPortableAuditError(
            "Home independent audit/source chain drifted")
    if recount.get("schema") \
            != "rtdl.goal5791.independent_home_token_recount.v1" \
            or recount.get("status") \
                != "PASS__10_OF_10_TOKEN_ONLY_EXACT_BEHAVIORAL_TRUE_OPTIX" \
            or recount.get("execution_source_archive_sha256") \
                != source_summary["archive_sha256"] \
            or recount.get("execution_source_tree_sha256") \
                != source_summary["source_tree_sha256"] \
            or recount.get("native_library_sha256") \
                != home.get("native_library_sha256") \
            or recount.get("target_materialization_receipt_sha256") \
                != home.get("target_materialization_receipt_sha256") \
            or recount.get("ptx_program_identity_sha256") \
                != home.get("ptx_program_identity_sha256") \
            or recount.get("raw_lane_count") != 10 \
            or recount.get("exact_lane_count") != 10 \
            or recount.get("behavioral_true_optix_lane_count") != 10 \
            or recount.get("token_only_lane_count") != 10 \
            or recount.get("fresh_parent_pid_count") != 10 \
            or recount.get("event_count_per_receipt") \
                != {"fusion_on": 2, "fusion_off": 7} \
            or recount.get("performance_or_compiler_fusion_claimed") is not False \
            or recount.get("product_or_execution_route_imported") is not False \
            or recount.get(
                "controller_worker_evaluator_or_formal_recount_imported") is not False \
            or any(recount.get(key) != value
                   for key, value in zero_fields.items()):
        raise IndependentPortableAuditError("Home recount/source chain drifted")
    if home.get("home_evidence_manifest_sha256") \
            != _sha_bytes(payloads["HOME_EVIDENCE_MANIFEST.json"]) \
            or home.get("home_evidence_independent_audit_sha256") \
                != _sha_bytes(payloads["HOME_EVIDENCE_INDEPENDENT_AUDIT.json"]) \
            or bundle_manifest.get("home_evidence_manifest_sha256") \
                != _sha_bytes(payloads["HOME_EVIDENCE_MANIFEST.json"]) \
            or bundle_manifest.get(
                "home_evidence_independent_audit_file_sha256") \
                != _sha_bytes(payloads["HOME_EVIDENCE_INDEPENDENT_AUDIT.json"]) \
            or bundle_manifest.get("home_functional_recount_sha256") \
                != _sha_bytes(payloads["HOME_FUNCTIONAL_RECOUNT.json"]) \
            or bundle_manifest.get(
                "home_independent_recount_reexecuted_and_byte_identical") is not True:
        raise IndependentPortableAuditError(
            "bundle/Home small-chain file binding drifted")
    return evidence_manifest, evidence_audit, recount


def _validate_semantic_authority(
    *, semantic: dict[str, object], source_summary: dict[str, object],
    source_payloads: dict[str, bytes], home: dict[str, object],
) -> None:
    source_policy_bytes = source_payloads[SOURCE_AUTHORITY_MEMBER]
    shared_bytes = source_payloads[SHARED_FREEZE_MEMBER]
    a1_bytes = source_payloads[A1_RESULT_MEMBER]
    a2_bytes = source_payloads[A2_RESULT_MEMBER]
    lineage_bytes = source_payloads[V4_LINEAGE_AUTHORITY_MEMBER]
    source_policy = _strict_json_bytes(
        source_policy_bytes, SOURCE_AUTHORITY_MEMBER)
    shared = _strict_json_bytes(shared_bytes, SHARED_FREEZE_MEMBER)
    a1 = _strict_json_bytes(a1_bytes, A1_RESULT_MEMBER)
    a2 = _strict_json_bytes(a2_bytes, A2_RESULT_MEMBER)
    lineage = _strict_json_bytes(lineage_bytes, V4_LINEAGE_AUTHORITY_MEMBER)
    lineage_unsigned = dict(lineage)
    lineage_claimed = lineage_unsigned.pop("authority_sha256", None)
    if lineage_claimed != _digest(lineage_unsigned) \
            or lineage.get("status") \
                != "V4_CONTROLLING_LINEAGE_FROZEN__NOT_EXECUTION_AUTHORITY" \
            or not isinstance(lineage.get("authorization"), dict) \
            or any(value is not False
                   for value in lineage["authorization"].values()):
        raise IndependentPortableAuditError(
            "Goal5791 v4 successor lineage seal/authorization drifted")
    body = {
        "schema": "rtdl.goal5791.semantic_physical_variant_successor_authority.v1",
        "goal": 5791,
        "status": "FROZEN_PRE_POD_SUCCESSOR_IDENTITY__NOT_EXECUTION_AUTHORITY",
        "source": {
            "archive_sha256": source_summary["archive_sha256"],
            "tree_sha256": source_summary["source_tree_sha256"],
            "manifest_sha256": source_summary["source_manifest_sha256"],
            "successor_source_policy_file_sha256": _sha_bytes(
                source_policy_bytes),
            "successor_source_policy_sha256": source_policy[
                "authority_sha256"],
            "exact_product_delta": {
                name: _sha_bytes(source_payloads[name])
                for name in sorted(PRODUCT_DELTA)
            },
            "v4_successor_lineage_authority_path": (
                V4_LINEAGE_AUTHORITY_MEMBER),
            "v4_successor_lineage_authority_file_sha256": _sha_bytes(
                lineage_bytes),
            "v4_successor_lineage_authority_sha256": lineage_claimed,
        },
        "shared_freeze": {
            "path": SHARED_FREEZE_MEMBER,
            "file_sha256": _sha_bytes(shared_bytes),
            "shared_contract_freeze_sha256": shared[
                "shared_contract_freeze_sha256"],
            "semantic_request_sha256": shared["semantic_request_sha256"],
            "physical_encoding_sha256": shared[
                "physical_encoding_sha256"],
        },
        "token_amendments": [
            {
                "amendment_id": "Goal5791-A1",
                "file_sha256": _sha_bytes(a1_bytes),
                "canonical_content_sha256": a1[
                    "canonical_content_sha256"],
            },
            {
                "amendment_id": "Goal5791-A2",
                "file_sha256": _sha_bytes(a2_bytes),
                "canonical_content_sha256": a2[
                    "canonical_content_sha256"],
            },
        ],
        "causal_pair": {
            "paper_algorithm": "RT-2A1",
            "mechanism_id": "checked_u64_product_sum_downstream_lowering.v1",
            "same_semantic_ir_required": True,
            "same_physical_encoding_required": True,
            "same_optix_per_ray_producer_required": True,
            "same_source_native_target_and_cohort_required": True,
            "fusion_on_operation_ids": [
                "checked_summary.kernel_launch",
                "checked_summary.summary_copy_sync",
            ],
            "fusion_off_operation_ids": [
                "maximum_weight.logical_reduce",
                "maximum_weight.scalar_copy_sync",
                "weight_sum.logical_reduce",
                "weight_sum.scalar_copy_sync",
                "weighted_product.materialize",
                "weighted_product_sum.logical_reduce",
                "weighted_product_sum.scalar_copy_sync",
            ],
            "sole_allowed_delta": (
                "downstream_checked_u64_reducer_operation_identity_and_event_sequence"
            ),
            "compiler_fusion_performance_claim_authorized_before_result": False,
        },
        "home_functional_closure": {
            "source_archive_sha256": home["execution_source_archive_sha256"],
            "source_tree_sha256": home["execution_source_tree_sha256"],
            "native_library_sha256": home["native_library_sha256"],
            "home_evidence_sha256": home["home_evidence_sha256"],
            "home_evidence_twin_sha256": home[
                "home_evidence_twin_sha256"],
            "home_evidence_manifest_sha256": home[
                "home_evidence_manifest_sha256"],
            "home_evidence_independent_audit_sha256": home[
                "home_evidence_independent_audit_sha256"],
            "exact_lane_count": home["exact_lane_count"],
            "behavioral_true_optix_lane_count": home[
                "behavioral_true_optix_lane_count"],
            "token_only_lane_count": home["token_only_lane_count"],
            "registered_performance_timing_count": home[
                "registered_performance_timing_count"],
            "elapsed_value_count": home["elapsed_value_count"],
            "clock_sample_count": home["clock_sample_count"],
            "home_performance_observation_created": home[
                "home_performance_observation_created"],
            "home_performance_diagnostic_used": home[
                "home_performance_diagnostic_used"],
            "home_native_is_not_target_native": True,
        },
        "authorization": {
            "authorizes_target_prepare": False,
            "authorizes_pod": False,
            "authorizes_formal_worker_zero": False,
            "authorizes_registered_timing": False,
            "authorizes_performance_claim": False,
            "authorizes_publication_or_submission": False,
        },
    }
    expected = {**body, "authority_sha256": _digest(body)}
    if semantic != expected:
        raise IndependentPortableAuditError(
            "semantic successor authority exact trusted reconstruction drifted")


def canonical_readme(
    *, source_sha256: str, source_tree_sha256: str,
) -> bytes:
    return f"""# Goal5791 pre-POD packet

Authority status: `NON_AUTHORITATIVE_RUNBOOK`. This README cannot authorize
Home, POD, Stage A, Stage B, any worker, registered timing, or a performance
claim. Only separately owner-issued, exact-byte authorities can authorize the
operations their schemas explicitly name.

This packet is reviewable preexecution material only. It contains zero owner
authority, formal workers, registered timings, target native, credentials,
real-scale data, wheels, or OptiX SDK headers. The source SHA-256 is
`{source_sha256}` and source tree is `{source_tree_sha256}`.

The native-free packet does not embed the raw Home evidence archive or its
native payload. Formal independent bundle admission is a joint-delivery audit:
the exact packet plus twin and the exact external Home evidence plus twin are
all mandatory. The trusted auditor byte-compares both pairs, reruns the full
external Home evidence audit and raw recount, then cross-binds the packet's
small Home chain. Missing or unequal external evidence fails closed. This
joint audit must complete before an owner creates Stage A. Target prepare sees
only the owner-pinned packet SHA and its internal small chain; it does not by
itself prove the external raw Home archive.

## Fresh Home functional qualification (no POD, no clock/elapsed observation)

Run the exact `HARNESS/CLEAN_VALIDATE.py` byte from this packet with the
matching `SOURCE.tar.gz`, an absent narrow work root, the frozen lx1 Python
3.12.3 environment, CUDA 12.2.2, OptiX 9 include root, and frozen Triangle data
root. Pass `--expected-source-sha256 {source_sha256}`. Preserve `RESULT.json`,
the evidence archive/twin, raw lanes, recount, source archive, and fresh native
before removing the remote work root. Functional lanes sample no clock and
record no elapsed value or performance diagnostic; subprocess timeouts are
unrecorded operational kill guards only.

## Modern-RTX create-only target prepare

Do not run without a separately created owner Stage-A authority that pins the
externally published SHA-256 of `GOAL5791_PRE_POD_BUNDLE.tar.gz`, this source,
all three external uploads, two distinct absent roots (upload staging and
target materialization), six exact staging leaves, target identity, final
formal contract/schedule, and an owner nonce. The exact
`HARNESS/OPEN_UPLOAD_STAGING.py` byte is the first authorized helper. The
Stage-A authority also pins a CPU-only stdin bootstrap; exact
`/usr/bin/python3 -c` rehashes that actual command source from `/proc`, then
verifies the complete helper stdin and Python path/SHA/version before it may
execute the helper. The helper creates only the staging root and seals the
double-absence plus bootstrap/helper/Python observation. The exact staged
`HARNESS/TARGET_PREPARE.py` byte then validates the seven-file read-only
staging set before it may create the target materialization root, build one
fresh native, run only untimed token smokes, and seal `RUNTIME.json`. It
creates zero formal workers and zero registered timings. It must never create
Stage B or remove staging before local evidence preservation.

`OWNER_AUTHORITY_REQUEST_PROTOCOL.md` gives the two exact create-only
generator commands and strict owner-request schemas. The packet contains the
generator but contains no request and no owner authority. Merely possessing
this packet is not approval to run either mode.

External uploads have data SHA-256
`f186cd28a5ae767f968eaa1372cd66285934be430bceb77ff14c6cf94e33e6eb`,
wheelhouse SHA-256
`d0c0f75365a78792cf0c2f548e0bdd144f0ad7175e0d8f83efcf335eb3b311f3`,
and OptiX headers SHA-256
`7fae86ce3dca2fbc2a47be075f02465cf6ee9d9eafd204234f2882fbdeebee54`.

## Formal execution

After Stage A, stop. A new owner Stage-B authority must pin the exact
postprepare authority, target binding, `RUNTIME.json` file SHA-256 and embedded
runtime SHA-256, formal identity, endpoint, existing bound target
materialization root, distinct absent same-parent formal output/controller
staging roots, live free-space admission, 96-worker count, and exactly-once
authorization. No supplied file creates that authority. Never retry, resume,
replace, relabel, drop rows, reuse timings, or extend a budget in place. Both
    the Stage-B authority builder and exact frozen controller must be
    launched with `env -i` and precisely the 14 frozen entries in
`RUNTIME.formal_worker_environment`; `CUPY_CACHE_DIR` and `NUMBA_CACHE_DIR`
are absent until the controller adds two distinct private sibling paths per
worker. The controller first
validates authority/runtime/three-root layout and creates its exact hidden
incomplete staging marker. It then validates the environment and loaded
source, admits exactly one live target row through `/usr/bin/nvidia-smi`, and
only then performs resource, data, and source admission before worker zero.
Cold means only a fresh process plus an empty private CuPy recipe cache; OS
page cache, CUDA driver JIT cache, and OptiX disk cache are not controlled.
Round-major ABBA is mitigation, not control.
""".encode("utf-8")


def audit_bundle(
    data: bytes, *, home_evidence: bytes | None = None,
    home_evidence_twin: bytes | None = None,
) -> dict[str, object]:
    if home_evidence is None or home_evidence_twin is None:
        raise IndependentPortableAuditError(
            "strict bundle audit requires external Home evidence and twin")
    if home_evidence != home_evidence_twin:
        raise IndependentPortableAuditError(
            "external Home evidence/twin bytes differ")
    payloads = _archive(data, label="bundle", source=False)
    _require_exact_bundle_member_set(payloads)
    manifest = _manifest_rehash(
        payloads, "BUNDLE_MANIFEST.json", BUNDLE_SCHEMA, "payloads")
    _reject_home_performance_observations(
        manifest, label="BUNDLE_MANIFEST.json")
    if manifest.get("source_is_only_nested_container") is not True \
            or any(manifest.get(name) is not False for name in (
                "contains_real_scale_data", "contains_wheelhouse",
                "contains_optix_headers", "contains_prebuilt_target_native",
                "contains_owner_prepare_authority",
                "contains_owner_formal_authority",
            )) \
            or manifest.get("formal_worker_count_executed") != 0 \
            or manifest.get("registered_performance_timing_count") != 0 \
            or manifest.get("elapsed_value_count") != 0 \
            or manifest.get("clock_sample_count") != 0 \
            or manifest.get("home_performance_observation_created") is not False \
            or manifest.get("home_performance_diagnostic_used") is not False:
        raise IndependentPortableAuditError("bundle scope/authorization drifted")
    source_data = payloads.get("SOURCE.tar.gz")
    if source_data is None or _sha_bytes(source_data) \
            != manifest.get("source_archive_sha256"):
        raise IndependentPortableAuditError("bundle source binding drifted")
    source = audit_source(source_data)
    source_payloads = _archive(
        source_data, label="bundle nested source", source=True)
    if source["source_tree_sha256"] != manifest.get("source_tree_sha256") \
            or source["source_manifest_sha256"] \
                != manifest.get("source_manifest_sha256"):
        raise IndependentPortableAuditError("bundle/source tree drifted")
    _validate_bundle_manifest(
        manifest=manifest, payloads=payloads,
        source_payloads=source_payloads, source_summary=source,
    )
    if payloads["README.md"] != canonical_readme(
        source_sha256=str(source["archive_sha256"]),
        source_tree_sha256=str(source["source_tree_sha256"]),
    ):
        raise IndependentPortableAuditError(
            "bundle README differs from trusted NON_AUTHORITATIVE_RUNBOOK bytes")
    _validate_bundle_source_chain(
        payloads=payloads, bundle_manifest=manifest,
        source_data=source_data, source_payloads=source_payloads,
        source_summary=source,
    )
    for outer_name, source_name in OUTER_HARNESS_TO_SOURCE.items():
        if payloads.get(outer_name) != source_payloads.get(source_name):
            raise IndependentPortableAuditError(
                f"bundle/source harness bytes drifted: {outer_name}")
    for outer_name, source_name in OUTER_TO_SOURCE_AUTHORITY_MEMBERS.items():
        if payloads.get(outer_name) != source_payloads.get(source_name):
            raise IndependentPortableAuditError(
                f"bundle/source authority bytes drifted: {outer_name}")
    for name, blob in payloads.items():
        if name == "SOURCE.tar.gz":
            continue
        if name.lower().endswith(CONTAINER_SUFFIXES) \
                or _blob_kind(blob) is not None:
            raise IndependentPortableAuditError(
                f"second nested bundle container/binary: {name}")
    home = _strict_json_bytes(
        payloads["HOME_FUNCTIONAL_CLOSURE.json"],
        "HOME_FUNCTIONAL_CLOSURE.json")
    if set(home) != HOME_FUNCTIONAL_CLOSURE_KEYS \
            or home.get("exact_lane_count") != 10 \
            or home.get("behavioral_true_optix_lane_count") != 10 \
            or home.get("token_only_lane_count") != 10 \
            or home.get("registered_performance_timing_count") != 0 \
            or home.get("elapsed_value_count") != 0 \
            or home.get("clock_sample_count") != 0 \
            or home.get("home_performance_observation_created") is not False \
            or home.get("home_performance_diagnostic_used") is not False \
            or home.get("pod_used") is not False:
        raise IndependentPortableAuditError("bundle Home closure drifted")
    _reject_home_performance_observations(
        home, label="HOME_FUNCTIONAL_CLOSURE.json")
    _, embedded_home_audit, _ = _validate_bundle_home_chain(
        payloads=payloads, bundle_manifest=manifest,
        home=home, source_summary=source,
    )
    external_home = audit_home_evidence(home_evidence)
    external_payloads = _archive(
        home_evidence, label="external Home evidence", source=False)
    expected_embedded_home_audit = {
        "schema": "rtdl.goal5791.independent_portable_audit.v1",
        "goal": 5791,
        "status": "PASS__INDEPENDENT_DEEP_ARCHIVE_AND_TWIN_AUDIT",
        "kind": "home-evidence",
        **external_home,
        "twin_sha256": _sha_bytes(home_evidence_twin),
        "twin_byte_identical": True,
        "implementation_imports_primary_builder": False,
        "home_or_target_execution_count": 0,
        "pod_execution_count": 0,
    }
    if embedded_home_audit != expected_embedded_home_audit \
            or external_payloads.get("EVIDENCE_MANIFEST.json") \
            != payloads["HOME_EVIDENCE_MANIFEST.json"] \
            or external_payloads.get("FUNCTIONAL_RECOUNT.json") \
                != payloads["HOME_FUNCTIONAL_RECOUNT.json"] \
            or external_home.get("archive_sha256") \
                != home.get("home_evidence_sha256") \
            or _sha_bytes(home_evidence_twin) \
                != home.get("home_evidence_twin_sha256") \
            or home.get("home_evidence_twin_byte_identical") is not True \
            or external_home.get("source") != source \
            or external_home.get("native_library_sha256") \
                != home.get("native_library_sha256") \
            or external_home.get("evidence_manifest_sha256") \
                != _sha_bytes(payloads["HOME_EVIDENCE_MANIFEST.json"]) \
            or external_home.get("raw_lane_count") != 10 \
            or external_home.get("independent_input_count") != 4 \
            or manifest.get("home_evidence_sha256") \
                != _sha_bytes(home_evidence) \
            or manifest.get("home_evidence_twin_sha256") \
                != _sha_bytes(home_evidence_twin):
        raise IndependentPortableAuditError(
            "external Home evidence/bundle small-chain binding drifted")
    semantic = _strict_json_bytes(
        payloads["SEMANTIC_PHYSICAL_VARIANT_SUCCESSOR_AUTHORITY.json"],
        "SEMANTIC_PHYSICAL_VARIANT_SUCCESSOR_AUTHORITY.json",
    )
    _validate_semantic_authority(
        semantic=semantic, source_summary=source,
        source_payloads=source_payloads, home=home,
    )
    source_receipt = _strict_json_bytes(
        payloads["SOURCE_BASE_AND_OVERLAY_AUTHORITY.json"],
        "SOURCE_BASE_AND_OVERLAY_AUTHORITY.json",
    )
    _reject_home_performance_observations(
        source_receipt, label="SOURCE_BASE_AND_OVERLAY_AUTHORITY.json")
    with tempfile.TemporaryDirectory(prefix="goal5791_independent_bundle_") as temp:
        exact = _extract_and_audit(payloads, Path(temp) / "bundle")
    return {
        "archive_sha256": _sha_bytes(data),
        "archive_bytes": len(data),
        "bundle_manifest_sha256": _sha_bytes(
            payloads["BUNDLE_MANIFEST.json"]),
        "payload_count_including_manifest": len(payloads),
        "source": source,
        "home_evidence_sha256": _sha_bytes(home_evidence),
        "home_evidence_twin_sha256": _sha_bytes(home_evidence_twin),
        "home_evidence_twin_byte_identical": True,
        "home_evidence_manifest_sha256": _sha_bytes(
            payloads["HOME_EVIDENCE_MANIFEST.json"]),
        "home_evidence_independent_audit_sha256": _sha_bytes(
            payloads["HOME_EVIDENCE_INDEPENDENT_AUDIT.json"]),
        "home_independent_raw_recount_reexecuted_and_byte_identical": True,
        "source_is_only_nested_container": True,
        "maximum_nested_container_depth": 1,
        "prebuilt_target_native_count": 0,
        "owner_authority_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
        "clean_extraction": exact,
    }


def audit_home_evidence(data: bytes) -> dict[str, object]:
    payloads = _archive(data, label="Home evidence", source=False)
    manifest = _manifest_rehash(
        payloads, "EVIDENCE_MANIFEST.json", HOME_EVIDENCE_SCHEMA, "files")
    raw_names = {
        name for name in payloads if name.startswith("RAW/")
    }
    input_names = {
        name for name in payloads if name.startswith("INPUTS/")
    }
    fixed = {
        "EXECUTION_SOURCE.tar.gz",
        "TARGET_NATIVE/librtdl_optix.so",
        "TARGET_MATERIALIZATION_AUTHORITY.json",
        "TARGET_MATERIALIZATION_EVIDENCE.tar.gz",
        "TARGET_PROGRAM_INSPECTION.json",
        "SOURCE_MANIFEST.json",
        "FUNCTIONAL_RECOUNT.json",
        "EVIDENCE_MANIFEST.json",
    }
    if set(manifest) != HOME_EVIDENCE_MANIFEST_KEYS \
            or manifest.get("goal") != 5791 \
            or manifest.get("manifest_is_non_self_referential") is not True \
            or raw_names != EXPECTED_HOME_RAW_MEMBERS \
            or input_names != EXPECTED_HOME_INPUT_MEMBERS \
            or set(payloads) != fixed | EXPECTED_HOME_RAW_MEMBERS \
                | EXPECTED_HOME_INPUT_MEMBERS \
            or manifest.get("status") \
                != "PASS__10_OF_10_TOKEN_ONLY_HOME_EVIDENCE" \
            or manifest.get("functional_recount_sha256") \
                != _sha_bytes(payloads["FUNCTIONAL_RECOUNT.json"]) \
            or manifest.get("payload_count_excluding_manifest") \
                != len(payloads) - 1 \
            or manifest.get("payload_bytes_excluding_manifest") \
                != sum(
                    len(blob) for name, blob in payloads.items()
                    if name != "EVIDENCE_MANIFEST.json"
                ) \
            or any(manifest.get(name) != expected for name, expected in {
                "exact_lane_count": 10,
                "behavioral_true_optix_lane_count": 10,
                "token_only_lane_count": 10,
                "formal_worker_count": 0,
                "registered_performance_timing_count": 0,
                "elapsed_value_count": 0,
                "clock_sample_count": 0,
                "home_performance_observation_created": False,
                "home_performance_diagnostic_used": False,
                "pod_used": False,
            }.items()):
        raise IndependentPortableAuditError(
            "Home evidence membership/scope drifted")
    source_bytes = payloads["EXECUTION_SOURCE.tar.gz"]
    source = audit_source(source_bytes)
    execution_source_payloads = _archive(
        source_bytes, label="Home execution source", source=True)
    embedded_recount = execution_source_payloads.get(
        "scripts/goal5791_independent_home_recount.py")
    embedded_audit = execution_source_payloads.get(
        "scripts/goal5791_independent_portable_audit.py")
    expected_recount_path = Path(__file__).resolve().with_name(
        "goal5791_independent_home_recount.py")
    if embedded_recount != expected_recount_path.read_bytes() \
            or embedded_audit != Path(__file__).resolve().read_bytes() \
            or execution_source_payloads.get(SOURCE_MANIFEST) \
                != payloads["SOURCE_MANIFEST.json"]:
        raise IndependentPortableAuditError(
            "Home evidence independent verifier/source bytes drifted")
    native_bytes = payloads["TARGET_NATIVE/librtdl_optix.so"]
    native_sha = _sha_bytes(native_bytes)
    _validate_elf_shared_object(native_bytes)
    if source["archive_sha256"] \
            != manifest.get("execution_source_archive_sha256") \
            or source["source_tree_sha256"] \
                != manifest.get("execution_source_tree_sha256") \
            or source["source_manifest_sha256"] \
                != manifest.get("source_manifest_sha256") \
            or native_sha != manifest.get("native_library_sha256"):
        raise IndependentPortableAuditError(
            "Home evidence source/native identity drifted")
    target_evidence = _archive(
        payloads["TARGET_MATERIALIZATION_EVIDENCE.tar.gz"],
        label="Home target materialization evidence", source=False)
    if set(target_evidence) != EXPECTED_TARGET_EVIDENCE_MEMBERS \
            or target_evidence.get("EXECUTION_SOURCE.tar.gz") \
            != payloads["EXECUTION_SOURCE.tar.gz"] \
            or target_evidence.get("TARGET_NATIVE/librtdl_optix.so") \
                != payloads["TARGET_NATIVE/librtdl_optix.so"] \
            or target_evidence.get("TARGET_PROGRAM_INSPECTION.json") \
                != payloads["TARGET_PROGRAM_INSPECTION.json"] \
            or target_evidence.get("SOURCE_MANIFEST.json") \
                != payloads["SOURCE_MANIFEST.json"]:
        raise IndependentPortableAuditError(
            "Home target evidence/source/native twin drifted")
    target_authority = _strict_json_bytes(
        payloads["TARGET_MATERIALIZATION_AUTHORITY.json"],
        "TARGET_MATERIALIZATION_AUTHORITY.json",
    )
    target_inspection = _strict_json_bytes(
        payloads["TARGET_PROGRAM_INSPECTION.json"],
        "TARGET_PROGRAM_INSPECTION.json",
    )
    _reject_home_performance_observations(
        target_authority, label="TARGET_MATERIALIZATION_AUTHORITY.json")
    _reject_home_performance_observations(
        target_inspection, label="TARGET_PROGRAM_INSPECTION.json")
    authority_unsigned = dict(target_authority)
    authority_claimed = authority_unsigned.pop("receipt_sha256", None)
    identity_fields = (
        "callback_ir_sha256", "callback_authority_nonce", "contract_sha256",
        "abi_sha256", "provider_identity", "program_bundle_identity",
        "composed_program_sha256", "cupy_version",
        "fusion_on_downstream_operation_recipe",
        "fusion_off_downstream_operation_recipe",
        "fusion_on_downstream_operation_recipe_sha256",
        "fusion_off_downstream_operation_recipe_sha256",
        "native_library_sha256", "target_identity_sha256",
    )
    nonce = target_authority.get("materialization_nonce")
    ptx_identity = target_inspection.get("ptx_program_identity")
    if set(target_authority) != TARGET_AUTHORITY_KEYS \
            or set(target_inspection) != TARGET_INSPECTION_KEYS \
            or target_authority.get("schema") \
            != "rtdl.v4.target_materialization_authority.v2" \
            or authority_claimed != _digest(authority_unsigned) \
            or target_authority.get("execution_source_archive_sha256") \
                != source["archive_sha256"] \
            or target_authority.get("execution_source_tree_sha256") \
                != source["source_tree_sha256"] \
            or target_authority.get("source_manifest_sha256") \
                != source["source_manifest_sha256"] \
            or target_authority.get("native_library_sha256") != native_sha \
            or target_authority.get("native_payload_sha256") != native_sha \
            or target_authority.get("evidence_archive_sha256") \
                != _sha_bytes(payloads[
                    "TARGET_MATERIALIZATION_EVIDENCE.tar.gz"]) \
            or target_authority.get("materializer_source_sha256") \
                != _sha_bytes(execution_source_payloads[
                    "scripts/goal5791_home_clean_validate.py"]) \
            or not isinstance(nonce, str) or len(nonce) != 64 \
            or any(character not in "0123456789abcdef" for character in nonce) \
            or target_authority.get(
                "actual_native_rehashed_from_preserved_payload") is not True \
            or target_authority.get(
                "actual_source_tree_recounted_from_preserved_archive") is not True \
            or target_authority.get(
                "cross_target_native_byte_reproducibility_claimed") is not False \
            or target_inspection.get("schema") \
                != "rtdl.goal5791.home_target_program_inspection.v1" \
            or target_inspection.get("provider_identity") != "optix" \
            or target_inspection.get("native_library_sha256") != native_sha \
            or target_inspection.get("application_worker_executed") is not False \
            or target_inspection.get("optix_launch_executed") is not False \
            or target_inspection.get(
                "registered_performance_timing_created") is not False \
            or target_inspection.get("goal5791_token_api_present") is not True \
            or not isinstance(ptx_identity, dict) \
            or target_inspection.get("ptx_program_identity_sha256") \
                != _digest(ptx_identity) \
            or any(target_authority.get(key) != target_inspection.get(key)
                   for key in identity_fields):
        raise IndependentPortableAuditError(
            "Home authority/inspection/source/native chain drifted")
    for name in (
        "TARGET_PROGRAM_INSPECTION.json",
        "PTX_PRODUCER_OBSERVATION.json",
    ):
        nested = target_evidence.get(name)
        if nested is None:
            raise IndependentPortableAuditError(
                f"Home target evidence JSON member absent: {name}")
        nested_value = _strict_json_bytes(
            nested, f"TARGET_MATERIALIZATION_EVIDENCE/{name}")
        _reject_home_performance_observations(
            nested_value, label=f"TARGET_MATERIALIZATION_EVIDENCE/{name}")
    producer_observation = _strict_json_bytes(
        target_evidence["PTX_PRODUCER_OBSERVATION.json"],
        "TARGET_MATERIALIZATION_EVIDENCE/PTX_PRODUCER_OBSERVATION.json",
    )
    home_authority = _strict_json_bytes(
        target_evidence["HOME_MACHINE_AUTHORITY.json"],
        "TARGET_MATERIALIZATION_EVIDENCE/HOME_MACHINE_AUTHORITY.json",
    )
    shared = _strict_json_bytes(
        target_evidence["SHARED_CONTRACT_FREEZE.json"],
        "TARGET_MATERIALIZATION_EVIDENCE/SHARED_CONTRACT_FREEZE.json",
    )
    shared_unsigned = dict(shared)
    shared_claimed = shared_unsigned.pop("shared_contract_freeze_sha256", None)
    if shared_claimed != _digest(shared_unsigned) \
            or shared.get("semantic_request_sha256") \
                != _digest(shared.get("semantic_request")) \
            or shared.get("physical_encoding_sha256") \
                != _digest(shared.get("physical_encoding")) \
            or target_authority.get("shared_contract_freeze_sha256") \
                != shared_claimed:
        raise IndependentPortableAuditError(
            "Home shared-contract freeze seal/cross-binding drifted")
    home_unsigned = dict(home_authority)
    home_claimed = home_unsigned.pop("receipt_sha256", None)
    if target_evidence.get("SHARED_CONTRACT_FREEZE.json") \
            != execution_source_payloads.get(SHARED_FREEZE_MEMBER) \
            or target_evidence.get("HOME_MACHINE_AUTHORITY.json") \
                != execution_source_payloads.get(HOME_AUTHORITY_MEMBER) \
            or home_claimed != _digest(home_unsigned) \
            or target_inspection.get("ptx_producer_observation") \
            != producer_observation \
            or target_inspection.get("home_machine_authority") \
                != home_authority \
            or target_inspection.get("home_machine_authority_sha256") \
                != home_authority.get("receipt_sha256"):
        raise IndependentPortableAuditError(
            "Home producer/machine authority evidence drifted")
    _validate_target_inspection(
        target_inspection, home_authority=home_authority,
        source_payloads=execution_source_payloads,
    )
    recount = _strict_json_bytes(
        payloads["FUNCTIONAL_RECOUNT.json"], "FUNCTIONAL_RECOUNT.json")
    if _sha_bytes(payloads["FUNCTIONAL_RECOUNT.json"]) \
            != manifest.get("functional_recount_sha256") \
            or recount.get("exact_lane_count") != 10 \
            or recount.get("behavioral_true_optix_lane_count") != 10 \
            or recount.get("token_only_lane_count") != 10 \
            or recount.get("elapsed_value_count") != 0 \
            or recount.get("clock_sample_count") != 0 \
            or recount.get("home_performance_observation_created") is not False \
            or recount.get("home_performance_diagnostic_used") is not False \
            or recount.get("target_materialization_receipt_sha256") \
                != target_authority.get("receipt_sha256") \
            or recount.get("ptx_program_identity_sha256") \
                != target_inspection.get("ptx_program_identity_sha256"):
        raise IndependentPortableAuditError("Home evidence recount drifted")
    _reject_home_performance_observations(
        manifest, label="EVIDENCE_MANIFEST.json")
    _reject_home_performance_observations(
        recount, label="FUNCTIONAL_RECOUNT.json")
    for name in sorted(raw_names):
        lane = _strict_json_bytes(payloads[name], name)
        _reject_home_performance_observations(lane, label=name)
    _validate_home_functional_facts(
        manifest.get("home_functional_facts"),
        source_summary=source, source_payloads=execution_source_payloads,
        evidence_payloads=payloads, target_evidence=target_evidence,
        target_authority=target_authority, inspection=target_inspection,
        recount=recount,
    )
    with tempfile.TemporaryDirectory(
        prefix="goal5791_independent_home_replay_",
    ) as replay_temp:
        replay_root = Path(replay_temp)
        source_root = replay_root / "source"
        home_root = replay_root / "home"
        _extract_and_audit(execution_source_payloads, source_root)
        _extract_and_audit(payloads, home_root)
        replay_output = replay_root / "FUNCTIONAL_RECOUNT_REPLAY.json"
        environment = dict(os.environ)
        environment.update({
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "PYTHONPATH": os.pathsep.join((
                str(source_root / "src"), str(source_root))),
        })
        completed = subprocess.run([
            sys.executable,
            str(source_root / "scripts/goal5791_independent_home_recount.py"),
            "--raw", str(home_root / "RAW"),
            "--inputs", str(home_root / "INPUTS"),
            "--expected-source-archive-sha256", source["archive_sha256"],
            "--expected-source-tree-sha256", source["source_tree_sha256"],
            "--expected-native-sha256", native_sha,
            "--output", str(replay_output),
        ], cwd=source_root, env=environment, text=True, encoding="utf-8",
            errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=600, check=False)
        if completed.returncode != 0 \
                or replay_output.read_bytes() \
                    != payloads["FUNCTIONAL_RECOUNT.json"]:
            raise IndependentPortableAuditError(
                "Home independent recount replay drifted: "
                + completed.stdout[-4000:])
    with tempfile.TemporaryDirectory(prefix="goal5791_independent_home_") as temp:
        exact = _extract_and_audit(payloads, Path(temp) / "home")
    return {
        "archive_sha256": _sha_bytes(data),
        "archive_bytes": len(data),
        "evidence_manifest_sha256": _sha_bytes(
            payloads["EVIDENCE_MANIFEST.json"]),
        "payload_count_including_manifest": len(payloads),
        "source": source,
        "native_library_sha256": native_sha,
        "raw_lane_count": len(raw_names),
        "independent_input_count": len(input_names),
        "maximum_nested_container_depth": 2,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
        "clean_extraction": exact,
    }


def joint_bundle_audit_receipt(
    *, bundle: bytes, bundle_twin: bytes,
    home_evidence: bytes, home_evidence_twin: bytes,
) -> dict[str, object]:
    """Recompute and self-seal the mandatory four-file delivery audit."""

    if bundle != bundle_twin:
        raise IndependentPortableAuditError("bundle/twin bytes differ")
    result = audit_bundle(
        bundle, home_evidence=home_evidence,
        home_evidence_twin=home_evidence_twin)
    body = {
        "schema": "rtdl.goal5791.joint_bundle_home_evidence_audit.v1",
        "goal": 5791,
        "status": "PASS__STRICT_JOINT_BUNDLE_AND_EXTERNAL_HOME_EVIDENCE_AUDIT",
        "kind": "bundle",
        **result,
        "twin_sha256": _sha_bytes(bundle_twin),
        "twin_byte_identical": True,
        "implementation_imports_primary_builder": False,
        "home_or_target_execution_count": 0,
        "pod_execution_count": 0,
    }
    return {**body, "receipt_sha256": _digest(body)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--kind", required=True,
        choices=("source", "bundle", "home-evidence"))
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    parser.add_argument("--home-evidence", type=Path)
    parser.add_argument("--home-evidence-twin", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    first = args.archive.read_bytes()
    second = args.twin.read_bytes()
    if first != second:
        raise IndependentPortableAuditError("archive/twin bytes differ")
    if args.kind == "source":
        result = audit_source(first)
    elif args.kind == "bundle":
        if args.home_evidence is None or args.home_evidence_twin is None:
            raise IndependentPortableAuditError(
                "joint bundle audit requires external Home evidence and twin")
        receipt = joint_bundle_audit_receipt(
            bundle=first, bundle_twin=second,
            home_evidence=args.home_evidence.read_bytes(),
            home_evidence_twin=args.home_evidence_twin.read_bytes(),
        )
    else:
        result = audit_home_evidence(first)
    if args.kind != "bundle":
        receipt = {
            "schema": "rtdl.goal5791.independent_portable_audit.v1",
            "goal": 5791,
            "status": "PASS__INDEPENDENT_DEEP_ARCHIVE_AND_TWIN_AUDIT",
            "kind": args.kind,
            **result,
            "twin_sha256": _sha_bytes(second),
            "twin_byte_identical": True,
            "implementation_imports_primary_builder": False,
            "home_or_target_execution_count": 0,
            "pod_execution_count": 0,
        }
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
