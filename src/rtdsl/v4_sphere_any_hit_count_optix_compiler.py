"""Trusted target compiler for the selected Goal5838 sphere topology."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from .v4_callback_abi import CompiledCallbackAbi
from .v4_callback_ir import CallbackRole
from .v4_callback_numba_codegen import (
    GeneratedFormalNumbaLeaf,
    compile_formal_numba_leaves_isolated,
)
from .v4_callback_optix_wrapper_codegen import GeneratedOptixWrapper
from .v4_callback_poc import DeviceFunctionArtifact
from .v4_callback_ptx_composer import ComposedCallbackPtx, compose_callback_ptx
from .v4_sphere_any_hit_count_contract import (
    SphereAnyHitCountCanonicalPlan,
    VerifiedSphereAnyHitCountAuthority,
    derive_sphere_any_hit_count_proof,
    verify_sphere_any_hit_count_abi,
    verify_sphere_any_hit_count_physical_schema,
)
from .v4_sphere_any_hit_count_numba_codegen import (
    generate_formal_sphere_any_hit_count_numba_leaf,
)
from .v4_sphere_any_hit_count_wrapper_codegen import (
    generate_trusted_optix_sphere_any_hit_count_wrapper_v1,
)
from .v4_sphere_optix_compiler import _compile_nvrtc


@dataclass(frozen=True, eq=False)
class VerifiedSphereAnyHitCountExecutable:
    """Live single-use authority for the composed selected-topology PTX."""

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
_ROLES = (
    CallbackRole.MAKE_RAY,
    CallbackRole.ANY_HIT,
    CallbackRole.MISS,
    CallbackRole.FINALIZE,
)


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    ).hexdigest()


def _authority_sha256(authority: VerifiedSphereAnyHitCountAuthority) -> str:
    return _digest(
        {
            "callback_ir_sha256": authority.callback.ir_sha256,
            "callback_effect_digest": authority.callback.effect_digest,
            "schema_sha256": authority.schema.schema_sha256,
            "target_sha256": authority.target.target_sha256,
            "authority_nonce": authority.authority_nonce,
        }
    )


def _fresh(
    authority: VerifiedSphereAnyHitCountAuthority,
    plan: SphereAnyHitCountCanonicalPlan,
    abi: CompiledCallbackAbi,
) -> VerifiedSphereAnyHitCountAuthority:
    fresh = verify_sphere_any_hit_count_physical_schema(
        authority.callback, authority.schema, target=authority.target
    )
    if fresh != authority or plan != fresh.canonical_plan or plan.executable:
        raise RuntimeError("selected sphere authority/plan does not rederive")
    proof = derive_sphere_any_hit_count_proof(fresh.callback)
    if verify_sphere_any_hit_count_abi(abi, fresh, proof) != abi:
        raise RuntimeError("selected sphere ABI binding drift")
    return fresh


def compile_verified_sphere_any_hit_count_executable(
    authority: VerifiedSphereAnyHitCountAuthority,
    plan: SphereAnyHitCountCanonicalPlan,
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
) -> tuple[VerifiedSphereAnyHitCountExecutable, str]:
    fresh = _fresh(authority, plan, abi)
    if compute_capability != tuple(
        int(item) for item in fresh.target.compute_capability.split(".")
    ):
        raise RuntimeError("target compute capability does not match authority")
    generated = tuple(
        generate_formal_sphere_any_hit_count_numba_leaf(fresh, abi, role)
        for role in _ROLES
    )
    compiled = tuple(
        compile_formal_numba_leaves_isolated(
            generated,
            compute_capability=compute_capability,
            accepted_ptx_isa=accepted_ptx_isa,
            allowed_external_symbols=frozenset(),
            expected_python_version=expected_python_version,
            expected_numba_version=expected_numba_version,
            expected_numpy_version=expected_numpy_version,
            python_executable=python_executable,
        )
    )
    symbols = {
        role.value: artifact.abi_name
        for role, artifact in zip(_ROLES, compiled, strict=True)
    }
    wrapper = generate_trusted_optix_sphere_any_hit_count_wrapper_v1(
        fresh, plan, abi
    )
    resolved_cuda = Path(cuda_include).resolve()
    options = (
        f"-I{Path(optix_include).resolve()}",
        f"-I{resolved_cuda}",
        f"-I{resolved_cuda / 'nv'}",
        "-I/usr/include",
        "-I/usr/include/x86_64-linux-gnu",
        "--std=c++14",
        (
            "--gpu-architecture=compute_"
            f"{compute_capability[0]}{compute_capability[1]}"
        ),
        "--relocatable-device-code=true",
        "-D__x86_64__=1",
        "-D__LP64__=1",
    )
    wrapper_ptx, log = _compile_nvrtc(
        wrapper.source, options, label="sphere_any_hit_count"
    )
    composed = compose_callback_ptx(
        wrapper_ptx, compiled, exact_symbols_by_role=symbols
    )
    record = {
        "schema": "rtdl.v4.verified_sphere_any_hit_count_executable.v1",
        "authority_sha256": _authority_sha256(fresh),
        "plan_sha256": plan.plan_sha256,
        "abi_sha256": abi.abi_sha256,
        "wrapper_source_sha256": wrapper.source_sha256,
        "wrapper_ptx_sha256": composed.wrapper_ptx_sha256,
        "generated_leaf_sha256": [
            item.generated_source_sha256 for item in generated
        ],
        "compiled_leaf_sha256": [item.ptx_sha256 for item in compiled],
        "composed_ptx_sha256": composed.ptx_sha256,
        "compiler_options": options,
        "nvrtc_log_sha256": hashlib.sha256(log.encode("utf-8")).hexdigest(),
    }
    executable = VerifiedSphereAnyHitCountExecutable(
        schema=record["schema"],
        authority_sha256=record["authority_sha256"],
        plan_sha256=plan.plan_sha256,
        abi_sha256=abi.abi_sha256,
        wrapper=wrapper,
        wrapper_ptx=wrapper_ptx,
        wrapper_ptx_sha256=composed.wrapper_ptx_sha256,
        generated_leaves=generated,
        compiled_leaves=compiled,
        composed=composed,
        compiler_options=options,
        nvrtc_log_sha256=record["nvrtc_log_sha256"],
        executable_sha256=_digest(record),
    )
    _LIVE_EXECUTABLES[id(executable)] = executable.executable_sha256
    return executable, log


def _rederive(
    executable: VerifiedSphereAnyHitCountExecutable,
    authority: VerifiedSphereAnyHitCountAuthority,
    plan: SphereAnyHitCountCanonicalPlan,
    abi: CompiledCallbackAbi,
) -> tuple[VerifiedSphereAnyHitCountAuthority, ComposedCallbackPtx, str]:
    if type(executable) is not VerifiedSphereAnyHitCountExecutable:
        raise TypeError("live VerifiedSphereAnyHitCountExecutable is required")
    fresh = _fresh(authority, plan, abi)
    expected_wrapper = generate_trusted_optix_sphere_any_hit_count_wrapper_v1(
        fresh, plan, abi
    )
    expected_generated = tuple(
        generate_formal_sphere_any_hit_count_numba_leaf(fresh, abi, role)
        for role in _ROLES
    )
    if (
        executable.wrapper != expected_wrapper
        or executable.generated_leaves != expected_generated
        or executable.authority_sha256 != _authority_sha256(fresh)
        or executable.plan_sha256 != plan.plan_sha256
        or executable.abi_sha256 != abi.abi_sha256
    ):
        raise RuntimeError("selected sphere executable authority binding drift")
    symbols = {item.role: item.abi_name for item in executable.compiled_leaves}
    recomposed = compose_callback_ptx(
        executable.wrapper_ptx,
        executable.compiled_leaves,
        exact_symbols_by_role=symbols,
    )
    wrapper_ptx_sha256 = hashlib.sha256(
        executable.wrapper_ptx.encode("utf-8")
    ).hexdigest()
    if (
        recomposed != executable.composed
        or wrapper_ptx_sha256 != executable.wrapper_ptx_sha256
        or wrapper_ptx_sha256 != recomposed.wrapper_ptx_sha256
    ):
        raise RuntimeError("selected sphere composed PTX identity drift")
    record = {
        "schema": "rtdl.v4.verified_sphere_any_hit_count_executable.v1",
        "authority_sha256": _authority_sha256(fresh),
        "plan_sha256": plan.plan_sha256,
        "abi_sha256": abi.abi_sha256,
        "wrapper_source_sha256": expected_wrapper.source_sha256,
        "wrapper_ptx_sha256": recomposed.wrapper_ptx_sha256,
        "generated_leaf_sha256": [
            item.generated_source_sha256 for item in expected_generated
        ],
        "compiled_leaf_sha256": [
            item.ptx_sha256 for item in executable.compiled_leaves
        ],
        "composed_ptx_sha256": recomposed.ptx_sha256,
        "compiler_options": executable.compiler_options,
        "nvrtc_log_sha256": executable.nvrtc_log_sha256,
    }
    return fresh, recomposed, _digest(record)


def rederive_verified_sphere_any_hit_count_executable_sha256(
    executable: VerifiedSphereAnyHitCountExecutable,
    authority: VerifiedSphereAnyHitCountAuthority,
    plan: SphereAnyHitCountCanonicalPlan,
    abi: CompiledCallbackAbi,
) -> str:
    _, _, derived = _rederive(executable, authority, plan, abi)
    if _LIVE_EXECUTABLES.get(id(executable)) != derived:
        raise RuntimeError("selected sphere live-registry identity drift")
    return derived


def consume_verified_sphere_any_hit_count_executable(
    executable: VerifiedSphereAnyHitCountExecutable,
    authority: VerifiedSphereAnyHitCountAuthority,
    plan: SphereAnyHitCountCanonicalPlan,
    abi: CompiledCallbackAbi,
) -> str:
    _, recomposed, derived = _rederive(executable, authority, plan, abi)
    if _LIVE_EXECUTABLES.get(id(executable)) != derived:
        raise RuntimeError(
            "selected sphere executable is forged, serialized, or consumed"
        )
    del _LIVE_EXECUTABLES[id(executable)]
    return recomposed.ptx


__all__ = [
    "VerifiedSphereAnyHitCountExecutable",
    "compile_verified_sphere_any_hit_count_executable",
    "consume_verified_sphere_any_hit_count_executable",
    "rederive_verified_sphere_any_hit_count_executable_sha256",
]
