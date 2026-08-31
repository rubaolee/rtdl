"""Deterministic CPU semantics for verified V4 Callback IR v1."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import struct
from typing import Mapping, Sequence

import numpy as np

from .v4_callback_ir import (
    AABB3F, BOOL, F32, F64, HIT, TRIANGLE_HIT, I32, I64, RAY3F, U32, U64, VEC2F32,
    CallbackEffect, CallbackExpr, CallbackFunction, CallbackProgramSpec,
    CallbackRecord, CallbackRole, CallbackStatement, CallbackType, EffectKind,
    IfStatement, LetStatement, ReturnEffectStatement, ReturnValueStatement,
    RuntimeStatus, ScalarKind, SetStatement, StaticForStatement, TypeKind,
    VerifiedCallbackProgram, verify_callback_program,
)


class CallbackRuntimeError(RuntimeError):
    def __init__(self, status: RuntimeStatus, path: str, message: str) -> None:
        self.status = status
        self.path = path
        self.message = message
        super().__init__(f"V4 callback execution failed: {status.value}@{path}: {message}")


@dataclass(frozen=True)
class RuntimeRecord:
    type_name: str
    fields: tuple[tuple[str, object], ...]

    def field(self, name: str) -> object:
        for key, value in self.fields:
            if key == name:
                return value
        _runtime_fail(RuntimeStatus.ABI_MISMATCH, self.type_name, f"unknown field {name}")
        raise AssertionError

    def to_dict(self) -> dict[str, object]:
        return {"type": self.type_name, "fields": {key: _semantic_value(value) for key, value in self.fields}}


@dataclass(frozen=True)
class RuntimeEffect:
    kind: EffectKind
    fields: tuple[tuple[str, object], ...]

    def field(self, name: str) -> object:
        for key, value in self.fields:
            if key == name:
                return value
        _runtime_fail(RuntimeStatus.INVALID_EFFECT, self.kind.value, f"unknown field {name}")
        raise AssertionError

    def to_dict(self) -> dict[str, object]:
        return {"kind": self.kind.value, "fields": {key: _semantic_value(value) for key, value in self.fields}}


@dataclass(frozen=True)
class CallbackExecutionResult:
    role: CallbackRole
    effect: RuntimeEffect
    semantic_sha256: str
    executed_statement_count: int
    executed_static_iterations: int
    helper_invocation_count: int
    status: RuntimeStatus = RuntimeStatus.OK

    def to_dict(self) -> dict[str, object]:
        return {
            "role": self.role.value,
            "effect": self.effect.to_dict(),
            "semantic_sha256": self.semantic_sha256,
            "executed_statement_count": self.executed_statement_count,
            "executed_static_iterations": self.executed_static_iterations,
            "helper_invocation_count": self.helper_invocation_count,
            "status": self.status.value,
        }


@dataclass
class _Counters:
    statements: int = 0
    static_iterations: int = 0
    helper_calls: int = 0


@dataclass(frozen=True)
class _Return:
    effect: RuntimeEffect | None = None
    value: object | None = None


def execute_callback_role(
    program: CallbackProgramSpec | VerifiedCallbackProgram,
    role: CallbackRole,
    arguments: Mapping[str, object],
) -> CallbackExecutionResult:
    """Execute one role using exact, deterministic Callback IR semantics."""

    verified = program if isinstance(program, VerifiedCallbackProgram) else verify_callback_program(program)
    spec = verified.program
    function = spec.function_for_role(role)
    records = {item.name: item for item in spec.records}
    constants = {
        item.name: _normalize_value(item.value, item.value_type, records, f"constants.{item.name}")
        for item in spec.manifest.constants
    }
    expected_names = {item.name for item in function.arguments}
    if set(arguments) != expected_names:
        _runtime_fail(RuntimeStatus.ABI_MISMATCH, role.value, "callback argument names mismatch")
    environment = dict(constants)
    for item in function.arguments:
        environment[item.name] = _normalize_value(
            arguments[item.name], item.value_type, records, f"{role.value}.{item.name}"
        )
    counters = _Counters()
    helpers = {item.name: item for item in spec.functions if item.is_helper}
    outcome = _execute_statements(
        function.body, environment, function=function, helpers=helpers,
        records=records, constants=constants, counters=counters, path=role.value,
    )
    if outcome is None or outcome.effect is None:
        _runtime_fail(RuntimeStatus.INVALID_EFFECT, role.value, "role did not return an effect")
    effect = _validate_effect(outcome.effect, role, spec, records)
    semantic = {"role": role.value, "effect": effect.to_dict(), "ir_sha256": verified.ir_sha256}
    digest = hashlib.sha256(
        json.dumps(semantic, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return CallbackExecutionResult(
        role=role,
        effect=effect,
        semantic_sha256=digest,
        executed_statement_count=counters.statements,
        executed_static_iterations=counters.static_iterations,
        helper_invocation_count=counters.helper_calls,
    )


def _execute_statements(
    statements: Sequence[CallbackStatement],
    environment: dict[str, object],
    *,
    function: CallbackFunction,
    helpers: Mapping[str, CallbackFunction],
    records: Mapping[str, CallbackRecord],
    constants: Mapping[str, object],
    counters: _Counters,
    path: str,
) -> _Return | None:
    for index, statement in enumerate(statements):
        counters.statements += 1
        item_path = f"{path}[{index}]"
        if isinstance(statement, LetStatement):
            environment[statement.name] = _eval_expr(
                statement.value, environment, helpers, records, constants, counters, item_path
            )
        elif isinstance(statement, SetStatement):
            if statement.name not in environment:
                _runtime_fail(RuntimeStatus.ABI_MISMATCH, item_path, statement.name)
            environment[statement.name] = _eval_expr(
                statement.value, environment, helpers, records, constants, counters, item_path
            )
        elif isinstance(statement, IfStatement):
            condition = _eval_expr(
                statement.condition, environment, helpers, records, constants, counters, item_path
            )
            selected = statement.then_body if bool(condition) else statement.else_body
            outcome = _execute_statements(
                selected, environment, function=function, helpers=helpers,
                records=records, constants=constants, counters=counters, path=item_path,
            )
            if outcome is not None:
                return outcome
        elif isinstance(statement, StaticForStatement):
            for loop_index in range(statement.trip_count):
                counters.static_iterations += 1
                environment[statement.index_name] = _checked_integer(loop_index, U32, item_path)
                outcome = _execute_statements(
                    statement.body, environment, function=function, helpers=helpers,
                    records=records, constants=constants, counters=counters,
                    path=f"{item_path}.iteration[{loop_index}]",
                )
                if outcome is not None:
                    return outcome
            environment.pop(statement.index_name, None)
        elif isinstance(statement, ReturnEffectStatement):
            fields = tuple(
                (
                    name,
                    _eval_expr(
                        value, environment, helpers, records, constants, counters,
                        f"{item_path}.{name}",
                    ),
                )
                for name, value in statement.effect.fields
            )
            return _Return(effect=RuntimeEffect(statement.effect.kind, fields))
        elif isinstance(statement, ReturnValueStatement):
            return _Return(value=_eval_expr(
                statement.value, environment, helpers, records, constants, counters, item_path
            ))
        else:
            raise AssertionError(type(statement))
    return None


def _eval_expr(
    expression: CallbackExpr,
    environment: Mapping[str, object],
    helpers: Mapping[str, CallbackFunction],
    records: Mapping[str, CallbackRecord],
    constants: Mapping[str, object],
    counters: _Counters,
    path: str,
) -> object:
    op = expression.opcode
    attrs = dict(expression.attributes)
    if op in {"argument", "local", "constant"}:
        name = str(attrs["name"])
        if name not in environment:
            _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, f"missing value {name}")
        return environment[name]
    if op == "literal":
        return _normalize_value(attrs["value"], expression.value_type, records, path)
    operands = tuple(
        _eval_expr(item, environment, helpers, records, constants, counters, path)
        for item in expression.operands
    )
    if op == "field":
        base = operands[0]
        name = str(attrs["name"])
        if isinstance(base, RuntimeRecord): return base.field(name)
        if isinstance(base, Mapping):
            if name not in base: _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, name)
            return base[name]
        if isinstance(base, tuple) and name in "xyzw": return base["xyzw".index(name)]
        _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, f"field {name} is unavailable")
    if op == "view_load":
        view, index = operands
        integer_index = int(index)
        if not isinstance(view, tuple) or not 0 <= integer_index < len(view):
            _runtime_fail(RuntimeStatus.VIEW_OUT_OF_BOUNDS, path, str(integer_index))
        return view[integer_index]
    if op in {"add", "sub", "mul", "div", "min", "max"}:
        return _numeric_binary(op, operands[0], operands[1], expression.value_type, path)
    if op in {"bit_and", "bit_or", "bit_xor", "shift_left", "shift_right"}:
        return _integer_binary(op, int(operands[0]), int(operands[1]), expression.value_type, path)
    if op in {"neg", "abs"}:
        return _numeric_unary(op, operands[0], expression.value_type, path)
    if op == "not": return not bool(operands[0])
    if op == "and": return all(bool(item) for item in operands)
    if op == "or": return any(bool(item) for item in operands)
    if op in {"eq", "ne", "lt", "le", "gt", "ge"}:
        left, right = operands
        return {
            "eq": left == right, "ne": left != right, "lt": left < right,
            "le": left <= right, "gt": left > right, "ge": left >= right,
        }[op]
    if op == "select": return operands[1] if bool(operands[0]) else operands[2]
    if op == "sqrt": return _sqrt(operands[0], expression.value_type, path)
    if op == "isfinite": return _isfinite(operands[0])
    if op == "dot":
        left, right = operands
        result: object = _normalize_value(0.0, expression.value_type, records, path)
        for a, b in zip(left, right):
            result = _numeric_binary(
                "add", result, _numeric_binary("mul", a, b, expression.value_type, path),
                expression.value_type, path,
            )
        return result
    if op == "construct":
        names = attrs["field_names"]
        if expression.value_type.kind is TypeKind.RECORD:
            return RuntimeRecord(expression.value_type.name or "", tuple(zip(names, operands)))
        return tuple(operands)
    if op == "helper_call":
        name = str(attrs["name"])
        helper = helpers.get(name)
        if helper is None:
            _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, f"unknown helper {name}")
        counters.helper_calls += 1
        # Helpers may read manifest-frozen constants, but never inherit caller
        # locals.  This keeps helper semantics lexical, deterministic and
        # identical to the verified frontend environment.
        helper_environment = dict(constants)
        helper_environment.update(
            {item.name: value for item, value in zip(helper.arguments, operands)}
        )
        outcome = _execute_statements(
            helper.body, helper_environment, function=helper, helpers=helpers,
            records=records, constants=constants, counters=counters,
            path=f"helper.{name}",
        )
        if outcome is None or outcome.effect is not None:
            _runtime_fail(RuntimeStatus.INVALID_EFFECT, path, f"helper {name} did not return a value")
        return outcome.value
    raise AssertionError(op)


def _validate_effect(
    effect: RuntimeEffect,
    role: CallbackRole,
    program: CallbackProgramSpec,
    records: Mapping[str, CallbackRecord],
) -> RuntimeEffect:
    fields = dict(effect.fields)
    for name, value in fields.items():
        if not _isfinite(value):
            _runtime_fail(RuntimeStatus.NONFINITE_RESULT, f"{role.value}.{name}", "effect contains nonfinite data")
    if effect.kind is EffectKind.AABB:
        lower, upper = fields["lower"], fields["upper"]
        if len(lower) != 3 or len(upper) != 3 or any(a > b for a, b in zip(lower, upper)):
            _runtime_fail(RuntimeStatus.INVALID_AABB, role.value, "AABB must be finite and ordered")
    elif effect.kind is EffectKind.TRACE_REQUEST:
        origin, direction = fields["origin"], fields["direction"]
        tmin, tmax = float(fields["tmin"]), float(fields["tmax"])
        if len(origin) != 3 or len(direction) != 3 or all(float(item) == 0.0 for item in direction) \
                or not (0.0 <= tmin < tmax):
            _runtime_fail(RuntimeStatus.INVALID_TRACE_REQUEST, role.value, "invalid finite ray interval/direction")
    elif effect.kind is EffectKind.HIT:
        if not 0 <= int(fields["hit_kind"]) <= 127:
            _runtime_fail(RuntimeStatus.INVALID_EFFECT, role.value, "custom hit kind must be in [0,127]")
        attributes = fields["attributes"]
        if not isinstance(attributes, tuple) or len(attributes) != len(program.manifest.attribute_types):
            _runtime_fail(RuntimeStatus.INVALID_EFFECT, role.value, "attribute layout mismatch")
    return effect


def _normalize_value(
    value: object,
    value_type: CallbackType,
    records: Mapping[str, CallbackRecord],
    path: str,
) -> object:
    if value_type.kind is TypeKind.SCALAR:
        if value_type.scalar is ScalarKind.BOOL:
            if not isinstance(value, bool): _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, "bool required")
            return value
        if value_type.scalar in {ScalarKind.I32, ScalarKind.U32, ScalarKind.I64, ScalarKind.U64}:
            if not isinstance(value, int) or isinstance(value, bool):
                _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, "integer required")
            return _checked_integer(value, value_type, path)
        if not isinstance(value, (int, float, np.floating)) or isinstance(value, bool):
            _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, "floating value required")
        result = np.float32(value) if value_type == F32 else float(value)
        if not math.isfinite(float(result)):
            _runtime_fail(RuntimeStatus.NONFINITE_INPUT, path, repr(value))
        return result
    if value_type.kind is TypeKind.VECTOR:
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != value_type.lanes:
            _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, "vector length mismatch")
        scalar = CallbackType(TypeKind.SCALAR, scalar=value_type.scalar)
        return tuple(_normalize_value(item, scalar, records, f"{path}[{index}]") for index, item in enumerate(value))
    if value_type.kind is TypeKind.TUPLE:
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != len(value_type.items):
            _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, "tuple length mismatch")
        return tuple(_normalize_value(item, item_type, records, f"{path}[{index}]") for index, (item, item_type) in enumerate(zip(value, value_type.items)))
    if value_type.kind is TypeKind.RECORD:
        record = records[value_type.name or ""]
        if isinstance(value, RuntimeRecord):
            if value.type_name != record.name: _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, "record identity mismatch")
            source = dict(value.fields)
        elif isinstance(value, Mapping): source = dict(value)
        else: _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, "record mapping required")
        if set(source) != {item.name for item in record.fields}:
            _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, "record fields mismatch")
        return RuntimeRecord(record.name, tuple((item.name, _normalize_value(source[item.name], item.value_type, records, f"{path}.{item.name}")) for item in record.fields))
    if value_type.kind is TypeKind.READ_ONLY_VIEW:
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, "read-only view sequence required")
        return tuple(_normalize_value(item, value_type.items[0], records, f"{path}[{index}]") for index, item in enumerate(value))
    if value_type == RAY3F:
        if not isinstance(value, Mapping): _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, "Ray3f mapping required")
        required = {"origin", "direction", "tmin", "tmax"}
        if set(value) != required: _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, "Ray3f fields mismatch")
        return {
            "origin": _normalize_value(value["origin"], CallbackType(TypeKind.VECTOR, scalar=ScalarKind.F32, lanes=3), records, path),
            "direction": _normalize_value(value["direction"], CallbackType(TypeKind.VECTOR, scalar=ScalarKind.F32, lanes=3), records, path),
            "tmin": _normalize_value(value["tmin"], F32, records, path),
            "tmax": _normalize_value(value["tmax"], F32, records, path),
        }
    if value_type == HIT:
        if not isinstance(value, Mapping) or set(value) != {"t", "hit_kind"}:
            _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, "Hit mapping required")
        return {"t": _normalize_value(value["t"], F32, records, path), "hit_kind": _normalize_value(value["hit_kind"], U32, records, path)}
    if value_type == TRIANGLE_HIT:
        required = {"t", "primitive_index", "hit_kind", "barycentrics"}
        if not isinstance(value, Mapping) or set(value) != required:
            _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, "TriangleHit mapping required")
        return {
            "t": _normalize_value(value["t"], F32, records, f"{path}.t"),
            "primitive_index": _normalize_value(
                value["primitive_index"], U32, records, f"{path}.primitive_index"
            ),
            "hit_kind": _normalize_value(value["hit_kind"], U32, records, f"{path}.hit_kind"),
            "barycentrics": _normalize_value(
                value["barycentrics"], VEC2F32, records, f"{path}.barycentrics"
            ),
        }
    if value_type == AABB3F:
        if not isinstance(value, Mapping) or set(value) != {"lower", "upper"}:
            _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, "Aabb3f mapping required")
        return {key: _normalize_value(value[key], CallbackType(TypeKind.VECTOR, scalar=ScalarKind.F32, lanes=3), records, path) for key in ("lower", "upper")}
    _runtime_fail(RuntimeStatus.ABI_MISMATCH, path, value_type.kind.value)
    raise AssertionError


def _numeric_binary(op: str, left: object, right: object, value_type: CallbackType, path: str) -> object:
    if value_type.kind is TypeKind.VECTOR:
        scalar = CallbackType(TypeKind.SCALAR, scalar=value_type.scalar)
        return tuple(_numeric_binary(op, a, b, scalar, path) for a, b in zip(left, right))
    if value_type.is_integer:
        if op == "div" and int(right) == 0: _runtime_fail(RuntimeStatus.DIVIDE_BY_ZERO, path, "integer division by zero")
        value = {
            "add": lambda: int(left) + int(right), "sub": lambda: int(left) - int(right),
            "mul": lambda: int(left) * int(right), "div": lambda: int(left) // int(right),
            "min": lambda: min(int(left), int(right)), "max": lambda: max(int(left), int(right)),
        }[op]()
        return _checked_integer(value, value_type, path)
    if op == "div" and float(right) == 0.0:
        _runtime_fail(RuntimeStatus.DIVIDE_BY_ZERO, path, "floating division by zero")
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        value = {
            "add": lambda: left + right, "sub": lambda: left - right,
            "mul": lambda: left * right, "div": lambda: left / right,
            "min": lambda: min(left, right), "max": lambda: max(left, right),
        }[op]()
    result = np.float32(value) if value_type == F32 else float(value)
    if not math.isfinite(float(result)):
        _runtime_fail(RuntimeStatus.NONFINITE_RESULT, path, op)
    return result


def _integer_binary(op: str, left: int, right: int, value_type: CallbackType, path: str) -> int:
    width = 32 if value_type in {I32, U32} else 64
    if op in {"shift_left", "shift_right"} and not 0 <= right < width:
        _runtime_fail(RuntimeStatus.INTEGER_OVERFLOW, path, "invalid shift count")
    value = {
        "bit_and": lambda: left & right, "bit_or": lambda: left | right,
        "bit_xor": lambda: left ^ right, "shift_left": lambda: left << right,
        "shift_right": lambda: left >> right,
    }[op]()
    return _checked_integer(value, value_type, path)


def _numeric_unary(op: str, value: object, value_type: CallbackType, path: str) -> object:
    if value_type.kind is TypeKind.VECTOR:
        scalar = CallbackType(TypeKind.SCALAR, scalar=value_type.scalar)
        return tuple(_numeric_unary(op, item, scalar, path) for item in value)
    result = -value if op == "neg" else abs(value)
    if value_type.is_integer: return _checked_integer(int(result), value_type, path)
    result = np.float32(result) if value_type == F32 else float(result)
    if not math.isfinite(float(result)): _runtime_fail(RuntimeStatus.NONFINITE_RESULT, path, op)
    return result


def _sqrt(value: object, value_type: CallbackType, path: str) -> object:
    if value_type.kind is TypeKind.VECTOR:
        scalar = CallbackType(TypeKind.SCALAR, scalar=value_type.scalar)
        return tuple(_sqrt(item, scalar, path) for item in value)
    if float(value) < 0.0 or not math.isfinite(float(value)):
        _runtime_fail(RuntimeStatus.INVALID_SQRT, path, repr(value))
    result = math.sqrt(float(value))
    return np.float32(result) if value_type == F32 else result


def _checked_integer(value: int, value_type: CallbackType, path: str) -> int:
    bounds = {
        ScalarKind.I32: (-(1 << 31), (1 << 31) - 1), ScalarKind.U32: (0, (1 << 32) - 1),
        ScalarKind.I64: (-(1 << 63), (1 << 63) - 1), ScalarKind.U64: (0, (1 << 64) - 1),
    }
    low, high = bounds[value_type.scalar]
    if not low <= value <= high:
        _runtime_fail(RuntimeStatus.INTEGER_OVERFLOW, path, str(value))
    return value


def _isfinite(value: object) -> bool:
    if isinstance(value, RuntimeRecord): return all(_isfinite(item) for _, item in value.fields)
    if isinstance(value, Mapping): return all(_isfinite(item) for item in value.values())
    if isinstance(value, tuple): return all(_isfinite(item) for item in value)
    if isinstance(value, (float, np.floating)): return math.isfinite(float(value))
    return True


def _semantic_value(value: object) -> object:
    if isinstance(value, RuntimeRecord): return value.to_dict()
    if isinstance(value, Mapping): return {key: _semantic_value(value[key]) for key in sorted(value)}
    if isinstance(value, tuple): return [_semantic_value(item) for item in value]
    if isinstance(value, np.float32):
        bits = struct.unpack(">I", struct.pack(">f", float(value)))[0]
        return {"f32_bits": f"0x{bits:08x}"}
    if isinstance(value, float):
        bits = struct.unpack(">Q", struct.pack(">d", value))[0]
        return {"f64_bits": f"0x{bits:016x}"}
    return value


def _runtime_fail(status: RuntimeStatus, path: str, message: str) -> None:
    raise CallbackRuntimeError(status, path, message)
