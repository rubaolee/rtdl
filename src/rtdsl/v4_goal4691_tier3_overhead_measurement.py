from __future__ import annotations


V4_GOAL4691_TIER3_OVERHEAD_MEASUREMENT_STATUS = (
    "goal4691_tier3_callback_overhead_measured_not_support"
)
V4_GOAL4691_NEXT_GOAL = "Goal4692 tier3 support decision after overhead measurement"


def classify_v4_goal4691_overhead_ratio(ratio: float | None) -> str:
    if ratio is None:
        return "blocked_no_ratio"
    if ratio <= 1.50:
        return "pass_overhead_gate_not_support"
    if ratio > 2.00:
        return "hard_kill_overhead_too_high"
    return "yellow_overhead_between_pass_and_kill"


def validate_v4_goal4691_tier3_overhead_measurement_contract() -> dict[str, object]:
    missing: list[str] = []
    if classify_v4_goal4691_overhead_ratio(1.50) != "pass_overhead_gate_not_support":
        missing.append("pass_threshold")
    if classify_v4_goal4691_overhead_ratio(2.01) != "hard_kill_overhead_too_high":
        missing.append("kill_threshold")
    if classify_v4_goal4691_overhead_ratio(1.75) != "yellow_overhead_between_pass_and_kill":
        missing.append("yellow_threshold")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "goal_status": V4_GOAL4691_TIER3_OVERHEAD_MEASUREMENT_STATUS,
        "next_goal": V4_GOAL4691_NEXT_GOAL,
        "release_authorized": False,
        "tier3_public_support_authorized": False,
        "performance_claim_authorized": False,
    }


__all__ = [
    "V4_GOAL4691_TIER3_OVERHEAD_MEASUREMENT_STATUS",
    "V4_GOAL4691_NEXT_GOAL",
    "classify_v4_goal4691_overhead_ratio",
    "validate_v4_goal4691_tier3_overhead_measurement_contract",
]
