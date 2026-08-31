#!/usr/bin/env python3
"""Freeze the load-bearing Goal5805 target runtime without timing work."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

from experiments.goal5805_successor.protocol import (
    RUNTIME_SCHEMA, TARGET_OBSERVATION_SCHEMA, digest, file_record,
    validate_runtime_manifest, validate_target_observation,
)


def _write(path: Path, value: object) -> None:
    if path.exists():
        raise RuntimeError(f"Goal5805 create-only output exists: {path}")
    path.write_bytes(json.dumps(
        value, indent=2, allow_nan=False, sort_keys=True).encode("utf-8") + b"\n")


def _gpu(nvidia_smi: Path) -> dict[str, object]:
    completed = subprocess.run([
        str(nvidia_smi),
        "--query-gpu=uuid,name,compute_cap,driver_version,memory.total",
        "--format=csv,noheader,nounits",
    ], capture_output=True, text=True, check=False)
    rows = completed.stdout.strip().splitlines()
    fields = [item.strip() for item in rows[0].split(",")] if len(rows) == 1 else []
    if completed.returncode or len(fields) != 5:
        raise RuntimeError("Goal5805 requires exactly one observable GPU")
    return {
        "gpu_uuid": fields[0], "gpu_name": fields[1],
        "compute_capability": fields[2], "driver_version": fields[3],
        "gpu_memory_total_mib": int(fields[4]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in (
        "candidate-manifest", "trust-root", "trust-head", "trust-package",
        "native-library", "matched-ptx", "relation-compaction-cubin",
        "rtdlexe-module", "nvcc", "nvidia-smi",
    ):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--target-observation-output", type=Path, required=True)
    parser.add_argument("--runtime-manifest-output", type=Path, required=True)
    args = parser.parse_args()

    nvcc = subprocess.run(
        [str(args.nvcc.resolve(strict=True)), "--version"],
        capture_output=True, text=True, check=True).stdout.strip()
    target = {
        "schema": TARGET_OBSERVATION_SCHEMA,
        "status": "PASS__OBSERVED_BEFORE_FORMAL_WORKER_ZERO",
        "hostname": platform.node(),
        **_gpu(args.nvidia_smi.resolve(strict=True)),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
        "nvcc_version": nvcc,
        "python_version": platform.python_version(),
        "clock_read_count": 0, "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0, "registered_performance_timing_count": 0,
    }
    target["target_observation_sha256"] = digest(target)
    validate_target_observation(target)
    _write(args.target_observation_output, target)

    numpy = importlib.import_module("numpy")
    cupy = importlib.import_module("cupy")
    optix = importlib.import_module("optix")
    extension = importlib.import_module("optix._optix")
    measurement_files = {
        name: file_record(getattr(args, name)) for name in (
            "candidate_manifest", "trust_root", "trust_head", "trust_package",
            "native_library", "matched_ptx", "relation_compaction_cubin",
        )
    }
    runtime_files = {
        "python_executable": file_record(Path(sys.executable)),
        "numpy_module": file_record(Path(numpy.__file__)),
        "cupy_module": file_record(Path(cupy.__file__)),
        "pyoptix_extension": file_record(Path(extension.__file__)),
        "rtdlexe_module": file_record(args.rtdlexe_module),
    }
    runtime = {
        "schema": RUNTIME_SCHEMA,
        "status": "TARGET_RUNTIME_FROZEN__FORMAL_WORKER_ZERO",
        "target_observation": file_record(args.target_observation_output),
        "measurement_files": measurement_files,
        "runtime_files": runtime_files,
        "runtime_versions": {
            "python": platform.python_version(), "numpy": str(numpy.__version__),
            "cupy": str(cupy.__version__),
            "pyoptix": importlib.metadata.version("pyoptix"),
            "optix_api": ".".join(str(item) for item in optix.version()),
        },
        "loader_environment": {
            "cuda_home": os.environ.get("CUDA_HOME"),
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "ld_library_path": os.environ.get("LD_LIBRARY_PATH"),
        },
        "clock_read_count": 0, "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0, "registered_performance_timing_count": 0,
    }
    runtime["runtime_manifest_sha256"] = digest(runtime)
    validate_runtime_manifest(runtime, rehash=True)
    _write(args.runtime_manifest_output, runtime)
    print(json.dumps({
        "runtime_manifest_sha256": runtime["runtime_manifest_sha256"],
        "target_observation_sha256": target["target_observation_sha256"],
        "formal_worker_count": 0, "registered_performance_timing_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
