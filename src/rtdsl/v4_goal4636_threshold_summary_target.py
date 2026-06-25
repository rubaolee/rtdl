from __future__ import annotations

from dataclasses import dataclass
from typing import Any


V4_GOAL4636_STATUS = "goal4636_threshold_summary_target_predeclared_pending_pod_gate_not_measured"
V4_GOAL4636_OPERATOR = "fixed_radius_threshold_summary_2d"
V4_GOAL4636_API_SURFACE = "v4_fixed_radius_threshold_summary_2d_prepared_runner"
V4_GOAL4636_GENERIC_PRIMITIVE = "FIXED_RADIUS_THRESHOLD_REACHED_COUNT_2D"
V4_GOAL4636_TARGET_APP_ROW = "hausdorff_xhd"
V4_GOAL4636_PARTNER_SCOPE = ("rtdl_native_prepared_runner",)
V4_GOAL4636_OUTPUT_CONTRACT = "generic_prepared_optix_scalar_threshold_count_2d"
V4_GOAL4636_RUNNER = "scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py"


@dataclass(frozen=True)
class V4Goal4636ThresholdSummaryTarget:
    operator: str
    api_surface: str
    generic_primitive: str
    target_coverage_row: str
    continuation_class: str
    partner_scope: tuple[str, ...]
    output_contract: str
    runner: str
    status: str = V4_GOAL4636_STATUS
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
            "partner_scope": self.partner_scope,
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
                "copies": 262_144,
                "points_per_side_floor": 1_048_576,
                "threshold": 0.4,
                "repeat": 5,
                "warmup": 1,
                "requires_rt_hardware": True,
                "runner_vs_embree_phase_total_floor": 1.20,
                "runner_vs_embree_wrapper_wall_floor": 1.20,
                "runner_vs_legacy_phase_total_floor": 0.98,
                "runner_vs_legacy_wrapper_wall_floor": 0.98,
                "requires_all_variants_ok": True,
                "requires_oracle_match_all_variants": True,
                "requires_runtime_trunk_end_to_end": True,
                "requires_both_directed_legs_runtime_executed": True,
                "forbids_threshold_rows_materialized_on_host": True,
                "requires_internal_device_residency_between_rtdl_phases": True,
                "requires_step3_audit_ready": True,
            },
            "coverage_effect_if_gate_passes": {
                "row": self.target_coverage_row,
                "from": "partial_measured_operator_coverage",
                "to": "strong_measured_operator_coverage",
                "reason": (
                    "Hausdorff/XHD's directed threshold workflow would have a reviewed "
                    "generic scalar threshold-summary runner at serious scale, without "
                    "adding a Hausdorff-native kernel or whole-app speedup claim."
                ),
            },
            "selection_reason": (
                "Goal4636 must prove Goal4635 was not a one-off. Threshold summary is a "
                "different continuation class from component_union and can be measured on "
                "the current POD without pulling CuPy validation forward from Goal4637."
            ),
        }


def v4_goal4636_threshold_summary_target() -> dict[str, Any]:
    return V4Goal4636ThresholdSummaryTarget(
        operator=V4_GOAL4636_OPERATOR,
        api_surface=V4_GOAL4636_API_SURFACE,
        generic_primitive=V4_GOAL4636_GENERIC_PRIMITIVE,
        target_coverage_row=V4_GOAL4636_TARGET_APP_ROW,
        continuation_class="threshold_summary",
        partner_scope=V4_GOAL4636_PARTNER_SCOPE,
        output_contract=V4_GOAL4636_OUTPUT_CONTRACT,
        runner=V4_GOAL4636_RUNNER,
    ).as_dict()


def validate_v4_goal4636_threshold_summary_target() -> dict[str, Any]:
    target = v4_goal4636_threshold_summary_target()
    if target["status"] != V4_GOAL4636_STATUS:
        raise ValueError("Goal4636 target status drift")
    if target["target_coverage_row"] != "hausdorff_xhd":
        raise ValueError("Goal4636 must target the hausdorff_xhd coverage row")
    if target["continuation_class"] != "threshold_summary":
        raise ValueError("Goal4636 must target generic threshold_summary continuation")
    if target["partner_scope"] != ("rtdl_native_prepared_runner",):
        raise ValueError("Goal4636 threshold-summary target must declare native runner scope explicitly")
    if not target["pod_gate_required"]:
        raise ValueError("Goal4636 must not promote without a POD gate")
    if target["measured_catalog_promotion_authorized"]:
        raise ValueError("Goal4636 target selection must not promote the catalog")
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
            raise ValueError(f"Goal4636 target selection must not authorize {flag}")
    gate = target["promotion_gate"]
    if gate["points_per_side_floor"] < 1_048_576:
        raise ValueError("Goal4636 serious floor must be at least 1,048,576 points per side")
    if gate["runner_vs_embree_phase_total_floor"] < 1.20:
        raise ValueError("Goal4636 material phase-total floor must be at least 1.20x")
    if gate["runner_vs_embree_wrapper_wall_floor"] < 1.20:
        raise ValueError("Goal4636 material wrapper-wall floor must be at least 1.20x")
    if gate["runner_vs_legacy_phase_total_floor"] < 0.98 or gate["runner_vs_legacy_wrapper_wall_floor"] < 0.98:
        raise ValueError("Goal4636 legacy no-regression floors must be at least 0.98x")
    if not gate["forbids_threshold_rows_materialized_on_host"]:
        raise ValueError("Goal4636 must forbid threshold-row materialization on the hot path")
    return target


__all__ = [
    "V4_GOAL4636_STATUS",
    "V4_GOAL4636_OPERATOR",
    "V4_GOAL4636_API_SURFACE",
    "V4_GOAL4636_GENERIC_PRIMITIVE",
    "V4_GOAL4636_TARGET_APP_ROW",
    "V4_GOAL4636_PARTNER_SCOPE",
    "V4_GOAL4636_OUTPUT_CONTRACT",
    "V4_GOAL4636_RUNNER",
    "V4Goal4636ThresholdSummaryTarget",
    "v4_goal4636_threshold_summary_target",
    "validate_v4_goal4636_threshold_summary_target",
]
