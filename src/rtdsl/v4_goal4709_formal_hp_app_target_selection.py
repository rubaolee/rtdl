from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4709_FORMAL_HP_APP_TARGET_SELECTION_STATUS = (
    "goal4709_formal_high_performance_app_target_selected_protocol_required"
)
V4_GOAL4709_SELECTED_APP = "ray_triangle_custom_scored_accumulation"
V4_GOAL4709_NEXT_GOAL = "Goal4710 ray-triangle custom scored accumulation app-level protocol freeze"


@dataclass(frozen=True)
class V4Goal4709TargetSelection:
    status: str
    selected_app: str
    rejected_existing_targets: tuple[dict[str, object], ...]
    selected_target_contract: dict[str, object]
    next_goal: str
    pod_authorized: bool = False
    app_level_speed_claim_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "selected_app": self.selected_app,
            "rejected_existing_targets": self.rejected_existing_targets,
            "selected_target_contract": self.selected_target_contract,
            "next_goal": self.next_goal,
            "pod_authorized": self.pod_authorized,
            "app_level_speed_claim_authorized": self.app_level_speed_claim_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
        }


def v4_goal4709_formal_hp_app_target_selection() -> V4Goal4709TargetSelection:
    rejected = (
        {
            "target": "rt_dbscan",
            "reason": "Goal4670/4671 found modest/no-go second-win evidence; component union is not solved by scalar callback fusion.",
        },
        {
            "target": "raydb_style",
            "reason": "Goal4655 app row is parity; no clean new V4 runtime lever identified.",
        },
        {
            "target": "triangle_counting",
            "reason": "Large V2.14 ratio is historical route evolution; V4-over-V3 increment is modest and not a clean new V4 feature proof.",
        },
        {
            "target": "librts_spatial_index",
            "reason": "Goal4655 app row is parity; no current V4 lever moves it.",
        },
        {
            "target": "hausdorff_xhd",
            "reason": "Current blocker is correctness/normalization, not proven V4 performance.",
        },
        {
            "target": "rtnn",
            "reason": "Ranked-summary/top-k candidate was deferred for serious-scale parity or below-parity rows.",
        },
    )
    contract = {
        "app_family": "ray/triangle custom scored accumulation",
        "why_v4_specific": (
            "The app requires user-defined scalar scoring/reduction inside the RT hit path. "
            "V2/V3 baselines must materialize hits or use fixed built-in reductions; V4 candidate fuses "
            "a constrained Numba C-ABI scalar callback into the RTDL-generated OptiX hit program."
        ),
        "not_app_specific_kernel": True,
        "generic_feature_under_test": "specialized Tier-3 scalar callback fusion for ray/triangle hit reduction",
        "required_baselines": (
            "V2.14 strongest materialized-hit or built-in fixed-reduction route",
            "V3.0.2 strongest current route",
            "V4 Tier-2 built-in route where semantically comparable",
        ),
        "minimum_scale": ">=262144 rays with dense and sparse hit regimes; larger row optional if POD budget allows",
        "required_callbacks": (
            "weighted_sum",
            "affine_score",
            "threshold_score",
            "minmax_score",
        ),
        "pass_condition_to_freeze_in_goal4710": (
            "Goal4710 must freeze numeric bars before POD. No all-app or release claim is allowed from Goal4709."
        ),
    }
    return V4Goal4709TargetSelection(
        status=V4_GOAL4709_FORMAL_HP_APP_TARGET_SELECTION_STATUS,
        selected_app=V4_GOAL4709_SELECTED_APP,
        rejected_existing_targets=rejected,
        selected_target_contract=contract,
        next_goal=V4_GOAL4709_NEXT_GOAL,
    )


def validate_v4_goal4709_formal_hp_app_target_selection() -> dict[str, object]:
    selection = v4_goal4709_formal_hp_app_target_selection()
    payload = selection.as_dict()
    contract = payload["selected_target_contract"]
    missing: list[str] = []
    if payload["selected_app"] != V4_GOAL4709_SELECTED_APP:
        missing.append("selected_app")
    if len(payload["rejected_existing_targets"]) < 5:
        missing.append("rejected_existing_targets")
    if contract.get("not_app_specific_kernel") is not True:
        missing.append("not_app_specific_kernel")
    if "callback fusion" not in str(contract.get("generic_feature_under_test")):
        missing.append("generic_feature")
    if "V2.14" not in " ".join(contract.get("required_baselines", ())):
        missing.append("v2_baseline")
    if "V3.0.2" not in " ".join(contract.get("required_baselines", ())):
        missing.append("v3_baseline")
    for key in ("pod_authorized", "app_level_speed_claim_authorized", "release_authorized", "performance_claim_authorized"):
        if payload[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "selection": payload,
    }


__all__ = [
    "V4_GOAL4709_FORMAL_HP_APP_TARGET_SELECTION_STATUS",
    "V4_GOAL4709_SELECTED_APP",
    "V4_GOAL4709_NEXT_GOAL",
    "V4Goal4709TargetSelection",
    "v4_goal4709_formal_hp_app_target_selection",
    "validate_v4_goal4709_formal_hp_app_target_selection",
]
