from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import json
import secrets
from typing import Mapping, NoReturn

from .action_ir import (
    ActionScalarKind,
    ActionScalarType,
    ActionSpec,
    StateScope,
)


ACTION_COMPOSITION_VERSION = "rtdl.action_consumer_composition.private_candidate.v1"
UINT32_MAX = (1 << 32) - 1
_COMPOSITION_SECRET = secrets.token_bytes(32)


class ActionConsumerCompositionKind(str, Enum):
    """Closed compiler-owned consumers that may follow a verified Action."""

    CERTIFIED_NEAREST_TO_GLOBAL_ARGMAX_WITH_WITNESS = (
        "certified_per_query_nearest_to_global_argmax_with_witness.v1"
    )


class ActionReducerOrder(str, Enum):
    """Total reducer orders whose tie behavior is part of semantics."""

    MAX_F64_THEN_LOWEST_SOURCE_ROW_THEN_LOWEST_ITEM_U32 = (
        "max_f64__tie_lowest_source_row__then_lowest_item_u32.v1"
    )


@dataclass(frozen=True)
class ActionCompositionOutputField:
    name: str
    scalar_kind: ActionScalarKind

    def to_metadata(self) -> dict[str, str]:
        return {"name": self.name, "scalar_kind": self.scalar_kind.value}


@dataclass(frozen=True)
class ActionConsumerCompositionResources:
    """Backend-independent semantic resource contract used during placement."""

    kind: ActionConsumerCompositionKind
    query_count: int
    output_row_bound: int
    output_byte_bound: int
    producer_state_bytes_per_query: int
    reducer_state_bytes: int
    total_state_byte_bound: int

    def to_metadata(self) -> dict[str, object]:
        return {
            "consumer_kind": self.kind.value,
            "query_count": self.query_count,
            "output_row_bound": self.output_row_bound,
            "output_byte_bound": self.output_byte_bound,
            "producer_state_bytes_per_query": self.producer_state_bytes_per_query,
            "reducer_state_bytes": self.reducer_state_bytes,
            "total_state_byte_bound": self.total_state_byte_bound,
            "state_bound": "query_count*(f64+u32)+(f64+u32+u32)",
            "state_resource_scope": (
                "action_semantic_state_only__native_target_index_and_scratch_separate"
            ),
            "backend_independent": True,
        }


@dataclass(frozen=True)
class ActionConsumerCompositionCertificate:
    """Signed compiler proof for one producer-to-consumer composition.

    This is deliberately separate from application metadata.  It binds the
    verified Action, its closed producer and selected physical template to one
    complete-input reducer with a fixed output schema and total tie order.
    """

    kind: ActionConsumerCompositionKind
    action_semantic_digest: str
    action_source_digest: str
    producer_kind: str
    producer_binding_digest: str
    selected_backend: str
    selected_placement: str
    selected_template: str
    template_identity_digest: str
    query_field: str
    candidate_field: str
    distance_field: str
    distance_state_name: str
    candidate_state_name: str
    query_count: int
    full_input_required: bool
    reducer_order: ActionReducerOrder
    output_schema: tuple[ActionCompositionOutputField, ...]
    output_row_bound: int
    output_byte_bound: int
    producer_state_bytes_per_query: int
    reducer_state_bytes: int
    total_state_byte_bound: int
    composition_digest: str
    _signature: str

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": ACTION_COMPOSITION_VERSION,
            "consumer_kind": self.kind.value,
            "action_semantic_digest": self.action_semantic_digest,
            "action_source_digest": self.action_source_digest,
            "producer_kind": self.producer_kind,
            "producer_binding_digest": self.producer_binding_digest,
            "selected_backend": self.selected_backend,
            "selected_placement": self.selected_placement,
            "selected_template": self.selected_template,
            "template_identity_digest": self.template_identity_digest,
            "query_field": self.query_field,
            "candidate_field": self.candidate_field,
            "distance_field": self.distance_field,
            "distance_state_name": self.distance_state_name,
            "candidate_state_name": self.candidate_state_name,
            "query_count": self.query_count,
            "full_input_required": self.full_input_required,
            "input_coverage_contract": "all_certified_query_state_rows_exactly_once",
            "reducer_order": self.reducer_order.value,
            "output_schema": [field.to_metadata() for field in self.output_schema],
            "output_row_bound": self.output_row_bound,
            "output_byte_bound": self.output_byte_bound,
            "producer_state_bytes_per_query": self.producer_state_bytes_per_query,
            "reducer_state_bytes": self.reducer_state_bytes,
            "total_state_byte_bound": self.total_state_byte_bound,
            "state_bound": "query_count*(f64+u32)+(f64+u32+u32)",
            "state_resource_scope": (
                "action_semantic_state_only__native_target_index_and_scratch_separate"
            ),
            "composition_digest": self.composition_digest,
            "compiler_issued": True,
            "certificate_integrity_checked": True,
            "application_identity_bound": False,
            "backend_may_append_consumer_implicitly": False,
        }


class ActionCompositionError(ValueError):
    pass


def action_template_identity_digest(metadata: Mapping[str, object]) -> str:
    if not isinstance(metadata, Mapping):
        _fail("template metadata must be a mapping")
    payload = json.dumps(
        dict(metadata), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(
        b"rtdl.action_template_identity.v1\x00" + payload
    ).hexdigest()


def issue_certified_nearest_global_argmax_composition(
    spec: ActionSpec,
    *,
    action_source_digest: str,
    producer_kind: str,
    producer_binding_digest: str,
    selected_backend: str,
    selected_placement: str,
    selected_template: str,
    template_identity_digest: str,
    query_field: str,
    candidate_field: str,
    distance_field: str,
    distance_state_name: str,
    candidate_state_name: str,
    query_count: int,
) -> ActionConsumerCompositionCertificate:
    """Validate and sign the generic nearest-state/global-witness pipeline."""

    resources = certified_nearest_global_argmax_resources(
        spec,
        query_field=query_field,
        candidate_field=candidate_field,
        distance_field=distance_field,
        distance_state_name=distance_state_name,
        candidate_state_name=candidate_state_name,
        query_count=query_count,
    )
    for label, value in (
        ("action_source_digest", action_source_digest),
        ("producer_binding_digest", producer_binding_digest),
    ):
        if not _is_sha256(value):
            _fail(f"{label} must be a SHA-256 digest")
    if producer_kind != "certified_nearest_state_3d.v1":
        _fail("certified nearest/global composition requires its closed producer")
    if selected_template not in {
        "certified_nearest_state_3d",
        "certified_nearest_state_3d_optix_traversal",
        "cell_mbr_exact_witness_3d_optix_traversal",
        "cpu_reference_interpreter",
    }:
        _fail("selected template cannot implement certified nearest/global composition")
    if not _is_sha256(template_identity_digest):
        _fail("template_identity_digest must be a SHA-256 digest")

    output_schema = (
        ActionCompositionOutputField("source_id", ActionScalarKind.U32),
        ActionCompositionOutputField("item_id", ActionScalarKind.U32),
        ActionCompositionOutputField("value", ActionScalarKind.F64),
    )
    unsigned = {
        "contract": ACTION_COMPOSITION_VERSION,
        "consumer_kind": (
            ActionConsumerCompositionKind.CERTIFIED_NEAREST_TO_GLOBAL_ARGMAX_WITH_WITNESS.value
        ),
        "action_semantic_digest": spec.semantic_digest,
        "action_source_digest": action_source_digest,
        "producer_kind": producer_kind,
        "producer_binding_digest": producer_binding_digest,
        "selected_backend": selected_backend,
        "selected_placement": selected_placement,
        "selected_template": selected_template,
        "template_identity_digest": template_identity_digest,
        "query_field": query_field,
        "candidate_field": candidate_field,
        "distance_field": distance_field,
        "distance_state_name": distance_state_name,
        "candidate_state_name": candidate_state_name,
        "query_count": query_count,
        "full_input_required": True,
        "reducer_order": (
            ActionReducerOrder.MAX_F64_THEN_LOWEST_SOURCE_ROW_THEN_LOWEST_ITEM_U32.value
        ),
        "output_schema": [field.to_metadata() for field in output_schema],
        "output_row_bound": resources.output_row_bound,
        "output_byte_bound": resources.output_byte_bound,
        "producer_state_bytes_per_query": resources.producer_state_bytes_per_query,
        "reducer_state_bytes": resources.reducer_state_bytes,
        "total_state_byte_bound": resources.total_state_byte_bound,
    }
    payload = _payload(unsigned)
    digest = hashlib.sha256(payload).hexdigest()
    signature = hmac.new(_COMPOSITION_SECRET, payload, hashlib.sha256).hexdigest()
    return ActionConsumerCompositionCertificate(
        kind=(
            ActionConsumerCompositionKind.CERTIFIED_NEAREST_TO_GLOBAL_ARGMAX_WITH_WITNESS
        ),
        action_semantic_digest=spec.semantic_digest,
        action_source_digest=action_source_digest,
        producer_kind=producer_kind,
        producer_binding_digest=producer_binding_digest,
        selected_backend=selected_backend,
        selected_placement=selected_placement,
        selected_template=selected_template,
        template_identity_digest=template_identity_digest,
        query_field=query_field,
        candidate_field=candidate_field,
        distance_field=distance_field,
        distance_state_name=distance_state_name,
        candidate_state_name=candidate_state_name,
        query_count=query_count,
        full_input_required=True,
        reducer_order=(
            ActionReducerOrder.MAX_F64_THEN_LOWEST_SOURCE_ROW_THEN_LOWEST_ITEM_U32
        ),
        output_schema=output_schema,
        output_row_bound=resources.output_row_bound,
        output_byte_bound=resources.output_byte_bound,
        producer_state_bytes_per_query=resources.producer_state_bytes_per_query,
        reducer_state_bytes=resources.reducer_state_bytes,
        total_state_byte_bound=resources.total_state_byte_bound,
        composition_digest=digest,
        _signature=signature,
    )


def certified_nearest_global_argmax_resources(
    spec: ActionSpec,
    *,
    query_field: str,
    candidate_field: str,
    distance_field: str,
    distance_state_name: str,
    candidate_state_name: str,
    query_count: int,
) -> ActionConsumerCompositionResources:
    """Validate the semantic shape and price it before any backend is chosen."""

    _validate_nearest_state_shape(
        spec,
        query_field=query_field,
        candidate_field=candidate_field,
        distance_field=distance_field,
        distance_state_name=distance_state_name,
        candidate_state_name=candidate_state_name,
    )
    if not isinstance(query_count, int) or isinstance(query_count, bool):
        _fail("query_count must be an integer")
    if query_count <= 0 or query_count > UINT32_MAX:
        _fail("query_count must be in [1, UINT32_MAX]")
    return ActionConsumerCompositionResources(
        kind=(
            ActionConsumerCompositionKind.CERTIFIED_NEAREST_TO_GLOBAL_ARGMAX_WITH_WITNESS
        ),
        query_count=query_count,
        output_row_bound=1,
        output_byte_bound=16,
        producer_state_bytes_per_query=12,
        reducer_state_bytes=16,
        total_state_byte_bound=query_count * 12 + 16,
    )


def validate_certified_nearest_global_argmax_composition(
    certificate: ActionConsumerCompositionCertificate,
    *,
    spec: ActionSpec,
    action_source_digest: str,
    producer_kind: str,
    producer_binding_digest: str,
    selected_backend: str,
    selected_placement: str,
    selected_template: str,
    template_identity_digest: str,
    query_count: int,
) -> None:
    """Fail closed if a certificate was forged or attached to another plan."""

    if not isinstance(certificate, ActionConsumerCompositionCertificate):
        _fail("typed ActionConsumerCompositionCertificate required")
    _validate_nearest_state_shape(
        spec,
        query_field=certificate.query_field,
        candidate_field=certificate.candidate_field,
        distance_field=certificate.distance_field,
        distance_state_name=certificate.distance_state_name,
        candidate_state_name=certificate.candidate_state_name,
    )
    expected = {
        "action_semantic_digest": spec.semantic_digest,
        "action_source_digest": action_source_digest,
        "producer_kind": producer_kind,
        "producer_binding_digest": producer_binding_digest,
        "selected_backend": selected_backend,
        "selected_placement": selected_placement,
        "selected_template": selected_template,
        "template_identity_digest": template_identity_digest,
        "query_count": query_count,
    }
    for name, value in expected.items():
        if getattr(certificate, name) != value:
            _fail(f"composition {name} does not match the selected Action plan")
    if (
        certificate.kind
        is not ActionConsumerCompositionKind.CERTIFIED_NEAREST_TO_GLOBAL_ARGMAX_WITH_WITNESS
        or not certificate.full_input_required
        or certificate.reducer_order
        is not ActionReducerOrder.MAX_F64_THEN_LOWEST_SOURCE_ROW_THEN_LOWEST_ITEM_U32
        or certificate.output_row_bound != 1
        or certificate.output_byte_bound != 16
        or certificate.producer_state_bytes_per_query != 12
        or certificate.reducer_state_bytes != 16
        or certificate.total_state_byte_bound != query_count * 12 + 16
        or certificate.output_schema
        != (
            ActionCompositionOutputField("source_id", ActionScalarKind.U32),
            ActionCompositionOutputField("item_id", ActionScalarKind.U32),
            ActionCompositionOutputField("value", ActionScalarKind.F64),
        )
    ):
        _fail("composition semantic/resource contract was modified")
    unsigned = _unsigned(certificate)
    payload = _payload(unsigned)
    digest = hashlib.sha256(payload).hexdigest()
    signature = hmac.new(_COMPOSITION_SECRET, payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(certificate.composition_digest, digest) or not hmac.compare_digest(
        certificate._signature, signature
    ):
        _fail("composition certificate signature is invalid")


def validate_certified_nearest_global_argmax_composition_metadata(
    metadata: Mapping[str, object],
) -> dict[str, object]:
    """Validate the complete persisted certificate and its public digest.

    Persisted evidence intentionally omits the process-local HMAC.  This
    validator therefore proves schema, semantic/resource invariants, and the
    reproducible public composition digest; it does not relabel that digest as
    the private compiler signature.
    """

    if not isinstance(metadata, Mapping):
        _fail("composition metadata must be a mapping")
    value = dict(metadata)
    unsigned_keys = {
        "contract",
        "consumer_kind",
        "action_semantic_digest",
        "action_source_digest",
        "producer_kind",
        "producer_binding_digest",
        "selected_backend",
        "selected_placement",
        "selected_template",
        "template_identity_digest",
        "query_field",
        "candidate_field",
        "distance_field",
        "distance_state_name",
        "candidate_state_name",
        "query_count",
        "full_input_required",
        "reducer_order",
        "output_schema",
        "output_row_bound",
        "output_byte_bound",
        "producer_state_bytes_per_query",
        "reducer_state_bytes",
        "total_state_byte_bound",
    }
    annotation_values = {
        "input_coverage_contract": "all_certified_query_state_rows_exactly_once",
        "state_bound": "query_count*(f64+u32)+(f64+u32+u32)",
        "state_resource_scope": (
            "action_semantic_state_only__native_target_index_and_scratch_separate"
        ),
        "compiler_issued": True,
        "certificate_integrity_checked": True,
        "application_identity_bound": False,
        "backend_may_append_consumer_implicitly": False,
    }
    expected_keys = unsigned_keys | set(annotation_values) | {"composition_digest"}
    if set(value) != expected_keys:
        _fail("composition metadata fields differ from the complete schema")
    if any(
        type(value[name]) is not type(expected) or value[name] != expected
        for name, expected in annotation_values.items()
    ):
        _fail("composition metadata annotations differ")
    expected_strings = {
        "contract": ACTION_COMPOSITION_VERSION,
        "consumer_kind": (
            ActionConsumerCompositionKind.CERTIFIED_NEAREST_TO_GLOBAL_ARGMAX_WITH_WITNESS.value
        ),
        "producer_kind": "certified_nearest_state_3d.v1",
        "query_field": "query_id",
        "candidate_field": "candidate_id",
        "distance_field": "distance",
        "distance_state_name": "best_distance",
        "candidate_state_name": "best_id",
        "reducer_order": (
            ActionReducerOrder.MAX_F64_THEN_LOWEST_SOURCE_ROW_THEN_LOWEST_ITEM_U32.value
        ),
    }
    for name, expected in expected_strings.items():
        if type(value[name]) is not str or value[name] != expected:
            _fail(f"composition metadata {name} differs")
    for name in (
        "selected_backend",
        "selected_placement",
        "selected_template",
    ):
        if type(value[name]) is not str or not value[name]:
            _fail(f"composition metadata {name} must be a nonempty string")
    for name in (
        "action_semantic_digest",
        "action_source_digest",
        "producer_binding_digest",
        "template_identity_digest",
        "composition_digest",
    ):
        if not _is_sha256(value[name]):
            _fail(f"composition metadata {name} must be a SHA-256 digest")
    if value["full_input_required"] is not True:
        _fail("composition metadata must require the complete producer input")
    query_count = value["query_count"]
    exact_ints = {
        "output_row_bound": 1,
        "output_byte_bound": 16,
        "producer_state_bytes_per_query": 12,
        "reducer_state_bytes": 16,
    }
    if (
        not isinstance(query_count, int)
        or isinstance(query_count, bool)
        or query_count <= 0
        or query_count > UINT32_MAX
    ):
        _fail("composition metadata query_count is invalid")
    for name, expected in exact_ints.items():
        actual = value[name]
        if not isinstance(actual, int) or isinstance(actual, bool) or actual != expected:
            _fail(f"composition metadata {name} differs")
    total_state = value["total_state_byte_bound"]
    if (
        not isinstance(total_state, int)
        or isinstance(total_state, bool)
        or total_state != query_count * 12 + 16
    ):
        _fail("composition metadata total_state_byte_bound differs")
    if value["output_schema"] != [
        {"name": "source_id", "scalar_kind": "u32"},
        {"name": "item_id", "scalar_kind": "u32"},
        {"name": "value", "scalar_kind": "f64"},
    ]:
        _fail("composition metadata output schema differs")
    unsigned = {name: value[name] for name in unsigned_keys}
    digest = hashlib.sha256(_payload(unsigned)).hexdigest()
    if not hmac.compare_digest(value["composition_digest"], digest):
        _fail("composition metadata public digest is invalid")
    return value


def _validate_nearest_state_shape(
    spec: ActionSpec,
    *,
    query_field: str,
    candidate_field: str,
    distance_field: str,
    distance_state_name: str,
    candidate_state_name: str,
) -> None:
    query = spec.event_type.field(query_field)
    candidate = spec.event_type.field(candidate_field)
    distance = spec.event_type.field(distance_field)
    if not _scalar_is(query, ActionScalarKind.U32):
        _fail("nearest-state query/source field must be U32")
    if not _scalar_is(candidate, ActionScalarKind.U32):
        _fail("nearest-state candidate field must be U32")
    if not _scalar_is(distance, ActionScalarKind.F64):
        _fail("nearest-state distance field must be F64")
    states = {state.name: state for state in spec.states}
    distance_state = states.get(distance_state_name)
    candidate_state = states.get(candidate_state_name)
    if distance_state is None or not _scalar_type_is(
        distance_state.value_type, ActionScalarKind.F64
    ):
        _fail("nearest-state distance state must be F64")
    if candidate_state is None or not _scalar_type_is(
        candidate_state.value_type, ActionScalarKind.U32
    ):
        _fail("nearest-state candidate state must be U32")
    for state in (distance_state, candidate_state):
        if state.scope is not StateScope.PER_QUERY or state.key_fields != (query_field,):
            _fail("nearest-state reducer inputs must have per-query source scope")


def _scalar_is(field, kind: ActionScalarKind) -> bool:
    return field is not None and _scalar_type_is(field.value_type, kind)


def _scalar_type_is(value_type, kind: ActionScalarKind) -> bool:
    return isinstance(value_type, ActionScalarType) and value_type.kind is kind


def _unsigned(certificate: ActionConsumerCompositionCertificate) -> dict[str, object]:
    return {
        "contract": ACTION_COMPOSITION_VERSION,
        "consumer_kind": certificate.kind.value,
        "action_semantic_digest": certificate.action_semantic_digest,
        "action_source_digest": certificate.action_source_digest,
        "producer_kind": certificate.producer_kind,
        "producer_binding_digest": certificate.producer_binding_digest,
        "selected_backend": certificate.selected_backend,
        "selected_placement": certificate.selected_placement,
        "selected_template": certificate.selected_template,
        "template_identity_digest": certificate.template_identity_digest,
        "query_field": certificate.query_field,
        "candidate_field": certificate.candidate_field,
        "distance_field": certificate.distance_field,
        "distance_state_name": certificate.distance_state_name,
        "candidate_state_name": certificate.candidate_state_name,
        "query_count": certificate.query_count,
        "full_input_required": certificate.full_input_required,
        "reducer_order": certificate.reducer_order.value,
        "output_schema": [field.to_metadata() for field in certificate.output_schema],
        "output_row_bound": certificate.output_row_bound,
        "output_byte_bound": certificate.output_byte_bound,
        "producer_state_bytes_per_query": certificate.producer_state_bytes_per_query,
        "reducer_state_bytes": certificate.reducer_state_bytes,
        "total_state_byte_bound": certificate.total_state_byte_bound,
    }


def _payload(unsigned: dict[str, object]) -> bytes:
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _is_sha256(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _fail(message: str) -> NoReturn:
    raise ActionCompositionError(message)


__all__ = (
    "ACTION_COMPOSITION_VERSION",
    "UINT32_MAX",
    "ActionCompositionError",
    "ActionCompositionOutputField",
    "ActionConsumerCompositionCertificate",
    "ActionConsumerCompositionKind",
    "ActionConsumerCompositionResources",
    "ActionReducerOrder",
    "action_template_identity_digest",
    "certified_nearest_global_argmax_resources",
    "issue_certified_nearest_global_argmax_composition",
    "validate_certified_nearest_global_argmax_composition",
    "validate_certified_nearest_global_argmax_composition_metadata",
)
