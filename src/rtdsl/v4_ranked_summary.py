from __future__ import annotations

from typing import Any

from .prepared_execution import PreparedExecutionSessionResult
from .prepared_execution import run_fixed_radius_ranked_summary_3d_prepared_session


V4_FIXED_RADIUS_RANKED_SUMMARY_3D_PREPARED_RUNNER_SURFACE = (
    "v4_fixed_radius_ranked_summary_3d_prepared_runner"
)
V4_FIXED_RADIUS_RANKED_SUMMARY_3D_CANDIDATE_STATUS = (
    "candidate_goal4660_needs_pod_scorecard_not_release"
)
V4_FIXED_RADIUS_RANKED_SUMMARY_3D_DEFERRED_STATUS = (
    "deferred_serious_scale_not_v4_0_release_surface"
)


def fixed_radius_ranked_summary_3d_prepared_runner_claim_boundary_v4(
    *,
    partner: str = "none",
) -> dict[str, object]:
    """Return the V4 claim boundary for the ranked-summary prepared runner."""

    return {
        "status": V4_FIXED_RADIUS_RANKED_SUMMARY_3D_DEFERRED_STATUS,
        "v4_api_surface": V4_FIXED_RADIUS_RANKED_SUMMARY_3D_PREPARED_RUNNER_SURFACE,
        "generic_primitive": "FIXED_RADIUS_RANKED_SUMMARY_3D",
        "continuation_class": "ranked_summary_topk",
        "partner": str(partner),
        "candidate_surface": False,
        "deferred_surface": True,
        "measured_v4_release_surface": False,
        "goal4678_no_go_reason": (
            "Goal4660/4661 serious rows executed and validated, but 262144-point "
            "rows were parity and 1048576-point rows were below parity; this does "
            "not move the RTNN app-level bar."
        ),
        "native_prepared_search_owned_by_rtdl": True,
        "app_specific_native_kernel_authorized": False,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "true_zero_copy_authorized": False,
        "tier3_callback_claim_authorized": False,
        "full_rtnn_paper_reproduction": False,
    }


def _with_v4_ranked_summary_metadata(
    result: PreparedExecutionSessionResult,
    *,
    partner: str,
) -> PreparedExecutionSessionResult:
    metadata = result.to_metadata()
    metadata.update(
        {
            "v4_surface": V4_FIXED_RADIUS_RANKED_SUMMARY_3D_PREPARED_RUNNER_SURFACE,
            "v4_candidate_status": V4_FIXED_RADIUS_RANKED_SUMMARY_3D_DEFERRED_STATUS,
            "generic_primitive": "FIXED_RADIUS_RANKED_SUMMARY_3D",
            "continuation_class": "ranked_summary_topk",
            "measured_v4_release_surface": False,
            "app_specific_native_kernel_authorized": False,
            "release_claim_authorized": False,
            "broad_v4_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    metadata["v4_claim_boundary"] = fixed_radius_ranked_summary_3d_prepared_runner_claim_boundary_v4(
        partner=partner
    )
    return PreparedExecutionSessionResult(
        prepared_value=result.prepared_value,
        output=result.output,
        validation_output=result.validation_output,
        metadata=metadata,
    )


def run_fixed_radius_ranked_summary_3d_prepared_runner_v4(
    *,
    search_points: Any,
    query_points: Any,
    radius: float,
    k_max: int,
    backend: str = "optix",
    partner: str = "none",
    **kwargs: Any,
) -> PreparedExecutionSessionResult:
    """Run the generic fixed-radius ranked-summary prepared runner as V4-deferred.

    This wrapper deliberately delegates to the existing generic prepared-session
    runner. Its job is not to claim new performance; Goal4678 keeps it out of
    the measured and candidate front doors after serious-scale parity evidence.
    """

    result = run_fixed_radius_ranked_summary_3d_prepared_session(
        search_points=search_points,
        query_points=query_points,
        radius=radius,
        k_max=k_max,
        backend=backend,
        partner=partner,
        **kwargs,
    )
    return _with_v4_ranked_summary_metadata(result, partner=partner)
