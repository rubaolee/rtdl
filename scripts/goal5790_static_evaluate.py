#!/usr/bin/env python3
"""Primary evaluator for the static Goal5790 six-row fusion cohort.

The evaluator is runnable only on supplied raw JSON.  Goal5790's controller
cannot create target workers, so executions during this goal are synthetic
contract tests rather than target observations.
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
    LIFECYCLES,
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
    digest,
    expected_operation_contract,
    lifecycle_contract,
    schedule,
    statistical_rows,
    timer_contract,
)


WORKER_SCHEMA = "rtdl.goal5790.synthetic_or_future_formal_worker.v2"
OPERATION_CONTRACT_SCHEMA = "rtdl.v4.operation_sequence_contract.v1"
OPERATION_RECEIPT_SCHEMA = "rtdl.v4.operation_evidence_receipt.v1"
OPERATION_EVENT_SCHEMA = "rtdl.v4.operation_evidence_event.v1"

COMMON_IDENTITIES = (
    "semantic_request_sha256",
    "physical_encoding_sha256",
    "shared_contract_freeze_file_sha256",
    "shared_contract_freeze_content_sha256",
    "execution_source_archive_sha256",
    "execution_source_tree_sha256",
    "native_library_sha256",
)

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
SEGMENT_FIELDS = {
    "segment_id", "partition", "relation_count", "primitive_count",
    "query_count", "scalar_sum", "output_sha256", "fusion_ablation_plan",
    "operation_evidence_receipt", "checked_u64_weighted_reduction",
    "traversal_receipt", "device_phase_terminal_state",
    "evidence_phase_terminal_state", "evidence_sealed_after_device_phase",
    "traversal_semantic_binding",
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
PROGRAM_BUNDLE = "v4_builtin_triangle_checked_reduction_composed"
FAMILY_ID = "v4_triangle_per_ray_optix_producer_plus_checked_u64_continuation.v1"
ALLOWLIST = "downstream_checked_u64_reducer_operation_identity_and_event_sequence"
LOWERING_NODES = {
    FUSION_ON: "checked_summary_kernel_then_one_summary_copy_sync",
    FUSION_OFF: "max_sum_materialize_product_sum_then_three_scalar_copy_sync",
}
REDUCTION_COUNTS = {
    FUSION_ON: (1, 1, 0, 0),
    FUSION_OFF: (0, 3, 3, 1),
}
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
FROZEN_PLAN_IDENTITIES = {
    "shared_contract_file_sha256": SHARED_FREEZE_FILE_SHA256,
    "shared_contract_freeze_sha256": SHARED_FREEZE_CONTENT_SHA256,
    "semantic_request_sha256": SEMANTIC_REQUEST_SHA256,
    "physical_encoding_sha256": PHYSICAL_ENCODING_SHA256,
    "admitted_reference_plan_sha256": (
        "8dc1c000146e6df31e77ad86f21ae799bb543aeda68de4054932222523409d8e"),
    "executable_family_plan_sha256": (
        "ddb4909e48ca37b5065e1db86b34ff9610bc9d9a915a76efb651bb692028faa3"),
    "transformation_variant_contract_sha256": (
        "425bb6cffe4edb121f8e1bf3e9a730405439e2af32507b3c8b0c8d6a6b613ff3"),
    "physical_schema_sha256": (
        "97e3e85f8ab60e612e922a156fe2ecd8349b94e51a34d6984d8ce75133070e73"),
}

WORKER_KEYS = {
    "schema",
    "goal",
    "synthetic_contract_test_only",
    "formal_worker",
    "worker_index",
    "row_id",
    "dataset_id",
    "lifecycle",
    "pair_index",
    "order_ordinal",
    "variant",
    "mechanism_id",
    "parent_pid",
    "registered_complete_endpoint_seconds",
    "phase_accounting",
    "input_sha256",
    "output_sha256",
    "oracle_output_sha256",
    "oracle_contract_sha256",
    "semantic_request_sha256",
    "physical_encoding_sha256",
    "shared_contract_freeze_file_sha256",
    "shared_contract_freeze_content_sha256",
    "execution_source_archive_sha256",
    "execution_source_tree_sha256",
    "native_library_sha256",
    "timer_contract_sha256",
    "timer_contract",
    "lifecycle_contract_sha256",
    "lifecycle_contract",
    "output_contract_sha256",
    "output_scalar_u64",
    "oracle_output_scalar_u64",
    "target_materialization_authority",
    "segment_evidence",
    "segment_count",
    "two_phase_execution_evidence_seal_enforced",
    "evidence_hashing_or_serialization_inside_registered_timer",
    "comparator_inside_registered_timer",
    "receipt_serialization_inside_registered_timer",
    "retry_resume_replacement_row_drop_relabel_used",
}


def _is_sha(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _program_bundle_id(name: str) -> int:
    value = 1469598103934665603
    for byte in name.encode("utf-8"):
        value ^= byte
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


def _read_workers(raw_root: Path) -> list[dict[str, object]]:
    if json.loads((raw_root / "FORMAL_CONTRACT.json").read_text(encoding="utf-8")) \
            != contract_document():
        raise RuntimeError("Goal5790 raw formal contract mismatch")
    if json.loads((raw_root / "SCHEDULE.json").read_text(encoding="utf-8")) \
            != list(schedule()):
        raise RuntimeError("Goal5790 raw schedule mismatch")
    paths = sorted((raw_root / "workers").glob("worker_*.json"))
    if len(paths) != len(schedule()):
        raise RuntimeError("Goal5790 raw worker cardinality mismatch")
    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


def _validate_behavioral_receipt(
    receipt: object,
    *,
    output_sha256: str,
    native_sha256: str,
    query_count: int,
    semantic_binding: object,
) -> str:
    if not isinstance(receipt, Mapping):
        raise RuntimeError("Goal5790 malformed behavioral receipt")
    try:
        snapshot = receipt["native_snapshot"]
        if not isinstance(snapshot, Mapping) or set(snapshot) != TRAVERSAL_SNAPSHOT_FIELDS:
            raise TypeError("native_snapshot")
        successful = int(snapshot["successful_launch_count"])
        complete = int(snapshot["complete_context_launch_count"])
        unbound = int(snapshot.get("unbound_launch_count", successful - complete))
        unsigned = dict(receipt)
        claimed = unsigned.pop("receipt_sha256", None)
        if not isinstance(semantic_binding, Mapping) or set(semantic_binding) != {
            "authority", "contract", "abi", "composed_ptx", "native",
            "device_column_count",
        }:
            raise TypeError("semantic_binding")
        bundle_id = _program_bundle_id(PROGRAM_BUNDLE)
        nonce = receipt.get("nonce")
        invalid = (
            set(receipt) != TRAVERSAL_RECEIPT_FIELDS
            or receipt.get("schema")
            != "rtdl.physical_execution.traversal_receipt.v1"
            or receipt.get("provider_library") != "librtdl_optix"
            or not isinstance(receipt.get("provider_library_path"), str)
            or not receipt.get("provider_library_path")
            or receipt.get("provider_library_sha256") != native_sha256
            or receipt.get("route_identity")
            != "v4_builtin_triangle_callback_ir:partner_resident_checked_count_v1"
            or receipt.get("semantic_digest") != digest(semantic_binding)
            or semantic_binding.get("native") != native_sha256
            or semantic_binding.get("device_column_count") is not True
            or any(not _is_sha(semantic_binding.get(name))
                   for name in ("contract", "abi", "composed_ptx"))
            or not isinstance(semantic_binding.get("authority"), str)
            or len(str(semantic_binding.get("authority"))) < 16
            or not isinstance(nonce, Mapping) or set(nonce) != {"hi", "lo"}
            or nonce.get("hi") != snapshot.get("nonce_hi")
            or nonce.get("lo") != snapshot.get("nonce_lo")
            or receipt.get("expected_program_bundles") != [PROGRAM_BUNDLE]
            or receipt.get("expected_program_bundle_ids") != [bundle_id]
            or receipt.get("expected_program_observed_at_receipt_edge") is not True
            or receipt.get("claim_rules") != TRAVERSAL_CLAIM_RULES
            or
            receipt["physical_executor_classification"]
            != "optix_traversal_observed"
            or receipt.get("output_digest") != output_sha256
            or successful <= 0
            or complete != successful
            or int(snapshot.get("attempted_launch_count", -1)) != successful
            or unbound != 0
            or int(snapshot["failed_launch_count"]) != 0
            or int(snapshot["incomplete_context_launch_count"]) != 0
            or int(snapshot["pending_context_at_finish"]) != 0
            or int(snapshot["session_error"]) != 0
            or not snapshot["first_traversable"]
            or not snapshot["last_traversable"]
            or int(snapshot.get("raygen_invocation_count", -1)) != query_count
            or int(snapshot.get("context_bind_count", -1)) < successful
            or int(snapshot.get("first_program_bundle_id", -1)) != bundle_id
            or int(snapshot.get("last_program_bundle_id", -1)) != bundle_id
            or int(snapshot.get("incomplete_callsite_record_count", -1)) != 0
            or not isinstance(snapshot.get("incomplete_callsite_lines"), list)
            or len(snapshot.get("incomplete_callsite_lines", [])) != 32
            or any(int(value) != 0
                   for value in snapshot.get("incomplete_callsite_lines", []))
            or not _is_sha(claimed)
            or claimed != digest(unsigned)
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("Goal5790 malformed behavioral receipt") from exc
    if invalid:
        raise RuntimeError("Goal5790 worker did not prove bound OptiX traversal")
    return str(receipt["receipt_sha256"])


def _validate_target_authority(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != TARGET_AUTHORITY_FIELDS:
        raise RuntimeError("Goal5790 target materialization authority shape mismatch")
    if (
        value.get("schema") != "rtdl.v4.target_materialization_authority.v2"
        or value.get("shared_contract_freeze_sha256")
        != SHARED_FREEZE_CONTENT_SHA256
        or value.get("provider_identity") != "optix"
        or value.get("program_bundle_identity") != PROGRAM_BUNDLE
        or value.get("native_library_sha256") != value.get("native_payload_sha256")
        or value.get("fusion_on_downstream_operation_recipe_sha256")
        == value.get("fusion_off_downstream_operation_recipe_sha256")
        or value.get("actual_native_rehashed_from_preserved_payload") is not True
        or value.get("actual_source_tree_recounted_from_preserved_archive") is not True
        or value.get("cross_target_native_byte_reproducibility_claimed") is not False
    ):
        raise RuntimeError("Goal5790 target materialization authority mismatch")
    target_identity = value.get("target_identity_sha256")
    cupy_version = value.get("cupy_version")
    if not _is_sha(target_identity) or not isinstance(cupy_version, str) \
            or not cupy_version or len(cupy_version) > 64:
        raise RuntimeError("Goal5790 target recipe context mismatch")
    for variant, prefix in ((FUSION_ON, "fusion_on"),
                            (FUSION_OFF, "fusion_off")):
        expected = _expected_downstream_recipe(
            variant, target_identity_sha256=str(target_identity),
            cupy_version=cupy_version)
        if value.get(prefix + "_downstream_operation_recipe") != expected \
                or value.get(prefix + "_downstream_operation_recipe_sha256") \
                    != digest(expected):
            raise RuntimeError("Goal5790 structured operation recipe mismatch")
    non_sha = {
        "schema", "provider_identity", "program_bundle_identity",
        "callback_authority_nonce", "cupy_version",
        "fusion_on_downstream_operation_recipe",
        "fusion_off_downstream_operation_recipe",
        "materialization_nonce", "actual_native_rehashed_from_preserved_payload",
        "actual_source_tree_recounted_from_preserved_archive",
        "cross_target_native_byte_reproducibility_claimed", "receipt_sha256",
    }
    if any(not _is_sha(value[name]) for name in TARGET_AUTHORITY_FIELDS - non_sha):
        raise RuntimeError("Goal5790 malformed target materialization identity")
    nonce = value.get("materialization_nonce")
    if not isinstance(nonce, str) or len(nonce) < 16:
        raise RuntimeError("Goal5790 target materialization nonce mismatch")
    callback_nonce = value.get("callback_authority_nonce")
    if not isinstance(callback_nonce, str) or len(callback_nonce) < 16:
        raise RuntimeError("Goal5790 callback authority nonce mismatch")
    unsigned = dict(value)
    claimed = unsigned.pop("receipt_sha256", None)
    if not _is_sha(claimed) or claimed != digest(unsigned):
        raise RuntimeError("Goal5790 target materialization receipt mismatch")
    return value


def _validate_plan(
    plan: object,
    *,
    worker: Mapping[str, object],
    target: Mapping[str, object],
    segment_input_sha256: str,
    query_count: int,
) -> Mapping[str, object]:
    if not isinstance(plan, Mapping) or set(plan) != PLAN_FIELDS:
        raise RuntimeError("Goal5790 FusionAblationPlan shape mismatch")
    variant = str(worker["variant"])
    if (
        plan.get("schema") != "rtdl.v4.fusion_ablation_plan.v2"
        or plan.get("mechanism_id") != MECHANISM_ID
        or plan.get("variant") != variant
        or plan.get("executable_family_id") != FAMILY_ID
        or plan.get("provider_identity") != "optix"
        or plan.get("program_bundle_identity") != PROGRAM_BUNDLE
        or plan.get("same_semantic_ir_required") is not True
        or plan.get("same_optix_producer_required") is not True
        or plan.get("performance_or_timing_claimed") is not False
        or plan.get("variant_selected_from_app_dataset_result_or_timing") is not False
        or plan.get("executable") is not False
        or plan.get("only_allowlisted_difference") != ALLOWLIST
        or plan.get("lowering_node") != LOWERING_NODES[variant]
    ):
        raise RuntimeError("Goal5790 FusionAblationPlan boundary mismatch")
    for name, expected in FROZEN_PLAN_IDENTITIES.items():
        if plan.get(name) != expected:
            raise RuntimeError("Goal5790 frozen plan identity mismatch: " + name)
    target_bindings = {
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
    for plan_name, target_name in target_bindings.items():
        if plan.get(plan_name) != target.get(target_name):
            raise RuntimeError("Goal5790 plan/target mismatch: " + plan_name)
    selected_recipe = target[
        "fusion_on_downstream_operation_recipe_sha256"
        if variant == FUSION_ON
        else "fusion_off_downstream_operation_recipe_sha256"
    ]
    for recipe_variant, prefix in ((FUSION_ON, "fusion_on"),
                                   (FUSION_OFF, "fusion_off")):
        expected_recipe = _expected_downstream_recipe(
            recipe_variant,
            target_identity_sha256=str(target["target_identity_sha256"]),
            cupy_version=str(target["cupy_version"]))
        if plan.get(prefix + "_downstream_operation_recipe") != expected_recipe \
                or plan.get(prefix + "_downstream_operation_recipe_sha256") \
                    != digest(expected_recipe):
            raise RuntimeError("Goal5790 plan operation recipe mismatch")
    if (
        plan.get("downstream_operation_recipe_sha256") != selected_recipe
        or plan.get("input_sha256") != segment_input_sha256
        or plan.get("output_contract_sha256") != worker["output_contract_sha256"]
        or plan.get("oracle_sha256") != worker["oracle_contract_sha256"]
        or plan.get("timer_contract_sha256") != worker["timer_contract_sha256"]
        or plan.get("lifecycle_contract_sha256")
        != worker["lifecycle_contract_sha256"]
        or plan.get("value_count") != query_count
    ):
        raise RuntimeError("Goal5790 FusionAblationPlan dynamic binding mismatch")
    requirements = expected_operation_contract(
        variant, declared_value_count=query_count)["requirements"]
    if plan.get("operation_requirements") != requirements:
        raise RuntimeError("Goal5790 FusionAblationPlan operation contract mismatch")
    variant_payload = dict(plan)
    shared_claim = variant_payload.pop("shared_identity_sha256", None)
    plan_claim = variant_payload.pop("plan_sha256", None)
    if not _is_sha(shared_claim) or not _is_sha(plan_claim) \
            or digest(variant_payload) != plan_claim:
        raise RuntimeError("Goal5790 FusionAblationPlan digest mismatch")
    common = dict(variant_payload)
    for name in (VARIANT_PLAN_FIELDS - {"plan_sha256"}) | {
        "only_allowlisted_difference"
    }:
        common.pop(name, None)
    if digest(common) != shared_claim:
        raise RuntimeError("Goal5790 FusionAblationPlan shared digest mismatch")
    return plan


def _operation_contract_payload(
    *, variant: str, plan_sha256: str, declared_value_count: int,
) -> dict[str, object]:
    contract = expected_operation_contract(
        variant, declared_value_count=declared_value_count)
    requirements = contract["requirements"]
    body = {
        "schema": OPERATION_CONTRACT_SCHEMA,
        "plan_sha256": plan_sha256,
        "mechanism_id": MECHANISM_ID,
        "variant": variant,
        "declared_value_count": declared_value_count,
        "requirements": requirements,
        "tcb_statement": OPERATION_EVIDENCE_TCB,
        "timing_or_duration_recorded": False,
        "hardware_introspection_claimed": False,
    }
    return {**body, "contract_sha256": digest(body)}


def _validate_operation_receipt(
    receipt: object,
    *,
    plan: Mapping[str, object],
    traversal_sha256: str,
    output_sha256: str,
) -> None:
    expected_keys = {
        "schema",
        "contract_sha256",
        "plan_sha256",
        "mechanism_id",
        "variant",
        "execution_nonce",
        "value_count",
        "output_sha256",
        "traversal_receipt_sha256",
        "events",
        "event_chain_sha256",
        "successful_event_count",
        "event_evidence_tcb",
        "hardware_introspection_claimed",
        "opaque_partner_kernel_count_claimed",
        "timing_or_duration_recorded",
        "receipt_sha256",
    }
    if not isinstance(receipt, Mapping) or set(receipt) != expected_keys:
        raise RuntimeError("Goal5790 operation receipt shape mismatch")
    variant = str(plan["variant"])
    plan_sha = str(plan["plan_sha256"])
    declared_value_count = plan["value_count"]
    if not isinstance(declared_value_count, int) \
            or isinstance(declared_value_count, bool) \
            or declared_value_count <= 0:
        raise RuntimeError("Goal5790 worker operation value count mismatch")
    contract = _operation_contract_payload(
        variant=variant,
        plan_sha256=plan_sha,
        declared_value_count=declared_value_count,
    )
    if (
        receipt["schema"] != OPERATION_RECEIPT_SCHEMA
        or receipt["contract_sha256"] != contract["contract_sha256"]
        or receipt["plan_sha256"] != plan_sha
        or receipt["mechanism_id"] != MECHANISM_ID
        or receipt["variant"] != variant
        or receipt["output_sha256"] != output_sha256
        or receipt["traversal_receipt_sha256"] != traversal_sha256
        or not isinstance(receipt["execution_nonce"], str)
        or len(receipt["execution_nonce"]) < 16
        or receipt["event_evidence_tcb"] != OPERATION_EVIDENCE_TCB
        or receipt["hardware_introspection_claimed"] is not False
        or receipt["opaque_partner_kernel_count_claimed"] is not False
        or receipt["timing_or_duration_recorded"] is not False
    ):
        raise RuntimeError("Goal5790 operation receipt identity mismatch")
    value_count = receipt["value_count"]
    if not isinstance(value_count, int) or isinstance(value_count, bool) \
            or value_count != declared_value_count:
        raise RuntimeError("Goal5790 operation receipt value count mismatch")
    requirements = contract["requirements"]
    events = receipt["events"]
    if not isinstance(events, list) or len(events) != len(requirements) \
            or receipt["successful_event_count"] != len(events):
        raise RuntimeError("Goal5790 operation event count mismatch")
    previous = str(contract["contract_sha256"])
    for index, (event, requirement) in enumerate(zip(events, requirements, strict=True)):
        units = (
            int(requirement["units_per_value"]) * value_count
            + int(requirement["fixed_units"])
        )
        byte_count = int(requirement["bytes_per_unit"]) * units + int(
            requirement["fixed_bytes"]
        )
        expected = {
            "schema": OPERATION_EVENT_SCHEMA,
            "sequence": index,
            "operation_id": requirement["operation_id"],
            "kind": requirement["kind"],
            "accounted_units": units,
            "accounted_bytes": byte_count,
            "previous_event_sha256": previous,
            "recorded_after_callable_success": True,
        }
        if not isinstance(event, Mapping) or set(event) != set(expected) | {"event_sha256"}:
            raise RuntimeError("Goal5790 operation event shape mismatch")
        event_sha = digest(expected)
        if dict(event) != {**expected, "event_sha256": event_sha}:
            raise RuntimeError("Goal5790 operation event content/order mismatch")
        previous = event_sha
    if receipt["event_chain_sha256"] != previous:
        raise RuntimeError("Goal5790 operation event chain mismatch")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256")
    if claimed != digest(unsigned):
        raise RuntimeError("Goal5790 operation receipt digest mismatch")


def _validate_checked_reduction(
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
        "maximum_value_is_device_observed",
        "maximum_value_provenance",
        "provisional_sum_trusted_only_after_bounds",
    }
    if not isinstance(value, Mapping) or set(value) != fields \
            or value.get("schema") \
            != "rtdl.v4.checked_u64_weighted_reduction.receipt.v1":
        raise RuntimeError("Goal5790 checked-U64 receipt shape mismatch")
    u64_names = ("maximum_value", "maximum_weight", "weight_sum")
    if any(
        not isinstance(value[name], int) or isinstance(value[name], bool)
        or not 0 <= int(value[name]) <= U64_MAX
        for name in u64_names
    ):
        raise RuntimeError("Goal5790 checked-U64 bounds malformed")
    maximum_value = int(value["maximum_value"])
    maximum_weight = int(value["maximum_weight"])
    weight_sum = int(value["weight_sum"])
    counts = (
        value.get("device_kernel_launch_count"),
        value.get("host_synchronization_count"),
        value.get("logical_reduction_count"),
        value.get("device_materialization_count"),
    )
    if (
        value.get("value_count") != query_count
        or value.get("value_upper_bound") != primitive_count
        or maximum_value > primitive_count
        or (maximum_weight and maximum_value > U64_MAX // maximum_weight)
        or (weight_sum and primitive_count > U64_MAX // weight_sum)
        or scalar_sum > primitive_count * weight_sum
        or counts != REDUCTION_COUNTS[variant]
        or value.get("operation_counts_event_derived") is not True
        or value.get("maximum_value_is_device_observed")
        is not (variant == FUSION_ON)
        or value.get("maximum_value_provenance")
        != ("device_observed" if variant == FUSION_ON
            else "optix_producer_declared_primitive_bound")
        or value.get("provisional_sum_trusted_only_after_bounds") is not True
    ):
        raise RuntimeError("Goal5790 checked-U64 evidence mismatch")


def _validate_segments(
    worker: Mapping[str, object], target: Mapping[str, object]
) -> tuple[str, ...]:
    segments = worker.get("segment_evidence")
    if not isinstance(segments, list) or not segments \
            or worker.get("segment_count") != len(segments):
        raise RuntimeError("Goal5790 segment evidence cardinality mismatch")
    scalar_total = 0
    plan_ids: list[str] = []
    for index, segment in enumerate(segments):
        if not isinstance(segment, Mapping) or set(segment) != SEGMENT_FIELDS \
                or segment.get("segment_id") != index:
            raise RuntimeError("Goal5790 segment evidence order/shape mismatch")
        if segment.get("device_phase_terminal_state") != "device_complete_unsealed" \
                or segment.get("evidence_phase_terminal_state") != "sealed" \
                or segment.get("evidence_sealed_after_device_phase") is not True:
            raise RuntimeError("Goal5790 two-phase segment evidence mismatch")
        integers = {
            name: segment.get(name)
            for name in ("relation_count", "primitive_count", "query_count", "scalar_sum")
        }
        if any(
            not isinstance(value, int) or isinstance(value, bool)
            or value <= 0 or value > U64_MAX
            for name, value in integers.items() if name != "scalar_sum"
        ) or not isinstance(integers["scalar_sum"], int) \
                or isinstance(integers["scalar_sum"], bool) \
                or not 0 <= int(integers["scalar_sum"]) <= U64_MAX:
            raise RuntimeError("Goal5790 segment physical extent mismatch")
        relation_count = int(integers["relation_count"])
        primitive_count = int(integers["primitive_count"])
        query_count = int(integers["query_count"])
        scalar_sum = int(integers["scalar_sum"])
        if scalar_total > U64_MAX - scalar_sum:
            raise RuntimeError("Goal5790 segmented scalar overflow")
        scalar_total += scalar_sum
        segment_output_sha = digest(scalar_sum)
        if segment.get("output_sha256") != segment_output_sha:
            raise RuntimeError("Goal5790 segment output digest mismatch")
        segment_input_sha = digest({
            "global_input_sha256": worker["input_sha256"],
            "segment_id": index,
            "partition": segment["partition"],
            "relation_count": relation_count,
            "primitive_count": primitive_count,
            "query_count": query_count,
        })
        plan = _validate_plan(
            segment.get("fusion_ablation_plan"), worker=worker, target=target,
            segment_input_sha256=segment_input_sha, query_count=query_count)
        semantic_binding = segment.get("traversal_semantic_binding")
        if not isinstance(semantic_binding, Mapping) \
                or semantic_binding.get("authority") \
                != target["callback_authority_nonce"] \
                or semantic_binding.get("contract") != target["contract_sha256"] \
                or semantic_binding.get("abi") != target["abi_sha256"] \
                or semantic_binding.get("native") != target["native_library_sha256"] \
                or semantic_binding.get("composed_ptx") \
                != target["composed_program_sha256"]:
            raise RuntimeError("Goal5790 traversal semantic target binding mismatch")
        traversal_sha = _validate_behavioral_receipt(
            segment.get("traversal_receipt"), output_sha256=segment_output_sha,
            native_sha256=str(target["native_library_sha256"]),
            query_count=query_count, semantic_binding=semantic_binding)
        _validate_operation_receipt(
            segment.get("operation_evidence_receipt"), plan=plan,
            traversal_sha256=traversal_sha, output_sha256=segment_output_sha)
        _validate_checked_reduction(
            segment.get("checked_u64_weighted_reduction"),
            variant=str(worker["variant"]), query_count=query_count,
            primitive_count=primitive_count, scalar_sum=scalar_sum)
        plan_ids.append(str(plan["plan_sha256"]))
    if scalar_total != worker.get("output_scalar_u64") \
            or digest(scalar_total) != worker.get("output_sha256"):
        raise RuntimeError("Goal5790 segment scalar aggregation mismatch")
    return tuple(plan_ids)


def _validate_phase_accounting(worker: Mapping[str, object]) -> None:
    phase = worker.get("phase_accounting")
    keys = {
        "loading_seconds",
        "preparation_seconds",
        "execute_seconds",
        "close_seconds",
        "same_worker_mutually_exclusive_phases",
        "nested_phase_medians_summed",
    }
    if not isinstance(phase, Mapping) or set(phase) != keys or (
        phase["same_worker_mutually_exclusive_phases"] is not True
        or phase["nested_phase_medians_summed"] is not False
    ):
        raise RuntimeError("Goal5790 phase accounting shape mismatch")
    values = []
    for key in ("loading_seconds", "preparation_seconds", "execute_seconds", "close_seconds"):
        value = phase[key]
        if not isinstance(value, (int, float)) or isinstance(value, bool) \
                or not math.isfinite(float(value)) or float(value) < 0.0:
            raise RuntimeError("Goal5790 phase accounting value mismatch")
        values.append(float(value))
    if values[2] <= 0.0:
        raise RuntimeError("Goal5790 execute time must be positive")
    registered = float(worker["registered_complete_endpoint_seconds"])
    expected = sum(values) if worker["lifecycle"] == COLD else values[2]
    if not math.isclose(registered, expected, rel_tol=0.0, abs_tol=1e-12):
        raise RuntimeError("Goal5790 registered timer boundary mismatch")
    expected_timer = timer_contract(str(worker["lifecycle"]))
    expected_lifecycle = lifecycle_contract(str(worker["lifecycle"]))
    if worker.get("timer_contract") != expected_timer \
            or worker.get("timer_contract_sha256") != digest(expected_timer) \
            or worker.get("lifecycle_contract") != expected_lifecycle \
            or worker.get("lifecycle_contract_sha256") != digest(expected_lifecycle):
        raise RuntimeError("Goal5790 serialized timer/lifecycle contract mismatch")


def _validate_worker(worker: dict[str, object]) -> None:
    if set(worker) != WORKER_KEYS or worker.get("schema") != WORKER_SCHEMA \
            or worker.get("goal") != 5790:
        raise RuntimeError("Goal5790 worker schema mismatch")
    if any(
        worker.get(key) is not expected
        for key, expected in (
            ("synthetic_contract_test_only", True),
            ("formal_worker", False),
            ("comparator_inside_registered_timer", False),
            ("receipt_serialization_inside_registered_timer", False),
            ("retry_resume_replacement_row_drop_relabel_used", False),
            ("two_phase_execution_evidence_seal_enforced", True),
            ("evidence_hashing_or_serialization_inside_registered_timer", False),
        )
    ):
        raise RuntimeError("Goal5790 worker claim boundary mismatch")
    if worker["mechanism_id"] != MECHANISM_ID or worker["variant"] not in VARIANTS \
            or worker["lifecycle"] not in LIFECYCLES:
        raise RuntimeError("Goal5790 worker mechanism/variant/lifecycle mismatch")
    if not isinstance(worker["parent_pid"], int) or isinstance(worker["parent_pid"], bool) \
            or worker["parent_pid"] <= 0:
        raise RuntimeError("Goal5790 parent PID mismatch")
    seconds = worker["registered_complete_endpoint_seconds"]
    if not isinstance(seconds, (int, float)) or isinstance(seconds, bool) \
            or not math.isfinite(float(seconds)) or float(seconds) <= 0.0:
        raise RuntimeError("Goal5790 registered seconds mismatch")
    for key in (
        "input_sha256",
        "output_sha256",
        "oracle_output_sha256",
        "oracle_contract_sha256",
        *COMMON_IDENTITIES,
        "timer_contract_sha256",
        "lifecycle_contract_sha256",
        "output_contract_sha256",
    ):
        if not _is_sha(worker[key]):
            raise RuntimeError(f"Goal5790 malformed identity: {key}")
    if worker["semantic_request_sha256"] != SEMANTIC_REQUEST_SHA256 \
            or worker["physical_encoding_sha256"] != PHYSICAL_ENCODING_SHA256 \
            or worker["shared_contract_freeze_file_sha256"] != SHARED_FREEZE_FILE_SHA256 \
            or worker["shared_contract_freeze_content_sha256"] != SHARED_FREEZE_CONTENT_SHA256:
        raise RuntimeError("Goal5790 shared freeze binding mismatch")
    if worker["output_contract_sha256"] != OUTPUT_CONTRACT_SHA256:
        raise RuntimeError("Goal5790 output contract mismatch")
    for name in ("output_scalar_u64", "oracle_output_scalar_u64"):
        value = worker.get(name)
        if not isinstance(value, int) or isinstance(value, bool) \
                or not 0 <= value <= U64_MAX:
            raise RuntimeError("Goal5790 malformed output scalar")
    if worker["output_scalar_u64"] != worker["oracle_output_scalar_u64"] \
            or worker["output_sha256"] != worker["oracle_output_sha256"] \
            or worker["output_sha256"] != digest(worker["output_scalar_u64"]):
        raise RuntimeError("Goal5790 exact output mismatch")
    target = _validate_target_authority(worker.get("target_materialization_authority"))
    if (
        worker["execution_source_archive_sha256"]
        != target["execution_source_archive_sha256"]
        or worker["execution_source_tree_sha256"]
        != target["execution_source_tree_sha256"]
        or worker["native_library_sha256"] != target["native_library_sha256"]
    ):
        raise RuntimeError("Goal5790 worker/target authority identity mismatch")
    _validate_phase_accounting(worker)
    _validate_segments(worker, target)


def _bootstrap(values: list[float], seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    draws = sorted(
        statistics.median(rng.choices(values, k=len(values)))
        for _ in range(BOOTSTRAP_DRAWS)
    )
    return (
        float(draws[BOOTSTRAP_CI_INDICES[0]]),
        float(draws[BOOTSTRAP_CI_INDICES[1]]),
    )


def build_evaluation(raw_root: Path) -> dict[str, object]:
    workers = _read_workers(raw_root)
    for worker in workers:
        _validate_worker(worker)
    if len({worker["parent_pid"] for worker in workers}) != len(workers):
        raise RuntimeError("Goal5790 reused parent PID")
    for key in COMMON_IDENTITIES:
        if len({worker[key] for worker in workers}) != 1:
            raise RuntimeError(f"Goal5790 mixed common identity: {key}")
    authorities = [worker["target_materialization_authority"] for worker in workers]
    if any(authority != authorities[0] for authority in authorities[1:]):
        raise RuntimeError("Goal5790 mixed target materialization authority")
    for row in statistical_rows():
        subset = [worker for worker in workers if worker["row_id"] == row["row_id"]]
        for identity in ("timer_contract_sha256", "lifecycle_contract_sha256"):
            if len({worker[identity] for worker in subset}) != 1:
                raise RuntimeError(
                    f"Goal5790 mixed row-local {identity} for {row['row_id']}")
    ordered = sorted(workers, key=lambda row: int(row["worker_index"]))
    observed_schedule = [
        {key: worker[key] for key in schedule_row}
        for worker, schedule_row in zip(ordered, schedule(), strict=True)
    ]
    if observed_schedule != list(schedule()):
        raise RuntimeError("Goal5790 observed schedule mismatch")

    grouped: dict[tuple[str, int], dict[str, dict[str, object]]] = {}
    for worker in workers:
        key = (str(worker["row_id"]), int(worker["pair_index"]))
        pair = grouped.setdefault(key, {})
        variant = str(worker["variant"])
        if variant in pair:
            raise RuntimeError("Goal5790 duplicate paired variant")
        pair[variant] = worker
    results = []
    for row in statistical_rows():
        ratios = []
        for pair_index in range(PAIR_COUNT):
            pair = grouped[(str(row["row_id"]), pair_index)]
            if set(pair) != set(VARIANTS):
                raise RuntimeError("Goal5790 incomplete paired variants")
            off = pair[FUSION_OFF]
            on = pair[FUSION_ON]
            for key in (
                "input_sha256",
                "output_sha256",
                "oracle_output_sha256",
                "timer_contract_sha256",
                "timer_contract",
                "lifecycle_contract_sha256",
                "lifecycle_contract",
                "output_contract_sha256",
                "oracle_contract_sha256",
                "output_scalar_u64",
                "oracle_output_scalar_u64",
                "segment_count",
                *COMMON_IDENTITIES,
            ):
                if off[key] != on[key]:
                    raise RuntimeError(f"Goal5790 paired identity mismatch: {key}")
            if off["target_materialization_authority"] \
                    != on["target_materialization_authority"]:
                raise RuntimeError("Goal5790 paired target authority mismatch")
            off_segments = off["segment_evidence"]
            on_segments = on["segment_evidence"]
            if not isinstance(off_segments, list) or not isinstance(on_segments, list):
                raise RuntimeError("Goal5790 paired segments missing")
            for off_segment, on_segment in zip(
                    off_segments, on_segments, strict=True):
                for name in (
                    "segment_id", "partition", "relation_count", "primitive_count",
                    "query_count", "scalar_sum", "output_sha256",
                ):
                    if off_segment[name] != on_segment[name]:
                        raise RuntimeError("Goal5790 paired segment mismatch: " + name)
                off_plan = off_segment["fusion_ablation_plan"]
                on_plan = on_segment["fusion_ablation_plan"]
                if off_plan["shared_identity_sha256"] \
                        != on_plan["shared_identity_sha256"]:
                    raise RuntimeError("Goal5790 paired shared plan identity mismatch")
                changed = {
                    name for name in off_plan if off_plan[name] != on_plan[name]
                }
                if changed != VARIANT_PLAN_FIELDS:
                    raise RuntimeError("Goal5790 unexpected paired plan delta")
            ratios.append(
                float(off["registered_complete_endpoint_seconds"])
                / float(on["registered_complete_endpoint_seconds"])
            )
        median = float(statistics.median(ratios))
        lower, upper = _bootstrap(
            ratios, BOOTSTRAP_SEED_BASE + int(row["row_index"])
        )
        results.append(
            {
                **row,
                "pair_count": PAIR_COUNT,
                "paired_unfused_over_fused_ratios": ratios,
                "paired_ratio_median": median,
                "bootstrap_ci95": [lower, upper],
                "greater_than_one_favors": FUSION_ON,
                "median_favors_fusion": median > 1.0,
                "independent_comparison_row": True,
            }
        )
    return {
        "schema": "rtdl.goal5790.static_primary_evaluation.v1",
        "formal_contract_sha256": contract_sha256(),
        "synthetic_contract_test_only": True,
        "target_performance_observation": False,
        "worker_count": len(workers),
        "unique_parent_pid_count": len(workers),
        "independent_row_count": len(results),
        "rows": results,
        "cross_dataset_or_lifecycle_compensation_used": False,
        "particle_rows": 0,
        "retry_resume_replacement_row_drop_relabel_used": False,
    }


def evaluate(raw_root: Path, output: Path) -> Path:
    if output.exists():
        raise FileExistsError(output)
    payload = build_evaluation(raw_root)
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
    print(evaluate(args.raw_root, args.output))


if __name__ == "__main__":
    main()
