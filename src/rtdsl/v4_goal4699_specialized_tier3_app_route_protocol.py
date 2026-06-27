from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4699_SPECIALIZED_TIER3_APP_ROUTE_PROTOCOL_STATUS = (
    "goal4699_specialized_tier3_app_route_validation_protocol_frozen_not_run"
)
V4_GOAL4699_NEXT_GOAL = "Goal4700 specialized Tier-3 app-route POD implementation"


@dataclass(frozen=True)
class V4Goal4699AppRouteProtocol:
    status: str
    selected_route: str
    selected_surface: str
    callback_contract: str
    correctness_denominator: str
    primary_performance_denominator: str
    context_denominator: str
    ray_counts: tuple[int, ...]
    warmup: int
    repeat: int
    callback_over_tier2_pass_ratio_max: float
    callback_over_tier2_hard_kill_ratio: float
    callback_over_context_speedup_min: float
    parity_requirement: str
    required_telemetry: tuple[str, ...]
    next_goal: str
    pod_required_for_next_goal: bool = True
    tier3_public_support_authorized: bool = False
    app_level_speed_claim_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "selected_route": self.selected_route,
            "selected_surface": self.selected_surface,
            "callback_contract": self.callback_contract,
            "correctness_denominator": self.correctness_denominator,
            "primary_performance_denominator": self.primary_performance_denominator,
            "context_denominator": self.context_denominator,
            "ray_counts": self.ray_counts,
            "warmup": self.warmup,
            "repeat": self.repeat,
            "callback_over_tier2_pass_ratio_max": self.callback_over_tier2_pass_ratio_max,
            "callback_over_tier2_hard_kill_ratio": self.callback_over_tier2_hard_kill_ratio,
            "callback_over_context_speedup_min": self.callback_over_context_speedup_min,
            "parity_requirement": self.parity_requirement,
            "required_telemetry": self.required_telemetry,
            "next_goal": self.next_goal,
            "pod_required_for_next_goal": self.pod_required_for_next_goal,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "app_level_speed_claim_authorized": self.app_level_speed_claim_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
        }


def v4_goal4699_specialized_tier3_app_route_protocol() -> V4Goal4699AppRouteProtocol:
    return V4Goal4699AppRouteProtocol(
        status=V4_GOAL4699_SPECIALIZED_TIER3_APP_ROUTE_PROTOCOL_STATUS,
        selected_route="ray_triangle_any_hit_weighted_sum_scalar_reduce",
        selected_surface="v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
        callback_contract="Goal4697 module_specialized_direct_device_callback / pure scalar Numba C-ABI callback",
        correctness_denominator="existing Tier-2 built-in weighted-sum device-output route, exact uint64 output",
        primary_performance_denominator="existing Tier-2 built-in weighted-sum fused route on the same fixture",
        context_denominator="legacy host-scalar/materialized weighted-sum route from Goal4633",
        ray_counts=(32768, 131072, 262144),
        warmup=3,
        repeat=10,
        callback_over_tier2_pass_ratio_max=1.20,
        callback_over_tier2_hard_kill_ratio=1.50,
        callback_over_context_speedup_min=1.20,
        parity_requirement="exact equality to Tier-2 built-in weighted-hit-sum for every tested size",
        required_telemetry=(
            "callback_contract_status",
            "compile_cache_key",
            "compile_stage",
            "tier3_callback_route_median_s",
            "tier2_builtin_route_median_s",
            "legacy_host_scalar_route_median_s",
            "callback_over_tier2_ratio",
            "legacy_host_over_callback_ratio",
            "parity_passed",
            "tier3_public_support_authorized_false",
        ),
        next_goal=V4_GOAL4699_NEXT_GOAL,
    )


def validate_v4_goal4699_specialized_tier3_app_route_protocol() -> dict[str, object]:
    protocol = v4_goal4699_specialized_tier3_app_route_protocol()
    payload = protocol.as_dict()
    missing: list[str] = []
    if payload["status"] != V4_GOAL4699_SPECIALIZED_TIER3_APP_ROUTE_PROTOCOL_STATUS:
        missing.append("status")
    if payload["selected_surface"] != "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays":
        missing.append("selected_surface")
    if "Tier-2 built-in" not in str(payload["primary_performance_denominator"]):
        missing.append("tier2_denominator")
    if payload["ray_counts"] != (32768, 131072, 262144):
        missing.append("ray_counts")
    if float(payload["callback_over_tier2_pass_ratio_max"]) > 1.20:
        missing.append("pass_ratio")
    if float(payload["callback_over_tier2_hard_kill_ratio"]) > 1.50:
        missing.append("hard_kill_ratio")
    if "exact equality" not in str(payload["parity_requirement"]):
        missing.append("parity")
    required_telemetry = tuple(payload["required_telemetry"])
    for required in (
        "compile_cache_key",
        "callback_over_tier2_ratio",
        "legacy_host_over_callback_ratio",
        "parity_passed",
        "tier3_public_support_authorized_false",
    ):
        if required not in required_telemetry:
            missing.append(required)
    for key in (
        "tier3_public_support_authorized",
        "app_level_speed_claim_authorized",
        "release_authorized",
        "performance_claim_authorized",
    ):
        if payload[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "protocol": payload,
    }


__all__ = [
    "V4_GOAL4699_SPECIALIZED_TIER3_APP_ROUTE_PROTOCOL_STATUS",
    "V4_GOAL4699_NEXT_GOAL",
    "V4Goal4699AppRouteProtocol",
    "v4_goal4699_specialized_tier3_app_route_protocol",
    "validate_v4_goal4699_specialized_tier3_app_route_protocol",
]
