from __future__ import annotations

from typing import Any


V1_5_BOUNDED_COLLECTION_PRIMITIVES = ("COLLECT_K_BOUNDED",)
V1_5_BOUNDED_COLLECTION_FAILURE_MODES = ("fail_closed_overflow",)
V1_5_BOUNDED_COLLECTION_PUBLIC_WORDING_ALLOWED = False


def v1_5_collect_k_bounded_contracts() -> tuple[dict[str, Any], ...]:
    """Return v1.5 contracts for experimental bounded collection primitives."""
    return (
        {
            "app": "polygon_set_jaccard",
            "subpath": "chunked_candidate_scoring",
            "status": "experimental_diagnostic_only",
            "collection_primitive": "COLLECT_K_BOUNDED",
            "input_primitive": "ANY_HIT",
            "follow_on_reduction": "REDUCE_FLOAT(SUM)",
            "result_layout": "bounded_candidate_pair_ids",
            "capacity_unit": "candidate_pair_rows",
            "capacity_parameter": "k",
            "ordering_policy": "stable_by_left_id_then_right_id_after_candidate_discovery",
            "overflow_policy": "no_silent_truncation",
            "failure_mode": "fail_closed_overflow",
            "truncation_allowed": False,
            "complete_candidate_coverage_required": True,
            "score_reduction_allowed_on_overflow": False,
            "public_wording_allowed": V1_5_BOUNDED_COLLECTION_PUBLIC_WORDING_ALLOWED,
            "promotion_requirements": (
                "publish capacity and ordering policy",
                "prove candidate coverage is complete or fail closed",
                "validate REDUCE_FLOAT(SUM) score parity only after complete coverage",
                "keep OptiX-vs-Embree performance reason documented",
            ),
            "claim_boundary": (
                "diagnostic bounded collection only; no public Jaccard speedup wording, "
                "no silent candidate truncation, and no score output after overflow"
            ),
        },
    )


def validate_v1_5_collect_k_bounded_contracts() -> tuple[dict[str, Any], ...]:
    contracts = v1_5_collect_k_bounded_contracts()
    required_fields = (
        "app",
        "subpath",
        "status",
        "collection_primitive",
        "input_primitive",
        "follow_on_reduction",
        "result_layout",
        "capacity_unit",
        "capacity_parameter",
        "ordering_policy",
        "overflow_policy",
        "failure_mode",
        "truncation_allowed",
        "complete_candidate_coverage_required",
        "score_reduction_allowed_on_overflow",
        "public_wording_allowed",
        "promotion_requirements",
        "claim_boundary",
    )
    for contract in contracts:
        for field in required_fields:
            if field not in contract:
                raise ValueError(f"missing bounded collection contract field: {field}")
            if field not in {
                "truncation_allowed",
                "complete_candidate_coverage_required",
                "score_reduction_allowed_on_overflow",
                "public_wording_allowed",
            } and not contract[field]:
                raise ValueError(f"bounded collection contract field must be non-empty: {field}")
        if contract["collection_primitive"] not in V1_5_BOUNDED_COLLECTION_PRIMITIVES:
            raise ValueError(f"invalid bounded collection primitive: {contract['collection_primitive']}")
        if contract["status"] != "experimental_diagnostic_only":
            raise ValueError("COLLECT_K_BOUNDED must remain experimental_diagnostic_only in v1.5")
        if contract["failure_mode"] not in V1_5_BOUNDED_COLLECTION_FAILURE_MODES:
            raise ValueError(f"invalid bounded collection failure mode: {contract['failure_mode']}")
        if contract["overflow_policy"] != "no_silent_truncation":
            raise ValueError("COLLECT_K_BOUNDED must reject silent truncation")
        if contract["truncation_allowed"] is not False:
            raise ValueError("COLLECT_K_BOUNDED truncation_allowed must be false")
        if contract["complete_candidate_coverage_required"] is not True:
            raise ValueError("COLLECT_K_BOUNDED requires complete candidate coverage")
        if contract["score_reduction_allowed_on_overflow"] is not False:
            raise ValueError("Jaccard score reduction must not run after collection overflow")
        if contract["public_wording_allowed"] is not False:
            raise ValueError("bounded collection public wording must remain blocked")
        if not tuple(contract["promotion_requirements"]):
            raise ValueError("promotion_requirements must not be empty")
    return contracts
