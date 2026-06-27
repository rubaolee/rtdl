from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4708_APP_VALUE_ROUTE_SELECTION_STATUS = (
    "goal4708_specialized_tier3_app_value_route_selection_no_app_level_claim"
)
V4_GOAL4708_NEXT_GOAL = "Goal4709 formal high-performance V4 app-level target selection outside Tier-3 candidate"


@dataclass(frozen=True)
class V4Goal4708RouteSelection:
    status: str
    selected_app_level_route: str | None
    operator_candidate_route: str
    route_rows: tuple[dict[str, object], ...]
    decision: str
    next_goal: str
    app_level_speed_claim_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "selected_app_level_route": self.selected_app_level_route,
            "operator_candidate_route": self.operator_candidate_route,
            "route_rows": self.route_rows,
            "decision": self.decision,
            "next_goal": self.next_goal,
            "app_level_speed_claim_authorized": self.app_level_speed_claim_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
        }


def v4_goal4708_app_value_route_selection() -> V4Goal4708RouteSelection:
    rows = (
        {
            "target": "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
            "classification": "operator_surface_candidate_value",
            "reason": "Goal4700/4703 prove constrained callback mechanics on weighted-sum route, but this is still an operator surface, not a promoted benchmark app.",
            "app_level_claim_authorized": False,
        },
        {
            "target": "rt_dbscan",
            "classification": "not_bound_to_specialized_tier3_candidate",
            "reason": "RTDBSCAN needs component/grouped-union style continuation, not scalar any-hit weighted-sum callback.",
            "app_level_claim_authorized": False,
        },
        {
            "target": "raydb_style",
            "classification": "not_bound_to_specialized_tier3_candidate",
            "reason": "Current RayDB-style app rows are parity and not solved by the scalar weighted-sum candidate.",
            "app_level_claim_authorized": False,
        },
        {
            "target": "triangle_counting",
            "classification": "not_bound_to_specialized_tier3_candidate",
            "reason": "Triangle counting's app-level win is historical route evolution plus modest V4 increment, not the specialized scalar callback route.",
            "app_level_claim_authorized": False,
        },
        {
            "target": "librts_spatial_index",
            "classification": "not_bound_to_specialized_tier3_candidate",
            "reason": "Spatial-index app rows are parity and do not use scalar any-hit weighted-sum.",
            "app_level_claim_authorized": False,
        },
        {
            "target": "hausdorff_xhd_or_rtnn",
            "classification": "not_bound_to_specialized_tier3_candidate",
            "reason": "Current blockers are exactness/parity for their own routes, not scalar any-hit weighted-sum callback support.",
            "app_level_claim_authorized": False,
        },
    )
    return V4Goal4708RouteSelection(
        status=V4_GOAL4708_APP_VALUE_ROUTE_SELECTION_STATUS,
        selected_app_level_route=None,
        operator_candidate_route="v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
        route_rows=rows,
        decision=(
            "do_not_count_specialized_tier3_candidate_as_app_level_high_performance_evidence; "
            "continue public-support hardening separately and select a real app-level V4 target separately"
        ),
        next_goal=V4_GOAL4708_NEXT_GOAL,
    )


def validate_v4_goal4708_app_value_route_selection() -> dict[str, object]:
    selection = v4_goal4708_app_value_route_selection()
    payload = selection.as_dict()
    missing: list[str] = []
    if payload["selected_app_level_route"] is not None:
        missing.append("selected_app_level_route")
    if "do_not_count" not in str(payload["decision"]):
        missing.append("decision")
    if len(payload["route_rows"]) < 5:
        missing.append("route_rows")
    for row in payload["route_rows"]:
        if row["app_level_claim_authorized"] is not False:
            missing.append(f"{row['target']}_claim")
    for key in ("app_level_speed_claim_authorized", "release_authorized", "performance_claim_authorized"):
        if payload[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "selection": payload,
    }


__all__ = [
    "V4_GOAL4708_APP_VALUE_ROUTE_SELECTION_STATUS",
    "V4_GOAL4708_NEXT_GOAL",
    "V4Goal4708RouteSelection",
    "v4_goal4708_app_value_route_selection",
    "validate_v4_goal4708_app_value_route_selection",
]
