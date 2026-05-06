from __future__ import annotations

from typing import Any


V1_5_BOUNDED_COLLECTION_PRIMITIVES = ("COLLECT_K_BOUNDED",)
V1_5_BOUNDED_COLLECTION_FAILURE_MODES = ("fail_closed_overflow",)
V1_5_BOUNDED_COLLECTION_PUBLIC_WORDING_ALLOWED = False
V1_5_COLLECT_K_BOUNDED_RESOLUTION_STATUS = "defined_pending_evidence"
V1_5_COLLECT_K_BOUNDED_RESOLUTION_STRATEGY = (
    "promote_to_standalone_if_native_fail_closed_parity_and_benchmarks_pass"
)
V1_5_COLLECT_K_BOUNDED_FALLBACK_STRATEGY = (
    "exclude_row_returning_apps_from_standalone_v1_5_if_gates_do_not_pass"
)
V1_5_COLLECT_K_BOUNDED_PROMOTION_GATES = (
    "published_capacity_ordering_overflow_contract",
    "python_fail_closed_reference_tests",
    "embree_native_fail_closed_collection",
    "optix_native_fail_closed_collection",
    "cross_backend_complete_candidate_coverage_parity",
    "score_reduction_guarded_by_complete_collection",
    "row_returning_app_scope_classified",
    "same_contract_app_correctness_suite",
    "same_contract_app_benchmark_suite",
    "external_review_before_public_promotion",
)


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
        boundary = str(contract["claim_boundary"])
        for required_boundary in (
            "diagnostic bounded collection only",
            "no public Jaccard speedup wording",
            "no silent candidate truncation",
            "no score output after overflow",
        ):
            if required_boundary not in boundary:
                raise ValueError("bounded collection claim boundary must block broad Jaccard claims")
    return contracts


def v1_5_collect_k_bounded_resolution() -> dict[str, Any]:
    """Return the standalone-v1.5 resolution plan for COLLECT_K_BOUNDED."""
    (contract,) = validate_v1_5_collect_k_bounded_contracts()
    gate_results = {
        "published_capacity_ordering_overflow_contract": True,
        "python_fail_closed_reference_tests": True,
        "embree_native_fail_closed_collection": False,
        "optix_native_fail_closed_collection": False,
        "cross_backend_complete_candidate_coverage_parity": False,
        "score_reduction_guarded_by_complete_collection": True,
        "row_returning_app_scope_classified": False,
        "same_contract_app_correctness_suite": False,
        "same_contract_app_benchmark_suite": False,
        "external_review_before_public_promotion": False,
    }
    return {
        "primitive": "COLLECT_K_BOUNDED",
        "status": V1_5_COLLECT_K_BOUNDED_RESOLUTION_STATUS,
        "resolution_strategy": V1_5_COLLECT_K_BOUNDED_RESOLUTION_STRATEGY,
        "fallback_strategy": V1_5_COLLECT_K_BOUNDED_FALLBACK_STRATEGY,
        "stable_promotion_authorized": False,
        "public_wording_allowed": False,
        "release_tag_action_authorized": False,
        "active_backend_scope": ("embree", "optix"),
        "capacity_parameter": contract["capacity_parameter"],
        "capacity_unit": contract["capacity_unit"],
        "ordering_policy": contract["ordering_policy"],
        "overflow_policy": contract["overflow_policy"],
        "failure_mode": contract["failure_mode"],
        "truncation_allowed": contract["truncation_allowed"],
        "complete_candidate_coverage_required": contract["complete_candidate_coverage_required"],
        "score_reduction_allowed_on_overflow": contract[
            "score_reduction_allowed_on_overflow"
        ],
        "promotion_gates": V1_5_COLLECT_K_BOUNDED_PROMOTION_GATES,
        "gate_results": gate_results,
        "passed_gates": tuple(gate for gate, passed in gate_results.items() if passed),
        "failed_gates": tuple(gate for gate, passed in gate_results.items() if not passed),
        "standalone_v1_5_decision": "pending_required_evidence",
        "claim_boundary": (
            "COLLECT_K_BOUNDED resolution is defined but not complete; keep experimental "
            "until native Embree/OptiX fail-closed collection, parity, app correctness, "
            "benchmark, and external review gates pass; otherwise exclude row-returning "
            "apps from standalone v1.5."
        ),
    }


def validate_v1_5_collect_k_bounded_resolution() -> dict[str, Any]:
    resolution = v1_5_collect_k_bounded_resolution()
    if resolution["primitive"] != "COLLECT_K_BOUNDED":
        raise ValueError("collect-k resolution must target COLLECT_K_BOUNDED")
    if resolution["status"] != V1_5_COLLECT_K_BOUNDED_RESOLUTION_STATUS:
        raise ValueError("collect-k resolution status must remain pending evidence")
    if resolution["resolution_strategy"] != V1_5_COLLECT_K_BOUNDED_RESOLUTION_STRATEGY:
        raise ValueError("collect-k resolution strategy changed unexpectedly")
    if resolution["fallback_strategy"] != V1_5_COLLECT_K_BOUNDED_FALLBACK_STRATEGY:
        raise ValueError("collect-k fallback strategy must exclude row-returning apps")
    if tuple(resolution["promotion_gates"]) != V1_5_COLLECT_K_BOUNDED_PROMOTION_GATES:
        raise ValueError("collect-k promotion gates must be preserved")
    gate_results = dict(resolution["gate_results"])
    if tuple(gate_results) != V1_5_COLLECT_K_BOUNDED_PROMOTION_GATES:
        raise ValueError("collect-k gate results must match promotion gates")
    if tuple(resolution["active_backend_scope"]) != ("embree", "optix"):
        raise ValueError("collect-k promotion must require Embree and OptiX")
    for flag in (
        "stable_promotion_authorized",
        "public_wording_allowed",
        "release_tag_action_authorized",
        "truncation_allowed",
        "score_reduction_allowed_on_overflow",
    ):
        if resolution[flag] is not False:
            raise ValueError(f"collect-k resolution must not authorize {flag}")
    if resolution["complete_candidate_coverage_required"] is not True:
        raise ValueError("collect-k resolution must require complete candidate coverage")
    if resolution["overflow_policy"] != "no_silent_truncation":
        raise ValueError("collect-k resolution must reject silent truncation")
    if resolution["failure_mode"] != "fail_closed_overflow":
        raise ValueError("collect-k resolution must fail closed on overflow")
    expected_passed = (
        "published_capacity_ordering_overflow_contract",
        "python_fail_closed_reference_tests",
        "score_reduction_guarded_by_complete_collection",
    )
    if tuple(resolution["passed_gates"]) != expected_passed:
        raise ValueError("collect-k passed gate set must remain evidence-bounded")
    expected_failed = tuple(
        gate for gate in V1_5_COLLECT_K_BOUNDED_PROMOTION_GATES if gate not in expected_passed
    )
    if tuple(resolution["failed_gates"]) != expected_failed:
        raise ValueError("collect-k failed gate set mismatch")
    boundary = str(resolution["claim_boundary"])
    for required_boundary in (
        "defined but not complete",
        "keep experimental",
        "otherwise exclude row-returning apps",
    ):
        if required_boundary not in boundary:
            raise ValueError("collect-k resolution boundary is too broad")
    return resolution
