"""Trusted target compiler for the Goal5758 triangle-reduction successor."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

from .v4_callback_abi import CompiledCallbackAbi
from .v4_callback_ir import CallbackRole, RuntimeStatus, ScalarKind
from .v4_callback_numba_codegen import (
    FORMAL_NUMBA_SOURCE_SCHEMA,
    GeneratedFormalNumbaLeaf,
    _Emitter,
    _Value,
    _emit_helper,
    _integer_bounds,
    _leaf_scalar_kinds,
    _parameter_types,
    _reachable_helpers,
    compile_formal_numba_leaves_isolated,
)
from .v4_callback_poc import DeviceFunctionArtifact
from .v4_callback_ptx_composer import ComposedCallbackPtx, compose_callback_ptx
from .v4_triangle_optix_compiler import _compile_nvrtc
from .v4_triangle_reduction import (
    CompiledTriangleReductionContract,
    VerifiedTriangleReductionAuthority,
    compile_triangle_reduction_abi,
    compile_triangle_reduction_contract,
    verify_triangle_reduction_schema,
)
from .v4_triangle_reduction_optix_wrapper_codegen import (
    generate_trusted_optix_triangle_reduction_wrapper_v1,
)
from .v4_callback_optix_wrapper_codegen import GeneratedOptixWrapper


@dataclass(frozen=True, eq=False)
class VerifiedTriangleReductionExecutable:
    schema: str
    authority_sha256: str
    contract_sha256: str
    abi_sha256: str
    wrapper: GeneratedOptixWrapper
    wrapper_ptx: str
    wrapper_ptx_sha256: str
    generated_leaves: tuple[GeneratedFormalNumbaLeaf, ...]
    compiled_leaves: tuple[DeviceFunctionArtifact, ...]
    composed: ComposedCallbackPtx
    compiler_options: tuple[str, ...]
    nvrtc_log_sha256: str
    executable_sha256: str


_LIVE_EXECUTABLES: dict[int, str] = {}


class _TriangleReductionEmitter(_Emitter):
    """Successor-only checked U64/I64 addition lowering.

    The frozen Goal5751 emitter intentionally rejects integer arithmetic.
    M1 needs exactly checked addition for per-ray counters.  The guard is
    emitted before the device arithmetic so fixed-width wrap cannot hide an
    overflow.  Other integer arithmetic remains rejected by the frozen base.
    """

    def _numeric(self, op, left, right, result_type, path):
        kinds = _leaf_scalar_kinds(result_type, self.records)
        if op != "add" or not all(
                kind in {ScalarKind.I32, ScalarKind.U32, ScalarKind.I64, ScalarKind.U64}
                for kind in kinds):
            return super()._numeric(op, left, right, result_type, path)
        leaves: list[str] = []
        for a, b, kind in zip(left.leaves, right.leaves, kinds):
            low, high = _integer_bounds(kind)
            if low == 0:
                self.emit(f"if {b} > {high} - {a}:")
            else:
                self.emit(
                    f"if ({b} > 0 and {a} > {high} - {b}) or "
                    f"({b} < 0 and {a} < {low} - {b}):")
            with self.block():
                self.emit_failure(RuntimeStatus.INTEGER_OVERFLOW, path)
            temp = self.temp("checked_add")
            self.emit(f"{temp} = {a} + {b}")
            leaves.append(temp)
        return _Value(result_type, tuple(leaves))


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _authority_sha256(authority: VerifiedTriangleReductionAuthority) -> str:
    return _digest({
        "callback": authority.callback.ir_sha256,
        "effect": authority.callback.effect_digest,
        "schema": authority.schema.schema_sha256,
        "target": authority.target.target_sha256,
        "nonce": authority.authority_nonce,
    })


def _fresh(
    authority: VerifiedTriangleReductionAuthority,
    contract: CompiledTriangleReductionContract,
    abi: CompiledCallbackAbi,
    any_hit_proof_authority,
) -> VerifiedTriangleReductionAuthority:
    fresh = verify_triangle_reduction_schema(
        authority.callback, authority.schema, target=authority.target)
    if fresh != authority:
        raise RuntimeError("triangle-reduction authority does not rederive")
    expected_abi = compile_triangle_reduction_abi(
        fresh, any_hit_proof_authority=any_hit_proof_authority)
    if expected_abi != abi:
        raise RuntimeError("triangle-reduction ABI binding drift")
    expected_contract = compile_triangle_reduction_contract(
        fresh, abi_sha256=abi.abi_sha256)
    if expected_contract != contract or contract.executable:
        raise RuntimeError("exact non-executable M1 contract is required")
    return fresh


def generate_triangle_reduction_numba_leaf(
    authority: VerifiedTriangleReductionAuthority,
    abi: CompiledCallbackAbi,
    role: CallbackRole,
    *,
    any_hit_proof_authority,
) -> GeneratedFormalNumbaLeaf:
    """Generate source only after successor-authority ABI reverification.

    This is intentionally a narrow bridge over the frozen Goal5751 source
    emitter.  It does not compile the original user callable and it does not
    bypass the successor schema; the exact ABI is regenerated first.
    """

    fresh = verify_triangle_reduction_schema(
        authority.callback, authority.schema, target=authority.target)
    if fresh != authority:
        raise RuntimeError("triangle-reduction authority does not rederive")
    if compile_triangle_reduction_abi(
            fresh, any_hit_proof_authority=any_hit_proof_authority) != abi:
        raise RuntimeError("triangle-reduction ABI binding drift")
    role_abi = next((item for item in abi.roles if item.role is role), None)
    if role_abi is None:
        raise RuntimeError(f"role is absent from successor ABI: {role.value}")
    function = fresh.callback.program.function_for_role(role)
    emitter = _TriangleReductionEmitter(
        verified=fresh.callback, abi=abi, role_abi=role_abi)
    for helper in sorted(emitter.helpers.values(), key=lambda item: item.name):
        _emit_helper(emitter, helper)
        emitter.emit()
    emitter.emit_role(function)
    source = "\n".join(emitter.lines) + "\n"
    compile(source, "<rtdl-v4-generated-triangle-reduction>", "exec")
    return GeneratedFormalNumbaLeaf(
        schema=FORMAL_NUMBA_SOURCE_SCHEMA,
        role=role,
        abi_name=role_abi.symbol,
        parameter_order=role_abi.parameter_order,
        parameter_types=_parameter_types(role_abi),
        generated_source=source,
        generated_source_sha256=hashlib.sha256(source.encode("utf-8")).hexdigest(),
        callback_ir_sha256=fresh.callback.ir_sha256,
        callback_effect_digest=fresh.callback.effect_digest,
        callback_abi_sha256=abi.abi_sha256,
        nonce_word=role_abi.nonce_word,
        numeric_mode="strict",
        error_sites=tuple(emitter.sites),
        compiler_function_count=1 + len(_reachable_helpers(function, emitter.helpers)),
    )


def compile_verified_triangle_reduction_executable(
    authority: VerifiedTriangleReductionAuthority,
    contract: CompiledTriangleReductionContract,
    abi: CompiledCallbackAbi,
    *,
    any_hit_proof_authority,
    compute_capability: tuple[int, int],
    optix_include: str | Path,
    cuda_include: str | Path,
    expected_python_version: str,
    expected_numba_version: str,
    expected_numpy_version: str,
    accepted_ptx_isa: tuple[str, str] = ("8.0", "9.0"),
    python_executable: str = sys.executable,
) -> tuple[VerifiedTriangleReductionExecutable, str]:
    fresh = _fresh(authority, contract, abi, any_hit_proof_authority)
    if compute_capability != tuple(
            int(item) for item in fresh.target.compute_capability.split(".")):
        raise RuntimeError("target compute capability does not match authority")
    roles = (
        CallbackRole.MAKE_RAY,
        CallbackRole.ANY_HIT,
        CallbackRole.MISS,
        CallbackRole.FINALIZE,
    )
    generated: list[GeneratedFormalNumbaLeaf] = []
    for role in roles:
        leaf = generate_triangle_reduction_numba_leaf(
            fresh, abi, role,
            any_hit_proof_authority=any_hit_proof_authority)
        generated.append(leaf)
    compiled = list(compile_formal_numba_leaves_isolated(
        generated,
        compute_capability=compute_capability,
        accepted_ptx_isa=accepted_ptx_isa,
        allowed_external_symbols=frozenset(),
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version,
        python_executable=python_executable,
    ))
    symbols = {
        role.value: artifact.abi_name
        for role, artifact in zip(roles, compiled, strict=True)
    }
    wrapper = generate_trusted_optix_triangle_reduction_wrapper_v1(
        fresh, contract, abi,
        any_hit_proof_authority=any_hit_proof_authority)
    options = (
        f"-I{Path(optix_include).resolve()}",
        f"-I{Path(cuda_include).resolve()}",
        f"-I{Path(cuda_include).resolve() / 'nv'}",
        "-I/usr/include",
        "-I/usr/include/x86_64-linux-gnu",
        "--std=c++14",
        f"--gpu-architecture=compute_{compute_capability[0]}{compute_capability[1]}",
        "--relocatable-device-code=true",
        "-D__x86_64__=1",
        "-D__LP64__=1",
    )
    wrapper_ptx, log = _compile_nvrtc(wrapper.source, options)
    composed = compose_callback_ptx(
        wrapper_ptx, compiled, exact_symbols_by_role=symbols,
        allow_unreferenced_exact_roles=not wrapper.linked_role_symbols)
    record = {
        "schema": "rtdl.v4.verified_triangle_reduction_executable.v1",
        "authority": _authority_sha256(fresh),
        "contract": contract.contract_sha256,
        "abi": abi.abi_sha256,
        "wrapper_source": wrapper.source_sha256,
        "wrapper_ptx": composed.wrapper_ptx_sha256,
        "generated": [item.generated_source_sha256 for item in generated],
        "compiled": [item.ptx_sha256 for item in compiled],
        "composed": composed.ptx_sha256,
        "options": options,
        "nvrtc_log": hashlib.sha256(log.encode("utf-8")).hexdigest(),
    }
    executable = VerifiedTriangleReductionExecutable(
        schema=record["schema"],
        authority_sha256=record["authority"],
        contract_sha256=contract.contract_sha256,
        abi_sha256=abi.abi_sha256,
        wrapper=wrapper,
        wrapper_ptx=wrapper_ptx,
        wrapper_ptx_sha256=composed.wrapper_ptx_sha256,
        generated_leaves=tuple(generated),
        compiled_leaves=tuple(compiled),
        composed=composed,
        compiler_options=options,
        nvrtc_log_sha256=record["nvrtc_log"],
        executable_sha256=_digest(record),
    )
    _LIVE_EXECUTABLES[id(executable)] = executable.executable_sha256
    return executable, log


def consume_verified_triangle_reduction_executable(
    executable: VerifiedTriangleReductionExecutable,
    authority: VerifiedTriangleReductionAuthority,
    contract: CompiledTriangleReductionContract,
    abi: CompiledCallbackAbi,
    *,
    any_hit_proof_authority,
) -> str:
    if not isinstance(executable, VerifiedTriangleReductionExecutable):
        raise TypeError("live VerifiedTriangleReductionExecutable is required")
    if _LIVE_EXECUTABLES.get(id(executable)) != executable.executable_sha256:
        raise RuntimeError("triangle-reduction executable is forged, serialized, or consumed")
    fresh = _fresh(authority, contract, abi, any_hit_proof_authority)
    expected_wrapper = generate_trusted_optix_triangle_reduction_wrapper_v1(
        fresh, contract, abi,
        any_hit_proof_authority=any_hit_proof_authority)
    if executable.wrapper != expected_wrapper \
            or executable.authority_sha256 != _authority_sha256(fresh) \
            or executable.contract_sha256 != contract.contract_sha256 \
            or executable.abi_sha256 != abi.abi_sha256:
        raise RuntimeError("triangle-reduction executable binding drift")
    expected_generated = tuple(
        generate_triangle_reduction_numba_leaf(
            fresh, abi, role,
            any_hit_proof_authority=any_hit_proof_authority)
        for role in (
            CallbackRole.MAKE_RAY, CallbackRole.ANY_HIT,
            CallbackRole.MISS, CallbackRole.FINALIZE,
        )
    )
    if executable.generated_leaves != expected_generated:
        raise RuntimeError("generated triangle-reduction leaf identity drift")
    symbols = {item.role: item.abi_name for item in executable.compiled_leaves}
    recomposed = compose_callback_ptx(
        executable.wrapper_ptx, executable.compiled_leaves,
        exact_symbols_by_role=symbols)
    if recomposed != executable.composed \
            or hashlib.sha256(executable.wrapper_ptx.encode()).hexdigest() \
            != executable.wrapper_ptx_sha256:
        raise RuntimeError("composed triangle-reduction PTX identity drift")
    del _LIVE_EXECUTABLES[id(executable)]
    return executable.composed.ptx


__all__ = [
    "VerifiedTriangleReductionExecutable",
    "compile_verified_triangle_reduction_executable",
    "consume_verified_triangle_reduction_executable",
    "generate_triangle_reduction_numba_leaf",
]
