#!/usr/bin/env python3
"""Independent stdlib recount of Goal5791 Home token-path lanes.

This file intentionally imports no RTDL product, Home worker/controller, or
formal worker/evaluator code.  It reconstructs JSON seals, operation-event
chains, output/oracle agreement, token-path phase boundaries, and behavioral
OptiX predicates directly from the ten raw lane documents.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct


ON_IDS = (
    "checked_summary.kernel_launch",
    "checked_summary.summary_copy_sync",
)
OFF_IDS = (
    "maximum_weight.logical_reduce",
    "maximum_weight.scalar_copy_sync",
    "weight_sum.logical_reduce",
    "weight_sum.scalar_copy_sync",
    "weighted_product.materialize",
    "weighted_product_sum.logical_reduce",
    "weighted_product_sum.scalar_copy_sync",
)
OPERATION_REQUIREMENTS = {
    "fusion_on": [
        {
            "ordinal": 0,
            "operation_id": "checked_summary.kernel_launch",
            "kind": "compiler_kernel_invocation",
            "units_per_value": 1,
            "fixed_units": 0,
            "bytes_per_unit": 0,
            "fixed_bytes": 0,
            "host_visibility_boundary": False,
            "compiler_visible_only": True,
        },
        {
            "ordinal": 1,
            "operation_id": "checked_summary.summary_copy_sync",
            "kind": "host_copy_synchronization",
            "units_per_value": 0,
            "fixed_units": 4,
            "bytes_per_unit": 8,
            "fixed_bytes": 0,
            "host_visibility_boundary": True,
            "compiler_visible_only": True,
        },
    ],
    "fusion_off": [
        {
            "ordinal": 0,
            "operation_id": "maximum_weight.logical_reduce",
            "kind": "logical_reduction",
            "units_per_value": 1,
            "fixed_units": 0,
            "bytes_per_unit": 0,
            "fixed_bytes": 0,
            "host_visibility_boundary": False,
            "compiler_visible_only": True,
        },
        {
            "ordinal": 1,
            "operation_id": "maximum_weight.scalar_copy_sync",
            "kind": "host_copy_synchronization",
            "units_per_value": 0,
            "fixed_units": 1,
            "bytes_per_unit": 8,
            "fixed_bytes": 0,
            "host_visibility_boundary": True,
            "compiler_visible_only": True,
        },
        {
            "ordinal": 2,
            "operation_id": "weight_sum.logical_reduce",
            "kind": "logical_reduction",
            "units_per_value": 1,
            "fixed_units": 0,
            "bytes_per_unit": 0,
            "fixed_bytes": 0,
            "host_visibility_boundary": False,
            "compiler_visible_only": True,
        },
        {
            "ordinal": 3,
            "operation_id": "weight_sum.scalar_copy_sync",
            "kind": "host_copy_synchronization",
            "units_per_value": 0,
            "fixed_units": 1,
            "bytes_per_unit": 8,
            "fixed_bytes": 0,
            "host_visibility_boundary": True,
            "compiler_visible_only": True,
        },
        {
            "ordinal": 4,
            "operation_id": "weighted_product.materialize",
            "kind": "device_materialization",
            "units_per_value": 1,
            "fixed_units": 0,
            "bytes_per_unit": 8,
            "fixed_bytes": 0,
            "host_visibility_boundary": False,
            "compiler_visible_only": True,
        },
        {
            "ordinal": 5,
            "operation_id": "weighted_product_sum.logical_reduce",
            "kind": "logical_reduction",
            "units_per_value": 1,
            "fixed_units": 0,
            "bytes_per_unit": 0,
            "fixed_bytes": 0,
            "host_visibility_boundary": False,
            "compiler_visible_only": True,
        },
        {
            "ordinal": 6,
            "operation_id": "weighted_product_sum.scalar_copy_sync",
            "kind": "host_copy_synchronization",
            "units_per_value": 0,
            "fixed_units": 1,
            "bytes_per_unit": 8,
            "fixed_bytes": 0,
            "host_visibility_boundary": True,
            "compiler_visible_only": True,
        },
    ],
}
OPERATION_EVIDENCE_TCB = (
    "trusted_runtime_records_each_compiler_instrumented_operation_only_after_"
    "its_callable_returns_successfully__not_hardware_or_opaque_partner_kernel_"
    "introspection"
)
EXPECTED_CACHE_POLICY = {
    "cupy_cache_dir_scope": "unique_per_worker",
    "numba_cache_dir_scope": "unique_per_worker",
    "cupy_and_numba_cache_dirs_are_distinct_siblings_under_worker_root": True,
    "shared_cache_between_workers_or_measured_arms": False,
    "cold_cache_initially_empty": True,
    "cold_definition": (
        "fresh_parent_process_and_empty_private_cupy_recipe_cache__"
        "not_cold_operating_system_page_cache_cuda_driver_jit_cache_or_"
        "optix_disk_cache"
    ),
    "cold_claim_excludes": [
        "operating_system_page_cache",
        "cuda_driver_jit_cache",
        "optix_disk_cache",
    ],
    "controller_rehashes_all_scheduled_inputs_before_worker_zero": True,
    "preworker_full_rehash_can_warm_operating_system_page_cache": True,
    "operating_system_page_cache_controlled_or_dropped": False,
    "operating_system_page_cache_scope": (
        "uncontrolled_same_cohort_balanced_pair_parity_interleaving"),
    "cuda_driver_jit_cache_controlled_or_isolated": False,
    "optix_disk_cache_controlled_or_isolated": False,
    "same_cohort_abba_symmetry_is_page_cache_mitigation_not_control": True,
    "round_major_abba_is_uncontrolled_cache_mitigation_not_control": True,
    "paper_must_disclose_page_cache_boundary": True,
    "cold_only_selected_recipe_first_compile_and_jit_inside_execute": True,
    "cold_preparation_may_compile_selected_recipe": False,
    "prepared_same_fresh_worker_prewarms_both_recipes": True,
    "prepared_private_cache_contains_both_neutral_prewarm_recipes": True,
    "prepared_neutral_recipe_prewarm_order": ["fusion_off", "fusion_on"],
    "prepared_each_recipe_launches_synchronizes_and_frees": True,
    "prepared_measurement_starts_only_after_both_neutral_prewarms": True,
    "prepared_cache_identity_bound_in_worker_receipt": True,
    "cache_receipts_preserved": True,
    "cache_payloads_are_authoritative_evidence": False,
    "successful_cohort_cache_payloads_removed_after_validation_before_publication": (
        True),
    "successful_cohort_empty_cache_directory_shells_preserved_for_offline_recount": (
        True),
    "successful_cohort_empty_cache_directory_shell_count": 96,
    "empty_cache_directory_shells_are_authoritative_evidence": False,
    "failed_terminal_staging_may_preserve_cache_payloads": True,
}
PLAN_FIELDS = {
    "schema", "mechanism_id", "shared_contract_file_sha256",
    "shared_contract_freeze_sha256", "semantic_request_sha256",
    "physical_encoding_sha256", "admitted_reference_plan_sha256",
    "executable_family_plan_sha256",
    "transformation_variant_contract_sha256", "physical_schema_sha256",
    "executable_family_id", "execution_source_archive_sha256",
    "execution_source_tree_sha256", "callback_ir_sha256",
    "callback_authority_nonce", "contract_sha256", "abi_sha256",
    "native_library_sha256", "provider_identity", "program_bundle_identity",
    "composed_program_sha256", "cupy_version",
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
OPERATION_RECEIPT_FIELDS = {
    "schema", "contract_sha256", "plan_sha256", "mechanism_id", "variant",
    "execution_nonce", "value_count", "output_sha256",
    "traversal_receipt_sha256", "events", "event_chain_sha256",
    "successful_event_count", "event_evidence_tcb",
    "hardware_introspection_claimed", "opaque_partner_kernel_count_claimed",
    "timing_or_duration_recorded", "receipt_sha256",
}
OPERATION_EVENT_FIELDS = {
    "schema", "sequence", "operation_id", "kind", "accounted_units",
    "accounted_bytes", "previous_event_sha256",
    "recorded_after_callable_success", "event_sha256",
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
REDUCTION_FIELDS = {
    "schema", "maximum_value", "maximum_weight", "weight_sum", "value_count",
    "value_upper_bound", "device_kernel_launch_count",
    "host_synchronization_count", "logical_reduction_count",
    "device_materialization_count", "operation_counts_event_derived",
    "maximum_value_is_device_observed", "maximum_value_provenance",
    "provisional_sum_trusted_only_after_bounds",
}
SEGMENT_FIELDS = {
    "segment_id", "descriptor", "descriptor_sha256", "plan_sha256",
    "fusion_ablation_plan", "segment_plan_input_binding",
    "plan_input_binding_sha256", "operation_execution_nonce", "token_path_only",
    "token_pre_admitted_in_preparation", "token_state_before_execute",
    "token_state_after_execute", "legacy_plan_argument_used_during_execute",
    "legacy_nonce_argument_used_during_execute", "device_phase_terminal_state",
    "evidence_phase_terminal_state", "reduced_output", "output_sha256",
    "operation_evidence_receipt", "checked_u64_weighted_reduction",
    "traversal_receipt", "traversal_semantic_binding",
}
SEGMENT_PLAN_INPUT_FIELDS = {
    "schema", "source_input_sha256", "segment_descriptor_sha256",
    "formal_input",
}
DESCRIPTOR_FIELDS = {
    "schema", "segment_id", "partition", "relation_count",
    "primitive_count", "query_count", "host_geometry_bytes",
    "maximum_weight", "weight_sum", "paper_algorithm", "gpu_touched",
}
PARTITION_FIELDS = {
    "source_begin", "source_end", "oversized_source_part",
    "global_segment_id",
}
PREWARM_ROW_FIELDS = {
    "variant", "purpose", "source_input_sha256", "descriptor",
    "segment_descriptor_sha256", "segment_plan_input_binding",
    "plan_input_binding_sha256", "fusion_ablation_plan",
    "token_pre_admitted", "token_consumed_once", "launch_completed",
    "synchronized", "device_pool_freed", "output_exact",
    "formal_evidence_created", "registered_performance_timing_created",
}
PHASE_ORDER_FIELDS = {
    "schema", "ordered_states", "loading_complete_before_preparation",
    "preparation_complete_before_prewarm_or_execute",
    "prewarm_complete_before_execute",
    "prewarm_not_required_before_execute",
    "execute_complete_before_device_iterator_close",
    "device_iterator_closed_before_seal", "seal_after_device_iterator_close",
    "seal_complete_before_executor_close",
    "executor_close_and_pool_release_complete",
}
LANE_FIELDS = {
    "schema", "status", "parent_pid", "input_kind", "dataset",
    "paper_algorithm", "variant", "lifecycle", "edge_file_sha256",
    "edge_file_bytes", "expected_triangle_count", "output", "matched",
    "output_sha256", "native_library_sha256",
    "execution_source_archive_sha256", "execution_source_tree_sha256",
    "target_materialization_receipt_sha256", "ptx_program_identity",
    "segment_count", "segments", "token_path_only", "cache_policy",
    "all_tokens_admitted_in_preparation",
    "deep_plan_authority_recipe_or_operation_verification_inside_execute",
    "execute_phase_contiguous_without_host_preparation_or_evidence_seal",
    "evidence_sealed_after_complete_execute", "prepared_neutral_prewarm",
    "functional_phase_order", "elapsed_value_count", "clock_sample_count",
    "home_performance_observation_created", "home_performance_diagnostic_used",
    "formal_worker",
    "formal_worker_count", "registered_performance_timing_count",
    "performance_or_compiler_fusion_claimed",
    "fresh_private_cupy_cache_at_process_start", "particle_included",
    "execution_environment_class", "pod_used",
}
EXPECTED_LANE_METADATA = {
    **{
        f"small__four_vertex_clique__{lifecycle}__{variant}.json": {
            "input_kind": "small", "dataset": "four_vertex_clique",
            "lifecycle": lifecycle, "variant": variant,
        }
        for lifecycle in ("cold", "prepared")
        for variant in ("fusion_on", "fusion_off")
    },
    **{
        f"bounded_real__{dataset}__bounded_smoke__{variant}.json": {
            "input_kind": "bounded_real", "dataset": dataset,
            "lifecycle": "bounded_smoke", "variant": variant,
        }
        for dataset in ("com-dblp", "cit-Patents", "soc-LiveJournal1")
        for variant in ("fusion_on", "fusion_off")
    },
}
EXPECTED_LANES = frozenset(EXPECTED_LANE_METADATA)
INPUT_AUTHORITIES = {
    ("small", "four_vertex_clique"): {
        "filename": "small__four_vertex_clique.edge",
        "sha256": "2f7f2b2d4f994e6abd593b71f5e28fe65b71d59e34f4134ad2037e5d037f746d",
        "bytes": 48,
        "triangle_count": 4,
    },
    ("bounded_real", "com-dblp"): {
        "filename": "bounded_real__com-dblp.edge",
        "sha256": "0a6d9608bd843e12ca1bac1d93a49e06cd40d76ab0526735dbf7204e6586be14",
        "bytes": 2_097_152,
        "triangle_count": 159_861,
    },
    ("bounded_real", "cit-Patents"): {
        "filename": "bounded_real__cit-Patents.edge",
        "sha256": "4b2b992c8efc9b67d6695245eb5d4647e39a9a1d996d4b05078f870dd1847ba0",
        "bytes": 2_097_152,
        "triangle_count": 97,
    },
    ("bounded_real", "soc-LiveJournal1"): {
        "filename": "bounded_real__soc-LiveJournal1.edge",
        "sha256": "86c12ecc87289f9fec53bf6f11f8607fde3d8b8380917a45dd6609fd26b4e8d1",
        "bytes": 2_097_152,
        "triangle_count": 70_758,
    },
}


class RecountError(RuntimeError):
    pass


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def _strict_json(path: Path) -> dict[str, object]:
    def pairs(rows):
        value: dict[str, object] = {}
        for key, item in rows:
            if key in value:
                raise RecountError(f"duplicate JSON key in {path.name}: {key}")
            value[key] = item
        return value

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                RecountError(f"non-finite JSON constant: {token}")),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RecountError(f"cannot read strict JSON: {path}") from exc
    if not isinstance(value, dict):
        raise RecountError(f"expected JSON object: {path}")
    return value


def _triangle_count(path: Path) -> int:
    """Reconstruct the simple-undirected oracle from raw little-endian pairs."""

    payload = path.read_bytes()
    if not payload or len(payload) % 8:
        raise RecountError(f"input is not an i32-pair stream: {path.name}")
    edges: set[tuple[int, int]] = set()
    for left, right in struct.iter_unpack("<ii", payload):
        if left < 0 or right < 0:
            raise RecountError(f"input has a negative vertex: {path.name}")
        if left != right:
            edges.add((min(left, right), max(left, right)))
    adjacency: dict[int, set[int]] = {}
    for left, right in edges:
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)
    return sum(
        1
        for left, right in edges
        for third in adjacency[left].intersection(adjacency[right])
        if third > right
    )


def _recount_inputs(root: Path) -> dict[tuple[str, str], dict[str, object]]:
    if root.is_symlink() or not root.is_dir():
        raise RecountError("independent input root is absent or a symlink")
    expected_names = {str(row["filename"]) for row in INPUT_AUTHORITIES.values()}
    observed = {path.name for path in root.iterdir() if path.is_file()}
    if observed != expected_names or any(
        path.is_symlink() or not path.is_file() for path in root.iterdir()
    ):
        raise RecountError("independent input member set drifted")
    result: dict[tuple[str, str], dict[str, object]] = {}
    for key, authority in INPUT_AUTHORITIES.items():
        path = root / str(authority["filename"])
        before = path.stat()
        observed_sha = _sha(path)
        triangle_count = _triangle_count(path)
        after = path.stat()
        if any(getattr(before, field) != getattr(after, field) for field in (
            "st_dev", "st_ino", "st_size", "st_mtime_ns", "st_mode",
        )):
            raise RecountError(f"input changed during recount: {path.name}")
        if before.st_size != authority["bytes"] \
                or observed_sha != authority["sha256"] \
                or triangle_count != authority["triangle_count"]:
            raise RecountError(f"independent input/oracle drifted: {path.name}")
        result[key] = {
            "filename": path.name,
            "size_bytes": before.st_size,
            "sha256": observed_sha,
            "independent_triangle_count": triangle_count,
        }
    return result


def _sealed(value: dict[str, object], field: str, label: str) -> None:
    claimed = value.get(field)
    unsigned = dict(value)
    unsigned.pop(field, None)
    if not isinstance(claimed, str) or _digest(unsigned) != claimed:
        raise RecountError(f"{label} seal mismatch")


def _behavioral_true_optix(
    receipt: dict[str, object], *, lane: dict[str, object],
    descriptor: dict[str, object], semantic_binding: object,
) -> bool:
    if set(receipt) != TRAVERSAL_RECEIPT_FIELDS \
            or not isinstance(semantic_binding, dict) \
            or set(semantic_binding) != {
                "authority", "contract", "abi", "composed_ptx", "native",
                "device_column_count",
            }:
        return False
    snapshot = receipt.get("native_snapshot")
    if not isinstance(snapshot, dict) or set(snapshot) != TRAVERSAL_SNAPSHOT_FIELDS:
        return False
    successful = snapshot.get("successful_launch_count")
    expected_bundles = receipt.get("expected_program_bundles")
    expected_bundle_ids = receipt.get("expected_program_bundle_ids")
    nonce = receipt.get("nonce")
    return (
        receipt.get("schema")
            == "rtdl.physical_execution.traversal_receipt.v1"
        and receipt.get("physical_executor_classification")
            == "optix_traversal_observed"
        and isinstance(successful, int) and not isinstance(successful, bool)
        and successful > 0
        and receipt.get("provider_library") == "librtdl_optix"
        and isinstance(receipt.get("provider_library_path"), str)
        and bool(receipt.get("provider_library_path"))
        and receipt.get("provider_library_sha256")
            == lane["native_library_sha256"]
        and receipt.get("route_identity")
            == "v4_builtin_triangle_callback_ir:partner_resident_checked_count_v1"
        and semantic_binding.get("native") == lane["native_library_sha256"]
        and semantic_binding.get("device_column_count") is True
        and receipt.get("semantic_digest") == _digest(semantic_binding)
        and receipt.get("claim_rules") == TRAVERSAL_CLAIM_RULES
        and isinstance(expected_bundles, list) and len(expected_bundles) == 1
        and expected_bundles[0]
            == "v4_builtin_triangle_checked_reduction_composed"
        and isinstance(expected_bundle_ids, list)
        and len(expected_bundle_ids) == 1
        and isinstance(expected_bundle_ids[0], int)
        and expected_bundle_ids[0] > 0
        and snapshot.get("first_program_bundle_id") == expected_bundle_ids[0]
        and snapshot.get("last_program_bundle_id") == expected_bundle_ids[0]
        and isinstance(nonce, dict) and set(nonce) == {"hi", "lo"}
        and nonce.get("hi") == snapshot.get("nonce_hi")
        and nonce.get("lo") == snapshot.get("nonce_lo")
        and snapshot.get("attempted_launch_count") == successful
        and snapshot.get("complete_context_launch_count") == successful
        and snapshot.get("context_bind_count") == successful
        and snapshot.get("raygen_invocation_count") == descriptor["query_count"]
        and snapshot.get("failed_launch_count") == 0
        and snapshot.get("incomplete_context_launch_count") == 0
        and snapshot.get("pending_context_at_finish") == 0
        and snapshot.get("session_error") == 0
        and isinstance(snapshot.get("first_traversable"), int)
        and snapshot["first_traversable"] != 0
        and isinstance(snapshot.get("last_traversable"), int)
        and snapshot["last_traversable"] != 0
        and snapshot.get("incomplete_callsite_record_count") == 0
        and snapshot.get("incomplete_callsite_lines") == [0] * 32
        and receipt.get("expected_program_observed_at_receipt_edge") is True
    )


def _verify_operation(
    receipt: dict[str, object], *, variant: str, output_sha256: str,
    traversal_sha256: str, plan: dict[str, object], nonce: str,
) -> int:
    ids = ON_IDS if variant == "fusion_on" else OFF_IDS
    requirements = plan["operation_requirements"]
    contract_payload = {
        "schema": "rtdl.v4.operation_sequence_contract.v1",
        "plan_sha256": plan["plan_sha256"],
        "mechanism_id": plan["mechanism_id"],
        "variant": variant,
        "declared_value_count": plan["value_count"],
        "requirements": requirements,
        "tcb_statement": OPERATION_EVIDENCE_TCB,
        "timing_or_duration_recorded": False,
        "hardware_introspection_claimed": False,
    }
    expected_contract_sha = _digest(contract_payload)
    if (
        set(receipt) != OPERATION_RECEIPT_FIELDS
        or receipt.get("schema") != "rtdl.v4.operation_evidence_receipt.v1"
        or receipt.get("variant") != variant
        or receipt.get("plan_sha256") != plan["plan_sha256"]
        or receipt.get("mechanism_id") != plan["mechanism_id"]
        or receipt.get("contract_sha256") != expected_contract_sha
        or receipt.get("execution_nonce") != nonce
        or receipt.get("value_count") != plan["value_count"]
        or receipt.get("output_sha256") != output_sha256
        or receipt.get("traversal_receipt_sha256") != traversal_sha256
        or receipt.get("successful_event_count") != len(ids)
        or receipt.get("event_evidence_tcb") != OPERATION_EVIDENCE_TCB
        or receipt.get("timing_or_duration_recorded") is not False
        or receipt.get("hardware_introspection_claimed") is not False
        or receipt.get("opaque_partner_kernel_count_claimed") is not False
    ):
        raise RecountError("operation receipt header/binding drifted")
    previous = expected_contract_sha
    events = receipt.get("events")
    if not isinstance(events, list) or len(events) != len(ids):
        raise RecountError("operation event cardinality drifted")
    for index, (event, operation_id, requirement) in enumerate(zip(
        events, ids, requirements, strict=True,
    )):
        units = (
            int(requirement["units_per_value"]) * int(plan["value_count"])
            + int(requirement["fixed_units"])
        )
        byte_count = (
            int(requirement["bytes_per_unit"]) * units
            + int(requirement["fixed_bytes"])
        )
        if not isinstance(event, dict) or set(event) != OPERATION_EVENT_FIELDS or (
            event.get("schema") != "rtdl.v4.operation_evidence_event.v1"
            or event.get("sequence") != index
            or event.get("operation_id") != operation_id
            or event.get("kind") != requirement["kind"]
            or event.get("accounted_units") != units
            or event.get("accounted_bytes") != byte_count
            or event.get("previous_event_sha256") != previous
            or event.get("recorded_after_callable_success") is not True
        ):
            raise RecountError("operation event order/binding drifted")
        _sealed(event, "event_sha256", "operation event")
        previous = str(event["event_sha256"])
    if receipt.get("event_chain_sha256") != previous:
        raise RecountError("operation event chain terminal digest drifted")
    _sealed(receipt, "receipt_sha256", "operation receipt")
    return len(events)


def _verify_plan(
    value: object, *, lane: dict[str, object], descriptor: dict[str, object],
    plan_input_binding: object, variant_override: str | None = None,
    source_input_sha256: str | None = None,
    oracle_contract_override: dict[str, object] | None = None,
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != PLAN_FIELDS:
        raise RecountError("fusion ablation plan shape drifted")
    plan = value
    shared_sha = plan.get("shared_identity_sha256")
    plan_sha = plan.get("plan_sha256")
    plan_payload = dict(plan)
    plan_payload.pop("shared_identity_sha256")
    plan_payload.pop("plan_sha256")
    common = dict(plan_payload)
    for name in (
        "variant", "only_allowlisted_difference", "lowering_node",
        "downstream_operation_recipe_sha256", "operation_requirements",
    ):
        common.pop(name)
    variant = (
        str(lane["variant"]) if variant_override is None
        else variant_override
    )
    if variant not in ("fusion_on", "fusion_off"):
        raise RecountError("fusion ablation plan variant drifted")
    ids = ON_IDS if variant == "fusion_on" else OFF_IDS
    requirements = plan.get("operation_requirements")
    if requirements != OPERATION_REQUIREMENTS[variant]:
        raise RecountError("plan operation requirements drifted")
    requirement_fields = {
        "ordinal", "operation_id", "kind", "units_per_value", "fixed_units",
        "bytes_per_unit", "fixed_bytes", "host_visibility_boundary",
        "compiler_visible_only",
    }
    for index, (requirement, operation_id) in enumerate(zip(
        requirements, ids, strict=True,
    )):
        if not isinstance(requirement, dict) \
                or set(requirement) != requirement_fields \
                or requirement.get("ordinal") != index \
                or requirement.get("operation_id") != operation_id \
                or any(type(requirement.get(name)) is not int \
                       or requirement[name] < 0 for name in (
                           "units_per_value", "fixed_units",
                           "bytes_per_unit", "fixed_bytes")) \
                or type(requirement.get("host_visibility_boundary")) is not bool \
                or type(requirement.get("compiler_visible_only")) is not bool:
            raise RecountError("plan operation requirement content drifted")
    if not isinstance(plan_input_binding, dict) \
            or set(plan_input_binding) != SEGMENT_PLAN_INPUT_FIELDS \
            or plan_input_binding.get("schema") \
                != "rtdl.goal5791.segment_plan_input.v1" \
            or plan_input_binding.get("source_input_sha256") \
                != (lane["edge_file_sha256"] if source_input_sha256 is None
                    else source_input_sha256) \
            or plan_input_binding.get("segment_descriptor_sha256") \
                != _digest(descriptor) \
            or plan_input_binding.get("formal_input") is not False:
        raise RecountError("segment plan input binding drifted")
    output_contract = {
        "schema": "rtdl.goal5791.home_output_contract.v1",
        "paper_algorithm": "RT-2A1",
        "result": "exact_u64_triangle_count",
        "overflow": "fail_closed_before_wraparound",
    }
    oracle_contract = (
        {
            "schema": "rtdl.goal5791.home_bounded_oracle.v1",
            "dataset": lane["dataset"],
            "edge_file_sha256": lane["edge_file_sha256"],
            "expected_triangle_count": lane["expected_triangle_count"],
            "authority": (
                "independent_stdlib_simple_undirected_triangle_recount"),
        }
        if oracle_contract_override is None else oracle_contract_override
    )
    no_elapsed_observation_contract = {
        "schema": "rtdl.goal5791.home_zero_elapsed_observation.v1",
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
        "token_admission_before_device_geometry": True,
        "device_iterator_closed_before_evidence_seal": True,
    }
    lifecycle_contract = {
        "schema": "rtdl.goal5791.home_lifecycle.v1",
        "lifecycle": lane["lifecycle"],
        "prepared_neutral_prewarm_order": (
            ["fusion_off", "fusion_on"]
            if lane["lifecycle"] == "prepared" else []
        ),
        "formal_worker": False,
    }
    on_recipe = plan.get("fusion_on_downstream_operation_recipe")
    off_recipe = plan.get("fusion_off_downstream_operation_recipe")
    if (
        plan.get("schema") != "rtdl.v4.fusion_ablation_plan.v2"
        or plan.get("mechanism_id")
            != "checked_u64_product_sum_downstream_lowering.v1"
        or plan.get("variant") != variant
        or plan.get("input_sha256") != _digest(plan_input_binding)
        or plan.get("output_contract_sha256") != _digest(output_contract)
        or plan.get("oracle_sha256") != _digest(oracle_contract)
        or plan.get("timer_contract_sha256")
            != _digest(no_elapsed_observation_contract)
        or plan.get("lifecycle_contract_sha256") != _digest(lifecycle_contract)
        or plan.get("value_count") != descriptor.get("query_count")
        or plan.get("execution_source_archive_sha256")
            != lane["execution_source_archive_sha256"]
        or plan.get("execution_source_tree_sha256")
            != lane["execution_source_tree_sha256"]
        or plan.get("native_library_sha256") != lane["native_library_sha256"]
        or plan.get("target_materialization_receipt_sha256")
            != lane["target_materialization_receipt_sha256"]
        or plan.get("provider_identity") != "optix"
        or plan.get("same_semantic_ir_required") is not True
        or plan.get("same_optix_producer_required") is not True
        or plan.get("performance_or_timing_claimed") is not False
        or plan.get("variant_selected_from_app_dataset_result_or_timing") is not False
        or plan.get("executable") is not False
        or plan.get("only_allowlisted_difference")
            != "downstream_checked_u64_reducer_operation_identity_and_event_sequence"
        or plan.get("lowering_node") != (
            "checked_summary_kernel_then_one_summary_copy_sync"
            if variant == "fusion_on" else
            "max_sum_materialize_product_sum_then_three_scalar_copy_sync"
        )
        or plan.get("downstream_operation_recipe_sha256") != plan.get(
            "fusion_on_downstream_operation_recipe_sha256"
            if variant == "fusion_on" else
            "fusion_off_downstream_operation_recipe_sha256"
        )
        or not isinstance(on_recipe, dict)
        or not isinstance(off_recipe, dict)
        or plan.get("fusion_on_downstream_operation_recipe_sha256")
            != _digest(on_recipe)
        or plan.get("fusion_off_downstream_operation_recipe_sha256")
            != _digest(off_recipe)
        or shared_sha != _digest(common)
        or plan_sha != _digest(plan_payload)
    ):
        raise RecountError("fusion ablation plan identity drifted")
    return plan


def _verify_reduction(
    value: dict[str, object], variant: str, *,
    descriptor: dict[str, object], reduced_output: int,
) -> None:
    expected = (
        {
            "device_kernel_launch_count": 1,
            "host_synchronization_count": 1,
            "logical_reduction_count": 0,
            "device_materialization_count": 0,
            "maximum_value_is_device_observed": True,
        }
        if variant == "fusion_on" else
        {
            "device_kernel_launch_count": 0,
            "host_synchronization_count": 3,
            "logical_reduction_count": 3,
            "device_materialization_count": 1,
            "maximum_value_is_device_observed": False,
        }
    )
    maximum = value.get("maximum_value")
    if set(value) != REDUCTION_FIELDS \
            or type(maximum) is not int or maximum < 0 \
            or value.get("schema") \
            != "rtdl.v4.checked_u64_weighted_reduction.receipt.v1" \
            or value.get("maximum_weight") != descriptor["maximum_weight"] \
            or value.get("weight_sum") != descriptor["weight_sum"] \
            or value.get("value_count") != descriptor["query_count"] \
            or value.get("value_upper_bound") != descriptor["primitive_count"] \
            or maximum > descriptor["primitive_count"] \
            or reduced_output > (
                descriptor["primitive_count"] * descriptor["weight_sum"]
            ) \
            or value.get("operation_counts_event_derived") is not True \
            or value.get("provisional_sum_trusted_only_after_bounds") is not True \
            or value.get("maximum_value_provenance") != (
                "device_observed" if variant == "fusion_on" else
                "optix_producer_declared_primitive_bound"
            ) \
            or any(value.get(name) != expected_item
                   for name, expected_item in expected.items()):
        raise RecountError("checked-U64 reduction receipt drifted")


def _verify_descriptor(value: object, *, segment_id: int) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != DESCRIPTOR_FIELDS:
        raise RecountError("segment descriptor shape drifted")
    partition = value.get("partition")
    if not isinstance(partition, dict) or set(partition) != PARTITION_FIELDS:
        raise RecountError("segment partition shape drifted")
    integer_fields = (
        "relation_count", "primitive_count", "query_count",
        "host_geometry_bytes", "maximum_weight", "weight_sum",
    )
    if (
        value.get("schema") != "rtdl.goal5791.rt2a1_segment_descriptor.v1"
        or value.get("segment_id") != segment_id
        or value.get("paper_algorithm") != "RT-2A1"
        or value.get("gpu_touched") is not False
        or any(type(value.get(name)) is not int or value[name] <= 0
               for name in integer_fields)
        or type(partition.get("source_begin")) is not int
        or type(partition.get("source_end")) is not int
        or type(partition.get("oversized_source_part")) is not int
        or type(partition.get("global_segment_id")) is not int
        or partition["source_begin"] < 0
        or partition["source_end"] <= partition["source_begin"]
        or partition["oversized_source_part"] < 0
        or partition["global_segment_id"] != segment_id
        or value["query_count"] > value["relation_count"]
        or value["maximum_weight"] > value["relation_count"]
        or value["weight_sum"] != value["relation_count"]
        or value["host_geometry_bytes"] != (
            76 * value["primitive_count"] + 68 * value["query_count"]
        )
    ):
        raise RecountError("segment descriptor content drifted")
    return value


def _lane(
    path: Path, *, expected: dict[str, str],
    input_record: dict[str, object],
) -> dict[str, object]:
    value = _strict_json(path)
    if not isinstance(value, dict) or set(value) != LANE_FIELDS or (
        value.get("schema") != "rtdl.goal5791.home_token_functional_lane.v1"
        or value.get("status")
            != "PASS__TOKEN_ONLY_EXACT_BEHAVIORAL_TRUE_OPTIX"
        or value.get("paper_algorithm") != "RT-2A1"
        or value.get("matched") is not True
        or value.get("output") != value.get("expected_triangle_count")
        or value.get("token_path_only") is not True
        or value.get("all_tokens_admitted_in_preparation") is not True
        or value.get(
            "deep_plan_authority_recipe_or_operation_verification_inside_execute"
        ) is not False
        or value.get(
            "execute_phase_contiguous_without_host_preparation_or_evidence_seal"
        ) is not True
        or value.get("evidence_sealed_after_complete_execute") is not True
        or value.get("elapsed_value_count") != 0
        or value.get("clock_sample_count") != 0
        or value.get("home_performance_observation_created") is not False
        or value.get("home_performance_diagnostic_used") is not False
        or value.get("formal_worker") is not False
        or value.get("formal_worker_count") != 0
        or value.get("registered_performance_timing_count") != 0
        or value.get("performance_or_compiler_fusion_claimed") is not False
        or value.get("fresh_private_cupy_cache_at_process_start") is not True
        or value.get("cache_policy") != EXPECTED_CACHE_POLICY
        or type(value.get("parent_pid")) is not int
        or value["parent_pid"] <= 0
        or value.get("particle_included") is not False
        or value.get("execution_environment_class")
            != "HOME_PASCAL_FUNCTIONAL_ONLY"
        or value.get("pod_used") is not False
        or any(value.get(name) != item for name, item in expected.items())
        or value.get("edge_file_sha256") != input_record["sha256"]
        or value.get("edge_file_bytes") != input_record["size_bytes"]
        or value.get("expected_triangle_count")
            != input_record["independent_triangle_count"]
        or value.get("output") != input_record["independent_triangle_count"]
        or value.get("output_sha256") != _digest(value.get("output"))
    ):
        raise RecountError(f"lane scope/status drifted: {path.name}")
    variant = value.get("variant")
    if variant not in ("fusion_on", "fusion_off"):
        raise RecountError("lane variant is invalid")
    expected_prepared = value.get("lifecycle") == "prepared"
    prewarm_state = (
        "prewarm_complete" if expected_prepared else "prewarm_not_required")
    expected_phase_states = [
        "loading_complete", "preparation_complete", prewarm_state,
        "execute_complete", "device_iterator_closed",
        "evidence_seal_complete", "executor_close_and_pool_release_complete",
    ]
    phases = value.get("functional_phase_order")
    if not isinstance(phases, dict) or set(phases) != PHASE_ORDER_FIELDS \
            or phases.get("schema") \
                != "rtdl.goal5791.home_functional_phase_order.v1" \
            or phases.get("ordered_states") != expected_phase_states \
            or phases.get("loading_complete_before_preparation") is not True \
            or phases.get(
                "preparation_complete_before_prewarm_or_execute") is not True \
            or phases.get("prewarm_complete_before_execute") \
                is not expected_prepared \
            or phases.get("prewarm_not_required_before_execute") \
                is expected_prepared \
            or phases.get(
                "execute_complete_before_device_iterator_close") is not True \
            or phases.get("device_iterator_closed_before_seal") is not True \
            or phases.get("seal_after_device_iterator_close") is not True \
            or phases.get("seal_complete_before_executor_close") is not True \
            or phases.get(
                "executor_close_and_pool_release_complete") is not True:
        raise RecountError("functional phase order drifted")
    prewarm = value.get("prepared_neutral_prewarm")
    if not isinstance(prewarm, dict) \
            or prewarm.get("performed") is not expected_prepared:
        raise RecountError("prepared prewarm policy drifted")
    if expected_prepared:
        if prewarm.get("order") != ["fusion_off", "fusion_on"] \
                or [row.get("variant") for row in prewarm.get("rows", [])] \
                    != ["fusion_off", "fusion_on"] \
                or any(
                    not isinstance(row, dict)
                    or set(row) != PREWARM_ROW_FIELDS
                    or row.get("purpose")
                        != "recipe_jit_cache_neutralization_only"
                    or row.get("source_input_sha256")
                        != INPUT_AUTHORITIES[(
                            "small", "four_vertex_clique")]["sha256"]
                    or row.get("segment_descriptor_sha256")
                        != _digest(row.get("descriptor"))
                    or row.get("segment_descriptor_sha256")
                        != row.get("segment_plan_input_binding", {}).get(
                            "segment_descriptor_sha256")
                    or row.get("plan_input_binding_sha256")
                        != _digest(row.get("segment_plan_input_binding"))
                    or not isinstance(row.get("fusion_ablation_plan"), dict)
                    or row["fusion_ablation_plan"].get("input_sha256")
                        != row.get("plan_input_binding_sha256")
                    or row["fusion_ablation_plan"].get("variant")
                        != row.get("variant")
                    or row.get("segment_plan_input_binding") != {
                        "schema": "rtdl.goal5791.segment_plan_input.v1",
                        "source_input_sha256": INPUT_AUTHORITIES[(
                            "small", "four_vertex_clique")]["sha256"],
                        "segment_descriptor_sha256": row.get(
                            "segment_descriptor_sha256"),
                        "formal_input": False,
                    }
                    or row.get("token_pre_admitted") is not True
                    or row.get("token_consumed_once") is not True
                    or row.get("launch_completed") is not True
                    or row.get("synchronized") is not True
                    or row.get("device_pool_freed") is not True
                    or row.get("output_exact") is not True
                    or row.get("formal_evidence_created") is not False
                    or row.get("registered_performance_timing_created") is not False
                    for row in prewarm.get("rows", [])
                ):
            raise RecountError("neutral prewarm receipt drifted")
    elif prewarm.get("order") != [] or prewarm.get("rows") != []:
        raise RecountError("non-prepared lane carried a prewarm")
    if expected_prepared:
        neutral_sha = str(INPUT_AUTHORITIES[(
            "small", "four_vertex_clique")]["sha256"])
        for row in prewarm["rows"]:
            descriptor = _verify_descriptor(row["descriptor"], segment_id=0)
            _verify_plan(
                row["fusion_ablation_plan"], lane=value,
                descriptor=descriptor,
                plan_input_binding=row["segment_plan_input_binding"],
                variant_override=str(row["variant"]),
                source_input_sha256=neutral_sha,
                oracle_contract_override={
                    "schema": "rtdl.goal5791.neutral_prewarm_oracle.v1",
                    "input_sha256": neutral_sha,
                    "expected_triangle_count": 4,
                    "formal_input": False,
                },
            )

    segments = value.get("segments")
    if not isinstance(segments, list) or not segments \
            or value.get("segment_count") != len(segments):
        raise RecountError("lane segment cardinality drifted")
    event_count = 0
    launch_count = 0
    raygen_count = 0
    reduced_sum = 0
    for index, row in enumerate(segments):
        if not isinstance(row, dict) or set(row) != SEGMENT_FIELDS or (
            row.get("segment_id") != index
            or row.get("descriptor_sha256") != _digest(row.get("descriptor"))
            or row.get("token_path_only") is not True
            or row.get("token_pre_admitted_in_preparation") is not True
            or row.get("token_state_before_execute") != "fresh"
            or row.get("token_state_after_execute") != "consumed"
            or row.get("legacy_plan_argument_used_during_execute") is not False
            or row.get("legacy_nonce_argument_used_during_execute") is not False
            or row.get("device_phase_terminal_state")
                != "device_complete_unsealed"
            or row.get("evidence_phase_terminal_state") != "sealed"
            or type(row.get("reduced_output")) is not int
            or row["reduced_output"] < 0
            or row.get("output_sha256") != _digest(row["reduced_output"])
        ):
            raise RecountError("segment token/descriptor boundary drifted")
        descriptor = _verify_descriptor(row.get("descriptor"), segment_id=index)
        plan_input_binding = row.get("segment_plan_input_binding")
        if row.get("plan_input_binding_sha256") \
                != _digest(plan_input_binding):
            raise RecountError("segment plan input binding seal drifted")
        plan = _verify_plan(
            row.get("fusion_ablation_plan"), lane=value,
            descriptor=descriptor, plan_input_binding=plan_input_binding,
        )
        nonce = row.get("operation_execution_nonce")
        if not isinstance(nonce, str) or not 16 <= len(nonce) <= 256:
            raise RecountError("segment operation nonce drifted")
        if row.get("plan_sha256") != plan["plan_sha256"]:
            raise RecountError("segment plan binding drifted")
        traversal = row.get("traversal_receipt")
        semantic_binding = row.get("traversal_semantic_binding")
        operation = row.get("operation_evidence_receipt")
        reduction = row.get("checked_u64_weighted_reduction")
        if not all(isinstance(item, dict)
                   for item in (traversal, operation, reduction)):
            raise RecountError("segment receipt is absent")
        _sealed(traversal, "receipt_sha256", "traversal receipt")
        if not _behavioral_true_optix(
            traversal, lane=value, descriptor=descriptor,
            semantic_binding=semantic_binding,
        ):
            raise RecountError("segment is not behaviorally true OptiX")
        if traversal.get("output_digest") != row.get("output_sha256"):
            raise RecountError("traversal output digest drifted")
        event_count += _verify_operation(
            operation, variant=str(variant),
            output_sha256=str(row.get("output_sha256")),
            traversal_sha256=str(traversal.get("receipt_sha256")),
            plan=plan, nonce=nonce,
        )
        _verify_reduction(
            reduction, str(variant), descriptor=descriptor,
            reduced_output=int(row["reduced_output"]),
        )
        snapshot = traversal["native_snapshot"]
        launch_count += int(snapshot["successful_launch_count"])
        raygen_count += int(snapshot["raygen_invocation_count"])
        reduced_sum += int(row["reduced_output"])
    if reduced_sum != value["output"]:
        raise RecountError("segment sum differs from lane output")
    value["_recount"] = {
        "operation_receipt_count": len(segments),
        "successful_operation_event_count": event_count,
        "successful_launch_count": launch_count,
        "raygen_invocation_count": raygen_count,
    }
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--expected-source-archive-sha256", required=True)
    parser.add_argument("--expected-source-tree-sha256", required=True)
    parser.add_argument("--expected-native-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    if args.raw.is_symlink() or not args.raw.is_dir():
        raise RecountError("raw Home lane root is absent or a symlink")
    raw_members = list(args.raw.iterdir())
    if any(path.is_symlink() or not path.is_file() for path in raw_members):
        raise RecountError("raw Home lane root contains a link/special/directory")
    files = {path.name: path for path in raw_members}
    if set(files) != EXPECTED_LANES:
        raise RecountError(
            f"raw lane set drifted: {sorted(set(files) ^ EXPECTED_LANES)!r}")
    inputs = _recount_inputs(args.inputs)
    lanes = [
        _lane(
            files[name], expected=EXPECTED_LANE_METADATA[name],
            input_record=inputs[(
                EXPECTED_LANE_METADATA[name]["input_kind"],
                EXPECTED_LANE_METADATA[name]["dataset"],
            )],
        )
        for name in sorted(files)
    ]
    if len({lane["parent_pid"] for lane in lanes}) != 10:
        raise RecountError("Home lanes did not use ten fresh parent PIDs")
    common_source = {lane["execution_source_archive_sha256"] for lane in lanes}
    common_tree = {lane["execution_source_tree_sha256"] for lane in lanes}
    common_native = {lane["native_library_sha256"] for lane in lanes}
    common_target_receipt = {
        lane["target_materialization_receipt_sha256"] for lane in lanes
    }
    # The frozen Home lane carries the complete PTX program identity object,
    # not a separately trusted scalar digest.  Reconstruct the canonical
    # digest here so the independent recount consumes the actual lane schema.
    common_ptx_identity = {
        _digest(lane["ptx_program_identity"]) for lane in lanes
    }
    if common_source != {args.expected_source_archive_sha256} \
            or common_tree != {args.expected_source_tree_sha256} \
            or common_native != {args.expected_native_sha256} \
            or len(common_target_receipt) != 1 \
            or len(common_ptx_identity) != 1:
        raise RecountError("lane source/tree/native identity drifted")
    by_variant = {
        variant: [lane for lane in lanes if lane["variant"] == variant]
        for variant in ("fusion_on", "fusion_off")
    }
    if any(len(rows) != 5 for rows in by_variant.values()):
        raise RecountError("Home ON/OFF lane balance drifted")
    totals = {
        key: sum(int(lane["_recount"][key]) for lane in lanes)
        for key in (
            "operation_receipt_count", "successful_operation_event_count",
            "successful_launch_count", "raygen_invocation_count",
        )
    }
    operation_by_variant = {
        variant: sum(int(lane["_recount"]["operation_receipt_count"])
                     for lane in rows)
        for variant, rows in by_variant.items()
    }
    event_by_variant = {
        variant: sum(int(lane["_recount"]["successful_operation_event_count"])
                     for lane in rows)
        for variant, rows in by_variant.items()
    }
    if event_by_variant["fusion_on"] \
            != 2 * operation_by_variant["fusion_on"] \
            or event_by_variant["fusion_off"] \
            != 7 * operation_by_variant["fusion_off"]:
        raise RecountError("two-versus-seven event relation drifted")
    result = {
        "schema": "rtdl.goal5791.independent_home_token_recount.v1",
        "status": "PASS__10_OF_10_TOKEN_ONLY_EXACT_BEHAVIORAL_TRUE_OPTIX",
        "execution_source_archive_sha256": args.expected_source_archive_sha256,
        "execution_source_tree_sha256": args.expected_source_tree_sha256,
        "native_library_sha256": args.expected_native_sha256,
        "raw_lane_count": len(lanes),
        "raw_lane_sha256": {name: _sha(files[name]) for name in sorted(files)},
        "independently_recounted_inputs": {
            f"{kind}__{dataset}": record
            for (kind, dataset), record in sorted(inputs.items())
        },
        "independent_simple_undirected_oracle_recomputed_from_raw_edges": True,
        "exact_lane_count": 10,
        "behavioral_true_optix_lane_count": 10,
        "token_only_lane_count": 10,
        "target_materialization_receipt_sha256": next(
            iter(common_target_receipt)),
        "ptx_program_identity_sha256": next(iter(common_ptx_identity)),
        "fresh_parent_pid_count": 10,
        **totals,
        "operation_receipt_count_by_variant": operation_by_variant,
        "successful_operation_event_count_by_variant": event_by_variant,
        "event_count_per_receipt": {"fusion_on": 2, "fusion_off": 7},
        "prepared_lane_count": 2,
        "prepared_neutral_off_then_on_prewarm_count": 2,
        "cache_policy_sha256": _digest(EXPECTED_CACHE_POLICY),
        "cold_definition": EXPECTED_CACHE_POLICY["cold_definition"],
        "cold_claim_excludes": EXPECTED_CACHE_POLICY["cold_claim_excludes"],
        "operating_system_page_cache_controlled_or_dropped": (
            EXPECTED_CACHE_POLICY[
                "operating_system_page_cache_controlled_or_dropped"]),
        "operating_system_page_cache_scope": EXPECTED_CACHE_POLICY[
            "operating_system_page_cache_scope"],
        "cuda_driver_jit_cache_controlled_or_isolated": False,
        "optix_disk_cache_controlled_or_isolated": False,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "performance_or_compiler_fusion_claimed": False,
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
        "product_or_execution_route_imported": False,
        "controller_worker_evaluator_or_formal_recount_imported": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
