"""Production, backend-neutral V4 callback IR and fail-closed verifier.

The IR is deliberately independent of Python, Numba and OptiX source syntax.
The restricted-Python frontend is only one producer.  Backends may consume a
program only after :func:`verify_callback_program` succeeds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math
import re
from typing import Mapping, Sequence, TypeAlias


CALLBACK_IR_SCHEMA_ID = "https://rtdl.dev/schemas/v4-callback-ir-v1.json"
CALLBACK_IR_SCHEMA_VERSION = "v1"
CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION = "v2"
MAX_STATIC_LOOP_TRIP_COUNT = 1024
MAX_HELPER_CALL_DEPTH = 8


class CallbackRole(str, Enum):
    BOUNDS = "bounds"
    MAKE_RAY = "make_ray"
    INTERSECTION = "intersection"
    ANY_HIT = "any_hit"
    CLOSEST_HIT = "closest_hit"
    MISS = "miss"
    FINALIZE = "finalize"


class CallbackStage(str, Enum):
    PREPARATION = "preparation"
    LANGUAGE_LEAF = "language_leaf"
    OPTIX_ENTRY = "optix_entry"


ROLE_STAGE: Mapping[CallbackRole, CallbackStage] = {
    CallbackRole.BOUNDS: CallbackStage.PREPARATION,
    CallbackRole.MAKE_RAY: CallbackStage.LANGUAGE_LEAF,
    CallbackRole.INTERSECTION: CallbackStage.OPTIX_ENTRY,
    CallbackRole.ANY_HIT: CallbackStage.OPTIX_ENTRY,
    CallbackRole.CLOSEST_HIT: CallbackStage.OPTIX_ENTRY,
    CallbackRole.MISS: CallbackStage.OPTIX_ENTRY,
    CallbackRole.FINALIZE: CallbackStage.LANGUAGE_LEAF,
}


class ScalarKind(str, Enum):
    BOOL = "bool"
    I32 = "i32"
    U32 = "u32"
    I64 = "i64"
    U64 = "u64"
    F32 = "f32"
    F64 = "f64"


class TypeKind(str, Enum):
    SCALAR = "scalar"
    VECTOR = "vector"
    TUPLE = "tuple"
    RECORD = "record"
    READ_ONLY_VIEW = "read_only_view"
    BUILTIN = "builtin"


class RecordPurpose(str, Enum):
    PAYLOAD = "payload"
    DATA = "data"
    OUTPUT = "output"


class GeometryAdmission(str, Enum):
    VERIFIED_CONTRACT = "verified_contract"
    TESTED_USER_GEOMETRY = "tested_user_geometry"
    OPTIX_BUILTIN_SEMANTICS = "optix_builtin_semantics"


class AnyHitDeliveryContract(str, Enum):
    ORDER_INDEPENDENT_CANONICAL = "order_independent_canonical"
    IDEMPOTENT_MONOTONE = "idempotent_monotone"
    ABSORBING_TERMINATION = "absorbing_termination"


class LinkageMechanism(str, Enum):
    TRUSTED_SINGLE_MODULE_COMPOSITION_V1 = "trusted_single_module_composition_v1"
    TWO_MODULE_ORDINARY_DIAGNOSTIC = "two_module_ordinary_diagnostic"


class EffectKind(str, Enum):
    AABB = "aabb"
    TRACE_REQUEST = "trace_request"
    HIT = "hit"
    NO_HIT = "no_hit"
    ACCEPT_CONTINUE = "accept_continue"
    IGNORE = "ignore"
    TERMINATE = "terminate"
    PAYLOAD = "payload"
    OUTPUT = "output"


class RuntimeStatus(str, Enum):
    OK = "ok"
    ABI_MISMATCH = "abi_mismatch"
    NONFINITE_INPUT = "nonfinite_input"
    NONFINITE_RESULT = "nonfinite_result"
    INTEGER_OVERFLOW = "integer_overflow"
    DIVIDE_BY_ZERO = "divide_by_zero"
    INVALID_SQRT = "invalid_sqrt"
    VIEW_OUT_OF_BOUNDS = "view_out_of_bounds"
    RESOURCE_BOUND_EXCEEDED = "resource_bound_exceeded"
    INVALID_TRACE_REQUEST = "invalid_trace_request"
    INVALID_AABB = "invalid_aabb"
    INVALID_EFFECT = "invalid_effect"


class CallbackVerificationError(ValueError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"V4 Callback IR verification failed: {code}@{path}: {message}")


@dataclass(frozen=True)
class CallbackType:
    kind: TypeKind
    scalar: ScalarKind | None = None
    lanes: int = 1
    name: str | None = None
    items: tuple["CallbackType", ...] = ()

    def __post_init__(self) -> None:
        if self.kind is TypeKind.SCALAR:
            if self.scalar is None or self.lanes != 1 or self.name is not None or self.items:
                raise ValueError("scalar type shape is invalid")
        elif self.kind is TypeKind.VECTOR:
            if self.scalar is None or self.lanes not in {2, 3, 4} or self.name is not None or self.items:
                raise ValueError("vector type shape is invalid")
        elif self.kind is TypeKind.TUPLE:
            if not self.items or self.scalar is not None or self.name is not None:
                raise ValueError("tuple type shape is invalid")
        elif self.kind in {TypeKind.RECORD, TypeKind.BUILTIN}:
            if (
                not isinstance(self.name, str)
                or re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", self.name) is None
                or self.scalar is not None
                or self.items
            ):
                raise ValueError(f"{self.kind.value} type requires one name")
        elif self.kind is TypeKind.READ_ONLY_VIEW:
            if len(self.items) != 1 or self.scalar is not None or self.name is not None:
                raise ValueError("read-only view requires one element type")
        else:
            raise ValueError("unknown callback type")

    @property
    def is_scalar(self) -> bool:
        return self.kind is TypeKind.SCALAR

    @property
    def is_vector(self) -> bool:
        return self.kind is TypeKind.VECTOR

    @property
    def is_integer(self) -> bool:
        return self.kind is TypeKind.SCALAR and self.scalar in {
            ScalarKind.I32, ScalarKind.U32, ScalarKind.I64, ScalarKind.U64,
        }

    @property
    def is_float(self) -> bool:
        return self.kind is TypeKind.SCALAR and self.scalar in {ScalarKind.F32, ScalarKind.F64}

    @property
    def is_bool(self) -> bool:
        return self == BOOL

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {"kind": self.kind.value}
        if self.scalar is not None:
            result["scalar"] = self.scalar.value
        if self.kind is TypeKind.VECTOR:
            result["lanes"] = self.lanes
        if self.name is not None:
            result["name"] = self.name
        if self.items:
            result["items"] = [item.to_dict() for item in self.items]
        return result


def scalar_type(kind: ScalarKind) -> CallbackType:
    return CallbackType(TypeKind.SCALAR, scalar=kind)


def vector_type(kind: ScalarKind, lanes: int) -> CallbackType:
    return CallbackType(TypeKind.VECTOR, scalar=kind, lanes=lanes)


def tuple_type(*items: CallbackType) -> CallbackType:
    return CallbackType(TypeKind.TUPLE, items=tuple(items))


def record_type(name: str) -> CallbackType:
    return CallbackType(TypeKind.RECORD, name=name)


def read_only_view(element: CallbackType) -> CallbackType:
    return CallbackType(TypeKind.READ_ONLY_VIEW, items=(element,))


def builtin_type(name: str) -> CallbackType:
    return CallbackType(TypeKind.BUILTIN, name=name)


BOOL = scalar_type(ScalarKind.BOOL)
I32 = scalar_type(ScalarKind.I32)
U32 = scalar_type(ScalarKind.U32)
I64 = scalar_type(ScalarKind.I64)
U64 = scalar_type(ScalarKind.U64)
F32 = scalar_type(ScalarKind.F32)
F64 = scalar_type(ScalarKind.F64)
VEC2F32 = vector_type(ScalarKind.F32, 2)
VEC3F32 = vector_type(ScalarKind.F32, 3)
VEC4F32 = vector_type(ScalarKind.F32, 4)
RAY3F = builtin_type("Ray3f")
HIT = builtin_type("Hit")
TRIANGLE_HIT = builtin_type("TriangleHit")
AABB3F = builtin_type("Aabb3f")


@dataclass(frozen=True)
class CallbackField:
    name: str
    value_type: CallbackType

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "type": self.value_type.to_dict()}


@dataclass(frozen=True)
class CallbackRecord:
    name: str
    purpose: RecordPurpose
    fields: tuple[CallbackField, ...]

    def field(self, name: str) -> CallbackField | None:
        return next((item for item in self.fields if item.name == name), None)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "purpose": self.purpose.value,
            "fields": [item.to_dict() for item in self.fields],
        }


@dataclass(frozen=True)
class CallbackArgument:
    name: str
    value_type: CallbackType

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "type": self.value_type.to_dict()}


JsonScalar: TypeAlias = str | int | bool | None
AttributeValue: TypeAlias = JsonScalar | tuple[str, ...] | tuple[int, ...]


@dataclass(frozen=True)
class CallbackExpr:
    opcode: str
    value_type: CallbackType
    operands: tuple["CallbackExpr", ...] = ()
    attributes: tuple[tuple[str, AttributeValue], ...] = ()

    def attribute(self, name: str) -> AttributeValue | None:
        return next((value for key, value in self.attributes if key == name), None)

    def to_dict(self) -> dict[str, object]:
        return {
            "opcode": self.opcode,
            "type": self.value_type.to_dict(),
            "operands": [item.to_dict() for item in self.operands],
            "attributes": {key: value for key, value in self.attributes},
        }


@dataclass(frozen=True)
class CallbackEffect:
    kind: EffectKind
    fields: tuple[tuple[str, CallbackExpr], ...] = ()

    def field(self, name: str) -> CallbackExpr | None:
        return next((value for key, value in self.fields if key == name), None)

    def to_dict(self) -> dict[str, object]:
        return {"kind": self.kind.value, "fields": {key: value.to_dict() for key, value in self.fields}}


@dataclass(frozen=True)
class LetStatement:
    name: str
    value: CallbackExpr

    def to_dict(self) -> dict[str, object]:
        return {"kind": "let", "name": self.name, "value": self.value.to_dict()}


@dataclass(frozen=True)
class SetStatement:
    name: str
    value: CallbackExpr

    def to_dict(self) -> dict[str, object]:
        return {"kind": "set", "name": self.name, "value": self.value.to_dict()}


@dataclass(frozen=True)
class IfStatement:
    condition: CallbackExpr
    then_body: tuple["CallbackStatement", ...]
    else_body: tuple["CallbackStatement", ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "if",
            "condition": self.condition.to_dict(),
            "then": [item.to_dict() for item in self.then_body],
            "else": [item.to_dict() for item in self.else_body],
        }


@dataclass(frozen=True)
class StaticForStatement:
    index_name: str
    trip_count: int
    body: tuple["CallbackStatement", ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "static_for",
            "index": self.index_name,
            "trip_count": self.trip_count,
            "body": [item.to_dict() for item in self.body],
        }


@dataclass(frozen=True)
class ReturnEffectStatement:
    effect: CallbackEffect

    def to_dict(self) -> dict[str, object]:
        return {"kind": "return_effect", "effect": self.effect.to_dict()}


@dataclass(frozen=True)
class ReturnValueStatement:
    value: CallbackExpr

    def to_dict(self) -> dict[str, object]:
        return {"kind": "return_value", "value": self.value.to_dict()}


CallbackStatement: TypeAlias = (
    LetStatement | SetStatement | IfStatement | StaticForStatement
    | ReturnEffectStatement | ReturnValueStatement
)


@dataclass(frozen=True)
class CallbackFunction:
    name: str
    arguments: tuple[CallbackArgument, ...]
    body: tuple[CallbackStatement, ...]
    role: CallbackRole | None = None
    return_type: CallbackType | None = None

    @property
    def is_helper(self) -> bool:
        return self.role is None

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "role": None if self.role is None else self.role.value,
            "arguments": [item.to_dict() for item in self.arguments],
            "return_type": None if self.return_type is None else self.return_type.to_dict(),
            "body": [item.to_dict() for item in self.body],
        }


@dataclass(frozen=True)
class FrozenConstant:
    name: str
    value_type: CallbackType
    value: bool | int | float | tuple[object, ...]

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "type": self.value_type.to_dict(), "value": self.value}


@dataclass(frozen=True)
class NumericContract:
    strict_f32: bool = True
    implicit_fast_math: bool = False
    integer_overflow: str = "fail_closed"
    nonfinite_input: str = "fail_closed"
    nonfinite_effect: str = "fail_closed"

    def to_dict(self) -> dict[str, object]:
        return {
            "strict_f32": self.strict_f32,
            "implicit_fast_math": self.implicit_fast_math,
            "integer_overflow": self.integer_overflow,
            "nonfinite_input": self.nonfinite_input,
            "nonfinite_effect": self.nonfinite_effect,
        }


@dataclass(frozen=True)
class ResourceBudget:
    max_payload_u32_slots: int = 32
    max_attribute_u32_slots: int = 8
    max_trace_depth: int = 1
    max_callable_depth: int = 0
    max_static_loop_trip_count: int = MAX_STATIC_LOOP_TRIP_COUNT
    max_total_static_iterations: int = 4096
    max_helper_call_depth: int = MAX_HELPER_CALL_DEPTH

    def to_dict(self) -> dict[str, object]:
        return {
            "max_payload_u32_slots": self.max_payload_u32_slots,
            "max_attribute_u32_slots": self.max_attribute_u32_slots,
            "max_trace_depth": self.max_trace_depth,
            "max_callable_depth": self.max_callable_depth,
            "max_static_loop_trip_count": self.max_static_loop_trip_count,
            "max_total_static_iterations": self.max_total_static_iterations,
            "max_helper_call_depth": self.max_helper_call_depth,
        }


@dataclass(frozen=True)
class GeometryContract:
    admission: GeometryAdmission
    contract_name: str
    target_f32_outward_rounding: bool
    proof_sha256: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "admission": self.admission.value,
            "contract_name": self.contract_name,
            "target_f32_outward_rounding": self.target_f32_outward_rounding,
            "proof_sha256": self.proof_sha256,
        }


@dataclass(frozen=True)
class GeometryProofAuthority:
    """Trusted, out-of-program authority for a verified geometry callback pair.

    A program cannot mint this authority by naming its own contract.  The
    verifier caller must supply an authority whose proof and exact normalized
    callback-source identities both match the submitted program.
    """

    contract_name: str
    callback_source_sha256: str
    proof_sha256: str
    target_f32_outward_rounding: bool


@dataclass(frozen=True)
class CallbackModuleManifest:
    name: str
    payload_record: str
    output_record: str
    attribute_types: tuple[CallbackType, ...]
    constants: tuple[FrozenConstant, ...]
    numeric: NumericContract
    resources: ResourceBudget
    geometry: GeometryContract
    any_hit_delivery: AnyHitDeliveryContract | None
    selected_linkage: LinkageMechanism
    linkage_selection_reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "payload_record": self.payload_record,
            "output_record": self.output_record,
            "attribute_types": [item.to_dict() for item in self.attribute_types],
            "constants": [item.to_dict() for item in self.constants],
            "numeric": self.numeric.to_dict(),
            "resources": self.resources.to_dict(),
            "geometry": self.geometry.to_dict(),
            "any_hit_delivery": None if self.any_hit_delivery is None else self.any_hit_delivery.value,
            "selected_linkage": self.selected_linkage.value,
            "linkage_selection_reason": self.linkage_selection_reason,
        }


@dataclass(frozen=True)
class CallbackProgramSpec:
    schema_id: str
    schema_version: str
    manifest: CallbackModuleManifest
    records: tuple[CallbackRecord, ...]
    functions: tuple[CallbackFunction, ...]
    normalized_source: str
    source_sha256: str

    def function_for_role(self, role: CallbackRole) -> CallbackFunction:
        matches = [item for item in self.functions if item.role is role]
        if len(matches) != 1:
            _fail("role_cardinality", f"functions.{role.value}", "expected exactly one role function")
        return matches[0]

    def record(self, name: str) -> CallbackRecord:
        matches = [item for item in self.records if item.name == name]
        if len(matches) != 1:
            _fail("record_cardinality", f"records.{name}", "expected exactly one record")
        return matches[0]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "manifest": self.manifest.to_dict(),
            "records": [item.to_dict() for item in self.records],
            "functions": [item.to_dict() for item in self.functions],
            "normalized_source": self.normalized_source,
            "source_sha256": self.source_sha256,
        }

    @property
    def ir_sha256(self) -> str:
        payload = dict(self.to_dict())
        payload.pop("normalized_source")
        payload.pop("source_sha256")
        return hashlib.sha256(_canonical_json(payload)).hexdigest()


@dataclass(frozen=True)
class VerifiedCallbackProgram:
    program: CallbackProgramSpec
    ir_sha256: str
    effect_digest: str
    payload_u32_slots: int
    attribute_u32_slots: int
    total_static_iterations: int
    helper_call_depth: int

    def to_dict(self) -> dict[str, object]:
        return {
            "ir_sha256": self.ir_sha256,
            "effect_digest": self.effect_digest,
            "payload_u32_slots": self.payload_u32_slots,
            "attribute_u32_slots": self.attribute_u32_slots,
            "total_static_iterations": self.total_static_iterations,
            "helper_call_depth": self.helper_call_depth,
        }


_ROLE_EFFECTS: Mapping[CallbackRole, frozenset[EffectKind]] = {
    CallbackRole.BOUNDS: frozenset({EffectKind.AABB}),
    CallbackRole.MAKE_RAY: frozenset({EffectKind.TRACE_REQUEST}),
    CallbackRole.INTERSECTION: frozenset({EffectKind.HIT, EffectKind.NO_HIT}),
    CallbackRole.ANY_HIT: frozenset({EffectKind.ACCEPT_CONTINUE, EffectKind.IGNORE, EffectKind.TERMINATE}),
    CallbackRole.CLOSEST_HIT: frozenset({EffectKind.PAYLOAD}),
    CallbackRole.MISS: frozenset({EffectKind.PAYLOAD}),
    CallbackRole.FINALIZE: frozenset({EffectKind.OUTPUT}),
}


def verify_callback_program(
    program: CallbackProgramSpec,
    *,
    geometry_proof_authorities: Mapping[str, GeometryProofAuthority] | None = None,
) -> VerifiedCallbackProgram:
    """Verify a legacy seven-role V4 Callback IR v1 program or fail closed."""

    return _verify_callback_program_with_role_contract(
        program,
        required_roles=frozenset({
            CallbackRole.BOUNDS,
            CallbackRole.MAKE_RAY,
            CallbackRole.INTERSECTION,
            CallbackRole.MISS,
            CallbackRole.FINALIZE,
        }),
        forbidden_roles=frozenset(),
        hit_value_type=HIT,
        allow_hit_read_only_views=False,
        allowed_geometry_admissions=frozenset({
            GeometryAdmission.VERIFIED_CONTRACT,
            GeometryAdmission.TESTED_USER_GEOMETRY,
        }),
        expected_schema_version=CALLBACK_IR_SCHEMA_VERSION,
        geometry_proof_authorities=geometry_proof_authorities,
    )


def _verify_callback_program_with_role_contract(
    program: CallbackProgramSpec,
    *,
    required_roles: frozenset[CallbackRole],
    forbidden_roles: frozenset[CallbackRole],
    hit_value_type: CallbackType,
    allow_hit_read_only_views: bool,
    allowed_geometry_admissions: frozenset[GeometryAdmission],
    expected_schema_version: str,
    geometry_proof_authorities: Mapping[str, GeometryProofAuthority] | None = None,
) -> VerifiedCallbackProgram:
    """Verify Callback IR under a compiler-owned physical role contract.

    The public legacy verifier above always supplies the frozen seven-role
    contract.  Goal5755's typed physical-schema verifier is the only product
    consumer of this package-private seam for geometry-indexed role topology.
    A result from this function is not physical execution authority by itself.
    """

    if hit_value_type not in {HIT, TRIANGLE_HIT}:
        _fail("hit_value_type", "role_contract", "unsupported hit builtin")
    if required_roles & forbidden_roles:
        _fail("role_contract_overlap", "role_contract", "required and forbidden roles overlap")

    if program.schema_id != CALLBACK_IR_SCHEMA_ID or program.schema_version != expected_schema_version:
        _fail("schema_identity", "program", "unsupported Callback IR schema")
    expected_source = hashlib.sha256(program.normalized_source.encode("utf-8")).hexdigest()
    if expected_source != program.source_sha256:
        _fail("source_digest", "program.source_sha256", "normalized source digest mismatch")
    manifest = program.manifest
    if not _identifier(manifest.name):
        _fail("manifest_name", "manifest.name", "manifest name must be an identifier")
    if manifest.selected_linkage is not LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1:
        _fail(
            "production_linkage_not_reviewed",
            "manifest.selected_linkage",
            "Goal5750 freezes the cross-target-evidenced single-module composer; diagnostics cannot be promoted",
        )
    if not manifest.linkage_selection_reason.strip():
        _fail("linkage_reason", "manifest.linkage_selection_reason", "selection reason is required")
    _verify_numeric_contract(manifest.numeric)
    _verify_resource_budget(manifest.resources)
    _verify_geometry_contract(
        manifest.geometry,
        program_source_sha256=program.source_sha256,
        authorities=geometry_proof_authorities,
        allowed_admissions=allowed_geometry_admissions,
    )
    records = _unique_named(program.records, "records")
    _verify_records(program.records, records)
    payload = records.get(manifest.payload_record)
    output = records.get(manifest.output_record)
    if payload is None or payload.purpose is not RecordPurpose.PAYLOAD:
        _fail("payload_record", "manifest.payload_record", "must name one payload record")
    if output is None or output.purpose is not RecordPurpose.OUTPUT:
        _fail("output_record", "manifest.output_record", "must name one output record")
    payload_slots = _type_u32_slots(record_type(payload.name), records, set())
    attribute_slots = sum(_type_u32_slots(item, records, set()) for item in manifest.attribute_types)
    if payload_slots > manifest.resources.max_payload_u32_slots:
        _fail("payload_resource", "manifest.payload_record", f"payload needs {payload_slots} u32 slots")
    if attribute_slots > manifest.resources.max_attribute_u32_slots:
        _fail("attribute_resource", "manifest.attribute_types", f"attributes need {attribute_slots} u32 slots")
    _verify_constants(manifest.constants, records)

    functions = _unique_named(program.functions, "functions")
    role_map: dict[CallbackRole, CallbackFunction] = {}
    helpers: dict[str, CallbackFunction] = {}
    for function in program.functions:
        if function.role is None:
            helpers[function.name] = function
        elif function.role in role_map:
            _fail("duplicate_role", f"functions.{function.name}", function.role.value)
        else:
            role_map[function.role] = function
    missing = required_roles - set(role_map)
    if missing:
        _fail("missing_roles", "functions", ",".join(sorted(item.value for item in missing)))
    conflicting = forbidden_roles & set(role_map)
    if conflicting:
        _fail("forbidden_roles", "functions", ",".join(sorted(item.value for item in conflicting)))
    if CallbackRole.ANY_HIT not in role_map and CallbackRole.CLOSEST_HIT not in role_map:
        _fail("hit_stage_missing", "functions", "any_hit or closest_hit is required")
    if CallbackRole.ANY_HIT in role_map and manifest.any_hit_delivery is None:
        _fail("any_hit_delivery_contract", "manifest.any_hit_delivery", "any-hit requires an explicit delivery contract")
    if CallbackRole.ANY_HIT not in role_map and manifest.any_hit_delivery is not None:
        _fail("unused_any_hit_delivery_contract", "manifest.any_hit_delivery", "contract supplied without any-hit")

    call_graph = _helper_call_graph(program.functions)
    helper_depth = _verify_helper_call_graph(call_graph, manifest.resources.max_helper_call_depth)
    total_static_iterations = 0
    effects: list[tuple[str, tuple[str, ...]]] = []
    constant_types = {item.name: item.value_type for item in manifest.constants}
    for index, function in enumerate(program.functions):
        path = f"functions[{index}]"
        _verify_function_signature(
            function,
            payload,
            output,
            records,
            path,
            hit_value_type=hit_value_type,
            allow_hit_read_only_views=allow_hit_read_only_views,
        )
        environment: dict[str, CallbackType] = dict(constant_types)
        for argument in function.arguments:
            if argument.name in environment or not _identifier(argument.name):
                _fail("argument_name", f"{path}.arguments", argument.name)
            _verify_type(argument.value_type, records, f"{path}.arguments.{argument.name}", set())
            environment[argument.name] = argument.value_type
        result = _verify_statements(
            function.body,
            environment,
            function=function,
            helpers=helpers,
            records=records,
            manifest=manifest,
            path=f"{path}.body",
            inside_loop=False,
        )
        if not result[1]:
            _fail("not_all_paths_return", path, "every callback/helper path must return")
        total_static_iterations += result[2]
        effects.append((function.name, tuple(sorted(item.value for item in result[3]))))
    if total_static_iterations > manifest.resources.max_total_static_iterations:
        _fail(
            "total_static_iterations",
            "functions",
            f"{total_static_iterations} exceeds {manifest.resources.max_total_static_iterations}",
        )
    effect_digest = hashlib.sha256(_canonical_json(effects)).hexdigest()
    return VerifiedCallbackProgram(
        program=program,
        ir_sha256=program.ir_sha256,
        effect_digest=effect_digest,
        payload_u32_slots=payload_slots,
        attribute_u32_slots=attribute_slots,
        total_static_iterations=total_static_iterations,
        helper_call_depth=helper_depth,
    )


def callback_program_from_dict(
    payload: Mapping[str, object],
    *,
    geometry_proof_authorities: Mapping[str, GeometryProofAuthority] | None = None,
) -> CallbackProgramSpec:
    """Reconstruct Callback IR from its strict canonical JSON representation."""

    try:
        return _callback_program_from_dict_impl(
            payload,
            geometry_proof_authorities=geometry_proof_authorities,
        )
    except CallbackVerificationError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        # Enum constructors and dataclass shape checks raise standard Python
        # exceptions.  They are safe rejections, but the public hostile-input
        # boundary must expose one coded fail-closed error family.
        raise CallbackVerificationError(
            "decode_error",
            "program",
            f"{type(exc).__name__}: {exc}",
        ) from exc


def _callback_program_from_dict_impl(
    payload: Mapping[str, object],
    *,
    geometry_proof_authorities: Mapping[str, GeometryProofAuthority] | None,
) -> CallbackProgramSpec:

    _keys(payload, {"schema_id", "schema_version", "manifest", "records", "functions", "normalized_source", "source_sha256"}, "program")
    manifest = _manifest_from_dict(_mapping(payload.get("manifest"), "program.manifest"))
    records = tuple(
        _record_from_dict(_mapping(item, f"program.records[{index}]"), f"program.records[{index}]")
        for index, item in enumerate(_sequence(payload.get("records"), "program.records"))
    )
    functions = tuple(
        _function_from_dict(_mapping(item, f"program.functions[{index}]"), f"program.functions[{index}]")
        for index, item in enumerate(_sequence(payload.get("functions"), "program.functions"))
    )
    result = CallbackProgramSpec(
        schema_id=_string(payload.get("schema_id"), "program.schema_id"),
        schema_version=_string(payload.get("schema_version"), "program.schema_version"),
        manifest=manifest,
        records=records,
        functions=functions,
        normalized_source=_string(payload.get("normalized_source"), "program.normalized_source"),
        source_sha256=_string(payload.get("source_sha256"), "program.source_sha256"),
    )
    verify_callback_program(result, geometry_proof_authorities=geometry_proof_authorities)
    return result


def _manifest_from_dict(payload: Mapping[str, object]) -> CallbackModuleManifest:
    path = "program.manifest"
    _keys(payload, {
        "name", "payload_record", "output_record", "attribute_types", "constants",
        "numeric", "resources", "geometry", "any_hit_delivery", "selected_linkage",
        "linkage_selection_reason",
    }, path)
    numeric_payload = _mapping(payload.get("numeric"), f"{path}.numeric")
    _keys(numeric_payload, {"strict_f32", "implicit_fast_math", "integer_overflow", "nonfinite_input", "nonfinite_effect"}, f"{path}.numeric")
    numeric = NumericContract(
        strict_f32=_boolean(numeric_payload.get("strict_f32"), f"{path}.numeric.strict_f32"),
        implicit_fast_math=_boolean(numeric_payload.get("implicit_fast_math"), f"{path}.numeric.implicit_fast_math"),
        integer_overflow=_string(numeric_payload.get("integer_overflow"), f"{path}.numeric.integer_overflow"),
        nonfinite_input=_string(numeric_payload.get("nonfinite_input"), f"{path}.numeric.nonfinite_input"),
        nonfinite_effect=_string(numeric_payload.get("nonfinite_effect"), f"{path}.numeric.nonfinite_effect"),
    )
    resource_payload = _mapping(payload.get("resources"), f"{path}.resources")
    resource_fields = {
        "max_payload_u32_slots", "max_attribute_u32_slots", "max_trace_depth",
        "max_callable_depth", "max_static_loop_trip_count", "max_total_static_iterations",
        "max_helper_call_depth",
    }
    _keys(resource_payload, resource_fields, f"{path}.resources")
    resources = ResourceBudget(**{
        key: _integer(resource_payload.get(key), f"{path}.resources.{key}") for key in resource_fields
    })
    geometry_payload = _mapping(payload.get("geometry"), f"{path}.geometry")
    _keys(
        geometry_payload,
        {"admission", "contract_name", "target_f32_outward_rounding", "proof_sha256"},
        f"{path}.geometry",
    )
    proof_sha = geometry_payload.get("proof_sha256")
    geometry = GeometryContract(
        GeometryAdmission(_string(geometry_payload.get("admission"), f"{path}.geometry.admission")),
        _string(geometry_payload.get("contract_name"), f"{path}.geometry.contract_name"),
        _boolean(geometry_payload.get("target_f32_outward_rounding"), f"{path}.geometry.target_f32_outward_rounding"),
        None if proof_sha is None else _string(proof_sha, f"{path}.geometry.proof_sha256"),
    )
    constants = tuple(
        _constant_from_dict(_mapping(item, f"{path}.constants[{index}]"), f"{path}.constants[{index}]")
        for index, item in enumerate(_sequence(payload.get("constants"), f"{path}.constants"))
    )
    any_hit = payload.get("any_hit_delivery")
    return CallbackModuleManifest(
        name=_string(payload.get("name"), f"{path}.name"),
        payload_record=_string(payload.get("payload_record"), f"{path}.payload_record"),
        output_record=_string(payload.get("output_record"), f"{path}.output_record"),
        attribute_types=tuple(
            _type_from_dict(_mapping(item, f"{path}.attribute_types[{index}]"), f"{path}.attribute_types[{index}]")
            for index, item in enumerate(_sequence(payload.get("attribute_types"), f"{path}.attribute_types"))
        ),
        constants=constants,
        numeric=numeric,
        resources=resources,
        geometry=geometry,
        any_hit_delivery=None if any_hit is None else AnyHitDeliveryContract(_string(any_hit, f"{path}.any_hit_delivery")),
        selected_linkage=LinkageMechanism(_string(payload.get("selected_linkage"), f"{path}.selected_linkage")),
        linkage_selection_reason=_string(payload.get("linkage_selection_reason"), f"{path}.linkage_selection_reason"),
    )


def _record_from_dict(payload: Mapping[str, object], path: str) -> CallbackRecord:
    _keys(payload, {"name", "purpose", "fields"}, path)
    return CallbackRecord(
        _string(payload.get("name"), f"{path}.name"),
        RecordPurpose(_string(payload.get("purpose"), f"{path}.purpose")),
        tuple(
            _field_from_dict(_mapping(item, f"{path}.fields[{index}]"), f"{path}.fields[{index}]")
            for index, item in enumerate(_sequence(payload.get("fields"), f"{path}.fields"))
        ),
    )


def _field_from_dict(payload: Mapping[str, object], path: str) -> CallbackField:
    _keys(payload, {"name", "type"}, path)
    return CallbackField(
        _string(payload.get("name"), f"{path}.name"),
        _type_from_dict(_mapping(payload.get("type"), f"{path}.type"), f"{path}.type"),
    )


def _constant_from_dict(payload: Mapping[str, object], path: str) -> FrozenConstant:
    _keys(payload, {"name", "type", "value"}, path)
    value_type = _type_from_dict(_mapping(payload.get("type"), f"{path}.type"), f"{path}.type")
    raw = payload.get("value")
    value = _literal_from_json(raw, value_type, f"{path}.value")
    return FrozenConstant(_string(payload.get("name"), f"{path}.name"), value_type, value)


def _function_from_dict(payload: Mapping[str, object], path: str) -> CallbackFunction:
    _keys(payload, {"name", "role", "arguments", "return_type", "body"}, path)
    raw_role = payload.get("role")
    raw_return = payload.get("return_type")
    return CallbackFunction(
        name=_string(payload.get("name"), f"{path}.name"),
        role=None if raw_role is None else CallbackRole(_string(raw_role, f"{path}.role")),
        arguments=tuple(
            _argument_from_dict(_mapping(item, f"{path}.arguments[{index}]"), f"{path}.arguments[{index}]")
            for index, item in enumerate(_sequence(payload.get("arguments"), f"{path}.arguments"))
        ),
        return_type=None if raw_return is None else _type_from_dict(_mapping(raw_return, f"{path}.return_type"), f"{path}.return_type"),
        body=tuple(
            _statement_from_dict(_mapping(item, f"{path}.body[{index}]"), f"{path}.body[{index}]")
            for index, item in enumerate(_sequence(payload.get("body"), f"{path}.body"))
        ),
    )


def _argument_from_dict(payload: Mapping[str, object], path: str) -> CallbackArgument:
    _keys(payload, {"name", "type"}, path)
    return CallbackArgument(
        _string(payload.get("name"), f"{path}.name"),
        _type_from_dict(_mapping(payload.get("type"), f"{path}.type"), f"{path}.type"),
    )


def _statement_from_dict(payload: Mapping[str, object], path: str) -> CallbackStatement:
    kind = _string(payload.get("kind"), f"{path}.kind")
    if kind in {"let", "set"}:
        _keys(payload, {"kind", "name", "value"}, path)
        cls = LetStatement if kind == "let" else SetStatement
        return cls(
            _string(payload.get("name"), f"{path}.name"),
            _expr_from_dict(_mapping(payload.get("value"), f"{path}.value"), f"{path}.value"),
        )
    if kind == "if":
        _keys(payload, {"kind", "condition", "then", "else"}, path)
        return IfStatement(
            _expr_from_dict(_mapping(payload.get("condition"), f"{path}.condition"), f"{path}.condition"),
            tuple(_statement_from_dict(_mapping(item, f"{path}.then[{i}]"), f"{path}.then[{i}]") for i, item in enumerate(_sequence(payload.get("then"), f"{path}.then"))),
            tuple(_statement_from_dict(_mapping(item, f"{path}.else[{i}]"), f"{path}.else[{i}]") for i, item in enumerate(_sequence(payload.get("else"), f"{path}.else"))),
        )
    if kind == "static_for":
        _keys(payload, {"kind", "index", "trip_count", "body"}, path)
        return StaticForStatement(
            _string(payload.get("index"), f"{path}.index"),
            _integer(payload.get("trip_count"), f"{path}.trip_count"),
            tuple(_statement_from_dict(_mapping(item, f"{path}.body[{i}]"), f"{path}.body[{i}]") for i, item in enumerate(_sequence(payload.get("body"), f"{path}.body"))),
        )
    if kind == "return_effect":
        _keys(payload, {"kind", "effect"}, path)
        effect_payload = _mapping(payload.get("effect"), f"{path}.effect")
        _keys(effect_payload, {"kind", "fields"}, f"{path}.effect")
        fields_payload = _mapping(effect_payload.get("fields"), f"{path}.effect.fields")
        return ReturnEffectStatement(CallbackEffect(
            EffectKind(_string(effect_payload.get("kind"), f"{path}.effect.kind")),
            tuple((name, _expr_from_dict(_mapping(value, f"{path}.effect.fields.{name}"), f"{path}.effect.fields.{name}")) for name, value in fields_payload.items()),
        ))
    if kind == "return_value":
        _keys(payload, {"kind", "value"}, path)
        return ReturnValueStatement(_expr_from_dict(_mapping(payload.get("value"), f"{path}.value"), f"{path}.value"))
    _fail("statement_kind", path, kind)
    raise AssertionError


def _expr_from_dict(payload: Mapping[str, object], path: str) -> CallbackExpr:
    _keys(payload, {"opcode", "type", "operands", "attributes"}, path)
    attributes_payload = _mapping(payload.get("attributes"), f"{path}.attributes")
    attributes: list[tuple[str, AttributeValue]] = []
    for name, value in attributes_payload.items():
        if isinstance(value, list):
            if all(isinstance(item, str) for item in value): normalized: AttributeValue = tuple(value)
            elif all(isinstance(item, int) and not isinstance(item, bool) for item in value): normalized = tuple(value)
            else: _fail("expression_attribute", f"{path}.attributes.{name}", repr(value))
        elif value is None or isinstance(value, (str, bool, int)):
            normalized = value
        elif isinstance(value, float) and math.isfinite(value):
            # Literal floating values are JSON-safe but AttributeValue is kept
            # closed elsewhere; they occur only on literal expressions.
            normalized = value  # type: ignore[assignment]
        else:
            _fail("expression_attribute", f"{path}.attributes.{name}", repr(value))
        attributes.append((name, normalized))
    return CallbackExpr(
        opcode=_string(payload.get("opcode"), f"{path}.opcode"),
        value_type=_type_from_dict(_mapping(payload.get("type"), f"{path}.type"), f"{path}.type"),
        operands=tuple(
            _expr_from_dict(_mapping(item, f"{path}.operands[{index}]"), f"{path}.operands[{index}]")
            for index, item in enumerate(_sequence(payload.get("operands"), f"{path}.operands"))
        ),
        attributes=tuple(attributes),
    )


def _type_from_dict(payload: Mapping[str, object], path: str) -> CallbackType:
    kind = TypeKind(_string(payload.get("kind"), f"{path}.kind"))
    allowed = {"kind"}
    if kind is TypeKind.SCALAR:
        allowed.add("scalar"); _keys(payload, allowed, path)
        return scalar_type(ScalarKind(_string(payload.get("scalar"), f"{path}.scalar")))
    if kind is TypeKind.VECTOR:
        allowed.update({"scalar", "lanes"}); _keys(payload, allowed, path)
        return vector_type(
            ScalarKind(_string(payload.get("scalar"), f"{path}.scalar")),
            _integer(payload.get("lanes"), f"{path}.lanes"),
        )
    if kind is TypeKind.TUPLE:
        allowed.add("items"); _keys(payload, allowed, path)
        return tuple_type(*(
            _type_from_dict(_mapping(item, f"{path}.items[{index}]"), f"{path}.items[{index}]")
            for index, item in enumerate(_sequence(payload.get("items"), f"{path}.items"))
        ))
    if kind in {TypeKind.RECORD, TypeKind.BUILTIN}:
        allowed.add("name"); _keys(payload, allowed, path)
        name = _string(payload.get("name"), f"{path}.name")
        return record_type(name) if kind is TypeKind.RECORD else builtin_type(name)
    if kind is TypeKind.READ_ONLY_VIEW:
        allowed.add("items"); _keys(payload, allowed, path)
        items = _sequence(payload.get("items"), f"{path}.items")
        if len(items) != 1: _fail("view_type", path, "one element type required")
        return read_only_view(_type_from_dict(_mapping(items[0], f"{path}.items[0]"), f"{path}.items[0]"))
    raise AssertionError(kind)


def _literal_from_json(value: object, value_type: CallbackType, path: str):
    if value_type.kind in {TypeKind.VECTOR, TypeKind.TUPLE}:
        values = _sequence(value, path)
        types = (
            tuple(scalar_type(value_type.scalar) for _ in range(value_type.lanes))
            if value_type.kind is TypeKind.VECTOR else value_type.items
        )
        if len(values) != len(types): _fail("literal_shape", path, "length mismatch")
        return tuple(_literal_from_json(item, item_type, f"{path}[{index}]") for index, (item, item_type) in enumerate(zip(values, types)))
    _verify_literal(value, value_type, path)
    return value


def _keys(payload: Mapping[str, object], expected: set[str], path: str) -> None:
    actual = set(payload)
    if actual != expected:
        _fail("object_keys", path, f"expected {sorted(expected)}, got {sorted(actual)}")


def _mapping(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
        _fail("mapping_required", path, type(value).__name__)
    return value


def _sequence(value: object, path: str) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        _fail("sequence_required", path, type(value).__name__)
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str): _fail("string_required", path, type(value).__name__)
    return value


def _integer(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool): _fail("integer_required", path, type(value).__name__)
    return value


def _boolean(value: object, path: str) -> bool:
    if not isinstance(value, bool): _fail("boolean_required", path, type(value).__name__)
    return value


def _verify_statements(
    statements: Sequence[CallbackStatement],
    environment: Mapping[str, CallbackType],
    *,
    function: CallbackFunction,
    helpers: Mapping[str, CallbackFunction],
    records: Mapping[str, CallbackRecord],
    manifest: CallbackModuleManifest,
    path: str,
    inside_loop: bool,
) -> tuple[dict[str, CallbackType], bool, int, frozenset[EffectKind]]:
    values = dict(environment)
    returned = False
    static_iterations = 0
    effects: set[EffectKind] = set()
    for index, statement in enumerate(statements):
        item_path = f"{path}[{index}]"
        if returned:
            _fail("unreachable_statement", item_path, "statement follows unconditional return")
        if isinstance(statement, LetStatement):
            if not _identifier(statement.name) or statement.name in values:
                _fail("ssa_name", item_path, statement.name)
            _verify_expr(statement.value, values, helpers, records, item_path)
            values[statement.name] = statement.value.value_type
        elif isinstance(statement, SetStatement):
            if not inside_loop:
                _fail("mutation_outside_static_loop", item_path, statement.name)
            prior = values.get(statement.name)
            if prior is None:
                _fail("mutation_unknown_value", item_path, statement.name)
            _verify_expr(statement.value, values, helpers, records, item_path)
            if statement.value.value_type != prior:
                _fail("mutation_type", item_path, statement.name)
        elif isinstance(statement, IfStatement):
            _verify_expr(statement.condition, values, helpers, records, f"{item_path}.condition")
            if statement.condition.value_type != BOOL:
                _fail("if_condition_type", item_path, "if condition must be bool")
            left = _verify_statements(
                statement.then_body, values, function=function, helpers=helpers,
                records=records, manifest=manifest, path=f"{item_path}.then", inside_loop=inside_loop,
            )
            right = _verify_statements(
                statement.else_body, values, function=function, helpers=helpers,
                records=records, manifest=manifest, path=f"{item_path}.else", inside_loop=inside_loop,
            )
            both_return = left[1] and right[1]
            if not both_return and left[0] != right[0]:
                _fail("branch_environment", item_path, "branches must define the same typed names")
            if not both_return:
                values = left[0]
            returned = both_return
            static_iterations += left[2] + right[2]
            effects.update(left[3]); effects.update(right[3])
        elif isinstance(statement, StaticForStatement):
            if not _identifier(statement.index_name) or statement.index_name in values:
                _fail("loop_index", item_path, statement.index_name)
            if not isinstance(statement.trip_count, int) or isinstance(statement.trip_count, bool) \
                    or not 0 <= statement.trip_count <= manifest.resources.max_static_loop_trip_count:
                _fail("loop_bound", item_path, str(statement.trip_count))
            loop_values = dict(values)
            loop_values[statement.index_name] = U32
            loop_result = _verify_statements(
                statement.body, loop_values, function=function, helpers=helpers,
                records=records, manifest=manifest, path=f"{item_path}.body", inside_loop=True,
            )
            if loop_result[1]:
                _fail("loop_return", item_path, "static loops cannot contain callback return")
            post_loop = dict(loop_result[0]); post_loop.pop(statement.index_name, None)
            if set(post_loop) != set(values) or any(post_loop[key] != values[key] for key in values):
                _fail("loop_scope", item_path, "loop may mutate existing values but cannot leak locals")
            static_iterations += statement.trip_count * max(1, 1 + loop_result[2])
            effects.update(loop_result[3])
        elif isinstance(statement, ReturnEffectStatement):
            if function.role is None:
                _fail("helper_effect", item_path, "helpers return values, not traversal effects")
            _verify_effect(statement.effect, function.role, values, helpers, records, manifest, item_path)
            effects.add(statement.effect.kind)
            returned = True
        elif isinstance(statement, ReturnValueStatement):
            if function.role is not None:
                _fail("callback_value_return", item_path, "callbacks return typed effects")
            if function.return_type is None:
                _fail("helper_return_type", item_path, "helper return type is missing")
            _verify_expr(statement.value, values, helpers, records, item_path)
            if statement.value.value_type != function.return_type:
                _fail("helper_return_type", item_path, "helper result type mismatch")
            returned = True
        else:
            _fail("statement_kind", item_path, type(statement).__name__)
    return values, returned, static_iterations, frozenset(effects)


def _verify_expr(
    expression: CallbackExpr,
    environment: Mapping[str, CallbackType],
    helpers: Mapping[str, CallbackFunction],
    records: Mapping[str, CallbackRecord],
    path: str,
) -> None:
    _verify_type(expression.value_type, records, f"{path}.type", set())
    for index, operand in enumerate(expression.operands):
        _verify_expr(operand, environment, helpers, records, f"{path}.operands[{index}]")
    attrs = dict(expression.attributes)
    if len(attrs) != len(expression.attributes):
        _fail("duplicate_expression_attribute", path, expression.opcode)
    op = expression.opcode
    operands = expression.operands
    if op == "argument" or op == "local" or op == "constant":
        name = attrs.get("name")
        if not isinstance(name, str) or environment.get(name) != expression.value_type or operands:
            _fail("value_reference", path, repr(name))
    elif op == "literal":
        if operands or "value" not in attrs:
            _fail("literal_shape", path, "literal requires one value attribute")
        _verify_literal(attrs["value"], expression.value_type, path)
    elif op == "field":
        if len(operands) != 1 or not isinstance(attrs.get("name"), str):
            _fail("field_shape", path, "field requires base and name")
        field_type = _field_type(operands[0].value_type, str(attrs["name"]), records, path)
        if field_type != expression.value_type:
            _fail("field_type", path, str(attrs["name"]))
    elif op == "view_load":
        if len(operands) != 2 or operands[0].value_type.kind is not TypeKind.READ_ONLY_VIEW \
                or not operands[1].value_type.is_integer:
            _fail("view_load_shape", path, "view_load(view, integer_index)")
        if operands[0].value_type.items[0] != expression.value_type:
            _fail("view_load_type", path, "view element type mismatch")
    elif op in {"add", "sub", "mul", "div", "min", "max"}:
        if len(operands) != 2 or operands[0].value_type != operands[1].value_type \
                or operands[0].value_type != expression.value_type \
                or not _numeric_shape(expression.value_type):
            _fail("numeric_binary_type", path, op)
    elif op in {"bit_and", "bit_or", "bit_xor", "shift_left", "shift_right"}:
        if len(operands) != 2 or not operands[0].value_type.is_integer \
                or not operands[1].value_type.is_integer or operands[0].value_type != expression.value_type:
            _fail("integer_binary_type", path, op)
    elif op in {"neg", "abs"}:
        if len(operands) != 1 or operands[0].value_type != expression.value_type \
                or not _numeric_shape(expression.value_type):
            _fail("numeric_unary_type", path, op)
    elif op == "not":
        if len(operands) != 1 or operands[0].value_type != BOOL or expression.value_type != BOOL:
            _fail("bool_not_type", path, op)
    elif op in {"and", "or"}:
        if len(operands) < 2 or expression.value_type != BOOL \
                or any(item.value_type != BOOL for item in operands):
            _fail("bool_operator_type", path, op)
    elif op in {"eq", "ne", "lt", "le", "gt", "ge"}:
        if len(operands) != 2 or operands[0].value_type != operands[1].value_type \
                or expression.value_type != BOOL or not _comparable(operands[0].value_type):
            _fail("comparison_type", path, op)
    elif op == "select":
        if len(operands) != 3 or operands[0].value_type != BOOL \
                or operands[1].value_type != operands[2].value_type \
                or operands[1].value_type != expression.value_type:
            _fail("select_type", path, op)
    elif op in {"sqrt", "isfinite"}:
        if len(operands) != 1 or not _float_shape(operands[0].value_type):
            _fail("float_intrinsic_type", path, op)
        expected = BOOL if op == "isfinite" else operands[0].value_type
        if expression.value_type != expected:
            _fail("float_intrinsic_result", path, op)
    elif op == "dot":
        if len(operands) != 2 or operands[0].value_type != operands[1].value_type \
                or operands[0].value_type.kind is not TypeKind.VECTOR \
                or operands[0].value_type.scalar not in {ScalarKind.F32, ScalarKind.F64} \
                or expression.value_type != scalar_type(operands[0].value_type.scalar):
            _fail("dot_type", path, op)
    elif op == "construct":
        _verify_construct(expression, records, path)
    elif op == "helper_call":
        name = attrs.get("name")
        helper = helpers.get(str(name))
        if helper is None or helper.return_type != expression.value_type \
                or tuple(item.value_type for item in operands) != tuple(arg.value_type for arg in helper.arguments):
            _fail("helper_call", path, repr(name))
    else:
        _fail("expression_opcode", path, op)


def _verify_effect(
    effect: CallbackEffect,
    role: CallbackRole,
    environment: Mapping[str, CallbackType],
    helpers: Mapping[str, CallbackFunction],
    records: Mapping[str, CallbackRecord],
    manifest: CallbackModuleManifest,
    path: str,
) -> None:
    if effect.kind not in _ROLE_EFFECTS[role]:
        _fail("role_effect", path, f"{effect.kind.value} is illegal in {role.value}")
    fields = dict(effect.fields)
    if len(fields) != len(effect.fields):
        _fail("duplicate_effect_field", path, effect.kind.value)
    expected: dict[str, CallbackType]
    payload_type = record_type(manifest.payload_record)
    output_type = record_type(manifest.output_record)
    if effect.kind is EffectKind.AABB:
        expected = {"lower": VEC3F32, "upper": VEC3F32}
    elif effect.kind is EffectKind.TRACE_REQUEST:
        expected = {
            "origin": VEC3F32, "direction": VEC3F32, "tmin": F32,
            "tmax": F32, "payload": payload_type,
        }
    elif effect.kind is EffectKind.HIT:
        expected = {
            "t": F32, "hit_kind": U32,
            "attributes": tuple_type(*manifest.attribute_types),
        }
    elif effect.kind is EffectKind.NO_HIT:
        expected = {}
    elif effect.kind in {
        EffectKind.ACCEPT_CONTINUE, EffectKind.IGNORE, EffectKind.TERMINATE,
        EffectKind.PAYLOAD,
    }:
        expected = {"payload": payload_type}
    elif effect.kind is EffectKind.OUTPUT:
        expected = {"value": output_type}
    else:
        raise AssertionError(effect.kind)
    if set(fields) != set(expected):
        _fail("effect_fields", path, f"expected {tuple(expected)}, got {tuple(fields)}")
    for name, value_type in expected.items():
        _verify_expr(fields[name], environment, helpers, records, f"{path}.{name}")
        if fields[name].value_type != value_type:
            _fail("effect_field_type", f"{path}.{name}", f"expected {value_type.to_dict()}")


def _verify_function_signature(
    function: CallbackFunction,
    payload: CallbackRecord,
    output: CallbackRecord,
    records: Mapping[str, CallbackRecord],
    path: str,
    *,
    hit_value_type: CallbackType = HIT,
    allow_hit_read_only_views: bool = False,
) -> None:
    if not _identifier(function.name) or not function.arguments:
        _fail("function_shape", path, function.name)
    argument_types = tuple(item.value_type for item in function.arguments)
    if function.role is None:
        if function.return_type is None:
            _fail("helper_return_type", path, function.name)
        _verify_type(function.return_type, records, f"{path}.return_type", set())
        return
    if function.return_type is not None:
        _fail("role_return_annotation", path, "role functions return effects")
    payload_type = record_type(payload.name)
    allowed: dict[CallbackRole, tuple[CallbackType, ...] | None] = {
        CallbackRole.BOUNDS: None,
        CallbackRole.MAKE_RAY: None,
        CallbackRole.INTERSECTION: (RAY3F,),
        CallbackRole.ANY_HIT: (hit_value_type, payload_type),
        CallbackRole.CLOSEST_HIT: (hit_value_type, payload_type),
        CallbackRole.MISS: (RAY3F, payload_type),
        CallbackRole.FINALIZE: (payload_type,),
    }
    exact = allowed[function.role]
    if function.role is CallbackRole.BOUNDS:
        if len(argument_types) != 1 or argument_types[0].kind is not TypeKind.RECORD:
            _fail("bounds_signature", path, "bounds requires one primitive record")
    elif function.role is CallbackRole.MAKE_RAY:
        if not argument_types or argument_types[0] not in {U32, I32}:
            _fail("make_ray_signature", path, "first argument must be a launch index")
        if any(item.kind not in {TypeKind.SCALAR, TypeKind.RECORD, TypeKind.READ_ONLY_VIEW} for item in argument_types[1:]):
            _fail("make_ray_signature", path, "remaining inputs must be typed records/views/scalars")
    elif function.role is CallbackRole.INTERSECTION:
        if len(argument_types) != 2 or argument_types[0] != RAY3F \
                or argument_types[1].kind is not TypeKind.RECORD:
            _fail("intersection_signature", path, "intersection requires Ray3f and primitive record")
    elif exact is not None:
        if function.role in {CallbackRole.ANY_HIT, CallbackRole.CLOSEST_HIT} \
                and allow_hit_read_only_views:
            prefix = argument_types[:2]
            suffix = argument_types[2:]
            if prefix != exact or any(item.kind is not TypeKind.READ_ONLY_VIEW for item in suffix):
                _fail(
                    "role_signature",
                    path,
                    "hit roles require the exact hit/payload prefix and only trailing ReadOnlyView metadata",
                )
        elif argument_types != exact:
            _fail("role_signature", path, f"expected {[item.to_dict() for item in exact]}")


def _verify_records(records_seq: Sequence[CallbackRecord], records: Mapping[str, CallbackRecord]) -> None:
    for index, record in enumerate(records_seq):
        path = f"records[{index}]"
        if not _identifier(record.name) or not record.fields:
            _fail("record_shape", path, record.name)
        seen: set[str] = set()
        for field_index, item in enumerate(record.fields):
            if not _identifier(item.name) or item.name in seen:
                _fail("record_field", f"{path}.fields[{field_index}]", item.name)
            seen.add(item.name)
            _verify_type(item.value_type, records, f"{path}.fields[{field_index}].type", {record.name})
            if item.value_type.kind is TypeKind.READ_ONLY_VIEW:
                _fail("view_in_record", path, "views are capability arguments, not record fields")


def _verify_type(
    value_type: CallbackType,
    records: Mapping[str, CallbackRecord],
    path: str,
    visiting: set[str],
) -> None:
    if value_type.kind is TypeKind.RECORD:
        assert value_type.name is not None
        if value_type.name not in records:
            _fail("unknown_record_type", path, value_type.name)
        if value_type.name in visiting:
            _fail("recursive_record", path, value_type.name)
        nested = set(visiting); nested.add(value_type.name)
        for item in records[value_type.name].fields:
            _verify_type(item.value_type, records, path, nested)
    elif value_type.kind is TypeKind.READ_ONLY_VIEW:
        _verify_type(value_type.items[0], records, path, visiting)
        if value_type.items[0].kind is TypeKind.READ_ONLY_VIEW:
            _fail("nested_view", path, "nested views are rejected")
    elif value_type.kind is TypeKind.TUPLE:
        for item in value_type.items:
            _verify_type(item, records, path, visiting)
    elif value_type.kind is TypeKind.BUILTIN and value_type not in {RAY3F, HIT, TRIANGLE_HIT, AABB3F}:
        _fail("unknown_builtin_type", path, str(value_type.name))


def _verify_numeric_contract(contract: NumericContract) -> None:
    if not contract.strict_f32 or contract.implicit_fast_math \
            or contract.integer_overflow != "fail_closed" \
            or contract.nonfinite_input != "fail_closed" \
            or contract.nonfinite_effect != "fail_closed":
        _fail("numeric_contract", "manifest.numeric", "MVP requires strict fail-closed numeric semantics")


def _verify_resource_budget(budget: ResourceBudget) -> None:
    if not 1 <= budget.max_payload_u32_slots <= 32:
        _fail("payload_budget", "manifest.resources", str(budget.max_payload_u32_slots))
    if not 2 <= budget.max_attribute_u32_slots <= 8:
        _fail("attribute_budget", "manifest.resources", str(budget.max_attribute_u32_slots))
    if budget.max_trace_depth != 1 or budget.max_callable_depth != 0:
        _fail("trace_callable_budget", "manifest.resources", "MVP requires trace depth 1 and user callable depth 0")
    if not 0 <= budget.max_static_loop_trip_count <= MAX_STATIC_LOOP_TRIP_COUNT:
        _fail("loop_budget", "manifest.resources", str(budget.max_static_loop_trip_count))
    if not 0 <= budget.max_total_static_iterations <= 1_000_000:
        _fail("iteration_budget", "manifest.resources", str(budget.max_total_static_iterations))
    if not 0 <= budget.max_helper_call_depth <= MAX_HELPER_CALL_DEPTH:
        _fail("helper_budget", "manifest.resources", str(budget.max_helper_call_depth))


def _verify_geometry_contract(
    contract: GeometryContract,
    *,
    program_source_sha256: str,
    authorities: Mapping[str, GeometryProofAuthority] | None,
    allowed_admissions: frozenset[GeometryAdmission],
) -> None:
    if not contract.contract_name.strip():
        _fail("geometry_contract_name", "manifest.geometry", "contract name is required")
    if contract.admission not in allowed_admissions:
        _fail(
            "geometry_admission_not_allowed",
            "manifest.geometry.admission",
            contract.admission.value,
        )
    if contract.admission is GeometryAdmission.OPTIX_BUILTIN_SEMANTICS:
        if contract.proof_sha256 is not None or contract.target_f32_outward_rounding:
            _fail(
                "builtin_geometry_self_authority",
                "manifest.geometry",
                "OptiX built-in semantics carry neither a user proof nor custom-AABB rounding authority",
            )
        return
    if contract.admission is GeometryAdmission.TESTED_USER_GEOMETRY:
        if contract.proof_sha256 is not None:
            _fail(
                "untrusted_geometry_proof",
                "manifest.geometry.proof_sha256",
                "tested-user geometry cannot carry verified-contract authority",
            )
        return
    if not contract.target_f32_outward_rounding:
        _fail("verified_geometry_rounding", "manifest.geometry", "verified geometry requires target-f32 outward rounding")
    if contract.proof_sha256 is None or re.fullmatch(r"[0-9a-f]{64}", contract.proof_sha256) is None:
        _fail(
            "geometry_proof_digest",
            "manifest.geometry.proof_sha256",
            "verified geometry requires one lowercase SHA-256 proof identity",
        )
    if authorities is None or contract.contract_name not in authorities:
        _fail(
            "geometry_proof_authority_missing",
            "manifest.geometry",
            "a program declaration cannot mint verified-geometry authority",
        )
    authority = authorities[contract.contract_name]
    if authority.contract_name != contract.contract_name \
            or authority.callback_source_sha256 != program_source_sha256 \
            or authority.proof_sha256 != contract.proof_sha256 \
            or authority.target_f32_outward_rounding != contract.target_f32_outward_rounding:
        _fail(
            "geometry_proof_authority_mismatch",
            "manifest.geometry",
            "trusted authority must bind contract, exact callback source, proof and rounding policy",
        )


def _verify_constants(constants: Sequence[FrozenConstant], records: Mapping[str, CallbackRecord]) -> None:
    seen: set[str] = set()
    for index, item in enumerate(constants):
        path = f"manifest.constants[{index}]"
        if not _identifier(item.name) or item.name in seen:
            _fail("constant_name", path, item.name)
        seen.add(item.name)
        _verify_type(item.value_type, records, f"{path}.type", set())
        _verify_literal(item.value, item.value_type, path)


def _verify_literal(value: object, value_type: CallbackType, path: str) -> None:
    if value_type.kind is TypeKind.SCALAR:
        kind = value_type.scalar
        if kind is ScalarKind.BOOL:
            if not isinstance(value, bool): _fail("literal_type", path, "bool required")
        elif kind in {ScalarKind.I32, ScalarKind.U32, ScalarKind.I64, ScalarKind.U64}:
            if not isinstance(value, int) or isinstance(value, bool): _fail("literal_type", path, "int required")
            low, high = _integer_bounds(kind)
            if not low <= value <= high: _fail("literal_range", path, str(value))
        else:
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
                _fail("literal_finite", path, repr(value))
    elif value_type.kind in {TypeKind.VECTOR, TypeKind.TUPLE}:
        if not isinstance(value, tuple): _fail("literal_shape", path, "tuple required")
        types = (
            tuple(scalar_type(value_type.scalar) for _ in range(value_type.lanes))
            if value_type.kind is TypeKind.VECTOR else value_type.items
        )
        if len(value) != len(types): _fail("literal_shape", path, "tuple length mismatch")
        for index, (item, item_type) in enumerate(zip(value, types)):
            _verify_literal(item, item_type, f"{path}[{index}]")
    else:
        _fail("literal_complex_type", path, value_type.kind.value)


def _verify_construct(expression: CallbackExpr, records: Mapping[str, CallbackRecord], path: str) -> None:
    attrs = dict(expression.attributes)
    names = attrs.get("field_names")
    if not isinstance(names, tuple) or not all(isinstance(item, str) for item in names):
        _fail("construct_fields", path, "field_names tuple required")
    if len(names) != len(expression.operands):
        _fail("construct_arity", path, "constructor arity mismatch")
    if expression.value_type.kind is TypeKind.RECORD:
        record = records[expression.value_type.name or ""]
        if names != tuple(item.name for item in record.fields):
            _fail("construct_fields", path, record.name)
        expected = tuple(item.value_type for item in record.fields)
    elif expression.value_type.kind is TypeKind.VECTOR:
        if names != tuple(str(index) for index in range(expression.value_type.lanes)):
            _fail("construct_fields", path, "vector fields must be positional")
        expected = tuple(scalar_type(expression.value_type.scalar) for _ in names)
    elif expression.value_type.kind is TypeKind.TUPLE:
        if names != tuple(str(index) for index in range(len(expression.value_type.items))):
            _fail("construct_fields", path, "tuple fields must be positional")
        expected = expression.value_type.items
    else:
        _fail("construct_type", path, expression.value_type.kind.value)
    if tuple(item.value_type for item in expression.operands) != expected:
        _fail("construct_type", path, "constructor operand type mismatch")


def _field_type(base: CallbackType, name: str, records: Mapping[str, CallbackRecord], path: str) -> CallbackType:
    if base.kind is TypeKind.RECORD:
        field = records[base.name or ""].field(name)
        if field is None: _fail("unknown_record_field", path, name)
        return field.value_type
    builtins: Mapping[CallbackType, Mapping[str, CallbackType]] = {
        RAY3F: {"origin": VEC3F32, "direction": VEC3F32, "tmin": F32, "tmax": F32},
        HIT: {"t": F32, "hit_kind": U32},
        TRIANGLE_HIT: {
            "t": F32,
            "primitive_index": U32,
            "hit_kind": U32,
            "barycentrics": VEC2F32,
        },
        AABB3F: {"lower": VEC3F32, "upper": VEC3F32},
    }
    if base in builtins and name in builtins[base]:
        return builtins[base][name]
    if base.kind is TypeKind.VECTOR and name in {"x", "y", "z", "w"}:
        index = "xyzw".index(name)
        if index < base.lanes:
            return scalar_type(base.scalar)
    _fail("field_base", path, name)
    raise AssertionError


def _type_u32_slots(value_type: CallbackType, records: Mapping[str, CallbackRecord], visiting: set[str]) -> int:
    if value_type.kind is TypeKind.SCALAR:
        return 2 if value_type.scalar in {ScalarKind.I64, ScalarKind.U64, ScalarKind.F64} else 1
    if value_type.kind is TypeKind.VECTOR:
        return value_type.lanes * (2 if value_type.scalar is ScalarKind.F64 else 1)
    if value_type.kind is TypeKind.TUPLE:
        return sum(_type_u32_slots(item, records, visiting) for item in value_type.items)
    if value_type.kind is TypeKind.RECORD:
        name = value_type.name or ""
        if name in visiting: _fail("recursive_record", f"records.{name}", name)
        nested = set(visiting); nested.add(name)
        return sum(_type_u32_slots(item.value_type, records, nested) for item in records[name].fields)
    _fail("register_layout_type", "type", value_type.kind.value)
    raise AssertionError


def _helper_call_graph(functions: Sequence[CallbackFunction]) -> dict[str, set[str]]:
    helpers = {item.name for item in functions if item.is_helper}
    graph = {item.name: set() for item in functions}
    for function in functions:
        for statement in function.body:
            for expression in _statement_expressions(statement):
                for nested in _walk_expr(expression):
                    if nested.opcode == "helper_call":
                        target = nested.attribute("name")
                        if not isinstance(target, str) or target not in helpers:
                            _fail("unknown_helper", f"functions.{function.name}", repr(target))
                        graph[function.name].add(target)
    return graph


def _verify_helper_call_graph(graph: Mapping[str, set[str]], limit: int) -> int:
    visiting: set[str] = set()
    memo: dict[str, int] = {}
    def depth(name: str) -> int:
        if name in visiting: _fail("recursive_helper", f"functions.{name}", name)
        if name in memo: return memo[name]
        visiting.add(name)
        result = 0 if not graph[name] else 1 + max(depth(item) for item in graph[name])
        visiting.remove(name); memo[name] = result
        return result
    maximum = max((depth(name) for name in graph), default=0)
    if maximum > limit:
        _fail("helper_call_depth", "functions", f"{maximum} exceeds {limit}")
    return maximum


def _statement_expressions(statement: CallbackStatement) -> tuple[CallbackExpr, ...]:
    if isinstance(statement, (LetStatement, SetStatement, ReturnValueStatement)):
        return (statement.value,)
    if isinstance(statement, ReturnEffectStatement):
        return tuple(value for _, value in statement.effect.fields)
    if isinstance(statement, IfStatement):
        nested = [statement.condition]
        for item in statement.then_body + statement.else_body:
            nested.extend(_statement_expressions(item))
        return tuple(nested)
    if isinstance(statement, StaticForStatement):
        nested: list[CallbackExpr] = []
        for item in statement.body: nested.extend(_statement_expressions(item))
        return tuple(nested)
    raise AssertionError(type(statement))


def _walk_expr(expression: CallbackExpr):
    yield expression
    for item in expression.operands:
        yield from _walk_expr(item)


def _unique_named(items: Sequence[object], path: str) -> dict[str, object]:
    result: dict[str, object] = {}
    for index, item in enumerate(items):
        name = getattr(item, "name", None)
        if not _identifier(name) or name in result:
            _fail("unique_name", f"{path}[{index}]", repr(name))
        result[name] = item
    return result


def _numeric_shape(value_type: CallbackType) -> bool:
    return value_type.is_integer or value_type.is_float or (
        value_type.kind is TypeKind.VECTOR and value_type.scalar is not ScalarKind.BOOL
    )


def _float_shape(value_type: CallbackType) -> bool:
    return value_type.is_float or (
        value_type.kind is TypeKind.VECTOR and value_type.scalar in {ScalarKind.F32, ScalarKind.F64}
    )


def _comparable(value_type: CallbackType) -> bool:
    return value_type.kind is TypeKind.SCALAR


def _integer_bounds(kind: ScalarKind | None) -> tuple[int, int]:
    return {
        ScalarKind.I32: (-(1 << 31), (1 << 31) - 1),
        ScalarKind.U32: (0, (1 << 32) - 1),
        ScalarKind.I64: (-(1 << 63), (1 << 63) - 1),
        ScalarKind.U64: (0, (1 << 64) - 1),
    }[kind]


def _identifier(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", value) is not None


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _fail(code: str, path: str, message: str) -> None:
    raise CallbackVerificationError(code, path, message)
