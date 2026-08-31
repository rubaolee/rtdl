"""Strict stdlib-only recount for Goal5790-A1 rejected-program evidence.

The recount deliberately imports no ``rtdsl`` module, paper application,
controller, or GPU package.  It verifies three independently recorded arms:

* production admission rejects the frozen association before compilation;
* an isolated, non-registrable diagnostic executes the rejected encoding;
* an accepted control executes the corresponding valid encoding.

The CPU contract is an upstream authority, not an execution schema.  This
module independently replays all six tiny oracles and binds a separate Home
execution specification to the exact upstream suite and case digests.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import struct
from typing import Mapping, Sequence


CPU_SUITE_SCHEMA = "rtdl.goal5790_a1.rejected_encoding_cases.cpu_contract.v1"
EXECUTION_SPEC_SCHEMA = "rtdl.goal5790_a1.home_execution_spec.v2"
EXECUTION_CASE_SCHEMA = "rtdl.goal5790_a1.home_execution_case.v2"
PRE_RUN_AUTHORITIES_SCHEMA = (
    "rtdl.goal5790_a1.pre_run_case_authorities.v1")
SEMANTIC_AUTHORITY_SCHEMA = (
    "rtdl.v4.verified_semantic_requirement_authority.v1")
PHYSICAL_REGISTRY_SCHEMA = (
    "rtdl.v4.verified_physical_guarantee_registry.v1")
PHYSICAL_AUTHORITY_SCHEMA = (
    "rtdl.v4.verified_physical_guarantee_authority.v1")
RAW_SCHEMA = "rtdl.goal5790_a1.home_raw_case.v1"
ADAPTED_RAW_SCHEMA = "rtdl.goal5790_a1.adapted_home_raw_case.v2"
CONTROLLER_SCHEMA = "rtdl.goal5790_a1.home_controller.v1"
WORKER_SCHEMA = "rtdl.goal5790_a1.home_worker.v1"
REJECT_SCHEMA = "rtdl.goal5790_a1.product_admission_reject.v1"
DECISION_SCHEMA = "rtdl.goal5790_a1.product_admission_decision_evidence.v1"
EXECUTION_ARM_SCHEMA = "rtdl.goal5790_a1.execution_arm.v1"
PHYSICAL_IDENTITY_SCHEMA = "rtdl.goal5790_a1.postrun_execution_identity.v2"
EXECUTED_INPUT_SCHEMA = "rtdl.goal5790_a1.exact_executed_input.v1"
DEVICE_CONTINUATION_SCHEMA = (
    "rtdl.goal5790_a1.test_only_device_continuation_receipt.v1")
DEVICE_RECIPE_SCHEMA = "rtdl.goal5790_a1.unchecked_u64_device_recipe.v1"
HOME_AUTHORITY_SCHEMA = "rtdl.goal5790.frozen_home_machine_authority.v3"
RECOUNT_SCHEMA = "rtdl.goal5790_a1.independent_recount.v1"
TRAVERSAL_SCHEMA = "rtdl.physical_execution.traversal_receipt.v1"

CASE_IDS = (
    "builtin_triangle.discrete_interval_boundary.v1",
    "builtin_triangle.deterministic_tie_rank.v1",
    "builtin_triangle.checked_u64_overflow.v1",
    "builtin_triangle.weighted_multiplicity.v1",
    "builtin_triangle.front_back_orientation.v1",
    "custom_aabb.closed_boundary.v1",
)
EXPECTED_RULES = {
    CASE_IDS[0]: "semantic_guarantee_mismatch:exactness",
    CASE_IDS[1]: "semantic_guarantee_mismatch:tie_policy",
    CASE_IDS[2]: "semantic_guarantee_mismatch:overflow_policy",
    CASE_IDS[3]: "semantic_guarantee_mismatch:multiplicity",
    CASE_IDS[4]: "triangle_orientation_mapping",
    CASE_IDS[5]: "semantic_guarantee_mismatch:exactness",
}
PRODUCT_RULE_BY_CASE_RULE = {
    "semantic_guarantee_mismatch:exactness": "SP024_EXACTNESS_POLICY_MISMATCH",
    "semantic_guarantee_mismatch:tie_policy": "SP025_TIE_POLICY_MISMATCH",
    "semantic_guarantee_mismatch:multiplicity": "SP026_MULTIPLICITY_POLICY_MISMATCH",
    "semantic_guarantee_mismatch:overflow_policy": "SP027_OVERFLOW_POLICY_MISMATCH",
    # This unsafe authority is rejected earlier by the production typed-
    # physical-schema orientation gate, before the SP039 admission-core rule.
    "triangle_orientation_mapping": "triangle_orientation_mapping",
}

HOME_AUTHORITY_FILE_SHA256 = (
    "bcfd6a99766621d474dc45aa1b8c896df725575fd1131b64471b5d3d75316314")
HOME_AUTHORITY_RECEIPT_SHA256 = (
    "73fc385cabf2ea5b6cff70eb6d0fc31750cda206377015805c2935f02de6bb40")
PARTICLE_GATE_AUTHORITY_PATH = (
    "history/internal_docs/"
    "goal5790_a1_amendment_a1_particle_earliest_product_gate_20260816.md")
PARTICLE_GATE_AUTHORITY_SHA256 = (
    "84872fdb24f5d398644ec421b55a8a53c7f6cc19af4860ac4ad10f440d958625")
GOAL5790_A1_PLAN_AUTHORITY_PATH = (
    "history/internal_docs/goal5790_a1_rejected_program_suite_plan_20260816.md")
GOAL5790_A1_PLAN_AUTHORITY_SHA256 = (
    "66123ebf1d1b3a6c61b77ac89c2ada61dcb730c6291cd195d5fc2ed11b57ce37")
EXPECTED_CUPY_VERSION = "14.0.1"

SHA_RE = re.compile(r"[0-9a-f]{64}")
IDENTIFIER_RE = re.compile(r"[a-z0-9][a-z0-9_.:-]{1,127}")
FORBIDDEN_GPU_TEXT = re.compile(
    r"(?:librtdl_optix|liboptix|libcuda|libcudart|libnvrtc|libnvvm|"
    r"libdevice(?:\.[^/\\\s\"]+)?\.bc|cupy_backends|numba[/\\]cuda)",
    re.IGNORECASE,
)
FORBIDDEN_MODULE_ROOTS = {"rtdsl", "cupy", "numba", "ctypes"}
ISOLATED_ADMISSION_MODULE = "goal5790_a1_isolated_product_admission"
AUDIT_KINDS = {"modules", "maps_before", "maps_after", "strace"}
U64_MAX = (1 << 64) - 1

# Deliberately duplicated from the isolated diagnostic harness.  The recount
# does not import that harness: it independently reconstructs the only device
# program allowed to demonstrate the unchecked-U64 counterexample.
UNCHECKED_U64_CONTINUATION_SOURCE = r'''
extern "C" __global__ void goal5790_a1_unchecked_weighted_sum(
    const unsigned long long* values,
    const unsigned long long* weights,
    unsigned long long count,
    unsigned long long* output) {
  if (blockIdx.x == 0 && threadIdx.x == 0) {
    unsigned long long total = 0ull;
    for (unsigned long long index = 0; index < count; ++index) {
      total += values[index] * weights[index];
    }
    output[0] = total;
  }
}
'''

CPU_SUITE_FIELDS = {"schema", "cases", "suite_sha256"}
CPU_CASE_FIELDS = {
    "case_id", "geometry_family", "source_authority", "semantic_authority",
    "physical_authority", "expected_rule_id", "minimal_witness",
    "independent_oracle", "unsafe_transform", "counterfactual_execution",
    "case_sha256",
}
EXECUTION_SPEC_FIELDS = {
    "schema", "upstream_suite_sha256", "home_machine_authority_sha256",
    "home_machine_authority_file_sha256",
    "home_machine_authority_evidence_path", "home_toolchain_identity_sha256",
    "cupy_version", "scientific_identity", "pre_run_source_members",
    "pre_run_capture_audit",
    "governance_authority_members",
    "case_count", "cases", "diagnostic_api_audit", "claim_boundary",
    "execution_spec_sha256",
}
PRE_RUN_CAPTURE_AUDIT_FIELDS = {
    "schema", "process_audit_before", "process_audit_after",
    "new_module_names", "forbidden_low_level_imports",
    "rtdsl_namespace_preseeded", "broad_rtdsl_initializer_executed",
    "low_level_compiler_call_count", "native_prepare_call_count",
    "native_execute_call_count", "traversal_launch_count", "audit_sha256",
}
PROCESS_SNAPSHOT_FIELDS = {
    "modules", "modules_sha256", "relevant_memory_maps",
    "relevant_memory_maps_sha256",
}
EXECUTION_CASE_FIELDS = {
    "schema", "case_id", "upstream_case_sha256", "shared_case_identity",
    "pre_run_case_authorities", "expected_product_rejection",
    "accepted_control_expected_disposition",
    "accepted_executed_input_sha256", "diagnostic_executed_input_sha256",
    "declared_executed_input_differences",
    "allowed_postrun_observation_fields",
    "case_execution_spec_sha256",
}
SCIENTIFIC_IDENTITY_FIELDS = {
    "execution_source_archive_sha256", "execution_source_tree_sha256",
    "native_library_sha256", "target_provider", "optix_sdk",
    "compute_capability", "target_identity_sha256",
}
PRE_RUN_SOURCE_MEMBER_FIELDS = {
    "logical_path", "evidence_path", "sha256", "roles",
}
GOVERNANCE_AUTHORITY_MEMBER_FIELDS = {
    "logical_path", "evidence_path", "sha256", "role",
}
PRE_RUN_AUTHORITIES_FIELDS = {
    "schema", "case_id", "case_sha256", "classifier_source_sha256",
    "semantic_authority", "physical_registry",
    "canonical_physical_authority", "diagnostic_physical_authority",
    "canonical_live_family", "diagnostic_live_family",
    "diagnostic_early_reject", "diagnostic_family_attempt",
    "diagnostic_transform_authority", "low_level_compiler_call_count",
    "native_prepare_call_count", "native_execute_call_count",
    "traversal_launch_count", "snapshot_sha256",
}
SEMANTIC_AUTHORITY_FIELDS = {
    "schema", "requirement", "oracle_source_sha256", "issuer_domain",
    "authority_sha256", "authority_nonce",
}
SEMANTIC_REQUIREMENT_FIELDS = {
    "schema", "contract_id", "algorithm_identity", "declared_domain_sha256",
    "policy", "required_hit_semantics", "orientation_contract_sha256",
    "specification_source_sha256",
}
REGISTRY_FIELDS = {
    "schema", "entries", "registry_source_sha256", "issuer_domain",
    "registry_sha256", "authority_nonce",
}
PHYSICAL_GUARANTEE_FIELDS = {
    "schema", "encoding_id", "supported_algorithm_identity",
    "supported_domain_sha256", "orientation_contract_sha256",
    "geometry_family", "schema_sha256", "callback_ir_sha256",
    "effect_digest", "guarantees", "maps", "hit_semantics",
    "gas_graph_depth", "gas_sbt_record_stride", "gas_update_policy",
    "buffer_contract_sha256", "required_target_capabilities",
    "source_manifest",
}
PHYSICAL_MAP_FIELDS = {
    "kind", "source_id", "source_sha256", "consumes", "produces",
}
PHYSICAL_MAP_GRAPH = {
    "encode": (["semantic_input"], ["geometry", "query_state"]),
    "ray": (["query_state"], ["ray"]),
    "trace": (["geometry", "ray"], ["hit_stream"]),
    "continuation": (["hit_stream"], ["candidate_output"]),
    "decode": (["candidate_output"], ["semantic_output"]),
}
REGISTRY_ENTRY_FIELDS = {
    "entry_id", "guarantee", "eligibility", "canonical_template_id",
    "classifier_source_sha256", "source_bytes_manifest_sha256",
}
PHYSICAL_AUTHORITY_FIELDS = {
    "schema", "registry_sha256", "entry", "entry_sha256",
    "authority_sha256", "authority_nonce",
}
LIVE_FAMILY_FIELDS = {
    "family", "callback_ir_sha256", "effect_digest", "schema_sha256",
    "target_sha256", "artifact_kind", "artifact_sha256", "abi_sha256",
    "orientation_contract_sha256", "canonical_template_id", "proof_sha256",
    "family_authority_sha256", "family_authority_nonce",
}
DIAGNOSTIC_ATTEMPT_FIELDS = {
    "family", "callback_ir_sha256", "effect_digest", "schema_sha256",
    "target_sha256", "orientation_authority_sha256",
    "orientation_author_source_sha256",
    "orientation_independent_oracle_sha256", "front_hit_kind",
    "back_hit_kind", "front_hit_selects", "back_hit_selects",
    "verified_family_authority_issued", "plan_issued", "abi_issued",
}
DIAGNOSTIC_TRANSFORM_REQUIRED_FIELDS = {
    "case_id", "transform_id", "unsafe_transform_sha256",
    "implementation_path", "implementation_sha256",
    "test_only_nonregistrable", "production_authority_minted",
    "transform_authority_sha256",
}
POSTRUN_OBSERVATION_FIELDS = (
    "family", "callback_ir_sha256", "callback_effect_digest",
    "physical_or_family_schema_sha256", "target_sha256", "abi_sha256",
    "plan_sha256", "contract_sha256", "executable_sha256",
    "composed_program_sha256", "semantic_admission_sha256",
    "native_library_sha256", "program_bundle",
)
SHARED_CASE_FIELDS = {
    "semantic_request_sha256", "input_sha256", "oracle_authority_sha256",
    "source_authority_sha256",
}
PHYSICAL_IDENTITY_FIELDS = {
    "schema", *POSTRUN_OBSERVATION_FIELDS, "observation_sha256",
}
EXPECTED_REJECTION_FIELDS = {
    "verdict", "expected_rule_id", "required_stable_product_rule_ids",
    "executable", "execution_authorized",
}
API_AUDIT_FIELDS = {
    "diagnostic_entrypoint_path", "diagnostic_entrypoint_sha256",
    "diagnostic_entrypoint_evidence_path",
    "diagnostic_symbol", "product_source_members",
    "diagnostic_symbol_absent_from_product_api",
    "test_only_entrypoint_not_imported_by_product",
    "production_bypass_parameter_present",
}
PRODUCT_SOURCE_MEMBER_FIELDS = {"logical_path", "evidence_path", "sha256"}
CLAIM_BOUNDARY_FIELDS = {
    "home_only", "pod_authorized", "performance_timing_authorized",
    "performance_claimed", "formal_worker", "diagnostic_is_product_bypass",
}
RAW_FIELDS = {
    "schema", "status", "upstream_suite_sha256", "execution_spec_sha256",
    "case_id", "case_sha256", "case_execution_spec_sha256",
    "shared_case_identity", "home_machine_authority_sha256",
    "home_machine_authority_file_sha256", "product_admission_reject",
    "diagnostic_counterfactual", "accepted_control", "claim_boundary",
    "raw_result_sha256",
}
ADAPTED_RAW_FIELDS = {
    "schema", "status", "upstream_suite_sha256", "execution_spec_sha256",
    "case_id", "case_sha256", "case_execution_spec_sha256",
    "controller_result_path", "controller_result_file_sha256",
    "controller_result_sha256", "controller_case_sha256", "source_workers",
    "source_worker_set_sha256", "raw_result_sha256",
}
SOURCE_WORKER_REFERENCE_FIELDS = {
    "path", "file_sha256", "worker_result_sha256", "parent_pid",
}
CONTROLLER_FIELDS = {
    "schema", "status", "scope", "suite_sha256", "suite_file_sha256",
    "execution_spec_file_sha256", "execution_spec_sha256",
    "native_library_sha256", "home_machine", "frozen_home_authority_file",
    "frozen_home_authority_file_sha256",
    "frozen_home_authority_receipt_sha256", "compute_capability", "optix_sdk",
    "case_count", "arm_count", "fresh_parent_pid_count",
    "product_admission_reject_count", "production_facade_reject_count",
    "typed_physical_schema_reject_count", "product_admission_launch_count",
    "accepted_control_count", "diagnostic_counterexample_count",
    "registered_performance_timing_count", "performance_claimed", "pod_used",
    "formal_worker_count", "cache_policy", "cases", "result_sha256",
}
CONTROLLER_CASE_FIELDS = {
    "case_id", "case_sha256", "expected_rule_id", "arms",
}
CONTROLLER_CACHE_FIELDS = {
    "formal_leaf_cache_environment_cleared", "per_arm_cupy_cache",
    "per_arm_numba_cache", "cache_contents_used_as_evidence",
}
WORKER_FIELDS = {
    "schema", "status", "case_id", "case_sha256", "upstream_suite_sha256",
    "execution_spec_sha256", "execution_spec_file_sha256",
    "case_execution_spec_sha256", "input_sha256", "arm", "parent_pid",
    "home_machine", "home_machine_authority_sha256", "cache_policy",
    "arm_result", "elapsed_values_recorded",
    "registered_performance_timing_created", "performance_claimed", "pod_used",
    "formal_worker", "worker_result_sha256",
}
WORKER_CACHE_FIELDS = {
    "formal_leaf_cache_environment_cleared", "cupy_cache_dir",
    "numba_cache_dir", "initially_empty", "per_arm_isolated",
    "cache_is_execution_authority", "cache_contents_used_as_evidence",
}
HOME_MACHINE_FIELDS = {
    "hostname", "gpu", "driver", "uuid", "compute_capability",
    "classification", "frozen_home_authority_file_sha256",
    "frozen_home_authority_receipt_sha256", "home_toolchain_identity_sha256",
    "home_machine_authority_sha256",
}
ACTUAL_EXECUTION_IDENTITY_FIELDS = {
    "family", "callback_ir_sha256", "callback_effect_digest",
    "physical_or_family_schema_sha256", "target_sha256", "abi_sha256",
    "plan_sha256", "contract_sha256", "executable_sha256",
    "composed_program_sha256", "expected_program_bundle",
    "family_authority_nonce", "family_authority_sha256",
    "semantic_admission_sha256", "native_library_sha256",
}
ACTUAL_REJECT_FIELDS = {
    "engine", "verdict", "product_rule_ids", "named_case_rule_id",
    "product_rejection_gate", "production_facade_called", "decision",
    "decision_sha256", "product_facade_path", "product_facade_sha256",
    "semantic_physical_calculus_path", "semantic_physical_calculus_sha256",
    "trusted_test_classifier_path", "trusted_test_classifier_sha256",
    "semantic_authority", "physical_registry", "canonical_physical_authority",
    "diagnostic_physical_authority", "canonical_live_family",
    "diagnostic_live_family", "diagnostic_family_attempt", "target_sha256",
    "native_library_sha256", "process_audit_before", "process_audit_after",
    "new_module_names", "forbidden_gpu_or_compiler_imports",
    "compiler_call_count", "low_level_compiler_call_count",
    "native_prepare_call_count", "native_execute_call_count",
    "traversal_launch_count", "cuda_or_gpu_library_map_observed",
    "cuda_driver_initialization_observed",
    "cuda_driver_initialization_proven_absent",
    "cuda_initialization_evidence_kind", "execution_authorized",
    "executable_issued", "claim_boundary",
}
ACTUAL_REJECT_DECISION_FIELDS = {
    "verdict", "finding", "semantic_authority_sha256",
    "physical_authority_sha256", "canonical_live_family",
    "diagnostic_live_family", "diagnostic_family_attempt",
}
ACTUAL_REJECT_FINDING_FIELDS = {"rule_id", "path", "detail", "gate"}
ACTUAL_REJECT_BOUNDARY_FIELDS = {
    "public_facade_rejects_raw_caller_self_proof",
    "compiler_internal_classifier_is_trusted_tcb",
    "malicious_same_process_reflection_resisted",
    "python_semantics_automatically_inferred",
    "concrete_runtime_input_certified_by_compile_admission",
}
ACTUAL_EXECUTION_COMMON_FIELDS = {
    "declared_semantics", "output", "own_oracle", "requested_semantic_oracle",
    "matches_own_oracle", "matches_requested_semantics",
    "counterexample_observed", "execution_identity", "executed_input",
    "executed_input_sha256", "declared_input_delta", "traversal_receipts",
    "traversal_semantic_bindings", "traversal_output_digest_inputs",
    "expected_program_bundles", "behaviorally_true_optix", "admitted_run_gate",
    "compile_admission_certifies_concrete_runtime_arrays",
}
ACTUAL_TRIANGLE_FIELDS = ACTUAL_EXECUTION_COMMON_FIELDS | {
    "accepted_disposition", "declared_physical_delta",
    "traversal_receipt_claim_scope", "per_ray_u64",
    "test_only_device_continuation", "test_only_optix_producer_diagnostic",
}
ACTUAL_OVERFLOW_ACCEPTED_FIELDS = ACTUAL_EXECUTION_COMMON_FIELDS | {
    "accepted_disposition", "correct_fail_closed", "zero_receipt_reason",
}
ACTUAL_OVERFLOW_DISPOSITION_FIELDS = {
    "status", "error_type", "error_code", "error_path", "output_produced",
}
ACTUAL_U64_PRODUCER_FIELDS = {
    "per_ray_u64", "traversal_receipt", "role_counters",
    "native_library_sha256", "composed_program_sha256",
    "traversal_semantic_binding", "expected_program_bundle",
    "test_only_nonregistrable", "standard_product_reduction_receipt_minted",
}
ACTUAL_ARMS = (
    "product_admission_reject", "accepted_control", "diagnostic_counterfactual",
)
REJECT_FIELDS = {
    "schema", "arm", "status", "parent_pid", "upstream_suite_sha256",
    "case_sha256", "case_execution_spec_sha256", "shared_case_identity",
    "home_machine_authority_sha256", "home_machine_authority_file_sha256",
    "rejected_physical_identity_sha256", "admission_decision",
    "process_audit", "raw_audit_artifacts", "compile_count",
    "native_prepare_count", "native_execute_count", "traversal_launch_count",
    "elapsed_values_recorded", "registered_performance_timing_created",
    "performance_claimed", "pod_used", "formal_worker", "receipt_sha256",
}
DECISION_FIELDS = {
    "schema", "verdict", "expected_rule_id", "stable_product_rule_ids",
    "executable", "execution_authorized", "decision_sha256",
}
PROCESS_AUDIT_FIELDS = {
    "compiler_call_count", "native_prepare_call_count",
    "native_execute_call_count", "traversal_launch_count",
    "admission_module_imported", "admission_module_name",
    "admission_module_source_sha256",
    "admission_module_loaded_from_exact_source", "rtdsl_package_imported",
    "compiler_or_runtime_module_imported", "cupy_imported", "numba_imported",
    "ctypes_imported",
}
AUDIT_ARTIFACT_FIELDS = {"kind", "path", "sha256", "size_bytes"}
EXECUTION_ARM_FIELDS = {
    "schema", "arm", "status", "parent_pid", "upstream_suite_sha256",
    "case_sha256", "case_execution_spec_sha256", "shared_case_identity",
    "home_machine_authority_sha256", "home_machine_authority_file_sha256",
    "physical_identity", "executed_input", "executed_input_sha256",
    "execution_binding_sha256", "outcome", "outcome_sha256", "oracle_value",
    "oracle_value_sha256", "matches_own_oracle",
    "matches_requested_semantics", "counterexample_observed",
    "isolated_test_only_diagnostic", "production_authority_minted",
    "product_api_bypass_parameter_present", "product_source_modified",
    "traversal_receipts", "traversal_semantic_bindings",
    "device_continuation_receipt",
    "traversal_receipt_count", "elapsed_values_recorded",
    "registered_performance_timing_created", "performance_claimed",
    "pod_used", "formal_worker", "receipt_sha256",
}
HOME_AUTHORITY_FIELDS = {
    "schema", "execution_environment_class", "gpu_name", "gpu_uuid",
    "driver_version", "compute_capability", "pod_used",
    "modern_rtx_execution_authorized", "cuda_toolkit_resolved_path",
    "cuda_nvrtc_resolved_path", "cuda_nvrtc_sha256",
    "cuda_nvrtc_builtins_resolved_path", "cuda_nvrtc_builtins_sha256",
    "cuda_nvrtc_runtime_version", "cuda_nvvm_resolved_path",
    "cuda_nvvm_sha256", "cuda_libdevice_resolved_path",
    "cuda_libdevice_sha256", "cuda_nvcc_version",
    "cuda_host_compiler_path", "cuda_host_compiler_version",
    "receipt_sha256",
}
DEVICE_CONTINUATION_FIELDS = {
    "schema", "kind", "kernel_source", "kernel_source_sha256",
    "operation_recipe", "operation_recipe_sha256", "cupy_version",
    "home_machine_authority_sha256", "home_toolchain_identity_sha256",
    "target_identity_sha256",
    "per_ray_u64", "weights_u64", "device_input_sha256", "launch_count",
    "synchronization_count", "device_output_u64", "device_output_sha256",
    "host_fallback_used", "evidence_kind", "receipt_sha256",
}
DEVICE_RECIPE_FIELDS = {
    "schema", "kind", "entry", "kernel_source_sha256", "grid", "block",
    "value_count", "cupy_version", "home_machine_authority_sha256",
    "home_toolchain_identity_sha256", "target_identity_sha256",
}
ACTUAL_DEVICE_CONTINUATION_FIELDS = {
    "schema", "test_only_nonregistrable", "production_authority_minted",
    "kernel_source", "kernel_source_sha256", "kernel_entry",
    "compiler_options", "cupy_version", "cuda_runtime_version", "device_id",
    "target_sha256", "frozen_home_authority_file_sha256",
    "frozen_home_authority_receipt_sha256",
    "home_toolchain_identity_sha256", "input_per_ray_sha256",
    "input_weights_sha256", "per_ray_u64", "weights_u64",
    "input_pair_sha256", "output_value", "output_sha256",
    "operation_recipe", "operation_recipe_sha256",
    "device_kernel_launch_count", "host_synchronization_count",
    "launch_count", "synchronization_count", "device_output_u64",
    "host_fallback_used", "evidence_kind",
    "registered_performance_timing_created",
}
ACTUAL_DEVICE_RECIPE_FIELDS = {
    "operation", "arithmetic", "grid", "block", "compiler_options",
    "input_origin", "host_fallback",
}
HOME_TOOLCHAIN_FIELDS = (
    "cuda_toolkit_resolved_path", "cuda_nvrtc_resolved_path",
    "cuda_nvrtc_sha256", "cuda_nvrtc_builtins_resolved_path",
    "cuda_nvrtc_builtins_sha256", "cuda_nvrtc_runtime_version",
    "cuda_nvvm_resolved_path", "cuda_nvvm_sha256",
    "cuda_libdevice_resolved_path", "cuda_libdevice_sha256",
    "cuda_nvcc_version", "cuda_host_compiler_path",
    "cuda_host_compiler_version",
)
TRIANGLE_EXECUTED_INPUT_FIELDS = {
    "schema", "family", "columns", "event_capacity",
}
RELATION_EXECUTED_INPUT_FIELDS = {
    "schema", "family", "columns", "capacity", "minimum_overlap_f32",
}
BINARY_COLUMN_FIELDS = {
    "scalar_type", "endianness", "count", "bytes_hex", "bytes_sha256",
}
TRIANGLE_COLUMN_FIELDS = {
    "vertices_xyz", "triangle_indices", "query_origin_direction_tmax",
    "primitive_front_values", "primitive_back_values", "query_weights",
}
RELATION_COLUMN_FIELDS = {
    "indexed_bounds_xyxy", "indexed_ids", "source_bounds_xyxy", "source_ids",
}
EXECUTED_INPUT_DELTA_BY_CASE = {
    CASE_IDS[0]: ["columns.query_origin_direction_tmax"],
    CASE_IDS[1]: ["columns.vertices_xyz"],
    CASE_IDS[2]: [],
    CASE_IDS[3]: ["columns.query_weights"],
    CASE_IDS[4]: [
        "columns.primitive_back_values", "columns.primitive_front_values"],
    CASE_IDS[5]: [],
}
OUTCOME_FIELDS = {
    "kind", "value", "error_code", "exception_type", "status_evidence",
}
STATUS_EVIDENCE_FIELDS = {
    "output_emitted", "overflow_detected", "fail_closed",
}
SEMANTIC_BINDING_FIELDS = {
    "authority", "contract", "abi", "composed_ptx", "native",
    "device_column_count",
}
TRAVERSAL_FIELDS = {
    "schema", "provider_library", "provider_library_path",
    "provider_library_sha256", "route_identity", "semantic_digest",
    "output_digest", "nonce", "physical_executor_classification",
    "expected_program_bundles", "expected_program_bundle_ids",
    "expected_program_observed_at_receipt_edge", "native_snapshot",
    "claim_rules", "receipt_sha256",
}
SNAPSHOT_FIELDS = {
    "nonce_hi", "nonce_lo", "attempted_launch_count",
    "successful_launch_count", "failed_launch_count",
    "complete_context_launch_count", "incomplete_context_launch_count",
    "context_bind_count", "raygen_invocation_count", "program_bundle_mix",
    "traversable_mix", "pipeline_mix", "sbt_mix", "stream_mix", "params_mix",
    "callsite_mix", "first_program_bundle_id", "last_program_bundle_id",
    "first_traversable", "last_traversable", "pending_context_at_finish",
    "session_error", "incomplete_callsite_record_count",
    "incomplete_callsite_lines",
}
CLAIM_RULES = {
    "provider_name_alone_proves_traversal": False,
    "selected_template_alone_proves_traversal": False,
    "successful_optix_launch_required": True,
    "nonzero_traversable_binding_required": True,
    "program_bundle_binding_required": True,
    "output_digest_bound": True,
}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _physical_program_bundle_id(name: str) -> int:
    """Independently reproduce the native audit layer's FNV-1a bundle id."""

    require(type(name) is str and bool(name),
            "physical program bundle name is invalid")
    value = 1469598103934665603
    for byte in name.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & U64_MAX
    return value


def sha_file(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def exact(value: object, fields: set[str], label: str) -> dict:
    require(isinstance(value, dict), f"{label} is not an object")
    require(set(value) == fields,
            f"{label} fields drift: {sorted(set(value) ^ fields)}")
    return value


def require_sha(value: object, label: str) -> str:
    require(isinstance(value, str) and SHA_RE.fullmatch(value) is not None,
            f"invalid {label}")
    return value


def require_identifier(value: object, label: str) -> str:
    require(isinstance(value, str) and IDENTIFIER_RE.fullmatch(value) is not None,
            f"invalid {label}")
    return value


def verify_seal(value: Mapping[str, object], field: str, label: str) -> str:
    claimed = require_sha(value.get(field), f"{label}.{field}")
    unsigned = dict(value)
    unsigned.pop(field)
    require(digest(unsigned) == claimed, f"{label} digest mismatch")
    return claimed


def safe_relative(value: object, label: str) -> str:
    require(isinstance(value, str) and value, f"invalid {label}")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts
            and "." not in path.parts and "" not in path.parts,
            f"unsafe {label}")
    return path.as_posix()


def strict_load(path: Path) -> object:
    def pairs(rows: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in rows:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(token: str) -> object:
        raise AssertionError(f"non-finite JSON constant: {token}")

    return json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
        parse_constant=constant,
    )


def _seq(value: object, label: str) -> list:
    require(isinstance(value, list), f"{label} is not a list")
    return value


def _int(value: object, label: str) -> int:
    require(isinstance(value, int) and not isinstance(value, bool),
            f"{label} is not an integer")
    return value


def verify_home_machine_authority(path: Path) -> dict[str, object]:
    """Re-hash and independently validate the frozen Goal5790 Home authority."""

    require(path.is_file(), "frozen Home-machine authority is absent")
    require(sha_file(path) == HOME_AUTHORITY_FILE_SHA256,
            "frozen Home-machine authority file SHA mismatch")
    authority = exact(strict_load(path), HOME_AUTHORITY_FIELDS,
                      "home_machine_authority")
    require(authority.get("schema") == HOME_AUTHORITY_SCHEMA,
            "Home-machine authority schema mismatch")
    require(verify_seal(authority, "receipt_sha256", "home_machine_authority")
            == HOME_AUTHORITY_RECEIPT_SHA256,
            "Home-machine authority receipt mismatch")
    expected = {
        "execution_environment_class": "HOME_PASCAL_FUNCTIONAL_ONLY",
        "gpu_name": "NVIDIA GeForce GTX 1070",
        "gpu_uuid": "GPU-8e04454e-c177-6e5b-3f43-e676980ecdfa",
        "driver_version": "580.126.09",
        "compute_capability": "6.1",
        "pod_used": False,
        "modern_rtx_execution_authorized": False,
        "cuda_toolkit_resolved_path": "/home/lestat/vendor/cuda-12.2.2",
        "cuda_nvrtc_resolved_path": (
            "/home/lestat/vendor/cuda-12.2.2/targets/x86_64-linux/lib/"
            "libnvrtc.so.12.2.140"),
        "cuda_nvrtc_sha256": (
            "000ca6278ba8b32a7dac383eb7440929c5a09095b43dd5f2df3911f63520db70"),
        "cuda_nvrtc_builtins_resolved_path": (
            "/home/lestat/vendor/cuda-12.2.2/targets/x86_64-linux/lib/"
            "libnvrtc-builtins.so.12.2.140"),
        "cuda_nvrtc_builtins_sha256": (
            "968ebb00640e461f587ad96d01735ac85bf4b2ab4d1cb35b3b489c3cf2cc7f18"),
        "cuda_nvrtc_runtime_version": [12, 2],
        "cuda_nvvm_resolved_path": (
            "/home/lestat/vendor/cuda-12.2.2/nvvm/lib64/libnvvm.so.4.0.0"),
        "cuda_nvvm_sha256": (
            "b69eaddcce6a063361f2d172ed535c3d6f7ae494a40c6ffdb7de024f89dbf80a"),
        "cuda_libdevice_resolved_path": (
            "/home/lestat/vendor/cuda-12.2.2/nvvm/libdevice/libdevice.10.bc"),
        "cuda_libdevice_sha256": (
            "5c9f80bf689d5d0e67dabf914a2a865a3d8b8c5ff86b86c46f63c3bb067ca523"),
        "cuda_nvcc_version": "Build cuda_12.2.r12.2/compiler.33191640_0",
        "cuda_host_compiler_path": "/usr/bin/g++-12",
        "cuda_host_compiler_version": (
            "g++-12 (Ubuntu 12.4.0-2ubuntu1~24.04.1) 12.4.0"),
    }
    for field, value in expected.items():
        require(authority.get(field) == value,
                f"Home-machine authority field drift: {field}")
    return authority


def home_toolchain_identity(authority: Mapping[str, object]) -> str:
    """Digest the exact producer/toolchain part of the frozen authority."""

    return digest({field: authority[field] for field in HOME_TOOLCHAIN_FIELDS})


def _leftmost_minimum(values: Sequence[int], left: int, right: int) -> int:
    require(values and 0 <= left <= right < len(values), "invalid RMQ witness")
    return min(range(left, right + 1), key=lambda index: (values[index], index))


def _orientation(a: Sequence[Fraction], b: Sequence[Fraction],
                 p: Sequence[Fraction]) -> Fraction:
    return (b[0] - a[0]) * (p[1] - a[1]) \
        - (b[1] - a[1]) * (p[0] - a[0])


def _inside_closed_triangle(point: Sequence[Fraction], vertices: Sequence[Sequence[Fraction]]) -> bool:
    signs = tuple(_orientation(vertices[i], vertices[(i + 1) % 3], point)
                  for i in range(3))
    return not (any(value < 0 for value in signs)
                and any(value > 0 for value in signs))


def _rmq_counterfactual(witness: Mapping[str, object], *, boundary: bool,
                        reverse_ties: bool) -> int:
    values = [_int(item, "values[]") for item in _seq(witness.get("values"), "values")]
    interval = _seq(witness.get("interval"), "interval")
    require(len(interval) == 2, "invalid interval")
    left, right = (_int(item, "interval[]") for item in interval)
    count = len(values)
    order = sorted(range(count), key=lambda i: (values[i], -i if reverse_ties else i))
    rank = {item: index for index, item in enumerate(order)}
    point = ((Fraction(left, count), Fraction(right, count)) if boundary else
             (Fraction(2 * left + 1, 2 * count),
              Fraction(2 * right - 1, 2 * count)))
    candidates = []
    for index in range(count):
        lo, hi = Fraction(index - 1, count), Fraction(index + 1, count)
        triangle = ((hi, lo), (hi, Fraction(2)), (Fraction(-1), lo))
        if _inside_closed_triangle(point, triangle):
            candidates.append(index)
    require(candidates, "RMQ counterfactual missed all triangles")
    return min(candidates, key=lambda item: rank[item])


def _sub(left: Sequence[Fraction], right: Sequence[Fraction]) -> tuple[Fraction, ...]:
    return tuple(a - b for a, b in zip(left, right))


def _cross(left: Sequence[Fraction], right: Sequence[Fraction]) -> tuple[Fraction, ...]:
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def _dot(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def _orientation_projection(witness: Mapping[str, object], swapped: bool) -> list[int]:
    vertices = tuple(tuple(Fraction(item) for item in _seq(row, "vertex"))
                     for row in _seq(witness.get("vertices"), "vertices"))
    triangle = tuple(_int(item, "triangle[]")
                     for item in _seq(witness.get("triangle"), "triangle"))
    require(len(vertices) == 3 and sorted(triangle) == [0, 1, 2],
            "invalid orientation triangle")
    origin = tuple(Fraction(item) for item in _seq(witness.get("ray_origin"), "origin"))
    direction = tuple(Fraction(item) for item in _seq(witness.get("ray_direction"), "direction"))
    a, b, c = (vertices[index] for index in triangle)
    normal = _cross(_sub(b, a), _sub(c, a))
    denominator = _dot(normal, direction)
    require(denominator != 0 and _dot(normal, _sub(a, origin)) / denominator >= 0,
            "invalid orientation ray")
    front = _int(witness.get("front_value"), "front_value")
    back = _int(witness.get("back_value"), "back_value")
    if swapped:
        front, back = back, front
    is_front = denominator < 0
    return [front if is_front else back, back if is_front else front, 0]


def evaluate_case(case_id: str, witness: Mapping[str, object]) -> tuple[object, object]:
    """Independent implementation of the six frozen CPU counterexamples."""

    if case_id in CASE_IDS[:2]:
        values = [_int(item, "values[]") for item in _seq(witness.get("values"), "values")]
        interval = [_int(item, "interval[]") for item in _seq(witness.get("interval"), "interval")]
        require(len(interval) == 2, "invalid RMQ interval")
        expected = _leftmost_minimum(values, interval[0], interval[1])
        return expected, _rmq_counterfactual(
            witness, boundary=case_id == CASE_IDS[0],
            reverse_ties=case_id == CASE_IDS[1])
    if case_id in CASE_IDS[2:4]:
        values = [_int(item, "values[]") for item in _seq(witness.get("values"), "values")]
        weights = [_int(item, "weights[]") for item in _seq(witness.get("weights"), "weights")]
        require(values and len(values) == len(weights), "invalid reduction witness")
        exact_value = sum(value * weight for value, weight in zip(values, weights))
        if case_id == CASE_IDS[2]:
            return exact_value, exact_value & U64_MAX
        return exact_value, sum(values)
    if case_id == CASE_IDS[4]:
        return (_orientation_projection(witness, False),
                _orientation_projection(witness, True))
    if case_id == CASE_IDS[5]:
        source = [_int(item, "source[]") for item in _seq(witness.get("source"), "source")]
        indexed = [_int(item, "indexed[]") for item in _seq(witness.get("indexed"), "indexed")]
        require(len(source) == len(indexed) == 5, "invalid AABB witness")
        closed = (source[0] <= indexed[2] and source[2] >= indexed[0]
                  and source[1] <= indexed[3] and source[3] >= indexed[1])
        strict = (source[0] < indexed[2] and source[2] > indexed[0]
                  and source[1] < indexed[3] and source[3] > indexed[1])
        return ([[source[4], indexed[4]]] if closed else [],
                [[source[4], indexed[4]]] if strict else [])
    raise AssertionError(f"unknown case: {case_id}")


def _binary_column(kind: str, values: Sequence[object]) -> dict[str, object]:
    formats = {"f32": "f", "u32": "I", "u64": "Q"}
    require(kind in formats, "unknown binary-column scalar type")
    normalized = tuple(float(value) if kind == "f32" else _int(value, kind)
                       for value in values)
    raw = b"".join(struct.pack("<" + formats[kind], value)
                   for value in normalized)
    return {
        "scalar_type": kind,
        "endianness": "little",
        "count": len(normalized),
        "bytes_hex": raw.hex(),
        "bytes_sha256": hashlib.sha256(raw).hexdigest(),
    }


def _triangle_input(*, family: str, vertices: Sequence[Sequence[object]],
                    triangles: Sequence[Sequence[object]],
                    queries: Sequence[tuple[Sequence[object], Sequence[object], object]],
                    front_values: Sequence[object] = (),
                    back_values: Sequence[object] = (),
                    weights: Sequence[object] = (),
                    event_capacity: int | None = None) -> dict[str, object]:
    return {
        "schema": EXECUTED_INPUT_SCHEMA,
        "family": family,
        "columns": {
            "vertices_xyz": _binary_column(
                "f32", tuple(value for row in vertices for value in row)),
            "triangle_indices": _binary_column(
                "u32", tuple(value for row in triangles for value in row)),
            "query_origin_direction_tmax": _binary_column(
                "f32", tuple(value for origin, direction, maximum in queries
                             for value in (*origin, *direction, maximum))),
            "primitive_front_values": _binary_column("u32", front_values),
            "primitive_back_values": _binary_column("u32", back_values),
            "query_weights": _binary_column("u64", weights),
        },
        "event_capacity": event_capacity,
    }


def _relation_input(*, indexed: Sequence[Sequence[object]],
                    sources: Sequence[Sequence[object]], capacity: int) -> dict[str, object]:
    return {
        "schema": EXECUTED_INPUT_SCHEMA,
        "family": "custom_aabb.bounded_relation",
        "columns": {
            "indexed_bounds_xyxy": _binary_column(
                "f32", tuple(value for row in indexed for value in row[:4])),
            "indexed_ids": _binary_column("u32", tuple(row[4] for row in indexed)),
            "source_bounds_xyxy": _binary_column(
                "f32", tuple(value for row in sources for value in row[:4])),
            "source_ids": _binary_column("u32", tuple(row[4] for row in sources)),
        },
        "capacity": capacity,
        "minimum_overlap_f32": _binary_column("f32", (0.0,)),
    }


def expected_executed_input(case: Mapping[str, object], *, diagnostic: bool) -> dict[str, object]:
    """Reconstruct the exact numeric values passed to a Home execution arm.

    Floating-point values are represented by their little-endian IEEE-754
    binary32 bit patterns.  This avoids treating a pretty-printed decimal as
    the value consumed by the native boundary.
    """

    case_id = str(case["case_id"])
    witness = case["minimal_witness"]
    if case_id in CASE_IDS[:2]:
        values = [_int(item, "values[]") for item in _seq(witness.get("values"), "values")]
        interval = [_int(item, "interval[]") for item in _seq(witness.get("interval"), "interval")]
        require(len(interval) == 2, "invalid RMQ interval")
        count = len(values)
        reverse = diagnostic and case_id == CASE_IDS[1]
        order = sorted(range(count), key=lambda index: (values[index],
                                                        -index if reverse else index))
        ranks = [0] * count
        for rank, index in enumerate(order, 1):
            ranks[index] = rank
        vertices: list[list[float]] = []
        triangles: list[list[int]] = []
        for index, rank in enumerate(ranks):
            lower = (index - 1) / count
            upper = (index + 1) / count
            first = len(vertices)
            vertices.extend((
                [float(rank), upper, lower],
                [float(rank), upper, 2.0],
                [float(rank), -1.0, lower],
            ))
            triangles.append([first, first + 1, first + 2])
        left, right = interval
        boundary = diagnostic and case_id == CASE_IDS[0]
        y = left / count if boundary else (left + 0.5) / count
        z = right / count if boundary else (right - 0.5) / count
        return _triangle_input(
            family="builtin_triangle.rtxrmq", vertices=vertices,
            triangles=triangles,
            front_values=tuple(range(count)), back_values=tuple(range(count)),
            queries=(((0.0, y, z), (1.0, 0.0, 0.0), count + 1),))
    elif case_id in CASE_IDS[2:4]:
        weights = [_int(item, "weights[]") for item in _seq(witness.get("weights"), "weights")]
        values = [_int(item, "values[]") for item in _seq(witness.get("values"), "values")]
        require(len(weights) == len(values) == 2, "triangle witness size drift")
        runtime_weights = () if diagnostic and case_id == CASE_IDS[3] else weights
        return _triangle_input(
            family="builtin_triangle.triangle_reduction",
            vertices=((-0.75, -0.75, 1.0), (0.75, -0.75, 1.0),
                      (0.0, 0.75, 1.0)), triangles=((0, 1, 2),),
            queries=(((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 10.0),
                     ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 10.0)),
            weights=runtime_weights, event_capacity=4)
    elif case_id == CASE_IDS[4]:
        front = [_int(witness.get("front_value"), "front_value")]
        back = [_int(witness.get("back_value"), "back_value")]
        if diagnostic:
            front, back = back, front
        return _triangle_input(
            family="builtin_triangle.particle_orientation",
            vertices=_seq(witness.get("vertices"), "vertices"),
            triangles=(_seq(witness.get("triangle"), "triangle"),),
            front_values=front, back_values=back,
            queries=((_seq(witness.get("ray_origin"), "ray_origin"),
                      _seq(witness.get("ray_direction"), "ray_direction"), 10.0),))
    elif case_id == CASE_IDS[5]:
        def box_row(row_value: object) -> list[object]:
            row = _seq(row_value, "AABB row")
            require(len(row) == 5, "AABB row size drift")
            return [float(row[index]) for index in range(4)] \
                + [_int(row[4], "AABB ID")]
        return _relation_input(
            indexed=(box_row(witness.get("indexed")),),
            sources=(box_row(witness.get("source")),), capacity=4)
    else:  # pragma: no cover - fixed suite guard
        raise AssertionError(f"unknown executed-input case: {case_id}")
    raise AssertionError(f"unknown executed-input case: {case_id}")


def verify_executed_input(value: object, case: dict, *, diagnostic: bool,
                          label: str) -> dict:
    require(isinstance(value, dict), f"{label} is not an object")
    fields = (RELATION_EXECUTED_INPUT_FIELDS if case["geometry_family"] == "custom_aabb"
              else TRIANGLE_EXECUTED_INPUT_FIELDS)
    executed = exact(value, fields, label)
    require(executed.get("schema") == EXECUTED_INPUT_SCHEMA,
            f"{label} schema mismatch")
    expected_column_fields = (RELATION_COLUMN_FIELDS
                              if case["geometry_family"] == "custom_aabb"
                              else TRIANGLE_COLUMN_FIELDS)
    columns = exact(executed.get("columns"), expected_column_fields,
                    f"{label}.columns")
    for name, column_value in columns.items():
        column = exact(column_value, BINARY_COLUMN_FIELDS,
                       f"{label}.columns.{name}")
        kind = column.get("scalar_type")
        require(kind in {"f32", "u32", "u64"}
                and column.get("endianness") == "little",
                f"{label}.columns.{name} scalar contract mismatch")
        raw_hex = column.get("bytes_hex")
        require(isinstance(raw_hex, str) and len(raw_hex) % 2 == 0,
                f"{label}.columns.{name} bytes malformed")
        try:
            raw = bytes.fromhex(raw_hex)
        except ValueError as error:
            raise AssertionError(
                f"{label}.columns.{name} bytes malformed") from error
        width = {"f32": 4, "u32": 4, "u64": 8}[kind]
        require(len(raw) == _int(column.get("count"), "binary column count") * width
                and column.get("bytes_sha256") == hashlib.sha256(raw).hexdigest(),
                f"{label}.columns.{name} byte identity mismatch")
    expected = expected_executed_input(case, diagnostic=diagnostic)
    require(executed == expected, f"{label} independent numeric-input mismatch")
    return executed


def executed_input_differences(accepted: Mapping[str, object],
                               diagnostic: Mapping[str, object]) -> list[str]:
    differences: list[str] = []
    for field in sorted(set(accepted) | set(diagnostic) - {"columns"}):
        if field != "columns" and accepted.get(field) != diagnostic.get(field):
            differences.append(field)
    left_columns = accepted.get("columns")
    right_columns = diagnostic.get("columns")
    require(isinstance(left_columns, dict) and isinstance(right_columns, dict),
            "executed input columns missing")
    for field in sorted(set(left_columns) | set(right_columns)):
        if left_columns.get(field) != right_columns.get(field):
            differences.append(f"columns.{field}")
    return differences


def expected_u64_device_continuation(
        executed_input: Mapping[str, object],
        physical_identity: Mapping[str, object],
        toolchain_identity_sha256: str,
        case: Mapping[str, object]) -> dict[str, object]:
    """Reconstruct the isolated unchecked-U64 device-event receipt.

    This is trusted harness event evidence, not hardware attestation.  It is
    deliberately separate from the OptiX traversal receipt: traversal proves
    the hit producer ran; this receipt proves that the *device* unchecked
    continuation consumed the preserved per-ray values and weights.
    """

    witness = case.get("minimal_witness")
    require(isinstance(witness, dict), "U64 witness absent")
    per_ray = _seq(witness.get("values"), "U64 per_ray")
    weights = _seq(witness.get("weights"), "U64 weights")
    require(len(per_ray) == len(weights) == 2, "U64 device input size drift")
    for label, rows in (("per_ray", per_ray), ("weights", weights)):
        for index, item in enumerate(rows):
            value = _int(item, f"{label}[{index}]")
            require(0 <= value <= U64_MAX, f"{label}[{index}] outside U64")
    source_sha = hashlib.sha256(
        UNCHECKED_U64_CONTINUATION_SOURCE.encode("utf-8")).hexdigest()
    recipe = {
        "schema": DEVICE_RECIPE_SCHEMA,
        "kind": "test_only_unchecked_u64_rawkernel_recipe",
        "entry": "goal5790_a1_unchecked_weighted_sum",
        "kernel_source_sha256": source_sha,
        "grid": [1, 1, 1],
        "block": [1, 1, 1],
        "value_count": len(per_ray),
        "cupy_version": EXPECTED_CUPY_VERSION,
        "home_machine_authority_sha256": HOME_AUTHORITY_RECEIPT_SHA256,
        "home_toolchain_identity_sha256": toolchain_identity_sha256,
        "target_identity_sha256": physical_identity["target_sha256"],
    }
    device_input = {"per_ray_u64": per_ray, "weights_u64": weights}
    receipt: dict[str, object] = {
        "schema": DEVICE_CONTINUATION_SCHEMA,
        "kind": "test_only_unchecked_u64_device_continuation",
        "kernel_source": UNCHECKED_U64_CONTINUATION_SOURCE,
        "kernel_source_sha256": source_sha,
        "operation_recipe": recipe,
        "operation_recipe_sha256": digest(recipe),
        "cupy_version": EXPECTED_CUPY_VERSION,
        "home_machine_authority_sha256": HOME_AUTHORITY_RECEIPT_SHA256,
        "home_toolchain_identity_sha256": toolchain_identity_sha256,
        "target_identity_sha256": physical_identity["target_sha256"],
        "per_ray_u64": per_ray,
        "weights_u64": weights,
        "device_input_sha256": digest(device_input),
        "launch_count": 1,
        "synchronization_count": 1,
        "device_output_u64": 0,
        "device_output_sha256": digest(0),
        "host_fallback_used": False,
        "evidence_kind": (
            "trusted_test_harness_event__not_hardware_attestation"),
    }
    receipt["receipt_sha256"] = digest(receipt)
    return receipt


def verify_device_continuation(
        value: object, *, case: Mapping[str, object], diagnostic: bool,
        executed_input: Mapping[str, object],
        physical_identity: Mapping[str, object],
        toolchain_identity_sha256: str) -> str | None:
    required = diagnostic and case["case_id"] == CASE_IDS[2]
    if not required:
        require(value is None, "unexpected device continuation receipt")
        return None
    receipt = exact(value, DEVICE_CONTINUATION_FIELDS,
                    "diagnostic_counterfactual.device_continuation_receipt")
    require(receipt.get("schema") == DEVICE_CONTINUATION_SCHEMA,
            "device continuation receipt schema mismatch")
    verify_seal(receipt, "receipt_sha256", "device_continuation_receipt")
    recipe = exact(receipt.get("operation_recipe"), DEVICE_RECIPE_FIELDS,
                   "device_continuation_receipt.operation_recipe")
    require(receipt.get("operation_recipe_sha256") == digest(recipe),
            "device continuation recipe digest mismatch")
    expected = expected_u64_device_continuation(
        executed_input, physical_identity, toolchain_identity_sha256, case)
    require(receipt == expected,
            "unchecked-U64 device continuation evidence mismatch")
    return receipt["receipt_sha256"]


def verify_actual_device_continuation(
        value: object, *, case: Mapping[str, object], diagnostic: bool,
        physical_identity: Mapping[str, object],
        toolchain_identity_sha256: str) -> str | None:
    """Reconstruct the exact event schema emitted by the executed Home worker.

    Unlike the older synthetic-evidence schema above, the worker event is
    transitively sealed by its worker and controller results and intentionally
    has no self-digest field.  This verifier therefore checks every field and
    returns its independently computed canonical digest.
    """

    required = diagnostic and case["case_id"] == CASE_IDS[2]
    if not required:
        require(value is None, "unexpected actual device continuation event")
        return None
    event = exact(value, ACTUAL_DEVICE_CONTINUATION_FIELDS,
                  "worker.diagnostic_counterfactual.device_continuation")
    witness = case.get("minimal_witness")
    require(isinstance(witness, dict), "actual U64 witness absent")
    per_ray = _seq(witness.get("values"), "actual U64 per_ray")
    weights = _seq(witness.get("weights"), "actual U64 weights")
    require(len(per_ray) == len(weights) == 2,
            "actual U64 device input size drift")
    for field, rows in (("per_ray", per_ray), ("weights", weights)):
        for index, item in enumerate(rows):
            number = _int(item, f"actual {field}[{index}]")
            require(0 <= number <= U64_MAX,
                    f"actual {field}[{index}] outside U64")
    source_sha = hashlib.sha256(
        UNCHECKED_U64_CONTINUATION_SOURCE.encode("utf-8")).hexdigest()
    recipe = exact(event.get("operation_recipe"),
                   ACTUAL_DEVICE_RECIPE_FIELDS,
                   "actual_device_continuation.operation_recipe")
    expected_recipe = {
        "operation": "unchecked_weighted_u64_product_sum",
        "arithmetic": "cuda_unsigned_long_long_modulo_2_pow_64",
        "grid": [1],
        "block": [1],
        "compiler_options": ["-std=c++11"],
        "input_origin": "exact_optix_per_ray_plus_frozen_query_weights",
        "host_fallback": False,
    }
    require(recipe == expected_recipe
            and event.get("operation_recipe_sha256") == digest(recipe),
            "actual device continuation recipe mismatch")
    require(
        event.get("schema")
            == "rtdl.goal5790_a1.test_only_unchecked_u64_device_continuation.v1"
        and event.get("test_only_nonregistrable") is True
        and event.get("production_authority_minted") is False
        and event.get("kernel_source") == UNCHECKED_U64_CONTINUATION_SOURCE
        and event.get("kernel_source_sha256") == source_sha
        and event.get("kernel_entry") == "goal5790_a1_unchecked_weighted_sum"
        and event.get("compiler_options") == ["-std=c++11"]
        and event.get("cupy_version") == EXPECTED_CUPY_VERSION
        and type(event.get("cuda_runtime_version")) is int
        and event["cuda_runtime_version"] > 0
        and type(event.get("device_id")) is int and event["device_id"] == 0
        and event.get("target_sha256") == physical_identity["target_sha256"]
        and event.get("frozen_home_authority_file_sha256")
            == HOME_AUTHORITY_FILE_SHA256
        and event.get("frozen_home_authority_receipt_sha256")
            == HOME_AUTHORITY_RECEIPT_SHA256
        and event.get("home_toolchain_identity_sha256")
            == toolchain_identity_sha256
        and event.get("per_ray_u64") == per_ray
        and event.get("weights_u64") == weights
        and event.get("input_per_ray_sha256") == digest(per_ray)
        and event.get("input_weights_sha256") == digest(weights)
        and event.get("input_pair_sha256")
            == digest({"per_ray": per_ray, "weights": weights})
        and type(event.get("output_value")) is int
        and event["output_value"] == 0
        and event.get("output_sha256") == digest(0)
        and event.get("device_output_u64") == 0
        and all(type(event.get(field)) is int and event[field] == 1
                for field in (
                    "device_kernel_launch_count", "host_synchronization_count",
                    "launch_count", "synchronization_count"))
        and event.get("host_fallback_used") is False
        and event.get("evidence_kind")
            == "trusted_test_harness_not_hardware_capability_claim"
        and event.get("registered_performance_timing_created") is False,
        "actual unchecked-U64 device continuation evidence mismatch",
    )
    return digest(event)


def verify_cpu_suite(payload: object, expected_sha256: str) -> tuple[dict, dict[str, dict]]:
    suite = exact(payload, CPU_SUITE_FIELDS, "cpu_suite")
    require(suite.get("schema") == CPU_SUITE_SCHEMA, "CPU suite schema mismatch")
    require(verify_seal(suite, "suite_sha256", "cpu_suite") == expected_sha256,
            "CPU suite identity mismatch")
    cases = _seq(suite.get("cases"), "cpu_suite.cases")
    require(len(cases) == len(CASE_IDS), "CPU suite case count mismatch")
    by_id: dict[str, dict] = {}
    observed: list[str] = []
    for index, item in enumerate(cases):
        case = exact(item, CPU_CASE_FIELDS, f"cpu_suite.cases[{index}]")
        verify_seal(case, "case_sha256", f"cpu_suite.cases[{index}]")
        case_id = case.get("case_id")
        require(case_id in CASE_IDS and case_id not in by_id, "CPU case ID drift")
        observed.append(case_id)
        for name in ("source_authority", "semantic_authority", "physical_authority"):
            authority = case.get(name)
            require(isinstance(authority, dict), f"{case_id} {name} malformed")
            verify_seal(authority, "authority_sha256", f"{case_id}.{name}")
        require(case.get("expected_rule_id") == EXPECTED_RULES[case_id],
                f"{case_id} rejection rule drift")
        witness = case.get("minimal_witness")
        require(isinstance(witness, dict), f"{case_id} witness malformed")
        expected, counterfactual = evaluate_case(case_id, witness)
        oracle = case.get("independent_oracle")
        execution = case.get("counterfactual_execution")
        require(isinstance(oracle, dict) and oracle.get("expected_output") == expected,
                f"{case_id} independent oracle mismatch")
        require(isinstance(execution, dict)
                and execution.get("counterfactual_output") == counterfactual
                and execution.get("oracle_mismatch") is True
                and counterfactual != expected,
                f"{case_id} counterfactual mismatch")
        transform = case.get("unsafe_transform")
        require(isinstance(transform, dict)
                and transform.get("scope") == "test_only_nonregistrable_counterfactual"
                and transform.get("production_authority_minted") is False,
                f"{case_id} unsafe transform boundary drift")
        by_id[case_id] = case
    require(tuple(observed) == CASE_IDS, "CPU suite order/coverage mismatch")
    return suite, by_id


def _shared_case(case: dict) -> dict[str, str]:
    return {
        "semantic_request_sha256": digest(case["semantic_authority"]),
        "input_sha256": digest(case["minimal_witness"]),
        "oracle_authority_sha256": digest(case["independent_oracle"]),
        "source_authority_sha256": case["source_authority"]["authority_sha256"],
    }


def verify_physical_identity(value: object, label: str) -> dict:
    identity = exact(value, PHYSICAL_IDENTITY_FIELDS, label)
    require(identity.get("schema") == PHYSICAL_IDENTITY_SCHEMA,
            f"{label} schema mismatch")
    verify_seal(identity, "observation_sha256", label)
    require(isinstance(identity.get("family"), str) and identity["family"],
            f"{label}.family malformed")
    require_identifier(identity.get("program_bundle"), f"{label}.program_bundle")
    for field in (
        "callback_ir_sha256", "callback_effect_digest",
        "physical_or_family_schema_sha256", "target_sha256", "abi_sha256",
        "executable_sha256", "composed_program_sha256",
        "native_library_sha256",
    ):
        require_sha(identity.get(field), f"{label}.{field}")
    plan = identity.get("plan_sha256")
    contract = identity.get("contract_sha256")
    require((plan is None) != (contract is None),
            f"{label} must carry exactly one plan/contract SHA")
    require_sha(plan if plan is not None else contract,
                f"{label}.artifact_sha256")
    admission = identity.get("semantic_admission_sha256")
    if admission is not None:
        require_sha(admission, f"{label}.semantic_admission_sha256")
    return identity


def _verify_postrun_identity(value: object, *, case: dict, case_spec: dict,
                             scientific: dict, diagnostic: bool,
                             label: str) -> dict:
    identity = verify_physical_identity(value, label)
    snapshot = case_spec["pre_run_case_authorities"]
    live = snapshot[
        "diagnostic_live_family" if diagnostic else "canonical_live_family"]
    # Particle's invalid orientation is rejected before a diagnostic physical
    # authority can be minted.  The isolated counterfactual therefore runs the
    # exact canonical program with only the frozen front/back input columns
    # swapped; it is not a second registrable family.
    if live is None and diagnostic and case["case_id"] == CASE_IDS[4]:
        live = snapshot["canonical_live_family"]
    require(isinstance(live, dict), f"{label} lacks pre-run live family")
    artifact_field = (
        "plan_sha256" if live["artifact_kind"] == "plan"
        else "contract_sha256")
    other_artifact = (
        "contract_sha256" if artifact_field == "plan_sha256"
        else "plan_sha256")
    require(identity["callback_ir_sha256"] == live["callback_ir_sha256"]
            and identity["callback_effect_digest"] == live["effect_digest"]
            and identity["physical_or_family_schema_sha256"]
                == live["schema_sha256"]
            and identity["target_sha256"] == live["target_sha256"]
                == scientific["target_identity_sha256"]
            and identity["abi_sha256"] == live["abi_sha256"]
            and identity[artifact_field] == live["artifact_sha256"]
            and identity[other_artifact] is None
            and identity["native_library_sha256"]
                == scientific["native_library_sha256"],
            f"{label} differs from frozen pre-run family")
    expected_family = {
        CASE_IDS[0]: "builtin_triangle.rtxrmq",
        CASE_IDS[1]: "builtin_triangle.rtxrmq",
        CASE_IDS[2]: "builtin_triangle.triangle_reduction",
        CASE_IDS[3]: "builtin_triangle.triangle_reduction",
        CASE_IDS[4]: "builtin_triangle.particle_orientation",
        CASE_IDS[5]: "custom_aabb.bounded_relation",
    }[case["case_id"]]
    require(identity["family"] == expected_family,
            f"{label} family mismatch")
    require((identity["semantic_admission_sha256"] is None) is diagnostic,
            f"{label} semantic admission authority mismatch")
    return identity


def _verify_scientific_identity(value: object) -> dict:
    identity = exact(value, SCIENTIFIC_IDENTITY_FIELDS, "scientific_identity")
    for field in (
        "execution_source_archive_sha256", "execution_source_tree_sha256",
        "native_library_sha256", "target_identity_sha256",
    ):
        require_sha(identity.get(field), f"scientific_identity.{field}")
    require(identity.get("target_provider") == "optix",
            "scientific target provider mismatch")
    require(isinstance(identity.get("optix_sdk"), str)
            and identity["optix_sdk"], "scientific OptiX SDK missing")
    require(identity.get("compute_capability") == "6.1",
            "scientific target is not frozen Home CC6.1")
    return identity


def _verify_source_members(value: object, evidence_root: Path) -> dict[str, dict]:
    rows = _seq(value, "pre_run_source_members")
    require(rows, "pre-run source manifest is empty")
    result: dict[str, dict] = {}
    for index, raw in enumerate(rows):
        row = exact(raw, PRE_RUN_SOURCE_MEMBER_FIELDS,
                    f"pre_run_source_members[{index}]")
        logical = safe_relative(row.get("logical_path"), "pre-run logical path")
        evidence = safe_relative(row.get("evidence_path"), "pre-run evidence path")
        require(logical not in result, "duplicate pre-run logical source path")
        roles = _seq(row.get("roles"), f"pre_run_source_members[{index}].roles")
        require(roles == sorted(set(roles)) and all(
            isinstance(role, str) and role for role in roles),
            "pre-run source roles malformed")
        claimed = require_sha(row.get("sha256"), "pre-run source SHA")
        path = evidence_root / evidence
        require(path.is_file() and sha_file(path) == claimed,
                f"pre-run source bytes mismatch: {logical}")
        result[logical] = row
    return result


def _verify_governance_authorities(value: object,
                                   evidence_root: Path) -> dict[str, dict]:
    rows = _seq(value, "governance_authority_members")
    require(rows, "governance authority manifest is empty")
    result: dict[str, dict] = {}
    for index, raw in enumerate(rows):
        row = exact(raw, GOVERNANCE_AUTHORITY_MEMBER_FIELDS,
                    f"governance_authority_members[{index}]")
        logical = safe_relative(row.get("logical_path"),
                                "governance logical path")
        evidence = safe_relative(row.get("evidence_path"),
                                 "governance evidence path")
        require(logical not in result and isinstance(row.get("role"), str)
                and row["role"], "governance authority row malformed")
        claimed = require_sha(row.get("sha256"), "governance authority SHA")
        path = evidence_root / evidence
        require(path.is_file() and sha_file(path) == claimed,
                f"governance authority bytes mismatch: {logical}")
        result[logical] = row
    require(PARTICLE_GATE_AUTHORITY_PATH in result
            and result[PARTICLE_GATE_AUTHORITY_PATH]["role"]
                == "particle_earliest_product_gate_authority",
            "Particle earliest-gate amendment authority absent")
    require(result[PARTICLE_GATE_AUTHORITY_PATH]["sha256"]
            == PARTICLE_GATE_AUTHORITY_SHA256,
            "Particle earliest-gate amendment authority is not exact")
    require(GOAL5790_A1_PLAN_AUTHORITY_PATH in result
            and result[GOAL5790_A1_PLAN_AUTHORITY_PATH]["role"]
                == "goal5790_a1_controlling_plan_authority"
            and result[GOAL5790_A1_PLAN_AUTHORITY_PATH]["sha256"]
                == GOAL5790_A1_PLAN_AUTHORITY_SHA256,
            "Goal5790-A1 controlling plan authority is not exact")
    return result


def _verify_pre_run_capture_audit(value: object) -> dict:
    audit = exact(value, PRE_RUN_CAPTURE_AUDIT_FIELDS,
                  "pre_run_capture_audit")
    require(audit.get("schema")
            == "rtdl.goal5790_a1.pre_run_capture_audit.v1",
            "pre-run capture audit schema mismatch")
    verify_seal(audit, "audit_sha256", "pre_run_capture_audit")
    snapshots: list[dict] = []
    for key in ("process_audit_before", "process_audit_after"):
        snapshot = exact(audit.get(key), PROCESS_SNAPSHOT_FIELDS,
                         f"pre_run_capture_audit.{key}")
        modules = _seq(snapshot.get("modules"), f"{key}.modules")
        maps = _seq(snapshot.get("relevant_memory_maps"), f"{key}.maps")
        require(snapshot.get("modules_sha256") == digest(modules)
                and snapshot.get("relevant_memory_maps_sha256") == digest(maps),
                f"{key} process snapshot digest mismatch")
        snapshots.append(snapshot)
    new_names = _seq(audit.get("new_module_names"),
                     "pre_run_capture_audit.new_module_names")
    forbidden = _seq(audit.get("forbidden_low_level_imports"),
                     "pre_run_capture_audit.forbidden_low_level_imports")
    independently_forbidden = sorted(name for name in new_names
        if name == "cupy" or name.startswith("cupy.")
        or name == "numba" or name.startswith("numba.")
        or "optix_runtime" in name or "optix_compiler" in name)
    require(new_names == sorted(set(new_names))
            and "rtdsl" in new_names
            and forbidden == independently_forbidden == [],
            "pre-run capture imported forbidden/eager modules")
    require(audit.get("rtdsl_namespace_preseeded") is True
            and audit.get("broad_rtdsl_initializer_executed") is False
            and snapshots[0]["relevant_memory_maps"]
                == snapshots[1]["relevant_memory_maps"],
            "pre-run capture namespace/map isolation mismatch")
    for field in ("low_level_compiler_call_count", "native_prepare_call_count",
                  "native_execute_call_count", "traversal_launch_count"):
        require(audit.get(field) == 0,
                f"pre-run capture performed work: {field}")
    return audit


def _verify_semantic_authority(value: object, label: str) -> dict:
    authority = exact(value, SEMANTIC_AUTHORITY_FIELDS, label)
    require(authority.get("schema") == SEMANTIC_AUTHORITY_SCHEMA,
            f"{label} schema mismatch")
    requirement = exact(authority.get("requirement"),
                        SEMANTIC_REQUIREMENT_FIELDS,
                        f"{label}.requirement")
    require(requirement.get("schema") == "rtdl.v4.semantic_requirement.v1",
            f"{label}.requirement schema mismatch")
    require(isinstance(requirement.get("policy"), dict)
            and requirement["policy"], f"{label}.requirement policy malformed")
    require(requirement.get("required_hit_semantics") == ["bound_hit_stream"],
            f"{label}.requirement hit semantics mismatch")
    for field in ("declared_domain_sha256", "orientation_contract_sha256",
                  "specification_source_sha256"):
        require_sha(requirement.get(field), f"{label}.requirement.{field}")
    requirement_sha = digest(requirement)
    expected_authority = digest({
        "schema": SEMANTIC_AUTHORITY_SCHEMA,
        "requirement_sha256": requirement_sha,
        "specification_source_sha256": requirement[
            "specification_source_sha256"],
        "oracle_source_sha256": require_sha(
            authority.get("oracle_source_sha256"),
            f"{label}.oracle_source_sha256"),
        "issuer_domain": authority.get("issuer_domain"),
    })
    require(authority.get("authority_sha256") == expected_authority,
            f"{label} authority digest mismatch")
    require(authority.get("authority_nonce") == digest({
        "kind": SEMANTIC_AUTHORITY_SCHEMA,
        "authority_sha256": expected_authority,
    }), f"{label} authority nonce mismatch")
    return authority


def _verify_registry_entry(value: object, *, classifier_sha256: str,
                           source_members: Mapping[str, dict], label: str) -> dict:
    entry = exact(value, REGISTRY_ENTRY_FIELDS, label)
    guarantee = exact(entry.get("guarantee"), PHYSICAL_GUARANTEE_FIELDS,
                      f"{label}.guarantee")
    require(guarantee.get("schema") == "rtdl.v4.physical_guarantee.v1",
            f"{label}.guarantee schema mismatch")
    for field in ("supported_domain_sha256", "orientation_contract_sha256",
                  "schema_sha256", "callback_ir_sha256", "effect_digest",
                  "buffer_contract_sha256"):
        require_sha(guarantee.get(field), f"{label}.guarantee.{field}")
    require(isinstance(guarantee.get("guarantees"), dict)
            and guarantee["guarantees"],
            f"{label}.guarantee policy malformed")
    require(guarantee.get("hit_semantics") == ["bound_hit_stream"]
            and guarantee.get("gas_graph_depth") == 1
            and guarantee.get("gas_sbt_record_stride") == 1
            and guarantee.get("gas_update_policy") == "static",
            f"{label}.guarantee closed physical invariants mismatch")
    manifest = guarantee.get("source_manifest")
    require(isinstance(manifest, dict) and manifest,
            f"{label}.source_manifest malformed")
    normalized_manifest: dict[str, str] = {}
    for logical, claimed in manifest.items():
        logical_path = safe_relative(logical, f"{label}.source_manifest path")
        claimed_sha = require_sha(claimed, f"{label}.source_manifest SHA")
        require(logical_path in source_members
                and source_members[logical_path]["sha256"] == claimed_sha,
                f"{label} source bytes are not frozen in pre-run evidence")
        normalized_manifest[logical_path] = claimed_sha
    raw_maps = _seq(guarantee.get("maps"), f"{label}.guarantee.maps")
    require(len(raw_maps) == len(PHYSICAL_MAP_GRAPH),
            f"{label}.guarantee map stage count mismatch")
    observed_sources: set[str] = set()
    for index, (expected_kind, expected_graph) in enumerate(
            PHYSICAL_MAP_GRAPH.items()):
        edge = exact(raw_maps[index], PHYSICAL_MAP_FIELDS,
                     f"{label}.guarantee.maps[{index}]")
        source_id = safe_relative(
            edge.get("source_id"),
            f"{label}.guarantee.maps[{index}].source_id")
        source_sha = require_sha(
            edge.get("source_sha256"),
            f"{label}.guarantee.maps[{index}].source_sha256")
        require(edge.get("kind") == expected_kind
                and edge.get("consumes") == expected_graph[0]
                and edge.get("produces") == expected_graph[1],
                f"{label}.guarantee map graph mismatch")
        require(source_id in normalized_manifest
                and normalized_manifest[source_id] == source_sha,
                f"{label}.guarantee map source binding mismatch")
        observed_sources.add(source_id)
    require(observed_sources == set(normalized_manifest),
            f"{label}.guarantee source manifest is not exact map-source union")
    require(entry.get("source_bytes_manifest_sha256")
            == digest(normalized_manifest),
            f"{label} source-manifest digest mismatch")
    require(entry.get("classifier_source_sha256") == classifier_sha256,
            f"{label} classifier source mismatch")
    eligibility = entry.get("eligibility")
    require(eligibility in {
        "CANONICAL_PRODUCTION", "DIAGNOSTIC_NONREGISTRABLE"},
        f"{label} eligibility mismatch")
    if eligibility == "CANONICAL_PRODUCTION":
        require(isinstance(entry.get("canonical_template_id"), str)
                and entry["canonical_template_id"],
                f"{label} canonical template absent")
    else:
        require(entry.get("canonical_template_id") is None,
                f"{label} diagnostic entry is registrable")
    return entry


def _expected_bridge_policy(case: Mapping[str, object], *,
                            diagnostic: bool) -> dict[str, str]:
    base = dict(case[
        "physical_authority" if diagnostic else "semantic_authority"][
            "guarantees" if diagnostic else "policy"])
    contract_id = str(case["semantic_authority"]["contract_id"])
    base["input_type"] = "frozen_minimal_witness:" + contract_id
    base["output_type"] = "declared_semantic_output:" + contract_id
    return base


def _verify_guarantee_case_binding(
        authority: Mapping[str, object], *, semantic: Mapping[str, object],
        live_family: Mapping[str, object], case: Mapping[str, object],
        diagnostic: bool, label: str) -> None:
    guarantee = authority["entry"]["guarantee"]
    requirement = semantic["requirement"]
    expected_policy = _expected_bridge_policy(case, diagnostic=diagnostic)
    expected_capability = (
        "optix_builtin_triangle" if case["geometry_family"] == "builtin_triangle"
        else "optix_custom_aabb")
    require(guarantee.get("supported_algorithm_identity")
            == requirement["algorithm_identity"]
            and guarantee.get("supported_domain_sha256")
                == requirement["declared_domain_sha256"]
            and guarantee.get("orientation_contract_sha256")
                == requirement["orientation_contract_sha256"]
            and guarantee.get("geometry_family") == case["geometry_family"]
            and guarantee.get("guarantees") == expected_policy
            and guarantee.get("schema_sha256")
                == live_family["schema_sha256"]
            and guarantee.get("callback_ir_sha256")
                == live_family["callback_ir_sha256"]
            and guarantee.get("effect_digest") == live_family["effect_digest"]
            and guarantee.get("required_target_capabilities")
                == ["bound_program_bundle", "optix", expected_capability],
            f"{label} guarantee semantic/live binding mismatch")


def _verify_registry(value: object, *, classifier_sha256: str,
                     source_members: Mapping[str, dict], label: str) -> dict:
    registry = exact(value, REGISTRY_FIELDS, label)
    require(registry.get("schema") == PHYSICAL_REGISTRY_SCHEMA,
            f"{label} schema mismatch")
    require(registry.get("registry_source_sha256") == classifier_sha256,
            f"{label} registry source mismatch")
    require(registry.get("issuer_domain")
            == "rtdsl.compiler.physical_guarantee_registry.v1",
            f"{label} issuer mismatch")
    entries = [
        _verify_registry_entry(
            row, classifier_sha256=classifier_sha256,
            source_members=source_members, label=f"{label}.entries[{index}]")
        for index, row in enumerate(_seq(registry.get("entries"),
                                        f"{label}.entries"))
    ]
    require(entries and len({entry["entry_id"] for entry in entries})
            == len(entries), f"{label} duplicate/empty entries")
    expected_registry = digest({
        "schema": PHYSICAL_REGISTRY_SCHEMA,
        "issuer_domain": registry["issuer_domain"],
        "registry_source_sha256": classifier_sha256,
        "entries": entries,
    })
    require(registry.get("registry_sha256") == expected_registry,
            f"{label} registry digest mismatch")
    require(registry.get("authority_nonce") == digest({
        "kind": PHYSICAL_REGISTRY_SCHEMA,
        "registry_sha256": expected_registry,
    }), f"{label} registry nonce mismatch")
    return registry


def _verify_physical_authority(value: object, *, registry: dict,
                               expected_eligibility: str, label: str) -> dict:
    authority = exact(value, PHYSICAL_AUTHORITY_FIELDS, label)
    require(authority.get("schema") == PHYSICAL_AUTHORITY_SCHEMA,
            f"{label} schema mismatch")
    entry = exact(authority.get("entry"), REGISTRY_ENTRY_FIELDS,
                  f"{label}.entry")
    entries = registry["entries"]
    require(entry in entries and entry.get("eligibility") == expected_eligibility,
            f"{label} entry/eligibility mismatch")
    entry_sha = digest(entry)
    require(authority.get("registry_sha256") == registry["registry_sha256"]
            and authority.get("entry_sha256") == entry_sha,
            f"{label} registry/entry digest mismatch")
    expected_authority = digest({
        "schema": PHYSICAL_AUTHORITY_SCHEMA,
        "registry_sha256": registry["registry_sha256"],
        "entry_sha256": entry_sha,
        "entry_id": entry["entry_id"],
        "eligibility": entry["eligibility"],
    })
    require(authority.get("authority_sha256") == expected_authority,
            f"{label} authority digest mismatch")
    require(authority.get("authority_nonce") == digest({
        "kind": PHYSICAL_AUTHORITY_SCHEMA,
        "authority_sha256": expected_authority,
        "registry_nonce": registry["authority_nonce"],
    }), f"{label} authority nonce mismatch")
    return authority


def _verify_live_family(value: object, authority: dict, scientific: dict,
                        label: str) -> dict:
    family = exact(value, LIVE_FAMILY_FIELDS, label)
    guarantee = authority["entry"]["guarantee"]
    require(family.get("callback_ir_sha256") == guarantee.get("callback_ir_sha256")
            and family.get("effect_digest") == guarantee.get("effect_digest")
            and family.get("schema_sha256") == guarantee.get("schema_sha256")
            and family.get("target_sha256")
                == scientific["target_identity_sha256"]
            and family.get("orientation_contract_sha256")
                == guarantee.get("orientation_contract_sha256"),
            f"{label} live-family binding mismatch")
    for field in ("callback_ir_sha256", "effect_digest", "schema_sha256",
                  "target_sha256", "artifact_sha256", "abi_sha256",
                  "orientation_contract_sha256", "family_authority_sha256",
                  "family_authority_nonce"):
        require_sha(family.get(field), f"{label}.{field}")
    if family.get("proof_sha256") is not None:
        require_sha(family["proof_sha256"], f"{label}.proof_sha256")
    require(family.get("artifact_kind") in {"plan", "contract"},
            f"{label}.artifact_kind mismatch")
    return family


def _verify_pre_run_authorities(value: object, *, case: dict,
                                scientific: dict,
                                source_members: Mapping[str, dict]) -> dict:
    snapshot = exact(value, PRE_RUN_AUTHORITIES_FIELDS,
                     f"{case['case_id']}.pre_run_case_authorities")
    require(snapshot.get("schema") == PRE_RUN_AUTHORITIES_SCHEMA,
            "pre-run authority snapshot schema mismatch")
    verify_seal(snapshot, "snapshot_sha256", "pre-run authority snapshot")
    require(snapshot.get("case_id") == case["case_id"]
            and snapshot.get("case_sha256") == case["case_sha256"],
            "pre-run authority case mismatch")
    classifier_sha = require_sha(snapshot.get("classifier_source_sha256"),
                                 "classifier source SHA")
    classifier_rows = [row for row in source_members.values()
                       if "trusted_test_classifier" in row["roles"]]
    require(len(classifier_rows) == 1
            and classifier_rows[0]["sha256"] == classifier_sha,
            "trusted classifier bytes are not uniquely frozen")
    semantic = _verify_semantic_authority(
        snapshot.get("semantic_authority"), "semantic_authority")
    requirement = semantic["requirement"]
    case_semantic = case["semantic_authority"]
    require(requirement.get("contract_id") == case_semantic["contract_id"]
            and requirement.get("algorithm_identity")
                == "goal5790_a1." + case["case_id"]
            and requirement.get("declared_domain_sha256")
                == digest(case["minimal_witness"])
            and requirement.get("policy")
                == _expected_bridge_policy(case, diagnostic=False)
            and requirement.get("specification_source_sha256")
                == case_semantic["oracle_source_sha256"]
            and semantic.get("oracle_source_sha256")
                == case_semantic["oracle_source_sha256"]
            and semantic.get("issuer_domain") == "rtdl.app.goal5790_a1",
            "semantic authority is not the frozen case contract")
    registry = _verify_registry(
        snapshot.get("physical_registry"), classifier_sha256=classifier_sha,
        source_members=source_members, label="physical_registry")
    expected_entries = 1 if case["case_id"] == CASE_IDS[4] else 2
    require(len(registry["entries"]) == expected_entries
            and sum(entry["eligibility"] == "CANONICAL_PRODUCTION"
                    for entry in registry["entries"]) == 1
            and sum(entry["eligibility"] == "DIAGNOSTIC_NONREGISTRABLE"
                    for entry in registry["entries"])
                == expected_entries - 1,
            "physical registry case cardinality mismatch")
    canonical = _verify_physical_authority(
        snapshot.get("canonical_physical_authority"), registry=registry,
        expected_eligibility="CANONICAL_PRODUCTION",
        label="canonical_physical_authority")
    canonical_live = _verify_live_family(
        snapshot.get("canonical_live_family"), canonical, scientific,
        "canonical_live_family")
    require(canonical["entry"]["canonical_template_id"]
            == canonical_live["canonical_template_id"],
            "canonical registry/live template mismatch")
    _verify_guarantee_case_binding(
        canonical, semantic=semantic, live_family=canonical_live, case=case,
        diagnostic=False, label="canonical_physical_authority")
    diagnostic_raw = snapshot.get("diagnostic_physical_authority")
    diagnostic_live_raw = snapshot.get("diagnostic_live_family")
    early = snapshot.get("diagnostic_early_reject")
    attempt = snapshot.get("diagnostic_family_attempt")
    if case["case_id"] == CASE_IDS[4]:
        require(diagnostic_raw is None and diagnostic_live_raw is None
                and isinstance(early, dict)
                and early.get("code") == "triangle_orientation_mapping",
                "orientation diagnostic did not freeze earliest TPS reject")
        attempt = exact(attempt, DIAGNOSTIC_ATTEMPT_FIELDS,
                        "diagnostic_family_attempt")
        require(attempt.get("family") == "builtin_triangle"
                and attempt.get("target_sha256")
                    == scientific["target_identity_sha256"]
                and attempt.get("front_hit_selects") == "back"
                and attempt.get("back_hit_selects") == "front"
                and all(attempt.get(field) is False for field in (
                    "verified_family_authority_issued", "plan_issued",
                    "abi_issued")),
                "orientation diagnostic attempt is not exact/rejected")
        for field in ("callback_ir_sha256", "effect_digest", "schema_sha256",
                      "target_sha256", "orientation_authority_sha256",
                      "orientation_author_source_sha256",
                      "orientation_independent_oracle_sha256"):
            require_sha(attempt.get(field),
                        f"diagnostic_family_attempt.{field}")
    else:
        diagnostic = _verify_physical_authority(
            diagnostic_raw, registry=registry,
            expected_eligibility="DIAGNOSTIC_NONREGISTRABLE",
            label="diagnostic_physical_authority")
        diagnostic_live = _verify_live_family(
            diagnostic_live_raw, diagnostic, scientific,
            "diagnostic_live_family")
        _verify_guarantee_case_binding(
            diagnostic, semantic=semantic, live_family=diagnostic_live,
            case=case, diagnostic=True,
            label="diagnostic_physical_authority")
        require(early is None and attempt is None,
                "unexpected diagnostic early rejection/attempt")
    transform = snapshot.get("diagnostic_transform_authority")
    require(isinstance(transform, dict),
            "diagnostic transform authority absent")
    allowed_transform_fields = set(DIAGNOSTIC_TRANSFORM_REQUIRED_FIELDS)
    if case["case_id"] == CASE_IDS[2]:
        allowed_transform_fields.update({
            "unchecked_u64_kernel_source_sha256",
            "unchecked_u64_kernel_entry",
        })
    if case["case_id"] == CASE_IDS[5]:
        allowed_transform_fields.add("strict_callback_source_sha256")
    transform = exact(transform, allowed_transform_fields,
                      "diagnostic_transform_authority")
    transform_body = dict(transform)
    transform_claimed = transform_body.pop("transform_authority_sha256", None)
    require(transform_claimed == digest(transform_body)
            and transform.get("case_id") == case["case_id"]
            and transform.get("transform_id")
                == case["unsafe_transform"]["transform_id"]
            and transform.get("unsafe_transform_sha256")
                == digest(case["unsafe_transform"])
            and transform.get("test_only_nonregistrable") is True
            and transform.get("production_authority_minted") is False,
            "diagnostic transform authority mismatch")
    implementation = safe_relative(
        transform.get("implementation_path"),
        "diagnostic transform implementation")
    require(implementation in source_members
            and source_members[implementation]["sha256"]
                == transform.get("implementation_sha256") == classifier_sha,
            "diagnostic transform implementation bytes are not frozen")
    if case["case_id"] == CASE_IDS[2]:
        require(transform.get("unchecked_u64_kernel_source_sha256")
                == hashlib.sha256(UNCHECKED_U64_CONTINUATION_SOURCE.encode(
                    "utf-8")).hexdigest()
                and transform.get("unchecked_u64_kernel_entry")
                    == "goal5790_a1_unchecked_weighted_sum",
                "unchecked-U64 transform source identity mismatch")
    if case["case_id"] == CASE_IDS[5]:
        require_sha(transform.get("strict_callback_source_sha256"),
                    "strict callback source SHA")
    for field in ("low_level_compiler_call_count", "native_prepare_call_count",
                  "native_execute_call_count", "traversal_launch_count"):
        require(snapshot.get(field) == 0,
                f"pre-run authority capture performed work: {field}")
    del canonical_live
    return snapshot


def _verify_api_audit(value: object, evidence_root: Path) -> str:
    audit = exact(value, API_AUDIT_FIELDS, "diagnostic_api_audit")
    entrypoint = safe_relative(audit.get("diagnostic_entrypoint_path"),
                               "diagnostic entrypoint")
    require(entrypoint.startswith(("scripts/", "tests/")),
            "diagnostic entrypoint is outside scripts/tests")
    entrypoint_sha = require_sha(audit.get("diagnostic_entrypoint_sha256"),
                                 "diagnostic entrypoint SHA")
    symbol = require_identifier(audit.get("diagnostic_symbol"), "diagnostic symbol")
    require(audit.get("diagnostic_symbol_absent_from_product_api") is True
            and audit.get("test_only_entrypoint_not_imported_by_product") is True
            and audit.get("production_bypass_parameter_present") is False,
            "diagnostic API boundary claim mismatch")
    entrypoint_evidence = evidence_root / safe_relative(
        audit.get("diagnostic_entrypoint_evidence_path"),
        "diagnostic entrypoint evidence path")
    require(entrypoint_evidence.is_file()
            and sha_file(entrypoint_evidence) == entrypoint_sha,
            "diagnostic entrypoint bytes mismatch")
    require(symbol in entrypoint_evidence.read_text(encoding="utf-8"),
            "diagnostic symbol missing from test-only entrypoint")
    rows = _seq(audit.get("product_source_members"), "product_source_members")
    require(rows, "product API audit has no source members")
    seen: set[str] = set()
    admission_sha: str | None = None
    for index, row_value in enumerate(rows):
        row = exact(row_value, PRODUCT_SOURCE_MEMBER_FIELDS, f"product_source_members[{index}]")
        logical = safe_relative(row.get("logical_path"), "logical product path")
        require(logical.startswith("src/rtdsl/"), "non-product file in API audit")
        require(logical not in seen, "duplicate product source member")
        seen.add(logical)
        evidence_path = evidence_root / safe_relative(row.get("evidence_path"),
                                                      "product evidence path")
        require(evidence_path.is_file(), "missing product API audit file")
        require(sha_file(evidence_path) == require_sha(row.get("sha256"), "product source SHA"),
                "product source audit SHA mismatch")
        text = evidence_path.read_text(encoding="utf-8")
        require(symbol not in text, "diagnostic symbol leaked into product API")
        if logical == "src/rtdsl/v4_semantic_physical_admission.py":
            admission_sha = row["sha256"]
    require(admission_sha is not None,
            "product admission source absent from exact API audit")
    return admission_sha


def verify_execution_spec(payload: object, suite: dict, cases: dict[str, dict],
                          evidence_root: Path) -> tuple[dict, dict[str, dict]]:
    spec = exact(payload, EXECUTION_SPEC_FIELDS, "execution_spec")
    require(spec.get("schema") == EXECUTION_SPEC_SCHEMA, "execution spec schema mismatch")
    verify_seal(spec, "execution_spec_sha256", "execution_spec")
    require(spec.get("upstream_suite_sha256") == suite["suite_sha256"],
            "execution spec CPU suite mismatch")
    authority_relative = safe_relative(
        spec.get("home_machine_authority_evidence_path"),
        "Home-machine authority evidence path")
    authority = verify_home_machine_authority(evidence_root / authority_relative)
    require(spec.get("home_machine_authority_sha256")
            == authority["receipt_sha256"] == HOME_AUTHORITY_RECEIPT_SHA256
            and spec.get("home_machine_authority_file_sha256")
            == HOME_AUTHORITY_FILE_SHA256,
            "execution spec Home-machine authority binding mismatch")
    require(spec.get("home_toolchain_identity_sha256")
            == home_toolchain_identity(authority),
            "execution spec Home toolchain identity mismatch")
    require(spec.get("cupy_version") == EXPECTED_CUPY_VERSION,
            "execution spec CuPy identity mismatch")
    scientific = _verify_scientific_identity(spec.get("scientific_identity"))
    require(scientific["native_library_sha256"]
            == authority.get("native_library_sha256", scientific[
                "native_library_sha256"]),
            "scientific native identity conflicts with Home authority")
    _verify_pre_run_capture_audit(spec.get("pre_run_capture_audit"))
    source_members = _verify_source_members(
        spec.get("pre_run_source_members"), evidence_root)
    _verify_governance_authorities(
        spec.get("governance_authority_members"), evidence_root)
    require(spec.get("case_count") == len(CASE_IDS), "execution spec case count mismatch")
    boundary = exact(spec.get("claim_boundary"), CLAIM_BOUNDARY_FIELDS, "claim_boundary")
    require(boundary == {
        "home_only": True,
        "pod_authorized": False,
        "performance_timing_authorized": False,
        "performance_claimed": False,
        "formal_worker": False,
        "diagnostic_is_product_bypass": False,
    }, "execution spec claim boundary drift")
    _verify_api_audit(spec.get("diagnostic_api_audit"), evidence_root)
    rows = _seq(spec.get("cases"), "execution_spec.cases")
    require(len(rows) == len(CASE_IDS), "execution spec coverage mismatch")
    by_id: dict[str, dict] = {}
    for index, row_value in enumerate(rows):
        row = exact(row_value, EXECUTION_CASE_FIELDS, f"execution_spec.cases[{index}]")
        require(row.get("schema") == EXECUTION_CASE_SCHEMA, "execution case schema mismatch")
        verify_seal(row, "case_execution_spec_sha256", f"execution_spec.cases[{index}]")
        case_id = row.get("case_id")
        require(case_id in cases and case_id not in by_id, "execution case ID drift")
        case = cases[case_id]
        require(row.get("upstream_case_sha256") == case["case_sha256"],
                f"{case_id} upstream case mismatch")
        shared = exact(row.get("shared_case_identity"), SHARED_CASE_FIELDS,
                       f"{case_id}.shared_case_identity")
        require(shared == _shared_case(case), f"{case_id} shared identity mismatch")
        _verify_pre_run_authorities(
            row.get("pre_run_case_authorities"), case=case,
            scientific=scientific, source_members=source_members)
        rejection = exact(row.get("expected_product_rejection"),
                          EXPECTED_REJECTION_FIELDS, f"{case_id}.expected_rejection")
        require(rejection.get("verdict") == "INCOMPATIBLE"
                and rejection.get("expected_rule_id") == case["expected_rule_id"]
                and rejection.get("executable") is False
                and rejection.get("execution_authorized") is False,
                f"{case_id} expected rejection mismatch")
        rules = _seq(rejection.get("required_stable_product_rule_ids"), "stable rules")
        require(rules == [PRODUCT_RULE_BY_CASE_RULE[case["expected_rule_id"]]],
                f"{case_id} stable product rule mapping mismatch")
        expected_disposition = ("FAIL_CLOSED_OVERFLOW" if case_id == CASE_IDS[2]
                                else "VALUE")
        require(row.get("accepted_control_expected_disposition") == expected_disposition,
                f"{case_id} accepted-control disposition drift")
        accepted_input = expected_executed_input(case, diagnostic=False)
        diagnostic_input = expected_executed_input(case, diagnostic=True)
        require(row.get("accepted_executed_input_sha256")
                == digest(accepted_input)
                and row.get("diagnostic_executed_input_sha256")
                == digest(diagnostic_input),
                f"{case_id} executed-input identity mismatch")
        declared_input_delta = _seq(
            row.get("declared_executed_input_differences"),
            f"{case_id}.declared_executed_input_differences")
        actual_input_delta = executed_input_differences(
            accepted_input, diagnostic_input)
        require(declared_input_delta == EXECUTED_INPUT_DELTA_BY_CASE[case_id]
                == actual_input_delta,
                f"{case_id} executed-input delta allowlist mismatch")
        require(row.get("allowed_postrun_observation_fields")
                == list(POSTRUN_OBSERVATION_FIELDS),
                f"{case_id} postrun observation allowlist mismatch")
        by_id[case_id] = row
    require(tuple(by_id) == CASE_IDS, "execution spec case order mismatch")
    return spec, by_id


def _expected_home_machine(authority: Mapping[str, object]) -> dict[str, object]:
    value: dict[str, object] = {
        "hostname": "lx1",
        "gpu": authority["gpu_name"],
        "driver": authority["driver_version"],
        "uuid": authority["gpu_uuid"],
        "compute_capability": authority["compute_capability"],
        "classification": "exact_home_lx1__not_pod",
        "frozen_home_authority_file_sha256": HOME_AUTHORITY_FILE_SHA256,
        "frozen_home_authority_receipt_sha256": HOME_AUTHORITY_RECEIPT_SHA256,
        "home_toolchain_identity_sha256": home_toolchain_identity(authority),
    }
    value["home_machine_authority_sha256"] = digest(value)
    return value


def _verify_actual_process_snapshot(value: object, label: str) -> dict:
    snapshot = exact(value, PROCESS_SNAPSHOT_FIELDS, label)
    modules = _seq(snapshot.get("modules"), f"{label}.modules")
    maps = _seq(snapshot.get("relevant_memory_maps"), f"{label}.maps")
    require(snapshot.get("modules_sha256") == digest(modules)
            and snapshot.get("relevant_memory_maps_sha256") == digest(maps),
            f"{label} process snapshot digest mismatch")
    require(all(isinstance(row, dict)
                and isinstance(row.get("module"), str)
                and isinstance(row.get("source_path"), str)
                for row in modules), f"{label} module rows malformed")
    require(all(isinstance(row, str) for row in maps),
            f"{label} memory-map rows malformed")
    return snapshot


def _verify_actual_identity(value: object, *, case: dict, case_spec: dict,
                            scientific: dict, diagnostic: bool,
                            label: str) -> dict:
    identity = exact(value, ACTUAL_EXECUTION_IDENTITY_FIELDS, label)
    snapshot = case_spec["pre_run_case_authorities"]
    live = snapshot[
        "diagnostic_live_family" if diagnostic else "canonical_live_family"]
    if live is None and diagnostic and case["case_id"] == CASE_IDS[4]:
        live = snapshot["canonical_live_family"]
    require(isinstance(live, dict), f"{label} has no frozen live family")
    artifact_field = (
        "plan_sha256" if live["artifact_kind"] == "plan" else "contract_sha256")
    other_field = (
        "contract_sha256" if artifact_field == "plan_sha256" else "plan_sha256")
    for field in (
            "callback_ir_sha256", "callback_effect_digest",
            "physical_or_family_schema_sha256", "target_sha256", "abi_sha256",
            "executable_sha256", "composed_program_sha256",
            "family_authority_nonce", "family_authority_sha256",
            "native_library_sha256"):
        require_sha(identity.get(field), f"{label}.{field}")
    require(identity["callback_ir_sha256"] == live["callback_ir_sha256"]
            and identity["callback_effect_digest"] == live["effect_digest"]
            and identity["physical_or_family_schema_sha256"]
                == live["schema_sha256"]
            and identity["target_sha256"] == live["target_sha256"]
                == scientific["target_identity_sha256"]
            and identity["abi_sha256"] == live["abi_sha256"]
            and identity[artifact_field] == live["artifact_sha256"]
            and identity[other_field] is None
            and identity["family_authority_nonce"]
                == live["family_authority_nonce"]
            and identity["family_authority_sha256"]
                == live["family_authority_sha256"]
            and identity["native_library_sha256"]
                == scientific["native_library_sha256"],
            f"{label} differs from frozen pre-run identity")
    expected_family = {
        CASE_IDS[0]: "builtin_triangle.rtxrmq",
        CASE_IDS[1]: "builtin_triangle.rtxrmq",
        CASE_IDS[2]: "builtin_triangle.triangle_reduction",
        CASE_IDS[3]: "builtin_triangle.triangle_reduction",
        CASE_IDS[4]: "builtin_triangle.particle_orientation",
        CASE_IDS[5]: "custom_aabb.bounded_relation",
    }[case["case_id"]]
    expected_bundle = {
        "builtin_triangle.rtxrmq":
            "v4_builtin_triangle_callback_ir_four_role_composed",
        "builtin_triangle.particle_orientation":
            "v4_builtin_triangle_callback_ir_four_role_composed",
        "builtin_triangle.triangle_reduction":
            "v4_builtin_triangle_checked_reduction_composed",
        "custom_aabb.bounded_relation":
            "v4_custom_aabb_bounded_relation_composed",
    }[expected_family]
    require(identity.get("family") == expected_family
            and identity.get("expected_program_bundle") == expected_bundle,
            f"{label} family/program-bundle mismatch")
    admission = identity.get("semantic_admission_sha256")
    if diagnostic:
        require(admission is None, f"{label} diagnostic minted admission")
    else:
        require_sha(admission, f"{label}.semantic_admission_sha256")
    return identity


def _verify_actual_traversal(
        receipt_value: object, binding_value: object, output_value: object,
        expected_bundle: str, identity: Mapping[str, object], *, label: str) -> None:
    receipt = exact(receipt_value, TRAVERSAL_FIELDS, label)
    require(receipt.get("schema") == TRAVERSAL_SCHEMA,
            f"{label} traversal schema mismatch")
    verify_seal(receipt, "receipt_sha256", label)
    binding = binding_value
    require(isinstance(binding, dict), f"{label} semantic binding malformed")
    if identity["family"] in {
            "builtin_triangle.rtxrmq", "builtin_triangle.particle_orientation"}:
        exact(binding, {
            "authority_nonce", "schema_sha256", "plan_sha256", "abi_sha256",
            "composed_ptx_sha256", "native_library_sha256",
            "buffer_binding_sha256",
        }, f"{label}.binding")
        require(binding["authority_nonce"] == identity["family_authority_nonce"]
                and binding["schema_sha256"]
                    == identity["physical_or_family_schema_sha256"]
                and binding["plan_sha256"] == identity["plan_sha256"]
                and binding["abi_sha256"] == identity["abi_sha256"]
                and binding["composed_ptx_sha256"]
                    == identity["composed_program_sha256"]
                and binding["native_library_sha256"]
                    == identity["native_library_sha256"],
                f"{label} built-in semantic binding mismatch")
        require_sha(binding.get("buffer_binding_sha256"),
                    f"{label}.binding.buffer_binding_sha256")
    else:
        allowed = {"authority", "contract", "abi", "composed_ptx", "native"}
        producer_scope = binding.get("diagnostic_scope")
        if producer_scope is not None:
            allowed.add("diagnostic_scope")
        exact(binding, allowed, f"{label}.binding")
        require(binding["authority"] == identity["family_authority_nonce"]
                and binding["contract"] == identity["contract_sha256"]
                and binding["abi"] == identity["abi_sha256"]
                and binding["composed_ptx"]
                    == identity["composed_program_sha256"]
                and binding["native"] == identity["native_library_sha256"],
                f"{label} contract semantic binding mismatch")
        if producer_scope is not None:
            require(producer_scope == "weighted_per_ray_producer_only",
                    f"{label} diagnostic producer scope mismatch")
    require(receipt.get("provider_library_sha256")
                == identity["native_library_sha256"]
            and receipt.get("output_digest") == digest(output_value)
            and receipt.get("semantic_digest") == digest(binding)
            and receipt.get("physical_executor_classification")
                == "optix_traversal_observed"
            and receipt.get("expected_program_bundles") == [expected_bundle]
            and receipt.get("expected_program_observed_at_receipt_edge") is True
            and receipt.get("claim_rules") == CLAIM_RULES,
            f"{label} behavioral receipt mismatch")
    require(receipt.get("expected_program_bundle_ids")
            == [receipt["native_snapshot"]["first_program_bundle_id"]],
            f"{label} program-bundle ID mismatch")
    _verify_snapshot(receipt.get("native_snapshot"), expected_bundle,
                     f"{label}.native_snapshot")


def _actual_diagnostic_input_delta(case: Mapping[str, object]) -> str:
    case_id = case["case_id"]
    if case_id == CASE_IDS[4]:
        return "swap_front_values_with_back_values"
    if case_id in {CASE_IDS[2], CASE_IDS[5]}:
        return "none"
    return str(case["unsafe_transform"]["transform_id"])


def _verify_actual_execution_result(
        value: object, *, arm_name: str, case: dict, case_spec: dict,
        spec: dict) -> None:
    diagnostic = arm_name == "diagnostic_counterfactual"
    overflow_accepted = arm_name == "accepted_control" \
        and case["case_id"] == CASE_IDS[2]
    expected_fields = (
        ACTUAL_OVERFLOW_ACCEPTED_FIELDS if overflow_accepted else
        ACTUAL_TRIANGLE_FIELDS if case["case_id"] in CASE_IDS[2:4] else
        ACTUAL_EXECUTION_COMMON_FIELDS)
    arm = exact(value, expected_fields, f"worker.{arm_name}.arm_result")
    identity = _verify_actual_identity(
        arm.get("execution_identity"), case=case, case_spec=case_spec,
        scientific=spec["scientific_identity"], diagnostic=diagnostic,
        label=f"worker.{arm_name}.execution_identity")
    executed_input = verify_executed_input(
        arm.get("executed_input"), case, diagnostic=diagnostic,
        label=f"worker.{arm_name}.executed_input")
    expected_input_field = (
        "diagnostic_executed_input_sha256" if diagnostic
        else "accepted_executed_input_sha256")
    require(arm.get("executed_input_sha256") == digest(executed_input)
            == case_spec[expected_input_field],
            f"worker.{arm_name} executed input mismatch")
    expected, counterfactual = evaluate_case(
        case["case_id"], case["minimal_witness"])
    if overflow_accepted:
        disposition = exact(
            arm.get("accepted_disposition"), ACTUAL_OVERFLOW_DISPOSITION_FIELDS,
            "worker.accepted_control.accepted_disposition")
        require(arm.get("output") is None
                and disposition == {
                    "status": "FAIL_CLOSED_OVERFLOW",
                    "error_type": "TriangleReductionError",
                    "error_code": "unsigned_overflow",
                    "error_path": "rows[1].sum",
                    "output_produced": False,
                }
                and arm.get("own_oracle") == {
                    "required_mathematical_value": expected,
                    "required_disposition": "FAIL_CLOSED_OVERFLOW",
                }
                and arm.get("requested_semantic_oracle") == expected
                and arm.get("correct_fail_closed") is True
                and arm.get("zero_receipt_reason")
                    == "checked reducer rejected overflow before audit receipt capture",
                "checked-U64 accepted control did not fail closed exactly")
    else:
        own = counterfactual if diagnostic else expected
        require(arm.get("output") == own and arm.get("own_oracle") == own
                and arm.get("requested_semantic_oracle") == expected,
                f"worker.{arm_name} output/oracle mismatch")
    require(arm.get("matches_own_oracle") is True
            and arm.get("matches_requested_semantics") is (not diagnostic)
            and arm.get("counterexample_observed") is diagnostic
            and arm.get("admitted_run_gate") is (not diagnostic)
            and arm.get("compile_admission_certifies_concrete_runtime_arrays")
                is False,
            f"worker.{arm_name} semantic boundary mismatch")
    require(arm.get("declared_input_delta")
            == ("none" if not diagnostic else _actual_diagnostic_input_delta(case)),
            f"worker.{arm_name} declared input delta mismatch")
    receipts = _seq(arm.get("traversal_receipts"), f"worker.{arm_name}.receipts")
    bindings = _seq(
        arm.get("traversal_semantic_bindings"), f"worker.{arm_name}.bindings")
    outputs = _seq(
        arm.get("traversal_output_digest_inputs"), f"worker.{arm_name}.outputs")
    bundles = _seq(
        arm.get("expected_program_bundles"), f"worker.{arm_name}.bundles")
    own_value = counterfactual if diagnostic else expected
    expected_output_inputs: list[object]
    if case["case_id"] in CASE_IDS[:2]:
        expected_output_inputs = [[[own_value, own_value, own_value]]]
    elif case["case_id"] == CASE_IDS[4]:
        expected_output_inputs = [[own_value]]
    elif case["case_id"] == CASE_IDS[5]:
        expected_output_inputs = [own_value]
    elif case["case_id"] == CASE_IDS[2] and diagnostic:
        expected_output_inputs = [list(case["minimal_witness"]["values"])]
    else:
        expected_output_inputs = [own_value]
    if overflow_accepted:
        require(receipts == bindings == outputs == bundles == []
                and arm.get("behaviorally_true_optix") is False,
                "overflow accepted control invented traversal evidence")
    else:
        require(len(receipts) == len(bindings) == len(outputs) == len(bundles)
                and len(receipts) > 0
                and outputs == expected_output_inputs
                and arm.get("behaviorally_true_optix") is True,
                f"worker.{arm_name} traversal coverage mismatch")
        for index, items in enumerate(zip(receipts, bindings, outputs, bundles)):
            receipt, binding, output_value, bundle = items
            require(bundle == identity["expected_program_bundle"],
                    f"worker.{arm_name} program bundle drift")
            _verify_actual_traversal(
                receipt, binding, output_value, bundle, identity,
                label=f"worker.{arm_name}.receipts[{index}]")
    continuation = (
        arm.get("test_only_device_continuation")
        if "test_only_device_continuation" in arm else None)
    verify_actual_device_continuation(
        continuation, case=case, diagnostic=diagnostic,
        physical_identity=identity,
        toolchain_identity_sha256=spec["home_toolchain_identity_sha256"])
    if case["case_id"] in CASE_IDS[2:4] and not overflow_accepted:
        expected_physical_delta = (
            str(case["unsafe_transform"]["transform_id"])
            if diagnostic else "none")
        require(arm.get("declared_physical_delta") == expected_physical_delta,
                f"worker.{arm_name} physical delta mismatch")
        producer = arm.get("test_only_optix_producer_diagnostic")
        if case["case_id"] == CASE_IDS[2] and diagnostic:
            producer = exact(producer, ACTUAL_U64_PRODUCER_FIELDS,
                             "worker.diagnostic_counterfactual.u64_producer")
            require(producer.get("per_ray_u64")
                        == list(case["minimal_witness"]["values"])
                    and producer.get("traversal_receipt") == receipts[0]
                    and producer.get("traversal_semantic_binding") == bindings[0]
                    and producer.get("expected_program_bundle") == bundles[0]
                    and producer.get("native_library_sha256")
                        == identity["native_library_sha256"]
                    and producer.get("composed_program_sha256")
                        == identity["composed_program_sha256"]
                    and producer.get("test_only_nonregistrable") is True
                    and producer.get("standard_product_reduction_receipt_minted")
                        is False,
                    "unchecked-U64 OptiX producer binding mismatch")
            counters = _seq(producer.get("role_counters"),
                            "worker.diagnostic_counterfactual.role_counters")
            require(counters and all(isinstance(item, int)
                                     and not isinstance(item, bool)
                                     and item >= 0 for item in counters),
                    "unchecked-U64 producer counters malformed")
        else:
            require(producer is None,
                    f"worker.{arm_name} unexpected diagnostic producer")


def _verify_actual_reject_result(
        value: object, *, case: dict, case_spec: dict, spec: dict,
        source_members: Mapping[str, dict]) -> None:
    arm = exact(value, ACTUAL_REJECT_FIELDS, "worker.product_reject.arm_result")
    snapshot = case_spec["pre_run_case_authorities"]
    require(arm.get("engine")
                == "production_semantically_admitted_compiler_facade_v1"
            and arm.get("verdict") == "INCOMPATIBLE"
            and arm.get("named_case_rule_id") == case["expected_rule_id"]
            and arm.get("product_rule_ids")
                == [PRODUCT_RULE_BY_CASE_RULE[case["expected_rule_id"]]]
            and arm.get("target_sha256")
                == spec["scientific_identity"]["target_identity_sha256"]
            and arm.get("native_library_sha256")
                == spec["scientific_identity"]["native_library_sha256"],
            "actual product reject identity mismatch")
    particle = case["case_id"] == CASE_IDS[4]
    require(arm.get("product_rejection_gate") == (
                "verify_typed_physical_schema" if particle
                else "v4_semantically_admitted_compiler.admit_*")
            and arm.get("production_facade_called") is (not particle),
            "actual product reject gate partition mismatch")
    for path_field, sha_field, logical in (
        ("product_facade_path", "product_facade_sha256",
         "src/rtdsl/v4_semantically_admitted_compiler.py"),
        ("semantic_physical_calculus_path", "semantic_physical_calculus_sha256",
         "src/rtdsl/v4_semantic_physical_admission.py"),
        ("trusted_test_classifier_path", "trusted_test_classifier_sha256",
         "scripts/goal5790_a1_home_worker.py"),
    ):
        require(arm.get(path_field) == logical
                and arm.get(sha_field) == source_members[logical]["sha256"],
                f"actual product reject source pin mismatch: {logical}")
    for field in (
            "semantic_authority", "physical_registry",
            "canonical_physical_authority", "diagnostic_physical_authority",
            "canonical_live_family", "diagnostic_live_family",
            "diagnostic_family_attempt"):
        require(arm.get(field) == snapshot[field],
                f"actual product reject {field} differs from pre-run authority")
    decision = exact(
        arm.get("decision"), ACTUAL_REJECT_DECISION_FIELDS,
        "worker.product_reject.decision")
    finding = exact(
        decision.get("finding"), ACTUAL_REJECT_FINDING_FIELDS,
        "worker.product_reject.finding")
    require(arm.get("decision_sha256") == digest(decision)
            and decision.get("verdict") == "INCOMPATIBLE"
            and decision.get("semantic_authority_sha256")
                == snapshot["semantic_authority"]["authority_sha256"]
            and decision.get("physical_authority_sha256") == (
                None if snapshot["diagnostic_physical_authority"] is None
                else snapshot["diagnostic_physical_authority"]["authority_sha256"])
            and decision.get("canonical_live_family")
                == snapshot["canonical_live_family"]
            and decision.get("diagnostic_live_family")
                == snapshot["diagnostic_live_family"]
            and decision.get("diagnostic_family_attempt")
                == snapshot["diagnostic_family_attempt"]
            and finding.get("rule_id")
                == PRODUCT_RULE_BY_CASE_RULE[case["expected_rule_id"]]
            and finding.get("gate") == arm["product_rejection_gate"],
            "actual product reject decision mismatch")
    before = _verify_actual_process_snapshot(
        arm.get("process_audit_before"), "worker.reject.process_before")
    after = _verify_actual_process_snapshot(
        arm.get("process_audit_after"), "worker.reject.process_after")
    imported = _seq(arm.get("new_module_names"), "worker.reject.new_modules")
    require(imported == sorted(set(imported)),
            "actual product reject module delta is nondeterministic")
    independently_forbidden = sorted(name for name in imported
        if name == "cupy" or name.startswith("cupy.")
        or name == "numba" or name.startswith("numba.")
        or "optix_runtime" in name or "optix_compiler" in name)
    require(arm.get("forbidden_gpu_or_compiler_imports")
                == independently_forbidden == []
            and before["relevant_memory_maps"] == after["relevant_memory_maps"]
                == []
            and arm.get("cuda_or_gpu_library_map_observed") is False
            and arm.get("cuda_driver_initialization_observed") is False
            and arm.get("cuda_driver_initialization_proven_absent") is False
            and arm.get("cuda_initialization_evidence_kind")
                == "negative_module_and_proc_maps_observation__not_a_formal_absence_proof",
            "actual product reject import/map audit mismatch")
    for field in (
            "compiler_call_count", "low_level_compiler_call_count",
            "native_prepare_call_count", "native_execute_call_count",
            "traversal_launch_count"):
        require(arm.get(field) == 0, f"actual product reject {field} is nonzero")
    boundary = exact(
        arm.get("claim_boundary"), ACTUAL_REJECT_BOUNDARY_FIELDS,
        "worker.product_reject.claim_boundary")
    require(boundary == {
        "public_facade_rejects_raw_caller_self_proof": True,
        "compiler_internal_classifier_is_trusted_tcb": True,
        "malicious_same_process_reflection_resisted": False,
        "python_semantics_automatically_inferred": False,
        "concrete_runtime_input_certified_by_compile_admission": False,
    } and arm.get("execution_authorized") is False
      and arm.get("executable_issued") is False,
      "actual product reject claim boundary mismatch")


def _verify_actual_worker(
        value: object, *, arm_name: str, case: dict, case_spec: dict, suite: dict,
        spec: dict, spec_file_sha256: str, expected_home_machine: dict,
        source_members: Mapping[str, dict]) -> int:
    worker = exact(value, WORKER_FIELDS, f"worker.{arm_name}")
    require(worker.get("schema") == WORKER_SCHEMA
            and worker.get("status") == "PASS"
            and worker.get("case_id") == case["case_id"]
            and worker.get("case_sha256") == case["case_sha256"]
            and worker.get("upstream_suite_sha256") == suite["suite_sha256"]
            and worker.get("execution_spec_sha256")
                == spec["execution_spec_sha256"]
            and worker.get("execution_spec_file_sha256") == spec_file_sha256
            and worker.get("case_execution_spec_sha256")
                == case_spec["case_execution_spec_sha256"]
            and worker.get("input_sha256") == digest(case["minimal_witness"])
            and worker.get("arm") == arm_name
            and worker.get("home_machine") == expected_home_machine
            and worker.get("home_machine_authority_sha256")
                == expected_home_machine["home_machine_authority_sha256"],
            f"worker.{arm_name} top-level binding mismatch")
    verify_seal(worker, "worker_result_sha256", f"worker.{arm_name}")
    pid = worker.get("parent_pid")
    require(isinstance(pid, int) and not isinstance(pid, bool) and pid > 0,
            f"worker.{arm_name} PID malformed")
    cache = exact(worker.get("cache_policy"), WORKER_CACHE_FIELDS,
                  f"worker.{arm_name}.cache_policy")
    require(cache.get("formal_leaf_cache_environment_cleared") is True
            and isinstance(cache.get("cupy_cache_dir"), str)
            and isinstance(cache.get("numba_cache_dir"), str)
            and cache["cupy_cache_dir"] != cache["numba_cache_dir"]
            and cache.get("initially_empty") is True
            and cache.get("per_arm_isolated") is True
            and cache.get("cache_is_execution_authority") is False
            and cache.get("cache_contents_used_as_evidence") is False,
            f"worker.{arm_name} cache boundary mismatch")
    for field in (
            "elapsed_values_recorded", "registered_performance_timing_created",
            "performance_claimed", "pod_used", "formal_worker"):
        require(worker.get(field) is False,
                f"worker.{arm_name} escaped functional-only scope: {field}")
    if arm_name == "product_admission_reject":
        _verify_actual_reject_result(
            worker.get("arm_result"), case=case, case_spec=case_spec,
            spec=spec, source_members=source_members)
    else:
        _verify_actual_execution_result(
            worker.get("arm_result"), arm_name=arm_name, case=case,
            case_spec=case_spec, spec=spec)
    return pid


def _verify_controller_result(
        value: object, *, suite: dict, spec: dict, suite_file_sha256: str,
        spec_file_sha256: str, expected_home_machine: dict) -> tuple[dict, dict[str, dict]]:
    controller = exact(value, CONTROLLER_FIELDS, "controller_result")
    require(controller.get("schema") == CONTROLLER_SCHEMA
            and controller.get("status") == "PASS"
            and controller.get("scope")
                == "home_functional_only__zero_registered_timing",
            "controller status/scope mismatch")
    verify_seal(controller, "result_sha256", "controller_result")
    require(controller.get("suite_sha256") == suite["suite_sha256"]
            and controller.get("suite_file_sha256") == suite_file_sha256
            and controller.get("execution_spec_file_sha256") == spec_file_sha256
            and controller.get("execution_spec_sha256")
                == spec["execution_spec_sha256"]
            and controller.get("native_library_sha256")
                == spec["scientific_identity"]["native_library_sha256"]
            and controller.get("home_machine") == expected_home_machine
            and controller.get("frozen_home_authority_file_sha256")
                == HOME_AUTHORITY_FILE_SHA256
            and controller.get("frozen_home_authority_receipt_sha256")
                == HOME_AUTHORITY_RECEIPT_SHA256
            and controller.get("compute_capability") == "61"
            and controller.get("optix_sdk")
                == spec["scientific_identity"]["optix_sdk"],
            "controller scientific identity mismatch")
    require(controller.get("case_count") == len(CASE_IDS)
            and controller.get("arm_count") == len(CASE_IDS) * len(ACTUAL_ARMS)
            and controller.get("fresh_parent_pid_count")
                == len(CASE_IDS) * len(ACTUAL_ARMS)
            and controller.get("product_admission_reject_count") == len(CASE_IDS)
            and controller.get("production_facade_reject_count") == 5
            and controller.get("typed_physical_schema_reject_count") == 1
            and controller.get("product_admission_launch_count") == 0
            and controller.get("accepted_control_count") == len(CASE_IDS)
            and controller.get("diagnostic_counterexample_count") == len(CASE_IDS)
            and controller.get("registered_performance_timing_count") == 0
            and controller.get("performance_claimed") is False
            and controller.get("pod_used") is False
            and controller.get("formal_worker_count") == 0,
            "controller coverage/scope accounting mismatch")
    cache = exact(controller.get("cache_policy"), CONTROLLER_CACHE_FIELDS,
                  "controller.cache_policy")
    require(cache == {
        "formal_leaf_cache_environment_cleared": True,
        "per_arm_cupy_cache": "create_only_isolated_non_authority",
        "per_arm_numba_cache": "create_only_isolated_non_authority",
        "cache_contents_used_as_evidence": False,
    }, "controller cache policy mismatch")
    rows = _seq(controller.get("cases"), "controller.cases")
    require(len(rows) == len(CASE_IDS), "controller case coverage mismatch")
    by_id: dict[str, dict] = {}
    all_pids: set[int] = set()
    for index, raw in enumerate(rows):
        row = exact(raw, CONTROLLER_CASE_FIELDS, f"controller.cases[{index}]")
        case_id = row.get("case_id")
        require(case_id == CASE_IDS[index] and case_id not in by_id,
                "controller case order/identity mismatch")
        case = next(item for item in suite["cases"] if item["case_id"] == case_id)
        require(row.get("case_sha256") == case["case_sha256"]
                and row.get("expected_rule_id") == case["expected_rule_id"],
                f"controller {case_id} CPU authority mismatch")
        arms = row.get("arms")
        require(isinstance(arms, dict) and set(arms) == set(ACTUAL_ARMS),
                f"controller {case_id} arm coverage mismatch")
        for arm_name in ACTUAL_ARMS:
            worker = arms[arm_name]
            require(isinstance(worker, dict),
                    f"controller {case_id}/{arm_name} worker malformed")
            pid = worker.get("parent_pid")
            require(isinstance(pid, int) and not isinstance(pid, bool)
                    and pid > 0 and pid not in all_pids,
                    "controller reused/malformed worker PID")
            all_pids.add(pid)
        by_id[case_id] = row
    require(len(all_pids) == len(CASE_IDS) * len(ACTUAL_ARMS),
            "controller fresh PID accounting mismatch")
    return controller, by_id


def verify_adapted_raw_case(
        payload: object, *, suite: dict, case: dict, spec: dict,
        case_spec: dict, evidence_root: Path, suite_file_sha256: str,
        spec_file_sha256: str, source_members: Mapping[str, dict],
        expected_home_machine: dict) -> dict[str, int]:
    manifest = exact(payload, ADAPTED_RAW_FIELDS, "adapted_raw")
    require(manifest.get("schema") == ADAPTED_RAW_SCHEMA
            and manifest.get("status") == "PASS",
            "adapted raw status/schema mismatch")
    verify_seal(manifest, "raw_result_sha256", "adapted_raw")
    require(manifest.get("upstream_suite_sha256") == suite["suite_sha256"]
            and manifest.get("execution_spec_sha256")
                == spec["execution_spec_sha256"]
            and manifest.get("case_id") == case["case_id"]
            and manifest.get("case_sha256") == case["case_sha256"]
            and manifest.get("case_execution_spec_sha256")
                == case_spec["case_execution_spec_sha256"],
            "adapted raw pre-run cross-binding mismatch")
    controller_path = evidence_root / safe_relative(
        manifest.get("controller_result_path"), "controller result path")
    require(controller_path.is_file()
            and sha_file(controller_path)
                == manifest.get("controller_result_file_sha256"),
            "adapted raw controller bytes mismatch")
    controller, controller_cases = _verify_controller_result(
        strict_load(controller_path), suite=suite, spec=spec,
        suite_file_sha256=suite_file_sha256,
        spec_file_sha256=spec_file_sha256,
        expected_home_machine=expected_home_machine)
    require(manifest.get("controller_result_sha256")
                == controller["result_sha256"],
            "adapted raw controller semantic digest mismatch")
    controller_case = controller_cases[case["case_id"]]
    require(manifest.get("controller_case_sha256") == digest(controller_case),
            "adapted raw controller-case digest mismatch")
    refs = manifest.get("source_workers")
    require(isinstance(refs, dict) and set(refs) == set(ACTUAL_ARMS),
            "adapted raw source-worker coverage mismatch")
    normalized_refs: dict[str, dict] = {}
    pids: dict[str, int] = {}
    for arm_name in ACTUAL_ARMS:
        ref = exact(refs[arm_name], SOURCE_WORKER_REFERENCE_FIELDS,
                    f"adapted_raw.source_workers.{arm_name}")
        path = evidence_root / safe_relative(
            ref.get("path"), f"adapted worker path {arm_name}")
        require(path.is_file() and sha_file(path) == ref.get("file_sha256"),
                f"adapted worker bytes mismatch: {arm_name}")
        worker = strict_load(path)
        require(worker == controller_case["arms"][arm_name],
                f"adapted worker differs from controller nested bytes: {arm_name}")
        require(ref.get("worker_result_sha256")
                    == worker.get("worker_result_sha256")
                and ref.get("parent_pid") == worker.get("parent_pid"),
                f"adapted worker reference drift: {arm_name}")
        pid = _verify_actual_worker(
            worker, arm_name=arm_name, case=case, case_spec=case_spec,
            suite=suite, spec=spec, spec_file_sha256=spec_file_sha256,
            expected_home_machine=expected_home_machine,
            source_members=source_members)
        pids[arm_name] = pid
        normalized_refs[arm_name] = ref
    require(manifest.get("source_worker_set_sha256") == digest(normalized_refs),
            "adapted raw worker-set digest mismatch")
    require(len(set(pids.values())) == len(ACTUAL_ARMS),
            "adapted raw reused a worker PID")
    return {
        "reject": pids["product_admission_reject"],
        "diagnostic": pids["diagnostic_counterfactual"],
        "accepted": pids["accepted_control"],
    }


def _verify_process_audit(value: object, artifacts: object, evidence_root: Path,
                          admission_source_sha256: str) -> None:
    audit = exact(value, PROCESS_AUDIT_FIELDS, "process_audit")
    for field in ("compiler_call_count", "native_prepare_call_count",
                  "native_execute_call_count", "traversal_launch_count"):
        require(audit.get(field) == 0, f"reject process {field} is nonzero")
    require(audit.get("admission_module_imported") is True
            and audit.get("admission_module_name") == ISOLATED_ADMISSION_MODULE
            and audit.get("admission_module_source_sha256")
            == admission_source_sha256
            and audit.get("admission_module_loaded_from_exact_source") is True,
            "exact isolated product-admission import not evidenced")
    for field in ("rtdsl_package_imported", "compiler_or_runtime_module_imported",
                  "cupy_imported", "numba_imported", "ctypes_imported"):
        require(audit.get(field) is False, f"reject process {field}")
    rows = _seq(artifacts, "raw_audit_artifacts")
    require({row.get("kind") for row in rows if isinstance(row, dict)} == AUDIT_KINDS,
            "reject audit artifact coverage mismatch")
    for index, row_value in enumerate(rows):
        row = exact(row_value, AUDIT_ARTIFACT_FIELDS, f"audit_artifacts[{index}]")
        require(row.get("kind") in AUDIT_KINDS, "unknown audit artifact kind")
        path = evidence_root / safe_relative(row.get("path"), "audit artifact path")
        require(path.is_file(), "missing audit artifact")
        data = path.read_bytes()
        require(len(data) == row.get("size_bytes")
                and hashlib.sha256(data).hexdigest() == row.get("sha256"),
                "audit artifact byte mismatch")
        text = data.decode("utf-8")
        if row.get("kind") == "modules":
            modules = json.loads(text)
            require(isinstance(modules, list)
                    and all(isinstance(name, str) for name in modules),
                    "modules audit malformed")
            require(ISOLATED_ADMISSION_MODULE in modules,
                    "isolated product-admission module absent from modules audit")
            require(not {name.partition(".")[0] for name in modules}
                    & FORBIDDEN_MODULE_ROOTS, "GPU/product module imported before reject")
        else:
            require(FORBIDDEN_GPU_TEXT.search(text) is None,
                    "GPU/native mapping or open occurred before reject")


def _verify_reject(value: object, case: dict, case_spec: dict, suite_sha: str,
                   spec_sha: str, evidence_root: Path,
                   admission_source_sha256: str) -> int:
    arm = exact(value, REJECT_FIELDS, "product_admission_reject")
    require(arm.get("schema") == REJECT_SCHEMA
            and arm.get("arm") == "product_admission_reject"
            and arm.get("status") == "PASS", "product reject status mismatch")
    require(arm.get("upstream_suite_sha256") == suite_sha
            and arm.get("case_sha256") == case["case_sha256"]
            and arm.get("case_execution_spec_sha256")
            == case_spec["case_execution_spec_sha256"]
            and arm.get("shared_case_identity") == case_spec["shared_case_identity"]
            and arm.get("rejected_physical_identity_sha256")
            == (case_spec["pre_run_case_authorities"]
                ["diagnostic_physical_authority"]["authority_sha256"]
                if case_spec["pre_run_case_authorities"]
                    ["diagnostic_physical_authority"] is not None
                else digest(case_spec["pre_run_case_authorities"]
                            ["diagnostic_early_reject"]))
            and arm.get("home_machine_authority_sha256")
            == HOME_AUTHORITY_RECEIPT_SHA256
            and arm.get("home_machine_authority_file_sha256")
            == HOME_AUTHORITY_FILE_SHA256,
            "product reject cross-binding mismatch")
    decision = exact(arm.get("admission_decision"), DECISION_FIELDS,
                     "admission_decision")
    require(decision.get("schema") == DECISION_SCHEMA, "decision schema mismatch")
    verify_seal(decision, "decision_sha256", "admission_decision")
    expected = case_spec["expected_product_rejection"]
    require(decision.get("verdict") == expected["verdict"]
            and decision.get("expected_rule_id") == expected["expected_rule_id"]
            and decision.get("stable_product_rule_ids")
            == expected["required_stable_product_rule_ids"]
            and decision.get("executable") is False
            and decision.get("execution_authorized") is False,
            "product admission verdict mismatch")
    for field in ("compile_count", "native_prepare_count", "native_execute_count",
                  "traversal_launch_count"):
        require(arm.get(field) == 0, f"reject arm {field} is nonzero")
    require(arm.get("elapsed_values_recorded") is False
            and arm.get("registered_performance_timing_created") is False
            and arm.get("performance_claimed") is False
            and arm.get("pod_used") is False and arm.get("formal_worker") is False,
            "reject arm boundary drift")
    _verify_process_audit(arm.get("process_audit"), arm.get("raw_audit_artifacts"),
                          evidence_root, admission_source_sha256)
    verify_seal(arm, "receipt_sha256", "product_admission_reject")
    pid = arm.get("parent_pid")
    require(isinstance(pid, int) and not isinstance(pid, bool) and pid > 0,
            "invalid reject PID")
    del spec_sha  # bound at raw top; retained in signature to make intent explicit.
    return pid


def _verify_snapshot(value: object, program_bundle: str, label: str) -> None:
    snapshot = exact(value, SNAPSHOT_FIELDS, label)
    positive_fields = (
        "attempted_launch_count", "successful_launch_count",
        "complete_context_launch_count", "context_bind_count",
        "raygen_invocation_count", "first_program_bundle_id",
        "last_program_bundle_id", "first_traversable", "last_traversable",
    )
    for field in positive_fields:
        require(type(snapshot.get(field)) is int and snapshot[field] > 0,
                f"{label}.{field} is not an exact positive integer")
    for field in (
            "nonce_hi", "nonce_lo", "program_bundle_mix", "traversable_mix",
            "pipeline_mix", "sbt_mix", "stream_mix", "params_mix",
            "callsite_mix"):
        require(type(snapshot.get(field)) is int and snapshot[field] >= 0,
                f"{label}.{field} is not an exact nonnegative integer")
    for field in ("failed_launch_count", "incomplete_context_launch_count",
                  "incomplete_callsite_record_count",
                  "pending_context_at_finish", "session_error"):
        require(type(snapshot.get(field)) is int and snapshot[field] == 0,
                f"{label}.{field} is not exact integer zero")
    require(snapshot.get("successful_launch_count") == snapshot.get("attempted_launch_count")
            == snapshot.get("complete_context_launch_count"),
            f"{label} launch accounting mismatch")
    expected_bundle_id = _physical_program_bundle_id(program_bundle)
    require(snapshot.get("first_program_bundle_id")
            == snapshot.get("last_program_bundle_id")
            == expected_bundle_id,
            f"{label} program bundle ID drift")
    if snapshot["attempted_launch_count"] == 1:
        require(snapshot.get("first_traversable")
                == snapshot.get("last_traversable"),
                f"{label} single-launch traversable drift")
    lines = snapshot.get("incomplete_callsite_lines")
    require(type(lines) is list and len(lines) == 32
            and all(type(item) is int and item == 0 for item in lines),
            f"{label}.incomplete_callsite_lines is not exact 32x integer zero")


def _verify_traversal(value: object, binding_value: object, identity: dict,
                      live_family: dict, output_sha: str, label: str) -> None:
    receipt = exact(value, TRAVERSAL_FIELDS, label)
    require(receipt.get("schema") == TRAVERSAL_SCHEMA, f"{label} schema mismatch")
    verify_seal(receipt, "receipt_sha256", label)
    binding = exact(binding_value, SEMANTIC_BINDING_FIELDS, f"{label}.binding")
    expected_binding = {
        "authority": live_family["family_authority_nonce"],
        "contract": (identity["plan_sha256"]
                     if identity["plan_sha256"] is not None
                     else identity["contract_sha256"]),
        "abi": identity["abi_sha256"],
        "composed_ptx": identity["composed_program_sha256"],
        "native": identity["native_library_sha256"],
        "device_column_count": 1,
    }
    require(binding == expected_binding, f"{label} semantic binding mismatch")
    require(receipt.get("provider_library_sha256") == identity["native_library_sha256"]
            and receipt.get("output_digest") == output_sha
            and receipt.get("physical_executor_classification")
            == "optix_traversal_observed"
            and receipt.get("expected_program_bundles") == [identity["program_bundle"]]
            and receipt.get("expected_program_observed_at_receipt_edge") is True
            and receipt.get("claim_rules") == CLAIM_RULES,
            f"{label} behavioral identity mismatch")
    require(receipt.get("semantic_digest") == digest(binding),
            f"{label} semantic digest mismatch")
    require(receipt.get("expected_program_bundle_ids")
            == [receipt["native_snapshot"]["first_program_bundle_id"]],
            f"{label} program ID mismatch")
    _verify_snapshot(receipt.get("native_snapshot"), identity["program_bundle"],
                     f"{label}.native_snapshot")


def _expected_outcome(case_id: str, value: object, accepted: bool) -> dict:
    if accepted and case_id == CASE_IDS[2]:
        return {"kind": "expected_fail_closed", "value": None,
                "error_code": "checked_u64_overflow",
                "exception_type": "OverflowError",
                "status_evidence": {
                    "output_emitted": False,
                    "overflow_detected": True,
                    "fail_closed": True,
                }}
    return {"kind": "value", "value": value, "error_code": None,
            "exception_type": None,
            "status_evidence": {
                "output_emitted": True,
                "overflow_detected": False,
                "fail_closed": False,
            }}


def _verify_execution(value: object, case: dict, case_spec: dict, *, arm_name: str,
                      suite_sha: str, toolchain_identity_sha256: str,
                      scientific_identity: dict) -> int:
    arm = exact(value, EXECUTION_ARM_FIELDS, arm_name)
    require(arm.get("schema") == EXECUTION_ARM_SCHEMA
            and arm.get("arm") == arm_name and arm.get("status") == "PASS",
            f"{arm_name} status mismatch")
    require(arm.get("upstream_suite_sha256") == suite_sha
            and arm.get("case_sha256") == case["case_sha256"]
            and arm.get("case_execution_spec_sha256")
            == case_spec["case_execution_spec_sha256"]
            and arm.get("shared_case_identity") == case_spec["shared_case_identity"]
            and arm.get("home_machine_authority_sha256")
            == HOME_AUTHORITY_RECEIPT_SHA256
            and arm.get("home_machine_authority_file_sha256")
            == HOME_AUTHORITY_FILE_SHA256,
            f"{arm_name} case binding mismatch")
    diagnostic = arm_name == "diagnostic_counterfactual"
    identity = _verify_postrun_identity(
        arm.get("physical_identity"), case=case, case_spec=case_spec,
        scientific=scientific_identity, diagnostic=diagnostic,
        label=f"{arm_name}.physical_identity")
    executed_input = verify_executed_input(
        arm.get("executed_input"), case, diagnostic=diagnostic,
        label=f"{arm_name}.executed_input")
    expected_input_key = ("diagnostic_executed_input_sha256" if diagnostic
                          else "accepted_executed_input_sha256")
    require(arm.get("executed_input_sha256")
            == digest(executed_input)
            == case_spec[expected_input_key],
            f"{arm_name} executed-input SHA mismatch")
    witness = case["minimal_witness"]
    expected, counterfactual = evaluate_case(case["case_id"], witness)
    oracle_value = counterfactual if arm_name == "diagnostic_counterfactual" else expected
    require(arm.get("oracle_value") == oracle_value
            and arm.get("oracle_value_sha256") == digest(oracle_value),
            f"{arm_name} oracle mismatch")
    outcome = exact(arm.get("outcome"), OUTCOME_FIELDS, f"{arm_name}.outcome")
    exact(outcome.get("status_evidence"), STATUS_EVIDENCE_FIELDS,
          f"{arm_name}.outcome.status_evidence")
    require(outcome == _expected_outcome(case["case_id"], oracle_value,
                                         arm_name == "accepted_control"),
            f"{arm_name} outcome mismatch")
    output_sha = digest(outcome)
    require(arm.get("outcome_sha256") == output_sha
            and arm.get("matches_own_oracle") is True,
            f"{arm_name} outcome digest/match mismatch")
    if arm_name == "diagnostic_counterfactual":
        require(arm.get("matches_requested_semantics") is False
                and arm.get("counterexample_observed") is True
                and arm.get("isolated_test_only_diagnostic") is True
                and arm.get("production_authority_minted") is False
                and arm.get("product_api_bypass_parameter_present") is False,
                "diagnostic isolation/counterexample mismatch")
    else:
        require(arm.get("matches_requested_semantics") is True
                and arm.get("counterexample_observed") is False
                and arm.get("isolated_test_only_diagnostic") is False
                and arm.get("production_authority_minted") is True
                and arm.get("product_api_bypass_parameter_present") is False,
                "accepted control authority mismatch")
    require(arm.get("product_source_modified") is False
            and arm.get("elapsed_values_recorded") is False
            and arm.get("registered_performance_timing_created") is False
            and arm.get("performance_claimed") is False
            and arm.get("pod_used") is False and arm.get("formal_worker") is False,
            f"{arm_name} claim boundary drift")
    receipts = _seq(arm.get("traversal_receipts"), f"{arm_name}.receipts")
    bindings = _seq(arm.get("traversal_semantic_bindings"), f"{arm_name}.bindings")
    overflow_reject = arm_name == "accepted_control" and case["case_id"] == CASE_IDS[2]
    if overflow_reject:
        require(receipts == [] and bindings == []
                and arm.get("traversal_receipt_count") == 0,
                "overflow accepted-control must not invent traversal evidence")
    else:
        require(receipts and len(receipts) == len(bindings)
                == arm.get("traversal_receipt_count"),
                f"{arm_name} receipt coverage mismatch")
    snapshot = case_spec["pre_run_case_authorities"]
    live_family = snapshot[
        "diagnostic_live_family" if diagnostic else "canonical_live_family"]
    if live_family is None:
        live_family = snapshot["canonical_live_family"]
    for index, (receipt, binding) in enumerate(zip(receipts, bindings)):
        _verify_traversal(receipt, binding, identity, live_family, output_sha,
                          f"{arm_name}.receipts[{index}]")
    device_continuation_sha256 = verify_device_continuation(
        arm.get("device_continuation_receipt"), case=case,
        diagnostic=diagnostic, executed_input=executed_input,
        physical_identity=identity,
        toolchain_identity_sha256=toolchain_identity_sha256)
    execution_binding = {
        "case_sha256": case["case_sha256"],
        "physical_identity_sha256": identity["observation_sha256"],
        "executed_input_sha256": digest(executed_input),
        "outcome_sha256": output_sha,
        "traversal_receipt_sha256s": [receipt["receipt_sha256"]
                                      for receipt in receipts],
        "device_continuation_receipt_sha256": device_continuation_sha256,
    }
    require(arm.get("execution_binding_sha256") == digest(execution_binding),
            f"{arm_name} host execution binding mismatch")
    verify_seal(arm, "receipt_sha256", arm_name)
    pid = arm.get("parent_pid")
    require(isinstance(pid, int) and not isinstance(pid, bool) and pid > 0,
            f"{arm_name} invalid PID")
    return pid


def verify_raw_case(payload: object, suite: dict, case: dict, spec: dict,
                    case_spec: dict, evidence_root: Path) -> dict[str, int]:
    raw = exact(payload, RAW_FIELDS, "raw")
    require(raw.get("schema") == RAW_SCHEMA and raw.get("status") == "PASS",
            "raw status/schema mismatch")
    verify_seal(raw, "raw_result_sha256", "raw")
    require(raw.get("upstream_suite_sha256") == suite["suite_sha256"]
            and raw.get("execution_spec_sha256") == spec["execution_spec_sha256"]
            and raw.get("case_id") == case["case_id"]
            and raw.get("case_sha256") == case["case_sha256"]
            and raw.get("case_execution_spec_sha256")
            == case_spec["case_execution_spec_sha256"]
            and raw.get("shared_case_identity") == case_spec["shared_case_identity"]
            and raw.get("home_machine_authority_sha256")
            == spec["home_machine_authority_sha256"]
            == HOME_AUTHORITY_RECEIPT_SHA256
            and raw.get("home_machine_authority_file_sha256")
            == spec["home_machine_authority_file_sha256"]
            == HOME_AUTHORITY_FILE_SHA256,
            "raw cross-binding mismatch")
    boundary = exact(raw.get("claim_boundary"), CLAIM_BOUNDARY_FIELDS,
                     "raw.claim_boundary")
    require(boundary == spec["claim_boundary"], "raw claim boundary mismatch")
    reject_pid = _verify_reject(raw.get("product_admission_reject"), case, case_spec,
                                suite["suite_sha256"], spec["execution_spec_sha256"],
                                evidence_root, _verify_api_audit(
                                    spec["diagnostic_api_audit"], evidence_root))
    diagnostic_pid = _verify_execution(raw.get("diagnostic_counterfactual"), case,
                                       case_spec, arm_name="diagnostic_counterfactual",
                                       suite_sha=suite["suite_sha256"],
                                       toolchain_identity_sha256=
                                       spec["home_toolchain_identity_sha256"],
                                       scientific_identity=
                                       spec["scientific_identity"])
    accepted_pid = _verify_execution(raw.get("accepted_control"), case, case_spec,
                                     arm_name="accepted_control",
                                     suite_sha=suite["suite_sha256"],
                                     toolchain_identity_sha256=
                                     spec["home_toolchain_identity_sha256"],
                                     scientific_identity=
                                     spec["scientific_identity"])
    require(len({reject_pid, diagnostic_pid, accepted_pid}) == 3,
            "three arms did not use fresh distinct PIDs")
    return {"reject": reject_pid, "diagnostic": diagnostic_pid,
            "accepted": accepted_pid}


def recount(cpu_suite_path: Path, execution_spec_path: Path,
            raw_root: Path, expected_suite_sha256: str) -> dict[str, object]:
    cpu_payload = strict_load(cpu_suite_path)
    expected_suite_sha256 = require_sha(expected_suite_sha256,
                                        "externally pinned CPU suite SHA")
    suite, cases = verify_cpu_suite(cpu_payload, expected_suite_sha256)
    spec, spec_cases = verify_execution_spec(
        strict_load(execution_spec_path), suite, cases, raw_root)
    suite_file_sha256 = sha_file(cpu_suite_path)
    spec_file_sha256 = sha_file(execution_spec_path)
    source_members = _verify_source_members(
        spec["pre_run_source_members"], raw_root)
    authority_path = raw_root / safe_relative(
        spec["home_machine_authority_evidence_path"],
        "Home-machine authority evidence path")
    expected_home_machine = _expected_home_machine(
        verify_home_machine_authority(authority_path))
    all_pids: set[int] = set()
    case_rows: list[dict[str, object]] = []
    for case_id in CASE_IDS:
        raw_path = raw_root / "raw" / f"{case_id}.json"
        require(raw_path.is_file(), f"missing raw case: {case_id}")
        payload = strict_load(raw_path)
        if isinstance(payload, dict) \
                and payload.get("schema") == ADAPTED_RAW_SCHEMA:
            pids = verify_adapted_raw_case(
                payload, suite=suite, case=cases[case_id], spec=spec,
                case_spec=spec_cases[case_id], evidence_root=raw_root,
                suite_file_sha256=suite_file_sha256,
                spec_file_sha256=spec_file_sha256,
                source_members=source_members,
                expected_home_machine=expected_home_machine)
        else:
            pids = verify_raw_case(payload, suite, cases[case_id], spec,
                                   spec_cases[case_id], raw_root)
        require(not (set(pids.values()) & all_pids), "PID reused across cases")
        all_pids.update(pids.values())
        case_rows.append({
            "case_id": case_id,
            "case_sha256": cases[case_id]["case_sha256"],
            "raw_sha256": sha_file(raw_path),
            "product_reject_pid": pids["reject"],
            "diagnostic_pid": pids["diagnostic"],
            "accepted_pid": pids["accepted"],
            "status": "PASS",
        })
    result: dict[str, object] = {
        "schema": RECOUNT_SCHEMA,
        "status": "PASS",
        "upstream_suite_sha256": suite["suite_sha256"],
        "execution_spec_sha256": spec["execution_spec_sha256"],
        "case_count": len(case_rows),
        "arm_count": len(case_rows) * 3,
        "unique_parent_pid_count": len(all_pids),
        "product_reject_count": len(case_rows),
        "diagnostic_wrong_answer_count": len(case_rows),
        "accepted_control_count": len(case_rows),
        # All six diagnostic encodings and five value-producing accepted
        # controls execute.  The checked-U64 accepted control fails closed
        # before audit.capture(), so claiming a twelfth receipt would be fake.
        "behavioral_true_optix_execution_count": len(case_rows) * 2 - 1,
        "registered_performance_timing_count": 0,
        "pod_used": False,
        "performance_claimed": False,
        "cases": case_rows,
    }
    result["recount_sha256"] = digest(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu-suite", type=Path, required=True)
    parser.add_argument("--execution-spec", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--expected-suite-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = recount(args.cpu_suite, args.execution_spec, args.raw_root,
                     args.expected_suite_sha256)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
