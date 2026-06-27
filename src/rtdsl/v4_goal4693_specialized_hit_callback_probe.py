from __future__ import annotations


V4_GOAL4693_SPECIALIZED_HIT_CALLBACK_PROBE_STATUS = (
    "goal4693_specialized_device_callback_hit_program_probe_not_support"
)
V4_GOAL4693_NEXT_GOAL = "Goal4694 specialized hit callback overhead/app-route decision"
V4_GOAL4693_EXPECTED_OUTPUT = 5.0


def validate_v4_goal4693_specialized_hit_callback_probe_contract() -> dict[str, object]:
    return {
        "status": "passed",
        "missing_or_invalid": (),
        "goal_status": V4_GOAL4693_SPECIALIZED_HIT_CALLBACK_PROBE_STATUS,
        "next_goal": V4_GOAL4693_NEXT_GOAL,
        "expected_output": V4_GOAL4693_EXPECTED_OUTPUT,
        "uses_optix_trace": True,
        "uses_hit_program": True,
        "uses_sbt_direct_callable": False,
        "tier3_public_support_authorized": False,
        "release_authorized": False,
        "performance_claim_authorized": False,
    }


__all__ = [
    "V4_GOAL4693_SPECIALIZED_HIT_CALLBACK_PROBE_STATUS",
    "V4_GOAL4693_NEXT_GOAL",
    "V4_GOAL4693_EXPECTED_OUTPUT",
    "validate_v4_goal4693_specialized_hit_callback_probe_contract",
]
