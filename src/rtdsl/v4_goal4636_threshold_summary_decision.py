from __future__ import annotations

from typing import Any


V4_GOAL4636_STATUS = "goal4636_threshold_summary_pod_gate_failed_no_promotion_not_release"
V4_GOAL4636_DECISION = "reject_threshold_summary_promotion_keep_hausdorff_partial"
V4_GOAL4636_EVIDENCE = (
    "tools/_archive/future/v4/evidence/v4_goal4636_threshold_summary_pod_gate_2026-06-25/summary.json",
    "tools/_archive/future/v4/evidence/v4_goal4636_threshold_summary_pod_gate_2026-06-25/README.md",
    "tools/_archive/future/v4/reviews/goal4636_threshold_summary_target_protocol_review_record_2026-06-25.md",
)


def v4_goal4636_threshold_summary_decision() -> dict[str, Any]:
    return {
        "status": V4_GOAL4636_STATUS,
        "decision": V4_GOAL4636_DECISION,
        "operator": "fixed_radius_threshold_summary_2d",
        "api_surface": "v4_fixed_radius_threshold_summary_2d_prepared_runner",
        "generic_primitive": "FIXED_RADIUS_THRESHOLD_REACHED_COUNT_2D",
        "target_coverage_row": "hausdorff_xhd",
        "continuation_class": "threshold_summary",
        "scope": "rtdl_native_prepared_runner",
        "same_contract_gate": {
            "status": "fail",
            "failed_checks": ("runner_regressed_vs_legacy_phase_total",),
            "points_per_side": 1_048_576,
            "repeat": 5,
            "warmup": 1,
            "runner_step3_residency_default_ready": True,
            "runner_vs_embree_phase_total_speedup": 1.2759701868849942,
            "runner_vs_embree_wrapper_wall_speedup": 1.7376484711304498,
            "runner_vs_embree_phase_total_floor": 1.20,
            "runner_vs_embree_wrapper_wall_floor": 1.20,
            "runner_vs_legacy_phase_total_speedup": 0.9693326333237459,
            "runner_vs_legacy_wrapper_wall_speedup": 0.9898664196438816,
            "runner_vs_legacy_phase_total_floor": 0.98,
            "runner_vs_legacy_wrapper_wall_floor": 0.98,
        },
        "coverage_effect": {
            "row": "hausdorff_xhd",
            "from": "partial_measured_operator_coverage",
            "to": "partial_measured_operator_coverage",
            "reason": (
                "The productized runner materially beat Embree but missed the "
                "predeclared legacy phase-total no-regression floor, so the "
                "Hausdorff/XHD row must remain partial."
            ),
        },
        "next_action": (
            "Do not promote threshold-summary from this gate. Continue Goal4636 by "
            "selecting a different predeclared generic target, or return to this "
            "target only with a new protocol that explains the legacy phase-total "
            "regression before any rerun."
        ),
        "evidence": V4_GOAL4636_EVIDENCE,
        "measured_catalog_promotion_authorized": False,
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


def validate_v4_goal4636_threshold_summary_decision() -> dict[str, Any]:
    decision = v4_goal4636_threshold_summary_decision()
    if decision["decision"] != V4_GOAL4636_DECISION:
        raise ValueError("Goal4636 decision drift")
    gate = decision["same_contract_gate"]
    if gate["status"] != "fail":
        raise ValueError("Goal4636 threshold-summary gate must remain failed")
    if "runner_regressed_vs_legacy_phase_total" not in gate["failed_checks"]:
        raise ValueError("Goal4636 failure reason must remain visible")
    if gate["runner_vs_embree_phase_total_speedup"] < gate["runner_vs_embree_phase_total_floor"]:
        raise ValueError("Goal4636 should preserve material Embree win evidence")
    if gate["runner_vs_embree_wrapper_wall_speedup"] < gate["runner_vs_embree_wrapper_wall_floor"]:
        raise ValueError("Goal4636 should preserve material Embree wall win evidence")
    if gate["runner_vs_legacy_phase_total_speedup"] >= gate["runner_vs_legacy_phase_total_floor"]:
        raise ValueError("Goal4636 legacy phase-total failure no longer matches evidence")
    if decision["coverage_effect"]["to"] != "partial_measured_operator_coverage":
        raise ValueError("Failed Goal4636 gate must keep Hausdorff partial")
    for flag in (
        "measured_catalog_promotion_authorized",
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
            raise ValueError(f"Goal4636 must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4636_STATUS",
    "V4_GOAL4636_DECISION",
    "V4_GOAL4636_EVIDENCE",
    "v4_goal4636_threshold_summary_decision",
    "validate_v4_goal4636_threshold_summary_decision",
]
