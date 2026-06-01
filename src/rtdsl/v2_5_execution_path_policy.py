from __future__ import annotations

from typing import Any


V2_5_EXECUTION_PATH_POLICY_VERSION = "rtdl.v2_5.execution_path_policy.v1"
V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_VERSION = (
    "rtdl.v2_5.primitive_first_selection_doctrine.v1"
)
V2_5_FIXED_RADIUS_AGGREGATE_DIRECT_GRAPH_MODE = (
    "ranked-summary-aggregate-prepared-query-batch-graph-float32"
)
V2_5_FIXED_RADIUS_AGGREGATE_SAME_STREAM_CUPY_MODE = (
    "ranked-summary-aggregate-prepared-query-batch-graph-same-stream-cupy-float32"
)
V2_5_FIXED_RADIUS_AGGREGATE_OPERATION = "fixed_radius_ranked_summary_aggregate_3d"
V2_5_EXECUTION_PATH_POLICY_CLAIM_BOUNDARY = (
    "v2.5 execution-path policy is explain-only guidance. It does not hide "
    "dispatch, force a partner, authorize public speedup wording, authorize "
    "RT-core speedup wording, authorize whole-app speedup wording, authorize "
    "true zero-copy wording, or authorize release readiness."
)
V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_CLAIM_BOUNDARY = (
    "v2.5 primitive-first selection doctrine is closeout policy only. It does "
    "not authorize release readiness, public speedup wording, whole-app speedup "
    "wording, broad RT-core wording, true zero-copy wording, automatic Triton "
    "selection, or app-specific native-engine behavior."
)


def v2_5_primitive_first_selection_doctrine() -> dict[str, Any]:
    """Return the v2.5 closeout selection doctrine.

    This is the post-Goal2896 rule: if a fused generic RTDL primitive exactly
    expresses the continuation, use that primitive-first path. Partners are
    for explicitly chosen, same-contract continuations that cannot be fused
    into the native primitive.
    """

    return {
        "doctrine_version": V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_VERSION,
        "status": "closeout_policy_not_release_authorization",
        "fast_path_rule": "primitive_first_native_rtdl_when_fused_generic_primitive_exactly_expresses_continuation",
        "partner_use_rule": "partner_continuation_only_for_unfused_continuations_or_explicit_app_choice",
        "partner_choice_rule": "choose_partner_by_same_contract_evidence_never_by_default",
        "tier_b_definition": (
            "Tier B means an explicit partner continuation is needed because no "
            "fused native primitive exactly expresses the continuation; it does "
            "not mean Triton is the selected or fastest partner."
        ),
        "triton_role": "preview_partner_candidate_not_default",
        "numba_role": "declared_generic_fallback_partner",
        "cupy_torch_role": "allowed_explicit_app_or_conformance_partners_when_same_contract_evidence_wins",
        "hidden_dispatch_allowed": False,
        "automatic_triton_selection_allowed": False,
        "automatic_partner_selection_allowed": False,
        "triton_default_allowed": False,
        "preview_kernel_availability_implies_selection": False,
        "same_contract_evidence_required": True,
        "phase_separated_timing_required": True,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "release_readiness_authorized": False,
        "source_reports": (
            "docs/reports/goal2898_raydb_perf_gate_readiness_integration_2026-05-31.md",
            "docs/reports/goal2976_v2_5_release_gap_position_after_toolchain_scope_2026-06-01.md",
            "docs/reports/claude_v2_5_closeout_and_v3_0_residency_first_roadmap_2026-05-31.md",
        ),
        "claim_boundary": V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_CLAIM_BOUNDARY,
    }


def validate_v2_5_primitive_first_selection_doctrine(
    doctrine: dict[str, Any] | None = None,
) -> dict[str, Any]:
    doctrine = v2_5_primitive_first_selection_doctrine() if doctrine is None else doctrine
    errors: list[str] = []
    if doctrine.get("doctrine_version") != V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_VERSION:
        errors.append("unexpected primitive-first doctrine version")
    if "primitive_first" not in str(doctrine.get("fast_path_rule", "")):
        errors.append("doctrine must name primitive-first as the fast path")
    if "unfused" not in str(doctrine.get("partner_use_rule", "")):
        errors.append("doctrine must reserve partner continuations for unfused work")
    if "same_contract" not in str(doctrine.get("partner_choice_rule", "")):
        errors.append("doctrine must require same-contract partner evidence")
    if "no fused native primitive" not in str(doctrine.get("tier_b_definition", "")):
        errors.append("Tier B definition must be coverage/unfused-continuation based")
    if doctrine.get("same_contract_evidence_required") is not True:
        errors.append("same-contract evidence must be required")
    if doctrine.get("phase_separated_timing_required") is not True:
        errors.append("phase-separated timing must be required")
    for field in (
        "hidden_dispatch_allowed",
        "automatic_triton_selection_allowed",
        "automatic_partner_selection_allowed",
        "triton_default_allowed",
        "preview_kernel_availability_implies_selection",
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "release_readiness_authorized",
    ):
        if doctrine.get(field) is not False:
            errors.append(f"{field} must remain false")
    return {
        "status": "accept" if not errors else "reject",
        "doctrine_version": doctrine.get("doctrine_version"),
        "errors": tuple(errors),
    }


def plan_v2_5_fixed_radius_aggregate_execution_path(
    *,
    requires_partner_continuation: bool,
    backend: str = "optix",
    partner: str = "cupy_conformance",
    prefer_fastest_native_aggregate: bool = True,
) -> dict[str, Any]:
    """Explain the v2.5 path choice for fixed-radius aggregate replay.

    Goal2841 showed that the same-stream CuPy consumer is correct and traceable,
    but slower than direct native graph replay when the app only needs the final
    native aggregate. This helper keeps that rule explicit instead of burying it
    in a hidden dispatcher.
    """

    normalized_backend = str(backend).strip().lower()
    normalized_partner = str(partner).strip().lower().replace("-", "_")
    continuation_required = bool(requires_partner_continuation)
    reasons: list[str] = []
    warnings: list[str] = []

    if normalized_backend != "optix":
        recommended_mode = "backend_specific_policy_required"
        selected_path = "no_optix_graph_policy"
        reasons.append("The measured Goal2841 policy applies only to the OptiX fixed-radius graph path.")
        warnings.append("Use explicit backend-specific measurement before selecting this path.")
    elif continuation_required:
        recommended_mode = V2_5_FIXED_RADIUS_AGGREGATE_SAME_STREAM_CUPY_MODE
        selected_path = "same_stream_partner_continuation"
        reasons.append("A partner continuation is required, so same-stream ordering and entrypoint metadata matter.")
        reasons.append("Goal2841 proves this path is traceable but slower than direct native graph replay.")
    else:
        recommended_mode = V2_5_FIXED_RADIUS_AGGREGATE_DIRECT_GRAPH_MODE
        selected_path = "direct_native_graph_replay"
        reasons.append("No partner continuation is required, so direct native graph replay is the fastest measured path.")
        reasons.append("Goal2841 measured same-stream replay at 1.923x the direct median on the 65K fixture.")

    explicit_mode_required = True
    return {
        "policy_version": V2_5_EXECUTION_PATH_POLICY_VERSION,
        "primitive_first_selection_doctrine_version": V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_VERSION,
        "operation": V2_5_FIXED_RADIUS_AGGREGATE_OPERATION,
        "backend": normalized_backend,
        "partner": normalized_partner,
        "requires_partner_continuation": continuation_required,
        "prefer_fastest_native_aggregate": bool(prefer_fastest_native_aggregate),
        "selected_path": selected_path,
        "recommended_result_mode": recommended_mode,
        "direct_native_graph_result_mode": V2_5_FIXED_RADIUS_AGGREGATE_DIRECT_GRAPH_MODE,
        "same_stream_partner_result_mode": V2_5_FIXED_RADIUS_AGGREGATE_SAME_STREAM_CUPY_MODE,
        "direct_native_graph_preferred_when_no_partner_continuation": normalized_backend == "optix"
        and not continuation_required,
        "same_stream_required_for_partner_continuation": normalized_backend == "optix"
        and continuation_required,
        "same_stream_over_direct_median_ratio": 1.9232031759290225,
        "same_stream_slower_than_direct_on_goal2841_fixture": True,
        "evidence_goal": "Goal2841",
        "evidence_artifact": "docs/reports/goal2841_rtnn_same_stream_scale_pod/goal2841_summary.json",
        "explicit_result_mode_required": explicit_mode_required,
        "hidden_auto_dispatch_allowed": False,
        "primitive_first_native_when_no_partner_continuation": normalized_backend == "optix"
        and not continuation_required,
        "partner_continuation_reserved_for_required_continuation": normalized_backend == "optix"
        and continuation_required,
        "automatic_triton_selection_allowed": False,
        "auto_select_same_stream_for_speed_allowed": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "release_readiness_authorized": False,
        "reasons": tuple(reasons),
        "warnings": tuple(warnings),
        "claim_boundary": V2_5_EXECUTION_PATH_POLICY_CLAIM_BOUNDARY,
    }


def validate_v2_5_execution_path_policy() -> dict[str, Any]:
    direct = plan_v2_5_fixed_radius_aggregate_execution_path(
        requires_partner_continuation=False
    )
    same_stream = plan_v2_5_fixed_radius_aggregate_execution_path(
        requires_partner_continuation=True
    )
    doctrine = v2_5_primitive_first_selection_doctrine()
    errors: list[str] = []
    doctrine_validation = validate_v2_5_primitive_first_selection_doctrine(doctrine)
    errors.extend(str(error) for error in doctrine_validation["errors"])
    if direct["recommended_result_mode"] != V2_5_FIXED_RADIUS_AGGREGATE_DIRECT_GRAPH_MODE:
        errors.append("direct path must be recommended when no partner continuation is required")
    if same_stream["recommended_result_mode"] != V2_5_FIXED_RADIUS_AGGREGATE_SAME_STREAM_CUPY_MODE:
        errors.append("same-stream path must be recommended when partner continuation is required")
    if direct["hidden_auto_dispatch_allowed"] is not False:
        errors.append("hidden auto-dispatch must remain blocked")
    if direct["primitive_first_native_when_no_partner_continuation"] is not True:
        errors.append("direct path must integrate primitive-first doctrine")
    if same_stream["automatic_triton_selection_allowed"] is not False:
        errors.append("automatic Triton selection must remain blocked")
    if same_stream["auto_select_same_stream_for_speed_allowed"] is not False:
        errors.append("same-stream must not be auto-selected for speed")
    for plan in (direct, same_stream):
        for field in (
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "release_readiness_authorized",
        ):
            if plan[field] is not False:
                errors.append(f"{field} must remain false")
        if float(plan["same_stream_over_direct_median_ratio"]) <= 1.0:
            errors.append("Goal2841 cost boundary must record same-stream as slower than direct")
    return {
        "status": "accept" if not errors else "reject",
        "policy_version": V2_5_EXECUTION_PATH_POLICY_VERSION,
        "primitive_first_selection_doctrine_version": V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_VERSION,
        "operation": V2_5_FIXED_RADIUS_AGGREGATE_OPERATION,
        "errors": tuple(errors),
    }
