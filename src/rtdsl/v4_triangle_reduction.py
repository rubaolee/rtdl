"""Generic built-in-triangle metadata and checked reduction contracts.

This module is the Goal5758/M1 successor to the orientation-specific
``TypedPhysicalSchemaV1``.  It does not weaken that schema.  Instead it admits
one closed family of read-only metadata channels and three exact integer
reducers.  The compiler never accepts a reducer callback or an application
identity.

The module deliberately contains an executable CPU reference for the reducer
algebras and a deterministic, non-executable target contract.  A target backend
must separately prove that it implements the contract before GPU execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Iterable, Mapping, Sequence

from .v4_callback_ir import (
    TRIANGLE_HIT,
    CallbackRole,
    ScalarKind,
    TypeKind,
    VerifiedCallbackProgram,
)
from .v4_typed_physical_schema import (
    BUILTIN_TRIANGLE_CONTRACT,
    GeometryFamily,
    ReferenceTargetProfile,
    verify_callback_program_for_geometry,
)


TRIANGLE_REDUCTION_SCHEMA_ID = (
    "https://rtdl.dev/schemas/v4-triangle-metadata-reduction-v1.json"
)
TRIANGLE_REDUCTION_SCHEMA_VERSION = "v1"
TRIANGLE_REDUCTION_TEMPLATE = "builtin_triangle_checked_reduction_v1"
_IDENTIFIER = re.compile(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*")
_U32_MAX = (1 << 32) - 1
_U64_MAX = (1 << 64) - 1
_I64_MIN = -(1 << 63)
_I64_MAX = (1 << 63) - 1


class TriangleReductionError(ValueError):
    """Stable fail-closed diagnostic for admission and reference execution."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"V4 triangle reduction rejected: {code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise TriangleReductionError(code, path, message)


class MetadataDomain(str, Enum):
    PRIMITIVE = "primitive"
    QUERY = "query"


class ReducerAlgebra(str, Enum):
    CHECKED_KEYED_I64_SUM = "checked_keyed_i64_sum"
    CHECKED_U64_SUM = "checked_u64_sum"
    CHECKED_U64_PRODUCT_SUM = "checked_u64_product_sum"


class ReducerSourceKind(str, Enum):
    LAUNCH_INDEX = "launch_index"
    PRIMITIVE_INDEX = "primitive_index"
    METADATA = "metadata"
    PER_RAY_OUTPUT = "per_ray_output"


class DuplicatePolicy(str, Enum):
    REJECT = "reject"
    KEYED_IDENTICAL_DEDUP = "keyed_identical_dedup"


@dataclass(frozen=True)
class TriangleMetadataChannel:
    semantic_id: str
    field_id: str
    scalar: ScalarKind
    domain: MetadataDomain
    exposed_to_callback: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "semantic_id": self.semantic_id,
            "field_id": self.field_id,
            "scalar": self.scalar.value,
            "domain": self.domain.value,
            "exposed_to_callback": self.exposed_to_callback,
            "access": "read_only",
            "residency": "device",
            "count_relation": (
                "primitive_count" if self.domain is MetadataDomain.PRIMITIVE
                else "query_count"
            ),
        }


@dataclass(frozen=True)
class TriangleMetadataBinding:
    role: CallbackRole
    argument_index: int
    semantic_id: str

    def to_dict(self) -> dict[str, object]:
        return {
            "role": self.role.value,
            "argument_index": self.argument_index,
            "semantic_id": self.semantic_id,
        }


@dataclass(frozen=True)
class ReducerSource:
    kind: ReducerSourceKind
    semantic_id: str | None = None
    output_field: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind.value,
            "semantic_id": self.semantic_id,
            "output_field": self.output_field,
        }


@dataclass(frozen=True)
class CheckedReducerSpec:
    algebra: ReducerAlgebra
    key_sources: tuple[ReducerSource, ...]
    value_source: ReducerSource
    multiplicand_source: ReducerSource | None = None
    include_source: ReducerSource | None = None
    event_identity_sources: tuple[ReducerSource, ...] = ()
    duplicate_policy: DuplicatePolicy = DuplicatePolicy.REJECT
    output_capacity: int = 1

    def semantic_dict(self) -> dict[str, object]:
        return {
            "algebra": self.algebra.value,
            "key_sources": [item.to_dict() for item in self.key_sources],
            "value_source": self.value_source.to_dict(),
            "multiplicand_source": (
                None if self.multiplicand_source is None
                else self.multiplicand_source.to_dict()
            ),
            "include_source": (
                None if self.include_source is None else self.include_source.to_dict()
            ),
            "event_identity_sources": [
                item.to_dict() for item in self.event_identity_sources
            ],
            "duplicate_policy": self.duplicate_policy.value,
            "output_capacity": self.output_capacity,
            "overflow_policy": "fail_closed",
            "ordering": "lexicographic_unsigned_keys",
        }

    @property
    def reducer_sha256(self) -> str:
        return _sha(self.semantic_dict())


@dataclass(frozen=True)
class TriangleReductionSchema:
    callback_ir_sha256: str
    effect_digest: str
    metadata_channels: tuple[TriangleMetadataChannel, ...]
    metadata_bindings: tuple[TriangleMetadataBinding, ...]
    reducer: CheckedReducerSpec
    schema_id: str = TRIANGLE_REDUCTION_SCHEMA_ID
    schema_version: str = TRIANGLE_REDUCTION_SCHEMA_VERSION

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "geometry_family": GeometryFamily.BUILTIN_TRIANGLE.value,
            "metadata_channels": [item.to_dict() for item in self.metadata_channels],
            "metadata_bindings": [item.to_dict() for item in self.metadata_bindings],
            "reducer": self.reducer.semantic_dict(),
            "particle_orientation_contract_modified": False,
        }

    @property
    def schema_sha256(self) -> str:
        return _sha(self.semantic_dict())

    def to_dict(self) -> dict[str, object]:
        return {**self.semantic_dict(), "schema_sha256": self.schema_sha256}


@dataclass(frozen=True)
class VerifiedTriangleReductionAuthority:
    callback: VerifiedCallbackProgram
    schema: TriangleReductionSchema
    target: ReferenceTargetProfile
    authority_nonce: str


@dataclass(frozen=True)
class CompiledTriangleReductionContract:
    callback_ir_sha256: str
    effect_digest: str
    schema_sha256: str
    target_sha256: str
    abi_sha256: str
    template_id: str
    metadata_channels: tuple[dict[str, object], ...]
    reducer: dict[str, object]
    role_topology: tuple[str, ...]
    authority_nonce: str
    executable: bool = False

    def semantic_dict(self) -> dict[str, object]:
        return {
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "schema_sha256": self.schema_sha256,
            "target_sha256": self.target_sha256,
            "abi_sha256": self.abi_sha256,
            "template_id": self.template_id,
            "metadata_channels": list(self.metadata_channels),
            "reducer": self.reducer,
            "role_topology": list(self.role_topology),
            "authority_nonce": self.authority_nonce,
            "executable": self.executable,
            "target_execution_receipt_required": True,
        }

    @property
    def contract_sha256(self) -> str:
        return _sha(self.semantic_dict())

    def to_dict(self) -> dict[str, object]:
        return {**self.semantic_dict(), "contract_sha256": self.contract_sha256}


def verify_triangle_reduction_schema(
    callback: VerifiedCallbackProgram,
    schema: TriangleReductionSchema,
    *,
    target: ReferenceTargetProfile,
) -> VerifiedTriangleReductionAuthority:
    """Reverify one live callback/schema/target tuple and mint local authority."""

    if not isinstance(callback, VerifiedCallbackProgram):
        _fail("verified_callback_required", "callback", type(callback).__name__)
    if schema.schema_id != TRIANGLE_REDUCTION_SCHEMA_ID \
            or schema.schema_version != TRIANGLE_REDUCTION_SCHEMA_VERSION:
        _fail("schema_identity", "schema", "unsupported successor schema")
    fresh = verify_callback_program_for_geometry(
        callback.program, GeometryFamily.BUILTIN_TRIANGLE)
    if fresh != callback:
        _fail("callback_reverification", "callback", "verified identity changed")
    if schema.callback_ir_sha256 != callback.ir_sha256 \
            or schema.effect_digest != callback.effect_digest:
        _fail("callback_binding", "schema", "schema does not bind exact callback")
    if callback.program.manifest.geometry.contract_name != BUILTIN_TRIANGLE_CONTRACT:
        _fail("geometry_contract", "callback.manifest", BUILTIN_TRIANGLE_CONTRACT)
    if target.provider != "optix" or not target.supports_builtin_triangle \
            or not re.fullmatch(r"[0-9a-f]{64}", target.native_sha256):
        _fail("target_identity", "target", "exact built-in-triangle OptiX target required")

    channels: dict[str, TriangleMetadataChannel] = {}
    field_ids: set[str] = set()
    for index, channel in enumerate(schema.metadata_channels):
        path = f"metadata_channels[{index}]"
        _semantic_id(channel.semantic_id, path + ".semantic_id")
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", channel.field_id) is None:
            _fail("field_id", path + ".field_id", channel.field_id)
        if channel.semantic_id in channels or channel.field_id in field_ids:
            _fail("metadata_duplicate", path, channel.semantic_id)
        if channel.scalar not in {ScalarKind.U32, ScalarKind.U64, ScalarKind.I64}:
            _fail("metadata_scalar", path, channel.scalar.value)
        channels[channel.semantic_id] = channel
        field_ids.add(channel.field_id)

    bindings: dict[tuple[CallbackRole, int], str] = {}
    for index, binding in enumerate(schema.metadata_bindings):
        path = f"metadata_bindings[{index}]"
        key = (binding.role, binding.argument_index)
        if key in bindings:
            _fail("metadata_binding_duplicate", path, repr(key))
        channel = channels.get(binding.semantic_id)
        if channel is None or not channel.exposed_to_callback:
            _fail("metadata_binding_channel", path, binding.semantic_id)
        function = callback.program.function_for_role(binding.role)
        if binding.role not in {CallbackRole.ANY_HIT, CallbackRole.CLOSEST_HIT} \
                or binding.argument_index < 2 \
                or binding.argument_index >= len(function.arguments):
            _fail("metadata_binding_role_index", path, repr(key))
        argument_type = function.arguments[binding.argument_index].value_type
        if argument_type.kind is not TypeKind.READ_ONLY_VIEW \
                or argument_type.items[0].kind is not TypeKind.SCALAR \
                or argument_type.items[0].scalar is not channel.scalar:
            _fail("metadata_binding_type", path, channel.scalar.value)
        bindings[key] = binding.semantic_id
    exposed = {item.semantic_id for item in channels.values() if item.exposed_to_callback}
    if set(bindings.values()) != exposed:
        _fail("metadata_binding_coverage", "metadata_bindings", repr(sorted(exposed)))

    hit_roles = [
        item for item in callback.program.functions
        if item.role in {CallbackRole.ANY_HIT, CallbackRole.CLOSEST_HIT}
    ]
    if not hit_roles:
        _fail("hit_role_required", "callback", "triangle reduction needs a hit role")
    for function in hit_roles:
        if not function.arguments or function.arguments[0].value_type != TRIANGLE_HIT:
            _fail("triangle_hit_required", function.name, "first argument must be TriangleHit")

    _verify_reducer(schema.reducer, channels, callback)
    nonce = _sha({
        "kind": "verified_triangle_reduction_authority_v1",
        "callback": callback.ir_sha256,
        "effect": callback.effect_digest,
        "schema": schema.schema_sha256,
        "target": target.target_sha256,
    })
    return VerifiedTriangleReductionAuthority(callback, schema, target, nonce)


def compile_triangle_reduction_contract(
    authority: VerifiedTriangleReductionAuthority,
    *,
    abi_sha256: str,
) -> CompiledTriangleReductionContract:
    """Emit the sole canonical target contract; this does not mint execution."""

    fresh = verify_triangle_reduction_schema(
        authority.callback, authority.schema, target=authority.target)
    if fresh != authority:
        _fail("authority_reverification", "authority", "live authority did not rederive")
    if re.fullmatch(r"[0-9a-f]{64}", abi_sha256) is None:
        _fail("abi_identity", "abi_sha256", abi_sha256)
    return CompiledTriangleReductionContract(
        callback_ir_sha256=authority.callback.ir_sha256,
        effect_digest=authority.callback.effect_digest,
        schema_sha256=authority.schema.schema_sha256,
        target_sha256=authority.target.target_sha256,
        abi_sha256=abi_sha256,
        template_id=TRIANGLE_REDUCTION_TEMPLATE,
        metadata_channels=tuple(
            item.to_dict() for item in authority.schema.metadata_channels),
        reducer=authority.schema.reducer.semantic_dict(),
        role_topology=tuple(
            item.role.value for item in authority.callback.program.functions
            if item.role is not None),
        authority_nonce=authority.authority_nonce,
        executable=False,
    )


def compile_triangle_reduction_abi(
    authority: VerifiedTriangleReductionAuthority,
    *,
    any_hit_proof_authority,
):
    """Compile the frozen V1 ABI shape through the live successor authority.

    ``v4_callback_abi.py`` is a Goal5757-frozen product input and cannot be
    edited by this successor.  This narrow bridge reuses its closed ABI data
    types and layout helpers after independently rederiving the M1 authority.
    It never accepts source text or a Python callable.
    """

    from . import v4_callback_abi as abi

    fresh = verify_triangle_reduction_schema(
        authority.callback, authority.schema, target=authority.target)
    if fresh != authority:
        _fail("authority_reverification", "authority", "live authority did not rederive")
    verified = fresh.callback
    role_functions = {
        item.role: item for item in verified.program.functions if item.role is not None
    }
    proof_sha = None
    if CallbackRole.ANY_HIT in role_functions:
        proof_sha = abi._verify_any_hit_authority(verified, any_hit_proof_authority)
    elif any_hit_proof_authority is not None:
        _fail("unused_any_hit_proof", "any_hit_proof", "program has no any-hit role")

    records = {item.name: item for item in verified.program.records}
    roles = []
    for role in CallbackRole:
        function = role_functions.get(role)
        if function is None:
            continue
        inputs = [
            abi.AbiField("in.context.launch_index", "u64", "in", "launch_index", True)
        ]
        for argument in function.arguments:
            inputs.extend(abi._flatten_type(
                argument.value_type, f"in.{argument.name}", direction="in",
                records=records, seen=set()))
        variants = abi._effect_variants(function, records)
        nonce = int(hashlib.sha256(
            f"{verified.ir_sha256}:{verified.effect_digest}:{role.value}".encode("ascii")
        ).hexdigest()[:8], 16)
        roles.append(abi.RoleAbi(
            role=role, role_tag=abi._ROLE_TAGS[role],
            stage_tag=abi._STAGE_TAGS[abi.ROLE_STAGE[role]],
            symbol=f"rtdl_v4_{role.value}_{verified.ir_sha256[:16]}",
            inputs=tuple(inputs), status=abi._STATUS_FIELDS, effects=variants,
            first_error_policy=abi._FIRST_ERROR_POLICY, nonce_word=nonce))
    base = abi.CompiledCallbackAbi(
        schema_id=abi.CALLBACK_ABI_SCHEMA_ID,
        schema_version=abi.CALLBACK_ABI_SCHEMA_VERSION,
        callback_ir_sha256=verified.ir_sha256,
        callback_effect_digest=verified.effect_digest,
        any_hit_proof_sha256=proof_sha,
        any_hit_proof_kind=(
            None if any_hit_proof_authority is None
            else any_hit_proof_authority.proof_kind),
        any_hit_delivery_contract=(
            None if any_hit_proof_authority is None
            else any_hit_proof_authority.delivery_contract.value),
        runtime_status_codes=abi._RUNTIME_STATUS_CODES,
        roles=tuple(roles), abi_sha256="")
    digest = hashlib.sha256(json.dumps(
        base.payload_without_digest(), sort_keys=True, separators=(",", ":"),
        ensure_ascii=False).encode("utf-8")).hexdigest()
    return abi.CompiledCallbackAbi(**{**base.__dict__, "abi_sha256": digest})


def execute_checked_reducer(
    reducer: CheckedReducerSpec,
    rows: Iterable[Mapping[str, int]],
) -> int | tuple[tuple[tuple[int, ...], int], ...]:
    """Independent exact reference semantics for the three closed algebras."""

    materialized = tuple(dict(row) for row in rows)
    if reducer.algebra is ReducerAlgebra.CHECKED_KEYED_I64_SUM:
        seen: dict[tuple[int, ...], tuple[tuple[int, ...], int, int]] = {}
        grouped: dict[tuple[int, ...], int] = {}
        for index, row in enumerate(materialized):
            path = f"rows[{index}]"
            include = 1
            if reducer.include_source is not None:
                include = _read_source(reducer.include_source, row, path)
                _unsigned(include, _U32_MAX, path + ".include")
                if include not in {0, 1}:
                    _fail("include_flag", path, str(include))
            key = tuple(_read_source(item, row, path) for item in reducer.key_sources)
            for part in key:
                _unsigned(part, _U32_MAX, path + ".key")
            value = _read_source(reducer.value_source, row, path)
            _signed_i64(value, path + ".value")
            identity = tuple(
                _read_source(item, row, path) for item in reducer.event_identity_sources)
            fingerprint = (key, value, include)
            previous = seen.get(identity)
            if previous is not None:
                if reducer.duplicate_policy is DuplicatePolicy.REJECT:
                    _fail("duplicate_event_identity", path, repr(identity))
                if previous != fingerprint:
                    _fail("conflicting_duplicate_event", path, repr(identity))
                continue
            seen[identity] = fingerprint
            if include == 0:
                continue
            total = grouped.get(key, 0) + value
            _signed_i64(total, path + ".sum")
            grouped[key] = total
        if len(grouped) > reducer.output_capacity:
            _fail("output_capacity", "rows", str(len(grouped)))
        return tuple((key, grouped[key]) for key in sorted(grouped) if grouped[key] != 0)

    total = 0
    for index, row in enumerate(materialized):
        path = f"rows[{index}]"
        value = _read_source(reducer.value_source, row, path)
        _unsigned(value, _U64_MAX, path + ".value")
        if reducer.algebra is ReducerAlgebra.CHECKED_U64_PRODUCT_SUM:
            assert reducer.multiplicand_source is not None
            multiplier = _read_source(reducer.multiplicand_source, row, path)
            _unsigned(multiplier, _U64_MAX, path + ".multiplicand")
            value *= multiplier
            _unsigned(value, _U64_MAX, path + ".product")
        total += value
        _unsigned(total, _U64_MAX, path + ".sum")
    return total


def _verify_reducer(
    reducer: CheckedReducerSpec,
    channels: Mapping[str, TriangleMetadataChannel],
    callback: VerifiedCallbackProgram,
) -> None:
    if not isinstance(reducer.output_capacity, int) or isinstance(reducer.output_capacity, bool) \
            or reducer.output_capacity <= 0:
        _fail("output_capacity", "reducer.output_capacity", str(reducer.output_capacity))
    sources = tuple(reducer.key_sources) + (reducer.value_source,) \
        + (() if reducer.multiplicand_source is None else (reducer.multiplicand_source,)) \
        + (() if reducer.include_source is None else (reducer.include_source,)) \
        + tuple(reducer.event_identity_sources)
    for index, source in enumerate(sources):
        _source_scalar(source, channels, callback, f"reducer.sources[{index}]")

    if reducer.algebra is ReducerAlgebra.CHECKED_KEYED_I64_SUM:
        if not reducer.key_sources or len(reducer.event_identity_sources) < 2:
            _fail("keyed_reducer_shape", "reducer", "keys and two-part event identity required")
        if reducer.multiplicand_source is not None:
            _fail("keyed_reducer_multiplicand", "reducer", "not permitted")
        if any(_source_scalar(item, channels, callback, "reducer.key") is not ScalarKind.U32
               for item in reducer.key_sources):
            _fail("key_scalar", "reducer.key_sources", "u32 required")
        if _source_scalar(reducer.value_source, channels, callback, "reducer.value") \
                is not ScalarKind.I64:
            _fail("value_scalar", "reducer.value_source", "i64 required")
        if reducer.include_source is not None \
                and _source_scalar(reducer.include_source, channels, callback, "reducer.include") \
                is not ScalarKind.U32:
            _fail("include_scalar", "reducer.include_source", "u32 required")
        for source in reducer.event_identity_sources:
            if _source_scalar(source, channels, callback, "reducer.event_identity") \
                    not in {ScalarKind.U32, ScalarKind.U64}:
                _fail("event_identity_scalar", "reducer.event_identity_sources", "u32/u64 required")
        return

    if reducer.key_sources or reducer.include_source is not None \
            or reducer.event_identity_sources:
        _fail("u64_reducer_shape", "reducer", "scalar U64 reducers have no keys/events/include")
    if reducer.duplicate_policy is not DuplicatePolicy.REJECT:
        _fail("u64_duplicate_policy", "reducer.duplicate_policy", "must be reject")
    if reducer.output_capacity != 1:
        _fail("u64_output_capacity", "reducer.output_capacity", "scalar output capacity must be one")
    if _source_scalar(reducer.value_source, channels, callback, "reducer.value") \
            is not ScalarKind.U64:
        _fail("value_scalar", "reducer.value_source", "u64 required")
    if reducer.algebra is ReducerAlgebra.CHECKED_U64_SUM:
        if reducer.multiplicand_source is not None:
            _fail("u64_sum_multiplicand", "reducer", "not permitted")
    elif reducer.algebra is ReducerAlgebra.CHECKED_U64_PRODUCT_SUM:
        if reducer.multiplicand_source is None \
                or _source_scalar(reducer.multiplicand_source, channels, callback,
                                  "reducer.multiplicand") is not ScalarKind.U64:
            _fail("u64_product_multiplicand", "reducer", "u64 required")
    else:
        _fail("reducer_algebra", "reducer.algebra", reducer.algebra.value)


def _source_scalar(
    source: ReducerSource,
    channels: Mapping[str, TriangleMetadataChannel],
    callback: VerifiedCallbackProgram,
    path: str,
) -> ScalarKind:
    if source.kind in {ReducerSourceKind.LAUNCH_INDEX, ReducerSourceKind.PRIMITIVE_INDEX}:
        if source.semantic_id is not None or source.output_field is not None:
            _fail("intrinsic_source_shape", path, repr(source))
        return ScalarKind.U32
    if source.kind is ReducerSourceKind.METADATA:
        if source.semantic_id is None or source.output_field is not None:
            _fail("metadata_source_shape", path, repr(source))
        channel = channels.get(source.semantic_id)
        if channel is None:
            _fail("metadata_source_missing", path, str(source.semantic_id))
        return channel.scalar
    if source.kind is ReducerSourceKind.PER_RAY_OUTPUT:
        if source.semantic_id is not None or source.output_field is None:
            _fail("output_source_shape", path, repr(source))
        record = next(
            (item for item in callback.program.records
             if item.name == callback.program.manifest.output_record), None)
        if record is None:
            _fail("output_record_missing", path, callback.program.manifest.output_record)
        field = next((item for item in record.fields if item.name == source.output_field), None)
        if field is None or field.value_type.kind is not TypeKind.SCALAR \
                or field.value_type.scalar is None:
            _fail("output_field_scalar", path, str(source.output_field))
        return field.value_type.scalar
    _fail("source_kind", path, source.kind.value)
    raise AssertionError


def _read_source(source: ReducerSource, row: Mapping[str, int], path: str) -> int:
    if source.kind is ReducerSourceKind.LAUNCH_INDEX:
        key = "launch_index"
    elif source.kind is ReducerSourceKind.PRIMITIVE_INDEX:
        key = "primitive_index"
    elif source.kind is ReducerSourceKind.METADATA:
        key = str(source.semantic_id)
    else:
        key = str(source.output_field)
    if key not in row:
        _fail("row_source_missing", path, key)
    value = row[key]
    if not isinstance(value, int) or isinstance(value, bool):
        _fail("row_source_type", path + "." + key, type(value).__name__)
    return value


def _semantic_id(value: str, path: str) -> None:
    if _IDENTIFIER.fullmatch(value) is None:
        _fail("semantic_id", path, value)


def _unsigned(value: int, maximum: int, path: str) -> None:
    if value < 0 or value > maximum:
        _fail("unsigned_overflow", path, str(value))


def _signed_i64(value: int, path: str) -> None:
    if value < _I64_MIN or value > _I64_MAX:
        _fail("signed_i64_overflow", path, str(value))


def _sha(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


__all__ = [
    "TRIANGLE_REDUCTION_SCHEMA_ID",
    "TRIANGLE_REDUCTION_SCHEMA_VERSION",
    "TRIANGLE_REDUCTION_TEMPLATE",
    "CheckedReducerSpec",
    "CompiledTriangleReductionContract",
    "DuplicatePolicy",
    "MetadataDomain",
    "ReducerAlgebra",
    "ReducerSource",
    "ReducerSourceKind",
    "TriangleMetadataBinding",
    "TriangleMetadataChannel",
    "TriangleReductionError",
    "TriangleReductionSchema",
    "VerifiedTriangleReductionAuthority",
    "compile_triangle_reduction_contract",
    "compile_triangle_reduction_abi",
    "execute_checked_reducer",
    "verify_triangle_reduction_schema",
]
