from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4692_TIER3_SUPPORT_DECISION_STATUS = (
    "goal4692_tier3_direct_callable_yellow_pivot_to_specialized_device_callback"
)
V4_GOAL4692_NEXT_GOAL = "Goal4693 specialized direct-device callback inside OptiX hit-program probe"


@dataclass(frozen=True)
class V4Goal4692Tier3SupportDecision:
    status: str
    measured_direct_callable_ratio: float
    decision: str
    selected_next_track: str
    next_goal: str
    direct_callable_public_support_authorized: bool = False
    specialized_device_callback_public_support_authorized: bool = False
    tier3_public_support_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "measured_direct_callable_ratio": self.measured_direct_callable_ratio,
            "decision": self.decision,
            "selected_next_track": self.selected_next_track,
            "next_goal": self.next_goal,
            "direct_callable_public_support_authorized": self.direct_callable_public_support_authorized,
            "specialized_device_callback_public_support_authorized": self.specialized_device_callback_public_support_authorized,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
        }


def v4_goal4692_tier3_support_decision() -> V4Goal4692Tier3SupportDecision:
    return V4Goal4692Tier3SupportDecision(
        status=V4_GOAL4692_TIER3_SUPPORT_DECISION_STATUS,
        measured_direct_callable_ratio=1.6705538933080346,
        decision=(
            "do_not_promote_sbt_direct_callable_support; continue Tier-3 through "
            "module-specialized direct device callback because the same Numba "
            "callback denominator ran correctly without OptiX callable SBT overhead"
        ),
        selected_next_track="module_specialized_direct_device_callback_in_hit_program",
        next_goal=V4_GOAL4692_NEXT_GOAL,
    )


def validate_v4_goal4692_tier3_support_decision() -> dict[str, object]:
    decision = v4_goal4692_tier3_support_decision()
    payload = decision.as_dict()
    missing: list[str] = []
    if payload["status"] != V4_GOAL4692_TIER3_SUPPORT_DECISION_STATUS:
        missing.append("status")
    ratio = float(payload["measured_direct_callable_ratio"])
    if not (1.50 < ratio < 2.00):
        missing.append("yellow_ratio")
    if "do_not_promote_sbt_direct_callable_support" not in str(payload["decision"]):
        missing.append("direct_callable_not_promoted")
    if payload["selected_next_track"] != "module_specialized_direct_device_callback_in_hit_program":
        missing.append("next_track")
    for key in (
        "direct_callable_public_support_authorized",
        "specialized_device_callback_public_support_authorized",
        "tier3_public_support_authorized",
        "release_authorized",
        "performance_claim_authorized",
    ):
        if payload[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "decision": payload,
    }


__all__ = [
    "V4_GOAL4692_TIER3_SUPPORT_DECISION_STATUS",
    "V4_GOAL4692_NEXT_GOAL",
    "V4Goal4692Tier3SupportDecision",
    "v4_goal4692_tier3_support_decision",
    "validate_v4_goal4692_tier3_support_decision",
]
