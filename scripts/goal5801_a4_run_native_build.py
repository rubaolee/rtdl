#!/usr/bin/env python3
"""Run one untimed Goal5801 native build and preserve exact build receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import stat
import subprocess


def canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def write_new(path: Path, value: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())


def run_receipt(path: Path, command: list[str], environment: dict[str, str]) -> None:
    completed = subprocess.run(
        command, check=False, env=environment,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    write_new(path, completed.stdout)
    if completed.returncode != 0:
        raise RuntimeError({"receipt_command": command, "exit": completed.returncode})


def regular_tool(path: Path, label: str) -> Path:
    """Resolve one explicitly supplied executable without assuming /usr/bin."""

    supplied = path.expanduser()
    resolved = supplied.resolve(strict=True)
    if not stat.S_ISREG(resolved.stat().st_mode) or not os.access(resolved, os.X_OK):
        raise ValueError(f"{label} is not an executable regular file: {resolved}")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--optix-prefix", type=Path, required=True)
    parser.add_argument("--cuda-prefix", type=Path, required=True)
    parser.add_argument("--build-id", required=True)
    parser.add_argument("--cuda-arch", required=True)
    parser.add_argument("--make", type=Path, required=True)
    parser.add_argument("--nvcc", type=Path, required=True)
    parser.add_argument("--host-cxx", type=Path, required=True)
    parser.add_argument("--git", type=Path, required=True)
    parser.add_argument("--uname", type=Path, required=True)
    parser.add_argument("--ldd", type=Path, required=True)
    parser.add_argument("--pkg-config", type=Path, required=True)
    args = parser.parse_args()

    source = args.source_root.resolve(strict=True)
    output = args.output_root.resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    tools = {
        "make": regular_tool(args.make, "make"),
        "nvcc": regular_tool(args.nvcc, "nvcc"),
        "host_cxx": regular_tool(args.host_cxx, "host C++ compiler"),
        "git": regular_tool(args.git, "git"),
        "uname": regular_tool(args.uname, "uname"),
        "ldd": regular_tool(args.ldd, "ldd"),
        "pkg_config": regular_tool(args.pkg_config, "pkg-config"),
    }
    dependency_file = output / "rtdl_optix_dependencies.d"
    native_directory = output / "native"
    command = [
        str(tools["make"]), "-C", str(source),
        f"BUILD_DIR={native_directory}",
        f"OPTIX_PREFIX={args.optix_prefix.resolve(strict=True)}",
        f"CUDA_PREFIX={args.cuda_prefix.resolve(strict=True)}",
        f"RTDL_OPTIX_BUILD_ID={args.build_id}",
        f"OPTIX_CUDA_ARCH={args.cuda_arch}",
        f"NVCC={tools['nvcc']}",
        f"CXX_OPTIX={tools['nvcc']} -MD -MF {dependency_file}",
        "build-optix",
    ]
    inherited_path = os.environ.get("PATH", "")
    inherited_parts = inherited_path.split(os.pathsep) if inherited_path else []
    if any(not item or not Path(item).is_absolute() for item in inherited_parts):
        raise ValueError("native build requires PATH with nonempty absolute entries")
    path_parts: list[str] = []
    for item in [*(str(path.parent) for path in tools.values()), *inherited_parts]:
        if item not in path_parts:
            path_parts.append(item)
    environment = {
        "HOME": str(Path.home()),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": os.pathsep.join(path_parts),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    write_new(output / "build_environment.json", canonical(environment) + b"\n")
    write_new(
        output / "build_command.txt",
        (" ".join(shlex.quote(value) for value in command) + "\n").encode("utf-8"),
    )
    completed = subprocess.run(
        command, check=False, env=environment,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    write_new(output / "build_stdout.txt", completed.stdout)
    write_new(output / "build_stderr.txt", completed.stderr)
    write_new(output / "build_exit_code.txt", f"{completed.returncode}\n".encode("ascii"))
    native = native_directory / "librtdl_optix.so"
    if completed.returncode != 0 or not dependency_file.is_file() \
            or not native.is_file():
        raise RuntimeError(f"native build failed; receipts preserved at {output}")

    receipts = output / "tool_receipts"
    receipts.mkdir()
    for name, receipt_command in (
            ("nvcc_version.txt", [str(tools["nvcc"]), "--version"]),
            ("make_version.txt", [str(tools["make"]), "--version"]),
            ("host_cxx_version.txt", [str(tools["host_cxx"]), "--version"]),
            ("git_version.txt", [str(tools["git"]), "--version"]),
            ("pkg_config_version.txt", [str(tools["pkg_config"]), "--version"]),
            ("uname.txt", [str(tools["uname"]), "-a"]),
            ("native_ldd.txt", [str(tools["ldd"]), str(native)])):
        run_receipt(receipts / name, receipt_command, environment)
    native_bytes = native.read_bytes()
    result = {
        "schema": "rtdl.goal5801.a4.native_build_run.v1",
        "status": "PASS__UNTIMED_NATIVE_BUILD",
        "registered_performance_timing_count": 0,
        "native_bytes": len(native_bytes),
        "native_sha256": hashlib.sha256(native_bytes).hexdigest(),
        "dependency_file_sha256": hashlib.sha256(
            dependency_file.read_bytes()).hexdigest(),
        "build_id": args.build_id,
        "cuda_arch": args.cuda_arch,
    }
    write_new(output / "result.json", canonical(result) + b"\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
