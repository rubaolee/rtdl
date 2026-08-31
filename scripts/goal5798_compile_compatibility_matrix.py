#!/usr/bin/env python3
"""Build-only verification of every frozen Goal5798 OptiX stack.

This successor runs only after the timed transaction.  It executes no RT
workload and observes no application result.  For every frozen header commit,
it builds the current NVIDIA PyOptiX source, the RTDL native library, and the
matched Direct CUDA/OptiX executable from unchanged sources.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tarfile
import time
import zipfile


def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, **kwargs)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


def create_json(path: Path, value: dict[str, object]) -> None:
    if path.exists():
        raise FileExistsError(path)
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}.{time.monotonic_ns()}")
    payload = json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        os.close(descriptor)
        temporary.unlink(missing_ok=True)


def load_compatibility(source_root: Path):
    path = source_root / "experiments/goal5798_premeasurement/compatibility.py"
    spec = importlib.util.spec_from_file_location("goal5798_compatibility", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load compatibility registry")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compute_process_rows() -> list[str]:
    result = run([
        "nvidia-smi", "--query-compute-apps=gpu_uuid,pid",
        "--format=csv,noheader,nounits",
    ], capture_output=True)
    return sorted(row.strip() for row in result.stdout.splitlines()
                  if row.strip() and "No running" not in row)


def optix_macro(header: Path) -> int:
    result = run([
        "g++", "-dM", "-E", "-x", "c++", "-include", str(header), "-",
    ], input="", capture_output=True)
    match = re.search(r"^#define OPTIX_VERSION\s+(\d+)\s*$", result.stdout, re.MULTILINE)
    if match is None:
        raise RuntimeError(f"OPTIX_VERSION absent from {header}")
    return int(match.group(1))


def version_at_least(actual: str, minimum: str) -> bool:
    actual_parts = tuple(int(value) for value in re.findall(r"\d+", actual))
    minimum_parts = tuple(int(value) for value in re.findall(r"\d+", minimum))
    width = max(len(actual_parts), len(minimum_parts))
    return (actual_parts + (0,) * (width - len(actual_parts)) >=
            minimum_parts + (0,) * (width - len(minimum_parts)))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--pyoptix-repo", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--cuda-root", type=Path)
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    pyoptix_repo = args.pyoptix_repo.resolve()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=False)
    compatibility = load_compatibility(source_root)

    cuda_root = args.cuda_root.resolve() if args.cuda_root else Path(
        run(["bash", "-lc", "cd \"$(dirname \"$(command -v nvcc)\")/..\" && pwd"],
            capture_output=True).stdout.strip()).resolve()
    nvcc = cuda_root / "bin/nvcc"
    if not nvcc.is_file() or not (cuda_root / "include/cuda.h").is_file():
        raise RuntimeError(f"invalid CUDA root: {cuda_root}")
    pyoptix_head = run(
        ["git", "-C", str(pyoptix_repo), "rev-parse", "HEAD"],
        capture_output=True).stdout.strip()
    if pyoptix_head != compatibility.PYOPTIX_COMMIT:
        raise RuntimeError("PyOptiX repository identity mismatch")

    gpu_fields = run([
        "nvidia-smi", "--query-gpu=driver_version,compute_cap",
        "--format=csv,noheader,nounits",
    ], capture_output=True).stdout.strip().splitlines()[0].split(",")
    observed_driver, capability = (value.strip() for value in gpu_fields)
    if re.fullmatch(r"\d+\.\d+", capability) is None:
        raise RuntimeError(f"invalid observed compute capability: {capability!r}")
    cuda_arch = "sm_" + capability.replace(".", "")
    before_processes = compute_process_rows()
    if before_processes:
        raise RuntimeError(f"GPU process present before build-only matrix: {before_processes}")

    rows: list[dict[str, object]] = []
    for index, stack in enumerate(compatibility.frozen_registry()):
        row_root = output_root / f"{index:02d}_{stack['stack_id']}"
        header_repo = row_root / "optix-dev"
        pyoptix_source = row_root / "otk-pyoptix"
        wheel_root = row_root / "wheel"
        wheel_unpack = row_root / "wheel-unpacked"
        row_root.mkdir()
        wheel_root.mkdir()
        wheel_unpack.mkdir()

        run(["git", "init", "-q", str(header_repo)])
        run(["git", "-C", str(header_repo), "remote", "add", "origin",
             "https://github.com/NVIDIA/optix-dev.git"])
        run(["git", "-C", str(header_repo), "fetch", "-q", "--depth", "1",
             "origin", stack["optix_header_commit"]])
        run(["git", "-C", str(header_repo), "checkout", "-q", "--detach", "FETCH_HEAD"])
        header_head = run(
            ["git", "-C", str(header_repo), "rev-parse", "HEAD"],
            capture_output=True).stdout.strip()
        if header_head != stack["optix_header_commit"]:
            raise RuntimeError("OptiX header checkout identity mismatch")
        pyoptix_archive = row_root / "otk-pyoptix.tar"
        run(["git", "-C", str(pyoptix_repo), "archive", "--format=tar",
             f"--output={pyoptix_archive}", "HEAD"])
        pyoptix_source.mkdir()
        with tarfile.open(pyoptix_archive) as archive:
            archive.extractall(pyoptix_source, filter="data")
        pyoptix_archive.unlink()

        environment = dict(os.environ)
        cmake_args = f"-DFETCHCONTENT_SOURCE_DIR_OPTIX_HEADERS={header_repo}"
        environment["CMAKE_ARGS"] = cmake_args
        environment["PYOPTIX_CMAKE_ARGS"] = cmake_args
        run([
            sys.executable, "-m", "pip", "wheel", "--no-build-isolation",
            "--no-deps", "--no-cache-dir", "--wheel-dir", str(wheel_root),
            str(pyoptix_source),
        ], env=environment)
        wheels = list(wheel_root.glob("*.whl"))
        if len(wheels) != 1:
            raise RuntimeError("PyOptiX build did not emit exactly one wheel")
        wheel = wheels[0]
        with zipfile.ZipFile(wheel) as archive:
            archive.extractall(wheel_unpack)
        expected_api = [int(value) for value in stack["optix_api_version"].split(".")]
        imported_api: list[int] | None = None
        if version_at_least(observed_driver, stack["minimum_driver"]):
            import_environment = dict(os.environ)
            import_environment["PYTHONPATH"] = str(wheel_unpack)
            import_environment["CUDA_VISIBLE_DEVICES"] = ""
            observed_api = run([
                sys.executable, "-c",
                "import json,optix; print(json.dumps(list(optix.version())))",
            ], env=import_environment, capture_output=True).stdout.strip()
            imported_api = json.loads(observed_api)
            if imported_api != expected_api:
                raise RuntimeError(
                    f"PyOptiX ABI mismatch for {stack['stack_id']}: {observed_api}")
            abi_import_status = "PASS_ON_OBSERVED_COMPATIBLE_DRIVER"
        else:
            abi_import_status = "NOT_ATTEMPTED__OBSERVED_DRIVER_BELOW_PUBLISHED_FLOOR"

        native = row_root / "librtdl_optix.so"
        system_include = Path(f"/usr/include/{platform.machine()}-linux-gnu")
        command = [
            str(nvcc), "-std=c++17", "-O3", "-shared",
            f"-I{header_repo / 'include'}", f"-I{cuda_root / 'include'}",
            f'-DRTDL_OPTIX_INCLUDE_DIR="{header_repo / "include"}"',
            f'-DRTDL_CUDA_INCLUDE_DIR="{cuda_root / "include"}"',
            f'-DRTDL_OPTIX_BUILD_ID="GOAL5798_COMPAT_{index}"',
            "-Xcompiler", "-fPIC", f"-arch={cuda_arch}",
            str(source_root / "src/native/rtdl_optix.cpp"),
            str(source_root / "src/native/optix/rtdl_optix_cuda_helpers.cu"),
            f"-L{cuda_root / 'lib64'}", "-lcuda", "-lnvrtc", "-lgeos_c",
            "-o", str(native),
        ]
        if system_include.is_dir():
            command.insert(6, f'-DRTDL_CUDA_SYSTEM_INCLUDE_DIR="{system_include}"')
        run(command)

        direct = row_root / "goal5798_direct_measurement"
        run([
            "bash", str(source_root / "experiments/goal5798_premeasurement/build_direct_measurement.sh"),
            str(header_repo / "include"), str(cuda_root / "include"), str(direct),
        ])
        major, minor, patch = expected_api
        expected_macro = major * 10000 + minor * 100 + patch
        actual_macro = optix_macro(header_repo / "include/optix.h")
        if actual_macro != expected_macro:
            raise RuntimeError(
                f"OptiX macro mismatch: {actual_macro} != {expected_macro}")
        rows.append({
            "stack_id": stack["stack_id"],
            "optix_api_version": stack["optix_api_version"],
            "optix_header_commit": header_head,
            "optix_header_macro": actual_macro,
            "pyoptix_commit": pyoptix_head,
            "pyoptix_source_edited": False,
            "pyoptix_wheel_sha256": sha256(wheel),
            "pyoptix_imported_api_version": imported_api,
            "pyoptix_abi_import_status": abi_import_status,
            "rtdl_native_sha256": sha256(native),
            "direct_binary_sha256": sha256(direct),
            "build_status": "PASS",
        })

    after_processes = compute_process_rows()
    if after_processes:
        raise RuntimeError(f"build-only matrix created GPU processes: {after_processes}")
    result: dict[str, object] = {
        "schema": "rtdl.goal5798.compile_compatibility_matrix.v2",
        "status": "PASS",
        "hostname": platform.node(),
        "observed_driver": observed_driver,
        "builder_sha256": sha256(Path(__file__).resolve()),
        "source_inputs": {
            path: sha256(source_root / path) for path in (
                "experiments/goal5798_premeasurement/compatibility.py",
                "experiments/goal5798_premeasurement/build_direct_measurement.sh",
                "experiments/goal5798_premeasurement/runtime_manifest_v9.json",
                "experiments/goal5796_matched/direct_optix.cpp",
                "src/native/rtdl_optix.cpp",
                "src/native/optix/rtdl_optix_cuda_helpers.cu",
            )
        },
        "observed_compute_capability_used_only_as_compile_target": capability,
        "gpu_workload_executed": False,
        "application_result_observed": False,
        "gpu_processes_before": before_processes,
        "gpu_processes_after": after_processes,
        "stack_count": len(rows),
        "rows": rows,
    }
    result["result_sha256"] = canonical_digest(result)
    create_json(output_root / "result.json", result)
    print(json.dumps({
        "status": result["status"], "stack_count": len(rows),
        "result_sha256": result["result_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
