from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4682_NEXT_TARGET_STATUS = (
    "goal4682_shape_pair_no_promotion_select_contact_witness_design_gate_no_pod"
)
V4_GOAL4682_REJECTED_SURFACE = "v4_shape_pair_relation_active_count_2d_prepared_left_executor"
V4_GOAL4682_SELECTED_DESIGN_TARGET = "AABB_PAIR_EXACT_WITNESS_DEVICE_COLUMNS_2D"


@dataclass(frozen=True)
class V4Goal4682NextTargetDecision:
    status: str
    rejected_surface: str
    rejected_reason: str
    selected_design_target: str
    target_class: str
    next_goal: str
    pod_authorized: bool = False
    implementation_authorized: bool = False
    release_authorized: bool = False
    promote_rejected_surface_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    app_identity_kernel_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "rejected_surface": self.rejected_surface,
            "rejected_reason": self.rejected_reason,
            "selected_design_target": self.selected_design_target,
            "target_class": self.target_class,
            "next_goal": self.next_goal,
            "pod_authorized": self.pod_authorized,
            "implementation_authorized": self.implementation_authorized,
            "release_authorized": self.release_authorized,
            "promote_rejected_surface_authorized": self.promote_rejected_surface_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "app_identity_kernel_authorized": self.app_identity_kernel_authorized,
        }


def v4_goal4682_next_target_after_shape_pair() -> V4Goal4682NextTargetDecision:
    return V4Goal4682NextTargetDecision(
        status=V4_GOAL4682_NEXT_TARGET_STATUS,
        rejected_surface=V4_GOAL4682_REJECTED_SURFACE,
        rejected_reason=(
            "Goal4681 passed correctness but failed V2.14/V3 performance bars: "
            "V4/V2.14 hot 0.963x, V4/V2.14 wall 0.605x, V4/V3.0.2 hot 0.977x"
        ),
        selected_design_target=V4_GOAL4682_SELECTED_DESIGN_TARGET,
        target_class=(
            "design_audit_gate_only; potential new generic contact/witness pipeline "
            "that must combine candidate discovery and exact witness refinement as "
            "device columns, not merely rewrap V2.14 bounded collect-k"
        ),
        next_goal=(
            "Goal4683 must prove whether AABB_PAIR_EXACT_WITNESS_DEVICE_COLUMNS_2D "
            "is absent from V2.14, app-name-free, and plausibly able to remove "
            "host candidate/witness materialization before any implementation or POD run"
        ),
    )


def validate_v4_goal4682_next_target_after_shape_pair() -> dict[str, object]:
    decision = v4_goal4682_next_target_after_shape_pair()
    payload = decision.as_dict()
    missing: list[str] = []
    if payload["status"] != V4_GOAL4682_NEXT_TARGET_STATUS:
        missing.append("status")
    if payload["rejected_surface"] != V4_GOAL4682_REJECTED_SURFACE:
        missing.append("rejected_surface")
    if "0.963x" not in str(payload["rejected_reason"]):
        missing.append("goal4681_ratio_record")
    if payload["selected_design_target"] != V4_GOAL4682_SELECTED_DESIGN_TARGET:
        missing.append("selected_design_target")
    if "not merely rewrap V2.14 bounded collect-k" not in str(payload["target_class"]):
        missing.append("v2_14_collect_k_boundary")
    if "before any implementation or POD run" not in str(payload["next_goal"]):
        missing.append("no_impl_no_pod_boundary")
    for key in (
        "pod_authorized",
        "implementation_authorized",
        "release_authorized",
        "promote_rejected_surface_authorized",
        "public_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "app_identity_kernel_authorized",
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
    "V4_GOAL4682_NEXT_TARGET_STATUS",
    "V4_GOAL4682_REJECTED_SURFACE",
    "V4_GOAL4682_SELECTED_DESIGN_TARGET",
    "V4Goal4682NextTargetDecision",
    "v4_goal4682_next_target_after_shape_pair",
    "validate_v4_goal4682_next_target_after_shape_pair",
]
