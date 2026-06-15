from __future__ import annotations

from .v3_0_execution_graph import BackendContract
from .v3_0_execution_graph import CapacityPolicy
from .v3_0_execution_graph import ContinuationNode
from .v3_0_execution_graph import GraphValidationError
from .v3_0_execution_graph import GraphValue
from .v3_0_execution_graph import LoweringHints
from .v3_0_execution_graph import PhaseMarker
from .v3_0_execution_graph import PreparedGraph
from .v3_0_execution_graph import PrimitiveNode
from .v3_0_execution_graph import prepare_graph


M5_TOPOLOGY_CONTRACT_KEY = "topology_face_contract_v1"
M5_TOPOLOGY_COMPACTION_OPERATION = "continuation.compact_mask"
M5_LOCAL_PREP_STATUS = "m5_local_topology_graphs_ready_pod_and_author_evidence_pending"


def m5_topology_pilot_graphs() -> tuple[PreparedGraph, PreparedGraph]:
    """Return no-execution topology graphs for M5 preparation."""

    return (
        _point_location_topology_graph(),
        _edge_intersection_topology_graph(),
    )


def validate_m5_topology_pilots() -> dict[str, object]:
    graphs = m5_topology_pilot_graphs()
    primitive_ids = tuple(
        node.primitive_id
        for graph in graphs
        for node in graph.nodes
        if isinstance(node, PrimitiveNode)
    )
    continuation_ops = tuple(
        node.operation
        for graph in graphs
        for node in graph.nodes
        if isinstance(node, ContinuationNode)
    )
    if continuation_ops != (M5_TOPOLOGY_COMPACTION_OPERATION, M5_TOPOLOGY_COMPACTION_OPERATION):
        raise GraphValidationError("M5 topology pilots must share the same compaction continuation")
    return {
        "status": M5_LOCAL_PREP_STATUS,
        "graph_ids": tuple(graph.graph_id for graph in graphs),
        "graph_count": len(graphs),
        "primitive_ids": primitive_ids,
        "shared_topology_contract": M5_TOPOLOGY_CONTRACT_KEY,
        "shared_continuation_operation": M5_TOPOLOGY_COMPACTION_OPERATION,
        "target_backends": tuple(graph.target_backends for graph in graphs),
        "author_code_comparison_required": True,
        "pod_evidence_required": True,
        "public_speedup_claim_authorized": False,
    }


def _point_location_topology_graph() -> PreparedGraph:
    values = (
        GraphValue(
            name="query_points",
            kind="geometry",
            dtype="struct:point2d",
            shape=("query_count",),
            storage="host",
            residency="host_resident",
            lifetime="caller_retained",
            consumers=("boundary_event_producer",),
        ),
        GraphValue(
            name="closed_shape_edges",
            kind="geometry",
            dtype="struct:segment2d",
            shape=("edge_count",),
            storage="host",
            residency="host_resident",
            lifetime="caller_retained",
            consumers=("boundary_event_producer",),
        ),
        *_topology_output_values("boundary_event_producer"),
        _selected_face_value(),
    )
    nodes = (
        PrimitiveNode(
            node_id="boundary_event_producer",
            primitive_id="primitive.closed_shape_boundary_event_2d",
            inputs=("query_points", "closed_shape_edges"),
            outputs=("topology_face_ids", "topology_event_mask"),
            backend_contract=_topology_backend_contract(),
            phase="rt_traversal",
            lowering_hints=LoweringHints(),
            capacity_policy=_topology_capacity_policy(),
            same_contract_key=M5_TOPOLOGY_CONTRACT_KEY,
        ),
        _topology_compaction_node(),
    )
    return prepare_graph(
        graph_id="point_location_topology_pilot",
        values=values,
        nodes=nodes,
        phase_markers=_required_phases(),
        target_backends=("optix", "embree"),
    )


def _edge_intersection_topology_graph() -> PreparedGraph:
    values = (
        GraphValue(
            name="left_edges",
            kind="geometry",
            dtype="struct:segment2d",
            shape=("left_count",),
            storage="host",
            residency="host_resident",
            lifetime="caller_retained",
            consumers=("edge_event_producer",),
        ),
        GraphValue(
            name="right_edges",
            kind="geometry",
            dtype="struct:segment2d",
            shape=("right_count",),
            storage="host",
            residency="host_resident",
            lifetime="caller_retained",
            consumers=("edge_event_producer",),
        ),
        *_topology_output_values("edge_event_producer"),
        _selected_face_value(),
    )
    nodes = (
        PrimitiveNode(
            node_id="edge_event_producer",
            primitive_id="primitive.segment_intersect_2d",
            inputs=("left_edges", "right_edges"),
            outputs=("topology_face_ids", "topology_event_mask"),
            backend_contract=_topology_backend_contract(),
            phase="rt_traversal",
            lowering_hints=LoweringHints(),
            capacity_policy=_topology_capacity_policy(),
            same_contract_key=M5_TOPOLOGY_CONTRACT_KEY,
        ),
        _topology_compaction_node(),
    )
    return prepare_graph(
        graph_id="edge_intersection_topology_pilot",
        values=values,
        nodes=nodes,
        phase_markers=_required_phases(),
        target_backends=("optix", "embree"),
    )


def _topology_output_values(producer: str) -> tuple[GraphValue, GraphValue]:
    return (
        GraphValue(
            name="topology_face_ids",
            kind="topology_stream",
            dtype="int64",
            shape=("event_count",),
            storage="host",
            residency="host_resident",
            lifetime="session_retained",
            producer=producer,
            consumers=("topology_compaction",),
            capacity="event_capacity",
            overflow_policy="fail_closed",
            materialization_policy="already_materialized",
        ),
        GraphValue(
            name="topology_event_mask",
            kind="status",
            dtype="bool",
            shape=("event_count",),
            storage="host",
            residency="host_resident",
            lifetime="session_retained",
            producer=producer,
            consumers=("topology_compaction",),
            capacity="event_capacity",
            overflow_policy="fail_closed",
            materialization_policy="already_materialized",
        ),
    )


def _selected_face_value() -> GraphValue:
    return GraphValue(
        name="selected_face_ids",
        kind="summary",
        dtype="int64",
        shape=("selected_count",),
        storage="host",
        residency="host_resident",
        lifetime="session_retained",
        producer="topology_compaction",
        materialization_policy="already_materialized",
    )


def _topology_compaction_node() -> ContinuationNode:
    return ContinuationNode(
        node_id="topology_compaction",
        operation=M5_TOPOLOGY_COMPACTION_OPERATION,
        inputs=("topology_face_ids", "topology_event_mask"),
        outputs=("selected_face_ids",),
        phase="continuation_or_reduction",
        deterministic=True,
        capacity_policy=CapacityPolicy(
            capacity_value="event_capacity",
            overflow_policy="fail_closed",
            complete_candidate_coverage_required=True,
        ),
    )


def _topology_backend_contract() -> BackendContract:
    return BackendContract(
        contract_id=M5_TOPOLOGY_CONTRACT_KEY,
        allowed_backends=("optix", "embree"),
        input_contract=("geometry_a", "geometry_b"),
        output_contract=("topology_face_ids", "topology_event_mask", "selected_face_ids"),
        precision_policy="float32_with_explicit_tie_policy",
        determinism_policy="stable_event_order_with_explicit_boundary_policy",
    )


def _topology_capacity_policy() -> CapacityPolicy:
    return CapacityPolicy(
        capacity_value="event_capacity",
        overflow_policy="fail_closed",
        complete_candidate_coverage_required=True,
    )


def _required_phases() -> tuple[PhaseMarker, ...]:
    return (
        PhaseMarker("prepare", "prepare graph metadata", setup_candidate=True),
        PhaseMarker("build", "build backend structures", setup_candidate=True),
        PhaseMarker("upload", "upload inputs", setup_candidate=True),
        PhaseMarker("query_prepare", "prepare query state", setup_candidate=True),
        PhaseMarker("rt_traversal", "run topology traversal", steady_state_candidate=True),
        PhaseMarker("stream_handoff", "handoff topology streams", steady_state_candidate=True),
        PhaseMarker("continuation_or_reduction", "compact topology events", steady_state_candidate=True),
        PhaseMarker("download_or_materialization", "materialize explicit topology output"),
        PhaseMarker("validation", "validate topology contract"),
        PhaseMarker("host_wrapper", "host wrapper timing"),
    )
