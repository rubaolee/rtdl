from __future__ import annotations

from typing import Any


V2_5_EXECUTION_PATH_POLICY_VERSION = "rtdl.v2_5.execution_path_policy.v1"
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
    errors: list[str] = []
    if direct["recommended_result_mode"] != V2_5_FIXED_RADIUS_AGGREGATE_DIRECT_GRAPH_MODE:
        errors.append("direct path must be recommended when no partner continuation is required")
    if same_stream["recommended_result_mode"] != V2_5_FIXED_RADIUS_AGGREGATE_SAME_STREAM_CUPY_MODE:
        errors.append("same-stream path must be recommended when partner continuation is required")
    if direct["hidden_auto_dispatch_allowed"] is not False:
        errors.append("hidden auto-dispatch must remain blocked")
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
        "operation": V2_5_FIXED_RADIUS_AGGREGATE_OPERATION,
        "errors": tuple(errors),
    }

