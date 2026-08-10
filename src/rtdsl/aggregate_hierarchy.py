from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping, Sequence


AGGREGATE_HIERARCHY_3D_CONTRACT_VERSION = "generic_aggregate_hierarchy_3d_contract_v1"
AGGREGATE_HIERARCHY_3D_API_MATURITY = (
    "reference_optional_numba_and_compiler_owned_native_continuation_executor"
)
AGGREGATE_HIERARCHY_3D_OPENING_SIZE_DISTANCE = "size_distance_opening"
AGGREGATE_HIERARCHY_3D_OPENING_CONTINUATION_PAYLOAD = "continuation_payload_opening"
AGGREGATE_HIERARCHY_3D_OPENING_LEAF_ONLY = "leaf_only_opening"
AGGREGATE_HIERARCHY_3D_SUPPORTED_OPENINGS = (
    AGGREGATE_HIERARCHY_3D_OPENING_SIZE_DISTANCE,
    AGGREGATE_HIERARCHY_3D_OPENING_CONTINUATION_PAYLOAD,
    AGGREGATE_HIERARCHY_3D_OPENING_LEAF_ONLY,
)
AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT = "aggregate_count"
AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM = "inverse_square_scalar_sum"
AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_VECTOR_SUM = "inverse_square_vector_sum"
AGGREGATE_HIERARCHY_3D_SUPPORTED_REDUCERS = (
    AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
    AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM,
    AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_VECTOR_SUM,
)
AGGREGATE_FRONTIER_REDUCE_3D_EXECUTION_CONTRACT = "generic_aggregate_frontier_reduce_3d_execution_contract_v1"
AGGREGATE_FRONTIER_REDUCE_3D_BACKENDS = ("reference", "numba", "cuda", "optix", "embree", "hiprt")
AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_REFERENCE = "implemented_cpu_reference"
AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_NUMBA = "optional_numba_cpu_reference_prototype"
AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_CUDA_COMPILER = (
    "implemented_precompiled_cuda_compiler_owned_continuation_template"
)
AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_NOT_IMPLEMENTED = "not_implemented_contract_only"
AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS = {
    "reference": AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_REFERENCE,
    "numba": AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_NUMBA,
    "cuda": AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_CUDA_COMPILER,
    "optix": AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_NOT_IMPLEMENTED,
    "embree": AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_NOT_IMPLEMENTED,
    "hiprt": AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_NOT_IMPLEMENTED,
}
AGGREGATE_FRONTIER_REDUCE_3D_REFERENCE_REDUCERS = (
    AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
    AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM,
)
AGGREGATE_FRONTIER_REDUCE_3D_NUMBA_REDUCERS = AGGREGATE_FRONTIER_REDUCE_3D_REFERENCE_REDUCERS
AGGREGATE_FRONTIER_REDUCE_3D_OVERFLOW_POLICY = "fail_closed_before_result_materialization"
AGGREGATE_FRONTIER_REDUCE_3D_OUTPUT_SCHEMA = (
    "source_id",
    "reducer_value_0",
    "reducer_value_1",
    "reducer_value_2",
    "visited_node_count",
    "aggregate_contribution_count",
    "exact_contribution_count",
    "status_code",
)
AGGREGATE_HIERARCHY_3D_CLAIM_BOUNDARY = (
    "reference_cpu_executor_available",
    "optional_numba_cpu_reference_prototype",
    "compiler_owned_precompiled_cuda_continuation_executor",
    "no_application_backend_or_template_selection",
    "no_paper_reproduction_claim",
    "no_speedup_claim",
    "no_app_identity_in_public_api",
)
_AGGREGATE_FRONTIER_REDUCE_NUMBA_KERNEL: Any | None = None


def _tuple_from_sequence(values: Sequence[Any], *, name: str) -> tuple[Any, ...]:
    if hasattr(values, "tolist"):
        values = values.tolist()
    try:
        result = tuple(values)
    except TypeError as exc:
        raise ValueError(f"{name} must be a finite sequence") from exc
    return result


def _float_tuple(values: Sequence[Any], *, name: str, allow_negative: bool = True) -> tuple[float, ...]:
    result = tuple(float(value) for value in _tuple_from_sequence(values, name=name))
    if not result:
        raise ValueError(f"{name} must not be empty")
    for value in result:
        if not math.isfinite(value):
            raise ValueError(f"{name} values must be finite")
        if not allow_negative and value < 0.0:
            raise ValueError(f"{name} values must be non-negative")
    return result


def _int_tuple(values: Sequence[Any], *, name: str, allow_empty: bool = False) -> tuple[int, ...]:
    result = tuple(int(value) for value in _tuple_from_sequence(values, name=name))
    if not result and not allow_empty:
        raise ValueError(f"{name} must not be empty")
    return result


def _require_same_length(columns: Mapping[str, Sequence[Any]], *, label: str) -> int:
    lengths = {name: len(column) for name, column in columns.items()}
    if not lengths:
        raise ValueError(f"{label} columns are required")
    unique = set(lengths.values())
    if len(unique) != 1:
        raise ValueError(f"{label} columns must have matching lengths: {lengths}")
    (length,) = unique
    if length <= 0:
        raise ValueError(f"{label} columns must not be empty")
    return length


def _validate_offsets(offsets: tuple[int, ...], *, limit: int, expected_len: int, name: str) -> None:
    if len(offsets) != expected_len:
        raise ValueError(f"{name} length must be node_count + 1")
    if offsets[0] != 0:
        raise ValueError(f"{name} must start at zero")
    previous = offsets[0]
    for offset in offsets[1:]:
        if offset < previous:
            raise ValueError(f"{name} must be monotonic")
        previous = offset
    if offsets[-1] > limit:
        raise ValueError(f"{name} last offset exceeds index column length")


def _validate_index_values(values: tuple[int, ...], *, limit: int, name: str) -> None:
    for value in values:
        if value < 0 or value >= limit:
            raise ValueError(f"{name} value {value} is outside [0, {limit})")


def _validate_continuation(values: tuple[int, ...], *, node_count: int, name: str) -> None:
    for value in values:
        if value < -1 or value >= node_count:
            raise ValueError(f"{name} values must be -1 or a node index")


def _validate_source_leaf_descriptor(
    values: tuple[int, ...],
    *,
    point_count: int,
    node_count: int,
    member_offsets: tuple[int, ...],
    member_indices: tuple[int, ...],
    child_offsets: tuple[int, ...],
    name: str,
) -> None:
    if len(values) != point_count:
        raise ValueError(f"{name} length must match point_count")
    for point_index, leaf_index in enumerate(values):
        if leaf_index < 0 or leaf_index >= node_count:
            raise ValueError(f"{name} values must be node indices")
        if child_offsets[leaf_index] != child_offsets[leaf_index + 1]:
            raise ValueError(f"{name} value {leaf_index} must reference a leaf node")
        begin = member_offsets[leaf_index]
        end = member_offsets[leaf_index + 1]
        if point_index not in member_indices[begin:end]:
            raise ValueError(f"{name} point {point_index} is not a member of leaf node {leaf_index}")


def _validate_subtree_end_descriptor(
    values: tuple[int, ...],
    *,
    node_count: int,
    child_offsets: tuple[int, ...],
    child_indices: tuple[int, ...],
    name: str,
) -> None:
    if len(values) != node_count:
        raise ValueError(f"{name} length must match node_count")
    for node_index, end_index in enumerate(values):
        if end_index <= node_index or end_index > node_count:
            raise ValueError(f"{name} values must satisfy node_index < end <= node_count")
        for offset in range(child_offsets[node_index], child_offsets[node_index + 1]):
            child_index = child_indices[offset]
            if child_index <= node_index or child_index >= end_index:
                raise ValueError(f"{name} child ranges must be contained in the parent subtree range")


@dataclass(frozen=True)
class SizeDistanceOpening:
    """Generic size-over-distance opening policy for aggregate hierarchies."""

    max_ratio: float

    def __post_init__(self) -> None:
        ratio = float(self.max_ratio)
        if not math.isfinite(ratio) or ratio <= 0.0:
            raise ValueError("max_ratio must be finite and positive")
        object.__setattr__(self, "max_ratio", ratio)

    def to_metadata(self) -> dict[str, Any]:
        return {
            "policy": AGGREGATE_HIERARCHY_3D_OPENING_SIZE_DISTANCE,
            "max_ratio": self.max_ratio,
            "app_specific_policy_allowed": False,
        }


@dataclass(frozen=True)
class LeafOnlyOpening:
    """Generic topology-only policy that descends to leaves before reducing."""

    def to_metadata(self) -> dict[str, Any]:
        return {
            "policy": AGGREGATE_HIERARCHY_3D_OPENING_LEAF_ONLY,
            "app_specific_policy_allowed": False,
            "uses_distance": False,
            "uses_node_size": False,
        }


@dataclass(frozen=True)
class ContinuationPayloadOpening:
    """Generic linearized-hierarchy policy driven by continuation columns."""

    max_ratio: float

    def __post_init__(self) -> None:
        ratio = float(self.max_ratio)
        if not math.isfinite(ratio) or ratio <= 0.0:
            raise ValueError("max_ratio must be finite and positive")
        object.__setattr__(self, "max_ratio", ratio)

    def to_metadata(self) -> dict[str, Any]:
        return {
            "policy": AGGREGATE_HIERARCHY_3D_OPENING_CONTINUATION_PAYLOAD,
            "max_ratio": self.max_ratio,
            "requires_continuation_columns": ("node_next_index", "node_rope_index"),
            "app_specific_policy_allowed": False,
        }


@dataclass(frozen=True)
class AggregateHierarchy3D:
    """Flat 3-D aggregate hierarchy schema.

    Continuation columns are zero-based node indices with -1 as the missing
    sentinel. Adapters for external dump formats must translate before using
    this public contract.
    """

    point_x: Sequence[Any]
    point_y: Sequence[Any]
    point_z: Sequence[Any]
    point_weight: Sequence[Any]
    node_cx: Sequence[Any]
    node_cy: Sequence[Any]
    node_cz: Sequence[Any]
    node_half_size: Sequence[Any]
    node_weight: Sequence[Any]
    member_offsets: Sequence[Any]
    member_indices: Sequence[Any]
    child_offsets: Sequence[Any]
    child_indices: Sequence[Any]
    node_next_index: Sequence[Any] | None = None
    node_resume_index: Sequence[Any] | None = None
    node_rope_index: Sequence[Any] | None = None
    source_leaf_node_index: Sequence[Any] | None = None
    node_subtree_end_index: Sequence[Any] | None = None

    def __post_init__(self) -> None:
        point_columns = {
            "point_x": _float_tuple(self.point_x, name="point_x"),
            "point_y": _float_tuple(self.point_y, name="point_y"),
            "point_z": _float_tuple(self.point_z, name="point_z"),
            "point_weight": _float_tuple(self.point_weight, name="point_weight", allow_negative=False),
        }
        point_count = _require_same_length(point_columns, label="point")

        node_columns = {
            "node_cx": _float_tuple(self.node_cx, name="node_cx"),
            "node_cy": _float_tuple(self.node_cy, name="node_cy"),
            "node_cz": _float_tuple(self.node_cz, name="node_cz"),
            "node_half_size": _float_tuple(self.node_half_size, name="node_half_size", allow_negative=False),
            "node_weight": _float_tuple(self.node_weight, name="node_weight", allow_negative=False),
        }
        node_count = _require_same_length(node_columns, label="node")

        member_offsets = _int_tuple(self.member_offsets, name="member_offsets")
        member_indices = _int_tuple(self.member_indices, name="member_indices", allow_empty=True)
        child_offsets = _int_tuple(self.child_offsets, name="child_offsets")
        child_indices = _int_tuple(self.child_indices, name="child_indices", allow_empty=True)
        _validate_offsets(member_offsets, limit=len(member_indices), expected_len=node_count + 1, name="member_offsets")
        _validate_offsets(child_offsets, limit=len(child_indices), expected_len=node_count + 1, name="child_offsets")
        _validate_index_values(member_indices, limit=point_count, name="member_indices")
        _validate_index_values(child_indices, limit=node_count, name="child_indices")

        continuation_columns: dict[str, tuple[int, ...]] = {}
        for name, values in (
            ("node_next_index", self.node_next_index),
            ("node_resume_index", self.node_resume_index),
            ("node_rope_index", self.node_rope_index),
        ):
            if values is None:
                continue
            column = _int_tuple(values, name=name)
            if len(column) != node_count:
                raise ValueError(f"{name} length must match node_count")
            _validate_continuation(column, node_count=node_count, name=name)
            continuation_columns[name] = column

        descriptor_columns: dict[str, tuple[int, ...]] = {}
        if self.source_leaf_node_index is not None:
            source_leaf = _int_tuple(self.source_leaf_node_index, name="source_leaf_node_index")
            _validate_source_leaf_descriptor(
                source_leaf,
                point_count=point_count,
                node_count=node_count,
                member_offsets=member_offsets,
                member_indices=member_indices,
                child_offsets=child_offsets,
                name="source_leaf_node_index",
            )
            descriptor_columns["source_leaf_node_index"] = source_leaf
        if self.node_subtree_end_index is not None:
            subtree_end = _int_tuple(self.node_subtree_end_index, name="node_subtree_end_index")
            _validate_subtree_end_descriptor(
                subtree_end,
                node_count=node_count,
                child_offsets=child_offsets,
                child_indices=child_indices,
                name="node_subtree_end_index",
            )
            descriptor_columns["node_subtree_end_index"] = subtree_end

        for name, values in point_columns.items():
            object.__setattr__(self, name, values)
        for name, values in node_columns.items():
            object.__setattr__(self, name, values)
        object.__setattr__(self, "member_offsets", member_offsets)
        object.__setattr__(self, "member_indices", member_indices)
        object.__setattr__(self, "child_offsets", child_offsets)
        object.__setattr__(self, "child_indices", child_indices)
        for name in ("node_next_index", "node_resume_index", "node_rope_index"):
            object.__setattr__(self, name, continuation_columns.get(name))
        for name in ("source_leaf_node_index", "node_subtree_end_index"):
            object.__setattr__(self, name, descriptor_columns.get(name))

    @property
    def point_count(self) -> int:
        return len(self.point_x)

    @property
    def node_count(self) -> int:
        return len(self.node_cx)

    def to_metadata(self) -> dict[str, Any]:
        continuation = tuple(
            name
            for name in ("node_next_index", "node_resume_index", "node_rope_index")
            if getattr(self, name) is not None
        )
        descriptors = tuple(
            name
            for name in ("source_leaf_node_index", "node_subtree_end_index")
            if getattr(self, name) is not None
        )
        return {
            "contract_version": AGGREGATE_HIERARCHY_3D_CONTRACT_VERSION,
            "schema": "AggregateHierarchy3D",
            "point_count": self.point_count,
            "node_count": self.node_count,
            "member_count": len(self.member_indices),
            "child_edge_count": len(self.child_indices),
            "continuation_columns": continuation,
            "descriptor_columns": descriptors,
            "app_specific_schema_allowed": False,
            "backend_execution_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "whole_program_speedup_claim_authorized": False,
            "claim_boundary": AGGREGATE_HIERARCHY_3D_CLAIM_BOUNDARY,
        }


@dataclass(frozen=True)
class PreparedAggregateHierarchy3D:
    hierarchy: AggregateHierarchy3D
    backend: str = "contract_only"
    producer_consumer_stream_ordering: str = "not_proven"

    def __post_init__(self) -> None:
        if not isinstance(self.hierarchy, AggregateHierarchy3D):
            raise ValueError("hierarchy must be an AggregateHierarchy3D")
        if self.backend != "contract_only":
            raise ValueError("this contract only authorizes the contract_only backend")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": AGGREGATE_HIERARCHY_3D_CONTRACT_VERSION,
            "api_maturity": AGGREGATE_HIERARCHY_3D_API_MATURITY,
            "backend": self.backend,
            "backend_execution_authorized": False,
            "device_resident_candidate": False,
            "materializes_host_rows_for_bridge": True,
            "producer_consumer_stream_ordering": self.producer_consumer_stream_ordering,
            "hierarchy": self.hierarchy.to_metadata(),
        }


@dataclass(frozen=True)
class AggregateFrontierReduceSpec3D:
    prepared_hierarchy: PreparedAggregateHierarchy3D
    opening: SizeDistanceOpening | ContinuationPayloadOpening | LeafOnlyOpening
    reducer: str = AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT

    def __post_init__(self) -> None:
        if not isinstance(self.prepared_hierarchy, PreparedAggregateHierarchy3D):
            raise ValueError("prepared_hierarchy must be a PreparedAggregateHierarchy3D")
        if not isinstance(self.opening, (SizeDistanceOpening, ContinuationPayloadOpening, LeafOnlyOpening)):
            raise ValueError("opening must be a supported aggregate hierarchy opening policy")
        if self.reducer not in AGGREGATE_HIERARCHY_3D_SUPPORTED_REDUCERS:
            raise ValueError(f"unsupported reducer: {self.reducer}")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": AGGREGATE_HIERARCHY_3D_CONTRACT_VERSION,
            "api_maturity": AGGREGATE_HIERARCHY_3D_API_MATURITY,
            "spec": "aggregate_frontier_reduce_3d",
            "opening": self.opening.to_metadata(),
            "reducer": self.reducer,
            "supported_reducers": AGGREGATE_HIERARCHY_3D_SUPPORTED_REDUCERS,
            "backend_execution_authorized": False,
            "app_specific_reducer_allowed": False,
            "paper_reproduction_claim_authorized": False,
            "whole_program_speedup_claim_authorized": False,
            "prepared_hierarchy": self.prepared_hierarchy.to_metadata(),
        }


@dataclass(frozen=True)
class AggregateFrontierReduceExecutionContract3D:
    spec: AggregateFrontierReduceSpec3D
    backend: str = "reference"
    max_output_rows: int | None = None
    overflow_policy: str = AGGREGATE_FRONTIER_REDUCE_3D_OVERFLOW_POLICY

    def __post_init__(self) -> None:
        if not isinstance(self.spec, AggregateFrontierReduceSpec3D):
            raise ValueError("spec must be an AggregateFrontierReduceSpec3D")
        if self.backend not in AGGREGATE_FRONTIER_REDUCE_3D_BACKENDS:
            raise ValueError(f"unsupported backend: {self.backend}")
        if self.overflow_policy != AGGREGATE_FRONTIER_REDUCE_3D_OVERFLOW_POLICY:
            raise ValueError("unsupported overflow_policy")
        if self.max_output_rows is not None and int(self.max_output_rows) < 0:
            raise ValueError("max_output_rows must be non-negative or None")
        object.__setattr__(
            self,
            "max_output_rows",
            None if self.max_output_rows is None else int(self.max_output_rows),
        )

    def to_metadata(self) -> dict[str, Any]:
        backend_status = AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS[self.backend]
        backend_authorized = self.backend in ("reference", "numba")
        return {
            "contract_version": AGGREGATE_FRONTIER_REDUCE_3D_EXECUTION_CONTRACT,
            "api_maturity": AGGREGATE_HIERARCHY_3D_API_MATURITY,
            "backend": self.backend,
            "backend_status": backend_status,
            "supported_backends": AGGREGATE_FRONTIER_REDUCE_3D_BACKENDS,
            "reference_supported_reducers": AGGREGATE_FRONTIER_REDUCE_3D_REFERENCE_REDUCERS,
            "numba_supported_reducers": AGGREGATE_FRONTIER_REDUCE_3D_NUMBA_REDUCERS,
            "backend_execution_authorized": backend_authorized,
            "reference_execution_authorized": self.backend == "reference",
            "numba_execution_authorized": self.backend == "numba",
            "runtime_dependency_required": "numba" if self.backend == "numba" else None,
            "native_backend_symbols_authorized": False,
            "compiler_owned_native_template_available": self.backend == "cuda",
            "direct_cuda_execution_authorized": False,
            "cuda_execution_requires_compiler_plan": self.backend == "cuda",
            "output_schema": AGGREGATE_FRONTIER_REDUCE_3D_OUTPUT_SCHEMA,
            "required_descriptor_columns": (
                "source_leaf_node_index",
                "node_subtree_end_index",
            ),
            "overflow_policy": self.overflow_policy,
            "max_output_rows": self.max_output_rows,
            "spec": self.spec.to_metadata(),
            "claim_boundary": (
                "reference_cpu_or_optional_numba_cpu_direct_execution",
                "native_cuda_only_through_compiler_owned_plan",
                "no_timing_claim",
                "no_paper_reproduction_claim",
            ),
        }


def aggregate_hierarchy_3d(**kwargs: Any) -> AggregateHierarchy3D:
    return AggregateHierarchy3D(**kwargs)


def prepare_aggregate_hierarchy_3d(
    hierarchy: AggregateHierarchy3D,
    *,
    backend: str = "contract_only",
    producer_consumer_stream_ordering: str = "not_proven",
) -> PreparedAggregateHierarchy3D:
    return PreparedAggregateHierarchy3D(
        hierarchy=hierarchy,
        backend=backend,
        producer_consumer_stream_ordering=producer_consumer_stream_ordering,
    )


def aggregate_frontier_reduce_spec_3d(
    prepared_hierarchy: PreparedAggregateHierarchy3D,
    *,
    opening: SizeDistanceOpening | ContinuationPayloadOpening | LeafOnlyOpening,
    reducer: str = AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
) -> AggregateFrontierReduceSpec3D:
    return AggregateFrontierReduceSpec3D(
        prepared_hierarchy=prepared_hierarchy,
        opening=opening,
        reducer=reducer,
    )


def aggregate_frontier_reduce_execution_contract_3d(
    spec: AggregateFrontierReduceSpec3D,
    *,
    backend: str = "reference",
    max_output_rows: int | None = None,
    overflow_policy: str = AGGREGATE_FRONTIER_REDUCE_3D_OVERFLOW_POLICY,
) -> AggregateFrontierReduceExecutionContract3D:
    return AggregateFrontierReduceExecutionContract3D(
        spec=spec,
        backend=backend,
        max_output_rows=max_output_rows,
        overflow_policy=overflow_policy,
    )


def _aggregate_hierarchy_root_nodes(hierarchy: AggregateHierarchy3D) -> tuple[int, ...]:
    child_nodes = set(hierarchy.child_indices)
    return tuple(node_index for node_index in range(hierarchy.node_count) if node_index not in child_nodes)


def _aggregate_hierarchy_node_contains_source(
    hierarchy: AggregateHierarchy3D,
    *,
    node_index: int,
    source_index: int,
) -> bool:
    if hierarchy.source_leaf_node_index is None or hierarchy.node_subtree_end_index is None:
        raise ValueError("reference execution requires source_leaf_node_index and node_subtree_end_index")
    source_leaf = hierarchy.source_leaf_node_index[source_index]
    return node_index <= source_leaf < hierarchy.node_subtree_end_index[node_index]


def _aggregate_hierarchy_reference_node_opens(
    hierarchy: AggregateHierarchy3D,
    opening: SizeDistanceOpening | LeafOnlyOpening,
    *,
    node_index: int,
    source_index: int,
) -> bool:
    if isinstance(opening, LeafOnlyOpening):
        return False
    if _aggregate_hierarchy_node_contains_source(hierarchy, node_index=node_index, source_index=source_index):
        return False
    dx = hierarchy.node_cx[node_index] - hierarchy.point_x[source_index]
    dy = hierarchy.node_cy[node_index] - hierarchy.point_y[source_index]
    dz = hierarchy.node_cz[node_index] - hierarchy.point_z[source_index]
    distance = math.sqrt(dx * dx + dy * dy + dz * dz)
    if distance <= 0.0:
        return False
    return (hierarchy.node_half_size[node_index] / distance) <= opening.max_ratio


def aggregate_frontier_reduce_reference_3d(
    execution: AggregateFrontierReduceExecutionContract3D,
    *,
    softening: float = 0.0,
) -> dict[str, Any]:
    """Run the generic aggregate frontier reduce contract on a CPU reference path."""

    if not isinstance(execution, AggregateFrontierReduceExecutionContract3D):
        raise ValueError("execution must be an AggregateFrontierReduceExecutionContract3D")
    if execution.backend != "reference":
        raise ValueError("reference executor requires backend='reference'")
    spec = execution.spec
    if spec.reducer not in AGGREGATE_FRONTIER_REDUCE_3D_REFERENCE_REDUCERS:
        raise ValueError("reference executor does not support reducer")
    softening = float(softening)
    if not math.isfinite(softening) or softening < 0.0:
        raise ValueError("softening must be finite and non-negative")

    hierarchy = spec.prepared_hierarchy.hierarchy
    if hierarchy.source_leaf_node_index is None or hierarchy.node_subtree_end_index is None:
        raise ValueError("reference execution requires descriptor columns")
    if execution.max_output_rows is not None and hierarchy.point_count > execution.max_output_rows:
        raise ValueError("max_output_rows would overflow before result materialization")

    roots = _aggregate_hierarchy_root_nodes(hierarchy)
    if not roots:
        raise ValueError("reference execution requires at least one root node")
    continuation_payload = isinstance(spec.opening, ContinuationPayloadOpening)
    if continuation_payload:
        if hierarchy.node_next_index is None or hierarchy.node_rope_index is None:
            raise ValueError("continuation-payload execution requires node_next_index and node_rope_index")
        if len(roots) != 1:
            raise ValueError("continuation-payload execution requires a single linearized root")

    rows: list[dict[str, int | float]] = []
    softening_sq = softening * softening

    for source_index in range(hierarchy.point_count):
        reducer_values = [0.0, 0.0, 0.0]
        visited_count = 0
        aggregate_count = 0
        exact_count = 0

        def add_inverse_square_contribution(weight: float, dx: float, dy: float, dz: float) -> None:
            distance_sq = dx * dx + dy * dy + dz * dz + softening_sq
            if distance_sq <= 0.0:
                return
            reducer_values[0] += hierarchy.point_weight[source_index] * weight / distance_sq

        def add_leaf_exact_contributions(node_index: int) -> None:
            nonlocal exact_count
            member_begin = hierarchy.member_offsets[node_index]
            member_end = hierarchy.member_offsets[node_index + 1]
            for member_offset in range(member_begin, member_end):
                point_index = hierarchy.member_indices[member_offset]
                if point_index == source_index:
                    continue
                if spec.reducer == AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT:
                    reducer_values[0] += 1.0
                else:
                    add_inverse_square_contribution(
                        hierarchy.point_weight[point_index],
                        hierarchy.point_x[point_index] - hierarchy.point_x[source_index],
                        hierarchy.point_y[point_index] - hierarchy.point_y[source_index],
                        hierarchy.point_z[point_index] - hierarchy.point_z[source_index],
                    )
                exact_count += 1

        if continuation_payload:
            node_index = roots[0]
            ray_self = 0
            status_code = 0
            while node_index >= 0:
                if node_index >= hierarchy.node_count:
                    status_code = 2
                    break
                visited_count += 1
                child_begin = hierarchy.child_offsets[node_index]
                child_end = hierarchy.child_offsets[node_index + 1]
                is_leaf = child_begin == child_end
                dx = hierarchy.point_x[source_index] - hierarchy.node_cx[node_index]
                dy = hierarchy.point_y[source_index] - hierarchy.node_cy[node_index]
                dz = hierarchy.point_z[source_index] - hierarchy.node_cz[node_index]
                raw_distance_sq = dx * dx + dy * dy + dz * dz
                distance_sq = raw_distance_sq + softening_sq
                ray_length = math.sqrt(raw_distance_sq) * spec.opening.max_ratio
                hit_current_node = hierarchy.node_half_size[node_index] < ray_length

                if hit_current_node:
                    if is_leaf:
                        add_leaf_exact_contributions(node_index)
                    elif distance_sq > 0.0:
                        if spec.reducer == AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT:
                            reducer_values[0] += 1.0
                        else:
                            reducer_values[0] += (
                                hierarchy.point_weight[source_index]
                                * hierarchy.node_weight[node_index]
                                / distance_sq
                            )
                        aggregate_count += 1
                    node_index = hierarchy.node_rope_index[node_index]
                else:
                    if is_leaf and ray_self == 0:
                        add_leaf_exact_contributions(node_index)
                    node_index = hierarchy.node_next_index[node_index]

                if node_index < 0:
                    break
                if node_index >= hierarchy.node_count:
                    status_code = 2
                    break
                ndx = hierarchy.point_x[source_index] - hierarchy.node_cx[node_index]
                ndy = hierarchy.point_y[source_index] - hierarchy.node_cy[node_index]
                ndz = hierarchy.point_z[source_index] - hierarchy.node_cz[node_index]
                next_ray_length = math.sqrt(ndx * ndx + ndy * ndy + ndz * ndz) * spec.opening.max_ratio
                ray_self = 1 if next_ray_length == 0.0 else 0

            rows.append(
                {
                    "source_id": source_index,
                    "reducer_value_0": reducer_values[0],
                    "reducer_value_1": reducer_values[1],
                    "reducer_value_2": reducer_values[2],
                    "visited_node_count": visited_count,
                    "aggregate_contribution_count": aggregate_count,
                    "exact_contribution_count": exact_count,
                    "status_code": status_code,
                }
            )
            continue

        def visit_node(node_index: int) -> None:
            nonlocal visited_count, aggregate_count, exact_count
            visited_count += 1
            child_begin = hierarchy.child_offsets[node_index]
            child_end = hierarchy.child_offsets[node_index + 1]
            is_leaf = child_begin == child_end

            if not is_leaf and _aggregate_hierarchy_reference_node_opens(
                hierarchy,
                spec.opening,
                node_index=node_index,
                source_index=source_index,
            ):
                if spec.reducer == AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT:
                    reducer_values[0] += 1.0
                else:
                    add_inverse_square_contribution(
                        hierarchy.node_weight[node_index],
                        hierarchy.node_cx[node_index] - hierarchy.point_x[source_index],
                        hierarchy.node_cy[node_index] - hierarchy.point_y[source_index],
                        hierarchy.node_cz[node_index] - hierarchy.point_z[source_index],
                    )
                aggregate_count += 1
                return

            if not is_leaf:
                for child_offset in range(child_begin, child_end):
                    visit_node(hierarchy.child_indices[child_offset])
                return

            member_begin = hierarchy.member_offsets[node_index]
            member_end = hierarchy.member_offsets[node_index + 1]
            add_leaf_exact_contributions(node_index)

        for root_index in roots:
            visit_node(root_index)

        rows.append(
            {
                "source_id": source_index,
                "reducer_value_0": reducer_values[0],
                "reducer_value_1": reducer_values[1],
                "reducer_value_2": reducer_values[2],
                "visited_node_count": visited_count,
                "aggregate_contribution_count": aggregate_count,
                "exact_contribution_count": exact_count,
                "status_code": 0,
            }
        )

    return {
        "contract_version": AGGREGATE_FRONTIER_REDUCE_3D_EXECUTION_CONTRACT,
        "backend": "reference",
        "backend_status": AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_REFERENCE,
        "output_schema": AGGREGATE_FRONTIER_REDUCE_3D_OUTPUT_SCHEMA,
        "row_count": len(rows),
        "partial_result_returned": False,
        "rows": tuple(rows),
        "metadata": {
            "opening_policy": spec.opening.to_metadata(),
            "reducer": spec.reducer,
            "root_nodes": roots,
            "softening": softening,
            "native_backend_symbols_authorized": False,
            "timing_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
        },
    }


run_aggregate_frontier_reduce_reference_3d = aggregate_frontier_reduce_reference_3d


def aggregate_frontier_reduce_numba_available() -> bool:
    try:
        import numba  # noqa: F401
        import numpy  # noqa: F401
    except ImportError:
        return False
    return True


def _aggregate_frontier_reduce_numba_kernel() -> Any:
    global _AGGREGATE_FRONTIER_REDUCE_NUMBA_KERNEL
    if _AGGREGATE_FRONTIER_REDUCE_NUMBA_KERNEL is not None:
        return _AGGREGATE_FRONTIER_REDUCE_NUMBA_KERNEL

    try:
        import numpy as np
        from numba import njit
    except ImportError as exc:
        raise RuntimeError("Numba and NumPy are required for the optional numba aggregate frontier executor") from exc

    @njit(cache=False)
    def _kernel(
        point_x,
        point_y,
        point_z,
        point_weight,
        node_cx,
        node_cy,
        node_cz,
        node_half_size,
        node_weight,
        member_offsets,
        member_indices,
        child_offsets,
        child_indices,
        source_leaf_node_index,
        node_subtree_end_index,
        node_next_index,
        node_rope_index,
        root_nodes,
        opening_kind,
        max_ratio,
        reducer_kind,
        softening,
    ):
        point_count = point_x.shape[0]
        node_count = node_cx.shape[0]
        source_ids = np.empty(point_count, np.int64)
        reducer_values = np.zeros((point_count, 3), np.float64)
        visited_counts = np.zeros(point_count, np.int64)
        aggregate_counts = np.zeros(point_count, np.int64)
        exact_counts = np.zeros(point_count, np.int64)
        status_codes = np.zeros(point_count, np.int64)
        softening_sq = softening * softening

        for source_index in range(point_count):
            source_ids[source_index] = source_index
            if opening_kind == 2:
                node_index = root_nodes[0]
                ray_self = 0
                while node_index >= 0:
                    if node_index >= node_count:
                        status_codes[source_index] = 2
                        break
                    visited_counts[source_index] += 1
                    child_begin = child_offsets[node_index]
                    child_end = child_offsets[node_index + 1]
                    is_leaf = child_begin == child_end
                    dx = point_x[source_index] - node_cx[node_index]
                    dy = point_y[source_index] - node_cy[node_index]
                    dz = point_z[source_index] - node_cz[node_index]
                    raw_distance_sq = dx * dx + dy * dy + dz * dz
                    distance_sq = raw_distance_sq + softening_sq
                    ray_length = math.sqrt(raw_distance_sq) * max_ratio
                    hit_current_node = node_half_size[node_index] < ray_length

                    if hit_current_node:
                        if is_leaf:
                            member_begin = member_offsets[node_index]
                            member_end = member_offsets[node_index + 1]
                            for member_offset in range(member_begin, member_end):
                                point_index = member_indices[member_offset]
                                if point_index == source_index:
                                    continue
                                if reducer_kind == 0:
                                    reducer_values[source_index, 0] += 1.0
                                else:
                                    ex = point_x[point_index] - point_x[source_index]
                                    ey = point_y[point_index] - point_y[source_index]
                                    ez = point_z[point_index] - point_z[source_index]
                                    exact_dist_sq = ex * ex + ey * ey + ez * ez + softening_sq
                                    if exact_dist_sq > 0.0:
                                        reducer_values[source_index, 0] += (
                                            point_weight[source_index] * point_weight[point_index] / exact_dist_sq
                                        )
                                exact_counts[source_index] += 1
                        elif distance_sq > 0.0:
                            if reducer_kind == 0:
                                reducer_values[source_index, 0] += 1.0
                            else:
                                reducer_values[source_index, 0] += (
                                    point_weight[source_index] * node_weight[node_index] / distance_sq
                                )
                            aggregate_counts[source_index] += 1
                        node_index = node_rope_index[node_index]
                    else:
                        if is_leaf and ray_self == 0:
                            member_begin = member_offsets[node_index]
                            member_end = member_offsets[node_index + 1]
                            for member_offset in range(member_begin, member_end):
                                point_index = member_indices[member_offset]
                                if point_index == source_index:
                                    continue
                                if reducer_kind == 0:
                                    reducer_values[source_index, 0] += 1.0
                                else:
                                    ex = point_x[point_index] - point_x[source_index]
                                    ey = point_y[point_index] - point_y[source_index]
                                    ez = point_z[point_index] - point_z[source_index]
                                    exact_dist_sq = ex * ex + ey * ey + ez * ez + softening_sq
                                    if exact_dist_sq > 0.0:
                                        reducer_values[source_index, 0] += (
                                            point_weight[source_index] * point_weight[point_index] / exact_dist_sq
                                        )
                                exact_counts[source_index] += 1
                        node_index = node_next_index[node_index]

                    if node_index < 0:
                        break
                    if node_index >= node_count:
                        status_codes[source_index] = 2
                        break
                    ndx = point_x[source_index] - node_cx[node_index]
                    ndy = point_y[source_index] - node_cy[node_index]
                    ndz = point_z[source_index] - node_cz[node_index]
                    next_ray_length = math.sqrt(ndx * ndx + ndy * ndy + ndz * ndz) * max_ratio
                    ray_self = 1 if next_ray_length == 0.0 else 0
                continue

            stack = np.empty(node_count, np.int64)
            top = 0
            for root_offset in range(root_nodes.shape[0] - 1, -1, -1):
                stack[top] = root_nodes[root_offset]
                top += 1

            while top > 0:
                top -= 1
                node_index = stack[top]
                visited_counts[source_index] += 1
                child_begin = child_offsets[node_index]
                child_end = child_offsets[node_index + 1]
                is_leaf = child_begin == child_end

                opened = False
                if not is_leaf and opening_kind == 1:
                    source_leaf = source_leaf_node_index[source_index]
                    contains_source = node_index <= source_leaf and source_leaf < node_subtree_end_index[node_index]
                    if not contains_source:
                        dx = node_cx[node_index] - point_x[source_index]
                        dy = node_cy[node_index] - point_y[source_index]
                        dz = node_cz[node_index] - point_z[source_index]
                        distance = math.sqrt(dx * dx + dy * dy + dz * dz)
                        if distance > 0.0 and (node_half_size[node_index] / distance) <= max_ratio:
                            opened = True

                if opened:
                    if reducer_kind == 0:
                        reducer_values[source_index, 0] += 1.0
                    else:
                        dx = node_cx[node_index] - point_x[source_index]
                        dy = node_cy[node_index] - point_y[source_index]
                        dz = node_cz[node_index] - point_z[source_index]
                        distance_sq = dx * dx + dy * dy + dz * dz + softening_sq
                        if distance_sq > 0.0:
                            reducer_values[source_index, 0] += point_weight[source_index] * node_weight[node_index] / distance_sq
                    aggregate_counts[source_index] += 1
                    continue

                if not is_leaf:
                    for child_offset in range(child_end - 1, child_begin - 1, -1):
                        stack[top] = child_indices[child_offset]
                        top += 1
                    continue

                member_begin = member_offsets[node_index]
                member_end = member_offsets[node_index + 1]
                for member_offset in range(member_begin, member_end):
                    point_index = member_indices[member_offset]
                    if point_index == source_index:
                        continue
                    if reducer_kind == 0:
                        reducer_values[source_index, 0] += 1.0
                    else:
                        dx = point_x[point_index] - point_x[source_index]
                        dy = point_y[point_index] - point_y[source_index]
                        dz = point_z[point_index] - point_z[source_index]
                        distance_sq = dx * dx + dy * dy + dz * dz + softening_sq
                        if distance_sq > 0.0:
                            reducer_values[source_index, 0] += point_weight[source_index] * point_weight[point_index] / distance_sq
                    exact_counts[source_index] += 1

        return source_ids, reducer_values, visited_counts, aggregate_counts, exact_counts, status_codes

    _AGGREGATE_FRONTIER_REDUCE_NUMBA_KERNEL = _kernel
    return _AGGREGATE_FRONTIER_REDUCE_NUMBA_KERNEL


def aggregate_frontier_reduce_numba_3d(
    execution: AggregateFrontierReduceExecutionContract3D,
    *,
    softening: float = 0.0,
) -> dict[str, Any]:
    """Run the aggregate frontier reduce contract through an optional CPU Numba prototype."""

    if not isinstance(execution, AggregateFrontierReduceExecutionContract3D):
        raise ValueError("execution must be an AggregateFrontierReduceExecutionContract3D")
    if execution.backend != "numba":
        raise ValueError("numba executor requires backend='numba'")
    spec = execution.spec
    if spec.reducer not in AGGREGATE_FRONTIER_REDUCE_3D_NUMBA_REDUCERS:
        raise ValueError("numba executor does not support reducer")
    softening = float(softening)
    if not math.isfinite(softening) or softening < 0.0:
        raise ValueError("softening must be finite and non-negative")

    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("NumPy is required for the optional numba aggregate frontier executor") from exc

    hierarchy = spec.prepared_hierarchy.hierarchy
    if hierarchy.source_leaf_node_index is None or hierarchy.node_subtree_end_index is None:
        raise ValueError("numba execution requires descriptor columns")
    if execution.max_output_rows is not None and hierarchy.point_count > execution.max_output_rows:
        raise ValueError("max_output_rows would overflow before result materialization")

    roots = _aggregate_hierarchy_root_nodes(hierarchy)
    if not roots:
        raise ValueError("numba execution requires at least one root node")

    if isinstance(spec.opening, LeafOnlyOpening):
        opening_kind = 0
        max_ratio = 0.0
    elif isinstance(spec.opening, ContinuationPayloadOpening):
        opening_kind = 2
        max_ratio = spec.opening.max_ratio
        if hierarchy.node_next_index is None or hierarchy.node_rope_index is None:
            raise ValueError("continuation-payload numba execution requires node_next_index and node_rope_index")
        if len(roots) != 1:
            raise ValueError("continuation-payload numba execution requires a single linearized root")
    else:
        opening_kind = 1
        max_ratio = spec.opening.max_ratio
    reducer_kind = 0 if spec.reducer == AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT else 1
    kernel = _aggregate_frontier_reduce_numba_kernel()
    (
        source_ids,
        reducer_values,
        visited_counts,
        aggregate_counts,
        exact_counts,
        status_codes,
    ) = kernel(
        np.asarray(hierarchy.point_x, dtype=np.float64),
        np.asarray(hierarchy.point_y, dtype=np.float64),
        np.asarray(hierarchy.point_z, dtype=np.float64),
        np.asarray(hierarchy.point_weight, dtype=np.float64),
        np.asarray(hierarchy.node_cx, dtype=np.float64),
        np.asarray(hierarchy.node_cy, dtype=np.float64),
        np.asarray(hierarchy.node_cz, dtype=np.float64),
        np.asarray(hierarchy.node_half_size, dtype=np.float64),
        np.asarray(hierarchy.node_weight, dtype=np.float64),
        np.asarray(hierarchy.member_offsets, dtype=np.int64),
        np.asarray(hierarchy.member_indices, dtype=np.int64),
        np.asarray(hierarchy.child_offsets, dtype=np.int64),
        np.asarray(hierarchy.child_indices, dtype=np.int64),
        np.asarray(hierarchy.source_leaf_node_index, dtype=np.int64),
        np.asarray(hierarchy.node_subtree_end_index, dtype=np.int64),
        np.asarray(hierarchy.node_next_index if hierarchy.node_next_index is not None else (), dtype=np.int64),
        np.asarray(hierarchy.node_rope_index if hierarchy.node_rope_index is not None else (), dtype=np.int64),
        np.asarray(roots, dtype=np.int64),
        opening_kind,
        float(max_ratio),
        reducer_kind,
        softening,
    )

    rows = tuple(
        {
            "source_id": int(source_ids[index]),
            "reducer_value_0": float(reducer_values[index, 0]),
            "reducer_value_1": float(reducer_values[index, 1]),
            "reducer_value_2": float(reducer_values[index, 2]),
            "visited_node_count": int(visited_counts[index]),
            "aggregate_contribution_count": int(aggregate_counts[index]),
            "exact_contribution_count": int(exact_counts[index]),
            "status_code": int(status_codes[index]),
        }
        for index in range(source_ids.shape[0])
    )
    return {
        "contract_version": AGGREGATE_FRONTIER_REDUCE_3D_EXECUTION_CONTRACT,
        "backend": "numba",
        "backend_status": AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_NUMBA,
        "output_schema": AGGREGATE_FRONTIER_REDUCE_3D_OUTPUT_SCHEMA,
        "row_count": len(rows),
        "partial_result_returned": False,
        "rows": rows,
        "metadata": {
            "opening_policy": spec.opening.to_metadata(),
            "reducer": spec.reducer,
            "root_nodes": roots,
            "softening": softening,
            "parity_oracle_backend": "reference",
            "native_backend_symbols_authorized": False,
            "timing_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
        },
    }


run_aggregate_frontier_reduce_numba_3d = aggregate_frontier_reduce_numba_3d


def describe_aggregate_hierarchy_3d_contract() -> dict[str, Any]:
    return {
        "contract_version": AGGREGATE_HIERARCHY_3D_CONTRACT_VERSION,
        "api_maturity": AGGREGATE_HIERARCHY_3D_API_MATURITY,
        "opening_policies": AGGREGATE_HIERARCHY_3D_SUPPORTED_OPENINGS,
        "supported_reducers": AGGREGATE_HIERARCHY_3D_SUPPORTED_REDUCERS,
        "execution_contract": AGGREGATE_FRONTIER_REDUCE_3D_EXECUTION_CONTRACT,
        "execution_backends": AGGREGATE_FRONTIER_REDUCE_3D_BACKENDS,
        "execution_backend_status": AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS,
        "reference_supported_reducers": AGGREGATE_FRONTIER_REDUCE_3D_REFERENCE_REDUCERS,
        "numba_supported_reducers": AGGREGATE_FRONTIER_REDUCE_3D_NUMBA_REDUCERS,
        "execution_output_schema": AGGREGATE_FRONTIER_REDUCE_3D_OUTPUT_SCHEMA,
        "execution_overflow_policy": AGGREGATE_FRONTIER_REDUCE_3D_OVERFLOW_POLICY,
        "schema": (
            "point_x",
            "point_y",
            "point_z",
            "point_weight",
            "node_cx",
            "node_cy",
            "node_cz",
            "node_half_size",
            "node_weight",
            "member_offsets",
            "member_indices",
            "child_offsets",
            "child_indices",
            "node_next_index",
            "node_resume_index",
            "node_rope_index",
            "source_leaf_node_index",
            "node_subtree_end_index",
        ),
        "descriptor_columns": ("source_leaf_node_index", "node_subtree_end_index"),
        "continuation_index_base": "zero_based",
        "continuation_missing_sentinel": -1,
        "descriptor_index_base": "zero_based",
        "app_specific_schema_allowed": False,
        "backend_execution_authorized": True,
        "reference_execution_authorized": True,
        "numba_execution_authorized": True,
        "numba_runtime_optional": True,
        "native_backend_symbols_authorized": False,
        "compiler_owned_native_symbols_authorized": True,
        "native_execution_compiler_owned_only": True,
        "application_backend_selection_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "whole_program_speedup_claim_authorized": False,
        "claim_boundary": AGGREGATE_HIERARCHY_3D_CLAIM_BOUNDARY,
    }


def validate_aggregate_hierarchy_3d_contract() -> dict[str, Any]:
    contract = describe_aggregate_hierarchy_3d_contract()
    if contract["api_maturity"] != AGGREGATE_HIERARCHY_3D_API_MATURITY:
        raise AssertionError("aggregate hierarchy contract maturity mismatch")
    if not contract["reference_execution_authorized"]:
        raise AssertionError("aggregate hierarchy contract must authorize the CPU reference executor")
    if contract["app_specific_schema_allowed"]:
        raise AssertionError("aggregate hierarchy contract must remain app-name-free")
    if AGGREGATE_HIERARCHY_3D_OPENING_SIZE_DISTANCE not in contract["opening_policies"]:
        raise AssertionError("size-distance opening policy missing")
    if AGGREGATE_HIERARCHY_3D_OPENING_LEAF_ONLY not in contract["opening_policies"]:
        raise AssertionError("leaf-only opening policy missing")
    return contract
