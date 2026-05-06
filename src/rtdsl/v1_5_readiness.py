from __future__ import annotations

from typing import Any

from .bounded_collection_contracts import validate_v1_5_collect_k_bounded_contracts
from .float_reduction_contracts import validate_v1_5_float_sum_reduction_contracts
from .generic_db_primitives import validate_v1_5_db_compact_summary_contracts
from .grouped_reduction_contracts import validate_v1_5_grouped_reduction_contracts
from .reduction_runtime import V1_5_GENERIC_SCALAR_REDUCTION_PRIMITIVES
from .v1_5_migration_inventory import (
    ACTIVE_V1_5_BACKENDS,
    FROZEN_BEFORE_V2_1_BACKENDS,
    validate_v1_5_generic_migration_inventory,
    v1_5_generic_migration_blockers,
)


V1_5_INTERNAL_READINESS_STATUS = "internal_v1_5_contract_gate_passing_non_public"
V1_5_INTERNAL_READINESS_CLAIM_BOUNDARY = (
    "internal v1.5 contract readiness only; not public v1.5 release wording; "
    "not public speedup wording; v1.0 tag remains unchanged; public claims require 3-AI consensus"
)
V1_5_INTERNAL_READINESS_STABLE_SUMMARY_PRIMITIVES = (
    "COUNT_HITS",
    "REDUCE_FLOAT(MIN)",
    "REDUCE_FLOAT(MAX)",
    "REDUCE_FLOAT(SUM)",
    "REDUCE_INT(COUNT)",
    "REDUCE_INT(SUM)",
)
V1_5_INTERNAL_READINESS_ALLOWED_INVENTORY_STATUSES = ("pod_verified_generic",)
V1_5_INTERNAL_READINESS_REQUIRED_BLOCKER_PHRASES = (
    "app-level continuations remain outside v1.5 generic subpath scope",
    "whole-app speedup wording remains blocked",
    "public NVIDIA wording remains blocked",
    "3-AI consensus",
)


def _count_inventory_statuses(inventory: tuple[dict[str, Any], ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in inventory:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def _contract_surface_counts(
    *,
    inventory_rows: int,
    grouped_contracts: int,
    db_contracts: int,
    float_sum_contracts: int,
    bounded_collection_contracts: int,
) -> dict[str, int]:
    return {
        "inventory_rows": inventory_rows,
        "grouped_contracts": grouped_contracts,
        "db_contracts": db_contracts,
        "float_sum_contracts": float_sum_contracts,
        "bounded_collection_contracts": bounded_collection_contracts,
    }


def v1_5_internal_readiness_gate() -> dict[str, Any]:
    """Return the aggregate internal v1.5 contract-readiness gate.

    The gate composes existing validators and summarizes counts for the
    currently verified contract surfaces. It is intentionally non-public:
    passing this gate does not authorize release tags, public v1.5 wording, or
    speedup language.
    """
    inventory = validate_v1_5_generic_migration_inventory()
    grouped_contracts = validate_v1_5_grouped_reduction_contracts()
    db_contracts = validate_v1_5_db_compact_summary_contracts()
    float_sum_contracts = validate_v1_5_float_sum_reduction_contracts()
    bounded_collection_contracts = validate_v1_5_collect_k_bounded_contracts()
    blockers = v1_5_generic_migration_blockers()
    contract_surface_counts = _contract_surface_counts(
        inventory_rows=len(inventory),
        grouped_contracts=len(grouped_contracts),
        db_contracts=len(db_contracts),
        float_sum_contracts=len(float_sum_contracts),
        bounded_collection_contracts=len(bounded_collection_contracts),
    )

    return {
        "status": V1_5_INTERNAL_READINESS_STATUS,
        **contract_surface_counts,
        "contract_surface_counts": contract_surface_counts,
        "total_contract_surfaces": sum(contract_surface_counts.values()),
        "stable_summary_primitives": V1_5_GENERIC_SCALAR_REDUCTION_PRIMITIVES,
        "active_backend_scope": ACTIVE_V1_5_BACKENDS,
        "frozen_before_v2_1_backends": FROZEN_BEFORE_V2_1_BACKENDS,
        "inventory_status_counts": _count_inventory_statuses(inventory),
        "allowed_inventory_statuses": V1_5_INTERNAL_READINESS_ALLOWED_INVENTORY_STATUSES,
        "validators": (
            "validate_v1_5_generic_migration_inventory",
            "validate_v1_5_grouped_reduction_contracts",
            "validate_v1_5_db_compact_summary_contracts",
            "validate_v1_5_float_sum_reduction_contracts",
            "validate_v1_5_collect_k_bounded_contracts",
        ),
        "blockers": blockers,
        "required_blocker_phrases": V1_5_INTERNAL_READINESS_REQUIRED_BLOCKER_PHRASES,
        "public_release_authorized": False,
        "public_speedup_wording_authorized": False,
        "release_tag_action_authorized": False,
        "requires_external_consensus_for_public_claims": "3-AI",
        "experimental_primitives": ("COLLECT_K_BOUNDED",),
        "claim_boundary": V1_5_INTERNAL_READINESS_CLAIM_BOUNDARY,
    }


def validate_v1_5_internal_readiness_gate() -> dict[str, Any]:
    gate = v1_5_internal_readiness_gate()
    if gate["status"] != V1_5_INTERNAL_READINESS_STATUS:
        raise ValueError("invalid v1.5 internal readiness gate status")
    for flag in (
        "public_release_authorized",
        "public_speedup_wording_authorized",
        "release_tag_action_authorized",
    ):
        if gate[flag] is not False:
            raise ValueError(f"v1.5 internal readiness gate must not authorize {flag}")
    if gate["requires_external_consensus_for_public_claims"] != "3-AI":
        raise ValueError("public v1.5 claims must remain behind 3-AI consensus")
    if tuple(gate["stable_summary_primitives"]) != V1_5_INTERNAL_READINESS_STABLE_SUMMARY_PRIMITIVES:
        raise ValueError("v1.5 internal readiness gate must preserve stable summary primitives")
    if tuple(gate["active_backend_scope"]) != ("embree", "optix"):
        raise ValueError("v1.5 internal readiness gate must stay scoped to Embree and OptiX")
    if tuple(gate["frozen_before_v2_1_backends"]) != ("vulkan", "hiprt", "apple_rt"):
        raise ValueError("v1.5 internal readiness gate must preserve frozen-before-v2.1 backends")
    if set(gate["active_backend_scope"]) & set(gate["frozen_before_v2_1_backends"]):
        raise ValueError("active and frozen v1.5 backend scopes must not overlap")
    invalid_statuses = sorted(
        set(gate["inventory_status_counts"]) - set(gate["allowed_inventory_statuses"])
    )
    if invalid_statuses:
        raise ValueError(
            "v1.5 internal readiness gate cannot pass with non-verified inventory statuses: "
            f"{', '.join(invalid_statuses)}"
        )
    if sum(int(count) for count in gate["inventory_status_counts"].values()) != int(
        gate["inventory_rows"]
    ):
        raise ValueError("v1.5 internal readiness inventory status counts must match row count")
    blockers = tuple(gate["blockers"])
    if not blockers:
        raise ValueError("v1.5 internal readiness gate must expose blockers")
    missing_blockers = [
        phrase
        for phrase in gate["required_blocker_phrases"]
        if not any(phrase in blocker for blocker in blockers)
    ]
    if missing_blockers:
        raise ValueError(
            "v1.5 internal readiness blockers are missing required phrases: "
            f"{', '.join(missing_blockers)}"
        )
    boundary = str(gate["claim_boundary"])
    for required_boundary in (
        "internal v1.5 contract readiness only",
        "not public v1.5 release wording",
        "not public speedup wording",
        "v1.0 tag remains unchanged",
        "public claims require 3-AI consensus",
    ):
        if required_boundary not in boundary:
            raise ValueError("v1.5 internal readiness claim boundary is too broad")
    if "COLLECT_K_BOUNDED" not in tuple(gate["experimental_primitives"]):
        raise ValueError("COLLECT_K_BOUNDED must remain represented as experimental")
    for count_field in (
        "inventory_rows",
        "grouped_contracts",
        "db_contracts",
        "float_sum_contracts",
        "bounded_collection_contracts",
    ):
        if int(gate[count_field]) <= 0:
            raise ValueError(f"v1.5 internal readiness count must be positive: {count_field}")
    expected_surface_total = sum(int(count) for count in gate["contract_surface_counts"].values())
    if int(gate["total_contract_surfaces"]) != expected_surface_total:
        raise ValueError("v1.5 internal readiness total contract surfaces must match component counts")
    for count_field, count in gate["contract_surface_counts"].items():
        if gate[count_field] != count:
            raise ValueError(
                f"v1.5 internal readiness surface count mismatch for {count_field}"
            )
    return gate
