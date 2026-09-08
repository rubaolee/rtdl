#!/usr/bin/env python3
"""Build, sign, load, and native-prepare the Graph triangle family artifact."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

from rtdsl.v4 import (
    AnyHitProtocolProof,
    TriangleReductionMode,
    TriangleReductionProtocol,
    V4Target,
    V4Toolchain,
    standard_protocol_physical_plan,
)
from rtdsl.v4_family_route_adapters import triangle_reduction_family_route
from rtdsl.v4_rtdlexe import (
    RTDLExecutableBuildRoots,
    build_family_rtdlexe,
    install_rtdlexe_deployment,
    load_rtdlexe,
)
from scripts.goal5801_rtdlexe_trust import create_root, freeze


SCHEMA = "rtdl.v4_long_workload.triangle_rtdlexe_build.v1"
PROOF_KIND = "external_machine_checked_order_independence_v1"
APP = Path("Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py")
BENCHMARK = Path(
    "examples/current/research_benchmarks/triangle_counting/"
    "rtdl_triangle_counting_benchmark_app.py"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=root, check=True, text=True,
        capture_output=True,
    ).stdout.strip()


def _write_create(path: Path, value: object) -> None:
    payload = json.dumps(
        value, indent=2, sort_keys=True, allow_nan=False,
    ).encode() + b"\n"
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
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--nvcc", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--deployment-id", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    return parser


def _graph_proof(protocol, source_root: Path) -> AnyHitProtocolProof:
    plan = standard_protocol_physical_plan(protocol)
    proof_sha256 = _digest({
        "kind": "triangle_counting_paper_mapping_order_independence_v1",
        "callback": plan.callback_ir_sha256,
        "app_source": _sha256(source_root / APP),
        "benchmark_source": _sha256(source_root / BENCHMARK),
        "paper_algorithms": ("RT-1A2", "RT-2A1"),
    })
    return AnyHitProtocolProof(
        callback_ir_sha256=plan.callback_ir_sha256,
        effect_digest=plan.effect_digest,
        proof_sha256=proof_sha256,
        proof_kind=PROOF_KIND,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    source_root = args.source_root.resolve(strict=True)
    execution_root = Path(__file__).resolve().parents[1]
    if source_root != execution_root:
        raise RuntimeError(
            "triangle builder source root differs from imported implementation")
    if _git(source_root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("triangle RTDL executable build requires a clean source tree")
    source_commit = _git(source_root, "rev-parse", "HEAD")
    source_tree = _git(source_root, "rev-parse", "HEAD^{tree}")
    native = args.native.resolve(strict=True)
    nvcc = args.nvcc.resolve(strict=True)
    optix_include = args.optix_include.resolve(strict=True)
    cuda_include = args.cuda_include.resolve(strict=True)
    output_root = args.output_root.resolve()
    if output_root.exists() or output_root.is_symlink():
        raise FileExistsError(output_root)
    output_root.mkdir(parents=True)
    major_text, minor_text = args.compute_capability.split(".", 1)
    compute_capability = (int(major_text), int(minor_text))
    native_sha256 = _sha256(native)
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)

    protocol = TriangleReductionProtocol(
        TriangleReductionMode.WEIGHTED_HIT_COUNT)
    proof = _graph_proof(protocol, source_root)
    target = V4Target.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=compute_capability,
    )
    toolchain = V4Toolchain.current(
        compute_capability=compute_capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
    )
    materialized = triangle_reduction_family_route(
        protocol, proof).compile().materialize(target=target, toolchain=toolchain)
    nvcc_version = subprocess.run(
        [str(nvcc), "--version"], check=True, text=True,
        capture_output=True,
    ).stdout.strip().splitlines()[-1]
    roots = RTDLExecutableBuildRoots(
        llvmlite_version=importlib.metadata.version("llvmlite"),
        cuda_toolkit_version=nvcc_version,
        link_options=("max_trace_depth=1", "debug=none"),
    )
    authority = output_root / "triangle.authority.json"
    built = build_family_rtdlexe(
        materialized,
        artifact_directory=output_root / "artifacts",
        authority_path=authority,
        build_roots=roots,
        deployment_id=args.deployment_id,
    )

    private_key = output_root / "TEST_ONLY_private.json"
    public_root = output_root / "TEST_ONLY_public.json"
    package = output_root / "package.json"
    head = output_root / "head.json"
    create_root(
        private_path=private_key,
        public_path=public_root,
        key_id="TEST_ONLY_v4_long_workload_triangle",
        bits=2048,
    )
    try:
        freeze(
            private_path=private_key,
            root_path=public_root,
            authority_path=authority,
            output_path=package,
            head_output_path=head,
            previous_path=None,
        )
    finally:
        private_key.unlink(missing_ok=True)
    if private_key.exists() or private_key.is_symlink():
        raise RuntimeError("triangle test-only private key survived artifact freeze")

    deployment = install_rtdlexe_deployment(
        trust_root_path=public_root,
        trust_head_path=head,
        trust_package_path=package,
        deployment_id=args.deployment_id,
    )
    loaded = load_rtdlexe(
        built.artifact_path,
        authority_path=authority,
        deployment=deployment,
    )
    executor = loaded.prepare_triangle_device_columns(
        native_library_path=native)
    try:
        if executor.composed_program_sha256 \
                != loaded.product_projection["composed_ptx_sha256"]:
            raise RuntimeError("triangle AOT device-program identity differs")
    finally:
        executor.close()

    formal_fragment = {
        "artifact_path": str(built.artifact_path),
        "authority_path": str(authority),
        "trust_root_path": str(public_root),
        "trust_head_path": str(head),
        "trust_package_path": str(package),
        "deployment_id": args.deployment_id,
        "expected_artifact_sha256": built.artifact_sha256,
        "expected_authority_sha256": built.authority_sha256,
        "expected_trust_root_sha256": _sha256(public_root),
        "expected_trust_head_sha256": _sha256(head),
        "expected_trust_package_sha256": _sha256(package),
        "expected_any_hit_proof_sha256": proof.proof_sha256,
        "expected_family_executable_identity_sha256": (
            built.family_executable_identity_sha256),
        "expected_native_sha256": native_sha256,
    }
    manifest = {
        "schema": SCHEMA,
        "status": "PASS__SIGNED_PUBLIC_LOAD_AND_DEVICE_PROGRAM_PREPARE_VERIFIED",
        "source": {
            "root": str(source_root),
            "commit": source_commit,
            "tree": source_tree,
            "builder_path": str(Path(__file__).resolve()),
            "builder_sha256": _sha256(Path(__file__).resolve()),
        },
        "protocol": {
            "family": protocol.family.value,
            "triangle_mode": protocol.mode.value,
            "proof_sha256": proof.proof_sha256,
            "proof_kind": proof.proof_kind,
            "app_source_sha256": _sha256(source_root / APP),
            "benchmark_source_sha256": _sha256(source_root / BENCHMARK),
            "app_specific_native_engine_logic": False,
        },
        "target": {
            "provider": "optix",
            "optix_sdk": args.optix_sdk,
            "compute_capability": args.compute_capability,
            "target_sha256": target.profile.target_sha256,
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
            "authority_path": str(authority),
            "authority_sha256": built.authority_sha256,
            "executable_identity_sha256": built.executable_identity_sha256,
            "family_executable_identity_sha256": (
                built.family_executable_identity_sha256),
            "compile_inside_measurement": False,
            "device_program_prepare_round_trip_verified": True,
            "test_only_private_key_deleted": True,
        },
        "formal_config_fragment": formal_fragment,
        "runtime": {
            "python_executable": sys.executable,
            "python_version": platform.python_version(),
            "numba_version": importlib.metadata.version("numba"),
            "numpy_version": importlib.metadata.version("numpy"),
            "llvmlite_version": importlib.metadata.version("llvmlite"),
        },
    }
    _write_create(args.manifest.resolve(), manifest)
    print(json.dumps({
        "status": manifest["status"],
        "manifest": str(args.manifest.resolve()),
        "artifact_sha256": built.artifact_sha256,
        "family_executable_identity_sha256": (
            built.family_executable_identity_sha256),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
