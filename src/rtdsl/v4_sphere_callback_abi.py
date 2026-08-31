"""Successor ABI adapter for the Goal5833 built-in-sphere authority.

The Goal5751 ABI compiler is frozen evidence.  This module deliberately does
not widen its accepted authority class.  Instead it reuses the frozen ABI
vocabulary and layout helpers after independently re-verifying the successor
sphere authority, then binds the result to the exact sphere Callback IR.
"""

from __future__ import annotations

import hashlib

from . import v4_callback_abi as _base
from .v4_callback_ir import CallbackRole, ROLE_STAGE
from .v4_sphere_physical_schema import (
    VerifiedSpherePhysicalAuthority,
    verify_builtin_sphere_physical_schema,
)


def _fresh(authority: VerifiedSpherePhysicalAuthority):
    if not isinstance(authority, VerifiedSpherePhysicalAuthority):
        raise _base.CallbackAbiError(
            "sphere_authority_required", "physical_schema_authority",
            "live VerifiedSpherePhysicalAuthority required")
    fresh = verify_builtin_sphere_physical_schema(
        authority.callback, authority.schema, target=authority.target)
    if fresh != authority:
        raise _base.CallbackAbiError(
            "sphere_authority_reverification", "physical_schema_authority",
            "sphere authority does not rederive exactly")
    return fresh


def compile_sphere_callback_abi(
    authority: VerifiedSpherePhysicalAuthority,
) -> _base.CompiledCallbackAbi:
    fresh = _fresh(authority)
    verified = fresh.callback
    role_functions = {
        item.role: item for item in verified.program.functions
        if item.role is not None
    }
    if CallbackRole.ANY_HIT in role_functions:
        raise _base.CallbackAbiError(
            "sphere_any_hit_forbidden", "program.functions",
            "the compiler-owned sphere enumerator is not user Callback IR")
    records = {item.name: item for item in verified.program.records}
    roles = []
    for role in CallbackRole:
        function = role_functions.get(role)
        if function is None:
            continue
        inputs = [
            _base.AbiField(
                "in.context.launch_index", "u64", "in", "launch_index", True),
        ]
        for argument in function.arguments:
            inputs.extend(_base._flatten_type(
                argument.value_type,
                f"in.{argument.name}",
                direction="in",
                records=records,
                seen=set(),
            ))
        nonce = int(hashlib.sha256(
            f"{verified.ir_sha256}:{verified.effect_digest}:{role.value}".encode(
                "ascii")
        ).hexdigest()[:8], 16)
        roles.append(_base.RoleAbi(
            role=role,
            role_tag=_base._ROLE_TAGS[role],
            stage_tag=_base._STAGE_TAGS[ROLE_STAGE[role]],
            symbol=f"rtdl_v4_{role.value}_{verified.ir_sha256[:16]}",
            inputs=tuple(inputs),
            status=_base._STATUS_FIELDS,
            effects=_base._effect_variants(function, records),
            first_error_policy=_base._FIRST_ERROR_POLICY,
            nonce_word=nonce,
        ))
    base = _base.CompiledCallbackAbi(
        schema_id=_base.CALLBACK_ABI_SCHEMA_ID,
        schema_version=_base.CALLBACK_ABI_SCHEMA_VERSION,
        callback_ir_sha256=verified.ir_sha256,
        callback_effect_digest=verified.effect_digest,
        any_hit_proof_sha256=None,
        any_hit_proof_kind=None,
        any_hit_delivery_contract=None,
        runtime_status_codes=_base._RUNTIME_STATUS_CODES,
        roles=tuple(roles),
        abi_sha256="",
    )
    digest = hashlib.sha256(
        _base._canonical_json(base.payload_without_digest())).hexdigest()
    return _base.CompiledCallbackAbi(**{**base.__dict__, "abi_sha256": digest})


def verify_sphere_callback_abi(
    artifact: _base.CompiledCallbackAbi,
    authority: VerifiedSpherePhysicalAuthority,
) -> _base.CompiledCallbackAbi:
    fresh = _fresh(authority)
    if type(artifact) is not _base.CompiledCallbackAbi:
        raise _base.CallbackAbiError(
            "sphere_abi_type", "abi", "CompiledCallbackAbi required")
    if artifact.callback_ir_sha256 != fresh.callback.ir_sha256 \
            or artifact.callback_effect_digest != fresh.callback.effect_digest:
        raise _base.CallbackAbiError(
            "sphere_abi_program_binding", "abi",
            "ABI does not bind the exact sphere Callback IR/effects")
    # Dataclass equality deliberately follows Python value equality, under
    # which (for example) ``readonly=1`` equals ``readonly=True``.  Re-decode
    # the serialized shape so every scalar has its exact ABI type and its
    # digest rederives before comparing canonical bytes to recompilation.
    try:
        decoded = _base.callback_abi_from_dict(artifact.to_dict())
    except _base.CallbackAbiError as exc:
        raise _base.CallbackAbiError(
            "sphere_abi_artifact_invalid", exc.path,
            f"{exc.code}: {exc.message}") from exc
    expected = compile_sphere_callback_abi(fresh)
    if _base._canonical_json(decoded.to_dict()) != \
            _base._canonical_json(expected.to_dict()):
        raise _base.CallbackAbiError(
            "sphere_abi_recompile_mismatch", "abi",
            "sphere ABI differs from exact successor recompilation")
    return decoded


__all__ = ["compile_sphere_callback_abi", "verify_sphere_callback_abi"]
