from __future__ import annotations

from typing import Any


V4_GOAL4636B_DECISION_STATUS = "goal4636b_grouped_any_hit_pod_gate_failed_no_promotion_not_release"
V4_GOAL4636B_DECISION = "reject_grouped_any_hit_promotion_keep_robot_collision_partial"
V4_GOAL4636B_EVIDENCE = (
    "future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/summary.json",
    "future/v4/reviews/goal4636b_grouped_any_hit_target_protocol_review_record_2026-06-25.md",
)


def v4_goal4636_grouped_any_hit_decision() -> dict[str, Any]:
    return {
        "status": V4_GOAL4636B_DECISION_STATUS,
        "decision": V4_GOAL4636B_DECISION,
        "operator": "ray_triangle_grouped_any_hit_flags_3d",
        "api_surface": "v4_ray_triangle_grouped_any_hit_flags_3d_prepared_runner",
        "generic_primitive": "RAY_TRIANGLE_GROUPED_ANY_HIT_FLAGS_3D",
        "target_coverage_row": "robot_collision",
        "continuation_class": "grouped_any_hit_flag_stream",
        "scope": "rtdl_native_prepared_runner",
        "same_contract_gate": {
            "status": "fail",
            "validation_status": "pass",
            "timed_status": "pass",
            "performance_floor_status": "fail",
            "failed_checks": (
                "wrapper_mean_embree_over_optix_below_floor",
                "wrapper_min_embree_over_optix_below_floor",
            ),
            "dataset": "scaled",
            "pose_count": 8_192,
            "obstacle_count": 2_048,
            "link_count": 2,
            "sample_count": 5,
            "timed_repeats": 101,
            "timed_warmup": 5,
            "validation_repeats": 5,
            "validation_warmup": 1,
            "timed_rows_probe_reference_disabled": True,
            "validation_and_timed_signatures_overlap": True,
            "all_timed_pairs_same_contract_shape_signature_counts": True,
            "tail_total_mean_embree_over_optix": 4.127811276781783,
            "tail_total_mean_embree_over_optix_floor": 3.0,
            "traversal_mean_embree_over_optix": 30.5146629599939,
            "traversal_mean_embree_over_optix_floor": 3.0,
            "wrapper_mean_embree_over_optix": 0.8566591773370428,
            "wrapper_mean_embree_over_optix_floor": 1.10,
            "wrapper_min_embree_over_optix": 0.8234887931897568,
            "wrapper_min_embree_over_optix_floor": 1.00,
        },
        "coverage_effect": {
            "row": "robot_collision",
            "from": "partial_measured_operator_coverage",
            "to": "partial_measured_operator_coverage",
            "reason": (
                "The native grouped any-hit flag stream passed correctness and "
                "showed strong tail/traversal ratios, but missed the predeclared "
                "wrapper-wall performance floors. Robot collision therefore "
                "remains partial operator coverage."
            ),
        },
        "next_action": (
            "Do not promote grouped any-hit from this gate. Continue Goal4636 with "
            "another predeclared generic target, or return only through a separate "
            "front-door/wrapper-hardening goal that explains the wrapper-wall loss."
        ),
        "evidence": V4_GOAL4636B_EVIDENCE,
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


def validate_v4_goal4636_grouped_any_hit_decision() -> dict[str, Any]:
    decision = v4_goal4636_grouped_any_hit_decision()
    if decision["decision"] != V4_GOAL4636B_DECISION:
        raise ValueError("Goal4636B decision drift")
    gate = decision["same_contract_gate"]
    if gate["status"] != "fail":
        raise ValueError("Goal4636B grouped-any-hit gate must remain failed")
    if gate["validation_status"] != "pass" or gate["timed_status"] != "pass":
        raise ValueError("Goal4636B must preserve correctness-pass evidence")
    if gate["performance_floor_status"] != "fail":
        raise ValueError("Goal4636B performance floor failure must remain visible")
    for failed_check in (
        "wrapper_mean_embree_over_optix_below_floor",
        "wrapper_min_embree_over_optix_below_floor",
    ):
        if failed_check not in gate["failed_checks"]:
            raise ValueError(f"Goal4636B missing failed check {failed_check}")
    if gate["tail_total_mean_embree_over_optix"] < gate["tail_total_mean_embree_over_optix_floor"]:
        raise ValueError("Goal4636B should preserve material tail-total win evidence")
    if gate["traversal_mean_embree_over_optix"] < gate["traversal_mean_embree_over_optix_floor"]:
        raise ValueError("Goal4636B should preserve material traversal win evidence")
    if gate["wrapper_mean_embree_over_optix"] >= gate["wrapper_mean_embree_over_optix_floor"]:
        raise ValueError("Goal4636B wrapper mean failure no longer matches evidence")
    if gate["wrapper_min_embree_over_optix"] >= gate["wrapper_min_embree_over_optix_floor"]:
        raise ValueError("Goal4636B wrapper min failure no longer matches evidence")
    if decision["coverage_effect"]["to"] != "partial_measured_operator_coverage":
        raise ValueError("Failed Goal4636B gate must keep robot_collision partial")
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
            raise ValueError(f"Goal4636B must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4636B_DECISION_STATUS",
    "V4_GOAL4636B_DECISION",
    "V4_GOAL4636B_EVIDENCE",
    "v4_goal4636_grouped_any_hit_decision",
    "validate_v4_goal4636_grouped_any_hit_decision",
]
