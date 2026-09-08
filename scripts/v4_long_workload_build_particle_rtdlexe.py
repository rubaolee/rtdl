#!/usr/bin/env python3
"""Build and verify the Particle AOT product for a successor transaction."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

import numba
import numpy as np

from experiments.v4_paper_apps_pyoptix.inputs import load_particle
from rtdsl.v4_builtin_triangle_standard_library import (
    compile_standard_builtin_triangle_program,
)
from rtdsl.v4_particle_rtdlexe import (
    build_particle_rtdlexe,
    install_particle_rtdlexe_deployment,
    load_particle_rtdlexe,
)
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


AUTHOR_SOURCE_SEMANTICS_SHA256 = (
    "e67c909d6bea027dc882189aacce4b6f82fde8e6a28c41315b46037692d3b8b7"
)
SCHEMA = "rtdl.v4_long_workload.particle_rtdlexe_build.v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=root, check=True, text=True,
        capture_output=True,
    ).stdout.strip()


def _write_create(path: Path, value: object) -> None:
    payload = json.dumps(
        value, indent=2, sort_keys=True, allow_nan=False,
    ).encode("utf-8") + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--nvcc", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--deployment-id", required=True)
    parser.add_argument("--build-directory", type=Path, required=True)
    parser.add_argument("--artifact-directory", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    source_root = args.source_root.resolve(strict=True)
    if _git(source_root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("Particle RTDL executable build requires a clean source tree")
    source_commit = _git(source_root, "rev-parse", "HEAD")
    source_tree = _git(source_root, "rev-parse", "HEAD^{tree}")
    native = args.native.resolve(strict=True)
    nvcc = args.nvcc.resolve(strict=True)
    optix_include = args.optix_include.resolve(strict=True)
    cuda_include = args.cuda_include.resolve(strict=True)
    data_root = args.data_root.resolve(strict=True)
    major_text, minor_text = args.compute_capability.split(".", 1)
    compute_capability = (int(major_text), int(minor_text))
    native_sha256 = _sha256(native)
    data = load_particle(data_root)

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
        independent_oracle_sha256=data["independent_oracle_sha256"],
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
        compute_arch=f"compute_{major_text}{minor_text}",
        build_directory=args.build_directory.resolve(),
        artifact_directory=args.artifact_directory.resolve(),
    )
    artifact = json.loads(built.artifact_path.read_text(encoding="utf-8"))
    ptx = base64.b64decode(artifact["ptx_base64"], validate=True)
    deployment = install_particle_rtdlexe_deployment(
        deployment_id=args.deployment_id,
        expected_artifact_sha256=built.artifact_sha256,
        expected_native_sha256=built.native_library_sha256,
        expected_protocol_decision_sha256=built.protocol_decision_sha256,
        expected_template_semantic_sha256=built.template_semantic_sha256,
    )
    loaded = load_particle_rtdlexe(
        built.artifact_path,
        deployment=deployment,
        native_library_path=native,
    )
    try:
        if loaded.ptx_bytes != ptx or loaded.ptx_sha256 != built.ptx_sha256:
            raise RuntimeError("Particle public artifact load round-trip differs")
    finally:
        loaded.close()

    manifest = {
        "schema": SCHEMA,
        "status": "PASS__BUILT_AND_PUBLIC_LOAD_VERIFIED__NO_EXECUTE",
        "source": {
            "root": str(source_root),
            "commit": source_commit,
            "tree": source_tree,
            "builder_path": str(Path(__file__).resolve()),
            "builder_sha256": _sha256(Path(__file__).resolve()),
        },
        "input": {
            "data_root": str(data_root),
            "input_sha256": data["input_sha256"],
            "independent_oracle_sha256": data["independent_oracle_sha256"],
            "route_independent_expected": data["route_independent_expected"],
        },
        "target": {
            "provider": "optix",
            "optix_sdk": args.optix_sdk,
            "compute_capability": args.compute_capability,
            "target_sha256": target.target_sha256,
            "native_path": str(native),
            "native_sha256": native_sha256,
            "nvcc_path": str(nvcc),
            "nvcc_sha256": _sha256(nvcc),
            "optix_include": str(optix_include),
            "cuda_include": str(cuda_include),
        },
        "product": {
            "artifact_path": str(built.artifact_path),
            "artifact_sha256": built.artifact_sha256,
            "artifact_bytes": built.artifact_bytes,
            "ptx_sha256": built.ptx_sha256,
            "ptx_bytes": len(ptx),
            "protocol_decision_sha256": built.protocol_decision_sha256,
            "template_semantic_sha256": built.template_semantic_sha256,
            "specialization_scope": (
                "STRICT_INTERIOR_STANDARD_LIBRARY_SPECIALIZATION_ONLY"
            ),
            "arbitrary_user_dsl_generalization_claimed": False,
            "compile_inside_measurement": False,
        },
        "formal_config_fragment": {
            "artifact_path": str(built.artifact_path),
            "deployment_id": args.deployment_id,
            "expected_artifact_sha256": built.artifact_sha256,
            "expected_native_sha256": built.native_library_sha256,
            "expected_protocol_decision_sha256": built.protocol_decision_sha256,
            "expected_template_semantic_sha256": built.template_semantic_sha256,
            "expected_input_sha256": data["input_sha256"],
            "expected_independent_oracle_sha256": (
                data["independent_oracle_sha256"]
            ),
            "expected_orientation_authority_sha256": artifact[
                "standard_protocol"
            ]["orientation_authority_sha256"],
        },
        "runtime": {
            "python_executable": sys.executable,
            "python_version": platform.python_version(),
            "numba_version": numba.__version__,
            "numpy_version": np.__version__,
        },
    }
    _write_create(args.manifest.resolve(), manifest)
    print(json.dumps({
        "status": manifest["status"],
        "manifest": str(args.manifest.resolve()),
        "artifact_sha256": built.artifact_sha256,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
