from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4703_SPECIALIZED_TIER3_RELIABILITY_RESULT_STATUS = (
    "goal4703_specialized_tier3_reliability_matrix_result_not_public_support"
)
V4_GOAL4703_NEXT_GOAL_IF_PASS = "Goal4704 specialized Tier-3 support wording and docs gate"
V4_GOAL4703_NEXT_GOAL_IF_FAIL = "Stop Tier-3 support promotion; repair failing compile/link/launch stage first"


@dataclass(frozen=True)
class V4Goal4703ReliabilitySummary:
    classification: str
    total_attempts: int
    successful_attempts: int
    success_rate: float
    correctness_passed: bool
    cache_checks_passed: bool
    stage_failures: tuple[dict[str, object], ...]
    next_goal: str
    tier3_public_support_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False
    arbitrary_callback_authorized: bool = False
    raw_optix_callback_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "total_attempts": self.total_attempts,
            "successful_attempts": self.successful_attempts,
            "success_rate": self.success_rate,
            "correctness_passed": self.correctness_passed,
            "cache_checks_passed": self.cache_checks_passed,
            "stage_failures": self.stage_failures,
            "next_goal": self.next_goal,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
            "arbitrary_callback_authorized": self.arbitrary_callback_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
        }


def classify_v4_goal4703_specialized_tier3_reliability_result(
    attempts: list[dict[str, object]],
    *,
    success_floor: float = 0.95,
    cache_checks_passed: bool = False,
) -> dict[str, object]:
    total = len(attempts)
    successful = sum(1 for row in attempts if bool(row.get("compile_link_launch_success")))
    success_rate = (successful / total) if total else 0.0
    correctness_passed = bool(attempts) and all(bool(row.get("correctness_passed")) for row in attempts)
    failures = tuple(
        dict(row.get("failure_classification") or {})
        for row in attempts
        if not bool(row.get("compile_link_launch_success"))
    )
    passed = (
        total >= 20
        and success_rate >= success_floor
        and correctness_passed
        and cache_checks_passed
        and all(bool(row.get("failure_classification")) for row in attempts if not bool(row.get("compile_link_launch_success")))
    )
    summary = V4Goal4703ReliabilitySummary(
        classification=(
            "pass_reliability_gate_not_public_support"
            if passed
            else "fail_reliability_gate_repair_before_public_support"
        ),
        total_attempts=total,
        successful_attempts=successful,
        success_rate=success_rate,
        correctness_passed=correctness_passed,
        cache_checks_passed=cache_checks_passed,
        stage_failures=failures,
        next_goal=V4_GOAL4703_NEXT_GOAL_IF_PASS if passed else V4_GOAL4703_NEXT_GOAL_IF_FAIL,
    )
    return summary.as_dict()


def validate_v4_goal4703_specialized_tier3_reliability_result_contract() -> dict[str, object]:
    attempts = [
        {
            "compile_link_launch_success": True,
            "correctness_passed": True,
            "variant": f"variant_{idx % 4}",
            "attempt_index": idx,
        }
        for idx in range(20)
    ]
    passed = classify_v4_goal4703_specialized_tier3_reliability_result(
        attempts,
        success_floor=0.95,
        cache_checks_passed=True,
    )
    failed = classify_v4_goal4703_specialized_tier3_reliability_result(
        attempts[:18]
        + [
            {
                "compile_link_launch_success": False,
                "correctness_passed": False,
                "failure_classification": {"stage": "launch_validation", "error_code": "RTDL_V4_TIER3_COMPILE_STAGE_FAILED_LAUNCH_VALIDATION"},
            },
            {
                "compile_link_launch_success": False,
                "correctness_passed": False,
                "failure_classification": {"stage": "pipeline_create", "error_code": "RTDL_V4_TIER3_COMPILE_STAGE_FAILED_PIPELINE_CREATE"},
            },
        ],
        success_floor=0.95,
        cache_checks_passed=True,
    )
    missing: list[str] = []
    if passed["classification"] != "pass_reliability_gate_not_public_support":
        missing.append("pass_classification")
    if failed["classification"] != "fail_reliability_gate_repair_before_public_support":
        missing.append("fail_classification")
    for key in (
        "tier3_public_support_authorized",
        "release_authorized",
        "performance_claim_authorized",
        "arbitrary_callback_authorized",
        "raw_optix_callback_authorized",
    ):
        if passed[key] is not False or failed[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "goal_status": V4_GOAL4703_SPECIALIZED_TIER3_RELIABILITY_RESULT_STATUS,
        "passing_example": passed,
        "failing_example": failed,
    }


__all__ = [
    "V4_GOAL4703_SPECIALIZED_TIER3_RELIABILITY_RESULT_STATUS",
    "V4_GOAL4703_NEXT_GOAL_IF_PASS",
    "V4_GOAL4703_NEXT_GOAL_IF_FAIL",
    "V4Goal4703ReliabilitySummary",
    "classify_v4_goal4703_specialized_tier3_reliability_result",
    "validate_v4_goal4703_specialized_tier3_reliability_result_contract",
]
