#!/usr/bin/env python3
"""Frozen static contract for the Goal5790/Goal5791 fusion ablation.

Goal5790 is implementation- and functional-only.  This module fixes the later
same-cohort shape but grants no execution authority.  Variant assignment is a
total function of pair parity; application, dataset contents, timings, and
results never participate in selection.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


SCHEMA = "rtdl.goal5790.static_fusion_ablation_contract.v1"
SHARED_FREEZE_SCHEMA = "rtdl.goal5789_goal5790.shared_contract_freeze.v1"
SHARED_FREEZE_RELATIVE_PATH = (
    "history/internal_docs/goal5789_contract_evidence_20260816/"
    "GOAL5789_GOAL5790_SHARED_CONTRACT_FREEZE.json"
)
SHARED_FREEZE_FILE_SHA256 = (
    "b62217a5374732cece8c7eaef93c0f21eb580666559e912eb8dd1bb2aaa7628b"
)
SHARED_FREEZE_CONTENT_SHA256 = (
    "8ada80c377241aa9a4fde29f26fdc9380257f93cc2264a3e60f2a96a437fced5"
)
SEMANTIC_REQUEST_SHA256 = (
    "492c59b92f3ab8138d5bff6b481bff16e51db5028868732d266ef2948810f02e"
)
PHYSICAL_ENCODING_SHA256 = (
    "7f1d101e8f588571c58958152ed7f20ef43387a50d9fd00c5c7925d7405dc656"
)
MECHANISM_ID = "checked_u64_product_sum_downstream_lowering.v1"
ALLOWED_DELTA_ID = (
    "downstream_checked_u64_reducer_operation_identity_and_event_sequence"
)

FUSION_OFF = "fusion_off"
FUSION_ON = "fusion_on"
VARIANTS = (FUSION_OFF, FUSION_ON)
COLD = "cold"
PREPARED = "prepared"
LIFECYCLES = (COLD, PREPARED)
PAIR_COUNT = 8
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_SEED_BASE = 57_900_000
BOOTSTRAP_CI_INDICES = (249, 9749)
EXECUTION_STATE = "STATIC_DRAFT__EXECUTION_FORBIDDEN"
OPERATION_EVIDENCE_TCB = (
    "trusted_runtime_records_each_compiler_instrumented_operation_only_after_"
    "its_callable_returns_successfully__not_hardware_or_opaque_partner_kernel_"
    "introspection"
)
OUTPUT_CONTRACT = {
    "paper_algorithm": "RT-2A1",
    "reducer": "checked_u64_product_sum",
    "result": "exact_u64_triangle_count",
    "overflow": "fail_closed_before_provisional_sum_is_trusted",
}
OUTPUT_CONTRACT_SHA256 = (
    "aa1082bdf1e61dde0e4f2b430b1ae99dc28fb3fd1d1c832781c43b36a8ea0846"
)
TIMER_CONTRACTS = {
    COLD: {
        "included": [
            "graph_input_load_and_degree_oriented_csr",
            "restricted_callback_verify_compile_and_program_prepare",
            "bounded_device_geometry_production",
            "optix_execute_and_declared_downstream_reducer",
            "scalar_host_materialization_and_owner_close",
        ],
        "excluded": ["oracle_comparison", "receipt_serialization"],
    },
    PREPARED: {
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
}


@dataclass(frozen=True)
class DatasetUnit:
    dataset_id: str
    frozen_input_role: str


DATASETS = (
    DatasetUnit("com_dblp", "small_graph_control"),
    DatasetUnit("cit_patents", "medium_graph"),
    DatasetUnit("soc_livejournal1", "large_graph"),
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def file_sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def validate_shared_freeze(path: Path) -> dict[str, object]:
    if not path.is_file() or file_sha256(path) != SHARED_FREEZE_FILE_SHA256:
        raise PermissionError("Goal5790 shared Goal5789 contract freeze drifted")
    payload = json.loads(path.read_text(encoding="utf-8"))
    unsigned = dict(payload) if isinstance(payload, dict) else {}
    unsigned.pop("shared_contract_freeze_sha256", None)
    if not isinstance(payload, dict) or (
        payload.get("schema") != SHARED_FREEZE_SCHEMA
        or payload.get("shared_contract_freeze_sha256")
        != SHARED_FREEZE_CONTENT_SHA256
        or digest(unsigned) != SHARED_FREEZE_CONTENT_SHA256
        or payload.get("semantic_request_sha256") != SEMANTIC_REQUEST_SHA256
        or payload.get("physical_encoding_sha256") != PHYSICAL_ENCODING_SHA256
        or payload.get("status")
        != "FROZEN_FOR_LOCAL_GOAL5790_IMPLEMENTATION_ONLY"
    ):
        raise PermissionError("Goal5790 shared semantic/physical freeze mismatch")
    variant = payload.get("transformation_variant_contract")
    boundary = payload.get("claim_boundary")
    if not isinstance(variant, dict) or not isinstance(boundary, dict) or (
        variant.get("mechanism_id") != MECHANISM_ID
        or variant.get("only_allowlisted_difference") != ALLOWED_DELTA_ID
        or variant.get("particle_included") is not False
        or boundary.get("same_optix_producer_required") is not True
        or boundary.get("same_semantic_ir_required") is not True
        or boundary.get("event_derived_operation_receipts_required") is not True
        or boundary.get("pod_or_target_worker_authorized") is not False
        or boundary.get("compiler_fusion_claim_authorized") is not False
    ):
        raise PermissionError("Goal5790 shared transformation freeze mismatch")
    return payload


def statistical_rows() -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "row_index": row_index,
            "row_id": f"{unit.dataset_id}__{lifecycle}",
            "dataset_id": unit.dataset_id,
            "frozen_input_role": unit.frozen_input_role,
            "lifecycle": lifecycle,
            "mechanism_id": MECHANISM_ID,
        }
        for row_index, (unit, lifecycle) in enumerate(
            (unit, lifecycle) for lifecycle in LIFECYCLES for unit in DATASETS
        )
    )


def schedule() -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for description in statistical_rows():
        for pair_index in range(PAIR_COUNT):
            order = VARIANTS if pair_index % 2 == 0 else tuple(reversed(VARIANTS))
            for order_ordinal, variant in enumerate(order):
                rows.append(
                    {
                        "worker_index": len(rows),
                        "row_id": description["row_id"],
                        "dataset_id": description["dataset_id"],
                        "lifecycle": description["lifecycle"],
                        "pair_index": pair_index,
                        "order_ordinal": order_ordinal,
                        "variant": variant,
                        "mechanism_id": MECHANISM_ID,
                    }
                )
    return tuple(rows)


def expected_operation_contract(
    variant: str, *, declared_value_count: int,
) -> dict[str, object]:
    if not isinstance(declared_value_count, int) \
            or isinstance(declared_value_count, bool) \
            or declared_value_count <= 0:
        raise ValueError("declared_value_count must be a positive integer")
    if variant == FUSION_OFF:
        requirements = [
            _requirement(0, "maximum_weight.logical_reduce", "logical_reduction", units_per_value=1),
            _requirement(1, "maximum_weight.scalar_copy_sync", "host_copy_synchronization", fixed_units=1, bytes_per_unit=8, host_visibility_boundary=True),
            _requirement(2, "weight_sum.logical_reduce", "logical_reduction", units_per_value=1),
            _requirement(3, "weight_sum.scalar_copy_sync", "host_copy_synchronization", fixed_units=1, bytes_per_unit=8, host_visibility_boundary=True),
            _requirement(4, "weighted_product.materialize", "device_materialization", units_per_value=1, bytes_per_unit=8),
            _requirement(5, "weighted_product_sum.logical_reduce", "logical_reduction", units_per_value=1),
            _requirement(6, "weighted_product_sum.scalar_copy_sync", "host_copy_synchronization", fixed_units=1, bytes_per_unit=8, host_visibility_boundary=True),
        ]
        counters = {
            "weighted_product_materializations": 1,
            "compiler_visible_logical_reductions": 3,
            "host_scalar_copy_or_sync_boundaries": 3,
            "checked_summary_kernel_invocations": 0,
            "summary_copy_or_sync_boundaries": 0,
        }
    elif variant == FUSION_ON:
        requirements = [
            _requirement(0, "checked_summary.kernel_launch", "compiler_kernel_invocation", units_per_value=1),
            _requirement(1, "checked_summary.summary_copy_sync", "host_copy_synchronization", fixed_units=4, bytes_per_unit=8, host_visibility_boundary=True),
        ]
        counters = {
            "weighted_product_materializations": 0,
            "compiler_visible_logical_reductions": 1,
            "host_scalar_copy_or_sync_boundaries": 1,
            "checked_summary_kernel_invocations": 1,
            "summary_copy_or_sync_boundaries": 1,
        }
    else:
        raise ValueError(f"unknown Goal5790 variant: {variant!r}")
    return {
        "declared_value_count": declared_value_count,
        "requirements": requirements,
        "counters": counters,
    }


def timer_contract(lifecycle: str) -> dict[str, object]:
    if lifecycle not in TIMER_CONTRACTS:
        raise ValueError(f"unknown Goal5790 lifecycle: {lifecycle!r}")
    return dict(TIMER_CONTRACTS[lifecycle])


def lifecycle_contract(lifecycle: str) -> dict[str, object]:
    if lifecycle not in LIFECYCLES:
        raise ValueError(f"unknown Goal5790 lifecycle: {lifecycle!r}")
    return {
        "lifecycle": lifecycle,
        "fresh_parent_pid": True,
        "first_prepared_execute_only": lifecycle == PREPARED,
        "complete_endpoint": lifecycle == COLD,
        "bounded_functional_smoke_only": False,
    }


def _requirement(
    ordinal: int,
    operation_id: str,
    kind: str,
    *,
    units_per_value: int = 0,
    fixed_units: int = 0,
    bytes_per_unit: int = 0,
    fixed_bytes: int = 0,
    host_visibility_boundary: bool = False,
) -> dict[str, object]:
    return {
        "ordinal": ordinal,
        "operation_id": operation_id,
        "kind": kind,
        "units_per_value": units_per_value,
        "fixed_units": fixed_units,
        "bytes_per_unit": bytes_per_unit,
        "fixed_bytes": fixed_bytes,
        "host_visibility_boundary": host_visibility_boundary,
        "compiler_visible_only": True,
    }


def contract_document() -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "goal": 5790,
        "successor_execution_goal": 5791,
        "execution_state": EXECUTION_STATE,
        "shared_contract_freeze": {
            "path": SHARED_FREEZE_RELATIVE_PATH,
            "file_sha256": SHARED_FREEZE_FILE_SHA256,
            "content_sha256": SHARED_FREEZE_CONTENT_SHA256,
            "semantic_request_sha256": SEMANTIC_REQUEST_SHA256,
            "physical_encoding_sha256": PHYSICAL_ENCODING_SHA256,
        },
        "mechanism_id": MECHANISM_ID,
        "allowed_delta_id": ALLOWED_DELTA_ID,
        "variants": list(VARIANTS),
        "lifecycles": list(LIFECYCLES),
        "datasets": [
            {
                "dataset_id": unit.dataset_id,
                "frozen_input_role": unit.frozen_input_role,
            }
            for unit in DATASETS
        ],
        "pair_count_per_row": PAIR_COUNT,
        "independent_row_count": len(statistical_rows()),
        "formal_worker_count": len(schedule()),
        "worker_count_derivation": (
            "3 datasets * 2 lifecycles * 8 ABBA pairs * 2 arms = 96"
        ),
        "particle_rows": 0,
        "statistics": {
            "ratio": "fusion_off_seconds / fusion_on_seconds",
            "greater_than_one_favors": FUSION_ON,
            "summary": "median of eight paired ABBA ratios",
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "bootstrap_sampler": "python_random_Random_choices",
            "bootstrap_seed": f"{BOOTSTRAP_SEED_BASE} + row_index",
            "bootstrap_ci_indices": list(BOOTSTRAP_CI_INDICES),
            "cross_dataset_or_lifecycle_compensation_allowed": False,
        },
        "timer": {
            "cold": "load + compile/prepare + execute + close",
            "prepared": "first_execute_only",
            "prepared_loading_preparation_and_close_reported_separately": True,
            "prepared_work_called_free": False,
            "comparator_inside_registered_timer": False,
            "receipt_serialization_inside_registered_timer": False,
            "same_boundary_for_both_variants": True,
        },
        "output_contract": OUTPUT_CONTRACT,
        "output_contract_sha256": OUTPUT_CONTRACT_SHA256,
        "worker_gates": {
            "fresh_parent_pid_required": True,
            "exact_oracle_output_required": True,
            "common_semantic_physical_source_native_provider_target_identity_required": True,
            "serialized_verified_target_materialization_authority_required": True,
            "strict_ordered_multisegment_evidence_required": True,
            "every_segment_fusion_ablation_plan_reconstructed": True,
            "every_segment_declared_value_count_equals_query_count": True,
            "every_segment_output_operation_and_traversal_binding_required": True,
            "two_phase_device_complete_then_evidence_seal_required": True,
            "evidence_hashing_or_serialization_inside_registered_timer": False,
            "variant_plan_and_downstream_operation_recipe_identity_required": True,
            "event_derived_operation_receipt_required": True,
            "behavioral_true_optix_required": True,
            "retry_resume_replacement_row_drop_relabel_allowed": False,
        },
        "selection": {
            "rule": "pair parity only: even off/on, odd on/off",
            "app_dataset_timing_result_dispatch_allowed": False,
        },
        "claim_boundary": {
            "static_harness_only": True,
            "target_worker_authorized": False,
            "pod_authorized": False,
            "performance_observed_or_claimed": False,
            "compiler_fusion_claim_authorized": False,
        },
    }


def contract_sha256() -> str:
    return digest(contract_document())


__all__ = [
    "ALLOWED_DELTA_ID",
    "BOOTSTRAP_CI_INDICES",
    "BOOTSTRAP_DRAWS",
    "BOOTSTRAP_SEED_BASE",
    "COLD",
    "DATASETS",
    "EXECUTION_STATE",
    "FUSION_OFF",
    "FUSION_ON",
    "LIFECYCLES",
    "MECHANISM_ID",
    "OPERATION_EVIDENCE_TCB",
    "OUTPUT_CONTRACT",
    "OUTPUT_CONTRACT_SHA256",
    "PAIR_COUNT",
    "PHYSICAL_ENCODING_SHA256",
    "PREPARED",
    "SEMANTIC_REQUEST_SHA256",
    "SHARED_FREEZE_CONTENT_SHA256",
    "SHARED_FREEZE_FILE_SHA256",
    "SHARED_FREEZE_RELATIVE_PATH",
    "VARIANTS",
    "contract_document",
    "contract_sha256",
    "digest",
    "expected_operation_contract",
    "lifecycle_contract",
    "schedule",
    "statistical_rows",
    "timer_contract",
    "validate_shared_freeze",
]
