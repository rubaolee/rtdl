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

PRIMITIVE_CAPABILITY_TAGS = (
    "intent:exists",
    "intent:count",
    "intent:nearest",
    "intent:membership",
    "intent:intersection",
    "intent:components",
    "intent:reduce",
    "intent:topk",
    "intent:collect_rows",
    "intent:frontier",
    "intent:order",
    "intent:prepare",
    "shape:generic",
    "shape:point_set",
    "shape:segment_set",
    "shape:fixed_radius",
    "shape:closed_shape",
    "shape:segment_pair",
    "shape:ray_triangle",
    "shape:aabb",
    "shape:point_in_polygon",
    "shape:aggregate_frontier",
    "dim:2d",
    "dim:3d",
    "output:scalar",
    "output:rows",
    "output:grouped",
    "output:mask",
    "output:witness",
    "output:columns",
    "exactness:exact",
    "exactness:approx",
    "exactness:bounded",
    "keying:none",
    "keying:by_group_id",
    "keying:caller_id",
    "keying:by_query_id",
    "keying:by_ray_id",
)

PRIMITIVE_DUPLICATE_KEY_FAMILIES = ("intent", "shape", "dim", "output", "keying")

PRIMITIVE_PROMOTION_METADATA_STATUSES = (
    "stable_primitive",
    "stable_behavior",
    "stable_compatibility_path",
    "candidate_behavior",
)

PRIMITIVE_DISCOVERY_METADATA_FIELDS = (
    "capability_tags",
    "aliases",
    "intent_phrases",
    "reference_path",
    "backends",
)

PRIMITIVE_DISCOVERY_VERSION = "rtdl.primitive_discovery.v1"

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
    capability_tags: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    intent_phrases: tuple[str, ...] = ()
    reference_path: str = ""
    backends: tuple[str, ...] = ()
    partner_ops: tuple[str, ...] = ()
    considered_alternatives: tuple[str, ...] = ()
    distinct_from: str = ""

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
            "capability_tags": self.capability_tags,
            "aliases": self.aliases,
            "intent_phrases": self.intent_phrases,
            "reference_path": self.reference_path,
            "backends": self.backends,
            "partner_ops": self.partner_ops,
            "considered_alternatives": self.considered_alternatives,
            "distinct_from": self.distinct_from,
        }


PRIMITIVE_HIERARCHY = (
    PrimitiveHierarchyNode(
        id="layer.execution_residency",
        title="Execution / Residency Layer",
        layer="execution_residency",
        status="stable_behavior",
        summary="Owns prepared runtime state, buffer descriptors, residency, and capacity contracts.",
        capability_tags=("intent:collect_rows", "shape:generic", "output:columns", "exactness:bounded", "keying:none"),
        aliases=("execution_residency", "prepared_state", "buffer_residency", "capacity_contracts"),
        intent_phrases=(
            "find prepared runtime state and buffer residency contracts",
            "understand execution capacity overflow and prepared handle behavior",
        ),
        reference_path="docs/rtdl_primitive_catalog.md",
        backends=("metadata_only",),
        children=(
            PrimitiveHierarchyNode(
                id="execution.prepared_rt_state",
                title="Prepared RT State",
                layer="execution_residency",
                status="stable_behavior",
                summary="Reusable prepared Embree/OptiX scenes, indexes, and query-side state.",
                outputs=("prepared_handle", "lifetime_metadata"),
                capability_tags=("intent:exists", "shape:generic", "output:columns", "exactness:bounded", "keying:none"),
                aliases=("prepared_rt_state", "prepared_scene", "prepared_handle", "reusable_index"),
                intent_phrases=(
                    "reuse prepared Embree or OptiX state across queries",
                    "find prepared scene and query state lifetime metadata",
                ),
                reference_path="docs/features/engine_support_matrix.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
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
                capability_tags=(
                    "intent:collect_rows",
                    "shape:generic",
                    "output:rows",
                    "exactness:bounded",
                    "keying:none",
                ),
                aliases=(
                    "capacity_overflow",
                    "overflow_contract",
                    "fail_closed_capacity",
                    "fail closed overflow capacity",
                    "bounded_capacity",
                ),
                intent_phrases=(
                    "fail closed when exact bounded output capacity is exceeded",
                    "find overflow and complete coverage metadata for bounded rows",
                ),
                reference_path="docs/rtdl_primitive_catalog.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
            ),
            PrimitiveHierarchyNode(
                id="execution.spatial_order_points_2d",
                title="Spatial Order Points 2D",
                layer="execution_residency",
                status="stable_behavior",
                summary="Deterministically reorder caller-owned 2-D point records for traversal locality before packing.",
                outputs=("ordered_records", "stable_id_order"),
                boundary=(
                    "This is a generic preparation hint. It preserves caller IDs and does not add "
                    "app-specific membership, join, or predicate semantics."
                ),
                capability_tags=(
                    "intent:order",
                    "shape:point_set",
                    "dim:2d",
                    "output:columns",
                    "exactness:exact",
                    "keying:none",
                ),
                aliases=("spatial_order_points_2d", "morton_point_order", "z_order_points", "locality_order_points"),
                intent_phrases=(
                    "order 2d points by spatial locality before packing",
                    "morton order points before packing",
                    "use morton or axis point ordering while preserving record ids",
                ),
                reference_path="docs/rtdl_primitive_catalog.md",
                backends=("cpu_python_reference",),
                considered_alternatives=("execution.prepared_rt_state", "rows.generic_candidate_rows"),
                distinct_from=(
                    "Reorders caller-owned query records before execution; it does not prepare an RT scene "
                    "or emit witness rows."
                ),
            ),
            PrimitiveHierarchyNode(
                id="execution.spatial_order_segments_2d",
                title="Spatial Order Segments 2D",
                layer="execution_residency",
                status="stable_behavior",
                summary="Deterministically reorder caller-owned 2-D segment records by centroid locality before packing.",
                outputs=("ordered_records", "stable_id_order"),
                boundary=(
                    "This is a generic preparation hint. It preserves caller segment IDs and does not add "
                    "app-specific intersection, join, overlay, or predicate semantics."
                ),
                capability_tags=(
                    "intent:order",
                    "shape:segment_set",
                    "dim:2d",
                    "output:columns",
                    "exactness:exact",
                    "keying:none",
                ),
                aliases=("spatial_order_segments_2d", "morton_segment_order", "z_order_segments", "locality_order_segments"),
                intent_phrases=(
                    "order 2d segments by centroid locality before packing",
                    "morton order segments before packing",
                    "use morton or axis segment ordering while preserving segment ids",
                ),
                reference_path="docs/rtdl_primitive_catalog.md",
                backends=("cpu_python_reference",),
                considered_alternatives=("execution.prepared_rt_state", "rows.generic_candidate_rows"),
                distinct_from=(
                    "Reorders caller-owned segment records before execution; it does not prepare an RT scene "
                    "or emit segment-pair witness rows."
                ),
            ),
            PrimitiveHierarchyNode(
                id="execution.segment_columns_2d",
                title="Segment Columns 2D",
                layer="execution_residency",
                status="stable_behavior",
                summary="Normalize caller-owned 2-D segment records into reusable column batches before packing.",
                outputs=("segment_id_column", "endpoint_columns", "column_batch"),
                boundary=(
                    "This is a generic preparation/layout primitive. It preserves caller IDs and geometry columns "
                    "and does not add app-specific intersection, join, overlay, or predicate semantics."
                ),
                capability_tags=(
                    "intent:prepare",
                    "shape:segment_set",
                    "dim:2d",
                    "output:columns",
                    "exactness:exact",
                    "keying:caller_id",
                ),
                aliases=(
                    "segment_columns_2d",
                    "segment_column_batch",
                    "packed_segment_columns",
                    "segment_column_layout",
                ),
                intent_phrases=(
                    "prepare reusable 2d segment columns before packing",
                    "convert segment records to id and endpoint columns",
                    "cache segment column arrays while preserving caller ids",
                ),
                reference_path="docs/rtdl_primitive_catalog.md",
                backends=("cpu_python_reference",),
                considered_alternatives=("execution.spatial_order_segments_2d", "execution.prepared_rt_state"),
                distinct_from=(
                    "Builds reusable segment columns for packing and prepared-state inputs; it does not itself "
                    "perform locality ordering unless the caller requests an order mode, and it does not build "
                    "an RT scene."
                ),
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
        capability_tags=("intent:exists", "shape:generic", "output:mask", "exactness:exact", "keying:none"),
        aliases=("traversal", "rt_traversal", "predicate_traversal", "ray_query"),
        intent_phrases=(
            "find app independent RT predicate traversal primitives",
            "choose any hit count hits or fixed radius traversal behavior",
        ),
        reference_path="docs/features/README.md",
        backends=("cpu_python_reference", "cpu", "embree", "optix"),
        children=(
            PrimitiveHierarchyNode(
                id="traversal.any_hit",
                title="ANY_HIT",
                layer="traversal",
                status="stable_primitive",
                summary="Existence of at least one hit between query geometry and prepared/build geometry.",
                outputs=("hit_flag",),
                depends_on=("execution.prepared_rt_state",),
                capability_tags=("intent:exists", "shape:generic", "output:mask", "exactness:exact", "keying:none"),
                aliases=("any_hit", "exists", "hit_exists", "has_hit", "boolean_hit"),
                intent_phrases=(
                    "does any query geometry hit prepared geometry",
                    "return a boolean hit flag without materializing witness rows",
                ),
                reference_path="docs/features/ray_tri_anyhit/README.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
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
                capability_tags=("intent:count", "shape:generic", "output:scalar", "exactness:exact", "keying:none"),
                aliases=("count_hits", "hit_count", "count_positive_hits", "scalar_count"),
                intent_phrases=(
                    "count hits without returning every witness row",
                    "compute a scalar hit count",
                ),
                reference_path="docs/features/ray_tri_hitcount/README.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
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
                capability_tags=(
                    "intent:count",
                    "shape:fixed_radius",
                    "dim:2d",
                    "dim:3d",
                    "output:scalar",
                    "output:mask",
                    "exactness:exact",
                    "keying:by_query_id",
                ),
                aliases=("fixed_radius_count", "within_radius_count", "neighbor_count", "density_count", "radius_threshold"),
                intent_phrases=(
                    "count points within a radius",
                    "return neighbor counts and threshold flags per query point",
                ),
                reference_path="docs/features/fixed_radius_neighbors/README.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
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
                id="rows.ray_triangle_hit_stream_3d",
                title="RAY_TRIANGLE_HIT_STREAM_3D",
                layer="row_emission",
                status="candidate_behavior",
                summary="Emit bounded app-free 3-D ray/triangle hit rows for partner continuation.",
                outputs=("ray_id", "primitive_id"),
                depends_on=("traversal.any_hit", "execution.capacity_overflow_contract"),
                boundary=(
                    "The engine emits only ray and primitive ids. Mapping primitive ids "
                    "to group keys, payload values, predicates, or app rows is app or partner code."
                ),
                capability_tags=(
                    "intent:collect_rows",
                    "shape:ray_triangle",
                    "dim:3d",
                    "output:rows",
                    "output:witness",
                    "exactness:bounded",
                    "keying:by_ray_id",
                ),
                aliases=("ray_triangle_rows", "hit_stream", "witness_rows", "all_hit_rows"),
                intent_phrases=(
                    "emit bounded ray triangle hit rows",
                    "collect ray id and primitive id witnesses for partner continuation",
                ),
                reference_path="docs/features/ray_tri_anyhit/README.md",
                backends=("cpu_python_reference", "embree", "optix"),
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
                capability_tags=(
                    "intent:membership",
                    "intent:collect_rows",
                    "shape:aabb",
                    "dim:2d",
                    "output:rows",
                    "exactness:bounded",
                    "keying:by_query_id",
                ),
                aliases=("expanded_aabb_rows", "aabb_point_membership_rows", "box_membership_rows"),
                intent_phrases=(
                    "emit rows for points inside caller expanded AABBs",
                    "collect source id and box id membership rows with overflow checks",
                ),
                reference_path="docs/features/db_workloads/README.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
            ),
            PrimitiveHierarchyNode(
                id="rows.point_closed_shape_boundary_event_columns",
                title="POINT_CLOSED_SHAPE_BOUNDARY_EVENT_COLUMNS_2D",
                layer="row_emission",
                status="candidate_behavior",
                summary=(
                    "Emit one deterministic first boundary-event column row for each "
                    "point/closed-shape pair that has a non-colinear crossing along "
                    "a caller-selected ray direction."
                ),
                outputs=(
                    "point_id",
                    "shape_id",
                    "boundary_id",
                    "crossing_t",
                    "crossing_x",
                    "crossing_y",
                    "event_kind",
                ),
                depends_on=("traversal.closest_hit", "execution.capacity_overflow_contract"),
                boundary=(
                    "The primitive emits generic boundary-event columns only. Shape "
                    "membership classification, map/entity lookup, parity rules, and "
                    "paper-system semantics remain caller-owned."
                ),
                capability_tags=(
                    "intent:membership",
                    "intent:nearest",
                    "intent:collect_rows",
                    "shape:closed_shape",
                    "dim:2d",
                    "output:columns",
                    "output:witness",
                    "exactness:exact",
                    "keying:by_query_id",
                ),
                aliases=(
                    "point_closed_shape_first_crossing",
                    "closed_shape_boundary_event",
                    "first_boundary_crossing",
                    "best_boundary_crossing",
                    "upward_ray_boundary_event",
                ),
                intent_phrases=(
                    "find the first boundary crossing for points against closed shapes",
                    "emit typed boundary event columns for point shape probes",
                    "select a closest crossing boundary event without app entity semantics",
                ),
                reference_path="docs/rtdl_primitive_catalog.md",
                backends=("cpu_python_reference", "planned_optix"),
                considered_alternatives=(
                    "rows.expanded_aabb_point_membership_rows",
                    "rows.segment_polygon_rows",
                    "traversal.count_hits",
                ),
                distinct_from=(
                    "Membership rows answer whether a point is inside a shape, segment/polygon rows "
                    "emit segment-shape witnesses, and count_hits returns only scalar hit counts; "
                    "this contract returns the representative boundary event itself."
                ),
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
                capability_tags=(
                    "intent:collect_rows",
                    "intent:nearest",
                    "shape:fixed_radius",
                    "dim:2d",
                    "dim:3d",
                    "output:rows",
                    "output:witness",
                    "exactness:bounded",
                    "keying:by_query_id",
                ),
                aliases=("fixed_radius_rows", "neighbor_rows", "nearest_neighbor_rows", "radius_neighbors"),
                intent_phrases=(
                    "emit neighbor rows within a fixed radius",
                    "return query neighbor distance rows for later ranking or reduction",
                ),
                reference_path="docs/features/fixed_radius_neighbors/README.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
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
                capability_tags=(
                    "intent:frontier",
                    "intent:collect_rows",
                    "shape:aggregate_frontier",
                    "dim:2d",
                    "dim:3d",
                    "output:rows",
                    "exactness:bounded",
                    "keying:by_query_id",
                ),
                aliases=("aggregate_frontier_rows", "frontier_collect", "aggregate_tree_rows"),
                intent_phrases=(
                    "emit aggregate frontier ids and offsets from prepared aggregate traversal",
                    "collect generic aggregate tree frontier rows without app force laws",
                ),
                reference_path="docs/rtdl_primitive_catalog.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
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
        capability_tags=("intent:collect_rows", "shape:generic", "output:rows", "exactness:bounded", "keying:none"),
        aliases=("bounded_materialization", "bounded_collect", "row_materialization", "row_schema"),
        intent_phrases=(
            "collect bounded rows with capacity and schema checks",
            "validate exact row output ordering and overflow behavior",
        ),
        reference_path="docs/rtdl_primitive_catalog.md",
        backends=("cpu_python_reference", "cpu", "embree", "optix"),
        children=(
            PrimitiveHierarchyNode(
                id="materialization.collect_k_bounded",
                title="COLLECT_K_BOUNDED",
                layer="bounded_materialization",
                status="stable_primitive",
                summary="Collect up to K rows with exact fail-closed overflow semantics.",
                outputs=("candidate_id_rows", "valid_count", "overflowed"),
                depends_on=("rows.generic_candidate_rows", "execution.capacity_overflow_contract"),
                capability_tags=(
                    "intent:topk",
                    "intent:collect_rows",
                    "shape:generic",
                    "output:rows",
                    "output:witness",
                    "exactness:bounded",
                    "keying:none",
                ),
                aliases=("collect_k", "bounded_collect", "bounded_witness", "top_k_rows"),
                intent_phrases=(
                    "collect a bounded number of witness rows",
                    "fail closed when exact bounded output overflows capacity",
                ),
                reference_path="docs/features/knn_rows/README.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
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
                capability_tags=(
                    "intent:collect_rows",
                    "shape:generic",
                    "output:rows",
                    "exactness:bounded",
                    "keying:none",
                ),
                aliases=("row_schema_validation", "row_width_validation", "bounded_result_validation"),
                intent_phrases=(
                    "validate row width ordering duplicate policy and completeness",
                    "check bounded row materialization metadata before consuming rows",
                ),
                reference_path="docs/rtdl_primitive_catalog.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
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
        capability_tags=("intent:reduce", "shape:generic", "output:scalar", "exactness:exact", "keying:none"),
        aliases=("reduction", "reduce_rows", "compact_summary", "scalar_or_grouped_reduce"),
        intent_phrases=(
            "find scalar and grouped reductions over traversal rows",
            "reduce hit rows or columnar payloads to compact summaries",
        ),
        reference_path="docs/features/reduce_rows/README.md",
        backends=("cpu_python_reference", "cpu", "embree", "optix"),
        children=(
            PrimitiveHierarchyNode(
                id="reduction.scalar",
                title="Scalar Reductions",
                layer="reduction",
                status="stable_primitive",
                summary="Reduce primitive outputs to scalar counts, sums, minima, or maxima.",
                outputs=("scalar_count", "scalar_sum", "scalar_min", "scalar_max"),
                depends_on=("layer.traversal",),
                capability_tags=("intent:reduce", "shape:generic", "output:scalar", "exactness:exact", "keying:none"),
                aliases=("scalar_reduction", "reduce_scalar", "count_sum_min_max", "compact_scalar_summary"),
                intent_phrases=(
                    "reduce primitive outputs to scalar counts sums minima or maxima",
                    "compute compact scalar summaries without returning rows",
                ),
                reference_path="docs/features/reduce_rows/README.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
                children=(
                    PrimitiveHierarchyNode(
                        id="reduction.count_hits",
                        title="COUNT_HITS",
                        layer="reduction",
                        status="stable_primitive",
                        summary="Scalar count over hit flags or emitted positive rows.",
                        outputs=("count",),
                        depends_on=("traversal.any_hit",),
                        capability_tags=("intent:count", "shape:generic", "output:scalar", "exactness:exact", "keying:none"),
                        aliases=("count_hits_reduction", "positive_row_count", "hit_flag_count"),
                        intent_phrases=(
                            "count hit flags or emitted positive rows",
                            "compute scalar hit count as a reduction",
                        ),
                        reference_path="docs/features/ray_tri_hitcount/README.md",
                        backends=("cpu_python_reference", "cpu", "embree", "optix"),
                    ),
                    PrimitiveHierarchyNode(
                        id="reduction.reduce_int",
                        title="REDUCE_INT(COUNT|SUM)",
                        layer="reduction",
                        status="stable_primitive",
                        summary="Integer count and sum reductions.",
                        outputs=("int64_result",),
                        depends_on=("rows.generic_candidate_rows",),
                        capability_tags=("intent:reduce", "shape:generic", "output:scalar", "exactness:exact", "keying:none"),
                        aliases=("reduce_int", "integer_reduction", "integer count sum reductions", "int_count_sum", "i64_reduce"),
                        intent_phrases=(
                            "reduce integer rows to count or sum",
                            "compute int64 scalar reductions over generic rows",
                        ),
                        reference_path="docs/features/reduce_rows/README.md",
                        backends=("cpu_python_reference", "cpu", "embree", "optix"),
                    ),
                    PrimitiveHierarchyNode(
                        id="reduction.reduce_float",
                        title="REDUCE_FLOAT(MIN|MAX|SUM)",
                        layer="reduction",
                        status="stable_primitive",
                        summary="Floating min, max, and sum with explicit tolerance policy.",
                        outputs=("float64_result",),
                        depends_on=("rows.generic_candidate_rows",),
                        capability_tags=("intent:reduce", "shape:generic", "output:scalar", "exactness:exact", "keying:none"),
                        aliases=("reduce_float", "floating_reduction", "float_min_max_sum", "f64_reduce"),
                        intent_phrases=(
                            "reduce floating rows to min max or sum",
                            "compute float64 scalar reductions with tolerance policy",
                        ),
                        reference_path="docs/features/reduce_rows/README.md",
                        backends=("cpu_python_reference", "cpu", "embree", "optix"),
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
                capability_tags=(
                    "intent:reduce",
                    "intent:count",
                    "shape:generic",
                    "output:grouped",
                    "output:scalar",
                    "exactness:exact",
                    "keying:by_group_id",
                ),
                aliases=("grouped_reduction", "group_by", "group_count", "group_sum", "segmented_reduction"),
                intent_phrases=(
                    "reduce rows per group id",
                    "compute grouped count sum min max or stats",
                ),
                reference_path="docs/features/reduce_rows/README.md",
                backends=("cpu_python_reference", "cpu", "optix"),
                partner_ops=("segmented_count_i64", "segmented_sum_f64", "grouped_argmin_f64"),
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
                        capability_tags=(
                            "intent:reduce",
                            "intent:count",
                            "shape:ray_triangle",
                            "dim:3d",
                            "output:grouped",
                            "exactness:exact",
                            "keying:by_group_id",
                        ),
                        aliases=("ray_triangle_grouped_reduction", "primitive_grouped_reduction", "grouped_i64_reduction"),
                        intent_phrases=(
                            "reduce ray triangle primitive hits by caller supplied group id",
                            "count or sum primitive payloads per group after ray triangle traversal",
                        ),
                        reference_path="examples/v2_0/research_benchmarks/raydb_style/README.md",
                        backends=("cpu_python_reference", "optix"),
                        considered_alternatives=("traversal.count_hits", "reduction.grouped", "rows.ray_triangle_hit_stream_3d"),
                        distinct_from=(
                            "Combines ray/triangle traversal with caller-supplied primitive group ids; "
                            "plain grouped reductions do not perform traversal and count_hits is not keyed."
                        ),
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
                capability_tags=("intent:reduce", "shape:generic", "output:columns", "exactness:exact", "keying:by_group_id"),
                aliases=("columnar_compact_summary", "columnar_grouped_aggregate", "columnar_payload_summary"),
                intent_phrases=(
                    "summarize app owned columnar payloads with grouped reductions",
                    "lower columnar aggregate rows without SQL or DBMS semantics",
                ),
                reference_path="docs/features/db_workloads/README.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
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
                capability_tags=(
                    "intent:components",
                    "intent:reduce",
                    "shape:fixed_radius",
                    "dim:3d",
                    "output:columns",
                    "output:grouped",
                    "exactness:exact",
                    "keying:by_query_id",
                ),
                aliases=(
                    "fixed_radius_graph_components",
                    "radius_graph_component_labels",
                    "grouped_stream_component_labels",
                    "fixed_radius_component_continuation",
                ),
                intent_phrases=(
                    "compute component labels over a fixed radius graph",
                    "avoid dense adjacency row materialization for fixed radius graph components",
                    "run grouped stream continuation for fixed radius graph component labels",
                ),
                reference_path="docs/reports/goal3155_fixed_radius_graph_component_front_door_2026-06-03.md",
                backends=("optix",),
                partner_ops=("cupy_grouped_stream_component_labels",),
                considered_alternatives=(
                    "rows.fixed_radius_neighbor_rows",
                    "continuation.segmented_chunked_rows",
                    "reduction.grouped",
                ),
                distinct_from=(
                    "Consumes fixed-radius traversal pressure into component-label columns; "
                    "it does not emit full neighbor rows like rows.fixed_radius_neighbor_rows, "
                    "page arbitrary row streams like continuation.segmented_chunked_rows, "
                    "or own app policy beyond the generic component threshold."
                ),
            ),
            PrimitiveHierarchyNode(
                id="continuation.partner_resident",
                title="Explicit Partner Continuation",
                layer="continuation",
                status="internal_substrate",
                summary=(
                    "Partner-selected post-traversal continuation over RTDL buffer descriptors. "
                    "Partner roles are explicit metadata, not hidden routing or native-engine policy."
                ),
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
                capability_tags=(
                    "intent:collect_rows",
                    "shape:generic",
                    "output:rows",
                    "output:columns",
                    "exactness:bounded",
                    "keying:by_query_id",
                ),
                aliases=("segmented_rows", "chunked_rows", "paged_rows", "streaming_rows"),
                intent_phrases=(
                    "page large row streams with deterministic continuation tokens",
                    "avoid all at once materialization of large generic row outputs",
                ),
                reference_path="docs/rtdl_primitive_catalog.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
            ),
            PrimitiveHierarchyNode(
                id="continuation.ranked_summary",
                title="Candidate-Quality / Ranked Summary Continuation",
                layer="continuation",
                status="internal_substrate",
                summary="Summarize candidate quality or bounded nearest/ranked rows without owning app policy.",
                outputs=("ranked_summary",),
                depends_on=("rows.fixed_radius_neighbor_rows", "reduction.scalar"),
                capability_tags=(
                    "intent:nearest",
                    "intent:topk",
                    "intent:reduce",
                    "shape:fixed_radius",
                    "dim:2d",
                    "dim:3d",
                    "output:grouped",
                    "output:scalar",
                    "exactness:bounded",
                    "keying:by_query_id",
                ),
                aliases=("ranked_summary", "top_k_summary", "nearest_ranked", "candidate_quality"),
                intent_phrases=(
                    "summarize nearest candidate quality by query id",
                    "compute bounded ranked nearest summaries from fixed radius rows",
                ),
                reference_path="docs/features/knn_rows/README.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
                partner_ops=("grouped_argmin_f64", "grouped_topk_f64"),
                considered_alternatives=("rows.fixed_radius_neighbor_rows", "materialization.collect_k_bounded"),
                distinct_from=(
                    "Summarizes already emitted fixed-radius rows; it does not own traversal or "
                    "materialize full witness rows like collect_k_bounded."
                ),
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
        capability_tags=("intent:collect_rows", "shape:generic", "output:rows", "exactness:bounded", "keying:none"),
        aliases=("candidate_experimental", "future_primitives", "experimental_primitives"),
        intent_phrases=(
            "find candidate primitive pressure not yet stable",
            "review future app independent primitive contracts",
        ),
        reference_path="docs/research/future_version_to_do_list.md",
        backends=("metadata_only",),
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
                capability_tags=(
                    "intent:frontier",
                    "intent:collect_rows",
                    "shape:aggregate_frontier",
                    "dim:2d",
                    "dim:3d",
                    "output:rows",
                    "exactness:bounded",
                    "keying:by_query_id",
                ),
                aliases=("aggregate_frontier_traversal", "aggregate_tree_traversal", "frontier_traversal"),
                intent_phrases=(
                    "traverse aggregate tree frontier behind generic row contract",
                    "future lowering for aggregate frontier rows without force law semantics",
                ),
                reference_path="docs/rtdl_primitive_catalog.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
            ),
            PrimitiveHierarchyNode(
                id="candidate.streamed_graph_lowering",
                title="Streamed / Segmented Graph Lowering",
                layer="candidate_experimental",
                status="candidate_behavior",
                summary="Lower large graph-like row contracts without all-at-once materialization.",
                outputs=("row_pages", "stream_state"),
                depends_on=("continuation.segmented_chunked_rows",),
                capability_tags=("intent:collect_rows", "shape:generic", "output:rows", "exactness:bounded", "keying:by_query_id"),
                aliases=("streamed_graph_lowering", "segmented_graph_rows", "paged_graph_rows"),
                intent_phrases=(
                    "lower large graph like row contracts with segmented row pages",
                    "avoid all at once graph row materialization",
                ),
                reference_path="docs/rtdl_primitive_catalog.md",
                backends=("cpu_python_reference", "cpu", "embree", "optix"),
            ),
            PrimitiveHierarchyNode(
                id="candidate.device_grouped_candidate_merge",
                title="Device-Resident Grouped Candidate Merge / Finalize",
                layer="candidate_experimental",
                status="candidate_behavior",
                summary="Merge grouped candidate streams on device before final materialization.",
                outputs=("grouped_candidate_summary",),
                depends_on=("reduction.grouped", "execution.partner_resident_handoff"),
                capability_tags=("intent:reduce", "shape:generic", "output:grouped", "exactness:bounded", "keying:by_group_id"),
                aliases=("device_grouped_candidate_merge", "grouped_candidate_finalize", "device_grouped_merge"),
                intent_phrases=(
                    "merge grouped candidate streams on device before materialization",
                    "finalize grouped candidate summaries without host row expansion",
                ),
                reference_path="docs/rtdl_primitive_catalog.md",
                backends=("cpu_python_reference", "cpu", "optix"),
                partner_ops=("segmented_count_i64", "segmented_sum_f64", "grouped_argmin_f64"),
            ),
            PrimitiveHierarchyNode(
                id="candidate.closed_shape_topology_membership_count_2d",
                title="Closed-Shape Topology-Aware Membership Count 2D",
                layer="candidate_experimental",
                status="candidate_behavior",
                summary=(
                    "Generic point/closed-shape membership count direction with an executable "
                    "owner-face Python reference contract, fail-closed incident-face selector, "
                    "explicit-priority tie-break helper, and future native/device lowering."
                ),
                outputs=("membership_count", "owner_face_id", "ownership_status", "topology_policy_metadata"),
                depends_on=(
                    "rows.point_closed_shape_boundary_event_columns",
                    "reduction.grouped",
                ),
                boundary=(
                    "The primitive must expose generic topology and caller-supplied owner-face "
                    "filtering only. CDB source naming, RayJoin assignment interpretation, "
                    "map/entity lookup, and paper-system semantics remain app code."
                ),
                capability_tags=(
                    "intent:membership",
                    "intent:count",
                    "shape:closed_shape",
                    "dim:2d",
                    "output:scalar",
                    "output:grouped",
                    "exactness:exact",
                    "keying:by_query_id",
                ),
                aliases=(
                    "closed_shape_topology_membership_count",
                    "topology_aware_membership_count",
                    "face_aware_closed_shape_count",
                    "boundary_ownership_count",
                    "ring_chain_membership_count",
                ),
                intent_phrases=(
                    "count point membership in closed shapes with explicit face ring chain topology",
                    "avoid duplicate boundary ownership overcounts in closed shape membership",
                    "filter closed shape candidates by caller supplied owner face ids",
                    "derive owner face only when incident topology has a unique maximum",
                    "break incident topology ties only with caller supplied face priorities",
                    "use deterministic boundary ownership policy for point closed shape counts",
                ),
                reference_path="docs/reports/goal3342_priority_owner_face_selector_reference_2026-06-04.md",
                backends=("cpu_python_reference", "planned_optix"),
                considered_alternatives=(
                    "traversal.count_hits",
                    "rows.point_closed_shape_boundary_event_columns",
                    "reduction.grouped",
                    "candidate.device_grouped_candidate_merge",
                ),
                distinct_from=(
                    "traversal.count_hits produces scalar counts without topology ownership policy; "
                    "rows.point_closed_shape_boundary_event_columns emits boundary witnesses but does not "
                    "classify membership; reduction.grouped only aggregates explicit keys; "
                    "candidate.device_grouped_candidate_merge merges candidate streams without owning "
                    "closed-shape boundary degeneracy semantics."
                ),
            ),
            PrimitiveHierarchyNode(
                id="candidate.zero_copy_row_streams",
                title="Future Zero-Copy Row Streams",
                layer="candidate_experimental",
                status="candidate_behavior",
                summary="Avoid unnecessary host materialization when the consumer remains device-resident.",
                outputs=("device_row_stream",),
                depends_on=("execution.partner_resident_handoff", "rows.generic_candidate_rows"),
                capability_tags=("intent:collect_rows", "shape:generic", "output:columns", "exactness:bounded", "keying:by_query_id"),
                aliases=("zero_copy_row_streams", "device_resident_rows", "resident_row_streams"),
                intent_phrases=(
                    "avoid host materialization when consuming rows on device",
                    "future device resident row stream handoff for partner continuation",
                ),
                reference_path="docs/research/future_version_to_do_list.md",
                backends=("metadata_only",),
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


def validate_primitive_hierarchy(
    nodes: Iterable[PrimitiveHierarchyNode] = PRIMITIVE_HIERARCHY,
    *,
    enforce_promotion_metadata: bool = False,
    promotion_candidate_ids: Iterable[str] = (),
    require_discovery_metadata: bool = False,
) -> dict[str, object]:
    nodes = iter_primitive_hierarchy_nodes(nodes)
    ids = [node.id for node in nodes]
    duplicate_ids = tuple(sorted({node_id for node_id in ids if ids.count(node_id) > 1}))
    id_set = set(ids)
    node_by_id = {node.id: node for node in nodes}
    promotion_candidate_id_set = set(promotion_candidate_ids)
    unknown_promotion_candidate_ids = tuple(sorted(promotion_candidate_id_set - id_set))
    promotion_candidate_scope_required = bool(enforce_promotion_metadata and not promotion_candidate_id_set)
    unknown_layers = tuple(sorted({node.layer for node in nodes if node.layer not in PRIMITIVE_HIERARCHY_LAYER_ORDER}))
    unknown_statuses = tuple(sorted({node.status for node in nodes if node.status not in PRIMITIVE_HIERARCHY_STATUSES}))
    unknown_capability_tags = tuple(
        sorted(
            {
                tag
                for node in nodes
                for tag in node.capability_tags
                if tag not in PRIMITIVE_CAPABILITY_TAGS
            }
        )
    )
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
            dependency = node_by_id[dependency_id]
            dependency_index = layer_index[dependency.layer]
            if dependency_index > node_index:
                backward_dependencies.append((node.id, dependency_id))
    promotion_metadata_missing = _promotion_metadata_missing(
        nodes,
        enforce_promotion_metadata=enforce_promotion_metadata,
        promotion_candidate_ids=promotion_candidate_id_set,
    )
    discovery_metadata_missing = _discovery_metadata_missing(
        nodes,
        require_discovery_metadata=require_discovery_metadata,
    )
    return {
        "version": PRIMITIVE_HIERARCHY_VERSION,
        "valid": (
            not duplicate_ids
            and not unknown_layers
            and not unknown_statuses
            and not unknown_capability_tags
            and not missing_dependencies
            and not backward_dependencies
            and not promotion_candidate_scope_required
            and (not enforce_promotion_metadata or not unknown_promotion_candidate_ids)
            and not promotion_metadata_missing
            and not discovery_metadata_missing
        ),
        "node_count": len(nodes),
        "layer_order": PRIMITIVE_HIERARCHY_LAYER_ORDER,
        "duplicate_ids": duplicate_ids,
        "unknown_layers": unknown_layers,
        "unknown_statuses": unknown_statuses,
        "unknown_capability_tags": unknown_capability_tags,
        "missing_dependencies": missing_dependencies,
        "backward_dependencies": tuple(backward_dependencies),
        "promotion_metadata_enforced": enforce_promotion_metadata,
        "promotion_candidate_ids": tuple(sorted(promotion_candidate_id_set)),
        "promotion_candidate_scope_required": promotion_candidate_scope_required,
        "unknown_promotion_candidate_ids": unknown_promotion_candidate_ids,
        "promotion_metadata_missing": promotion_metadata_missing,
        "discovery_metadata_required": require_discovery_metadata,
        "discovery_metadata_missing": discovery_metadata_missing,
        "app_owned_boundary_exclusions": APP_OWNED_BOUNDARY_EXCLUSIONS,
    }


def _discovery_metadata_missing(
    nodes: tuple[PrimitiveHierarchyNode, ...],
    *,
    require_discovery_metadata: bool,
) -> tuple[dict[str, object], ...]:
    if not require_discovery_metadata:
        return ()

    missing: list[dict[str, object]] = []
    for node in nodes:
        if node.status not in PRIMITIVE_PROMOTION_METADATA_STATUSES:
            continue
        missing_fields = tuple(
            field
            for field in PRIMITIVE_DISCOVERY_METADATA_FIELDS
            if not getattr(node, field)
        )
        if missing_fields:
            missing.append(
                {
                    "node_id": node.id,
                    "status": node.status,
                    "missing_fields": missing_fields,
                }
            )
    return tuple(missing)


def _promotion_metadata_missing(
    nodes: tuple[PrimitiveHierarchyNode, ...],
    *,
    enforce_promotion_metadata: bool,
    promotion_candidate_ids: set[str],
) -> tuple[dict[str, object], ...]:
    if not enforce_promotion_metadata or not promotion_candidate_ids:
        return ()

    missing: list[dict[str, object]] = []
    for node in nodes:
        if node.id not in promotion_candidate_ids:
            continue
        if node.status not in PRIMITIVE_PROMOTION_METADATA_STATUSES:
            continue
        possible_duplicates = _possible_duplicate_nodes(node, nodes)
        if possible_duplicates and not (node.considered_alternatives and node.distinct_from.strip()):
            missing.append(
                {
                    "node_id": node.id,
                    "status": node.status,
                    "possible_duplicates": possible_duplicates,
                    "message": "set considered_alternatives and distinct_from or reuse an existing node",
                }
            )
    return tuple(missing)


def _possible_duplicate_nodes(
    candidate: PrimitiveHierarchyNode,
    existing_nodes: tuple[PrimitiveHierarchyNode, ...],
) -> tuple[dict[str, object], ...]:
    candidate_map = _capability_facet_map(candidate.capability_tags)
    candidate_key_family_count = sum(
        1 for family in PRIMITIVE_DUPLICATE_KEY_FAMILIES if candidate_map.get(family)
    )
    nearest: list[tuple[str, int, tuple[str, ...]]] = []
    for node in existing_nodes:
        if node.id == candidate.id:
            continue
        overlap: list[str] = []
        existing_map = _capability_facet_map(node.capability_tags)
        for family in PRIMITIVE_DUPLICATE_KEY_FAMILIES:
            shared = sorted(set(candidate_map.get(family, ())) & set(existing_map.get(family, ())))
            overlap.extend(f"{family}:{value}" for value in shared)
        if overlap:
            nearest.append((node.id, len(overlap), tuple(overlap)))

    threshold = max(3, candidate_key_family_count)
    return tuple(
        {
            "node_id": node_id,
            "shared_key_facets": shared,
            "overlap_score": score,
        }
        for node_id, score, shared in sorted(nearest, key=lambda item: (-item[1], item[0]))[:5]
        if score >= threshold
    )


def _capability_facet_map(tags: Iterable[str]) -> dict[str, tuple[str, ...]]:
    by_family: dict[str, list[str]] = {}
    for tag in tags:
        if ":" not in tag:
            continue
        family, value = tag.split(":", 1)
        by_family.setdefault(family, []).append(value)
    return {family: tuple(sorted(set(values))) for family, values in by_family.items()}


__all__ = [
    "APP_OWNED_BOUNDARY_EXCLUSIONS",
    "PRIMITIVE_CAPABILITY_TAGS",
    "PRIMITIVE_DISCOVERY_VERSION",
    "PRIMITIVE_DISCOVERY_METADATA_FIELDS",
    "PRIMITIVE_DUPLICATE_KEY_FAMILIES",
    "PRIMITIVE_HIERARCHY",
    "PRIMITIVE_HIERARCHY_LAYER_ORDER",
    "PRIMITIVE_HIERARCHY_STATUSES",
    "PRIMITIVE_HIERARCHY_VERSION",
    "PRIMITIVE_PROMOTION_METADATA_STATUSES",
    "PrimitiveHierarchyNode",
    "find_primitive_hierarchy_node",
    "iter_primitive_hierarchy_nodes",
    "primitive_hierarchy",
    "primitive_layer_map",
    "validate_primitive_hierarchy",
]
