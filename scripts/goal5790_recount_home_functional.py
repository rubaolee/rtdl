#!/usr/bin/env python3
"""Independent standard-library recount of Goal5790 Home evidence.

This verifier imports neither RTDL nor the Triangle application. It rebuilds
the exact ten-lane matrix, bounded-view triangle oracles, frozen plan identity,
operation contracts/events/receipts, and scalar-output bindings from JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct


VARIANTS = ("fusion_on", "fusion_off")
SMALL_DATASET = "four_vertex_clique"
PREFIX_EDGE_RECORD_COUNT = 262_144
REAL_PREFIX_RULE = (
    "first_262144_little_endian_i32_pair_records_preserve_order"
)
REAL_DATASETS = {
    "com-dblp": {
        "filename": "com-dblp.edge",
        "sha256": "e9647564c1ca96589cc52314cabf5569ec80b9f5d697578a55d47fbe7aafca67",
        "size_bytes": 8_398_928,
        "prefix_sha256": "0a6d9608bd843e12ca1bac1d93a49e06cd40d76ab0526735dbf7204e6586be14",
        "prefix_triangle_count": 159_861,
    },
    "cit-Patents": {
        "filename": "cit-Patents.edge",
        "sha256": "c5b2c9203eeabb46414965755c33befdb1810e71cb51155eb940a68a6179d855",
        "size_bytes": 132_151_584,
        "prefix_sha256": "4b2b992c8efc9b67d6695245eb5d4647e39a9a1d996d4b05078f870dd1847ba0",
        "prefix_triangle_count": 97,
    },
    "soc-LiveJournal1": {
        "filename": "soc-LiveJournal1.edge",
        "sha256": "80199ecebb7ebdf3b4861748e009d16b1c5f93c35eba837a7ce37f94ada35f83",
        "size_bytes": 551_950_184,
        "prefix_sha256": "86c12ecc87289f9fec53bf6f11f8607fde3d8b8380917a45dd6609fd26b4e8d1",
        "prefix_triangle_count": 70_758,
    },
}
ORACLE_AUTHORITY = (
    "independent_stdlib_simple_undirected_triangle_recount_from_shipped_bounded_edges"
)
MECHANISM = "checked_u64_product_sum_downstream_lowering.v1"
OPERATION_TCB = (
    "trusted_runtime_records_each_compiler_instrumented_operation_only_after_"
    "its_callable_returns_successfully__not_hardware_or_opaque_partner_kernel_"
    "introspection"
)
PROGRAM_BUNDLE = "v4_builtin_triangle_checked_reduction_composed"
FAMILY_ID = (
    "v4_triangle_per_ray_optix_producer_plus_checked_u64_continuation.v1"
)
ALLOWLIST = (
    "downstream_checked_u64_reducer_operation_identity_and_event_sequence"
)
FROZEN_PLAN_IDENTITIES = {
    "shared_contract_file_sha256": (
        "b62217a5374732cece8c7eaef93c0f21eb580666559e912eb8dd1bb2aaa7628b"),
    "shared_contract_freeze_sha256": (
        "8ada80c377241aa9a4fde29f26fdc9380257f93cc2264a3e60f2a96a437fced5"),
    "semantic_request_sha256": (
        "492c59b92f3ab8138d5bff6b481bff16e51db5028868732d266ef2948810f02e"),
    "physical_encoding_sha256": (
        "7f1d101e8f588571c58958152ed7f20ef43387a50d9fd00c5c7925d7405dc656"),
    "admitted_reference_plan_sha256": (
        "8dc1c000146e6df31e77ad86f21ae799bb543aeda68de4054932222523409d8e"),
    "executable_family_plan_sha256": (
        "ddb4909e48ca37b5065e1db86b34ff9610bc9d9a915a76efb651bb692028faa3"),
    "transformation_variant_contract_sha256": (
        "425bb6cffe4edb121f8e1bf3e9a730405439e2af32507b3c8b0c8d6a6b613ff3"),
    "physical_schema_sha256": (
        "97e3e85f8ab60e612e922a156fe2ecd8349b94e51a34d6984d8ce75133070e73"),
}
HOME_MACHINE_AUTHORITY = {
    "schema": "rtdl.goal5790.frozen_home_machine_authority.v3",
    "execution_environment_class": "HOME_PASCAL_FUNCTIONAL_ONLY",
    "gpu_name": "NVIDIA GeForce GTX 1070",
    "gpu_uuid": "GPU-8e04454e-c177-6e5b-3f43-e676980ecdfa",
    "driver_version": "580.126.09",
    "compute_capability": "6.1",
    "cuda_nvcc_version": "Build cuda_12.2.r12.2/compiler.33191640_0",
    "cuda_host_compiler_path": "/usr/bin/g++-12",
    "cuda_host_compiler_version": (
        "g++-12 (Ubuntu 12.4.0-2ubuntu1~24.04.1) 12.4.0"
    ),
    "cuda_nvrtc_resolved_path": (
        "/home/lestat/vendor/cuda-12.2.2/targets/x86_64-linux/lib/"
        "libnvrtc.so.12.2.140"
    ),
    "cuda_nvrtc_sha256": (
        "000ca6278ba8b32a7dac383eb7440929c5a09095b43dd5f2df3911f63520db70"
    ),
    "cuda_nvrtc_builtins_resolved_path": (
        "/home/lestat/vendor/cuda-12.2.2/targets/x86_64-linux/lib/"
        "libnvrtc-builtins.so.12.2.140"
    ),
    "cuda_nvrtc_builtins_sha256": (
        "968ebb00640e461f587ad96d01735ac85bf4b2ab4d1cb35b3b489c3cf2cc7f18"
    ),
    "cuda_nvrtc_runtime_version": [12, 2],
    "cuda_nvvm_resolved_path": (
        "/home/lestat/vendor/cuda-12.2.2/nvvm/lib64/libnvvm.so.4.0.0"
    ),
    "cuda_nvvm_sha256": (
        "b69eaddcce6a063361f2d172ed535c3d6f7ae494a40c6ffdb7de024f89dbf80a"
    ),
    "cuda_libdevice_resolved_path": (
        "/home/lestat/vendor/cuda-12.2.2/nvvm/libdevice/libdevice.10.bc"
    ),
    "cuda_libdevice_sha256": (
        "5c9f80bf689d5d0e67dabf914a2a865a3d8b8c5ff86b86c46f63c3bb067ca523"
    ),
    "cuda_toolkit_resolved_path": "/home/lestat/vendor/cuda-12.2.2",
    "modern_rtx_execution_authorized": False,
    "pod_used": False,
    "receipt_sha256": (
        "73fc385cabf2ea5b6cff70eb6d0fc31750cda206377015805c2935f02de6bb40"),
}
OUTPUT_CONTRACT = {
    "paper_algorithm": "RT-2A1",
    "reducer": "checked_u64_product_sum",
    "result": "exact_u64_triangle_count",
    "overflow": "fail_closed_before_provisional_sum_is_trusted",
}
TIMER_CONTRACTS = {
    "cold": {
        "included": [
            "graph_input_load_and_degree_oriented_csr",
            "restricted_callback_verify_compile_and_program_prepare",
            "bounded_device_geometry_production",
            "optix_execute_and_declared_downstream_reducer",
            "scalar_host_materialization_and_owner_close",
        ],
        "excluded": ["oracle_comparison", "receipt_serialization"],
    },
    "prepared": {
        "included": [
            "first_prepared_execute_only",
            "bounded_device_geometry_production",
            "optix_execute_and_declared_downstream_reducer",
            "scalar_host_materialization",
        ],
        "separately_reported": [
            "graph_load", "compile_and_prepare", "owner_close"],
        "excluded": ["oracle_comparison", "receipt_serialization"],
    },
    "bounded_smoke": {
        "functional_only": True,
        "registered_timing": False,
        "included": [],
        "excluded": [
            "all_elapsed_values", "oracle_comparison", "receipt_serialization"],
    },
}
EXPECTED_REQUIREMENTS = {
    "fusion_on": (
        ("checked_summary.kernel_launch", "compiler_kernel_invocation",
         1, 0, 0, 0, False, True),
        ("checked_summary.summary_copy_sync", "host_copy_synchronization",
         0, 4, 8, 0, True, True),
    ),
    "fusion_off": (
        ("maximum_weight.logical_reduce", "logical_reduction",
         1, 0, 0, 0, False, True),
        ("maximum_weight.scalar_copy_sync", "host_copy_synchronization",
         0, 1, 8, 0, True, True),
        ("weight_sum.logical_reduce", "logical_reduction",
         1, 0, 0, 0, False, True),
        ("weight_sum.scalar_copy_sync", "host_copy_synchronization",
         0, 1, 8, 0, True, True),
        ("weighted_product.materialize", "device_materialization",
         1, 0, 8, 0, False, True),
        ("weighted_product_sum.logical_reduce", "logical_reduction",
         1, 0, 0, 0, False, True),
        ("weighted_product_sum.scalar_copy_sync", "host_copy_synchronization",
         0, 1, 8, 0, True, True),
    ),
}
LOWERING_NODES = {
    "fusion_on": "checked_summary_kernel_then_one_summary_copy_sync",
    "fusion_off": "max_sum_materialize_product_sum_then_three_scalar_copy_sync",
}
REDUCTION_COUNTS = {
    "fusion_on": (1, 1, 0, 0),
    "fusion_off": (0, 3, 3, 1),
}
FUSION_ON_SOURCE_SHA256 = (
    "c2ff69bfbfd5739aa3b502466bedf4d28390025f819f5756c65fcaecd20a7e73"
)
FUSION_OFF_OPERATIONS = [
    "cp.max(weights)",
    "maximum_weight.item()",
    "cp.sum(weights,dtype=cp.uint64)",
    "weight_sum.item()",
    "values*weights",
    "cp.sum(weighted_product,dtype=cp.uint64)",
    "weighted_sum.item()",
]
VARIANT_PLAN_FIELDS = {
    "variant", "lowering_node", "downstream_operation_recipe_sha256",
    "operation_requirements", "plan_sha256",
}
VARIANT_PAYLOAD_ONLY_FIELDS = (
    VARIANT_PLAN_FIELDS - {"plan_sha256"}
) | {"only_allowlisted_difference"}
TARGET_AUTHORITY_FIELDS = {
    "schema", "shared_contract_freeze_sha256",
    "execution_source_archive_sha256", "execution_source_tree_sha256",
    "callback_ir_sha256", "provider_identity", "program_bundle_identity",
    "callback_authority_nonce", "contract_sha256", "abi_sha256",
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
    "traversable_mix", "pipeline_mix", "sbt_mix", "stream_mix",
    "params_mix", "callsite_mix", "first_program_bundle_id",
    "last_program_bundle_id", "first_traversable", "last_traversable",
    "pending_context_at_finish", "session_error",
    "incomplete_callsite_record_count", "incomplete_callsite_lines",
}
TRAVERSAL_CLAIM_RULES = {
    "provider_name_alone_proves_traversal": False,
    "selected_template_alone_proves_traversal": False,
    "successful_optix_launch_required": True,
    "nonzero_traversable_binding_required": True,
    "program_bundle_binding_required": True,
    "output_digest_bound": True,
}
SEGMENT_FIELDS = {
    "segment_id", "partition", "relation_count", "primitive_count",
    "query_count", "scalar_sum", "output_sha256", "fusion_ablation_plan",
    "operation_evidence_receipt", "checked_u64_weighted_reduction",
    "traversal_receipt", "traversal_semantic_binding",
    "device_phase_terminal_state",
    "evidence_phase_terminal_state", "evidence_sealed_after_device_phase",
}
LANE_FIELDS = {
    "schema", "status", "parent_pid", "input_kind", "dataset",
    "paper_algorithm", "variant", "lifecycle", "input_view",
    "input_contract", "input_sha256", "oracle_contract", "oracle_sha256",
    "output", "expected", "output_sha256", "matched",
    "native_library_sha256", "execution_source_archive_sha256",
    "execution_source_tree_sha256", "target_materialization_authority",
    "timer_contract", "timer_contract_sha256", "lifecycle_contract_sha256",
    "elapsed_values_recorded", "segments", "segment_count",
    "particle_included", "registered_performance_timing_created",
    "performance_claimed", "compiler_fusion_claimed",
    "home_timing_is_diagnostic_only", "formal_worker", "pod_used",
    "execution_environment_class", "home_machine_authority",
    "home_machine_authority_sha256",
    "downstream_operation_recipe_scope",
    "opaque_compiled_binary_attestation_claimed",
    "two_phase_execution_evidence_seal_enforced",
    "evidence_hashing_or_serialization_inside_registered_timer",
    "ptx_producer_observation", "ptx_program_identity",
    "ptx_program_identity_sha256",
}
SHA_RE = re.compile(r"[0-9a-f]{64}")
NONCE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{15,255}")
U64_MAX = (1 << 64) - 1


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ensure_ascii=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _sha256(value: object, label: str) -> str:
    _require(isinstance(value, str) and SHA_RE.fullmatch(value) is not None,
             f"invalid {label}")
    return value


def _u64(value: object, label: str) -> int:
    _require(isinstance(value, int) and not isinstance(value, bool)
             and 0 <= value <= U64_MAX, f"invalid {label}")
    return value


def _program_bundle_id(name: str) -> int:
    value = 1469598103934665603
    for byte in name.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & U64_MAX
    return value


def _triangle_count(raw_edges: list[list[int]]) -> int:
    edges: set[tuple[int, int]] = set()
    for index, row in enumerate(raw_edges):
        _require(isinstance(row, list) and len(row) == 2,
                 f"raw edge {index} is not a pair")
        left, right = row
        _require(isinstance(left, int) and not isinstance(left, bool)
                 and isinstance(right, int) and not isinstance(right, bool)
                 and 0 <= left < (1 << 31) and 0 <= right < (1 << 31),
                 f"raw edge {index} is outside nonnegative i32")
        if left != right:
            edges.add((min(left, right), max(left, right)))
    adjacency: dict[int, set[int]] = {}
    for left, right in edges:
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)
    total = 0
    for left, right in edges:
        total += sum(1 for third in adjacency[left].intersection(adjacency[right])
                     if third > right)
    return total


def _verify_input_view(
    row: dict[str, object], oracle_cache: dict[str, int],
) -> tuple[int, str, int]:
    value = row.get("input_view")
    _require(isinstance(value, dict), "input view missing")
    expected_fields = {
        "schema", "input_kind", "dataset", "edge_record_encoding",
        "source_mode", "original_full_edge_filename",
        "original_full_edge_sha256",
        "original_full_edge_size_bytes", "prefix_rule",
        "requested_prefix_edge_record_count", "actual_edge_record_count",
        "bounded_view_edge_sha256", "bounded_view_edge_size_bytes", "raw_edges",
    }
    _require(set(value) == expected_fields, "input-view fields drift")
    _require(value.get("schema") == "rtdl.goal5790.bounded_triangle_input.v1"
             and value.get("input_kind") == row.get("input_kind")
             and value.get("dataset") == row.get("dataset")
             and value.get("edge_record_encoding") == "little_endian_i32_pair",
             "input-view identity drift")
    raw_edges = value.get("raw_edges")
    _require(isinstance(raw_edges, list) and raw_edges,
             "input view has no shipped raw edges")
    payload_parts = []
    for index, edge in enumerate(raw_edges):
        _require(isinstance(edge, list) and len(edge) == 2,
                 f"raw edge {index} is not a pair")
        left, right = edge
        _require(isinstance(left, int) and not isinstance(left, bool)
                 and isinstance(right, int) and not isinstance(right, bool)
                 and 0 <= left < (1 << 31) and 0 <= right < (1 << 31),
                 f"raw edge {index} is outside nonnegative i32")
        payload_parts.append(struct.pack("<ii", left, right))
    payload = b"".join(payload_parts)
    edge_sha = hashlib.sha256(payload).hexdigest()
    _require(value.get("actual_edge_record_count") == len(raw_edges)
             and value.get("bounded_view_edge_size_bytes") == len(payload)
             and value.get("bounded_view_edge_sha256") == edge_sha,
             "bounded-view byte identity mismatch")
    dataset = row.get("dataset")
    if row.get("input_kind") == "small":
        expected_edges = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
        _require(dataset == SMALL_DATASET and raw_edges == expected_edges
                 and value.get("source_mode") == "inline_fixture"
                  and value.get("prefix_rule") == "entire_inline_fixture"
                 and value.get("requested_prefix_edge_record_count") == 6
                  and value.get("original_full_edge_sha256") == edge_sha
                  and value.get("original_full_edge_filename") == "small_k4.edge"
                 and value.get("original_full_edge_size_bytes") == len(payload),
                 "small fixture identity drift")
    else:
        _require(dataset in REAL_DATASETS, "unknown bounded-real dataset")
        identity = REAL_DATASETS[str(dataset)]
        _require(value.get("source_mode") == "frozen_full_file_prefix"
                 and value.get("prefix_rule") == REAL_PREFIX_RULE
                 and value.get("requested_prefix_edge_record_count")
                    == PREFIX_EDGE_RECORD_COUNT
                 and len(raw_edges) == PREFIX_EDGE_RECORD_COUNT
                  and edge_sha == identity["prefix_sha256"]
                  and value.get("original_full_edge_filename")
                     == identity["filename"]
                 and value.get("original_full_edge_sha256") == identity["sha256"]
                 and value.get("original_full_edge_size_bytes")
                    == identity["size_bytes"],
                 "bounded-real source/prefix identity drift")
    # Every ON/OFF pair ships and rehashes its own raw view.  The expensive
    # graph oracle is pure in those verified bytes, so recompute it only once
    # per exact view digest rather than wasting Home time on identical arms.
    if edge_sha not in oracle_cache:
        oracle_cache[edge_sha] = _triangle_count(raw_edges)
    count = oracle_cache[edge_sha]
    if row.get("input_kind") == "bounded_real":
        _require(count == REAL_DATASETS[str(dataset)]["prefix_triangle_count"],
                 "bounded-real independent oracle drift")
    return count, edge_sha, len(payload)


def _expected_downstream_recipe(
    variant: str, *, target_identity_sha256: str, cupy_version: str,
) -> dict[str, object]:
    _require(variant in VARIANTS, "unknown downstream recipe variant")
    implementation = (
        {
            "kind": "compiler_owned_rawkernel_recipe",
            "entry": "rtdl_v4_checked_u64_weighted_reduce",
            "source_sha256": FUSION_ON_SOURCE_SHA256,
            "options": ["-std=c++11"],
            "opaque_partner_kernel_binary_claimed": False,
        }
        if variant == "fusion_on"
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


def _verify_target_authority(value: dict[str, object]) -> str:
    _require(set(value) == TARGET_AUTHORITY_FIELDS,
             "target materialization authority fields drift")
    _require(value.get("schema") == "rtdl.v4.target_materialization_authority.v2"
             and value.get("shared_contract_freeze_sha256")
                == FROZEN_PLAN_IDENTITIES["shared_contract_freeze_sha256"]
             and value.get("provider_identity") == "optix"
             and value.get("program_bundle_identity") == PROGRAM_BUNDLE,
             "target authority frozen identity drift")
    _require(value.get("native_library_sha256")
             == value.get("native_payload_sha256"),
             "native/preserved-payload identity mismatch")
    target_identity = _sha256(
        value.get("target_identity_sha256"), "target identity")
    cupy_version = value.get("cupy_version")
    _require(isinstance(cupy_version, str) and 0 < len(cupy_version) <= 64,
             "target CuPy version invalid")
    expected_recipes = {
        variant: _expected_downstream_recipe(
            variant, target_identity_sha256=target_identity,
            cupy_version=cupy_version)
        for variant in VARIANTS
    }
    for variant in VARIANTS:
        prefix = "fusion_on" if variant == "fusion_on" else "fusion_off"
        recipe = value.get(prefix + "_downstream_operation_recipe")
        claimed = value.get(prefix + "_downstream_operation_recipe_sha256")
        _require(recipe == expected_recipes[variant]
                 and claimed == _digest(expected_recipes[variant]),
                 f"{variant} structured recipe reconstruction mismatch")
    _require(value.get("fusion_on_downstream_operation_recipe_sha256")
             != value.get("fusion_off_downstream_operation_recipe_sha256"),
             "ON/OFF operation recipes are not distinct")
    _require(value.get("actual_native_rehashed_from_preserved_payload") is True
             and value.get("actual_source_tree_recounted_from_preserved_archive")
                is True
             and value.get("cross_target_native_byte_reproducibility_claimed")
                is False,
             "target materialization boundary drift")
    for name in {
        "shared_contract_freeze_sha256", "execution_source_archive_sha256",
        "execution_source_tree_sha256", "callback_ir_sha256",
        "contract_sha256", "abi_sha256", "composed_program_sha256",
        "fusion_on_downstream_operation_recipe_sha256",
        "fusion_off_downstream_operation_recipe_sha256",
        "native_library_sha256", "native_payload_sha256",
        "target_identity_sha256", "materializer_source_sha256",
        "source_manifest_sha256", "evidence_archive_sha256",
    }:
        _sha256(value.get(name), "target authority " + name)
    _require(isinstance(value.get("callback_authority_nonce"), str)
             and NONCE_RE.fullmatch(
                 str(value["callback_authority_nonce"])) is not None,
             "callback authority nonce invalid")
    _require(isinstance(value.get("materialization_nonce"), str)
             and NONCE_RE.fullmatch(str(value["materialization_nonce"])) is not None,
             "target materialization nonce invalid")
    claimed = _sha256(value.get("receipt_sha256"), "target receipt digest")
    unsigned = dict(value)
    unsigned.pop("receipt_sha256")
    _require(_digest(unsigned) == claimed, "target materialization digest mismatch")
    return claimed


def _verify_ptx_producer_observation(
    value: object, target: dict[str, object],
) -> None:
    fields = {
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
    }
    _require(isinstance(value, dict) and set(value) == fields,
             "PTX producer observation fields drift")
    toolkit = HOME_MACHINE_AUTHORITY["cuda_toolkit_resolved_path"]
    exact_nvrtc = sorted((
        HOME_MACHINE_AUTHORITY["cuda_nvrtc_resolved_path"],
        HOME_MACHINE_AUTHORITY["cuda_nvrtc_builtins_resolved_path"],
    ))
    directives = value.get("numba_probe_ptx_directives")
    _require(
        value.get("schema")
            == "rtdl.goal5790.home_ptx_producer_observation.v1"
        and value.get("cuda_home") == toolkit
        and value.get("cuda_path") == toolkit
        and value.get("numba_selected_nvvm_by") == "CUDA_HOME"
        and value.get("numba_selected_nvvm_path")
            == HOME_MACHINE_AUTHORITY["cuda_nvvm_resolved_path"]
        and value.get("numba_selected_nvvm_sha256")
            == HOME_MACHINE_AUTHORITY["cuda_nvvm_sha256"]
        and value.get("numba_selected_libdevice_by") == "CUDA_HOME"
        and value.get("numba_selected_libdevice_path")
            == HOME_MACHINE_AUTHORITY["cuda_libdevice_resolved_path"]
        and value.get("numba_selected_libdevice_sha256")
            == HOME_MACHINE_AUTHORITY["cuda_libdevice_sha256"]
        and value.get("loaded_nvvm_paths")
            == [HOME_MACHINE_AUTHORITY["cuda_nvvm_resolved_path"]]
        and value.get("cupy_nvrtc_runtime_version")
            == HOME_MACHINE_AUTHORITY["cuda_nvrtc_runtime_version"]
        and value.get("loaded_nvrtc_family_paths") == exact_nvrtc
        and value.get("nvrtc_probe_output") == 5790
        and value.get("cupy") == target["cupy_version"]
        and isinstance(directives, dict)
        and set(directives) == {"version", "target", "address_size"}
        and directives.get("target") == "sm_61"
        and directives.get("address_size") == "64"
        and value.get("elapsed_values_recorded") is False
        and value.get("application_input_used") is False
        and value.get("registered_performance_timing_created") is False,
        "PTX producer observation identity/boundary drift",
    )
    for name in ("numba_probe_ptx_sha256", "nvrtc_probe_source_sha256"):
        _sha256(value.get(name), "PTX producer " + name)
    for name in ("python", "numba", "numpy", "llvmlite", "cupy"):
        _require(isinstance(value.get(name), str) and value[name],
                 f"PTX producer version missing: {name}")


def _verify_ptx_program_identity(
    value: object, claimed_sha256: object, target: dict[str, object],
) -> str:
    _require(isinstance(value, dict) and set(value) == {
        "schema", "wrapper", "ordered_leaves", "composed",
        "composer_leaf_bindings",
        "wrapper_leaf_composed_directive_equality_verified",
    }, "PTX program identity fields drift")
    _require(value.get("schema") == "rtdl.goal5790.ptx_program_identity.v1"
             and value.get("wrapper_leaf_composed_directive_equality_verified")
                is True,
             "PTX program identity schema/equality drift")
    wrapper = value.get("wrapper")
    composed = value.get("composed")
    leaves = value.get("ordered_leaves")
    bindings = value.get("composer_leaf_bindings")
    _require(isinstance(wrapper, dict) and set(wrapper) == {
        "ptx_sha256", "directives"}, "wrapper PTX identity drift")
    _require(isinstance(composed, dict) and set(composed) == {
        "ptx_sha256", "directives"}, "composed PTX identity drift")
    _require(isinstance(leaves, list) and leaves
             and isinstance(bindings, list) and len(bindings) == len(leaves),
             "leaf PTX identity cardinality drift")
    common = composed.get("directives")
    _require(isinstance(common, dict)
             and set(common) == {"version", "target", "address_size"}
             and common.get("target") == "sm_61"
             and common.get("address_size") == "64"
             and wrapper.get("directives") == common,
             "wrapper/composed PTX directive drift")
    _sha256(wrapper.get("ptx_sha256"), "wrapper PTX")
    _require(composed.get("ptx_sha256") == target["composed_program_sha256"],
             "composed PTX/target authority digest mismatch")
    roles: set[str] = set()
    for index, leaf in enumerate(leaves):
        _require(isinstance(leaf, dict) and set(leaf) == {
            "role", "abi_name", "ptx_sha256", "directives"},
            "leaf PTX identity fields drift")
        role = leaf.get("role")
        abi_name = leaf.get("abi_name")
        _require(isinstance(role, str) and role and role not in roles
                 and isinstance(abi_name, str) and abi_name
                 and leaf.get("directives") == common
                 and bindings[index] == [role, abi_name],
                 "leaf PTX role/symbol/directive binding drift")
        roles.add(role)
        _sha256(leaf.get("ptx_sha256"), "leaf PTX")
    claimed = _sha256(claimed_sha256, "PTX program identity")
    _require(_digest(value) == claimed, "PTX program identity digest mismatch")
    return claimed


def _requirements_as_dict(variant: str) -> list[dict[str, object]]:
    result = []
    for index, requirement in enumerate(EXPECTED_REQUIREMENTS[variant]):
        (operation_id, kind, units_per_value, fixed_units, bytes_per_unit,
         fixed_bytes, host_boundary, compiler_visible_only) = requirement
        result.append({
            "ordinal": index, "operation_id": operation_id, "kind": kind,
            "units_per_value": units_per_value, "fixed_units": fixed_units,
            "bytes_per_unit": bytes_per_unit, "fixed_bytes": fixed_bytes,
            "host_visibility_boundary": host_boundary,
            "compiler_visible_only": compiler_visible_only,
        })
    return result


def _verify_plan(
    plan: dict[str, object], *, variant: str, target: dict[str, object],
    row: dict[str, object], segment_input_sha: str, query_count: int,
) -> None:
    _require(set(plan) == PLAN_FIELDS, "plan fields drift")
    _require(plan.get("schema") == "rtdl.v4.fusion_ablation_plan.v2"
             and plan.get("mechanism_id") == MECHANISM
             and plan.get("variant") == variant,
             "plan schema/mechanism/variant drift")
    for name, expected in FROZEN_PLAN_IDENTITIES.items():
        _require(plan.get(name) == expected, f"plan frozen identity drift: {name}")
    _require(plan.get("executable_family_id") == FAMILY_ID
             and plan.get("provider_identity") == "optix"
             and plan.get("program_bundle_identity") == PROGRAM_BUNDLE
             and plan.get("same_semantic_ir_required") is True
             and plan.get("same_optix_producer_required") is True
             and plan.get("performance_or_timing_claimed") is False
             and plan.get("variant_selected_from_app_dataset_result_or_timing")
                is False
             and plan.get("executable") is False
             and plan.get("only_allowlisted_difference") == ALLOWLIST
             and plan.get("lowering_node") == LOWERING_NODES[variant],
             "plan frozen provider/boundary drift")
    authority_bindings = {
        "execution_source_archive_sha256": "execution_source_archive_sha256",
        "execution_source_tree_sha256": "execution_source_tree_sha256",
        "callback_ir_sha256": "callback_ir_sha256",
        "callback_authority_nonce": "callback_authority_nonce",
        "contract_sha256": "contract_sha256",
        "abi_sha256": "abi_sha256",
        "native_library_sha256": "native_library_sha256",
        "composed_program_sha256": "composed_program_sha256",
        "cupy_version": "cupy_version",
        "fusion_on_downstream_operation_recipe": (
            "fusion_on_downstream_operation_recipe"),
        "fusion_off_downstream_operation_recipe": (
            "fusion_off_downstream_operation_recipe"),
        "fusion_on_downstream_operation_recipe_sha256": (
            "fusion_on_downstream_operation_recipe_sha256"),
        "fusion_off_downstream_operation_recipe_sha256": (
            "fusion_off_downstream_operation_recipe_sha256"),
        "target_identity_sha256": "target_identity_sha256",
        "target_materialization_receipt_sha256": "receipt_sha256",
        "materializer_source_sha256": "materializer_source_sha256",
        "source_manifest_sha256": "source_manifest_sha256",
        "materialization_evidence_archive_sha256": "evidence_archive_sha256",
        "materialization_nonce": "materialization_nonce",
    }
    for plan_name, target_name in authority_bindings.items():
        _require(plan.get(plan_name) == target.get(target_name),
                 f"plan/target authority mismatch: {plan_name}")
    selected = target[
        "fusion_on_downstream_operation_recipe_sha256"
        if variant == "fusion_on"
        else "fusion_off_downstream_operation_recipe_sha256"]
    _require(plan.get("downstream_operation_recipe_sha256") == selected,
             "plan selected operation recipe mismatch")
    target_identity = str(target["target_identity_sha256"])
    cupy_version = str(target["cupy_version"])
    for recipe_variant in VARIANTS:
        prefix = (
            "fusion_on" if recipe_variant == "fusion_on" else "fusion_off")
        expected_recipe = _expected_downstream_recipe(
            recipe_variant, target_identity_sha256=target_identity,
            cupy_version=cupy_version)
        _require(plan.get(prefix + "_downstream_operation_recipe")
                 == expected_recipe
                 and plan.get(prefix + "_downstream_operation_recipe_sha256")
                    == _digest(expected_recipe),
                 f"plan {recipe_variant} recipe reconstruction mismatch")
    _require(plan.get("input_sha256") == segment_input_sha
             and plan.get("output_contract_sha256") == _digest(OUTPUT_CONTRACT)
             and plan.get("oracle_sha256") == row.get("oracle_sha256")
             and plan.get("timer_contract_sha256")
                == row.get("timer_contract_sha256")
             and plan.get("lifecycle_contract_sha256")
                == row.get("lifecycle_contract_sha256")
             and plan.get("value_count") == query_count,
             "plan dynamic identity/value-count mismatch")
    requirements = _requirements_as_dict(variant)
    _require(plan.get("operation_requirements") == requirements,
             "plan operation requirement content mismatch")
    variant_payload = dict(plan)
    claimed_shared = _sha256(
        variant_payload.pop("shared_identity_sha256", None), "shared plan digest")
    claimed_plan = _sha256(
        variant_payload.pop("plan_sha256", None), "variant plan digest")
    _require(_digest(variant_payload) == claimed_plan, "variant plan digest mismatch")
    common = dict(variant_payload)
    for name in VARIANT_PAYLOAD_ONLY_FIELDS:
        common.pop(name, None)
    _require(_digest(common) == claimed_shared, "shared plan digest mismatch")


def _operation_contract(plan: dict[str, object]) -> dict[str, object]:
    return {
        "schema": "rtdl.v4.operation_sequence_contract.v1",
        "plan_sha256": plan["plan_sha256"], "mechanism_id": MECHANISM,
        "variant": plan["variant"],
        "declared_value_count": plan["value_count"],
        "requirements": plan["operation_requirements"],
        "tcb_statement": OPERATION_TCB, "timing_or_duration_recorded": False,
        "hardware_introspection_claimed": False,
    }


def _verify_operation_receipt(
    receipt: dict[str, object], plan: dict[str, object],
    traversal: dict[str, object], *, variant: str, query_count: int,
    output_sha: str, expected_execution_nonce: str,
) -> None:
    contract_sha = _digest(_operation_contract(plan))
    _require(set(receipt) == OPERATION_RECEIPT_FIELDS,
             "operation receipt fields drift")
    _require(receipt.get("schema") == "rtdl.v4.operation_evidence_receipt.v1"
             and receipt.get("contract_sha256") == contract_sha
             and receipt.get("plan_sha256") == plan.get("plan_sha256")
             and receipt.get("mechanism_id") == MECHANISM
             and receipt.get("variant") == variant
             and receipt.get("value_count") == query_count
             and receipt.get("output_sha256") == output_sha,
             "operation receipt contract/value/output binding mismatch")
    _require(receipt.get("execution_nonce") == expected_execution_nonce
             and NONCE_RE.fullmatch(expected_execution_nonce) is not None,
             "operation receipt nonce/replay binding invalid")
    _require(receipt.get("event_evidence_tcb") == OPERATION_TCB
             and receipt.get("timing_or_duration_recorded") is False
             and receipt.get("hardware_introspection_claimed") is False
             and receipt.get("opaque_partner_kernel_count_claimed") is False,
             "operation evidence boundary drift")
    _require(receipt.get("traversal_receipt_sha256")
             == traversal.get("receipt_sha256"),
             "operation/traversal digest binding mismatch")
    requirements = plan["operation_requirements"]
    events = receipt.get("events")
    _require(isinstance(events, list) and len(events) == len(requirements)
             and receipt.get("successful_event_count") == len(events),
             "operation event cardinality mismatch")
    previous = contract_sha
    for index, (event, requirement) in enumerate(zip(
            events, requirements, strict=True)):
        _require(isinstance(event, dict) and set(event) == OPERATION_EVENT_FIELDS,
                 f"operation event {index} fields drift")
        units = requirement["units_per_value"] * query_count \
            + requirement["fixed_units"]
        byte_count = requirement["bytes_per_unit"] * units \
            + requirement["fixed_bytes"]
        expected = {
            "schema": "rtdl.v4.operation_evidence_event.v1",
            "sequence": index, "operation_id": requirement["operation_id"],
            "kind": requirement["kind"], "accounted_units": units,
            "accounted_bytes": byte_count, "previous_event_sha256": previous,
            "recorded_after_callable_success": True,
        }
        _require({key: event.get(key) for key in expected} == expected,
                 f"operation event {index} content mismatch")
        previous = _digest(expected)
        _require(event.get("event_sha256") == previous,
                 f"operation event {index} digest mismatch")
    _require(receipt.get("event_chain_sha256") == previous,
             "operation event chain mismatch")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    _require(_digest(unsigned) == claimed, "operation receipt digest mismatch")


def _receipt_ok(
    receipt: dict[str, object], *, output_sha: str,
    expected_native_sha256: str, query_count: int,
    semantic_binding: dict[str, object],
) -> bool:
    snapshot = receipt.get("native_snapshot")
    if not isinstance(snapshot, dict):
        return False
    try:
        successful = int(snapshot["successful_launch_count"])
        attempted = int(snapshot["attempted_launch_count"])
        bundle_id = _program_bundle_id(PROGRAM_BUNDLE)
        claimed = receipt.get("receipt_sha256")
        unsigned = dict(receipt)
        unsigned.pop("receipt_sha256", None)
        nonce = receipt.get("nonce")
        expected_semantic_fields = {
            "authority", "contract", "abi", "composed_ptx", "native",
            "device_column_count",
        }
        return (
            set(receipt) == TRAVERSAL_RECEIPT_FIELDS
            and set(snapshot) == TRAVERSAL_SNAPSHOT_FIELDS
            and receipt.get("schema")
                == "rtdl.physical_execution.traversal_receipt.v1"
            and receipt.get("provider_library") == "librtdl_optix"
            and isinstance(receipt.get("provider_library_path"), str)
            and bool(receipt.get("provider_library_path"))
            and receipt.get("provider_library_sha256")
                == expected_native_sha256
            and receipt.get("route_identity")
                == "v4_builtin_triangle_callback_ir:partner_resident_checked_count_v1"
            and set(semantic_binding) == expected_semantic_fields
            and isinstance(semantic_binding.get("authority"), str)
            and bool(semantic_binding.get("authority"))
            and all(
                isinstance(semantic_binding.get(name), str)
                and SHA_RE.fullmatch(str(semantic_binding[name])) is not None
                for name in ("contract", "abi", "composed_ptx", "native")
            )
            and semantic_binding.get("native") == expected_native_sha256
            and semantic_binding.get("device_column_count") is True
            and receipt.get("semantic_digest") == _digest(semantic_binding)
            and receipt.get("physical_executor_classification")
                == "optix_traversal_observed"
            and receipt.get("output_digest") == output_sha
            and isinstance(nonce, dict) and set(nonce) == {"hi", "lo"}
            and nonce.get("hi") == snapshot.get("nonce_hi")
            and nonce.get("lo") == snapshot.get("nonce_lo")
            and receipt.get("expected_program_bundles") == [PROGRAM_BUNDLE]
            and receipt.get("expected_program_bundle_ids") == [bundle_id]
            and receipt.get("expected_program_observed_at_receipt_edge") is True
            and receipt.get("claim_rules") == TRAVERSAL_CLAIM_RULES
            and successful > 0
            and attempted == successful
            and int(snapshot["complete_context_launch_count"]) == successful
            and all(int(snapshot.get(name, -1)) == 0 for name in (
                "failed_launch_count", "incomplete_context_launch_count",
                "pending_context_at_finish", "session_error",
                "incomplete_callsite_record_count",
            ))
            and int(snapshot["context_bind_count"]) >= successful
            and int(snapshot["raygen_invocation_count"]) == query_count
            and int(snapshot["first_program_bundle_id"]) == bundle_id
            and int(snapshot["last_program_bundle_id"]) == bundle_id
            and bool(snapshot.get("first_traversable"))
            and bool(snapshot.get("last_traversable"))
            and isinstance(snapshot.get("incomplete_callsite_lines"), list)
            and len(snapshot["incomplete_callsite_lines"]) == 32
            and all(int(value) == 0
                    for value in snapshot["incomplete_callsite_lines"])
            and isinstance(claimed, str) and _digest(unsigned) == claimed
        )
    except (KeyError, TypeError, ValueError):
        return False


def _verify_semantic_binding_against_target(
    semantic_binding: dict[str, object], target: dict[str, object],
) -> None:
    _require(
        semantic_binding.get("authority") == target["callback_authority_nonce"]
        and semantic_binding.get("contract") == target["contract_sha256"]
        and semantic_binding.get("abi") == target["abi_sha256"]
        and semantic_binding.get("composed_ptx")
            == target["composed_program_sha256"]
        and semantic_binding.get("native") == target["native_library_sha256"],
        "traversal semantic binding/target authority mismatch",
    )


def _verify_reduction(
    value: dict[str, object], *, variant: str, query_count: int,
    primitive_count: int, scalar_sum: int,
) -> None:
    expected_fields = {
        "schema", "maximum_value", "maximum_weight", "weight_sum",
        "value_count", "value_upper_bound", "device_kernel_launch_count",
        "host_synchronization_count", "logical_reduction_count",
        "device_materialization_count", "operation_counts_event_derived",
        "maximum_value_is_device_observed", "maximum_value_provenance",
        "provisional_sum_trusted_only_after_bounds",
    }
    _require(set(value) == expected_fields
             and value.get("schema")
                == "rtdl.v4.checked_u64_weighted_reduction.receipt.v1",
             "checked-U64 reduction receipt fields/schema drift")
    maximum_value = _u64(value.get("maximum_value"), "maximum value")
    maximum_weight = _u64(value.get("maximum_weight"), "maximum weight")
    weight_sum = _u64(value.get("weight_sum"), "weight sum")
    _require(value.get("value_count") == query_count
             and value.get("value_upper_bound") == primitive_count
             and maximum_value <= primitive_count
             and (maximum_weight == 0 or maximum_value <= U64_MAX // maximum_weight)
             and (weight_sum == 0 or primitive_count <= U64_MAX // weight_sum)
             and scalar_sum <= primitive_count * weight_sum,
             "checked-U64 reduction bounds/value-count drift")
    actual_counts = (
        value.get("device_kernel_launch_count"),
        value.get("host_synchronization_count"),
        value.get("logical_reduction_count"),
        value.get("device_materialization_count"),
    )
    expected_device_observed = variant == "fusion_on"
    expected_provenance = (
        "device_observed" if expected_device_observed
        else "optix_producer_declared_primitive_bound"
    )
    _require(actual_counts == REDUCTION_COUNTS[variant]
             and value.get("operation_counts_event_derived") is True
             and value.get("maximum_value_is_device_observed")
                is expected_device_observed
             and value.get("maximum_value_provenance") == expected_provenance
             and (expected_device_observed or maximum_value == primitive_count)
             and value.get("provisional_sum_trusted_only_after_bounds") is True,
             "checked-U64 operation-count/evidence drift")


def _expected_keys() -> set[tuple[str, str, str, str]]:
    result = {
        ("small", SMALL_DATASET, lifecycle, variant)
        for lifecycle in ("cold", "prepared") for variant in VARIANTS
    }
    result.update({
        ("bounded_real", dataset, "bounded_smoke", variant)
        for dataset in REAL_DATASETS for variant in VARIANTS
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--expected-native-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.raw.resolve()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    expected_native = _sha256(
        args.expected_native_sha256.lower(), "expected native digest")
    paths = sorted(raw.glob("*.json"))
    _require(len(paths) == 10, f"expected 10 raw lanes, got {len(paths)}")
    rows: dict[tuple[str, str, str, str], dict[str, object]] = {}
    pids: set[int] = set()
    authority_sha = None
    target_authority: dict[str, object] | None = None
    ptx_program_identity_sha = None
    source_archive_sha = source_tree_sha = None
    total_traversals = total_operations = total_events = 0
    operation_receipts_by_variant = {variant: 0 for variant in VARIANTS}
    operation_events_by_variant = {variant: 0 for variant in VARIANTS}
    bounded_oracles: dict[str, int] = {}
    oracle_cache: dict[str, int] = {}
    for path in paths:
        row = json.loads(path.read_text(encoding="utf-8"))
        _require(isinstance(row, dict) and set(row) == LANE_FIELDS,
                 f"lane fields drift: {path.name}")
        _require(row.get("schema") == "rtdl.goal5790.home_functional_lane.v1"
                 and row.get("status")
                    == "PASS__FUNCTIONAL_OPERATION_EVIDENCE_ONLY",
                 f"lane schema/status drift: {path.name}")
        key = (str(row.get("input_kind")), str(row.get("dataset")),
               str(row.get("lifecycle")), str(row.get("variant")))
        _require(key in _expected_keys() and key not in rows,
                 f"unknown/duplicate lane identity: {key!r}")
        _require(row.get("paper_algorithm") == "RT-2A1"
                 and row.get("particle_included") is False,
                 "Goal5790 scope drifted beyond weighted RT-2A1")
        _require(row.get("registered_performance_timing_created") is False
                 and row.get("performance_claimed") is False
                 and row.get("compiler_fusion_claimed") is False
                 and row.get("home_timing_is_diagnostic_only") is True
                 and row.get("formal_worker") is False
                 and row.get("pod_used") is False
                 and row.get("elapsed_values_recorded") is False,
                 "Home functional lane created timing/performance evidence")
        _require(
            row.get("execution_environment_class")
                == "HOME_PASCAL_FUNCTIONAL_ONLY"
            and row.get("home_machine_authority") == HOME_MACHINE_AUTHORITY
            and row.get("home_machine_authority_sha256")
                == HOME_MACHINE_AUTHORITY["receipt_sha256"],
            "Home functional lane is not bound to frozen lx1 identity",
        )
        _require(row.get("downstream_operation_recipe_scope")
                 == "source_dependency_target_recipe__not_opaque_compiled_binary"
                 and row.get("opaque_compiled_binary_attestation_claimed") is False
                 and row.get("two_phase_execution_evidence_seal_enforced") is True
                 and row.get(
                     "evidence_hashing_or_serialization_inside_registered_timer"
                 ) is False,
                 "downstream recipe was overclaimed as compiled binary attestation")
        oracle_count, edge_sha, edge_size = _verify_input_view(row, oracle_cache)
        bounded_oracles[str(row["dataset"])] = oracle_count
        view = row["input_view"]
        expected_input = {
            "dataset": row["dataset"], "input_kind": row["input_kind"],
            "edge_file_sha256": edge_sha, "edge_file_bytes": edge_size,
            "original_full_edge_filename": view[
                "original_full_edge_filename"],
            "original_full_edge_sha256": view["original_full_edge_sha256"],
            "original_full_edge_size_bytes": view["original_full_edge_size_bytes"],
            "bounded_prefix_rule": view["prefix_rule"],
            "bounded_prefix_edge_record_count": view[
                "requested_prefix_edge_record_count"],
            "paper_algorithm": "RT-2A1", "max_relation_rows": 1_000_000,
            "expected_triangle_count": oracle_count,
        }
        expected_oracle = {
            "authority": ORACLE_AUTHORITY, "dataset": row["dataset"],
            "original_full_edge_filename": view[
                "original_full_edge_filename"],
            "original_full_edge_sha256": view["original_full_edge_sha256"],
            "edge_file_sha256": edge_sha,
            "raw_edges_sha256": _digest(view["raw_edges"]),
            "expected_triangle_count": oracle_count,
        }
        _require(row.get("input_contract") == expected_input
                 and row.get("input_sha256") == _digest(expected_input)
                 and row.get("oracle_contract") == expected_oracle
                 and row.get("oracle_sha256") == _digest(expected_oracle),
                 "input/oracle contract reconstruction mismatch")
        lifecycle = str(row["lifecycle"])
        lifecycle_contract = {
            "lifecycle": lifecycle, "fresh_parent_pid": True,
            "first_prepared_execute_only": lifecycle == "prepared",
            "complete_endpoint": lifecycle == "cold",
            "bounded_functional_smoke_only": lifecycle == "bounded_smoke",
        }
        _require(row.get("timer_contract") == TIMER_CONTRACTS[lifecycle]
                 and row.get("timer_contract_sha256")
                    == _digest(TIMER_CONTRACTS[lifecycle])
                 and row.get("lifecycle_contract_sha256")
                    == _digest(lifecycle_contract),
                 "timer/lifecycle contract mismatch")
        output = _u64(row.get("output"), "lane output")
        _require(output == oracle_count and row.get("expected") == oracle_count
                 and row.get("matched") is True
                 and row.get("output_sha256") == _digest(output),
                 f"lane oracle/output mismatch: {path.name}")
        _require(row.get("native_library_sha256") == expected_native,
                 f"native mismatch: {path.name}")
        pid = row.get("parent_pid")
        _require(isinstance(pid, int) and pid > 0 and pid not in pids,
                 f"non-fresh/invalid parent PID: {path.name}")
        pids.add(pid)
        target = row.get("target_materialization_authority")
        _require(isinstance(target, dict), "target authority missing")
        target_digest = _verify_target_authority(target)
        _require(target.get("native_library_sha256") == expected_native,
                 "target authority native mismatch")
        if authority_sha is None:
            authority_sha, target_authority = target_digest, target
            source_archive_sha = target["execution_source_archive_sha256"]
            source_tree_sha = target["execution_source_tree_sha256"]
        _require(target_digest == authority_sha and target == target_authority,
                  "more than one target materialization authority")
        _verify_ptx_producer_observation(
            row.get("ptx_producer_observation"), target)
        ptx_identity_sha = _verify_ptx_program_identity(
            row.get("ptx_program_identity"),
            row.get("ptx_program_identity_sha256"), target)
        _require(
            row["ptx_producer_observation"]["numba_probe_ptx_directives"]
                == row["ptx_program_identity"]["composed"]["directives"],
            "probe/program PTX directive identity mismatch",
        )
        if ptx_program_identity_sha is None:
            ptx_program_identity_sha = ptx_identity_sha
        _require(ptx_identity_sha == ptx_program_identity_sha,
                 "more than one PTX program identity")
        _require(row.get("execution_source_archive_sha256") == source_archive_sha
                 and row.get("execution_source_tree_sha256") == source_tree_sha,
                 "lane source identity drift")
        segments = row.get("segments")
        _require(isinstance(segments, list) and segments
                 and row.get("segment_count") == len(segments),
                 f"lane segment evidence missing/cardinality drift: {path.name}")
        scalar_total = 0
        for index, segment in enumerate(segments):
            _require(isinstance(segment, dict) and set(segment) == SEGMENT_FIELDS,
                     f"segment {index} fields drift")
            _require(segment.get("segment_id") == index,
                     f"segment {index} ID/order drift")
            _require(
                segment.get("device_phase_terminal_state")
                    == "device_complete_unsealed"
                and segment.get("evidence_phase_terminal_state") == "sealed"
                and segment.get("evidence_sealed_after_device_phase") is True,
                f"segment {index} two-phase evidence boundary drift",
            )
            relation_count = _u64(segment.get("relation_count"), "relation count")
            primitive_count = _u64(segment.get("primitive_count"), "primitive count")
            query_count = _u64(segment.get("query_count"), "query count")
            _require(relation_count > 0 and primitive_count > 0 and query_count > 0,
                     f"segment {index} has empty physical domain")
            scalar = _u64(segment.get("scalar_sum"), "segment scalar")
            _require(scalar_total <= U64_MAX - scalar,
                     "segmented lane U64 sum overflow")
            scalar_total += scalar
            segment_output_sha = _digest(scalar)
            _require(segment.get("output_sha256") == segment_output_sha,
                     f"segment {index} scalar/output digest mismatch")
            segment_input_sha = _digest({
                "global_input_sha256": row["input_sha256"],
                "segment_id": index, "partition": segment["partition"],
                "relation_count": relation_count,
                "primitive_count": primitive_count, "query_count": query_count,
            })
            plan = segment.get("fusion_ablation_plan")
            operation = segment.get("operation_evidence_receipt")
            traversal = segment.get("traversal_receipt")
            semantic_binding = segment.get("traversal_semantic_binding")
            reduction = segment.get("checked_u64_weighted_reduction")
            _require(isinstance(plan, dict) and isinstance(operation, dict)
                     and isinstance(traversal, dict)
                     and isinstance(semantic_binding, dict)
                     and isinstance(reduction, dict),
                     "segment evidence missing")
            assert target_authority is not None
            _verify_plan(
                plan, variant=key[3], target=target_authority, row=row,
                segment_input_sha=segment_input_sha, query_count=query_count)
            _require(_receipt_ok(
                traversal, output_sha=segment_output_sha,
                expected_native_sha256=expected_native,
                query_count=query_count,
                semantic_binding=semantic_binding,
            ),
                     "segment is not output-bound behavioral true OptiX")
            _verify_semantic_binding_against_target(
                semantic_binding, target_authority)
            _verify_operation_receipt(
                operation, plan, traversal, variant=key[3],
                query_count=query_count, output_sha=segment_output_sha,
                expected_execution_nonce=(
                    f"goal5790-home-{pid}-{key[0]}-{lifecycle}-{key[3]}-"
                    f"{index:06d}"
                ),
            )
            _verify_reduction(
                reduction, variant=key[3], query_count=query_count,
                primitive_count=primitive_count, scalar_sum=scalar)
            total_traversals += 1
            total_operations += 1
            total_events += len(operation["events"])
            operation_receipts_by_variant[key[3]] += 1
            operation_events_by_variant[key[3]] += len(operation["events"])
        _require(scalar_total == output
                 and _digest(scalar_total) == row.get("output_sha256"),
                 "segment scalar sum does not reconstruct lane output")
        rows[key] = row

    expected_keys = _expected_keys()
    _require(set(rows) == expected_keys, "ten-lane matrix shape mismatch")
    pair_keys = {
        (input_kind, dataset, lifecycle)
        for input_kind, dataset, lifecycle, _variant in expected_keys
    }
    for input_kind, dataset, lifecycle in pair_keys:
        on = rows[(input_kind, dataset, lifecycle, "fusion_on")]
        off = rows[(input_kind, dataset, lifecycle, "fusion_off")]
        for name in (
            "input_view", "input_contract", "input_sha256", "oracle_contract",
            "oracle_sha256", "output", "expected", "output_sha256",
            "timer_contract", "timer_contract_sha256",
            "lifecycle_contract_sha256", "segment_count",
            "execution_environment_class", "home_machine_authority",
            "home_machine_authority_sha256", "pod_used",
        ):
            _require(on[name] == off[name],
                     f"ON/OFF semantic mismatch: {dataset}/{lifecycle}/{name}")
        for on_segment, off_segment in zip(
                on["segments"], off["segments"], strict=True):
            for name in (
                "segment_id", "partition", "relation_count", "primitive_count",
                "query_count", "scalar_sum", "output_sha256",
            ):
                _require(on_segment[name] == off_segment[name],
                         f"ON/OFF segment mismatch: {dataset}/{lifecycle}/{name}")
            on_plan = on_segment["fusion_ablation_plan"]
            off_plan = off_segment["fusion_ablation_plan"]
            _require(on_plan["shared_identity_sha256"]
                     == off_plan["shared_identity_sha256"],
                     "ON/OFF shared plan identity mismatch")
            changed = {
                name for name in on_plan if on_plan.get(name) != off_plan.get(name)
            }
            _require(changed == VARIANT_PLAN_FIELDS,
                     f"unexpected ON/OFF plan delta: {sorted(changed)}")

    _require(
        operation_receipts_by_variant == {"fusion_on": 5, "fusion_off": 5}
        and operation_events_by_variant == {
            "fusion_on": 10, "fusion_off": 35,
        },
        "bounded Home lanes no longer have one two/seven-event segment each",
    )

    result = {
        "schema": "rtdl.goal5790.independent_home_functional_recount.v1",
        "verdict": "PASS__10_OF_10_EXACT_BEHAVIORAL_AND_EVENT_DERIVED",
        "raw_file_count": len(paths),
        "raw_manifest": [
            {"path": path.name, "size_bytes": path.stat().st_size,
             "sha256": _sha_file(path)} for path in paths
        ],
        "fresh_parent_pid_count": len(pids), "small_fixture_lane_count": 4,
        "bounded_real_smoke_lane_count": 6, "bounded_real_dataset_count": 3,
        "variant_count": 2, "exact_lane_count": len(rows),
        "behavioral_true_optix_lane_count": len(rows),
        "traversal_receipt_count": total_traversals,
        "operation_receipt_count": total_operations,
        "successful_operation_event_count": total_events,
        "operation_receipt_count_by_variant": operation_receipts_by_variant,
        "successful_operation_event_count_by_variant": (
            operation_events_by_variant),
        "invalid_traversal_or_operation_receipt_count": 0,
        "bounded_view_triangle_oracles": bounded_oracles,
        "target_materialization_receipt_sha256": authority_sha,
        "ptx_program_identity_sha256": ptx_program_identity_sha,
        "execution_source_archive_sha256": source_archive_sha,
        "execution_source_tree_sha256": source_tree_sha,
        "native_library_sha256": expected_native, "particle_included": False,
        "formal_worker_count": 0, "registered_performance_timing_count": 0,
        "performance_or_compiler_fusion_claimed": False,
        "elapsed_values_recounted": False,
        "execution_environment_class": "HOME_PASCAL_FUNCTIONAL_ONLY",
        "home_machine_authority": HOME_MACHINE_AUTHORITY,
        "home_machine_authority_sha256": HOME_MACHINE_AUTHORITY[
            "receipt_sha256"],
        "pod_used": HOME_MACHINE_AUTHORITY["pod_used"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
