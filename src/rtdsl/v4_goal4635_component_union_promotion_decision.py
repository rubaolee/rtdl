from __future__ import annotations

from typing import Any


V4_GOAL4635_STATUS = "goal4635_component_union_measured_pod_gate_pass_not_release"
V4_GOAL4635_DECISION = "promote_component_union_to_measured_tier2_operator_coverage_not_release"
V4_GOAL4635_EVIDENCE = (
    "future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/summary.json",
    "future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/README.md",
    "future/v4/reviews/claude_v4_goal4635_component_union_target_protocol_review_2026-06-25.md",
)


def v4_goal4635_component_union_promotion_decision() -> dict[str, Any]:
    return {
        "status": V4_GOAL4635_STATUS,
        "decision": V4_GOAL4635_DECISION,
        "operator": "fixed_radius_graph_component_union_3d",
        "api_surface": "v4_fixed_radius_graph_component_union_3d_device_arrays",
        "generic_primitive": "FIXED_RADIUS_GRAPH_COMPONENT_UNION_3D",
        "target_coverage_row": "rt_dbscan",
        "continuation_class": "component_union",
        "measured_partners": ("numba",),
        "declared_unmeasured_partners": ("torch", "cupy"),
        "validated_scope": {
            "gpu": "NVIDIA RTX A5000",
            "driver": "570.195.03",
            "optix_abi": "8.0",
            "python": "3.12.3",
            "numba": "0.65.1",
            "dataset": "clustered3d",
            "point_count": 262_144,
            "repeat": 5,
            "warmup": 1,
        },
        "same_contract_gate": {
            "status": "pass",
            "failed_checks": (),
            "all_variant_canonical_component_signatures_match": True,
            "legacy_no_regression": True,
            "component_labels_contract": True,
            "component_signature_shortcut_blocked": True,
            "runner_vs_embree_hot_speedup": 1.3930791165731065,
            "runner_vs_embree_wall_speedup": 1.6001250028719352,
            "runner_vs_legacy_hot_speedup": 1.0009063305938157,
            "runner_vs_legacy_wall_speedup": 1.2080037787208602,
            "runner_vs_embree_hot_floor": 1.20,
            "runner_vs_embree_wall_floor": 1.20,
            "runner_vs_legacy_wall_floor": 0.98,
        },
        "coverage_effect": {
            "row": "rt_dbscan",
            "from": "partial_measured_operator_coverage",
            "to": "strong_measured_operator_coverage",
            "reason": (
                "RTDBSCAN now maps to measured generic count-threshold plus "
                "measured generic component-union operator coverage without adding "
                "a DBSCAN-native kernel."
            ),
        },
        "evidence": V4_GOAL4635_EVIDENCE,
        "release_authorized": False,
        "release_candidate_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "all_benchmark_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "torch_component_union_claim_authorized": False,
        "c_abi_or_embedding_claim_authorized": False,
        "non_python_host_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


def validate_v4_goal4635_component_union_promotion_decision() -> dict[str, Any]:
    decision = v4_goal4635_component_union_promotion_decision()
    if decision["decision"] != V4_GOAL4635_DECISION:
        raise ValueError("Goal4635 decision drift")
    gate = decision["same_contract_gate"]
    if gate["failed_checks"]:
        raise ValueError("Goal4635 promotion requires zero failed gate checks")
    if not gate["all_variant_canonical_component_signatures_match"]:
        raise ValueError("Goal4635 requires canonical component signatures to match")
    if gate["runner_vs_embree_hot_speedup"] < gate["runner_vs_embree_hot_floor"]:
        raise ValueError("Goal4635 runner vs Embree hot speedup below floor")
    if gate["runner_vs_embree_wall_speedup"] < gate["runner_vs_embree_wall_floor"]:
        raise ValueError("Goal4635 runner vs Embree wall speedup below floor")
    if gate["runner_vs_legacy_wall_speedup"] < gate["runner_vs_legacy_wall_floor"]:
        raise ValueError("Goal4635 runner vs legacy wall speedup below floor")
    if decision["measured_partners"] != ("numba",):
        raise ValueError("Goal4635 component-union promotion is Numba-scoped only")
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
        "torch_component_union_claim_authorized",
        "c_abi_or_embedding_claim_authorized",
        "non_python_host_claim_authorized",
        "app_specific_native_kernel_authorized",
    ):
        if decision[flag]:
            raise ValueError(f"Goal4635 must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4635_STATUS",
    "V4_GOAL4635_DECISION",
    "V4_GOAL4635_EVIDENCE",
    "v4_goal4635_component_union_promotion_decision",
    "validate_v4_goal4635_component_union_promotion_decision",
]
