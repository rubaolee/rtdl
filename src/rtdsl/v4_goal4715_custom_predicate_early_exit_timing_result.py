from __future__ import annotations

import math
from dataclasses import dataclass


V4_GOAL4715_TIMING_STATUS = "goal4715_custom_predicate_early_exit_focused_timing_pending_pod"
V4_GOAL4715_NEXT_GOAL_IF_PASS = (
    "Productize custom predicate early-exit as a measured V4 route and broaden app-level validation"
)
V4_GOAL4715_NEXT_GOAL_IF_FAIL = (
    "Stop custom predicate early-exit as formal high-performance evidence; diagnose or reselect the runtime lever"
)


@dataclass(frozen=True)
class V4Goal4715TimingSummary:
    classification: str
    correctness_all_passed: bool
    denominator_discovery_complete: bool
    early_termination_primary_passed: bool
    primary_speed_row_count: int
    primary_geomean_v2_speedup: float | None
    primary_geomean_v3_speedup: float | None
    min_primary_v3_speedup: float | None
    control_geomean_v3_speedup: float | None
    next_goal: str
    release_authorized: bool = False
    app_level_speed_claim_authorized: bool = False
    formal_high_performance_authorized: bool = False
    public_tier3_support_authorized: bool = False
    arbitrary_callback_authorized: bool = False
    raw_optix_callback_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "correctness_all_passed": self.correctness_all_passed,
            "denominator_discovery_complete": self.denominator_discovery_complete,
            "early_termination_primary_passed": self.early_termination_primary_passed,
            "primary_speed_row_count": self.primary_speed_row_count,
            "primary_geomean_v2_speedup": self.primary_geomean_v2_speedup,
            "primary_geomean_v3_speedup": self.primary_geomean_v3_speedup,
            "min_primary_v3_speedup": self.min_primary_v3_speedup,
            "control_geomean_v3_speedup": self.control_geomean_v3_speedup,
            "next_goal": self.next_goal,
            "release_authorized": self.release_authorized,
            "app_level_speed_claim_authorized": self.app_level_speed_claim_authorized,
            "formal_high_performance_authorized": self.formal_high_performance_authorized,
            "public_tier3_support_authorized": self.public_tier3_support_authorized,
            "arbitrary_callback_authorized": self.arbitrary_callback_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
        }


def _geomean(values: list[float]) -> float | None:
    if not values or any(value <= 0.0 for value in values):
        return None
    return float(math.exp(sum(math.log(value) for value in values) / len(values)))


def classify_v4_goal4715_custom_predicate_early_exit_timing(
    rows: list[dict[str, object]],
    denominator_discovery: dict[str, object],
    *,
    primary_geomean_bar: float = 1.50,
    per_primary_row_bar: float = 1.20,
    control_geomean_floor: float = 0.95,
) -> dict[str, object]:
    correctness_all = bool(rows) and all(
        bool(row.get("v4_correctness_passed")) and bool(row.get("materialized_fallback_correctness_passed"))
        for row in rows
    )
    denominator_complete = bool(denominator_discovery.get("completed_before_v4_timing")) and bool(
        denominator_discovery.get("v2_14", {}).get("selected_baseline")
    ) and bool(denominator_discovery.get("v3_0_2", {}).get("selected_baseline"))
    primary_rows = [row for row in rows if row.get("row_role") == "primary"]
    control_rows = [row for row in rows if row.get("row_role") == "control"]
    early_ok = bool(primary_rows) and all(
        bool(row.get("early_termination_observed"))
        and int(row.get("v4_anyhit_invocations", 0)) < int(row.get("fallback_all_hit_invocations", 0))
        for row in primary_rows
    )
    primary_v2 = [float(row["v2_baseline_over_v4_ratio"]) for row in primary_rows if row.get("v2_baseline_over_v4_ratio")]
    primary_v3 = [float(row["v3_baseline_over_v4_ratio"]) for row in primary_rows if row.get("v3_baseline_over_v4_ratio")]
    control_v3 = [float(row["v3_baseline_over_v4_ratio"]) for row in control_rows if row.get("v3_baseline_over_v4_ratio")]
    primary_geomean_v2 = _geomean(primary_v2)
    primary_geomean_v3 = _geomean(primary_v3)
    control_geomean_v3 = _geomean(control_v3)
    min_primary_v3 = min(primary_v3) if primary_v3 else None

    primary_pass = bool(
        primary_geomean_v2 is not None
        and primary_geomean_v3 is not None
        and primary_geomean_v2 >= primary_geomean_bar
        and primary_geomean_v3 >= primary_geomean_bar
        and min_primary_v3 is not None
        and min_primary_v3 >= per_primary_row_bar
    )
    control_pass = bool(control_geomean_v3 is None or control_geomean_v3 >= control_geomean_floor)
    pass_gate = bool(
        correctness_all
        and denominator_complete
        and early_ok
        and len(primary_rows) >= 6
        and primary_pass
        and control_pass
    )
    if pass_gate:
        classification = "pass_focused_timing_gate_not_release"
        next_goal = V4_GOAL4715_NEXT_GOAL_IF_PASS
    elif not correctness_all or not denominator_complete or not early_ok:
        classification = "invalid_or_fail_timing_gate_repair_required"
        next_goal = V4_GOAL4715_NEXT_GOAL_IF_FAIL
    else:
        classification = "fail_focused_timing_gate_not_high_performance"
        next_goal = V4_GOAL4715_NEXT_GOAL_IF_FAIL

    return V4Goal4715TimingSummary(
        classification=classification,
        correctness_all_passed=correctness_all,
        denominator_discovery_complete=denominator_complete,
        early_termination_primary_passed=early_ok,
        primary_speed_row_count=len(primary_rows),
        primary_geomean_v2_speedup=primary_geomean_v2,
        primary_geomean_v3_speedup=primary_geomean_v3,
        min_primary_v3_speedup=min_primary_v3,
        control_geomean_v3_speedup=control_geomean_v3,
        next_goal=next_goal,
    ).as_dict()


def validate_v4_goal4715_custom_predicate_early_exit_timing_result_contract() -> dict[str, object]:
    discovery = {
        "completed_before_v4_timing": True,
        "v2_14": {"selected_baseline": "materialized_all_hit_ids_plus_device_predicate_reduce_fallback"},
        "v3_0_2": {"selected_baseline": "materialized_all_hit_ids_plus_device_predicate_reduce_fallback"},
    }
    passing_rows = []
    for regime, k in (("dense_early_accept_k8", 8), ("dense_early_accept_k32", 32), ("sparse_early_accept_k32", 32)):
        for scale in (65536, 131072):
            passing_rows.append(
                {
                    "row_role": "primary",
                    "regime": regime,
                    "scale": scale,
                    "v4_correctness_passed": True,
                    "materialized_fallback_correctness_passed": True,
                    "early_termination_observed": True,
                    "v4_anyhit_invocations": scale,
                    "fallback_all_hit_invocations": scale * k,
                    "v2_baseline_over_v4_ratio": 1.8,
                    "v3_baseline_over_v4_ratio": 1.8,
                }
            )
    passing_rows.append(
        {
            "row_role": "control",
            "regime": "dense_reject_all_k32",
            "scale": 65536,
            "v4_correctness_passed": True,
            "materialized_fallback_correctness_passed": True,
            "v2_baseline_over_v4_ratio": 1.0,
            "v3_baseline_over_v4_ratio": 1.0,
        }
    )
    passing = classify_v4_goal4715_custom_predicate_early_exit_timing(passing_rows, discovery)
    failing = classify_v4_goal4715_custom_predicate_early_exit_timing(
        [{**row, "v2_baseline_over_v4_ratio": 1.05, "v3_baseline_over_v4_ratio": 1.05} for row in passing_rows],
        discovery,
    )
    invalid = classify_v4_goal4715_custom_predicate_early_exit_timing(
        [{**row, "early_termination_observed": False, "v4_anyhit_invocations": row.get("fallback_all_hit_invocations", 0)} for row in passing_rows],
        discovery,
    )
    missing: list[str] = []
    if passing["classification"] != "pass_focused_timing_gate_not_release":
        missing.append("passing_classification")
    if failing["classification"] != "fail_focused_timing_gate_not_high_performance":
        missing.append("failing_classification")
    if invalid["classification"] != "invalid_or_fail_timing_gate_repair_required":
        missing.append("invalid_classification")
    for name, payload in (("passing", passing), ("failing", failing), ("invalid", invalid)):
        for key in (
            "release_authorized",
            "app_level_speed_claim_authorized",
            "formal_high_performance_authorized",
            "public_tier3_support_authorized",
            "arbitrary_callback_authorized",
            "raw_optix_callback_authorized",
        ):
            if payload[key] is not False:
                missing.append(f"{name}_{key}")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "goal_status": V4_GOAL4715_TIMING_STATUS,
        "passing_example": passing,
        "failing_example": failing,
        "invalid_example": invalid,
    }


__all__ = [
    "V4_GOAL4715_TIMING_STATUS",
    "V4_GOAL4715_NEXT_GOAL_IF_PASS",
    "V4_GOAL4715_NEXT_GOAL_IF_FAIL",
    "V4Goal4715TimingSummary",
    "classify_v4_goal4715_custom_predicate_early_exit_timing",
    "validate_v4_goal4715_custom_predicate_early_exit_timing_result_contract",
]
