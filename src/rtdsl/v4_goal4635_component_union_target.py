from __future__ import annotations

from dataclasses import dataclass
from typing import Any


V4_GOAL4635_STATUS = "goal4635_component_union_target_predeclared_pending_pod_gate_not_measured"
V4_GOAL4635_OPERATOR = "fixed_radius_graph_component_union_3d"
V4_GOAL4635_API_SURFACE = "v4_fixed_radius_graph_component_union_3d_device_arrays"
V4_GOAL4635_GENERIC_PRIMITIVE = "FIXED_RADIUS_GRAPH_COMPONENT_UNION_3D"
V4_GOAL4635_TARGET_APP_ROW = "rt_dbscan"
V4_GOAL4635_PARTNER_SCOPE = ("numba",)
V4_GOAL4635_OUTPUT_CONTRACT = "generic_prepared_optix_numba_grouped_stream_component_labels_3d"
V4_GOAL4635_RUNNER = "scripts/v3_phoenix_component_union_m38_pod_ab.py"


@dataclass(frozen=True)
class V4Goal4635ComponentUnionTarget:
    operator: str
    api_surface: str
    generic_primitive: str
    target_coverage_row: str
    continuation_class: str
    partner_scope: tuple[str, ...]
    output_contract: str
    runner: str
    status: str = V4_GOAL4635_STATUS
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
                "dataset": "clustered3d",
                "point_count_floor": 262_144,
                "repeat": 5,
                "warmup": 1,
                "requires_rt_hardware": True,
                "runner_vs_embree_hot_floor": 1.20,
                "runner_vs_embree_wall_floor": 1.20,
                "runner_vs_legacy_wall_floor": 0.98,
                "requires_canonical_component_signature_match": True,
                "requires_component_label_columns": True,
                "forbids_component_signature_substitution": True,
                "requires_runtime_trunk_end_to_end": True,
                "forbids_hot_path_host_materialization": True,
            },
            "coverage_effect_if_gate_passes": {
                "row": self.target_coverage_row,
                "from": "partial_measured_operator_coverage",
                "to": "strong_measured_operator_coverage",
                "reason": (
                    "fixed-radius count-threshold plus generic component labels would cover "
                    "the RTDBSCAN continuation class without adding a DBSCAN-native kernel"
                ),
            },
        }


def v4_goal4635_component_union_target() -> dict[str, Any]:
    return V4Goal4635ComponentUnionTarget(
        operator=V4_GOAL4635_OPERATOR,
        api_surface=V4_GOAL4635_API_SURFACE,
        generic_primitive=V4_GOAL4635_GENERIC_PRIMITIVE,
        target_coverage_row=V4_GOAL4635_TARGET_APP_ROW,
        continuation_class="component_union",
        partner_scope=V4_GOAL4635_PARTNER_SCOPE,
        output_contract=V4_GOAL4635_OUTPUT_CONTRACT,
        runner=V4_GOAL4635_RUNNER,
    ).as_dict()


def validate_v4_goal4635_component_union_target() -> dict[str, Any]:
    target = v4_goal4635_component_union_target()
    if target["status"] != V4_GOAL4635_STATUS:
        raise ValueError("Goal4635 target status drift")
    if target["target_coverage_row"] != "rt_dbscan":
        raise ValueError("Goal4635 must target the rt_dbscan coverage row")
    if target["continuation_class"] != "component_union":
        raise ValueError("Goal4635 must target generic component_union continuation")
    if target["partner_scope"] != ("numba",):
        raise ValueError("Goal4635 component-union target must declare Numba scope explicitly")
    if not target["pod_gate_required"]:
        raise ValueError("Goal4635 must not promote without a POD gate")
    if target["measured_catalog_promotion_authorized"]:
        raise ValueError("Goal4635 target selection must not promote the catalog")
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
            raise ValueError(f"Goal4635 target selection must not authorize {flag}")
    gate = target["promotion_gate"]
    if gate["runner_vs_embree_hot_floor"] < 1.20 or gate["runner_vs_embree_wall_floor"] < 1.20:
        raise ValueError("Goal4635 material floor must be at least 1.20x")
    if gate["runner_vs_legacy_wall_floor"] < 0.98:
        raise ValueError("Goal4635 legacy no-regression floor must be at least 0.98x")
    if not gate["forbids_component_signature_substitution"]:
        raise ValueError("Goal4635 must forbid component-signature substitution")
    return target


__all__ = [
    "V4_GOAL4635_STATUS",
    "V4_GOAL4635_OPERATOR",
    "V4_GOAL4635_API_SURFACE",
    "V4_GOAL4635_GENERIC_PRIMITIVE",
    "V4_GOAL4635_TARGET_APP_ROW",
    "V4_GOAL4635_PARTNER_SCOPE",
    "V4_GOAL4635_OUTPUT_CONTRACT",
    "V4_GOAL4635_RUNNER",
    "V4Goal4635ComponentUnionTarget",
    "v4_goal4635_component_union_target",
    "validate_v4_goal4635_component_union_target",
]
