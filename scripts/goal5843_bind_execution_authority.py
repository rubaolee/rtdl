#!/usr/bin/env python3
"""Bind Goal5843 to one exact clean NVIDIA execution environment."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

from experiments.goal5843_post_r1_baseline.contracts import (
    CACHE_PREPARATION_SCHEMA,
    EXECUTION_AUTHORITY_SCHEMA,
    ORACLE_WITNESS_SCHEMA,
    digest,
    load_preregistration,
    sha256_file,
)
from experiments.goal5843_post_r1_baseline.runtime import (
    command_output,
    create_json,
    git_head,
    git_status_short,
    verify_seal,
)


ROOT = Path(__file__).resolve().parents[1]
PYOPTIX_REPOSITORY_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"


def architecture_generation(capability: str) -> str:
    mapping = {
        "7.5": "TURING",
        "8.0": "AMPERE",
        "8.6": "AMPERE",
        "8.7": "AMPERE",
        "8.9": "ADA",
        "9.0": "HOPPER",
        "10.0": "BLACKWELL",
        "12.0": "BLACKWELL",
    }
    if capability not in mapping:
        raise RuntimeError(f"unregistered compute capability: {capability}")
    return mapping[capability]


def module_tree_identity(module: object) -> dict[str, object]:
    module_file = Path(str(getattr(module, "__file__", ""))).resolve(strict=True)
    root = module_file.parent
    rows = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    if not rows:
        raise RuntimeError("loaded PyOptiX module tree is empty")
    return {
        "root": str(root),
        "file_count": len(rows),
        "files": rows,
        "tree_sha256": digest(rows),
    }


def module_file_identity(module: object) -> dict[str, object]:
    path = Path(str(getattr(module, "__file__", ""))).resolve(strict=True)
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def gpu_row() -> dict[str, str]:
    rows = command_output(
        [
            "nvidia-smi",
            "--query-gpu=name,uuid,driver_version,compute_cap,memory.total",
            "--format=csv,noheader,nounits",
        ]
    ).splitlines()
    if len(rows) != 1:
        raise RuntimeError("exactly one visible GPU is required")
    model, uuid, driver, capability, memory_mib = (
        part.strip() for part in rows[0].split(",")
    )
    return {
        "gpu_model": model,
        "gpu_uuid": uuid,
        "driver_version": driver,
        "compute_capability": capability,
        "architecture_generation": architecture_generation(capability),
        "vram_bytes": str(int(memory_mib) * 1024 * 1024),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--native-build-manifest", type=Path, required=True)
    parser.add_argument("--direct-binary", type=Path, required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--cache-manifest", type=Path, required=True)
    parser.add_argument("--cache-preparation", type=Path, required=True)
    parser.add_argument("--oracle-witness", type=Path, required=True)
    parser.add_argument("--pyoptix-distribution", default="pyoptix")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--owner-authorized", action="store_true")
    args = parser.parse_args()
    if not args.owner_authorized:
        raise RuntimeError("explicit --owner-authorized flag required")
    prereg_path = args.preregistration.resolve()
    prereg = load_preregistration(prereg_path, ROOT, verify_files=True)
    if git_status_short(ROOT):
        raise RuntimeError("execution authority requires a clean repository")
    compute_pids = command_output(
        [
            "nvidia-smi",
            "--query-compute-apps=pid",
            "--format=csv,noheader,nounits",
        ]
    )
    if compute_pids and "No running" not in compute_pids:
        raise RuntimeError(f"foreign GPU compute process present: {compute_pids}")
    native = args.native.resolve(strict=True)
    build_manifest = args.native_build_manifest.resolve(strict=True)
    direct_binary = args.direct_binary.resolve(strict=True)
    device_source = args.device_source.resolve(strict=True)
    optix = args.optix_include.resolve(strict=True)
    cuda = args.cuda_include.resolve(strict=True)
    cache_root = args.cache_root.resolve(strict=True)
    cache_manifest = args.cache_manifest.resolve(strict=True)
    cache_preparation_path = args.cache_preparation.resolve(strict=True)
    oracle_witness_path = args.oracle_witness.resolve(strict=True)
    cache_preparation = json.loads(cache_preparation_path.read_text(encoding="utf-8"))
    verify_seal(cache_preparation, "preparation_sha256", "cache preparation")
    if (
        cache_preparation.get("schema") != CACHE_PREPARATION_SCHEMA
        or cache_preparation.get("source_commit") != git_head(ROOT)
        or cache_preparation.get("preregistration_sha256")
        != prereg["preregistration_sha256"]
        or Path(cache_preparation.get("cache_root", "")).resolve() != cache_root
        or Path(cache_preparation.get("manifest", "")).resolve() != cache_manifest
        or cache_preparation.get("manifest_file_sha256") != sha256_file(cache_manifest)
        or cache_preparation.get("native_library_sha256") != sha256_file(native)
        or cache_preparation.get("gpu_complete_execution_count") != 0
        or cache_preparation.get(
            "goal5843_registered_estimand_timing_observation_count"
        )
        != 0
    ):
        raise RuntimeError("formal cache preparation binding mismatch")
    hardware = gpu_row()
    if hardware["compute_capability"] != cache_preparation["compute_capability"]:
        raise RuntimeError("cache preparation compute capability mismatch")
    oracle_witness = json.loads(oracle_witness_path.read_text(encoding="utf-8"))
    verify_seal(oracle_witness, "witness_sha256", "independent oracle witness")
    if (
        oracle_witness.get("schema") != ORACLE_WITNESS_SCHEMA
        or oracle_witness.get("source_commit") != git_head(ROOT)
        or oracle_witness.get("preregistration_sha256")
        != prereg["preregistration_sha256"]
        or oracle_witness.get("implementation_route_import_count") != 0
        or oracle_witness.get("registered_timing_observation_count") != 0
    ):
        raise RuntimeError("independent oracle witness binding mismatch")
    from experiments.goal5796_matched import pyoptix_baseline

    api_version = ".".join(str(part) for part in pyoptix_baseline.optix.version())
    if api_version != args.optix_sdk:
        raise RuntimeError("loaded PyOptiX API differs from selected OptiX SDK")
    if pyoptix_baseline.PYOPTIX_COMMIT != PYOPTIX_REPOSITORY_COMMIT:
        raise RuntimeError("pinned PyOptiX repository commit drift")
    manifest = json.loads(cache_manifest.read_text(encoding="utf-8"))
    authority: dict[str, object] = {
        "schema": EXECUTION_AUTHORITY_SCHEMA,
        "status": "AUTHORIZED_FOR_GOAL5843_FORMAL_WORKER_ZERO",
        "owner_authorized_goal5843_execution": True,
        "source_commit": git_head(ROOT),
        "repository_status_short": [],
        "preregistration_sha256": prereg["preregistration_sha256"],
        "preregistration_file_sha256": sha256_file(prereg_path),
        "hardware": hardware,
        "host": {
            "hostname": platform.node(),
            "kernel": platform.release(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "numpy": importlib.metadata.version("numpy"),
            "numba": importlib.metadata.version("numba"),
            "cupy": pyoptix_baseline.cp.__version__,
        },
        "toolchain": {
            "optix_sdk": args.optix_sdk,
            "optix_h_sha256": sha256_file(optix / "optix.h"),
            "cuda_h_sha256": sha256_file(cuda / "cuda.h"),
            "nvcc_version": command_output(["nvcc", "--version"]),
        },
        "pyoptix": {
            "distribution_name": args.pyoptix_distribution,
            "distribution_version": importlib.metadata.version(
                args.pyoptix_distribution
            ),
            "repository_commit": PYOPTIX_REPOSITORY_COMMIT,
            "optix_api_version": api_version,
            "module_tree": module_tree_identity(pyoptix_baseline.optix),
            "cupy_module_file": module_file_identity(pyoptix_baseline.cp),
        },
        "execution_paths": {
            "native_library": str(native),
            "native_library_sha256": sha256_file(native),
            "native_build_manifest": str(build_manifest),
            "native_build_manifest_sha256": sha256_file(build_manifest),
            "direct_binary": str(direct_binary),
            "direct_binary_sha256": sha256_file(direct_binary),
            "device_source": str(device_source),
            "device_source_sha256": sha256_file(device_source),
            "optix_include": str(optix),
            "optix_h_sha256": sha256_file(optix / "optix.h"),
            "cuda_include": str(cuda),
            "cuda_h_sha256": sha256_file(cuda / "cuda.h"),
        },
        "formal_leaf_cache": {
            "root": str(cache_root),
            "manifest": str(cache_manifest),
            "manifest_file_sha256": sha256_file(cache_manifest),
            "entry_count": manifest["entry_count"],
            "entries_sha256": manifest["entries_sha256"],
            "preparation_receipt": str(cache_preparation_path),
            "preparation_receipt_file_sha256": sha256_file(cache_preparation_path),
            "preparation_sha256": cache_preparation["preparation_sha256"],
            "worker_policy": "EXPLICIT_SEALED_READ_ONLY",
        },
        "independent_oracle_witness": {
            "path": str(oracle_witness_path),
            "file_sha256": sha256_file(oracle_witness_path),
            "witness_sha256": oracle_witness["witness_sha256"],
            "tasks": oracle_witness["tasks"],
        },
        "environment": {
            "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "foreign_compute_process_count_before_binding": 0,
        },
        "registered_timing_observation_count": 0,
        "gpu_complete_execution_count": 0,
    }
    authority["authority_sha256"] = digest(authority)
    create_json(args.output, authority)
    print(json.dumps(authority, sort_keys=True))


if __name__ == "__main__":
    main()
