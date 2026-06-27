from __future__ import annotations

import math
from dataclasses import dataclass


V4_GOAL4711_CUSTOM_SCORED_APP_RESULT_STATUS = (
    "goal4711_ray_triangle_custom_scored_app_focused_result_pending_pod"
)
V4_GOAL4711_NEXT_GOAL_IF_PASS = (
    "Goal4712 external denominator review for custom-scored app and release-hardening decision"
)
V4_GOAL4711_NEXT_GOAL_IF_FAIL = (
    "Stop custom-scored app as formal high-performance V4 proof; reselect or redesign the runtime lever"
)


@dataclass(frozen=True)
class V4Goal4711FocusedSummary:
    classification: str
    correctness_all_passed: bool
    denominator_discovery_complete: bool
    denominator_quality: str
    primary_speed_row_count: int
    primary_geomean_v2_speedup: float | None
    primary_geomean_v3_speedup: float | None
    min_primary_v3_speedup: float | None
    primary_callbacks_min_v3_speedup: tuple[dict[str, object], ...]
    weighted_sum_used_as_claim_evidence: bool
    next_goal: str
    release_authorized: bool = False
    app_level_speed_claim_authorized: bool = False
    formal_high_performance_authorized: bool = False
    tier3_public_support_authorized: bool = False
    arbitrary_callback_authorized: bool = False
    raw_optix_callback_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "correctness_all_passed": self.correctness_all_passed,
            "denominator_discovery_complete": self.denominator_discovery_complete,
            "denominator_quality": self.denominator_quality,
            "primary_speed_row_count": self.primary_speed_row_count,
            "primary_geomean_v2_speedup": self.primary_geomean_v2_speedup,
            "primary_geomean_v3_speedup": self.primary_geomean_v3_speedup,
            "min_primary_v3_speedup": self.min_primary_v3_speedup,
            "primary_callbacks_min_v3_speedup": self.primary_callbacks_min_v3_speedup,
            "weighted_sum_used_as_claim_evidence": self.weighted_sum_used_as_claim_evidence,
            "next_goal": self.next_goal,
            "release_authorized": self.release_authorized,
            "app_level_speed_claim_authorized": self.app_level_speed_claim_authorized,
            "formal_high_performance_authorized": self.formal_high_performance_authorized,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "arbitrary_callback_authorized": self.arbitrary_callback_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
        }


def _geomean(values: list[float]) -> float | None:
    if not values or any(value <= 0.0 for value in values):
        return None
    return float(math.exp(sum(math.log(value) for value in values) / len(values)))


def _is_primary_speed_row(row: dict[str, object]) -> bool:
    return (
        row.get("callback_role") == "primary"
        and row.get("regime") in {"dense_hits", "sparse_hits"}
        and row.get("v4_fused_median_s") is not None
        and row.get("v3_baseline_median_s") is not None
    )


def classify_v4_goal4711_custom_scored_app_result(
    rows: list[dict[str, object]],
    denominator_discovery: dict[str, object],
    *,
    v2_geomean_bar: float = 1.50,
    v3_geomean_bar: float = 1.20,
    per_callback_v3_bar: float = 1.10,
    hard_regression_floor: float = 0.95,
) -> dict[str, object]:
    correctness_all = bool(rows) and all(
        bool(row.get("v4_fused_correctness_passed"))
        and bool(row.get("materialized_fallback_correctness_passed"))
        for row in rows
    )
    denominator_complete = bool(denominator_discovery.get("completed_before_v4_timing")) and bool(
        denominator_discovery.get("v2_14", {}).get("selected_baseline")
    ) and bool(denominator_discovery.get("v3_0_2", {}).get("selected_baseline"))
    denominator_quality = str(denominator_discovery.get("quality", "unknown"))
    weighted_sum_used_as_claim = any(
        row.get("callback_role") == "control" and bool(row.get("counts_toward_primary_claim"))
        for row in rows
    )

    speed_rows = [row for row in rows if _is_primary_speed_row(row)]
    v2_ratios = [float(row["v2_baseline_over_v4_ratio"]) for row in speed_rows]
    v3_ratios = [float(row["v3_baseline_over_v4_ratio"]) for row in speed_rows]
    geomean_v2 = _geomean(v2_ratios)
    geomean_v3 = _geomean(v3_ratios)
    min_v3 = min(v3_ratios) if v3_ratios else None

    callback_names = sorted({str(row.get("protocol_callback")) for row in speed_rows})
    callback_min_rows = []
    for name in callback_names:
        callback_ratios = [
            float(row["v3_baseline_over_v4_ratio"])
            for row in speed_rows
            if str(row.get("protocol_callback")) == name
        ]
        callback_min_rows.append(
            {
                "protocol_callback": name,
                "min_v3_speedup": min(callback_ratios) if callback_ratios else None,
                "passes": bool(callback_ratios) and min(callback_ratios) >= per_callback_v3_bar,
            }
        )
    callbacks_pass = bool(callback_min_rows) and all(bool(row["passes"]) for row in callback_min_rows)
    hard_regression = min_v3 is None or min_v3 < hard_regression_floor

    numeric_pass = bool(
        correctness_all
        and denominator_complete
        and not weighted_sum_used_as_claim
        and len(speed_rows) >= 12
        and geomean_v2 is not None
        and geomean_v3 is not None
        and geomean_v2 >= v2_geomean_bar
        and geomean_v3 >= v3_geomean_bar
        and callbacks_pass
        and not hard_regression
    )
    exact_denominator = denominator_quality == "exact_repo_route"
    if numeric_pass and exact_denominator:
        classification = "pass_focused_app_gate_not_release"
        next_goal = V4_GOAL4711_NEXT_GOAL_IF_PASS
    elif numeric_pass:
        classification = "pass_numeric_gate_pending_external_denominator_review_not_release"
        next_goal = V4_GOAL4711_NEXT_GOAL_IF_PASS
    else:
        classification = "fail_focused_app_gate_not_high_performance"
        next_goal = V4_GOAL4711_NEXT_GOAL_IF_FAIL

    return V4Goal4711FocusedSummary(
        classification=classification,
        correctness_all_passed=correctness_all,
        denominator_discovery_complete=denominator_complete,
        denominator_quality=denominator_quality,
        primary_speed_row_count=len(speed_rows),
        primary_geomean_v2_speedup=geomean_v2,
        primary_geomean_v3_speedup=geomean_v3,
        min_primary_v3_speedup=min_v3,
        primary_callbacks_min_v3_speedup=tuple(callback_min_rows),
        weighted_sum_used_as_claim_evidence=weighted_sum_used_as_claim,
        next_goal=next_goal,
    ).as_dict()


def validate_v4_goal4711_custom_scored_app_result_contract() -> dict[str, object]:
    discovery = {
        "completed_before_v4_timing": True,
        "quality": "strong_materialized_device_fallback_after_no_custom_repo_route_found",
        "v2_14": {"selected_baseline": "materialized_device_fallback"},
        "v3_0_2": {"selected_baseline": "materialized_device_fallback"},
    }
    rows = []
    for callback in ("affine_score", "threshold_score", "minmax_score"):
        for regime in ("dense_hits", "sparse_hits"):
            for scale in (262144, 524288):
                rows.append(
                    {
                        "protocol_callback": callback,
                        "callback_role": "primary",
                        "regime": regime,
                        "scale": scale,
                        "v4_fused_median_s": 1.0,
                        "v2_baseline_median_s": 1.6,
                        "v3_baseline_median_s": 1.3,
                        "v2_baseline_over_v4_ratio": 1.6,
                        "v3_baseline_over_v4_ratio": 1.3,
                        "v4_fused_correctness_passed": True,
                        "materialized_fallback_correctness_passed": True,
                        "counts_toward_primary_claim": True,
                    }
                )
    passing = classify_v4_goal4711_custom_scored_app_result(rows, discovery)
    weighted_control_claim = classify_v4_goal4711_custom_scored_app_result(
        rows
        + [
            {
                "protocol_callback": "weighted_sum",
                "callback_role": "control",
                "regime": "dense_hits",
                "scale": 262144,
                "v4_fused_median_s": 1.0,
                "v2_baseline_median_s": 2.0,
                "v3_baseline_median_s": 2.0,
                "v2_baseline_over_v4_ratio": 2.0,
                "v3_baseline_over_v4_ratio": 2.0,
                "v4_fused_correctness_passed": True,
                "materialized_fallback_correctness_passed": True,
                "counts_toward_primary_claim": True,
            }
        ],
        discovery,
    )
    failing = classify_v4_goal4711_custom_scored_app_result(
        [{**row, "v3_baseline_over_v4_ratio": 1.01, "v3_baseline_median_s": 1.01} for row in rows],
        discovery,
    )
    missing: list[str] = []
    if passing["classification"] != "pass_numeric_gate_pending_external_denominator_review_not_release":
        missing.append("passing_classification")
    if weighted_control_claim["classification"] != "fail_focused_app_gate_not_high_performance":
        missing.append("weighted_control_claim_rejection")
    if failing["classification"] != "fail_focused_app_gate_not_high_performance":
        missing.append("failing_classification")
    for name, payload in (("passing", passing), ("control", weighted_control_claim), ("failing", failing)):
        for key in (
            "release_authorized",
            "app_level_speed_claim_authorized",
            "formal_high_performance_authorized",
            "tier3_public_support_authorized",
            "arbitrary_callback_authorized",
            "raw_optix_callback_authorized",
        ):
            if payload[key] is not False:
                missing.append(f"{name}_{key}")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "goal_status": V4_GOAL4711_CUSTOM_SCORED_APP_RESULT_STATUS,
        "passing_example": passing,
        "weighted_control_claim_example": weighted_control_claim,
        "failing_example": failing,
    }


__all__ = [
    "V4_GOAL4711_CUSTOM_SCORED_APP_RESULT_STATUS",
    "V4_GOAL4711_NEXT_GOAL_IF_PASS",
    "V4_GOAL4711_NEXT_GOAL_IF_FAIL",
    "V4Goal4711FocusedSummary",
    "classify_v4_goal4711_custom_scored_app_result",
    "validate_v4_goal4711_custom_scored_app_result_contract",
]
