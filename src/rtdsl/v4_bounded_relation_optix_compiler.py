"""Trusted compiler for V4 custom-AABB bounded relation emission."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path
import sys

from .v4_bounded_relation import (
    CompiledBoundedRelationContract,
    VerifiedBoundedRelationAuthority,
    compile_bounded_relation_contract,
    verify_bounded_relation_schema,
)
from .v4_bounded_relation_optix_wrapper_codegen import (
    generate_trusted_bounded_relation_wrapper_v1,
)
from .v4_callback_abi import CompiledCallbackAbi, verify_compiled_callback_abi
from .v4_callback_ir import CallbackRole, RuntimeStatus, ScalarKind
from .v4_callback_numba_codegen import (
    FORMAL_NUMBA_SOURCE_SCHEMA,
    GeneratedFormalNumbaLeaf,
    FormalNumbaLeafCachePolicy,
    _Emitter,
    _Value,
    _emit_helper,
    _integer_bounds,
    _leaf_scalar_kinds,
    _parameter_types,
    _parameter_name,
    _reachable_helpers,
    compile_formal_numba_leaves_isolated,
)
from .v4_callback_optix_wrapper_codegen import GeneratedOptixWrapper
from .v4_callback_optix_wrapper_codegen import _prototype
from .v4_callback_poc import DeviceFunctionArtifact
from .v4_callback_ptx_composer import (
    ComposedCallbackPtx,
    bind_inline_callback_ptx,
)
from .v4_inline_cuda_codegen import lower_formal_leaves_to_inline_cuda
from .v4_triangle_optix_compiler import _compile_nvrtc


@dataclass(frozen=True, eq=False)
class VerifiedBoundedRelationExecutable:
    schema: str
    authority_sha256: str
    contract_sha256: str
    abi_sha256: str
    wrapper: GeneratedOptixWrapper
    wrapper_ptx: str
    wrapper_ptx_sha256: str
    generated_leaves: tuple[GeneratedFormalNumbaLeaf, ...]
    compiled_leaves: tuple[DeviceFunctionArtifact, ...]
    inline_cuda_source_sha256: str
    inline_cuda_leaf_sha256: tuple[tuple[str, str], ...]
    composed: ComposedCallbackPtx
    compiler_options: tuple[str, ...]
    nvrtc_log_sha256: str
    executable_sha256: str


_LIVE_EXECUTABLES: dict[int, str] = {}


def _inline_wrapper(
    wrapper: GeneratedOptixWrapper,
    abi: CompiledCallbackAbi,
    leaves: tuple[GeneratedFormalNumbaLeaf, ...],
) -> tuple[GeneratedOptixWrapper, str, tuple[tuple[str, str], ...]]:
    if not leaves or any(
            leaf.callback_ir_sha256 != abi.callback_ir_sha256
            or leaf.callback_effect_digest != abi.callback_effect_digest
            for leaf in leaves):
        raise RuntimeError(
            "bounded-relation fused lowering requires the exact standard "
            "callback IR and effect projection")
    roles = {item.role: item for item in abi.roles}
    trusted_finite = {
        role.value: frozenset(
            _parameter_name(field.path)
            for field in roles[role].inputs
            if field.scalar == "f32" or field.scalar == "device_ptr<f32>"
        )
        for role in CallbackRole
    }
    definitions, leaf_identities = lower_formal_leaves_to_inline_cuda(
        leaves,
        trusted_finite_inputs_by_role=trusted_finite,
        # These exact emitter error-code/site pairs are discharged by
        # ``v4_relation_boxes`` before any GAS/cache/launch publication.  The
        # inline lowerer requires every listed pair to exist and removes no
        # unlisted failure guard.  ANY_HIT is deliberately absent: its checked
        # U32 payload increment remains a dynamic device obligation.
        proven_failure_guards_by_role={
            CallbackRole.BOUNDS.value: frozenset(
                [(2, site) for site in range(1, 7)]
                + [(3, site) for site in range(7, 13)]
                + [(10, 13)]),
            CallbackRole.MAKE_RAY.value: frozenset(
                [(7, 1)]
                + [(2, site) for site in range(2, 8)]
                + [(3, site) for site in range(8, 18)]
                + [(9, 18)]
                + [(3, site) for site in range(19, 29)]
                + [(9, 29)]),
            CallbackRole.INTERSECTION.value: frozenset(
                [(2, site) for site in range(1, 15)]
                + [(3, 15), (3, 16), (3, 17), (11, 18)]),
            CallbackRole.CLOSEST_HIT.value: frozenset({(2, 1)}),
            CallbackRole.MISS.value: frozenset(
                (2, site) for site in range(1, 9)),
        },
    )
    prototypes = "\n".join(_prototype(roles[role]) for role in CallbackRole)
    if wrapper.source.count(prototypes) != 1:
        raise RuntimeError("bounded-relation wrapper prototype anchor drift")
    source = wrapper.source.replace(
        prototypes, prototypes + "\n\n" + definitions, 1)
    source_sha256 = hashlib.sha256(source.encode("utf-8")).hexdigest()
    return (
        replace(wrapper, source=source, source_sha256=source_sha256),
        hashlib.sha256(definitions.encode("utf-8")).hexdigest(),
        leaf_identities,
    )


class _BoundedRelationEmitter(_Emitter):
    """Checked integer addition needed by payload counters.

    This extends only the frozen verified IR-to-Numba emitter.  It does not
    accept Python callables or arbitrary device code.
    """

    def _numeric(self, op, left, right, result_type, path):
        kinds = _leaf_scalar_kinds(result_type, self.records)
        if op != "add" or not all(
                kind in {ScalarKind.I32, ScalarKind.U32,
                         ScalarKind.I64, ScalarKind.U64}
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


def _authority_sha256(authority: VerifiedBoundedRelationAuthority) -> str:
    return _digest({
        "callback": authority.physical.callback.ir_sha256,
        "effect": authority.physical.callback.effect_digest,
        "physical_schema": authority.physical.schema.schema_sha256,
        "target": authority.physical.target.target_sha256,
        "relation_schema": authority.schema.schema_sha256,
        "nonce": authority.authority_nonce,
    })


def _fresh(authority, contract, abi, any_hit_proof_authority):
    fresh = verify_bounded_relation_schema(authority.physical, authority.schema)
    if fresh != authority:
        raise RuntimeError("bounded-relation authority does not rederive")
    expected_abi = verify_compiled_callback_abi(
        abi, fresh.physical.callback,
        any_hit_proof_authority=any_hit_proof_authority,
        physical_schema_authority=fresh.physical)
    if expected_abi != abi:
        raise RuntimeError("bounded-relation ABI binding drift")
    expected_contract = compile_bounded_relation_contract(
        fresh, abi_sha256=abi.abi_sha256)
    if expected_contract != contract or contract.executable:
        raise RuntimeError("exact non-executable relation contract is required")
    return fresh


def generate_bounded_relation_numba_leaf(
    authority: VerifiedBoundedRelationAuthority,
    abi: CompiledCallbackAbi,
    role: CallbackRole,
    *,
    any_hit_proof_authority,
) -> GeneratedFormalNumbaLeaf:
    fresh = verify_bounded_relation_schema(authority.physical, authority.schema)
    if fresh != authority:
        raise RuntimeError("bounded-relation authority does not rederive")
    if verify_compiled_callback_abi(
            abi, fresh.physical.callback,
            any_hit_proof_authority=any_hit_proof_authority,
            physical_schema_authority=fresh.physical) != abi:
        raise RuntimeError("bounded-relation ABI binding drift")
    role_abi = next((item for item in abi.roles if item.role is role), None)
    if role_abi is None:
        raise RuntimeError(f"role is absent from ABI: {role.value}")
    function = fresh.physical.callback.program.function_for_role(role)
    emitter = _BoundedRelationEmitter(
        verified=fresh.physical.callback, abi=abi, role_abi=role_abi)
    for helper in sorted(emitter.helpers.values(), key=lambda item: item.name):
        _emit_helper(emitter, helper)
        emitter.emit()
    emitter.emit_role(function)
    source = "\n".join(emitter.lines) + "\n"
    compile(source, "<rtdl-v4-generated-bounded-relation>", "exec")
    return GeneratedFormalNumbaLeaf(
        schema=FORMAL_NUMBA_SOURCE_SCHEMA,
        role=role,
        abi_name=role_abi.symbol,
        parameter_order=role_abi.parameter_order,
        parameter_types=_parameter_types(role_abi),
        generated_source=source,
        generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        callback_ir_sha256=fresh.physical.callback.ir_sha256,
        callback_effect_digest=fresh.physical.callback.effect_digest,
        callback_abi_sha256=abi.abi_sha256,
        nonce_word=role_abi.nonce_word,
        numeric_mode="strict",
        error_sites=tuple(emitter.sites),
        compiler_function_count=1 + len(_reachable_helpers(function, emitter.helpers)),
    )


def compile_verified_bounded_relation_executable(
    authority: VerifiedBoundedRelationAuthority,
    contract: CompiledBoundedRelationContract,
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
    formal_leaf_cache: FormalNumbaLeafCachePolicy | None = None,
) -> tuple[VerifiedBoundedRelationExecutable, str]:
    fresh = _fresh(authority, contract, abi, any_hit_proof_authority)
    if compute_capability != tuple(
            int(item) for item in fresh.physical.target.compute_capability.split(".")):
        raise RuntimeError("target compute capability does not match authority")
    generated: list[GeneratedFormalNumbaLeaf] = []
    for role in CallbackRole:
        leaf = generate_bounded_relation_numba_leaf(
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
        formal_leaf_cache=formal_leaf_cache,
    ))
    symbols = {
        role.value: artifact.abi_name
        for role, artifact in zip(CallbackRole, compiled, strict=True)
    }
    base_wrapper = generate_trusted_bounded_relation_wrapper_v1(
        fresh, contract, abi,
        any_hit_proof_authority=any_hit_proof_authority)
    wrapper, inline_cuda_sha256, inline_leaf_sha256 = _inline_wrapper(
        base_wrapper, abi, tuple(generated))
    options = (
        f"-I{Path(optix_include).resolve()}",
        f"-I{Path(cuda_include).resolve()}",
        f"-I{Path(cuda_include).resolve() / 'nv'}",
        "-I/usr/include", "-I/usr/include/x86_64-linux-gnu",
        "--std=c++14",
        f"--gpu-architecture=compute_{compute_capability[0]}{compute_capability[1]}",
        "--relocatable-device-code=true", "-D__x86_64__=1", "-D__LP64__=1",
    )
    wrapper_ptx, log = _compile_nvrtc(wrapper.source, options)
    composed = bind_inline_callback_ptx(
        wrapper_ptx, exact_symbols_by_role=symbols)
    record = {
        "schema": "rtdl.v4.verified_bounded_relation_executable.v1",
        "authority": _authority_sha256(fresh),
        "contract": contract.contract_sha256,
        "abi": abi.abi_sha256,
        "wrapper_source": wrapper.source_sha256,
        "wrapper_ptx": composed.wrapper_ptx_sha256,
        "generated": [item.generated_source_sha256 for item in generated],
        "compiled": [item.ptx_sha256 for item in compiled],
        "inline_cuda": inline_cuda_sha256,
        "inline_cuda_leaves": inline_leaf_sha256,
        "composed": composed.ptx_sha256,
        "options": options,
        "nvrtc_log": hashlib.sha256(log.encode()).hexdigest(),
    }
    executable = VerifiedBoundedRelationExecutable(
        schema=record["schema"], authority_sha256=record["authority"],
        contract_sha256=contract.contract_sha256, abi_sha256=abi.abi_sha256,
        wrapper=wrapper, wrapper_ptx=wrapper_ptx,
        wrapper_ptx_sha256=composed.wrapper_ptx_sha256,
        generated_leaves=tuple(generated), compiled_leaves=tuple(compiled),
        inline_cuda_source_sha256=inline_cuda_sha256,
        inline_cuda_leaf_sha256=inline_leaf_sha256,
        composed=composed, compiler_options=options,
        nvrtc_log_sha256=record["nvrtc_log"],
        executable_sha256=_digest(record),
    )
    _LIVE_EXECUTABLES[id(executable)] = executable.executable_sha256
    return executable, log


def consume_verified_bounded_relation_executable(
    executable: VerifiedBoundedRelationExecutable,
    authority: VerifiedBoundedRelationAuthority,
    contract: CompiledBoundedRelationContract,
    abi: CompiledCallbackAbi,
    *,
    any_hit_proof_authority,
) -> str:
    if not isinstance(executable, VerifiedBoundedRelationExecutable):
        raise TypeError("live VerifiedBoundedRelationExecutable is required")
    if _LIVE_EXECUTABLES.get(id(executable)) != executable.executable_sha256:
        raise RuntimeError("bounded-relation executable is forged, serialized, or consumed")
    fresh = _fresh(authority, contract, abi, any_hit_proof_authority)
    base_wrapper = generate_trusted_bounded_relation_wrapper_v1(
        fresh, contract, abi,
        any_hit_proof_authority=any_hit_proof_authority)
    expected_generated = tuple(
        generate_bounded_relation_numba_leaf(
            fresh, abi, role,
            any_hit_proof_authority=any_hit_proof_authority)
        for role in CallbackRole)
    if executable.generated_leaves != expected_generated:
        raise RuntimeError("generated bounded-relation leaf identity drift")
    expected_wrapper, inline_cuda_sha256, inline_leaf_sha256 = _inline_wrapper(
        base_wrapper, abi, expected_generated)
    if executable.wrapper != expected_wrapper \
            or executable.inline_cuda_source_sha256 != inline_cuda_sha256 \
            or executable.inline_cuda_leaf_sha256 != inline_leaf_sha256 \
            or executable.authority_sha256 != _authority_sha256(fresh) \
            or executable.contract_sha256 != contract.contract_sha256 \
            or executable.abi_sha256 != abi.abi_sha256:
        raise RuntimeError("bounded-relation executable binding drift")
    symbols = {item.role: item.abi_name for item in executable.compiled_leaves}
    recomposed = bind_inline_callback_ptx(
        executable.wrapper_ptx, exact_symbols_by_role=symbols)
    if recomposed != executable.composed \
            or hashlib.sha256(executable.wrapper_ptx.encode()).hexdigest() \
            != executable.wrapper_ptx_sha256:
        raise RuntimeError("composed bounded-relation PTX identity drift")
    del _LIVE_EXECUTABLES[id(executable)]
    return executable.composed.ptx


__all__ = [
    "VerifiedBoundedRelationExecutable",
    "compile_verified_bounded_relation_executable",
    "consume_verified_bounded_relation_executable",
    "generate_bounded_relation_numba_leaf",
]
