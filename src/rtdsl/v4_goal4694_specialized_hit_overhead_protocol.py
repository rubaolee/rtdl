from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4694_SPECIALIZED_HIT_OVERHEAD_PROTOCOL_STATUS = (
    "goal4694_specialized_hit_callback_overhead_protocol_frozen_not_measured"
)
V4_GOAL4694_NEXT_GOAL = "Goal4695 specialized hit callback overhead POD measurement"


@dataclass(frozen=True)
class V4Goal4694SpecializedHitOverheadProtocol:
    status: str
    primary_ratio: str
    trace_iterations: int
    warmup_launches: int
    measured_launches: int
    pass_ratio_max: float
    hard_kill_ratio_min: float
    correctness_required: bool
    baseline_variant: str
    measured_variant: str
    next_goal: str
    release_authorized: bool = False
    tier3_public_support_authorized: bool = False
    performance_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "primary_ratio": self.primary_ratio,
            "trace_iterations": self.trace_iterations,
            "warmup_launches": self.warmup_launches,
            "measured_launches": self.measured_launches,
            "pass_ratio_max": self.pass_ratio_max,
            "hard_kill_ratio_min": self.hard_kill_ratio_min,
            "correctness_required": self.correctness_required,
            "baseline_variant": self.baseline_variant,
            "measured_variant": self.measured_variant,
            "next_goal": self.next_goal,
            "release_authorized": self.release_authorized,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
        }


def v4_goal4694_specialized_hit_overhead_protocol() -> V4Goal4694SpecializedHitOverheadProtocol:
    return V4Goal4694SpecializedHitOverheadProtocol(
        status=V4_GOAL4694_SPECIALIZED_HIT_OVERHEAD_PROTOCOL_STATUS,
        primary_ratio="hit_direct_device_callback_trace_loop_median_ms / hit_inline_formula_trace_loop_median_ms",
        trace_iterations=100_000,
        warmup_launches=3,
        measured_launches=20,
        pass_ratio_max=1.50,
        hard_kill_ratio_min=2.00,
        correctness_required=True,
        baseline_variant="hit_inline_formula_trace_loop_context",
        measured_variant="hit_direct_device_callback_trace_loop",
        next_goal=V4_GOAL4694_NEXT_GOAL,
    )


def validate_v4_goal4694_specialized_hit_overhead_protocol() -> dict[str, object]:
    protocol = v4_goal4694_specialized_hit_overhead_protocol()
    payload = protocol.as_dict()
    missing: list[str] = []
    if payload["status"] != V4_GOAL4694_SPECIALIZED_HIT_OVERHEAD_PROTOCOL_STATUS:
        missing.append("status")
    if payload["trace_iterations"] < 10_000:
        missing.append("trace_iterations")
    if payload["warmup_launches"] < 3:
        missing.append("warmup_launches")
    if payload["measured_launches"] < 20:
        missing.append("measured_launches")
    if payload["pass_ratio_max"] != 1.50:
        missing.append("pass_ratio_max")
    if payload["hard_kill_ratio_min"] != 2.00:
        missing.append("hard_kill_ratio_min")
    if payload["baseline_variant"] != "hit_inline_formula_trace_loop_context":
        missing.append("baseline_variant")
    if payload["measured_variant"] != "hit_direct_device_callback_trace_loop":
        missing.append("measured_variant")
    for key in ("release_authorized", "tier3_public_support_authorized", "performance_claim_authorized"):
        if payload[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "protocol": payload,
    }


__all__ = [
    "V4_GOAL4694_SPECIALIZED_HIT_OVERHEAD_PROTOCOL_STATUS",
    "V4_GOAL4694_NEXT_GOAL",
    "V4Goal4694SpecializedHitOverheadProtocol",
    "v4_goal4694_specialized_hit_overhead_protocol",
    "validate_v4_goal4694_specialized_hit_overhead_protocol",
]
