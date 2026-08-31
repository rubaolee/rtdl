from __future__ import annotations

from dataclasses import dataclass
from functools import cmp_to_key
import math
import struct
from typing import Mapping, Sequence

from .action_ir import (
    ActionBlock,
    ActionEmitSpec,
    ActionOp,
    ActionRecordType,
    ActionScalarKind,
    ActionScalarLiteral,
    ActionScalarType,
    ActionSpec,
    ActionStateSpec,
    ActionStaticLoop,
    ActionTupleType,
    ActionValueType,
    CapacityExtent,
    DeliveryEnforcement,
    DuplicatePolicy,
    ExtentKind,
    OrderKey,
    OutputOrderKind,
    ReductionOperator,
    StateScope,
    canonical_float32_key,
    canonical_float64_key,
    evaluate_capacity,
    verify_action_spec,
)


@dataclass(frozen=True)
class ActionExecutionIssue:
    code: str
    path: str
    message: str


class ActionExecutionError(RuntimeError):
    def __init__(self, issue: ActionExecutionIssue) -> None:
        self.issue = issue
        super().__init__(f"Action reference execution failed: {issue.code}@{issue.path}: {issue.message}")


@dataclass(frozen=True)
class EmittedRelation:
    name: str
    fields: tuple[str, ...]
    rows: tuple[tuple[object, ...], ...]
    order_kind: OutputOrderKind

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "fields": list(self.fields),
            "rows": [list(row) for row in self.rows],
            "order_kind": self.order_kind.value,
        }


@dataclass(frozen=True)
class ReductionRelation:
    name: str
    key_fields: tuple[str, ...]
    rows: tuple[tuple[tuple[object, ...], object], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "key_fields": list(self.key_fields),
            "rows": [
                {"key": list(key), "value": value}
                for key, value in self.rows
            ],
        }


@dataclass(frozen=True)
class StateRelation:
    name: str
    scope: StateScope
    key_fields: tuple[str, ...]
    rows: tuple[tuple[tuple[object, ...], object], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "scope": self.scope.value,
            "key_fields": list(self.key_fields),
            "rows": [
                {"key": list(key), "value": value}
                for key, value in self.rows
            ],
        }


@dataclass(frozen=True)
class ActionExecutionResult:
    semantic_digest: str
    physical_event_count: int
    logical_event_count: int
    duplicate_physical_event_count: int
    terminated_event_count: int
    filtered_event_count: int
    accepted_event_count: int
    ignored_event_count: int
    emitted_relations: tuple[EmittedRelation, ...]
    reductions: tuple[ReductionRelation, ...]
    states: tuple[StateRelation, ...]

    def semantic_dict(self) -> dict[str, object]:
        return {
            "semantic_digest": self.semantic_digest,
            "emitted_relations": [item.to_dict() for item in self.emitted_relations],
            "reductions": [item.to_dict() for item in self.reductions],
            "states": [item.to_dict() for item in self.states],
        }

    def to_dict(self) -> dict[str, object]:
        return self.semantic_dict() | {
            "physical_event_count": self.physical_event_count,
            "logical_event_count": self.logical_event_count,
            "duplicate_physical_event_count": self.duplicate_physical_event_count,
            "terminated_event_count": self.terminated_event_count,
            "filtered_event_count": self.filtered_event_count,
            "accepted_event_count": self.accepted_event_count,
            "ignored_event_count": self.ignored_event_count,
        }


@dataclass
class _Counters:
    logical: int = 0
    duplicates: int = 0
    terminated: int = 0
    filtered: int = 0
    accepted: int = 0
    ignored: int = 0


@dataclass(frozen=True)
class _Control:
    kind: str
    proof_name: str | None = None


_CONTINUE = _Control("continue")


@dataclass(frozen=True)
class _EmitRuntimePolicy:
    capacity: int
    selection_limit: int | None = None
    selection_scope_extent: int | None = None


def execute_action_reference(
    spec: ActionSpec,
    events: Sequence[Mapping[str, object]],
    parameters: Mapping[str, object],
    *,
    extents: Mapping[ExtentKind | str, int] | None = None,
    allocator_limit: int = (1 << 63) - 1,
    discharged_termination_proofs: frozenset[str] = frozenset(),
) -> ActionExecutionResult:
    """Execute one verified Action IR program with deterministic CPU semantics."""

    verified = verify_action_spec(spec)
    normalized_parameters = _normalize_record(
        spec.parameter_type,
        parameters,
        spec=spec,
        path="parameters",
    )
    normalized_events = tuple(
        _normalize_record(spec.event_type, event, spec=spec, path=f"events[{index}]")
        for index, event in enumerate(events)
    )
    normalized_extents = dict(extents or {})
    capacity_parameters = {
        name: value
        for name, value in normalized_parameters.items()
        if isinstance(value, int) and not isinstance(value, bool)
    }
    emit_policies: dict[str, _EmitRuntimePolicy] = {}
    for emit in spec.emits:
        try:
            capacity = evaluate_capacity(
                emit.capacity,
                extents=normalized_extents,
                parameters=capacity_parameters,
                allocator_limit=allocator_limit,
            )
            selection_limit = None
            selection_scope_extent = None
            if emit.selection is not None:
                selection_limit = evaluate_capacity(
                    emit.selection.limit,
                    extents=normalized_extents,
                    parameters=capacity_parameters,
                    allocator_limit=allocator_limit,
                )
                selection_scope_extent = evaluate_capacity(
                    CapacityExtent(emit.selection.scope_extent),
                    extents=normalized_extents,
                    parameters=capacity_parameters,
                    allocator_limit=allocator_limit,
                )
            emit_policies[emit.name] = _EmitRuntimePolicy(
                capacity=capacity,
                selection_limit=selection_limit,
                selection_scope_extent=selection_scope_extent,
            )
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            _fail("capacity_evaluation_failed", f"emits.{emit.name}.capacity", str(exc))

    states: dict[str, dict[tuple[object, ...], object]] = {
        state.name: {} for state in spec.states
    }
    reductions: dict[str, dict[tuple[object, ...], object]] = {
        reduction.name: {} for reduction in spec.reductions
    }
    emitted: dict[str, list[tuple[object, ...]]] = {emit.name: [] for emit in spec.emits}
    emit_selection_scopes: dict[str, set[tuple[object, ...]]] = {
        emit.name: set() for emit in spec.emits
    }
    terminated_scopes: set[tuple[str, tuple[object, ...]]] = set()
    seen_logical: dict[tuple[object, ...], tuple[tuple[str, object], ...]] = {}
    counters = _Counters()

    state_specs = {state.name: state for state in spec.states}
    reduction_specs = {item.name: item for item in spec.reductions}
    emit_specs = {item.name: item for item in spec.emits}
    proof_specs = {item.name: item for item in spec.termination_proofs}

    for event_index, event in enumerate(normalized_events):
        logical_key = _field_key(spec.logical_event.key_fields, event, normalized_parameters)
        payload_identity = tuple(sorted(event.items()))
        prior = seen_logical.get(logical_key)
        if prior is not None:
            counters.duplicates += 1
            if prior != payload_identity:
                _fail(
                    "logical_event_key_collision",
                    f"events[{event_index}]",
                    "one logical-event key mapped to different normalized payloads",
                )
            if spec.logical_event.enforcement is DeliveryEnforcement.KEYED_DEDUP:
                continue
            _fail(
                "unexpected_duplicate_physical_delivery",
                f"events[{event_index}]",
                "duplicate physical delivery is not discharged by keyed dedup",
            )
        seen_logical[logical_key] = payload_identity
        counters.logical += 1

        if _event_is_terminated(
            event,
            normalized_parameters,
            terminated_scopes,
            proof_specs,
            state_specs,
        ):
            counters.terminated += 1
            continue

        values: dict[str, object] = {}
        control = _CONTINUE
        for block_index, block in enumerate(spec.blocks):
            control = _execute_block(
                block,
                path=f"blocks[{block_index}]",
                spec=spec,
                event=event,
                parameters=normalized_parameters,
                values=values,
                states=states,
                reductions=reductions,
                emitted=emitted,
                emit_policies=emit_policies,
                emit_selection_scopes=emit_selection_scopes,
                state_specs=state_specs,
                reduction_specs=reduction_specs,
                emit_specs=emit_specs,
                discharged_termination_proofs=discharged_termination_proofs,
            )
            if control.kind != "continue":
                break

        if control.kind == "filter":
            counters.filtered += 1
        elif control.kind == "accept":
            counters.accepted += 1
        elif control.kind == "ignore":
            counters.ignored += 1
        elif control.kind == "terminate":
            proof = proof_specs[control.proof_name or ""]
            state = state_specs[proof.state_name or ""]
            scope_key = _field_key(state.key_fields, event, normalized_parameters)
            terminated_scopes.add((proof.name, scope_key))
            counters.terminated += 1

    emitted_relations = tuple(
        _finalize_emit(emit, emitted[emit.name]) for emit in spec.emits
    )
    reduction_relations = tuple(
        ReductionRelation(
            name=reduction.name,
            key_fields=reduction.key_fields,
            rows=tuple(
                sorted(
                    reductions[reduction.name].items(),
                    key=lambda item: _generic_tuple_key(item[0]),
                )
            ),
        )
        for reduction in spec.reductions
    )
    state_relations = tuple(
        StateRelation(
            name=state.name,
            scope=state.scope,
            key_fields=state.key_fields,
            rows=tuple(
                sorted(
                    states[state.name].items(),
                    key=lambda item: _generic_tuple_key(item[0]),
                )
            ),
        )
        for state in spec.states
    )
    return ActionExecutionResult(
        semantic_digest=verified.semantic_digest,
        physical_event_count=len(normalized_events),
        logical_event_count=counters.logical,
        duplicate_physical_event_count=counters.duplicates,
        terminated_event_count=counters.terminated,
        filtered_event_count=counters.filtered,
        accepted_event_count=counters.accepted,
        ignored_event_count=counters.ignored,
        emitted_relations=emitted_relations,
        reductions=reduction_relations,
        states=state_relations,
    )


def _execute_block(
    block: ActionBlock,
    *,
    path: str,
    spec: ActionSpec,
    event: Mapping[str, object],
    parameters: Mapping[str, object],
    values: dict[str, object],
    states: dict[str, dict[tuple[object, ...], object]],
    reductions: dict[str, dict[tuple[object, ...], object]],
    emitted: dict[str, list[tuple[object, ...]]],
    emit_policies: Mapping[str, _EmitRuntimePolicy],
    emit_selection_scopes: dict[str, set[tuple[object, ...]]],
    state_specs: Mapping[str, ActionStateSpec],
    reduction_specs,
    emit_specs: Mapping[str, ActionEmitSpec],
    discharged_termination_proofs: frozenset[str],
) -> _Control:
    for index, statement in enumerate(block.operations):
        statement_path = f"{path}.operations[{index}]"
        if isinstance(statement, ActionStaticLoop):
            for iteration in range(statement.trip_count):
                nested_values = dict(values)
                control = _execute_block(
                    statement.body,
                    path=f"{statement_path}.body[{iteration}]",
                    spec=spec,
                    event=event,
                    parameters=parameters,
                    values=nested_values,
                    states=states,
                    reductions=reductions,
                    emitted=emitted,
                    emit_policies=emit_policies,
                    emit_selection_scopes=emit_selection_scopes,
                    state_specs=state_specs,
                    reduction_specs=reduction_specs,
                    emit_specs=emit_specs,
                    discharged_termination_proofs=discharged_termination_proofs,
                )
                if control.kind != "continue":
                    return control
            continue
        control = _execute_op(
            statement,
            path=statement_path,
            spec=spec,
            event=event,
            parameters=parameters,
            values=values,
            states=states,
            reductions=reductions,
            emitted=emitted,
            emit_policies=emit_policies,
            emit_selection_scopes=emit_selection_scopes,
            state_specs=state_specs,
            reduction_specs=reduction_specs,
            emit_specs=emit_specs,
            discharged_termination_proofs=discharged_termination_proofs,
        )
        if control.kind != "continue":
            return control
    return _CONTINUE


def _execute_op(
    op: ActionOp,
    *,
    path: str,
    spec: ActionSpec,
    event: Mapping[str, object],
    parameters: Mapping[str, object],
    values: dict[str, object],
    states: dict[str, dict[tuple[object, ...], object]],
    reductions: dict[str, dict[tuple[object, ...], object]],
    emitted: dict[str, list[tuple[object, ...]]],
    emit_policies: Mapping[str, _EmitRuntimePolicy],
    emit_selection_scopes: dict[str, set[tuple[object, ...]]],
    state_specs: Mapping[str, ActionStateSpec],
    reduction_specs,
    emit_specs: Mapping[str, ActionEmitSpec],
    discharged_termination_proofs: frozenset[str],
) -> _Control:
    inputs = [values[name] for name in op.inputs]
    opcode = op.opcode
    outputs: tuple[object, ...] = ()
    if opcode == "load_event":
        outputs = (event[str(op.attribute("field"))],)
    elif opcode == "load_param":
        outputs = (parameters[str(op.attribute("field"))],)
    elif opcode == "const":
        literal = op.attribute("literal")
        assert isinstance(literal, ActionScalarLiteral)
        outputs = (literal.to_python(),)
    elif opcode == "compare":
        outputs = (_compare(inputs[0], inputs[1], str(op.attribute("predicate"))),)
    elif opcode == "bool_and":
        outputs = (bool(inputs[0]) and bool(inputs[1]),)
    elif opcode == "bool_or":
        outputs = (bool(inputs[0]) or bool(inputs[1]),)
    elif opcode == "bool_not":
        outputs = (not bool(inputs[0]),)
    elif opcode in {"add", "sub", "mul", "min", "max"}:
        outputs = (
            _arithmetic(opcode, inputs[0], inputs[1], op.outputs[0].value_type, spec),
        )
    elif opcode == "select":
        outputs = (inputs[1] if bool(inputs[0]) else inputs[2],)
    elif opcode == "cast":
        outputs = (_coerce_value(op.outputs[0].value_type, inputs[0], spec, path),)
    elif opcode == "state_read":
        state = state_specs[str(op.attribute("state"))]
        key = _field_key(state.key_fields, event, parameters)
        outputs = (states[state.name].get(key, state.initial_value.to_python()),)
    elif opcode == "state_write":
        state = state_specs[str(op.attribute("state"))]
        key = _field_key(state.key_fields, event, parameters)
        states[state.name][key] = _coerce_value(state.value_type, inputs[0], spec, path)
    elif opcode == "filter":
        if not bool(inputs[0]):
            return _Control("filter")
    elif opcode == "reduce":
        reduction = reduction_specs[str(op.attribute("reduction"))]
        key = _field_key(reduction.key_fields, event, parameters)
        current = reductions[reduction.name].get(key, reduction.identity.to_python())
        value = None if reduction.operator is ReductionOperator.COUNT else inputs[0]
        reductions[reduction.name][key] = _apply_reduction(
            reduction.operator,
            current,
            value,
            reduction.value_type,
            spec,
            path,
        )
    elif opcode == "emit":
        emit = emit_specs[str(op.attribute("emit"))]
        row = tuple(
            _coerce_value(field.value_type, value, spec, path)
            for field, value in zip(emit.record_type.fields, inputs, strict=True)
        )
        _apply_emit(
            emit,
            row,
            rows=emitted[emit.name],
            policy=emit_policies[emit.name],
            selection_scopes=emit_selection_scopes[emit.name],
            path=path,
        )
    elif opcode in {"accept", "ignore"}:
        return _Control(opcode)
    elif opcode == "terminate":
        proof_name = str(op.attribute("proof"))
        if proof_name not in discharged_termination_proofs:
            _fail(
                "termination_proof_not_discharged",
                path,
                f"proof {proof_name!r} was declared but not discharged for this execution",
            )
        return _Control("terminate", proof_name)
    else:
        _fail("unreachable_unverified_opcode", path, opcode)

    for output, value in zip(op.outputs, outputs, strict=True):
        values[output.name] = _coerce_value(output.value_type, value, spec, path)
    return _CONTINUE


def _apply_emit(
    emit: ActionEmitSpec,
    row: tuple[object, ...],
    *,
    rows: list[tuple[object, ...]],
    policy: _EmitRuntimePolicy,
    selection_scopes: set[tuple[object, ...]],
    path: str,
) -> None:
    selection = emit.selection
    if selection is None:
        if len(rows) >= policy.capacity:
            _fail(
                "emit_capacity_exceeded",
                path,
                f"emit {emit.name!r} exceeded verified capacity",
            )
        rows.append(row)
        return

    assert policy.selection_limit is not None
    assert policy.selection_scope_extent is not None
    field_index = {
        field.name: index for index, field in enumerate(emit.record_type.fields)
    }
    scope = tuple(row[field_index[name]] for name in selection.scope_key_fields)
    if scope not in selection_scopes:
        if len(selection_scopes) >= policy.selection_scope_extent:
            _fail(
                "selection_scope_extent_exceeded",
                path,
                f"emit {emit.name!r} observed more scopes than {selection.scope_extent.value}",
            )
        selection_scopes.add(scope)

    limit = policy.selection_limit
    if limit == 0:
        return
    group_indices = [
        index
        for index, existing in enumerate(rows)
        if tuple(existing[field_index[name]] for name in selection.scope_key_fields)
        == scope
    ]
    if len(group_indices) < limit:
        if len(rows) >= policy.capacity:
            _fail(
                "emit_capacity_exceeded",
                path,
                f"emit {emit.name!r} exceeded verified selected capacity",
            )
        rows.append(row)
        return

    worst_index = max(
        group_indices,
        key=cmp_to_key(
            lambda left_index, right_index: _compare_rows_by_keys(
                emit,
                selection.order_keys,
                rows[left_index],
                rows[right_index],
            )
        ),
    )
    if _compare_rows_by_keys(emit, selection.order_keys, row, rows[worst_index]) < 0:
        rows[worst_index] = row


def _normalize_record(
    record_type: ActionRecordType,
    row: object,
    *,
    spec: ActionSpec,
    path: str,
) -> dict[str, object]:
    if not isinstance(row, Mapping):
        _fail("record_not_mapping", path, "runtime records must be mappings")
    expected = {field.name for field in record_type.fields}
    actual = set(row)
    if actual != expected:
        _fail(
            "record_shape_mismatch",
            path,
            f"expected fields {sorted(expected)!r}, got {sorted(actual)!r}",
        )
    return {
        field.name: _coerce_value(field.value_type, row[field.name], spec, f"{path}.{field.name}")
        for field in record_type.fields
    }


def _coerce_value(
    value_type: ActionValueType,
    value: object,
    spec: ActionSpec,
    path: str,
) -> object:
    if isinstance(value_type, ActionTupleType):
        if not isinstance(value, (tuple, list)) or len(value) != len(value_type.items):
            _fail("tuple_shape_mismatch", path, "tuple value does not match its IR type")
        return tuple(
            _coerce_value(item_type, item, spec, f"{path}[{index}]")
            for index, (item_type, item) in enumerate(zip(value_type.items, value, strict=True))
        )
    if not isinstance(value_type, ActionScalarType):
        _fail("invalid_runtime_type", path, type(value_type).__name__)
    kind = value_type.kind
    if kind is ActionScalarKind.BOOL:
        if not isinstance(value, bool):
            _fail("runtime_type_mismatch", path, "bool value required")
        return value
    if kind in {
        ActionScalarKind.I32,
        ActionScalarKind.I64,
        ActionScalarKind.U32,
        ActionScalarKind.U64,
    }:
        if not isinstance(value, int) or isinstance(value, bool):
            _fail("runtime_type_mismatch", path, "integer value required")
        bits = 32 if kind in {ActionScalarKind.I32, ActionScalarKind.U32} else 64
        if kind in {ActionScalarKind.U32, ActionScalarKind.U64}:
            minimum, maximum = 0, (1 << bits) - 1
        else:
            minimum, maximum = -(1 << (bits - 1)), (1 << (bits - 1)) - 1
        if value < minimum or value > maximum:
            _fail("integer_overflow", path, f"value {value} is outside [{minimum},{maximum}]")
        return value
    if kind in {ActionScalarKind.F32, ActionScalarKind.F64}:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            _fail("runtime_type_mismatch", path, "floating value required")
        number = float(value)
        if math.isnan(number):
            _fail("nan_rejected", path, "NaN is not admitted")
        if math.isinf(number) and not spec.numeric_contract.allow_infinity:
            _fail("infinity_not_admitted", path, "infinity is not admitted")
        if kind is ActionScalarKind.F32:
            try:
                number = struct.unpack(">f", struct.pack(">f", number))[0]
            except OverflowError:
                _fail("float_overflow", path, "value cannot be represented as f32")
        if spec.numeric_contract.normalize_signed_zero and number == 0.0:
            number = 0.0
        return number
    _fail("invalid_runtime_type", path, str(kind))


def _field_key(
    fields: Sequence[str],
    event: Mapping[str, object],
    parameters: Mapping[str, object],
) -> tuple[object, ...]:
    return tuple(event[name] if name in event else parameters[name] for name in fields)


def _compare(left: object, right: object, predicate: str) -> bool:
    if predicate == "eq":
        return left == right
    if predicate == "ne":
        return left != right
    if predicate == "lt":
        return left < right
    if predicate == "le":
        return left <= right
    if predicate == "gt":
        return left > right
    if predicate == "ge":
        return left >= right
    raise AssertionError(predicate)


def _arithmetic(
    opcode: str,
    left: object,
    right: object,
    value_type: ActionValueType,
    spec: ActionSpec,
) -> object:
    if opcode == "add":
        value = left + right
    elif opcode == "sub":
        value = left - right
    elif opcode == "mul":
        value = left * right
    elif opcode == "min":
        value = left if left <= right else right
    else:
        value = left if left >= right else right
    return _coerce_value(value_type, value, spec, f"arithmetic.{opcode}")


def _apply_reduction(
    operator: ReductionOperator,
    current: object,
    value: object | None,
    value_type: ActionValueType,
    spec: ActionSpec,
    path: str,
) -> object:
    if operator is ReductionOperator.COUNT:
        result = current + 1
    elif operator is ReductionOperator.SUM:
        result = current + value
    elif operator is ReductionOperator.ANY:
        result = bool(current) or bool(value)
    elif operator is ReductionOperator.MIN:
        result = current if current <= value else value
    elif operator is ReductionOperator.MAX:
        result = current if current >= value else value
    else:
        raise AssertionError(operator)
    return _coerce_value(value_type, result, spec, path)


def _event_is_terminated(
    event: Mapping[str, object],
    parameters: Mapping[str, object],
    terminated_scopes: set[tuple[str, tuple[object, ...]]],
    proof_specs,
    state_specs: Mapping[str, ActionStateSpec],
) -> bool:
    for proof in proof_specs.values():
        if proof.state_name is None:
            continue
        state = state_specs[proof.state_name]
        key = _field_key(state.key_fields, event, parameters)
        if (proof.name, key) in terminated_scopes:
            return True
    return False


def _finalize_emit(emit: ActionEmitSpec, rows: list[tuple[object, ...]]) -> EmittedRelation:
    finalized = rows
    if emit.duplicate_policy is DuplicatePolicy.COLLAPSE_EXACT_ROWS:
        finalized = list(dict.fromkeys(finalized))
    if emit.order_kind is OutputOrderKind.CANONICAL_ORDER:
        finalized = sorted(finalized, key=cmp_to_key(lambda a, b: _compare_rows(emit, a, b)))
    elif emit.order_kind in {OutputOrderKind.SET, OutputOrderKind.MULTISET}:
        finalized = sorted(finalized, key=_generic_tuple_key)
    return EmittedRelation(
        name=emit.name,
        fields=tuple(field.name for field in emit.record_type.fields),
        rows=tuple(finalized),
        order_kind=emit.order_kind,
    )


def _compare_rows(emit: ActionEmitSpec, left: tuple[object, ...], right: tuple[object, ...]) -> int:
    return _compare_rows_by_keys(emit, emit.order_keys, left, right)


def _compare_rows_by_keys(
    emit: ActionEmitSpec,
    order_keys: Sequence[OrderKey],
    left: tuple[object, ...],
    right: tuple[object, ...],
) -> int:
    field_index = {field.name: index for index, field in enumerate(emit.record_type.fields)}
    for key in order_keys:
        index = field_index[key.field]
        field = emit.record_type.fields[index]
        left_key = _typed_order_key(field.value_type, left[index])
        right_key = _typed_order_key(field.value_type, right[index])
        if left_key < right_key:
            return -1 if key.ascending else 1
        if left_key > right_key:
            return 1 if key.ascending else -1
    return 0


def _typed_order_key(value_type: ActionValueType, value: object):
    if isinstance(value_type, ActionTupleType):
        return tuple(
            _typed_order_key(item_type, item)
            for item_type, item in zip(value_type.items, value, strict=True)
        )
    if value_type.kind is ActionScalarKind.F32:
        return canonical_float32_key(float(value))
    if value_type.kind is ActionScalarKind.F64:
        return canonical_float64_key(float(value))
    return value


def _generic_tuple_key(values: tuple[object, ...]):
    return tuple(_generic_value_key(value) for value in values)


def _generic_value_key(value: object):
    if isinstance(value, tuple):
        return ("tuple", tuple(_generic_value_key(item) for item in value))
    if isinstance(value, bool):
        return ("bool", int(value))
    if isinstance(value, int):
        return ("int", value)
    if isinstance(value, float):
        return ("float", canonical_float64_key(value))
    return (type(value).__name__, repr(value))


def _fail(code: str, path: str, message: str):
    raise ActionExecutionError(ActionExecutionIssue(code, path, message))


__all__ = [
    "ActionExecutionError",
    "ActionExecutionIssue",
    "ActionExecutionResult",
    "EmittedRelation",
    "ReductionRelation",
    "StateRelation",
    "execute_action_reference",
]
