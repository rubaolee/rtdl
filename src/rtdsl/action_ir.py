from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math
import struct
from typing import Mapping, Sequence, TypeAlias


ACTION_IR_SCHEMA_ID = "https://rtdl.dev/schemas/action-ir-v1.json"
ACTION_IR_SCHEMA_VERSION = "v1"
MAX_U64 = (1 << 64) - 1
MAX_STATIC_LOOP_TRIP_COUNT = 1024


class ActionScalarKind(str, Enum):
    BOOL = "bool"
    I32 = "i32"
    I64 = "i64"
    U32 = "u32"
    U64 = "u64"
    F32 = "f32"
    F64 = "f64"


class ActionEffect(str, Enum):
    FILTER = "filter"
    STATE_UPDATE = "state_update"
    KEYED_REDUCE = "keyed_reduce"
    BOUNDED_EMIT = "bounded_emit"
    TRAVERSAL_CONTROL = "traversal_control"


class OutputOrderKind(str, Enum):
    EVENT_ORDER = "event_order"
    CANONICAL_ORDER = "canonical_order"
    SET = "set"
    MULTISET = "multiset"


class OrderKeyRole(str, Enum):
    VALUE = "value"
    ITEM_ID = "item_id"


class DuplicatePolicy(str, Enum):
    PRESERVE_LOGICAL_MULTIPLICITY = "preserve_logical_multiplicity"
    STABLE_ITEM_ID = "stable_item_id"
    COLLAPSE_EXACT_ROWS = "collapse_exact_rows"


class StateScope(str, Enum):
    PER_QUERY = "per_query"
    PER_PARTITION = "per_partition"


class ReductionOperator(str, Enum):
    COUNT = "count"
    SUM = "sum"
    MIN = "min"
    MAX = "max"
    ANY = "any"


class OverflowPolicy(str, Enum):
    FAIL_CLOSED = "fail_closed"


class PhysicalDelivery(str, Enum):
    PROVEN_SINGLE = "proven_single"
    MAY_REPEAT = "may_repeat"


class DeliveryEnforcement(str, Enum):
    PROVEN_SINGLE = "proven_single"
    KEYED_DEDUP = "keyed_dedup"
    REJECT_FUSED = "reject_fused"


class TerminationProofKind(str, Enum):
    ABSORBING_RESULT = "absorbing_result"
    CAPACITY_COMPLETE = "capacity_complete"
    MONOTONE_BOUND = "monotone_bound"


class ExtentKind(str, Enum):
    QUERY_COUNT = "query_count"
    PARTITION_COUNT = "partition_count"
    PRIMITIVE_COUNT = "primitive_count"


@dataclass(frozen=True, order=True)
class ActionScalarType:
    kind: ActionScalarKind

    @property
    def is_integer(self) -> bool:
        return self.kind in {
            ActionScalarKind.I32,
            ActionScalarKind.I64,
            ActionScalarKind.U32,
            ActionScalarKind.U64,
        }

    @property
    def is_float(self) -> bool:
        return self.kind in {ActionScalarKind.F32, ActionScalarKind.F64}

    @property
    def is_numeric(self) -> bool:
        return self.is_integer or self.is_float

    @property
    def is_unsigned(self) -> bool:
        return self.kind in {ActionScalarKind.U32, ActionScalarKind.U64}

    def to_dict(self) -> dict[str, str]:
        return {"kind": "scalar", "scalar": self.kind.value}


BOOL = ActionScalarType(ActionScalarKind.BOOL)
I32 = ActionScalarType(ActionScalarKind.I32)
I64 = ActionScalarType(ActionScalarKind.I64)
U32 = ActionScalarType(ActionScalarKind.U32)
U64 = ActionScalarType(ActionScalarKind.U64)
F32 = ActionScalarType(ActionScalarKind.F32)
F64 = ActionScalarType(ActionScalarKind.F64)


_SCALAR_WIDTH_BITS = {
    ActionScalarKind.BOOL: 1,
    ActionScalarKind.I32: 32,
    ActionScalarKind.I64: 64,
    ActionScalarKind.U32: 32,
    ActionScalarKind.U64: 64,
    ActionScalarKind.F32: 32,
    ActionScalarKind.F64: 64,
}


@dataclass(frozen=True)
class ActionScalarLiteral:
    """An exact, typed scalar literal encoded without JSON float ambiguity."""

    value_type: ActionScalarType
    bits: int

    def __post_init__(self) -> None:
        width = _SCALAR_WIDTH_BITS[self.value_type.kind]
        if not isinstance(self.bits, int) or isinstance(self.bits, bool):
            raise TypeError("ActionScalarLiteral bits must be an integer")
        if self.bits < 0 or self.bits >= (1 << width):
            raise ValueError(f"literal bits must fit {width} bits")
        if self.value_type == BOOL and self.bits not in {0, 1}:
            raise ValueError("bool literal bits must be 0 or 1")
        if self.value_type.is_float and math.isnan(self.to_python()):
            raise ValueError("NaN is not admitted by Action IR v1")

    @classmethod
    def from_python(
        cls,
        value_type: ActionScalarType,
        value: bool | int | float,
    ) -> ActionScalarLiteral:
        kind = value_type.kind
        if kind is ActionScalarKind.BOOL:
            if not isinstance(value, bool):
                raise TypeError("bool literal requires a bool value")
            return cls(value_type, int(value))
        if value_type.is_integer:
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError("integer literal requires an int value")
            width = _SCALAR_WIDTH_BITS[kind]
            if value_type.is_unsigned:
                minimum, maximum = 0, (1 << width) - 1
            else:
                minimum, maximum = -(1 << (width - 1)), (1 << (width - 1)) - 1
            if value < minimum or value > maximum:
                raise ValueError(f"integer literal must be in [{minimum},{maximum}]")
            return cls(value_type, value & ((1 << width) - 1))
        if value_type.is_float:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError("float literal requires a numeric value")
            numeric = float(value)
            if math.isnan(numeric):
                raise ValueError("NaN is not admitted by Action IR v1")
            if kind is ActionScalarKind.F32:
                bits = struct.unpack(">I", struct.pack(">f", numeric))[0]
            else:
                bits = struct.unpack(">Q", struct.pack(">d", numeric))[0]
            return cls(value_type, bits)
        raise TypeError(f"unsupported scalar literal type: {kind.value}")

    def to_python(self) -> bool | int | float:
        kind = self.value_type.kind
        if kind is ActionScalarKind.BOOL:
            return bool(self.bits)
        if self.value_type.is_integer:
            width = _SCALAR_WIDTH_BITS[kind]
            if self.value_type.is_unsigned:
                return self.bits
            sign = 1 << (width - 1)
            return self.bits - (1 << width) if self.bits & sign else self.bits
        if kind is ActionScalarKind.F32:
            return struct.unpack(">f", struct.pack(">I", self.bits))[0]
        if kind is ActionScalarKind.F64:
            return struct.unpack(">d", struct.pack(">Q", self.bits))[0]
        raise TypeError(f"unsupported scalar literal type: {kind.value}")

    def to_dict(self) -> dict[str, object]:
        width = _SCALAR_WIDTH_BITS[self.value_type.kind]
        hex_digits = max(1, (width + 3) // 4)
        return {
            "kind": "scalar_literal",
            "type": self.value_type.to_dict(),
            "bits": f"0x{self.bits:0{hex_digits}x}",
        }


@dataclass(frozen=True)
class ActionTupleType:
    items: tuple[ActionScalarType, ...]

    def to_dict(self) -> dict[str, object]:
        return {"kind": "tuple", "items": [item.to_dict() for item in self.items]}


ActionValueType: TypeAlias = ActionScalarType | ActionTupleType


@dataclass(frozen=True)
class ActionField:
    name: str
    value_type: ActionValueType
    nonnegative: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "type": self.value_type.to_dict(),
            "nonnegative": self.nonnegative,
        }


@dataclass(frozen=True)
class ActionRecordType:
    name: str
    fields: tuple[ActionField, ...]

    def field(self, name: str) -> ActionField | None:
        return next((item for item in self.fields if item.name == name), None)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "fields": [item.to_dict() for item in self.fields],
        }


ActionAttributeValue: TypeAlias = (
    str
    | int
    | bool
    | None
    | tuple[str, ...]
    | tuple[int, ...]
    | ActionScalarLiteral
)


@dataclass(frozen=True)
class ActionAttribute:
    name: str
    value: ActionAttributeValue

    def __post_init__(self) -> None:
        scalar = self.value is None or isinstance(
            self.value, (str, bool, int, ActionScalarLiteral)
        )
        string_tuple = isinstance(self.value, tuple) and all(
            isinstance(item, str) for item in self.value
        )
        integer_tuple = isinstance(self.value, tuple) and all(
            isinstance(item, int) and not isinstance(item, bool) for item in self.value
        )
        if not (scalar or string_tuple or integer_tuple):
            raise TypeError("Action attributes must use the closed JSON-safe v1 value set")

    def to_dict(self) -> object:
        if isinstance(self.value, ActionScalarLiteral):
            return self.value.to_dict()
        if isinstance(self.value, tuple):
            return list(self.value)
        return self.value


def action_attributes(**values: ActionAttributeValue) -> tuple[ActionAttribute, ...]:
    return tuple(ActionAttribute(name, values[name]) for name in sorted(values))


@dataclass(frozen=True)
class ActionValue:
    name: str
    value_type: ActionValueType

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "type": self.value_type.to_dict()}


@dataclass(frozen=True)
class ActionOp:
    opcode: str
    inputs: tuple[str, ...] = ()
    outputs: tuple[ActionValue, ...] = ()
    attributes: tuple[ActionAttribute, ...] = ()

    def __post_init__(self) -> None:
        names = [item.name for item in self.attributes]
        if len(names) != len(set(names)):
            raise ValueError("ActionOp attributes must have unique names")

    def attribute(self, name: str) -> ActionAttributeValue | None:
        item = next((item for item in self.attributes if item.name == name), None)
        return None if item is None else item.value

    def to_dict(self) -> dict[str, object]:
        return {
            "opcode": self.opcode,
            "inputs": list(self.inputs),
            "outputs": [item.to_dict() for item in self.outputs],
            "attributes": {item.name: item.to_dict() for item in self.attributes},
        }


@dataclass(frozen=True)
class ActionBlock:
    label: str
    operations: tuple[ActionStatement, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "operations": [item.to_dict() for item in self.operations],
        }


@dataclass(frozen=True)
class ActionStaticLoop:
    trip_count: int
    body: ActionBlock

    def to_dict(self) -> dict[str, object]:
        return {
            "opcode": "for_static",
            "trip_count": self.trip_count,
            "body": self.body.to_dict(),
        }


ActionStatement: TypeAlias = ActionOp | ActionStaticLoop


@dataclass(frozen=True)
class CapacityConst:
    value: int

    def to_dict(self) -> dict[str, object]:
        return {"kind": "const", "value": self.value}


@dataclass(frozen=True)
class CapacityExtent:
    extent: ExtentKind

    def to_dict(self) -> dict[str, object]:
        return {"kind": "extent", "name": self.extent.value}


@dataclass(frozen=True)
class CapacityParam:
    name: str

    def to_dict(self) -> dict[str, object]:
        return {"kind": "param", "name": self.name}


@dataclass(frozen=True)
class CapacityAdd:
    left: CapacityExpr
    right: CapacityExpr

    def to_dict(self) -> dict[str, object]:
        return {"kind": "add", "left": self.left.to_dict(), "right": self.right.to_dict()}


@dataclass(frozen=True)
class CapacityMul:
    left: CapacityExpr
    right: CapacityExpr

    def to_dict(self) -> dict[str, object]:
        return {"kind": "mul", "left": self.left.to_dict(), "right": self.right.to_dict()}


CapacityExpr: TypeAlias = CapacityConst | CapacityExtent | CapacityParam | CapacityAdd | CapacityMul


@dataclass(frozen=True)
class ActionStateSpec:
    name: str
    value_type: ActionValueType
    scope: StateScope
    initial_value: ActionScalarLiteral
    key_fields: tuple[str, ...]
    merge_reduction: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "type": self.value_type.to_dict(),
            "scope": self.scope.value,
            "initial_value": self.initial_value.to_dict(),
            "key_fields": list(self.key_fields),
            "merge_reduction": self.merge_reduction,
        }


@dataclass(frozen=True)
class ActionReductionSpec:
    name: str
    key_fields: tuple[str, ...]
    value_type: ActionValueType
    operator: ReductionOperator
    identity: ActionScalarLiteral
    overflow_policy: OverflowPolicy = OverflowPolicy.FAIL_CLOSED

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "key_fields": list(self.key_fields),
            "value_type": self.value_type.to_dict(),
            "operator": self.operator.value,
            "identity": self.identity.to_dict(),
            "overflow_policy": self.overflow_policy.value,
        }


@dataclass(frozen=True)
class OrderKey:
    field: str
    ascending: bool = True
    role: OrderKeyRole = OrderKeyRole.VALUE

    def to_dict(self) -> dict[str, object]:
        return {
            "field": self.field,
            "ascending": self.ascending,
            "role": self.role.value,
        }


@dataclass(frozen=True)
class BoundedSelectionSpec:
    """Retain at most ``limit`` best rows inside each logical scope."""

    scope_key_fields: tuple[str, ...]
    scope_extent: ExtentKind
    limit: CapacityExpr
    order_keys: tuple[OrderKey, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "scope_key_fields": list(self.scope_key_fields),
            "scope_extent": self.scope_extent.value,
            "limit": self.limit.to_dict(),
            "order_keys": [item.to_dict() for item in self.order_keys],
        }


@dataclass(frozen=True)
class ActionEmitSpec:
    name: str
    record_type: ActionRecordType
    capacity: CapacityExpr
    order_kind: OutputOrderKind
    order_keys: tuple[OrderKey, ...] = ()
    duplicate_policy: DuplicatePolicy = DuplicatePolicy.PRESERVE_LOGICAL_MULTIPLICITY
    event_order_proof: str | None = None
    allow_empty_complete: bool = True
    selection: BoundedSelectionSpec | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "record_type": self.record_type.to_dict(),
            "capacity": self.capacity.to_dict(),
            "order_kind": self.order_kind.value,
            "order_keys": [item.to_dict() for item in self.order_keys],
            "selection": None if self.selection is None else self.selection.to_dict(),
            "duplicate_policy": self.duplicate_policy.value,
            "event_order_proof": self.event_order_proof,
            "allow_empty_complete": self.allow_empty_complete,
        }


@dataclass(frozen=True)
class LogicalEventContract:
    key_fields: tuple[str, ...]
    physical_delivery: PhysicalDelivery
    enforcement: DeliveryEnforcement
    proof_reference: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "semantics": "exactly_once_logical_delivery",
            "key_fields": list(self.key_fields),
            "physical_delivery": self.physical_delivery.value,
            "enforcement": self.enforcement.value,
            "proof_reference": self.proof_reference,
        }


@dataclass(frozen=True)
class TerminationProofSpec:
    name: str
    kind: TerminationProofKind
    certificate: str
    state_name: str | None = None
    order_independent: bool = False
    unseen_cannot_improve: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "kind": self.kind.value,
            "certificate": self.certificate,
            "state_name": self.state_name,
            "order_independent": self.order_independent,
            "unseen_cannot_improve": self.unseen_cannot_improve,
        }


@dataclass(frozen=True)
class NumericContract:
    strict_cross_placement_equality: bool = True
    reject_nan: bool = True
    normalize_signed_zero: bool = True
    allow_infinity: bool = False

    def to_dict(self) -> dict[str, bool]:
        return {
            "strict_cross_placement_equality": self.strict_cross_placement_equality,
            "reject_nan": self.reject_nan,
            "normalize_signed_zero": self.normalize_signed_zero,
            "allow_infinity": self.allow_infinity,
        }


@dataclass(frozen=True)
class ActionEffectSet:
    effects: tuple[ActionEffect, ...]

    def __post_init__(self) -> None:
        canonical = tuple(sorted(set(self.effects), key=lambda item: item.value))
        object.__setattr__(self, "effects", canonical)

    def to_dict(self) -> list[str]:
        return [item.value for item in self.effects]


@dataclass(frozen=True)
class ActionSpec:
    name: str
    event_type: ActionRecordType
    parameter_type: ActionRecordType
    states: tuple[ActionStateSpec, ...]
    reductions: tuple[ActionReductionSpec, ...]
    emits: tuple[ActionEmitSpec, ...]
    termination_proofs: tuple[TerminationProofSpec, ...]
    blocks: tuple[ActionBlock, ...]
    declared_effects: ActionEffectSet
    logical_event: LogicalEventContract
    numeric_contract: NumericContract = field(default_factory=NumericContract)
    overflow_policy: OverflowPolicy = OverflowPolicy.FAIL_CLOSED
    diagnostic_label: str | None = None

    def semantic_dict(self) -> dict[str, object]:
        return {
            "$schema": ACTION_IR_SCHEMA_ID,
            "schema_version": ACTION_IR_SCHEMA_VERSION,
            "event_type": self.event_type.to_dict(),
            "parameter_type": self.parameter_type.to_dict(),
            "states": [item.to_dict() for item in self.states],
            "reductions": [item.to_dict() for item in self.reductions],
            "emits": [item.to_dict() for item in self.emits],
            "termination_proofs": [item.to_dict() for item in self.termination_proofs],
            "blocks": [item.to_dict() for item in self.blocks],
            "declared_effects": self.declared_effects.to_dict(),
            "logical_event": self.logical_event.to_dict(),
            "numeric_contract": self.numeric_contract.to_dict(),
            "overflow_policy": self.overflow_policy.value,
        }

    def to_dict(self) -> dict[str, object]:
        payload = self.semantic_dict()
        payload["name"] = self.name
        payload["diagnostic_label"] = self.diagnostic_label
        return payload

    def canonical_json(self, *, include_diagnostic_identity: bool = True) -> str:
        payload = self.to_dict() if include_diagnostic_identity else self.semantic_dict()
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)

    @property
    def semantic_digest(self) -> str:
        return hashlib.sha256(
            self.canonical_json(include_diagnostic_identity=False).encode("utf-8")
        ).hexdigest()

    @property
    def source_digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class VerificationIssue:
    code: str
    path: str
    message: str


class ActionVerificationError(ValueError):
    def __init__(self, issues: Sequence[VerificationIssue]) -> None:
        self.issues = tuple(issues)
        detail = "; ".join(f"{item.code}@{item.path}: {item.message}" for item in self.issues)
        super().__init__(f"Action IR verification failed: {detail}")


@dataclass(frozen=True)
class VerifiedActionContract:
    schema_version: str
    semantic_digest: str
    source_digest: str
    inferred_effects: tuple[ActionEffect, ...]
    placement_obligations: tuple[str, ...]
    name_is_diagnostic_only: bool = True
    verified: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "semantic_digest": self.semantic_digest,
            "source_digest": self.source_digest,
            "inferred_effects": [item.value for item in self.inferred_effects],
            "placement_obligations": list(self.placement_obligations),
            "name_is_diagnostic_only": self.name_is_diagnostic_only,
            "verified": self.verified,
        }


_EFFECT_BY_OPCODE = {
    "filter": ActionEffect.FILTER,
    "accept": ActionEffect.FILTER,
    "ignore": ActionEffect.FILTER,
    "state_write": ActionEffect.STATE_UPDATE,
    "reduce": ActionEffect.KEYED_REDUCE,
    "emit": ActionEffect.BOUNDED_EMIT,
    "terminate": ActionEffect.TRAVERSAL_CONTROL,
}

_PURE_OPCODES = {
    "load_event",
    "load_param",
    "const",
    "compare",
    "bool_and",
    "bool_or",
    "bool_not",
    "add",
    "sub",
    "mul",
    "min",
    "max",
    "select",
    "cast",
    "state_read",
}

_ILLEGAL_OPCODE_CODES = {
    "pointer_load": "raw_pointer_forbidden",
    "pointer_store": "raw_pointer_forbidden",
    "global_store": "global_mutation_forbidden",
    "recursive_call": "recursion_forbidden",
    "while": "unbounded_loop_forbidden",
    "atomic_add": "undeclared_atomic_forbidden",
    "backend_intrinsic": "backend_intrinsic_forbidden",
    "dynamic_alloc": "dynamic_allocation_forbidden",
    "io": "io_forbidden",
    "raise": "exception_forbidden",
    "for_static": "structured_loop_required",
}

_ALLOWED_ATTRIBUTES_BY_OPCODE = {
    "load_event": {"field"},
    "load_param": {"field"},
    "const": {"literal"},
    "compare": {"predicate"},
    "bool_and": set(),
    "bool_or": set(),
    "bool_not": set(),
    "add": set(),
    "sub": set(),
    "mul": set(),
    "min": set(),
    "max": set(),
    "select": set(),
    "cast": set(),
    "state_read": {"state"},
    "state_write": {"state"},
    "filter": set(),
    "accept": set(),
    "ignore": set(),
    "reduce": {"reduction"},
    "emit": {"emit"},
    "terminate": {"proof"},
}

_SAFE_CASTS = {
    (ActionScalarKind.I32, ActionScalarKind.I64),
    (ActionScalarKind.U32, ActionScalarKind.U64),
    (ActionScalarKind.F32, ActionScalarKind.F64),
}

_NON_IDEMPOTENT_EFFECTS = {
    ActionEffect.STATE_UPDATE,
    ActionEffect.KEYED_REDUCE,
    ActionEffect.BOUNDED_EMIT,
    ActionEffect.TRAVERSAL_CONTROL,
}


def infer_action_effects(blocks: Sequence[ActionBlock]) -> tuple[ActionEffect, ...]:
    inferred: set[ActionEffect] = set()

    def visit(block: ActionBlock) -> None:
        for statement in block.operations:
            if isinstance(statement, ActionStaticLoop):
                visit(statement.body)
            elif statement.opcode in _EFFECT_BY_OPCODE:
                inferred.add(_EFFECT_BY_OPCODE[statement.opcode])

    for block in blocks:
        visit(block)
    return tuple(sorted(inferred, key=lambda item: item.value))


class ActionBuilder:
    def __init__(
        self,
        *,
        name: str,
        event_type: ActionRecordType,
        parameter_type: ActionRecordType,
        logical_event: LogicalEventContract,
        numeric_contract: NumericContract | None = None,
    ) -> None:
        self._require_type("name", name, str)
        if not name:
            self._fail_input(
                "invalid_builder_name",
                "name",
                "ActionBuilder name must be a nonempty diagnostic string",
            )
        self._require_type("event_type", event_type, ActionRecordType)
        self._require_type("parameter_type", parameter_type, ActionRecordType)
        self._require_type("logical_event", logical_event, LogicalEventContract)
        if numeric_contract is not None:
            self._require_type("numeric_contract", numeric_contract, NumericContract)
        self.name = name
        self.event_type = event_type
        self.parameter_type = parameter_type
        self.logical_event = logical_event
        self.numeric_contract = numeric_contract or NumericContract()
        self.states: list[ActionStateSpec] = []
        self.reductions: list[ActionReductionSpec] = []
        self.emits: list[ActionEmitSpec] = []
        self.termination_proofs: list[TerminationProofSpec] = []
        self.blocks: list[ActionBlock] = []

    def add_state(self, spec: ActionStateSpec) -> ActionBuilder:
        self._require_type("states", spec, ActionStateSpec)
        self.states.append(spec)
        return self

    def add_reduction(self, spec: ActionReductionSpec) -> ActionBuilder:
        self._require_type("reductions", spec, ActionReductionSpec)
        self.reductions.append(spec)
        return self

    def add_emit(self, spec: ActionEmitSpec) -> ActionBuilder:
        self._require_type("emits", spec, ActionEmitSpec)
        self.emits.append(spec)
        return self

    def add_termination_proof(self, spec: TerminationProofSpec) -> ActionBuilder:
        self._require_type("termination_proofs", spec, TerminationProofSpec)
        self.termination_proofs.append(spec)
        return self

    def add_block(self, block: ActionBlock) -> ActionBuilder:
        self._require_type("blocks", block, ActionBlock)
        self.blocks.append(block)
        return self

    def build(self, *, declared_effects: Sequence[ActionEffect] | None = None) -> ActionSpec:
        try:
            if declared_effects is None:
                effects = infer_action_effects(self.blocks)
            else:
                if isinstance(declared_effects, (str, bytes)) or not isinstance(
                    declared_effects, Sequence
                ):
                    self._fail_input(
                        "invalid_builder_declared_effects",
                        "declared_effects",
                        "declared effects must be a sequence of ActionEffect values",
                    )
                effects = tuple(declared_effects)
                if any(not isinstance(effect, ActionEffect) for effect in effects):
                    self._fail_input(
                        "invalid_builder_declared_effect",
                        "declared_effects",
                        "every declared effect must be a closed ActionEffect value",
                    )
            spec = ActionSpec(
                name=self.name,
                event_type=self.event_type,
                parameter_type=self.parameter_type,
                states=tuple(self.states),
                reductions=tuple(self.reductions),
                emits=tuple(self.emits),
                termination_proofs=tuple(self.termination_proofs),
                blocks=tuple(self.blocks),
                declared_effects=ActionEffectSet(tuple(effects)),
                logical_event=self.logical_event,
                numeric_contract=self.numeric_contract,
            )
            # Exercise the complete direct-builder object shape here so dynamic
            # Python type mistakes cannot escape later as raw attribute/index
            # errors. Semantic legality remains the verifier's responsibility.
            spec.semantic_dict()
            return spec
        except ActionVerificationError:
            raise
        except (AttributeError, IndexError, KeyError, TypeError, ValueError, OverflowError) as exc:
            self._fail_input(
                "malformed_builder_input",
                "builder",
                f"{type(exc).__name__}: {exc}",
            )

    @staticmethod
    def _fail_input(code: str, path: str, message: str) -> None:
        raise ActionVerificationError((VerificationIssue(code, path, message),))

    @classmethod
    def _require_type(cls, path: str, value: object, expected: type[object]) -> None:
        if not isinstance(value, expected):
            cls._fail_input(
                "invalid_builder_argument",
                path,
                f"expected {expected.__name__}, got {type(value).__name__}",
            )


def canonical_float32_key(value: float, *, allow_infinity: bool = False) -> int:
    if math.isnan(value):
        raise ValueError("NaN is not admitted by the canonical float32 key")
    if math.isinf(value) and not allow_infinity:
        raise ValueError("infinity requires explicit admission")
    normalized = 0.0 if value == 0.0 else value
    bits = struct.unpack(">I", struct.pack(">f", normalized))[0]
    return (~bits) & 0xFFFFFFFF if bits & 0x80000000 else bits ^ 0x80000000


def canonical_float64_key(value: float, *, allow_infinity: bool = False) -> int:
    if math.isnan(value):
        raise ValueError("NaN is not admitted by the canonical float64 key")
    if math.isinf(value) and not allow_infinity:
        raise ValueError("infinity requires explicit admission")
    normalized = 0.0 if value == 0.0 else value
    bits = struct.unpack(">Q", struct.pack(">d", normalized))[0]
    return (
        (~bits) & 0xFFFFFFFFFFFFFFFF
        if bits & 0x8000000000000000
        else bits ^ 0x8000000000000000
    )


def evaluate_capacity(
    expression: CapacityExpr,
    *,
    extents: Mapping[str | ExtentKind, int],
    parameters: Mapping[str, int],
    allocator_limit: int = MAX_U64,
) -> int:
    if allocator_limit < 0 or allocator_limit > MAX_U64:
        raise ValueError("allocator_limit must be an unsigned 64-bit value")

    normalized_extents = {
        key.value if isinstance(key, ExtentKind) else key: value
        for key, value in extents.items()
    }

    def checked(value: int, label: str) -> int:
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"{label} must be an integer")
        if value < 0:
            raise ValueError(f"{label} must be nonnegative")
        if value > MAX_U64:
            raise OverflowError(f"{label} exceeds unsigned 64-bit capacity")
        return value

    def visit(node: CapacityExpr) -> int:
        if isinstance(node, CapacityConst):
            return checked(node.value, "capacity constant")
        if isinstance(node, CapacityExtent):
            name = node.extent.value
            if name not in normalized_extents:
                raise KeyError(f"missing capacity extent: {name}")
            return checked(normalized_extents[name], f"capacity extent {name}")
        if isinstance(node, CapacityParam):
            if node.name not in parameters:
                raise KeyError(f"missing capacity parameter: {node.name}")
            return checked(parameters[node.name], f"capacity parameter {node.name}")
        if isinstance(node, CapacityAdd):
            left = visit(node.left)
            right = visit(node.right)
            if left > MAX_U64 - right:
                raise OverflowError("capacity addition exceeds unsigned 64-bit range")
            return left + right
        if isinstance(node, CapacityMul):
            left = visit(node.left)
            right = visit(node.right)
            if left and right > MAX_U64 // left:
                raise OverflowError("capacity multiplication exceeds unsigned 64-bit range")
            return left * right
        raise TypeError(f"unsupported capacity expression: {type(node).__name__}")

    value = visit(expression)
    if value > allocator_limit:
        raise OverflowError("capacity exceeds allocator/platform limit")
    return value


def verify_action_spec(spec: ActionSpec) -> VerifiedActionContract:
    issues: list[VerificationIssue] = []

    def issue(code: str, path: str, message: str) -> None:
        issues.append(VerificationIssue(code=code, path=path, message=message))

    if not spec.name:
        issue("missing_diagnostic_name", "name", "ActionSpec name must be nonempty")
    _verify_record(spec.event_type, "event_type", issues)
    _verify_record(spec.parameter_type, "parameter_type", issues)

    states = _unique_by_name(spec.states, "states", issues)
    reductions = _unique_by_name(spec.reductions, "reductions", issues)
    emits = _unique_by_name(spec.emits, "emits", issues)
    proofs = _unique_by_name(spec.termination_proofs, "termination_proofs", issues)

    if not spec.blocks:
        issue("missing_block", "blocks", "an ActionSpec requires at least one block")
    for state in spec.states:
        _verify_value_type(
            state.value_type,
            f"states.{state.name}.value_type",
            issues,
        )
        _verify_scalar_literal(
            state.initial_value,
            expected_type=state.value_type,
            numeric_contract=spec.numeric_contract,
            path=f"states.{state.name}.initial_value",
            issue=issue,
        )
        if not state.key_fields:
            issue(
                "scoped_state_missing_key",
                f"states.{state.name}.key_fields",
                "query/partition state requires explicit app-neutral key fields",
            )
        if len(state.key_fields) != len(set(state.key_fields)):
            issue(
                "duplicate_state_key",
                f"states.{state.name}.key_fields",
                "state key fields must be unique",
            )
        for key in state.key_fields:
            event_field = spec.event_type.field(key)
            parameter_field = spec.parameter_type.field(key)
            if event_field is None and parameter_field is None:
                issue(
                    "unknown_state_key",
                    f"states.{state.name}.key_fields",
                    f"unknown key field {key!r}",
                )
            elif event_field is not None and parameter_field is not None:
                issue(
                    "ambiguous_state_key",
                    f"states.{state.name}.key_fields",
                    f"key field {key!r} exists in both event and parameter records",
                )
            else:
                field = event_field or parameter_field
                if (
                    field is not None
                    and (
                        not isinstance(field.value_type, ActionScalarType)
                        or not field.value_type.is_integer
                    )
                ):
                    issue(
                        "unstable_state_key_type",
                        f"states.{state.name}.key_fields",
                        f"key field {key!r} must be an integer scalar",
                    )
        if state.scope is StateScope.PER_PARTITION and not state.merge_reduction:
            issue(
                "partition_state_missing_merge",
                f"states.{state.name}",
                "per-partition state requires an associative merge reduction",
            )
        if state.merge_reduction and state.merge_reduction not in reductions:
            issue(
                "unknown_state_merge_reduction",
                f"states.{state.name}",
                f"unknown reduction {state.merge_reduction!r}",
            )
        elif state.merge_reduction:
            merge = reductions[state.merge_reduction]
            if merge.value_type != state.value_type:
                issue(
                    "state_merge_type_mismatch",
                    f"states.{state.name}.merge_reduction",
                    "state and merge reduction value types must match",
                )

    for reduction in spec.reductions:
        _verify_value_type(
            reduction.value_type,
            f"reductions.{reduction.name}.value_type",
            issues,
        )
        _verify_scalar_literal(
            reduction.identity,
            expected_type=reduction.value_type,
            numeric_contract=spec.numeric_contract,
            path=f"reductions.{reduction.name}.identity",
            issue=issue,
        )
        for key in reduction.key_fields:
            event_field = spec.event_type.field(key)
            parameter_field = spec.parameter_type.field(key)
            if event_field is None and parameter_field is None:
                issue(
                    "unknown_reduction_key",
                    f"reductions.{reduction.name}.key_fields",
                    f"unknown key field {key!r}",
                )
            elif event_field is not None and parameter_field is not None:
                issue(
                    "ambiguous_reduction_key",
                    f"reductions.{reduction.name}.key_fields",
                    f"key field {key!r} exists in both event and parameter records",
                )
        if reduction.overflow_policy is not OverflowPolicy.FAIL_CLOSED:
            issue(
                "non_fail_closed_reduction",
                f"reductions.{reduction.name}.overflow_policy",
                "v1 reductions require fail-closed overflow",
            )
        if (
            spec.numeric_contract.strict_cross_placement_equality
            and reduction.operator is ReductionOperator.SUM
            and _is_float_type(reduction.value_type)
        ):
            issue(
                "float_reassociation_not_exact",
                f"reductions.{reduction.name}",
                "floating sum is not admitted by strict cross-placement v1",
            )
        if len(reduction.key_fields) != len(set(reduction.key_fields)):
            issue(
                "duplicate_reduction_key",
                f"reductions.{reduction.name}.key_fields",
                "reduction keys must be unique",
            )
        if isinstance(reduction.identity, ActionScalarLiteral):
            identity = reduction.identity.to_python()
            if reduction.operator is ReductionOperator.COUNT:
                if (
                    not isinstance(reduction.value_type, ActionScalarType)
                    or not reduction.value_type.is_unsigned
                ):
                    issue(
                        "count_requires_unsigned_integer",
                        f"reductions.{reduction.name}",
                        "count reduction requires an unsigned integer value type",
                    )
                if identity != 0:
                    issue(
                        "count_identity_not_zero",
                        f"reductions.{reduction.name}.identity",
                        "count identity must be zero",
                    )
            elif reduction.operator is ReductionOperator.SUM:
                if not _is_numeric_type(reduction.value_type):
                    issue(
                        "sum_requires_numeric_type",
                        f"reductions.{reduction.name}",
                        "sum reduction requires a numeric scalar value type",
                    )
                if identity != 0:
                    issue(
                        "sum_identity_not_zero",
                        f"reductions.{reduction.name}.identity",
                        "sum identity must be zero",
                    )
            elif reduction.operator is ReductionOperator.ANY:
                if reduction.value_type != BOOL:
                    issue(
                        "any_requires_bool",
                        f"reductions.{reduction.name}",
                        "any reduction requires bool values",
                    )
                if identity is not False:
                    issue(
                        "any_identity_not_false",
                        f"reductions.{reduction.name}.identity",
                        "any identity must be false",
                    )
            elif reduction.operator in {ReductionOperator.MIN, ReductionOperator.MAX}:
                if not _is_numeric_type(reduction.value_type):
                    issue(
                        "minmax_requires_numeric_type",
                        f"reductions.{reduction.name}",
                        "min/max reduction requires a numeric scalar value type",
                    )

    for emit in spec.emits:
        _verify_record(emit.record_type, f"emits.{emit.name}.record_type", issues)
        _verify_capacity_expression(emit.capacity, spec.parameter_type, f"emits.{emit.name}.capacity", issues)
        if not isinstance(emit.duplicate_policy, DuplicatePolicy):
            issue(
                "invalid_duplicate_policy",
                f"emits.{emit.name}.duplicate_policy",
                "duplicate policy must be a closed DuplicatePolicy value",
            )
        field_names = {field.name for field in emit.record_type.fields}
        order_key_names = [key.field for key in emit.order_keys]
        if len(order_key_names) != len(set(order_key_names)):
            issue(
                "duplicate_order_key",
                f"emits.{emit.name}.order_keys",
                "canonical order keys must be unique",
            )
        if emit.order_kind is OutputOrderKind.EVENT_ORDER and not emit.event_order_proof:
            issue(
                "event_order_unproven",
                f"emits.{emit.name}.order_kind",
                "event_order requires a stable traversal-order proof",
            )
        if emit.order_kind is OutputOrderKind.CANONICAL_ORDER and not emit.order_keys:
            issue(
                "canonical_order_missing_keys",
                f"emits.{emit.name}.order_keys",
                "canonical_order requires at least one order key",
            )
        if emit.order_kind is OutputOrderKind.CANONICAL_ORDER and set(order_key_names) != field_names:
            issue(
                "canonical_order_not_total",
                f"emits.{emit.name}.order_keys",
                "strict v1 canonical order must cover every output field exactly once",
            )
        if emit.order_kind in {OutputOrderKind.SET, OutputOrderKind.MULTISET} and emit.order_keys:
            issue(
                "unordered_output_has_order_keys",
                f"emits.{emit.name}.order_keys",
                "set/multiset output must not claim observable row order",
            )
        for key in emit.order_keys:
            if not isinstance(key.role, OrderKeyRole):
                issue(
                    "invalid_order_key_role",
                    f"emits.{emit.name}.order_keys",
                    "order-key role must be a closed OrderKeyRole value",
                )
                continue
            field = emit.record_type.field(key.field)
            if key.field not in field_names or field is None:
                issue(
                    "unknown_order_key",
                    f"emits.{emit.name}.order_keys",
                    f"unknown output field {key.field!r}",
                )
            elif _is_float_type(field.value_type):
                if not spec.numeric_contract.reject_nan:
                    issue(
                        "float_order_nan_policy",
                        f"emits.{emit.name}.order_keys",
                        "float order requires NaN rejection",
                    )
                if not spec.numeric_contract.normalize_signed_zero:
                    issue(
                        "float_order_zero_policy",
                        f"emits.{emit.name}.order_keys",
                        "float order requires signed-zero normalization",
                    )
                key_index = order_key_names.index(key.field)
                later_fields = [
                    emit.record_type.field(name) for name in order_key_names[key_index + 1 :]
                ]
                if not any(
                    later is not None
                    and isinstance(later.value_type, ActionScalarType)
                    and later.value_type.is_integer
                    and emit.order_keys[key_index + 1 + offset].role is OrderKeyRole.ITEM_ID
                    for offset, later in enumerate(later_fields)
                ):
                    issue(
                        "float_order_missing_integer_tiebreak",
                        f"emits.{emit.name}.order_keys",
                        "a canonical float key requires a later integer item-id tie-break",
                    )
            if key.role is OrderKeyRole.ITEM_ID and field is not None:
                if (
                    not isinstance(field.value_type, ActionScalarType)
                    or not field.value_type.is_integer
                ):
                    issue(
                        "item_id_order_key_not_integer",
                        f"emits.{emit.name}.order_keys",
                        "item-id order keys must have integer scalar type",
                    )

        selection = emit.selection
        if selection is not None:
            selection_path = f"emits.{emit.name}.selection"
            _verify_capacity_expression(
                selection.limit,
                spec.parameter_type,
                f"{selection_path}.limit",
                issues,
            )
            if not isinstance(selection.limit, (CapacityConst, CapacityParam)):
                issue(
                    "selection_limit_not_scalar",
                    f"{selection_path}.limit",
                    "v1 per-scope selection limit must be a constant or nonnegative integer parameter",
                )
            if not isinstance(selection.scope_extent, ExtentKind):
                issue(
                    "invalid_selection_scope_extent",
                    f"{selection_path}.scope_extent",
                    "selection scope extent must be a closed ExtentKind value",
                )
            if not selection.scope_key_fields:
                issue(
                    "selection_scope_missing_key",
                    f"{selection_path}.scope_key_fields",
                    "bounded selection requires at least one scope key",
                )
            if len(selection.scope_key_fields) != len(set(selection.scope_key_fields)):
                issue(
                    "duplicate_selection_scope_key",
                    f"{selection_path}.scope_key_fields",
                    "selection scope keys must be unique",
                )
            for field_name in selection.scope_key_fields:
                field = emit.record_type.field(field_name)
                if field is None:
                    issue(
                        "unknown_selection_scope_key",
                        f"{selection_path}.scope_key_fields",
                        f"unknown output field {field_name!r}",
                    )
                elif (
                    not isinstance(field.value_type, ActionScalarType)
                    or not field.value_type.is_integer
                ):
                    issue(
                        "unstable_selection_scope_key_type",
                        f"{selection_path}.scope_key_fields",
                        "selection scope keys must be integer scalar fields",
                    )

            selection_key_names = [key.field for key in selection.order_keys]
            if not selection.order_keys:
                issue(
                    "selection_order_missing_keys",
                    f"{selection_path}.order_keys",
                    "bounded selection requires a deterministic rank order",
                )
            if len(selection_key_names) != len(set(selection_key_names)):
                issue(
                    "duplicate_selection_order_key",
                    f"{selection_path}.order_keys",
                    "selection order keys must be unique",
                )
            expected_rank_fields = field_names - set(selection.scope_key_fields)
            if set(selection_key_names) != expected_rank_fields:
                issue(
                    "selection_order_not_total_within_scope",
                    f"{selection_path}.order_keys",
                    "selection rank order must cover every non-scope output field exactly once",
                )
            expected_output_order = tuple(selection.scope_key_fields) + tuple(
                selection_key_names
            )
            if tuple(order_key_names) != expected_output_order:
                issue(
                    "selection_output_order_mismatch",
                    f"{selection_path}.order_keys",
                    "canonical output order must be scope keys followed by selection rank keys",
                )
            for key_index, key in enumerate(selection.order_keys):
                if not isinstance(key.role, OrderKeyRole):
                    issue(
                        "invalid_selection_order_key_role",
                        f"{selection_path}.order_keys",
                        "selection order-key role must be a closed OrderKeyRole value",
                    )
                    continue
                field = emit.record_type.field(key.field)
                if field is None:
                    issue(
                        "unknown_selection_order_key",
                        f"{selection_path}.order_keys",
                        f"unknown output field {key.field!r}",
                    )
                    continue
                if _is_float_type(field.value_type):
                    later = selection.order_keys[key_index + 1 :]
                    if not any(
                        later_key.role is OrderKeyRole.ITEM_ID
                        and (
                            (later_field := emit.record_type.field(later_key.field))
                            is not None
                        )
                        and isinstance(later_field.value_type, ActionScalarType)
                        and later_field.value_type.is_integer
                        for later_key in later
                    ):
                        issue(
                            "selection_float_order_missing_integer_tiebreak",
                            f"{selection_path}.order_keys",
                            "a float selection key requires a later integer item-id tie-break",
                        )
                if key.role is OrderKeyRole.ITEM_ID and (
                    not isinstance(field.value_type, ActionScalarType)
                    or not field.value_type.is_integer
                ):
                    issue(
                        "selection_item_id_order_key_not_integer",
                        f"{selection_path}.order_keys",
                        "selection item-id order keys must have integer scalar type",
                    )

            expected_capacity = CapacityMul(
                CapacityExtent(selection.scope_extent), selection.limit
            )
            if emit.capacity != expected_capacity:
                issue(
                    "selection_capacity_not_scope_times_limit",
                    f"emits.{emit.name}.capacity",
                    "v1 selected emit capacity must be canonical scope_extent * per-scope limit",
                )

    for proof in spec.termination_proofs:
        if not proof.certificate:
            issue(
                "termination_proof_missing_certificate",
                f"termination_proofs.{proof.name}",
                "termination proof requires a generic certificate reference",
            )
        if proof.kind is TerminationProofKind.MONOTONE_BOUND:
            if proof.state_name is None or proof.state_name not in states:
                issue(
                    "monotone_bound_missing_state",
                    f"termination_proofs.{proof.name}",
                    "monotone bound requires an existing per-query state",
                )
            elif states[proof.state_name].scope is not StateScope.PER_QUERY:
                issue(
                    "monotone_bound_not_query_local",
                    f"termination_proofs.{proof.name}",
                    "v1 monotone-bound termination is query-local only",
                )
        if proof.kind is TerminationProofKind.CAPACITY_COMPLETE and (
            not proof.order_independent or not proof.unseen_cannot_improve
        ):
            issue(
                "capacity_complete_not_proven",
                f"termination_proofs.{proof.name}",
                "capacity complete requires order independence and proof that unseen rows cannot improve output",
            )

    seen_block_labels: set[str] = set()

    def visit_block(
        block: ActionBlock,
        *,
        path: str,
        values: dict[str, ActionValueType],
        iteration_product: int,
    ) -> None:
        if not _is_ir_identifier(block.label):
            issue("invalid_block_label", f"{path}.label", "block labels must be ASCII IR identifiers")
        if block.label in seen_block_labels:
            issue("duplicate_block_label", f"{path}.label", "block labels must be unique")
        seen_block_labels.add(block.label)
        for statement_index, statement in enumerate(block.operations):
            statement_path = f"{path}.operations[{statement_index}]"
            if isinstance(statement, ActionStaticLoop):
                trip_count = statement.trip_count
                if (
                    not isinstance(trip_count, int)
                    or isinstance(trip_count, bool)
                    or trip_count < 0
                    or trip_count > MAX_STATIC_LOOP_TRIP_COUNT
                ):
                    issue(
                        "invalid_static_loop_bound",
                        statement_path,
                        f"trip_count must be in [0,{MAX_STATIC_LOOP_TRIP_COUNT}]",
                    )
                    nested_product = iteration_product
                else:
                    nested_product = iteration_product * trip_count
                    if nested_product > MAX_STATIC_LOOP_TRIP_COUNT:
                        issue(
                            "static_loop_iteration_budget_exceeded",
                            statement_path,
                            f"nested static loops may execute at most {MAX_STATIC_LOOP_TRIP_COUNT} body instances",
                        )
                visit_block(
                    statement.body,
                    path=f"{statement_path}.body",
                    values=dict(values),
                    iteration_product=nested_product,
                )
                continue
            if not isinstance(statement, ActionOp):
                issue("unsupported_statement", statement_path, type(statement).__name__)
                continue
            _verify_operation(
                statement,
                path=statement_path,
                values=values,
                event_type=spec.event_type,
                parameter_type=spec.parameter_type,
                states=states,
                reductions=reductions,
                emits=emits,
                proofs=proofs,
                numeric_contract=spec.numeric_contract,
                issue=issue,
            )
            if statement.opcode in {"accept", "ignore", "terminate"} and (
                statement_index != len(block.operations) - 1
            ):
                issue(
                    "operations_after_terminal_decision",
                    statement_path,
                    f"{statement.opcode} must terminate its enclosing block",
                )
            for output in statement.outputs:
                _verify_value_type(
                    output.value_type,
                    f"{statement_path}.outputs.{output.name}.value_type",
                    issues,
                )
                if not _is_ir_identifier(output.name):
                    issue(
                        "invalid_ssa_name",
                        f"{statement_path}.outputs",
                        "SSA names must be ASCII IR identifiers",
                    )
                if output.name in values:
                    issue(
                        "duplicate_ssa_value",
                        f"{statement_path}.outputs",
                        f"duplicate SSA value {output.name!r}",
                    )
                else:
                    values[output.name] = output.value_type

    values: dict[str, ActionValueType] = {}
    for block_index, block in enumerate(spec.blocks):
        visit_block(
            block,
            path=f"blocks[{block_index}]",
            values=values,
            iteration_product=1,
        )

    inferred = infer_action_effects(spec.blocks)
    if tuple(spec.declared_effects.effects) != inferred:
        issue(
            "declared_effect_mismatch",
            "declared_effects",
            f"declared {[item.value for item in spec.declared_effects.effects]!r} but inferred {[item.value for item in inferred]!r}",
        )

    if spec.overflow_policy is not OverflowPolicy.FAIL_CLOSED:
        issue("non_fail_closed_action", "overflow_policy", "v1 requires fail-closed overflow")
    if not spec.numeric_contract.strict_cross_placement_equality:
        issue(
            "nonstrict_numeric_contract_not_supported_v1",
            "numeric_contract",
            "Action IR v1 admits strict cross-placement numeric contracts only",
        )
    if not spec.numeric_contract.reject_nan:
        issue("strict_numeric_nan_policy", "numeric_contract", "strict v1 requires NaN rejection")
    if not spec.numeric_contract.normalize_signed_zero:
        issue("strict_numeric_zero_policy", "numeric_contract", "strict v1 requires signed-zero normalization")

    _verify_logical_event_contract(spec, inferred, issue)

    if issues:
        raise ActionVerificationError(issues)

    obligations = ["fail_closed_overflow", "canonical_result_contract"]
    if spec.logical_event.enforcement is DeliveryEnforcement.KEYED_DEDUP:
        obligations.append("keyed_logical_event_dedup_before_non_idempotent_effects")
    elif spec.logical_event.enforcement is DeliveryEnforcement.REJECT_FUSED:
        obligations.append("fused_placement_rejected_until_single_delivery_or_dedup_is_proven")
    else:
        obligations.append("single_physical_delivery_proof_required_by_lowering")
    if ActionEffect.TRAVERSAL_CONTROL in inferred:
        obligations.append("termination_certificate_requires_compiler_legality_analysis")
    if any(emit.selection is not None for emit in spec.emits):
        obligations.append("bounded_selection_scope_extent_requires_lowering_proof")

    return VerifiedActionContract(
        schema_version=ACTION_IR_SCHEMA_VERSION,
        semantic_digest=spec.semantic_digest,
        source_digest=spec.source_digest,
        inferred_effects=inferred,
        placement_obligations=tuple(obligations),
    )


def action_spec_from_dict(payload: Mapping[str, object]) -> ActionSpec:
    _reject_unknown_keys(
        payload,
        {
            "$schema",
            "schema_version",
            "name",
            "diagnostic_label",
            "event_type",
            "parameter_type",
            "states",
            "reductions",
            "emits",
            "termination_proofs",
            "blocks",
            "declared_effects",
            "logical_event",
            "numeric_contract",
            "overflow_policy",
        },
        "ActionSpec",
    )
    if payload.get("$schema") != ACTION_IR_SCHEMA_ID:
        raise ValueError("unsupported Action IR schema")
    if payload.get("schema_version") != ACTION_IR_SCHEMA_VERSION:
        raise ValueError("unsupported Action IR schema version")

    return ActionSpec(
        name=_required_str(payload, "name"),
        event_type=_record_from_dict(_required_mapping(payload, "event_type")),
        parameter_type=_record_from_dict(_required_mapping(payload, "parameter_type")),
        states=tuple(_state_from_dict(item) for item in _required_sequence(payload, "states")),
        reductions=tuple(
            _reduction_from_dict(item) for item in _required_sequence(payload, "reductions")
        ),
        emits=tuple(_emit_from_dict(item) for item in _required_sequence(payload, "emits")),
        termination_proofs=tuple(
            _proof_from_dict(item) for item in _required_sequence(payload, "termination_proofs")
        ),
        blocks=tuple(_block_from_dict(item) for item in _required_sequence(payload, "blocks")),
        declared_effects=ActionEffectSet(
            tuple(ActionEffect(str(item)) for item in _required_sequence(payload, "declared_effects"))
        ),
        logical_event=_logical_event_from_dict(_required_mapping(payload, "logical_event")),
        numeric_contract=_numeric_from_dict(_required_mapping(payload, "numeric_contract")),
        overflow_policy=OverflowPolicy(_required_str(payload, "overflow_policy")),
        diagnostic_label=_optional_str(payload.get("diagnostic_label")),
    )


def _verify_value_type(
    value_type: object,
    path: str,
    issues: list[VerificationIssue],
) -> None:
    if isinstance(value_type, ActionScalarType):
        if not isinstance(value_type.kind, ActionScalarKind):
            issues.append(
                VerificationIssue(
                    "invalid_scalar_type",
                    path,
                    "scalar type kind must be a closed ActionScalarKind value",
                )
            )
        return
    if isinstance(value_type, ActionTupleType):
        if not value_type.items:
            issues.append(
                VerificationIssue(
                    "empty_tuple_type",
                    path,
                    "tuple types require at least one scalar item",
                )
            )
        for index, item in enumerate(value_type.items):
            if not isinstance(item, ActionScalarType) or not isinstance(
                item.kind, ActionScalarKind
            ):
                issues.append(
                    VerificationIssue(
                        "invalid_tuple_item_type",
                        f"{path}.items[{index}]",
                        "tuple items must be closed scalar types",
                    )
                )
        return
    issues.append(
        VerificationIssue(
            "invalid_value_type",
            path,
            "value types must belong to the closed scalar-or-tuple Action IR set",
        )
    )


def _verify_record(
    record: ActionRecordType,
    path: str,
    issues: list[VerificationIssue],
) -> None:
    if not _is_ir_identifier(record.name):
        issues.append(
            VerificationIssue(
                "invalid_record_name",
                path,
                "record names must be ASCII IR identifiers",
            )
        )
    names = [field.name for field in record.fields]
    if len(names) != len(set(names)):
        issues.append(VerificationIssue("duplicate_field", path, "record fields must be unique"))
    for field_spec in record.fields:
        _verify_value_type(field_spec.value_type, f"{path}.{field_spec.name}.type", issues)
        if not _is_ir_identifier(field_spec.name):
            issues.append(
                VerificationIssue(
                    "invalid_field_name",
                    f"{path}.{field_spec.name}",
                    "field names must be ASCII IR identifiers",
                )
            )
        if field_spec.nonnegative and (
            not isinstance(field_spec.value_type, ActionScalarType)
            or not field_spec.value_type.is_integer
        ):
            issues.append(
                VerificationIssue(
                    "invalid_nonnegative_annotation",
                    f"{path}.{field_spec.name}",
                    "nonnegative annotation requires an integer scalar",
                )
            )


def _unique_by_name(
    items: Sequence[object],
    path: str,
    issues: list[VerificationIssue],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for item in items:
        name = getattr(item, "name")
        if name in result:
            issues.append(VerificationIssue("duplicate_name", path, f"duplicate name {name!r}"))
        else:
            result[name] = item
    return result


def _verify_capacity_expression(
    expression: CapacityExpr,
    parameters: ActionRecordType,
    path: str,
    issues: list[VerificationIssue],
) -> None:
    if isinstance(expression, CapacityConst):
        if not isinstance(expression.value, int) or isinstance(expression.value, bool):
            issues.append(VerificationIssue("invalid_capacity_constant", path, "constant must be an integer"))
        elif expression.value < 0 or expression.value > MAX_U64:
            issues.append(VerificationIssue("invalid_capacity_constant", path, "constant must fit unsigned 64-bit"))
        return
    if isinstance(expression, CapacityExtent):
        return
    if isinstance(expression, CapacityParam):
        field_spec = parameters.field(expression.name)
        if field_spec is None:
            issues.append(VerificationIssue("unknown_capacity_parameter", path, expression.name))
        elif (
            not isinstance(field_spec.value_type, ActionScalarType)
            or not field_spec.value_type.is_integer
            or not field_spec.nonnegative
        ):
            issues.append(
                VerificationIssue(
                    "unsafe_capacity_parameter",
                    path,
                    "capacity parameter must be a declared nonnegative integer",
                )
            )
        return
    if isinstance(expression, (CapacityAdd, CapacityMul)):
        _verify_capacity_expression(expression.left, parameters, f"{path}.left", issues)
        _verify_capacity_expression(expression.right, parameters, f"{path}.right", issues)
        return
    issues.append(VerificationIssue("unsupported_capacity_expression", path, type(expression).__name__))


def _verify_logical_event_contract(
    spec: ActionSpec,
    inferred: tuple[ActionEffect, ...],
    issue,
) -> None:
    contract = spec.logical_event
    if not contract.key_fields:
        issue("missing_logical_event_key", "logical_event.key_fields", "logical event key cannot be empty")
    if len(contract.key_fields) != len(set(contract.key_fields)):
        issue("duplicate_logical_event_key", "logical_event.key_fields", "logical event key fields must be unique")
    for field_name in contract.key_fields:
        field_spec = spec.event_type.field(field_name)
        if field_spec is None:
            issue("unknown_logical_event_key", "logical_event.key_fields", field_name)
        elif not isinstance(field_spec.value_type, ActionScalarType) or not field_spec.value_type.is_integer:
            issue("unstable_logical_event_key_type", "logical_event.key_fields", field_name)

    has_non_idempotent = bool(set(inferred) & _NON_IDEMPOTENT_EFFECTS)
    if contract.physical_delivery is PhysicalDelivery.PROVEN_SINGLE:
        if contract.enforcement is not DeliveryEnforcement.PROVEN_SINGLE:
            issue(
                "single_delivery_enforcement_mismatch",
                "logical_event.enforcement",
                "proven-single delivery requires proven-single enforcement",
            )
        if not contract.proof_reference:
            issue(
                "single_delivery_missing_proof",
                "logical_event.proof_reference",
                "single physical delivery requires a proof reference",
            )
    elif contract.enforcement is DeliveryEnforcement.PROVEN_SINGLE:
        issue(
            "repeat_delivery_not_proven_single",
            "logical_event.enforcement",
            "may-repeat delivery cannot claim proven-single enforcement",
        )

    if has_non_idempotent and contract.physical_delivery is PhysicalDelivery.MAY_REPEAT:
        if contract.enforcement not in {
            DeliveryEnforcement.KEYED_DEDUP,
            DeliveryEnforcement.REJECT_FUSED,
        }:
            issue(
                "duplicate_delivery_non_idempotent_effect",
                "logical_event.enforcement",
                "non-idempotent effects require keyed dedup or fused-placement rejection",
            )


def _verify_operation(
    op: ActionOp,
    *,
    path: str,
    values: Mapping[str, ActionValueType],
    event_type: ActionRecordType,
    parameter_type: ActionRecordType,
    states: Mapping[str, ActionStateSpec],
    reductions: Mapping[str, ActionReductionSpec],
    emits: Mapping[str, ActionEmitSpec],
    proofs: Mapping[str, TerminationProofSpec],
    numeric_contract: NumericContract,
    issue,
) -> None:
    if op.opcode in _ILLEGAL_OPCODE_CODES:
        issue(_ILLEGAL_OPCODE_CODES[op.opcode], path, f"opcode {op.opcode!r} is forbidden")
        return
    if op.opcode not in _PURE_OPCODES and op.opcode not in _EFFECT_BY_OPCODE:
        issue("unsupported_opcode", path, f"opcode {op.opcode!r} is outside the closed v1 set")
        return

    allowed_attributes = _ALLOWED_ATTRIBUTES_BY_OPCODE[op.opcode]
    actual_attributes = {item.name for item in op.attributes}
    for unknown in sorted(actual_attributes - allowed_attributes):
        issue(
            "unknown_opcode_attribute",
            f"{path}.attributes.{unknown}",
            f"opcode {op.opcode!r} does not admit attribute {unknown!r}",
        )

    input_types: list[ActionValueType | None] = []
    for name in op.inputs:
        input_type = values.get(name)
        if input_type is None:
            issue("unknown_ssa_input", f"{path}.inputs", name)
        input_types.append(input_type)

    if op.opcode == "load_event":
        _verify_load(op, path, event_type, "field", issue)
    elif op.opcode == "load_param":
        _verify_load(op, path, parameter_type, "field", issue)
    elif op.opcode == "const":
        _expect_counts(op, path, inputs=0, outputs=1, issue=issue)
        literal = op.attribute("literal")
        if literal is None:
            issue("const_missing_literal", f"{path}.attributes", "const requires a typed literal")
        elif op.outputs:
            _verify_scalar_literal(
                literal,
                expected_type=op.outputs[0].value_type,
                numeric_contract=numeric_contract,
                path=f"{path}.attributes.literal",
                issue=issue,
            )
    elif op.opcode == "compare":
        _expect_counts(op, path, inputs=2, outputs=1, issue=issue)
        if len(input_types) == 2 and None not in input_types and input_types[0] != input_types[1]:
            issue("compare_type_mismatch", path, "compare operands must have identical types")
        if op.outputs and op.outputs[0].value_type != BOOL:
            issue("compare_result_not_bool", path, "compare result must be bool")
        if op.attribute("predicate") not in {"eq", "ne", "lt", "le", "gt", "ge"}:
            issue("unsupported_compare_predicate", path, "invalid compare predicate")
    elif op.opcode in {"bool_and", "bool_or"}:
        _expect_counts(op, path, inputs=2, outputs=1, issue=issue)
        _require_types(input_types, BOOL, path, issue)
        if op.outputs and op.outputs[0].value_type != BOOL:
            issue("boolean_result_type", path, "boolean result must be bool")
    elif op.opcode == "bool_not":
        _expect_counts(op, path, inputs=1, outputs=1, issue=issue)
        _require_types(input_types, BOOL, path, issue)
        if op.outputs and op.outputs[0].value_type != BOOL:
            issue("boolean_result_type", path, "boolean result must be bool")
    elif op.opcode in {"add", "sub", "mul", "min", "max"}:
        _expect_counts(op, path, inputs=2, outputs=1, issue=issue)
        if len(input_types) == 2 and None not in input_types:
            if input_types[0] != input_types[1] or not _is_numeric_type(input_types[0]):
                issue("arithmetic_type_mismatch", path, "arithmetic operands must share one numeric type")
            elif op.outputs and op.outputs[0].value_type != input_types[0]:
                issue("arithmetic_result_type", path, "arithmetic result type must match operands")
    elif op.opcode == "select":
        _expect_counts(op, path, inputs=3, outputs=1, issue=issue)
        if input_types and input_types[0] is not None and input_types[0] != BOOL:
            issue("select_condition_type", path, "select condition must be bool")
        if len(input_types) == 3 and input_types[1] is not None and input_types[2] is not None:
            if input_types[1] != input_types[2]:
                issue("select_value_type", path, "select values must have identical types")
            elif op.outputs and op.outputs[0].value_type != input_types[1]:
                issue("select_result_type", path, "select result must match selected values")
    elif op.opcode == "cast":
        _expect_counts(op, path, inputs=1, outputs=1, issue=issue)
        if input_types and input_types[0] is not None and op.outputs:
            source_type = input_types[0]
            target_type = op.outputs[0].value_type
            if (
                not isinstance(source_type, ActionScalarType)
                or not isinstance(target_type, ActionScalarType)
                or (source_type.kind, target_type.kind) not in _SAFE_CASTS
            ):
                issue(
                    "unsafe_cast",
                    path,
                    "v1 admits only i32->i64, u32->u64, and f32->f64 widening casts",
                )
    elif op.opcode == "state_read":
        _expect_counts(op, path, inputs=0, outputs=1, issue=issue)
        state_name = op.attribute("state")
        state = states.get(str(state_name)) if state_name is not None else None
        if state is None:
            issue("unknown_state", path, str(state_name))
        elif op.outputs and op.outputs[0].value_type != state.value_type:
            issue("state_read_type", path, "state read result type mismatch")
    elif op.opcode == "state_write":
        _expect_counts(op, path, inputs=1, outputs=0, issue=issue)
        state_name = op.attribute("state")
        state = states.get(str(state_name)) if state_name is not None else None
        if state is None:
            issue("unknown_state", path, str(state_name))
        elif input_types and input_types[0] is not None and input_types[0] != state.value_type:
            issue("state_write_type", path, "state write input type mismatch")
    elif op.opcode in {"filter", "accept", "ignore"}:
        expected_inputs = 1 if op.opcode == "filter" else 0
        _expect_counts(op, path, inputs=expected_inputs, outputs=0, issue=issue)
        if op.opcode == "filter":
            _require_types(input_types, BOOL, path, issue)
    elif op.opcode == "reduce":
        reduction_name = op.attribute("reduction")
        reduction = reductions.get(str(reduction_name)) if reduction_name is not None else None
        if reduction is None:
            issue("unknown_reduction", path, str(reduction_name))
        else:
            expected_inputs = 0 if reduction.operator is ReductionOperator.COUNT else 1
            _expect_counts(op, path, inputs=expected_inputs, outputs=0, issue=issue)
            if expected_inputs and input_types and input_types[0] is not None:
                if input_types[0] != reduction.value_type:
                    issue("reduction_value_type", path, "reduction input type mismatch")
    elif op.opcode == "emit":
        emit_name = op.attribute("emit")
        emit = emits.get(str(emit_name)) if emit_name is not None else None
        if emit is None:
            issue("unknown_emit", path, str(emit_name))
        else:
            _expect_counts(op, path, inputs=len(emit.record_type.fields), outputs=0, issue=issue)
            for index, field_spec in enumerate(emit.record_type.fields):
                if index < len(input_types) and input_types[index] is not None:
                    if input_types[index] != field_spec.value_type:
                        issue("emit_field_type", f"{path}.inputs[{index}]", field_spec.name)
    elif op.opcode == "terminate":
        _expect_counts(op, path, inputs=0, outputs=0, issue=issue)
        proof_name = op.attribute("proof")
        if proof_name is None or str(proof_name) not in proofs:
            issue("illegal_terminate", path, "terminate requires a declared proof")
def _verify_load(op: ActionOp, path: str, record: ActionRecordType, attribute: str, issue) -> None:
    _expect_counts(op, path, inputs=0, outputs=1, issue=issue)
    field_name = op.attribute(attribute)
    field_spec = record.field(str(field_name)) if field_name is not None else None
    if field_spec is None:
        issue("unknown_load_field", path, str(field_name))
    elif op.outputs and op.outputs[0].value_type != field_spec.value_type:
        issue("load_result_type", path, "load result type must match field")


def _verify_scalar_literal(
    literal: object,
    *,
    expected_type: ActionValueType,
    numeric_contract: NumericContract | None,
    path: str,
    issue,
) -> None:
    if not isinstance(literal, ActionScalarLiteral):
        issue("untyped_scalar_literal", path, "a typed scalar literal is required")
        return
    if not isinstance(expected_type, ActionScalarType):
        issue("literal_for_nonscalar_type", path, "v1 literals support scalar values only")
        return
    if literal.value_type != expected_type:
        issue("literal_type_mismatch", path, "literal type must match its declared value type")
        return
    value = literal.to_python()
    if isinstance(value, float) and math.isinf(value):
        if numeric_contract is not None and not numeric_contract.allow_infinity:
            issue("infinity_not_admitted", path, "infinity requires explicit numeric-contract admission")


def _expect_counts(op: ActionOp, path: str, *, inputs: int, outputs: int, issue) -> None:
    if len(op.inputs) != inputs:
        issue("operand_count", f"{path}.inputs", f"expected {inputs}, got {len(op.inputs)}")
    if len(op.outputs) != outputs:
        issue("result_count", f"{path}.outputs", f"expected {outputs}, got {len(op.outputs)}")


def _require_types(input_types: Sequence[ActionValueType | None], expected: ActionValueType, path: str, issue) -> None:
    for index, input_type in enumerate(input_types):
        if input_type is not None and input_type != expected:
            issue("operand_type", f"{path}.inputs[{index}]", f"expected {expected!r}")


def _is_float_type(value_type: ActionValueType) -> bool:
    return isinstance(value_type, ActionScalarType) and value_type.is_float


def _is_numeric_type(value_type: ActionValueType) -> bool:
    return isinstance(value_type, ActionScalarType) and value_type.is_numeric


def _type_from_dict(payload: Mapping[str, object]) -> ActionValueType:
    kind = payload.get("kind")
    if kind == "scalar":
        _reject_unknown_keys(payload, {"kind", "scalar"}, "scalar type")
        return ActionScalarType(ActionScalarKind(_required_str(payload, "scalar")))
    if kind == "tuple":
        _reject_unknown_keys(payload, {"kind", "items"}, "tuple type")
        return ActionTupleType(
            tuple(
                _scalar_type_from_dict(_as_mapping(item))
                for item in _required_sequence(payload, "items")
            )
        )
    raise ValueError(f"unsupported Action type kind: {kind!r}")


def _field_from_dict(payload: Mapping[str, object]) -> ActionField:
    _reject_unknown_keys(payload, {"name", "type", "nonnegative"}, "field")
    return ActionField(
        name=_required_str(payload, "name"),
        value_type=_type_from_dict(_required_mapping(payload, "type")),
        nonnegative=_optional_bool_field(payload, "nonnegative", False),
    )


def _record_from_dict(payload: Mapping[str, object]) -> ActionRecordType:
    _reject_unknown_keys(payload, {"name", "fields"}, "record")
    return ActionRecordType(
        name=_required_str(payload, "name"),
        fields=tuple(_field_from_dict(_as_mapping(item)) for item in _required_sequence(payload, "fields")),
    )


def _capacity_from_dict(payload: Mapping[str, object]) -> CapacityExpr:
    kind = payload.get("kind")
    if kind == "const":
        _reject_unknown_keys(payload, {"kind", "value"}, "capacity const")
        if not isinstance(payload.get("value"), int) or isinstance(payload.get("value"), bool):
            raise ValueError("capacity constant value must be an integer")
        return CapacityConst(int(payload["value"]))
    if kind == "extent":
        _reject_unknown_keys(payload, {"kind", "name"}, "capacity extent")
        return CapacityExtent(ExtentKind(_required_str(payload, "name")))
    if kind == "param":
        _reject_unknown_keys(payload, {"kind", "name"}, "capacity param")
        return CapacityParam(_required_str(payload, "name"))
    if kind == "add":
        _reject_unknown_keys(payload, {"kind", "left", "right"}, "capacity add")
        return CapacityAdd(
            _capacity_from_dict(_required_mapping(payload, "left")),
            _capacity_from_dict(_required_mapping(payload, "right")),
        )
    if kind == "mul":
        _reject_unknown_keys(payload, {"kind", "left", "right"}, "capacity mul")
        return CapacityMul(
            _capacity_from_dict(_required_mapping(payload, "left")),
            _capacity_from_dict(_required_mapping(payload, "right")),
        )
    raise ValueError(f"unsupported capacity kind: {kind!r}")


def _state_from_dict(payload: object) -> ActionStateSpec:
    row = _as_mapping(payload)
    _reject_unknown_keys(
        row,
        {"name", "type", "scope", "initial_value", "key_fields", "merge_reduction"},
        "state",
    )
    return ActionStateSpec(
        name=_required_str(row, "name"),
        value_type=_type_from_dict(_required_mapping(row, "type")),
        scope=StateScope(_required_str(row, "scope")),
        initial_value=_scalar_literal_from_dict(_as_mapping(row.get("initial_value"))),
        key_fields=tuple(str(item) for item in _required_sequence(row, "key_fields")),
        merge_reduction=_optional_str(row.get("merge_reduction")),
    )


def _reduction_from_dict(payload: object) -> ActionReductionSpec:
    row = _as_mapping(payload)
    _reject_unknown_keys(
        row,
        {"name", "key_fields", "value_type", "operator", "identity", "overflow_policy"},
        "reduction",
    )
    return ActionReductionSpec(
        name=_required_str(row, "name"),
        key_fields=tuple(str(item) for item in _required_sequence(row, "key_fields")),
        value_type=_type_from_dict(_required_mapping(row, "value_type")),
        operator=ReductionOperator(_required_str(row, "operator")),
        identity=_scalar_literal_from_dict(_as_mapping(row.get("identity"))),
        overflow_policy=OverflowPolicy(_required_str(row, "overflow_policy")),
    )


def _emit_from_dict(payload: object) -> ActionEmitSpec:
    row = _as_mapping(payload)
    _reject_unknown_keys(
        row,
        {
            "name",
            "record_type",
            "capacity",
            "order_kind",
            "order_keys",
            "selection",
            "duplicate_policy",
            "event_order_proof",
            "allow_empty_complete",
        },
        "emit",
    )
    return ActionEmitSpec(
        name=_required_str(row, "name"),
        record_type=_record_from_dict(_required_mapping(row, "record_type")),
        capacity=_capacity_from_dict(_required_mapping(row, "capacity")),
        order_kind=OutputOrderKind(_required_str(row, "order_kind")),
        order_keys=tuple(
            OrderKey(
                field=_required_str(_as_mapping(item), "field"),
                ascending=_order_key_ascending(_as_mapping(item)),
                role=OrderKeyRole(_required_str(_as_mapping(item), "role")),
            )
            for item in _required_sequence(row, "order_keys")
        ),
        selection=(
            None
            if row.get("selection") is None
            else _selection_from_dict(_required_mapping(row, "selection"))
        ),
        duplicate_policy=DuplicatePolicy(_required_str(row, "duplicate_policy")),
        event_order_proof=_optional_str(row.get("event_order_proof")),
        allow_empty_complete=_optional_bool_field(row, "allow_empty_complete", True),
    )


def _selection_from_dict(payload: Mapping[str, object]) -> BoundedSelectionSpec:
    _reject_unknown_keys(
        payload,
        {"scope_key_fields", "scope_extent", "limit", "order_keys"},
        "bounded selection",
    )
    return BoundedSelectionSpec(
        scope_key_fields=tuple(
            str(item) for item in _required_sequence(payload, "scope_key_fields")
        ),
        scope_extent=ExtentKind(_required_str(payload, "scope_extent")),
        limit=_capacity_from_dict(_required_mapping(payload, "limit")),
        order_keys=tuple(
            OrderKey(
                field=_required_str(_as_mapping(item), "field"),
                ascending=_order_key_ascending(_as_mapping(item)),
                role=OrderKeyRole(_required_str(_as_mapping(item), "role")),
            )
            for item in _required_sequence(payload, "order_keys")
        ),
    )


def _proof_from_dict(payload: object) -> TerminationProofSpec:
    row = _as_mapping(payload)
    _reject_unknown_keys(
        row,
        {
            "name",
            "kind",
            "certificate",
            "state_name",
            "order_independent",
            "unseen_cannot_improve",
        },
        "termination proof",
    )
    return TerminationProofSpec(
        name=_required_str(row, "name"),
        kind=TerminationProofKind(_required_str(row, "kind")),
        certificate=_required_str(row, "certificate"),
        state_name=_optional_str(row.get("state_name")),
        order_independent=_optional_bool_field(row, "order_independent", False),
        unseen_cannot_improve=_optional_bool_field(row, "unseen_cannot_improve", False),
    )


def _block_from_dict(payload: object) -> ActionBlock:
    row = _as_mapping(payload)
    _reject_unknown_keys(row, {"label", "operations"}, "block")
    return ActionBlock(
        label=_required_str(row, "label"),
        operations=tuple(
            _statement_from_dict(item) for item in _required_sequence(row, "operations")
        ),
    )


def _statement_from_dict(payload: object) -> ActionStatement:
    row = _as_mapping(payload)
    if row.get("opcode") == "for_static":
        _reject_unknown_keys(row, {"opcode", "trip_count", "body"}, "static loop")
        trip_count = row.get("trip_count")
        if not isinstance(trip_count, int) or isinstance(trip_count, bool):
            raise ValueError("static-loop trip_count must be an integer")
        return ActionStaticLoop(
            trip_count=trip_count,
            body=_block_from_dict(_required_mapping(row, "body")),
        )
    return _op_from_dict(row)


def _op_from_dict(payload: object) -> ActionOp:
    row = _as_mapping(payload)
    _reject_unknown_keys(row, {"opcode", "inputs", "outputs", "attributes"}, "operation")
    attrs = _required_mapping(row, "attributes")
    return ActionOp(
        opcode=_required_str(row, "opcode"),
        inputs=tuple(str(item) for item in _required_sequence(row, "inputs")),
        outputs=tuple(
            ActionValue(
                name=_required_str(_as_mapping(item), "name"),
                value_type=_type_from_dict(_required_mapping(_as_mapping(item), "type")),
            )
            for item in _required_sequence(row, "outputs")
        ),
        attributes=tuple(
            ActionAttribute(name, _attribute_value(attrs[name])) for name in sorted(attrs)
        ),
    )


def _logical_event_from_dict(payload: Mapping[str, object]) -> LogicalEventContract:
    _reject_unknown_keys(
        payload,
        {"semantics", "key_fields", "physical_delivery", "enforcement", "proof_reference"},
        "logical event",
    )
    if payload.get("semantics") != "exactly_once_logical_delivery":
        raise ValueError("Action IR v1 supports exactly-once logical delivery only")
    return LogicalEventContract(
        key_fields=tuple(str(item) for item in _required_sequence(payload, "key_fields")),
        physical_delivery=PhysicalDelivery(_required_str(payload, "physical_delivery")),
        enforcement=DeliveryEnforcement(_required_str(payload, "enforcement")),
        proof_reference=_optional_str(payload.get("proof_reference")),
    )


def _numeric_from_dict(payload: Mapping[str, object]) -> NumericContract:
    _reject_unknown_keys(
        payload,
        {
            "strict_cross_placement_equality",
            "reject_nan",
            "normalize_signed_zero",
            "allow_infinity",
        },
        "numeric contract",
    )
    return NumericContract(
        strict_cross_placement_equality=_optional_bool_field(
            payload, "strict_cross_placement_equality", True
        ),
        reject_nan=_optional_bool_field(payload, "reject_nan", True),
        normalize_signed_zero=_optional_bool_field(payload, "normalize_signed_zero", True),
        allow_infinity=_optional_bool_field(payload, "allow_infinity", False),
    )


def _attribute_value(value: object) -> ActionAttributeValue:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, Mapping):
        return _scalar_literal_from_dict(value)
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(value)
    if isinstance(value, list) and all(isinstance(item, int) and not isinstance(item, bool) for item in value):
        return tuple(value)
    raise ValueError(f"unsupported Action attribute value: {value!r}")


def _scalar_literal_from_dict(payload: Mapping[str, object]) -> ActionScalarLiteral:
    _reject_unknown_keys(payload, {"kind", "type", "bits"}, "scalar literal")
    if payload.get("kind") != "scalar_literal":
        raise ValueError("expected a scalar_literal payload")
    value_type = _type_from_dict(_required_mapping(payload, "type"))
    if not isinstance(value_type, ActionScalarType):
        raise ValueError("scalar literal type must be scalar")
    encoded = _required_str(payload, "bits")
    if not encoded.startswith("0x"):
        raise ValueError("scalar literal bits must use 0x-prefixed hexadecimal")
    try:
        bits = int(encoded[2:], 16)
    except ValueError as exc:
        raise ValueError("scalar literal bits must be hexadecimal") from exc
    width = _SCALAR_WIDTH_BITS[value_type.kind]
    hex_digits = max(1, (width + 3) // 4)
    if len(encoded) != 2 + hex_digits:
        raise ValueError(f"scalar literal bits must contain exactly {hex_digits} hex digits")
    return ActionScalarLiteral(value_type, bits)


def _scalar_type_from_dict(payload: Mapping[str, object]) -> ActionScalarType:
    value_type = _type_from_dict(payload)
    if not isinstance(value_type, ActionScalarType):
        raise ValueError("tuple items must be scalar types")
    return value_type


def _order_key_ascending(payload: Mapping[str, object]) -> bool:
    _reject_unknown_keys(payload, {"field", "ascending", "role"}, "order key")
    return _optional_bool_field(payload, "ascending", True)


def _optional_bool_field(
    payload: Mapping[str, object],
    name: str,
    default: bool,
) -> bool:
    if name not in payload:
        return default
    value = payload[name]
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a JSON boolean")
    return value


def _reject_unknown_keys(
    payload: Mapping[str, object],
    allowed: set[str],
    context: str,
) -> None:
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ValueError(f"{context} has unknown fields: {unknown!r}")


def _is_ir_identifier(value: object) -> bool:
    if not isinstance(value, str) or not value or not value.isascii():
        return False
    return (value[0].isalpha() or value[0] == "_") and all(
        char.isalnum() or char == "_" for char in value[1:]
    )


def _required_mapping(payload: Mapping[str, object], name: str) -> Mapping[str, object]:
    return _as_mapping(payload.get(name))


def _as_mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"expected mapping, got {type(value).__name__}")
    return value


def _required_sequence(payload: Mapping[str, object], name: str) -> Sequence[object]:
    value = payload.get(name)
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a JSON array")
    return value


def _required_str(payload: Mapping[str, object], name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a nonempty string")
    return value


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("optional string field must be a string or null")
    return value


__all__ = [
    "ACTION_IR_SCHEMA_ID",
    "ACTION_IR_SCHEMA_VERSION",
    "ActionAttribute",
    "ActionBlock",
    "ActionBuilder",
    "ActionEffect",
    "ActionEffectSet",
    "ActionEmitSpec",
    "ActionField",
    "ActionOp",
    "ActionRecordType",
    "ActionReductionSpec",
    "ActionScalarKind",
    "ActionScalarLiteral",
    "ActionScalarType",
    "ActionSpec",
    "ActionStaticLoop",
    "ActionStateSpec",
    "ActionTupleType",
    "ActionValue",
    "ActionVerificationError",
    "BOOL",
    "BoundedSelectionSpec",
    "CapacityAdd",
    "CapacityConst",
    "CapacityExtent",
    "CapacityMul",
    "CapacityParam",
    "DeliveryEnforcement",
    "DuplicatePolicy",
    "ExtentKind",
    "F32",
    "F64",
    "I32",
    "I64",
    "LogicalEventContract",
    "NumericContract",
    "OrderKey",
    "OrderKeyRole",
    "OutputOrderKind",
    "OverflowPolicy",
    "PhysicalDelivery",
    "ReductionOperator",
    "StateScope",
    "TerminationProofKind",
    "TerminationProofSpec",
    "U32",
    "U64",
    "VerifiedActionContract",
    "action_attributes",
    "action_spec_from_dict",
    "canonical_float32_key",
    "canonical_float64_key",
    "evaluate_capacity",
    "infer_action_effects",
    "verify_action_spec",
]
