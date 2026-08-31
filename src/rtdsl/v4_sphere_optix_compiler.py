"""Trusted target compiler and single-use executable authority for Goal5756."""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import Sequence

from .v4_callback_abi import CompiledCallbackAbi
from .v4_callback_ir import CallbackRole
from .v4_callback_numba_codegen import (
    GeneratedFormalNumbaLeaf,
    compile_formal_numba_leaf_isolated,
)
from .v4_callback_optix_wrapper_codegen import GeneratedOptixWrapper
from .v4_callback_poc import DeviceFunctionArtifact
from .v4_callback_ptx_composer import ComposedCallbackPtx, compose_callback_ptx
from .v4_sphere_optix_wrapper_codegen import (
    generate_trusted_optix_sphere_wrapper_v1,
)
from .v4_sphere_callback_abi import verify_sphere_callback_abi
from .v4_sphere_callback_numba_codegen import generate_formal_sphere_numba_leaf
from .v4_sphere_physical_schema import (
    SphereCanonicalPlan,
    VerifiedSpherePhysicalAuthority,
    verify_builtin_sphere_physical_schema,
)


@dataclass(frozen=True, eq=False)
class VerifiedSphereExecutable:
    """Live, single-use result of the trusted IR-to-target compiler chain."""

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


def _authority_sha256(authority: VerifiedSpherePhysicalAuthority) -> str:
    return _digest({
        "callback_ir_sha256": authority.callback.ir_sha256,
        "callback_effect_digest": authority.callback.effect_digest,
        "schema_sha256": authority.schema.schema_sha256,
        "target_sha256": authority.target.target_sha256,
        "authority_nonce": authority.authority_nonce,
    })


def _fresh(
    authority: VerifiedSpherePhysicalAuthority,
    plan: SphereCanonicalPlan,
    abi: CompiledCallbackAbi,
) -> VerifiedSpherePhysicalAuthority:
    fresh = verify_builtin_sphere_physical_schema(
        authority.callback,
        authority.schema,
        target=authority.target,
    )
    if fresh != authority:
        raise RuntimeError("typed physical authority does not rederive")
    expected_plan = fresh.canonical_plan
    if plan != expected_plan or plan.executable:
        raise RuntimeError("exact Goal5755 reference plan is required")
    verify_sphere_callback_abi(abi, fresh)
    return fresh


def _load_nvrtc() -> ctypes.CDLL:
    for name in ("libnvrtc.so.12", "libnvrtc.so"):
        try:
            return ctypes.CDLL(name)
        except OSError:
            pass
    raise RuntimeError("libnvrtc.so is unavailable")


def _compile_nvrtc(
    source: str, options: Sequence[str], *, label: str = "sphere",
) -> tuple[str, str]:
    library = _load_nvrtc()
    program = ctypes.c_void_p()
    create = library.nvrtcCreateProgram
    create.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_char_p,
                       ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p,
                       ctypes.c_void_p]
    create.restype = ctypes.c_int
    status = int(create(
        ctypes.byref(program), source.encode("utf-8"),
        f"rtdl_v4_trusted_{label}_wrapper.cu".encode("ascii"),
        0, None, None))
    if status:
        raise RuntimeError(f"NVRTC create failed with status {status}")
    encoded = [item.encode("utf-8") for item in options]
    option_array = (ctypes.c_char_p * len(encoded))(*encoded)
    compile_program = library.nvrtcCompileProgram
    compile_program.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_char_p)]
    compile_program.restype = ctypes.c_int
    status = int(compile_program(program, len(encoded), option_array))
    log_size = ctypes.c_size_t()
    library.nvrtcGetProgramLogSize(program, ctypes.byref(log_size))
    log = ctypes.create_string_buffer(max(1, log_size.value))
    library.nvrtcGetProgramLog(program, log)
    if status:
        raise RuntimeError(
            f"NVRTC trusted {label} wrapper compile failed:\n" +
            log.value.decode(errors="replace"))
    ptx_size = ctypes.c_size_t()
    if int(library.nvrtcGetPTXSize(program, ctypes.byref(ptx_size))):
        raise RuntimeError("NVRTC get PTX size failed")
    ptx = ctypes.create_string_buffer(ptx_size.value)
    if int(library.nvrtcGetPTX(program, ptx)):
        raise RuntimeError("NVRTC get PTX failed")
    library.nvrtcDestroyProgram(ctypes.byref(program))
    return ptx.value.decode("utf-8"), log.value.decode(errors="replace")


def compile_verified_sphere_executable(
    authority: VerifiedSpherePhysicalAuthority,
    plan: SphereCanonicalPlan,
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
) -> tuple[VerifiedSphereExecutable, str]:
    """Compile only trusted generated source and issue a live authority."""

    fresh = _fresh(authority, plan, abi)
    if compute_capability != tuple(
        int(item) for item in fresh.target.compute_capability.split(".")
    ):
        raise RuntimeError("target compute capability does not match authority")
    roles = (
        CallbackRole.MAKE_RAY,
        CallbackRole.CLOSEST_HIT,
        CallbackRole.MISS,
        CallbackRole.FINALIZE,
    )
    generated: list[GeneratedFormalNumbaLeaf] = []
    compiled: list[DeviceFunctionArtifact] = []
    symbols: dict[str, str] = {}
    for role in roles:
        leaf = generate_formal_sphere_numba_leaf(fresh, abi, role)
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
    wrapper = generate_trusted_optix_sphere_wrapper_v1(fresh, plan, abi)
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
    wrapper_ptx, log = _compile_nvrtc(wrapper.source, options)
    composed = compose_callback_ptx(
        wrapper_ptx, compiled, exact_symbols_by_role=symbols)
    record = {
        "schema": "rtdl.v4.verified_sphere_executable.v1",
        "authority_sha256": _authority_sha256(fresh),
        "plan_sha256": plan.plan_sha256,
        "abi_sha256": abi.abi_sha256,
        "wrapper_source_sha256": wrapper.source_sha256,
        "wrapper_ptx_sha256": composed.wrapper_ptx_sha256,
        "generated_leaf_sha256": [item.generated_source_sha256 for item in generated],
        "compiled_leaf_sha256": [item.ptx_sha256 for item in compiled],
        "composed_ptx_sha256": composed.ptx_sha256,
        "compiler_options": options,
        "nvrtc_log_sha256": hashlib.sha256(log.encode("utf-8")).hexdigest(),
    }
    executable = VerifiedSphereExecutable(
        schema=record["schema"],
        authority_sha256=_authority_sha256(fresh),
        plan_sha256=plan.plan_sha256,
        abi_sha256=abi.abi_sha256,
        wrapper=wrapper,
        wrapper_ptx=wrapper_ptx,
        wrapper_ptx_sha256=composed.wrapper_ptx_sha256,
        generated_leaves=tuple(generated),
        compiled_leaves=tuple(compiled),
        composed=composed,
        compiler_options=options,
        nvrtc_log_sha256=record["nvrtc_log_sha256"],
        executable_sha256=_digest(record),
    )
    _LIVE_EXECUTABLES[id(executable)] = executable.executable_sha256
    return executable, log


def consume_verified_sphere_executable(
    executable: VerifiedSphereExecutable,
    authority: VerifiedSpherePhysicalAuthority,
    plan: SphereCanonicalPlan,
    abi: CompiledCallbackAbi,
) -> str:
    """Reverify and consume one live executable exactly once."""

    if not isinstance(executable, VerifiedSphereExecutable):
        raise TypeError("live VerifiedSphereExecutable is required")
    if _LIVE_EXECUTABLES.get(id(executable)) != executable.executable_sha256:
        raise RuntimeError("sphere executable is forged, serialized, or consumed")
    fresh = _fresh(authority, plan, abi)
    expected_wrapper = generate_trusted_optix_sphere_wrapper_v1(
        fresh, plan, abi)
    if executable.wrapper != expected_wrapper:
        raise RuntimeError("trusted wrapper identity drift")
    if executable.authority_sha256 != _authority_sha256(fresh) \
            or executable.plan_sha256 != plan.plan_sha256 \
            or executable.abi_sha256 != abi.abi_sha256:
        raise RuntimeError("sphere executable authority binding drift")
    expected_generated = tuple(
        generate_formal_sphere_numba_leaf(fresh, abi, role)
        for role in (
            CallbackRole.MAKE_RAY, CallbackRole.CLOSEST_HIT,
            CallbackRole.MISS, CallbackRole.FINALIZE,
        )
    )
    if executable.generated_leaves != expected_generated:
        raise RuntimeError("generated leaf identity drift")
    symbols = {item.role: item.abi_name for item in executable.compiled_leaves}
    recomposed = compose_callback_ptx(
        executable.wrapper_ptx,
        executable.compiled_leaves,
        exact_symbols_by_role=symbols,
    )
    if recomposed != executable.composed \
            or hashlib.sha256(executable.wrapper_ptx.encode()).hexdigest() \
            != executable.wrapper_ptx_sha256:
        raise RuntimeError("composed sphere PTX identity drift")
    del _LIVE_EXECUTABLES[id(executable)]
    return executable.composed.ptx


def rederive_verified_sphere_executable_sha256(
    executable: VerifiedSphereExecutable,
    authority: VerifiedSpherePhysicalAuthority,
    plan: SphereCanonicalPlan,
    abi: CompiledCallbackAbi,
) -> str:
    """Independently rederive one still-live executable's sealed identity.

    The returned digest is computed from reverified compiler inputs and the
    generated/compiled artifacts; it is not copied from
    ``executable.executable_sha256``.  The process-local live registry must
    still carry that independently derived digest.  This gives protocol gates
    a non-self-comparison for checked-vs-actual executable identity without
    consuming the single-use capability.
    """

    if not isinstance(executable, VerifiedSphereExecutable):
        raise TypeError("live VerifiedSphereExecutable is required")
    fresh = _fresh(authority, plan, abi)
    expected_wrapper = generate_trusted_optix_sphere_wrapper_v1(
        fresh, plan, abi)
    if executable.wrapper != expected_wrapper:
        raise RuntimeError("trusted wrapper identity drift")
    expected_generated = tuple(
        generate_formal_sphere_numba_leaf(fresh, abi, role)
        for role in (
            CallbackRole.MAKE_RAY, CallbackRole.CLOSEST_HIT,
            CallbackRole.MISS, CallbackRole.FINALIZE,
        )
    )
    if executable.generated_leaves != expected_generated:
        raise RuntimeError("generated leaf identity drift")
    symbols = {item.role: item.abi_name for item in executable.compiled_leaves}
    recomposed = compose_callback_ptx(
        executable.wrapper_ptx,
        executable.compiled_leaves,
        exact_symbols_by_role=symbols,
    )
    if recomposed != executable.composed:
        raise RuntimeError("composed sphere PTX identity drift")
    wrapper_ptx_sha = hashlib.sha256(
        executable.wrapper_ptx.encode("utf-8")).hexdigest()
    if wrapper_ptx_sha != executable.wrapper_ptx_sha256 \
            or executable.wrapper_ptx_sha256 != executable.composed.wrapper_ptx_sha256:
        raise RuntimeError("sphere wrapper PTX identity drift")
    record = {
        "schema": "rtdl.v4.verified_sphere_executable.v1",
        "authority_sha256": _authority_sha256(fresh),
        "plan_sha256": plan.plan_sha256,
        "abi_sha256": abi.abi_sha256,
        "wrapper_source_sha256": expected_wrapper.source_sha256,
        "wrapper_ptx_sha256": recomposed.wrapper_ptx_sha256,
        "generated_leaf_sha256": [
            item.generated_source_sha256 for item in expected_generated],
        "compiled_leaf_sha256": [
            item.ptx_sha256 for item in executable.compiled_leaves],
        "composed_ptx_sha256": recomposed.ptx_sha256,
        "compiler_options": executable.compiler_options,
        "nvrtc_log_sha256": executable.nvrtc_log_sha256,
    }
    derived = _digest(record)
    if _LIVE_EXECUTABLES.get(id(executable)) != derived:
        raise RuntimeError("sphere executable live-registry identity drift")
    return derived


__all__ = [
    "VerifiedSphereExecutable",
    "compile_verified_sphere_executable",
    "consume_verified_sphere_executable",
    "rederive_verified_sphere_executable_sha256",
]
