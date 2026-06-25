from __future__ import annotations

from dataclasses import dataclass
from typing import Any


V4_GOAL4633_STATUS = "goal4633_weighted_sum_promoted_measured_with_recorded_review_debt"
V4_GOAL4633_SURFACE = "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays"
V4_GOAL4633_OPERATOR = "ray_triangle_any_hit_weighted_sum"
V4_GOAL4633_DECISION = "promote_weighted_sum_measured_torch_v4_tier2"
V4_GOAL4633_COMPARISON_CLASS = "same_operator_comparable_route"


@dataclass(frozen=True)
class V4WeightedSumPromotionRatio:
    ray_count: int
    triangle_count: int
    parity_passed: bool
    device_output_median_seconds: float
    host_scalar_median_seconds: float
    comparable_route_ratio: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "ray_count": self.ray_count,
            "triangle_count": self.triangle_count,
            "parity_passed": self.parity_passed,
            "device_output_median_seconds": self.device_output_median_seconds,
            "host_scalar_median_seconds": self.host_scalar_median_seconds,
            "comparable_route_ratio": self.comparable_route_ratio,
        }


V4_GOAL4633_WEIGHTED_SUM_RATIOS = (
    V4WeightedSumPromotionRatio(
        ray_count=32768,
        triangle_count=32768,
        parity_passed=True,
        device_output_median_seconds=0.00007508881390094757,
        host_scalar_median_seconds=0.00016112998127937317,
        comparable_route_ratio=2.1458586560166695,
    ),
    V4WeightedSumPromotionRatio(
        ray_count=131072,
        triangle_count=131072,
        parity_passed=True,
        device_output_median_seconds=0.00014383159577846527,
        host_scalar_median_seconds=0.0002348572015762329,
        comparable_route_ratio=1.632862378430179,
    ),
    V4WeightedSumPromotionRatio(
        ray_count=262144,
        triangle_count=262144,
        parity_passed=True,
        device_output_median_seconds=0.00024349428713321686,
        host_scalar_median_seconds=0.00033028237521648407,
        comparable_route_ratio=1.3564276152227959,
    ),
    V4WeightedSumPromotionRatio(
        ray_count=524288,
        triangle_count=524288,
        parity_passed=True,
        device_output_median_seconds=0.0004368126392364502,
        host_scalar_median_seconds=0.000524669885635376,
        comparable_route_ratio=1.2011325646448796,
    ),
)


V4_GOAL4633_EVIDENCE_FILES = (
    "future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.json",
    "future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.md",
    "future/v4/v4_goal4633_weighted_sum_promotion_decision_2026-06-25.md",
    "future/v4/reviews/claude_v4_goal4633_weighted_sum_promotion_gate_protocol_review_2026-06-24.md",
    "future/v4/reviews/claude_v4_goal4633_weighted_sum_promotion_completion_review_2026-06-25.md",
    "future/v4/reviews/antigravity_v4_goal4633_weighted_sum_promotion_completion_review_blocked_2026-06-25.md",
)


def v4_goal4633_weighted_sum_promotion_decision() -> dict[str, Any]:
    ratios = tuple(row.as_dict() for row in V4_GOAL4633_WEIGHTED_SUM_RATIOS)
    min_ratio = min(row.comparable_route_ratio for row in V4_GOAL4633_WEIGHTED_SUM_RATIOS)
    geomean_ratio = 1.5457333064727565
    return {
        "status": V4_GOAL4633_STATUS,
        "decision": V4_GOAL4633_DECISION,
        "surface": V4_GOAL4633_SURFACE,
        "operator": V4_GOAL4633_OPERATOR,
        "comparison_class": V4_GOAL4633_COMPARISON_CLASS,
        "comparison_boundary": (
            "host_materialization_path_vs_device_resident_output_path_not_pure_kernel_speedup"
        ),
        "surface_status_before_goal4633": "tier2_candidate_goal4620_not_measured",
        "surface_status_after_goal4633": "tier2_measured_pod_validated_not_release",
        "promotion_thresholds_passed": True,
        "measured_catalog_promotion_authorized": True,
        "weighted_sum_can_count_as_measured_release_surface": True,
        "completion_review_status": "claude_approved_antigravity_blocked_debt_recorded_codex_applied",
        "completion_review_debt_recorded": True,
        "ratios": ratios,
        "min_comparable_route_ratio": min_ratio,
        "geomean_comparable_route_ratio": geomean_ratio,
        "min_per_shape_ratio_required": 1.20,
        "min_geomean_ratio_required": 1.50,
        "ray_counts": (32768, 131072, 262144, 524288),
        "triangle_counts": (32768, 131072, 262144, 524288),
        "repeat_count": 30,
        "warmup_count": 5,
        "hardware": "NVIDIA RTX A5000",
        "driver": "570.195.03",
        "torch": "2.8.0+cu128",
        "partner_scope": ("torch_cuda",),
        "cupy_performance_claim_authorized": False,
        "parity_all_passed": all(row.parity_passed for row in V4_GOAL4633_WEIGHTED_SUM_RATIOS),
        "device_output_used": True,
        "host_materialization_in_hot_path": False,
        "host_scalar_read_before_consumer": False,
        "weighted_sum_downloaded_to_host_in_hot_path": False,
        "true_zero_copy_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_speedup_claim_authorized": False,
        "release_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "c_abi_or_embedding_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
        "evidence_files": V4_GOAL4633_EVIDENCE_FILES,
        "promotion_caveats": (
            "minimum_shape_ratio_is_barely_above_gate_at_524288_rows",
            "ratio_measures_host_materialization_path_vs_device_resident_path_not_kernel_speedup",
            "antigravity_cli_empty_output_recorded_as_review_debt",
            "does_not_authorize_whole_app_or_broad_speedup_claims",
        ),
    }


def validate_v4_goal4633_weighted_sum_promotion_decision() -> dict[str, Any]:
    decision = v4_goal4633_weighted_sum_promotion_decision()
    if decision["comparison_class"] != V4_GOAL4633_COMPARISON_CLASS:
        raise ValueError("Goal4633 must use the same-operator comparable-route boundary")
    if not decision["promotion_thresholds_passed"]:
        raise ValueError("Goal4633 evidence intake expects the promotion gate to pass thresholds")
    if not decision["parity_all_passed"]:
        raise ValueError("Goal4633 parity must pass at every shape")
    if decision["min_comparable_route_ratio"] < decision["min_per_shape_ratio_required"]:
        raise ValueError("Goal4633 minimum comparable-route ratio is below the frozen threshold")
    if decision["geomean_comparable_route_ratio"] < decision["min_geomean_ratio_required"]:
        raise ValueError("Goal4633 geomean comparable-route ratio is below the frozen threshold")
    if not decision["measured_catalog_promotion_authorized"]:
        raise ValueError("Goal4633 should authorize measured catalog promotion after review/debt closure")
    if not decision["weighted_sum_can_count_as_measured_release_surface"]:
        raise ValueError("Goal4633 should count weighted-sum as measured after promotion")
    if not decision["completion_review_debt_recorded"]:
        raise ValueError("Goal4633 must record the Antigravity review debt")
    for flag in (
        "release_claim_authorized",
        "broad_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "tier3_callback_claim_authorized",
        "cupy_performance_claim_authorized",
        "c_abi_or_embedding_claim_authorized",
        "app_specific_native_kernel_authorized",
    ):
        if decision[flag]:
            raise ValueError(f"Goal4633 must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4633_STATUS",
    "V4_GOAL4633_SURFACE",
    "V4_GOAL4633_OPERATOR",
    "V4_GOAL4633_DECISION",
    "V4_GOAL4633_COMPARISON_CLASS",
    "V4_GOAL4633_WEIGHTED_SUM_RATIOS",
    "V4_GOAL4633_EVIDENCE_FILES",
    "V4WeightedSumPromotionRatio",
    "v4_goal4633_weighted_sum_promotion_decision",
    "validate_v4_goal4633_weighted_sum_promotion_decision",
]
