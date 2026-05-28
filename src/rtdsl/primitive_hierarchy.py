from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


PRIMITIVE_HIERARCHY_VERSION = "rtdl.primitive_hierarchy.v1"

PRIMITIVE_HIERARCHY_LAYER_ORDER = (
    "execution_residency",
    "traversal",
    "row_emission",
    "bounded_materialization",
    "reduction",
    "continuation",
    "candidate_experimental",
)

PRIMITIVE_HIERARCHY_STATUSES = (
    "stable_primitive",
    "stable_behavior",
    "stable_compatibility_path",
    "internal_substrate",
    "internal_generic_path",
    "candidate_behavior",
    "app_or_partner_code",
)

APP_OWNED_BOUNDARY_EXCLUSIONS = (
    "DBSCAN cluster expansion",
    "robot pose/link sampling",
    "contact manifold interpretation",
    "collision/contact physics semantics",
    "Barnes-Hut inverse-square force law",
    "SQL/DBMS query semantics",
    "RTNN ANN policy semantics",
    "RayJoin paper-system reproduction semantics",
    "triangle-counting graph meaning beyond emitted row contracts",
)


@dataclass(frozen=True)
class PrimitiveHierarchyNode:
    """A behavior-first primitive node in the RTDL hierarchy."""

    id: str
    title: str
    layer: str
    status: str
    summary: str
    outputs: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    children: tuple["PrimitiveHierarchyNode", ...] = ()
    boundary: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "layer": self.layer,
            "status": self.status,
            "summary": self.summary,
            "outputs": self.outputs,
            "depends_on": self.depends_on,
            "children": tuple(child.to_dict() for child in self.children),
            "boundary": self.boundary,
        }


PRIMITIVE_HIERARCHY = (
    PrimitiveHierarchyNode(
        id="layer.execution_residency",
        title="Execution / Residency Layer",
        layer="execution_residency",
        status="stable_behavior",
        summary="Owns prepared runtime state, buffer descriptors, residency, and capacity contracts.",
        children=(
            PrimitiveHierarchyNode(
                id="execution.prepared_rt_state",
                title="Prepared RT State",
                layer="execution_residency",
                status="stable_behavior",
                summary="Reusable prepared Embree/OptiX scenes, indexes, and query-side state.",
                outputs=("prepared_handle", "lifetime_metadata"),
            ),
            PrimitiveHierarchyNode(
                id="execution.buffer_descriptors",
                title="Buffer Descriptors",
                layer="execution_residency",
                status="internal_substrate",
                summary="Typed host/device buffers and result-buffer descriptors.",
                outputs=("typed_buffer_descriptor", "result_buffer_descriptor"),
            ),
            PrimitiveHierarchyNode(
                id="execution.partner_resident_handoff",
                title="Partner-Resident Handoff",
                layer="execution_residency",
                status="internal_substrate",
                summary="Describes user/partner-owned device columns handed to RTDL without changing app ownership.",
                outputs=("partner_column_descriptor", "device_pointer_handoff"),
            ),
            PrimitiveHierarchyNode(
                id="execution.capacity_overflow_contract",
                title="Capacity / Overflow Contract",
                layer="execution_residency",
                status="stable_behavior",
                summary="Shared capacity accounting and fail-closed overflow behavior for exact outputs.",
                outputs=("capacity", "overflowed", "complete_candidate_coverage"),
            ),
        ),
    ),
    PrimitiveHierarchyNode(
        id="layer.traversal",
        title="Traversal Layer",
        layer="traversal",
        status="stable_behavior",
        summary="Owns app-independent RT predicate traversal against prepared or query geometry.",
        depends_on=("execution.prepared_rt_state",),
        children=(
            PrimitiveHierarchyNode(
                id="traversal.any_hit",
                title="ANY_HIT",
                layer="traversal",
                status="stable_primitive",
                summary="Existence of at least one hit between query geometry and prepared/build geometry.",
                outputs=("hit_flag",),
                depends_on=("execution.prepared_rt_state",),
            ),
            PrimitiveHierarchyNode(
                id="traversal.closest_hit",
                title="CLOSEST_HIT / First-Hit-Like Paths",
                layer="traversal",
                status="internal_substrate",
                summary="Closest or first accepted hit where the contract needs one representative primitive.",
                outputs=("hit_flag", "hit_id", "hit_distance"),
                depends_on=("execution.prepared_rt_state",),
            ),
            PrimitiveHierarchyNode(
                id="traversal.count_hits",
                title="COUNT_HITS",
                layer="traversal",
                status="stable_primitive",
                summary="Count positive hit results without materializing full witness rows.",
                outputs=("hit_count",),
                depends_on=("traversal.any_hit",),
            ),
            PrimitiveHierarchyNode(
                id="traversal.aabb_index_query_2d",
                title="AABB_INDEX_QUERY_2D Predicates",
                layer="traversal",
                status="internal_generic_path",
                summary="Prepared 2-D AABB point/range predicate queries.",
                outputs=("predicate_count", "predicate_flag"),
                depends_on=("execution.prepared_rt_state",),
                children=(
                    PrimitiveHierarchyNode(
                        id="traversal.aabb_point_contains",
                        title="point_contains",
                        layer="traversal",
                        status="internal_generic_path",
                        summary="Indexed AABB contains query point.",
                        outputs=("count",),
                        depends_on=("traversal.aabb_index_query_2d",),
                    ),
                    PrimitiveHierarchyNode(
                        id="traversal.aabb_range_contains",
                        title="range_contains",
                        layer="traversal",
                        status="internal_generic_path",
                        summary="Indexed AABB contains query AABB.",
                        outputs=("count",),
                        depends_on=("traversal.aabb_index_query_2d",),
                    ),
                    PrimitiveHierarchyNode(
                        id="traversal.aabb_range_intersects",
                        title="range_intersects",
                        layer="traversal",
                        status="internal_generic_path",
                        summary="Indexed AABB intersects query AABB.",
                        outputs=("count",),
                        depends_on=("traversal.aabb_index_query_2d",),
                    ),
                ),
            ),
            PrimitiveHierarchyNode(
                id="traversal.fixed_radius_count_threshold",
                title="FIXED_RADIUS_COUNT_THRESHOLD",
                layer="traversal",
                status="stable_primitive",
                summary="Count nearby points within a radius and optionally return threshold/core flags.",
                outputs=("count", "threshold_reached"),
                depends_on=("execution.prepared_rt_state",),
            ),
        ),
    ),
    PrimitiveHierarchyNode(
        id="layer.row_emission",
        title="Row Emission Layer",
        layer="row_emission",
        status="internal_substrate",
        summary="Owns exact or candidate row emission before bounded materialization or reduction.",
        depends_on=("layer.traversal", "execution.capacity_overflow_contract"),
        children=(
            PrimitiveHierarchyNode(
                id="rows.generic_candidate_rows",
                title="Generic Candidate / Witness Rows",
                layer="row_emission",
                status="internal_substrate",
                summary="App-independent row streams that carry IDs, not domain meaning.",
                outputs=("row_stream",),
                depends_on=("layer.traversal",),
            ),
            PrimitiveHierarchyNode(
                id="rows.aabb_range_intersection_rows",
                title="AABB range_intersection_rows",
                layer="row_emission",
                status="internal_generic_path",
                summary="Emit generic (query_id, indexed_id) rows for 2-D AABB intersections.",
                outputs=("query_id", "indexed_id"),
                depends_on=("traversal.aabb_range_intersects", "execution.capacity_overflow_contract"),
                boundary="Exact app refinement remains outside this primitive.",
            ),
            PrimitiveHierarchyNode(
                id="rows.expanded_aabb_point_membership_rows",
                title="EXPANDED_AABB_POINT_MEMBERSHIP_2D",
                layer="row_emission",
                status="candidate_behavior",
                summary="Emit generic bounded rows for points contained by caller-expanded 2-D AABBs.",
                outputs=("source_id", "box_id", "metadata_flags", "row_offsets"),
                depends_on=("traversal.aabb_point_contains", "execution.capacity_overflow_contract"),
                boundary="Box expansion and row interpretation are caller-owned; native code emits app-free IDs only.",
            ),
            PrimitiveHierarchyNode(
                id="rows.segment_polygon_rows",
                title="Segment / Polygon Rows",
                layer="row_emission",
                status="internal_substrate",
                summary="Generic segment/polygon witness rows used by spatial workloads.",
                outputs=("segment_id", "polygon_id"),
                depends_on=("traversal.any_hit",),
            ),
            PrimitiveHierarchyNode(
                id="rows.fixed_radius_neighbor_rows",
                title="Fixed-Radius Neighbor Rows",
                layer="row_emission",
                status="internal_substrate",
                summary="Neighbor candidate rows emitted by fixed-radius search paths.",
                outputs=("query_id", "neighbor_id", "distance"),
                depends_on=("traversal.fixed_radius_count_threshold",),
            ),
            PrimitiveHierarchyNode(
                id="rows.aggregate_frontier_collect",
                title="Aggregate-Frontier Collect Rows",
                layer="row_emission",
                status="candidate_behavior",
                summary=(
                    "Emit app-independent aggregate-frontier IDs, kind codes, "
                    "and source offsets from prepared aggregate-tree traversal."
                ),
                outputs=(
                    "source_id",
                    "frontier_kind_code",
                    "item_id",
                    "owner_aggregate_id",
                    "dfs_index",
                    "resume_index",
                    "metadata_flags",
                    "row_offsets",
                ),
                depends_on=("rows.generic_candidate_rows", "execution.capacity_overflow_contract"),
                boundary="Force laws, scores, and app-owned reductions remain app or partner code.",
            ),
            PrimitiveHierarchyNode(
                id="rows.graph_triangle_witness_rows",
                title="Graph / Triangle Witness Rows",
                layer="row_emission",
                status="internal_substrate",
                summary="Generic row shapes used by graph-like and triangle-witness examples.",
                outputs=("left_id", "right_id", "witness_id"),
                depends_on=("rows.generic_candidate_rows",),
                boundary="Graph interpretation remains app code.",
            ),
        ),
    ),
    PrimitiveHierarchyNode(
        id="layer.bounded_materialization",
        title="Bounded Materialization Layer",
        layer="bounded_materialization",
        status="stable_behavior",
        summary="Owns bounded exact output materialization and row-schema validation.",
        depends_on=("rows.generic_candidate_rows", "execution.capacity_overflow_contract"),
        children=(
            PrimitiveHierarchyNode(
                id="materialization.collect_k_bounded",
                title="COLLECT_K_BOUNDED",
                layer="bounded_materialization",
                status="stable_primitive",
                summary="Collect up to K rows with exact fail-closed overflow semantics.",
                outputs=("candidate_id_rows", "valid_count", "overflowed"),
                depends_on=("rows.generic_candidate_rows", "execution.capacity_overflow_contract"),
            ),
            PrimitiveHierarchyNode(
                id="materialization.prepared_output_buffers",
                title="Prepared Output Buffers",
                layer="bounded_materialization",
                status="internal_substrate",
                summary="Reusable host/device result buffers for bounded row output.",
                outputs=("prepared_result_buffer",),
                depends_on=("execution.buffer_descriptors", "materialization.collect_k_bounded"),
            ),
            PrimitiveHierarchyNode(
                id="materialization.row_schema_validation",
                title="Row Schema Validation",
                layer="bounded_materialization",
                status="stable_behavior",
                summary="Validate row width, row ordering, duplicate policy, and exact-output completeness.",
                outputs=("validated_result",),
                depends_on=("materialization.collect_k_bounded",),
            ),
        ),
    ),
    PrimitiveHierarchyNode(
        id="layer.reduction",
        title="Reduction Layer",
        layer="reduction",
        status="stable_behavior",
        summary="Owns compact summaries over traversal hits, rows, or partner-resident columns.",
        depends_on=("layer.traversal", "rows.generic_candidate_rows"),
        children=(
            PrimitiveHierarchyNode(
                id="reduction.scalar",
                title="Scalar Reductions",
                layer="reduction",
                status="stable_primitive",
                summary="Reduce primitive outputs to scalar counts, sums, minima, or maxima.",
                outputs=("scalar_count", "scalar_sum", "scalar_min", "scalar_max"),
                depends_on=("layer.traversal",),
                children=(
                    PrimitiveHierarchyNode(
                        id="reduction.count_hits",
                        title="COUNT_HITS",
                        layer="reduction",
                        status="stable_primitive",
                        summary="Scalar count over hit flags or emitted positive rows.",
                        outputs=("count",),
                        depends_on=("traversal.any_hit",),
                    ),
                    PrimitiveHierarchyNode(
                        id="reduction.reduce_int",
                        title="REDUCE_INT(COUNT|SUM)",
                        layer="reduction",
                        status="stable_primitive",
                        summary="Integer count and sum reductions.",
                        outputs=("int64_result",),
                        depends_on=("rows.generic_candidate_rows",),
                    ),
                    PrimitiveHierarchyNode(
                        id="reduction.reduce_float",
                        title="REDUCE_FLOAT(MIN|MAX|SUM)",
                        layer="reduction",
                        status="stable_primitive",
                        summary="Floating min, max, and sum with explicit tolerance policy.",
                        outputs=("float64_result",),
                        depends_on=("rows.generic_candidate_rows",),
                    ),
                ),
            ),
            PrimitiveHierarchyNode(
                id="reduction.grouped",
                title="Grouped / Keyed Reductions",
                layer="reduction",
                status="internal_substrate",
                summary="Per-group flags, counts, sums, minima, maxima, and fused stats.",
                outputs=("grouped_rows",),
                depends_on=("rows.generic_candidate_rows",),
                children=(
                    PrimitiveHierarchyNode(
                        id="reduction.group_any",
                        title="group_any",
                        layer="reduction",
                        status="internal_substrate",
                        summary="Per-group boolean existence.",
                        outputs=("group_id", "any_flag"),
                        depends_on=("reduction.grouped",),
                    ),
                    PrimitiveHierarchyNode(
                        id="reduction.group_count",
                        title="group_count",
                        layer="reduction",
                        status="internal_substrate",
                        summary="Per-group count aggregation.",
                        outputs=("group_id", "count"),
                        depends_on=("reduction.grouped",),
                    ),
                    PrimitiveHierarchyNode(
                        id="reduction.group_sum",
                        title="group_sum_i64 / group_sum_f64",
                        layer="reduction",
                        status="internal_substrate",
                        summary="Per-group integer or floating sum.",
                        outputs=("group_id", "sum"),
                        depends_on=("reduction.grouped",),
                    ),
                    PrimitiveHierarchyNode(
                        id="reduction.group_min_max",
                        title="group_min / group_max",
                        layer="reduction",
                        status="internal_substrate",
                        summary="Per-group minimum and maximum.",
                        outputs=("group_id", "min", "max"),
                        depends_on=("reduction.grouped",),
                    ),
                    PrimitiveHierarchyNode(
                        id="reduction.group_stats",
                        title="group_sum_count / group_stats",
                        layer="reduction",
                        status="internal_substrate",
                        summary="Fused grouped count, sum, min, and max statistics.",
                        outputs=("group_id", "count", "sum", "min", "max"),
                        depends_on=("reduction.grouped",),
                    ),
                    PrimitiveHierarchyNode(
                        id="reduction.ray_triangle_primitive_grouped_i64",
                        title="RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D",
                        layer="reduction",
                        status="candidate_behavior",
                        summary=(
                            "All-hit 3-D ray/triangle primitive-id deduplication followed by "
                            "grouped integer reduction over app-provided group ids and payloads."
                        ),
                        outputs=("group_id", "count", "sum", "min", "max"),
                        depends_on=("traversal.any_hit", "reduction.grouped"),
                        boundary="Query encoding and group/value semantics remain app code.",
                    ),
                ),
            ),
            PrimitiveHierarchyNode(
                id="reduction.columnar_compact_summary",
                title="Columnar Compact Summary",
                layer="reduction",
                status="stable_compatibility_path",
                summary="Compact summaries over app-owned columnar/denormalized input.",
                outputs=("compact_summary",),
                depends_on=("execution.partner_resident_handoff", "reduction.grouped"),
                boundary="Not SQL, not a DBMS, and not a query planner.",
            ),
        ),
    ),
    PrimitiveHierarchyNode(
        id="layer.continuation",
        title="Continuation Layer",
        layer="continuation",
        status="internal_substrate",
        summary="Owns reusable post-traversal continuations that remain app-independent.",
        depends_on=("layer.reduction", "layer.bounded_materialization"),
        children=(
            PrimitiveHierarchyNode(
                id="continuation.fixed_radius_graph",
                title="Fixed-Radius Graph Continuation",
                layer="continuation",
                status="internal_substrate",
                summary="Generic continuation over fixed-radius candidate streams and group/component pressure.",
                outputs=("component_or_group_rows",),
                depends_on=("rows.fixed_radius_neighbor_rows", "reduction.grouped"),
                boundary="Cluster semantics remain app code.",
            ),
            PrimitiveHierarchyNode(
                id="continuation.partner_resident",
                title="Partner-Resident Continuation",
                layer="continuation",
                status="internal_substrate",
                summary="Continuation in NumPy/CuPy/PyTorch-style partner arrays after RTDL traversal.",
                outputs=("partner_owned_result",),
                depends_on=("execution.partner_resident_handoff",),
            ),
            PrimitiveHierarchyNode(
                id="continuation.segmented_chunked_rows",
                title="Segmented / Chunked Row Continuation",
                layer="continuation",
                status="internal_substrate",
                summary=(
                    "Page generic row streams with deterministic continuation tokens "
                    "to avoid unbounded materialization and device-memory pressure."
                ),
                outputs=("row_pages", "continuation_state"),
                depends_on=("rows.generic_candidate_rows", "execution.capacity_overflow_contract"),
            ),
            PrimitiveHierarchyNode(
                id="continuation.ranked_summary",
                title="Candidate-Quality / Ranked Summary Continuation",
                layer="continuation",
                status="internal_substrate",
                summary="Summarize candidate quality or bounded nearest/ranked rows without owning app policy.",
                outputs=("ranked_summary",),
                depends_on=("rows.fixed_radius_neighbor_rows", "reduction.scalar"),
            ),
        ),
    ),
    PrimitiveHierarchyNode(
        id="layer.candidate_experimental",
        title="Candidate / Experimental Layer",
        layer="candidate_experimental",
        status="candidate_behavior",
        summary="Records design pressure that is not yet a stable app-independent primitive contract.",
        depends_on=("layer.continuation",),
        children=(
            PrimitiveHierarchyNode(
                id="candidate.aggregate_frontier_traversal",
                title="Aggregate-Frontier Traversal",
                layer="candidate_experimental",
                status="candidate_behavior",
                summary=(
                    "Future native/partner lowering of aggregate-tree traversal "
                    "behind the generic aggregate-frontier row contract."
                ),
                outputs=("frontier_rows", "summary_inputs"),
                depends_on=("rows.aggregate_frontier_collect", "continuation.partner_resident"),
                boundary="Force law and scoring math remain app or partner code.",
            ),
            PrimitiveHierarchyNode(
                id="candidate.streamed_graph_lowering",
                title="Streamed / Segmented Graph Lowering",
                layer="candidate_experimental",
                status="candidate_behavior",
                summary="Lower large graph-like row contracts without all-at-once materialization.",
                outputs=("row_pages", "stream_state"),
                depends_on=("continuation.segmented_chunked_rows",),
            ),
            PrimitiveHierarchyNode(
                id="candidate.device_grouped_candidate_merge",
                title="Device-Resident Grouped Candidate Merge / Finalize",
                layer="candidate_experimental",
                status="candidate_behavior",
                summary="Merge grouped candidate streams on device before final materialization.",
                outputs=("grouped_candidate_summary",),
                depends_on=("reduction.grouped", "execution.partner_resident_handoff"),
            ),
            PrimitiveHierarchyNode(
                id="candidate.zero_copy_row_streams",
                title="Future Zero-Copy Row Streams",
                layer="candidate_experimental",
                status="candidate_behavior",
                summary="Avoid unnecessary host materialization when the consumer remains device-resident.",
                outputs=("device_row_stream",),
                depends_on=("execution.partner_resident_handoff", "rows.generic_candidate_rows"),
            ),
        ),
    ),
)


def iter_primitive_hierarchy_nodes(
    nodes: Iterable[PrimitiveHierarchyNode] = PRIMITIVE_HIERARCHY,
) -> tuple[PrimitiveHierarchyNode, ...]:
    flattened: list[PrimitiveHierarchyNode] = []

    def visit(node: PrimitiveHierarchyNode) -> None:
        flattened.append(node)
        for child in node.children:
            visit(child)

    for root in nodes:
        visit(root)
    return tuple(flattened)


def primitive_hierarchy() -> tuple[dict[str, object], ...]:
    """Return a serializable snapshot of the current primitive hierarchy."""

    return tuple(node.to_dict() for node in PRIMITIVE_HIERARCHY)


def primitive_layer_map() -> dict[str, tuple[str, ...]]:
    layers: dict[str, list[str]] = {layer: [] for layer in PRIMITIVE_HIERARCHY_LAYER_ORDER}
    for node in iter_primitive_hierarchy_nodes():
        layers.setdefault(node.layer, []).append(node.id)
    return {layer: tuple(ids) for layer, ids in layers.items()}


def find_primitive_hierarchy_node(node_id: str) -> PrimitiveHierarchyNode:
    for node in iter_primitive_hierarchy_nodes():
        if node.id == node_id:
            return node
    raise KeyError(f"unknown primitive hierarchy node: {node_id}")


def validate_primitive_hierarchy() -> dict[str, object]:
    nodes = iter_primitive_hierarchy_nodes()
    ids = [node.id for node in nodes]
    duplicate_ids = tuple(sorted({node_id for node_id in ids if ids.count(node_id) > 1}))
    id_set = set(ids)
    unknown_layers = tuple(sorted({node.layer for node in nodes if node.layer not in PRIMITIVE_HIERARCHY_LAYER_ORDER}))
    unknown_statuses = tuple(sorted({node.status for node in nodes if node.status not in PRIMITIVE_HIERARCHY_STATUSES}))
    missing_dependencies = tuple(
        sorted(
            {
                dependency
                for node in nodes
                for dependency in node.depends_on
                if dependency not in id_set
            }
        )
    )
    layer_index = {layer: index for index, layer in enumerate(PRIMITIVE_HIERARCHY_LAYER_ORDER)}
    backward_dependencies = []
    for node in nodes:
        node_index = layer_index.get(node.layer, -1)
        for dependency_id in node.depends_on:
            if dependency_id not in id_set:
                continue
            dependency = find_primitive_hierarchy_node(dependency_id)
            dependency_index = layer_index[dependency.layer]
            if dependency_index > node_index:
                backward_dependencies.append((node.id, dependency_id))
    return {
        "version": PRIMITIVE_HIERARCHY_VERSION,
        "valid": not duplicate_ids and not unknown_layers and not unknown_statuses and not missing_dependencies and not backward_dependencies,
        "node_count": len(nodes),
        "layer_order": PRIMITIVE_HIERARCHY_LAYER_ORDER,
        "duplicate_ids": duplicate_ids,
        "unknown_layers": unknown_layers,
        "unknown_statuses": unknown_statuses,
        "missing_dependencies": missing_dependencies,
        "backward_dependencies": tuple(backward_dependencies),
        "app_owned_boundary_exclusions": APP_OWNED_BOUNDARY_EXCLUSIONS,
    }


__all__ = [
    "APP_OWNED_BOUNDARY_EXCLUSIONS",
    "PRIMITIVE_HIERARCHY",
    "PRIMITIVE_HIERARCHY_LAYER_ORDER",
    "PRIMITIVE_HIERARCHY_STATUSES",
    "PRIMITIVE_HIERARCHY_VERSION",
    "PrimitiveHierarchyNode",
    "find_primitive_hierarchy_node",
    "iter_primitive_hierarchy_nodes",
    "primitive_hierarchy",
    "primitive_layer_map",
    "validate_primitive_hierarchy",
]
