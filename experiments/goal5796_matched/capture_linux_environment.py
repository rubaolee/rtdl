#!/usr/bin/env python3
"""Capture the exact non-timed Goal5796 Linux functional environment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


REMOTE_FILES = {
    "direct_binary": (
        "/home/lestat/work/goal5796_matched_20260823_v2/"
        "experiments/goal5796_matched/direct_optix"),
    "direct_result": (
        "/home/lestat/work/goal5796_matched_20260823_v2/"
        "experiments/goal5796_matched/DIRECT_RESULT.json"),
    "direct_oracle": (
        "/home/lestat/work/goal5796_matched_20260823_v2/"
        "experiments/goal5796_matched/DIRECT_ORACLE.json"),
    "rtdl_native": (
        "/home/lestat/work/goal5796_rtdl_source_20260823_v1/"
        "source/build/librtdl_optix.so"),
    "rtdl_result": (
        "/home/lestat/work/goal5796_matched_20260823_v2/"
        "experiments/goal5796_matched/RTDL_RESULT.json"),
    "rtdl_oracle": (
        "/home/lestat/work/goal5796_matched_20260823_v2/"
        "experiments/goal5796_matched/RTDL_ORACLE.json"),
    "optix_header": "/home/lestat/vendor/optix-dev/include/optix.h",
    "cuda_header": "/usr/include/cuda.h",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ssh(host: str, command: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", host, command],
        check=check, text=True, capture_output=True,
    )


def one(host: str, command: str) -> str:
    return ssh(host, command).stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="lestat@192.168.1.20")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    root = args.root.resolve()
    remote_hash_lines = one(
        args.host, "sha256sum " + " ".join(REMOTE_FILES.values()))
    remote_hashes = {}
    for line in remote_hash_lines.splitlines():
        digest, path = line.split(None, 1)
        remote_hashes[path] = digest

    driver = one(
        args.host,
        "nvidia-smi --query-gpu=name,driver_version,uuid,compute_cap "
        "--format=csv,noheader")
    driver_version = driver.split(",")[1].strip()
    gate = ssh(
        args.host,
        "driver_version=$(nvidia-smi --query-gpu=driver_version "
        "--format=csv,noheader | head -n 1); "
        "driver_branch=${driver_version%%.*}; "
        "printf 'driver_version=%s\\n' \"$driver_version\"; "
        "if [ \"$driver_branch\" -lt 590 ]; then "
        "printf 'BLOCKED_CURRENT_PYOPTIX_9_1_REQUIRES_R590_OR_LATER\\n'; "
        "exit 42; fi",
        check=False,
    )
    if int(driver_version.split(".", 1)[0]) < 590:
        if gate.returncode != 42 or "BLOCKED_CURRENT_PYOPTIX" not in gate.stdout:
            raise RuntimeError("current PyOptiX fail-before-install gate did not fire")

    local_sources = {}
    for path in (
        "experiments/goal5796_matched/semantic_spec.json",
        "experiments/goal5796_matched/independent_oracle.py",
        "experiments/goal5796_matched/matched_device.cu",
        "experiments/goal5796_matched/direct_optix.cpp",
        "experiments/goal5796_matched/pyoptix_baseline.py",
        "experiments/goal5796_matched/rtdl_baseline.py",
        "experiments/goal5796_matched/build_direct.sh",
        "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
        "src/native/optix/rtdl_optix_api.cpp",
        "src/rtdsl/v4_bounded_relation_prepared_runtime.py",
        "src/rtdsl/v4_callback_lifecycle.py",
    ):
        source = root / path
        local_sources[path] = {"bytes": source.stat().st_size, "sha256": sha(source)}

    result = {
        "schema": "rtdl.goal5796.linux_functional_environment.v1",
        "status": "A_AND_D_FUNCTIONAL_ENVIRONMENT_CAPTURED__B_BLOCKED_BEFORE_INSTALL",
        "transport": {
            "host": args.host,
            "wsl_used": False,
            "kernel": one(args.host, "uname -a"),
            "hostname": one(args.host, "hostname"),
        },
        "gpu": {"nvidia_smi": driver},
        "toolchain": {
            "python": one(args.host, "python3 --version"),
            "nvcc": one(args.host, "nvcc --version"),
            "gxx": one(args.host, "g++ --version | head -n 1"),
            "optix_version_macro": one(
                args.host,
                "grep -h '^#define OPTIX_VERSION ' "
                "/home/lestat/vendor/optix-dev/include/optix.h "
                "/home/lestat/vendor/optix-dev/include/optix_types.h | head -n 1"),
        },
        "remote_files": {
            name: {
                "path": path,
                "sha256": remote_hashes[path],
                "bytes": int(one(args.host, f"stat -c %s {path}")),
            }
            for name, path in REMOTE_FILES.items()
        },
        "direct_build": {
            "argv_contract": (
                "g++ -std=c++17 -O2 -Wall -Wextra -Werror "
                "-I/home/lestat/vendor/optix-dev/include -I/usr/include "
                "direct_optix.cpp -L/usr/lib64 -lcuda -lnvrtc -ldl -o direct_optix"),
            "ldd": one(args.host, f"ldd {REMOTE_FILES['direct_binary']}"),
        },
        "rtdl_build": {
            "source_root": "/home/lestat/work/goal5796_rtdl_source_20260823_v1/source",
            "make_contract": (
                "make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev "
                "CUDA_PREFIX=/usr OPTIX_CUDA_ARCH=sm_61"),
            "semantic_capacity_abi_symbol_present": "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v2"
                in one(args.host, f"nm -D {REMOTE_FILES['rtdl_native']}"),
            "ldd": one(args.host, f"ldd {REMOTE_FILES['rtdl_native']}"),
        },
        "local_source_identities": local_sources,
        "current_pyoptix_gate": {
            "repository_commit": "3144f224c0fd18733925faf3d8fb82c7376b8dcf",
            "package_version": "9.1.0",
            "required_driver_branch_minimum": 590,
            "observed_driver_version": driver_version,
            "exit_code": gate.returncode,
            "stdout": gate.stdout.strip(),
            "stderr": gate.stderr.strip(),
            "package_install_attempted": False,
            "optix_context_created": False,
            "substitution_used": False,
            "status": "ENVIRONMENT_INELIGIBLE__CURRENT_PYOPTIX_NOT_EXECUTED",
        },
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(
        result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
