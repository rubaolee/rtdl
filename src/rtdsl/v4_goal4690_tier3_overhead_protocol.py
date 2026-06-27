from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4690_TIER3_OVERHEAD_PROTOCOL_STATUS = (
    "goal4690_tier3_callback_overhead_protocol_frozen_not_measured"
)
V4_GOAL4690_NEXT_GOAL = "Goal4691 tier3 callback overhead pod measurement"


@dataclass(frozen=True)
class V4Goal4690Tier3OverheadProtocol:
    status: str
    callback_shape: str
    primary_ratio: str
    inner_iterations: int
    warmup_launches: int
    measured_launches: int
    pass_ratio_max: float
    hard_kill_ratio_min: float
    correctness_required: bool
    baseline_variants: tuple[str, ...]
    measured_variants: tuple[str, ...]
    next_goal: str
    pod_authorized: bool = False
    tier3_public_support_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "callback_shape": self.callback_shape,
            "primary_ratio": self.primary_ratio,
            "inner_iterations": self.inner_iterations,
            "warmup_launches": self.warmup_launches,
            "measured_launches": self.measured_launches,
            "pass_ratio_max": self.pass_ratio_max,
            "hard_kill_ratio_min": self.hard_kill_ratio_min,
            "correctness_required": self.correctness_required,
            "baseline_variants": self.baseline_variants,
            "measured_variants": self.measured_variants,
            "next_goal": self.next_goal,
            "pod_authorized": self.pod_authorized,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
        }


def v4_goal4690_tier3_overhead_protocol() -> V4Goal4690Tier3OverheadProtocol:
    return V4Goal4690Tier3OverheadProtocol(
        status=V4_GOAL4690_TIER3_OVERHEAD_PROTOCOL_STATUS,
        callback_shape="double_return_four_args_scalar_reduce",
        primary_ratio="direct_callable_loop_median_ms / direct_device_function_loop_median_ms",
        inner_iterations=1_000_000,
        warmup_launches=5,
        measured_launches=30,
        pass_ratio_max=1.50,
        hard_kill_ratio_min=2.00,
        correctness_required=True,
        baseline_variants=(
            "direct_device_function_loop_same_numba_callback",
            "inline_formula_loop_context_only",
        ),
        measured_variants=("optix_direct_callable_loop_same_numba_callback",),
        next_goal=V4_GOAL4690_NEXT_GOAL,
    )


def validate_v4_goal4690_tier3_overhead_protocol() -> dict[str, object]:
    protocol = v4_goal4690_tier3_overhead_protocol()
    payload = protocol.as_dict()
    missing: list[str] = []
    if payload["status"] != V4_GOAL4690_TIER3_OVERHEAD_PROTOCOL_STATUS:
        missing.append("status")
    if payload["callback_shape"] != "double_return_four_args_scalar_reduce":
        missing.append("callback_shape")
    if payload["inner_iterations"] < 100_000:
        missing.append("inner_iterations")
    if payload["warmup_launches"] < 3:
        missing.append("warmup_launches")
    if payload["measured_launches"] < 20:
        missing.append("measured_launches")
    if payload["pass_ratio_max"] != 1.50:
        missing.append("pass_ratio_max")
    if payload["hard_kill_ratio_min"] != 2.00:
        missing.append("hard_kill_ratio_min")
    if payload["correctness_required"] is not True:
        missing.append("correctness_required")
    baselines = tuple(payload["baseline_variants"])
    measured = tuple(payload["measured_variants"])
    if "direct_device_function_loop_same_numba_callback" not in baselines:
        missing.append("direct_device_function_baseline")
    if "inline_formula_loop_context_only" not in baselines:
        missing.append("inline_formula_context")
    if "optix_direct_callable_loop_same_numba_callback" not in measured:
        missing.append("direct_callable_variant")
    for key in (
        "pod_authorized",
        "tier3_public_support_authorized",
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
    "V4_GOAL4690_TIER3_OVERHEAD_PROTOCOL_STATUS",
    "V4_GOAL4690_NEXT_GOAL",
    "V4Goal4690Tier3OverheadProtocol",
    "v4_goal4690_tier3_overhead_protocol",
    "validate_v4_goal4690_tier3_overhead_protocol",
]
