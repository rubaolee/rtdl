from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v4_operator_catalog import plan_v4_operator_request


V4_GOAL4652_APP_ROUTE_BINDING_STATUS = "goal4652_app_route_binding_or_blocker_declaration"

V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE = "v4_fused_operator_addressable"
V4_ROUTE_PARTNER_MIGRATION_OR_PARITY = "partner_migration_or_parity"
V4_ROUTE_BACKEND_BOUND_PARITY_CONTROL = "backend_bound_parity_control"
V4_ROUTE_REQUIRES_NEW_GENERIC_OPERATOR = "requires_new_generic_operator"
V4_ROUTE_REQUIRES_CUPY_PROMOTION = "requires_cupy_promotion"
V4_ROUTE_REQUIRES_FIXED_NUMBA_CONTINUATION = "requires_fixed_numba_continuation"
V4_ROUTE_NO_V4_APP_ROUTE_BLOCKER = "no_v4_app_route_blocker"
V4_ROUTE_DEFERRED_EXCLUDED_WITH_REASON = "deferred_excluded_with_reason"

V4_GOAL4652_ROUTE_CLASSES = (
    V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE,
    V4_ROUTE_PARTNER_MIGRATION_OR_PARITY,
    V4_ROUTE_BACKEND_BOUND_PARITY_CONTROL,
    V4_ROUTE_REQUIRES_NEW_GENERIC_OPERATOR,
    V4_ROUTE_REQUIRES_CUPY_PROMOTION,
    V4_ROUTE_REQUIRES_FIXED_NUMBA_CONTINUATION,
    V4_ROUTE_NO_V4_APP_ROUTE_BLOCKER,
    V4_ROUTE_DEFERRED_EXCLUDED_WITH_REASON,
)

V4_GOAL4652_APP_ORDER = (
    "rt_dbscan",
    "raydb_style",
    "triangle_counting",
    "librts_spatial_index",
    "hausdorff_xhd",
    "robot_collision",
    "contact_manifold",
    "rtnn",
    "spatial_rayjoin",
    "barnes_hut",
)


@dataclass(frozen=True)
class V4PlannerDryRun:
    operator: str
    partner: str
    expected_status: str

    def as_dict(self) -> dict[str, object]:
        plan = plan_v4_operator_request(self.operator, partner=self.partner)
        return {
            "operator": self.operator,
            "partner": self.partner,
            "expected_status": self.expected_status,
            "actual_status": plan.status,
            "status_matches": plan.status == self.expected_status,
            "tier": plan.tier,
            "api_surface": plan.api_surface,
            "generic_primitive": plan.generic_primitive,
            "measured_partner": plan.measured_partner,
            "release_claim_authorized": plan.release_claim_authorized,
            "broad_v4_speedup_claim_authorized": plan.broad_v4_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": plan.whole_app_speedup_claim_authorized,
            "cupy_performance_claim_authorized": plan.cupy_performance_claim_authorized,
            "app_specific_native_kernel_authorized": plan.app_specific_native_kernel_authorized,
        }


@dataclass(frozen=True)
class V4AppRouteBinding:
    app: str
    route_class: str
    route_status: str
    route_actually_uses_v4_code: bool
    full_app_route_bound: bool
    mapped_v4_operators: tuple[str, ...]
    planner_dry_runs: tuple[V4PlannerDryRun, ...]
    blocker_or_gap: str
    next_goal4653_protocol_action: str
    evidence_refs: tuple[str, ...]
    dry_run_possible: bool = True
    release_claim_authorized: bool = False
    broad_v4_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    app_specific_native_kernel_authorized: bool = False

    def __post_init__(self) -> None:
        if self.app not in V4_GOAL4652_APP_ORDER:
            raise ValueError(f"{self.app}: unexpected Goal4652 app")
        if self.route_class not in V4_GOAL4652_ROUTE_CLASSES:
            raise ValueError(f"{self.app}: invalid route class")
        if not self.route_status:
            raise ValueError(f"{self.app}: route status must be explicit")
        if not self.blocker_or_gap:
            raise ValueError(f"{self.app}: blocker/gap must be explicit")
        if not self.next_goal4653_protocol_action:
            raise ValueError(f"{self.app}: Goal4653 protocol action must be explicit")
        if not self.evidence_refs:
            raise ValueError(f"{self.app}: evidence refs must not be empty")
        if self.full_app_route_bound and not self.route_actually_uses_v4_code:
            raise ValueError(f"{self.app}: full route cannot be bound without V4 code")
        if self.route_class == V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE and not self.planner_dry_runs:
            raise ValueError(f"{self.app}: V4-addressable route needs planner dry-runs")
        for flag in (
            "release_claim_authorized",
            "broad_v4_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "app_specific_native_kernel_authorized",
        ):
            if getattr(self, flag):
                raise ValueError(f"{self.app}: {flag} must remain false")

    def as_dict(self) -> dict[str, Any]:
        return {
            "app": self.app,
            "route_class": self.route_class,
            "route_status": self.route_status,
            "route_actually_uses_v4_code": self.route_actually_uses_v4_code,
            "full_app_route_bound": self.full_app_route_bound,
            "mapped_v4_operators": self.mapped_v4_operators,
            "planner_dry_runs": tuple(run.as_dict() for run in self.planner_dry_runs),
            "dry_run_possible": self.dry_run_possible,
            "blocker_or_gap": self.blocker_or_gap,
            "next_goal4653_protocol_action": self.next_goal4653_protocol_action,
            "evidence_refs": self.evidence_refs,
            "release_claim_authorized": self.release_claim_authorized,
            "broad_v4_speedup_claim_authorized": self.broad_v4_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "app_specific_native_kernel_authorized": self.app_specific_native_kernel_authorized,
        }


_ROUTE_BINDINGS = (
    V4AppRouteBinding(
        app="rt_dbscan",
        route_class=V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE,
        route_status="route_bound_to_generic_count_threshold_plus_fixed_numba_component_union",
        route_actually_uses_v4_code=True,
        full_app_route_bound=True,
        mapped_v4_operators=(
            "v4_fixed_radius_count_threshold_2d_device_arrays",
            "v4_fixed_radius_graph_component_union_3d_device_arrays",
        ),
        planner_dry_runs=(
            V4PlannerDryRun("fixed_radius", "torch", "tier2_measured_ready"),
            V4PlannerDryRun("component_union", "numba", "tier2_measured_ready"),
        ),
        blocker_or_gap=(
            "Route is operator-addressable, but this remains operator coverage; "
            "whole-app RTDBSCAN speedup is not authorized before Goal4654/4655."
        ),
        next_goal4653_protocol_action="Freeze RTDBSCAN as a V4 fused-operator-addressable row with correctness parity and app-level timing.",
        evidence_refs=(
            "future/v4/evidence/v4_goal4650_fixed_numba_continuation_certification_2026-06-25.json",
            "src/rtdsl/v4_coverage_audit.py",
        ),
    ),
    V4AppRouteBinding(
        app="raydb_style",
        route_class=V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE,
        route_status="route_bound_to_ray_triangle_grouped_and_any_hit_operator_surfaces",
        route_actually_uses_v4_code=True,
        full_app_route_bound=True,
        mapped_v4_operators=(
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
            "v4_closest_hit_grouped_argmin_3d_device_arrays",
            "v4_ray_triangle_any_hit_flags_2d_device_arrays",
        ),
        planner_dry_runs=(
            V4PlannerDryRun("primitive_grouped_i64", "torch", "tier2_measured_ready"),
            V4PlannerDryRun("grouped_argmin", "torch", "tier2_measured_ready"),
            V4PlannerDryRun("any_hit", "torch", "tier2_measured_ready"),
        ),
        blocker_or_gap="Route is addressable, but app-level V4/V2/V3 result must be measured in the frozen protocol.",
        next_goal4653_protocol_action="Freeze RayDB-style route with grouped-i64, grouped-argmin, and any-hit operator timings.",
        evidence_refs=(
            "future/v4/reviews/goal4617_grouped_i64_completion_review_2026-06-24.raw.md",
            "src/rtdsl/v4_coverage_audit.py",
        ),
    ),
    V4AppRouteBinding(
        app="triangle_counting",
        route_class=V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE,
        route_status="route_bound_to_weighted_sum_plus_grouped_i64_operator_surfaces",
        route_actually_uses_v4_code=True,
        full_app_route_bound=True,
        mapped_v4_operators=(
            "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
        ),
        planner_dry_runs=(
            V4PlannerDryRun("any_hit_weighted_sum", "torch", "tier2_measured_ready"),
            V4PlannerDryRun("primitive_grouped_i64", "torch", "tier2_measured_ready"),
        ),
        blocker_or_gap="Route is addressable after weighted-sum promotion, but whole-app triangle-counting speedup is not authorized.",
        next_goal4653_protocol_action="Freeze triangle-counting route with weighted-sum and grouped-i64 correctness contracts.",
        evidence_refs=(
            "future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.md",
            "src/rtdsl/v4_coverage_audit.py",
        ),
    ),
    V4AppRouteBinding(
        app="librts_spatial_index",
        route_class=V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE,
        route_status="route_bound_to_generic_aabb_all_ops_count_operator",
        route_actually_uses_v4_code=True,
        full_app_route_bound=True,
        mapped_v4_operators=("v4_aabb_index_query_2d_all_ops_count_prepared_runner",),
        planner_dry_runs=(V4PlannerDryRun("aabb_index_query", "rtdl_native", "tier2_measured_ready"),),
        blocker_or_gap=(
            "Route is generic AABB operator coverage, not LibRTS paper reproduction "
            "or broad spatial-index whole-app speedup."
        ),
        next_goal4653_protocol_action="Freeze LibRTS spatial-index as generic AABB all-ops count row with explicit denominator.",
        evidence_refs=(
            "future/v4/v4_goal4637_aabb_frontdoor_catalog_promotion_2026-06-25.md",
            "src/rtdsl/v4_coverage_audit.py",
        ),
    ),
    V4AppRouteBinding(
        app="hausdorff_xhd",
        route_class=V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE,
        route_status="official_v4_route_with_coordinate_normalized_correctness_boundary",
        route_actually_uses_v4_code=True,
        full_app_route_bound=True,
        mapped_v4_operators=(
            "v4_point_group_nearest_witness_2d_device_arrays",
            "v4_fixed_radius_count_threshold_2d_device_arrays",
        ),
        planner_dry_runs=(
            V4PlannerDryRun("point_group_nearest", "torch", "tier2_measured_ready"),
            V4PlannerDryRun("fixed_radius", "torch", "tier2_measured_ready"),
        ),
        blocker_or_gap=(
            "Official V4 Hausdorff route exists through generic point-group "
            "nearest-witness plus Torch or CuPy global argmax. Goal4666 shows "
            "the CuPy official route repairs the 262k hot/prepare failure, but "
            "the focused gate remains mixed because the 65k row stays below bar "
            "and the directed-summary denominator is still parity/slower."
        ),
        next_goal4653_protocol_action=(
            "Freeze as official V4 route with coordinate-normalized correctness "
            "boundary and Goal4666 mixed-result caveat; keep out of all-app "
            "rerun and formal speed-row claims until a focused gate clears."
        ),
        evidence_refs=(
            "future/v4/evidence/v4_goal4659_hausdorff_v4_route_20260625/summary.json",
            "future/v4/v4_goal4659_hausdorff_official_v4_route_evidence_2026-06-25.md",
            "future/v4/evidence/v4_goal4666_hausdorff_cupy_official_20260625/summary.json",
            "future/v4/v4_goal4666_hausdorff_cupy_official_route_evidence_2026-06-25.md",
        ),
    ),
    V4AppRouteBinding(
        app="robot_collision",
        route_class=V4_ROUTE_REQUIRES_NEW_GENERIC_OPERATOR,
        route_status="partial_any_hit_flags_coverage_no_full_collision_route",
        route_actually_uses_v4_code=True,
        full_app_route_bound=False,
        mapped_v4_operators=("v4_ray_triangle_any_hit_flags_2d_device_arrays",),
        planner_dry_runs=(V4PlannerDryRun("any_hit", "torch", "tier2_measured_ready"),),
        blocker_or_gap="Robot collision app planning/setup and grouped segment lowering are not a full V4 route.",
        next_goal4653_protocol_action="Freeze as partial any-hit coverage with blocker for full collision route.",
        evidence_refs=("src/rtdsl/v4_coverage_audit.py",),
    ),
    V4AppRouteBinding(
        app="contact_manifold",
        route_class=V4_ROUTE_REQUIRES_NEW_GENERIC_OPERATOR,
        route_status="partial_nearest_witness_coverage_no_full_contact_route",
        route_actually_uses_v4_code=True,
        full_app_route_bound=False,
        mapped_v4_operators=("v4_point_group_nearest_witness_2d_device_arrays",),
        planner_dry_runs=(V4PlannerDryRun("point_group_nearest", "torch", "tier2_measured_ready"),),
        blocker_or_gap="Contact-manifold bounded witness collection is adjacent to nearest-witness coverage but not a full route.",
        next_goal4653_protocol_action="Freeze as partial nearest-witness coverage with blocker for full contact-manifold route.",
        evidence_refs=("src/rtdsl/v4_coverage_audit.py",),
    ),
    V4AppRouteBinding(
        app="rtnn",
        route_class=V4_ROUTE_REQUIRES_NEW_GENERIC_OPERATOR,
        route_status="deferred_ranked_summary_parity_no_open_candidate",
        route_actually_uses_v4_code=True,
        full_app_route_bound=False,
        mapped_v4_operators=(
            "v4_point_group_nearest_witness_2d_device_arrays",
            "v4_fixed_radius_ranked_summary_3d_prepared_runner",
        ),
        planner_dry_runs=(
            V4PlannerDryRun("point_group_nearest", "torch", "tier2_measured_ready"),
            V4PlannerDryRun(
                "ranked_summary",
                "rtdl_native",
                "deferred_serious_scale_not_v4_0_release_surface",
            ),
        ),
        blocker_or_gap=(
            "RTNN ranked fixed-radius/top-k V4 route executed and validated, "
            "but Goal4660/4661 POD evidence shows hot-path parity or below "
            "parity at serious scales and does not move the app-level bar, so "
            "Goal4678 defers it out of the current candidate front door."
        ),
        next_goal4653_protocol_action=(
            "Freeze as deferred/no-open-candidate route; do not count RTNN as "
            "formal high-performance V4 evidence without a new generic lever."
        ),
        evidence_refs=(
            "future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/summary.json",
            "future/v4/v4_goal4660_4661_rtnn_ranked_summary_candidate_evidence_2026-06-25.md",
        ),
    ),
    V4AppRouteBinding(
        app="spatial_rayjoin",
        route_class=V4_ROUTE_NO_V4_APP_ROUTE_BLOCKER,
        route_status="blocked_no_current_v4_relation_topology_route",
        route_actually_uses_v4_code=False,
        full_app_route_bound=False,
        mapped_v4_operators=(),
        planner_dry_runs=(),
        dry_run_possible=False,
        blocker_or_gap="Spatial relation/topology and repeated PIP routes are not current V4 GPU-array Tier-2 surfaces.",
        next_goal4653_protocol_action="Freeze as no-route blocker; do not silently fall back to V2/V3.",
        evidence_refs=("src/rtdsl/v4_coverage_audit.py",),
    ),
    V4AppRouteBinding(
        app="barnes_hut",
        route_class=V4_ROUTE_DEFERRED_EXCLUDED_WITH_REASON,
        route_status="deferred_app_identity_aggregate_tree_force_law",
        route_actually_uses_v4_code=False,
        full_app_route_bound=False,
        mapped_v4_operators=(),
        planner_dry_runs=(),
        dry_run_possible=False,
        blocker_or_gap="Aggregate-tree weighted vector sum is Barnes-Hut/N-body specific and was rejected for V4.0 generic Tier-2.",
        next_goal4653_protocol_action="Freeze as deferred/excluded with reason; do not add a Barnes-Hut native kernel.",
        evidence_refs=("future/v4/v2_primitives_to_v4_tier2_inventory_2026-06-24.md",),
    ),
)


def v4_goal4652_app_route_bindings() -> tuple[dict[str, Any], ...]:
    return tuple(row.as_dict() for row in _ROUTE_BINDINGS)


def v4_goal4652_route_binding_summary() -> dict[str, Any]:
    rows = v4_goal4652_app_route_bindings()
    by_class = {route_class: 0 for route_class in V4_GOAL4652_ROUTE_CLASSES}
    for row in rows:
        by_class[str(row["route_class"])] += 1
    return {
        "status": V4_GOAL4652_APP_ROUTE_BINDING_STATUS,
        "app_count": len(rows),
        "app_order": V4_GOAL4652_APP_ORDER,
        "by_route_class": by_class,
        "full_app_route_bound_count": sum(1 for row in rows if row["full_app_route_bound"]),
        "partial_or_blocked_count": sum(1 for row in rows if not row["full_app_route_bound"]),
        "route_actually_uses_v4_code_count": sum(1 for row in rows if row["route_actually_uses_v4_code"]),
        "no_silent_fallback_to_v2_or_v3": True,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


def validate_v4_goal4652_app_route_bindings() -> dict[str, Any]:
    rows = v4_goal4652_app_route_bindings()
    apps = tuple(str(row["app"]) for row in rows)
    if apps != V4_GOAL4652_APP_ORDER:
        raise ValueError(f"Goal4652 app order drift: {apps!r}")
    if len(set(apps)) != len(apps):
        raise ValueError("Goal4652 route binding apps must be unique")
    for row in rows:
        if row["route_class"] not in V4_GOAL4652_ROUTE_CLASSES:
            raise ValueError(f"{row['app']}: invalid route class")
        if row["full_app_route_bound"] and not row["route_actually_uses_v4_code"]:
            raise ValueError(f"{row['app']}: bound route does not use V4 code")
        if not row["full_app_route_bound"] and not row["blocker_or_gap"]:
            raise ValueError(f"{row['app']}: unbound route needs blocker/gap")
        for check in row["planner_dry_runs"]:
            if not check["status_matches"]:
                raise ValueError(
                    f"{row['app']}: planner dry-run drift for {check['operator']} / {check['partner']}"
                )
            if check["actual_status"] in {"tier2_measured_ready", "certified_partner_measured_ready"}:
                if not check["api_surface"]:
                    raise ValueError(f"{row['app']}: measured planner route needs api surface")
                if not check["measured_partner"]:
                    raise ValueError(f"{row['app']}: measured planner route needs measured partner")
            for flag in (
                "release_claim_authorized",
                "broad_v4_speedup_claim_authorized",
                "whole_app_speedup_claim_authorized",
                "cupy_performance_claim_authorized",
                "app_specific_native_kernel_authorized",
            ):
                if check[flag]:
                    raise ValueError(f"{row['app']}: planner dry-run authorized {flag}")
        for flag in (
            "release_claim_authorized",
            "broad_v4_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "app_specific_native_kernel_authorized",
        ):
            if row[flag]:
                raise ValueError(f"{row['app']}: row authorized {flag}")
    return v4_goal4652_route_binding_summary()


__all__ = [
    "V4_GOAL4652_APP_ROUTE_BINDING_STATUS",
    "V4_GOAL4652_APP_ORDER",
    "V4_GOAL4652_ROUTE_CLASSES",
    "V4_ROUTE_FUSED_OPERATOR_ADDRESSABLE",
    "V4_ROUTE_PARTNER_MIGRATION_OR_PARITY",
    "V4_ROUTE_BACKEND_BOUND_PARITY_CONTROL",
    "V4_ROUTE_REQUIRES_NEW_GENERIC_OPERATOR",
    "V4_ROUTE_REQUIRES_CUPY_PROMOTION",
    "V4_ROUTE_REQUIRES_FIXED_NUMBA_CONTINUATION",
    "V4_ROUTE_NO_V4_APP_ROUTE_BLOCKER",
    "V4_ROUTE_DEFERRED_EXCLUDED_WITH_REASON",
    "v4_goal4652_app_route_bindings",
    "v4_goal4652_route_binding_summary",
    "validate_v4_goal4652_app_route_bindings",
]
