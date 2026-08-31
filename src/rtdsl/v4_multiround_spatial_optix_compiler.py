"""Trusted compiler for prepared multi-round V4 spatial composition."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

from .v4_bounded_relation_optix_compiler import (
    generate_bounded_relation_numba_leaf,
)
from .v4_callback_ir import CallbackRole
from .v4_callback_optix_wrapper_codegen import GeneratedOptixWrapper
from .v4_callback_poc import DeviceFunctionArtifact
from .v4_callback_ptx_composer import ComposedCallbackPtx, compose_callback_ptx
from .v4_multiround_spatial import (
    VerifiedMultiRoundSpatialAuthority,
    verify_multiround_spatial_schema,
)
from .v4_multiround_spatial_optix_wrapper_codegen import (
    generate_trusted_multiround_spatial_wrapper_v1,
)
from .v4_triangle_optix_compiler import _compile_nvrtc
from .v4_callback_numba_codegen import compile_formal_numba_leaf_isolated


@dataclass(frozen=True, eq=False)
class VerifiedMultiRoundSpatialExecutable:
    schema: str
    authority_sha256: str
    wrapper: GeneratedOptixWrapper
    wrapper_ptx: str
    wrapper_ptx_sha256: str
    generated_leaf_sha256: tuple[str, ...]
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


def _fresh(authority, *, any_hit_proof_authority):
    fresh = verify_multiround_spatial_schema(
        authority.relation,
        authority.relation_contract,
        authority.abi,
        authority.schema,
        any_hit_proof_authority=any_hit_proof_authority,
    )
    if fresh != authority:
        raise RuntimeError("multi-round spatial authority did not rederive")
    return fresh


def compile_verified_multiround_spatial_executable(
    authority: VerifiedMultiRoundSpatialAuthority,
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
) -> tuple[VerifiedMultiRoundSpatialExecutable, str]:
    fresh = _fresh(authority, any_hit_proof_authority=any_hit_proof_authority)
    expected_cc = tuple(int(item) for item in
                        fresh.relation.physical.target.compute_capability.split("."))
    if tuple(compute_capability) != expected_cc:
        raise RuntimeError("target compute capability does not match authority")
    generated = []
    compiled = []
    symbols: dict[str, str] = {}
    for role in CallbackRole:
        leaf = generate_bounded_relation_numba_leaf(
            fresh.relation,
            fresh.abi,
            role,
            any_hit_proof_authority=any_hit_proof_authority,
        )
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
    wrapper = generate_trusted_multiround_spatial_wrapper_v1(
        fresh.relation,
        fresh.relation_contract,
        fresh.abi,
        any_hit_proof_authority=any_hit_proof_authority,
    )
    options = (
        f"-I{Path(optix_include).resolve()}",
        f"-I{Path(cuda_include).resolve()}",
        "-I/usr/include", "-I/usr/include/x86_64-linux-gnu",
        "--std=c++14",
        f"--gpu-architecture=compute_{compute_capability[0]}{compute_capability[1]}",
        "--relocatable-device-code=true", "-D__x86_64__=1", "-D__LP64__=1",
    )
    wrapper_ptx, log = _compile_nvrtc(wrapper.source, options)
    composed = compose_callback_ptx(
        wrapper_ptx, compiled, exact_symbols_by_role=symbols)
    authority_sha = _digest({
        "nonce": fresh.authority_nonce,
        "schema": fresh.schema.schema_sha256,
        "relation": fresh.relation.authority_nonce,
        "contract": fresh.relation_contract.contract_sha256,
        "abi": fresh.abi.abi_sha256,
    })
    record = {
        "schema": "rtdl.v4.verified_multiround_spatial_executable.v1",
        "authority": authority_sha,
        "wrapper_source": wrapper.source_sha256,
        "wrapper_ptx": composed.wrapper_ptx_sha256,
        "generated": [item.generated_source_sha256 for item in generated],
        "compiled": [item.ptx_sha256 for item in compiled],
        "composed": composed.ptx_sha256,
        "options": options,
        "nvrtc_log": hashlib.sha256(log.encode()).hexdigest(),
    }
    executable = VerifiedMultiRoundSpatialExecutable(
        schema=record["schema"],
        authority_sha256=authority_sha,
        wrapper=wrapper,
        wrapper_ptx=wrapper_ptx,
        wrapper_ptx_sha256=composed.wrapper_ptx_sha256,
        generated_leaf_sha256=tuple(record["generated"]),
        compiled_leaves=tuple(compiled),
        composed=composed,
        compiler_options=options,
        nvrtc_log_sha256=record["nvrtc_log"],
        executable_sha256=_digest(record),
    )
    _LIVE_EXECUTABLES[id(executable)] = executable.executable_sha256
    return executable, log


def consume_verified_multiround_spatial_executable(
    executable: VerifiedMultiRoundSpatialExecutable,
    authority: VerifiedMultiRoundSpatialAuthority,
    *,
    any_hit_proof_authority,
) -> str:
    if not isinstance(executable, VerifiedMultiRoundSpatialExecutable):
        raise TypeError("live VerifiedMultiRoundSpatialExecutable is required")
    if _LIVE_EXECUTABLES.get(id(executable)) != executable.executable_sha256:
        raise RuntimeError("multi-round spatial executable is forged, serialized, or consumed")
    fresh = _fresh(authority, any_hit_proof_authority=any_hit_proof_authority)
    wrapper = generate_trusted_multiround_spatial_wrapper_v1(
        fresh.relation,
        fresh.relation_contract,
        fresh.abi,
        any_hit_proof_authority=any_hit_proof_authority,
    )
    authority_sha = _digest({
        "nonce": fresh.authority_nonce,
        "schema": fresh.schema.schema_sha256,
        "relation": fresh.relation.authority_nonce,
        "contract": fresh.relation_contract.contract_sha256,
        "abi": fresh.abi.abi_sha256,
    })
    if executable.wrapper != wrapper or executable.authority_sha256 != authority_sha:
        raise RuntimeError("multi-round spatial executable binding drift")
    symbols = {item.role: item.abi_name for item in executable.compiled_leaves}
    recomposed = compose_callback_ptx(
        executable.wrapper_ptx,
        executable.compiled_leaves,
        exact_symbols_by_role=symbols,
    )
    if recomposed != executable.composed \
            or hashlib.sha256(executable.wrapper_ptx.encode()).hexdigest() \
            != executable.wrapper_ptx_sha256:
        raise RuntimeError("multi-round spatial composed PTX identity drift")
    del _LIVE_EXECUTABLES[id(executable)]
    return executable.composed.ptx


__all__ = [
    "VerifiedMultiRoundSpatialExecutable",
    "compile_verified_multiround_spatial_executable",
    "consume_verified_multiround_spatial_executable",
]
