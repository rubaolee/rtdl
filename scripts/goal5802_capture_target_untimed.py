#!/usr/bin/env python3
"""Capture the first owner-provided target identity without timing or kernels."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

from experiments.goal5802_premeasurement.runtime_manifest import (
    digest,
    validate_target_observation_receipt,
)


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _tool(path: Path) -> dict[str, object]:
    original = path.absolute()
    resolved = original.resolve(strict=True)
    metadata = resolved.lstat()
    if not stat.S_ISREG(metadata.st_mode):
        raise RuntimeError(f"target-observation tool is not regular: {resolved}")
    if original.is_symlink():
        return {
            "path": str(original),
            "path_kind": "EXACT_SYMLINK_TO_REGULAR_FILE",
            "symlink_target": str(original.readlink()),
            "resolved_path": str(resolved),
            "bytes": metadata.st_size,
            "sha256": _sha(resolved),
        }
    return {
        "path": str(resolved), "path_kind": "REGULAR_FILE",
        "bytes": metadata.st_size, "sha256": _sha(resolved),
    }


def _one(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(command, check=False, capture_output=True)
    try:
        stdout = completed.stdout.decode("utf-8")
        stderr = completed.stderr.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RuntimeError("target-observation command output is not UTF-8") from error
    if completed.returncode != 0:
        raise RuntimeError({
            "command": command,
            "exit_code": completed.returncode,
            "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
        })
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout_utf8": stdout,
        "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
        "stderr_utf8": stderr,
        "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nvidia-smi", type=Path, required=True)
    parser.add_argument("--nvcc", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    if os.environ.get("LD_PRELOAD") is not None:
        raise RuntimeError("Goal5802 target capture forbids LD_PRELOAD")
    loader_path = os.environ.get("LD_LIBRARY_PATH")
    if loader_path is not None and (
            not loader_path or any(
                not item or not Path(item).is_absolute()
                for item in loader_path.split(os.pathsep))):
        raise RuntimeError(
            "Goal5802 LD_LIBRARY_PATH requires nonempty absolute entries")
    nvidia_smi = _tool(args.nvidia_smi)
    nvcc_tool = _tool(args.nvcc)
    # Metadata calls only.  No allocation, launch, synchronization, or clock.
    gpu_command = _one([
        str(nvidia_smi["path"]),
        "--query-gpu=name,compute_cap,driver_version",
        "--format=csv,noheader,nounits",
    ])
    gpu_rows = str(gpu_command["stdout_utf8"]).strip().splitlines()
    if len(gpu_rows) != 1:
        raise RuntimeError(
            "Goal5802 requires the first owner-provided single visible GPU; "
            "the capture tool does not select among devices")
    fields = [item.strip() for item in gpu_rows[0].split(",")]
    if len(fields) != 3 or not all(fields):
        raise RuntimeError("nvidia-smi target observation malformed")
    import cupy as cp
    import optix
    cuda_driver = str(cp.cuda.runtime.driverGetVersion())
    optix_version = ".".join(map(str, optix.version()))
    nvcc_command = _one([str(nvcc_tool["path"]), "--version"])
    nvcc_stdout = str(nvcc_command["stdout_utf8"]).strip()
    if not nvcc_stdout:
        raise RuntimeError("nvcc target observation output is empty")
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.target_observation.v2",
        "status": "PASS__UNTIMED_EXACT_TARGET_OBSERVATION",
        "tools": {"nvidia_smi": nvidia_smi, "nvcc": nvcc_tool},
        "command_receipts": {
            "nvidia_smi": gpu_command, "nvcc": nvcc_command},
        "gpu_name": fields[0],
        "compute_capability": fields[1],
        "driver_version": fields[2],
        "cuda_driver_version": cuda_driver,
        "cuda_toolkit_version": nvcc_stdout.splitlines()[-1],
        "optix_version": optix_version,
        "loader_environment": {
            "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH"),
            "LD_PRELOAD": None,
        },
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0,
    }
    value["observation_sha256"] = digest(value)
    validate_target_observation_receipt(
        value, {"nvidia_smi": nvidia_smi, "nvcc": nvcc_tool},
        require_current_loader_environment=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
