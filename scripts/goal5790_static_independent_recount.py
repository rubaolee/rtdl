#!/usr/bin/env python3
"""Independent raw recount for the static Goal5790 fusion cohort.

This module imports neither the controller nor the primary evaluator and has no
application execution import.  It reconstructs schedule, receipt chains,
identity pairing, and row statistics directly from raw JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
from typing import Mapping

from scripts.goal5790_static_formal_contract import (
    BOOTSTRAP_CI_INDICES,
    BOOTSTRAP_DRAWS,
    BOOTSTRAP_SEED_BASE,
    COLD,
    FUSION_OFF,
    FUSION_ON,
    MECHANISM_ID,
    OPERATION_EVIDENCE_TCB,
    OUTPUT_CONTRACT_SHA256,
    PAIR_COUNT,
    PHYSICAL_ENCODING_SHA256,
    SEMANTIC_REQUEST_SHA256,
    SHARED_FREEZE_CONTENT_SHA256,
    SHARED_FREEZE_FILE_SHA256,
    VARIANTS,
    contract_document,
    contract_sha256,
    expected_operation_contract,
    lifecycle_contract,
    schedule,
    statistical_rows,
    timer_contract,
)


WORKER_SCHEMA = "rtdl.goal5790.synthetic_or_future_formal_worker.v2"
WORKER_FIELDS = {
    "schema", "goal", "synthetic_contract_test_only", "formal_worker",
    "worker_index", "row_id", "dataset_id", "lifecycle", "pair_index",
    "order_ordinal", "variant", "mechanism_id", "parent_pid",
    "registered_complete_endpoint_seconds", "phase_accounting", "input_sha256",
    "output_sha256", "oracle_output_sha256", "oracle_contract_sha256",
    "semantic_request_sha256",
    "physical_encoding_sha256", "shared_contract_freeze_file_sha256",
    "shared_contract_freeze_content_sha256", "execution_source_archive_sha256",
    "execution_source_tree_sha256", "native_library_sha256",
    "timer_contract", "timer_contract_sha256",
    "lifecycle_contract", "lifecycle_contract_sha256",
    "output_contract_sha256", "output_scalar_u64", "oracle_output_scalar_u64",
    "target_materialization_authority", "segment_evidence", "segment_count",
    "two_phase_execution_evidence_seal_enforced",
    "evidence_hashing_or_serialization_inside_registered_timer",
    "comparator_inside_registered_timer",
    "receipt_serialization_inside_registered_timer",
    "retry_resume_replacement_row_drop_relabel_used",
}
COMMON_FIELDS = (
    "semantic_request_sha256", "physical_encoding_sha256",
    "shared_contract_freeze_file_sha256", "shared_contract_freeze_content_sha256",
    "execution_source_archive_sha256", "execution_source_tree_sha256",
    "native_library_sha256",
)

TARGET_FIELDS = {
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
SEGMENT_FIELDS = {
    "segment_id", "partition", "relation_count", "primitive_count",
    "query_count", "scalar_sum", "output_sha256", "fusion_ablation_plan",
    "operation_evidence_receipt", "checked_u64_weighted_reduction",
    "traversal_receipt", "device_phase_terminal_state",
    "evidence_phase_terminal_state", "evidence_sealed_after_device_phase",
    "traversal_semantic_binding",
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
    "session_error", "incomplete_callsite_record_count", "incomplete_callsite_lines",
}
CLAIM_RULES = {
    "provider_name_alone_proves_traversal": False,
    "selected_template_alone_proves_traversal": False,
    "successful_optix_launch_required": True,
    "nonzero_traversable_binding_required": True,
    "program_bundle_binding_required": True,
    "output_digest_bound": True,
}
VARIANT_PLAN_FIELDS = {
    "variant", "lowering_node", "downstream_operation_recipe_sha256",
    "operation_requirements", "plan_sha256",
}
FROZEN_PLAN_IDENTITIES = {
    "shared_contract_file_sha256": SHARED_FREEZE_FILE_SHA256,
    "shared_contract_freeze_sha256": SHARED_FREEZE_CONTENT_SHA256,
    "semantic_request_sha256": SEMANTIC_REQUEST_SHA256,
    "physical_encoding_sha256": PHYSICAL_ENCODING_SHA256,
    "admitted_reference_plan_sha256": "8dc1c000146e6df31e77ad86f21ae799bb543aeda68de4054932222523409d8e",
    "executable_family_plan_sha256": "ddb4909e48ca37b5065e1db86b34ff9610bc9d9a915a76efb651bb692028faa3",
    "transformation_variant_contract_sha256": "425bb6cffe4edb121f8e1bf3e9a730405439e2af32507b3c8b0c8d6a6b613ff3",
    "physical_schema_sha256": "97e3e85f8ab60e612e922a156fe2ecd8349b94e51a34d6984d8ce75133070e73",
}
PROGRAM_BUNDLE = "v4_builtin_triangle_checked_reduction_composed"
FAMILY_ID = "v4_triangle_per_ray_optix_producer_plus_checked_u64_continuation.v1"
ALLOWLIST = "downstream_checked_u64_reducer_operation_identity_and_event_sequence"
LOWERING = {
    FUSION_ON: "checked_summary_kernel_then_one_summary_copy_sync",
    FUSION_OFF: "max_sum_materialize_product_sum_then_three_scalar_copy_sync",
}
REDUCTION_COUNTS = {FUSION_ON: (1, 1, 0, 0), FUSION_OFF: (0, 3, 3, 1)}
FUSION_ON_SOURCE_SHA256 = (
    "c2ff69bfbfd5739aa3b502466bedf4d28390025f819f5756c65fcaecd20a7e73"
)
FUSION_OFF_OPERATIONS = [
    "cp.max(weights)", "maximum_weight.item()",
    "cp.sum(weights,dtype=cp.uint64)", "weight_sum.item()",
    "values*weights", "cp.sum(weighted_product,dtype=cp.uint64)",
    "weighted_sum.item()",
]
U64_MAX = (1 << 64) - 1


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


def _sha(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def _bundle_id(name: str) -> int:
    value = 1469598103934665603
    for octet in name.encode("utf-8"):
        value ^= octet
        value = (value * 1099511628211) & U64_MAX
    return value


def _expected_downstream_recipe(
    variant: str, *, target_identity_sha256: str, cupy_version: str,
) -> dict[str, object]:
    implementation = (
        {
            "kind": "compiler_owned_rawkernel_recipe",
            "entry": "rtdl_v4_checked_u64_weighted_reduce",
            "source_sha256": FUSION_ON_SOURCE_SHA256,
            "options": ["-std=c++11"],
            "opaque_partner_kernel_binary_claimed": False,
        }
        if variant == FUSION_ON
        else {
            "kind": "trusted_cupy_operation_graph",
            "operations": list(FUSION_OFF_OPERATIONS),
            "opaque_partner_kernel_binary_claimed": False,
        }
    )
    return {
        "schema": "rtdl.v4.checked_u64_downstream_operation_identity.v1",
        "variant": variant,
        "target_identity_sha256": target_identity_sha256,
        "cupy_version": cupy_version,
        "implementation": implementation,
    }


def _behavioral_digest(
    receipt: object,
    expected_output_sha: str,
    expected_native_sha: str,
    query_count: int,
    semantic_binding: object,
) -> str:
    if not isinstance(receipt, Mapping):
        raise RuntimeError("independent recount: behavioral receipt is not an object")
    snapshot = receipt.get("native_snapshot")
    if not isinstance(snapshot, Mapping) or set(snapshot) != SNAPSHOT_FIELDS:
        raise RuntimeError("independent recount: native snapshot missing")
    try:
        successful = int(snapshot["successful_launch_count"])
        complete = int(snapshot["complete_context_launch_count"])
        unbound = int(snapshot.get("unbound_launch_count", successful - complete))
        zero_fields = sum(int(snapshot[key]) for key in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error",
        ))
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("independent recount: malformed native snapshot") from exc
    if not isinstance(semantic_binding, Mapping) or set(semantic_binding) != {
        "authority", "contract", "abi", "composed_ptx", "native",
        "device_column_count",
    }:
        raise RuntimeError("independent recount: semantic binding differs")
    bundle_id = _bundle_id(PROGRAM_BUNDLE)
    nonce = receipt.get("nonce")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if set(receipt) != TRAVERSAL_FIELDS \
            or receipt.get("schema") \
            != "rtdl.physical_execution.traversal_receipt.v1" \
            or receipt.get("provider_library") != "librtdl_optix" \
            or not isinstance(receipt.get("provider_library_path"), str) \
            or not receipt.get("provider_library_path") \
            or receipt.get("provider_library_sha256") != expected_native_sha \
            or receipt.get("route_identity") \
            != "v4_builtin_triangle_callback_ir:partner_resident_checked_count_v1" \
            or receipt.get("semantic_digest") != _canonical_digest(semantic_binding) \
            or semantic_binding.get("native") != expected_native_sha \
            or semantic_binding.get("device_column_count") is not True \
            or any(not _sha(semantic_binding.get(name))
                   for name in ("contract", "abi", "composed_ptx")) \
            or not isinstance(semantic_binding.get("authority"), str) \
            or len(str(semantic_binding.get("authority"))) < 16 \
            or not isinstance(nonce, Mapping) or set(nonce) != {"hi", "lo"} \
            or nonce.get("hi") != snapshot.get("nonce_hi") \
            or nonce.get("lo") != snapshot.get("nonce_lo") \
            or receipt.get("expected_program_bundles") != [PROGRAM_BUNDLE] \
            or receipt.get("expected_program_bundle_ids") != [bundle_id] \
            or receipt.get("expected_program_observed_at_receipt_edge") is not True \
            or receipt.get("claim_rules") != CLAIM_RULES \
            or receipt.get("physical_executor_classification") != "optix_traversal_observed" \
            or receipt.get("output_digest") != expected_output_sha \
            or successful <= 0 or successful != complete or unbound != 0 \
            or int(snapshot.get("attempted_launch_count", -1)) != successful \
            or zero_fields != 0 or not snapshot.get("first_traversable") \
            or not snapshot.get("last_traversable") \
            or int(snapshot.get("raygen_invocation_count", -1)) != query_count \
            or int(snapshot.get("context_bind_count", -1)) < successful \
            or int(snapshot.get("first_program_bundle_id", -1)) != bundle_id \
            or int(snapshot.get("last_program_bundle_id", -1)) != bundle_id \
            or int(snapshot.get("incomplete_callsite_record_count", -1)) != 0 \
            or not isinstance(snapshot.get("incomplete_callsite_lines"), list) \
            or len(snapshot.get("incomplete_callsite_lines", [])) != 32 \
            or any(int(item) != 0 for item in snapshot.get("incomplete_callsite_lines", [])) \
            or not _sha(claimed) \
            or claimed != _canonical_digest(unsigned):
        raise RuntimeError("independent recount: traversal not completely bound")
    return str(claimed)


def _audit_target(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != TARGET_FIELDS:
        raise RuntimeError("independent recount: target authority fields differ")
    if value.get("schema") != "rtdl.v4.target_materialization_authority.v2" \
            or value.get("shared_contract_freeze_sha256") \
            != SHARED_FREEZE_CONTENT_SHA256 \
            or value.get("provider_identity") != "optix" \
            or value.get("program_bundle_identity") != PROGRAM_BUNDLE \
            or value.get("native_library_sha256") != value.get("native_payload_sha256") \
            or value.get("fusion_on_downstream_operation_recipe_sha256") \
            == value.get("fusion_off_downstream_operation_recipe_sha256") \
            or value.get("actual_native_rehashed_from_preserved_payload") is not True \
            or value.get("actual_source_tree_recounted_from_preserved_archive") is not True \
            or value.get("cross_target_native_byte_reproducibility_claimed") is not False:
        raise RuntimeError("independent recount: target authority differs")
    target_identity = value.get("target_identity_sha256")
    cupy_version = value.get("cupy_version")
    if not _sha(target_identity) or not isinstance(cupy_version, str) \
            or not cupy_version or len(cupy_version) > 64:
        raise RuntimeError("independent recount: target recipe context differs")
    for variant, prefix in ((FUSION_ON, "fusion_on"),
                            (FUSION_OFF, "fusion_off")):
        expected = _expected_downstream_recipe(
            variant, target_identity_sha256=str(target_identity),
            cupy_version=cupy_version)
        if value.get(prefix + "_downstream_operation_recipe") != expected \
                or value.get(prefix + "_downstream_operation_recipe_sha256") \
                    != _canonical_digest(expected):
            raise RuntimeError(
                "independent recount: structured operation recipe differs")
    excluded = {
        "schema", "provider_identity", "program_bundle_identity",
        "callback_authority_nonce", "cupy_version",
        "fusion_on_downstream_operation_recipe",
        "fusion_off_downstream_operation_recipe",
        "materialization_nonce", "actual_native_rehashed_from_preserved_payload",
        "actual_source_tree_recounted_from_preserved_archive",
        "cross_target_native_byte_reproducibility_claimed", "receipt_sha256",
    }
    if any(not _sha(value[name]) for name in TARGET_FIELDS - excluded):
        raise RuntimeError("independent recount: malformed target identity")
    nonce = value.get("materialization_nonce")
    callback_nonce = value.get("callback_authority_nonce")
    unsigned = dict(value)
    receipt_sha = unsigned.pop("receipt_sha256", None)
    if not isinstance(nonce, str) or len(nonce) < 16 \
            or not isinstance(callback_nonce, str) or len(callback_nonce) < 16 \
            or not _sha(receipt_sha) \
            or receipt_sha != _canonical_digest(unsigned):
        raise RuntimeError("independent recount: target authority signature differs")
    return value


def _audit_plan(
    plan: object,
    *,
    worker: Mapping[str, object],
    target: Mapping[str, object],
    segment_input_sha: str,
    query_count: int,
) -> Mapping[str, object]:
    if not isinstance(plan, Mapping) or set(plan) != PLAN_FIELDS:
        raise RuntimeError("independent recount: plan fields differ")
    variant = str(worker["variant"])
    fixed_checks = (
        plan.get("schema") == "rtdl.v4.fusion_ablation_plan.v2",
        plan.get("mechanism_id") == MECHANISM_ID,
        plan.get("variant") == variant,
        plan.get("executable_family_id") == FAMILY_ID,
        plan.get("provider_identity") == "optix",
        plan.get("program_bundle_identity") == PROGRAM_BUNDLE,
        plan.get("same_semantic_ir_required") is True,
        plan.get("same_optix_producer_required") is True,
        plan.get("performance_or_timing_claimed") is False,
        plan.get("variant_selected_from_app_dataset_result_or_timing") is False,
        plan.get("executable") is False,
        plan.get("only_allowlisted_difference") == ALLOWLIST,
        plan.get("lowering_node") == LOWERING[variant],
    )
    if not all(fixed_checks):
        raise RuntimeError("independent recount: plan boundary differs")
    if any(plan.get(name) != expected
           for name, expected in FROZEN_PLAN_IDENTITIES.items()):
        raise RuntimeError("independent recount: frozen plan identity differs")
    bindings = {
        "execution_source_archive_sha256": "execution_source_archive_sha256",
        "execution_source_tree_sha256": "execution_source_tree_sha256",
        "callback_ir_sha256": "callback_ir_sha256",
        "callback_authority_nonce": "callback_authority_nonce",
        "contract_sha256": "contract_sha256",
        "abi_sha256": "abi_sha256",
        "native_library_sha256": "native_library_sha256",
        "composed_program_sha256": "composed_program_sha256",
        "cupy_version": "cupy_version",
        "fusion_on_downstream_operation_recipe":
            "fusion_on_downstream_operation_recipe",
        "fusion_off_downstream_operation_recipe":
            "fusion_off_downstream_operation_recipe",
        "fusion_on_downstream_operation_recipe_sha256":
            "fusion_on_downstream_operation_recipe_sha256",
        "fusion_off_downstream_operation_recipe_sha256":
            "fusion_off_downstream_operation_recipe_sha256",
        "target_identity_sha256": "target_identity_sha256",
        "target_materialization_receipt_sha256": "receipt_sha256",
        "materializer_source_sha256": "materializer_source_sha256",
        "source_manifest_sha256": "source_manifest_sha256",
        "materialization_evidence_archive_sha256": "evidence_archive_sha256",
        "materialization_nonce": "materialization_nonce",
    }
    if any(plan.get(left) != target.get(right) for left, right in bindings.items()):
        raise RuntimeError("independent recount: plan/target authority differs")
    chosen = target[
        "fusion_on_downstream_operation_recipe_sha256"
        if variant == FUSION_ON else "fusion_off_downstream_operation_recipe_sha256"
    ]
    for recipe_variant, prefix in ((FUSION_ON, "fusion_on"),
                                   (FUSION_OFF, "fusion_off")):
        expected_recipe = _expected_downstream_recipe(
            recipe_variant,
            target_identity_sha256=str(target["target_identity_sha256"]),
            cupy_version=str(target["cupy_version"]))
        if plan.get(prefix + "_downstream_operation_recipe") != expected_recipe \
                or plan.get(prefix + "_downstream_operation_recipe_sha256") \
                    != _canonical_digest(expected_recipe):
            raise RuntimeError("independent recount: plan recipe differs")
    if plan.get("downstream_operation_recipe_sha256") != chosen \
            or plan.get("input_sha256") != segment_input_sha \
            or plan.get("output_contract_sha256") != worker["output_contract_sha256"] \
            or plan.get("oracle_sha256") != worker["oracle_contract_sha256"] \
            or plan.get("timer_contract_sha256") != worker["timer_contract_sha256"] \
            or plan.get("lifecycle_contract_sha256") \
            != worker["lifecycle_contract_sha256"] \
            or plan.get("value_count") != query_count:
        raise RuntimeError("independent recount: plan dynamic binding differs")
    requirements = expected_operation_contract(
        variant, declared_value_count=query_count)["requirements"]
    if plan.get("operation_requirements") != requirements:
        raise RuntimeError("independent recount: plan requirements differ")
    unsigned = dict(plan)
    shared_sha = unsigned.pop("shared_identity_sha256", None)
    plan_sha = unsigned.pop("plan_sha256", None)
    if not _sha(shared_sha) or not _sha(plan_sha) \
            or plan_sha != _canonical_digest(unsigned):
        raise RuntimeError("independent recount: plan digest differs")
    shared_payload = dict(unsigned)
    for field in (VARIANT_PLAN_FIELDS - {"plan_sha256"}) | {
        "only_allowlisted_difference"
    }:
        shared_payload.pop(field, None)
    if shared_sha != _canonical_digest(shared_payload):
        raise RuntimeError("independent recount: shared plan digest differs")
    return plan


def _requirements_contract(
    variant: str, plan_sha: str, declared_value_count: int,
) -> dict[str, object]:
    body = {
        "schema": "rtdl.v4.operation_sequence_contract.v1",
        "plan_sha256": plan_sha,
        "mechanism_id": MECHANISM_ID,
        "variant": variant,
        "declared_value_count": declared_value_count,
        "requirements": expected_operation_contract(
            variant, declared_value_count=declared_value_count)["requirements"],
        "tcb_statement": OPERATION_EVIDENCE_TCB,
        "timing_or_duration_recorded": False,
        "hardware_introspection_claimed": False,
    }
    body["contract_sha256"] = _canonical_digest(body)
    return body


def _audit_operation_receipt(
    receipt: object,
    *,
    plan: Mapping[str, object],
    traversal_sha: str,
    expected_output_sha: str,
) -> None:
    fields = {
        "schema", "contract_sha256", "plan_sha256", "mechanism_id", "variant",
        "execution_nonce", "value_count", "output_sha256",
        "traversal_receipt_sha256", "events", "event_chain_sha256",
        "successful_event_count", "event_evidence_tcb",
        "hardware_introspection_claimed", "opaque_partner_kernel_count_claimed",
        "timing_or_duration_recorded", "receipt_sha256",
    }
    if not isinstance(receipt, Mapping) or set(receipt) != fields:
        raise RuntimeError("independent recount: operation receipt fields differ")
    variant = str(plan["variant"])
    plan_sha = str(plan["plan_sha256"])
    declared_value_count = plan.get("value_count")
    if not isinstance(declared_value_count, int) \
            or isinstance(declared_value_count, bool) \
            or declared_value_count <= 0:
        raise RuntimeError("independent recount: worker value count differs")
    contract = _requirements_contract(variant, plan_sha, declared_value_count)
    if receipt.get("schema") != "rtdl.v4.operation_evidence_receipt.v1" \
            or receipt.get("contract_sha256") != contract["contract_sha256"] \
            or receipt.get("plan_sha256") != plan_sha \
            or receipt.get("mechanism_id") != MECHANISM_ID \
            or receipt.get("variant") != variant \
            or receipt.get("output_sha256") != expected_output_sha \
            or receipt.get("traversal_receipt_sha256") != traversal_sha \
            or receipt.get("event_evidence_tcb") != OPERATION_EVIDENCE_TCB \
            or receipt.get("hardware_introspection_claimed") is not False \
            or receipt.get("opaque_partner_kernel_count_claimed") is not False \
            or receipt.get("timing_or_duration_recorded") is not False:
        raise RuntimeError("independent recount: operation receipt binding differs")
    nonce = receipt.get("execution_nonce")
    count = receipt.get("value_count")
    if not isinstance(nonce, str) or len(nonce) < 16 \
            or not isinstance(count, int) or isinstance(count, bool) \
            or count != declared_value_count:
        raise RuntimeError("independent recount: operation nonce/count differs")
    requirements = contract["requirements"]
    events = receipt.get("events")
    if not isinstance(events, list) or len(events) != len(requirements) \
            or receipt.get("successful_event_count") != len(events):
        raise RuntimeError("independent recount: operation event cardinality differs")
    previous = str(contract["contract_sha256"])
    for ordinal in range(len(requirements)):
        requirement = requirements[ordinal]
        event = events[ordinal]
        units = int(requirement["units_per_value"]) * count + int(
            requirement["fixed_units"]
        )
        bytes_observed = int(requirement["bytes_per_unit"]) * units + int(
            requirement["fixed_bytes"]
        )
        expected = {
            "schema": "rtdl.v4.operation_evidence_event.v1",
            "sequence": ordinal,
            "operation_id": requirement["operation_id"],
            "kind": requirement["kind"],
            "accounted_units": units,
            "accounted_bytes": bytes_observed,
            "previous_event_sha256": previous,
            "recorded_after_callable_success": True,
        }
        expected["event_sha256"] = _canonical_digest(expected)
        if not isinstance(event, Mapping) or dict(event) != expected:
            raise RuntimeError("independent recount: operation event differs")
        previous = str(expected["event_sha256"])
    if receipt.get("event_chain_sha256") != previous:
        raise RuntimeError("independent recount: event chain differs")
    unsigned = dict(receipt)
    receipt_sha = unsigned.pop("receipt_sha256")
    if receipt_sha != _canonical_digest(unsigned):
        raise RuntimeError("independent recount: operation receipt digest differs")


def _audit_reduction(
    value: object,
    *,
    variant: str,
    query_count: int,
    primitive_count: int,
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
    if not isinstance(value, Mapping) or set(value) != fields \
            or value.get("schema") \
            != "rtdl.v4.checked_u64_weighted_reduction.receipt.v1":
        raise RuntimeError("independent recount: reduction receipt fields differ")
    numbers = [value.get(name) for name in (
        "maximum_value", "maximum_weight", "weight_sum")]
    if any(not isinstance(item, int) or isinstance(item, bool)
           or item < 0 or item > U64_MAX for item in numbers):
        raise RuntimeError("independent recount: reduction U64 value differs")
    maximum_value, maximum_weight, weight_sum = map(int, numbers)
    counts = tuple(value.get(name) for name in (
        "device_kernel_launch_count", "host_synchronization_count",
        "logical_reduction_count", "device_materialization_count"))
    expected_observed = variant == FUSION_ON
    expected_provenance = (
        "device_observed" if expected_observed
        else "optix_producer_declared_primitive_bound")
    if value.get("value_count") != query_count \
            or value.get("value_upper_bound") != primitive_count \
            or maximum_value > primitive_count \
            or (maximum_weight and maximum_value > U64_MAX // maximum_weight) \
            or (weight_sum and primitive_count > U64_MAX // weight_sum) \
            or scalar_sum > primitive_count * weight_sum \
            or counts != REDUCTION_COUNTS[variant] \
            or value.get("operation_counts_event_derived") is not True \
            or value.get("maximum_value_is_device_observed") is not expected_observed \
            or value.get("maximum_value_provenance") != expected_provenance \
            or value.get("provisional_sum_trusted_only_after_bounds") is not True:
        raise RuntimeError("independent recount: reduction binding differs")


def _audit_segments(
    worker: Mapping[str, object], target: Mapping[str, object]
) -> None:
    segments = worker.get("segment_evidence")
    if not isinstance(segments, list) or not segments \
            or worker.get("segment_count") != len(segments):
        raise RuntimeError("independent recount: segment cardinality differs")
    scalar_total = 0
    for ordinal, segment in enumerate(segments):
        if not isinstance(segment, Mapping) or set(segment) != SEGMENT_FIELDS \
                or segment.get("segment_id") != ordinal:
            raise RuntimeError("independent recount: segment order/fields differ")
        if segment.get("device_phase_terminal_state") != "device_complete_unsealed" \
                or segment.get("evidence_phase_terminal_state") != "sealed" \
                or segment.get("evidence_sealed_after_device_phase") is not True:
            raise RuntimeError("independent recount: two-phase evidence differs")
        extents = [segment.get(name) for name in (
            "relation_count", "primitive_count", "query_count", "scalar_sum")]
        if any(not isinstance(item, int) or isinstance(item, bool)
               or item <= 0 or item > U64_MAX for item in extents[:3]) \
                or not isinstance(extents[3], int) \
                or isinstance(extents[3], bool) \
                or not 0 <= int(extents[3]) <= U64_MAX:
            raise RuntimeError("independent recount: segment extent differs")
        relation_count, primitive_count, query_count, scalar_sum = map(int, extents)
        if scalar_total > U64_MAX - scalar_sum:
            raise RuntimeError("independent recount: segment aggregate overflow")
        scalar_total += scalar_sum
        segment_output_sha = _canonical_digest(scalar_sum)
        if segment.get("output_sha256") != segment_output_sha:
            raise RuntimeError("independent recount: segment output digest differs")
        segment_input_sha = _canonical_digest({
            "global_input_sha256": worker["input_sha256"],
            "segment_id": ordinal,
            "partition": segment["partition"],
            "relation_count": relation_count,
            "primitive_count": primitive_count,
            "query_count": query_count,
        })
        plan = _audit_plan(
            segment.get("fusion_ablation_plan"), worker=worker, target=target,
            segment_input_sha=segment_input_sha, query_count=query_count)
        semantic_binding = segment.get("traversal_semantic_binding")
        if not isinstance(semantic_binding, Mapping) \
                or semantic_binding.get("authority") \
                != target["callback_authority_nonce"] \
                or semantic_binding.get("contract") != target["contract_sha256"] \
                or semantic_binding.get("abi") != target["abi_sha256"] \
                or semantic_binding.get("native") != target["native_library_sha256"] \
                or semantic_binding.get("composed_ptx") \
                != target["composed_program_sha256"]:
            raise RuntimeError("independent recount: traversal target binding differs")
        traversal_sha = _behavioral_digest(
            segment.get("traversal_receipt"), segment_output_sha,
            str(target["native_library_sha256"]), query_count, semantic_binding)
        _audit_operation_receipt(
            segment.get("operation_evidence_receipt"), plan=plan,
            traversal_sha=traversal_sha, expected_output_sha=segment_output_sha)
        _audit_reduction(
            segment.get("checked_u64_weighted_reduction"),
            variant=str(worker["variant"]), query_count=query_count,
            primitive_count=primitive_count, scalar_sum=scalar_sum)
    if scalar_total != worker.get("output_scalar_u64") \
            or _canonical_digest(scalar_total) != worker.get("output_sha256"):
        raise RuntimeError("independent recount: segmented scalar sum differs")


def _audit_worker(worker: dict[str, object]) -> None:
    if set(worker) != WORKER_FIELDS or worker.get("schema") != WORKER_SCHEMA \
            or worker.get("goal") != 5790:
        raise RuntimeError("independent recount: worker schema differs")
    required_bools = {
        "synthetic_contract_test_only": True,
        "formal_worker": False,
        "comparator_inside_registered_timer": False,
        "receipt_serialization_inside_registered_timer": False,
        "retry_resume_replacement_row_drop_relabel_used": False,
        "two_phase_execution_evidence_seal_enforced": True,
        "evidence_hashing_or_serialization_inside_registered_timer": False,
    }
    if any(worker.get(key) is not value for key, value in required_bools.items()):
        raise RuntimeError("independent recount: worker boundary differs")
    if worker.get("mechanism_id") != MECHANISM_ID or worker.get("variant") not in VARIANTS:
        raise RuntimeError("independent recount: mechanism or variant differs")
    pid = worker.get("parent_pid")
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        raise RuntimeError("independent recount: PID differs")
    for key in (
        "input_sha256", "output_sha256", "oracle_output_sha256",
        "oracle_contract_sha256", *COMMON_FIELDS,
        "timer_contract_sha256", "lifecycle_contract_sha256",
        "output_contract_sha256",
    ):
        if not _sha(worker.get(key)):
            raise RuntimeError("independent recount: malformed identity " + key)
    if worker["semantic_request_sha256"] != SEMANTIC_REQUEST_SHA256 \
            or worker["physical_encoding_sha256"] != PHYSICAL_ENCODING_SHA256 \
            or worker["shared_contract_freeze_file_sha256"] != SHARED_FREEZE_FILE_SHA256 \
            or worker["shared_contract_freeze_content_sha256"] != SHARED_FREEZE_CONTENT_SHA256:
        raise RuntimeError("independent recount: shared freeze differs")
    if worker["output_contract_sha256"] != OUTPUT_CONTRACT_SHA256:
        raise RuntimeError("independent recount: output contract differs")
    for name in ("output_scalar_u64", "oracle_output_scalar_u64"):
        scalar = worker.get(name)
        if not isinstance(scalar, int) or isinstance(scalar, bool) \
                or scalar < 0 or scalar > U64_MAX:
            raise RuntimeError("independent recount: malformed output scalar")
    if worker["output_scalar_u64"] != worker["oracle_output_scalar_u64"] \
            or worker["output_sha256"] != worker["oracle_output_sha256"] \
            or worker["output_sha256"] != _canonical_digest(worker["output_scalar_u64"]):
        raise RuntimeError("independent recount: oracle output differs")
    target = _audit_target(worker.get("target_materialization_authority"))
    if worker["execution_source_archive_sha256"] \
            != target["execution_source_archive_sha256"] \
            or worker["execution_source_tree_sha256"] \
            != target["execution_source_tree_sha256"] \
            or worker["native_library_sha256"] != target["native_library_sha256"]:
        raise RuntimeError("independent recount: worker/target identity differs")
    phase = worker.get("phase_accounting")
    phase_fields = {
        "loading_seconds", "preparation_seconds", "execute_seconds",
        "close_seconds", "same_worker_mutually_exclusive_phases",
        "nested_phase_medians_summed",
    }
    if not isinstance(phase, Mapping) or set(phase) != phase_fields \
            or phase.get("same_worker_mutually_exclusive_phases") is not True \
            or phase.get("nested_phase_medians_summed") is not False:
        raise RuntimeError("independent recount: phase shape differs")
    phase_values = []
    for key in ("loading_seconds", "preparation_seconds", "execute_seconds", "close_seconds"):
        value = phase[key]
        if not isinstance(value, (int, float)) or isinstance(value, bool) \
                or not math.isfinite(float(value)) or float(value) < 0.0:
            raise RuntimeError("independent recount: invalid phase")
        phase_values.append(float(value))
    registered = worker.get("registered_complete_endpoint_seconds")
    if not isinstance(registered, (int, float)) or isinstance(registered, bool) \
            or not math.isfinite(float(registered)) or float(registered) <= 0.0:
        raise RuntimeError("independent recount: invalid registered seconds")
    expected = sum(phase_values) if worker["lifecycle"] == COLD else phase_values[2]
    if phase_values[2] <= 0.0 or not math.isclose(
        float(registered), expected, rel_tol=0.0, abs_tol=1e-12
    ):
        raise RuntimeError("independent recount: timer boundary differs")
    expected_timer = timer_contract(str(worker["lifecycle"]))
    expected_lifecycle = lifecycle_contract(str(worker["lifecycle"]))
    if worker.get("timer_contract") != expected_timer \
            or worker.get("timer_contract_sha256") != _canonical_digest(expected_timer) \
            or worker.get("lifecycle_contract") != expected_lifecycle \
            or worker.get("lifecycle_contract_sha256") \
            != _canonical_digest(expected_lifecycle):
        raise RuntimeError("independent recount: serialized timer/lifecycle differs")
    _audit_segments(worker, target)


def _bootstrap(values: list[float], row_index: int) -> list[float]:
    random_source = random.Random(BOOTSTRAP_SEED_BASE + row_index)
    medians = [
        float(statistics.median(random_source.choices(values, k=len(values))))
        for _ in range(BOOTSTRAP_DRAWS)
    ]
    medians.sort()
    return [
        medians[BOOTSTRAP_CI_INDICES[0]],
        medians[BOOTSTRAP_CI_INDICES[1]],
    ]


def build_recount(raw_root: Path) -> dict[str, object]:
    raw_contract = json.loads((raw_root / "FORMAL_CONTRACT.json").read_text(encoding="utf-8"))
    raw_schedule = json.loads((raw_root / "SCHEDULE.json").read_text(encoding="utf-8"))
    if raw_contract != contract_document() or raw_schedule != list(schedule()):
        raise RuntimeError("independent recount: frozen contract/schedule differs")
    worker_paths = sorted((raw_root / "workers").glob("worker_*.json"))
    workers = [json.loads(path.read_text(encoding="utf-8")) for path in worker_paths]
    if len(workers) != 96:
        raise RuntimeError("independent recount: expected exactly 96 workers")
    for worker in workers:
        _audit_worker(worker)
    if len({worker["parent_pid"] for worker in workers}) != 96:
        raise RuntimeError("independent recount: parent PID reuse")
    for identity in COMMON_FIELDS:
        if len({worker[identity] for worker in workers}) != 1:
            raise RuntimeError("independent recount: mixed identity " + identity)
    authorities = [worker["target_materialization_authority"] for worker in workers]
    if any(value != authorities[0] for value in authorities[1:]):
        raise RuntimeError("independent recount: mixed target authority")
    ordered = sorted(workers, key=lambda item: int(item["worker_index"]))
    observed = []
    for worker in ordered:
        observed.append({
            "worker_index": worker["worker_index"],
            "row_id": worker["row_id"],
            "dataset_id": worker["dataset_id"],
            "lifecycle": worker["lifecycle"],
            "pair_index": worker["pair_index"],
            "order_ordinal": worker["order_ordinal"],
            "variant": worker["variant"],
            "mechanism_id": worker["mechanism_id"],
        })
    if observed != list(schedule()):
        raise RuntimeError("independent recount: observed ABBA schedule differs")
    for description in statistical_rows():
        subset = [worker for worker in workers
                  if worker["row_id"] == description["row_id"]]
        for field in ("timer_contract_sha256", "lifecycle_contract_sha256"):
            if len({worker[field] for worker in subset}) != 1:
                raise RuntimeError("independent recount: row-local identity differs")

    pair_index: dict[tuple[str, int], dict[str, dict[str, object]]] = {}
    for worker in workers:
        key = (str(worker["row_id"]), int(worker["pair_index"]))
        variant = str(worker["variant"])
        pair = pair_index.setdefault(key, {})
        if variant in pair:
            raise RuntimeError("independent recount: duplicate variant in pair")
        pair[variant] = worker
    rows = []
    for description in statistical_rows():
        ratios = []
        for pair_number in range(PAIR_COUNT):
            pair = pair_index[(str(description["row_id"]), pair_number)]
            if set(pair) != set(VARIANTS):
                raise RuntimeError("independent recount: incomplete pair")
            off, on = pair[FUSION_OFF], pair[FUSION_ON]
            for field in (
                "input_sha256", "output_sha256", "oracle_output_sha256",
                "timer_contract_sha256", "lifecycle_contract_sha256",
                "timer_contract", "lifecycle_contract",
                "output_contract_sha256", "oracle_contract_sha256",
                "output_scalar_u64",
                "oracle_output_scalar_u64", "segment_count", *COMMON_FIELDS,
            ):
                if off[field] != on[field]:
                    raise RuntimeError("independent recount: paired identity differs " + field)
            if off["target_materialization_authority"] \
                    != on["target_materialization_authority"]:
                raise RuntimeError("independent recount: paired target differs")
            off_segments = off["segment_evidence"]
            on_segments = on["segment_evidence"]
            if not isinstance(off_segments, list) or not isinstance(on_segments, list):
                raise RuntimeError("independent recount: paired segments missing")
            for left, right in zip(off_segments, on_segments, strict=True):
                for field in (
                    "segment_id", "partition", "relation_count", "primitive_count",
                    "query_count", "scalar_sum", "output_sha256",
                ):
                    if left[field] != right[field]:
                        raise RuntimeError("independent recount: paired segment differs")
                left_plan = left["fusion_ablation_plan"]
                right_plan = right["fusion_ablation_plan"]
                if left_plan["shared_identity_sha256"] \
                        != right_plan["shared_identity_sha256"]:
                    raise RuntimeError("independent recount: paired shared plan differs")
                delta = {
                    field for field in left_plan
                    if left_plan[field] != right_plan[field]
                }
                if delta != VARIANT_PLAN_FIELDS:
                    raise RuntimeError("independent recount: paired plan delta differs")
            ratios.append(
                float(off["registered_complete_endpoint_seconds"])
                / float(on["registered_complete_endpoint_seconds"])
            )
        median = float(statistics.median(ratios))
        rows.append({
            **description,
            "pair_count": PAIR_COUNT,
            "paired_unfused_over_fused_ratios": ratios,
            "paired_ratio_median": median,
            "bootstrap_ci95": _bootstrap(ratios, int(description["row_index"])),
            "greater_than_one_favors": FUSION_ON,
            "median_favors_fusion": median > 1.0,
            "independent_comparison_row": True,
        })
    return {
        "schema": "rtdl.goal5790.static_independent_recount.v1",
        "formal_contract_sha256": contract_sha256(),
        "synthetic_contract_test_only": True,
        "target_performance_observation": False,
        "worker_count": 96,
        "unique_parent_pid_count": 96,
        "independent_row_count": 6,
        "rows": rows,
        "cross_dataset_or_lifecycle_compensation_used": False,
        "particle_rows": 0,
        "retry_resume_replacement_row_drop_relabel_used": False,
    }


def recount(raw_root: Path, output: Path) -> Path:
    if output.exists():
        raise FileExistsError(output)
    payload = build_recount(raw_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(recount(args.raw_root, args.output))


if __name__ == "__main__":
    main()
