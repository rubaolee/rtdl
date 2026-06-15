from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any, Mapping, Sequence
import re


V3_EXECUTION_GRAPH_IR_VERSION = "rtdl.v3_0.execution_graph_ir.m1"
V3_EXECUTION_GRAPH_STATUS = "m2_no_execution_skeleton"

VALUE_KINDS = (
    "geometry",
    "parameter",
    "prepared_handle",
    "candidate_stream",
    "hit_stream",
    "topology_stream",
    "row_stream",
    "summary",
    "status",
    "partner_output",
    "validation_output",
)
STORAGE_KINDS = ("host", "cuda", "embree_cpu", "backend_native", "dual", "opaque")
RESIDENCY_STATES = (
    "host_resident",
    "device_resident",
    "backend_resident",
    "dual_resident",
    "materialized",
    "unknown_pending_evidence",
)
LIFETIME_STATES = (
    "caller_retained",
    "session_retained",
    "borrowed",
    "native_owned",
    "partner_owned",
    "released",
)
OVERFLOW_POLICIES = (
    "not_applicable",
    "fail_closed",
    "grow_explicitly",
    "truncate_forbidden",
)
MATERIALIZATION_POLICIES = (
    "forbidden",
    "allowed_explicit",
    "required",
    "already_materialized",
)
STREAM_ORDERINGS = ("same_stream", "event_wait", "host_synchronized", "not_proven")
BACKENDS = ("cpu", "embree", "optix", "hiprt", "apple_rt", "vulkan")
PARTNERS = ("python_reference", "numba", "cupy", "triton", "torch")
PREPARED_GRAPH_STATES = ("pending_validation", "validated", "prepared", "invalidated", "closed")
MATERIALIZE_DIRECTIONS = (
    "host_to_device",
    "device_to_host",
    "backend_to_host",
    "host_to_backend",
    "device_to_device",
)
REQUIRED_PHASE_NAMES = (
    "prepare",
    "build",
    "upload",
    "query_prepare",
    "rt_traversal",
    "stream_handoff",
    "continuation_or_reduction",
    "download_or_materialization",
    "validation",
    "host_wrapper",
)
PRIMITIVE_IDS = (
    "primitive.aabb_query_2d",
    "primitive.ray_triangle_intersect_3d",
    "primitive.segment_intersect_2d",
    "primitive.closed_shape_boundary_event_2d",
    "primitive.fixed_radius_candidate_2d",
    "primitive.fixed_radius_candidate_3d",
    "primitive.aggregate_frontier_2d",
    "primitive.aggregate_frontier_3d",
    "primitive.generic_row_stream",
    "primitive.generic_hit_stream",
)
CONTINUATION_OPERATIONS = (
    "continuation.compact_mask",
    "continuation.grouped_count",
    "continuation.grouped_sum",
    "continuation.grouped_min",
    "continuation.grouped_max",
    "continuation.grouped_argmin",
    "continuation.grouped_argmax",
    "continuation.grouped_topk",
    "continuation.component_union",
    "continuation.frontier_expand",
    "continuation.vector_sum",
    "continuation.status_reduce",
)
CLAIM_BOUNDARY_KEYS = (
    "public_speedup_authorized",
    "rt_core_speedup_authorized",
    "true_zero_copy_authorized",
    "same_stream_claim_authorized",
    "device_resident_claim_authorized",
    "hidden_partner_selection_authorized",
    "automatic_partner_selection_authorized",
    "automatic_backend_selection_authorized",
    "app_specific_native_engine_authorized",
    "raw_optix_callback_user_api_authorized",
    "paper_reproduction_claim_authorized",
)

_FORBIDDEN_PUBLIC_TOKENS = (
    "rayjoin",
    "lsi",
    "pip",
    "overlay",
    "dbscan",
    "rt_dbscan",
    "barnes",
    "barnes_hut",
    "raydb",
    "database",
    "sql",
    "robot",
    "robot_collision",
    "contact",
    "contact_manifold",
    "librts",
    "rtnn",
    "hausdorff",
    "triangle_counting",
    "paper",
    "author",
)
_COMPACT_TOKEN_MATCHES = {"rayjoin", "rt_dbscan", "barnes_hut", "robot_collision", "contact_manifold"}


class GraphValidationError(ValueError):
    """Raised when V3 execution-graph metadata violates the M1 contract."""


@dataclass(frozen=True)
class ClaimBoundary:
    public_speedup_authorized: bool = False
    rt_core_speedup_authorized: bool = False
    true_zero_copy_authorized: bool = False
    same_stream_claim_authorized: bool = False
    device_resident_claim_authorized: bool = False
    hidden_partner_selection_authorized: bool = False
    automatic_partner_selection_authorized: bool = False
    automatic_backend_selection_authorized: bool = False
    app_specific_native_engine_authorized: bool = False
    raw_optix_callback_user_api_authorized: bool = False
    paper_reproduction_claim_authorized: bool = False

    def __post_init__(self) -> None:
        for key in CLAIM_BOUNDARY_KEYS:
            if bool(getattr(self, key)):
                raise GraphValidationError(f"V3 M2 claim boundary must not authorize {key}")

    def to_metadata(self) -> dict[str, bool]:
        return {key: bool(getattr(self, key)) for key in CLAIM_BOUNDARY_KEYS}


@dataclass(frozen=True)
class PartnerPolicy:
    explicit_partner_required: bool = False
    best_partner: str | None = None
    numba_reference_required: bool = False
    numba_omission_justification: str | None = None
    partner_timing_separated: bool = False
    auto_selection_allowed: bool = False
    allowed_partners: tuple[str, ...] = PARTNERS
    benchmark_requires_dual_partner_rows: bool = False

    def __post_init__(self) -> None:
        partners = tuple(str(partner) for partner in self.allowed_partners)
        _validate_subset(partners, PARTNERS, "allowed_partners")
        best_partner = None if self.best_partner is None else str(self.best_partner)
        if best_partner is not None and best_partner not in partners:
            raise GraphValidationError("best_partner must be present in allowed_partners")
        if self.auto_selection_allowed:
            raise GraphValidationError("V3 M2 partner policy forbids automatic partner selection")
        if self.benchmark_requires_dual_partner_rows:
            if not self.explicit_partner_required:
                raise GraphValidationError("benchmark partner policy requires explicit partner selection")
            if best_partner is None:
                raise GraphValidationError("benchmark partner policy requires best_partner")
            if not self.partner_timing_separated:
                raise GraphValidationError("benchmark partner policy requires separated partner timing")
            if not self.numba_reference_required and not _nonempty(self.numba_omission_justification):
                raise GraphValidationError("omitting a Numba reference requires written justification")
        object.__setattr__(self, "allowed_partners", partners)
        object.__setattr__(self, "best_partner", best_partner)

    def to_metadata(self) -> dict[str, object]:
        return {
            "explicit_partner_required": bool(self.explicit_partner_required),
            "best_partner": self.best_partner,
            "numba_reference_required": bool(self.numba_reference_required),
            "numba_omission_justification": self.numba_omission_justification,
            "partner_timing_separated": bool(self.partner_timing_separated),
            "auto_selection_allowed": bool(self.auto_selection_allowed),
            "allowed_partners": self.allowed_partners,
            "benchmark_requires_dual_partner_rows": bool(self.benchmark_requires_dual_partner_rows),
        }


@dataclass(frozen=True)
class StreamBinding:
    stream_id: str
    backend_stream_handle: int | None = None
    ordering: str = "not_proven"
    producer_event: str | None = None
    consumer_wait: str | None = None
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not _nonempty(self.stream_id):
            raise GraphValidationError("stream binding requires stream_id")
        if self.ordering not in STREAM_ORDERINGS:
            raise GraphValidationError("unsupported stream ordering")
        evidence = tuple(str(item) for item in self.evidence)
        if self.ordering == "same_stream" and not evidence:
            raise GraphValidationError("same_stream ordering requires CUDA event or Nsight evidence")
        if self.ordering == "event_wait":
            if not _nonempty(self.producer_event) or not _nonempty(self.consumer_wait):
                raise GraphValidationError("event_wait ordering requires producer_event and consumer_wait")
            if not evidence:
                raise GraphValidationError("event_wait ordering requires evidence")
        object.__setattr__(self, "evidence", evidence)

    def to_metadata(self) -> dict[str, object]:
        return {
            "stream_id": self.stream_id,
            "backend_stream_handle": self.backend_stream_handle,
            "ordering": self.ordering,
            "producer_event": self.producer_event,
            "consumer_wait": self.consumer_wait,
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class GraphValue:
    name: str
    kind: str
    dtype: str
    shape: tuple[int | str, ...]
    storage: str
    residency: str
    lifetime: str
    stream_binding: StreamBinding | None = None
    producer: str | None = None
    consumers: tuple[str, ...] = ()
    capacity: int | str | None = None
    overflow_policy: str = "not_applicable"
    materialization_policy: str = "allowed_explicit"
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        validate_v3_public_name(self.name, label="graph value")
        if self.kind not in VALUE_KINDS:
            raise GraphValidationError("unsupported graph value kind")
        if not _nonempty(self.dtype):
            raise GraphValidationError("graph value requires dtype")
        if self.storage not in STORAGE_KINDS:
            raise GraphValidationError("unsupported graph value storage")
        if self.residency not in RESIDENCY_STATES:
            raise GraphValidationError("unsupported graph value residency")
        if self.lifetime not in LIFETIME_STATES:
            raise GraphValidationError("unsupported graph value lifetime")
        if self.overflow_policy not in OVERFLOW_POLICIES:
            raise GraphValidationError("unsupported graph value overflow policy")
        if self.materialization_policy not in MATERIALIZATION_POLICIES:
            raise GraphValidationError("unsupported graph value materialization policy")
        shape = tuple(self.shape)
        if any(isinstance(dim, int) and dim < 0 for dim in shape):
            raise GraphValidationError("graph value shape dimensions must be non-negative")
        if (
            self.residency == "device_resident"
            and self.kind != "prepared_handle"
            and self.stream_binding is None
        ):
            raise GraphValidationError("device-resident graph values require stream binding")
        if self.capacity is not None and isinstance(self.capacity, int) and self.capacity < 0:
            raise GraphValidationError("graph value capacity must be non-negative")
        if self.overflow_policy != "not_applicable" and self.capacity is None:
            raise GraphValidationError("bounded overflow policy requires capacity")
        object.__setattr__(self, "shape", shape)
        object.__setattr__(self, "consumers", tuple(str(item) for item in self.consumers))
        object.__setattr__(self, "evidence", tuple(str(item) for item in self.evidence))

    def to_metadata(self) -> dict[str, object]:
        return {
            "name": self.name,
            "kind": self.kind,
            "dtype": self.dtype,
            "shape": self.shape,
            "storage": self.storage,
            "residency": self.residency,
            "lifetime": self.lifetime,
            "stream_binding": None if self.stream_binding is None else self.stream_binding.to_metadata(),
            "producer": self.producer,
            "consumers": self.consumers,
            "capacity": self.capacity,
            "overflow_policy": self.overflow_policy,
            "materialization_policy": self.materialization_policy,
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class PhaseMarker:
    name: str
    role: str
    required: bool = True
    steady_state_candidate: bool = False
    setup_candidate: bool = False
    evidence_required: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not _nonempty(self.name):
            raise GraphValidationError("phase marker requires name")
        if not _nonempty(self.role):
            raise GraphValidationError("phase marker requires role")
        object.__setattr__(self, "evidence_required", tuple(str(item) for item in self.evidence_required))

    def to_metadata(self) -> dict[str, object]:
        return {
            "name": self.name,
            "role": self.role,
            "required": bool(self.required),
            "steady_state_candidate": bool(self.steady_state_candidate),
            "setup_candidate": bool(self.setup_candidate),
            "evidence_required": self.evidence_required,
        }


@dataclass(frozen=True)
class BackendContract:
    contract_id: str
    allowed_backends: tuple[str, ...]
    input_contract: tuple[str, ...]
    output_contract: tuple[str, ...]
    precision_policy: str
    determinism_policy: str

    def __post_init__(self) -> None:
        if not _nonempty(self.contract_id):
            raise GraphValidationError("backend contract requires contract_id")
        backends = tuple(str(backend) for backend in self.allowed_backends)
        _validate_subset(backends, BACKENDS, "backend contract allowed_backends")
        if not backends:
            raise GraphValidationError("backend contract requires at least one backend")
        if not self.input_contract or not self.output_contract:
            raise GraphValidationError("backend contract requires input and output contracts")
        if not _nonempty(self.precision_policy) or not _nonempty(self.determinism_policy):
            raise GraphValidationError("backend contract requires precision and determinism policy")
        object.__setattr__(self, "allowed_backends", backends)
        object.__setattr__(self, "input_contract", tuple(str(item) for item in self.input_contract))
        object.__setattr__(self, "output_contract", tuple(str(item) for item in self.output_contract))

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "allowed_backends": self.allowed_backends,
            "input_contract": self.input_contract,
            "output_contract": self.output_contract,
            "precision_policy": self.precision_policy,
            "determinism_policy": self.determinism_policy,
        }


@dataclass(frozen=True)
class LoweringHints:
    preferred_build_quality: str | None = None
    preferred_traversal_mode: str | None = None
    allow_internal_backend_programs: bool = True
    allow_user_raw_callbacks: bool = False

    def __post_init__(self) -> None:
        if self.allow_user_raw_callbacks:
            raise GraphValidationError("V3 stable API forbids user raw backend callbacks")

    def to_metadata(self) -> dict[str, object]:
        return {
            "preferred_build_quality": self.preferred_build_quality,
            "preferred_traversal_mode": self.preferred_traversal_mode,
            "allow_internal_backend_programs": bool(self.allow_internal_backend_programs),
            "allow_user_raw_callbacks": bool(self.allow_user_raw_callbacks),
        }


@dataclass(frozen=True)
class CapacityPolicy:
    capacity_value: int | str | None = None
    overflow_policy: str = "not_applicable"
    complete_candidate_coverage_required: bool = False

    def __post_init__(self) -> None:
        if self.overflow_policy not in OVERFLOW_POLICIES:
            raise GraphValidationError("unsupported capacity overflow policy")
        if self.capacity_value is not None and isinstance(self.capacity_value, int) and self.capacity_value < 0:
            raise GraphValidationError("capacity_value must be non-negative")
        if self.overflow_policy != "not_applicable" and self.capacity_value is None:
            raise GraphValidationError("capacity policy with overflow handling requires capacity_value")

    def to_metadata(self) -> dict[str, object]:
        return {
            "capacity_value": self.capacity_value,
            "overflow_policy": self.overflow_policy,
            "complete_candidate_coverage_required": bool(self.complete_candidate_coverage_required),
        }


@dataclass(frozen=True)
class PrimitiveNode:
    node_id: str
    primitive_id: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    backend_contract: BackendContract
    phase: str
    lowering_hints: LoweringHints
    capacity_policy: CapacityPolicy
    same_contract_key: str

    def __post_init__(self) -> None:
        _validate_node_id(self.node_id)
        if self.primitive_id not in PRIMITIVE_IDS:
            raise GraphValidationError("unsupported primitive_id")
        _validate_names(self.inputs, "primitive inputs")
        _validate_names(self.outputs, "primitive outputs")
        if not _nonempty(self.phase):
            raise GraphValidationError("primitive node requires phase")
        if not _nonempty(self.same_contract_key):
            raise GraphValidationError("primitive node requires same_contract_key")
        object.__setattr__(self, "inputs", tuple(str(item) for item in self.inputs))
        object.__setattr__(self, "outputs", tuple(str(item) for item in self.outputs))

    def to_metadata(self) -> dict[str, object]:
        return {
            "node_type": "PrimitiveNode",
            "node_id": self.node_id,
            "primitive_id": self.primitive_id,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "backend_contract": self.backend_contract.to_metadata(),
            "phase": self.phase,
            "lowering_hints": self.lowering_hints.to_metadata(),
            "capacity_policy": self.capacity_policy.to_metadata(),
            "same_contract_key": self.same_contract_key,
        }


@dataclass(frozen=True)
class ContinuationNode:
    node_id: str
    operation: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    phase: str
    stream_binding: StreamBinding | None = None
    deterministic: bool = True
    capacity_policy: CapacityPolicy = field(default_factory=CapacityPolicy)

    def __post_init__(self) -> None:
        _validate_node_id(self.node_id)
        if self.operation not in CONTINUATION_OPERATIONS:
            raise GraphValidationError("unsupported continuation operation")
        _validate_names(self.inputs, "continuation inputs")
        _validate_names(self.outputs, "continuation outputs")
        if not _nonempty(self.phase):
            raise GraphValidationError("continuation node requires phase")
        object.__setattr__(self, "inputs", tuple(str(item) for item in self.inputs))
        object.__setattr__(self, "outputs", tuple(str(item) for item in self.outputs))

    def to_metadata(self) -> dict[str, object]:
        return {
            "node_type": "ContinuationNode",
            "node_id": self.node_id,
            "operation": self.operation,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "phase": self.phase,
            "stream_binding": None if self.stream_binding is None else self.stream_binding.to_metadata(),
            "deterministic": bool(self.deterministic),
            "capacity_policy": self.capacity_policy.to_metadata(),
        }


@dataclass(frozen=True)
class PartnerNode:
    node_id: str
    partner: str
    operation: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    stream_binding: StreamBinding | None
    phase: str
    reference_required: bool = True
    numba_reference_required: bool = True
    omission_justification: str | None = None
    timing_separated: bool = True

    def __post_init__(self) -> None:
        _validate_node_id(self.node_id)
        if self.partner not in PARTNERS:
            raise GraphValidationError("unsupported partner")
        if self.partner == "auto":
            raise GraphValidationError("partner selection must be explicit")
        if not _nonempty(self.operation):
            raise GraphValidationError("partner node requires operation")
        _validate_names(self.inputs, "partner inputs")
        _validate_names(self.outputs, "partner outputs")
        if not _nonempty(self.phase):
            raise GraphValidationError("partner node requires phase")
        if not self.timing_separated:
            raise GraphValidationError("partner timing must be separated")
        if self.numba_reference_required and self.omission_justification is not None:
            raise GraphValidationError("Numba reference path should not carry omission justification")
        if not self.numba_reference_required and not _nonempty(self.omission_justification):
            raise GraphValidationError("omitting Numba reference requires justification")
        object.__setattr__(self, "inputs", tuple(str(item) for item in self.inputs))
        object.__setattr__(self, "outputs", tuple(str(item) for item in self.outputs))

    def to_metadata(self) -> dict[str, object]:
        return {
            "node_type": "PartnerNode",
            "node_id": self.node_id,
            "partner": self.partner,
            "operation": self.operation,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "stream_binding": None if self.stream_binding is None else self.stream_binding.to_metadata(),
            "phase": self.phase,
            "reference_required": bool(self.reference_required),
            "numba_reference_required": bool(self.numba_reference_required),
            "omission_justification": self.omission_justification,
            "timing_separated": bool(self.timing_separated),
        }


@dataclass(frozen=True)
class MaterializeNode:
    node_id: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    direction: str
    reason: str
    phase: str
    bytes: int = 0
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_node_id(self.node_id)
        _validate_names(self.inputs, "materialize inputs")
        _validate_names(self.outputs, "materialize outputs")
        if self.direction not in MATERIALIZE_DIRECTIONS:
            raise GraphValidationError("unsupported materialize direction")
        if not _nonempty(self.reason):
            raise GraphValidationError("materialize node requires reason")
        if not _nonempty(self.phase):
            raise GraphValidationError("materialize node requires phase")
        if int(self.bytes) < 0:
            raise GraphValidationError("materialize bytes must be non-negative")
        object.__setattr__(self, "inputs", tuple(str(item) for item in self.inputs))
        object.__setattr__(self, "outputs", tuple(str(item) for item in self.outputs))
        object.__setattr__(self, "bytes", int(self.bytes))
        object.__setattr__(self, "evidence", tuple(str(item) for item in self.evidence))

    def to_metadata(self) -> dict[str, object]:
        return {
            "node_type": "MaterializeNode",
            "node_id": self.node_id,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "direction": self.direction,
            "reason": self.reason,
            "phase": self.phase,
            "bytes": self.bytes,
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class ValidationNode:
    node_id: str
    contract: str
    inputs: tuple[str, ...]
    oracle: str
    tolerance: str
    phase: str
    comparison_scope: str

    def __post_init__(self) -> None:
        _validate_node_id(self.node_id)
        if not _nonempty(self.contract):
            raise GraphValidationError("validation node requires contract")
        _validate_names(self.inputs, "validation inputs")
        if not _nonempty(self.oracle):
            raise GraphValidationError("validation node requires oracle")
        if not _nonempty(self.tolerance):
            raise GraphValidationError("validation node requires tolerance")
        if not _nonempty(self.phase):
            raise GraphValidationError("validation node requires phase")
        if not _nonempty(self.comparison_scope):
            raise GraphValidationError("validation node requires comparison_scope")
        object.__setattr__(self, "inputs", tuple(str(item) for item in self.inputs))

    def to_metadata(self) -> dict[str, object]:
        return {
            "node_type": "ValidationNode",
            "node_id": self.node_id,
            "contract": self.contract,
            "inputs": self.inputs,
            "oracle": self.oracle,
            "tolerance": self.tolerance,
            "phase": self.phase,
            "comparison_scope": self.comparison_scope,
        }


GraphNode = PrimitiveNode | ContinuationNode | PartnerNode | MaterializeNode | ValidationNode


@dataclass(frozen=True)
class BackendPlan:
    backend: str
    graph_id: str
    same_contract_key: str
    lowered_nodes: tuple[str, ...]
    prepared_handles: tuple[str, ...]
    phase_markers: tuple[PhaseMarker, ...]
    unsupported_nodes: tuple[str, ...] = ()
    required_partner_nodes: tuple[str, ...] = ()
    claim_boundary: ClaimBoundary = field(default_factory=ClaimBoundary)

    def __post_init__(self) -> None:
        if self.backend not in BACKENDS:
            raise GraphValidationError("unsupported backend")
        if not _nonempty(self.graph_id) or not _nonempty(self.same_contract_key):
            raise GraphValidationError("backend plan requires graph_id and same_contract_key")
        object.__setattr__(self, "lowered_nodes", tuple(str(item) for item in self.lowered_nodes))
        object.__setattr__(self, "prepared_handles", tuple(str(item) for item in self.prepared_handles))
        object.__setattr__(self, "unsupported_nodes", tuple(str(item) for item in self.unsupported_nodes))
        object.__setattr__(self, "required_partner_nodes", tuple(str(item) for item in self.required_partner_nodes))

    def to_metadata(self) -> dict[str, object]:
        return {
            "backend": self.backend,
            "graph_id": self.graph_id,
            "same_contract_key": self.same_contract_key,
            "lowered_nodes": self.lowered_nodes,
            "prepared_handles": self.prepared_handles,
            "phase_markers": tuple(phase.to_metadata() for phase in self.phase_markers),
            "unsupported_nodes": self.unsupported_nodes,
            "required_partner_nodes": self.required_partner_nodes,
            "claim_boundary": self.claim_boundary.to_metadata(),
            "executes": False,
        }


@dataclass(frozen=True)
class PreparedGraph:
    graph_id: str
    values: tuple[GraphValue, ...]
    nodes: tuple[GraphNode, ...]
    phase_markers: tuple[PhaseMarker, ...]
    target_backends: tuple[str, ...]
    partner_policy: PartnerPolicy = field(default_factory=PartnerPolicy)
    claim_boundary: ClaimBoundary = field(default_factory=ClaimBoundary)
    backend_plan: BackendPlan | None = None
    state: str = "validated"
    validation_errors: tuple[str, ...] = ()
    ir_version: str = V3_EXECUTION_GRAPH_IR_VERSION

    def __post_init__(self) -> None:
        if self.ir_version != V3_EXECUTION_GRAPH_IR_VERSION:
            raise GraphValidationError("unexpected V3 execution graph IR version")
        if not _nonempty(self.graph_id):
            raise GraphValidationError("prepared graph requires graph_id")
        if self.state not in PREPARED_GRAPH_STATES:
            raise GraphValidationError("unsupported prepared graph state")
        backends = tuple(str(backend) for backend in self.target_backends)
        _validate_subset(backends, BACKENDS, "target_backends")
        if not backends:
            raise GraphValidationError("prepared graph requires at least one target backend")
        values = tuple(self.values)
        nodes = tuple(self.nodes)
        phases = tuple(self.phase_markers)
        _validate_graph_values(values)
        _validate_graph_nodes(values, nodes)
        _validate_graph_phases(phases, nodes)
        _validate_graph_partner_policy(nodes, self.partner_policy)
        errors = tuple(str(item) for item in self.validation_errors)
        if self.state in {"validated", "prepared"} and errors:
            raise GraphValidationError("validated or prepared graph must not carry validation errors")
        object.__setattr__(self, "target_backends", backends)
        object.__setattr__(self, "values", values)
        object.__setattr__(self, "nodes", nodes)
        object.__setattr__(self, "phase_markers", phases)
        object.__setattr__(self, "validation_errors", errors)

    @property
    def value_table(self) -> dict[str, GraphValue]:
        return {value.name: value for value in self.values}

    @property
    def validated_graph(self) -> dict[str, object]:
        return {
            "graph_id": self.graph_id,
            "ir_version": self.ir_version,
            "values": tuple(value.to_metadata() for value in self.values),
            "nodes": tuple(node.to_metadata() for node in self.nodes),
            "phase_markers": tuple(phase.to_metadata() for phase in self.phase_markers),
            "target_backends": self.target_backends,
            "partner_policy": self.partner_policy.to_metadata(),
            "claim_boundary": self.claim_boundary.to_metadata(),
        }

    def to_metadata(self) -> dict[str, object]:
        return {
            "graph_id": self.graph_id,
            "ir_version": self.ir_version,
            "status": V3_EXECUTION_GRAPH_STATUS,
            "validated_graph": self.validated_graph,
            "backend_plan": None if self.backend_plan is None else self.backend_plan.to_metadata(),
            "state": self.state,
            "value_table": {name: value.to_metadata() for name, value in self.value_table.items()},
            "phase_plan": tuple(phase.to_metadata() for phase in self.phase_markers),
            "partner_policy": self.partner_policy.to_metadata(),
            "claim_boundary": self.claim_boundary.to_metadata(),
            "validation_errors": self.validation_errors,
            "executes": False,
            "native_execution_authorized": False,
            "public_speedup_claim_authorized": False,
        }


@dataclass(frozen=True)
class ExecutionReport:
    graph_id: str
    backend: str
    partner: str
    hardware: str
    dataset: str
    scale: str
    data_start_residency: str
    warmups: int
    repeats: int
    timing_statistic: str
    phase_timings: Mapping[str, float]
    correctness_contract: str
    same_contract_key: str
    evidence_paths: tuple[str, ...] = ()
    claim_boundary: ClaimBoundary = field(default_factory=ClaimBoundary)
    ir_version: str = V3_EXECUTION_GRAPH_IR_VERSION

    def __post_init__(self) -> None:
        if self.ir_version != V3_EXECUTION_GRAPH_IR_VERSION:
            raise GraphValidationError("unexpected execution report IR version")
        if self.backend not in BACKENDS:
            raise GraphValidationError("unsupported execution report backend")
        if self.partner not in (*PARTNERS, "none"):
            raise GraphValidationError("unsupported execution report partner")
        if self.data_start_residency not in RESIDENCY_STATES:
            raise GraphValidationError("unsupported data_start_residency")
        if int(self.warmups) < 0 or int(self.repeats) <= 0:
            raise GraphValidationError("execution report warmups/repeats are invalid")
        for key, value in self.phase_timings.items():
            if not _nonempty(key) or float(value) < 0.0:
                raise GraphValidationError("execution report phase timings must be non-negative")
        if not _nonempty(self.correctness_contract) or not _nonempty(self.same_contract_key):
            raise GraphValidationError("execution report requires correctness_contract and same_contract_key")
        object.__setattr__(self, "warmups", int(self.warmups))
        object.__setattr__(self, "repeats", int(self.repeats))
        object.__setattr__(self, "evidence_paths", tuple(str(item) for item in self.evidence_paths))

    def to_metadata(self) -> dict[str, object]:
        return {
            "graph_id": self.graph_id,
            "ir_version": self.ir_version,
            "backend": self.backend,
            "partner": self.partner,
            "hardware": self.hardware,
            "dataset": self.dataset,
            "scale": self.scale,
            "data_start_residency": self.data_start_residency,
            "warmups": self.warmups,
            "repeats": self.repeats,
            "timing_statistic": self.timing_statistic,
            "phase_timings": dict(self.phase_timings),
            "correctness_contract": self.correctness_contract,
            "same_contract_key": self.same_contract_key,
            "evidence_paths": self.evidence_paths,
            "claim_boundary": self.claim_boundary.to_metadata(),
        }


def prepare_graph(
    *,
    graph_id: str,
    values: Sequence[GraphValue],
    nodes: Sequence[GraphNode],
    phase_markers: Sequence[PhaseMarker],
    target_backends: Sequence[str],
    partner_policy: PartnerPolicy | None = None,
    claim_boundary: ClaimBoundary | None = None,
    backend_plan: BackendPlan | None = None,
    state: str = "validated",
) -> PreparedGraph:
    """Validate V3 graph metadata without executing native or partner code."""

    return PreparedGraph(
        graph_id=graph_id,
        values=tuple(values),
        nodes=tuple(nodes),
        phase_markers=tuple(phase_markers),
        target_backends=tuple(target_backends),
        partner_policy=PartnerPolicy() if partner_policy is None else partner_policy,
        claim_boundary=ClaimBoundary() if claim_boundary is None else claim_boundary,
        backend_plan=backend_plan,
        state=state,
    )


def validate_v3_public_name(name: str, *, label: str = "name") -> None:
    if not _nonempty(name):
        raise GraphValidationError(f"{label} must be non-empty")
    normalized = _split_identifier(name)
    compact = "".join(normalized)
    for token in _FORBIDDEN_PUBLIC_TOKENS:
        token_parts = tuple(part for part in token.split("_") if part)
        if len(token_parts) > 1:
            if _contains_subsequence(normalized, token_parts):
                raise GraphValidationError(f"{label} contains forbidden V3 public token {token!r}")
            if token in _COMPACT_TOKEN_MATCHES and "".join(token_parts) in compact:
                raise GraphValidationError(f"{label} contains forbidden V3 public token {token!r}")
        elif token in normalized:
            raise GraphValidationError(f"{label} contains forbidden V3 public token {token!r}")
        elif token in _COMPACT_TOKEN_MATCHES and token in compact:
            raise GraphValidationError(f"{label} contains forbidden V3 public token {token!r}")


def _validate_graph_values(values: tuple[GraphValue, ...]) -> None:
    if not values:
        raise GraphValidationError("prepared graph requires values")
    names = tuple(value.name for value in values)
    if len(set(names)) != len(names):
        raise GraphValidationError("graph value names must be unique")


def _validate_graph_nodes(values: tuple[GraphValue, ...], nodes: tuple[GraphNode, ...]) -> None:
    if not nodes:
        raise GraphValidationError("prepared graph requires nodes")
    value_names = {value.name for value in values}
    node_ids = tuple(node.node_id for node in nodes)
    if len(set(node_ids)) != len(node_ids):
        raise GraphValidationError("graph node ids must be unique")
    for node in nodes:
        for input_name in node.inputs:
            if input_name not in value_names:
                raise GraphValidationError(f"node {node.node_id} input {input_name!r} is not a graph value")
        for output_name in node.outputs:
            if output_name not in value_names:
                raise GraphValidationError(f"node {node.node_id} output {output_name!r} is not a graph value")
    for value in values:
        if value.producer is not None and value.producer not in node_ids:
            raise GraphValidationError(f"value {value.name!r} producer is not a graph node")
        producer_count = sum(1 for node in nodes if value.name in node.outputs)
        if value.producer is None and producer_count:
            raise GraphValidationError(f"value {value.name!r} has output producer but no producer field")
        if value.producer is not None and producer_count != 1:
            raise GraphValidationError(f"value {value.name!r} must have exactly one producing node")


def _validate_graph_phases(phases: tuple[PhaseMarker, ...], nodes: tuple[GraphNode, ...]) -> None:
    phase_names = tuple(phase.name for phase in phases)
    missing = tuple(phase for phase in REQUIRED_PHASE_NAMES if phase not in phase_names)
    if missing:
        raise GraphValidationError("prepared graph is missing required phases: " + ", ".join(missing))
    for node in nodes:
        if node.phase not in phase_names:
            raise GraphValidationError(f"node {node.node_id} phase {node.phase!r} is not declared")


def _validate_graph_partner_policy(nodes: tuple[GraphNode, ...], policy: PartnerPolicy) -> None:
    has_partner = any(isinstance(node, PartnerNode) for node in nodes)
    if has_partner and not policy.explicit_partner_required:
        raise GraphValidationError("graphs with PartnerNode require explicit partner policy")
    if has_partner and policy.auto_selection_allowed:
        raise GraphValidationError("graphs with PartnerNode must not allow auto selection")


def _validate_node_id(node_id: str) -> None:
    validate_v3_public_name(node_id, label="node id")


def _validate_names(names: Sequence[str], label: str) -> None:
    if not names:
        raise GraphValidationError(f"{label} must be non-empty")
    for name in names:
        validate_v3_public_name(str(name), label=label)


def _validate_subset(values: Sequence[str], allowed: Sequence[str], label: str) -> None:
    unknown = sorted(set(values) - set(allowed))
    if unknown:
        raise GraphValidationError(f"{label} contains unsupported values: {unknown!r}")


def _nonempty(value: object) -> bool:
    return bool(str(value).strip()) if value is not None else False


def _split_identifier(name: str) -> tuple[str, ...]:
    camel_split = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(name))
    return tuple(part for part in re.split(r"[^A-Za-z0-9]+", camel_split.lower()) if part)


def _contains_subsequence(parts: Sequence[str], needle: Sequence[str]) -> bool:
    if not needle or len(needle) > len(parts):
        return False
    width = len(needle)
    return any(tuple(parts[index : index + width]) == tuple(needle) for index in range(len(parts) - width + 1))
