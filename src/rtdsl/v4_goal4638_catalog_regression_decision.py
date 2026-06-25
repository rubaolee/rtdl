from __future__ import annotations

from typing import Any


# Historical filename note: this module records the AABB-after-catalog GPU
# regression gate as supporting evidence. The controlling owner-approved
# Goal4638 exit gate is the formal release scorecard freeze module.
V4_GOAL4638_DECISION_STATUS = "goal4638_catalog_regression_gpu_after_aabb_passed_not_release"
V4_GOAL4638_DECISION = "accept_catalog_regression_gpu_gate_after_aabb_not_release"
V4_GOAL4638_EVIDENCE = (
    "future/v4/evidence/v4_goal4638_catalog_regression_gpu_after_aabb_2026-06-25.json",
    "future/v4/evidence/v4_goal4638_catalog_regression_gpu_after_aabb_2026-06-25.md",
)


def v4_goal4638_catalog_regression_decision() -> dict[str, Any]:
    return {
        "status": V4_GOAL4638_DECISION_STATUS,
        "decision": V4_GOAL4638_DECISION,
        "mode": "gpu",
        "example_count": 11,
        "failed_examples": (),
        "quickstart_measured_surface_count": 8,
        "quickstart_candidate_surface_count": 0,
        "quickstart_measured_partners": ("numba", "rtdl_native", "torch"),
        "aabb_example_status": "measured",
        "aabb_example_backend": "optix",
        "aabb_example_correctness_passed": True,
        "weighted_sum_example_status": "measured",
        "evidence": V4_GOAL4638_EVIDENCE,
        "release_authorized": False,
        "release_candidate_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "all_benchmark_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "c_abi_or_embedding_claim_authorized": False,
        "non_python_host_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


def validate_v4_goal4638_catalog_regression_decision() -> dict[str, Any]:
    decision = v4_goal4638_catalog_regression_decision()
    if decision["decision"] != V4_GOAL4638_DECISION:
        raise ValueError("Goal4638 decision drift")
    if decision["example_count"] != 11:
        raise ValueError("Goal4638 catalog gate must include 11 examples after AABB")
    if decision["failed_examples"]:
        raise ValueError("Goal4638 catalog gate must preserve zero failed examples")
    if decision["quickstart_measured_surface_count"] != 8:
        raise ValueError("Goal4638 quickstart surface count must remain 8")
    if decision["quickstart_candidate_surface_count"] != 0:
        raise ValueError("Goal4638 quickstart candidate count must remain 0")
    if decision["aabb_example_status"] != "measured" or not decision["aabb_example_correctness_passed"]:
        raise ValueError("Goal4638 AABB example must be measured and correctness-passing")
    for flag in (
        "release_authorized",
        "release_candidate_authorized",
        "broad_v4_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "all_benchmark_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "tier3_callback_claim_authorized",
        "raw_optix_callback_claim_authorized",
        "cupy_performance_claim_authorized",
        "c_abi_or_embedding_claim_authorized",
        "non_python_host_claim_authorized",
        "app_specific_native_kernel_authorized",
    ):
        if decision[flag]:
            raise ValueError(f"Goal4638 must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4638_DECISION_STATUS",
    "V4_GOAL4638_DECISION",
    "V4_GOAL4638_EVIDENCE",
    "v4_goal4638_catalog_regression_decision",
    "validate_v4_goal4638_catalog_regression_decision",
]
