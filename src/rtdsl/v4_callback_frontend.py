"""Text-only restricted Python frontend for V4 Callback IR v1.

The module is parsed with :mod:`ast`; it is never imported or executed.  The
separate manifest is authoritative for resources, geometry, numeric policy and
the selected backend linkage mechanism.
"""

from __future__ import annotations

import ast
import hashlib
import math
import textwrap
from typing import Mapping, Sequence

from .v4_callback_ir import (
    AABB3F, BOOL, CALLBACK_IR_SCHEMA_ID, CALLBACK_IR_SCHEMA_VERSION,
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION, F32, F64,
    HIT, TRIANGLE_HIT, I32, I64, RAY3F, U32, U64, VEC2F32, VEC3F32, VEC4F32,
    CallbackArgument, CallbackEffect, CallbackExpr, CallbackField,
    CallbackFunction, CallbackModuleManifest, CallbackProgramSpec,
    CallbackRecord, CallbackRole, CallbackStatement, CallbackType, GeometryProofAuthority,
    CallbackVerificationError, EffectKind, IfStatement, LetStatement,
    RecordPurpose, ReturnEffectStatement, ReturnValueStatement, ScalarKind,
    SetStatement, StaticForStatement, TypeKind, VerifiedCallbackProgram,
    builtin_type, read_only_view, record_type, scalar_type, tuple_type,
    vector_type, verify_callback_program,
)


_SCALAR_TYPES: Mapping[str, CallbackType] = {
    "bool": BOOL, "i32": I32, "u32": U32, "i64": I64, "u64": U64,
    "f32": F32, "f64": F64,
}
_VECTOR_TYPES: Mapping[str, CallbackType] = {
    "vec2f32": VEC2F32, "vec3f32": VEC3F32, "vec4f32": VEC4F32,
    "vec2i32": vector_type(ScalarKind.I32, 2),
    "vec3i32": vector_type(ScalarKind.I32, 3),
    "vec4i32": vector_type(ScalarKind.I32, 4),
    "vec2u32": vector_type(ScalarKind.U32, 2),
    "vec3u32": vector_type(ScalarKind.U32, 3),
    "vec4u32": vector_type(ScalarKind.U32, 4),
}
_BUILTIN_TYPES: Mapping[str, CallbackType] = {
    "Ray3f": RAY3F, "Hit": HIT, "TriangleHit": TRIANGLE_HIT,
    "Aabb3f": AABB3F,
}
_RECORD_DECORATORS = {
    "optix.payload": RecordPurpose.PAYLOAD,
    "optix.record": RecordPurpose.DATA,
    "optix.output": RecordPurpose.OUTPUT,
}
_ROLE_DECORATORS = {f"optix.{role.value}": role for role in CallbackRole}
_BINOPS = {
    ast.Add: "add", ast.Sub: "sub", ast.Mult: "mul", ast.Div: "div",
    ast.BitAnd: "bit_and", ast.BitOr: "bit_or", ast.BitXor: "bit_xor",
    ast.LShift: "shift_left", ast.RShift: "shift_right",
}
_CMPOPS = {
    ast.Eq: "eq", ast.NotEq: "ne", ast.Lt: "lt", ast.LtE: "le",
    ast.Gt: "gt", ast.GtE: "ge",
}
_EFFECTS = {
    "optix.aabb": EffectKind.AABB,
    "optix.trace_request": EffectKind.TRACE_REQUEST,
    "optix.hit": EffectKind.HIT,
    "optix.no_hit": EffectKind.NO_HIT,
    "optix.accept_continue": EffectKind.ACCEPT_CONTINUE,
    "optix.ignore": EffectKind.IGNORE,
    "optix.terminate": EffectKind.TERMINATE,
    "optix.payload": EffectKind.PAYLOAD,
    "optix.output": EffectKind.OUTPUT,
}


def compile_callback_source(
    source: str,
    manifest: CallbackModuleManifest,
    *,
    geometry_proof_authorities: Mapping[str, GeometryProofAuthority] | None = None,
) -> VerifiedCallbackProgram:
    """Compile source text to verified, backend-neutral Callback IR."""

    spec = parse_callback_source(source, manifest)
    return verify_callback_program(
        spec,
        geometry_proof_authorities=geometry_proof_authorities,
    )


def parse_callback_source(
    source: str,
    manifest: CallbackModuleManifest,
    *,
    schema_version: str = CALLBACK_IR_SCHEMA_VERSION,
) -> CallbackProgramSpec:
    if schema_version not in {CALLBACK_IR_SCHEMA_VERSION, CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION}:
        _fail("schema_version", "module", schema_version)
    if not isinstance(source, str) or not source.strip():
        _fail("empty_source", "module", "source must be nonempty UTF-8 text")
    try:
        tree = ast.parse(textwrap.dedent(source), mode="exec", type_comments=False)
    except SyntaxError as exc:
        raise CallbackVerificationError("syntax_error", "module", str(exc)) from exc
    if any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(tree)):
        _fail("import_forbidden", "module", "imports are never executed or admitted")

    record_nodes: list[tuple[ast.ClassDef, RecordPurpose]] = []
    program_nodes: list[ast.ClassDef] = []
    helper_nodes: list[ast.FunctionDef] = []
    for index, node in enumerate(tree.body):
        path = f"module.body[{index}]"
        if isinstance(node, ast.ClassDef):
            decorator = _single_decorator_name(node.decorator_list, path)
            if decorator in _RECORD_DECORATORS:
                record_nodes.append((node, _RECORD_DECORATORS[decorator]))
            elif _is_program_decorator(node.decorator_list):
                program_nodes.append(node)
            else:
                _fail("class_decorator", path, repr(decorator))
        elif isinstance(node, ast.FunctionDef):
            decorator = _single_decorator_name(node.decorator_list, path)
            if decorator != "optix.helper":
                _fail("top_level_function", path, "only @optix.helper is admitted")
            helper_nodes.append(node)
        else:
            _fail("top_level_statement", path, type(node).__name__)
    if len(program_nodes) != 1:
        _fail("program_cardinality", "module", "exactly one @optix.program class is required")

    record_names = {node.name for node, _ in record_nodes}
    if len(record_names) != len(record_nodes):
        _fail("record_name", "module", "record names must be unique")
    records = tuple(_compile_record(node, purpose, record_names) for node, purpose in record_nodes)
    records_by_name = {item.name: item for item in records}
    _verify_program_decorator(program_nodes[0], manifest, records_by_name)

    helper_signatures: dict[str, tuple[tuple[CallbackType, ...], CallbackType]] = {}
    for node in helper_nodes:
        if node.name in helper_signatures:
            _fail("helper_name", f"helper.{node.name}", "duplicate helper")
        arguments, return_type = _function_signature(node, records_by_name, require_return=True)
        assert return_type is not None
        helper_signatures[node.name] = (tuple(item.value_type for item in arguments), return_type)

    functions: list[CallbackFunction] = []
    for node in helper_nodes:
        arguments, return_type = _function_signature(node, records_by_name, require_return=True)
        compiler = _FunctionCompiler(
            node, arguments, records_by_name, manifest, helper_signatures,
            role=None, return_type=return_type,
        )
        functions.append(compiler.compile())

    role_names: set[CallbackRole] = set()
    for index, item in enumerate(program_nodes[0].body):
        if not isinstance(item, ast.FunctionDef):
            _fail("program_member", f"program.body[{index}]", "only role methods are admitted")
        decorator = _single_decorator_name(item.decorator_list, f"program.body[{index}]")
        role = _ROLE_DECORATORS.get(decorator)
        if role is None:
            _fail("role_decorator", f"program.body[{index}]", repr(decorator))
        if role in role_names:
            _fail("duplicate_role", f"program.body[{index}]", role.value)
        role_names.add(role)
        arguments, _ = _function_signature(item, records_by_name, require_return=True)
        _verify_role_annotation(item.returns, role, manifest)
        compiler = _FunctionCompiler(
            item, arguments, records_by_name, manifest, helper_signatures,
            role=role, return_type=None,
        )
        functions.append(compiler.compile())

    normalized_source = ast.unparse(tree).strip() + "\n"
    return CallbackProgramSpec(
        schema_id=CALLBACK_IR_SCHEMA_ID,
        schema_version=schema_version,
        manifest=manifest,
        records=tuple(sorted(records, key=lambda item: item.name)),
        functions=tuple(sorted(functions, key=lambda item: (item.role is not None, "" if item.role is None else item.role.value, item.name))),
        normalized_source=normalized_source,
        source_sha256=hashlib.sha256(normalized_source.encode("utf-8")).hexdigest(),
    )


class _FunctionCompiler:
    def __init__(
        self,
        node: ast.FunctionDef,
        arguments: tuple[CallbackArgument, ...],
        records: Mapping[str, CallbackRecord],
        manifest: CallbackModuleManifest,
        helpers: Mapping[str, tuple[tuple[CallbackType, ...], CallbackType]],
        *,
        role: CallbackRole | None,
        return_type: CallbackType | None,
    ) -> None:
        self.node = node
        self.arguments = arguments
        self.records = records
        self.manifest = manifest
        self.helpers = helpers
        self.role = role
        self.return_type = return_type
        self.constant_types = {item.name: item.value_type for item in manifest.constants}

    def compile(self) -> CallbackFunction:
        environment = dict(self.constant_types)
        for argument in self.arguments:
            if argument.name in environment:
                _fail("argument_constant_collision", f"function.{self.node.name}", argument.name)
            environment[argument.name] = argument.value_type
        body, _ = self._compile_statements(self.node.body, environment, inside_loop=False)
        return CallbackFunction(
            name=self.node.name,
            arguments=self.arguments,
            body=body,
            role=self.role,
            return_type=self.return_type,
        )

    def _compile_statements(
        self,
        statements: Sequence[ast.stmt],
        environment: Mapping[str, CallbackType],
        *,
        inside_loop: bool,
    ) -> tuple[tuple[CallbackStatement, ...], dict[str, CallbackType]]:
        values = dict(environment)
        result: list[CallbackStatement] = []
        for index, statement in enumerate(statements):
            path = f"function.{self.node.name}.body[{index}]"
            if isinstance(statement, ast.Assign):
                if len(statement.targets) != 1 or not isinstance(statement.targets[0], ast.Name):
                    _fail("assignment_target", path, "one local name is required")
                name = statement.targets[0].id
                if name.startswith("_"):
                    _fail("reserved_local", path, name)
                expected = values.get(name)
                value = self._expr(statement.value, values, expected=expected)
                if expected is None:
                    values[name] = value.value_type
                    result.append(LetStatement(name, value))
                else:
                    if not inside_loop:
                        _fail("ssa_reassignment", path, name)
                    if value.value_type != expected:
                        _fail("assignment_type", path, name)
                    result.append(SetStatement(name, value))
            elif isinstance(statement, ast.AugAssign):
                if not inside_loop or not isinstance(statement.target, ast.Name) or statement.target.id not in values:
                    _fail("augassign_scope", path, "augmented assignment is loop-local mutation only")
                name = statement.target.id
                left = _reference(name, values[name], constant=name in self.constant_types)
                right = self._expr(statement.value, values, expected=values[name])
                opcode = _BINOPS.get(type(statement.op))
                if opcode is None:
                    _fail("augassign_operator", path, type(statement.op).__name__)
                result.append(SetStatement(name, CallbackExpr(opcode, values[name], (left, right))))
            elif isinstance(statement, ast.If):
                if not statement.orelse:
                    _fail("if_else_required", path, "both branches are explicit")
                condition = self._expr(statement.test, values, expected=BOOL)
                then_body, then_values = self._compile_statements(statement.body, dict(values), inside_loop=inside_loop)
                else_body, else_values = self._compile_statements(statement.orelse, dict(values), inside_loop=inside_loop)
                both_return = _statements_definitely_return(then_body) and _statements_definitely_return(else_body)
                if not both_return and then_values != else_values:
                    _fail("branch_environment", path, "branches must define the same typed locals")
                if not both_return:
                    values = then_values
                result.append(IfStatement(condition, then_body, else_body))
            elif isinstance(statement, ast.For):
                if not isinstance(statement.target, ast.Name) or statement.orelse:
                    _fail("for_shape", path, "for requires one index and no else")
                index_name = statement.target.id
                if index_name in values:
                    _fail("loop_index_collision", path, index_name)
                trip_count = self._static_range(statement.iter, path)
                loop_values = dict(values); loop_values[index_name] = U32
                body, body_values = self._compile_statements(statement.body, loop_values, inside_loop=True)
                body_values.pop(index_name, None)
                if body_values != values:
                    _fail("loop_local_escape", path, "loop may mutate existing locals but not define escaping names")
                result.append(StaticForStatement(index_name, trip_count, body))
            elif isinstance(statement, ast.Return):
                if statement.value is None:
                    _fail("return_value", path, "a typed result is required")
                if self.role is None:
                    assert self.return_type is not None
                    result.append(ReturnValueStatement(self._expr(statement.value, values, expected=self.return_type)))
                else:
                    result.append(ReturnEffectStatement(self._effect(statement.value, values, path)))
            else:
                _fail("statement_forbidden", path, type(statement).__name__)
        return tuple(result), values

    def _static_range(self, node: ast.expr, path: str) -> int:
        if not isinstance(node, ast.Call) or _dotted_name(node.func) != "range" \
                or len(node.args) != 1 or node.keywords:
            _fail("static_range", path, "only range(CONSTANT) is admitted")
        value_node = node.args[0]
        if isinstance(value_node, ast.Constant) and isinstance(value_node.value, int) \
                and not isinstance(value_node.value, bool):
            value = value_node.value
        elif isinstance(value_node, ast.Name):
            constant = next((item for item in self.manifest.constants if item.name == value_node.id), None)
            if constant is None or constant.value_type not in {I32, U32} or not isinstance(constant.value, int):
                _fail("static_range_constant", path, value_node.id)
            value = constant.value
        else:
            _fail("static_range_constant", path, "literal or frozen integer required")
        if not 0 <= value <= self.manifest.resources.max_static_loop_trip_count:
            _fail("static_range_bound", path, str(value))
        return value

    def _effect(self, node: ast.expr, values: Mapping[str, CallbackType], path: str) -> CallbackEffect:
        if not isinstance(node, ast.Call):
            _fail("effect_call", path, "callback returns one optix effect constructor")
        name = _dotted_name(node.func)
        kind = _EFFECTS.get(name)
        if kind is None or node.args:
            _fail("effect_call", path, repr(name))
        supplied = {item.arg: item.value for item in node.keywords if item.arg is not None}
        if len(supplied) != len(node.keywords):
            _fail("effect_keywords", path, "duplicate or expanded keywords are rejected")
        expected: Mapping[str, CallbackType]
        payload = record_type(self.manifest.payload_record)
        output = record_type(self.manifest.output_record)
        if kind is EffectKind.AABB:
            expected = {"lower": VEC3F32, "upper": VEC3F32}
        elif kind is EffectKind.TRACE_REQUEST:
            expected = {"origin": VEC3F32, "direction": VEC3F32, "tmin": F32, "tmax": F32, "payload": payload}
        elif kind is EffectKind.HIT:
            expected = {"t": F32, "hit_kind": U32, "attributes": tuple_type(*self.manifest.attribute_types)}
        elif kind is EffectKind.NO_HIT:
            expected = {}
        elif kind in {EffectKind.ACCEPT_CONTINUE, EffectKind.IGNORE, EffectKind.TERMINATE, EffectKind.PAYLOAD}:
            expected = {"payload": payload}
        else:
            expected = {"value": output}
        if set(supplied) != set(expected):
            _fail("effect_fields", path, f"{kind.value} requires {tuple(expected)}")
        fields = tuple((key, self._expr(supplied[key], values, expected=value_type)) for key, value_type in expected.items())
        return CallbackEffect(kind, fields)

    def _expr(
        self,
        node: ast.expr,
        values: Mapping[str, CallbackType],
        *,
        expected: CallbackType | None = None,
    ) -> CallbackExpr:
        if isinstance(node, ast.Name):
            value_type = values.get(node.id)
            if value_type is None:
                _fail("undefined_name", f"function.{self.node.name}", node.id)
            result = _reference(node.id, value_type, constant=node.id in self.constant_types)
        elif isinstance(node, ast.Constant):
            value_type = expected or _literal_type(node.value)
            result = CallbackExpr("literal", value_type, attributes=(("value", node.value),))
        elif isinstance(node, ast.Attribute):
            base = self._expr(node.value, values)
            value_type = _field_type(base.value_type, node.attr, self.records)
            result = CallbackExpr("field", value_type, (base,), (("name", node.attr),))
        elif isinstance(node, ast.Subscript):
            base = self._expr(node.value, values)
            index = self._expr(node.slice, values)
            if base.value_type.kind is not TypeKind.READ_ONLY_VIEW:
                _fail("subscript_base", f"function.{self.node.name}", "only ReadOnlyView is subscriptable")
            result = CallbackExpr("view_load", base.value_type.items[0], (base, index))
        elif isinstance(node, ast.BinOp):
            opcode = _BINOPS.get(type(node.op))
            if opcode is None:
                _fail("binary_operator", f"function.{self.node.name}", type(node.op).__name__)
            left, right = self._binary_operands(node.left, node.right, values, expected)
            result = CallbackExpr(opcode, left.value_type, (left, right))
        elif isinstance(node, ast.UnaryOp):
            value = self._expr(node.operand, values, expected=expected)
            if isinstance(node.op, ast.Not): opcode, value_type = "not", BOOL
            elif isinstance(node.op, ast.USub): opcode, value_type = "neg", value.value_type
            elif isinstance(node.op, ast.UAdd): return value
            else: _fail("unary_operator", f"function.{self.node.name}", type(node.op).__name__)
            result = CallbackExpr(opcode, value_type, (value,))
        elif isinstance(node, ast.BoolOp):
            opcode = "and" if isinstance(node.op, ast.And) else "or" if isinstance(node.op, ast.Or) else None
            if opcode is None: _fail("bool_operator", f"function.{self.node.name}", type(node.op).__name__)
            result = CallbackExpr(opcode, BOOL, tuple(self._expr(item, values, expected=BOOL) for item in node.values))
        elif isinstance(node, ast.Compare) and len(node.ops) == 1 and len(node.comparators) == 1:
            opcode = _CMPOPS.get(type(node.ops[0]))
            if opcode is None: _fail("comparison_operator", f"function.{self.node.name}", type(node.ops[0]).__name__)
            left, right = self._binary_operands(node.left, node.comparators[0], values, None)
            result = CallbackExpr(opcode, BOOL, (left, right))
        elif isinstance(node, ast.IfExp):
            condition = self._expr(node.test, values, expected=BOOL)
            left = self._expr(node.body, values, expected=expected)
            right = self._expr(node.orelse, values, expected=left.value_type)
            result = CallbackExpr("select", left.value_type, (condition, left, right))
        elif isinstance(node, ast.Tuple):
            items = tuple(self._expr(item, values, expected=None) for item in node.elts)
            value_type = expected or tuple_type(*(item.value_type for item in items))
            names = tuple(str(index) for index in range(len(items)))
            result = CallbackExpr("construct", value_type, items, (("field_names", names),))
        elif isinstance(node, ast.Call):
            result = self._call(node, values, expected)
        else:
            _fail("expression_forbidden", f"function.{self.node.name}", type(node).__name__)
        if expected is not None and result.value_type != expected:
            _fail("expression_type", f"function.{self.node.name}", f"expected {expected.to_dict()}, got {result.value_type.to_dict()}")
        return result

    def _binary_operands(
        self, left_node: ast.expr, right_node: ast.expr,
        values: Mapping[str, CallbackType], expected: CallbackType | None,
    ) -> tuple[CallbackExpr, CallbackExpr]:
        if isinstance(left_node, ast.Constant) and not isinstance(right_node, ast.Constant):
            right = self._expr(right_node, values, expected=expected)
            left = self._expr(left_node, values, expected=right.value_type)
        else:
            left = self._expr(left_node, values, expected=expected)
            right = self._expr(right_node, values, expected=left.value_type)
        return left, right

    def _call(
        self, node: ast.Call, values: Mapping[str, CallbackType], expected: CallbackType | None,
    ) -> CallbackExpr:
        name = _dotted_name(node.func)
        if node.keywords:
            if name in self.records:
                record = self.records[name]
                supplied = {item.arg: item.value for item in node.keywords if item.arg is not None}
                if len(supplied) != len(node.keywords) or set(supplied) != {item.name for item in record.fields}:
                    _fail("record_constructor_fields", f"function.{self.node.name}", str(name))
                operands = tuple(self._expr(supplied[item.name], values, expected=item.value_type) for item in record.fields)
                return CallbackExpr("construct", record_type(name), operands, (("field_names", tuple(item.name for item in record.fields)),))
            _fail("call_keywords", f"function.{self.node.name}", str(name))
        if name in _SCALAR_TYPES:
            if len(node.args) != 1: _fail("cast_arity", f"function.{self.node.name}", str(name))
            operand = self._expr(node.args[0], values)
            # Explicit casts are represented as constructors only when they are
            # identity-safe in v1. Narrowing/float-int conversion remains rejected.
            if operand.value_type != _SCALAR_TYPES[name]:
                _fail("cast_not_lossless", f"function.{self.node.name}", str(name))
            return operand
        if name in _VECTOR_TYPES:
            value_type = _VECTOR_TYPES[name]
            if len(node.args) != value_type.lanes: _fail("vector_arity", f"function.{self.node.name}", str(name))
            element = scalar_type(value_type.scalar)
            operands = tuple(self._expr(item, values, expected=element) for item in node.args)
            return CallbackExpr("construct", value_type, operands, (("field_names", tuple(str(i) for i in range(len(operands)))),))
        intrinsic = {
            "optix.sqrt": "sqrt", "optix.abs": "abs", "optix.min": "min",
            "optix.max": "max", "optix.isfinite": "isfinite", "optix.dot": "dot",
        }.get(name)
        if intrinsic is not None:
            if node.keywords: _fail("intrinsic_keywords", f"function.{self.node.name}", str(name))
            operands = tuple(self._expr(item, values, expected=expected if len(node.args) == 1 else None) for item in node.args)
            if intrinsic == "isfinite": value_type = BOOL
            elif intrinsic == "dot":
                if not operands or operands[0].value_type.kind is not TypeKind.VECTOR:
                    _fail("dot_argument", f"function.{self.node.name}", "vector required")
                value_type = scalar_type(operands[0].value_type.scalar)
            else:
                if not operands: _fail("intrinsic_arity", f"function.{self.node.name}", str(name))
                value_type = operands[0].value_type
            return CallbackExpr(intrinsic, value_type, operands)
        signature = self.helpers.get(str(name))
        if signature is not None:
            argument_types, return_type = signature
            if len(node.args) != len(argument_types):
                _fail("helper_arity", f"function.{self.node.name}", str(name))
            operands = tuple(self._expr(item, values, expected=value_type) for item, value_type in zip(node.args, argument_types))
            return CallbackExpr("helper_call", return_type, operands, (("name", str(name)),))
        _fail("call_forbidden", f"function.{self.node.name}", repr(name))
        raise AssertionError


def _compile_record(
    node: ast.ClassDef, purpose: RecordPurpose, record_names: set[str],
) -> CallbackRecord:
    if node.bases or node.keywords or getattr(node, "type_params", ()):
        _fail("record_inheritance", f"record.{node.name}", "inheritance and generics are rejected")
    fields: list[CallbackField] = []
    for index, item in enumerate(node.body):
        if not isinstance(item, ast.AnnAssign) or not isinstance(item.target, ast.Name) \
                or item.value is not None or item.simple != 1:
            _fail("record_member", f"record.{node.name}[{index}]", "annotated fields only")
        fields.append(CallbackField(item.target.id, _parse_type(item.annotation, record_names)))
    return CallbackRecord(node.name, purpose, tuple(fields))


def _function_signature(
    node: ast.FunctionDef,
    records: Mapping[str, CallbackRecord],
    *,
    require_return: bool,
) -> tuple[tuple[CallbackArgument, ...], CallbackType | None]:
    args = node.args
    if args.posonlyargs or args.kwonlyargs or args.vararg or args.kwarg \
            or args.defaults or args.kw_defaults or getattr(node, "type_params", ()):
        _fail("function_signature", f"function.{node.name}", "defaults/variadics/generics are rejected")
    arguments = tuple(CallbackArgument(item.arg, _parse_type(item.annotation, set(records))) for item in args.args)
    if require_return and node.returns is None:
        _fail("return_annotation", f"function.{node.name}", "explicit return annotation required")
    return_type = None if node.returns is None else _parse_type(node.returns, set(records), allow_effect_names=True)
    return arguments, return_type


def _verify_program_decorator(
    node: ast.ClassDef,
    manifest: CallbackModuleManifest,
    records: Mapping[str, CallbackRecord],
) -> None:
    if node.bases or node.keywords or getattr(node, "type_params", ()):
        _fail("program_inheritance", f"program.{node.name}", "inheritance and generics are rejected")
    decorator = node.decorator_list[0]
    if not isinstance(decorator, ast.Call) or _dotted_name(decorator.func) != "optix.program" or decorator.args:
        _fail("program_decorator", f"program.{node.name}", "@optix.program uses named fields")
    values = {item.arg: item.value for item in decorator.keywords if item.arg is not None}
    if len(values) != len(decorator.keywords) or set(values) != {
        "payload", "output", "attributes", "max_trace_depth", "max_callable_depth",
    }:
        _fail("program_decorator_fields", f"program.{node.name}", "exact program fields required")
    if not isinstance(values["payload"], ast.Name) or values["payload"].id != manifest.payload_record:
        _fail("program_payload", f"program.{node.name}", manifest.payload_record)
    if not isinstance(values["output"], ast.Name) or values["output"].id != manifest.output_record:
        _fail("program_output", f"program.{node.name}", manifest.output_record)
    attributes_node = values["attributes"]
    if not isinstance(attributes_node, ast.Tuple):
        _fail("program_attributes", f"program.{node.name}", "tuple required")
    attribute_types = tuple(_parse_type(item, set(records)) for item in attributes_node.elts)
    if attribute_types != manifest.attribute_types:
        _fail("program_attributes", f"program.{node.name}", "manifest mismatch")
    for key, expected in {
        "max_trace_depth": manifest.resources.max_trace_depth,
        "max_callable_depth": manifest.resources.max_callable_depth,
    }.items():
        value = values[key]
        if not isinstance(value, ast.Constant) or value.value != expected:
            _fail("program_resource", f"program.{node.name}.{key}", str(expected))


def _verify_role_annotation(node: ast.AST | None, role: CallbackRole, manifest: CallbackModuleManifest) -> None:
    name = _annotation_text(node)
    expected = {
        CallbackRole.BOUNDS: "Aabb3f",
        CallbackRole.MAKE_RAY: "TraceRequest",
        CallbackRole.INTERSECTION: "IntersectionEffect",
        CallbackRole.ANY_HIT: "AnyHitEffect",
        CallbackRole.CLOSEST_HIT: manifest.payload_record,
        CallbackRole.MISS: manifest.payload_record,
        CallbackRole.FINALIZE: manifest.output_record,
    }[role]
    if name != expected:
        _fail("role_return_annotation", f"role.{role.value}", f"expected {expected}, got {name}")


def _parse_type(node: ast.AST | None, record_names: set[str], *, allow_effect_names: bool = False) -> CallbackType:
    if isinstance(node, ast.Name):
        if node.id in _SCALAR_TYPES: return _SCALAR_TYPES[node.id]
        if node.id in _VECTOR_TYPES: return _VECTOR_TYPES[node.id]
        if node.id in _BUILTIN_TYPES: return _BUILTIN_TYPES[node.id]
        if node.id in record_names: return record_type(node.id)
        if allow_effect_names and node.id in {"TraceRequest", "IntersectionEffect", "AnyHitEffect"}:
            return builtin_type(node.id)
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
            and node.value.id == "ReadOnlyView":
        return read_only_view(_parse_type(node.slice, record_names))
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
            and node.value.id == "tuple" and isinstance(node.slice, ast.Tuple):
        return tuple_type(*(_parse_type(item, record_names) for item in node.slice.elts))
    _fail("type_annotation", "annotation", ast.unparse(node) if node is not None else "None")
    raise AssertionError


def _field_type(base: CallbackType, name: str, records: Mapping[str, CallbackRecord]) -> CallbackType:
    if base.kind is TypeKind.RECORD:
        field = records[base.name or ""].field(name)
        if field is not None: return field.value_type
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
    if base in builtins and name in builtins[base]: return builtins[base][name]
    if base.kind is TypeKind.VECTOR and name in "xyzw" and "xyzw".index(name) < base.lanes:
        return scalar_type(base.scalar)
    _fail("field_access", "expression", f"{base.to_dict()}.{name}")
    raise AssertionError


def _literal_type(value: object) -> CallbackType:
    if isinstance(value, bool): return BOOL
    if isinstance(value, int) and not isinstance(value, bool): return I32
    if isinstance(value, float) and math.isfinite(value): return F32
    _fail("literal", "expression", repr(value))
    raise AssertionError


def _reference(name: str, value_type: CallbackType, *, constant: bool) -> CallbackExpr:
    return CallbackExpr("constant" if constant else "local", value_type, attributes=(("name", name),))


def _statements_definitely_return(statements: Sequence[CallbackStatement]) -> bool:
    for statement in statements:
        if isinstance(statement, (ReturnEffectStatement, ReturnValueStatement)):
            return True
        if isinstance(statement, IfStatement) and _statements_definitely_return(statement.then_body) \
                and _statements_definitely_return(statement.else_body):
            return True
    return False


def _single_decorator_name(decorators: Sequence[ast.expr], path: str) -> str | None:
    if len(decorators) != 1:
        _fail("decorator_cardinality", path, "exactly one decorator required")
    return _dotted_name(decorators[0])


def _is_program_decorator(decorators: Sequence[ast.expr]) -> bool:
    return len(decorators) == 1 and isinstance(decorators[0], ast.Call) \
        and _dotted_name(decorators[0].func) == "optix.program"


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name): return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted_name(node.value)
        return None if base is None else f"{base}.{node.attr}"
    return None


def _annotation_text(node: ast.AST | None) -> str:
    if node is None: return "None"
    if isinstance(node, ast.Name): return node.id
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name): return node.value.id
    return ast.unparse(node)


def _fail(code: str, path: str, message: str) -> None:
    raise CallbackVerificationError(code, path, message)
