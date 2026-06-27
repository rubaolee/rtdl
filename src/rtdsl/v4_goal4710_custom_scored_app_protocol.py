from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4710_CUSTOM_SCORED_APP_PROTOCOL_STATUS = (
    "goal4710_ray_triangle_custom_scored_app_protocol_frozen_not_run"
)
V4_GOAL4710_NEXT_GOAL = "Goal4711 ray-triangle custom scored accumulation focused POD benchmark"


@dataclass(frozen=True)
class V4Goal4710Protocol:
    status: str
    app: str
    primary_callbacks: tuple[str, ...]
    control_callbacks: tuple[str, ...]
    regimes: tuple[str, ...]
    scales: tuple[int, ...]
    baselines: tuple[dict[str, object], ...]
    pass_conditions: tuple[str, ...]
    kill_conditions: tuple[str, ...]
    next_goal: str
    pod_authorized_for_next_goal: bool = True
    app_level_speed_claim_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "app": self.app,
            "primary_callbacks": self.primary_callbacks,
            "control_callbacks": self.control_callbacks,
            "regimes": self.regimes,
            "scales": self.scales,
            "baselines": self.baselines,
            "pass_conditions": self.pass_conditions,
            "kill_conditions": self.kill_conditions,
            "next_goal": self.next_goal,
            "pod_authorized_for_next_goal": self.pod_authorized_for_next_goal,
            "app_level_speed_claim_authorized": self.app_level_speed_claim_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
        }


def v4_goal4710_custom_scored_app_protocol() -> V4Goal4710Protocol:
    baselines = (
        {
            "name": "v2_14_strongest_available",
            "root": "/root/rtdl_v2_14_tag",
            "required_discovery": (
                "discover strongest semantically comparable route before timing: built-in fixed reduction if exactly equivalent, "
                "materialized hit IDs plus partner/device reduction, then host scalar fallback only if no stronger route exists"
            ),
        },
        {
            "name": "v3_0_2_strongest_available",
            "root": "/root/rtdl_v3_0_2_tag",
            "required_discovery": (
                "discover strongest semantically comparable current route before timing under the same callback semantics"
            ),
        },
        {
            "name": "v4_specialized_callback_candidate",
            "root": "/root/rtdl_v4_candidate_pod",
            "required_discovery": "use the Goal4700-4706 specialized direct-device callback path",
        },
        {
            "name": "v4_tier2_builtin_control",
            "root": "/root/rtdl_v4_candidate_pod",
            "required_discovery": "weighted_sum only; context/control row, not primary app-level win evidence",
        },
    )
    return V4Goal4710Protocol(
        status=V4_GOAL4710_CUSTOM_SCORED_APP_PROTOCOL_STATUS,
        app="ray_triangle_custom_scored_accumulation",
        primary_callbacks=("affine_score", "threshold_score", "minmax_score"),
        control_callbacks=("weighted_sum",),
        regimes=("dense_hits", "sparse_hits", "no_hit_empty_reduction"),
        scales=(262144, 524288),
        baselines=baselines,
        pass_conditions=(
            "correctness must pass for every callback x regime x scale x implementation row",
            "primary custom-callback geomean speedup over strongest V2.14 baseline must be >=1.50x",
            "primary custom-callback geomean speedup over strongest V3.0.2 baseline must be >=1.20x",
            "every primary callback must be >=1.10x over the strongest V3.0.2 baseline in both dense and sparse regimes",
            "weighted_sum is a control row only and cannot by itself support the app-level claim",
            "all denominators and fallback selections must be recorded before reading V4 timing",
        ),
        kill_conditions=(
            "any correctness failure kills the goal",
            "if V2/V3 denominator discovery is missing or only a known-slow fallback is used without proof no stronger route exists, the result is invalid",
            "if the win comes only from weighted_sum or operator-only rows, the app-level claim is invalid",
            "if primary custom-callback geomean over V3.0.2 is <1.20x, do not continue toward high-performance wording",
            "if any primary callback regresses below 0.95x versus V3.0.2, stop and diagnose before more POD spend",
        ),
        next_goal=V4_GOAL4710_NEXT_GOAL,
    )


def validate_v4_goal4710_custom_scored_app_protocol() -> dict[str, object]:
    protocol = v4_goal4710_custom_scored_app_protocol()
    payload = protocol.as_dict()
    missing: list[str] = []
    if payload["status"] != V4_GOAL4710_CUSTOM_SCORED_APP_PROTOCOL_STATUS:
        missing.append("status")
    if payload["app"] != "ray_triangle_custom_scored_accumulation":
        missing.append("app")
    if "weighted_sum" not in payload["control_callbacks"]:
        missing.append("weighted_control")
    for callback in ("affine_score", "threshold_score", "minmax_score"):
        if callback not in payload["primary_callbacks"]:
            missing.append(callback)
    for regime in ("dense_hits", "sparse_hits", "no_hit_empty_reduction"):
        if regime not in payload["regimes"]:
            missing.append(regime)
    for scale in (262144, 524288):
        if scale not in payload["scales"]:
            missing.append(str(scale))
    baseline_names = {row["name"] for row in payload["baselines"]}
    for name in ("v2_14_strongest_available", "v3_0_2_strongest_available", "v4_specialized_callback_candidate"):
        if name not in baseline_names:
            missing.append(name)
    if not any(">=1.50x" in item for item in payload["pass_conditions"]):
        missing.append("v2_speed_bar")
    if not any(">=1.20x" in item for item in payload["pass_conditions"]):
        missing.append("v3_speed_bar")
    if not any("correctness failure" in item for item in payload["kill_conditions"]):
        missing.append("correctness_kill")
    for key in ("app_level_speed_claim_authorized", "release_authorized", "performance_claim_authorized"):
        if payload[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "protocol": payload,
    }


__all__ = [
    "V4_GOAL4710_CUSTOM_SCORED_APP_PROTOCOL_STATUS",
    "V4_GOAL4710_NEXT_GOAL",
    "V4Goal4710Protocol",
    "v4_goal4710_custom_scored_app_protocol",
    "validate_v4_goal4710_custom_scored_app_protocol",
]
