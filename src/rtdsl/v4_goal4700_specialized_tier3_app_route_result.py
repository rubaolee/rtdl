from __future__ import annotations

from .v4_goal4699_specialized_tier3_app_route_protocol import (
    v4_goal4699_specialized_tier3_app_route_protocol,
)


V4_GOAL4700_SPECIALIZED_TIER3_APP_ROUTE_RESULT_STATUS = (
    "goal4700_specialized_tier3_app_route_result_pending_pod"
)
V4_GOAL4700_NEXT_GOAL_IF_PASS = "Goal4701 specialized Tier-3 support-candidate review packet"
V4_GOAL4700_NEXT_GOAL_IF_FAIL = "Goal4701 specialized Tier-3 no-go/reframe decision"


def classify_v4_goal4700_specialized_tier3_app_route_result(rows: list[dict[str, object]]) -> dict[str, object]:
    protocol = v4_goal4699_specialized_tier3_app_route_protocol()
    parity_all = bool(rows) and all(bool(row.get("parity_passed")) for row in rows)
    callback_over_tier2 = [float(row["callback_over_tier2_ratio"]) for row in rows]
    legacy_over_callback = [float(row["legacy_host_over_callback_ratio"]) for row in rows]
    max_callback_over_tier2 = max(callback_over_tier2) if callback_over_tier2 else None
    min_legacy_over_callback = min(legacy_over_callback) if legacy_over_callback else None
    hard_kill = (
        not parity_all
        or max_callback_over_tier2 is None
        or max_callback_over_tier2 > protocol.callback_over_tier2_hard_kill_ratio
    )
    pass_gate = bool(
        parity_all
        and max_callback_over_tier2 is not None
        and min_legacy_over_callback is not None
        and max_callback_over_tier2 <= protocol.callback_over_tier2_pass_ratio_max
        and min_legacy_over_callback >= protocol.callback_over_context_speedup_min
    )
    if pass_gate:
        classification = "pass_app_route_gate_not_public_support"
        next_goal = V4_GOAL4700_NEXT_GOAL_IF_PASS
    elif hard_kill:
        classification = "no_go_app_route_gate_failed_or_killed"
        next_goal = V4_GOAL4700_NEXT_GOAL_IF_FAIL
    else:
        classification = "yellow_app_route_between_pass_and_kill"
        next_goal = V4_GOAL4700_NEXT_GOAL_IF_FAIL
    return {
        "classification": classification,
        "parity_all_passed": parity_all,
        "max_callback_over_tier2_ratio": max_callback_over_tier2,
        "min_legacy_host_over_callback_ratio": min_legacy_over_callback,
        "next_goal": next_goal,
        "tier3_public_support_authorized": False,
        "app_level_speed_claim_authorized": False,
        "release_authorized": False,
        "performance_claim_authorized": False,
    }


def validate_v4_goal4700_specialized_tier3_app_route_result_contract() -> dict[str, object]:
    passing = classify_v4_goal4700_specialized_tier3_app_route_result(
        [
            {"parity_passed": True, "callback_over_tier2_ratio": 1.05, "legacy_host_over_callback_ratio": 1.4},
            {"parity_passed": True, "callback_over_tier2_ratio": 1.08, "legacy_host_over_callback_ratio": 1.3},
        ]
    )
    killed = classify_v4_goal4700_specialized_tier3_app_route_result(
        [{"parity_passed": True, "callback_over_tier2_ratio": 1.51, "legacy_host_over_callback_ratio": 2.0}]
    )
    parity_fail = classify_v4_goal4700_specialized_tier3_app_route_result(
        [{"parity_passed": False, "callback_over_tier2_ratio": 1.01, "legacy_host_over_callback_ratio": 2.0}]
    )
    missing: list[str] = []
    if passing["classification"] != "pass_app_route_gate_not_public_support":
        missing.append("passing_classification")
    if killed["classification"] != "no_go_app_route_gate_failed_or_killed":
        missing.append("killed_classification")
    if parity_fail["classification"] != "no_go_app_route_gate_failed_or_killed":
        missing.append("parity_fail_classification")
    for name, payload in (("passing", passing), ("killed", killed), ("parity_fail", parity_fail)):
        for key in (
            "tier3_public_support_authorized",
            "app_level_speed_claim_authorized",
            "release_authorized",
            "performance_claim_authorized",
        ):
            if payload[key] is not False:
                missing.append(f"{name}_{key}")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "goal_status": V4_GOAL4700_SPECIALIZED_TIER3_APP_ROUTE_RESULT_STATUS,
        "passing_example": passing,
        "killed_example": killed,
        "parity_fail_example": parity_fail,
    }


__all__ = [
    "V4_GOAL4700_SPECIALIZED_TIER3_APP_ROUTE_RESULT_STATUS",
    "V4_GOAL4700_NEXT_GOAL_IF_PASS",
    "V4_GOAL4700_NEXT_GOAL_IF_FAIL",
    "classify_v4_goal4700_specialized_tier3_app_route_result",
    "validate_v4_goal4700_specialized_tier3_app_route_result_contract",
]
