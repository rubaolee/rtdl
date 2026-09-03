#!/usr/bin/env python3
"""Bind Goal5842's frozen experiment to one exact clean NVIDIA host."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

from experiments.goal5842_causal_admission.contracts import (
    EXECUTION_AUTHORITY_SCHEMA,
    digest,
    load_preregistration,
    sha256_file,
)
from experiments.goal5842_causal_admission.runtime import (
    create_json,
    git_head,
    git_status_short,
)

ROOT = Path(__file__).resolve().parents[1]
PYOPTIX_REPOSITORY_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"


def architecture_generation(compute_capability: str) -> str:
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
    try:
        return mapping[compute_capability]
    except KeyError as exc:
        raise RuntimeError(
            f"unregistered compute capability {compute_capability}; add a "
            "pre-timing architecture classification rather than guessing"
        ) from exc


def command_output(command: list[str]) -> str:
    return subprocess.run(
        command, check=True, text=True, capture_output=True
    ).stdout.strip()


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
        raise RuntimeError(f"loaded module tree is empty: {root}")
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
        raise RuntimeError(f"exactly one visible GPU required, observed {len(rows)}")
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
    parser.add_argument("--pyoptix-distribution", default="pyoptix")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--owner-authorized", action="store_true")
    args = parser.parse_args()
    if not args.owner_authorized:
        raise RuntimeError("explicit --owner-authorized flag required")
    prereg_path = args.preregistration.resolve()
    prereg = load_preregistration(prereg_path, ROOT, verify_files=True)
    dirty = git_status_short(ROOT)
    if dirty:
        raise RuntimeError(f"execution authority requires clean repository: {dirty!r}")
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
    hardware = gpu_row()
    from experiments.goal5796_matched import pyoptix_baseline

    optix_api_version = ".".join(str(part) for part in pyoptix_baseline.optix.version())
    if optix_api_version != args.optix_sdk:
        raise RuntimeError(
            f"loaded PyOptiX API {optix_api_version} differs from requested "
            f"OptiX SDK {args.optix_sdk}"
        )
    if pyoptix_baseline.PYOPTIX_COMMIT != PYOPTIX_REPOSITORY_COMMIT:
        raise RuntimeError("pinned PyOptiX repository commit constant drift")
    pyoptix_distribution_version = importlib.metadata.version(args.pyoptix_distribution)
    pyoptix_tree = module_tree_identity(pyoptix_baseline.optix)
    cupy_file = module_file_identity(pyoptix_baseline.cp)
    authority: dict[str, object] = {
        "schema": EXECUTION_AUTHORITY_SCHEMA,
        "status": "AUTHORIZED_FOR_FORMAL_WORKER_ZERO",
        "owner_authorized_goal5842_execution": True,
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
            "distribution_version": pyoptix_distribution_version,
            "repository_commit": PYOPTIX_REPOSITORY_COMMIT,
            "optix_api_version": optix_api_version,
            "module_tree": pyoptix_tree,
            "cupy_module_file": cupy_file,
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
        "environment": {
            "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "foreign_compute_process_count": 0,
        },
        "registered_timing_observation_count": 0,
        "gpu_execution_count": 0,
    }
    authority["authority_sha256"] = digest(authority)
    create_json(args.output, authority)
    print(json.dumps(authority, sort_keys=True))


if __name__ == "__main__":
    main()
