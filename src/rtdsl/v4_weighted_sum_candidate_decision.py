from __future__ import annotations

from dataclasses import dataclass
from typing import Any


V4_GOAL4629_STATUS = "goal4629_weighted_sum_keep_candidate_not_promoted"
V4_GOAL4629_SURFACE = "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays"
V4_GOAL4629_OPERATOR = "ray_triangle_any_hit_weighted_sum"
V4_GOAL4629_SURFACE_STATUS = "tier2_candidate_goal4620_not_measured"
V4_GOAL4629_DECISION = "keep_candidate_not_promoted"


@dataclass(frozen=True)
class V4WeightedSumCandidateRatio:
    ray_count: int
    triangle_count: int
    parity_passed: bool
    device_output_median_seconds: float
    host_scalar_median_seconds: float
    same_contract_ratio: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "ray_count": self.ray_count,
            "triangle_count": self.triangle_count,
            "parity_passed": self.parity_passed,
            "device_output_median_seconds": self.device_output_median_seconds,
            "host_scalar_median_seconds": self.host_scalar_median_seconds,
            "same_contract_ratio": self.same_contract_ratio,
        }


V4_GOAL4629_WEIGHTED_SUM_RATIOS = (
    V4WeightedSumCandidateRatio(
        ray_count=32768,
        triangle_count=32768,
        parity_passed=True,
        device_output_median_seconds=0.000068050,
        host_scalar_median_seconds=0.000139300,
        same_contract_ratio=2.047,
    ),
    V4WeightedSumCandidateRatio(
        ray_count=131072,
        triangle_count=131072,
        parity_passed=True,
        device_output_median_seconds=0.000146613,
        host_scalar_median_seconds=0.000228226,
        same_contract_ratio=1.557,
    ),
)


V4_GOAL4629_EVIDENCE_FILES = (
    "future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.json",
    "future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.md",
    "future/v4/reviews/claude_v4_goal4620_weighted_sum_completion_review_2026-06-24.raw.md",
    "future/v4/reviews/goal4620_completion_consensus_and_review_debt_2026-06-24.md",
)


def v4_goal4629_weighted_sum_candidate_decision() -> dict[str, Any]:
    ratios = tuple(row.as_dict() for row in V4_GOAL4629_WEIGHTED_SUM_RATIOS)
    min_ratio = min(row.same_contract_ratio for row in V4_GOAL4629_WEIGHTED_SUM_RATIOS)
    max_ratio = max(row.same_contract_ratio for row in V4_GOAL4629_WEIGHTED_SUM_RATIOS)
    return {
        "status": V4_GOAL4629_STATUS,
        "decision": V4_GOAL4629_DECISION,
        "surface": V4_GOAL4629_SURFACE,
        "operator": V4_GOAL4629_OPERATOR,
        "surface_status_before_goal4629": V4_GOAL4629_SURFACE_STATUS,
        "surface_status_after_goal4629": V4_GOAL4629_SURFACE_STATUS,
        "candidate_gate_passed": True,
        "candidate_evidence_is_positive": True,
        "measured_catalog_promotion_authorized": False,
        "release_scorecard_slot_closed_as": "explicit_candidate_kept_not_promoted",
        "weighted_sum_can_count_as_measured_release_surface": False,
        "triangle_counting_release_coverage_after_goal4629": "candidate_not_measured_release_coverage",
        "evidence_files": V4_GOAL4629_EVIDENCE_FILES,
        "ratios": ratios,
        "min_same_contract_ratio": min_ratio,
        "max_same_contract_ratio": max_ratio,
        "ray_counts": (32768, 131072),
        "triangle_counts": (32768, 131072),
        "repeat_count": 5,
        "warmup_count": 2,
        "hardware": "NVIDIA RTX A5000",
        "optix_abi_scope": "8.0_only",
        "partner_scope": ("torch_cuda",),
        "parity_all_passed": all(row.parity_passed for row in V4_GOAL4629_WEIGHTED_SUM_RATIOS),
        "device_output_used": True,
        "host_scalar_read_before_consumer": False,
        "host_row_materialization_before_consumer": False,
        "query_rays_uploaded_each_run": False,
        "ray_weights_uploaded_each_run": False,
        "cuda_stream_ptr_nonzero": True,
        "promotion_blockers": (
            "goal4620_external_review_authorized_candidate_completion_but_not_measured_catalog_promotion",
            "evidence_matrix_has_two_ray_triangle_sizes_only",
            "repeat_count_is_candidate_gate_level_not_release_promotion_level",
            "large_size_ratio_is_positive_but_not_enough_to_override_missing_promotion_authorization",
            "cupy_and_non_torch_partner_performance_unmeasured",
            "triangle_counting_whole_app_or_primary_route_release_coverage_not_proven",
        ),
        "future_promotion_requirements": (
            "predeclare_promotion_gate_before_rerun",
            "expand_same_contract_shape_matrix_beyond_two_sizes",
            "increase_repeat_count_to_release_gate_level_beyond_5_candidate_repeats",
            "preserve_correctness_parity_at_every_shape",
            "preserve_device_output_no_hot_path_host_materialization_metadata",
            "measure_cupy_and_non_torch_partner_performance",
            "prove_triangle_counting_primary_route_release_coverage",
            "obtain_external_review_explicitly_authorizing_measured_catalog_promotion",
        ),
        "release_claim_authorized": False,
        "broad_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "measured_catalog_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "c_abi_or_embedding_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


def validate_v4_goal4629_weighted_sum_candidate_decision() -> dict[str, Any]:
    decision = v4_goal4629_weighted_sum_candidate_decision()
    if decision["decision"] != V4_GOAL4629_DECISION:
        raise ValueError("Goal4629 must keep weighted-sum candidate unless a new promotion review authorizes otherwise")
    if decision["surface"] != V4_GOAL4629_SURFACE:
        raise ValueError("Goal4629 must decide the ray/triangle weighted-sum surface")
    if decision["surface_status_after_goal4629"] != V4_GOAL4629_SURFACE_STATUS:
        raise ValueError("Goal4629 must not silently change weighted-sum measured status")
    if not decision["candidate_gate_passed"]:
        raise ValueError("Goal4629 must preserve the positive candidate gate result")
    if not decision["parity_all_passed"]:
        raise ValueError("Goal4629 weighted-sum parity must pass at every recorded size")
    if decision["measured_catalog_promotion_authorized"]:
        raise ValueError("Goal4629 must not authorize measured catalog promotion")
    if decision["weighted_sum_can_count_as_measured_release_surface"]:
        raise ValueError("Weighted-sum candidate must not count as a measured release surface")
    if decision["triangle_counting_release_coverage_after_goal4629"] != "candidate_not_measured_release_coverage":
        raise ValueError("Triangle counting must remain candidate-bound after Goal4629")
    for flag in (
        "release_claim_authorized",
        "broad_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "measured_catalog_claim_authorized",
        "true_zero_copy_claim_authorized",
        "tier3_callback_claim_authorized",
        "cupy_performance_claim_authorized",
        "c_abi_or_embedding_claim_authorized",
        "app_specific_native_kernel_authorized",
    ):
        if decision[flag]:
            raise ValueError(f"Goal4629 must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4629_STATUS",
    "V4_GOAL4629_SURFACE",
    "V4_GOAL4629_OPERATOR",
    "V4_GOAL4629_SURFACE_STATUS",
    "V4_GOAL4629_DECISION",
    "V4_GOAL4629_WEIGHTED_SUM_RATIOS",
    "V4_GOAL4629_EVIDENCE_FILES",
    "V4WeightedSumCandidateRatio",
    "v4_goal4629_weighted_sum_candidate_decision",
    "validate_v4_goal4629_weighted_sum_candidate_decision",
]
