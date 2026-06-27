from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4712_NEXT_LEVER_STATUS = (
    "goal4712_next_lever_after_custom_scored_failure_selected_protocol_required"
)
V4_GOAL4712_SELECTED_TARGET = "custom_predicate_early_exit_multi_hit"
V4_GOAL4712_NEXT_GOAL = "Goal4713 custom predicate early-exit multi-hit protocol freeze"


@dataclass(frozen=True)
class V4Goal4712NextLever:
    status: str
    selected_target: str
    failure_fact: dict[str, object]
    rejected_patterns: tuple[dict[str, object], ...]
    selected_target_contract: dict[str, object]
    next_goal: str
    pod_authorized: bool = False
    release_authorized: bool = False
    formal_high_performance_authorized: bool = False
    app_level_speed_claim_authorized: bool = False
    arbitrary_callback_authorized: bool = False
    raw_optix_callback_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "selected_target": self.selected_target,
            "failure_fact": self.failure_fact,
            "rejected_patterns": self.rejected_patterns,
            "selected_target_contract": self.selected_target_contract,
            "next_goal": self.next_goal,
            "pod_authorized": self.pod_authorized,
            "release_authorized": self.release_authorized,
            "formal_high_performance_authorized": self.formal_high_performance_authorized,
            "app_level_speed_claim_authorized": self.app_level_speed_claim_authorized,
            "arbitrary_callback_authorized": self.arbitrary_callback_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
        }


def v4_goal4712_next_lever_after_custom_scored_failure() -> V4Goal4712NextLever:
    failure_fact = {
        "source_goal": "Goal4711",
        "failed_target": "ray_triangle_custom_scored_accumulation",
        "classification": "fail_focused_app_gate_not_high_performance",
        "primary_geomean_v3_speedup": 1.0289410940907995,
        "min_primary_v3_speedup": 1.0144917291107025,
        "reason": (
            "Post-hit scalar scoring only removes a small amount of materialization or callback-placement cost. "
            "It does not reduce traversal work, candidate count, or high-volume hit attribute movement enough to "
            "support formal high-performance V4."
        ),
    }
    rejected_patterns = (
        {
            "pattern": "post_hit_scalar_accumulation_polish",
            "reason": "Goal4711 already measured this shape at about 1.029x geomean; more wording or minor polish is not a new lever.",
        },
        {
            "pattern": "weighted_sum_or_existing_operator_control",
            "reason": "Weighted sum exists in V2/V3 and is control-only, not V4-specific app evidence.",
        },
        {
            "pattern": "global_atomic_scalar_accumulation",
            "reason": "Goal4711 smoke showed global atomic accumulation is a diagnostic control, not a performance route.",
        },
        {
            "pattern": "same_target_rerun_without_changed_cost_model",
            "reason": "Rerunning the same custom-scored app cannot move the frozen bar unless the mechanism changes.",
        },
    )
    selected_contract = {
        "generic_feature_under_test": "constrained custom predicate callback in any-hit with RTDL-owned early-exit policy",
        "why_this_can_win": (
            "Unlike post-hit accumulation, a predicate callback can affect traversal-side control flow. "
            "V4 can reject or terminate inside any-hit before materializing every candidate, while V2/V3 fallback "
            "must materialize all hit IDs or hit attributes and then run a separate device predicate/filter."
        ),
        "app_family": "ray/triangle multi-hit custom predicate early-exit",
        "not_app_specific_kernel": True,
        "allowed_callback_shape": "pure scalar/boolean Numba C-ABI device function with no side effects",
        "engine_owned_action": "RTDL applies terminate_on_first_accept or count_until_threshold; user callback does not mutate external state",
        "required_scene_shape": (
            "multi-hit rays with frozen candidate densities, e.g. >=8 and >=32 possible hits per ray, "
            "plus sparse/no-hit controls"
        ),
        "v2_v3_denominator": (
            "same OptiX hit discovery with device materialization of all candidate IDs/attributes, followed by "
            "separate device predicate/filter/reduction"
        ),
        "v4_route": "callback predicate evaluated inside any-hit with early termination/filtering controlled by RTDL",
        "must_freeze_before_pod": (
            "correctness oracle, candidate density, scales, callback variants, V2/V3 fallback, numeric bars, "
            "kill conditions, and public-claim boundaries"
        ),
        "minimum_bar_to_consider_formal_hp": (
            "Goal4713 must freeze numeric bars; expected bar should require material speedup in high-candidate regimes, "
            "not a 1.03x polish win"
        ),
    }
    return V4Goal4712NextLever(
        status=V4_GOAL4712_NEXT_LEVER_STATUS,
        selected_target=V4_GOAL4712_SELECTED_TARGET,
        failure_fact=failure_fact,
        rejected_patterns=rejected_patterns,
        selected_target_contract=selected_contract,
        next_goal=V4_GOAL4712_NEXT_GOAL,
    )


def validate_v4_goal4712_next_lever_after_custom_scored_failure() -> dict[str, object]:
    payload = v4_goal4712_next_lever_after_custom_scored_failure().as_dict()
    missing: list[str] = []
    if payload["selected_target"] != V4_GOAL4712_SELECTED_TARGET:
        missing.append("selected_target")
    if payload["failure_fact"].get("classification") != "fail_focused_app_gate_not_high_performance":
        missing.append("failure_fact")
    if float(payload["failure_fact"].get("primary_geomean_v3_speedup", 0.0)) >= 1.20:
        missing.append("failure_geomean")
    rejected_names = {str(row["pattern"]) for row in payload["rejected_patterns"]}
    for name in ("post_hit_scalar_accumulation_polish", "weighted_sum_or_existing_operator_control", "global_atomic_scalar_accumulation"):
        if name not in rejected_names:
            missing.append(name)
    contract = payload["selected_target_contract"]
    if "early-exit" not in str(contract.get("generic_feature_under_test")):
        missing.append("early_exit_feature")
    if contract.get("not_app_specific_kernel") is not True:
        missing.append("app_specific_kernel")
    if "materialize all" not in str(contract.get("why_this_can_win")):
        missing.append("cost_model")
    if payload["pod_authorized"] is not False:
        missing.append("pod_authorized")
    for key in (
        "release_authorized",
        "formal_high_performance_authorized",
        "app_level_speed_claim_authorized",
        "arbitrary_callback_authorized",
        "raw_optix_callback_authorized",
    ):
        if payload[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "selection": payload,
    }


__all__ = [
    "V4_GOAL4712_NEXT_LEVER_STATUS",
    "V4_GOAL4712_SELECTED_TARGET",
    "V4_GOAL4712_NEXT_GOAL",
    "V4Goal4712NextLever",
    "v4_goal4712_next_lever_after_custom_scored_failure",
    "validate_v4_goal4712_next_lever_after_custom_scored_failure",
]
