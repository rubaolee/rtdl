from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4714_SMOKE_STATUS = "goal4714_custom_predicate_early_exit_smoke_pending_pod"
V4_GOAL4714_NEXT_GOAL_IF_PASS = "Goal4715 custom predicate early-exit focused POD timing gate"
V4_GOAL4714_NEXT_GOAL_IF_FAIL = "Repair custom predicate early-exit runner before timing"


@dataclass(frozen=True)
class V4Goal4714SmokeSummary:
    classification: str
    total_rows: int
    correctness_all_passed: bool
    early_termination_primary_passed: bool
    primary_rows: int
    control_rows: int
    next_goal: str
    pod_timing_authorized: bool = False
    release_authorized: bool = False
    formal_high_performance_authorized: bool = False
    app_level_speed_claim_authorized: bool = False
    public_tier3_support_authorized: bool = False
    arbitrary_callback_authorized: bool = False
    raw_optix_callback_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "total_rows": self.total_rows,
            "correctness_all_passed": self.correctness_all_passed,
            "early_termination_primary_passed": self.early_termination_primary_passed,
            "primary_rows": self.primary_rows,
            "control_rows": self.control_rows,
            "next_goal": self.next_goal,
            "pod_timing_authorized": self.pod_timing_authorized,
            "release_authorized": self.release_authorized,
            "formal_high_performance_authorized": self.formal_high_performance_authorized,
            "app_level_speed_claim_authorized": self.app_level_speed_claim_authorized,
            "public_tier3_support_authorized": self.public_tier3_support_authorized,
            "arbitrary_callback_authorized": self.arbitrary_callback_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
        }


def classify_v4_goal4714_custom_predicate_early_exit_smoke(rows: list[dict[str, object]]) -> dict[str, object]:
    total = len(rows)
    primary = [row for row in rows if row.get("row_role") == "primary"]
    control = [row for row in rows if row.get("row_role") == "control"]
    correctness = bool(rows) and all(bool(row.get("correctness_passed")) for row in rows)
    early_ok = bool(primary) and all(
        bool(row.get("early_termination_observed"))
        and int(row.get("v4_anyhit_invocations", 0)) < int(row.get("fallback_all_hit_invocations", 0))
        for row in primary
    )
    passed = bool(total >= 4 and correctness and early_ok)
    summary = V4Goal4714SmokeSummary(
        classification=(
            "pass_smoke_gate_not_timing_not_release"
            if passed
            else "fail_smoke_gate_repair_before_timing"
        ),
        total_rows=total,
        correctness_all_passed=correctness,
        early_termination_primary_passed=early_ok,
        primary_rows=len(primary),
        control_rows=len(control),
        next_goal=V4_GOAL4714_NEXT_GOAL_IF_PASS if passed else V4_GOAL4714_NEXT_GOAL_IF_FAIL,
    )
    return summary.as_dict()


def validate_v4_goal4714_custom_predicate_early_exit_smoke_result_contract() -> dict[str, object]:
    passing = classify_v4_goal4714_custom_predicate_early_exit_smoke(
        [
            {
                "row_role": "primary",
                "correctness_passed": True,
                "early_termination_observed": True,
                "v4_anyhit_invocations": 100,
                "fallback_all_hit_invocations": 800,
            },
            {
                "row_role": "primary",
                "correctness_passed": True,
                "early_termination_observed": True,
                "v4_anyhit_invocations": 120,
                "fallback_all_hit_invocations": 3200,
            },
            {"row_role": "control", "correctness_passed": True},
            {"row_role": "control", "correctness_passed": True},
        ]
    )
    failing = classify_v4_goal4714_custom_predicate_early_exit_smoke(
        [
            {
                "row_role": "primary",
                "correctness_passed": True,
                "early_termination_observed": False,
                "v4_anyhit_invocations": 800,
                "fallback_all_hit_invocations": 800,
            },
            {"row_role": "control", "correctness_passed": True},
            {"row_role": "control", "correctness_passed": True},
            {"row_role": "control", "correctness_passed": True},
        ]
    )
    missing: list[str] = []
    if passing["classification"] != "pass_smoke_gate_not_timing_not_release":
        missing.append("passing_classification")
    if failing["classification"] != "fail_smoke_gate_repair_before_timing":
        missing.append("failing_classification")
    for name, payload in (("passing", passing), ("failing", failing)):
        for key in (
            "pod_timing_authorized",
            "release_authorized",
            "formal_high_performance_authorized",
            "app_level_speed_claim_authorized",
            "public_tier3_support_authorized",
            "arbitrary_callback_authorized",
            "raw_optix_callback_authorized",
        ):
            if payload[key] is not False:
                missing.append(f"{name}_{key}")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "goal_status": V4_GOAL4714_SMOKE_STATUS,
        "passing_example": passing,
        "failing_example": failing,
    }


__all__ = [
    "V4_GOAL4714_SMOKE_STATUS",
    "V4_GOAL4714_NEXT_GOAL_IF_PASS",
    "V4_GOAL4714_NEXT_GOAL_IF_FAIL",
    "V4Goal4714SmokeSummary",
    "classify_v4_goal4714_custom_predicate_early_exit_smoke",
    "validate_v4_goal4714_custom_predicate_early_exit_smoke_result_contract",
]
