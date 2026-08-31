from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping


class SemanticCapability(str, Enum):
    ONE_FIXED_OUTPUT_RECORD_PER_LAUNCH = "one_fixed_output_record_per_launch"
    CUSTOM_AABB_TRAVERSAL = "custom_aabb_traversal"
    BUILTIN_TRIANGLE_TRAVERSAL = "builtin_triangle_traversal"
    ORDER_INDEPENDENT_PAYLOAD = "order_independent_payload"
    BOUNDED_MULTI_ROUND_TOPK = "bounded_multi_round_topk"
    BOUNDED_VARIABLE_ROW_EMIT = "bounded_variable_row_emit"
    CROSS_LAUNCH_GLOBAL_ARGMAX_WITNESS = "cross_launch_global_argmax_witness"
    RADIUS_GRAPH_COMPONENT_CLOSURE = "radius_graph_component_closure"
    EXACT_SCALED_INTEGER_SOS = "exact_scaled_integer_simulation_of_simplicity"
    GROUPED_I64X2_CHECKED_REDUCTION = "grouped_i64x2_checked_reduction"
    GROUPED_EXACT_SEGMENT_PAIR_COUNT = "grouped_exact_segment_pair_count"
    MULTI_STAGE_HIERARCHY_FRONTIER = "multi_stage_hierarchy_frontier"
    GENERIC_TRIANGLE_METADATA = "generic_triangle_metadata"
    CHECKED_CROSS_RAY_U64_REDUCTION = "checked_cross_ray_u64_reduction"


@dataclass(frozen=True)
class LaneSemanticRequirement:
    required: frozenset[SemanticCapability]
    stable_fail_code: str


class LaneSemanticCoverageError(ValueError):
    def __init__(self, code: str, missing: tuple[str, ...]) -> None:
        self.code = code
        self.missing = missing
        super().__init__(f"Goal5757 canonical lane coverage rejected: {code}: missing={missing!r}")


LANE_REQUIREMENTS: Mapping[str, LaneSemanticRequirement] = {
    "point_selection.spatial_bounded.v1": LaneSemanticRequirement(
        frozenset({SemanticCapability.CUSTOM_AABB_TRAVERSAL, SemanticCapability.BOUNDED_MULTI_ROUND_TOPK}),
        "canonical_plan_missing_bounded_multi_round_topk",
    ),
    "aabb_index.prepared_query_2d.v1": LaneSemanticRequirement(
        frozenset({SemanticCapability.CUSTOM_AABB_TRAVERSAL, SemanticCapability.BOUNDED_VARIABLE_ROW_EMIT}),
        "canonical_plan_missing_bounded_candidate_rows",
    ),
    "aabb_overlap.filter_bounded_emit_2d.v1": LaneSemanticRequirement(
        frozenset({SemanticCapability.CUSTOM_AABB_TRAVERSAL, SemanticCapability.BOUNDED_VARIABLE_ROW_EMIT}),
        "canonical_plan_missing_bounded_pair_emit",
    ),
    "nearest_state.cell_mbr_exact_witness.v1": LaneSemanticRequirement(
        frozenset({SemanticCapability.CUSTOM_AABB_TRAVERSAL, SemanticCapability.CROSS_LAUNCH_GLOBAL_ARGMAX_WITNESS}),
        "canonical_plan_missing_global_argmax_witness",
    ),
    "fixed_radius.prepared_spatial_components.v1": LaneSemanticRequirement(
        frozenset({SemanticCapability.CUSTOM_AABB_TRAVERSAL, SemanticCapability.RADIUS_GRAPH_COMPONENT_CLOSURE}),
        "canonical_plan_missing_radius_graph_components",
    ),
    "planar_map.directed_segment_point_location_2d.v1": LaneSemanticRequirement(
        frozenset({SemanticCapability.CUSTOM_AABB_TRAVERSAL, SemanticCapability.EXACT_SCALED_INTEGER_SOS}),
        "canonical_plan_missing_exact_sos_point_location",
    ),
    "planar_map.segment_pair_grouped_range_exact_count_2d.v1": LaneSemanticRequirement(
        frozenset({SemanticCapability.CUSTOM_AABB_TRAVERSAL, SemanticCapability.GROUPED_EXACT_SEGMENT_PAIR_COUNT}),
        "canonical_plan_missing_grouped_exact_segment_pairs",
    ),
}


def fragment_capabilities(*, geometry_family: str, has_any_hit: bool) -> frozenset[SemanticCapability]:
    result = {SemanticCapability.ONE_FIXED_OUTPUT_RECORD_PER_LAUNCH}
    if geometry_family == "custom_aabb":
        result.add(SemanticCapability.CUSTOM_AABB_TRAVERSAL)
    elif geometry_family == "builtin_triangle":
        result.add(SemanticCapability.BUILTIN_TRIANGLE_TRAVERSAL)
    if has_any_hit:
        result.add(SemanticCapability.ORDER_INDEPENDENT_PAYLOAD)
    return frozenset(result)


def require_complete_lane(lane_id: str, observed: Iterable[SemanticCapability]) -> None:
    requirement = LANE_REQUIREMENTS[lane_id]
    present = frozenset(observed)
    missing = tuple(sorted(item.value for item in requirement.required - present))
    if missing:
        raise LaneSemanticCoverageError(requirement.stable_fail_code, missing)


__all__ = [
    "LANE_REQUIREMENTS",
    "LaneSemanticCoverageError",
    "LaneSemanticRequirement",
    "SemanticCapability",
    "fragment_capabilities",
    "require_complete_lane",
]
