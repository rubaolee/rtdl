from __future__ import annotations

from dataclasses import dataclass
from typing import Any


V4_GOAL4628_SECOND_GATE_STATUS = "goal4628_second_tier2_gate_scorecard_not_release"
V4_GOAL4628_TARGET_OPERATOR = "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays"
V4_GOAL4628_GENERIC_PRIMITIVE = "RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D"
V4_GOAL4628_ANCHOR_APP = "raydb_style"
V4_GOAL4628_FIXED_RADIUS_PREREQUISITE = "external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive"


@dataclass(frozen=True)
class V4SecondGateRatio:
    group_width: int
    ray_count: int
    group_count: int
    same_contract_ratio: float
    parity_passed: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "group_width": self.group_width,
            "ray_count": self.ray_count,
            "group_count": self.group_count,
            "same_contract_ratio": self.same_contract_ratio,
            "parity_passed": self.parity_passed,
        }


V4_GOAL4628_GROUPED_I64_RATIOS = (
    V4SecondGateRatio(group_width=1, ray_count=32768, group_count=32768, same_contract_ratio=166.5457315834383, parity_passed=True),
    V4SecondGateRatio(group_width=1, ray_count=131072, group_count=131072, same_contract_ratio=411.8665310113891, parity_passed=True),
    V4SecondGateRatio(group_width=16, ray_count=32768, group_count=2048, same_contract_ratio=11.270692268822637, parity_passed=True),
    V4SecondGateRatio(group_width=16, ray_count=131072, group_count=8192, same_contract_ratio=21.3693298753451, parity_passed=True),
    V4SecondGateRatio(group_width=256, ray_count=32768, group_count=128, same_contract_ratio=1.6413506440190897, parity_passed=True),
    V4SecondGateRatio(group_width=256, ray_count=131072, group_count=512, same_contract_ratio=2.977954183815882, parity_passed=True),
)


V4_GOAL4628_EVIDENCE_FILES = (
    "future/v4/evidence/v4_goal4617_grouped_i64_width1_pod_gate_32768_131072_2026-06-24.json",
    "future/v4/evidence/v4_goal4617_grouped_i64_width16_pod_gate_32768_131072_2026-06-24.json",
    "future/v4/evidence/v4_goal4617_grouped_i64_width256_pod_gate_32768_131072_2026-06-24.json",
    "future/v4/reviews/claude_v4_goal4617_grouped_i64_promotion_decision_review_2026-06-24.raw.md",
    "future/v4/reviews/goal4627_completion_consensus_and_review_debt_2026-06-24.md",
)


def v4_goal4628_second_gate_scorecard() -> dict[str, Any]:
    ratios = tuple(row.as_dict() for row in V4_GOAL4628_GROUPED_I64_RATIOS)
    min_ratio = min(row.same_contract_ratio for row in V4_GOAL4628_GROUPED_I64_RATIOS)
    max_ratio = max(row.same_contract_ratio for row in V4_GOAL4628_GROUPED_I64_RATIOS)
    return {
        "status": V4_GOAL4628_SECOND_GATE_STATUS,
        "anchor_app": V4_GOAL4628_ANCHOR_APP,
        "operator": V4_GOAL4628_TARGET_OPERATOR,
        "generic_primitive": V4_GOAL4628_GENERIC_PRIMITIVE,
        "continuation_class": "grouped_i64_reduction",
        "fixed_radius_wrapper_prerequisite": V4_GOAL4628_FIXED_RADIUS_PREREQUISITE,
        "fixed_radius_wrapper_prerequisite_satisfied_by": (
            "src/rtdsl/v4_fixed_radius.py",
            "future/v4/fixed_radius_device_array_frontdoor.md",
            "future/v4/examples/fixed_radius_torch_device_arrays.py",
            "future/v4/reviews/claude_v4_section8_device_array_frontdoor_amendment_closure_2026-06-24.md",
            "tests/v4_fixed_radius_device_array_api_test.py",
            "tests/v4_fixed_radius_docs_and_example_test.py",
        ),
        "evidence_files": V4_GOAL4628_EVIDENCE_FILES,
        "ratios": ratios,
        "min_same_contract_ratio": min_ratio,
        "max_same_contract_ratio": max_ratio,
        "parity_all_passed": all(row.parity_passed for row in V4_GOAL4628_GROUPED_I64_RATIOS),
        "group_widths": (1, 16, 256),
        "ray_counts": (32768, 131072),
        "win_source": "direct_device_output_columns_remove_legacy_group_row_host_materialization",
        "fresh_pod_rerun_required_before_goal4628_completion": False,
        "fresh_pod_rerun_reason": "Existing serious RTX A5000 POD evidence covers the selected grouped-i64 second gate unless external review finds a same-contract or product-boundary gap.",
        "release_claim_authorized": False,
        "broad_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


def validate_v4_goal4628_second_gate_scorecard() -> dict[str, Any]:
    scorecard = v4_goal4628_second_gate_scorecard()
    if scorecard["operator"] != V4_GOAL4628_TARGET_OPERATOR:
        raise ValueError("Goal4628 must target grouped-i64")
    if scorecard["anchor_app"] != V4_GOAL4628_ANCHOR_APP:
        raise ValueError("Goal4628 must stay anchored to raydb_style")
    if scorecard["min_same_contract_ratio"] <= 1.0:
        raise ValueError("Goal4628 grouped-i64 gate must be faster than the legacy host-output route at every tested point")
    if not scorecard["parity_all_passed"]:
        raise ValueError("Goal4628 grouped-i64 parity must pass at every tested point")
    if scorecard["fresh_pod_rerun_required_before_goal4628_completion"]:
        raise ValueError("Goal4628 scorecard unexpectedly requires a fresh POD rerun")
    for flag in (
        "release_claim_authorized",
        "broad_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "tier3_callback_claim_authorized",
        "cupy_performance_claim_authorized",
        "app_specific_native_kernel_authorized",
    ):
        if scorecard[flag]:
            raise ValueError(f"Goal4628 must not authorize {flag}")
    return scorecard


__all__ = [
    "V4_GOAL4628_SECOND_GATE_STATUS",
    "V4_GOAL4628_TARGET_OPERATOR",
    "V4_GOAL4628_GENERIC_PRIMITIVE",
    "V4_GOAL4628_ANCHOR_APP",
    "V4_GOAL4628_FIXED_RADIUS_PREREQUISITE",
    "V4_GOAL4628_GROUPED_I64_RATIOS",
    "V4_GOAL4628_EVIDENCE_FILES",
    "V4SecondGateRatio",
    "v4_goal4628_second_gate_scorecard",
    "validate_v4_goal4628_second_gate_scorecard",
]
