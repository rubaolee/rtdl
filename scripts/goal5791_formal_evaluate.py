#!/usr/bin/env python3
"""Primary fail-closed evaluator for the Goal5791 formal matrix.

The evaluator consumes only the create-only raw transaction directory.  It
does not import the formal worker, controller, application, or RTDL product.
It revalidates every authority and worker seal, the same-source OFF/ON
ablation boundary, two-phase evidence, behavioral OptiX receipts, and the
frozen row-local bootstrap before emitting a sealed result.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import random
import statistics
from typing import Mapping

from scripts.goal5791_formal_contract import (
    ALLOWED_DELTA_ID,
    AUTHORITY_ROLES,
    BOOTSTRAP_CI_INDICES,
    BOOTSTRAP_DRAWS,
    BOOTSTRAP_SEED_BASE,
    CACHE_POLICY,
    COLD,
    CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT,
    DATA_AUTHORITY_DATASETS,
    DATA_AUTHORITY_FILE_SHA256,
    DATA_AUTHORITY_SHA256,
    DATASET_IDS,
    FUSION_OFF,
    FUSION_OFF_OPERATION_IDS,
    FUSION_ON,
    FUSION_ON_OPERATION_IDS,
    FORMAL_AUTHORIZATION,
    FORMAL_EXECUTION_POLICY,
    FORMAL_OUTPUT_LAYOUT_CONTRACT,
    FORMAL_WORKER_ENVIRONMENT_CONTRACT,
    GOAL,
    INDEPENDENT_RECOUNT_REVIEW_STATUS,
    LIFECYCLES,
    IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT,
    MECHANISM_ID,
    NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT,
    OWNER_FORMAL_EXECUTION_AUTHORITY_SCHEMA,
    OWNER_FORMAL_EXECUTION_STATUS,
    PAIR_COUNT,
    PAPER_ALGORITHM,
    PAPER_OUTCOME_CONSEQUENCE_CONTRACT,
    POSTPREPARE_STATUS,
    PREEXECUTION_AUTHORITY_SCHEMA,
    PREPARED,
    RESOURCE_ADMISSION_CONTRACT,
    SEMANTIC_REQUEST_SHA256,
    PHYSICAL_ENCODING_SHA256,
    SEGMENT_PLAN_INPUT_CONTRACT,
    SOURCE_ADMISSION_POLICY,
    TARGET_BINDING_STATUS,
    TARGET_RUNTIME_ADMISSION_CONTRACT,
    TRACE_INSTRUMENTATION_CONTRACT,
    VARIANTS,
    contract_document,
    contract_sha256,
    digest,
    lifecycle_contract,
    lifecycle_contract_sha256,
    oracle_contract_sha256,
    output_contract_sha256,
    pod_endpoint_identity_record,
    result_lifecycle_label,
    result_row_id,
    schedule,
    schedule_document,
    schedule_sha256,
    statistical_rows,
    timer_contract,
    timer_contract_sha256,
    validate_phase_accounting,
    validate_citation_authority,
    validate_data_authority,
    validate_expected_value_authority,
    validate_runtime_budget_authority,
    validate_source_authority,
    validate_target_materialization_binding,
)


WORKER_SCHEMA = "rtdl.goal5791.formal_worker.v1"
WORKER_STATUS = "COMPLETE"
RUNTIME_SCHEMA = "rtdl.goal5791.formal_runtime.v1"
RESOURCE_ADMISSION_SCHEMA = RESOURCE_ADMISSION_CONTRACT["schema"]
RESOURCE_ADMISSION_STATUS = RESOURCE_ADMISSION_CONTRACT["status"]
TARGET_RUNTIME_ADMISSION_SCHEMA = TARGET_RUNTIME_ADMISSION_CONTRACT["schema"]
TARGET_RUNTIME_ADMISSION_STATUS = TARGET_RUNTIME_ADMISSION_CONTRACT["status"]
CONTROLLER_BOOTSTRAP_OBSERVATION_SCHEMA = (
    CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT["schema"]
)
CONTROLLER_BOOTSTRAP_SOURCE_PATHS = tuple(
    CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT["loaded_harness_source_paths"]
)
MINIMUM_FORMAL_FREE_DISK_BYTES = RESOURCE_ADMISSION_CONTRACT[
    "minimum_required_free_disk_bytes"
]
NVIDIA_SMI_EXECUTABLE = TARGET_RUNTIME_ADMISSION_CONTRACT[
    "nvidia_smi_executable"
]
NVIDIA_SMI_QUERY = TARGET_RUNTIME_ADMISSION_CONTRACT["nvidia_smi_query"]
FORMAL_SOURCE_PATHS = (
    "scripts/goal5791_formal_contract.py",
    "scripts/goal5791_segment_descriptors.py",
    "scripts/goal5791_formal_worker.py",
    "scripts/goal5791_formal_controller.py",
    "scripts/goal5791_formal_evaluate.py",
    "scripts/goal5791_formal_independent_recount.py",
)
SOURCE_TCB_BOUNDARY = str(SOURCE_ADMISSION_POLICY["tcb_boundary"])
TARGET_AUTHORITY_SCHEMA = "rtdl.v4.target_materialization_authority.v2"
OPERATION_CONTRACT_SCHEMA = "rtdl.v4.operation_sequence_contract.v1"
OPERATION_RECEIPT_SCHEMA = "rtdl.v4.operation_evidence_receipt.v1"
OPERATION_EVENT_SCHEMA = "rtdl.v4.operation_evidence_event.v1"
SEGMENT_DESCRIPTOR_SCHEMA = "rtdl.goal5791.rt2a1_segment_descriptor.v1"
PROGRAM_BUNDLE = "v4_builtin_triangle_checked_reduction_composed"
FAMILY_ID = (
    "v4_triangle_per_ray_optix_producer_plus_checked_u64_continuation.v1"
)
OPERATION_EVIDENCE_TCB = (
    "trusted_runtime_records_each_compiler_instrumented_operation_only_after_"
    "its_callable_returns_successfully__not_hardware_or_opaque_partner_kernel_"
    "introspection"
)
U64_MAX = (1 << 64) - 1

FROZEN_PLAN_IDENTITIES = {
    "shared_contract_file_sha256": (
        "b62217a5374732cece8c7eaef93c0f21eb580666559e912eb8dd1bb2aaa7628b"
    ),
    "shared_contract_freeze_sha256": (
        "8ada80c377241aa9a4fde29f26fdc9380257f93cc2264a3e60f2a96a437fced5"
    ),
    "semantic_request_sha256": SEMANTIC_REQUEST_SHA256,
    "physical_encoding_sha256": PHYSICAL_ENCODING_SHA256,
    "admitted_reference_plan_sha256": (
        "8dc1c000146e6df31e77ad86f21ae799bb543aeda68de4054932222523409d8e"
    ),
    "executable_family_plan_sha256": (
        "ddb4909e48ca37b5065e1db86b34ff9610bc9d9a915a76efb651bb692028faa3"
    ),
    "transformation_variant_contract_sha256": (
        "425bb6cffe4edb121f8e1bf3e9a730405439e2af32507b3c8b0c8d6a6b613ff3"
    ),
    "physical_schema_sha256": (
        "97e3e85f8ab60e612e922a156fe2ecd8349b94e51a34d6984d8ce75133070e73"
    ),
}

TARGET_AUTHORITY_FIELDS = {
    "schema", "shared_contract_freeze_sha256",
    "execution_source_archive_sha256", "execution_source_tree_sha256",
    "callback_ir_sha256", "callback_authority_nonce", "contract_sha256",
    "abi_sha256", "provider_identity", "program_bundle_identity",
    "composed_program_sha256", "cupy_version",
    "fusion_on_downstream_operation_recipe",
    "fusion_off_downstream_operation_recipe",
    "fusion_on_downstream_operation_recipe_sha256",
    "fusion_off_downstream_operation_recipe_sha256", "native_library_sha256",
    "native_payload_sha256", "target_identity_sha256",
    "materializer_source_sha256", "source_manifest_sha256",
    "evidence_archive_sha256", "materialization_nonce",
    "actual_native_rehashed_from_preserved_payload",
    "actual_source_tree_recounted_from_preserved_archive",
    "cross_target_native_byte_reproducibility_claimed", "receipt_sha256",
}

PLAN_FIELDS = {
    "schema", "mechanism_id", "shared_contract_file_sha256",
    "shared_contract_freeze_sha256", "semantic_request_sha256",
    "physical_encoding_sha256", "admitted_reference_plan_sha256",
    "executable_family_plan_sha256", "transformation_variant_contract_sha256",
    "physical_schema_sha256", "executable_family_id",
    "execution_source_archive_sha256", "execution_source_tree_sha256",
    "callback_ir_sha256", "callback_authority_nonce", "contract_sha256",
    "abi_sha256", "native_library_sha256", "provider_identity",
    "program_bundle_identity", "composed_program_sha256", "cupy_version",
    "fusion_on_downstream_operation_recipe",
    "fusion_off_downstream_operation_recipe",
    "fusion_on_downstream_operation_recipe_sha256",
    "fusion_off_downstream_operation_recipe_sha256", "target_identity_sha256",
    "target_materialization_receipt_sha256", "materializer_source_sha256",
    "source_manifest_sha256", "materialization_evidence_archive_sha256",
    "materialization_nonce", "input_sha256", "output_contract_sha256",
    "oracle_sha256", "timer_contract_sha256", "lifecycle_contract_sha256",
    "value_count", "same_semantic_ir_required", "same_optix_producer_required",
    "performance_or_timing_claimed",
    "variant_selected_from_app_dataset_result_or_timing", "executable",
    "variant", "only_allowlisted_difference", "lowering_node",
    "downstream_operation_recipe_sha256", "operation_requirements",
    "shared_identity_sha256", "plan_sha256",
}
VARIANT_PLAN_FIELDS = {
    "variant", "lowering_node", "downstream_operation_recipe_sha256",
    "operation_requirements", "plan_sha256",
}
LOWERING_NODES = {
    FUSION_ON: "checked_summary_kernel_then_one_summary_copy_sync",
    FUSION_OFF: "max_sum_materialize_product_sum_then_three_scalar_copy_sync",
}
REDUCTION_COUNTS = {
    FUSION_ON: (1, 1, 0, 0),
    FUSION_OFF: (0, 3, 3, 1),
}

TRAVERSAL_RECEIPT_FIELDS = {
    "schema", "provider_library", "provider_library_path",
    "provider_library_sha256", "route_identity", "semantic_digest",
    "output_digest", "nonce", "physical_executor_classification",
    "expected_program_bundles", "expected_program_bundle_ids",
    "expected_program_observed_at_receipt_edge", "native_snapshot",
    "claim_rules", "receipt_sha256",
}
TRAVERSAL_SNAPSHOT_FIELDS = {
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
TRAVERSAL_CLAIM_RULES = {
    "provider_name_alone_proves_traversal": False,
    "selected_template_alone_proves_traversal": False,
    "successful_optix_launch_required": True,
    "nonzero_traversable_binding_required": True,
    "program_bundle_binding_required": True,
    "output_digest_bound": True,
}

PREEXECUTION_FIELDS = {
    "schema", "goal", "status", "formal_contract_sha256",
    "schedule_sha256", "authority_records", "dataset_input_sha256",
    "oracle_authority_sha256", "target_materialization_binding",
    "formal_worker_count", "registered_performance_timing_count",
    "authorization", "authority_sha256",
}
FORMAL_AUTHORITY_FIELDS = {
    "schema", "goal", "status", "formal_contract_sha256",
    "schedule_sha256", "preexecution_authority_file_sha256",
    "target_materialization_binding_sha256", "formal_identity_sha256",
    "runtime_budget_authority_sha256", "runtime_file_sha256",
    "runtime_sha256", "owner_authorization_nonce", "independent_row_count",
    "formal_worker_count", "execution_target", "resource_confirmation",
    "execution_policy", "authorization", "authority_sha256",
}
RUNTIME_FIELDS = {
    "schema", "goal", "status", "formal_contract_sha256",
    "schedule_sha256", "preexecution_authority_file_sha256",
    "target_materialization_binding_sha256", "formal_identity_sha256",
    "runtime_budget_authority_sha256", "execution_source_root",
    "execution_source_manifest_path",
    "execution_source_manifest_file_sha256", "formal_identity_record",
    "python_executable", "python_executable_sha256", "python_version",
    "numba_version", "llvmlite_version", "numpy_version", "cupy_version",
    "native_library_path",
    "native_library_sha256", "optix_include", "cuda_include",
    "compute_capability", "optix_sdk_version", "shared_contract_freeze_path",
    "shared_contract_freeze_file_sha256", "target_materialization_authority_path",
    "target_materialization_authority_file_sha256", "max_relation_rows",
    "datasets", "neutral_prewarm", "formal_worker_environment",
    "worker_timeout_seconds", "formal_conservative_budget_seconds",
    "runtime_sha256",
}
RESOURCE_ADMISSION_FIELDS = set(RESOURCE_ADMISSION_CONTRACT["fields"])
TARGET_RUNTIME_ADMISSION_FIELDS = set(
    TARGET_RUNTIME_ADMISSION_CONTRACT["fields"]
)


class Goal5791EvaluationError(RuntimeError):
    """Raised when any raw fact, binding, or statistic fails closed."""


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _file_sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def _reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise Goal5791EvaluationError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicates,
            parse_constant=lambda token: (_ for _ in ()).throw(
                Goal5791EvaluationError(f"non-finite JSON token {token}")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Goal5791EvaluationError(f"cannot read strict JSON {path}") from exc
    if not isinstance(value, dict):
        raise Goal5791EvaluationError(f"{path} must contain one object")
    return value


def _keys(value: object, expected: set[str], label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != expected:
        raise Goal5791EvaluationError(f"{label} exact field set drifted")
    return value


def _sha(value: object) -> bool:
    return (
        isinstance(value, str) and len(value) == 64 and value != "0" * 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _sealed(value: Mapping[str, object], field: str, label: str) -> None:
    claimed = value.get(field)
    unsigned = dict(value)
    unsigned.pop(field, None)
    if not _sha(claimed) or claimed != digest(unsigned):
        raise Goal5791EvaluationError(f"{label} canonical seal mismatch")


def _positive_int(value: object, label: str, *, zero: bool = False) -> int:
    if type(value) is not int or value < (0 if zero else 1):
        raise Goal5791EvaluationError(f"{label} is not a valid integer")
    return value


def _seconds(value: object, label: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) \
            or not math.isfinite(float(value)) \
            or float(value) < (0.0 if not positive else 0.0) \
            or (positive and float(value) <= 0.0):
        raise Goal5791EvaluationError(f"{label} is not a valid duration")
    return float(value)


def _cold_claim_boundary() -> dict[str, object]:
    """Reify the cache layers excluded by ``cold_process_warm_system``."""

    exclusions = [
        "operating_system_page_cache",
        "cuda_driver_jit_cache",
        "optix_disk_cache",
    ]
    if CACHE_POLICY.get("cold_claim_excludes") != exclusions \
            or CACHE_POLICY.get(
                "operating_system_page_cache_controlled_or_dropped") is not False \
            or CACHE_POLICY.get(
                "cuda_driver_jit_cache_controlled_or_isolated") is not False \
            or CACHE_POLICY.get(
                "optix_disk_cache_controlled_or_isolated") is not False \
            or CACHE_POLICY.get(
                "round_major_abba_is_uncontrolled_cache_mitigation_not_control") \
                is not True:
        raise Goal5791EvaluationError("formal cold-cache claim boundary drifted")
    return {
        "cold_process_warm_system_definition": CACHE_POLICY["cold_definition"],
        "cold_process_warm_system_excludes": list(exclusions),
        "cuda_driver_jit_cache_controlled_or_isolated": CACHE_POLICY[
            "cuda_driver_jit_cache_controlled_or_isolated"
        ],
        "optix_disk_cache_controlled_or_isolated": CACHE_POLICY[
            "optix_disk_cache_controlled_or_isolated"
        ],
        "round_major_abba_is_uncontrolled_cache_mitigation_not_control": (
            CACHE_POLICY[
                "round_major_abba_is_uncontrolled_cache_mitigation_not_control"
            ]
        ),
    }


def _operation_requirements(variant: str, value_count: int) -> list[dict[str, object]]:
    _positive_int(value_count, "operation value count")
    def req(ordinal: int, operation_id: str, kind: str, *, units: int = 0,
            fixed: int = 0, bytes_per: int = 0, host: bool = False) -> dict[str, object]:
        return {
            "ordinal": ordinal, "operation_id": operation_id, "kind": kind,
            "units_per_value": units, "fixed_units": fixed,
            "bytes_per_unit": bytes_per, "fixed_bytes": 0,
            "host_visibility_boundary": host, "compiler_visible_only": True,
        }
    if variant == FUSION_OFF:
        return [
            req(0, FUSION_OFF_OPERATION_IDS[0], "logical_reduction", units=1),
            req(1, FUSION_OFF_OPERATION_IDS[1], "host_copy_synchronization", fixed=1, bytes_per=8, host=True),
            req(2, FUSION_OFF_OPERATION_IDS[2], "logical_reduction", units=1),
            req(3, FUSION_OFF_OPERATION_IDS[3], "host_copy_synchronization", fixed=1, bytes_per=8, host=True),
            req(4, FUSION_OFF_OPERATION_IDS[4], "device_materialization", units=1, bytes_per=8),
            req(5, FUSION_OFF_OPERATION_IDS[5], "logical_reduction", units=1),
            req(6, FUSION_OFF_OPERATION_IDS[6], "host_copy_synchronization", fixed=1, bytes_per=8, host=True),
        ]
    if variant == FUSION_ON:
        return [
            req(0, FUSION_ON_OPERATION_IDS[0], "compiler_kernel_invocation", units=1),
            req(1, FUSION_ON_OPERATION_IDS[1], "host_copy_synchronization", fixed=4, bytes_per=8, host=True),
        ]
    raise Goal5791EvaluationError("unknown operation variant")


def _program_bundle_id() -> int:
    value = 1469598103934665603
    for byte in PROGRAM_BUNDLE.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & U64_MAX
    return value


def _audit_preexecution(value: dict[str, object]) -> dict[str, object]:
    _keys(value, PREEXECUTION_FIELDS, "preexecution authority")
    if value.get("schema") != PREEXECUTION_AUTHORITY_SCHEMA \
            or value.get("goal") != GOAL or value.get("status") != POSTPREPARE_STATUS \
            or value.get("formal_contract_sha256") != contract_sha256() \
            or value.get("schedule_sha256") != schedule_sha256() \
            or value.get("formal_worker_count") != 0 \
            or value.get("registered_performance_timing_count") != 0:
        raise Goal5791EvaluationError("preexecution authority header drifted")
    _sealed(value, "authority_sha256", "preexecution authority")
    records = _keys(value.get("authority_records"), set(AUTHORITY_ROLES), "authority records")
    for role in AUTHORITY_ROLES:
        record = _keys(records[role], {"path", "sha256", "bytes"}, f"authority {role}")
        if not isinstance(record["path"], str) or not record["path"] \
                or not _sha(record["sha256"]) or type(record["bytes"]) is not int \
                or record["bytes"] < 0:
            raise Goal5791EvaluationError(f"authority record {role} malformed")
    for name in ("dataset_input_sha256", "oracle_authority_sha256"):
        mapping = _keys(value.get(name), set(DATASET_IDS), name)
        if any(not _sha(mapping[dataset]) for dataset in DATASET_IDS):
            raise Goal5791EvaluationError(f"{name} malformed")
    authorization = _keys(
        value.get("authorization"),
        {"authorizes_pod", "authorizes_target_prepare", "authorizes_formal_workers", "authorizes_registered_timing"},
        "preexecution authorization",
    )
    if any(item is not False for item in authorization.values()):
        raise Goal5791EvaluationError("preexecution authority grants execution")
    target = validate_target_materialization_binding(
        value.get("target_materialization_binding")
    )
    return {**value, "target_materialization_binding": target}


def _audit_formal_authority(
    value: dict[str, object], *, preexecution_file_sha256: str,
    preexecution: Mapping[str, object], runtime_file_sha256: str,
    runtime: Mapping[str, object],
) -> dict[str, object]:
    _keys(value, FORMAL_AUTHORITY_FIELDS, "formal authority")
    if FORMAL_OUTPUT_LAYOUT_CONTRACT.get(
        "three_roots_are_pairwise_distinct_same_parent_siblings"
    ) is not True or FORMAL_OUTPUT_LAYOUT_CONTRACT.get(
        "controller_staging_is_exact_hidden_derivative_of_formal_output"
    ) is not True or FORMAL_OUTPUT_LAYOUT_CONTRACT.get(
        "materialization_preexists_formal_output_and_staging_are_absent"
    ) is not True or FORMAL_OUTPUT_LAYOUT_CONTRACT.get(
        "runtime_preexecution_and_formal_authority_are_canonical_distinct_read_only_regular_nonlink_files_before_marker"
    ) is not True or FORMAL_OUTPUT_LAYOUT_CONTRACT.get(
        "exclusive_controller_staging_marker_precedes_bootstrap_target_resource_data_and_source_admissions"
    ) is not True or FORMAL_OUTPUT_LAYOUT_CONTRACT.get(
        "any_post_marker_failure_is_terminal_and_preserves_staging"
    ) is not True:
        raise Goal5791EvaluationError("formal output layout contract drifted")
    target = preexecution["target_materialization_binding"]
    budget = preexecution["authority_records"]["runtime_budget_authority"]
    if value.get("schema") != OWNER_FORMAL_EXECUTION_AUTHORITY_SCHEMA \
            or value.get("goal") != GOAL \
            or value.get("status") != OWNER_FORMAL_EXECUTION_STATUS \
            or value.get("formal_contract_sha256") != contract_sha256() \
            or value.get("schedule_sha256") != schedule_sha256() \
            or value.get("preexecution_authority_file_sha256") != preexecution_file_sha256 \
            or value.get("target_materialization_binding_sha256") != target["binding_sha256"] \
            or value.get("formal_identity_sha256") != target["hashes"]["formal_identity_sha256"] \
            or value.get("runtime_budget_authority_sha256") != budget["sha256"] \
            or value.get("runtime_file_sha256") != runtime_file_sha256 \
            or value.get("runtime_sha256") != runtime["runtime_sha256"] \
            or value.get("independent_row_count") != len(statistical_rows()) \
            or value.get("formal_worker_count") != len(schedule()) \
            or value.get("execution_policy") != FORMAL_EXECUTION_POLICY \
            or value.get("authorization") != FORMAL_AUTHORIZATION:
        raise Goal5791EvaluationError("formal authority binding drifted")
    execution_target = _keys(
        value.get("execution_target"),
        set(FORMAL_OUTPUT_LAYOUT_CONTRACT["execution_target_fields"]),
        "formal execution target",
    )
    endpoint = _keys(
        execution_target.get("pod_endpoint"),
        {"ssh_user", "host", "port", "identity_sha256"}, "POD endpoint",
    )
    try:
        expected_endpoint = pod_endpoint_identity_record(
            ssh_user=endpoint["ssh_user"], host=endpoint["host"],
            port=endpoint["port"],
        )
    except Exception as exc:
        raise Goal5791EvaluationError("POD endpoint identity malformed") from exc
    roots = tuple(
        execution_target.get(name) for name in (
            "target_materialization_root", "create_only_formal_output_root",
            "controller_incomplete_staging_root",
        )
    )
    if any(not isinstance(root, str) for root in roots):
        raise Goal5791EvaluationError("formal execution root is malformed")
    pure_roots = tuple(PurePosixPath(root) for root in roots)
    materialization, formal_output, formal_staging = pure_roots
    expected_staging = formal_output.with_name(
        f".{formal_output.name}.goal5791_incomplete"
    )
    if endpoint != expected_endpoint \
            or any(
                "\\" in raw or pure.as_posix() != raw or not pure.is_absolute()
                or raw in ("/", "/root", "/tmp", "/workspace")
                or any(part in (".", "..") for part in pure.parts)
                or "goal5791" not in pure.name.lower()
                for raw, pure in zip(roots, pure_roots, strict=True)
            ) \
            or len(set(pure_roots)) != 3 \
            or len({pure.parent for pure in pure_roots}) != 1 \
            or formal_staging != expected_staging \
            or PurePosixPath(str(runtime["execution_source_root"])) \
                != materialization / "source" \
            or execution_target.get(
                "target_materialization_root_observed_existing_and_bound_at_authority_creation"
            ) is not True \
            or execution_target.get(
                "formal_output_root_observed_absent_at_authority_creation"
            ) is not True \
            or execution_target.get(
                "controller_incomplete_staging_root_observed_absent_at_authority_creation"
            ) is not True \
            or execution_target.get(
                "preexisting_or_shared_formal_output_root_allowed"
            ) is not False:
        raise Goal5791EvaluationError("formal create-only execution target drifted")
    resources = _keys(
        value.get("resource_confirmation"),
        set(FORMAL_OUTPUT_LAYOUT_CONTRACT["resource_confirmation_fields"]),
        "formal resource confirmation",
    )
    window = resources.get("owner_confirmed_uninterrupted_window_hours")
    disk = resources.get("confirmed_free_disk_bytes")
    observed = resources.get(
        "formal_output_parent_free_bytes_observed_at_authority_creation"
    )
    minimum = resources.get("minimum_required_free_disk_bytes")
    if isinstance(window, bool) or not isinstance(window, (int, float)) \
            or not math.isfinite(float(window)) or float(window) < 7.0 \
            or type(disk) is not int \
            or type(observed) is not int or observed < disk \
            or type(minimum) is not int \
            or minimum != FORMAL_OUTPUT_LAYOUT_CONTRACT[
                "minimum_required_free_disk_bytes"
            ] \
            or disk < minimum \
            or resources.get("formal_output_parent_resolved_path") \
                != formal_output.parent.as_posix() \
            or resources.get("confirmed_before_formal_worker_zero") is not True:
        raise Goal5791EvaluationError("formal resource confirmation drifted")
    nonce = value.get("owner_authorization_nonce")
    if not isinstance(nonce, str) or len(nonce) != 64 or not all(c in "0123456789abcdef" for c in nonce):
        raise Goal5791EvaluationError("formal authority nonce malformed")
    _sealed(value, "authority_sha256", "formal authority")
    return value


def _audit_runtime(
    value: dict[str, object], *, preexecution_file_sha256: str,
    preexecution: Mapping[str, object],
    runtime_budget_authority: Mapping[str, object],
) -> dict[str, object]:
    _keys(value, RUNTIME_FIELDS, "runtime")
    target = preexecution["target_materialization_binding"]
    budget = preexecution["authority_records"]["runtime_budget_authority"]
    if value.get("schema") != RUNTIME_SCHEMA or value.get("goal") != GOAL \
            or value.get("status") != "TARGET_PREPARED__FORMAL_AUTHORITY_STILL_REQUIRED" \
            or value.get("formal_contract_sha256") != contract_sha256() \
            or value.get("schedule_sha256") != schedule_sha256() \
            or value.get("preexecution_authority_file_sha256") != preexecution_file_sha256 \
            or value.get("target_materialization_binding_sha256") != target["binding_sha256"] \
            or value.get("formal_identity_sha256") != target["hashes"]["formal_identity_sha256"] \
            or value.get("runtime_budget_authority_sha256") != budget["sha256"] \
            or value.get("native_library_sha256") != target["hashes"]["native_library_sha256"] \
            or value.get("cupy_version") != target["versions"]["cupy_version"] \
            or value.get("python_version") != target["versions"]["python_version"] \
            or value.get("compute_capability") != target["versions"]["compute_capability"] \
            or value.get("optix_sdk_version") != target["versions"]["optix_sdk_version"] \
            or value.get("target_materialization_authority_file_sha256") != target["hashes"]["target_materialization_authority_sha256"] \
            or value.get("max_relation_rows") != 1_000_000:
        raise Goal5791EvaluationError("runtime identity drifted")
    _sealed(value, "runtime_sha256", "runtime")
    for name in (
        "execution_source_root", "execution_source_manifest_path",
        "python_executable", "native_library_path",
        "optix_include", "cuda_include", "shared_contract_freeze_path",
        "target_materialization_authority_path",
    ):
        if not isinstance(value.get(name), str) or not value[name]:
            raise Goal5791EvaluationError(f"runtime path is empty: {name}")
    for name in (
        "python_version", "numba_version", "llvmlite_version",
        "numpy_version", "cupy_version",
    ):
        if not isinstance(value.get(name), str) or not value[name]:
            raise Goal5791EvaluationError(f"runtime version is empty: {name}")
    if value.get("llvmlite_version") != "0.47.0":
        raise Goal5791EvaluationError("runtime llvmlite identity drifted")
    frozen_budget = runtime_budget_authority.get("frozen_budget")
    if not isinstance(frozen_budget, Mapping):
        raise Goal5791EvaluationError("runtime budget authority is malformed")
    expected_worker_timeout = _seconds(
        FORMAL_EXECUTION_POLICY["per_worker_timeout_seconds"],
        "formal execution policy worker timeout", positive=True,
    )
    expected_formal_budget = _seconds(
        frozen_budget.get("formal_conservative_budget_seconds"),
        "runtime budget authority formal conservative budget", positive=True,
    )
    if not _sha(value.get("python_executable_sha256")) \
            or value.get("execution_source_manifest_file_sha256") \
                != target["hashes"]["execution_source_manifest_sha256"] \
            or value.get("shared_contract_freeze_file_sha256") \
                != FROZEN_PLAN_IDENTITIES["shared_contract_file_sha256"] \
            or _seconds(
                value.get("worker_timeout_seconds"), "worker timeout",
                positive=True,
            ) != expected_worker_timeout \
            or _seconds(
                value.get("formal_conservative_budget_seconds"),
                "formal conservative budget", positive=True,
            ) != expected_formal_budget:
        raise Goal5791EvaluationError("runtime frozen identity or budget drifted")
    identity = _keys(
        value.get("formal_identity_record"),
        {
            "schema", "prepared_identity_sha256", "runtime_identity_sha256",
            "formal_contract_sha256", "schedule_sha256", "formal_sources",
            "formal_worker_count", "independent_row_count",
            "formal_identity_sha256",
        },
        "runtime formal identity record",
    )
    formal_sources = _keys(
        identity.get("formal_sources"), set(FORMAL_SOURCE_PATHS),
        "runtime formal source map",
    )
    identity_unsigned = dict(identity)
    identity_claim = identity_unsigned.pop("formal_identity_sha256", None)
    if identity.get("schema") != "rtdl.goal5791.formal_identity.v1" \
            or identity.get("prepared_identity_sha256") \
                != target["hashes"]["prepared_identity_sha256"] \
            or identity.get("runtime_identity_sha256") \
                != target["hashes"]["runtime_identity_sha256"] \
            or identity.get("formal_contract_sha256") != contract_sha256() \
            or identity.get("schedule_sha256") != schedule_sha256() \
            or identity.get("formal_worker_count") != len(schedule()) \
            or identity.get("independent_row_count") != len(statistical_rows()) \
            or identity_claim != value["formal_identity_sha256"] \
            or identity_claim != target["hashes"]["formal_identity_sha256"] \
            or identity_claim != digest(identity_unsigned) \
            or any(not _sha(formal_sources[name]) for name in FORMAL_SOURCE_PATHS):
        raise Goal5791EvaluationError("runtime formal identity preimage drifted")
    datasets = _keys(value.get("datasets"), set(DATASET_IDS), "runtime datasets")
    for dataset_id in DATASET_IDS:
        record = _keys(
            datasets[dataset_id],
            {"edge_path", "input_sha256", "size_bytes", "expected_triangle_count", "oracle_authority_sha256"},
            f"runtime dataset {dataset_id}",
        )
        frozen = DATA_AUTHORITY_DATASETS[dataset_id]
        if not isinstance(record.get("edge_path"), str) or not record["edge_path"] \
                or record["input_sha256"] != preexecution["dataset_input_sha256"][dataset_id] \
                or record["input_sha256"] != frozen["sha256"] \
                or record["oracle_authority_sha256"] != preexecution["oracle_authority_sha256"][dataset_id] \
                or record["oracle_authority_sha256"] != frozen["oracle_authority_sha256"] \
                or record["size_bytes"] != frozen["bytes"] \
                or record["expected_triangle_count"] != frozen["expected_triangle_count"]:
            raise Goal5791EvaluationError(f"runtime dataset {dataset_id} drifted")
    neutral = _keys(
        value.get("neutral_prewarm"),
        {"edge_path", "input_sha256", "size_bytes", "expected_triangle_count", "purpose", "formal_input", "variant_order"},
        "neutral prewarm",
    )
    if not isinstance(neutral.get("edge_path"), str) or not neutral["edge_path"] \
            or not _sha(neutral["input_sha256"]) \
            or type(neutral.get("size_bytes")) is not int or neutral["size_bytes"] <= 0 \
            or type(neutral.get("expected_triangle_count")) is not int \
            or neutral["expected_triangle_count"] <= 0 \
            or neutral["purpose"] != "recipe_jit_cache_neutralization_only" \
            or neutral["formal_input"] is not False \
            or neutral["variant_order"] != [FUSION_OFF, FUSION_ON]:
        raise Goal5791EvaluationError("neutral prewarm drifted")
    frozen_environment_keys = FORMAL_WORKER_ENVIRONMENT_CONTRACT.get(
        "frozen_keys"
    )
    dynamic_environment_keys = FORMAL_WORKER_ENVIRONMENT_CONTRACT.get(
        "dynamic_keys"
    )
    if not isinstance(frozen_environment_keys, list) \
            or len(frozen_environment_keys) != 14 \
            or any(not isinstance(name, str) or not name
                   for name in frozen_environment_keys) \
            or len(set(frozen_environment_keys)) != len(frozen_environment_keys) \
            or dynamic_environment_keys != ["CUPY_CACHE_DIR", "NUMBA_CACHE_DIR"] \
            or FORMAL_WORKER_ENVIRONMENT_CONTRACT.get(
                "exact_live_key_set_required") is not True \
            or FORMAL_WORKER_ENVIRONMENT_CONTRACT.get(
                "ambient_environment_inherited") is not False \
            or FORMAL_WORKER_ENVIRONMENT_CONTRACT.get(
                "python_locale_coercion_or_injected_lc_ctype_allowed") is not False:
        raise Goal5791EvaluationError(
            "formal worker environment contract drifted"
        )
    environment = _keys(
        value.get("formal_worker_environment"), set(frozen_environment_keys),
        "formal worker environment",
    )
    if any(
        not isinstance(item, str) or (name != "LD_PRELOAD" and not item)
        for name, item in environment.items()
    ) or environment["PYTHONHASHSEED"] != "0" \
            or environment["PYTHONDONTWRITEBYTECODE"] != "1" \
            or environment["PYTHONNOUSERSITE"] != "1" \
            or environment["LC_ALL"] \
                != FORMAL_WORKER_ENVIRONMENT_CONTRACT["lc_all"] \
            or environment["LD_PRELOAD"] \
                != FORMAL_WORKER_ENVIRONMENT_CONTRACT["ld_preload"] \
            or any(
                not isinstance(environment[name], str) or not environment[name]
                for name in (
                    "PYTHONPATH", "PATH", "RTDL_OPTIX_LIB",
                    "RTDL_OPTIX_LIBRARY", "RTDL_V4_CUDA_PREFIX",
                    "RTDL_V4_OPTIX_PREFIX",
                )
            ) \
            or environment["RTDL_OPTIX_LIB"] != value["native_library_path"] \
            or environment["RTDL_OPTIX_LIBRARY"] != value["native_library_path"]:
        raise Goal5791EvaluationError("formal worker environment policy drifted")
    return value


def _audit_resource_admission(
    value: dict[str, object], *, formal: Mapping[str, object],
    formal_authority_file_sha256: str,
) -> dict[str, object]:
    _keys(value, RESOURCE_ADMISSION_FIELDS, "resource admission")
    _sealed(value, "admission_sha256", "resource admission")
    target = formal["execution_target"]
    resources = formal["resource_confirmation"]
    confirmed = resources["confirmed_free_disk_bytes"]
    authority_observed = resources[
        "formal_output_parent_free_bytes_observed_at_authority_creation"
    ]
    minimum = resources["minimum_required_free_disk_bytes"]
    controller_observed = value.get(
        "controller_observed_free_disk_bytes_before_worker_zero"
    )
    if RESOURCE_ADMISSION_CONTRACT.get(
        "controller_live_free_must_meet_authority_confirmed_and_minimum"
    ) is not True or any(type(number) is not int for number in (
        confirmed, authority_observed, minimum, controller_observed,
    )) or minimum != MINIMUM_FORMAL_FREE_DISK_BYTES \
            or authority_observed < confirmed or confirmed < minimum \
            or controller_observed < confirmed or controller_observed < minimum:
        raise Goal5791EvaluationError("resource admission threshold drifted")
    if value.get("schema") != RESOURCE_ADMISSION_SCHEMA \
            or value.get("goal") != GOAL \
            or value.get("status") != RESOURCE_ADMISSION_STATUS \
            or value.get("formal_authority_file_sha256") \
                != formal_authority_file_sha256 \
            or value.get("formal_authority_sha256") \
                != formal["authority_sha256"] \
            or value.get("target_materialization_root") \
                != target["target_materialization_root"] \
            or value.get("create_only_formal_output_root") \
                != target["create_only_formal_output_root"] \
            or value.get("controller_incomplete_staging_root") \
                != target["controller_incomplete_staging_root"] \
            or value.get("formal_output_parent_resolved_path") \
                != resources["formal_output_parent_resolved_path"] \
            or value.get("authority_confirmed_free_disk_bytes") != confirmed \
            or value.get(
                "authority_observed_free_disk_bytes_at_authority_creation"
            ) != authority_observed \
            or value.get("minimum_required_free_disk_bytes") != minimum \
            or value.get("same_parent_sibling_roots_verified") is not True \
            or value.get(
                "controller_observation_meets_authority_confirmed_threshold"
            ) is not True \
            or value.get(
                "controller_observation_meets_minimum_required_threshold"
            ) is not True \
            or value.get("created_before_worker_zero") is not True:
        raise Goal5791EvaluationError("resource admission binding drifted")
    return value


def _audit_target_runtime_admission(
    value: dict[str, object], *, formal: Mapping[str, object],
    formal_authority_file_sha256: str,
    preexecution: Mapping[str, object], runtime: Mapping[str, object],
) -> dict[str, object]:
    _keys(value, TARGET_RUNTIME_ADMISSION_FIELDS, "target runtime admission")
    _sealed(value, "admission_sha256", "target runtime admission")
    if TARGET_RUNTIME_ADMISSION_CONTRACT.get(
        "bound_target_version_fields"
    ) != ["gpu_uuid", "driver_version", "compute_capability"]:
        raise Goal5791EvaluationError("target runtime version contract drifted")
    target = preexecution["target_materialization_binding"]
    versions = target["versions"]
    before_state = _audit_no_gpu_product_process_state(
        value.get("no_gpu_product_process_state_before_nvidia_smi"),
        expected_phase="before_nvidia_smi",
    )
    after_state = _audit_no_gpu_product_process_state(
        value.get("no_gpu_product_process_state_after_nvidia_smi"),
        expected_phase="after_nvidia_smi",
    )
    if value.get("schema") != TARGET_RUNTIME_ADMISSION_SCHEMA \
            or value.get("goal") != GOAL \
            or value.get("status") != TARGET_RUNTIME_ADMISSION_STATUS \
            or value.get("formal_authority_file_sha256") \
                != formal_authority_file_sha256 \
            or value.get("formal_authority_sha256") \
                != formal["authority_sha256"] \
            or value.get("target_materialization_binding_sha256") \
                != target["binding_sha256"] \
            or value.get("pod_endpoint") \
                != formal["execution_target"]["pod_endpoint"] \
            or value.get("nvidia_smi_executable") != NVIDIA_SMI_EXECUTABLE \
            or value.get("nvidia_smi_query") != NVIDIA_SMI_QUERY \
            or type(value.get("visible_gpu_row_count")) is not int \
            or value.get("visible_gpu_row_count") \
                != TARGET_RUNTIME_ADMISSION_CONTRACT[
                    "exact_visible_gpu_row_count"
                ] \
            or value.get("observed_gpu_uuid") != versions["gpu_uuid"] \
            or value.get("observed_driver_version") \
                != versions["driver_version"] \
            or value.get("observed_compute_capability") \
                != versions["compute_capability"] \
            or value.get("controlled_environment_sha256") \
                != digest(runtime["formal_worker_environment"]) \
            or value.get(
                "controlled_environment_exact_14_keys_verified") is not True \
            or value.get("cupy_cache_dir_absent") is not True \
            or before_state["forbidden_module_matches"] \
            or before_state["forbidden_dso_map_matches"] \
            or after_state["forbidden_module_matches"] \
            or after_state["forbidden_dso_map_matches"] \
            or value.get("cuda_context_or_product_import_used") is not False \
            or value.get("created_before_worker_zero") is not True:
        raise Goal5791EvaluationError("target runtime admission drifted")
    return value


def _audit_target_authority(
    value: dict[str, object], *, file_sha256: str,
    target_binding: Mapping[str, object],
) -> dict[str, object]:
    _keys(value, TARGET_AUTHORITY_FIELDS, "target materialization authority")
    hashes = target_binding["hashes"]
    nonces = target_binding["nonces"]
    versions = target_binding["versions"]
    if value.get("schema") != TARGET_AUTHORITY_SCHEMA \
            or value.get("shared_contract_freeze_sha256") != FROZEN_PLAN_IDENTITIES["shared_contract_freeze_sha256"] \
            or value.get("provider_identity") != "optix" \
            or value.get("program_bundle_identity") != PROGRAM_BUNDLE \
            or value.get("native_library_sha256") != value.get("native_payload_sha256") \
            or value.get("actual_native_rehashed_from_preserved_payload") is not True \
            or value.get("actual_source_tree_recounted_from_preserved_archive") is not True \
            or value.get("cross_target_native_byte_reproducibility_claimed") is not False:
        raise Goal5791EvaluationError("target materialization authority header drifted")
    _sealed(value, "receipt_sha256", "target materialization authority")
    mapping = {
        "execution_source_archive_sha256": "execution_source_archive_sha256",
        "execution_source_tree_sha256": "execution_source_tree_sha256",
        "callback_ir_sha256": "callback_ir_sha256",
        "contract_sha256": "contract_sha256",
        "abi_sha256": "abi_sha256",
        "native_library_sha256": "native_library_sha256",
        "native_payload_sha256": "native_payload_sha256",
        "target_identity_sha256": "target_identity_sha256",
        "composed_program_sha256": "composed_program_sha256",
        "materializer_source_sha256": "materializer_sha256",
        "source_manifest_sha256": "target_source_manifest_sha256",
    }
    if any(value[left] != hashes[right] for left, right in mapping.items()) \
            or value["callback_authority_nonce"] != nonces["callback_authority_nonce"] \
            or value["cupy_version"] != versions["cupy_version"] \
            or value["native_library_sha256"] != hashes["provider_library_sha256"] \
            or value["composed_program_sha256"] != hashes["composed_ptx_sha256"] \
            or file_sha256 != hashes["target_materialization_authority_sha256"]:
        raise Goal5791EvaluationError("target authority/binding cross-link drifted")
    for variant, prefix in ((FUSION_OFF, "fusion_off"), (FUSION_ON, "fusion_on")):
        record = target_binding["recipes"][variant]
        if value[prefix + "_downstream_operation_recipe"] != record["actual_recipe"] \
                or value[prefix + "_downstream_operation_recipe_sha256"] != record["actual_recipe_sha256"] \
                or hashes[prefix + "_recipe_sha256"] != record["actual_recipe_sha256"]:
            raise Goal5791EvaluationError("target actual product recipe drifted")
    return value


def _audit_traversal(
    receipt: object, *, output_sha256: str, query_count: int,
    target_authority: Mapping[str, object], semantic_binding: object,
) -> str:
    value = _keys(receipt, TRAVERSAL_RECEIPT_FIELDS, "traversal receipt")
    snapshot = _keys(
        value.get("native_snapshot"), TRAVERSAL_SNAPSHOT_FIELDS,
        "traversal native snapshot",
    )
    binding = _keys(
        semantic_binding,
        {"authority", "contract", "abi", "composed_ptx", "native", "device_column_count"},
        "traversal semantic binding",
    )
    if binding != {
        "authority": target_authority["callback_authority_nonce"],
        "contract": target_authority["contract_sha256"],
        "abi": target_authority["abi_sha256"],
        "composed_ptx": target_authority["composed_program_sha256"],
        "native": target_authority["native_library_sha256"],
        "device_column_count": True,
    }:
        raise Goal5791EvaluationError("traversal semantic target binding drifted")
    bundle_id = _program_bundle_id()
    nonce = _keys(value.get("nonce"), {"hi", "lo"}, "traversal nonce")
    successful = _positive_int(snapshot.get("successful_launch_count"), "successful launches")
    complete = _positive_int(snapshot.get("complete_context_launch_count"), "complete launches")
    if value.get("schema") != "rtdl.physical_execution.traversal_receipt.v1" \
            or value.get("provider_library") != "librtdl_optix" \
            or not isinstance(value.get("provider_library_path"), str) \
            or not value.get("provider_library_path") \
            or value.get("provider_library_sha256") != target_authority["native_library_sha256"] \
            or value.get("route_identity") != "v4_builtin_triangle_callback_ir:partner_resident_checked_count_v1" \
            or value.get("semantic_digest") != digest(binding) \
            or value.get("output_digest") != output_sha256 \
            or value.get("physical_executor_classification") != "optix_traversal_observed" \
            or value.get("expected_program_bundles") != [PROGRAM_BUNDLE] \
            or value.get("expected_program_bundle_ids") != [bundle_id] \
            or value.get("expected_program_observed_at_receipt_edge") is not True \
            or value.get("claim_rules") != TRAVERSAL_CLAIM_RULES \
            or nonce.get("hi") != snapshot.get("nonce_hi") \
            or nonce.get("lo") != snapshot.get("nonce_lo") \
            or complete != successful \
            or snapshot.get("attempted_launch_count") != successful \
            or snapshot.get("failed_launch_count") != 0 \
            or snapshot.get("incomplete_context_launch_count") != 0 \
            or snapshot.get("pending_context_at_finish") != 0 \
            or snapshot.get("session_error") != 0 \
            or snapshot.get("raygen_invocation_count") != query_count \
            or type(snapshot.get("context_bind_count")) is not int \
            or snapshot["context_bind_count"] != successful \
            or snapshot.get("first_program_bundle_id") != bundle_id \
            or snapshot.get("last_program_bundle_id") != bundle_id \
            or not snapshot.get("first_traversable") \
            or not snapshot.get("last_traversable") \
            or snapshot.get("incomplete_callsite_record_count") != 0 \
            or snapshot.get("incomplete_callsite_lines") != [0] * 32:
        raise Goal5791EvaluationError("behavioral OptiX traversal proof failed")
    zero_allowed = {
        "failed_launch_count", "incomplete_context_launch_count",
        "pending_context_at_finish", "session_error",
        "incomplete_callsite_record_count",
    }
    for name in (
        "attempted_launch_count", "successful_launch_count",
        "complete_context_launch_count", "failed_launch_count",
        "incomplete_context_launch_count", "context_bind_count",
        "raygen_invocation_count", "program_bundle_mix", "traversable_mix",
        "pipeline_mix", "sbt_mix", "stream_mix", "params_mix",
        "callsite_mix", "first_program_bundle_id", "last_program_bundle_id",
        "pending_context_at_finish", "session_error",
        "incomplete_callsite_record_count",
    ):
        _positive_int(
            snapshot.get(name), f"traversal snapshot {name}",
            zero=name in zero_allowed,
        )
    _positive_int(nonce.get("hi"), "traversal nonce hi", zero=True)
    _positive_int(nonce.get("lo"), "traversal nonce lo", zero=True)
    if any(
        type(item) is not int or item != 0
        for item in snapshot["incomplete_callsite_lines"]
    ):
        raise Goal5791EvaluationError("behavioral OptiX callsite proof malformed")
    _sealed(value, "receipt_sha256", "traversal receipt")
    return str(value["receipt_sha256"])


def _audit_plan(
    plan: object, *, worker: Mapping[str, object], plan_input_sha256: str,
    query_count: int, target_authority: Mapping[str, object],
    target_binding: Mapping[str, object],
) -> Mapping[str, object]:
    value = _keys(plan, PLAN_FIELDS, "fusion ablation plan")
    variant = str(worker["variant"])
    if value.get("schema") != "rtdl.v4.fusion_ablation_plan.v2" \
            or value.get("mechanism_id") != MECHANISM_ID \
            or value.get("variant") != variant \
            or value.get("executable_family_id") != FAMILY_ID \
            or value.get("provider_identity") != "optix" \
            or value.get("program_bundle_identity") != PROGRAM_BUNDLE \
            or value.get("same_semantic_ir_required") is not True \
            or value.get("same_optix_producer_required") is not True \
            or value.get("performance_or_timing_claimed") is not False \
            or value.get("variant_selected_from_app_dataset_result_or_timing") is not False \
            or value.get("executable") is not False \
            or value.get("only_allowlisted_difference") != ALLOWED_DELTA_ID \
            or value.get("lowering_node") != LOWERING_NODES[variant]:
        raise Goal5791EvaluationError("fusion ablation plan boundary drifted")
    for name, expected in FROZEN_PLAN_IDENTITIES.items():
        if value.get(name) != expected:
            raise Goal5791EvaluationError(f"frozen plan identity drifted: {name}")
    target_map = {
        "execution_source_archive_sha256": "execution_source_archive_sha256",
        "execution_source_tree_sha256": "execution_source_tree_sha256",
        "callback_ir_sha256": "callback_ir_sha256",
        "callback_authority_nonce": "callback_authority_nonce",
        "contract_sha256": "contract_sha256", "abi_sha256": "abi_sha256",
        "native_library_sha256": "native_library_sha256",
        "composed_program_sha256": "composed_program_sha256",
        "cupy_version": "cupy_version",
        "fusion_on_downstream_operation_recipe": "fusion_on_downstream_operation_recipe",
        "fusion_off_downstream_operation_recipe": "fusion_off_downstream_operation_recipe",
        "fusion_on_downstream_operation_recipe_sha256": "fusion_on_downstream_operation_recipe_sha256",
        "fusion_off_downstream_operation_recipe_sha256": "fusion_off_downstream_operation_recipe_sha256",
        "target_identity_sha256": "target_identity_sha256",
        "target_materialization_receipt_sha256": "receipt_sha256",
        "materializer_source_sha256": "materializer_source_sha256",
        "source_manifest_sha256": "source_manifest_sha256",
        "materialization_evidence_archive_sha256": "evidence_archive_sha256",
        "materialization_nonce": "materialization_nonce",
    }
    for plan_name, target_name in target_map.items():
        if value.get(plan_name) != target_authority.get(target_name):
            raise Goal5791EvaluationError(f"plan/target mismatch: {plan_name}")
    for recipe_variant, prefix in ((FUSION_OFF, "fusion_off"), (FUSION_ON, "fusion_on")):
        record = target_binding["recipes"][recipe_variant]
        if value[prefix + "_downstream_operation_recipe"] != record["actual_recipe"] \
                or value[prefix + "_downstream_operation_recipe_sha256"] != record["actual_recipe_sha256"]:
            raise Goal5791EvaluationError("plan/product recipe binding drifted")
    selected = value[f"{variant}_downstream_operation_recipe_sha256"]
    if value.get("downstream_operation_recipe_sha256") != selected \
            or value.get("input_sha256") != plan_input_sha256 \
            or value.get("output_contract_sha256") != worker["output_contract_sha256"] \
            or value.get("oracle_sha256") != worker["dataset_oracle_authority_sha256"] \
            or value.get("timer_contract_sha256") != worker["timer_contract_sha256"] \
            or value.get("lifecycle_contract_sha256") != worker["lifecycle_contract_sha256"] \
            or value.get("value_count") != query_count \
            or value.get("operation_requirements") != _operation_requirements(variant, query_count):
        raise Goal5791EvaluationError("plan dynamic or operation binding drifted")
    unsigned = dict(value)
    shared_claim = unsigned.pop("shared_identity_sha256", None)
    plan_claim = unsigned.pop("plan_sha256", None)
    if not _sha(plan_claim) or plan_claim != digest(unsigned):
        raise Goal5791EvaluationError("plan seal mismatch")
    common = dict(unsigned)
    for name in (VARIANT_PLAN_FIELDS - {"plan_sha256"}) | {"only_allowlisted_difference"}:
        common.pop(name, None)
    if not _sha(shared_claim) or shared_claim != digest(common):
        raise Goal5791EvaluationError("plan shared identity seal mismatch")
    return value


def _operation_contract(
    variant: str, plan_sha256: str, value_count: int,
) -> dict[str, object]:
    body = {
        "schema": OPERATION_CONTRACT_SCHEMA,
        "plan_sha256": plan_sha256,
        "mechanism_id": MECHANISM_ID,
        "variant": variant,
        "declared_value_count": value_count,
        "requirements": _operation_requirements(variant, value_count),
        "tcb_statement": OPERATION_EVIDENCE_TCB,
        "timing_or_duration_recorded": False,
        "hardware_introspection_claimed": False,
    }
    return {**body, "contract_sha256": digest(body)}


def _audit_operation_receipt(
    receipt: object, *, plan: Mapping[str, object], traversal_sha256: str,
    output_sha256: str, token_nonce: str,
) -> None:
    fields = {
        "schema", "contract_sha256", "plan_sha256", "mechanism_id", "variant",
        "execution_nonce", "value_count", "output_sha256",
        "traversal_receipt_sha256", "events", "event_chain_sha256",
        "successful_event_count", "event_evidence_tcb",
        "hardware_introspection_claimed", "opaque_partner_kernel_count_claimed",
        "timing_or_duration_recorded", "receipt_sha256",
    }
    value = _keys(receipt, fields, "operation receipt")
    variant = str(plan["variant"])
    count = _positive_int(plan["value_count"], "plan value count")
    contract = _operation_contract(variant, str(plan["plan_sha256"]), count)
    if value.get("schema") != OPERATION_RECEIPT_SCHEMA \
            or value.get("contract_sha256") != contract["contract_sha256"] \
            or value.get("plan_sha256") != plan["plan_sha256"] \
            or value.get("mechanism_id") != MECHANISM_ID \
            or value.get("variant") != variant \
            or value.get("execution_nonce") != token_nonce \
            or len(token_nonce) < 16 \
            or value.get("value_count") != count \
            or value.get("output_sha256") != output_sha256 \
            or value.get("traversal_receipt_sha256") != traversal_sha256 \
            or value.get("event_evidence_tcb") != OPERATION_EVIDENCE_TCB \
            or value.get("hardware_introspection_claimed") is not False \
            or value.get("opaque_partner_kernel_count_claimed") is not False \
            or value.get("timing_or_duration_recorded") is not False:
        raise Goal5791EvaluationError("operation receipt identity drifted")
    requirements = contract["requirements"]
    events = value.get("events")
    if not isinstance(events, list) or len(events) != len(requirements) \
            or value.get("successful_event_count") != len(requirements):
        raise Goal5791EvaluationError("operation event cardinality drifted")
    previous = str(contract["contract_sha256"])
    for index, (event, requirement) in enumerate(zip(events, requirements, strict=True)):
        units = requirement["units_per_value"] * count + requirement["fixed_units"]
        expected = {
            "schema": OPERATION_EVENT_SCHEMA, "sequence": index,
            "operation_id": requirement["operation_id"], "kind": requirement["kind"],
            "accounted_units": units,
            "accounted_bytes": requirement["bytes_per_unit"] * units + requirement["fixed_bytes"],
            "previous_event_sha256": previous,
            "recorded_after_callable_success": True,
        }
        checked = _keys(event, set(expected) | {"event_sha256"}, "operation event")
        event_sha = digest(expected)
        if dict(checked) != {**expected, "event_sha256": event_sha}:
            raise Goal5791EvaluationError("operation event order/content drifted")
        previous = event_sha
    if value.get("event_chain_sha256") != previous:
        raise Goal5791EvaluationError("operation event chain drifted")
    _sealed(value, "receipt_sha256", "operation receipt")


def _audit_reduction(
    value: object, *, variant: str, descriptor: Mapping[str, object],
    scalar_sum: int,
) -> None:
    fields = {
        "schema", "maximum_value", "maximum_weight", "weight_sum",
        "value_count", "value_upper_bound", "device_kernel_launch_count",
        "host_synchronization_count", "logical_reduction_count",
        "device_materialization_count", "operation_counts_event_derived",
        "maximum_value_is_device_observed", "maximum_value_provenance",
        "provisional_sum_trusted_only_after_bounds",
    }
    record = _keys(value, fields, "checked-U64 reduction")
    query_count = int(descriptor["query_count"])
    primitive_count = int(descriptor["primitive_count"])
    maximum = _positive_int(record.get("maximum_value"), "maximum value", zero=True)
    maximum_weight = _positive_int(record.get("maximum_weight"), "maximum weight", zero=True)
    weight_sum = _positive_int(record.get("weight_sum"), "weight sum", zero=True)
    counts = (
        record.get("device_kernel_launch_count"),
        record.get("host_synchronization_count"),
        record.get("logical_reduction_count"),
        record.get("device_materialization_count"),
    )
    if record.get("schema") != "rtdl.v4.checked_u64_weighted_reduction.receipt.v1" \
            or record.get("value_count") != query_count \
            or record.get("value_upper_bound") != primitive_count \
            or maximum_weight != descriptor["maximum_weight"] \
            or weight_sum != descriptor["weight_sum"] \
            or maximum > primitive_count \
            or (variant == FUSION_OFF and maximum != primitive_count) \
            or (maximum_weight and maximum > U64_MAX // maximum_weight) \
            or (weight_sum and primitive_count > U64_MAX // weight_sum) \
            or scalar_sum > maximum * weight_sum \
            or scalar_sum > primitive_count * weight_sum \
            or counts != REDUCTION_COUNTS[variant] \
            or record.get("operation_counts_event_derived") is not True \
            or record.get("maximum_value_is_device_observed") is not (variant == FUSION_ON) \
            or record.get("maximum_value_provenance") != ("device_observed" if variant == FUSION_ON else "optix_producer_declared_primitive_bound") \
            or record.get("provisional_sum_trusted_only_after_bounds") is not True:
        raise Goal5791EvaluationError("checked-U64 reduction proof drifted")


def _audit_descriptor(value: object, *, segment_id: int) -> Mapping[str, object]:
    fields = {
        "schema", "segment_id", "partition", "relation_count",
        "primitive_count", "query_count", "host_geometry_bytes",
        "maximum_weight", "weight_sum", "paper_algorithm", "gpu_touched",
    }
    descriptor = _keys(value, fields, "segment descriptor")
    partition = _keys(
        descriptor.get("partition"),
        {"source_begin", "source_end", "oversized_source_part", "global_segment_id"},
        "segment partition",
    )
    relation_count = _positive_int(descriptor.get("relation_count"), "relation count")
    primitive_count = _positive_int(descriptor.get("primitive_count"), "primitive count")
    query_count = _positive_int(descriptor.get("query_count"), "query count")
    maximum_weight = _positive_int(descriptor.get("maximum_weight"), "maximum weight")
    weight_sum = _positive_int(descriptor.get("weight_sum"), "weight sum")
    if descriptor.get("schema") != SEGMENT_DESCRIPTOR_SCHEMA \
            or descriptor.get("segment_id") != segment_id \
            or descriptor.get("paper_algorithm") != PAPER_ALGORITHM \
            or descriptor.get("gpu_touched") is not False \
            or relation_count > 1_000_000 \
            or primitive_count > 1_000_000 \
            or query_count > relation_count \
            or descriptor.get("host_geometry_bytes") != 76 * primitive_count + 68 * query_count \
            or maximum_weight > relation_count or weight_sum != relation_count \
            or partition.get("global_segment_id") != segment_id \
            or type(partition.get("source_begin")) is not int \
            or type(partition.get("source_end")) is not int \
            or type(partition.get("oversized_source_part")) is not int \
            or partition["source_begin"] < 0 \
            or partition["source_end"] <= partition["source_begin"] \
            or partition["oversized_source_part"] < 0:
        raise Goal5791EvaluationError("segment descriptor drifted")
    return descriptor


def _audit_token(
    value: object, *, worker: Mapping[str, object], segment_id: int,
    descriptor_sha256: str, plan_sha256: str, plan_input_sha256: str,
) -> str:
    fields = {
        "pre_admitted_in_preparation", "admitted_during_phase", "creator_pid",
        "segment_ordinal", "descriptor_sha256", "plan_sha256",
        "plan_input_sha256",
        "operation_execution_nonce", "state_before_execute",
        "state_after_execute", "single_use",
    }
    token = _keys(value, fields, "token admission")
    nonce = token.get("operation_execution_nonce")
    if token.get("pre_admitted_in_preparation") is not True \
            or token.get("admitted_during_phase") != "preparation" \
            or token.get("creator_pid") != worker["parent_pid"] \
            or token.get("segment_ordinal") != segment_id \
            or token.get("descriptor_sha256") != descriptor_sha256 \
            or token.get("plan_sha256") != plan_sha256 \
            or token.get("plan_input_sha256") != plan_input_sha256 \
            or token.get("state_before_execute") != "fresh" \
            or token.get("state_after_execute") != "consumed" \
            or token.get("single_use") is not True \
            or not isinstance(nonce, str) or len(nonce) < 16:
        raise Goal5791EvaluationError("execution token admission/consumption drifted")
    return str(nonce)


def _audit_segments(
    worker: Mapping[str, object], *, target_authority: Mapping[str, object],
    target_binding: Mapping[str, object],
) -> tuple[dict[str, object], ...]:
    segment_fields = {
        "segment_id", "descriptor", "segment_descriptor_sha256", "partition",
        "relation_count", "primitive_count", "query_count", "host_geometry_bytes",
        "scalar_sum", "output_sha256", "plan_input_binding",
        "fusion_ablation_plan", "token_admission",
        "operation_evidence_receipt", "checked_u64_weighted_reduction",
        "traversal_receipt", "traversal_semantic_binding",
        "device_phase_terminal_state", "evidence_phase_terminal_state",
        "evidence_sealed_after_device_phase",
    }
    segments = worker.get("segment_evidence")
    if not isinstance(segments, list) or not segments \
            or worker.get("segment_count") != len(segments):
        raise Goal5791EvaluationError("segment cardinality drifted")
    scalar_total = 0
    summary: list[dict[str, object]] = []
    seen_token_nonces: set[str] = set()
    for segment_id, raw_segment in enumerate(segments):
        segment = _keys(raw_segment, segment_fields, "segment evidence")
        if segment.get("segment_id") != segment_id \
                or segment.get("device_phase_terminal_state") != "device_complete_unsealed" \
                or segment.get("evidence_phase_terminal_state") != "sealed" \
                or segment.get("evidence_sealed_after_device_phase") is not True:
            raise Goal5791EvaluationError("two-phase segment evidence drifted")
        descriptor = _audit_descriptor(segment.get("descriptor"), segment_id=segment_id)
        descriptor_sha = segment.get("segment_descriptor_sha256")
        if descriptor_sha != digest(descriptor):
            raise Goal5791EvaluationError("segment descriptor seal drifted")
        plan_input_binding = _keys(
            segment.get("plan_input_binding"),
            set(SEGMENT_PLAN_INPUT_CONTRACT["fields"]),
            "segment plan input binding",
        )
        if SEGMENT_PLAN_INPUT_CONTRACT.get("formal_source_input") \
                != "selected_frozen_dataset_input_sha256" \
                or SEGMENT_PLAN_INPUT_CONTRACT.get(
                    "descriptor_only_input_identity_allowed") is not False:
            raise Goal5791EvaluationError(
                "segment plan input contract drifted"
            )
        expected_plan_input_binding = {
            "schema": SEGMENT_PLAN_INPUT_CONTRACT["schema"],
            "source_input_sha256": worker["input_sha256"],
            "segment_descriptor_sha256": descriptor_sha,
            "formal_input": True,
        }
        if dict(plan_input_binding) != expected_plan_input_binding:
            raise Goal5791EvaluationError(
                "segment plan input/source binding drifted"
            )
        for name in (
            "partition", "relation_count", "primitive_count", "query_count",
            "host_geometry_bytes",
        ):
            if segment.get(name) != descriptor[name]:
                raise Goal5791EvaluationError(f"segment/descriptor mismatch: {name}")
        scalar = _positive_int(segment.get("scalar_sum"), "segment scalar", zero=True)
        if scalar_total > U64_MAX - scalar:
            raise Goal5791EvaluationError("segment scalar aggregation overflow")
        scalar_total += scalar
        segment_output = digest(scalar)
        if segment.get("output_sha256") != segment_output:
            raise Goal5791EvaluationError("segment output seal drifted")
        plan = _audit_plan(
            segment.get("fusion_ablation_plan"), worker=worker,
            plan_input_sha256=digest(expected_plan_input_binding),
            query_count=int(descriptor["query_count"]),
            target_authority=target_authority, target_binding=target_binding,
        )
        token_nonce = _audit_token(
            segment.get("token_admission"), worker=worker,
            segment_id=segment_id, descriptor_sha256=str(descriptor_sha),
            plan_sha256=str(plan["plan_sha256"]),
            plan_input_sha256=digest(expected_plan_input_binding),
        )
        if token_nonce in seen_token_nonces:
            raise Goal5791EvaluationError("worker reused an execution token nonce")
        seen_token_nonces.add(token_nonce)
        traversal_sha = _audit_traversal(
            segment.get("traversal_receipt"), output_sha256=segment_output,
            query_count=int(descriptor["query_count"]),
            target_authority=target_authority,
            semantic_binding=segment.get("traversal_semantic_binding"),
        )
        _audit_operation_receipt(
            segment.get("operation_evidence_receipt"), plan=plan,
            traversal_sha256=traversal_sha, output_sha256=segment_output,
            token_nonce=token_nonce,
        )
        _audit_reduction(
            segment.get("checked_u64_weighted_reduction"),
            variant=str(worker["variant"]), descriptor=descriptor,
            scalar_sum=scalar,
        )
        summary.append({
            "segment_id": segment_id,
            "descriptor": dict(descriptor),
            "descriptor_sha256": descriptor_sha,
            "plan_input_binding": dict(plan_input_binding),
            "scalar_sum": scalar,
            "output_sha256": segment_output,
            "shared_plan_identity_sha256": plan["shared_identity_sha256"],
            "plan_sha256": plan["plan_sha256"],
            "operation_execution_nonce": token_nonce,
            "traversal_semantic_binding": dict(segment["traversal_semantic_binding"]),
            "successful_operation_event_count": segment["operation_evidence_receipt"]["successful_event_count"],
        })
    if scalar_total != worker.get("output_scalar_u64") \
            or digest(scalar_total) != worker.get("output_sha256"):
        raise Goal5791EvaluationError("worker segment aggregation drifted")
    return tuple(summary)


def _audit_phase_sequence(worker: Mapping[str, object]) -> None:
    phases = ("loading", "preparation", "prewarm", "execute", "close")
    seconds = _keys(worker.get("phase_seconds"), set(phases), "phase seconds")
    for phase in phases:
        _seconds(seconds[phase], f"phase {phase}", positive=(phase != "prewarm"))
    sequence = worker.get("phase_sequence")
    if not isinstance(sequence, list) or len(sequence) != len(phases):
        raise Goal5791EvaluationError("phase sequence cardinality drifted")
    try:
        validate_phase_accounting(
            str(worker["lifecycle"]), seconds,
            worker["registered_complete_endpoint_seconds"], sequence,
        )
    except Exception as exc:
        raise Goal5791EvaluationError("registered phase accounting drifted") from exc
    previous_end: int | None = None
    for phase, raw in zip(phases, sequence, strict=True):
        record = _keys(raw, {"phase", "started_ns", "ended_ns", "seconds"}, "phase interval")
        start = _positive_int(record.get("started_ns"), "phase start", zero=True)
        end = _positive_int(record.get("ended_ns"), "phase end")
        recorded = _seconds(record.get("seconds"), "phase interval seconds")
        if record.get("phase") != phase or end < start \
                or not math.isclose(recorded, (end - start) / 1_000_000_000.0, rel_tol=0.0, abs_tol=1e-12) \
                or not math.isclose(recorded, float(seconds[phase]), rel_tol=0.0, abs_tol=1e-12) \
                or (previous_end is not None and start < previous_end):
            raise Goal5791EvaluationError("phase interval/order drifted")
        previous_end = end


def _audit_cache(worker: Mapping[str, object]) -> str:
    fields = {
        "schema", "worker_index", "cupy_cache_dir_identity",
        "cupy_cache_dir_name", "unique_per_worker",
        "cupy_cache_relative_path", "numba_cache_relative_path",
        "numba_cache_dir_identity",
        "shared_between_workers_or_measured_arms",
        "prepared_same_worker_cache_contains_both_variant_recipes",
        "initially_empty_before_product_import",
        "cold_empty_immediately_before_execute",
        "cold_empty_before_execute_applicable",
        "selected_recipe_first_compile_inside_execute",
        "measurement_started_after_both_prewarms", "receipt_sha256",
        "cold_definition", "cold_claim_excludes",
        "operating_system_page_cache_controlled_or_dropped",
        "cuda_driver_jit_cache_controlled_or_isolated",
        "optix_disk_cache_controlled_or_isolated",
        "round_major_abba_is_uncontrolled_cache_mitigation_not_control",
    }
    cache = _keys(worker.get("cache_receipt"), fields, "cache receipt")
    _sealed(cache, "receipt_sha256", "cache receipt")
    lifecycle = worker["lifecycle"]
    name = cache.get("cupy_cache_dir_name")
    identity = cache.get("cupy_cache_dir_identity")
    if cache.get("schema") != "rtdl.goal5791.worker_cache_receipt.v2" \
            or cache.get("worker_index") != worker["worker_index"] \
            or name != f"worker_{int(worker['worker_index']):04d}" \
            or identity != digest({
                "worker_index": worker["worker_index"],
                "directory_name": name,
            }) \
            or cache.get("cupy_cache_relative_path") != "cupy" \
            or cache.get("numba_cache_relative_path") != "numba" \
            or cache.get("numba_cache_dir_identity") != digest({
                "worker_index": worker["worker_index"],
                "directory_name": name,
                "relative_path": "numba",
            }) \
            or cache.get("unique_per_worker") is not True \
            or cache.get("shared_between_workers_or_measured_arms") \
                is not CACHE_POLICY["shared_cache_between_workers_or_measured_arms"] \
            or cache.get(
                "prepared_same_worker_cache_contains_both_variant_recipes") \
                is not (lifecycle == PREPARED) \
            or cache.get("initially_empty_before_product_import") is not True \
            or cache.get("cold_empty_immediately_before_execute") is not (lifecycle == COLD) \
            or cache.get("cold_empty_before_execute_applicable") is not (lifecycle == COLD) \
            or cache.get("selected_recipe_first_compile_inside_execute") is not (lifecycle == COLD) \
            or cache.get("measurement_started_after_both_prewarms") is not (lifecycle == PREPARED) \
            or cache.get("cold_definition") != CACHE_POLICY["cold_definition"] \
            or cache.get("cold_claim_excludes") != CACHE_POLICY["cold_claim_excludes"] \
            or cache.get("operating_system_page_cache_controlled_or_dropped") \
                != CACHE_POLICY["operating_system_page_cache_controlled_or_dropped"] \
            or cache.get("cuda_driver_jit_cache_controlled_or_isolated") \
                != CACHE_POLICY["cuda_driver_jit_cache_controlled_or_isolated"] \
            or cache.get("optix_disk_cache_controlled_or_isolated") \
                != CACHE_POLICY["optix_disk_cache_controlled_or_isolated"] \
            or cache.get(
                "round_major_abba_is_uncontrolled_cache_mitigation_not_control"
            ) != CACHE_POLICY[
                "round_major_abba_is_uncontrolled_cache_mitigation_not_control"
            ]:
        raise Goal5791EvaluationError("worker cache policy drifted")
    return str(identity)


def _audit_prewarm(worker: Mapping[str, object], runtime: Mapping[str, object]) -> None:
    fields = {
        "schema", "performed", "order", "input_sha256", "rows",
        "reported_seconds", "receipt_sha256",
    }
    receipt = _keys(worker.get("prewarm_receipt"), fields, "prewarm receipt")
    _sealed(receipt, "receipt_sha256", "prewarm receipt")
    lifecycle = worker["lifecycle"]
    if receipt.get("schema") != "rtdl.goal5791.worker_prewarm_receipt.v1" \
            or not math.isclose(
                _seconds(receipt.get("reported_seconds"), "prewarm reported seconds"),
                float(worker["phase_seconds"]["prewarm"]), rel_tol=0.0, abs_tol=1e-12,
            ):
        raise Goal5791EvaluationError("prewarm duration binding drifted")
    if lifecycle == COLD:
        if receipt.get("performed") is not False or receipt.get("order") != [] \
                or receipt.get("input_sha256") is not None or receipt.get("rows") != [] \
                or receipt.get("reported_seconds") != 0.0:
            raise Goal5791EvaluationError("cold worker contains prewarm work")
        return
    rows = receipt.get("rows")
    if receipt.get("performed") is not True \
            or receipt.get("order") != [FUSION_OFF, FUSION_ON] \
            or receipt.get("input_sha256") != runtime["neutral_prewarm"]["input_sha256"] \
            or not isinstance(rows, list) or len(rows) != 2:
        raise Goal5791EvaluationError("prepared neutral prewarm drifted")
    for variant, row in zip(VARIANTS, rows, strict=True):
        item = _keys(
            row,
            {
                "variant", "token_pre_admitted_in_preparation",
                "token_consumed_once", "launch_completed", "synchronized",
                "device_pool_freed", "output_exact", "formal_evidence_created",
            },
            "prepared prewarm row",
        )
        if item.get("variant") != variant or any(
            item.get(name) is not True for name in (
                "token_pre_admitted_in_preparation", "token_consumed_once",
                "launch_completed", "synchronized", "device_pool_freed",
                "output_exact",
            )
        ) or item.get("formal_evidence_created") is not False:
            raise Goal5791EvaluationError("prepared recipe prewarm proof drifted")


def _audit_data_admission(
    value: dict[str, object], *, preexecution: Mapping[str, object],
) -> dict[str, object]:
    fields = {
        "schema", "goal", "status", "data_authority_file_sha256",
        "data_authority_sha256", "datasets", "created_before_worker_zero",
        "full_rehash_complete", "unscheduled_bundle_members_opened",
        "drop_caches_or_page_cache_control_used", "admission_sha256",
    }
    _keys(value, fields, "data admission")
    if value.get("schema") != "rtdl.goal5791.data_admission.v1" \
            or value.get("goal") != GOAL \
            or value.get("status") != "PASS__ALL_SCHEDULED_EDGE_BYTES_REHASHED_BEFORE_WORKER_ZERO" \
            or value.get("data_authority_file_sha256") != DATA_AUTHORITY_FILE_SHA256 \
            or value.get("data_authority_sha256") != DATA_AUTHORITY_SHA256 \
            or value.get("created_before_worker_zero") is not True \
            or value.get("full_rehash_complete") is not True \
            or value.get("unscheduled_bundle_members_opened") is not False \
            or value.get("drop_caches_or_page_cache_control_used") is not False:
        raise Goal5791EvaluationError("data admission header drifted")
    _sealed(value, "admission_sha256", "data admission")
    rows = _keys(value.get("datasets"), set(DATASET_IDS), "data admission datasets")
    for dataset_id in DATASET_IDS:
        row = _keys(
            rows[dataset_id],
            {"resolved_path", "sha256", "bytes", "st_dev", "st_ino", "st_mtime_ns", "st_mode", "read_only", "full_rehash_complete"},
            f"data admission {dataset_id}",
        )
        frozen = DATA_AUTHORITY_DATASETS[dataset_id]
        resolved = row["resolved_path"]
        pure = PurePosixPath(resolved) if isinstance(resolved, str) else None
        if pure is None or not pure.is_absolute() or ".." in pure.parts \
                or pure.as_posix() != resolved \
                or row["sha256"] != frozen["sha256"] \
                or row["sha256"] != preexecution["dataset_input_sha256"][dataset_id] \
                or row["bytes"] != frozen["bytes"] \
                or row["read_only"] is not True \
                or row["full_rehash_complete"] is not True \
                or any(type(row[name]) is not int or row[name] < 0 for name in ("st_dev", "st_ino", "st_mtime_ns", "st_mode")) \
                or (row["st_mode"] & 0o170000) != 0o100000 \
                or (row["st_mode"] & 0o222) != 0:
            raise Goal5791EvaluationError(f"data admission row drifted: {dataset_id}")
    return value


def _audit_no_gpu_product_process_state(
    value: object, *, expected_phase: str,
) -> dict[str, object]:
    observation = dict(_keys(
        value,
        set(NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT["fields"]),
        f"no-GPU process-state observation {expected_phase}",
    ))
    phases = NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT["phases"]
    prefixes = NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT[
        "forbidden_module_prefixes"
    ]
    markers = NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT[
        "forbidden_dso_map_markers"
    ]
    names = observation.get("loaded_module_names")
    lines = observation.get("proc_self_maps_lines")
    if not isinstance(names, list) or any(
        not isinstance(name, str) or not name for name in names
    ) or names != sorted(set(names)):
        raise Goal5791EvaluationError("loaded module observation drifted")
    if not isinstance(lines, list) or not lines or any(
        not isinstance(line, str) or not line or "\n" in line or "\r" in line
        for line in lines
    ):
        raise Goal5791EvaluationError("proc-self-maps observation drifted")
    maps_bytes = ("\n".join(lines) + "\n").encode("utf-8")
    module_matches = [
        name for name in names
        if any(
            name == prefix or name.startswith(prefix + ".")
            for prefix in prefixes
        )
    ]
    dso_matches = [
        line for line in lines
        if any(marker in line.lower() for marker in markers)
    ]
    if observation.get("schema") \
            != NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT["schema"] \
            or expected_phase not in phases \
            or observation.get("phase") != expected_phase \
            or observation.get("forbidden_module_prefixes") != prefixes \
            or observation.get("forbidden_dso_map_markers") != markers \
            or observation.get("proc_self_maps_sha256") \
                != hashlib.sha256(maps_bytes).hexdigest() \
            or observation.get("forbidden_module_matches") != module_matches \
            or observation.get("forbidden_dso_map_matches") != dso_matches \
            or module_matches or dso_matches \
            or NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT.get(
                "proc_self_maps_encoding") != "utf-8-strict" \
            or NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT.get(
                "proc_self_maps_line_representation"
            ) != (
                "split_on_lf_without_terminators__all_lines_nonempty__"
                "reconstruct_by_joining_with_lf_and_appending_one_terminal_lf"
            ) \
            or NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT.get(
                "actual_formal_linux_must_read_proc_self_maps"
            ) is not True \
            or NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT.get(
                "forbidden_matches_must_be_empty"
            ) is not True:
        raise Goal5791EvaluationError(
            f"no-GPU process-state observation drifted: {expected_phase}"
        )
    return observation


def _audit_source_admission(
    value: dict[str, object], *, runtime: Mapping[str, object],
    runtime_file_sha256: str, target_binding: Mapping[str, object],
    control_file_copies: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    if SOURCE_ADMISSION_POLICY.get(
        "portable_manifest_is_non_self_referential") is not True \
            or SOURCE_ADMISSION_POLICY.get("expected_regular_file_set") \
                != "manifest_rows_plus_manifest_itself" \
            or SOURCE_ADMISSION_POLICY.get("expected_directory_set") \
                != "root_plus_parents_implied_by_expected_files" \
            or SOURCE_ADMISSION_POLICY.get(
                "controller_full_rehash_and_exact_set_before_worker_zero") \
                is not True \
            or SOURCE_ADMISSION_POLICY.get(
                "every_worker_full_rehash_and_exact_set_before_product_import") \
                is not True \
            or SOURCE_ADMISSION_POLICY.get(
                "all_source_paths_without_write_bits_required") is not True \
            or SOURCE_ADMISSION_POLICY.get(
                "extra_missing_symlink_reparse_or_special_paths_allowed") \
                is not False \
            or SOURCE_ADMISSION_POLICY.get(
                "worker_source_rehash_receipt_required") is not True \
            or SOURCE_ADMISSION_POLICY.get(
                "same_host_malicious_root_race_excluded") is not False \
            or SOURCE_TCB_BOUNDARY \
                != "does_not_exclude_a_malicious_same_host_root_race" \
            or CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT.get(
                "stdlib_environment_and_entrypoint_gate_precedes_shared_imports"
            ) is not True \
            or CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT.get(
                "runtime_bound_module_path_and_hash_gate_required"
            ) is not True:
        raise Goal5791EvaluationError("source admission policy drifted")
    fields = {
        "schema", "goal", "status", "runtime_file_sha256",
        "runtime_sha256", "execution_source_root",
        "execution_source_manifest_file_sha256",
        "execution_source_tree_sha256", "manifest_payload_count",
        "manifest_payload_bytes", "full_manifest_rehash_complete",
        "all_manifest_payloads_read_only", "manifest_file_read_only",
        "exact_regular_file_set_verified",
        "exact_implied_directory_set_verified", "unmanifested_path_count",
        "missing_manifest_payload_count", "symlink_or_special_path_count",
        "all_source_paths_without_write_bits", "regular_file_count",
        "source_directory_count_including_root", "source_path_count",
        "controller_bootstrap_observation",
        "created_before_worker_zero", "same_host_root_race_excluded",
        "tcb_boundary", "admission_sha256",
    }
    _keys(value, fields, "source admission")
    _sealed(value, "admission_sha256", "source admission")
    payload_count = _positive_int(
        value.get("manifest_payload_count"), "source manifest payload count",
    )
    _positive_int(
        value.get("manifest_payload_bytes"), "source manifest payload bytes",
    )
    source_path_count = _positive_int(
        value.get("source_path_count"), "source path count",
    )
    regular_file_count = _positive_int(
        value.get("regular_file_count"), "source regular-file count",
    )
    directory_count = _positive_int(
        value.get("source_directory_count_including_root"),
        "source directory count",
    )
    controller = _keys(
        value.get("controller_bootstrap_observation"),
        set(CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT["fields"]),
        "controller bootstrap observation",
    )
    loaded_sources = _keys(
        controller.get("loaded_harness_sources"),
        set(CONTROLLER_BOOTSTRAP_SOURCE_PATHS),
        "controller bootstrap loaded sources",
    )
    source_root = PurePosixPath(str(runtime["execution_source_root"]))
    formal_sources = runtime["formal_identity_record"]["formal_sources"]
    for relative in CONTROLLER_BOOTSTRAP_SOURCE_PATHS:
        row = _keys(
            loaded_sources[relative], {"resolved_path", "file_sha256"},
            f"controller bootstrap source {relative}",
        )
        if row.get("resolved_path") \
                != (source_root / PurePosixPath(relative)).as_posix() \
                or row.get("file_sha256") != formal_sources[relative]:
            raise Goal5791EvaluationError(
                f"controller bootstrap source drifted: {relative}"
            )
    control_roles = tuple(
        IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT["roles"]
    )
    controls = _keys(
        controller.get("immutable_control_file_observations"),
        set(control_roles), "immutable control-file observations",
    )
    if set(control_file_copies) != set(control_roles):
        raise Goal5791EvaluationError("raw control-file copies drifted")
    control_paths: list[PurePosixPath] = []
    for role in control_roles:
        row = _keys(
            controls[role],
            set(IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT["fields"]),
            f"immutable control file {role}",
        )
        resolved = row.get("resolved_path")
        pure = PurePosixPath(resolved) if isinstance(resolved, str) else None
        mode = row.get("st_mode")
        copy = control_file_copies[role]
        if pure is None or "\\" in resolved or not pure.is_absolute() \
                or pure.as_posix() != resolved or ".." in pure.parts \
                or row.get("file_sha256") != copy["file_sha256"] \
                or row.get("bytes") != copy["bytes"] \
                or any(
                    type(row.get(name)) is not int or row[name] < 0
                    for name in ("st_dev", "st_ino", "st_mtime_ns")
                ) \
                or type(mode) is not int or mode < 0 \
                or (mode & 0o170000) != 0o100000 \
                or (mode & 0o222) != 0 \
                or row.get("regular_nonlink") is not True \
                or row.get("read_only") is not True:
            raise Goal5791EvaluationError(
                f"immutable control-file observation drifted: {role}"
            )
        control_paths.append(pure)
    if len(set(control_paths)) != len(control_roles) \
            or IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT.get(
                "captured_before_transaction_marker"
            ) is not True \
            or IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT.get(
                "rehash_and_stat_unchanged_after_marker_before_other_admissions"
            ) is not True:
        raise Goal5791EvaluationError(
            "immutable control-file transaction observation drifted"
        )
    _audit_no_gpu_product_process_state(
        controller.get("no_gpu_product_process_state_observation"),
        expected_phase="after_shared_import_before_target_probe",
    )
    if value.get("schema") != "rtdl.goal5791.source_admission.v1" \
            or value.get("goal") != GOAL \
            or value.get("status") \
                != "PASS__FULL_EXECUTION_SOURCE_REHASHED_BEFORE_WORKER_ZERO" \
            or value.get("runtime_file_sha256") != runtime_file_sha256 \
            or value.get("runtime_sha256") != runtime["runtime_sha256"] \
            or value.get("execution_source_root") != runtime["execution_source_root"] \
            or value.get("execution_source_manifest_file_sha256") \
                != runtime["execution_source_manifest_file_sha256"] \
            or value.get("execution_source_tree_sha256") \
                != target_binding["hashes"]["execution_source_tree_sha256"] \
            or value.get("full_manifest_rehash_complete") is not True \
            or value.get("all_manifest_payloads_read_only") is not True \
            or value.get("manifest_file_read_only") is not True \
            or value.get("exact_regular_file_set_verified") is not True \
            or value.get("exact_implied_directory_set_verified") is not True \
            or any(
                type(value.get(name)) is not int or value[name] != 0
                for name in (
                    "unmanifested_path_count",
                    "missing_manifest_payload_count",
                    "symlink_or_special_path_count",
                )
            ) \
            or value.get("all_source_paths_without_write_bits") is not True \
            or regular_file_count != payload_count + 1 \
            or source_path_count != regular_file_count + directory_count \
            or controller.get("schema") \
                != CONTROLLER_BOOTSTRAP_OBSERVATION_SCHEMA \
            or controller.get("controller_environment_sha256") \
                != digest(runtime["formal_worker_environment"]) \
            or controller.get(
                "controller_environment_exact_frozen_14_keys_verified"
            ) is not True \
            or controller.get("controller_environment_key_count") != 14 \
            or controller.get("controller_cupy_cache_dir_absent") is not True \
            or controller.get("preimport_stdlib_bootstrap_verified") is not True \
            or controller.get(
                "loaded_harness_paths_and_hashes_match_formal_identity_record"
            ) is not True \
            or controller.get("cuda_context_or_product_import_used") is not False \
            or controller.get(
                "completed_after_transaction_marker_before_worker_zero"
            ) is not True \
            or value.get("created_before_worker_zero") is not True \
            or value.get("same_host_root_race_excluded") is not False \
            or value.get("tcb_boundary") != SOURCE_TCB_BOUNDARY:
        raise Goal5791EvaluationError("source admission identity/boundary drifted")
    return value


def _audit_source_rehash_receipt(
    worker: Mapping[str, object], *, source_admission: Mapping[str, object],
) -> None:
    fields = {
        "schema", "worker_index", "source_admission_sha256",
        "execution_source_root", "execution_source_manifest_file_sha256",
        "execution_source_tree_sha256", "manifest_payload_count",
        "manifest_payload_bytes", "full_manifest_rehash_complete",
        "all_manifest_payloads_read_only", "manifest_file_read_only",
        "exact_regular_file_set_verified",
        "exact_implied_directory_set_verified", "unmanifested_path_count",
        "missing_manifest_payload_count", "symlink_or_special_path_count",
        "all_source_paths_without_write_bits", "regular_file_count",
        "source_directory_count_including_root", "source_path_count",
        "observed_before_product_import", "same_host_root_race_excluded",
        "tcb_boundary", "receipt_sha256",
    }
    receipt = _keys(
        worker.get("source_rehash_receipt"), fields,
        "worker source rehash receipt",
    )
    _sealed(receipt, "receipt_sha256", "worker source rehash receipt")
    shared = (
        "execution_source_root", "execution_source_manifest_file_sha256",
        "execution_source_tree_sha256", "manifest_payload_count",
        "manifest_payload_bytes", "full_manifest_rehash_complete",
        "all_manifest_payloads_read_only", "manifest_file_read_only",
        "exact_regular_file_set_verified",
        "exact_implied_directory_set_verified", "unmanifested_path_count",
        "missing_manifest_payload_count", "symlink_or_special_path_count",
        "all_source_paths_without_write_bits", "regular_file_count",
        "source_directory_count_including_root", "source_path_count",
    )
    if receipt.get("schema") \
            != "rtdl.goal5791.worker_source_rehash_receipt.v1" \
            or receipt.get("worker_index") != worker["worker_index"] \
            or receipt.get("source_admission_sha256") \
                != source_admission["admission_sha256"] \
            or any(receipt.get(name) != source_admission[name] for name in shared) \
            or receipt.get("observed_before_product_import") is not True \
            or receipt.get("same_host_root_race_excluded") is not False \
            or receipt.get("tcb_boundary") != SOURCE_TCB_BOUNDARY:
        raise Goal5791EvaluationError("worker source rehash evidence drifted")


def _audit_input_file_receipt(
    worker: Mapping[str, object], *, data_admission: Mapping[str, object],
) -> None:
    fields = {
        "schema", "dataset_id", "resolved_path", "bytes", "st_dev", "st_ino",
        "st_mtime_ns", "st_mode", "read_only", "observed_before_loader_read",
        "pre_and_post_loader_fstat_equal", "proc_self_fd_used", "receipt_sha256",
    }
    receipt = _keys(worker.get("input_file_receipt"), fields, "worker input file receipt")
    _sealed(receipt, "receipt_sha256", "worker input file receipt")
    admitted = data_admission["datasets"][worker["dataset_id"]]
    if receipt.get("schema") != "rtdl.goal5791.worker_input_file_receipt.v1" \
            or receipt.get("dataset_id") != worker["dataset_id"] \
            or any(receipt.get(name) != admitted[name] for name in (
                "resolved_path", "bytes", "st_dev", "st_ino", "st_mtime_ns", "st_mode", "read_only",
            )) \
            or receipt.get("observed_before_loader_read") is not True \
            or receipt.get("pre_and_post_loader_fstat_equal") is not True \
            or receipt.get("proc_self_fd_used") is not True:
        raise Goal5791EvaluationError("worker input file/admission binding drifted")


def _audit_authority_manifest(
    raw_root: Path, *, preexecution: Mapping[str, object],
    preexecution_file_sha256: str,
) -> dict[str, object]:
    manifest = _read_json(raw_root / "AUTHORITY_MANIFEST.json")
    _keys(
        manifest,
        {"schema", "goal", "preexecution_authority_file_sha256", "authorities", "manifest_sha256"},
        "raw authority manifest",
    )
    if manifest.get("schema") != "rtdl.goal5791.raw_authority_manifest.v1" \
            or manifest.get("goal") != GOAL \
            or manifest.get("preexecution_authority_file_sha256") != preexecution_file_sha256:
        raise Goal5791EvaluationError("raw authority manifest header drifted")
    _sealed(manifest, "manifest_sha256", "raw authority manifest")
    rows = _keys(manifest.get("authorities"), set(AUTHORITY_ROLES), "raw authorities")
    validators = {
        "source_authority": validate_source_authority,
        "data_authority": validate_data_authority,
        "runtime_budget_authority": validate_runtime_budget_authority,
        "expected_value_authority": validate_expected_value_authority,
        "citation_authority": validate_citation_authority,
    }
    authority_root = raw_root / "AUTHORITIES"
    expected_authority_names = sorted(
        f"{role}.json" for role in AUTHORITY_ROLES
    )
    observed_authority_paths = (
        sorted(authority_root.iterdir(), key=lambda path: path.name)
        if authority_root.is_dir() and not authority_root.is_symlink()
        else []
    )
    if [path.name for path in observed_authority_paths] \
            != expected_authority_names or any(
        path.is_symlink() or not path.is_file()
        for path in observed_authority_paths
    ):
        raise Goal5791EvaluationError("raw authority file set drifted")
    for role in AUTHORITY_ROLES:
        record = _keys(
            rows[role], {"path", "file_sha256", "bytes"},
            f"raw authority manifest {role}",
        )
        expected_relative = f"AUTHORITIES/{role}.json"
        path = authority_root / f"{role}.json"
        pre_record = preexecution["authority_records"][role]
        if record.get("path") != expected_relative \
                or not path.is_file() or path.is_symlink() \
                or record.get("file_sha256") != _file_sha256(path) \
                or record.get("file_sha256") != pre_record["sha256"] \
                or record.get("bytes") != path.stat().st_size \
                or record.get("bytes") != pre_record["bytes"]:
            raise Goal5791EvaluationError(f"raw authority bytes drifted: {role}")
        # Strict duplicate-key JSON parse is independent of the semantic
        # authority validator and is intentionally required for every role.
        _read_json(path)
        try:
            validators[role](path)
        except Exception as exc:
            raise Goal5791EvaluationError(
                f"raw authority semantic validation failed: {role}"
            ) from exc
    top_data = raw_root / "DATA_AUTHORITY.json"
    copied_data = authority_root / "data_authority.json"
    if top_data.read_bytes() != copied_data.read_bytes():
        raise Goal5791EvaluationError("duplicate raw data-authority copies differ")
    return manifest


WORKER_FIELDS = {
    "schema", "goal", "status", "formal_worker", "worker_index", "row_index",
    "row_id", "dataset_id", "lifecycle", "pair_index", "order_ordinal",
    "variant", "paper_algorithm", "mechanism_id", "parent_pid",
    "registered_complete_endpoint_seconds", "phase_seconds", "phase_sequence",
    "timer_contract_sha256", "timer_contract", "lifecycle_contract_sha256",
    "lifecycle_contract", "input_sha256", "output_scalar_u64", "output_sha256",
    "oracle_output_scalar_u64", "oracle_output_sha256",
    "output_contract_sha256", "oracle_contract_sha256",
    "dataset_oracle_authority_sha256", "formal_contract_sha256",
    "schedule_sha256", "runtime_sha256", "runtime_file_sha256",
    "preexecution_authority_file_sha256",
    "preexecution_authority_sha256", "target_materialization_binding_sha256",
    "target_materialization_authority_file_sha256",
    "formal_authority_file_sha256", "formal_authority_sha256",
    "formal_identity_sha256", "runtime_budget_authority_sha256",
    "data_admission_sha256", "data_authority_file_sha256",
    "source_admission_sha256", "source_rehash_receipt", "llvmlite_version",
    "target_materialization_binding", "cache_receipt", "prewarm_receipt",
    "input_file_receipt", "segment_count", "segment_evidence",
    "two_phase_execution_evidence_seal_enforced",
    "evidence_hashing_or_serialization_inside_registered_timer",
    "comparator_inside_registered_timer",
    "receipt_serialization_inside_registered_timer",
    "execute_timer_continuous_without_pause", "deep_verification_inside_execute",
    "constant_time_pre_admitted_token_binding_only_inside_execute",
    "evidence_seal_started_after_registered_endpoint",
    "registered_endpoint_is_one_continuous_interval",
    "cold_registered_endpoint_includes_interphase_dispatch_and_cache_check",
    "retry_resume_replacement_row_drop_relabel_used", "worker_sha256",
}


def _audit_worker(
    worker: dict[str, object], *, expected: Mapping[str, object],
    preexecution: Mapping[str, object], formal: Mapping[str, object],
    runtime: Mapping[str, object], data_admission: Mapping[str, object],
    source_admission: Mapping[str, object],
    target_authority: Mapping[str, object], preexecution_file_sha256: str,
    formal_file_sha256: str, target_authority_file_sha256: str,
    runtime_file_sha256: str,
) -> dict[str, object]:
    _keys(worker, WORKER_FIELDS, "formal worker")
    _sealed(worker, "worker_sha256", "formal worker")
    for name in (
        "worker_index", "row_index", "row_id", "dataset_id", "lifecycle",
        "pair_index", "order_ordinal", "variant", "paper_algorithm",
        "mechanism_id",
    ):
        if worker.get(name) != expected[name]:
            raise Goal5791EvaluationError(f"worker schedule drifted: {name}")
    if worker.get("schema") != WORKER_SCHEMA or worker.get("goal") != GOAL \
            or worker.get("status") != WORKER_STATUS \
            or worker.get("formal_worker") is not True \
            or worker.get("paper_algorithm") != PAPER_ALGORITHM \
            or worker.get("mechanism_id") != MECHANISM_ID \
            or worker.get("llvmlite_version") != runtime["llvmlite_version"] \
            or worker.get("llvmlite_version") != "0.47.0" \
            or worker.get("variant") not in VARIANTS \
            or worker.get("lifecycle") not in LIFECYCLES:
        raise Goal5791EvaluationError("formal worker header drifted")
    _positive_int(worker.get("parent_pid"), "parent PID")
    _seconds(worker.get("registered_complete_endpoint_seconds"), "registered endpoint", positive=True)
    false_flags = (
        "evidence_hashing_or_serialization_inside_registered_timer",
        "comparator_inside_registered_timer",
        "receipt_serialization_inside_registered_timer",
        "deep_verification_inside_execute",
        "retry_resume_replacement_row_drop_relabel_used",
    )
    true_flags = (
        "two_phase_execution_evidence_seal_enforced",
        "execute_timer_continuous_without_pause",
        "constant_time_pre_admitted_token_binding_only_inside_execute",
        "evidence_seal_started_after_registered_endpoint",
        "registered_endpoint_is_one_continuous_interval",
    )
    if any(worker.get(name) is not False for name in false_flags) \
            or any(worker.get(name) is not True for name in true_flags):
        raise Goal5791EvaluationError("formal timer/evidence claim boundary drifted")
    lifecycle = str(worker["lifecycle"])
    if worker.get(
        "cold_registered_endpoint_includes_interphase_dispatch_and_cache_check"
    ) is not (lifecycle == COLD):
        raise Goal5791EvaluationError(
            "formal continuous endpoint scope drifted"
        )
    if worker.get("timer_contract") != timer_contract(lifecycle) \
            or worker.get("timer_contract_sha256") != timer_contract_sha256(lifecycle) \
            or worker.get("lifecycle_contract") != lifecycle_contract(lifecycle) \
            or worker.get("lifecycle_contract_sha256") != lifecycle_contract_sha256(lifecycle):
        raise Goal5791EvaluationError("serialized timer/lifecycle contract drifted")
    dataset = str(worker["dataset_id"])
    runtime_dataset = runtime["datasets"][dataset]
    frozen = DATA_AUTHORITY_DATASETS[dataset]
    output = _positive_int(worker.get("output_scalar_u64"), "worker output", zero=True)
    oracle = _positive_int(worker.get("oracle_output_scalar_u64"), "oracle output", zero=True)
    if worker.get("input_sha256") != preexecution["dataset_input_sha256"][dataset] \
            or worker.get("input_sha256") != frozen["sha256"] \
            or output != oracle or oracle != runtime_dataset["expected_triangle_count"] \
            or oracle != frozen["expected_triangle_count"] \
            or worker.get("output_sha256") != digest(output) \
            or worker.get("oracle_output_sha256") != digest(oracle) \
            or worker.get("output_sha256") != worker.get("oracle_output_sha256") \
            or worker.get("output_contract_sha256") != output_contract_sha256() \
            or worker.get("oracle_contract_sha256") != oracle_contract_sha256() \
            or worker.get("dataset_oracle_authority_sha256") != preexecution["oracle_authority_sha256"][dataset] \
            or worker.get("dataset_oracle_authority_sha256") != frozen["oracle_authority_sha256"]:
        raise Goal5791EvaluationError("formal input/output/oracle binding drifted")
    target = preexecution["target_materialization_binding"]
    budget = preexecution["authority_records"]["runtime_budget_authority"]["sha256"]
    expected_pins = {
        "formal_contract_sha256": contract_sha256(),
        "schedule_sha256": schedule_sha256(),
        "runtime_sha256": runtime["runtime_sha256"],
        "runtime_file_sha256": runtime_file_sha256,
        "preexecution_authority_file_sha256": preexecution_file_sha256,
        "preexecution_authority_sha256": preexecution["authority_sha256"],
        "target_materialization_binding_sha256": target["binding_sha256"],
        "target_materialization_authority_file_sha256": target_authority_file_sha256,
        "formal_authority_file_sha256": formal_file_sha256,
        "formal_authority_sha256": formal["authority_sha256"],
        "formal_identity_sha256": target["hashes"]["formal_identity_sha256"],
        "runtime_budget_authority_sha256": budget,
        "data_admission_sha256": data_admission["admission_sha256"],
        "data_authority_file_sha256": DATA_AUTHORITY_FILE_SHA256,
        "source_admission_sha256": source_admission["admission_sha256"],
    }
    if any(worker.get(name) != value for name, value in expected_pins.items()) \
            or worker.get("target_materialization_binding") != target:
        raise Goal5791EvaluationError("worker authority chain drifted")
    _audit_phase_sequence(worker)
    cache_identity = _audit_cache(worker)
    _audit_prewarm(worker, runtime)
    _audit_input_file_receipt(worker, data_admission=data_admission)
    _audit_source_rehash_receipt(
        worker, source_admission=source_admission,
    )
    segment_summary = _audit_segments(
        worker, target_authority=target_authority, target_binding=target,
    )
    return {
        "cache_identity": cache_identity,
        "segments": segment_summary,
        "worker_sha256": worker["worker_sha256"],
    }


def _read_raw(raw_root: Path) -> tuple[
    list[dict[str, object]], dict[str, object], dict[str, object],
    dict[str, object], dict[str, object], dict[str, object], dict[str, object],
    dict[str, object],
]:
    if not raw_root.is_dir() or raw_root.is_symlink():
        raise Goal5791EvaluationError("raw root is absent")
    required_regular_files = {
        "FORMAL_CONTRACT.json", "SCHEDULE.json", "PREEXECUTION_AUTHORITY.json",
        "OWNER_FORMAL_AUTHORITY.json", "TARGET_BINDING.json",
        "TARGET_MATERIALIZATION_AUTHORITY.json", "RUNTIME.json",
        "DATA_AUTHORITY.json", "DATA_ADMISSION.json", "SOURCE_ADMISSION.json",
        "RESOURCE_ADMISSION.json", "TARGET_RUNTIME_ADMISSION.json",
        "AUTHORITY_MANIFEST.json",
    }
    required_directories = {"AUTHORITIES", "workers", "worker_caches"}
    observed_top_level = {entry.name for entry in raw_root.iterdir()}
    if observed_top_level != required_regular_files | required_directories:
        raise Goal5791EvaluationError(
            "primary raw top-level exact set drifted"
        )
    if any(
        not (raw_root / name).is_file() or (raw_root / name).is_symlink()
        for name in required_regular_files
    ) or any(
        not (raw_root / name).is_dir() or (raw_root / name).is_symlink()
        for name in required_directories
    ):
        raise Goal5791EvaluationError("required raw evidence file drifted")
    formal_contract = _read_json(raw_root / "FORMAL_CONTRACT.json")
    schedule_value = _read_json(raw_root / "SCHEDULE.json")
    if formal_contract != contract_document() or schedule_value != schedule_document():
        raise Goal5791EvaluationError("raw contract or schedule drifted")
    pre_path = raw_root / "PREEXECUTION_AUTHORITY.json"
    formal_path = raw_root / "OWNER_FORMAL_AUTHORITY.json"
    target_path = raw_root / "TARGET_MATERIALIZATION_AUTHORITY.json"
    data_authority_path = raw_root / "DATA_AUTHORITY.json"
    try:
        validate_data_authority(data_authority_path)
    except Exception as exc:
        raise Goal5791EvaluationError("raw frozen data authority drifted") from exc
    pre = _audit_preexecution(_read_json(pre_path))
    if pre["authority_records"]["data_authority"]["sha256"] \
            != _file_sha256(data_authority_path):
        raise Goal5791EvaluationError("preexecution/raw data authority mismatch")
    authority_manifest = _audit_authority_manifest(
        raw_root, preexecution=pre,
        preexecution_file_sha256=_file_sha256(pre_path),
    )
    runtime_budget_authority = _read_json(
        raw_root / "AUTHORITIES" / "runtime_budget_authority.json"
    )
    target_copy = _read_json(raw_root / "TARGET_BINDING.json")
    if target_copy != pre["target_materialization_binding"]:
        raise Goal5791EvaluationError("separate target-binding copy drifted")
    runtime_path = raw_root / "RUNTIME.json"
    runtime = _audit_runtime(
        _read_json(runtime_path),
        preexecution_file_sha256=_file_sha256(pre_path), preexecution=pre,
        runtime_budget_authority=runtime_budget_authority,
    )
    runtime_file_sha256 = _file_sha256(runtime_path)
    formal = _audit_formal_authority(
        _read_json(formal_path), preexecution_file_sha256=_file_sha256(pre_path),
        preexecution=pre, runtime_file_sha256=runtime_file_sha256,
        runtime=runtime,
    )
    formal_file_sha256 = _file_sha256(formal_path)
    resource_path = raw_root / "RESOURCE_ADMISSION.json"
    resource_admission = _audit_resource_admission(
        _read_json(resource_path), formal=formal,
        formal_authority_file_sha256=formal_file_sha256,
    )
    target_runtime_path = raw_root / "TARGET_RUNTIME_ADMISSION.json"
    target_runtime_admission = _audit_target_runtime_admission(
        _read_json(target_runtime_path), formal=formal,
        formal_authority_file_sha256=formal_file_sha256,
        preexecution=pre, runtime=runtime,
    )
    source_admission = _audit_source_admission(
        _read_json(raw_root / "SOURCE_ADMISSION.json"), runtime=runtime,
        runtime_file_sha256=runtime_file_sha256,
        target_binding=pre["target_materialization_binding"],
        control_file_copies={
            "runtime": {
                "file_sha256": runtime_file_sha256,
                "bytes": runtime_path.stat().st_size,
            },
            "preexecution_authority": {
                "file_sha256": _file_sha256(pre_path),
                "bytes": pre_path.stat().st_size,
            },
            "formal_authority": {
                "file_sha256": formal_file_sha256,
                "bytes": formal_path.stat().st_size,
            },
        },
    )
    data_admission = _audit_data_admission(
        _read_json(raw_root / "DATA_ADMISSION.json"), preexecution=pre,
    )
    for dataset_id in DATASET_IDS:
        if runtime["datasets"][dataset_id]["edge_path"] \
                != data_admission["datasets"][dataset_id]["resolved_path"]:
            raise Goal5791EvaluationError(
                f"runtime/data-admission path drifted: {dataset_id}"
            )
    target_authority = _audit_target_authority(
        _read_json(target_path), file_sha256=_file_sha256(target_path),
        target_binding=pre["target_materialization_binding"],
    )
    worker_dir = raw_root / "workers"
    expected_names = [
        f"worker_{index:04d}.json" for index in range(len(schedule()))
    ]
    paths = (
        sorted(worker_dir.iterdir(), key=lambda path: path.name)
        if worker_dir.is_dir() and not worker_dir.is_symlink()
        else []
    )
    if [path.name for path in paths] != expected_names or any(
        not path.is_file() or path.is_symlink() for path in paths
    ):
        raise Goal5791EvaluationError("raw worker set/cardinality drifted")
    workers = [_read_json(path) for path in paths]
    cache_root = raw_root / "worker_caches"
    expected_cache_names = [
        f"worker_{index:04d}" for index in range(len(schedule()))
    ]
    cache_paths = sorted(cache_root.iterdir(), key=lambda path: path.name)
    if [path.name for path in cache_paths] != expected_cache_names or any(
        not path.is_dir() or path.is_symlink() for path in cache_paths
    ):
        raise Goal5791EvaluationError(
            "raw worker-cache directory set/cardinality drifted"
        )
    return (
        workers, pre, formal, runtime, data_admission, source_admission,
        target_authority, {
        "preexecution_file_sha256": _file_sha256(pre_path),
        "formal_file_sha256": formal_file_sha256,
        "target_authority_file_sha256": _file_sha256(target_path),
        "authority_manifest_sha256": authority_manifest["manifest_sha256"],
        "runtime_file_sha256": runtime_file_sha256,
        "resource_admission_sha256": resource_admission["admission_sha256"],
        "resource_admission_file_sha256": _file_sha256(resource_path),
        "target_runtime_admission_sha256": target_runtime_admission[
            "admission_sha256"
        ],
        "target_runtime_admission_file_sha256": _file_sha256(
            target_runtime_path
        ),
        },
    )


def _bootstrap(values: list[float], seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    draws = sorted(
        statistics.median(rng.choices(values, k=len(values)))
        for _ in range(BOOTSTRAP_DRAWS)
    )
    return float(draws[BOOTSTRAP_CI_INDICES[0]]), float(draws[BOOTSTRAP_CI_INDICES[1]])


def _pair_ratio(
    off: Mapping[str, object], on: Mapping[str, object],
    off_summary: Mapping[str, object], on_summary: Mapping[str, object],
) -> float:
    same_fields = (
        "row_index", "row_id", "dataset_id", "lifecycle", "pair_index",
        "paper_algorithm", "mechanism_id", "input_sha256", "output_scalar_u64",
        "output_sha256", "oracle_output_scalar_u64", "oracle_output_sha256",
        "output_contract_sha256", "oracle_contract_sha256",
        "dataset_oracle_authority_sha256", "formal_contract_sha256",
        "schedule_sha256", "runtime_sha256", "runtime_file_sha256",
        "preexecution_authority_file_sha256",
        "preexecution_authority_sha256", "target_materialization_binding_sha256",
        "target_materialization_authority_file_sha256",
        "formal_authority_file_sha256", "formal_authority_sha256",
        "formal_identity_sha256", "runtime_budget_authority_sha256",
        "data_admission_sha256", "data_authority_file_sha256",
        "source_admission_sha256", "timer_contract",
        "timer_contract_sha256", "lifecycle_contract", "lifecycle_contract_sha256",
        "segment_count", "input_file_receipt", "llvmlite_version",
        "registered_endpoint_is_one_continuous_interval",
        "cold_registered_endpoint_includes_interphase_dispatch_and_cache_check",
    )
    for name in same_fields:
        if off.get(name) != on.get(name):
            raise Goal5791EvaluationError(f"paired OFF/ON fact drifted: {name}")
    if off.get("target_materialization_binding") != on.get("target_materialization_binding"):
        raise Goal5791EvaluationError("paired target binding drifted")
    off_segments = off.get("segment_evidence")
    on_segments = on.get("segment_evidence")
    if not isinstance(off_segments, list) or not isinstance(on_segments, list):
        raise Goal5791EvaluationError("paired segment evidence missing")
    for off_segment, on_segment in zip(off_segments, on_segments, strict=True):
        for name in (
            "segment_id", "descriptor", "segment_descriptor_sha256", "partition",
            "relation_count", "primitive_count", "query_count",
            "host_geometry_bytes", "scalar_sum", "output_sha256",
            "plan_input_binding",
            "traversal_semantic_binding",
        ):
            if off_segment[name] != on_segment[name]:
                raise Goal5791EvaluationError(f"paired segment fact drifted: {name}")
        off_plan = off_segment["fusion_ablation_plan"]
        on_plan = on_segment["fusion_ablation_plan"]
        if off_plan["shared_identity_sha256"] != on_plan["shared_identity_sha256"]:
            raise Goal5791EvaluationError("paired shared plan identity drifted")
        changed = {name for name in off_plan if off_plan[name] != on_plan[name]}
        if changed != VARIANT_PLAN_FIELDS:
            raise Goal5791EvaluationError(
                f"paired plan delta is not the five-field allowlist: {sorted(changed)!r}"
            )
        if off_segment["operation_evidence_receipt"]["successful_event_count"] != 7 \
                or on_segment["operation_evidence_receipt"]["successful_event_count"] != 2:
            raise Goal5791EvaluationError("paired 7-vs-2 operation delta drifted")
    if off_summary["cache_identity"] == on_summary["cache_identity"]:
        raise Goal5791EvaluationError("paired workers shared a CuPy cache")
    off_seconds = float(off["registered_complete_endpoint_seconds"])
    on_seconds = float(on["registered_complete_endpoint_seconds"])
    if off_seconds <= 0.0 or on_seconds <= 0.0:
        raise Goal5791EvaluationError("paired registered endpoint is nonpositive")
    return off_seconds / on_seconds


def _paper_outcome_summary(
    rows: list[dict[str, object]],
) -> dict[str, object]:
    paper_clear_ids = [
        str(row["row_id"])
        for row in rows
        if row.get("mechanism_performance_statement_eligible") is True
    ]
    trace_inconclusive_ids = [
        str(row["row_id"])
        for row in rows
        if row.get("classification") == "ci_clear_win"
        and row.get("mechanism_performance_statement_eligible") is not True
    ]
    paper_clear_count = len(paper_clear_ids)
    if paper_clear_count == 0:
        branch = "zero_clear_winning_rows"
    elif paper_clear_count == len(statistical_rows()):
        branch = "all_six_clear_winning_rows"
    else:
        branch = "mixed_one_through_five_clear_winning_rows"
    selection_payload = {
        "schema": "rtdl.goal5791.paper_outcome_consequence_selection.v1",
        "paper_clear_winning_row_count": paper_clear_count,
        "paper_clear_winning_row_ids": paper_clear_ids,
        "ci_clear_win_count": paper_clear_count + len(trace_inconclusive_ids),
        "ci_clear_win_trace_cost_inconclusive_count": (
            len(trace_inconclusive_ids)
        ),
        "ci_clear_win_trace_cost_inconclusive_row_ids": (
            trace_inconclusive_ids
        ),
        "paper_outcome_consequence_contract_sha256": digest(
            PAPER_OUTCOME_CONSEQUENCE_CONTRACT
        ),
        "paper_outcome_consequence_branch": branch,
        "paper_outcome_consequence": dict(
            PAPER_OUTCOME_CONSEQUENCE_CONTRACT[branch]
        ),
    }
    selection = {
        **selection_payload,
        "selection_sha256": digest(selection_payload),
    }
    return {
        "paper_clear_winning_row_count": paper_clear_count,
        "paper_clear_winning_row_ids": paper_clear_ids,
        "ci_clear_win_trace_cost_inconclusive_count": (
            len(trace_inconclusive_ids)
        ),
        "ci_clear_win_trace_cost_inconclusive_row_ids": (
            trace_inconclusive_ids
        ),
        "paper_outcome_consequence_selection": selection,
    }


def _registered_endpoint_nanoseconds(worker: Mapping[str, object]) -> int:
    sequence = worker["phase_sequence"]
    if not isinstance(sequence, list) or len(sequence) != 5:
        raise Goal5791EvaluationError("registered endpoint intervals drifted")
    if worker["lifecycle"] == COLD:
        return int(sequence[-1]["ended_ns"]) - int(sequence[0]["started_ns"])
    execute = sequence[3]
    if execute.get("phase") != "execute":
        raise Goal5791EvaluationError("registered execute interval drifted")
    return int(execute["ended_ns"]) - int(execute["started_ns"])


def _exact_integer_median(values: list[int]) -> Fraction:
    ordered = sorted(values)
    if not ordered:
        raise Goal5791EvaluationError("empty exact endpoint sample")
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return Fraction(ordered[midpoint], 1)
    return Fraction(ordered[midpoint - 1] + ordered[midpoint], 2)


def build_evaluation(raw_root: Path) -> dict[str, object]:
    (
        workers, preexecution, formal, runtime, data_admission,
        source_admission,
        target_authority, raw_hashes,
    ) = _read_raw(raw_root)
    frozen_schedule = schedule()
    cold_claim_boundary = _cold_claim_boundary()
    summaries: list[dict[str, object]] = []
    for worker, expected in zip(workers, frozen_schedule, strict=True):
        summaries.append(_audit_worker(
            worker, expected=expected, preexecution=preexecution,
            formal=formal, runtime=runtime, data_admission=data_admission,
            source_admission=source_admission,
            target_authority=target_authority,
            preexecution_file_sha256=raw_hashes["preexecution_file_sha256"],
            formal_file_sha256=raw_hashes["formal_file_sha256"],
            target_authority_file_sha256=raw_hashes["target_authority_file_sha256"],
            runtime_file_sha256=raw_hashes["runtime_file_sha256"],
        ))
    pids = [int(worker["parent_pid"]) for worker in workers]
    cache_ids = [str(summary["cache_identity"]) for summary in summaries]
    token_nonces = [
        str(segment["operation_execution_nonce"])
        for summary in summaries for segment in summary["segments"]
    ]
    if len(set(pids)) != len(workers):
        raise Goal5791EvaluationError("formal matrix reused a parent PID")
    if len(set(cache_ids)) != len(workers):
        raise Goal5791EvaluationError("formal matrix reused a worker cache")
    if len(set(token_nonces)) != len(token_nonces):
        raise Goal5791EvaluationError("formal matrix reused an execution token nonce")
    common_fields = (
        "formal_contract_sha256", "schedule_sha256", "runtime_sha256",
        "runtime_file_sha256",
        "preexecution_authority_file_sha256", "preexecution_authority_sha256",
        "target_materialization_binding_sha256",
        "target_materialization_authority_file_sha256",
        "formal_authority_file_sha256", "formal_authority_sha256",
        "formal_identity_sha256", "runtime_budget_authority_sha256",
        "data_admission_sha256", "data_authority_file_sha256",
        "source_admission_sha256",
        "llvmlite_version",
        "output_contract_sha256", "oracle_contract_sha256",
    )
    for name in common_fields:
        if len({worker[name] for worker in workers}) != 1:
            raise Goal5791EvaluationError(f"mixed formal cohort identity: {name}")
    grouped: dict[tuple[str, int], dict[str, tuple[dict[str, object], dict[str, object]]]] = {}
    for worker, summary in zip(workers, summaries, strict=True):
        key = (str(worker["row_id"]), int(worker["pair_index"]))
        pair = grouped.setdefault(key, {})
        variant = str(worker["variant"])
        if variant in pair:
            raise Goal5791EvaluationError("duplicate paired variant")
        pair[variant] = (worker, summary)
    result_rows: list[dict[str, object]] = []
    for row in statistical_rows():
        if row["bootstrap_seed"] != BOOTSTRAP_SEED_BASE + row["row_index"]:
            raise Goal5791EvaluationError("row bootstrap seed drifted")
        ratios: list[float] = []
        off_seconds_values: list[float] = []
        on_seconds_values: list[float] = []
        off_endpoint_ns_values: list[int] = []
        on_endpoint_ns_values: list[int] = []
        row_segment_counts: set[int] = set()
        pair_records: list[dict[str, object]] = []
        for pair_index in range(PAIR_COUNT):
            pair = grouped.get((str(row["row_id"]), pair_index))
            if pair is None or set(pair) != set(VARIANTS):
                raise Goal5791EvaluationError("incomplete row-local ABBA pair")
            off, off_summary = pair[FUSION_OFF]
            on, on_summary = pair[FUSION_ON]
            ratio = _pair_ratio(off, on, off_summary, on_summary)
            ratios.append(ratio)
            off_seconds_values.append(float(
                off["registered_complete_endpoint_seconds"]))
            on_seconds_values.append(float(
                on["registered_complete_endpoint_seconds"]))
            off_endpoint_ns_values.append(_registered_endpoint_nanoseconds(off))
            on_endpoint_ns_values.append(_registered_endpoint_nanoseconds(on))
            row_segment_counts.add(int(off["segment_count"]))
            row_segment_counts.add(int(on["segment_count"]))
            pair_records.append({
                "pair_index": pair_index,
                "fusion_off_worker_index": off["worker_index"],
                "fusion_on_worker_index": on["worker_index"],
                "fusion_off_seconds": off["registered_complete_endpoint_seconds"],
                "fusion_on_seconds": on["registered_complete_endpoint_seconds"],
                "fusion_off_over_fusion_on": ratio,
                "operation_delta_exact_7_vs_2_per_segment": True,
            })
        median = float(statistics.median(ratios))
        lower, upper = _bootstrap(ratios, int(row["bootstrap_seed"]))
        if len(row_segment_counts) != 1:
            raise Goal5791EvaluationError(
                "row segment count drifted across paired workers")
        row_segment_count = next(iter(row_segment_counts))
        off_seconds_median = float(statistics.median(off_seconds_values))
        on_seconds_median = float(statistics.median(on_seconds_values))
        absolute_median_difference_ns = abs(
            _exact_integer_median(off_endpoint_ns_values)
            - _exact_integer_median(on_endpoint_ns_values)
        )
        absolute_median_difference = float(
            absolute_median_difference_ns / 1_000_000_000
        )
        row_trace_bound_ns = int(
            TRACE_INSTRUMENTATION_CONTRACT[
                "five_extra_event_differential_bound_per_segment_ns"
            ]
        ) * row_segment_count
        row_trace_bound_seconds = row_trace_bound_ns / 1_000_000_000.0
        exact_trace_fraction = (
            Fraction(row_trace_bound_ns, 1) / absolute_median_difference_ns
            if absolute_median_difference_ns > 0 else None
        )
        trace_fraction = (
            float(exact_trace_fraction)
            if exact_trace_fraction is not None else None
        )
        trace_bound_small = (
            exact_trace_fraction is not None
            and exact_trace_fraction <= Fraction(
                str(TRACE_INSTRUMENTATION_CONTRACT[
                    "small_relative_max_fraction"
                ])
            )
        )
        mechanism_claim_eligible = lower > 1.0 and trace_bound_small
        mechanism_claim_classification = (
            "eligible_clear_win"
            if mechanism_claim_eligible
            else (
                "trace_cost_inconclusive"
                if lower > 1.0 and not trace_bound_small
                else "not_a_statistical_clear_win"
            )
        )
        if lower > 1.0:
            classification = "ci_clear_win"
        elif upper < 1.0:
            classification = "ci_clear_loss"
        else:
            classification = "ci_crosses_one__not_a_demonstrated_win"
        public_row = {name: value for name, value in row.items()
                      if name not in {"lifecycle", "row_id"}}
        result_rows.append({
            **public_row,
            "row_id_internal_schedule_id": row["row_id"],
            "row_id": result_row_id(
                str(row["dataset_id"]), str(row["lifecycle"])),
            "lifecycle_internal_schedule_id": row["lifecycle"],
            "lifecycle": result_lifecycle_label(str(row["lifecycle"])),
            "pair_count": PAIR_COUNT,
            "pairs": pair_records,
            "paired_fusion_off_over_fusion_on_ratios": ratios,
            "paired_ratio_median": median,
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "bootstrap_seed": int(row["bootstrap_seed"]),
            "bootstrap_ci_indices": list(BOOTSTRAP_CI_INDICES),
            "bootstrap_ci95": [lower, upper],
            "greater_than_one_favors": FUSION_ON,
            "operation_delta_exact_all_pairs_and_segments": True,
            "demonstrated_clear_win": mechanism_claim_eligible,
            "classification": classification,
            "fusion_off_seconds_median": off_seconds_median,
            "fusion_on_seconds_median": on_seconds_median,
            "absolute_median_seconds_difference": absolute_median_difference,
            "trace_cost_diagnostic_authority_file_sha256": (
                TRACE_INSTRUMENTATION_CONTRACT[
                    "cpu_only_diagnostic_authority_file_sha256"
                ]
            ),
            "trace_cost_diagnostic_authority_sha256": (
                TRACE_INSTRUMENTATION_CONTRACT[
                    "cpu_only_diagnostic_authority_sha256"
                ]
            ),
            "per_event_record_cost_bound_ns": (
                TRACE_INSTRUMENTATION_CONTRACT[
                    "per_event_record_cost_bound_ns"
                ]
            ),
            "extra_trace_event_count_per_segment": (
                TRACE_INSTRUMENTATION_CONTRACT[
                    "extra_event_count_per_segment"
                ]
            ),
            "five_extra_event_differential_bound_per_segment_ns": (
                TRACE_INSTRUMENTATION_CONTRACT[
                    "five_extra_event_differential_bound_per_segment_ns"
                ]
            ),
            "exact_row_segment_count": row_segment_count,
            "row_total_trace_differential_bound_ns": row_trace_bound_ns,
            "row_total_trace_differential_bound_seconds": (
                row_trace_bound_seconds
            ),
            "trace_differential_fraction_of_absolute_median_seconds_difference": (
                trace_fraction
            ),
            "trace_cost_bound_small_relative_to_observed_difference": (
                trace_bound_small
            ),
            "trace_small_relative_max_fraction": (
                TRACE_INSTRUMENTATION_CONTRACT[
                    "small_relative_max_fraction"
                ]
            ),
            "diagnostic_may_change_row_statistic_ci_threshold_or_verdict": False,
            "statistical_classification_unchanged_by_trace_diagnostic": True,
            "mechanism_performance_statement_eligible": (
                mechanism_claim_eligible
            ),
            "mechanism_performance_statement_classification": (
                mechanism_claim_classification
            ),
            "estimand_includes_evidence_overhead": True,
            "pure_device_kernel_timing_claimed": False,
            "independent_comparison_row": True,
        })
    classifications = [str(row["classification"]) for row in result_rows]
    paper_outcome = _paper_outcome_summary(result_rows)
    payload = {
        "schema": "rtdl.goal5791.formal_primary_evaluation.v1",
        "goal": GOAL,
        "status": "PASS__COMPLETE_FAIL_CLOSED_FORMAL_EVALUATION",
        "formal_contract_sha256": contract_sha256(),
        "schedule_sha256": schedule_sha256(),
        "preexecution_authority_file_sha256": raw_hashes["preexecution_file_sha256"],
        "target_materialization_binding_sha256": preexecution["target_materialization_binding"]["binding_sha256"],
        "target_materialization_authority_file_sha256": raw_hashes["target_authority_file_sha256"],
        "formal_authority_file_sha256": raw_hashes["formal_file_sha256"],
        "runtime_sha256": runtime["runtime_sha256"],
        "runtime_file_sha256": raw_hashes["runtime_file_sha256"],
        "data_admission_sha256": data_admission["admission_sha256"],
        "source_admission_sha256": source_admission["admission_sha256"],
        "resource_admission_sha256": raw_hashes[
            "resource_admission_sha256"
        ],
        "resource_admission_file_sha256": raw_hashes[
            "resource_admission_file_sha256"
        ],
        "target_runtime_admission_sha256": raw_hashes[
            "target_runtime_admission_sha256"
        ],
        "target_runtime_admission_file_sha256": raw_hashes[
            "target_runtime_admission_file_sha256"
        ],
        "raw_authority_manifest_sha256": raw_hashes["authority_manifest_sha256"],
        "raw_worker_set_sha256": digest([worker["worker_sha256"] for worker in workers]),
        "worker_count": len(workers),
        "unique_parent_pid_count": len(set(pids)),
        "unique_worker_cache_count": len(set(cache_ids)),
        "unique_execution_token_count": len(set(token_nonces)),
        "source_rehash_receipt_worker_count": len(workers),
        "source_exact_path_set_verified": True,
        "source_admission_policy_verified": True,
        "cache_receipts_preserved": CACHE_POLICY["cache_receipts_preserved"],
        "cache_payloads_non_authoritative": not CACHE_POLICY[
            "cache_payloads_are_authoritative_evidence"
        ],
        "cache_payloads_must_be_removed_before_final_cohort_publication": (
            CACHE_POLICY[
                "successful_cohort_cache_payloads_removed_after_validation_before_publication"
            ]
        ),
        "failed_terminal_staging_may_preserve_cache_payloads": CACHE_POLICY[
            "failed_terminal_staging_may_preserve_cache_payloads"
        ],
        "successful_cohort_empty_cache_directory_shells_preserved_for_offline_recount": (
            CACHE_POLICY[
                "successful_cohort_empty_cache_directory_shells_preserved_for_offline_recount"
            ]
        ),
        "successful_cohort_empty_cache_directory_shell_count": CACHE_POLICY[
            "successful_cohort_empty_cache_directory_shell_count"
        ],
        "empty_cache_directory_shells_are_authoritative_evidence": CACHE_POLICY[
            "empty_cache_directory_shells_are_authoritative_evidence"
        ],
        "exact_output_worker_count": len(workers),
        "behavioral_true_optix_worker_count": len(workers),
        "independent_row_count": len(result_rows),
        "rows": result_rows,
        "result_lifecycle_labels": {
            lifecycle: result_lifecycle_label(lifecycle)
            for lifecycle in LIFECYCLES
        },
        "trace_cost_diagnostic_authority": {
            "file_sha256": TRACE_INSTRUMENTATION_CONTRACT[
                "cpu_only_diagnostic_authority_file_sha256"
            ],
            "diagnostic_sha256": TRACE_INSTRUMENTATION_CONTRACT[
                "cpu_only_diagnostic_authority_sha256"
            ],
            "per_event_record_cost_bound_ns": TRACE_INSTRUMENTATION_CONTRACT[
                "per_event_record_cost_bound_ns"
            ],
            "five_extra_event_differential_bound_per_segment_ns": (
                TRACE_INSTRUMENTATION_CONTRACT[
                    "five_extra_event_differential_bound_per_segment_ns"
                ]
            ),
            "required_before_stage_b_worker_zero": True,
        },
        "independent_recount_external_review_status": (
            INDEPENDENT_RECOUNT_REVIEW_STATUS
        ),
        "every_figure_caption_must_state_includes_evidence_overhead": True,
        "ci_clear_win_count": classifications.count("ci_clear_win"),
        "ci_clear_loss_count": classifications.count("ci_clear_loss"),
        "ci_crossing_count": classifications.count("ci_crosses_one__not_a_demonstrated_win"),
        **paper_outcome,
        "all_six_rows_retained": len(result_rows) == 6,
        "cross_dataset_lifecycle_or_row_compensation_used": False,
        "operation_delta_exact_all_workers": True,
        "same_source_target_and_optix_producer_all_workers": True,
        **cold_claim_boundary,
        "operating_system_page_cache_controlled_or_dropped": CACHE_POLICY[
            "operating_system_page_cache_controlled_or_dropped"
        ],
        "operating_system_page_cache_scope": CACHE_POLICY[
            "operating_system_page_cache_scope"
        ],
        "same_cohort_abba_symmetry_is_page_cache_mitigation_not_control": (
            CACHE_POLICY[
                "same_cohort_abba_symmetry_is_page_cache_mitigation_not_control"
            ]
        ),
        "same_host_root_race_excluded": SOURCE_ADMISSION_POLICY[
            "same_host_malicious_root_race_excluded"
        ],
        "same_host_root_race_tcb_boundary": SOURCE_TCB_BOUNDARY,
        "retry_resume_replacement_row_drop_relabel_used": False,
        "claim_boundary": (
            "row-local same-source RT-2A1 downstream-lowering ablation; "
            "a named mechanism-performance win requires CI lower > 1, exact "
            "7-vs-2 operation evidence, and the frozen trace-cost bound to be "
            "small relative to the observed absolute median-seconds difference; "
            "the estimand includes evidence overhead"
        ),
    }
    return {**payload, "evaluation_sha256": digest(payload)}


def evaluate(raw_root: Path, output: Path) -> Path:
    if output.exists():
        raise FileExistsError(output)
    payload = build_evaluation(raw_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(evaluate(args.raw_root, args.output))


if __name__ == "__main__":
    main()
