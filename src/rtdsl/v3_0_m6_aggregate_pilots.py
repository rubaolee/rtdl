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


M6_VECTOR_SUM_OPERATION = "continuation.vector_sum"
M6_FRONTIER_CONTRACT_KEY = "aggregate_frontier_vector_contract_v1"
M6_LOCAL_PREP_STATUS = "m6_local_frontier_vector_graphs_ready_pod_evidence_pending"


def m6_frontier_vector_pilot_graphs() -> tuple[PreparedGraph, PreparedGraph]:
    """Return no-execution M6 graphs sharing generic vector-sum continuation."""

    return (
        _aggregate_frontier_vector_graph(),
        _generic_frontier_vector_graph(),
    )


def validate_m6_frontier_vector_pilots() -> dict[str, object]:
    graphs = m6_frontier_vector_pilot_graphs()
    continuation_ops = tuple(
        node.operation
        for graph in graphs
        for node in graph.nodes
        if isinstance(node, ContinuationNode)
    )
    if continuation_ops != (M6_VECTOR_SUM_OPERATION, M6_VECTOR_SUM_OPERATION):
        raise GraphValidationError("M6 pilots must reuse the same vector-sum continuation")
    return {
        "status": M6_LOCAL_PREP_STATUS,
        "graph_ids": tuple(graph.graph_id for graph in graphs),
        "graph_count": len(graphs),
        "shared_frontier_contract": M6_FRONTIER_CONTRACT_KEY,
        "shared_continuation_operation": M6_VECTOR_SUM_OPERATION,
        "partner_nodes_present": any(
            node.to_metadata()["node_type"] == "PartnerNode"
            for graph in graphs
            for node in graph.nodes
        ),
        "target_backends": tuple(graph.target_backends for graph in graphs),
        "pod_evidence_required": True,
        "public_speedup_claim_authorized": False,
    }


def _aggregate_frontier_vector_graph() -> PreparedGraph:
    values = (
        GraphValue(
            name="source_nodes",
            kind="geometry",
            dtype="struct:weighted_point2d",
            shape=("source_count",),
            storage="host",
            residency="host_resident",
            lifetime="caller_retained",
            consumers=("frontier_producer",),
        ),
        GraphValue(
            name="query_nodes",
            kind="geometry",
            dtype="struct:weighted_point2d",
            shape=("query_count",),
            storage="host",
            residency="host_resident",
            lifetime="caller_retained",
            consumers=("frontier_producer",),
        ),
        *_frontier_output_values("frontier_producer"),
        *_vector_output_values(),
    )
    nodes = (
        PrimitiveNode(
            node_id="frontier_producer",
            primitive_id="primitive.aggregate_frontier_2d",
            inputs=("source_nodes", "query_nodes"),
            outputs=("frontier_group_ids", "frontier_vector_x", "frontier_vector_y"),
            backend_contract=_frontier_backend_contract(),
            phase="rt_traversal",
            lowering_hints=LoweringHints(),
            capacity_policy=_frontier_capacity_policy(),
            same_contract_key=M6_FRONTIER_CONTRACT_KEY,
        ),
        _vector_sum_node(),
    )
    return prepare_graph(
        graph_id="aggregate_frontier_vector_pilot",
        values=values,
        nodes=nodes,
        phase_markers=_required_phases(),
        target_backends=("optix", "embree"),
    )


def _generic_frontier_vector_graph() -> PreparedGraph:
    values = (
        GraphValue(
            name="frontier_rows",
            kind="row_stream",
            dtype="struct:frontier_vector_row",
            shape=("frontier_count",),
            storage="host",
            residency="host_resident",
            lifetime="caller_retained",
            consumers=("frontier_row_adapter",),
            capacity="frontier_capacity",
            overflow_policy="fail_closed",
        ),
        *_frontier_output_values("frontier_row_adapter"),
        *_vector_output_values(),
    )
    nodes = (
        PrimitiveNode(
            node_id="frontier_row_adapter",
            primitive_id="primitive.generic_row_stream",
            inputs=("frontier_rows",),
            outputs=("frontier_group_ids", "frontier_vector_x", "frontier_vector_y"),
            backend_contract=_frontier_backend_contract(),
            phase="stream_handoff",
            lowering_hints=LoweringHints(),
            capacity_policy=_frontier_capacity_policy(),
            same_contract_key=M6_FRONTIER_CONTRACT_KEY,
        ),
        _vector_sum_node(),
    )
    return prepare_graph(
        graph_id="generic_frontier_vector_pilot",
        values=values,
        nodes=nodes,
        phase_markers=_required_phases(),
        target_backends=("cpu", "optix", "embree"),
    )


def _frontier_output_values(producer: str) -> tuple[GraphValue, GraphValue, GraphValue]:
    return (
        GraphValue(
            name="frontier_group_ids",
            kind="row_stream",
            dtype="int64",
            shape=("frontier_count",),
            storage="host",
            residency="host_resident",
            lifetime="session_retained",
            producer=producer,
            consumers=("frontier_vector_sum",),
            capacity="frontier_capacity",
            overflow_policy="fail_closed",
            materialization_policy="already_materialized",
        ),
        GraphValue(
            name="frontier_vector_x",
            kind="row_stream",
            dtype="float64",
            shape=("frontier_count",),
            storage="host",
            residency="host_resident",
            lifetime="session_retained",
            producer=producer,
            consumers=("frontier_vector_sum",),
            capacity="frontier_capacity",
            overflow_policy="fail_closed",
            materialization_policy="already_materialized",
        ),
        GraphValue(
            name="frontier_vector_y",
            kind="row_stream",
            dtype="float64",
            shape=("frontier_count",),
            storage="host",
            residency="host_resident",
            lifetime="session_retained",
            producer=producer,
            consumers=("frontier_vector_sum",),
            capacity="frontier_capacity",
            overflow_policy="fail_closed",
            materialization_policy="already_materialized",
        ),
    )


def _vector_output_values() -> tuple[GraphValue, GraphValue]:
    return (
        GraphValue(
            name="vector_sum_x",
            kind="summary",
            dtype="float64",
            shape=("group_count",),
            storage="host",
            residency="host_resident",
            lifetime="session_retained",
            producer="frontier_vector_sum",
            materialization_policy="already_materialized",
        ),
        GraphValue(
            name="vector_sum_y",
            kind="summary",
            dtype="float64",
            shape=("group_count",),
            storage="host",
            residency="host_resident",
            lifetime="session_retained",
            producer="frontier_vector_sum",
            materialization_policy="already_materialized",
        ),
    )


def _vector_sum_node() -> ContinuationNode:
    return ContinuationNode(
        node_id="frontier_vector_sum",
        operation=M6_VECTOR_SUM_OPERATION,
        inputs=("frontier_group_ids", "frontier_vector_x", "frontier_vector_y"),
        outputs=("vector_sum_x", "vector_sum_y"),
        phase="continuation_or_reduction",
        deterministic=True,
        capacity_policy=CapacityPolicy(
            capacity_value="group_count",
            overflow_policy="fail_closed",
            complete_candidate_coverage_required=True,
        ),
    )


def _frontier_backend_contract() -> BackendContract:
    return BackendContract(
        contract_id=M6_FRONTIER_CONTRACT_KEY,
        allowed_backends=("cpu", "optix", "embree"),
        input_contract=("frontier_source", "frontier_query"),
        output_contract=("frontier_group_ids", "frontier_vector_x", "frontier_vector_y", "vector_sum_x", "vector_sum_y"),
        precision_policy="float64_continuation_explicit",
        determinism_policy="stable_group_order",
    )


def _frontier_capacity_policy() -> CapacityPolicy:
    return CapacityPolicy(
        capacity_value="frontier_capacity",
        overflow_policy="fail_closed",
        complete_candidate_coverage_required=True,
    )


def _required_phases() -> tuple[PhaseMarker, ...]:
    return (
        PhaseMarker("prepare", "prepare graph metadata", setup_candidate=True),
        PhaseMarker("build", "build backend structures", setup_candidate=True),
        PhaseMarker("upload", "upload inputs", setup_candidate=True),
        PhaseMarker("query_prepare", "prepare query state", setup_candidate=True),
        PhaseMarker("rt_traversal", "run frontier traversal", steady_state_candidate=True),
        PhaseMarker("stream_handoff", "handoff frontier streams", steady_state_candidate=True),
        PhaseMarker("continuation_or_reduction", "sum frontier vectors", steady_state_candidate=True),
        PhaseMarker("download_or_materialization", "materialize explicit vector output"),
        PhaseMarker("validation", "validate vector sums"),
        PhaseMarker("host_wrapper", "host wrapper timing"),
    )
