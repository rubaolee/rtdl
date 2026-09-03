"""Formal Numba-leaf adapter for the selected Goal5838 sphere topology."""

from __future__ import annotations

import hashlib

from . import v4_callback_numba_codegen as _base
from .v4_callback_abi import CompiledCallbackAbi
from .v4_callback_ir import CallbackRole, RuntimeStatus, ScalarKind
from .v4_sphere_any_hit_count_contract import (
    VerifiedSphereAnyHitCountAuthority,
    verify_sphere_any_hit_count_abi,
)


class _SphereAnyHitCountEmitter(_base._Emitter):
    """Narrow checked-integer extension for the selected count topology."""

    def _numeric(self, op, left, right, result_type, path):
        kinds = _base._leaf_scalar_kinds(result_type, self.records)
        if op != "add" or not all(
            kind in {
                ScalarKind.I32,
                ScalarKind.U32,
                ScalarKind.I64,
                ScalarKind.U64,
            }
            for kind in kinds
        ):
            return super()._numeric(op, left, right, result_type, path)
        leaves: list[str] = []
        for left_leaf, right_leaf, kind in zip(
            left.leaves, right.leaves, kinds
        ):
            low, high = _base._integer_bounds(kind)
            if low == 0:
                self.emit(f"if {right_leaf} > {high} - {left_leaf}:")
            else:
                self.emit(
                    f"if ({right_leaf} > 0 and {left_leaf} > "
                    f"{high} - {right_leaf}) or ({right_leaf} < 0 and "
                    f"{left_leaf} < {low} - {right_leaf}):"
                )
            with self.block():
                self.emit_failure(RuntimeStatus.INTEGER_OVERFLOW, path)
            temporary = self.temp("checked_add")
            self.emit(f"{temporary} = {left_leaf} + {right_leaf}")
            leaves.append(temporary)
        return _base._Value(result_type, tuple(leaves))


def generate_formal_sphere_any_hit_count_numba_leaf(
    authority: VerifiedSphereAnyHitCountAuthority,
    abi: CompiledCallbackAbi,
    role: CallbackRole,
) -> _base.GeneratedFormalNumbaLeaf:
    """Lower one selected-topology role through the generic leaf emitter."""

    proof = _proof_for(authority)
    canonical = verify_sphere_any_hit_count_abi(abi, authority, proof)
    verified = authority.callback
    role_abi = next((item for item in canonical.roles if item.role is role), None)
    if role_abi is None:
        raise _base.CallbackCodegenError(
            "role", role.value, "role is not present in selected sphere ABI"
        )
    function = verified.program.function_for_role(role)
    emitter = _SphereAnyHitCountEmitter(
        verified=verified, abi=canonical, role_abi=role_abi
    )
    for helper in sorted(emitter.helpers.values(), key=lambda item: item.name):
        _base._emit_helper(emitter, helper)
        emitter.emit()
    emitter.emit_role(function)
    source = "\n".join(emitter.lines) + "\n"
    compile(source, "<rtdl-v4-sphere-any-hit-count-numba>", "exec")
    return _base.GeneratedFormalNumbaLeaf(
        schema=_base.FORMAL_NUMBA_SOURCE_SCHEMA,
        role=role,
        abi_name=role_abi.symbol,
        parameter_order=role_abi.parameter_order,
        parameter_types=_base._parameter_types(role_abi),
        generated_source=source,
        generated_source_sha256=hashlib.sha256(
            source.encode("utf-8")
        ).hexdigest(),
        callback_ir_sha256=verified.ir_sha256,
        callback_effect_digest=verified.effect_digest,
        callback_abi_sha256=canonical.abi_sha256,
        nonce_word=role_abi.nonce_word,
        numeric_mode="strict",
        error_sites=tuple(emitter.sites),
        compiler_function_count=(
            1 + len(_base._reachable_helpers(function, emitter.helpers))
        ),
    )


def _proof_for(authority: VerifiedSphereAnyHitCountAuthority):
    from .v4_sphere_any_hit_count_contract import (
        derive_sphere_any_hit_count_proof,
    )

    return derive_sphere_any_hit_count_proof(authority.callback)


__all__ = ["generate_formal_sphere_any_hit_count_numba_leaf"]
