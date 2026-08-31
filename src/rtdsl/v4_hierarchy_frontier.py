"""Verified bounded hierarchy-frontier composition for V4.

The application supplies a typed aggregate-hierarchy statement, not a Python
controller and not an OptiX callback.  The compiler accepts only the existing
single-root continuation representation and one of two closed reducers.  It
then binds that statement to the already registered true-OptiX hierarchy
executor.

This module deliberately adds no native symbol and does not raise OptiX trace
or callable depth.  The native executor performs one launch; its raygen walks
the bounded threaded hierarchy and performs one trace per visited node.  A
status row is required for every source and any malformed continuation,
capacity breach, traversal-audit failure, or visit-bound breach fails closed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import json
import math
import os
import re
import secrets
import threading
import time
from typing import Mapping

from .aggregate_hierarchy import (
    AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
    AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM,
    AggregateFrontierReduceSpec3D,
    ContinuationPayloadOpening,
)
from .aggregate_hierarchy_native import (
    AGGREGATE_HIERARCHY_OPTIX_TEMPLATE,
    PreparedNativeAggregateHierarchy3D,
    compile_aggregate_frontier_reduce_candidate_for_functional_validation_3d,
    consume_canonical_hierarchy_output_binding,
    run_aggregate_frontier_reduce_candidate_for_functional_validation_3d,
)
from . import optix_runtime
from .physical_execution_provenance import OptixTraversalAuditSession


HIERARCHY_FRONTIER_SCHEMA_ID = (
    "https://rtdl.dev/schemas/v4-hierarchy-frontier-reduce-v1.json"
)
HIERARCHY_FRONTIER_SCHEMA_VERSION = "v1"
HIERARCHY_FRONTIER_PROGRAM_BUNDLE = (
    "aggregate_hierarchy_continuation_reduce_3d"
)
U32_MAX = (1 << 32) - 1
_PLAN_KEY = secrets.token_bytes(32)
_PREPARED_AUTHORITY_KEY = secrets.token_bytes(32)
_PACKED_OUTPUT_BINDING_KEY = secrets.token_bytes(32)

_HIERARCHY_COLUMN_NAMES = (
    "point_x", "point_y", "point_z", "point_weight",
    "node_cx", "node_cy", "node_cz", "node_half_size", "node_weight",
    "member_offsets", "member_indices", "child_offsets", "child_indices",
    "node_next_index", "node_resume_index", "node_rope_index",
    "source_leaf_node_index", "node_subtree_end_index",
)


class HierarchyFrontierError(ValueError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(
            f"V4 hierarchy-frontier rejected: {code}@{path}: {message}"
        )


def _fail(code: str, path: str, message: str) -> None:
    raise HierarchyFrontierError(code, path, message)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _sha(value: str, path: str) -> str:
    if re.fullmatch(r"[0-9a-f]{64}", value) is None:
        _fail("identity", path, "lower-case SHA-256 identity required")
    return value


class HierarchyReducer(str, Enum):
    AGGREGATE_COUNT = AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT
    INVERSE_SQUARE_SCALAR_SUM = (
        AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM
    )


@dataclass(frozen=True)
class HierarchyFrontierSchema:
    producer_contract_sha256: str
    hierarchy_sha256: str
    reducer: HierarchyReducer
    maximum_output_rows: int
    maximum_visits_per_source: int
    schema_id: str = HIERARCHY_FRONTIER_SCHEMA_ID
    schema_version: str = HIERARCHY_FRONTIER_SCHEMA_VERSION

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "producer_contract_sha256": self.producer_contract_sha256,
            "hierarchy_sha256": self.hierarchy_sha256,
            "reducer": self.reducer.value,
            "maximum_output_rows": self.maximum_output_rows,
            "maximum_visits_per_source": self.maximum_visits_per_source,
            "opening": "continuation_payload_size_distance_v1",
            "physical_candidate": "true_optix_threaded_hierarchy_v1",
            "max_trace_depth": 1,
            "max_callable_depth": 0,
            "frontier_controller_owner": "compiler",
            "raw_device_order_is_semantic": False,
            "arbitrary_user_controller_or_reducer_allowed": False,
            "capacity_and_status_policy": "fail_closed_complete_result",
        }

    @property
    def schema_sha256(self) -> str:
        return _digest(self.semantic_dict())

    def to_dict(self) -> dict[str, object]:
        return {**self.semantic_dict(), "schema_sha256": self.schema_sha256}


@dataclass(frozen=True)
class CompiledHierarchyFrontier:
    schema: HierarchyFrontierSchema
    spec_sha256: str
    node_count: int
    point_count: int
    plan_sha256: str
    compiler_seal: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema.to_dict(),
            "spec_sha256": self.spec_sha256,
            "node_count": self.node_count,
            "point_count": self.point_count,
            "plan_sha256": self.plan_sha256,
            "selected_template": AGGREGATE_HIERARCHY_OPTIX_TEMPLATE,
            "program_bundle": HIERARCHY_FRONTIER_PROGRAM_BUNDLE,
            "new_native_symbol_added": False,
            "application_or_publication_identity_used": False,
        }


@dataclass(frozen=True)
class HierarchyFrontierResult:
    rows: tuple[Mapping[str, int | float], ...]
    output_sha256: str
    plan_sha256: str
    traversal_receipt: dict[str, object]
    endpoint_metadata: dict[str, object]


@dataclass(frozen=True)
class _VerifiedPackedHierarchyRowsBinding:
    """Private single-process authority for one immutable endpoint snapshot."""

    rows: tuple[Mapping[str, int | float], ...]
    output_sha256: str
    plan_sha256: str
    point_count: int
    endpoint_identity: int
    selected_backend: str
    selected_template: str
    physical_executor_kind: str
    authority_seal: str


def hierarchy_content_sha256(spec: AggregateFrontierReduceSpec3D) -> str:
    """Hash every semantic hierarchy column, not merely shape metadata."""

    hierarchy = spec.prepared_hierarchy.hierarchy
    return _digest({
        name: getattr(hierarchy, name)
        for name in (
            "point_x", "point_y", "point_z", "point_weight",
            "node_cx", "node_cy", "node_cz", "node_half_size", "node_weight",
            "member_offsets", "member_indices", "child_offsets", "child_indices",
            "node_next_index", "node_rope_index", "source_leaf_node_index",
            "node_subtree_end_index",
        )
    })


def _spec_digest(spec: AggregateFrontierReduceSpec3D) -> str:
    return _digest(spec.to_metadata())


def compile_hierarchy_frontier(
    spec: AggregateFrontierReduceSpec3D,
    schema: HierarchyFrontierSchema,
) -> CompiledHierarchyFrontier:
    if not isinstance(spec, AggregateFrontierReduceSpec3D):
        _fail("spec", "spec", "AggregateFrontierReduceSpec3D required")
    if not isinstance(schema, HierarchyFrontierSchema):
        _fail("schema", "schema", "HierarchyFrontierSchema required")
    if schema.schema_id != HIERARCHY_FRONTIER_SCHEMA_ID \
            or schema.schema_version != HIERARCHY_FRONTIER_SCHEMA_VERSION:
        _fail("schema_identity", "schema", "unsupported schema")
    _sha(schema.producer_contract_sha256, "schema.producer_contract_sha256")
    _sha(schema.hierarchy_sha256, "schema.hierarchy_sha256")
    if not isinstance(schema.reducer, HierarchyReducer):
        _fail("reducer", "schema.reducer", "closed reducer enum required")
    hierarchy = spec.prepared_hierarchy.hierarchy
    if schema.hierarchy_sha256 != hierarchy_content_sha256(spec):
        _fail("hierarchy_binding", "schema", "exact hierarchy metadata required")
    if schema.reducer.value != spec.reducer:
        _fail("reducer_binding", "schema.reducer", "schema/spec reducer mismatch")
    if not isinstance(spec.opening, ContinuationPayloadOpening):
        _fail("opening", "spec.opening", "continuation payload opening required")
    if hierarchy.node_next_index is None or hierarchy.node_rope_index is None:
        _fail("continuation", "spec.hierarchy", "next and rope columns required")
    roots = set(range(hierarchy.node_count)) - set(hierarchy.child_indices)
    if len(roots) != 1:
        _fail("root_count", "spec.hierarchy", "one threaded root required")
    if not isinstance(schema.maximum_output_rows, int) \
            or isinstance(schema.maximum_output_rows, bool) \
            or not hierarchy.point_count <= schema.maximum_output_rows <= U32_MAX:
        _fail("output_capacity", "schema.maximum_output_rows", "complete u32 capacity required")
    exact_visit_bound = hierarchy.node_count * 2 + 1
    if schema.maximum_visits_per_source != exact_visit_bound:
        _fail(
            "visit_bound", "schema.maximum_visits_per_source",
            f"must equal compiler-derived bound {exact_visit_bound}",
        )
    body = {
        "schema_sha256": schema.schema_sha256,
        "spec_sha256": _spec_digest(spec),
        "node_count": hierarchy.node_count,
        "point_count": hierarchy.point_count,
        "selected_template": AGGREGATE_HIERARCHY_OPTIX_TEMPLATE,
        "program_bundle": HIERARCHY_FRONTIER_PROGRAM_BUNDLE,
    }
    plan_sha = _digest(body)
    seal = hmac.new(_PLAN_KEY, plan_sha.encode("ascii"), hashlib.sha256).hexdigest()
    return CompiledHierarchyFrontier(
        schema=schema,
        spec_sha256=body["spec_sha256"],
        node_count=hierarchy.node_count,
        point_count=hierarchy.point_count,
        plan_sha256=plan_sha,
        compiler_seal=seal,
    )


def _verify_compiled(
    compiled: CompiledHierarchyFrontier,
    spec: AggregateFrontierReduceSpec3D,
) -> None:
    fresh = compile_hierarchy_frontier(spec, compiled.schema)
    if fresh != compiled or not hmac.compare_digest(
        compiled.compiler_seal,
        hmac.new(
            _PLAN_KEY, compiled.plan_sha256.encode("ascii"), hashlib.sha256,
        ).hexdigest(),
    ):
        _fail("plan_authority", "compiled", "compiler-owned exact plan required")


def _prepared_static_authority_payload(
    compiled: CompiledHierarchyFrontier,
    spec: AggregateFrontierReduceSpec3D,
) -> tuple[object, ...]:
    """Return the constant-size identity binding for one prepared owner.

    Full semantic validation and hashing happens once in ``__init__``.  All
    hierarchy columns are immutable tuples after construction, so subsequent
    executions only need to prove that the compiler-owned object graph and its
    scalar policy fields have not been replaced.  This is not a trust-on-name
    shortcut: replacing any frozen object with ``object.__setattr__`` changes
    one of the identities or scalar values below and fails closed.
    """

    prepared = spec.prepared_hierarchy
    hierarchy = prepared.hierarchy
    opening = spec.opening
    schema = compiled.schema
    return (
        "rtdl.v4.prepared_hierarchy_static_authority.v1",
        id(compiled),
        id(schema),
        schema.producer_contract_sha256,
        schema.hierarchy_sha256,
        schema.reducer.value,
        schema.maximum_output_rows,
        schema.maximum_visits_per_source,
        schema.schema_id,
        schema.schema_version,
        compiled.spec_sha256,
        compiled.node_count,
        compiled.point_count,
        compiled.plan_sha256,
        compiled.compiler_seal,
        id(spec),
        id(prepared),
        prepared.backend,
        prepared.producer_consumer_stream_ordering,
        id(hierarchy),
        tuple(
            (name, id(getattr(hierarchy, name)))
            for name in _HIERARCHY_COLUMN_NAMES
        ),
        id(opening),
        type(opening).__module__,
        type(opening).__qualname__,
        getattr(opening, "max_ratio", None),
        spec.reducer,
    )


def _prepared_static_authority_seal(payload: tuple[object, ...]) -> str:
    return hmac.new(
        _PREPARED_AUTHORITY_KEY,
        repr(payload).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _verify_receipt(receipt: Mapping[str, object], output_sha256: str) -> None:
    body = dict(receipt)
    claimed = body.pop("receipt_sha256", None)
    if claimed != _digest(body):
        _fail("receipt_digest", "receipt", "receipt digest mismatch")
    snapshot = receipt.get("native_snapshot")
    if type(snapshot) is not dict:
        _fail("receipt", "receipt.native_snapshot", "exact dict required")
    successful = snapshot.get("successful_launch_count")
    if (
        receipt.get("physical_executor_classification")
        != "optix_traversal_observed"
        or not isinstance(successful, int)
        or successful <= 0
        or snapshot.get("complete_context_launch_count") != successful
        or snapshot.get("failed_launch_count") != 0
        or snapshot.get("incomplete_context_launch_count") != 0
        or snapshot.get("pending_context_at_finish") != 0
        or snapshot.get("session_error") != 0
        or not snapshot.get("first_traversable")
        or not snapshot.get("last_traversable")
        or receipt.get("expected_program_observed_at_receipt_edge") is not True
        or receipt.get("output_digest") != output_sha256
    ):
        _fail("behavioral_optix", "receipt", "complete bound traversal required")


def _packed_binding_seal_payload(
    binding: _VerifiedPackedHierarchyRowsBinding,
) -> bytes:
    return repr((
        "rtdl.v4.hierarchy_frontier.packed_binding_authority.v1",
        id(binding.rows),
        binding.output_sha256,
        binding.plan_sha256,
        binding.point_count,
        binding.endpoint_identity,
        binding.selected_backend,
        binding.selected_template,
        binding.physical_executor_kind,
    )).encode("utf-8")


def _seal_packed_binding(
    binding: _VerifiedPackedHierarchyRowsBinding,
) -> str:
    return hmac.new(
        _PACKED_OUTPUT_BINDING_KEY,
        _packed_binding_seal_payload(binding),
        hashlib.sha256,
    ).hexdigest()


def _bind_canonical_packed_hierarchy_endpoint(
    compiled: CompiledHierarchyFrontier,
    endpoint: Mapping[str, object],
) -> _VerifiedPackedHierarchyRowsBinding:
    """Consume the provider's vectorized canonical-column authority.

    The trusted provider already owns the typed output columns.  It validates
    and hashes them before creating immutable public rows, so the compiler does
    not serialize or rescan the same 32K-row object graph.  Missing, replaced
    or replayed provider authority fails closed.
    """

    try:
        raw_rows, output_sha256 = consume_canonical_hierarchy_output_binding(
            endpoint
        )
    except (RuntimeError, TypeError, ValueError) as exc:
        _fail("packed_binding", "endpoint", str(exc))
    if len(raw_rows) != compiled.point_count:
        _fail("complete_output", "endpoint", "one complete row per source required")
    metadata = endpoint.get("metadata")
    if type(metadata) is not dict:
        _fail("physical_identity", "endpoint.metadata", "exact dict required")
    physical_executor_kind = metadata.get("physical_executor_kind")
    if (
        endpoint.get("selected_backend") != "optix_traversal"
        or endpoint.get("selected_template") != AGGREGATE_HIERARCHY_OPTIX_TEMPLATE
        or physical_executor_kind
        != "true_optix_triangle_traversal_with_exact_f64_opening"
    ):
        _fail("physical_identity", "endpoint", "registered true-OptiX family required")
    provisional = _VerifiedPackedHierarchyRowsBinding(
        rows=raw_rows,
        output_sha256=output_sha256,
        plan_sha256=compiled.plan_sha256,
        point_count=compiled.point_count,
        endpoint_identity=id(endpoint),
        selected_backend=str(endpoint["selected_backend"]),
        selected_template=str(endpoint["selected_template"]),
        physical_executor_kind=str(physical_executor_kind),
        authority_seal="",
    )
    return _VerifiedPackedHierarchyRowsBinding(
        **{
            **provisional.__dict__,
            "authority_seal": _seal_packed_binding(provisional),
        }
    )


def _accept_hierarchy_endpoint(
    compiled: CompiledHierarchyFrontier,
    endpoint: Mapping[str, object],
    receipt: Mapping[str, object],
    *,
    binding: _VerifiedPackedHierarchyRowsBinding,
) -> HierarchyFrontierResult:
    """Accept only the private immutable binding issued for this endpoint."""

    if type(binding) is not _VerifiedPackedHierarchyRowsBinding:
        _fail("packed_binding", "binding", "private verified binding required")
    _verify_receipt(receipt, binding.output_sha256)
    if (
        binding.plan_sha256 != compiled.plan_sha256
        or binding.point_count != compiled.point_count
        or binding.endpoint_identity != id(endpoint)
        or binding.selected_backend != endpoint.get("selected_backend")
        or binding.selected_template != endpoint.get("selected_template")
        or type(endpoint.get("metadata")) is not dict
        or binding.physical_executor_kind
        != endpoint["metadata"].get("physical_executor_kind")
        or not hmac.compare_digest(
            binding.authority_seal, _seal_packed_binding(
                _VerifiedPackedHierarchyRowsBinding(
                    **{**binding.__dict__, "authority_seal": ""}
                )
            ),
        )
    ):
        _fail("packed_binding", "binding", "binding authority changed or replayed")
    metadata = dict(endpoint["metadata"])
    if (
        binding.selected_backend != "optix_traversal"
        or binding.selected_template != AGGREGATE_HIERARCHY_OPTIX_TEMPLATE
        or binding.physical_executor_kind
        != "true_optix_triangle_traversal_with_exact_f64_opening"
    ):
        _fail("physical_identity", "endpoint", "registered true-OptiX family required")
    return HierarchyFrontierResult(
        rows=binding.rows,
        output_sha256=binding.output_sha256,
        plan_sha256=compiled.plan_sha256,
        traversal_receipt=dict(receipt),
        endpoint_metadata=metadata,
    )


class PreparedHierarchyFrontierOwner:
    """Explicit owner reusing the existing generic hierarchy native handle."""

    def __init__(
        self,
        compiled: CompiledHierarchyFrontier,
        spec: AggregateFrontierReduceSpec3D,
    ) -> None:
        started = time.perf_counter()
        _verify_compiled(compiled, spec)
        plan = compile_aggregate_frontier_reduce_candidate_for_functional_validation_3d(
            spec,
            physical_candidate="optix_traversal",
            max_output_rows=compiled.schema.maximum_output_rows,
        )
        if plan.selected_template != AGGREGATE_HIERARCHY_OPTIX_TEMPLATE:
            _fail("physical_identity", "plan", "true-OptiX hierarchy plan required")
        self._compiled = compiled
        self._spec = spec
        self._native = PreparedNativeAggregateHierarchy3D(plan)
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._nonce = secrets.token_hex(16)
        self._active = threading.Lock()
        self._closed = False
        self._execution_count = 0
        self._static_authority_payload = _prepared_static_authority_payload(
            compiled, spec)
        self._static_authority_seal = _prepared_static_authority_seal(
            self._static_authority_payload)
        self.prepare_seconds = time.perf_counter() - started
        self._session_identity = _digest({
            "schema": "rtdl.v4.prepared_hierarchy_frontier_owner.v1",
            "plan": compiled.plan_sha256,
            "spec": compiled.spec_sha256,
            "pid": self._pid,
            "thread": self._thread,
            "nonce": self._nonce,
        })

    def __getstate__(self):
        raise RuntimeError("prepared hierarchy owner cannot be serialized")

    def _check_owner(self) -> None:
        if self._closed:
            raise RuntimeError("prepared hierarchy owner is closed")
        if os.getpid() != self._pid:
            raise RuntimeError("prepared hierarchy owner crossed process boundary")
        if threading.get_ident() != self._thread:
            raise RuntimeError("prepared hierarchy owner crossed thread boundary")

    def _check_static_authority(self) -> None:
        current = _prepared_static_authority_payload(
            self._compiled, self._spec)
        if (
            current != self._static_authority_payload
            or not hmac.compare_digest(
                self._static_authority_seal,
                _prepared_static_authority_seal(current),
            )
        ):
            _fail(
                "prepared_static_authority",
                "prepared",
                "compiled plan, schema, hierarchy, or policy changed after prepare",
            )

    @property
    def lifecycle_receipt(self) -> dict[str, object]:
        self._check_owner()
        return {
            "schema": "rtdl.v4.prepared_application_lifecycle.v1",
            "session_identity": self._session_identity,
            "plan_sha256": self._compiled.plan_sha256,
            "process_bound": True,
            "thread_bound": True,
            "nonserializable": True,
            "nonreentrant": True,
            "prepare_seconds_reported_separately": True,
            "cold_result_replaced": False,
            "execution_count": self._execution_count,
        }

    def execute(self, *, softening: float = 0.0) -> HierarchyFrontierResult:
        self._check_owner()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("prepared hierarchy owner is already executing")
        try:
            self._check_static_authority()
            library = self._native._library
            audit = OptixTraversalAuditSession.open(library=library)
            try:
                endpoint = self._native.execute(
                    softening=softening,
                    canonical_output_binding=True,
                )
                binding = _bind_canonical_packed_hierarchy_endpoint(
                    self._compiled, endpoint)
                receipt = audit.finish(
                    semantic_digest=self._compiled.spec_sha256,
                    output_digest=binding.output_sha256,
                    route_identity="v4_generic_bounded_hierarchy_frontier_reduce",
                    expected_program_bundles=(HIERARCHY_FRONTIER_PROGRAM_BUNDLE,),
                )
            except Exception:
                audit.abort()
                raise
            accepted = _accept_hierarchy_endpoint(
                self._compiled, endpoint, receipt,
                binding=binding)
            self._execution_count += 1
            return accepted
        finally:
            self._active.release()

    def close(self) -> None:
        self._check_owner()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("cannot close prepared hierarchy owner during execution")
        try:
            self._native.close()
            self._closed = True
        finally:
            self._active.release()

    def __enter__(self):
        self._check_owner()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_hierarchy_frontier(
    compiled: CompiledHierarchyFrontier,
    spec: AggregateFrontierReduceSpec3D,
) -> PreparedHierarchyFrontierOwner:
    return PreparedHierarchyFrontierOwner(compiled, spec)


def execute_hierarchy_frontier(
    compiled: CompiledHierarchyFrontier,
    spec: AggregateFrontierReduceSpec3D,
    *,
    softening: float = 0.0,
) -> HierarchyFrontierResult:
    """Execute one complete bounded true-OptiX hierarchy result."""

    _verify_compiled(compiled, spec)
    library = optix_runtime._load_optix_library()
    semantic_digest = compiled.spec_sha256
    with OptixTraversalAuditSession.open(library=library) as audit:
        endpoint = run_aggregate_frontier_reduce_candidate_for_functional_validation_3d(
            spec,
            physical_candidate="optix_traversal",
            softening=softening,
            max_output_rows=compiled.schema.maximum_output_rows,
            canonical_output_binding=True,
        )
        binding = _bind_canonical_packed_hierarchy_endpoint(compiled, endpoint)
        receipt = audit.finish(
            semantic_digest=semantic_digest,
            output_digest=binding.output_sha256,
            route_identity="v4_generic_bounded_hierarchy_frontier_reduce",
            expected_program_bundles=(HIERARCHY_FRONTIER_PROGRAM_BUNDLE,),
        )
    return _accept_hierarchy_endpoint(
        compiled, endpoint, receipt, binding=binding)


__all__ = (
    "CompiledHierarchyFrontier",
    "HierarchyFrontierError",
    "HierarchyFrontierResult",
    "HierarchyFrontierSchema",
    "HierarchyReducer",
    "PreparedHierarchyFrontierOwner",
    "compile_hierarchy_frontier",
    "execute_hierarchy_frontier",
    "hierarchy_content_sha256",
    "prepare_hierarchy_frontier",
)
