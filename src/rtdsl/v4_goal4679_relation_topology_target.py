from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4679_RELATION_TOPOLOGY_TARGET_STATUS = (
    "goal4679_select_relation_topology_same_primitive_target_no_pod_no_release"
)
V4_GOAL4679_SELECTED_OPERATOR = "SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR"
V4_GOAL4679_SELECTED_SURFACE = "v4_shape_pair_relation_active_count_2d_prepared_left_executor"


@dataclass(frozen=True)
class V4Goal4679RelationTopologyTarget:
    status: str
    selected_operator: str
    selected_surface: str
    app_probe: str
    app_probe_role: str
    work_class: str
    v2_14_same_primitive_existed: bool
    v2_14_denominator_required: bool
    clean_new_v4_lever: bool
    same_primitive_speed_credit_requires_material_improvement: bool
    pod_run_authorized_by_this_artifact: bool
    frozen_numeric_bars: dict[str, float | bool]
    required_next_goal: str
    release_authorized: bool = False
    broad_v4_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    app_identity_native_kernel_authorized: bool = False
    partner_migration_counts_as_v4_speed_win: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "selected_operator": self.selected_operator,
            "selected_surface": self.selected_surface,
            "app_probe": self.app_probe,
            "app_probe_role": self.app_probe_role,
            "work_class": self.work_class,
            "v2_14_same_primitive_existed": self.v2_14_same_primitive_existed,
            "v2_14_denominator_required": self.v2_14_denominator_required,
            "clean_new_v4_lever": self.clean_new_v4_lever,
            "same_primitive_speed_credit_requires_material_improvement": (
                self.same_primitive_speed_credit_requires_material_improvement
            ),
            "pod_run_authorized_by_this_artifact": self.pod_run_authorized_by_this_artifact,
            "frozen_numeric_bars": dict(self.frozen_numeric_bars),
            "required_next_goal": self.required_next_goal,
            "release_authorized": self.release_authorized,
            "broad_v4_speedup_claim_authorized": self.broad_v4_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "app_identity_native_kernel_authorized": self.app_identity_native_kernel_authorized,
            "partner_migration_counts_as_v4_speed_win": self.partner_migration_counts_as_v4_speed_win,
        }


def v4_goal4679_relation_topology_target() -> V4Goal4679RelationTopologyTarget:
    return V4Goal4679RelationTopologyTarget(
        status=V4_GOAL4679_RELATION_TOPOLOGY_TARGET_STATUS,
        selected_operator=V4_GOAL4679_SELECTED_OPERATOR,
        selected_surface=V4_GOAL4679_SELECTED_SURFACE,
        app_probe="spatial_rayjoin.overlay_active_count",
        app_probe_role=(
            "route_coverage_probe_only; the engine target is a generic shape-pair "
            "relation/topology operator, not a RayJoin native kernel"
        ),
        work_class=(
            "same_primitive_productization_or_material_improvement; V2.14 already "
            "had prepared shape-pair active-count routes"
        ),
        v2_14_same_primitive_existed=True,
        v2_14_denominator_required=True,
        clean_new_v4_lever=False,
        same_primitive_speed_credit_requires_material_improvement=True,
        pod_run_authorized_by_this_artifact=False,
        frozen_numeric_bars={
            "correctness_parity_required": True,
            "v4_over_v2_14_same_primitive_hot_min_for_speed_credit": 1.20,
            "v4_over_v2_14_same_primitive_wall_min_for_speed_credit": 1.10,
            "v4_over_v3_0_2_hot_parity_floor": 0.98,
            "hot_path_host_row_stream_materialization_allowed": False,
            "partner_migration_counts_as_speed": False,
        },
        required_next_goal=(
            "Goal4680 must build the local/static V4 frontdoor and protocol gate "
            "for this generic operator before any POD run"
        ),
    )


def validate_v4_goal4679_relation_topology_target() -> dict[str, object]:
    decision = v4_goal4679_relation_topology_target()
    payload = decision.as_dict()
    bars = dict(payload["frozen_numeric_bars"])
    missing: list[str] = []
    if payload["status"] != V4_GOAL4679_RELATION_TOPOLOGY_TARGET_STATUS:
        missing.append("status")
    if payload["selected_operator"] != V4_GOAL4679_SELECTED_OPERATOR:
        missing.append("selected_operator")
    if payload["clean_new_v4_lever"] is not False:
        missing.append("clean_new_v4_lever_false")
    if payload["v2_14_same_primitive_existed"] is not True:
        missing.append("v2_14_same_primitive_existed")
    if payload["v2_14_denominator_required"] is not True:
        missing.append("v2_14_denominator_required")
    if payload["same_primitive_speed_credit_requires_material_improvement"] is not True:
        missing.append("same_primitive_speed_credit_requires_material_improvement")
    if payload["pod_run_authorized_by_this_artifact"] is not False:
        missing.append("pod_run_authorized_false")
    if bars.get("correctness_parity_required") is not True:
        missing.append("correctness_parity_required")
    if float(bars.get("v4_over_v2_14_same_primitive_hot_min_for_speed_credit", 0.0)) < 1.20:
        missing.append("same_primitive_hot_bar")
    if float(bars.get("v4_over_v2_14_same_primitive_wall_min_for_speed_credit", 0.0)) < 1.10:
        missing.append("same_primitive_wall_bar")
    if bars.get("hot_path_host_row_stream_materialization_allowed") is not False:
        missing.append("host_row_stream_materialization_forbidden")
    for key in (
        "release_authorized",
        "broad_v4_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "app_identity_native_kernel_authorized",
        "partner_migration_counts_as_v4_speed_win",
    ):
        if payload.get(key) is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "decision": payload,
        "release_authorized": False,
    }


__all__ = [
    "V4_GOAL4679_RELATION_TOPOLOGY_TARGET_STATUS",
    "V4_GOAL4679_SELECTED_OPERATOR",
    "V4_GOAL4679_SELECTED_SURFACE",
    "V4Goal4679RelationTopologyTarget",
    "v4_goal4679_relation_topology_target",
    "validate_v4_goal4679_relation_topology_target",
]
