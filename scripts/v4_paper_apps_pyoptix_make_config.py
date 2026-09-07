#!/usr/bin/env python3
"""Create one identity-bound config for V4/PyOptiX dry run and formal use."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root must be an object: {path}")
    return value


def _compute_capability(text: str) -> tuple[int, int]:
    parts = text.split(".")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        raise ValueError("compute capability must be MAJOR.MINOR")
    major, minor = (int(part) for part in parts)
    if not (1 <= major <= 99 and 0 <= minor <= 9):
        raise ValueError("compute capability is outside the accepted range")
    return major, minor


def _registered_machine(compute_capability: tuple[int, int]) -> dict[str, Any]:
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not visible or "," in visible:
        raise RuntimeError("config requires exactly one CUDA_VISIBLE_DEVICES selector")
    completed = subprocess.run(
        [
            "nvidia-smi",
            "-i",
            visible,
            "--query-gpu=name,uuid,compute_cap,driver_version",
            "--format=csv,noheader,nounits",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    rows = [row.strip() for row in completed.stdout.splitlines() if row.strip()]
    if len(rows) != 1:
        raise RuntimeError("config requires exactly one registered GPU")
    fields = [field.strip() for field in rows[0].split(",")]
    if len(fields) != 4:
        raise RuntimeError("registered nvidia-smi row is malformed")
    gpu = dict(zip(("name", "uuid", "compute_capability", "driver"), fields))
    expected_cc = f"{compute_capability[0]}.{compute_capability[1]}"
    if gpu["compute_capability"] != expected_cc:
        raise RuntimeError("registered GPU compute capability differs from argument")
    return {
        "gpu": gpu,
        "cuda_visible_devices": visible,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--data-manifest", type=Path, required=True)
    parser.add_argument("--native-library", type=Path, required=True)
    parser.add_argument("--native-build-manifest", type=Path, required=True)
    parser.add_argument("--pyoptix-build-receipt", type=Path, required=True)
    parser.add_argument("--pyoptix-ptx-manifest", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    source = args.source_root.resolve(strict=True)
    if source != ROOT.resolve(strict=True):
        raise PermissionError("source-root must be this experiment-script checkout")
    data = args.data_root.resolve(strict=True)
    data_manifest = args.data_manifest.resolve(strict=True)
    native = args.native_library.resolve(strict=True)
    native_manifest_path = args.native_build_manifest.resolve(strict=True)
    pyoptix_receipt_path = args.pyoptix_build_receipt.resolve(strict=True)
    pyoptix_ptx_manifest_path = args.pyoptix_ptx_manifest.resolve(strict=True)
    optix = args.optix_include.resolve(strict=True)
    cuda = args.cuda_include.resolve(strict=True)
    if not (optix / "optix.h").is_file() or not (optix / "optix_device.h").is_file():
        raise FileNotFoundError("OptiX include directory lacks required headers")
    if not (cuda / "cuda.h").is_file():
        raise FileNotFoundError("CUDA include directory lacks cuda.h")
    cc = _compute_capability(args.compute_capability)
    machine = _registered_machine(cc)
    dirty = _git(source, "status", "--porcelain")
    if dirty:
        raise PermissionError("experiment config requires a clean source checkout")
    commit = _git(source, "rev-parse", "HEAD")
    tree = _git(source, "rev-parse", "HEAD^{tree}")
    native_manifest = _read_object(native_manifest_path)
    if (
        native_manifest.get("git_commit") != commit
        or native_manifest.get("git_commit_after_build") != commit
        or native_manifest.get("native_sha256") != _sha(native)
        or native_manifest.get("status", "").find("PASS") != 0
        or tuple(native_manifest.get("build_input", {}).get("compute_capability", ()))
        != cc
        or native_manifest.get("build_input", {}).get("expected_optix_sdk")
        != args.optix_sdk
    ):
        raise RuntimeError("native build manifest differs from selected source/runtime")
    pyoptix_receipt = _read_object(pyoptix_receipt_path)
    installed = pyoptix_receipt.get("installed", {})
    extension = (
        installed.get("loaded_extension", {}) if isinstance(installed, dict) else {}
    )
    if (
        pyoptix_receipt.get("status", "").find("PASS") != 0
        or not isinstance(installed, dict)
        or installed.get("optix_api_version") != args.optix_sdk
        or not isinstance(extension, dict)
        or not isinstance(extension.get("sha256"), str)
    ):
        raise RuntimeError("PyOptiX build receipt differs from selected OptiX API")
    package_names = (
        "cuda-bindings",
        "cuda-python",
        "cupy-cuda12x",
        "numba",
        "numpy",
        "pyoptix",
    )
    package_versions = {
        name: importlib.metadata.version(name) for name in package_names
    }
    receipt_versions = installed.get("installed_distributions")
    if not isinstance(receipt_versions, dict) or any(
        receipt_versions.get(name) != version
        for name, version in package_versions.items()
    ):
        raise RuntimeError("current package versions differ from PyOptiX build receipt")
    pyoptix_ptx_manifest = _read_object(pyoptix_ptx_manifest_path)
    ptx_programs = pyoptix_ptx_manifest.get("programs")
    expected_programs = {
        "particle_tracking": "experiments/v4_paper_apps_pyoptix/particle_device.cu",
        "triangle_counting": (
            "experiments/v4_paper_apps_pyoptix/triangle_counting_device.cu"
        ),
        "librts": "experiments/v4_paper_apps_pyoptix/librts_device.cu",
    }
    if (
        pyoptix_ptx_manifest.get("schema")
        != "rtdl.v4_paper_apps_pyoptix.prebuilt_ptx.v1"
        or pyoptix_ptx_manifest.get("status")
        != "PASS__PREBUILT_PTX_READY_FOR_UNTIMED_DRY_RUN"
        or pyoptix_ptx_manifest.get("source_commit") != commit
        or pyoptix_ptx_manifest.get("source_tree") != tree
        or pyoptix_ptx_manifest.get("source_clean_after_build") is not True
        or tuple(pyoptix_ptx_manifest.get("compute_capability", ())) != cc
        or pyoptix_ptx_manifest.get("optix_header_sha256") != _sha(optix / "optix.h")
        or pyoptix_ptx_manifest.get("optix_device_header_sha256")
        != _sha(optix / "optix_device.h")
        or pyoptix_ptx_manifest.get("cuda_header_sha256") != _sha(cuda / "cuda.h")
        or pyoptix_ptx_manifest.get("python_executable")
        != str(Path(sys.executable).resolve(strict=True))
        or pyoptix_ptx_manifest.get("cuda_bindings_version")
        != package_versions["cuda-bindings"]
        or not isinstance(ptx_programs, dict)
        or set(ptx_programs) != set(expected_programs)
        or pyoptix_ptx_manifest.get("compile_time_in_primary_a_c_timer") is not False
    ):
        raise RuntimeError("prebuilt PyOptiX PTX manifest differs")
    prebuilt_ptx = {}
    for app, source_relative in expected_programs.items():
        row = ptx_programs[app]
        if not isinstance(row, dict) or row.get("source_path") != source_relative:
            raise RuntimeError(f"prebuilt PyOptiX PTX row differs: {app}")
        source_path = source / source_relative
        ptx_path = Path(str(row.get("ptx_path"))).resolve(strict=True)
        ptx_prefix = ptx_path.read_bytes()[:4096]
        if (
            row.get("source_sha256") != _sha(source_path)
            or row.get("ptx_sha256") != _sha(ptx_path)
            or row.get("ptx_size_bytes") != ptx_path.stat().st_size
            or ptx_path.stat().st_size <= 0
            or b".version" not in ptx_prefix
        ):
            raise RuntimeError(f"prebuilt PyOptiX PTX bytes differ: {app}")
        prebuilt_ptx[app] = {
            "path": str(ptx_path),
            "sha256": row["ptx_sha256"],
            "source_sha256": row["source_sha256"],
        }
    value = {
        "schema": "rtdl.v4_paper_apps_pyoptix.config.v1",
        "source_root": str(source),
        "source_commit": commit,
        "source_tree": tree,
        "data_root": str(data),
        "data_manifest_path": str(data_manifest),
        "data_manifest_sha256": _sha(data_manifest),
        "native_library_path": str(native),
        "native_library_sha256": _sha(native),
        "native_build_manifest_path": str(native_manifest_path),
        "native_build_manifest_sha256": _sha(native_manifest_path),
        "pyoptix_build_receipt_path": str(pyoptix_receipt_path),
        "pyoptix_build_receipt_sha256": _sha(pyoptix_receipt_path),
        "pyoptix_ptx_manifest_path": str(pyoptix_ptx_manifest_path),
        "pyoptix_ptx_manifest_sha256": _sha(pyoptix_ptx_manifest_path),
        "pyoptix_prebuilt_ptx": prebuilt_ptx,
        "pyoptix_loaded_extension_sha256": extension["sha256"],
        "optix_include": str(optix),
        "cuda_include": str(cuda),
        "compute_capability": list(cc),
        "registered_machine": machine,
        "optix_sdk": args.optix_sdk,
        "python_executable": str(Path(sys.executable).resolve(strict=True)),
        "python_executable_sha256": _sha(Path(sys.executable).resolve(strict=True)),
        "python_version": platform.python_version(),
        "package_versions": package_versions,
        "prepared_repetitions": {
            "particle_tracking": 32,
            "triangle_counting__com_dblp__rt_2a1": 4,
            "librts__parks__point_contains": 4,
            "librts__parks__range_contains": 4,
        },
        "prepared_warmups": 1,
        "registered_before_performance_observation": True,
        "performance_threshold_present": False,
        "retry_allowed": False,
        "discard_allowed": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(
        json.dumps(
            {
                "source_commit": value["source_commit"],
                "source_tree": value["source_tree"],
                "native_library_sha256": value["native_library_sha256"],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
