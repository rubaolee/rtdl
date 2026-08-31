"""Closed, deterministic PTX composer for verified V4 callback leaves.

This is deliberately not a PTX linker or public PTX input API.  It implements
the reviewed Goal5749 single-module construction for an arbitrary finite set
of already-audited compiler-generated leaves.  Unknown grammar or identity
drift fails closed.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Mapping, Sequence

from .v4_callback_poc import DeviceFunctionArtifact


class CallbackPtxCompositionError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"V4 PTX composition failed: {code}: {detail}")


@dataclass(frozen=True)
class ComposedCallbackPtx:
    ptx: str
    ptx_sha256: str
    ptx_version: str
    ptx_target: str
    address_size: str
    wrapper_ptx_sha256: str
    leaf_bindings: tuple[tuple[str, str], ...]
    stripped_wrapper_externs: tuple[str, ...]
    stripped_numba_environments: tuple[str, ...]


_DIRECTIVE = re.compile(r"^\s*(\.(?:version|target|address_size))\s+(.+?)\s*$")
_EXTERN_START = re.compile(r"^\s*\.extern\s+\.func(?:\s+\([^)]*\))?\s*(.*)$")
_COMMON_ENV = re.compile(
    r"^\s*\.common\s+\.global\b.*\b"
    r"([A-Za-z_.$][A-Za-z0-9_.$]*NumbaEnv[A-Za-z0-9_.$]*)"
    r"(?:\[[^\]]+\])?\s*;\s*$"
)
_DEFINITION = re.compile(r"^\s*(?:\.visible\s+)?\.func(?:\s+\([^)]*\))?\s+([^\s(;]+)")


def _fail(code: str, detail: str) -> None:
    raise CallbackPtxCompositionError(code, detail)


def _directives(ptx: str, label: str) -> tuple[str, str, str]:
    found: dict[str, str] = {}
    for line in ptx.splitlines():
        match = _DIRECTIVE.match(line)
        if match:
            key, value = match.groups()
            if key in found:
                _fail("duplicate_directive", f"{label}:{key}")
            found[key] = value
    expected = {".version", ".target", ".address_size"}
    if set(found) != expected:
        _fail("directive_set", f"{label}:{sorted(set(found) ^ expected)}")
    return found[".version"], found[".target"], found[".address_size"]


def _strip_wrapper_externs(
    wrapper_ptx: str, symbols: Sequence[str]
) -> tuple[str, tuple[str, ...]]:
    lines = wrapper_ptx.splitlines(keepends=True)
    output: list[str] = []
    matched: dict[str, int] = {symbol: 0 for symbol in symbols}
    removed: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not _EXTERN_START.match(line):
            output.append(line)
            index += 1
            continue
        block = [line]
        index += 1
        while index < len(lines):
            block.append(lines[index])
            terminal = lines[index].strip() == ";" or lines[index].rstrip().endswith(";")
            index += 1
            if terminal:
                break
        else:
            _fail("unterminated_wrapper_extern", "wrapper")
        text = "".join(block)
        hits = [symbol for symbol in symbols if symbol in text]
        if len(hits) != 1:
            _fail("wrapper_extern_identity", repr(hits))
        symbol = hits[0]
        matched[symbol] += 1
        removed.append(symbol)
    bad = {symbol: count for symbol, count in matched.items() if count != 1}
    if bad:
        _fail("wrapper_extern_cardinality", repr(bad))
    return "".join(output), tuple(removed)


def _leaf_body(ptx: str, symbol: str, expected_environment_count: int) -> tuple[str, tuple[str, ...]]:
    if ptx.count(symbol) < 1:
        _fail("leaf_symbol_missing", symbol)
    definitions = [match.group(1) for line in ptx.splitlines() if (match := _DEFINITION.match(line))]
    if definitions.count(symbol) != 1:
        _fail("leaf_symbol_definition_cardinality", f"{symbol}:{definitions.count(symbol)}")
    lines = ptx.splitlines(keepends=True)
    retained: list[str] = []
    environments: list[str] = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith((".version", ".target", ".address_size", ".file", ".loc")):
            continue
        if stripped.startswith(".extern"):
            _fail("leaf_external_dependency", symbol)
        match = _COMMON_ENV.match(line)
        if match:
            candidate = match.group(1)
            # The sole declaration is removable only if no second byte-level
            # occurrence exists anywhere in the leaf.
            if ptx.find(candidate, ptx.find(candidate) + len(candidate)) != -1:
                _fail("referenced_numba_environment", candidate)
            if candidate in environments:
                _fail("duplicate_numba_environment", candidate)
            environments.append(candidate)
            continue
        retained.append(line)
    if len(environments) != expected_environment_count:
        _fail(
            "numba_environment_cardinality",
            f"{symbol}: expected {expected_environment_count}, got {len(environments)}",
        )
    return "".join(retained), tuple(environments)


def compose_callback_ptx(
    wrapper_ptx: str,
    leaves: Sequence[DeviceFunctionArtifact],
    *,
    exact_symbols_by_role: Mapping[str, str],
    allow_unreferenced_exact_roles: bool = False,
) -> ComposedCallbackPtx:
    """Compose exact audited leaves into one trusted OptiX wrapper module."""

    if not isinstance(wrapper_ptx, str) or not wrapper_ptx:
        _fail("wrapper", "empty")
    if not leaves:
        _fail("leaves", "empty")
    roles = [leaf.role for leaf in leaves]
    if len(set(roles)) != len(roles):
        _fail("duplicate_role", repr(roles))
    if set(roles) != set(exact_symbols_by_role):
        _fail("role_set", repr(sorted(set(roles) ^ set(exact_symbols_by_role))))
    symbols = [exact_symbols_by_role[role] for role in roles]
    if len(set(symbols)) != len(symbols) or any(not item for item in symbols):
        _fail("symbol_set", repr(symbols))
    wrapper_identity = _directives(wrapper_ptx, "wrapper")
    for leaf, symbol in zip(leaves, symbols):
        if leaf.abi_name != symbol:
            _fail("artifact_symbol_binding", f"{leaf.role}:{leaf.abi_name}!={symbol}")
        if hashlib.sha256(leaf.ptx.encode("utf-8")).hexdigest() != leaf.ptx_sha256:
            _fail("leaf_digest", leaf.role)
        if _directives(leaf.ptx, leaf.role) != wrapper_identity:
            _fail("target_identity", leaf.role)
        for other in symbols:
            if other != symbol and other in leaf.ptx:
                _fail("cross_leaf_symbol", f"{leaf.role}:{other}")

    if allow_unreferenced_exact_roles:
        present = [symbol for symbol in symbols if symbol in wrapper_ptx]
        if present:
            _fail("unreferenced_role_specialization_is_partial", repr(present))
        wrapper = wrapper_ptx
        removed: tuple[str, ...] = ()
    else:
        wrapper, removed = _strip_wrapper_externs(wrapper_ptx, symbols)
    address_line = f".address_size {wrapper_identity[2]}"
    address_index = wrapper.find(address_line)
    if address_index < 0:
        _fail("wrapper_address", address_line)
    header_end = wrapper.find("\n", address_index)
    if header_end < 0:
        _fail("wrapper_header", "address directive has no newline")
    bodies: list[str] = []
    environments: list[str] = []
    if not allow_unreferenced_exact_roles:
        for leaf, symbol in zip(leaves, symbols):
            if leaf.compiler_function_count <= 0:
                _fail("compiler_function_count", f"{leaf.role}:{leaf.compiler_function_count}")
            body, leaf_environments = _leaf_body(
                leaf.ptx, symbol, leaf.compiler_function_count
            )
            bodies.append(body)
            environments.extend(leaf_environments)
    composed = wrapper[: header_end + 1] + "".join(bodies) + wrapper[header_end + 1 :]
    return ComposedCallbackPtx(
        ptx=composed,
        ptx_sha256=hashlib.sha256(composed.encode("utf-8")).hexdigest(),
        ptx_version=wrapper_identity[0],
        ptx_target=wrapper_identity[1],
        address_size=wrapper_identity[2],
        wrapper_ptx_sha256=hashlib.sha256(wrapper_ptx.encode("utf-8")).hexdigest(),
        leaf_bindings=tuple((leaf.role, symbol) for leaf, symbol in zip(leaves, symbols)),
        stripped_wrapper_externs=removed,
        stripped_numba_environments=tuple(environments),
    )


def bind_inline_callback_ptx(
    ptx: str,
    *,
    exact_symbols_by_role: Mapping[str, str],
) -> ComposedCallbackPtx:
    """Bind a closed single-module PTX produced from verified inline leaves.

    The source compiler has already resolved the exact leaf definitions before
    NVRTC.  Optimized PTX may contain a definition, a call, or neither after
    forced inlining, so byte presence is not an identity test here; the caller
    binds the generated inline-source digests separately.
    """

    if not isinstance(ptx, str) or not ptx:
        _fail("inline_wrapper", "empty")
    if not exact_symbols_by_role:
        _fail("inline_leaf_bindings", "empty")
    roles = tuple(exact_symbols_by_role)
    symbols = tuple(exact_symbols_by_role[role] for role in roles)
    if len(set(roles)) != len(roles) or len(set(symbols)) != len(symbols) \
            or any(not item for item in symbols):
        _fail("inline_leaf_bindings", repr(exact_symbols_by_role))
    for symbol in symbols:
        pattern = re.compile(
            r"\.extern\s+\.func(?:\s+\([^)]*\))?[\s\S]{0,4096}?"
            + re.escape(symbol) + r"\b")
        if pattern.search(ptx):
            _fail("unresolved_inline_leaf", symbol)
    version, target, address_size = _directives(ptx, "inline_wrapper")
    digest = hashlib.sha256(ptx.encode("utf-8")).hexdigest()
    return ComposedCallbackPtx(
        ptx=ptx,
        ptx_sha256=digest,
        ptx_version=version,
        ptx_target=target,
        address_size=address_size,
        wrapper_ptx_sha256=digest,
        leaf_bindings=tuple((role, exact_symbols_by_role[role]) for role in roles),
        stripped_wrapper_externs=symbols,
        stripped_numba_environments=(),
    )


__all__ = [
    "bind_inline_callback_ptx",
    "CallbackPtxCompositionError",
    "ComposedCallbackPtx",
    "compose_callback_ptx",
]
