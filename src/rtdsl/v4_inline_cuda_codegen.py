"""Fail-closed inline CUDA lowering for compiler-generated formal leaves.

This is deliberately not a Python-to-CUDA frontend.  It accepts only the
small deterministic Python AST emitted by ``v4_callback_numba_codegen`` after
Callback IR verification.  Unknown syntax is rejected; user source never
enters this lowering.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
from typing import Mapping, Sequence

from .v4_callback_numba_codegen import (
    FORMAL_NUMBA_SOURCE_SCHEMA,
    GeneratedFormalNumbaLeaf,
)


class InlineCudaCodegenError(ValueError):
    pass


_C_TYPES = {
    "bool": "unsigned char",
    "i32": "int",
    "u32": "unsigned int",
    "i64": "long long",
    "u64": "unsigned long long",
    "f32": "float",
    "f64": "double",
}


def _ctype(value: str) -> str:
    if value.startswith("ptr<") and value.endswith(">"):
        return _C_TYPES[value[4:-1]] + "*"
    if value.startswith("device_ptr<") and value.endswith(">"):
        return "const " + _C_TYPES[value[11:-1]] + "*"
    try:
        return _C_TYPES[value]
    except KeyError as exc:
        raise InlineCudaCodegenError(
            f"unsupported generated ABI type: {value!r}") from exc


@dataclass
class _State:
    scalar_names: set[str]
    tuples: dict[str, tuple[str, ...]]
    finite_names: set[str]
    tuple_finite: dict[str, tuple[bool, ...]]

    def fork(self) -> "_State":
        return _State(
            set(self.scalar_names), dict(self.tuples), set(self.finite_names),
            dict(self.tuple_finite))


class _Translator:
    def __init__(
        self,
        leaf: GeneratedFormalNumbaLeaf,
        *,
        trusted_finite_inputs: frozenset[str],
        proven_failure_guards: frozenset[tuple[int, int]],
    ) -> None:
        self.leaf = leaf
        self.trusted_finite_inputs = trusted_finite_inputs
        self.proven_failure_guards = proven_failure_guards
        self.elided_failure_guards: set[tuple[int, int]] = set()
        self.lines: list[str] = []

    def fail(self, node: ast.AST, message: str) -> None:
        raise InlineCudaCodegenError(
            f"{self.leaf.role}:{type(node).__name__}@"
            f"{getattr(node, 'lineno', 0)}: {message}")

    def emit(self, indent: int, text: str) -> None:
        self.lines.append("    " * indent + text)

    def expr(self, node: ast.AST, state: _State) -> str | tuple[str, ...]:
        if isinstance(node, ast.Name):
            if node.id in state.tuples:
                return state.tuples[node.id]
            return node.id
        if isinstance(node, ast.Constant):
            if node.value is True:
                return "true"
            if node.value is False:
                return "false"
            if node.value is None:
                self.fail(node, "None is not a device value")
            if isinstance(node.value, (int, float)):
                return repr(node.value)
            self.fail(node, "only numeric and boolean literals are admitted")
        if isinstance(node, ast.Tuple):
            values = tuple(self.scalar(item, state) for item in node.elts)
            return values
        if isinstance(node, ast.Subscript):
            base = self.expr(node.value, state)
            index = self.scalar(node.slice, state)
            if isinstance(base, tuple):
                if not isinstance(node.slice, ast.Constant) \
                        or not isinstance(node.slice.value, int):
                    self.fail(node, "generated tuple index must be constant")
                try:
                    return base[node.slice.value]
                except IndexError:
                    self.fail(node, "generated tuple index is outside arity")
            return f"{base}[{index}]"
        if isinstance(node, ast.BinOp):
            operators = {
                ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
                ast.BitAnd: "&", ast.BitOr: "|", ast.BitXor: "^",
                ast.LShift: "<<", ast.RShift: ">>",
            }
            operator = operators.get(type(node.op))
            if operator is None:
                self.fail(node, "unsupported generated binary operator")
            return (
                f"({self.scalar(node.left, state)} {operator} "
                f"{self.scalar(node.right, state)})")
        if isinstance(node, ast.UnaryOp):
            operators = {ast.Not: "!", ast.USub: "-", ast.UAdd: "+", ast.Invert: "~"}
            operator = operators.get(type(node.op))
            if operator is None:
                self.fail(node, "unsupported generated unary operator")
            return f"({operator}{self.scalar(node.operand, state)})"
        if isinstance(node, ast.BoolOp):
            operator = " && " if isinstance(node.op, ast.And) else " || " \
                if isinstance(node.op, ast.Or) else None
            if operator is None:
                self.fail(node, "unsupported generated boolean operator")
            return "(" + operator.join(
                self.scalar(item, state) for item in node.values) + ")"
        if isinstance(node, ast.Compare):
            operators = {
                ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=",
                ast.Gt: ">", ast.GtE: ">=",
            }
            pieces = []
            left = node.left
            for operation, right in zip(node.ops, node.comparators):
                operator = operators.get(type(operation))
                if operator is None:
                    self.fail(node, "unsupported generated comparison")
                pieces.append(
                    f"({self.scalar(left, state)} {operator} "
                    f"{self.scalar(right, state)})")
                left = right
            return "(" + " && ".join(pieces) + ")"
        if isinstance(node, ast.IfExp):
            return (
                f"({self.scalar(node.test, state)} ? "
                f"{self.scalar(node.body, state)} : "
                f"{self.scalar(node.orelse, state)})")
        if isinstance(node, ast.Call):
            arguments = [self.scalar(item, state) for item in node.args]
            if node.keywords:
                self.fail(node, "keyword arguments are not admitted")
            if isinstance(node.func, ast.Attribute) \
                    and isinstance(node.func.value, ast.Name) \
                    and node.func.value.id == "math" \
                    and node.func.attr == "isfinite" \
                    and len(arguments) == 1:
                return f"isfinite({arguments[0]})"
            if isinstance(node.func, ast.Name) and node.func.id == "_f32" \
                    and len(arguments) == 1:
                return f"((float)({arguments[0]}))"
            if isinstance(node.func, ast.Name) and node.func.id == "abs" \
                    and len(arguments) == 1:
                return f"fabs({arguments[0]})"
            self.fail(node, "unsupported generated call")
        self.fail(node, "unsupported generated expression")
        raise AssertionError

    def scalar(self, node: ast.AST, state: _State) -> str:
        value = self.expr(node, state)
        if isinstance(value, tuple):
            self.fail(node, "tuple used where scalar is required")
        return value

    def statements(
        self, nodes: Sequence[ast.stmt], state: _State, indent: int,
    ) -> None:
        for node in nodes:
            if isinstance(node, ast.Assign):
                if len(node.targets) != 1:
                    self.fail(node, "multiple assignment targets are not admitted")
                target = node.targets[0]
                value_is_finite = self._expr_proven_finite(node.value, state)
                value = self.expr(node.value, state)
                if isinstance(target, ast.Name):
                    if isinstance(value, tuple):
                        state.tuples[target.id] = value
                        if isinstance(value_is_finite, tuple):
                            state.tuple_finite[target.id] = value_is_finite
                        else:
                            state.tuple_finite[target.id] = tuple(
                                False for _ in value)
                        state.scalar_names.discard(target.id)
                        state.finite_names.discard(target.id)
                    else:
                        state.tuples.pop(target.id, None)
                        state.tuple_finite.pop(target.id, None)
                        declaration = target.id not in state.scalar_names
                        state.scalar_names.add(target.id)
                        if value_is_finite is True:
                            state.finite_names.add(target.id)
                        else:
                            state.finite_names.discard(target.id)
                        self.emit(
                            indent,
                            ("auto " if declaration else "") +
                            f"{target.id} = {value};")
                    continue
                if isinstance(target, ast.Subscript):
                    if isinstance(value, tuple):
                        self.fail(node, "cannot store tuple through ABI pointer")
                    destination = self.scalar(target, state)
                    self.emit(indent, f"{destination} = {value};")
                    continue
                self.fail(node, "unsupported generated assignment target")
            elif isinstance(node, ast.If):
                failure_guard = self._generated_failure_guard(node)
                if failure_guard in self.proven_failure_guards:
                    self.elided_failure_guards.add(failure_guard)
                    continue
                finite_value = self._finite_guard_value(node)
                if finite_value is not None \
                        and self._expr_proven_finite(finite_value, state) is True:
                    continue
                condition = self.scalar(node.test, state)
                self.emit(indent, f"if ({condition}) {{")
                self.statements(node.body, state.fork(), indent + 1)
                if node.orelse:
                    self.emit(indent, "} else {")
                    self.statements(node.orelse, state.fork(), indent + 1)
                self.emit(indent, "}")
                if finite_value is not None \
                        and not node.orelse \
                        and node.body \
                        and isinstance(node.body[-1], ast.Return):
                    self._mark_finite(finite_value, state)
            elif isinstance(node, ast.Return):
                if node.value is not None:
                    self.fail(node, "formal role must return None")
                self.emit(indent, "return 0ull;")
            elif isinstance(node, ast.Pass):
                continue
            else:
                self.fail(node, "unsupported generated statement")

    @staticmethod
    def _generated_failure_guard(node: ast.If) -> tuple[int, int] | None:
        """Return the exact error-code/site of an emitter failure block."""

        if node.orelse or not node.body \
                or not isinstance(node.body[-1], ast.Return):
            return None
        assigned: dict[str, int] = {}
        for statement in node.body[:-1]:
            if not isinstance(statement, ast.Assign) \
                    or len(statement.targets) != 1 \
                    or not isinstance(statement.targets[0], ast.Subscript) \
                    or not isinstance(statement.targets[0].value, ast.Name):
                return None
            name = statement.targets[0].value.id
            if name not in {"status_ok", "status_error_code", "status_error_site"}:
                return None
            if not isinstance(statement.value, ast.Constant) \
                    or not isinstance(statement.value.value, int):
                return None
            assigned[name] = statement.value.value
        if set(assigned) != {
                "status_ok", "status_error_code", "status_error_site"} \
                or assigned["status_ok"] != 0 \
                or assigned["status_error_code"] == 0 \
                or assigned["status_error_site"] <= 0:
            return None
        return assigned["status_error_code"], assigned["status_error_site"]

    def _finite_guard_value(self, node: ast.If) -> ast.AST | None:
        """Recognize only ``if not math.isfinite(exact_input): fail``.

        This does not infer arithmetic closure.  Computed values retain their
        device checks; only inputs named by an explicit caller proof may be
        discharged.
        """

        if node.orelse or not isinstance(node.test, ast.UnaryOp) \
                or not isinstance(node.test.op, ast.Not) \
                or not isinstance(node.test.operand, ast.Call):
            return None
        call = node.test.operand
        if len(call.args) != 1 or call.keywords \
                or not isinstance(call.func, ast.Attribute) \
                or not isinstance(call.func.value, ast.Name) \
                or call.func.value.id != "math" \
                or call.func.attr != "isfinite":
            return None
        return call.args[0]

    def _expr_proven_finite(
        self, node: ast.AST, state: _State,
    ) -> bool | tuple[bool, ...]:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return True
        if isinstance(node, ast.Name):
            if node.id in state.tuple_finite:
                return state.tuple_finite[node.id]
            return node.id in state.finite_names \
                or node.id in self.trusted_finite_inputs
        if isinstance(node, ast.Tuple):
            return tuple(
                self._expr_proven_finite(item, state) is True
                for item in node.elts)
        if isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name):
                if node.value.id in self.trusted_finite_inputs:
                    return True
                finite = state.tuple_finite.get(node.value.id)
                if finite is not None and isinstance(node.slice, ast.Constant) \
                        and isinstance(node.slice.value, int):
                    try:
                        return finite[node.slice.value]
                    except IndexError:
                        return False
            return False
        if isinstance(node, ast.UnaryOp) \
                and isinstance(node.op, (ast.USub, ast.UAdd)):
            return self._expr_proven_finite(node.operand, state) is True
        if isinstance(node, ast.IfExp):
            return self._expr_proven_finite(node.body, state) is True \
                and self._expr_proven_finite(node.orelse, state) is True
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "_f32" and len(node.args) == 1:
            # A cast preserves an already finite value, but arithmetic inside
            # the cast is not assumed closed under float32.
            return self._expr_proven_finite(node.args[0], state) is True
        return False

    def _mark_finite(self, node: ast.AST, state: _State) -> None:
        if isinstance(node, ast.Name):
            state.finite_names.add(node.id)
        elif isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
                and isinstance(node.slice, ast.Constant) \
                and isinstance(node.slice.value, int):
            existing = list(state.tuple_finite.get(node.value.id, ()))
            if existing and -len(existing) <= node.slice.value < len(existing):
                existing[node.slice.value] = True
                state.tuple_finite[node.value.id] = tuple(existing)

    def translate(self) -> str:
        if self.leaf.schema != FORMAL_NUMBA_SOURCE_SCHEMA:
            raise InlineCudaCodegenError(
                f"{self.leaf.role}: non-formal leaf schema")
        if hashlib.sha256(self.leaf.generated_source.encode("utf-8")).hexdigest() \
                != self.leaf.generated_source_sha256:
            raise InlineCudaCodegenError(
                f"{self.leaf.role}: generated source digest mismatch")
        tree = ast.parse(self.leaf.generated_source, mode="exec")
        functions = [item for item in tree.body if isinstance(item, ast.FunctionDef)]
        if len(functions) != 1 or len(tree.body) != 1:
            raise InlineCudaCodegenError(
                f"{self.leaf.role}: helpers or non-function statements are unsupported")
        function = functions[0]
        if function.name != self.leaf.abi_name \
                or function.decorator_list or function.returns is not None:
            raise InlineCudaCodegenError(
                f"{self.leaf.role}: generated function identity is invalid")
        arguments = [item.arg for item in function.args.args]
        if function.args.vararg or function.args.kwarg \
                or function.args.kwonlyargs or function.args.defaults \
                or len(arguments) != len(self.leaf.parameter_types):
            raise InlineCudaCodegenError(
                f"{self.leaf.role}: generated signature is outside closed ABI")
        parameters = ", ".join(
            f"{_ctype(value_type)} {name}"
            for name, value_type in zip(arguments, self.leaf.parameter_types)
        )
        self.emit(
            0,
            f'extern "C" __forceinline__ __device__ unsigned long long '
            f"{function.name}({parameters}) {{")
        state = _State(
            set(arguments), {}, set(self.trusted_finite_inputs), {})
        self.statements(function.body, state, 1)
        if self.elided_failure_guards != set(self.proven_failure_guards):
            missing = sorted(
                set(self.proven_failure_guards) - self.elided_failure_guards)
            raise InlineCudaCodegenError(
                f"{self.leaf.role}: staged failure-guard proof drift: "
                f"missing {missing!r}")
        self.emit(1, "return 0ull;")
        self.emit(0, "}")
        return "\n".join(self.lines) + "\n"


def lower_formal_leaves_to_inline_cuda(
    leaves: Sequence[GeneratedFormalNumbaLeaf],
    *,
    trusted_finite_inputs_by_role: Mapping[str, frozenset[str]] | None = None,
    proven_failure_guards_by_role: Mapping[
        str, frozenset[tuple[int, int]]
    ] | None = None,
) -> tuple[str, tuple[tuple[str, str], ...]]:
    if not leaves:
        raise InlineCudaCodegenError("at least one formal leaf is required")
    roles: set[str] = set()
    definitions: list[str] = []
    identities: list[tuple[str, str]] = []
    trusted = {} if trusted_finite_inputs_by_role is None \
        else dict(trusted_finite_inputs_by_role)
    unknown_roles = set(trusted) - {leaf.role for leaf in leaves}
    if unknown_roles:
        raise InlineCudaCodegenError(
            f"trusted-finite proof names unknown roles: {sorted(unknown_roles)!r}")
    guard_proofs = {} if proven_failure_guards_by_role is None \
        else dict(proven_failure_guards_by_role)
    unknown_guard_roles = set(guard_proofs) - {
        leaf.role for leaf in leaves}
    if unknown_guard_roles:
        raise InlineCudaCodegenError(
            f"failure-guard proof names unknown roles: "
            f"{sorted(unknown_guard_roles)!r}")
    for leaf in leaves:
        if leaf.role in roles:
            raise InlineCudaCodegenError(f"duplicate formal role: {leaf.role}")
        roles.add(leaf.role)
        definition = _Translator(
            leaf,
            trusted_finite_inputs=frozenset(trusted.get(leaf.role, ())),
            proven_failure_guards=frozenset(guard_proofs.get(leaf.role, ())),
        ).translate()
        definitions.append(definition)
        identities.append((
            leaf.role, hashlib.sha256(definition.encode("utf-8")).hexdigest()))
    return "\n".join(definitions), tuple(identities)


__all__ = [
    "InlineCudaCodegenError",
    "lower_formal_leaves_to_inline_cuda",
]
