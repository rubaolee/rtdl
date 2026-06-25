from __future__ import annotations

from dataclasses import dataclass
from typing import Any


V4_GOAL4627_COVERAGE_AUDIT_STATUS = "goal4627_coverage_audit_not_release"

V4_COVERAGE_STRONG_MEASURED = "strong_measured_operator_coverage"
V4_COVERAGE_PARTIAL_MEASURED = "partial_measured_operator_coverage"
V4_COVERAGE_CANDIDATE = "candidate_not_measured_release_coverage"
V4_COVERAGE_DEFERRED = "deferred_or_uncovered_v4_0"

V4_COVERAGE_STATUSES = (
    V4_COVERAGE_STRONG_MEASURED,
    V4_COVERAGE_PARTIAL_MEASURED,
    V4_COVERAGE_CANDIDATE,
    V4_COVERAGE_DEFERRED,
)


@dataclass(frozen=True)
class V4BenchmarkCoverageRow:
    app: str
    coverage_status: str
    mapped_v4_operators: tuple[str, ...]
    continuation_classes: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    release_gap: str
    next_action: str
    recommended_for_goal4628: bool = False
    release_claim_authorized: bool = False
    broad_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    tier3_callback_claim_authorized: bool = False
    app_specific_native_kernel_authorized: bool = False

    def __post_init__(self) -> None:
        if self.coverage_status not in V4_COVERAGE_STATUSES:
            raise ValueError(f"{self.app}: invalid V4 coverage status")
        if not self.app:
            raise ValueError("coverage app name must not be empty")
        if not self.release_gap:
            raise ValueError(f"{self.app}: release gap must be explicit")
        if not self.next_action:
            raise ValueError(f"{self.app}: next action must be explicit")
        if not self.evidence_refs:
            raise ValueError(f"{self.app}: evidence refs must not be empty")
        for flag in (
            "release_claim_authorized",
            "broad_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "tier3_callback_claim_authorized",
            "app_specific_native_kernel_authorized",
        ):
            if getattr(self, flag):
                raise ValueError(f"{self.app}: {flag} must remain false")

    def as_dict(self) -> dict[str, Any]:
        return {
            "app": self.app,
            "coverage_status": self.coverage_status,
            "mapped_v4_operators": self.mapped_v4_operators,
            "continuation_classes": self.continuation_classes,
            "evidence_refs": self.evidence_refs,
            "release_gap": self.release_gap,
            "next_action": self.next_action,
            "recommended_for_goal4628": self.recommended_for_goal4628,
            "release_claim_authorized": self.release_claim_authorized,
            "broad_speedup_claim_authorized": self.broad_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "tier3_callback_claim_authorized": self.tier3_callback_claim_authorized,
            "app_specific_native_kernel_authorized": self.app_specific_native_kernel_authorized,
        }


_COVERAGE_ROWS = (
    V4BenchmarkCoverageRow(
        app="hausdorff_xhd",
        coverage_status=V4_COVERAGE_PARTIAL_MEASURED,
        mapped_v4_operators=(
            "v4_point_group_nearest_witness_2d_device_arrays",
            "v4_fixed_radius_count_threshold_2d_device_arrays",
        ),
        continuation_classes=("nearest_witness", "count_threshold"),
        evidence_refs=(
            "future/v4/reviews/goal4618_completion_consensus_and_review_debt_2026-06-24.md",
            "future/v4/reviews/claude_v4_section8_fixed_radius_wrapper_surface_review_2026-06-24.md",
        ),
        release_gap="Hausdorff app-level directed distance/threshold workflows are not yet a reviewed V4 release scorecard row.",
        next_action="Keep as partial coverage; do not use as the second release gate before a clearer same-contract operator target.",
    ),
    V4BenchmarkCoverageRow(
        app="spatial_rayjoin",
        coverage_status=V4_COVERAGE_DEFERRED,
        mapped_v4_operators=(),
        continuation_classes=("relation_topology", "aabb_prefilter"),
        evidence_refs=("future/v4/v2_primitives_to_v4_tier2_inventory_2026-06-24.md",),
        release_gap="Spatial relation/topology and repeated PIP routes are not current V4 GPU-array Tier-2 surfaces.",
        next_action="Defer to a future generic relation/AABB operator audit; do not use as the second V4 gate.",
    ),
    V4BenchmarkCoverageRow(
        app="rt_dbscan",
        coverage_status=V4_COVERAGE_STRONG_MEASURED,
        mapped_v4_operators=(
            "v4_fixed_radius_count_threshold_2d_device_arrays",
            "v4_fixed_radius_graph_component_union_3d_device_arrays",
        ),
        continuation_classes=("count_threshold", "component_union"),
        evidence_refs=(
            "future/v4/reviews/claude_v4_section8_fixed_radius_wrapper_surface_review_2026-06-24.md",
            "future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/README.md",
        ),
        release_gap=(
            "RTDBSCAN's count-threshold and component-union continuation classes now have measured "
            "generic operator coverage, including Goal4635 Numba-scoped component-union evidence. "
            "This is operator coverage, not whole-app RTDBSCAN release evidence."
        ),
        next_action=(
            "Count as strong measured operator coverage, but keep whole-app RTDBSCAN speedup unauthorized "
            "until the formal release scorecard/all-app gate."
        ),
    ),
    V4BenchmarkCoverageRow(
        app="robot_collision",
        coverage_status=V4_COVERAGE_PARTIAL_MEASURED,
        mapped_v4_operators=("v4_ray_triangle_any_hit_flags_2d_device_arrays",),
        continuation_classes=("any_hit_flag",),
        evidence_refs=("future/v4/evidence/v4_section8_any_hit_flags_device_frontdoor_report_2026-06-24.md",),
        release_gap="Collision app planning/setup and grouped segment lowering are not a full V4 release benchmark row.",
        next_action="Treat any-hit flags as partial generic coverage; do not claim whole-app collision acceleration.",
    ),
    V4BenchmarkCoverageRow(
        app="contact_manifold",
        coverage_status=V4_COVERAGE_PARTIAL_MEASURED,
        mapped_v4_operators=("v4_point_group_nearest_witness_2d_device_arrays",),
        continuation_classes=("nearest_witness",),
        evidence_refs=("future/v4/reviews/goal4618_completion_consensus_and_review_debt_2026-06-24.md",),
        release_gap="Bounded witness collection is adjacent to nearest-witness coverage but not a reviewed contact-manifold V4 gate.",
        next_action="Keep as partial nearest-witness coverage.",
    ),
    V4BenchmarkCoverageRow(
        app="raydb_style",
        coverage_status=V4_COVERAGE_STRONG_MEASURED,
        mapped_v4_operators=(
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
            "v4_closest_hit_grouped_argmin_3d_device_arrays",
            "v4_ray_triangle_any_hit_flags_2d_device_arrays",
        ),
        continuation_classes=("grouped_i64_reduction", "argmin", "any_hit_flag"),
        evidence_refs=(
            "future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.md",
            "future/v4/reviews/claude_v4_goal4617_grouped_i64_promotion_decision_review_2026-06-24.raw.md",
        ),
        release_gap="Needs Goal4628 scorecard reconciliation as the second non-fixed-radius same-contract gate.",
        next_action="Use grouped-i64 as the recommended Goal4628 second Tier-2 same-contract gate.",
        recommended_for_goal4628=True,
    ),
    V4BenchmarkCoverageRow(
        app="barnes_hut",
        coverage_status=V4_COVERAGE_DEFERRED,
        mapped_v4_operators=(),
        continuation_classes=("aggregate_tree_weighted_vector_sum",),
        evidence_refs=("future/v4/v2_primitives_to_v4_tier2_inventory_2026-06-24.md",),
        release_gap="Aggregate-tree weighted vector sum was rejected for V4.0 because it is Barnes-Hut/N-body specific rather than a generic RT-core operator.",
        next_action="Keep deferred; do not use Barnes-Hut as a V4.0 Tier-2 release gate.",
    ),
    V4BenchmarkCoverageRow(
        app="librts_spatial_index",
        coverage_status=V4_COVERAGE_STRONG_MEASURED,
        mapped_v4_operators=("v4_aabb_index_query_2d_all_ops_count_prepared_runner",),
        continuation_classes=("aabb_index_query",),
        evidence_refs=(
            "future/v4/evidence/v4_goal4636c_aabb_index_all_ops_pod_gate_2026-06-25/m30_all_ops.json",
            "future/v4/v4_goal4636c_aabb_index_pod_gate_decision_2026-06-25.md",
        ),
        release_gap=(
            "LibRTS spatial-index now maps to measured generic AABB all-ops operator coverage. "
            "This is not a LibRTS paper reproduction, authors-code comparison, or whole-app speedup claim."
        ),
        next_action=(
            "Count as strong generic operator coverage after Goal4637 front-door/catalog promotion, "
            "but keep LibRTS paper and whole-app speedup wording unauthorized until a formal release scorecard."
        ),
    ),
    V4BenchmarkCoverageRow(
        app="rtnn",
        coverage_status=V4_COVERAGE_PARTIAL_MEASURED,
        mapped_v4_operators=("v4_point_group_nearest_witness_2d_device_arrays",),
        continuation_classes=("nearest_witness", "ranked_summary_topk"),
        evidence_refs=("future/v4/reviews/goal4618_completion_consensus_and_review_debt_2026-06-24.md",),
        release_gap="RTNN ranked fixed-radius/top-k 3D summaries are not current V4 measured surfaces.",
        next_action="Keep nearest-witness as partial coverage; ranked/top-k remains deferred.",
    ),
    V4BenchmarkCoverageRow(
        app="triangle_counting",
        coverage_status=V4_COVERAGE_STRONG_MEASURED,
        mapped_v4_operators=(
            "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
        ),
        continuation_classes=("any_hit_weighted_sum", "grouped_i64_reduction"),
        evidence_refs=(
            "future/v4/reviews/goal4620_completion_consensus_and_review_debt_2026-06-24.md",
            "future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.md",
            "future/v4/reviews/goal4633_completion_consensus_and_review_debt_2026-06-25.md",
        ),
        release_gap=(
            "Triangle counting's dominant any-hit weighted/count continuation path now has a measured "
            "Torch CUDA weighted-sum operator after Goal4633. This is operator coverage, not whole-app "
            "triangle-counting release evidence."
        ),
        next_action=(
            "Count as strong measured operator coverage for Torch CUDA, but keep whole-app triangle-counting "
            "speedup unauthorized until the formal release scorecard/all-app gate."
        ),
    ),
)


def v4_goal4627_coverage_rows() -> tuple[V4BenchmarkCoverageRow, ...]:
    return _COVERAGE_ROWS


def v4_goal4627_coverage_summary() -> dict[str, Any]:
    rows = v4_goal4627_coverage_rows()
    by_status = {status: 0 for status in V4_COVERAGE_STATUSES}
    for row in rows:
        by_status[row.coverage_status] += 1
    recommended = tuple(row.app for row in rows if row.recommended_for_goal4628)
    return {
        "status": V4_GOAL4627_COVERAGE_AUDIT_STATUS,
        "row_count": len(rows),
        "by_status": by_status,
        "recommended_goal4628_apps": recommended,
        "recommended_goal4628_operator": "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
        "fixed_radius_wrapper_prerequisite": "external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive",
        "latest_refresh_goal": "Goal4637_after_aabb_index_frontdoor_catalog",
        "release_claim_authorized": False,
        "broad_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


def validate_v4_goal4627_coverage_audit() -> dict[str, Any]:
    rows = v4_goal4627_coverage_rows()
    app_names = tuple(row.app for row in rows)
    expected = (
        "hausdorff_xhd",
        "spatial_rayjoin",
        "rt_dbscan",
        "robot_collision",
        "contact_manifold",
        "raydb_style",
        "barnes_hut",
        "librts_spatial_index",
        "rtnn",
        "triangle_counting",
    )
    if app_names != expected:
        raise ValueError(f"unexpected V4 coverage app order: {app_names!r}")
    summary = v4_goal4627_coverage_summary()
    if summary["row_count"] != 10:
        raise ValueError("V4 coverage audit must cover the 10 promoted benchmark apps")
    if summary["recommended_goal4628_apps"] != ("raydb_style",):
        raise ValueError("Goal4628 recommendation must be exactly raydb_style/grouped-i64")
    if summary["by_status"][V4_COVERAGE_DEFERRED] < 1:
        raise ValueError("coverage audit must keep uncovered/deferred rows visible")
    return summary


__all__ = [
    "V4_GOAL4627_COVERAGE_AUDIT_STATUS",
    "V4_COVERAGE_STRONG_MEASURED",
    "V4_COVERAGE_PARTIAL_MEASURED",
    "V4_COVERAGE_CANDIDATE",
    "V4_COVERAGE_DEFERRED",
    "V4_COVERAGE_STATUSES",
    "V4BenchmarkCoverageRow",
    "v4_goal4627_coverage_rows",
    "v4_goal4627_coverage_summary",
    "validate_v4_goal4627_coverage_audit",
]
