"""Goal5749: bounded restricted-Python -> Callback IR -> Numba PTX spike.

This is deliberately *not* the full V4 frontend.  It is the smallest
application-neutral slice that can answer the load-bearing feasibility
question without letting Numba reinterpret user Python.  The authority chain
is:

    source text -> verified Callback IR -> deterministic generated source
                -> isolated Numba C-ABI compilation -> audited PTX

The original source is parsed, never imported or executed.  Only generated
source from the verified IR is executed by the compiler child.
"""

from __future__ import annotations

import ast
import dataclasses
import enum
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np


CALLBACK_POC_SCHEMA = "rtdl.v4.callback_poc.v1"
GENERATED_SOURCE_SCHEMA = "rtdl.v4.generated_numba_leaf.v1"
GENERATED_SCALAR_PROBE_SCHEMA = "rtdl.v4.generated_numba_scalar_probe.v1"


class CallbackRole(str, enum.Enum):
    INTERSECTION = "intersection"
    ANY_HIT = "any_hit"
    MISS = "miss"


class ScalarType(str, enum.Enum):
    F32 = "f32"
    U32 = "u32"


class StatusCode(enum.IntEnum):
    OK = 0
    INVALID_SQRT = 1
    NONFINITE_EFFECT = 2
    U32_OVERFLOW = 3
    ABI_MISMATCH = 4
    CALLBACK_NOT_INVOKED = 5


class EffectKind(str, enum.Enum):
    HIT = "hit"
    NO_HIT = "no_hit"
    ACCEPT_CONTINUE = "accept_continue"
    PAYLOAD = "payload"


class CallbackVerificationError(ValueError):
    pass


class CallbackRuntimeError(RuntimeError):
    def __init__(self, status: StatusCode, message: str):
        super().__init__(message)
        self.status = status


@dataclasses.dataclass(frozen=True)
class RoleSchema:
    arguments: tuple[tuple[str, ScalarType], ...]
    effects: frozenset[EffectKind]


ROLE_SCHEMAS: Mapping[CallbackRole, RoleSchema] = {
    CallbackRole.INTERSECTION: RoleSchema(
        arguments=(
            ("ox", ScalarType.F32), ("oy", ScalarType.F32), ("oz", ScalarType.F32),
            ("dx", ScalarType.F32), ("dy", ScalarType.F32), ("dz", ScalarType.F32),
            ("tmin", ScalarType.F32), ("tmax", ScalarType.F32),
            ("cx", ScalarType.F32), ("cy", ScalarType.F32), ("cz", ScalarType.F32),
            ("radius", ScalarType.F32), ("item_id", ScalarType.U32),
        ),
        effects=frozenset((EffectKind.HIT, EffectKind.NO_HIT)),
    ),
    CallbackRole.ANY_HIT: RoleSchema(
        arguments=(("hit_t", ScalarType.F32), ("hit_id", ScalarType.U32),
                   ("best_t", ScalarType.F32), ("best_id", ScalarType.U32)),
        effects=frozenset((EffectKind.ACCEPT_CONTINUE,)),
    ),
    CallbackRole.MISS: RoleSchema(
        arguments=(("best_t", ScalarType.F32), ("best_id", ScalarType.U32)),
        effects=frozenset((EffectKind.PAYLOAD,)),
    ),
}


@dataclasses.dataclass(frozen=True)
class VerifiedCallbackFunction:
    role: CallbackRole
    name: str
    arguments: tuple[tuple[str, ScalarType], ...]
    body: tuple[ast.stmt, ...] = dataclasses.field(compare=False, repr=False)
    canonical_body: tuple[object, ...]


@dataclasses.dataclass(frozen=True)
class VerifiedCallbackModule:
    schema: str
    functions: tuple[VerifiedCallbackFunction, ...]
    normalized_source: str
    source_sha256: str
    ir_sha256: str

    def function(self, role: CallbackRole) -> VerifiedCallbackFunction:
        matches = [item for item in self.functions if item.role is role]
        if len(matches) != 1:
            raise CallbackVerificationError(f"expected one {role.value} function")
        return matches[0]


@dataclasses.dataclass(frozen=True)
class EffectValue:
    kind: EffectKind
    f0: float = 0.0
    u0: int = 0
    u1: int = 0


@dataclasses.dataclass(frozen=True)
class GeneratedLeaf:
    role: CallbackRole
    abi_name: str
    generated_source: str
    generated_source_sha256: str
    argument_types: tuple[ScalarType, ...]
    numeric_mode: str
    ir_sha256: str
    nonce_word: int


@dataclasses.dataclass(frozen=True)
class GeneratedScalarProbe:
    """Compiler-owned scalar-return ABI probe bound to one verified module.

    Callback effects use the explicit status/out envelope below.  This probe
    separately proves that the frozen Numba C ABI and compiler-owned OptiX
    composition preserve a plain scalar return.  It is generated from verified
    IR identity and is never sourced from or callable by user code.
    """

    abi_name: str
    generated_source: str
    generated_source_sha256: str
    numeric_mode: str
    ir_sha256: str


@dataclasses.dataclass(frozen=True)
class DeviceFunctionArtifact:
    schema: str
    role: str
    abi_name: str
    compute_capability: tuple[int, int]
    numeric_mode: str
    generated_source_sha256: str
    ir_sha256: str
    ptx: str
    ptx_sha256: str
    ptx_version: str
    ptx_target: str
    external_symbols: tuple[str, ...]
    numba_version: str
    python_version: str
    nonce_word: int
    compiler_function_count: int = 1


_ROLE_DECORATORS = {f"optix.{role.value}": role for role in CallbackRole}
_ALLOWED_INTRINSICS = {"optix.sqrt", "optix.hit", "optix.no_hit",
                       "optix.accept_continue", "optix.payload"}
_ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult)
_ALLOWED_CMPOPS = (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq)


def _fail(node: ast.AST | None, message: str) -> None:
    location = ""
    if node is not None and hasattr(node, "lineno"):
        location = f" at line {node.lineno}, column {node.col_offset}"
    raise CallbackVerificationError(message + location)


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _dotted_name(node.value)
        return None if prefix is None else f"{prefix}.{node.attr}"
    return None


def _annotation(node: ast.AST | None) -> ScalarType:
    if not isinstance(node, ast.Name):
        _fail(node, "every argument requires a scalar f32/u32 annotation")
    try:
        return ScalarType(node.id)
    except ValueError:
        _fail(node, f"unsupported scalar annotation {node.id!r}")
        raise AssertionError


def _canonical_expr(node: ast.expr, defined: set[str]) -> object:
    if isinstance(node, ast.Name):
        if node.id not in defined:
            _fail(node, f"undefined value {node.id!r}")
        return ("name", node.id)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            return ("bool", node.value)
        if isinstance(node.value, int) and 0 <= node.value <= 0xFFFFFFFF:
            return ("int", node.value)
        if isinstance(node.value, float) and math.isfinite(node.value):
            return ("float", float(node.value).hex())
        _fail(node, "only finite numeric/bool literals are admitted")
    if isinstance(node, ast.BinOp) and isinstance(node.op, _ALLOWED_BINOPS):
        return (type(node.op).__name__, _canonical_expr(node.left, defined),
                _canonical_expr(node.right, defined))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd, ast.Not)):
        return (type(node.op).__name__, _canonical_expr(node.operand, defined))
    if isinstance(node, ast.Compare) and len(node.ops) == 1 and len(node.comparators) == 1 \
            and isinstance(node.ops[0], _ALLOWED_CMPOPS):
        return (type(node.ops[0]).__name__, _canonical_expr(node.left, defined),
                _canonical_expr(node.comparators[0], defined))
    if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
        return (type(node.op).__name__, tuple(_canonical_expr(v, defined) for v in node.values))
    if isinstance(node, ast.IfExp):
        return ("if", _canonical_expr(node.test, defined),
                _canonical_expr(node.body, defined), _canonical_expr(node.orelse, defined))
    if isinstance(node, ast.Call):
        name = _dotted_name(node.func)
        if name not in _ALLOWED_INTRINSICS:
            _fail(node, f"call to non-RTDL intrinsic {name!r}")
        if name != "optix.sqrt":
            _fail(node, "effect constructors may appear only in return statements")
        if len(node.args) != 1 or node.keywords:
            _fail(node, "optix.sqrt requires one positional argument")
        return ("sqrt", _canonical_expr(node.args[0], defined))
    _fail(node, f"unsupported expression {type(node).__name__}")
    raise AssertionError


def _effect_call(node: ast.expr, role: CallbackRole, defined: set[str]) -> object:
    if not isinstance(node, ast.Call):
        _fail(node, "callback return must be a typed optix effect")
    name = _dotted_name(node.func)
    if name not in _ALLOWED_INTRINSICS or name == "optix.sqrt":
        _fail(node, "callback return must be a typed optix effect")
    effect = EffectKind(name.removeprefix("optix."))
    if effect not in ROLE_SCHEMAS[role].effects:
        _fail(node, f"effect {effect.value} is illegal in {role.value}")
    if node.args:
        _fail(node, "effect fields must be named")
    supplied = {item.arg: _canonical_expr(item.value, defined) for item in node.keywords}
    expected = {
        EffectKind.NO_HIT: (),
        EffectKind.HIT: ("t", "item_id"),
        EffectKind.ACCEPT_CONTINUE: ("best_t", "best_id"),
        EffectKind.PAYLOAD: ("best_t", "best_id"),
    }[effect]
    if tuple(sorted(supplied)) != tuple(sorted(expected)):
        _fail(node, f"{effect.value} requires exactly {expected}")
    return ("return", effect.value, tuple((key, supplied[key]) for key in expected))


def _verify_statements(statements: Sequence[ast.stmt], role: CallbackRole,
                       defined: set[str], *, top_level: bool) -> tuple[tuple[object, ...], set[str], bool]:
    canonical: list[object] = []
    returned = False
    local_defined = set(defined)
    for statement in statements:
        if returned:
            _fail(statement, "unreachable statement after return")
        if isinstance(statement, ast.Assign):
            if len(statement.targets) != 1 or not isinstance(statement.targets[0], ast.Name):
                _fail(statement, "assignment target must be one local name")
            name = statement.targets[0].id
            if name.startswith("_") or name in local_defined:
                _fail(statement, f"local {name!r} is reserved or reassigned; PoC IR is SSA")
            expression = _canonical_expr(statement.value, local_defined)
            local_defined.add(name)
            canonical.append(("assign", name, expression))
        elif isinstance(statement, ast.If):
            if not statement.body or not statement.orelse:
                _fail(statement, "bounded PoC requires explicit if/else returns")
            condition = _canonical_expr(statement.test, local_defined)
            body, _, body_returned = _verify_statements(
                statement.body, role, set(local_defined), top_level=False)
            orelse, _, else_returned = _verify_statements(
                statement.orelse, role, set(local_defined), top_level=False)
            if not body_returned or not else_returned:
                _fail(statement, "both branches must return in the bounded PoC")
            canonical.append(("if", condition, body, orelse))
            returned = True
        elif isinstance(statement, ast.Return):
            if statement.value is None:
                _fail(statement, "callback return requires an effect")
            canonical.append(_effect_call(statement.value, role, local_defined))
            returned = True
        else:
            _fail(statement, f"unsupported statement {type(statement).__name__}")
    if top_level and not returned:
        _fail(statements[-1] if statements else None, "all callback paths must return")
    return tuple(canonical), local_defined, returned


def verify_callback_source(source: str) -> VerifiedCallbackModule:
    """Parse source text without importing/executing it and produce verified IR."""

    if not isinstance(source, str) or not source.strip():
        raise CallbackVerificationError("callback source must be nonempty UTF-8 text")
    try:
        tree = ast.parse(source, mode="exec", type_comments=False)
    except SyntaxError as exc:
        raise CallbackVerificationError(f"invalid callback syntax: {exc}") from exc
    if any(not isinstance(node, ast.FunctionDef) for node in tree.body):
        _fail(next((n for n in tree.body if not isinstance(n, ast.FunctionDef)), None),
              "PoC module admits only callback function definitions")
    functions: list[VerifiedCallbackFunction] = []
    roles: set[CallbackRole] = set()
    for function in tree.body:
        assert isinstance(function, ast.FunctionDef)
        if function.args.vararg or function.args.kwarg or function.args.kwonlyargs \
                or function.args.defaults or function.args.kw_defaults:
            _fail(function, "variadic/default/keyword-only arguments are rejected")
        if len(function.decorator_list) != 1:
            _fail(function, "callback requires exactly one optix role decorator")
        decorator = _dotted_name(function.decorator_list[0])
        if decorator not in _ROLE_DECORATORS:
            _fail(function.decorator_list[0], f"unknown callback role {decorator!r}")
        role = _ROLE_DECORATORS[decorator]
        if role in roles:
            _fail(function, f"duplicate callback role {role.value}")
        roles.add(role)
        arguments = tuple((arg.arg, _annotation(arg.annotation)) for arg in function.args.args)
        if arguments != ROLE_SCHEMAS[role].arguments:
            _fail(function, f"{role.value} ABI mismatch: expected {ROLE_SCHEMAS[role].arguments!r}")
        canonical, _, _ = _verify_statements(
            function.body, role, {name for name, _ in arguments}, top_level=True)
        functions.append(VerifiedCallbackFunction(role, function.name, arguments,
                                                  tuple(function.body), canonical))
    required = set(CallbackRole)
    if roles != required:
        raise CallbackVerificationError(
            f"PoC source requires roles {sorted(r.value for r in required)}; got {sorted(r.value for r in roles)}")
    canonical_module = tuple(
        (item.role.value, item.name,
         tuple((name, kind.value) for name, kind in item.arguments), item.canonical_body)
        for item in sorted(functions, key=lambda value: value.role.value)
    )
    normalized_source = ast.unparse(tree).strip() + "\n"
    source_sha = hashlib.sha256(normalized_source.encode("utf-8")).hexdigest()
    ir_bytes = json.dumps(canonical_module, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ir_sha = hashlib.sha256(ir_bytes).hexdigest()
    return VerifiedCallbackModule(
        CALLBACK_POC_SCHEMA,
        tuple(sorted(functions, key=lambda value: value.role.value)),
        normalized_source,
        source_sha,
        ir_sha,
    )


def _f32(value: Any) -> np.float32:
    return np.float32(value)


def _eval_expr(node: ast.expr, values: Mapping[str, Any]) -> Any:
    if isinstance(node, ast.Name):
        return values[node.id]
    if isinstance(node, ast.Constant):
        if isinstance(node.value, float):
            return _f32(node.value)
        return node.value
    if isinstance(node, ast.BinOp):
        left, right = _eval_expr(node.left, values), _eval_expr(node.right, values)
        # IEEE-754 overflow/nonfinite is part of the checked device semantics,
        # not a host warning channel.  The enclosing effect validation converts
        # it into an explicit StatusCode.
        with np.errstate(over="ignore", invalid="ignore"):
            if isinstance(node.op, ast.Add): return _f32(left + right)
            if isinstance(node.op, ast.Sub): return _f32(left - right)
            if isinstance(node.op, ast.Mult): return _f32(left * right)
    if isinstance(node, ast.UnaryOp):
        value = _eval_expr(node.operand, values)
        if isinstance(node.op, ast.USub): return _f32(-value)
        if isinstance(node.op, ast.UAdd): return value
        if isinstance(node.op, ast.Not): return not bool(value)
    if isinstance(node, ast.Compare):
        left, right = _eval_expr(node.left, values), _eval_expr(node.comparators[0], values)
        op = node.ops[0]
        if isinstance(op, ast.Lt): return left < right
        if isinstance(op, ast.LtE): return left <= right
        if isinstance(op, ast.Gt): return left > right
        if isinstance(op, ast.GtE): return left >= right
        if isinstance(op, ast.Eq): return left == right
        if isinstance(op, ast.NotEq): return left != right
    if isinstance(node, ast.BoolOp):
        items = [_eval_expr(item, values) for item in node.values]
        return all(items) if isinstance(node.op, ast.And) else any(items)
    if isinstance(node, ast.IfExp):
        return _eval_expr(node.body if _eval_expr(node.test, values) else node.orelse, values)
    if isinstance(node, ast.Call) and _dotted_name(node.func) == "optix.sqrt":
        value = _f32(_eval_expr(node.args[0], values))
        if not math.isfinite(float(value)) or value < 0:
            raise CallbackRuntimeError(StatusCode.INVALID_SQRT, "sqrt operand is invalid")
        return _f32(math.sqrt(float(value)))
    raise AssertionError(f"unverified expression {ast.dump(node)}")


def _interpret_statements(statements: Sequence[ast.stmt], values: dict[str, Any]) -> EffectValue:
    for statement in statements:
        if isinstance(statement, ast.Assign):
            values[statement.targets[0].id] = _eval_expr(statement.value, values)
        elif isinstance(statement, ast.If):
            selected = statement.body if _eval_expr(statement.test, values) else statement.orelse
            return _interpret_statements(selected, dict(values))
        elif isinstance(statement, ast.Return):
            call = statement.value
            assert isinstance(call, ast.Call)
            kind = EffectKind(_dotted_name(call.func).removeprefix("optix."))
            fields = {item.arg: _eval_expr(item.value, values) for item in call.keywords}
            f0 = float(fields.get("t", fields.get("best_t", 0.0)))
            u0 = int(fields.get("item_id", fields.get("best_id", 0)))
            if not math.isfinite(f0):
                raise CallbackRuntimeError(StatusCode.NONFINITE_EFFECT, "effect carries nonfinite f32")
            if not 0 <= u0 <= 0xFFFFFFFF:
                raise CallbackRuntimeError(StatusCode.U32_OVERFLOW, "effect carries invalid u32")
            return EffectValue(kind, f0=f0, u0=u0)
    raise AssertionError("verified callback failed to return")


def interpret_callback(function: VerifiedCallbackFunction, arguments: Mapping[str, Any]) -> EffectValue:
    expected = {name for name, _ in function.arguments}
    if set(arguments) != expected:
        raise CallbackRuntimeError(StatusCode.ABI_MISMATCH, "callback argument names mismatch")
    values: dict[str, Any] = {}
    for name, scalar_type in function.arguments:
        value = arguments[name]
        if scalar_type is ScalarType.F32:
            value = _f32(value)
            if not math.isfinite(float(value)):
                raise CallbackRuntimeError(StatusCode.NONFINITE_EFFECT, f"{name} is nonfinite")
        else:
            value = int(value)
            if not 0 <= value <= 0xFFFFFFFF:
                raise CallbackRuntimeError(StatusCode.U32_OVERFLOW, f"{name} is outside u32")
        values[name] = value
    return _interpret_statements(function.body, values)


_BIN_TEXT = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*"}
_CMP_TEXT = {ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=", ast.Eq: "==", ast.NotEq: "!="}


def _emit_expr(node: ast.expr) -> str:
    if isinstance(node, ast.Name): return node.id
    if isinstance(node, ast.Constant): return repr(node.value)
    if isinstance(node, ast.BinOp):
        return f"({_emit_expr(node.left)} {_BIN_TEXT[type(node.op)]} {_emit_expr(node.right)})"
    if isinstance(node, ast.UnaryOp):
        prefix = {ast.USub: "-", ast.UAdd: "+", ast.Not: "not "}[type(node.op)]
        return f"({prefix}{_emit_expr(node.operand)})"
    if isinstance(node, ast.Compare):
        return f"({_emit_expr(node.left)} {_CMP_TEXT[type(node.ops[0])]} {_emit_expr(node.comparators[0])})"
    if isinstance(node, ast.BoolOp):
        joiner = " and " if isinstance(node.op, ast.And) else " or "
        return "(" + joiner.join(_emit_expr(item) for item in node.values) + ")"
    if isinstance(node, ast.IfExp):
        return f"({_emit_expr(node.body)} if {_emit_expr(node.test)} else {_emit_expr(node.orelse)})"
    if isinstance(node, ast.Call) and _dotted_name(node.func) == "optix.sqrt":
        return f"math.sqrt({_emit_expr(node.args[0])})"
    raise AssertionError(ast.dump(node))


def _emit_effect(call: ast.Call, indent: str, nonce_word: int) -> list[str]:
    kind = EffectKind(_dotted_name(call.func).removeprefix("optix."))
    fields = {item.arg: _emit_expr(item.value) for item in call.keywords}
    lines = [f"{indent}out_status[0] = 0"]
    if kind is EffectKind.NO_HIT:
        lines.extend((f"{indent}out_effect[0] = 0", f"{indent}out_f0[0] = 0.0",
                      f"{indent}out_u0[0] = 0"))
    else:
        effect_code = {EffectKind.HIT: 1, EffectKind.ACCEPT_CONTINUE: 2, EffectKind.PAYLOAD: 3}[kind]
        f0 = fields.get("t", fields.get("best_t", "0.0"))
        u0 = fields.get("item_id", fields.get("best_id", "0"))
        lines.extend((
            f"{indent}_effect_f0 = {f0}",
            f"{indent}_effect_u0 = {u0}",
            f"{indent}if not math.isfinite(_effect_f0):",
            f"{indent}    out_status[0] = {int(StatusCode.NONFINITE_EFFECT)}",
            f"{indent}    return",
            f"{indent}if _effect_u0 < 0 or _effect_u0 > 4294967295:",
            f"{indent}    out_status[0] = {int(StatusCode.U32_OVERFLOW)}",
            f"{indent}    return",
            f"{indent}out_effect[0] = {effect_code}",
            f"{indent}out_f0[0] = _effect_f0",
            f"{indent}out_u0[0] = _effect_u0",
        ))
    lines.extend((f"{indent}out_nonce[0] = {nonce_word}", f"{indent}return"))
    return lines


def _emit_statements(statements: Sequence[ast.stmt], indent: str, nonce_word: int) -> list[str]:
    lines: list[str] = []
    sqrt_index = 0
    for statement in statements:
        if isinstance(statement, ast.Assign):
            target = statement.targets[0].id
            value = statement.value
            if isinstance(value, ast.Call) and _dotted_name(value.func) == "optix.sqrt":
                temp = f"_sqrt_operand_{sqrt_index}"
                sqrt_index += 1
                lines.extend((
                    f"{indent}{temp} = {_emit_expr(value.args[0])}",
                    f"{indent}if (not math.isfinite({temp})) or {temp} < 0.0:",
                    f"{indent}    out_status[0] = {int(StatusCode.INVALID_SQRT)}",
                    f"{indent}    return",
                    f"{indent}{target} = math.sqrt({temp})",
                ))
            else:
                lines.append(f"{indent}{target} = {_emit_expr(value)}")
        elif isinstance(statement, ast.If):
            lines.append(f"{indent}if {_emit_expr(statement.test)}:")
            lines.extend(_emit_statements(statement.body, indent + "    ", nonce_word))
            lines.append(f"{indent}else:")
            lines.extend(_emit_statements(statement.orelse, indent + "    ", nonce_word))
        else:
            assert isinstance(statement, ast.Return) and isinstance(statement.value, ast.Call)
            lines.extend(_emit_effect(statement.value, indent, nonce_word))
    return lines


def generate_numba_leaf(module: VerifiedCallbackModule, role: CallbackRole, *,
                        numeric_mode: str = "strict") -> GeneratedLeaf:
    if numeric_mode not in ("strict", "fast"):
        raise ValueError("numeric_mode must be strict or fast")
    function = module.function(role)
    # Deliberately an ordinary C-ABI device function.  OptiX callable entry
    # points belong to the trusted wrapper; the verified Numba leaf is never
    # promoted to a raw user-authored OptiX entry point.
    abi_name = f"rtdl_v4_{role.value}_leaf_{module.ir_sha256[:16]}"
    args = ", ".join(name for name, _ in function.arguments)
    signature = args + (", " if args else "") + \
        "out_status, out_effect, out_f0, out_u0, out_nonce"
    nonce_word = int(hashlib.sha256((module.ir_sha256 + role.value).encode()).hexdigest()[:8], 16)
    lines = [
        f"# {GENERATED_SOURCE_SCHEMA}",
        f"def {abi_name}({signature}):",
        "    out_status[0] = 5",
        "    out_effect[0] = 0",
        "    out_f0[0] = 0.0",
        "    out_u0[0] = 0",
        "    out_nonce[0] = 0",
    ]
    lines.extend(_emit_statements(function.body, "    ", nonce_word))
    source = "\n".join(lines) + "\n"
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    return GeneratedLeaf(role, abi_name, source, digest,
                         tuple(kind for _, kind in function.arguments), numeric_mode,
                         module.ir_sha256, nonce_word)


def generate_numba_scalar_probe(
    module: VerifiedCallbackModule, *, numeric_mode: str = "strict"
) -> GeneratedScalarProbe:
    """Generate the frozen scalar C-ABI probe without executing user source."""

    if numeric_mode not in ("strict", "fast"):
        raise ValueError("numeric_mode must be strict or fast")
    abi_name = f"rtdl_v4_scalar_probe_{module.ir_sha256[:16]}"
    source = "\n".join((
        f"# {GENERATED_SCALAR_PROBE_SCHEMA}",
        f"def {abi_name}(value):",
        "    return value + 1.0",
        "",
    ))
    return GeneratedScalarProbe(
        abi_name=abi_name,
        generated_source=source,
        generated_source_sha256=hashlib.sha256(source.encode("utf-8")).hexdigest(),
        numeric_mode=numeric_mode,
        ir_sha256=module.ir_sha256,
    )


_PTX_VERSION = re.compile(r"(?m)^\s*\.version\s+([0-9]+\.[0-9]+)")
_PTX_TARGET = re.compile(r"(?m)^\s*\.target\s+([^\s,]+)")
_PTX_EXTERN = re.compile(r"(?m)^\s*\.extern\s+\.func(?:\s+\([^)]*\))?\s+([^\s(;]+)")


def audit_ptx(ptx: str, *, abi_name: str, accepted_isa: tuple[str, str],
              allowed_external_symbols: frozenset[str]) -> dict[str, object]:
    version_match = _PTX_VERSION.search(ptx)
    target_match = _PTX_TARGET.search(ptx)
    if not version_match or not target_match:
        raise CallbackVerificationError("PTX is missing .version or .target")
    version = tuple(int(item) for item in version_match.group(1).split("."))
    low = tuple(int(item) for item in accepted_isa[0].split("."))
    high = tuple(int(item) for item in accepted_isa[1].split("."))
    if not low <= version <= high:
        raise CallbackVerificationError(
            f"PTX ISA {version_match.group(1)} outside accepted [{accepted_isa[0]}, {accepted_isa[1]}]")
    if abi_name not in ptx:
        raise CallbackVerificationError(f"PTX does not define ABI symbol {abi_name}")
    # Address conversion is expected for the compiler-owned output pointers;
    # dynamic calls, kernels, barriers and atomics are not part of a leaf.
    forbidden_tokens = (".entry", "bar.sync", "atom.", "call.uni (%")
    found_forbidden = [token for token in forbidden_tokens if token in ptx]
    if found_forbidden:
        raise CallbackVerificationError(f"forbidden PTX features: {found_forbidden}")
    external = tuple(sorted(set(_PTX_EXTERN.findall(ptx))))
    unexpected = sorted(set(external) - set(allowed_external_symbols))
    if unexpected:
        raise CallbackVerificationError(f"unallowlisted PTX externals: {unexpected}")
    return {
        "ptx_version": version_match.group(1),
        "ptx_target": target_match.group(1),
        "external_symbols": external,
        "ptx_sha256": hashlib.sha256(ptx.encode("utf-8")).hexdigest(),
    }


def compile_numba_leaf_isolated(
    leaf: GeneratedLeaf,
    *,
    compute_capability: tuple[int, int],
    accepted_ptx_isa: tuple[str, str],
    allowed_external_symbols: frozenset[str],
    python_executable: str | os.PathLike[str] = sys.executable,
) -> DeviceFunctionArtifact:
    """Compile only deterministic generated source in a fresh child process."""

    if len(compute_capability) != 2 or min(compute_capability) <= 0:
        raise ValueError("compute_capability must be an explicit (major, minor) tuple")
    request = {
        "schema": GENERATED_SOURCE_SCHEMA,
        "generated_source": leaf.generated_source,
        "generated_source_sha256": leaf.generated_source_sha256,
        "abi_name": leaf.abi_name,
        "argument_types": [item.value for item in leaf.argument_types],
        "numeric_mode": leaf.numeric_mode,
        "compute_capability": list(compute_capability),
    }
    with tempfile.TemporaryDirectory(prefix="rtdl-v4-numba-") as directory:
        request_path = Path(directory) / "request.json"
        response_path = Path(directory) / "response.json"
        request_path.write_text(json.dumps(request, sort_keys=True), encoding="utf-8")
        environment = dict(os.environ)
        environment["PYTHONHASHSEED"] = "0"
        completed = subprocess.run(
            [os.fspath(python_executable), "-m", "rtdsl._v4_numba_compile_child",
             os.fspath(request_path), os.fspath(response_path)],
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )
        if completed.returncode:
            raise RuntimeError(
                "isolated Numba compilation failed\nstdout:\n"
                + completed.stdout + "\nstderr:\n" + completed.stderr)
        response = json.loads(response_path.read_text(encoding="utf-8"))
    if response.get("generated_source_sha256") != leaf.generated_source_sha256:
        raise CallbackVerificationError("compiler child source identity mismatch")
    ptx = response["ptx"]
    audit = audit_ptx(
        ptx,
        abi_name=leaf.abi_name,
        accepted_isa=accepted_ptx_isa,
        allowed_external_symbols=allowed_external_symbols,
    )
    return DeviceFunctionArtifact(
        schema="rtdl.v4.device_function_artifact.v1",
        role=leaf.role.value,
        abi_name=leaf.abi_name,
        compute_capability=compute_capability,
        numeric_mode=leaf.numeric_mode,
        generated_source_sha256=leaf.generated_source_sha256,
        ir_sha256=leaf.ir_sha256,
        ptx=ptx,
        ptx_sha256=str(audit["ptx_sha256"]),
        ptx_version=str(audit["ptx_version"]),
        ptx_target=str(audit["ptx_target"]),
        external_symbols=tuple(audit["external_symbols"]),
        numba_version=response["numba_version"],
        python_version=response["python_version"],
        nonce_word=leaf.nonce_word,
    )


def compile_numba_scalar_probe_isolated(
    probe: GeneratedScalarProbe,
    *,
    compute_capability: tuple[int, int],
    accepted_ptx_isa: tuple[str, str],
    allowed_external_symbols: frozenset[str],
    python_executable: str | os.PathLike[str] = sys.executable,
) -> DeviceFunctionArtifact:
    """Compile the compiler-owned scalar-return probe in a fresh child."""

    if len(compute_capability) != 2 or min(compute_capability) <= 0:
        raise ValueError("compute_capability must be an explicit (major, minor) tuple")
    request = {
        "schema": GENERATED_SCALAR_PROBE_SCHEMA,
        "generated_source": probe.generated_source,
        "generated_source_sha256": probe.generated_source_sha256,
        "abi_name": probe.abi_name,
        "numeric_mode": probe.numeric_mode,
        "compute_capability": list(compute_capability),
    }
    with tempfile.TemporaryDirectory(prefix="rtdl-v4-numba-scalar-") as directory:
        request_path = Path(directory) / "request.json"
        response_path = Path(directory) / "response.json"
        request_path.write_text(json.dumps(request, sort_keys=True), encoding="utf-8")
        environment = dict(os.environ)
        environment["PYTHONHASHSEED"] = "0"
        completed = subprocess.run(
            [os.fspath(python_executable), "-m", "rtdsl._v4_numba_compile_child",
             os.fspath(request_path), os.fspath(response_path)],
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )
        if completed.returncode:
            raise RuntimeError(
                "isolated Numba scalar compilation failed\nstdout:\n"
                + completed.stdout + "\nstderr:\n" + completed.stderr)
        response = json.loads(response_path.read_text(encoding="utf-8"))
    if response.get("generated_source_sha256") != probe.generated_source_sha256:
        raise CallbackVerificationError("compiler child scalar source identity mismatch")
    ptx = response["ptx"]
    audit = audit_ptx(
        ptx,
        abi_name=probe.abi_name,
        accepted_isa=accepted_ptx_isa,
        allowed_external_symbols=allowed_external_symbols,
    )
    return DeviceFunctionArtifact(
        schema="rtdl.v4.device_function_artifact.v1",
        role="scalar_probe",
        abi_name=probe.abi_name,
        compute_capability=compute_capability,
        numeric_mode=probe.numeric_mode,
        generated_source_sha256=probe.generated_source_sha256,
        ir_sha256=probe.ir_sha256,
        ptx=ptx,
        ptx_sha256=str(audit["ptx_sha256"]),
        ptx_version=str(audit["ptx_version"]),
        ptx_target=str(audit["ptx_target"]),
        external_symbols=tuple(audit["external_symbols"]),
        numba_version=response["numba_version"],
        python_version=response["python_version"],
        nonce_word=0,
    )


def module_identity(module: VerifiedCallbackModule) -> dict[str, object]:
    return {
        "schema": module.schema,
        "source_sha256": module.source_sha256,
        "ir_sha256": module.ir_sha256,
        "roles": [item.role.value for item in module.functions],
    }


def verified_sphere_aabb(center: Sequence[float], radius: float) -> tuple[float, ...]:
    """Compiler-known analytic sphere contract used by the feasibility spike."""

    if len(center) != 3:
        raise CallbackVerificationError("sphere center must have three coordinates")
    c = tuple(_f32(item) for item in center)
    r = _f32(radius)
    if not all(math.isfinite(float(item)) for item in c) or not math.isfinite(float(r)) or r < 0:
        raise CallbackVerificationError("sphere geometry must be finite with nonnegative radius")
    # nextafter is the target-f32 outward enclosure rule; it is part of this
    # named verified geometry schema rather than inferred from arbitrary code.
    lower = tuple(float(np.nextafter(_f32(item - r), _f32(-math.inf))) for item in c)
    upper = tuple(float(np.nextafter(_f32(item + r), _f32(math.inf))) for item in c)
    return lower + upper


def verify_sphere_aabb(center: Sequence[float], radius: float,
                       candidate: Sequence[float]) -> None:
    expected = verified_sphere_aabb(center, radius)
    if len(candidate) != 6 or any(_f32(a) != _f32(b) for a, b in zip(candidate, expected)):
        raise CallbackVerificationError("custom AABB is not the verified outward-rounded sphere enclosure")


def trace_spheres_with_interpreter(
    module: VerifiedCallbackModule,
    *,
    origin: Sequence[float],
    direction: Sequence[float],
    tmin: float,
    tmax: float,
    spheres: Sequence[tuple[Sequence[float], float, int]],
) -> EffectValue:
    """Independent CPU execution of the exact PoC callback semantics."""

    if len(origin) != 3 or len(direction) != 3:
        raise ValueError("origin/direction must be vec3")
    intersection = module.function(CallbackRole.INTERSECTION)
    any_hit = module.function(CallbackRole.ANY_HIT)
    miss = module.function(CallbackRole.MISS)
    best_t = _f32(tmax)
    best_id = 0xFFFFFFFF
    found = False
    for center, radius, item_id in spheres:
        verify_sphere_aabb(center, radius, verified_sphere_aabb(center, radius))
        effect = interpret_callback(intersection, {
            "ox": origin[0], "oy": origin[1], "oz": origin[2],
            "dx": direction[0], "dy": direction[1], "dz": direction[2],
            "tmin": tmin, "tmax": best_t,
            "cx": center[0], "cy": center[1], "cz": center[2],
            "radius": radius, "item_id": item_id,
        })
        if effect.kind is EffectKind.HIT:
            update = interpret_callback(any_hit, {
                "hit_t": effect.f0, "hit_id": effect.u0,
                "best_t": best_t, "best_id": best_id,
            })
            best_t, best_id = _f32(update.f0), update.u0
            found = True
    if not found:
        return interpret_callback(miss, {"best_t": best_t, "best_id": best_id})
    return EffectValue(EffectKind.PAYLOAD, float(best_t), best_id)
