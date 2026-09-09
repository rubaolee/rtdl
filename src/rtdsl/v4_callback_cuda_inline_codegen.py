"""Straight-line verified Callback IR projection into CUDA expressions.

This lowering is deliberately structural.  It accepts only a final effect
preceded by immutable ``let`` bindings whose expressions are pure projection,
construction, selection, comparison, or read-only view loads.  Unsupported
IR fails closed so the caller can retain the ordinary verified Numba leaf.

The caller owns the physical mapping from callback arguments to CUDA values.
This module never inspects application names, source digests, or field names
to select behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping

from .v4_callback_ir import (
    CallbackExpr,
    CallbackFunction,
    CallbackRecord,
    CallbackType,
    EffectKind,
    LetStatement,
    ReturnEffectStatement,
    ScalarKind,
    TypeKind,
    VerifiedCallbackProgram,
)


class CudaInlineLoweringError(ValueError):
    """The verified role is outside the straight-line inline subset."""


@dataclass(frozen=True)
class CudaInlineValue:
    value_type: CallbackType
    leaves: tuple[str, ...]


@dataclass(frozen=True)
class CudaInlineView:
    value_type: CallbackType
    columns: tuple[str, ...]
    length: str


@dataclass(frozen=True)
class CudaInlineProjection:
    effect_kind: EffectKind
    fields: tuple[tuple[str, tuple[str, ...]], ...]
    lines: tuple[str, ...]
    lowering_sha256: str

    def field(self, name: str) -> tuple[str, ...]:
        matches = [value for key, value in self.fields if key == name]
        if len(matches) != 1:
            raise CudaInlineLoweringError(
                f"inline effect field is missing or duplicated: {name}")
        return matches[0]


_SCALAR_C = {
    ScalarKind.BOOL: "bool",
    ScalarKind.I32: "int",
    ScalarKind.U32: "unsigned int",
    ScalarKind.I64: "long long",
    ScalarKind.U64: "unsigned long long",
    ScalarKind.F32: "float",
    ScalarKind.F64: "double",
}

_BUILTIN_FIELDS: Mapping[str, tuple[tuple[str, CallbackType], ...]] = {}


def _scalar(kind: ScalarKind) -> CallbackType:
    return CallbackType(TypeKind.SCALAR, scalar=kind)


def _vector(kind: ScalarKind, lanes: int) -> CallbackType:
    return CallbackType(TypeKind.VECTOR, scalar=kind, lanes=lanes)


_BUILTIN_FIELDS = {
    "Ray3f": (
        ("origin", _vector(ScalarKind.F32, 3)),
        ("direction", _vector(ScalarKind.F32, 3)),
        ("tmin", _scalar(ScalarKind.F32)),
        ("tmax", _scalar(ScalarKind.F32)),
    ),
    "Hit": (
        ("t", _scalar(ScalarKind.F32)),
        ("hit_kind", _scalar(ScalarKind.U32)),
    ),
    "TriangleHit": (
        ("t", _scalar(ScalarKind.F32)),
        ("primitive_index", _scalar(ScalarKind.U32)),
        ("hit_kind", _scalar(ScalarKind.U32)),
        ("barycentrics", _vector(ScalarKind.F32, 2)),
    ),
    "Aabb3f": (
        ("lower", _vector(ScalarKind.F32, 3)),
        ("upper", _vector(ScalarKind.F32, 3)),
    ),
}


def cuda_inline_value(
    value_type: CallbackType, *leaves: str,
) -> CudaInlineValue:
    return CudaInlineValue(value_type, tuple(leaves))


def cuda_inline_view(
    value_type: CallbackType, columns: tuple[str, ...], length: str,
) -> CudaInlineView:
    return CudaInlineView(value_type, tuple(columns), length)


def _fields(
    value_type: CallbackType,
    records: Mapping[str, CallbackRecord],
) -> tuple[tuple[str, CallbackType], ...]:
    if value_type.kind is TypeKind.RECORD:
        record = records.get(str(value_type.name))
        if record is None:
            raise CudaInlineLoweringError(
                f"inline record is absent: {value_type.name}")
        return tuple((item.name, item.value_type) for item in record.fields)
    if value_type.kind is TypeKind.BUILTIN:
        try:
            return _BUILTIN_FIELDS[str(value_type.name)]
        except KeyError as error:
            raise CudaInlineLoweringError(
                f"inline builtin is unsupported: {value_type.name}") from error
    if value_type.kind is TypeKind.VECTOR:
        names = ("x", "y", "z", "w")[:value_type.lanes]
        assert value_type.scalar is not None
        return tuple((name, _scalar(value_type.scalar)) for name in names)
    raise CudaInlineLoweringError(
        f"inline field access is unsupported for {value_type.kind.value}")


def _leaf_kinds(
    value_type: CallbackType,
    records: Mapping[str, CallbackRecord],
) -> tuple[ScalarKind, ...]:
    if value_type.kind is TypeKind.SCALAR:
        assert value_type.scalar is not None
        return (value_type.scalar,)
    if value_type.kind is TypeKind.VECTOR:
        assert value_type.scalar is not None
        return (value_type.scalar,) * value_type.lanes
    result: list[ScalarKind] = []
    for _, field_type in _fields(value_type, records):
        result.extend(_leaf_kinds(field_type, records))
    return tuple(result)


def _field_value(
    value: CudaInlineValue,
    name: str,
    records: Mapping[str, CallbackRecord],
) -> CudaInlineValue:
    offset = 0
    for field_name, field_type in _fields(value.value_type, records):
        width = len(_leaf_kinds(field_type, records))
        if field_name == name:
            return CudaInlineValue(
                field_type, value.leaves[offset:offset + width])
        offset += width
    raise CudaInlineLoweringError(f"inline field is absent: {name}")


def _literal(value_type: CallbackType, value: object) -> CudaInlineValue:
    if value_type.kind is not TypeKind.SCALAR or value_type.scalar is None:
        raise CudaInlineLoweringError("inline literal must be scalar")
    kind = value_type.scalar
    if kind is ScalarKind.BOOL:
        code = "true" if bool(value) else "false"
    elif kind is ScalarKind.F32:
        code = f"{float(value).hex()}f"
    elif kind is ScalarKind.F64:
        code = float(value).hex()
    elif kind is ScalarKind.U32:
        code = f"{int(value)}u"
    elif kind is ScalarKind.U64:
        code = f"{int(value)}ull"
    elif kind is ScalarKind.I64:
        code = f"{int(value)}ll"
    else:
        code = str(int(value))
    return CudaInlineValue(value_type, (code,))


class _Emitter:
    def __init__(
        self,
        verified: VerifiedCallbackProgram,
        arguments: Mapping[str, CudaInlineValue | CudaInlineView],
        *,
        prefix: str,
        failure_statement: str,
    ) -> None:
        self.records = {
            item.name: item for item in verified.program.records
        }
        self.environment: dict[str, CudaInlineValue | CudaInlineView] = dict(
            arguments)
        self.environment.update({
            item.name: _literal(item.value_type, item.value)
            for item in verified.program.manifest.constants
        })
        self.prefix = prefix
        self.failure_statement = failure_statement
        self.lines: list[str] = []
        self.checked_bounds: set[tuple[str, str]] = set()
        self.binding_index = 0

    def expression(self, expression: CallbackExpr) -> CudaInlineValue | CudaInlineView:
        op = expression.opcode
        attributes = dict(expression.attributes)
        if op in {"argument", "local", "constant"}:
            name = str(attributes["name"])
            try:
                return self.environment[name]
            except KeyError as error:
                raise CudaInlineLoweringError(
                    f"inline environment value is absent: {name}") from error
        if op == "literal":
            return _literal(expression.value_type, attributes["value"])
        if op == "field":
            base = self.expression(expression.operands[0])
            if not isinstance(base, CudaInlineValue):
                raise CudaInlineLoweringError("inline field base is a view")
            return _field_value(base, str(attributes["name"]), self.records)
        if op == "construct":
            values = [self.expression(item) for item in expression.operands]
            if any(not isinstance(item, CudaInlineValue) for item in values):
                raise CudaInlineLoweringError("inline construct contains a view")
            leaves = tuple(
                leaf for item in values for leaf in item.leaves  # type: ignore[union-attr]
            )
            if len(leaves) != len(_leaf_kinds(expression.value_type, self.records)):
                raise CudaInlineLoweringError("inline construct layout differs")
            return CudaInlineValue(expression.value_type, leaves)
        if op == "view_load":
            view = self.expression(expression.operands[0])
            index = self.expression(expression.operands[1])
            if not isinstance(view, CudaInlineView) \
                    or not isinstance(index, CudaInlineValue) \
                    or len(index.leaves) != 1:
                raise CudaInlineLoweringError("inline view load shape differs")
            index_code = index.leaves[0]
            bound = (index_code, view.length)
            if bound not in self.checked_bounds:
                self.lines.append(
                    "if ((unsigned long long)(%s) >= "
                    "(unsigned long long)(%s)) { %s }"
                    % (index_code, view.length, self.failure_statement))
                self.checked_bounds.add(bound)
            leaves = tuple(f"{column}[{index_code}]" for column in view.columns)
            if len(leaves) != len(_leaf_kinds(expression.value_type, self.records)):
                raise CudaInlineLoweringError("inline view column layout differs")
            return CudaInlineValue(expression.value_type, leaves)
        operands = [self.expression(item) for item in expression.operands]
        if any(not isinstance(item, CudaInlineValue) for item in operands):
            raise CudaInlineLoweringError(f"inline {op} contains a view")
        values = [item for item in operands if isinstance(item, CudaInlineValue)]
        if op in {"eq", "ne", "lt", "le", "gt", "ge"}:
            if len(values) != 2 or any(len(item.leaves) != 1 for item in values):
                raise CudaInlineLoweringError(f"inline comparison shape differs: {op}")
            operator = {
                "eq": "==", "ne": "!=", "lt": "<", "le": "<=",
                "gt": ">", "ge": ">=",
            }[op]
            return CudaInlineValue(
                expression.value_type,
                (f"({values[0].leaves[0]} {operator} {values[1].leaves[0]})",),
            )
        if op == "select":
            if len(values) != 3 or len(values[0].leaves) != 1 \
                    or len(values[1].leaves) != len(values[2].leaves):
                raise CudaInlineLoweringError("inline select shape differs")
            condition = values[0].leaves[0]
            return CudaInlineValue(
                expression.value_type,
                tuple(
                    f"({condition} ? {left} : {right})"
                    for left, right in zip(values[1].leaves, values[2].leaves)
                ),
            )
        raise CudaInlineLoweringError(
            f"inline opcode is unsupported: {expression.opcode}")

    def bind(self, name: str, expression: CallbackExpr) -> None:
        value = self.expression(expression)
        if not isinstance(value, CudaInlineValue):
            raise CudaInlineLoweringError("inline let cannot bind a view")
        kinds = _leaf_kinds(value.value_type, self.records)
        leaves: list[str] = []
        self.binding_index += 1
        for index, (kind, expression_code) in enumerate(zip(kinds, value.leaves)):
            local = (
                f"_rtdl_inline_{self.prefix}_let_{self.binding_index}_{index}")
            self.lines.append(
                f"const {_SCALAR_C[kind]} {local} = {expression_code};")
            leaves.append(local)
        self.environment[name] = CudaInlineValue(
            value.value_type, tuple(leaves))


def lower_straight_line_effect_to_cuda(
    verified: VerifiedCallbackProgram,
    function: CallbackFunction,
    arguments: Mapping[str, CudaInlineValue | CudaInlineView],
    *,
    prefix: str,
    failure_statement: str,
) -> CudaInlineProjection:
    """Lower one verified, immutable, straight-line role or reject it."""

    if not isinstance(verified, VerifiedCallbackProgram):
        raise CudaInlineLoweringError("verified callback program is required")
    if function not in verified.program.functions or function.role is None:
        raise CudaInlineLoweringError("function is not owned by the verified program")
    if set(arguments) != {item.name for item in function.arguments}:
        raise CudaInlineLoweringError("inline argument mapping differs")
    for argument in function.arguments:
        mapped = arguments[argument.name]
        if mapped.value_type != argument.value_type:
            raise CudaInlineLoweringError(
                f"inline argument type differs: {argument.name}")
    if not function.body or not isinstance(
            function.body[-1], ReturnEffectStatement):
        raise CudaInlineLoweringError("inline role needs one final effect")
    if any(not isinstance(item, LetStatement) for item in function.body[:-1]):
        raise CudaInlineLoweringError(
            "inline role admits only immutable straight-line lets")

    emitter = _Emitter(
        verified, arguments, prefix=prefix,
        failure_statement=failure_statement)
    for statement in function.body[:-1]:
        assert isinstance(statement, LetStatement)
        emitter.bind(statement.name, statement.value)
    terminal = function.body[-1]
    assert isinstance(terminal, ReturnEffectStatement)
    fields: list[tuple[str, tuple[str, ...]]] = []
    for name, expression in terminal.effect.fields:
        value = emitter.expression(expression)
        if not isinstance(value, CudaInlineValue):
            raise CudaInlineLoweringError("inline effect cannot return a view")
        fields.append((name, value.leaves))
    canonical = json.dumps({
        "effect": terminal.effect.kind.value,
        "fields": fields,
        "lines": emitter.lines,
        "role": function.role.value,
        "verified_ir": verified.ir_sha256,
    }, sort_keys=True, separators=(",", ":"))
    return CudaInlineProjection(
        effect_kind=terminal.effect.kind,
        fields=tuple(fields),
        lines=tuple(emitter.lines),
        lowering_sha256=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    )


__all__ = [
    "CudaInlineLoweringError",
    "CudaInlineProjection",
    "CudaInlineValue",
    "CudaInlineView",
    "cuda_inline_value",
    "cuda_inline_view",
    "lower_straight_line_effect_to_cuda",
]
