#!/usr/bin/env python3
"""Capture exact host/runtime dependencies for Goal5802 without timing GPU work."""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys


THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
    "PYTHONHASHSEED", "CUDA_VISIBLE_DEVICES",
    "PATH", "LD_LIBRARY_PATH", "LD_PRELOAD",
)
DISTRIBUTIONS = (
    "numpy", "cupy-cuda12x", "cuda-python", "numba", "llvmlite")
MODULES = (
    "numpy", "cupy", "cuda.bindings.driver", "cuda.bindings.nvrtc", "optix",
    "numba", "llvmlite")


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _file(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        raise RuntimeError(f"host-runtime payload is not a file: {resolved}")
    return {"path": str(resolved), "bytes": resolved.stat().st_size,
            "sha256": _sha(resolved)}


def _distribution(name: str) -> dict[str, object]:
    dist = importlib.metadata.distribution(name)
    rows = []
    for item in sorted(dist.files or (), key=lambda value: str(value)):
        path = Path(dist.locate_file(item))
        if path.is_file():
            record = _file(path)
            rows.append({"relative_path": str(item).replace("\\", "/"),
                         "path": record["path"],
                         "bytes": record["bytes"], "sha256": record["sha256"]})
    encoded = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return {"name": name, "version": dist.version,
            "file_count": len(rows),
            "payload_bytes": sum(int(row["bytes"]) for row in rows),
            "tree_sha256": hashlib.sha256(encoded).hexdigest(),
            "files": rows}


def _cpu_model() -> str:
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                return line.split(":", 1)[1].strip()
    return platform.processor() or "UNKNOWN"


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: goal5802_capture_host_runtime_provenance.py OUTPUT")
    output = Path(sys.argv[1])
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    if os.environ.get("LD_PRELOAD") is not None:
        raise RuntimeError("Goal5802 host capture forbids LD_PRELOAD")
    search_path = os.environ.get("PATH")
    if not search_path or any(
            not item or not Path(item).is_absolute()
            for item in search_path.split(os.pathsep)):
        raise RuntimeError(
            "Goal5802 PATH requires nonempty absolute entries")
    loader_path = os.environ.get("LD_LIBRARY_PATH")
    if loader_path is not None and (
            not loader_path or any(
                not item or not Path(item).is_absolute()
                for item in loader_path.split(os.pathsep))):
        raise RuntimeError(
            "Goal5802 LD_LIBRARY_PATH requires nonempty absolute entries")
    modules = {}
    for name in MODULES:
        module = importlib.import_module(name)
        module_path = getattr(module, "__file__", None)
        if not module_path:
            raise RuntimeError(f"runtime module has no file identity: {name}")
        modules[name] = _file(Path(module_path))
    governors = sorted({
        path.read_text(encoding="utf-8").strip()
        for path in Path("/sys/devices/system/cpu").glob(
            "cpu[0-9]*/cpufreq/scaling_governor") if path.is_file()})
    affinity = (sorted(os.sched_getaffinity(0))
                if hasattr(os, "sched_getaffinity") else None)
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.host_runtime_provenance.v3",
        "status": "PASS__UNTIMED_EXACT_HOST_RUNTIME_CAPTURE",
        "python": {"version": sys.version, "implementation": platform.python_implementation(),
                   "executable": _file(Path(sys.executable))},
        "distributions": [_distribution(name) for name in DISTRIBUTIONS],
        "loaded_module_files": modules,
        "host": {"system": platform.system(), "release": platform.release(),
                 "machine": platform.machine(), "libc": list(platform.libc_ver()),
                 "cpu_model": _cpu_model(), "affinity": affinity,
                 "cpu_governors": governors or ["UNAVAILABLE"]},
        "thread_and_visibility_environment": {
            key: (None if key == "LD_PRELOAD" else os.environ.get(key))
            for key in THREAD_ENV_KEYS},
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    value["receipt_sha256"] = hashlib.sha256(encoded).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(json.dumps(value, indent=2, sort_keys=True).encode() + b"\n")
    print(json.dumps({"status": value["status"],
                      "receipt_sha256": value["receipt_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
