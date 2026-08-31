#!/usr/bin/env python3
"""Build and freeze the Goal5814 strict-interior Particle executable.

This is an untimed build/custody entry point.  It deliberately constructs the
accepted standard built-in-triangle protocol before lowering the fixed
strict-interior library specialization.  It performs no Particle prepare,
OptiX launch, scientific-data read, or registered measurement.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import platform
import sys

import numba
import numpy as np

from rtdsl import (
    build_particle_rtdlexe,
    install_particle_rtdlexe_deployment,
    load_particle_rtdlexe,
)
from rtdsl.v4_builtin_triangle_standard_library import (
    compile_standard_builtin_triangle_program,
)
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


AUTHOR_SOURCE_SEMANTICS_SHA256 = (
    "e67c909d6bea027dc882189aacce4b6f82fde8e6a28c41315b46037692d3b8b7"
)
INDEPENDENT_ORACLE_VERIFIER_SHA256 = (
    "7afc8971436987d29d6ce4d5078693528300f8e109e487c4658882b42d823767"
)
LOADER_ORACLE_BINDING_SHA256 = (
    "7351cc39534961f5c0626cbf6f6e6039305ca200307bca63decc06ce4f810c99"
)
CONTROLLING_POLICY_SHA256 = (
    "79f0d56f8765894666eaaec363f7e149c92de68e85d35ce43d3aa765132e625e"
)


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_file(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")


def _create_or_exact(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        if path.read_bytes() != payload:
            raise RuntimeError(f"create-only collision: {path}")
        return
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _load_controlling_policy(path: Path) -> tuple[dict[str, object], bytes]:
    raw = path.expanduser().resolve(strict=True).read_bytes()
    if _sha_bytes(raw) != CONTROLLING_POLICY_SHA256:
        raise RuntimeError("controlling Goal5814 policy identity mismatch")
    value = json.loads(raw)
    if (value.get("schema")
            != "rtdl.goal5814.particle_tracking_scientific_scope_and_measurement_policy_preaction.v1"
            or value.get("controlling_input", {}).get(
                "loader_oracle_binding_sha256")
                != LOADER_ORACLE_BINDING_SHA256):
        raise RuntimeError("controlling loader-oracle binding mismatch")
    return value, raw


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--nvcc", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--controlling-policy", type=Path, required=True)
    parser.add_argument("--compute-capability", default="6.1")
    parser.add_argument("--optix-sdk", default="9.0.0")
    parser.add_argument("--build-host", default="lx1")
    parser.add_argument(
        "--deployment-id",
        default="goal5814/lx1/particle-strict-interior/freeze-v1",
    )
    parser.add_argument("--build-directory", type=Path, required=True)
    parser.add_argument("--artifact-directory", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    return parser


def main() -> None:
    args = _argument_parser().parse_args()

    native = args.native.expanduser().resolve(strict=True)
    nvcc = args.nvcc.expanduser().resolve(strict=True)
    optix_include = args.optix_include.expanduser().resolve(strict=True)
    cuda_include = args.cuda_include.expanduser().resolve(strict=True)
    controlling_policy_path = args.controlling_policy.expanduser().resolve(
        strict=True)
    _controlling_policy, controlling_policy_bytes = _load_controlling_policy(
        controlling_policy_path)
    major_text, minor_text = args.compute_capability.split(".", 1)
    compute_capability = (int(major_text), int(minor_text))
    compute_arch = f"compute_{major_text}{minor_text}"
    native_sha256 = _sha_file(native)

    target = ReferenceTargetProfile(
        provider="optix",
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
        native_sha256=native_sha256,
        supports_custom_aabb=True,
        supports_builtin_triangle=True,
    )
    standard = compile_standard_builtin_triangle_program(
        target,
        source_semantics_sha256=AUTHOR_SOURCE_SEMANTICS_SHA256,
        independent_oracle_sha256=LOADER_ORACLE_BINDING_SHA256,
        compute_capability=compute_capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
        expected_python_version=platform.python_version(),
        expected_numba_version=numba.__version__,
        expected_numpy_version=np.__version__,
    )
    built = build_particle_rtdlexe(
        standard,
        native_library_path=native,
        nvcc_path=nvcc,
        optix_include=optix_include,
        compute_arch=compute_arch,
        build_directory=args.build_directory,
        artifact_directory=args.artifact_directory,
    )

    artifact_bytes = built.artifact_path.read_bytes()
    artifact = json.loads(artifact_bytes)
    ptx = base64.b64decode(artifact["ptx_base64"], validate=True)
    deployment = install_particle_rtdlexe_deployment(
        deployment_id=args.deployment_id,
        expected_artifact_sha256=built.artifact_sha256,
        expected_native_sha256=built.native_library_sha256,
        expected_protocol_decision_sha256=built.protocol_decision_sha256,
        expected_template_semantic_sha256=built.template_semantic_sha256,
    )
    loaded = load_particle_rtdlexe(
        built.artifact_path, deployment=deployment,
        native_library_path=native)
    try:
        if loaded.ptx_bytes != ptx:
            raise RuntimeError("public load roundtrip changed PTX bytes")
    finally:
        loaded.close()

    body = {
        "schema": "rtdl.goal5814.particle_strict_interior_executable_manifest.v1",
        "status": "PASS__EXACT_PUBLIC_ARTIFACT_BUILT_AND_LOAD_VERIFIED__NO_EXECUTE",
        "build_host": args.build_host,
        "build_only_no_registered_timing": True,
        "standard_protocol": {
            "producer": "compile_standard_builtin_triangle_program",
            "source_semantics_sha256": AUTHOR_SOURCE_SEMANTICS_SHA256,
            "independent_oracle_binding_sha256": (
                LOADER_ORACLE_BINDING_SHA256),
            "independent_oracle_verifier_source_sha256": (
                INDEPENDENT_ORACLE_VERIFIER_SHA256),
            "decision_sha256": built.protocol_decision_sha256,
            "verdict": artifact["standard_protocol"]["decision"]["verdict"],
            "findings": artifact["standard_protocol"]["decision"]["findings"],
        },
        "specialization_scope": {
            "name": "STRICT_INTERIOR_STANDARD_LIBRARY_SPECIALIZATION_ONLY",
            "arbitrary_user_dsl_generalization_claimed": False,
            "complete_particle_advection_claimed": False,
        },
        "controlling_policy": {
            "absolute_path": str(controlling_policy_path),
            "sha256": _sha_bytes(controlling_policy_bytes),
            "loader_oracle_binding_sha256": LOADER_ORACLE_BINDING_SHA256,
        },
        "identities": {
            "builder_source_absolute_path": str(Path(__file__).resolve()),
            "builder_source_sha256": _sha_file(Path(__file__).resolve()),
            "native_absolute_path": str(native),
            "native_sha256": built.native_library_sha256,
            "template_source_absolute_path": str(built.source_path),
            "template_source_sha256": artifact["source_sha256"],
            "descriptor_absolute_path": str(built.descriptor_path),
            "descriptor_sha256": artifact["descriptor_sha256"],
            "ptx_pass1_absolute_path": str(built.ptx_pass1_path),
            "ptx_pass2_absolute_path": str(built.ptx_pass2_path),
            "ptx_sha256": built.ptx_sha256,
            "ptx_bytes": len(ptx),
            "ptx_passes_byte_identical": (
                built.ptx_pass1_path.read_bytes()
                == built.ptx_pass2_path.read_bytes() == ptx),
            "artifact_absolute_path": str(built.artifact_path),
            "artifact_sha256": built.artifact_sha256,
            "artifact_bytes": built.artifact_bytes,
            "template_semantic_sha256": built.template_semantic_sha256,
            "specialization_binding_sha256": (
                artifact["specialization_binding"]["binding_sha256"]),
        },
        "tool_identity": {
            "python_executable": sys.executable,
            "python_version": platform.python_version(),
            "numba_version": numba.__version__,
            "numpy_version": np.__version__,
            "nvcc_absolute_path": str(built.nvcc_absolute_path),
            "nvcc_executable_sha256": built.nvcc_executable_sha256,
            "optix_include_absolute_path": str(
                built.optix_include_absolute_path),
            "optix_device_header_sha256": (
                built.optix_device_header_sha256),
            "compute_arch": compute_arch,
        },
        "runtime_boundary": {
            "build_self_consistency_public_load_roundtrip_passed": True,
            "external_manifest_authority_kat_passed": False,
            "installer_authenticates_provenance_by_itself": False,
            "runtime_product_abi_symbol_count": 6,
            "runtime_product_abi_symbols": [
                "rtdl_optix_v4_particle_strict_interior_source_v1",
                "rtdl_optix_v4_particle_strict_interior_descriptor_v1",
                "rtdl_optix_v4_prepare_particle_strict_interior_v1",
                "rtdl_optix_v4_execute_prepared_particle_strict_interior_v2",
                "rtdl_optix_v4_execute_prepared_particle_strict_interior_prevalidated_v3",
                "rtdl_optix_v4_destroy_prepared_particle_strict_interior_v1",
            ],
            "compiler_numba_or_nvrtc_imported_on_cache_hit": False,
            "real_prepare_or_execute_attempted": False,
            "formal_worker_zero_authorized": False,
            "performance_claimed": False,
        },
        "build_argv": sys.argv,
    }
    manifest = {**body, "manifest_body_sha256": _sha_bytes(_canonical(body))}
    manifest_bytes = json.dumps(
        manifest, indent=2, sort_keys=True, ensure_ascii=False,
        allow_nan=False).encode("utf-8") + b"\n"
    _create_or_exact(args.manifest.expanduser().resolve(), manifest_bytes)
    print(json.dumps({
        "artifact_path": str(built.artifact_path),
        "artifact_sha256": built.artifact_sha256,
        "native_sha256": built.native_library_sha256,
        "ptx_sha256": built.ptx_sha256,
        "manifest_path": str(args.manifest.expanduser().resolve()),
        "manifest_file_sha256": _sha_bytes(manifest_bytes),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
