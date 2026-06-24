from __future__ import annotations

from dataclasses import dataclass


V4_OPERATOR_CATALOG_STATUS = "v4_development_catalog_not_release"

V4_TIER2_FIXED_RADIUS_COUNT_THRESHOLD = "fixed_radius_count_threshold"
V4_TIER2_CLOSEST_HIT_GROUPED_ARGMIN = "closest_hit_grouped_argmin"
V4_TIER2_RAY_TRIANGLE_ANY_HIT_FLAGS = "ray_triangle_any_hit_flags"

V4_TIER2_OPERATOR_SURFACES = {
    V4_TIER2_FIXED_RADIUS_COUNT_THRESHOLD: {
        "api_surface": "v4_fixed_radius_count_threshold_2d_device_arrays",
        "generic_primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
        "measured_partners": ("torch",),
        "declared_unmeasured_partners": ("cupy",),
        "continuation_class": "count_threshold",
    },
    V4_TIER2_CLOSEST_HIT_GROUPED_ARGMIN: {
        "api_surface": "v4_closest_hit_grouped_argmin_3d_device_arrays",
        "generic_primitive": "CLOSEST_HIT_GROUPED_ARGMIN_3D",
        "measured_partners": ("torch",),
        "declared_unmeasured_partners": ("cupy",),
        "continuation_class": "argmin",
    },
    V4_TIER2_RAY_TRIANGLE_ANY_HIT_FLAGS: {
        "api_surface": "v4_ray_triangle_any_hit_flags_2d_device_arrays",
        "generic_primitive": "RAY_TRIANGLE_ANY_HIT_FLAGS_2D",
        "measured_partners": ("torch",),
        "declared_unmeasured_partners": ("cupy",),
        "continuation_class": "any_hit_flag",
    },
}

V4_OPERATOR_ALIASES = {
    "fixed_radius": V4_TIER2_FIXED_RADIUS_COUNT_THRESHOLD,
    "radius_count_threshold": V4_TIER2_FIXED_RADIUS_COUNT_THRESHOLD,
    "count_threshold": V4_TIER2_FIXED_RADIUS_COUNT_THRESHOLD,
    "grouped_argmin": V4_TIER2_CLOSEST_HIT_GROUPED_ARGMIN,
    "closest_hit_argmin": V4_TIER2_CLOSEST_HIT_GROUPED_ARGMIN,
    "any_hit": V4_TIER2_RAY_TRIANGLE_ANY_HIT_FLAGS,
    "any_hit_flags": V4_TIER2_RAY_TRIANGLE_ANY_HIT_FLAGS,
}

V4_SCALAR_TIER3_CANDIDATE_CONTINUATIONS = {
    "custom_scalar_reduce",
    "custom_score",
    "custom_threshold",
    "custom_minmax",
}


@dataclass(frozen=True)
class V4OperatorPlan:
    """Planner result for one V4 operator or callback request."""

    request: str
    status: str
    tier: str
    api_surface: str | None
    generic_primitive: str | None
    measured_partner: bool
    partner: str
    continuation_class: str | None
    guidance: str
    release_claim_authorized: bool = False
    broad_v4_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    tier3_callback_claim_authorized: bool = False
    tier3_spike_authorized: bool = False
    app_specific_native_kernel_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "request": self.request,
            "status": self.status,
            "tier": self.tier,
            "api_surface": self.api_surface,
            "generic_primitive": self.generic_primitive,
            "measured_partner": self.measured_partner,
            "partner": self.partner,
            "continuation_class": self.continuation_class,
            "guidance": self.guidance,
            "release_claim_authorized": self.release_claim_authorized,
            "broad_v4_speedup_claim_authorized": self.broad_v4_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "tier3_callback_claim_authorized": self.tier3_callback_claim_authorized,
            "tier3_spike_authorized": self.tier3_spike_authorized,
            "app_specific_native_kernel_authorized": self.app_specific_native_kernel_authorized,
        }


def _normalize_operator_name(operator: str) -> str:
    key = str(operator).strip().lower().replace("-", "_").replace(" ", "_")
    return V4_OPERATOR_ALIASES.get(key, key)


def plan_v4_operator_request(
    operator: str,
    *,
    partner: str = "torch",
    callback_shape: str | None = None,
    numba_device_function: bool = False,
    mutates_shared_state: bool = False,
    variable_length_output: bool = False,
    dynamic_allocation: bool = False,
) -> V4OperatorPlan:
    """Classify a V4 request into Tier-2, Tier-3 spike, or rejected guidance.

    The planner is intentionally conservative. It does not execute callbacks or
    authorize release wording; it gives users the V4 boundary before they spend
    time on a path that the engine cannot honestly fuse.
    """

    partner = str(partner)
    normalized = _normalize_operator_name(operator)
    if partner not in {"torch", "cupy"}:
        raise ValueError("partner must be one of: torch, cupy")

    if normalized in V4_TIER2_OPERATOR_SURFACES and callback_shape in (None, "", "builtin"):
        surface = V4_TIER2_OPERATOR_SURFACES[normalized]
        measured = partner in surface["measured_partners"]
        status = "tier2_measured_ready" if measured else "tier2_declared_unmeasured_partner"
        guidance = (
            f"Use {surface['api_surface']} for this recognized fused operator."
            if measured
            else f"{surface['api_surface']} is measured for Torch only; treat {partner} as unmeasured."
        )
        return V4OperatorPlan(
            request=normalized,
            status=status,
            tier="tier2_fused_operator",
            api_surface=str(surface["api_surface"]),
            generic_primitive=str(surface["generic_primitive"]),
            measured_partner=measured,
            partner=partner,
            continuation_class=str(surface["continuation_class"]),
            guidance=guidance,
        )

    if mutates_shared_state or dynamic_allocation or variable_length_output:
        reasons = []
        if mutates_shared_state:
            reasons.append("shared mutation")
        if dynamic_allocation:
            reasons.append("dynamic allocation")
        if variable_length_output:
            reasons.append("variable-length output")
        return V4OperatorPlan(
            request=normalized,
            status="rejected_action_shaped_callback_deferred",
            tier="unsupported_v4_0_deferred",
            api_surface=None,
            generic_primitive=None,
            measured_partner=False,
            partner=partner,
            continuation_class=callback_shape,
            guidance=(
                "This callback is action-shaped ("
                + ", ".join(reasons)
                + "). V4.0 does not expose raw OptiX callbacks or app-specific native kernels; "
                "rewrite as a recognized reduce/filter operator or defer to a future constrained Tier-3 design."
            ),
        )

    callback_key = str(callback_shape or normalized).strip().lower().replace("-", "_").replace(" ", "_")
    if numba_device_function and callback_key in V4_SCALAR_TIER3_CANDIDATE_CONTINUATIONS:
        return V4OperatorPlan(
            request=normalized,
            status="tier3_spike_only_not_v4_0_release_surface",
            tier="tier3_numba_ptx_spike",
            api_surface=None,
            generic_primitive=None,
            measured_partner=False,
            partner=partner,
            continuation_class=callback_key,
            guidance=(
                "This is a scalar per-hit reduce candidate for the Numba->PTX->OptiX spike. "
                "It is not a V4.0 measured surface and must not be documented as supported until the spike links, runs, and is measured."
            ),
            tier3_spike_authorized=True,
        )

    return V4OperatorPlan(
        request=normalized,
        status="unsupported_no_fused_surface",
        tier="unsupported",
        api_surface=None,
        generic_primitive=None,
        measured_partner=False,
        partner=partner,
        continuation_class=callback_shape,
        guidance=(
            "No V4 fused operator matches this request. Use a measured Tier-2 operator, "
            "rewrite the logic as count/threshold/argmin/any-hit, or treat it as future Tier-3 research."
        ),
    )


def measured_v4_tier2_operator_catalog() -> list[dict[str, object]]:
    """Return the current measured V4 Tier-2 operator catalog."""

    rows: list[dict[str, object]] = []
    for name, surface in V4_TIER2_OPERATOR_SURFACES.items():
        rows.append(
            {
                "operator": name,
                "api_surface": surface["api_surface"],
                "generic_primitive": surface["generic_primitive"],
                "measured_partners": surface["measured_partners"],
                "declared_unmeasured_partners": surface["declared_unmeasured_partners"],
                "continuation_class": surface["continuation_class"],
                "release_claim_authorized": False,
                "tier3_callback_claim_authorized": False,
                "app_specific_native_kernel_authorized": False,
            }
        )
    return rows

