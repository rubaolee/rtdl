"""Typed physical-schema admission and non-executable reference lowering.

This module is the Goal5755 product boundary between verified Callback IR and
an eventual OptiX object graph.  It deliberately performs no native loading,
GAS construction, GPU execution, or performance selection.  Serialized data
cannot mint authority: callers must provide independently constructed target
and triangle-orientation authorities when admission is rerun.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import re
import struct
from typing import Mapping, Sequence

from .v4_callback_ir import (
    HIT,
    TRIANGLE_HIT,
    CallbackProgramSpec,
    CallbackRole,
    GeometryAdmission,
    GeometryProofAuthority,
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    TypeKind,
    VerifiedCallbackProgram,
    _verify_callback_program_with_role_contract,
    verify_callback_program,
)


PHYSICAL_SCHEMA_ID = "https://rtdl.dev/schemas/v4-typed-physical-schema-v1.json"
PHYSICAL_SCHEMA_VERSION = "v1"
BUILTIN_TRIANGLE_CONTRACT = "optix_builtin_triangle_v1"


class PhysicalSchemaError(ValueError):
    """Fail-closed typed physical-schema diagnostic."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"V4 physical schema rejected: {code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise PhysicalSchemaError(code, path, message)


class GeometryFamily(str, Enum):
    CUSTOM_AABB = "custom_aabb"
    BUILTIN_TRIANGLE = "builtin_triangle"


class BufferSemantic(str, Enum):
    CUSTOM_PRIMITIVE_DATA = "custom_primitive_data"
    VERTEX_POSITIONS = "vertex_positions"
    TRIANGLE_INDICES = "triangle_indices"
    PRIMITIVE_FRONT_VALUE = "primitive_front_value"
    PRIMITIVE_BACK_VALUE = "primitive_back_value"
    QUERY_INPUT = "query_input"
    OUTPUT_VALUE = "output_value"
    STATUS = "status"


class BufferDomain(str, Enum):
    VERTEX = "vertex"
    PRIMITIVE = "primitive"
    QUERY = "query"
    OUTPUT = "output"
    LAUNCH_PARAM = "launch_param"
    SBT_RECORD = "sbt_record"


class BufferAccess(str, Enum):
    READ_ONLY = "read_only"
    WRITE_ONLY = "write_only"
    INTERNAL_STATUS = "internal_status"


class CountRelation(str, Enum):
    VERTEX_COUNT = "vertex_count"
    PRIMITIVE_COUNT = "primitive_count"
    QUERY_COUNT = "query_count"
    OUTPUT_COUNT_EQUALS_QUERY_COUNT = "output_count_equals_query_count"
    SINGLETON = "singleton"


class PhysicalValueType(str, Enum):
    U32 = "u32"
    F32 = "f32"
    VEC2F32 = "vec2f32"
    VEC3F32 = "vec3f32"
    VEC3U32 = "vec3u32"
    OPAQUE_RECORD = "opaque_record"
    STATUS_RECORD = "status_record"


class HitChannelSemantic(str, Enum):
    CUSTOM_HIT_KIND = "custom_hit_kind"
    CUSTOM_ATTRIBUTE = "custom_attribute"
    PRIMITIVE_INDEX = "primitive_index_u32"
    TRIANGLE_FRONT_BACK_HIT_KIND = "triangle_front_back_hit_kind_u32"
    TRIANGLE_BARYCENTRICS = "triangle_barycentrics_f32x2"
    PRIMITIVE_METADATA = "primitive_metadata_lookup"


class HitChannelProducer(str, Enum):
    OPTIX_BUILTIN = "optix_builtin"
    VERIFIED_INTERSECTION_EFFECT = "verified_intersection_effect"
    COMPILER_METADATA_LOOKUP = "compiler_metadata_lookup"


class GasUpdatePolicy(str, Enum):
    STATIC = "static"
    DECLARED_REFIT = "declared_refit"


class TriangleWindingPolicy(str, Enum):
    CCW_IS_FRONT = "ccw_is_front"
    CW_IS_FRONT = "cw_is_front"


class AdjacencySide(str, Enum):
    FRONT = "front"
    BACK = "back"


class ReferenceTemplateId(str, Enum):
    CUSTOM_AABB_V1 = "custom_aabb_v1"
    BUILTIN_TRIANGLE_V1 = "builtin_triangle_v1"


@dataclass(frozen=True)
class BufferFieldSchema:
    field_id: str
    semantic: BufferSemantic
    domain: BufferDomain
    value_type: PhysicalValueType
    access: BufferAccess
    count_relation: CountRelation
    alignment_bytes: int = 4
    contiguous: bool = True
    residency: str = "device"

    def to_dict(self) -> dict[str, object]:
        return {
            "field_id": self.field_id,
            "semantic": self.semantic.value,
            "domain": self.domain.value,
            "value_type": self.value_type.value,
            "access": self.access.value,
            "count_relation": self.count_relation.value,
            "alignment_bytes": self.alignment_bytes,
            "contiguous": self.contiguous,
            "residency": self.residency,
        }


@dataclass(frozen=True)
class HitChannelSchema:
    semantic: HitChannelSemantic
    value_type: PhysicalValueType
    producer: HitChannelProducer
    readable_roles: tuple[CallbackRole, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "semantic": self.semantic.value,
            "value_type": self.value_type.value,
            "producer": self.producer.value,
            "readable_roles": [item.value for item in self.readable_roles],
        }


@dataclass(frozen=True)
class HitMetadataBinding:
    role: CallbackRole
    argument_index: int
    buffer_semantic: BufferSemantic

    def to_dict(self) -> dict[str, object]:
        return {
            "role": self.role.value,
            "argument_index": self.argument_index,
            "buffer_semantic": self.buffer_semantic.value,
        }


@dataclass(frozen=True)
class GasSchema:
    geometry_family: GeometryFamily
    build_inputs: tuple[BufferSemantic, ...]
    update_policy: GasUpdatePolicy
    graph_depth: int
    sbt_record_stride: int

    def to_dict(self) -> dict[str, object]:
        return {
            "geometry_family": self.geometry_family.value,
            "build_inputs": [item.value for item in self.build_inputs],
            "update_policy": self.update_policy.value,
            "graph_depth": self.graph_depth,
            "sbt_record_stride": self.sbt_record_stride,
        }


@dataclass(frozen=True)
class TypedPhysicalSchemaV1:
    callback_ir_sha256: str
    effect_digest: str
    geometry_family: GeometryFamily
    buffers: tuple[BufferFieldSchema, ...]
    hit_channels: tuple[HitChannelSchema, ...]
    hit_metadata_bindings: tuple[HitMetadataBinding, ...]
    gas: GasSchema
    triangle_winding: TriangleWindingPolicy | None = None
    triangle_orientation_authority_sha256: str | None = None
    schema_id: str = PHYSICAL_SCHEMA_ID
    schema_version: str = PHYSICAL_SCHEMA_VERSION

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "geometry_family": self.geometry_family.value,
            "buffers": [item.to_dict() for item in self.buffers],
            "hit_channels": [item.to_dict() for item in self.hit_channels],
            "hit_metadata_bindings": [item.to_dict() for item in self.hit_metadata_bindings],
            "gas": self.gas.to_dict(),
            "triangle_winding": None if self.triangle_winding is None else self.triangle_winding.value,
            "triangle_orientation_authority_sha256": self.triangle_orientation_authority_sha256,
        }

    @property
    def schema_sha256(self) -> str:
        return _sha(self.semantic_dict())

    def to_dict(self) -> dict[str, object]:
        result = self.semantic_dict()
        result["schema_sha256"] = self.schema_sha256
        return result


@dataclass(frozen=True)
class TriangleOrientationAuthority:
    contract_name: str
    callback_ir_sha256: str
    effect_digest: str
    vertex_positions_semantic: BufferSemantic
    triangle_indices_semantic: BufferSemantic
    front_values_semantic: BufferSemantic
    back_values_semantic: BufferSemantic
    winding_policy: TriangleWindingPolicy
    front_hit_kind: int
    back_hit_kind: int
    callback_front_hit_kind_constant: str
    callback_back_hit_kind_constant: str
    front_hit_selects: AdjacencySide
    back_hit_selects: AdjacencySide
    author_source_sha256: str
    author_semantics_sha256: str
    independent_cpu_oracle_sha256: str
    proof_kind: str = "author_source_plus_independent_cpu_oracle_v1"

    def semantic_dict(self) -> dict[str, object]:
        return {
            "contract_name": self.contract_name,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "vertex_positions_semantic": self.vertex_positions_semantic.value,
            "triangle_indices_semantic": self.triangle_indices_semantic.value,
            "front_values_semantic": self.front_values_semantic.value,
            "back_values_semantic": self.back_values_semantic.value,
            "winding_policy": self.winding_policy.value,
            "front_hit_kind": self.front_hit_kind,
            "back_hit_kind": self.back_hit_kind,
            "callback_front_hit_kind_constant": self.callback_front_hit_kind_constant,
            "callback_back_hit_kind_constant": self.callback_back_hit_kind_constant,
            "front_hit_selects": self.front_hit_selects.value,
            "back_hit_selects": self.back_hit_selects.value,
            "author_source_sha256": self.author_source_sha256,
            "author_semantics_sha256": self.author_semantics_sha256,
            "independent_cpu_oracle_sha256": self.independent_cpu_oracle_sha256,
            "proof_kind": self.proof_kind,
        }

    @property
    def authority_sha256(self) -> str:
        return _sha(self.semantic_dict())


@dataclass(frozen=True)
class ReferenceTargetProfile:
    provider: str
    optix_sdk: str
    compute_capability: str
    native_sha256: str
    supports_custom_aabb: bool
    supports_builtin_triangle: bool
    max_graph_depth: int = 1
    triangle_front_hit_kind: int = 0xFE
    triangle_back_hit_kind: int = 0xFF

    @property
    def target_sha256(self) -> str:
        return _sha({
            "provider": self.provider,
            "optix_sdk": self.optix_sdk,
            "compute_capability": self.compute_capability,
            "native_sha256": self.native_sha256,
            "supports_custom_aabb": self.supports_custom_aabb,
            "supports_builtin_triangle": self.supports_builtin_triangle,
            "max_graph_depth": self.max_graph_depth,
            "triangle_front_hit_kind": self.triangle_front_hit_kind,
            "triangle_back_hit_kind": self.triangle_back_hit_kind,
        })


@dataclass(frozen=True)
class ReferencePhysicalTemplate:
    template_id: ReferenceTemplateId
    geometry_family: GeometryFamily
    required_buffers: tuple[BufferSemantic, ...]
    required_hit_channels: tuple[HitChannelSemantic, ...]
    canonical: bool = True


@dataclass(frozen=True)
class VerifiedPhysicalSchemaAuthority:
    callback: VerifiedCallbackProgram
    schema: TypedPhysicalSchemaV1
    target: ReferenceTargetProfile
    triangle_orientation_authority: TriangleOrientationAuthority | None
    authority_nonce: str


@dataclass(frozen=True)
class CanonicalPhysicalPlan:
    template_id: ReferenceTemplateId
    schema_sha256: str
    callback_ir_sha256: str
    effect_digest: str
    target_sha256: str
    role_topology: tuple[str, ...]
    ordered_buffer_semantics: tuple[BufferSemantic, ...]
    authority_nonce: str
    executable: bool = False

    @property
    def plan_sha256(self) -> str:
        return _sha({
            "template_id": self.template_id.value,
            "schema_sha256": self.schema_sha256,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "target_sha256": self.target_sha256,
            "role_topology": list(self.role_topology),
            "ordered_buffer_semantics": [item.value for item in self.ordered_buffer_semantics],
            "authority_nonce": self.authority_nonce,
            "executable": self.executable,
        })


@dataclass(frozen=True)
class PhysicalBufferBinding:
    semantic: BufferSemantic
    element_count: int
    device_id: int
    stream_id: int
    owner_nonce: str
    mutation_epoch: int
    alignment_bytes: int
    contiguous: bool
    writable: bool
    maximum_index: int | None = None


def verify_callback_program_for_geometry(
    program: CallbackProgramSpec,
    geometry_family: GeometryFamily,
    *,
    geometry_proof_authorities: Mapping[str, GeometryProofAuthority] | None = None,
) -> VerifiedCallbackProgram:
    """Verify one Callback IR under a geometry-indexed role topology."""

    if geometry_family is GeometryFamily.CUSTOM_AABB:
        return verify_callback_program(program, geometry_proof_authorities=geometry_proof_authorities)
    if program.manifest.geometry.contract_name != BUILTIN_TRIANGLE_CONTRACT:
        _fail("triangle_contract", "manifest.geometry.contract_name", BUILTIN_TRIANGLE_CONTRACT)
    if program.manifest.attribute_types:
        _fail("triangle_attributes", "manifest.attribute_types", "built-in triangle attributes are compiler-owned")
    return _verify_callback_program_with_role_contract(
        program,
        required_roles=frozenset({
            CallbackRole.MAKE_RAY,
            CallbackRole.MISS,
            CallbackRole.FINALIZE,
        }),
        forbidden_roles=frozenset({CallbackRole.BOUNDS, CallbackRole.INTERSECTION}),
        hit_value_type=TRIANGLE_HIT,
        allow_hit_read_only_views=True,
        allowed_geometry_admissions=frozenset({GeometryAdmission.OPTIX_BUILTIN_SEMANTICS}),
        expected_schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    )


def typed_physical_schema_from_dict(payload: Mapping[str, object]) -> TypedPhysicalSchemaV1:
    """Parse an exact closed schema and rederive its digest.

    This returns inert data.  It does not return a verified authority.
    """

    _keys(payload, {
        "schema_id", "schema_version", "callback_ir_sha256", "effect_digest",
        "geometry_family", "buffers", "hit_channels", "hit_metadata_bindings",
        "gas", "triangle_winding", "triangle_orientation_authority_sha256",
        "schema_sha256",
    }, "schema")
    buffers = tuple(_buffer_from_dict(item, f"buffers[{index}]") for index, item in enumerate(_list(payload["buffers"], "buffers")))
    channels = tuple(_channel_from_dict(item, f"hit_channels[{index}]") for index, item in enumerate(_list(payload["hit_channels"], "hit_channels")))
    bindings = tuple(_metadata_binding_from_dict(item, f"hit_metadata_bindings[{index}]") for index, item in enumerate(_list(payload["hit_metadata_bindings"], "hit_metadata_bindings")))
    gas = _gas_from_dict(_mapping(payload["gas"], "gas"))
    winding_raw = payload["triangle_winding"]
    schema = TypedPhysicalSchemaV1(
        callback_ir_sha256=_digest(payload["callback_ir_sha256"], "callback_ir_sha256"),
        effect_digest=_digest(payload["effect_digest"], "effect_digest"),
        geometry_family=_enum(GeometryFamily, payload["geometry_family"], "geometry_family"),
        buffers=buffers,
        hit_channels=channels,
        hit_metadata_bindings=bindings,
        gas=gas,
        triangle_winding=None if winding_raw is None else _enum(TriangleWindingPolicy, winding_raw, "triangle_winding"),
        triangle_orientation_authority_sha256=None if payload["triangle_orientation_authority_sha256"] is None else _digest(payload["triangle_orientation_authority_sha256"], "triangle_orientation_authority_sha256"),
        schema_id=_string(payload["schema_id"], "schema_id"),
        schema_version=_string(payload["schema_version"], "schema_version"),
    )
    if schema.schema_sha256 != _digest(payload["schema_sha256"], "schema_sha256"):
        _fail("schema_digest", "schema.schema_sha256", "canonical digest mismatch")
    return schema


def verify_typed_physical_schema(
    callback: VerifiedCallbackProgram,
    schema: TypedPhysicalSchemaV1,
    *,
    target: ReferenceTargetProfile,
    orientation_authorities: Mapping[str, TriangleOrientationAuthority] | None = None,
) -> VerifiedPhysicalSchemaAuthority:
    """Rerun closed schema admission and return non-serializable authority."""

    if schema.schema_id != PHYSICAL_SCHEMA_ID or schema.schema_version != PHYSICAL_SCHEMA_VERSION:
        _fail("schema_identity", "schema", "unsupported typed physical schema")
    reverified = verify_callback_program_for_geometry(callback.program, schema.geometry_family)
    if reverified.ir_sha256 != callback.ir_sha256 or reverified.effect_digest != callback.effect_digest:
        _fail("callback_reverification", "callback", "verified callback identities changed")
    if schema.callback_ir_sha256 != callback.ir_sha256 or schema.effect_digest != callback.effect_digest:
        _fail("callback_binding", "schema", "schema must bind exact callback and effect digests")
    if target.provider != "optix" or not _is_digest(target.native_sha256):
        _fail("target_identity", "target", "exact OptiX target/native identity required")
    if schema.gas.geometry_family is not schema.geometry_family:
        _fail("gas_family", "gas.geometry_family", "GAS family mismatch")
    if schema.gas.graph_depth != 1 or schema.gas.graph_depth > target.max_graph_depth:
        _fail("gas_graph_depth", "gas.graph_depth", str(schema.gas.graph_depth))
    if schema.gas.sbt_record_stride != 1:
        _fail("sbt_record_stride", "gas.sbt_record_stride", "v1 requires one record per primitive family")

    fields = _unique_by(schema.buffers, lambda item: item.semantic, "buffers.semantic")
    _unique_by(schema.buffers, lambda item: item.field_id, "buffers.field_id")
    channels = _unique_by(schema.hit_channels, lambda item: item.semantic, "hit_channels.semantic")
    for index, field in enumerate(schema.buffers):
        _verify_buffer_field(field, f"buffers[{index}]")
    for index, channel in enumerate(schema.hit_channels):
        _verify_hit_channel(channel, f"hit_channels[{index}]")

    triangle_authority: TriangleOrientationAuthority | None = None
    if schema.geometry_family is GeometryFamily.CUSTOM_AABB:
        if not target.supports_custom_aabb:
            _fail("target_custom_aabb", "target", "custom-AABB capability absent")
        if schema.triangle_winding is not None or schema.triangle_orientation_authority_sha256 is not None:
            _fail("custom_triangle_authority", "schema", "custom AABB cannot carry triangle authority")
        if schema.hit_metadata_bindings:
            _fail("custom_metadata_binding", "hit_metadata_bindings", "v1 custom AABB has no compiler metadata lookup")
        _require(fields, BufferSemantic.CUSTOM_PRIMITIVE_DATA, "buffers")
        required_inputs = (BufferSemantic.CUSTOM_PRIMITIVE_DATA,)
        _require_channel(channels, HitChannelSemantic.CUSTOM_HIT_KIND, HitChannelProducer.VERIFIED_INTERSECTION_EFFECT)
    else:
        if not target.supports_builtin_triangle:
            _fail("target_builtin_triangle", "target", "built-in triangle capability absent")
        if schema.gas.update_policy is not GasUpdatePolicy.STATIC:
            _fail("triangle_update_policy", "gas.update_policy", "triangle v1 is static")
        required_inputs = (BufferSemantic.VERTEX_POSITIONS, BufferSemantic.TRIANGLE_INDICES)
        _verify_triangle_fields(fields)
        _require_channel(channels, HitChannelSemantic.PRIMITIVE_INDEX, HitChannelProducer.OPTIX_BUILTIN)
        _require_channel(channels, HitChannelSemantic.TRIANGLE_FRONT_BACK_HIT_KIND, HitChannelProducer.OPTIX_BUILTIN)
        _require_channel(channels, HitChannelSemantic.TRIANGLE_BARYCENTRICS, HitChannelProducer.OPTIX_BUILTIN)
        _require_channel(channels, HitChannelSemantic.PRIMITIVE_METADATA, HitChannelProducer.COMPILER_METADATA_LOOKUP)
        triangle_authority = _triangle_authority(
            schema, callback, orientation_authorities)
        if triangle_authority.front_hit_kind != target.triangle_front_hit_kind \
                or triangle_authority.back_hit_kind != target.triangle_back_hit_kind:
            _fail(
                "triangle_target_hit_kind",
                "target",
                "typed authority must match the exact target SDK front/back hit-kind values",
            )
        _verify_metadata_bindings(callback, schema, fields, triangle_authority)

    if tuple(schema.gas.build_inputs) != required_inputs:
        _fail("gas_build_inputs", "gas.build_inputs", f"expected {[item.value for item in required_inputs]}")
    nonce = _sha({
        "callback": callback.ir_sha256,
        "effect": callback.effect_digest,
        "schema": schema.schema_sha256,
        "target": target.target_sha256,
        "kind": "reference_admission_nonce_v1",
    })
    return VerifiedPhysicalSchemaAuthority(
        callback, schema, target, triangle_authority, nonce)


def lower_canonical_reference_plan(
    authority: VerifiedPhysicalSchemaAuthority,
    templates: Sequence[ReferencePhysicalTemplate],
) -> CanonicalPhysicalPlan:
    """Choose the sole canonical exact-capability template; never execute it."""

    schema = authority.schema
    buffer_semantics = frozenset(item.semantic for item in schema.buffers)
    channel_semantics = frozenset(item.semantic for item in schema.hit_channels)
    candidates = [
        item for item in templates
        if item.canonical
        and item.geometry_family is schema.geometry_family
        and frozenset(item.required_buffers) <= buffer_semantics
        and frozenset(item.required_hit_channels) <= channel_semantics
    ]
    if not candidates:
        _fail("unsupported_physical_schema", "templates", schema.geometry_family.value)
    if len(candidates) != 1:
        _fail("ambiguous_canonical_template", "templates", str(len(candidates)))
    template = candidates[0]
    roles = tuple(
        item.role.value for item in authority.callback.program.functions if item.role is not None
    )
    return CanonicalPhysicalPlan(
        template_id=template.template_id,
        schema_sha256=schema.schema_sha256,
        callback_ir_sha256=authority.callback.ir_sha256,
        effect_digest=authority.callback.effect_digest,
        target_sha256=authority.target.target_sha256,
        role_topology=roles,
        ordered_buffer_semantics=tuple(item.semantic for item in schema.buffers),
        authority_nonce=authority.authority_nonce,
        executable=False,
    )


def verify_buffer_bindings(
    schema: TypedPhysicalSchemaV1,
    bindings: Sequence[PhysicalBufferBinding],
) -> None:
    """Check reference ownership/count/epoch invariants before any future build."""

    by_semantic = _unique_by(bindings, lambda item: item.semantic, "bindings.semantic")
    if set(by_semantic) != {item.semantic for item in schema.buffers}:
        _fail("binding_membership", "bindings", "bindings must exactly cover schema fields")
    owner_nonces = {item.owner_nonce for item in bindings}
    devices = {item.device_id for item in bindings}
    streams = {item.stream_id for item in bindings}
    if len(owner_nonces) != 1 or len(devices) != 1 or len(streams) != 1:
        _fail("binding_owner_device_stream", "bindings", "one owner, device and stream required")
    counts: dict[CountRelation, int] = {}
    for field in schema.buffers:
        binding = by_semantic[field.semantic]
        if binding.element_count < 0 or binding.mutation_epoch < 0:
            _fail("binding_count_epoch", field.semantic.value, "nonnegative count/epoch required")
        if not binding.contiguous or binding.alignment_bytes < field.alignment_bytes:
            _fail("binding_layout", field.semantic.value, "contiguous aligned binding required")
        expected_writable = field.access is not BufferAccess.READ_ONLY
        if binding.writable != expected_writable:
            _fail("binding_access", field.semantic.value, "binding mutability mismatch")
        relation = field.count_relation
        if relation is CountRelation.OUTPUT_COUNT_EQUALS_QUERY_COUNT:
            continue
        if relation is CountRelation.SINGLETON and binding.element_count != 1:
            _fail("binding_singleton", field.semantic.value, str(binding.element_count))
        if relation in counts and counts[relation] != binding.element_count:
            _fail("binding_count_relation", field.semantic.value, relation.value)
        counts[relation] = binding.element_count
    query_count = counts.get(CountRelation.QUERY_COUNT)
    for field in schema.buffers:
        if field.count_relation is CountRelation.OUTPUT_COUNT_EQUALS_QUERY_COUNT:
            if query_count is None or by_semantic[field.semantic].element_count != query_count:
                _fail("binding_output_count", field.semantic.value, "output count must equal query count")
    triangle_count = counts.get(CountRelation.PRIMITIVE_COUNT)
    vertex_count = counts.get(CountRelation.VERTEX_COUNT)
    triangle_indices = by_semantic.get(BufferSemantic.TRIANGLE_INDICES)
    if triangle_indices is not None:
        if vertex_count is None or triangle_indices.maximum_index is None \
                or not (triangle_indices.maximum_index < vertex_count):
            _fail("triangle_index_range", "triangle_indices", "maximum index must be below vertex count")
        if triangle_count != triangle_indices.element_count:
            _fail("triangle_count", "triangle_indices", "primitive count mismatch")


def verify_reference_triangle_contents(
    vertices: Sequence[Sequence[float]],
    indices: Sequence[Sequence[int]],
) -> None:
    """Apply the frozen target-f32 finite/range/nondegenerate predicate."""

    # Real paper meshes contain millions of faces.  Preserve the exact same
    # target-f32 predicate while avoiding one Python object and one Python
    # callback per scalar when callers already provide contiguous NumPy
    # columns.  This is validation acceleration only; it does not weaken or
    # sample the predicate.
    try:
        import numpy as _np
    except ImportError:  # pragma: no cover - NumPy is an optional partner
        _np = None
    if _np is not None and isinstance(vertices, _np.ndarray) \
            and isinstance(indices, _np.ndarray):
        if vertices.ndim != 2 or vertices.shape[1] != 3:
            _fail("vertex_shape", "vertices", "Nx3 array required")
        if indices.ndim != 2 or indices.shape[1] != 3 \
                or indices.dtype.kind not in "iu":
            _fail("triangle_shape", "indices", "Nx3 integer array required")
        normalized = _np.ascontiguousarray(vertices, dtype=_np.float32)
        if not bool(_np.isfinite(normalized).all()):
            _fail("nonfinite", "vertices", "target-f32 coordinates must be finite")
        if len(normalized) == 0 and len(indices):
            _fail("triangle_index", "indices", "vertex domain is empty")
        if indices.dtype.kind == "i" and bool((indices < 0).any()):
            _fail("triangle_index", "indices", "negative index")
        maximum = int(indices.max(initial=0))
        if maximum >= len(normalized):
            _fail("triangle_index", "indices", "index outside vertex domain")
        normalized_indices = _np.ascontiguousarray(indices, dtype=_np.uint32)
        if bool(((normalized_indices[:, 0] == normalized_indices[:, 1])
                 | (normalized_indices[:, 0] == normalized_indices[:, 2])
                 | (normalized_indices[:, 1] == normalized_indices[:, 2])).any()):
            _fail("triangle_index", "indices", "distinct indices required")
        # Bound peak temporary memory while checking every primitive.
        for begin in range(0, len(normalized_indices), 262_144):
            chunk = normalized_indices[begin:begin + 262_144]
            a = normalized[chunk[:, 0]]
            ab = normalized[chunk[:, 1]] - a
            ac = normalized[chunk[:, 2]] - a
            cross = _np.cross(ab, ac)
            invalid = _np.flatnonzero(_np.all(cross == _np.float32(0.0), axis=1))
            if len(invalid):
                row_index = begin + int(invalid[0])
                _fail("triangle_degenerate_f32", f"indices[{row_index}]",
                      "target-f32 area is zero")
        return

    normalized: list[tuple[float, float, float]] = []
    for row_index, row in enumerate(vertices):
        if len(row) != 3:
            _fail("vertex_shape", f"vertices[{row_index}]", "vec3 required")
        value = tuple(_f32(item, f"vertices[{row_index}]") for item in row)
        normalized.append(value)
    for row_index, row in enumerate(indices):
        if len(row) != 3 or any(not isinstance(item, int) or isinstance(item, bool) for item in row):
            _fail("triangle_shape", f"indices[{row_index}]", "three integer indices required")
        if len(set(row)) != 3 or any(item < 0 or item >= len(normalized) for item in row):
            _fail("triangle_index", f"indices[{row_index}]", "distinct in-range indices required")
        a, b, c = (normalized[item] for item in row)
        ab = tuple(_f32(b[i] - a[i], "triangle.ab") for i in range(3))
        ac = tuple(_f32(c[i] - a[i], "triangle.ac") for i in range(3))
        cross = (
            _f32(ab[1] * ac[2] - ab[2] * ac[1], "triangle.cross"),
            _f32(ab[2] * ac[0] - ab[0] * ac[2], "triangle.cross"),
            _f32(ab[0] * ac[1] - ab[1] * ac[0], "triangle.cross"),
        )
        if cross == (0.0, 0.0, 0.0):
            _fail("triangle_degenerate_f32", f"indices[{row_index}]", "target-f32 area is zero")


def resolve_triangle_adjacency(
    authority: TriangleOrientationAuthority,
    *,
    hit_kind: int,
    primitive_index: int,
    front_values: Sequence[int],
    back_values: Sequence[int],
) -> tuple[int, int]:
    """Reference author semantics: return (selected_tet, neighbor_tet)."""

    if len(front_values) != len(back_values) or not 0 <= primitive_index < len(front_values):
        _fail("triangle_metadata_range", "primitive_index", str(primitive_index))
    if hit_kind == authority.front_hit_kind:
        side = authority.front_hit_selects
    elif hit_kind == authority.back_hit_kind:
        side = authority.back_hit_selects
    else:
        _fail("triangle_hit_kind", "hit_kind", str(hit_kind))
    if side is AdjacencySide.FRONT:
        return int(front_values[primitive_index]), int(back_values[primitive_index])
    return int(back_values[primitive_index]), int(front_values[primitive_index])


def triangle_author_semantics_sha256(
    *,
    front_hit_kind: int,
    back_hit_kind: int,
    front_hit_selects: AdjacencySide,
    back_hit_selects: AdjacencySide,
) -> str:
    """Canonical digest of the explicit mapping, independent of field names."""

    return _sha({
        "front_hit_kind": front_hit_kind,
        "back_hit_kind": back_hit_kind,
        "front_hit_selects": front_hit_selects.value,
        "back_hit_selects": back_hit_selects.value,
        "selected_neighbor_rule": "opposite_sides_v1",
    })


def default_reference_templates() -> tuple[ReferencePhysicalTemplate, ...]:
    return (
        ReferencePhysicalTemplate(
            ReferenceTemplateId.CUSTOM_AABB_V1,
            GeometryFamily.CUSTOM_AABB,
            (BufferSemantic.CUSTOM_PRIMITIVE_DATA,),
            (HitChannelSemantic.CUSTOM_HIT_KIND,),
        ),
        ReferencePhysicalTemplate(
            ReferenceTemplateId.BUILTIN_TRIANGLE_V1,
            GeometryFamily.BUILTIN_TRIANGLE,
            (BufferSemantic.VERTEX_POSITIONS, BufferSemantic.TRIANGLE_INDICES),
            (
                HitChannelSemantic.PRIMITIVE_INDEX,
                HitChannelSemantic.TRIANGLE_FRONT_BACK_HIT_KIND,
                HitChannelSemantic.TRIANGLE_BARYCENTRICS,
                HitChannelSemantic.PRIMITIVE_METADATA,
            ),
        ),
    )


def _triangle_authority(
    schema: TypedPhysicalSchemaV1,
    callback: VerifiedCallbackProgram,
    authorities: Mapping[str, TriangleOrientationAuthority] | None,
) -> TriangleOrientationAuthority:
    digest = schema.triangle_orientation_authority_sha256
    if schema.triangle_winding is None or digest is None or authorities is None or digest not in authorities:
        _fail("triangle_orientation_authority_missing", "schema", "external authority is required")
    authority = authorities[digest]
    if authority.authority_sha256 != digest:
        _fail("triangle_orientation_authority_digest", "authority", "authority digest mismatch")
    if authority.callback_ir_sha256 != callback.ir_sha256 \
            or authority.effect_digest != callback.effect_digest \
            or authority.winding_policy is not schema.triangle_winding:
        _fail("triangle_orientation_callback_binding", "authority", "callback/effect/winding mismatch")
    if authority.front_hit_kind == authority.back_hit_kind \
            or authority.front_hit_selects is not AdjacencySide.FRONT \
            or authority.back_hit_selects is not AdjacencySide.BACK:
        _fail("triangle_orientation_mapping", "authority", "front/back mapping is not the frozen author rule")
    expected_semantics = triangle_author_semantics_sha256(
        front_hit_kind=authority.front_hit_kind,
        back_hit_kind=authority.back_hit_kind,
        front_hit_selects=authority.front_hit_selects,
        back_hit_selects=authority.back_hit_selects,
    )
    if expected_semantics != authority.author_semantics_sha256:
        _fail("triangle_author_semantics", "authority", "explicit mapping digest mismatch")
    constants = {item.name: item.value for item in callback.program.manifest.constants}
    if constants.get(authority.callback_front_hit_kind_constant) != authority.front_hit_kind \
            or constants.get(authority.callback_back_hit_kind_constant) != authority.back_hit_kind:
        _fail(
            "triangle_callback_hit_kind_constants",
            "callback.manifest.constants",
            "Callback IR constants must match the exact target/authority hit-kind values",
        )
    for path, value in (
        ("author_source_sha256", authority.author_source_sha256),
        ("independent_cpu_oracle_sha256", authority.independent_cpu_oracle_sha256),
    ):
        if not _is_digest(value):
            _fail("triangle_evidence_digest", path, value)
    return authority


def _verify_triangle_fields(fields: Mapping[BufferSemantic, BufferFieldSchema]) -> None:
    expected = {
        BufferSemantic.VERTEX_POSITIONS: (BufferDomain.VERTEX, PhysicalValueType.VEC3F32, BufferAccess.READ_ONLY, CountRelation.VERTEX_COUNT),
        BufferSemantic.TRIANGLE_INDICES: (BufferDomain.PRIMITIVE, PhysicalValueType.VEC3U32, BufferAccess.READ_ONLY, CountRelation.PRIMITIVE_COUNT),
        BufferSemantic.PRIMITIVE_FRONT_VALUE: (BufferDomain.PRIMITIVE, PhysicalValueType.U32, BufferAccess.READ_ONLY, CountRelation.PRIMITIVE_COUNT),
        BufferSemantic.PRIMITIVE_BACK_VALUE: (BufferDomain.PRIMITIVE, PhysicalValueType.U32, BufferAccess.READ_ONLY, CountRelation.PRIMITIVE_COUNT),
    }
    for semantic, contract in expected.items():
        field = _require(fields, semantic, "buffers")
        observed = (field.domain, field.value_type, field.access, field.count_relation)
        if observed != contract:
            _fail("triangle_buffer_contract", semantic.value, repr(observed))


def _verify_metadata_bindings(
    callback: VerifiedCallbackProgram,
    schema: TypedPhysicalSchemaV1,
    fields: Mapping[BufferSemantic, BufferFieldSchema],
    authority: TriangleOrientationAuthority,
) -> None:
    if authority.vertex_positions_semantic is not BufferSemantic.VERTEX_POSITIONS \
            or authority.triangle_indices_semantic is not BufferSemantic.TRIANGLE_INDICES \
            or authority.front_values_semantic is not BufferSemantic.PRIMITIVE_FRONT_VALUE \
            or authority.back_values_semantic is not BufferSemantic.PRIMITIVE_BACK_VALUE:
        _fail("triangle_authority_semantics", "authority", "semantic IDs, not field names, must match")
    actual = {(item.role, item.argument_index): item.buffer_semantic for item in schema.hit_metadata_bindings}
    if len(actual) != len(schema.hit_metadata_bindings):
        _fail("triangle_metadata_binding_duplicate", "hit_metadata_bindings", "role/index binding must be unique")
    hit_functions = {
        item.role: item for item in callback.program.functions
        if item.role in {CallbackRole.ANY_HIT, CallbackRole.CLOSEST_HIT}
    }
    expected_keys = {
        (role, index)
        for role, function in hit_functions.items()
        for index in range(2, len(function.arguments))
    }
    if set(actual) != expected_keys:
        _fail("triangle_metadata_bindings", "hit_metadata_bindings", "every trailing hit-role view needs one exact binding")
    bound_semantics = set(actual.values())
    if not {
        BufferSemantic.PRIMITIVE_FRONT_VALUE,
        BufferSemantic.PRIMITIVE_BACK_VALUE,
    } <= bound_semantics:
        _fail("triangle_adjacency_bindings", "hit_metadata_bindings", "both explicit adjacency sides are required")
    for (role, index), semantic in actual.items():
        function = hit_functions[role]
        argument_type = function.arguments[index].value_type
        if argument_type.kind is not TypeKind.READ_ONLY_VIEW \
                or argument_type.items[0].to_dict() != {"kind": "scalar", "scalar": "u32"}:
            _fail("triangle_metadata_argument_type", "closest_hit", str(index))
        if fields[semantic].value_type is not PhysicalValueType.U32:
            _fail("triangle_metadata_buffer_type", semantic.value, "u32 required")


def _verify_buffer_field(field: BufferFieldSchema, path: str) -> None:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", field.field_id) is None:
        _fail("buffer_field_id", path, field.field_id)
    if field.alignment_bytes not in {4, 8, 16} or not field.contiguous or field.residency != "device":
        _fail("buffer_layout", path, "v1 requires contiguous device storage aligned to 4/8/16 bytes")
    if field.access is BufferAccess.READ_ONLY and field.domain is BufferDomain.OUTPUT:
        _fail("buffer_access_domain", path, "outputs cannot be read-only")


def _verify_hit_channel(channel: HitChannelSchema, path: str) -> None:
    if not channel.readable_roles or any(role not in {CallbackRole.ANY_HIT, CallbackRole.CLOSEST_HIT} for role in channel.readable_roles):
        _fail("hit_channel_roles", path, "hit channels are readable only in hit roles")
    if channel.semantic in {
        HitChannelSemantic.PRIMITIVE_INDEX,
        HitChannelSemantic.TRIANGLE_FRONT_BACK_HIT_KIND,
        HitChannelSemantic.TRIANGLE_BARYCENTRICS,
    } and channel.producer is not HitChannelProducer.OPTIX_BUILTIN:
        _fail("hit_channel_producer", path, "built-in channel requires OptiX authority")
    expected_types = {
        HitChannelSemantic.CUSTOM_HIT_KIND: PhysicalValueType.U32,
        HitChannelSemantic.CUSTOM_ATTRIBUTE: PhysicalValueType.U32,
        HitChannelSemantic.PRIMITIVE_INDEX: PhysicalValueType.U32,
        HitChannelSemantic.TRIANGLE_FRONT_BACK_HIT_KIND: PhysicalValueType.U32,
        HitChannelSemantic.TRIANGLE_BARYCENTRICS: PhysicalValueType.VEC2F32,
        HitChannelSemantic.PRIMITIVE_METADATA: PhysicalValueType.U32,
    }
    if channel.value_type is not expected_types[channel.semantic]:
        _fail("hit_channel_type", path, expected_types[channel.semantic].value)
    if channel.semantic is HitChannelSemantic.PRIMITIVE_METADATA \
            and channel.producer is not HitChannelProducer.COMPILER_METADATA_LOOKUP:
        _fail("hit_channel_producer", path, "primitive metadata requires compiler lookup authority")


def _require_channel(
    channels: Mapping[HitChannelSemantic, HitChannelSchema],
    semantic: HitChannelSemantic,
    producer: HitChannelProducer,
) -> HitChannelSchema:
    channel = _require(channels, semantic, "hit_channels")
    if channel.producer is not producer:
        _fail("hit_channel_producer", semantic.value, producer.value)
    return channel


def _buffer_from_dict(payload: object, path: str) -> BufferFieldSchema:
    data = _mapping(payload, path)
    _keys(data, {"field_id", "semantic", "domain", "value_type", "access", "count_relation", "alignment_bytes", "contiguous", "residency"}, path)
    return BufferFieldSchema(
        _string(data["field_id"], f"{path}.field_id"),
        _enum(BufferSemantic, data["semantic"], f"{path}.semantic"),
        _enum(BufferDomain, data["domain"], f"{path}.domain"),
        _enum(PhysicalValueType, data["value_type"], f"{path}.value_type"),
        _enum(BufferAccess, data["access"], f"{path}.access"),
        _enum(CountRelation, data["count_relation"], f"{path}.count_relation"),
        _integer(data["alignment_bytes"], f"{path}.alignment_bytes"),
        _boolean(data["contiguous"], f"{path}.contiguous"),
        _string(data["residency"], f"{path}.residency"),
    )


def _channel_from_dict(payload: object, path: str) -> HitChannelSchema:
    data = _mapping(payload, path)
    _keys(data, {"semantic", "value_type", "producer", "readable_roles"}, path)
    return HitChannelSchema(
        _enum(HitChannelSemantic, data["semantic"], f"{path}.semantic"),
        _enum(PhysicalValueType, data["value_type"], f"{path}.value_type"),
        _enum(HitChannelProducer, data["producer"], f"{path}.producer"),
        tuple(_enum(CallbackRole, item, f"{path}.readable_roles") for item in _list(data["readable_roles"], f"{path}.readable_roles")),
    )


def _metadata_binding_from_dict(payload: object, path: str) -> HitMetadataBinding:
    data = _mapping(payload, path)
    _keys(data, {"role", "argument_index", "buffer_semantic"}, path)
    return HitMetadataBinding(
        _enum(CallbackRole, data["role"], f"{path}.role"),
        _integer(data["argument_index"], f"{path}.argument_index"),
        _enum(BufferSemantic, data["buffer_semantic"], f"{path}.buffer_semantic"),
    )


def _gas_from_dict(data: Mapping[str, object]) -> GasSchema:
    _keys(data, {"geometry_family", "build_inputs", "update_policy", "graph_depth", "sbt_record_stride"}, "gas")
    return GasSchema(
        _enum(GeometryFamily, data["geometry_family"], "gas.geometry_family"),
        tuple(_enum(BufferSemantic, item, "gas.build_inputs") for item in _list(data["build_inputs"], "gas.build_inputs")),
        _enum(GasUpdatePolicy, data["update_policy"], "gas.update_policy"),
        _integer(data["graph_depth"], "gas.graph_depth"),
        _integer(data["sbt_record_stride"], "gas.sbt_record_stride"),
    )


def _sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def _f32(value: object, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        _fail("nonfinite_f32", path, repr(value))
    result = struct.unpack("<f", struct.pack("<f", float(value)))[0]
    if not math.isfinite(result):
        _fail("nonfinite_f32", path, repr(value))
    return result


def _keys(payload: Mapping[str, object], expected: set[str], path: str) -> None:
    if set(payload) != expected:
        _fail("closed_shape", path, f"expected {sorted(expected)}, got {sorted(payload)}")


def _mapping(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        _fail("mapping", path, "object required")
    return value


def _list(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        _fail("list", path, "array required")
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str):
        _fail("string", path, "string required")
    return value


def _integer(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        _fail("integer", path, "integer required")
    return value


def _boolean(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        _fail("boolean", path, "boolean required")
    return value


def _enum(enum_type, value: object, path: str):
    try:
        return enum_type(_string(value, path))
    except ValueError as exc:
        _fail("enum", path, str(value))
        raise AssertionError from exc


def _digest(value: object, path: str) -> str:
    result = _string(value, path)
    if not _is_digest(result):
        _fail("sha256", path, result)
    return result


def _is_digest(value: str) -> bool:
    return re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _unique_by(items: Sequence[object], key, path: str):
    result = {}
    for item in items:
        identity = key(item)
        if identity in result:
            _fail("duplicate", path, str(identity))
        result[identity] = item
    return result


def _require(mapping: Mapping[object, object], key: object, path: str):
    if key not in mapping:
        _fail("required_semantic", path, getattr(key, "value", str(key)))
    return mapping[key]
