#!/usr/bin/env python3
"""Build the V4 OptiX native snapshot without relying on an omitted Makefile."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION_UNITS = (
    ROOT / "src/native/rtdl_optix.cpp",
    ROOT / "src/native/optix/rtdl_optix_cuda_helpers.cu",
)
REQUIRED_SYMBOLS = (
    "rtdl_optix_v4_warm_runtime_v1",
    "rtdl_optix_v4_prepare_curve_owner_grouped_any_hit_v1",
    "rtdl_optix_v4_execute_curve_owner_grouped_any_hit_v1",
    "rtdl_optix_v4_describe_curve_owner_grouped_any_hit_v1",
    "rtdl_optix_v4_destroy_curve_owner_grouped_any_hit_v1",
)
HEADER_SUFFIXES = frozenset({".h", ".hpp", ".inl", ".cuh"})


def _validate_output_paths(*paths: Path) -> None:
    resolved = tuple(path.resolve() for path in paths)
    for index, left in enumerate(resolved):
        for right in resolved[index + 1:]:
            if left == right or left in right.parents or right in left.parents:
                raise ValueError(
                    f"build outputs must be distinct non-nested files: "
                    f"{left} and {right}")


def _publish_exclusive(source: Path, destination: Path) -> None:
    try:
        os.link(source, destination)
    except FileExistsError:
        raise FileExistsError(destination) from None
    source.unlink()


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _capture(command: list[str], *, required: bool = True) -> str:
    completed = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, check=False)
    output = (completed.stdout + completed.stderr).strip()
    if required and completed.returncode:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {command!r}: {output}")
    return output


def _source_inventory() -> list[dict[str, object]]:
    paths = [ROOT / "src/native/rtdl_optix.cpp"]
    paths.extend(sorted(
        path for path in (ROOT / "src/native/optix").iterdir()
        if path.is_file() and path.suffix in {".cpp", ".cu", ".h"}
    ))
    return [{
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha(path),
    } for path in paths]


def _header_inventory(root: Path) -> list[dict[str, object]]:
    if not root.is_dir():
        raise NotADirectoryError(root)
    paths = sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in HEADER_SUFFIXES)
    if not paths:
        raise RuntimeError(f"header inventory is empty: {root}")
    return [{
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha(path),
    } for path in paths]


def _pkg_config_geos() -> tuple[list[str], list[str], str]:
    executable = shutil.which("pkg-config")
    if executable is not None:
        for package in ("geos-c", "geos"):
            cflags = subprocess.run(
                [executable, "--cflags", package], text=True,
                capture_output=True, check=False)
            libraries = subprocess.run(
                [executable, "--libs", package], text=True,
                capture_output=True, check=False)
            if cflags.returncode == 0 and libraries.returncode == 0:
                return (
                    shlex.split(cflags.stdout),
                    shlex.split(libraries.stdout),
                    f"pkg-config:{package}",
                )
    if Path("/usr/include/geos_c.h").is_file():
        return [], ["-lgeos_c"], "system-header-and-link-name"
    return [], [], "disabled-header-absent"


def _compute_capability(value: str | None) -> tuple[int, int]:
    if value is None:
        rows = _capture([
            "nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader",
        ]).splitlines()
        rows = [row.strip() for row in rows if row.strip()]
        if len(rows) != 1:
            raise RuntimeError(
                f"exactly one visible GPU is required, observed {len(rows)}")
        value = rows[0]
    match = re.fullmatch(r"([0-9]{1,2})\.([0-9]{1,2})", value)
    if match is None:
        raise ValueError(f"invalid compute capability: {value!r}")
    return int(match.group(1)), int(match.group(2))


def _gpu_identity() -> tuple[str, tuple[int, int]]:
    rows = _capture([
        "nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap",
        "--format=csv,noheader",
    ]).splitlines()
    rows = [row.strip() for row in rows if row.strip()]
    if len(rows) != 1:
        raise RuntimeError(
            f"exactly one visible GPU is required, observed {len(rows)}")
    columns = tuple(part.strip() for part in rows[0].split(","))
    if len(columns) != 4:
        raise RuntimeError("unexpected nvidia-smi GPU identity format")
    return rows[0], _compute_capability(columns[3])


def _optix_version(header: Path) -> int:
    text = header.read_text(encoding="utf-8", errors="strict")
    match = re.search(
        r"^\s*#\s*define\s+OPTIX_VERSION\s+([0-9]+)\s*$",
        text,
        re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("OPTIX_VERSION is absent from optix.h")
    return int(match.group(1))


def _optix_sdk_number(value: str) -> int:
    match = re.fullmatch(
        r"([0-9]{1,2})\.([0-9]{1,2})\.([0-9]{1,2})", value)
    if match is None:
        raise ValueError(f"invalid OptiX SDK version: {value!r}")
    major, minor, patch = (int(item) for item in match.groups())
    if major == 0:
        raise ValueError(f"invalid OptiX SDK version: {value!r}")
    return major * 10000 + minor * 100 + patch


def _write_json(path: Path, value: object) -> None:
    payload = json.dumps(
        value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".partial", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        _publish_exclusive(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _build_input_id(identity: dict[str, object]) -> str:
    return hashlib.sha256(json.dumps(
        identity, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode("utf-8")).hexdigest()


def build(args) -> dict[str, object]:
    cuda = args.cuda_prefix.resolve(strict=True)
    optix = args.optix_prefix.resolve(strict=True)
    output = args.output.resolve()
    manifest = args.manifest.resolve()
    log = args.log.resolve()
    _validate_output_paths(output, manifest, log)
    for path in (output, manifest, log):
        if path.exists():
            raise FileExistsError(path)
        path.parent.mkdir(parents=True, exist_ok=True)
    if not cuda.is_dir() or not optix.is_dir():
        raise NotADirectoryError(
            cuda if not cuda.is_dir() else optix)
    nvcc = (cuda / "bin/nvcc").resolve(strict=True)
    if args.host_compiler is None:
        discovered_host_compiler = shutil.which("g++")
        if discovered_host_compiler is None:
            raise RuntimeError("g++ is required as the explicit nvcc host compiler")
        host_compiler = Path(discovered_host_compiler)
    else:
        host_compiler = args.host_compiler
    host_compiler = host_compiler.expanduser().resolve(strict=True)
    optix_include = optix / "include"
    cuda_include = cuda / "include"
    optix_h = optix_include / "optix.h"
    cuda_h = cuda_include / "cuda.h"
    nvrtc_h = cuda_include / "nvrtc.h"
    for path in (
        *TRANSLATION_UNITS, nvcc, host_compiler,
        optix_h, cuda_h, nvrtc_h,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)
    if not os.access(nvcc, os.X_OK):
        raise PermissionError(f"nvcc is not executable: {nvcc}")
    if not os.access(host_compiler, os.X_OK):
        raise PermissionError(
            f"nvcc host compiler is not executable: {host_compiler}")
    if not cuda_include.is_dir() or not optix_include.is_dir():
        raise NotADirectoryError(
            cuda_include if not cuda_include.is_dir() else optix_include)
    git_commit = _capture(["git", "rev-parse", "HEAD"])
    git_status = _capture(["git", "status", "--porcelain"])
    if git_status and not args.allow_dirty:
        raise RuntimeError("native evidence build requires a clean Git tree")
    gpu_identity, observed_capability = _gpu_identity()
    capability = observed_capability if args.compute_capability is None \
        else _compute_capability(args.compute_capability)
    if capability != observed_capability:
        raise RuntimeError(
            "--compute-capability differs from the visible GPU: "
            f"requested={capability}, observed={observed_capability}")
    optix_version = _optix_version(optix_h)
    expected_optix_version = _optix_sdk_number(args.expected_optix_sdk)
    if optix_version != expected_optix_version:
        raise RuntimeError(
            "OptiX header version differs from --expected-optix-sdk: "
            f"header={optix_version}, expected={expected_optix_version}")
    source_inventory = _source_inventory()
    optix_header_inventory = _header_inventory(optix_include)
    cuda_header_inventory = _header_inventory(cuda_include)
    geos_cflags, geos_libraries, geos_mode = _pkg_config_geos()
    system_include = Path("/usr/include/x86_64-linux-gnu")
    cuda_system_include = str(system_include) if system_include.is_dir() else ""
    library_dirs = []
    for candidate in (
        cuda / "lib64",
        cuda / "targets/x86_64-linux/lib",
        Path("/usr/lib/x86_64-linux-gnu"),
    ):
        if candidate.is_dir() and candidate not in library_dirs:
            library_dirs.append(candidate)
    identity = {
        "schema": "rtdl.v4.optix_native_build_input.v1",
        "git_commit": git_commit,
        "builder_sha256": _sha(Path(__file__).resolve()),
        "source_inventory": source_inventory,
        "translation_units": [
            path.relative_to(ROOT).as_posix() for path in TRANSLATION_UNITS],
        "nvcc_path": str(nvcc),
        "nvcc_sha256": _sha(nvcc),
        "nvcc_version": _capture([str(nvcc), "--version"]),
        "host_compiler_path": str(host_compiler),
        "host_compiler_sha256": _sha(host_compiler),
        "host_compiler_version": _capture(
            [str(host_compiler), "--version"]),
        "optix_include": str(optix_include),
        "cuda_include": str(cuda_include),
        "optix_h_sha256": _sha(optix_h),
        "cuda_h_sha256": _sha(cuda_h),
        "nvrtc_h_sha256": _sha(nvrtc_h),
        "optix_header_inventory": optix_header_inventory,
        "cuda_header_inventory": cuda_header_inventory,
        "optix_version": optix_version,
        "expected_optix_sdk": args.expected_optix_sdk,
        "compute_capability": list(capability),
        "gpu": gpu_identity,
        "language_standard": "c++17",
        "optimization": "O3",
        "position_independent_code": True,
        "geos_cflags": geos_cflags,
        "geos_libraries": geos_libraries,
        "library_dirs": [str(path) for path in library_dirs],
    }
    build_id = _build_input_id(identity)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".partial", dir=output.parent)
    os.close(descriptor)
    temporary_output = Path(temporary_name)
    temporary_output.unlink()
    command = [
        str(nvcc), "-ccbin", str(host_compiler),
        "-std=c++17", "-O3", "-shared",
        f"-I{optix_include}", f"-I{cuda_include}", *geos_cflags,
        f'-DRTDL_OPTIX_INCLUDE_DIR="{optix_include}"',
        f'-DRTDL_CUDA_INCLUDE_DIR="{cuda_include}"',
        f'-DRTDL_CUDA_SYSTEM_INCLUDE_DIR="{cuda_system_include}"',
        f'-DRTDL_OPTIX_BUILD_ID="{build_id}"',
        f"-arch=sm_{capability[0]}{capability[1]}",
        "-Xcompiler", "-fPIC",
        *(str(path) for path in TRANSLATION_UNITS),
        *(f"-L{path}" for path in library_dirs),
        "-lcuda", "-lnvrtc", *geos_libraries,
        "-o", str(temporary_output),
    ]
    try:
        with log.open("x", encoding="utf-8", newline="\n") as stream:
            process = subprocess.Popen(
                command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            if process.stdout is None:
                raise RuntimeError("native build stdout pipe is unavailable")
            for line in process.stdout:
                stream.write(line)
                stream.flush()
                print(line, end="", flush=True)
            status = process.wait()
        if status:
            raise RuntimeError(f"native build failed ({status}); see {log}")
        if not temporary_output.is_file() or temporary_output.stat().st_size == 0:
            raise RuntimeError("native build produced no shared library")
        nm = shutil.which("nm")
        if nm is None:
            raise RuntimeError("nm is required for exported-symbol verification")
        exported = _capture([nm, "-D", "--defined-only", str(temporary_output)])
        exported_names = {
            line.split()[-1] for line in exported.splitlines() if line.split()}
        missing = [name for name in REQUIRED_SYMBOLS
                   if name not in exported_names]
        if missing:
            raise RuntimeError(
                f"native owner-grouped symbols are missing: {missing}")
        native_bytes = temporary_output.stat().st_size
        native_sha256 = _sha(temporary_output)
        _publish_exclusive(temporary_output, output)
    finally:
        temporary_output.unlink(missing_ok=True)
    post_commit = _capture(["git", "rev-parse", "HEAD"])
    post_status = _capture(["git", "status", "--porcelain"])
    if post_commit != git_commit or post_status != git_status \
            or _source_inventory() != source_inventory \
            or _sha(Path(__file__).resolve()) != identity["builder_sha256"] \
            or _sha(nvcc) != identity["nvcc_sha256"] \
            or _capture([str(nvcc), "--version"]) != \
                identity["nvcc_version"] \
            or _sha(host_compiler) != identity["host_compiler_sha256"] \
            or _capture([str(host_compiler), "--version"]) != \
                identity["host_compiler_version"] \
            or _gpu_identity() != (gpu_identity, observed_capability) \
            or _header_inventory(optix_include) != optix_header_inventory \
            or _header_inventory(cuda_include) != cuda_header_inventory:
        output.unlink()
        raise RuntimeError("build input identity changed during native build")
    reproduction_command = [
        str(output) if item == str(temporary_output) else item
        for item in command
    ]
    result = {
        "schema": "rtdl.v4.optix_native_snapshot_build.v1",
        "status": "PASS__FRESH_NATIVE_BUILT_AND_REQUIRED_SYMBOLS_EXPORTED",
        "git_commit": git_commit,
        "git_commit_after_build": post_commit,
        "git_status_before_build": git_status.splitlines(),
        "git_status_after_build": post_status.splitlines(),
        "dirty_build_authorized": bool(args.allow_dirty),
        "build_id": build_id,
        "build_input": identity,
        "executed_command": command,
        "executed_command_display": shlex.join(command),
        "reproduction_command": reproduction_command,
        "reproduction_command_display": shlex.join(reproduction_command),
        "log_path": str(log),
        "log_sha256": _sha(log),
        "native_path": str(output),
        "native_bytes": native_bytes,
        "native_sha256": native_sha256,
        "nvcc_path": str(nvcc),
        "nvcc_sha256": identity["nvcc_sha256"],
        "nvcc_version": identity["nvcc_version"],
        "host_compiler_path": str(host_compiler),
        "host_compiler_sha256": identity["host_compiler_sha256"],
        "host_compiler_version": identity["host_compiler_version"],
        "optix_version": optix_version,
        "gpu": gpu_identity,
        "geos_mode": geos_mode,
        "required_symbols": list(REQUIRED_SYMBOLS),
        "exported_symbol_match_mode": "exact_nm_dynamic_defined_name",
        "all_required_symbols_exported": True,
    }
    try:
        _write_json(manifest, result)
    except Exception:
        output.unlink(missing_ok=True)
        raise
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cuda-prefix", required=True, type=Path)
    parser.add_argument("--optix-prefix", required=True, type=Path)
    parser.add_argument("--expected-optix-sdk", default="9.0.0")
    parser.add_argument("--compute-capability")
    parser.add_argument("--host-compiler", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args()
    result = build(args)
    print(json.dumps({
        "status": result["status"],
        "native_path": result["native_path"],
        "native_sha256": result["native_sha256"],
        "optix_version": result["optix_version"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
