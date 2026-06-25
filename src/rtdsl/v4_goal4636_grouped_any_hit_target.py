from __future__ import annotations

from dataclasses import dataclass
from typing import Any


V4_GOAL4636B_STATUS = "goal4636_grouped_any_hit_target_predeclared_pending_pod_gate_not_measured"
V4_GOAL4636B_OPERATOR = "ray_triangle_grouped_any_hit_flags_3d"
V4_GOAL4636B_API_SURFACE = "v4_ray_triangle_grouped_any_hit_flags_3d_prepared_runner"
V4_GOAL4636B_GENERIC_PRIMITIVE = "RAY_TRIANGLE_GROUPED_ANY_HIT_FLAGS_3D"
V4_GOAL4636B_TARGET_APP_ROW = "robot_collision"
V4_GOAL4636B_SCOPE = ("rtdl_native_prepared_runner",)
V4_GOAL4636B_OUTPUT_CONTRACT = "prepared_triangle_scene_grouped_segment_any_hit_flags"
V4_GOAL4636B_RUNNER = "scripts/v3_phoenix_robot_collision_flag_stream_no_probe_paired.py"


@dataclass(frozen=True)
class V4Goal4636GroupedAnyHitTarget:
    operator: str
    api_surface: str
    generic_primitive: str
    target_coverage_row: str
    continuation_class: str
    scope: tuple[str, ...]
    output_contract: str
    runner: str
    status: str = V4_GOAL4636B_STATUS
    pod_gate_required: bool = True
    measured_catalog_promotion_authorized: bool = False
    release_claim_authorized: bool = False
    broad_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    app_specific_native_kernel_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    cupy_performance_claim_authorized: bool = False
    c_abi_or_embedding_claim_authorized: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "operator": self.operator,
            "api_surface": self.api_surface,
            "generic_primitive": self.generic_primitive,
            "target_coverage_row": self.target_coverage_row,
            "continuation_class": self.continuation_class,
            "scope": self.scope,
            "output_contract": self.output_contract,
            "runner": self.runner,
            "pod_gate_required": self.pod_gate_required,
            "measured_catalog_promotion_authorized": self.measured_catalog_promotion_authorized,
            "release_claim_authorized": self.release_claim_authorized,
            "broad_speedup_claim_authorized": self.broad_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "app_specific_native_kernel_authorized": self.app_specific_native_kernel_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "cupy_performance_claim_authorized": self.cupy_performance_claim_authorized,
            "c_abi_or_embedding_claim_authorized": self.c_abi_or_embedding_claim_authorized,
            "promotion_gate": {
                "dataset": "scaled",
                "pose_count": 8_192,
                "obstacle_count": 2_048,
                "link_count": 2,
                "sample_count": 5,
                "timed_repeats": 101,
                "timed_warmup": 5,
                "validation_repeats": 5,
                "validation_warmup": 1,
                "requires_rt_hardware": True,
                "requires_validation_status": "pass",
                "requires_timed_status": "pass",
                "tail_total_mean_embree_over_optix_floor": 3.0,
                "traversal_mean_embree_over_optix_floor": 3.0,
                "wrapper_mean_embree_over_optix_floor": 1.10,
                "wrapper_min_embree_over_optix_floor": 1.00,
                "requires_probe_reference_disabled_for_timed_rows": True,
                "requires_validation_and_timed_signature_overlap": True,
                "requires_same_contract_shape_signature_counts": True,
                "timed_status_is_correctness_gate_only": True,
                "requires_post_pod_performance_floor_review": True,
                "requires_traversal_ratio_evaluable": True,
                "promotion_scope": "operator_coverage_only_not_robot_app_wall_time",
                "catalog_surface_addition_requires_separate_frontdoor_goal": True,
            },
            "coverage_effect_if_gate_passes": {
                "row": self.target_coverage_row,
                "from": "partial_measured_operator_coverage",
                "to": "strong_measured_operator_coverage",
                "reason": (
                    "Robot-collision grouped segment flags would map to a reviewed "
                    "generic grouped any-hit flag stream, without adding a robot "
                    "collision native kernel or whole-app planning claim."
                ),
            },
            "selection_reason": (
                "The threshold-summary candidate failed Goal4636. Grouped any-hit "
                "flags target a different generic ray/triangle continuation class, "
                "use the existing same-contract paired runner, and do not require CuPy."
            ),
        }


def v4_goal4636_grouped_any_hit_target() -> dict[str, Any]:
    return V4Goal4636GroupedAnyHitTarget(
        operator=V4_GOAL4636B_OPERATOR,
        api_surface=V4_GOAL4636B_API_SURFACE,
        generic_primitive=V4_GOAL4636B_GENERIC_PRIMITIVE,
        target_coverage_row=V4_GOAL4636B_TARGET_APP_ROW,
        continuation_class="grouped_any_hit_flag_stream",
        scope=V4_GOAL4636B_SCOPE,
        output_contract=V4_GOAL4636B_OUTPUT_CONTRACT,
        runner=V4_GOAL4636B_RUNNER,
    ).as_dict()


def validate_v4_goal4636_grouped_any_hit_target() -> dict[str, Any]:
    target = v4_goal4636_grouped_any_hit_target()
    if target["status"] != V4_GOAL4636B_STATUS:
        raise ValueError("Goal4636 grouped-any-hit target status drift")
    if target["target_coverage_row"] != "robot_collision":
        raise ValueError("Goal4636 grouped-any-hit target must target robot_collision")
    if target["continuation_class"] != "grouped_any_hit_flag_stream":
        raise ValueError("Goal4636 grouped-any-hit target must use generic grouped flag-stream continuation")
    if target["scope"] != ("rtdl_native_prepared_runner",):
        raise ValueError("Goal4636 grouped-any-hit target must declare native runner scope explicitly")
    if not target["pod_gate_required"]:
        raise ValueError("Goal4636 grouped-any-hit target must require POD gate")
    if target["measured_catalog_promotion_authorized"]:
        raise ValueError("Goal4636 grouped-any-hit target must not promote before POD evidence")
    gate = target["promotion_gate"]
    if gate["tail_total_mean_embree_over_optix_floor"] < 3.0:
        raise ValueError("Goal4636 grouped-any-hit tail-total floor must be material")
    if gate["traversal_mean_embree_over_optix_floor"] < 3.0:
        raise ValueError("Goal4636 grouped-any-hit traversal floor must be material")
    if gate["wrapper_mean_embree_over_optix_floor"] < 1.10:
        raise ValueError("Goal4636 grouped-any-hit wrapper mean floor must not be trivial")
    if gate["wrapper_min_embree_over_optix_floor"] < 1.00:
        raise ValueError("Goal4636 grouped-any-hit wrapper min floor must avoid regressions")
    if not gate["timed_status_is_correctness_gate_only"]:
        raise ValueError("Goal4636 grouped-any-hit must treat timed_status as correctness-only")
    if not gate["requires_post_pod_performance_floor_review"]:
        raise ValueError("Goal4636 grouped-any-hit must require post-POD performance floor review")
    if not gate["requires_traversal_ratio_evaluable"]:
        raise ValueError("Goal4636 grouped-any-hit must require evaluable traversal ratio")
    if gate["promotion_scope"] != "operator_coverage_only_not_robot_app_wall_time":
        raise ValueError("Goal4636 grouped-any-hit promotion scope must stay operator-only")
    if not gate["catalog_surface_addition_requires_separate_frontdoor_goal"]:
        raise ValueError("Goal4636 grouped-any-hit catalog addition must require a separate front-door goal")
    for flag in (
        "release_claim_authorized",
        "broad_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "app_specific_native_kernel_authorized",
        "true_zero_copy_claim_authorized",
        "cupy_performance_claim_authorized",
        "c_abi_or_embedding_claim_authorized",
    ):
        if target[flag]:
            raise ValueError(f"Goal4636 grouped-any-hit target must not authorize {flag}")
    return target


__all__ = [
    "V4_GOAL4636B_STATUS",
    "V4_GOAL4636B_OPERATOR",
    "V4_GOAL4636B_API_SURFACE",
    "V4_GOAL4636B_GENERIC_PRIMITIVE",
    "V4_GOAL4636B_TARGET_APP_ROW",
    "V4_GOAL4636B_SCOPE",
    "V4_GOAL4636B_OUTPUT_CONTRACT",
    "V4_GOAL4636B_RUNNER",
    "V4Goal4636GroupedAnyHitTarget",
    "v4_goal4636_grouped_any_hit_target",
    "validate_v4_goal4636_grouped_any_hit_target",
]
