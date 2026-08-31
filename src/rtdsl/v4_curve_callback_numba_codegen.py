"""Curve-authority adapter for the frozen formal Numba leaf generator."""

from __future__ import annotations

import hashlib

from . import v4_callback_numba_codegen as _base
from .v4_callback_abi import CompiledCallbackAbi
from .v4_callback_ir import CallbackRole
from .v4_curve_callback_abi import verify_curve_callback_abi
from .v4_curve_physical_schema import VerifiedCurvePhysicalAuthority


def generate_formal_curve_numba_leaf(
    authority: VerifiedCurvePhysicalAuthority,
    abi: CompiledCallbackAbi,
    role: CallbackRole,
) -> _base.GeneratedFormalNumbaLeaf:
    canonical = verify_curve_callback_abi(abi, authority)
    verified = authority.callback
    role_abi = next((item for item in canonical.roles if item.role is role), None)
    if role_abi is None:
        raise _base.CallbackCodegenError(
            "role", role.value, "role is not present in exact curve ABI")
    function = verified.program.function_for_role(role)
    emitter = _base._Emitter(
        verified=verified, abi=canonical, role_abi=role_abi)
    for helper in sorted(emitter.helpers.values(), key=lambda item: item.name):
        _base._emit_helper(emitter, helper)
        emitter.emit()
    emitter.emit_role(function)
    source = "\n".join(emitter.lines) + "\n"
    compile(source, "<rtdl-v4-generated-formal-curve-numba>", "exec")
    return _base.GeneratedFormalNumbaLeaf(
        schema=_base.FORMAL_NUMBA_SOURCE_SCHEMA,
        role=role,
        abi_name=role_abi.symbol,
        parameter_order=role_abi.parameter_order,
        parameter_types=_base._parameter_types(role_abi),
        generated_source=source,
        generated_source_sha256=hashlib.sha256(source.encode("utf-8")).hexdigest(),
        callback_ir_sha256=verified.ir_sha256,
        callback_effect_digest=verified.effect_digest,
        callback_abi_sha256=canonical.abi_sha256,
        nonce_word=role_abi.nonce_word,
        numeric_mode="strict",
        error_sites=tuple(emitter.sites),
        compiler_function_count=(
            1 + len(_base._reachable_helpers(function, emitter.helpers))),
    )


__all__ = ["generate_formal_curve_numba_leaf"]
