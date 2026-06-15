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


M4_COMPONENT_UNION_OPERATION = "continuation.component_union"
M4_LOCAL_PREP_STATUS = "m4_local_graph_reuse_ready_pod_evidence_pending"


def m4_component_union_pilot_graphs() -> tuple[PreparedGraph, PreparedGraph]:
    """Return two no-execution M4 graphs sharing one generic continuation."""

    return (
        _fixed_radius_component_graph(),
        _generic_edge_component_graph(),
    )


def validate_m4_component_union_reuse() -> dict[str, object]:
    graphs = m4_component_union_pilot_graphs()
    operations = tuple(
        node.operation
        for graph in graphs
        for node in graph.nodes
        if isinstance(node, ContinuationNode)
    )
    if operations != (M4_COMPONENT_UNION_OPERATION, M4_COMPONENT_UNION_OPERATION):
        raise GraphValidationError("M4 pilot graphs must reuse the same component-union continuation")
    graph_ids = tuple(graph.graph_id for graph in graphs)
    return {
        "status": M4_LOCAL_PREP_STATUS,
        "graph_ids": graph_ids,
        "graph_count": len(graphs),
        "shared_continuation_operation": M4_COMPONENT_UNION_OPERATION,
        "partner_nodes_present": any(
            node.to_metadata()["node_type"] == "PartnerNode"
            for graph in graphs
            for node in graph.nodes
        ),
        "target_backends": tuple(graph.target_backends for graph in graphs),
        "pod_evidence_required": True,
        "public_speedup_claim_authorized": False,
    }


def _fixed_radius_component_graph() -> PreparedGraph:
    values = (
        GraphValue(
            name="source_points",
            kind="geometry",
            dtype="struct:point2d",
            shape=("source_count",),
            storage="host",
            residency="host_resident",
            lifetime="caller_retained",
            consumers=("candidate_edge_producer",),
        ),
        GraphValue(
            name="query_points",
            kind="geometry",
            dtype="struct:point2d",
            shape=("query_count",),
            storage="host",
            residency="host_resident",
            lifetime="caller_retained",
            consumers=("candidate_edge_producer",),
        ),
        GraphValue(
            name="edge_source_ids",
            kind="candidate_stream",
            dtype="int64",
            shape=("edge_count",),
            storage="host",
            residency="host_resident",
            lifetime="session_retained",
            producer="candidate_edge_producer",
            consumers=("component_union",),
            capacity="edge_capacity",
            overflow_policy="fail_closed",
            materialization_policy="already_materialized",
        ),
        GraphValue(
            name="edge_target_ids",
            kind="candidate_stream",
            dtype="int64",
            shape=("edge_count",),
            storage="host",
            residency="host_resident",
            lifetime="session_retained",
            producer="candidate_edge_producer",
            consumers=("component_union",),
            capacity="edge_capacity",
            overflow_policy="fail_closed",
            materialization_policy="already_materialized",
        ),
        GraphValue(
            name="component_ids",
            kind="summary",
            dtype="int64",
            shape=("node_count",),
            storage="host",
            residency="host_resident",
            lifetime="session_retained",
            producer="component_union",
            materialization_policy="already_materialized",
        ),
    )
    nodes = (
        PrimitiveNode(
            node_id="candidate_edge_producer",
            primitive_id="primitive.fixed_radius_candidate_2d",
            inputs=("source_points", "query_points"),
            outputs=("edge_source_ids", "edge_target_ids"),
            backend_contract=_component_edge_backend_contract(),
            phase="rt_traversal",
            lowering_hints=LoweringHints(),
            capacity_policy=_edge_capacity_policy(),
            same_contract_key="component_edge_contract_v1",
        ),
        _component_union_node(),
    )
    return prepare_graph(
        graph_id="fixed_radius_component_pilot",
        values=values,
        nodes=nodes,
        phase_markers=_required_phases(),
        target_backends=("optix", "embree"),
    )


def _generic_edge_component_graph() -> PreparedGraph:
    values = (
        GraphValue(
            name="edge_rows",
            kind="row_stream",
            dtype="struct:edge_pair",
            shape=("edge_count",),
            storage="host",
            residency="host_resident",
            lifetime="caller_retained",
            consumers=("edge_row_adapter",),
            capacity="edge_capacity",
            overflow_policy="fail_closed",
        ),
        GraphValue(
            name="edge_source_ids",
            kind="candidate_stream",
            dtype="int64",
            shape=("edge_count",),
            storage="host",
            residency="host_resident",
            lifetime="session_retained",
            producer="edge_row_adapter",
            consumers=("component_union",),
            capacity="edge_capacity",
            overflow_policy="fail_closed",
            materialization_policy="already_materialized",
        ),
        GraphValue(
            name="edge_target_ids",
            kind="candidate_stream",
            dtype="int64",
            shape=("edge_count",),
            storage="host",
            residency="host_resident",
            lifetime="session_retained",
            producer="edge_row_adapter",
            consumers=("component_union",),
            capacity="edge_capacity",
            overflow_policy="fail_closed",
            materialization_policy="already_materialized",
        ),
        GraphValue(
            name="component_ids",
            kind="summary",
            dtype="int64",
            shape=("node_count",),
            storage="host",
            residency="host_resident",
            lifetime="session_retained",
            producer="component_union",
            materialization_policy="already_materialized",
        ),
    )
    nodes = (
        PrimitiveNode(
            node_id="edge_row_adapter",
            primitive_id="primitive.generic_row_stream",
            inputs=("edge_rows",),
            outputs=("edge_source_ids", "edge_target_ids"),
            backend_contract=_component_edge_backend_contract(),
            phase="stream_handoff",
            lowering_hints=LoweringHints(),
            capacity_policy=_edge_capacity_policy(),
            same_contract_key="component_edge_contract_v1",
        ),
        _component_union_node(),
    )
    return prepare_graph(
        graph_id="generic_edge_component_pilot",
        values=values,
        nodes=nodes,
        phase_markers=_required_phases(),
        target_backends=("cpu", "optix", "embree"),
    )


def _component_union_node() -> ContinuationNode:
    return ContinuationNode(
        node_id="component_union",
        operation=M4_COMPONENT_UNION_OPERATION,
        inputs=("edge_source_ids", "edge_target_ids"),
        outputs=("component_ids",),
        phase="continuation_or_reduction",
        deterministic=True,
        capacity_policy=CapacityPolicy(
            capacity_value="node_count",
            overflow_policy="fail_closed",
            complete_candidate_coverage_required=True,
        ),
    )


def _component_edge_backend_contract() -> BackendContract:
    return BackendContract(
        contract_id="component_edge_contract_v1",
        allowed_backends=("cpu", "optix", "embree"),
        input_contract=("edge_sources", "edge_targets"),
        output_contract=("component_ids",),
        precision_policy="integer_ids_exact",
        determinism_policy="stable_lowest_id_component_label",
    )


def _edge_capacity_policy() -> CapacityPolicy:
    return CapacityPolicy(
        capacity_value="edge_capacity",
        overflow_policy="fail_closed",
        complete_candidate_coverage_required=True,
    )


def _required_phases() -> tuple[PhaseMarker, ...]:
    return (
        PhaseMarker("prepare", "prepare graph metadata", setup_candidate=True),
        PhaseMarker("build", "build backend structures", setup_candidate=True),
        PhaseMarker("upload", "upload inputs", setup_candidate=True),
        PhaseMarker("query_prepare", "prepare query state", setup_candidate=True),
        PhaseMarker("rt_traversal", "run traversal", steady_state_candidate=True),
        PhaseMarker("stream_handoff", "handoff streams", steady_state_candidate=True),
        PhaseMarker("continuation_or_reduction", "run shared continuation", steady_state_candidate=True),
        PhaseMarker("download_or_materialization", "materialize explicit outputs"),
        PhaseMarker("validation", "validate component labels"),
        PhaseMarker("host_wrapper", "host wrapper timing"),
    )
