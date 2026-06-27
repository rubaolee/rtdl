from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4713_PROTOCOL_STATUS = "goal4713_custom_predicate_early_exit_protocol_frozen_not_run"
V4_GOAL4713_APP = "ray_triangle_custom_predicate_early_exit_multi_hit"
V4_GOAL4713_NEXT_GOAL = "Goal4714 custom predicate early-exit local runner and POD smoke gate"


@dataclass(frozen=True)
class V4Goal4713Protocol:
    status: str
    app: str
    primary_regimes: tuple[dict[str, object], ...]
    control_regimes: tuple[dict[str, object], ...]
    callback_variants: tuple[dict[str, object], ...]
    scales: tuple[int, ...]
    baselines: tuple[dict[str, object], ...]
    pass_conditions: tuple[str, ...]
    kill_conditions: tuple[str, ...]
    next_goal: str
    pod_authorized: bool = False
    release_authorized: bool = False
    formal_high_performance_authorized: bool = False
    app_level_speed_claim_authorized: bool = False
    public_tier3_support_authorized: bool = False
    arbitrary_callback_authorized: bool = False
    raw_optix_callback_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "app": self.app,
            "primary_regimes": self.primary_regimes,
            "control_regimes": self.control_regimes,
            "callback_variants": self.callback_variants,
            "scales": self.scales,
            "baselines": self.baselines,
            "pass_conditions": self.pass_conditions,
            "kill_conditions": self.kill_conditions,
            "next_goal": self.next_goal,
            "pod_authorized": self.pod_authorized,
            "release_authorized": self.release_authorized,
            "formal_high_performance_authorized": self.formal_high_performance_authorized,
            "app_level_speed_claim_authorized": self.app_level_speed_claim_authorized,
            "public_tier3_support_authorized": self.public_tier3_support_authorized,
            "arbitrary_callback_authorized": self.arbitrary_callback_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
        }


def v4_goal4713_custom_predicate_early_exit_protocol() -> V4Goal4713Protocol:
    primary_regimes = (
        {
            "name": "dense_early_accept_k8",
            "candidate_hits_per_ray": 8,
            "accept_layer": 0,
            "expected_v4_advantage": "V4 can terminate on first accepted candidate instead of materializing 8 candidates per ray.",
        },
        {
            "name": "dense_early_accept_k32",
            "candidate_hits_per_ray": 32,
            "accept_layer": 0,
            "expected_v4_advantage": "V4 can terminate on first accepted candidate instead of materializing 32 candidates per ray.",
        },
        {
            "name": "sparse_early_accept_k32",
            "candidate_hits_per_ray": 32,
            "active_ray_fraction": 0.25,
            "accept_layer": 0,
            "expected_v4_advantage": "V4 should still reduce materialization on active rays while preserving sparse correctness.",
        },
    )
    control_regimes = (
        {
            "name": "dense_late_accept_k32",
            "candidate_hits_per_ray": 32,
            "accept_layer": 31,
            "purpose": "control: little early-exit opportunity; should not be used as primary speed evidence.",
        },
        {
            "name": "dense_reject_all_k32",
            "candidate_hits_per_ray": 32,
            "accept_layer": None,
            "purpose": "control: callback rejects every candidate; verifies no false positives and exposes worst-case predicate cost.",
        },
        {
            "name": "no_hit_empty",
            "candidate_hits_per_ray": 0,
            "purpose": "control: validates empty traversal and no-hit accounting.",
        },
    )
    callback_variants = (
        {
            "name": "accept_layer_zero",
            "shape": "pure_boolean_numba_cabi_device_function",
            "semantics": "return true when layer index is zero",
        },
        {
            "name": "accept_layer_threshold",
            "shape": "pure_boolean_numba_cabi_device_function",
            "semantics": "return true when layer index is less than a frozen scalar threshold",
        },
    )
    baselines = (
        {
            "name": "v2_14_materialized_all_hits_device_predicate",
            "root": "/root/rtdl_v2_14_tag",
            "required_discovery": "confirm no custom predicate any-hit early-exit route exists; fallback materializes all candidate hit IDs/attributes then filters on device",
        },
        {
            "name": "v3_0_2_materialized_all_hits_device_predicate",
            "root": "/root/rtdl_v3_0_2_tag",
            "required_discovery": "confirm no custom predicate any-hit early-exit route exists; fallback materializes all candidate hit IDs/attributes then filters on device",
        },
        {
            "name": "v4_callback_predicate_early_exit",
            "root": "/root/rtdl_v4_candidate_pod",
            "required_discovery": "generated OptiX any-hit route evaluates pure predicate callback and RTDL applies terminate_on_first_accept",
        },
    )
    return V4Goal4713Protocol(
        status=V4_GOAL4713_PROTOCOL_STATUS,
        app=V4_GOAL4713_APP,
        primary_regimes=primary_regimes,
        control_regimes=control_regimes,
        callback_variants=callback_variants,
        scales=(65536, 131072),
        baselines=baselines,
        pass_conditions=(
            "correctness must pass for every callback x regime x scale x implementation row",
            "primary early-accept regimes geomean V4 over V3.0.2 must be >=1.50x",
            "primary early-accept regimes geomean V4 over V2.14 must be >=1.50x",
            "every primary early-accept regime at every scale must be >=1.20x over V3.0.2",
            "control regimes must preserve correctness and must not regress below 0.95x geomean over V3.0.2",
            "wins from late-accept, reject-all, no-hit, weighted-sum, or post-hit accumulation controls cannot support the primary claim",
            "all denominators and fallback selections must be recorded before V4 timing",
        ),
        kill_conditions=(
            "any correctness failure kills the goal",
            "missing V2/V3 denominator discovery invalidates the run",
            "if V4 cannot prove early termination occurred in primary regimes, the run is invalid",
            "if primary early-accept geomean over V3.0.2 is <1.50x, do not continue toward formal high-performance wording",
            "if any primary early-accept row is below 1.00x over V3.0.2, stop and diagnose before more POD spend",
            "if control-regime correctness fails, do not promote the route even if primary speed rows pass",
        ),
        next_goal=V4_GOAL4713_NEXT_GOAL,
    )


def validate_v4_goal4713_custom_predicate_early_exit_protocol() -> dict[str, object]:
    protocol = v4_goal4713_custom_predicate_early_exit_protocol()
    payload = protocol.as_dict()
    missing: list[str] = []
    if payload["status"] != V4_GOAL4713_PROTOCOL_STATUS:
        missing.append("status")
    if payload["app"] != V4_GOAL4713_APP:
        missing.append("app")
    primary_names = {str(row["name"]) for row in payload["primary_regimes"]}
    for name in ("dense_early_accept_k8", "dense_early_accept_k32", "sparse_early_accept_k32"):
        if name not in primary_names:
            missing.append(name)
    control_names = {str(row["name"]) for row in payload["control_regimes"]}
    for name in ("dense_late_accept_k32", "dense_reject_all_k32", "no_hit_empty"):
        if name not in control_names:
            missing.append(name)
    if not any(int(row["candidate_hits_per_ray"]) >= 32 for row in payload["primary_regimes"]):
        missing.append("primary_k32")
    if not any(">=1.50x" in item for item in payload["pass_conditions"]):
        missing.append("primary_speed_bar")
    if not any("early termination" in item for item in payload["kill_conditions"]):
        missing.append("early_termination_evidence")
    if payload["pod_authorized"] is not False:
        missing.append("pod_authorized")
    for key in (
        "release_authorized",
        "formal_high_performance_authorized",
        "app_level_speed_claim_authorized",
        "public_tier3_support_authorized",
        "arbitrary_callback_authorized",
        "raw_optix_callback_authorized",
    ):
        if payload[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "protocol": payload,
    }


__all__ = [
    "V4_GOAL4713_PROTOCOL_STATUS",
    "V4_GOAL4713_APP",
    "V4_GOAL4713_NEXT_GOAL",
    "V4Goal4713Protocol",
    "v4_goal4713_custom_predicate_early_exit_protocol",
    "validate_v4_goal4713_custom_predicate_early_exit_protocol",
]
