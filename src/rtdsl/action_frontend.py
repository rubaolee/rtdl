from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect
import textwrap
from typing import Callable, NoReturn

from .action_ir import (
    BOOL,
    F32,
    F64,
    I32,
    I64,
    U32,
    U64,
    ActionBlock,
    ActionBuilder,
    ActionEmitSpec,
    ActionOp,
    ActionRecordType,
    ActionReductionSpec,
    ActionScalarLiteral,
    ActionScalarType,
    ActionSpec,
    ActionStateSpec,
    TerminationProofSpec,
    ActionValue,
    LogicalEventContract,
    NumericContract,
    action_attributes,
    verify_action_spec,
)


@dataclass(frozen=True)
class RestrictedActionFrontendContract:
    """Compiler-owned context for the deliberately small research frontend."""

    event_type: ActionRecordType
    parameter_type: ActionRecordType
    logical_event: LogicalEventContract
    states: tuple[ActionStateSpec, ...] = ()
    reductions: tuple[ActionReductionSpec, ...] = ()
    emits: tuple[ActionEmitSpec, ...] = ()
    termination_proofs: tuple[TerminationProofSpec, ...] = ()
    numeric_contract: NumericContract = NumericContract()


@dataclass(frozen=True)
class ActionFrontendIssue:
    code: str
    path: str
    message: str


class ActionFrontendError(ValueError):
    def __init__(self, issue: ActionFrontendIssue) -> None:
        self.issue = issue
        super().__init__(
            f"Restricted Action frontend failed: {issue.code}@{issue.path}: {issue.message}"
        )


_SCALAR_CONSTRUCTORS = {
    "bool": BOOL,
    "i32": I32,
    "i64": I64,
    "u32": U32,
    "u64": U64,
    "f32": F32,
    "f64": F64,
}

_COMPARE_PREDICATES = {
    ast.Eq: "eq",
    ast.NotEq: "ne",
    ast.Lt: "lt",
    ast.LtE: "le",
    ast.Gt: "gt",
    ast.GtE: "ge",
}

_BINARY_OPCODES = {ast.Add: "add", ast.Sub: "sub", ast.Mult: "mul"}


def compile_restricted_action_source(
    source: str,
    contract: RestrictedActionFrontendContract,
) -> ActionSpec:
    """Compile a closed Python AST subset into verified Action IR v1."""

    if not isinstance(source, str) or not source.strip():
        _fail("empty_source", "module", "source must contain one action function")
    try:
        module = ast.parse(textwrap.dedent(source), mode="exec")
    except SyntaxError as exc:
        _fail("syntax_error", "module", str(exc))
    functions = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    if len(module.body) != 1 or len(functions) != 1:
        _fail(
            "one_function_required",
            "module",
            "the frontend admits exactly one top-level function and no imports or globals",
        )
    compiler = _RestrictedActionCompiler(functions[0], contract)
    spec = compiler.compile()
    verify_action_spec(spec)
    return spec


def compile_restricted_action_function(
    function: Callable[..., object],
    contract: RestrictedActionFrontendContract,
) -> ActionSpec:
    """Compile source for a normal Python function without executing it."""

    if not inspect.isfunction(function):
        _fail("python_function_required", "function", "expected a Python function object")
    try:
        source = inspect.getsource(function)
    except (OSError, TypeError) as exc:
        _fail("function_source_unavailable", "function", str(exc))
    return compile_restricted_action_source(source, contract)


class _RestrictedActionCompiler:
    def __init__(
        self,
        function: ast.FunctionDef,
        contract: RestrictedActionFrontendContract,
    ) -> None:
        self.function = function
        self.contract = contract
        self.operations: list[ActionOp] = []
        self.values: dict[str, tuple[str, ActionScalarType]] = {}
        self.temporary_index = 0

    def compile(self) -> ActionSpec:
        self._verify_function_shape()
        for index, statement in enumerate(self.function.body):
            self._compile_statement(statement, f"function.body[{index}]")
        builder = ActionBuilder(
            name=self.function.name,
            event_type=self.contract.event_type,
            parameter_type=self.contract.parameter_type,
            logical_event=self.contract.logical_event,
            numeric_contract=self.contract.numeric_contract,
        )
        for state in self.contract.states:
            builder.add_state(state)
        for reduction in self.contract.reductions:
            builder.add_reduction(reduction)
        for emit in self.contract.emits:
            builder.add_emit(emit)
        for proof in self.contract.termination_proofs:
            builder.add_termination_proof(proof)
        builder.add_block(ActionBlock("entry", tuple(self.operations)))
        return builder.build()

    def _verify_function_shape(self) -> None:
        arguments = self.function.args
        if (
            len(arguments.args) != 2
            or [item.arg for item in arguments.args] != ["event", "params"]
            or arguments.posonlyargs
            or arguments.kwonlyargs
            or arguments.vararg is not None
            or arguments.kwarg is not None
            or arguments.defaults
            or arguments.kw_defaults
        ):
            _fail(
                "invalid_action_signature",
                "function.args",
                "the only admitted signature is action(event, params)",
            )
        if self.function.decorator_list:
            _fail("decorator_forbidden", "function.decorator_list", "decorators are not admitted")
        if getattr(self.function, "type_params", ()):
            _fail("type_parameter_forbidden", "function.type_params", "type parameters are not admitted")
        if self.function.returns is not None or any(
            argument.annotation is not None for argument in arguments.args
        ):
            _fail("annotation_forbidden", "function.args", "Python annotations are not part of Action semantics")

    def _compile_statement(self, statement: ast.stmt, path: str) -> None:
        if isinstance(statement, ast.Assign):
            if len(statement.targets) != 1 or not isinstance(statement.targets[0], ast.Name):
                _fail("simple_ssa_assignment_required", path, "assignment target must be one name")
            target = statement.targets[0].id
            if target in self.values or target in {"event", "params"}:
                _fail("ssa_reassignment_forbidden", path, f"{target!r} is already defined")
            value_name, value_type = self._compile_expression(statement.value, path, target)
            self.values[target] = (value_name, value_type)
            return
        if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
            self._compile_effect_call(statement.value, path)
            return
        if isinstance(statement, ast.Return) and (
            statement.value is None
            or isinstance(statement.value, ast.Constant) and statement.value.value is None
        ):
            return
        if isinstance(statement, ast.Pass):
            return
        _fail(
            "statement_forbidden",
            path,
            f"{type(statement).__name__} is outside the restricted Action frontend",
        )

    def _compile_effect_call(self, call: ast.Call, path: str) -> None:
        name = self._plain_call_name(call, path)
        if call.keywords:
            _fail("keyword_arguments_forbidden", path, "effect calls use positional arguments only")
        if name == "require":
            if len(call.args) != 1:
                _fail("require_arity", path, "require expects one bool expression")
            value_name, value_type = self._compile_expression(call.args[0], path)
            if value_type != BOOL:
                _fail("require_bool_required", path, "require condition must be bool")
            self.operations.append(ActionOp("filter", inputs=(value_name,)))
            return
        if name == "emit":
            effect_name, arguments = self._named_effect_arguments(call, path)
            spec = next((item for item in self.contract.emits if item.name == effect_name), None)
            if spec is None:
                _fail("unknown_emit", path, effect_name)
            if len(arguments) != len(spec.record_type.fields):
                _fail("emit_arity", path, f"emit {effect_name!r} field count mismatch")
            inputs: list[str] = []
            for index, (argument, field) in enumerate(zip(arguments, spec.record_type.fields)):
                value_name, value_type = self._compile_expression(argument, f"{path}.args[{index + 1}]")
                if value_type != field.value_type:
                    _fail("emit_type_mismatch", path, field.name)
                inputs.append(value_name)
            self.operations.append(
                ActionOp("emit", inputs=tuple(inputs), attributes=action_attributes(emit=effect_name))
            )
            return
        if name == "reduce":
            effect_name, arguments = self._named_effect_arguments(call, path)
            spec = next(
                (item for item in self.contract.reductions if item.name == effect_name), None
            )
            if spec is None:
                _fail("unknown_reduction", path, effect_name)
            expected = 0 if spec.operator.value == "count" else 1
            if len(arguments) != expected:
                _fail("reduction_arity", path, f"reduction {effect_name!r} expects {expected} values")
            inputs: tuple[str, ...] = ()
            if arguments:
                value_name, value_type = self._compile_expression(arguments[0], f"{path}.args[1]")
                if value_type != spec.value_type:
                    _fail("reduction_type_mismatch", path, effect_name)
                inputs = (value_name,)
            self.operations.append(
                ActionOp("reduce", inputs=inputs, attributes=action_attributes(reduction=effect_name))
            )
            return
        if name == "write_state":
            state_name, arguments = self._named_effect_arguments(call, path)
            state = next((item for item in self.contract.states if item.name == state_name), None)
            if state is None:
                _fail("unknown_state", path, state_name)
            if len(arguments) != 1:
                _fail("state_write_arity", path, "write_state expects one state value")
            value_name, value_type = self._compile_expression(arguments[0], f"{path}.args[1]")
            if value_type != state.value_type:
                _fail("state_write_type_mismatch", path, state_name)
            self.operations.append(
                ActionOp(
                    "state_write",
                    inputs=(value_name,),
                    attributes=action_attributes(state=state_name),
                )
            )
            return
        if name == "terminate":
            proof_name, arguments = self._named_effect_arguments(call, path)
            if arguments:
                _fail("terminate_arity", path, "terminate expects only a proof name")
            if not any(item.name == proof_name for item in self.contract.termination_proofs):
                _fail("unknown_termination_proof", path, proof_name)
            self.operations.append(
                ActionOp("terminate", attributes=action_attributes(proof=proof_name))
            )
            return
        if name in {"accept", "ignore"}:
            if call.args:
                _fail("control_arity", path, f"{name} expects no arguments")
            self.operations.append(ActionOp(name))
            return
        _fail("effect_call_forbidden", path, f"call to {name!r} is not admitted")

    def _compile_expression(
        self,
        expression: ast.expr,
        path: str,
        requested_output: str | None = None,
    ) -> tuple[str, ActionScalarType]:
        output = requested_output or self._temporary()
        if isinstance(expression, ast.Attribute):
            if not isinstance(expression.value, ast.Name) or expression.value.id not in {"event", "params"}:
                _fail("attribute_access_forbidden", path, "only event.field and params.field are admitted")
            record = (
                self.contract.event_type
                if expression.value.id == "event"
                else self.contract.parameter_type
            )
            field = record.field(expression.attr)
            if field is None or not isinstance(field.value_type, ActionScalarType):
                _fail("unknown_scalar_field", path, expression.attr)
            opcode = "load_event" if expression.value.id == "event" else "load_param"
            self.operations.append(
                ActionOp(
                    opcode,
                    outputs=(ActionValue(output, field.value_type),),
                    attributes=action_attributes(field=expression.attr),
                )
            )
            return output, field.value_type
        if isinstance(expression, ast.Name):
            value = self.values.get(expression.id)
            if value is None:
                _fail("unknown_ssa_name", path, expression.id)
            if requested_output is not None and requested_output != value[0]:
                _fail("alias_assignment_forbidden", path, "SSA aliases must be used directly")
            return value
        if isinstance(expression, ast.Compare):
            if len(expression.ops) != 1 or len(expression.comparators) != 1:
                _fail("chained_compare_forbidden", path, "comparisons must be binary")
            left_name, left_type = self._compile_expression(expression.left, path)
            right_name, right_type = self._compile_expression(expression.comparators[0], path)
            if left_type != right_type:
                _fail("compare_type_mismatch", path, "comparison operands must share a type")
            predicate = _COMPARE_PREDICATES.get(type(expression.ops[0]))
            if predicate is None:
                _fail("compare_operator_forbidden", path, type(expression.ops[0]).__name__)
            self.operations.append(
                ActionOp(
                    "compare",
                    inputs=(left_name, right_name),
                    outputs=(ActionValue(output, BOOL),),
                    attributes=action_attributes(predicate=predicate),
                )
            )
            return output, BOOL
        if isinstance(expression, ast.BoolOp):
            if len(expression.values) < 2:
                _fail("boolean_arity", path, "boolean expression needs two operands")
            opcode = "bool_and" if isinstance(expression.op, ast.And) else "bool_or"
            if not isinstance(expression.op, (ast.And, ast.Or)):
                _fail("boolean_operator_forbidden", path, type(expression.op).__name__)
            current_name, current_type = self._compile_expression(expression.values[0], path)
            if current_type != BOOL:
                _fail("boolean_type_mismatch", path, "boolean operands must be bool")
            for index, item in enumerate(expression.values[1:]):
                right_name, right_type = self._compile_expression(item, path)
                if right_type != BOOL:
                    _fail("boolean_type_mismatch", path, "boolean operands must be bool")
                result_name = output if index == len(expression.values) - 2 else self._temporary()
                self.operations.append(
                    ActionOp(
                        opcode,
                        inputs=(current_name, right_name),
                        outputs=(ActionValue(result_name, BOOL),),
                    )
                )
                current_name = result_name
            return current_name, BOOL
        if isinstance(expression, ast.UnaryOp) and isinstance(expression.op, ast.Not):
            value_name, value_type = self._compile_expression(expression.operand, path)
            if value_type != BOOL:
                _fail("boolean_type_mismatch", path, "not operand must be bool")
            self.operations.append(
                ActionOp("bool_not", inputs=(value_name,), outputs=(ActionValue(output, BOOL),))
            )
            return output, BOOL
        if isinstance(expression, ast.BinOp):
            opcode = _BINARY_OPCODES.get(type(expression.op))
            if opcode is None:
                _fail("arithmetic_operator_forbidden", path, type(expression.op).__name__)
            return self._binary_expression(opcode, expression.left, expression.right, path, output)
        if isinstance(expression, ast.Call):
            name = self._plain_call_name(expression, path)
            if expression.keywords:
                _fail("keyword_arguments_forbidden", path, "expression calls use positional arguments only")
            if name in {"min", "max"}:
                if len(expression.args) != 2:
                    _fail("arithmetic_arity", path, f"{name} expects two arguments")
                return self._binary_expression(name, expression.args[0], expression.args[1], path, output)
            if name == "select":
                if len(expression.args) != 3:
                    _fail("select_arity", path, "select expects condition, true value, false value")
                condition_name, condition_type = self._compile_expression(expression.args[0], path)
                true_name, true_type = self._compile_expression(expression.args[1], path)
                false_name, false_type = self._compile_expression(expression.args[2], path)
                if condition_type != BOOL or true_type != false_type:
                    _fail("select_type_mismatch", path, "select types do not match")
                self.operations.append(
                    ActionOp(
                        "select",
                        inputs=(condition_name, true_name, false_name),
                        outputs=(ActionValue(output, true_type),),
                    )
                )
                return output, true_type
            if name == "read_state":
                state_name, arguments = self._named_effect_arguments(expression, path)
                if arguments:
                    _fail("state_read_arity", path, "read_state expects only a state name")
                state = next(
                    (item for item in self.contract.states if item.name == state_name),
                    None,
                )
                if state is None:
                    _fail("unknown_state", path, state_name)
                if not isinstance(state.value_type, ActionScalarType):
                    _fail("state_scalar_required", path, state_name)
                self.operations.append(
                    ActionOp(
                        "state_read",
                        outputs=(ActionValue(output, state.value_type),),
                        attributes=action_attributes(state=state_name),
                    )
                )
                return output, state.value_type
            scalar_type = _SCALAR_CONSTRUCTORS.get(name)
            if scalar_type is not None:
                if len(expression.args) != 1:
                    _fail("scalar_constructor_arity", path, f"{name} expects one argument")
                argument = expression.args[0]
                if isinstance(argument, ast.Constant):
                    try:
                        literal = ActionScalarLiteral.from_python(scalar_type, argument.value)
                    except (TypeError, ValueError, OverflowError) as exc:
                        _fail("invalid_typed_literal", path, str(exc))
                    self.operations.append(
                        ActionOp(
                            "const",
                            outputs=(ActionValue(output, scalar_type),),
                            attributes=action_attributes(literal=literal),
                        )
                    )
                    return output, scalar_type
                value_name, value_type = self._compile_expression(argument, path)
                self.operations.append(
                    ActionOp("cast", inputs=(value_name,), outputs=(ActionValue(output, scalar_type),))
                )
                return output, scalar_type
            _fail("expression_call_forbidden", path, f"call to {name!r} is not admitted")
        if isinstance(expression, ast.Constant):
            _fail(
                "untyped_literal_forbidden",
                path,
                "scalar literals require an explicit bool/i32/i64/u32/u64/f32/f64 constructor",
            )
        _fail("expression_forbidden", path, type(expression).__name__)

    def _binary_expression(
        self,
        opcode: str,
        left: ast.expr,
        right: ast.expr,
        path: str,
        output: str,
    ) -> tuple[str, ActionScalarType]:
        left_name, left_type = self._compile_expression(left, path)
        right_name, right_type = self._compile_expression(right, path)
        if left_type != right_type or not left_type.is_numeric:
            _fail("arithmetic_type_mismatch", path, "arithmetic operands must share a numeric type")
        self.operations.append(
            ActionOp(
                opcode,
                inputs=(left_name, right_name),
                outputs=(ActionValue(output, left_type),),
            )
        )
        return output, left_type

    def _named_effect_arguments(
        self, call: ast.Call, path: str
    ) -> tuple[str, tuple[ast.expr, ...]]:
        if not call.args or not isinstance(call.args[0], ast.Constant) or not isinstance(
            call.args[0].value, str
        ):
            _fail("effect_name_literal_required", path, "effect name must be a string literal")
        return call.args[0].value, tuple(call.args[1:])

    @staticmethod
    def _plain_call_name(call: ast.Call, path: str) -> str:
        if not isinstance(call.func, ast.Name):
            _fail("dynamic_call_forbidden", path, "only closed, unqualified builtin names are admitted")
        return call.func.id

    def _temporary(self) -> str:
        name = f"__tmp{self.temporary_index}"
        self.temporary_index += 1
        return name


def _fail(code: str, path: str, message: str) -> NoReturn:
    raise ActionFrontendError(ActionFrontendIssue(code, path, message))
