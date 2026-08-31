"""Trusted target compiler for the Goal5834 round-linear curve route."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

from .v4_callback_abi import CompiledCallbackAbi
from .v4_callback_ir import CallbackRole
from .v4_callback_numba_codegen import (
    GeneratedFormalNumbaLeaf,
    compile_formal_numba_leaf_isolated,
)
from .v4_callback_optix_wrapper_codegen import GeneratedOptixWrapper
from .v4_callback_poc import DeviceFunctionArtifact
from .v4_callback_ptx_composer import ComposedCallbackPtx, compose_callback_ptx
from .v4_curve_callback_abi import verify_curve_callback_abi
from .v4_curve_callback_numba_codegen import generate_formal_curve_numba_leaf
from .v4_curve_optix_wrapper_codegen import generate_trusted_optix_curve_wrapper_v1
from .v4_curve_physical_schema import (
    CurveCanonicalPlan,
    VerifiedCurvePhysicalAuthority,
    verify_builtin_curve_physical_schema,
)
from .v4_sphere_optix_compiler import _compile_nvrtc


@dataclass(frozen=True, eq=False)
class VerifiedCurveExecutable:
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


_LIVE_EXECUTABLES: dict[int, str] = {}


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _authority_sha256(authority: VerifiedCurvePhysicalAuthority) -> str:
    return _digest({
        "callback_ir_sha256": authority.callback.ir_sha256,
        "callback_effect_digest": authority.callback.effect_digest,
        "schema_sha256": authority.schema.schema_sha256,
        "target_sha256": authority.target.target_sha256,
        "authority_nonce": authority.authority_nonce,
    })


def _fresh(authority, plan, abi):
    fresh = verify_builtin_curve_physical_schema(
        authority.callback, authority.schema, target=authority.target)
    if fresh != authority or plan != fresh.canonical_plan or plan.executable:
        raise RuntimeError("curve authority/plan does not rederive")
    verify_curve_callback_abi(abi, fresh)
    return fresh


_ROLES = (
    CallbackRole.MAKE_RAY,
    CallbackRole.CLOSEST_HIT,
    CallbackRole.MISS,
    CallbackRole.FINALIZE,
)


def _record(fresh, plan, abi, wrapper, generated, compiled, composed,
            options, log_sha):
    return {
        "schema": "rtdl.v4.verified_curve_executable.v1",
        "authority_sha256": _authority_sha256(fresh),
        "plan_sha256": plan.plan_sha256,
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


def compile_verified_curve_executable(
    authority: VerifiedCurvePhysicalAuthority,
    plan: CurveCanonicalPlan,
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
) -> tuple[VerifiedCurveExecutable, str]:
    fresh = _fresh(authority, plan, abi)
    if compute_capability != tuple(
            int(item) for item in fresh.target.compute_capability.split(".")):
        raise RuntimeError("target compute capability does not match authority")
    generated = []
    compiled = []
    symbols = {}
    for role in _ROLES:
        leaf = generate_formal_curve_numba_leaf(fresh, abi, role)
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
    wrapper = generate_trusted_optix_curve_wrapper_v1(fresh, plan, abi)
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
        wrapper.source, options, label="curve")
    composed = compose_callback_ptx(
        wrapper_ptx, compiled, exact_symbols_by_role=symbols)
    log_sha = hashlib.sha256(log.encode("utf-8")).hexdigest()
    record = _record(
        fresh, plan, abi, wrapper, generated, compiled, composed, options, log_sha)
    executable = VerifiedCurveExecutable(
        schema=record["schema"],
        authority_sha256=record["authority_sha256"],
        plan_sha256=plan.plan_sha256,
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


def _rederive(
    executable: VerifiedCurveExecutable,
    authority: VerifiedCurvePhysicalAuthority,
    plan: CurveCanonicalPlan,
    abi: CompiledCallbackAbi,
) -> tuple[VerifiedCurvePhysicalAuthority, str]:
    if not isinstance(executable, VerifiedCurveExecutable):
        raise TypeError("live VerifiedCurveExecutable required")
    fresh = _fresh(authority, plan, abi)
    wrapper = generate_trusted_optix_curve_wrapper_v1(fresh, plan, abi)
    generated = tuple(
        generate_formal_curve_numba_leaf(fresh, abi, role) for role in _ROLES)
    if executable.wrapper != wrapper or executable.generated_leaves != generated:
        raise RuntimeError("curve generated source identity drift")
    symbols = {item.role: item.abi_name for item in executable.compiled_leaves}
    recomposed = compose_callback_ptx(
        executable.wrapper_ptx, executable.compiled_leaves,
        exact_symbols_by_role=symbols)
    if recomposed != executable.composed \
            or hashlib.sha256(executable.wrapper_ptx.encode("utf-8")).hexdigest() \
                != executable.wrapper_ptx_sha256:
        raise RuntimeError("curve composed PTX identity drift")
    record = _record(
        fresh, plan, abi, wrapper, generated, executable.compiled_leaves,
        recomposed, executable.compiler_options, executable.nvrtc_log_sha256)
    derived = _digest(record)
    if _LIVE_EXECUTABLES.get(id(executable)) != derived:
        raise RuntimeError("curve executable live-registry identity drift")
    return fresh, derived


def rederive_verified_curve_executable_sha256(
    executable: VerifiedCurveExecutable,
    authority: VerifiedCurvePhysicalAuthority,
    plan: CurveCanonicalPlan,
    abi: CompiledCallbackAbi,
) -> str:
    return _rederive(executable, authority, plan, abi)[1]


def consume_verified_curve_executable(
    executable: VerifiedCurveExecutable,
    authority: VerifiedCurvePhysicalAuthority,
    plan: CurveCanonicalPlan,
    abi: CompiledCallbackAbi,
) -> str:
    _fresh_authority, derived = _rederive(executable, authority, plan, abi)
    if executable.executable_sha256 != derived:
        raise RuntimeError("curve executable sealed identity differs")
    del _LIVE_EXECUTABLES[id(executable)]
    return executable.composed.ptx


__all__ = [
    "VerifiedCurveExecutable", "compile_verified_curve_executable",
    "consume_verified_curve_executable",
    "rederive_verified_curve_executable_sha256",
]
