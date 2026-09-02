"""Trusted target compiler for curve owner-grouped any-hit."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

from .v4_callback_abi import CompiledCallbackAbi
from .v4_callback_ir import CallbackRole
from .v4_callback_numba_codegen import (
    FORMAL_NUMBA_SOURCE_SCHEMA,
    GeneratedFormalNumbaLeaf,
    _Emitter,
    _emit_helper,
    _parameter_types,
    _reachable_helpers,
    compile_formal_numba_leaf_isolated,
)
from .v4_callback_poc import DeviceFunctionArtifact
from .v4_callback_ptx_composer import ComposedCallbackPtx, compose_callback_ptx
from .v4_curve_owner_grouped_any_hit import (
    VerifiedCurveOwnerGroupedAnyHitAuthority,
    verify_curve_owner_grouped_any_hit_physical_schema,
)
from .v4_curve_owner_grouped_any_hit_optix_wrapper_codegen import (
    generate_trusted_optix_curve_owner_grouped_any_hit_wrapper_v1,
)
from .v4_owner_grouped_any_hit import verify_owner_grouped_any_hit_abi
from .v4_sphere_optix_compiler import _compile_nvrtc
from .v4_callback_optix_wrapper_codegen import GeneratedOptixWrapper


@dataclass(frozen=True, eq=False)
class VerifiedCurveOwnerGroupedAnyHitExecutable:
    schema: str
    authority_sha256: str
    plan_sha256: str
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


_ROLES = (
    CallbackRole.MAKE_RAY,
    CallbackRole.ANY_HIT,
    CallbackRole.MISS,
    CallbackRole.FINALIZE,
)
_LIVE_EXECUTABLES: dict[int, str] = {}


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _fresh(authority, abi):
    fresh = verify_curve_owner_grouped_any_hit_physical_schema(
        authority.behavior, authority.schema, target=authority.target)
    if fresh != authority or authority.canonical_plan.executable:
        raise RuntimeError("curve owner-grouped authority does not rederive")
    verify_owner_grouped_any_hit_abi(abi, fresh.behavior)
    return fresh


def _authority_sha256(authority) -> str:
    return _digest({
        "behavior": authority.behavior.authority_sha256,
        "physical_schema": authority.schema.schema_sha256,
        "target": authority.target.target_sha256,
        "nonce": authority.authority_nonce,
    })


def generate_curve_owner_grouped_any_hit_numba_leaf(
    authority: VerifiedCurveOwnerGroupedAnyHitAuthority,
    abi: CompiledCallbackAbi,
    role: CallbackRole,
) -> GeneratedFormalNumbaLeaf:
    fresh = _fresh(authority, abi)
    role_abi = next((item for item in abi.roles if item.role is role), None)
    if role_abi is None:
        raise RuntimeError(f"role is absent from owner-grouped ABI: {role.value}")
    function = fresh.callback.program.function_for_role(role)
    emitter = _Emitter(
        verified=fresh.callback, abi=abi, role_abi=role_abi)
    for helper in sorted(emitter.helpers.values(), key=lambda item: item.name):
        _emit_helper(emitter, helper)
        emitter.emit()
    emitter.emit_role(function)
    source = "\n".join(emitter.lines) + "\n"
    compile(source, "<rtdl-v4-generated-curve-owner-grouped-numba>", "exec")
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
        compiler_function_count=(
            1 + len(_reachable_helpers(function, emitter.helpers))),
    )


def _record(authority, abi, wrapper, generated, compiled, composed,
            options, log_sha):
    return {
        "schema": "rtdl.v4.verified_curve_owner_grouped_any_hit_executable.v1",
        "authority_sha256": _authority_sha256(authority),
        "plan_sha256": authority.canonical_plan.plan_sha256,
        "abi_sha256": abi.abi_sha256,
        "wrapper_source_sha256": wrapper.source_sha256,
        "wrapper_ptx_sha256": composed.wrapper_ptx_sha256,
        "generated_leaf_sha256": [
            item.generated_source_sha256 for item in generated],
        "compiled_leaf_sha256": [item.ptx_sha256 for item in compiled],
        "composed_ptx_sha256": composed.ptx_sha256,
        "compiler_options": options,
        "nvrtc_log_sha256": log_sha,
    }


def compile_verified_curve_owner_grouped_any_hit_executable(
    authority: VerifiedCurveOwnerGroupedAnyHitAuthority,
    abi: CompiledCallbackAbi,
    *,
    compute_capability: tuple[int, int],
    optix_include: str | Path,
    cuda_include: str | Path,
    expected_python_version: str,
    expected_numba_version: str,
    expected_numpy_version: str,
    accepted_ptx_isa: tuple[str, str] = ("8.0", "9.0"),
    python_executable: str = sys.executable,
) -> tuple[VerifiedCurveOwnerGroupedAnyHitExecutable, str]:
    fresh = _fresh(authority, abi)
    if compute_capability != tuple(
            int(item) for item in fresh.target.compute_capability.split(".")):
        raise RuntimeError("target compute capability does not match authority")
    generated = []
    compiled = []
    symbols = {}
    for role in _ROLES:
        leaf = generate_curve_owner_grouped_any_hit_numba_leaf(
            fresh, abi, role)
        artifact = compile_formal_numba_leaf_isolated(
            leaf,
            compute_capability=compute_capability,
            accepted_ptx_isa=accepted_ptx_isa,
            allowed_external_symbols=frozenset(),
            expected_python_version=expected_python_version,
            expected_numba_version=expected_numba_version,
            expected_numpy_version=expected_numpy_version,
            python_executable=python_executable,
        )
        generated.append(leaf)
        compiled.append(artifact)
        symbols[role.value] = artifact.abi_name
    wrapper = generate_trusted_optix_curve_owner_grouped_any_hit_wrapper_v1(
        fresh, abi)
    options = (
        f"-I{Path(optix_include).resolve()}",
        f"-I{Path(cuda_include).resolve()}",
        "-I/usr/include",
        "-I/usr/include/x86_64-linux-gnu",
        "--std=c++14",
        f"--gpu-architecture=compute_{compute_capability[0]}{compute_capability[1]}",
        "--relocatable-device-code=true",
        "-D__x86_64__=1",
        "-D__LP64__=1",
    )
    wrapper_ptx, log = _compile_nvrtc(
        wrapper.source, options, label="curve-owner-grouped-any-hit")
    composed = compose_callback_ptx(
        wrapper_ptx, compiled, exact_symbols_by_role=symbols)
    log_sha = hashlib.sha256(log.encode("utf-8")).hexdigest()
    record = _record(
        fresh, abi, wrapper, generated, compiled, composed, options, log_sha)
    executable = VerifiedCurveOwnerGroupedAnyHitExecutable(
        schema=record["schema"],
        authority_sha256=record["authority_sha256"],
        plan_sha256=fresh.canonical_plan.plan_sha256,
        abi_sha256=abi.abi_sha256,
        wrapper=wrapper,
        wrapper_ptx=wrapper_ptx,
        wrapper_ptx_sha256=composed.wrapper_ptx_sha256,
        generated_leaves=tuple(generated),
        compiled_leaves=tuple(compiled),
        composed=composed,
        compiler_options=options,
        nvrtc_log_sha256=log_sha,
        executable_sha256=_digest(record),
    )
    _LIVE_EXECUTABLES[id(executable)] = executable.executable_sha256
    return executable, log


def _rederive(executable, authority, abi):
    if not isinstance(executable, VerifiedCurveOwnerGroupedAnyHitExecutable):
        raise TypeError("live VerifiedCurveOwnerGroupedAnyHitExecutable required")
    fresh = _fresh(authority, abi)
    wrapper = generate_trusted_optix_curve_owner_grouped_any_hit_wrapper_v1(
        fresh, abi)
    generated = tuple(
        generate_curve_owner_grouped_any_hit_numba_leaf(fresh, abi, role)
        for role in _ROLES)
    if executable.wrapper != wrapper or executable.generated_leaves != generated:
        raise RuntimeError("owner-grouped generated source identity drift")
    symbols = {item.role: item.abi_name for item in executable.compiled_leaves}
    recomposed = compose_callback_ptx(
        executable.wrapper_ptx,
        executable.compiled_leaves,
        exact_symbols_by_role=symbols,
    )
    if recomposed != executable.composed \
            or hashlib.sha256(executable.wrapper_ptx.encode("utf-8")).hexdigest() \
                != executable.wrapper_ptx_sha256:
        raise RuntimeError("owner-grouped composed PTX identity drift")
    record = _record(
        fresh, abi, wrapper, generated, executable.compiled_leaves,
        recomposed, executable.compiler_options, executable.nvrtc_log_sha256)
    derived = _digest(record)
    if _LIVE_EXECUTABLES.get(id(executable)) != derived:
        raise RuntimeError("owner-grouped executable live identity drift")
    return fresh, derived


def consume_verified_curve_owner_grouped_any_hit_executable(
    executable: VerifiedCurveOwnerGroupedAnyHitExecutable,
    authority: VerifiedCurveOwnerGroupedAnyHitAuthority,
    abi: CompiledCallbackAbi,
) -> str:
    _fresh_authority, derived = _rederive(executable, authority, abi)
    if executable.executable_sha256 != derived:
        raise RuntimeError("owner-grouped executable sealed identity differs")
    del _LIVE_EXECUTABLES[id(executable)]
    return executable.composed.ptx


__all__ = [
    "VerifiedCurveOwnerGroupedAnyHitExecutable",
    "compile_verified_curve_owner_grouped_any_hit_executable",
    "consume_verified_curve_owner_grouped_any_hit_executable",
    "generate_curve_owner_grouped_any_hit_numba_leaf",
]
