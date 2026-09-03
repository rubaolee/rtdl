"""Deterministic formal Callback IR -> trusted Numba-leaf source lowering.

The original restricted-Python source/callable never enters this module.  It
consumes an exact verified IR plus its canonical Goal5751 ABI and emits one
ordinary C-ABI device function source per callback role.  The generated source
contains no imports, globals, defaults, overloads or application dispatch.

This module intentionally stops before Numba/PTX compilation.  The isolated
compiler child and trusted PTX composer are separate authorities.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Mapping, Sequence

from .v4_callback_abi import (
    AnyHitProofAuthority,
    CallbackAbiError,
    CompiledCallbackAbi,
    RoleAbi,
    compile_callback_abi,
    verify_compiled_callback_abi,
)
from .v4_callback_ir import (
    CallbackEffect,
    CallbackExpr,
    CallbackFunction,
    CallbackRecord,
    CallbackRole,
    CallbackStatement,
    CallbackType,
    EffectKind,
    GeometryProofAuthority,
    IfStatement,
    LetStatement,
    ReturnEffectStatement,
    ReturnValueStatement,
    RuntimeStatus,
    ScalarKind,
    SetStatement,
    StaticForStatement,
    TypeKind,
    VerifiedCallbackProgram,
)
from .v4_callback_poc import DeviceFunctionArtifact, audit_ptx


FORMAL_NUMBA_SOURCE_SCHEMA = "rtdl.v4.generated_formal_numba_leaf.v1"
FORMAL_NUMBA_CACHE_SCHEMA = "rtdl.v4.formal_numba_leaf_cache.v1"
FORMAL_NUMBA_CACHE_ENV = "RTDL_V4_FORMAL_LEAF_CACHE"
FORMAL_NUMBA_CACHE_MANIFEST_ENV = "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST"
FORMAL_NUMBA_CACHE_MANIFEST_SHA256_ENV = (
    "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256"
)

_FORMAL_NUMBA_CACHE_COUNTS = {"hit": 0, "miss": 0, "disabled": 0}


class CallbackCodegenError(ValueError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"V4 Numba codegen failed: {code}@{path}: {message}")


@dataclass(frozen=True)
class FormalNumbaLeafCachePolicy:
    """Explicit content-addressed cache policy for formal Numba leaves.

    A root without a manifest is a create-only development cache. Supplying a
    manifest and its digest makes the cache read-only and binds exact entry
    membership. The legacy environment variables remain supported for old
    harnesses, but a supplied policy is authoritative and requires no process-
    global environment mutation.
    """

    root: Path
    manifest: Path | None = None
    manifest_sha256: str | None = None

    def __post_init__(self) -> None:
        root = Path(self.root).expanduser().absolute()
        manifest = (
            None
            if self.manifest is None
            else Path(self.manifest).expanduser().absolute()
        )
        digest = self.manifest_sha256
        if (manifest is None) != (digest is None):
            raise ValueError(
                "formal leaf cache manifest and manifest_sha256 must be supplied together"
            )
        if digest is not None and re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise ValueError("formal leaf cache manifest_sha256 must be lowercase SHA-256")
        object.__setattr__(self, "root", root)
        object.__setattr__(self, "manifest", manifest)


@dataclass(frozen=True)
class GeneratedFormalNumbaLeaf:
    schema: str
    role: CallbackRole
    abi_name: str
    parameter_order: tuple[str, ...]
    parameter_types: tuple[str, ...]
    generated_source: str
    generated_source_sha256: str
    callback_ir_sha256: str
    callback_effect_digest: str
    callback_abi_sha256: str
    nonce_word: int
    numeric_mode: str
    error_sites: tuple[tuple[int, str], ...]
    compiler_function_count: int

    def to_dict(self, *, include_source: bool = True) -> dict[str, object]:
        result: dict[str, object] = {
            "schema": self.schema,
            "role": self.role.value,
            "abi_name": self.abi_name,
            "parameter_order": list(self.parameter_order),
            "parameter_types": list(self.parameter_types),
            "generated_source_sha256": self.generated_source_sha256,
            "callback_ir_sha256": self.callback_ir_sha256,
            "callback_effect_digest": self.callback_effect_digest,
            "callback_abi_sha256": self.callback_abi_sha256,
            "nonce_word": self.nonce_word,
            "numeric_mode": self.numeric_mode,
            "error_sites": {str(key): value for key, value in self.error_sites},
            "compiler_function_count": self.compiler_function_count,
        }
        if include_source:
            result["generated_source"] = self.generated_source
        return result


def formal_numba_leaf_cache_lifecycle_metadata() -> dict[str, object]:
    """Return process-local diagnostic counts for the explicit leaf cache.

    The counters are diagnostic metadata only.  They never authorize a cache
    entry and never replace the entry's exact identity checks.
    """

    return {
        "schema": FORMAL_NUMBA_CACHE_SCHEMA,
        "environment_variable": FORMAL_NUMBA_CACHE_ENV,
        "manifest_environment_variable": FORMAL_NUMBA_CACHE_MANIFEST_ENV,
        "hit_count": int(_FORMAL_NUMBA_CACHE_COUNTS["hit"]),
        "miss_count": int(_FORMAL_NUMBA_CACHE_COUNTS["miss"]),
        "disabled_count": int(_FORMAL_NUMBA_CACHE_COUNTS["disabled"]),
    }


@dataclass(frozen=True)
class _Value:
    value_type: CallbackType
    leaves: tuple[str, ...]


@dataclass(frozen=True)
class _View:
    value_type: CallbackType
    columns: tuple[str, ...]
    length: str


class _Emitter:
    def __init__(
        self,
        *,
        verified: VerifiedCallbackProgram,
        abi: CompiledCallbackAbi,
        role_abi: RoleAbi,
    ) -> None:
        self.verified = verified
        self.abi = abi
        self.role_abi = role_abi
        self.records = {item.name: item for item in verified.program.records}
        self.helpers = {item.name: item for item in verified.program.functions if item.is_helper}
        self.lines: list[str] = []
        self.indent = ""
        self.temp_index = 0
        self.site_index = 0
        self.sites: list[tuple[int, str]] = []
        self.current_return_type: CallbackType | None = None
        self.status_names = {
            field.path: _parameter_name(field.path) for field in role_abi.status
        }
        self.output_names: dict[str, str] = {"out.effect_tag": _parameter_name("out.effect_tag")}
        for variant in role_abi.effects:
            for field in variant.fields:
                self.output_names[field.path] = _parameter_name(field.path)

    def emit(self, text: str = "") -> None:
        self.lines.append(self.indent + text)

    def block(self) -> "_Block":
        return _Block(self)

    def temp(self, stem: str) -> str:
        self.temp_index += 1
        return f"_rtdl_{stem}_{self.temp_index}"

    def site(self, path: str) -> int:
        self.site_index += 1
        self.sites.append((self.site_index, path))
        return self.site_index

    def status(self, leaf: str) -> str:
        return self.status_names[f"status.{leaf}"]

    def emit_failure(self, status: RuntimeStatus, path: str) -> None:
        code = dict(self.abi.runtime_status_codes)[status.value]
        site = self.site(path)
        self.emit(f"{self.status('ok')}[0] = 0")
        self.emit(f"{self.status('error_code')}[0] = {code}")
        self.emit(f"{self.status('error_site')}[0] = {site}")
        if self.current_return_type is None:
            self.emit("return")
        else:
            self.emit(f"return {_default_expression(self.current_return_type, self.records)}")

    def emit_role(self, function: CallbackFunction) -> None:
        parameter_names = [_parameter_name(item) for item in self.role_abi.parameter_order]
        self.emit(f"# {FORMAL_NUMBA_SOURCE_SCHEMA}")
        self.emit(f"# callback_ir_sha256={self.verified.ir_sha256}")
        self.emit(f"# callback_abi_sha256={self.abi.abi_sha256}")
        self.emit(f"def {self.role_abi.symbol}({', '.join(parameter_names)}):")
        with self.block():
            self._emit_status_initialization()
            environment = self._role_argument_environment(function)
            environment.update(self._constant_environment())
            self._emit_input_checks(environment, function)
            self.emit(f"{self.status('error_code')}[0] = 0")
            self._emit_statements(function.body, environment, function.name)

    def _emit_status_initialization(self) -> None:
        launch = _parameter_name("in.context.launch_index")
        self.emit(f"{self.status('ok')}[0] = 0")
        # ok=0 plus invocation_mask/nonce is the explicit not-completed state;
        # error_code remains zero until a concrete checked fault occurs.
        self.emit(f"{self.status('error_code')}[0] = 0")
        self.emit(f"{self.status('stage')}[0] = {self.role_abi.stage_tag}")
        self.emit(f"{self.status('role')}[0] = {self.role_abi.role_tag}")
        self.emit(f"{self.status('launch_index')}[0] = {launch}")
        self.emit(f"{self.status('error_site')}[0] = 0")
        self.emit(f"{self.status('effect_tag')}[0] = 0")
        self.emit(f"{self.status('nonce_word')}[0] = {self.role_abi.nonce_word}")
        self.emit(f"{self.status('invocation_mask')}[0] = {1 << (self.role_abi.role_tag - 1)}")
        self.emit(f"{self.status('first_error_claimed')}[0] = 0")
        self.emit(f"{self.output_names['out.effect_tag']}[0] = 0")
        for path, name in sorted(self.output_names.items()):
            if path == "out.effect_tag":
                continue
            field = _abi_output_field(self.role_abi, path)
            self.emit(f"{name}[0] = {_scalar_default(field.scalar)}")

    def _role_argument_environment(
        self, function: CallbackFunction
    ) -> dict[str, _Value | _View]:
        environment: dict[str, _Value | _View] = {}
        for argument in function.arguments:
            environment[argument.name] = self._argument_value(
                argument.value_type, f"in.{argument.name}"
            )
        return environment

    def _argument_value(self, value_type: CallbackType, path: str) -> _Value | _View:
        if value_type.kind is TypeKind.READ_ONLY_VIEW:
            prefix = f"{path}.columns"
            fields = [
                item for item in self.role_abi.inputs
                if item.path == prefix or item.path.startswith(prefix + ".")
            ]
            return _View(
                value_type=value_type,
                columns=tuple(_parameter_name(item.path) for item in fields),
                length=_parameter_name(f"{path}.length"),
            )
        expected = _leaf_count(value_type, self.records)
        fields = [
            item for item in self.role_abi.inputs
            if item.path == path or item.path.startswith(path + ".")
        ]
        if len(fields) != expected:
            _fail("argument_layout", path, f"expected {expected} leaves, got {len(fields)}")
        return _Value(value_type, tuple(_parameter_name(item.path) for item in fields))

    def _constant_environment(self) -> dict[str, _Value]:
        return {
            item.name: _literal_value(item.value_type, item.value, self.records)
            for item in self.verified.program.manifest.constants
        }

    def _emit_input_checks(
        self,
        environment: Mapping[str, _Value | _View],
        function: CallbackFunction,
    ) -> None:
        for argument in function.arguments:
            value = environment[argument.name]
            if isinstance(value, _View):
                continue
            for leaf, kind in zip(value.leaves, _leaf_scalar_kinds(value.value_type, self.records)):
                if kind in {ScalarKind.F32, ScalarKind.F64}:
                    self.emit(f"if not math.isfinite({leaf}):")
                    with self.block():
                        self.emit_failure(RuntimeStatus.NONFINITE_INPUT, f"{function.role.value}.{argument.name}")

    def _emit_statements(
        self,
        statements: Sequence[CallbackStatement],
        environment: dict[str, _Value | _View],
        path: str,
    ) -> None:
        for index, statement in enumerate(statements):
            item_path = f"{path}[{index}]"
            if isinstance(statement, (LetStatement, SetStatement)):
                value = self._emit_expr(statement.value, environment, item_path)
                if isinstance(value, _View):
                    _fail("view_assignment", item_path, "views cannot be constructed")
                target = _local_name(statement.name)
                expression = _value_expression(value)
                self.emit(f"{target} = {expression}")
                environment[statement.name] = _value_from_code(
                    statement.value.value_type, target, self.records
                )
            elif isinstance(statement, IfStatement):
                condition = self._emit_expr(statement.condition, environment, f"{item_path}.condition")
                assert isinstance(condition, _Value) and len(condition.leaves) == 1
                self.emit(f"if {condition.leaves[0]}:")
                with self.block():
                    self._emit_statements(statement.then_body, dict(environment), f"{item_path}.then")
                self.emit("else:")
                with self.block():
                    self._emit_statements(statement.else_body, dict(environment), f"{item_path}.else")
            elif isinstance(statement, StaticForStatement):
                index_name = _local_name(statement.index_name)
                self.emit(f"for {index_name} in range({statement.trip_count}):")
                with self.block():
                    nested = dict(environment)
                    nested[statement.index_name] = _Value(
                        _scalar_type(ScalarKind.U32), (index_name,)
                    )
                    self._emit_statements(statement.body, nested, f"{item_path}.body")
            elif isinstance(statement, ReturnEffectStatement):
                self._emit_effect(statement.effect, environment, item_path)
            elif isinstance(statement, ReturnValueStatement):
                value = self._emit_expr(statement.value, environment, item_path)
                assert isinstance(value, _Value)
                self.emit(f"return {_value_expression(value)}")
            else:
                _fail("statement", item_path, type(statement).__name__)

    def _emit_effect(
        self,
        effect: CallbackEffect,
        environment: Mapping[str, _Value | _View],
        path: str,
    ) -> None:
        variant = next(
            (item for item in self.role_abi.effects if item.kind is effect.kind), None
        )
        if variant is None:
            _fail("effect_abi", path, effect.kind.value)
        evaluated: list[tuple[str, CallbackExpr, _Value, list[object]]] = []
        for name, expression in effect.fields:
            value = self._emit_expr(expression, environment, f"{path}.{name}")
            assert isinstance(value, _Value)
            target_fields = [
                item for item in variant.fields
                if item.path == f"out.{effect.kind.value}.{name}"
                or item.path.startswith(f"out.{effect.kind.value}.{name}.")
            ]
            if len(target_fields) != len(value.leaves):
                _fail("effect_field_layout", f"{path}.{name}", str(len(target_fields)))
            evaluated.append((name, expression, value, target_fields))
            for target, leaf, kind in zip(
                target_fields,
                value.leaves,
                _leaf_scalar_kinds(expression.value_type, self.records),
            ):
                if kind in {ScalarKind.F32, ScalarKind.F64}:
                    self.emit(f"if not math.isfinite({leaf}):")
                    with self.block():
                        self.emit_failure(RuntimeStatus.NONFINITE_RESULT, f"{path}.{name}")
        values = {name: value for name, _, value, _ in evaluated}
        self._emit_effect_contract_checks(effect.kind, values, path)
        for _, _, value, target_fields in evaluated:
            for target, leaf in zip(target_fields, value.leaves):
                self.emit(f"{self.output_names[target.path]}[0] = {leaf}")
        self.emit(f"{self.output_names['out.effect_tag']}[0] = {variant.tag}")
        self.emit(f"{self.status('effect_tag')}[0] = {variant.tag}")
        self.emit(f"{self.status('error_code')}[0] = 0")
        self.emit(f"{self.status('ok')}[0] = 1")
        self.emit("return")

    def _emit_effect_contract_checks(
        self,
        kind: EffectKind,
        values: Mapping[str, _Value],
        path: str,
    ) -> None:
        if kind is EffectKind.AABB:
            lower, upper = values["lower"], values["upper"]
            invalid = " or ".join(
                f"({left} > {right})" for left, right in zip(lower.leaves, upper.leaves)
            )
            self.emit(f"if {invalid}:")
            with self.block():
                self.emit_failure(RuntimeStatus.INVALID_AABB, path)
        elif kind is EffectKind.TRACE_REQUEST:
            direction = values["direction"].leaves
            tmin = values["tmin"].leaves[0]
            tmax = values["tmax"].leaves[0]
            zero_direction = " and ".join(f"({item} == 0.0)" for item in direction)
            self.emit(f"if ({zero_direction}) or (not (0.0 <= {tmin} < {tmax})): ")
            with self.block():
                self.emit_failure(RuntimeStatus.INVALID_TRACE_REQUEST, path)
        elif kind is EffectKind.HIT:
            hit_kind = values["hit_kind"].leaves[0]
            self.emit(f"if {hit_kind} < 0 or {hit_kind} > 127:")
            with self.block():
                self.emit_failure(RuntimeStatus.INVALID_EFFECT, path)

    def _emit_expr(
        self,
        expression: CallbackExpr,
        environment: Mapping[str, _Value | _View],
        path: str,
    ) -> _Value | _View:
        op = expression.opcode
        attrs = dict(expression.attributes)
        if op in {"argument", "local", "constant"}:
            name = str(attrs["name"])
            value = environment.get(name)
            if value is None:
                _fail("environment", path, name)
            return value
        if op == "literal":
            return _literal_value(expression.value_type, attrs["value"], self.records)
        if op == "field":
            base = self._emit_expr(expression.operands[0], environment, path)
            if isinstance(base, _View):
                _fail("view_field", path, str(attrs["name"]))
            return _field_value(base, str(attrs["name"]), self.records)
        if op == "view_load":
            view = self._emit_expr(expression.operands[0], environment, path)
            index = self._emit_expr(expression.operands[1], environment, path)
            if not isinstance(view, _View) or not isinstance(index, _Value):
                _fail("view_load", path, "invalid view/index")
            index_code = index.leaves[0]
            self.emit(f"if {index_code} < 0 or {index_code} >= {view.length}:")
            with self.block():
                self.emit_failure(RuntimeStatus.VIEW_OUT_OF_BOUNDS, path)
            leaves = tuple(f"{column}[{index_code}]" for column in view.columns)
            result = _Value(expression.value_type, leaves)
            for leaf, kind in zip(leaves, _leaf_scalar_kinds(expression.value_type, self.records)):
                if kind in {ScalarKind.F32, ScalarKind.F64}:
                    self.emit(f"if not math.isfinite({leaf}):")
                    with self.block():
                        self.emit_failure(RuntimeStatus.NONFINITE_INPUT, path)
            return result
        operands = [self._emit_expr(item, environment, path) for item in expression.operands]
        if any(isinstance(item, _View) for item in operands):
            _fail("view_operand", path, op)
        values = [item for item in operands if isinstance(item, _Value)]
        if op in {"add", "sub", "mul", "div", "min", "max"}:
            return self._numeric(op, values[0], values[1], expression.value_type, path)
        if op in {"bit_and", "bit_or", "bit_xor", "shift_left", "shift_right"}:
            return self._integer(op, values[0], values[1], expression.value_type, path)
        if op in {"neg", "abs"}:
            return self._unary(op, values[0], expression.value_type, path)
        if op == "not":
            return _Value(expression.value_type, (f"(not {values[0].leaves[0]})",))
        if op in {"and", "or"}:
            joiner = " and " if op == "and" else " or "
            return _Value(expression.value_type, (
                "(" + joiner.join(item.leaves[0] for item in values) + ")",
            ))
        if op in {"eq", "ne", "lt", "le", "gt", "ge"}:
            operator = {"eq": "==", "ne": "!=", "lt": "<", "le": "<=", "gt": ">", "ge": ">="}[op]
            return _Value(expression.value_type, (
                f"({values[0].leaves[0]} {operator} {values[1].leaves[0]})",
            ))
        if op == "select":
            condition = values[0].leaves[0]
            return _Value(expression.value_type, tuple(
                f"({left} if {condition} else {right})"
                for left, right in zip(values[1].leaves, values[2].leaves)
            ))
        if op == "sqrt":
            operand = values[0].leaves[0]
            self.emit(f"if (not math.isfinite({operand})) or {operand} < 0.0:")
            with self.block():
                self.emit_failure(RuntimeStatus.INVALID_SQRT, path)
            code = f"math.sqrt({operand})"
            if expression.value_type.scalar is ScalarKind.F32:
                code = f"_f32({code})"
            return _Value(expression.value_type, (code,))
        if op == "isfinite":
            return _Value(expression.value_type, (
                "(" + " and ".join(f"math.isfinite({item})" for item in values[0].leaves) + ")",
            ))
        if op == "dot":
            kind = expression.value_type.scalar
            assert kind is not None
            accumulator = self.temp("dot_acc")
            self.emit(f"{accumulator} = {'_f32(0.0)' if kind is ScalarKind.F32 else '0.0'}")
            for left, right in zip(values[0].leaves, values[1].leaves):
                product = self.temp("dot_product")
                product_code = f"({left} * {right})"
                if kind is ScalarKind.F32:
                    product_code = f"_f32({product_code})"
                self.emit(f"{product} = {product_code}")
                add_code = f"({accumulator} + {product})"
                if kind is ScalarKind.F32:
                    add_code = f"_f32({add_code})"
                self.emit(f"{accumulator} = {add_code}")
                self.emit(f"if not math.isfinite({accumulator}):")
                with self.block():
                    self.emit_failure(RuntimeStatus.NONFINITE_RESULT, path)
            return _Value(expression.value_type, (accumulator,))
        if op == "construct":
            return _Value(expression.value_type, tuple(
                leaf for item in values for leaf in item.leaves
            ))
        if op == "helper_call":
            name = str(attrs["name"])
            helper = self.helpers.get(name)
            if helper is None or helper.return_type is None:
                _fail("helper", path, name)
            call_name = f"_rtdl_helper_{_identifier(name)}"
            args = [_value_expression(item) for item in values]
            args.extend(self.status_names[item.path] for item in self.role_abi.status)
            temp = self.temp("helper")
            self.emit(f"{temp} = {call_name}({', '.join(args)})")
            self.emit(f"if {self.status('error_code')}[0] != 0:")
            with self.block():
                if self.current_return_type is None:
                    self.emit("return")
                else:
                    self.emit(f"return {_default_expression(self.current_return_type, self.records)}")
            return _value_from_code(helper.return_type, temp, self.records)
        _fail("expression", path, op)
        raise AssertionError

    def _numeric(
        self, op: str, left: _Value, right: _Value, result_type: CallbackType, path: str
    ) -> _Value:
        operator = {"add": "+", "sub": "-", "mul": "*", "div": "/"}.get(op)
        kinds = _leaf_scalar_kinds(result_type, self.records)
        leaves: list[str] = []
        for a, b, kind in zip(left.leaves, right.leaves, kinds):
            if kind in {ScalarKind.I32, ScalarKind.U32, ScalarKind.I64, ScalarKind.U64}:
                _fail(
                    "integer_numeric_codegen_pending",
                    path,
                    "checked integer add/sub/mul/div requires a reviewed no-wrap lowering",
                )
            if op == "div":
                self.emit(f"if {b} == 0:")
                with self.block():
                    self.emit_failure(RuntimeStatus.DIVIDE_BY_ZERO, path)
            if op == "min":
                code = f"({a} if {a} <= {b} else {b})"
            elif op == "max":
                code = f"({a} if {a} >= {b} else {b})"
            else:
                code = f"({a} {operator} {b})"
            if kind is ScalarKind.F32:
                code = f"_f32({code})"
            temp = self.temp("numeric")
            self.emit(f"{temp} = {code}")
            if kind in {ScalarKind.F32, ScalarKind.F64}:
                self.emit(f"if not math.isfinite({temp}):")
                with self.block():
                    self.emit_failure(RuntimeStatus.NONFINITE_RESULT, path)
            elif kind in {ScalarKind.I32, ScalarKind.U32, ScalarKind.I64, ScalarKind.U64}:
                low, high = _integer_bounds(kind)
                self.emit(f"if {temp} < {low} or {temp} > {high}:")
                with self.block():
                    self.emit_failure(RuntimeStatus.INTEGER_OVERFLOW, path)
            leaves.append(temp)
        return _Value(result_type, tuple(leaves))

    def _integer(
        self, op: str, left: _Value, right: _Value, result_type: CallbackType, path: str
    ) -> _Value:
        if op == "shift_left":
            _fail(
                "integer_shift_left_codegen_pending",
                path,
                "checked left shift requires a reviewed no-wrap lowering",
            )
        operator = {
            "bit_and": "&", "bit_or": "|", "bit_xor": "^",
            "shift_left": "<<", "shift_right": ">>",
        }[op]
        code = f"({left.leaves[0]} {operator} {right.leaves[0]})"
        temp = self.temp("integer")
        self.emit(f"{temp} = {code}")
        kind = result_type.scalar
        assert kind is not None
        low, high = _integer_bounds(kind)
        self.emit(f"if {temp} < {low} or {temp} > {high}:")
        with self.block():
            self.emit_failure(RuntimeStatus.INTEGER_OVERFLOW, path)
        return _Value(result_type, (temp,))

    def _unary(self, op: str, value: _Value, result_type: CallbackType, path: str) -> _Value:
        leaves: list[str] = []
        kinds = _leaf_scalar_kinds(result_type, self.records)
        for item, kind in zip(value.leaves, kinds):
            if kind in {ScalarKind.I32, ScalarKind.U32, ScalarKind.I64, ScalarKind.U64}:
                _fail(
                    "integer_unary_codegen_pending",
                    path,
                    "checked integer neg/abs requires a reviewed no-wrap lowering",
                )
            code = f"(-{item})" if op == "neg" else f"abs({item})"
            if kind is ScalarKind.F32:
                code = f"_f32({code})"
            temp = self.temp("unary")
            self.emit(f"{temp} = {code}")
            if kind in {ScalarKind.I32, ScalarKind.U32, ScalarKind.I64, ScalarKind.U64}:
                low, high = _integer_bounds(kind)
                self.emit(f"if {temp} < {low} or {temp} > {high}:")
                with self.block():
                    self.emit_failure(RuntimeStatus.INTEGER_OVERFLOW, path)
            leaves.append(temp)
        return _Value(result_type, tuple(leaves))


class _Block:
    def __init__(self, emitter: _Emitter) -> None:
        self.emitter = emitter
        self.previous = emitter.indent

    def __enter__(self) -> None:
        self.emitter.indent += "    "

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.emitter.indent = self.previous


def generate_formal_numba_leaf(
    verified: VerifiedCallbackProgram,
    abi: CompiledCallbackAbi | Mapping[str, object],
    role: CallbackRole,
    *,
    any_hit_proof_authority: AnyHitProofAuthority | None = None,
    geometry_proof_authorities: Mapping[str, GeometryProofAuthority] | None = None,
    physical_schema_authority: object | None = None,
    numeric_mode: str = "strict",
) -> GeneratedFormalNumbaLeaf:
    """Generate one trusted source leaf from formal IR and canonical ABI."""

    if numeric_mode != "strict":
        _fail("numeric_mode", role.value, "formal Callback IR v1 permits strict mode only")
    try:
        canonical = verify_compiled_callback_abi(
            abi,
            verified,
            any_hit_proof_authority=any_hit_proof_authority,
            geometry_proof_authorities=geometry_proof_authorities,
            physical_schema_authority=physical_schema_authority,
        )
    except CallbackAbiError as exc:
        raise CallbackCodegenError(
            "abi_admission", exc.path, f"{exc.code}: {exc.message}"
        ) from exc
    role_abi = next((item for item in canonical.roles if item.role is role), None)
    if role_abi is None:
        _fail("role", role.value, "role is not present in exact ABI")
    function = verified.program.function_for_role(role)
    emitter = _Emitter(verified=verified, abi=canonical, role_abi=role_abi)
    # Helpers are emitted before the C-ABI leaf.  They are compiler-generated
    # internal functions and never public symbols or user callables.
    for helper in sorted(emitter.helpers.values(), key=lambda item: item.name):
        _emit_helper(emitter, helper)
        emitter.emit()
    emitter.emit_role(function)
    source = "\n".join(emitter.lines) + "\n"
    compile(source, "<rtdl-v4-generated-formal-numba>", "exec")
    return GeneratedFormalNumbaLeaf(
        schema=FORMAL_NUMBA_SOURCE_SCHEMA,
        role=role,
        abi_name=role_abi.symbol,
        parameter_order=role_abi.parameter_order,
        parameter_types=_parameter_types(role_abi),
        generated_source=source,
        generated_source_sha256=hashlib.sha256(source.encode("utf-8")).hexdigest(),
        callback_ir_sha256=verified.ir_sha256,
        callback_effect_digest=verified.effect_digest,
        callback_abi_sha256=canonical.abi_sha256,
        nonce_word=role_abi.nonce_word,
        numeric_mode=numeric_mode,
        error_sites=tuple(emitter.sites),
        compiler_function_count=1 + len(_reachable_helpers(function, emitter.helpers)),
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _formal_numba_cache_policy_sources() -> dict[str, str]:
    directory = Path(__file__).resolve().parent
    paths = {
        "formal_codegen": Path(__file__).resolve(),
        "isolated_compile_child": directory / "_v4_numba_compile_child.py",
        "ptx_auditor": directory / "v4_callback_poc.py",
    }
    result: dict[str, str] = {}
    for name, path in paths.items():
        if not path.is_file() or path.is_symlink():
            _fail("formal_leaf_cache_policy_source", name, os.fspath(path))
        result[name] = _sha256_file(path)
    return result


def _formal_numba_cache_policy_identity(
    python_executable: str | os.PathLike[str],
    *,
    role: str,
) -> dict[str, object]:
    """Hash one exact compiler-policy snapshot for a closed leaf batch."""

    executable = Path(python_executable).resolve(strict=True)
    if not executable.is_file() or executable.is_symlink():
        _fail("formal_leaf_cache_python", role, os.fspath(executable))
    return {
        "python_executable": os.fspath(executable),
        "python_executable_sha256": _sha256_file(executable),
        "compiler_policy_source_sha256": _formal_numba_cache_policy_sources(),
    }


def _formal_numba_cache_key(
    leaf: GeneratedFormalNumbaLeaf,
    *,
    compute_capability: tuple[int, int],
    accepted_ptx_isa: tuple[str, str],
    allowed_external_symbols: frozenset[str],
    expected_python_version: str,
    expected_numba_version: str,
    expected_numpy_version: str,
    python_executable: str | os.PathLike[str],
    policy_identity: Mapping[str, object] | None = None,
) -> tuple[str, dict[str, object]]:
    policy = (
        _formal_numba_cache_policy_identity(
            python_executable, role=leaf.role.value)
        if policy_identity is None else dict(policy_identity)
    )
    if set(policy) != {
        "python_executable", "python_executable_sha256",
        "compiler_policy_source_sha256",
    }:
        _fail("formal_leaf_cache_policy_identity", leaf.role.value,
              "unexpected policy identity shape")
    key: dict[str, object] = {
        "schema": FORMAL_NUMBA_CACHE_SCHEMA,
        "generated_source_sha256": leaf.generated_source_sha256,
        "callback_ir_sha256": leaf.callback_ir_sha256,
        "callback_effect_digest": leaf.callback_effect_digest,
        "callback_abi_sha256": leaf.callback_abi_sha256,
        "role": leaf.role.value,
        "abi_name": leaf.abi_name,
        "parameter_types": list(leaf.parameter_types),
        "numeric_mode": leaf.numeric_mode,
        "nonce_word": int(leaf.nonce_word),
        "compiler_function_count": int(leaf.compiler_function_count),
        "compute_capability": list(compute_capability),
        "accepted_ptx_isa": list(accepted_ptx_isa),
        "allowed_external_symbols": sorted(allowed_external_symbols),
        "expected_python_version": expected_python_version,
        "expected_numba_version": expected_numba_version,
        "expected_numpy_version": expected_numpy_version,
        **policy,
    }
    encoded = json.dumps(key, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest(), key


def _device_function_artifact_dict(artifact: DeviceFunctionArtifact) -> dict[str, object]:
    return {
        "schema": artifact.schema,
        "role": artifact.role,
        "abi_name": artifact.abi_name,
        "compute_capability": list(artifact.compute_capability),
        "numeric_mode": artifact.numeric_mode,
        "generated_source_sha256": artifact.generated_source_sha256,
        "ir_sha256": artifact.ir_sha256,
        "ptx": artifact.ptx,
        "ptx_sha256": artifact.ptx_sha256,
        "ptx_version": artifact.ptx_version,
        "ptx_target": artifact.ptx_target,
        "external_symbols": list(artifact.external_symbols),
        "numba_version": artifact.numba_version,
        "python_version": artifact.python_version,
        "nonce_word": int(artifact.nonce_word),
        "compiler_function_count": int(artifact.compiler_function_count),
    }


def _device_function_artifact_from_dict(
    value: object,
    *,
    leaf: GeneratedFormalNumbaLeaf,
    compute_capability: tuple[int, int],
    accepted_ptx_isa: tuple[str, str],
    allowed_external_symbols: frozenset[str],
    expected_python_version: str,
    expected_numba_version: str,
) -> DeviceFunctionArtifact:
    if not isinstance(value, dict):
        _fail("formal_leaf_cache_artifact", leaf.role.value, "artifact is not an object")
    expected_fields = {
        "schema", "role", "abi_name", "compute_capability", "numeric_mode",
        "generated_source_sha256", "ir_sha256", "ptx", "ptx_sha256",
        "ptx_version", "ptx_target", "external_symbols", "numba_version",
        "python_version", "nonce_word", "compiler_function_count",
    }
    if set(value) != expected_fields:
        _fail("formal_leaf_cache_artifact_fields", leaf.role.value, repr(sorted(value)))
    try:
        artifact = DeviceFunctionArtifact(
            schema=str(value["schema"]),
            role=str(value["role"]),
            abi_name=str(value["abi_name"]),
            compute_capability=tuple(int(item) for item in value["compute_capability"]),
            numeric_mode=str(value["numeric_mode"]),
            generated_source_sha256=str(value["generated_source_sha256"]),
            ir_sha256=str(value["ir_sha256"]),
            ptx=str(value["ptx"]),
            ptx_sha256=str(value["ptx_sha256"]),
            ptx_version=str(value["ptx_version"]),
            ptx_target=str(value["ptx_target"]),
            external_symbols=tuple(str(item) for item in value["external_symbols"]),
            numba_version=str(value["numba_version"]),
            python_version=str(value["python_version"]),
            nonce_word=int(value["nonce_word"]),
            compiler_function_count=int(value["compiler_function_count"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise CallbackCodegenError(
            "formal_leaf_cache_artifact", leaf.role.value, f"malformed artifact: {exc}"
        ) from exc
    expected_identity = {
        "schema": "rtdl.v4.formal_device_function_artifact.v1",
        "role": leaf.role.value,
        "abi_name": leaf.abi_name,
        "compute_capability": compute_capability,
        "numeric_mode": leaf.numeric_mode,
        "generated_source_sha256": leaf.generated_source_sha256,
        "ir_sha256": leaf.callback_ir_sha256,
        "numba_version": expected_numba_version,
        "python_version": expected_python_version,
        "nonce_word": leaf.nonce_word,
        "compiler_function_count": leaf.compiler_function_count,
    }
    observed_identity = {
        name: getattr(artifact, name) for name in expected_identity
    }
    if observed_identity != expected_identity:
        _fail(
            "formal_leaf_cache_artifact_identity",
            leaf.role.value,
            f"expected {expected_identity}, observed {observed_identity}",
        )
    audit = audit_ptx(
        artifact.ptx,
        abi_name=leaf.abi_name,
        accepted_isa=accepted_ptx_isa,
        allowed_external_symbols=allowed_external_symbols,
    )
    audited = {
        "ptx_sha256": str(audit["ptx_sha256"]),
        "ptx_version": str(audit["ptx_version"]),
        "ptx_target": str(audit["ptx_target"]),
        "external_symbols": tuple(audit["external_symbols"]),
    }
    recorded = {name: getattr(artifact, name) for name in audited}
    if recorded != audited:
        _fail(
            "formal_leaf_cache_ptx_audit",
            leaf.role.value,
            f"recorded {recorded}, audited {audited}",
        )
    return artifact


def _formal_numba_cache_root(
    leaf: GeneratedFormalNumbaLeaf,
    policy: FormalNumbaLeafCachePolicy | None,
) -> Path | None:
    configured = (
        os.fspath(policy.root)
        if policy is not None
        else os.environ.get(FORMAL_NUMBA_CACHE_ENV, "")
    )
    if not configured:
        _FORMAL_NUMBA_CACHE_COUNTS["disabled"] += 1
        return None
    configured_root = Path(configured)
    sealed = (
        policy.manifest is not None
        if policy is not None
        else bool(
            os.environ.get(FORMAL_NUMBA_CACHE_MANIFEST_ENV)
            or os.environ.get(FORMAL_NUMBA_CACHE_MANIFEST_SHA256_ENV)
        )
    )
    if configured_root.is_symlink():
        _fail("formal_leaf_cache_root", leaf.role.value, os.fspath(configured_root))
    if not configured_root.exists():
        if sealed:
            _fail(
                "formal_leaf_cache_root",
                leaf.role.value,
                "sealed cache root does not exist",
            )
        configured_root.mkdir(parents=True)
    if not configured_root.is_dir():
        _fail("formal_leaf_cache_root", leaf.role.value, os.fspath(configured_root))
    root = configured_root.resolve(strict=True)
    if not root.is_dir() or root.is_symlink():
        _fail("formal_leaf_cache_root", leaf.role.value, os.fspath(root))
    return root


def materialize_formal_numba_leaf_cache_manifest(
    cache_root: str | os.PathLike[str],
    output: str | os.PathLike[str],
) -> Path:
    """Seal the exact create-only leaf-cache membership for formal reuse.

    The manifest is intentionally separate from the cache directory so cache
    membership remains exactly one directory per content key.  Formal workers
    bind both the manifest bytes and every entry document byte before accepting
    a hit.  This is installation evidence; it does not make compilation free.
    """

    root_path = Path(cache_root)
    if root_path.is_symlink() or not root_path.is_dir():
        raise CallbackCodegenError(
            "formal_leaf_cache_root", "manifest", os.fspath(root_path)
        )
    root = root_path.resolve(strict=True)
    output_path = Path(output)
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"refusing to replace cache manifest: {output_path}")
    rows: list[dict[str, object]] = []
    for entry in sorted(root.iterdir(), key=lambda item: item.name):
        if (
            entry.is_symlink()
            or not entry.is_dir()
            or re.fullmatch(r"[0-9a-f]{64}", entry.name) is None
        ):
            raise CallbackCodegenError(
                "formal_leaf_cache_membership", "manifest", os.fspath(entry)
            )
        members = list(entry.iterdir())
        if len(members) != 1 or members[0].name != "artifact.json":
            raise CallbackCodegenError(
                "formal_leaf_cache_membership", entry.name,
                repr(sorted(item.name for item in members)),
            )
        artifact = members[0]
        if artifact.is_symlink() or not artifact.is_file():
            raise CallbackCodegenError(
                "formal_leaf_cache_member", entry.name, os.fspath(artifact)
            )
        rows.append({
            "key_sha256": entry.name,
            "artifact_json_sha256": _sha256_file(artifact),
            "artifact_json_size_bytes": artifact.stat().st_size,
        })
    if not rows:
        raise CallbackCodegenError(
            "formal_leaf_cache_empty", "manifest", "no compiled leaves"
        )
    entries_digest = hashlib.sha256(json.dumps(
        rows, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    document = {
        "schema": "rtdl.v4.formal_numba_leaf_cache_manifest.v1",
        "cache_root": os.fspath(root),
        "entry_count": len(rows),
        "entries_sha256": entries_digest,
        "entries": rows,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return output_path


def _formal_numba_cache_manifest_entry(
    root: Path,
    key_sha256: str,
    *,
    leaf: GeneratedFormalNumbaLeaf,
    policy: FormalNumbaLeafCachePolicy | None,
) -> Mapping[str, object] | None:
    if policy is None:
        manifest_name = os.environ.get(FORMAL_NUMBA_CACHE_MANIFEST_ENV, "")
        manifest_sha256 = os.environ.get(
            FORMAL_NUMBA_CACHE_MANIFEST_SHA256_ENV, ""
        )
    else:
        manifest_name = os.fspath(policy.manifest) if policy.manifest else ""
        manifest_sha256 = policy.manifest_sha256 or ""
    if not manifest_name and not manifest_sha256:
        return None
    if not manifest_name or re.fullmatch(r"[0-9a-f]{64}", manifest_sha256) is None:
        _fail("formal_leaf_cache_manifest_authority", leaf.role.value, "incomplete authority")
    path = Path(manifest_name)
    if path.is_symlink() or not path.is_file():
        _fail("formal_leaf_cache_manifest", leaf.role.value, os.fspath(path))
    if _sha256_file(path) != manifest_sha256:
        _fail("formal_leaf_cache_manifest_digest", leaf.role.value, "manifest digest mismatch")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CallbackCodegenError(
            "formal_leaf_cache_manifest", leaf.role.value, f"cannot read manifest: {exc}"
        ) from exc
    expected_fields = {
        "schema", "cache_root", "entry_count", "entries_sha256", "entries"
    }
    if not isinstance(document, dict) or set(document) != expected_fields:
        _fail("formal_leaf_cache_manifest_fields", leaf.role.value, "unexpected manifest shape")
    rows = document["entries"]
    if (
        document["schema"] != "rtdl.v4.formal_numba_leaf_cache_manifest.v1"
        or document["cache_root"] != os.fspath(root)
        or not isinstance(rows, list)
        or document["entry_count"] != len(rows)
        or document["entries_sha256"] != hashlib.sha256(json.dumps(
            rows, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")).hexdigest()
    ):
        _fail("formal_leaf_cache_manifest_identity", leaf.role.value, "manifest identity mismatch")
    by_key: dict[str, Mapping[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "key_sha256", "artifact_json_sha256", "artifact_json_size_bytes"
        }:
            _fail("formal_leaf_cache_manifest_row", leaf.role.value, "malformed row")
        name = row["key_sha256"]
        if not isinstance(name, str) or name in by_key:
            _fail("formal_leaf_cache_manifest_row", leaf.role.value, "duplicate key")
        by_key[name] = row
    row = by_key.get(key_sha256)
    if row is None:
        _fail("formal_leaf_cache_manifest_miss", leaf.role.value, key_sha256)
    artifact = root / key_sha256 / "artifact.json"
    if (
        artifact.is_symlink()
        or not artifact.is_file()
        or artifact.stat().st_size != row["artifact_json_size_bytes"]
        or _sha256_file(artifact) != row["artifact_json_sha256"]
    ):
        _fail("formal_leaf_cache_manifest_entry", leaf.role.value, key_sha256)
    return row


def _load_formal_numba_cache_entry(
    root: Path,
    key_sha256: str,
    key: Mapping[str, object],
    *,
    leaf: GeneratedFormalNumbaLeaf,
    compute_capability: tuple[int, int],
    accepted_ptx_isa: tuple[str, str],
    allowed_external_symbols: frozenset[str],
    expected_python_version: str,
    expected_numba_version: str,
) -> DeviceFunctionArtifact | None:
    entry = root / key_sha256
    if not entry.exists():
        return None
    if entry.is_symlink() or not entry.is_dir() or entry.parent.resolve() != root:
        _fail("formal_leaf_cache_entry", leaf.role.value, os.fspath(entry))
    members = list(entry.iterdir())
    if len(members) != 1 or members[0].name != "artifact.json":
        _fail("formal_leaf_cache_membership", leaf.role.value, repr(sorted(item.name for item in members)))
    path = members[0]
    if path.is_symlink() or not path.is_file():
        _fail("formal_leaf_cache_member", leaf.role.value, os.fspath(path))
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CallbackCodegenError(
            "formal_leaf_cache_document", leaf.role.value, f"cannot read entry: {exc}"
        ) from exc
    if not isinstance(document, dict) or set(document) != {
        "schema", "key_sha256", "key", "artifact"
    }:
        _fail("formal_leaf_cache_document_fields", leaf.role.value, "unexpected document shape")
    if document["schema"] != FORMAL_NUMBA_CACHE_SCHEMA:
        _fail("formal_leaf_cache_schema", leaf.role.value, repr(document["schema"]))
    if document["key_sha256"] != key_sha256 or document["key"] != dict(key):
        _fail("formal_leaf_cache_key", leaf.role.value, "cache key mismatch")
    return _device_function_artifact_from_dict(
        document["artifact"],
        leaf=leaf,
        compute_capability=compute_capability,
        accepted_ptx_isa=accepted_ptx_isa,
        allowed_external_symbols=allowed_external_symbols,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
    )


def _store_formal_numba_cache_entry(
    root: Path,
    key_sha256: str,
    key: Mapping[str, object],
    artifact: DeviceFunctionArtifact,
) -> None:
    destination = root / key_sha256
    temporary = Path(tempfile.mkdtemp(prefix=f".{key_sha256}.tmp-", dir=root))
    try:
        document = {
            "schema": FORMAL_NUMBA_CACHE_SCHEMA,
            "key_sha256": key_sha256,
            "key": dict(key),
            "artifact": _device_function_artifact_dict(artifact),
        }
        payload = json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n"
        path = temporary / "artifact.json"
        path.write_text(payload, encoding="utf-8", newline="\n")
        try:
            temporary.rename(destination)
        except OSError:
            # A concurrent compiler won the create-only race.  Its exact entry
            # is reloaded and verified by the caller before use.
            if not destination.exists():
                raise
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def _artifact_from_formal_compile_response(
    leaf: GeneratedFormalNumbaLeaf,
    response: object,
    *,
    compute_capability: tuple[int, int],
    accepted_ptx_isa: tuple[str, str],
    allowed_external_symbols: frozenset[str],
    expected_python_version: str,
    expected_numba_version: str,
    expected_numpy_version: str,
) -> DeviceFunctionArtifact:
    expected_response_fields = {
        "schema", "generated_source_sha256", "ptx", "numba_version",
        "numpy_version", "python_version", "cuda_available_was_queried",
        "explicit_compute_capability",
    }
    if not isinstance(response, dict) or set(response) != expected_response_fields:
        _fail("compiler_response_fields", leaf.role.value,
              "unexpected compiler response shape")
    if response["schema"] != "rtdl.v4.numba_compile_response.v1":
        _fail("compiler_response_schema", leaf.role.value,
              repr(response["schema"]))
    if response["cuda_available_was_queried"] is not False:
        _fail("compiler_cuda_probe", leaf.role.value,
              "isolated leaf compiler queried CUDA availability")
    if response["explicit_compute_capability"] != list(compute_capability):
        _fail("compiler_compute_capability", leaf.role.value,
              "compiler child target mismatch")
    if response.get("generated_source_sha256") != leaf.generated_source_sha256:
        _fail("compiler_source_identity", leaf.role.value,
              "compiler child source mismatch")
    observed = {
        "python": response.get("python_version"),
        "numba": response.get("numba_version"),
        "numpy": response.get("numpy_version"),
    }
    expected = {
        "python": expected_python_version,
        "numba": expected_numba_version,
        "numpy": expected_numpy_version,
    }
    if observed != expected:
        _fail("compiler_toolchain_identity", leaf.role.value,
              f"expected {expected}, observed {observed}")
    ptx = response["ptx"]
    audit = audit_ptx(
        ptx,
        abi_name=leaf.abi_name,
        accepted_isa=accepted_ptx_isa,
        allowed_external_symbols=allowed_external_symbols,
    )
    return DeviceFunctionArtifact(
        schema="rtdl.v4.formal_device_function_artifact.v1",
        role=leaf.role.value,
        abi_name=leaf.abi_name,
        compute_capability=compute_capability,
        numeric_mode=leaf.numeric_mode,
        generated_source_sha256=leaf.generated_source_sha256,
        ir_sha256=leaf.callback_ir_sha256,
        ptx=ptx,
        ptx_sha256=str(audit["ptx_sha256"]),
        ptx_version=str(audit["ptx_version"]),
        ptx_target=str(audit["ptx_target"]),
        external_symbols=tuple(audit["external_symbols"]),
        numba_version=str(observed["numba"]),
        python_version=str(observed["python"]),
        nonce_word=leaf.nonce_word,
        compiler_function_count=leaf.compiler_function_count,
    )


def _isolated_numba_child_command(
    python_executable: str | os.PathLike[str],
    request_path: Path,
    response_path: Path,
) -> list[str]:
    """Address the frozen compiler child without installing RTDL in its venv.

    Source-first callers insert RTDL into the parent process's ``sys.path``;
    that in-memory insertion cannot cross a subprocess boundary.  Execute the
    exact sibling child file instead of asking a fresh interpreter to resolve
    an independently installed ``rtdsl`` package.  The child imports no RTDL
    module and receives only compiler-generated source through the request.
    """

    child = Path(__file__).with_name("_v4_numba_compile_child.py").absolute()
    if child.is_symlink():
        _fail("isolated_numba_compile_child", "path", "symlink forbidden")
    try:
        resolved = child.resolve(strict=True)
    except OSError as error:
        raise CallbackCodegenError(
            "isolated_numba_compile_child", "path", "child is absent") from error
    if not resolved.is_file():
        _fail(
            "isolated_numba_compile_child", "path",
            "child is not a regular file")
    return [
        os.fspath(python_executable), "-s", "-B", "-P",
        os.fspath(resolved), os.fspath(request_path), os.fspath(response_path),
    ]


def _isolated_numba_child_environment() -> dict[str, str]:
    environment = {
        key: value for key, value in os.environ.items()
        if not key.upper().startswith("PYTHON")
    }
    environment.update({
        "PYTHONHASHSEED": "0",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONSAFEPATH": "1",
    })
    return environment


def compile_formal_numba_leaf_isolated(
    leaf: GeneratedFormalNumbaLeaf,
    *,
    compute_capability: tuple[int, int],
    accepted_ptx_isa: tuple[str, str],
    allowed_external_symbols: frozenset[str],
    expected_python_version: str,
    expected_numba_version: str,
    expected_numpy_version: str,
    python_executable: str | os.PathLike[str] = sys.executable,
    formal_leaf_cache: FormalNumbaLeafCachePolicy | None = None,
    _cache_policy_identity: Mapping[str, object] | None = None,
) -> DeviceFunctionArtifact:
    """Compile only the deterministic formal leaf in a fresh child process."""

    if leaf.schema != FORMAL_NUMBA_SOURCE_SCHEMA:
        _fail("leaf_schema", leaf.role.value, leaf.schema)
    if hashlib.sha256(leaf.generated_source.encode("utf-8")).hexdigest() != leaf.generated_source_sha256:
        _fail("leaf_source_digest", leaf.role.value, "generated source identity mismatch")
    if len(compute_capability) != 2 or min(compute_capability) <= 0:
        _fail("compute_capability", leaf.role.value, repr(compute_capability))
    request = {
        "schema": FORMAL_NUMBA_SOURCE_SCHEMA,
        "generated_source": leaf.generated_source,
        "generated_source_sha256": leaf.generated_source_sha256,
        "abi_name": leaf.abi_name,
        "parameter_types": list(leaf.parameter_types),
        "numeric_mode": leaf.numeric_mode,
        "compute_capability": list(compute_capability),
    }
    if formal_leaf_cache is not None and not isinstance(
        formal_leaf_cache, FormalNumbaLeafCachePolicy
    ):
        raise TypeError("formal_leaf_cache must be FormalNumbaLeafCachePolicy or None")
    cache_root = _formal_numba_cache_root(leaf, formal_leaf_cache)
    cache_key_sha256: str | None = None
    cache_key: dict[str, object] | None = None
    if cache_root is not None:
        cache_key_sha256, cache_key = _formal_numba_cache_key(
            leaf,
            compute_capability=compute_capability,
            accepted_ptx_isa=accepted_ptx_isa,
            allowed_external_symbols=allowed_external_symbols,
            expected_python_version=expected_python_version,
            expected_numba_version=expected_numba_version,
            expected_numpy_version=expected_numpy_version,
            python_executable=python_executable,
            policy_identity=_cache_policy_identity,
        )
        manifest_entry = _formal_numba_cache_manifest_entry(
            cache_root,
            cache_key_sha256,
            leaf=leaf,
            policy=formal_leaf_cache,
        )
        cached = _load_formal_numba_cache_entry(
            cache_root,
            cache_key_sha256,
            cache_key,
            leaf=leaf,
            compute_capability=compute_capability,
            accepted_ptx_isa=accepted_ptx_isa,
            allowed_external_symbols=allowed_external_symbols,
            expected_python_version=expected_python_version,
            expected_numba_version=expected_numba_version,
        )
        if cached is not None:
            _FORMAL_NUMBA_CACHE_COUNTS["hit"] += 1
            return cached
        if manifest_entry is not None:
            _fail(
                "formal_leaf_cache_manifest_miss",
                leaf.role.value,
                "sealed entry was not loadable",
            )
    with tempfile.TemporaryDirectory(prefix="rtdl-v4-formal-numba-") as directory:
        request_path = Path(directory) / "request.json"
        response_path = Path(directory) / "response.json"
        request_path.write_text(json.dumps(request, sort_keys=True), encoding="utf-8")
        environment = _isolated_numba_child_environment()
        completed = subprocess.run(
            _isolated_numba_child_command(
                python_executable, request_path, response_path),
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )
        if completed.returncode:
            raise CallbackCodegenError(
                "isolated_numba_compile",
                leaf.role.value,
                "stdout:\n" + completed.stdout + "\nstderr:\n" + completed.stderr,
            )
        response = json.loads(response_path.read_text(encoding="utf-8"))
    artifact = _artifact_from_formal_compile_response(
        leaf,
        response,
        compute_capability=compute_capability,
        accepted_ptx_isa=accepted_ptx_isa,
        allowed_external_symbols=allowed_external_symbols,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version,
    )
    if cache_root is None:
        return artifact
    sealed = (
        formal_leaf_cache.manifest is not None
        if formal_leaf_cache is not None
        else bool(
            os.environ.get(FORMAL_NUMBA_CACHE_MANIFEST_ENV)
            or os.environ.get(FORMAL_NUMBA_CACHE_MANIFEST_SHA256_ENV)
        )
    )
    if sealed:
        _fail(
            "formal_leaf_cache_sealed_write",
            leaf.role.value,
            "sealed formal cache is read-only",
        )
    assert cache_key_sha256 is not None and cache_key is not None
    _store_formal_numba_cache_entry(cache_root, cache_key_sha256, cache_key, artifact)
    persisted = _load_formal_numba_cache_entry(
        cache_root,
        cache_key_sha256,
        cache_key,
        leaf=leaf,
        compute_capability=compute_capability,
        accepted_ptx_isa=accepted_ptx_isa,
        allowed_external_symbols=allowed_external_symbols,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
    )
    if persisted is None:
        _fail("formal_leaf_cache_materialization", leaf.role.value, "entry missing after create")
    if _device_function_artifact_dict(persisted) != _device_function_artifact_dict(artifact):
        _fail("formal_leaf_cache_materialization", leaf.role.value, "persisted artifact mismatch")
    _FORMAL_NUMBA_CACHE_COUNTS["miss"] += 1
    return persisted


def compile_formal_numba_leaves_isolated(
    leaves: Sequence[GeneratedFormalNumbaLeaf],
    *,
    compute_capability: tuple[int, int],
    accepted_ptx_isa: tuple[str, str],
    allowed_external_symbols: frozenset[str],
    expected_python_version: str,
    expected_numba_version: str,
    expected_numpy_version: str,
    python_executable: str | os.PathLike[str] = sys.executable,
    formal_leaf_cache: FormalNumbaLeafCachePolicy | None = None,
) -> tuple[DeviceFunctionArtifact, ...]:
    """Compile a closed leaf set in one fresh compiler child.

    A configured cache retains the existing per-leaf sealed-cache semantics.
    With no cache authority, batching pays the isolated Python/Numba startup
    once while preserving one request, response, PTX audit, and identity check
    per leaf.
    """

    rows = tuple(leaves)
    if not rows:
        raise ValueError("at least one formal leaf is required")
    if formal_leaf_cache is not None and not isinstance(
        formal_leaf_cache, FormalNumbaLeafCachePolicy
    ):
        raise TypeError("formal_leaf_cache must be FormalNumbaLeafCachePolicy or None")
    if formal_leaf_cache is not None or any(
        os.environ.get(name)
        for name in (
            FORMAL_NUMBA_CACHE_ENV,
            FORMAL_NUMBA_CACHE_MANIFEST_ENV,
            FORMAL_NUMBA_CACHE_MANIFEST_SHA256_ENV,
        )
    ):
        before_policy = _formal_numba_cache_policy_identity(
            python_executable, role="batch")
        artifacts = tuple(compile_formal_numba_leaf_isolated(
            leaf,
            compute_capability=compute_capability,
            accepted_ptx_isa=accepted_ptx_isa,
            allowed_external_symbols=allowed_external_symbols,
            expected_python_version=expected_python_version,
            expected_numba_version=expected_numba_version,
            expected_numpy_version=expected_numpy_version,
            python_executable=python_executable,
            formal_leaf_cache=formal_leaf_cache,
            _cache_policy_identity=before_policy,
        ) for leaf in rows)
        after_policy = _formal_numba_cache_policy_identity(
            python_executable, role="batch")
        if after_policy != before_policy:
            _fail(
                "formal_leaf_cache_policy_snapshot",
                "batch",
                "compiler policy changed while loading the closed leaf set",
            )
        return artifacts
    if len(compute_capability) != 2 or min(compute_capability) <= 0:
        _fail("compute_capability", "batch", repr(compute_capability))
    requests = []
    for leaf in rows:
        if leaf.schema != FORMAL_NUMBA_SOURCE_SCHEMA:
            _fail("leaf_schema", leaf.role.value, leaf.schema)
        if hashlib.sha256(leaf.generated_source.encode("utf-8")).hexdigest() \
                != leaf.generated_source_sha256:
            _fail("leaf_source_digest", leaf.role.value,
                  "generated source identity mismatch")
        requests.append({
            "schema": FORMAL_NUMBA_SOURCE_SCHEMA,
            "generated_source": leaf.generated_source,
            "generated_source_sha256": leaf.generated_source_sha256,
            "abi_name": leaf.abi_name,
            "parameter_types": list(leaf.parameter_types),
            "numeric_mode": leaf.numeric_mode,
            "compute_capability": list(compute_capability),
        })
    _FORMAL_NUMBA_CACHE_COUNTS["disabled"] += len(rows)
    batch_request = {
        "schema": "rtdl.v4.generated_formal_numba_leaf_batch.v1",
        "requests": requests,
    }
    with tempfile.TemporaryDirectory(
            prefix="rtdl-v4-formal-numba-batch-") as directory:
        request_path = Path(directory) / "request.json"
        response_path = Path(directory) / "response.json"
        request_path.write_text(
            json.dumps(batch_request, sort_keys=True), encoding="utf-8")
        environment = _isolated_numba_child_environment()
        completed = subprocess.run(
            _isolated_numba_child_command(
                python_executable, request_path, response_path),
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )
        if completed.returncode:
            raise CallbackCodegenError(
                "isolated_numba_compile_batch",
                ",".join(leaf.role.value for leaf in rows),
                "stdout:\n" + completed.stdout + "\nstderr:\n" + completed.stderr,
            )
        response = json.loads(response_path.read_text(encoding="utf-8"))
    if not isinstance(response, dict) or set(response) != {"schema", "responses"} \
            or response["schema"] != "rtdl.v4.numba_compile_batch_response.v1" \
            or not isinstance(response["responses"], list) \
            or len(response["responses"]) != len(rows):
        _fail("compiler_batch_response", "batch",
              "unexpected compiler batch response shape")
    return tuple(
        _artifact_from_formal_compile_response(
            leaf,
            item,
            compute_capability=compute_capability,
            accepted_ptx_isa=accepted_ptx_isa,
            allowed_external_symbols=allowed_external_symbols,
            expected_python_version=expected_python_version,
            expected_numba_version=expected_numba_version,
            expected_numpy_version=expected_numpy_version,
        )
        for leaf, item in zip(rows, response["responses"], strict=True)
    )


def _reachable_helpers(
    function: CallbackFunction,
    helpers: Mapping[str, CallbackFunction],
) -> frozenset[str]:
    """Return the exact transitive helper set reachable from one role."""

    result: set[str] = set()

    def visit_expression(expression: CallbackExpr) -> None:
        if expression.opcode == "helper_call":
            name = str(dict(expression.attributes)["name"])
            if name not in result:
                helper = helpers.get(name)
                if helper is None:
                    _fail("helper", function.name, name)
                result.add(name)
                visit_statements(helper.body)
        for operand in expression.operands:
            visit_expression(operand)

    def visit_statements(statements: Sequence[CallbackStatement]) -> None:
        for statement in statements:
            if isinstance(statement, (LetStatement, SetStatement, ReturnValueStatement)):
                visit_expression(statement.value)
            elif isinstance(statement, ReturnEffectStatement):
                for _, expression in statement.effect.fields:
                    visit_expression(expression)
            elif isinstance(statement, IfStatement):
                visit_expression(statement.condition)
                visit_statements(statement.then_body)
                visit_statements(statement.else_body)
            elif isinstance(statement, StaticForStatement):
                visit_statements(statement.body)

    visit_statements(function.body)
    return frozenset(result)


def _emit_helper(emitter: _Emitter, helper: CallbackFunction) -> None:
    assert helper.return_type is not None
    semantic_names = [_local_name(item.name) for item in helper.arguments]
    status_names = [emitter.status_names[item.path] for item in emitter.role_abi.status]
    emitter.emit(f"def _rtdl_helper_{_identifier(helper.name)}({', '.join(semantic_names + status_names)}):")
    with emitter.block():
        environment: dict[str, _Value | _View] = emitter._constant_environment()
        for argument, name in zip(helper.arguments, semantic_names):
            if argument.value_type.kind is TypeKind.READ_ONLY_VIEW:
                _fail("helper_view", helper.name, "view helpers require the later pointer-threading tranche")
            environment[argument.name] = _value_from_code(argument.value_type, name, emitter.records)
        previous = emitter.current_return_type
        emitter.current_return_type = helper.return_type
        emitter._emit_statements(helper.body, environment, f"helper.{helper.name}")
        emitter.current_return_type = previous


def _parameter_types(role: RoleAbi) -> tuple[str, ...]:
    fields = {item.path: item for item in role.inputs + role.status}
    for variant in role.effects:
        fields.update({item.path: item for item in variant.fields})
    result: list[str] = []
    for path in role.parameter_order:
        if path == "out.effect_tag":
            result.append("ptr<u32>")
            continue
        field = fields[path]
        if field.direction == "out":
            result.append(f"ptr<{field.scalar}>")
        else:
            result.append(field.scalar)
    return tuple(result)


def _abi_output_field(role: RoleAbi, path: str):
    for variant in role.effects:
        for field in variant.fields:
            if field.path == path:
                return field
    raise KeyError(path)


def _parameter_name(path: str) -> str:
    return _identifier(path.replace(".", "_"))


def _local_name(name: str) -> str:
    return f"_rtdl_local_{_identifier(name)}"


def _identifier(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not result or result[0].isdigit():
        result = "_" + result
    return result


def _scalar_type(kind: ScalarKind) -> CallbackType:
    return CallbackType(TypeKind.SCALAR, scalar=kind)


def _record_members(
    value_type: CallbackType,
    records: Mapping[str, CallbackRecord],
) -> tuple[tuple[str, CallbackType], ...]:
    if value_type.kind is TypeKind.VECTOR:
        assert value_type.scalar is not None
        return tuple((name, _scalar_type(value_type.scalar)) for name in "xyzw"[:value_type.lanes])
    if value_type.kind is TypeKind.TUPLE:
        return tuple((str(index), item) for index, item in enumerate(value_type.items))
    if value_type.kind is TypeKind.RECORD:
        record = records[value_type.name or ""]
        return tuple((item.name, item.value_type) for item in record.fields)
    if value_type.kind is TypeKind.BUILTIN:
        if value_type.name == "Ray3f":
            return (
                ("origin", CallbackType(TypeKind.VECTOR, scalar=ScalarKind.F32, lanes=3)),
                ("direction", CallbackType(TypeKind.VECTOR, scalar=ScalarKind.F32, lanes=3)),
                ("tmin", _scalar_type(ScalarKind.F32)),
                ("tmax", _scalar_type(ScalarKind.F32)),
            )
        if value_type.name == "Hit":
            return (("t", _scalar_type(ScalarKind.F32)), ("hit_kind", _scalar_type(ScalarKind.U32)))
        if value_type.name == "TriangleHit":
            return (
                ("t", _scalar_type(ScalarKind.F32)),
                ("primitive_index", _scalar_type(ScalarKind.U32)),
                ("hit_kind", _scalar_type(ScalarKind.U32)),
                (
                    "barycentrics",
                    CallbackType(TypeKind.VECTOR, scalar=ScalarKind.F32, lanes=2),
                ),
            )
        if value_type.name == "Aabb3f":
            vector = CallbackType(TypeKind.VECTOR, scalar=ScalarKind.F32, lanes=3)
            return (("lower", vector), ("upper", vector))
    _fail("compound_type", "type", json.dumps(value_type.to_dict(), sort_keys=True))
    raise AssertionError


def _leaf_count(value_type: CallbackType, records: Mapping[str, CallbackRecord]) -> int:
    if value_type.kind is TypeKind.SCALAR:
        return 1
    if value_type.kind is TypeKind.READ_ONLY_VIEW:
        _fail("view_leaf_count", "type", "view has pointer columns, not value leaves")
    return sum(_leaf_count(item, records) for _, item in _record_members(value_type, records))


def _leaf_scalar_kinds(
    value_type: CallbackType,
    records: Mapping[str, CallbackRecord],
) -> tuple[ScalarKind, ...]:
    if value_type.kind is TypeKind.SCALAR:
        assert value_type.scalar is not None
        return (value_type.scalar,)
    if value_type.kind is TypeKind.READ_ONLY_VIEW:
        _fail("view_scalar_kinds", "type", "view has no inline scalar leaves")
    return tuple(
        kind
        for _, item in _record_members(value_type, records)
        for kind in _leaf_scalar_kinds(item, records)
    )


def _field_value(
    base: _Value,
    name: str,
    records: Mapping[str, CallbackRecord],
) -> _Value:
    offset = 0
    for field_name, field_type in _record_members(base.value_type, records):
        count = _leaf_count(field_type, records)
        if field_name == name:
            return _Value(field_type, base.leaves[offset:offset + count])
        offset += count
    _fail("field", name, "field not present in compound value")
    raise AssertionError


def _value_from_code(
    value_type: CallbackType,
    code: str,
    records: Mapping[str, CallbackRecord],
) -> _Value:
    count = _leaf_count(value_type, records)
    if count == 1:
        return _Value(value_type, (code,))
    return _Value(value_type, tuple(f"{code}[{index}]" for index in range(count)))


def _value_expression(value: _Value) -> str:
    if len(value.leaves) == 1:
        return value.leaves[0]
    return "(" + ", ".join(value.leaves) + ",)"


def _literal_value(
    value_type: CallbackType,
    value: object,
    records: Mapping[str, CallbackRecord],
) -> _Value:
    kinds = _leaf_scalar_kinds(value_type, records)
    flat = _flatten_literal(value)
    if len(kinds) != len(flat):
        _fail("literal_layout", "literal", repr(value))
    leaves = tuple(_literal_scalar(kind, item) for kind, item in zip(kinds, flat))
    return _Value(value_type, leaves)


def _flatten_literal(value: object) -> tuple[object, ...]:
    if isinstance(value, tuple):
        return tuple(item for nested in value for item in _flatten_literal(nested))
    return (value,)


def _literal_scalar(kind: ScalarKind, value: object) -> str:
    if kind is ScalarKind.BOOL:
        return "True" if bool(value) else "False"
    if kind is ScalarKind.F32:
        return f"_f32({float(value)!r})"
    if kind is ScalarKind.F64:
        return repr(float(value))
    return repr(int(value))


def _default_expression(
    value_type: CallbackType,
    records: Mapping[str, CallbackRecord],
) -> str:
    kinds = _leaf_scalar_kinds(value_type, records)
    leaves = ["False" if kind is ScalarKind.BOOL else "0.0" if kind in {ScalarKind.F32, ScalarKind.F64} else "0" for kind in kinds]
    if len(leaves) == 1:
        return leaves[0]
    return "(" + ", ".join(leaves) + ",)"


def _integer_bounds(kind: ScalarKind) -> tuple[int, int]:
    return {
        ScalarKind.I32: (-(1 << 31), (1 << 31) - 1),
        ScalarKind.U32: (0, (1 << 32) - 1),
        ScalarKind.I64: (-(1 << 63), (1 << 63) - 1),
        ScalarKind.U64: (0, (1 << 64) - 1),
    }[kind]


def _scalar_default(scalar: str) -> str:
    if scalar.startswith("device_ptr"):
        return "0"
    return "0.0" if scalar in {"f32", "f64"} else "0"


def _fail(code: str, path: str, message: str) -> None:
    raise CallbackCodegenError(code, path, message)


__all__ = [
    "FORMAL_NUMBA_CACHE_ENV",
    "FORMAL_NUMBA_CACHE_MANIFEST_ENV",
    "FORMAL_NUMBA_CACHE_MANIFEST_SHA256_ENV",
    "FORMAL_NUMBA_CACHE_SCHEMA",
    "FORMAL_NUMBA_SOURCE_SCHEMA",
    "CallbackCodegenError",
    "FormalNumbaLeafCachePolicy",
    "GeneratedFormalNumbaLeaf",
    "compile_formal_numba_leaf_isolated",
    "compile_formal_numba_leaves_isolated",
    "formal_numba_leaf_cache_lifecycle_metadata",
    "generate_formal_numba_leaf",
    "materialize_formal_numba_leaf_cache_manifest",
]
