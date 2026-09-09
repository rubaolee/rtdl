#!/usr/bin/env python3
"""Build and bind the public-PyOptiX PTX for authored Particle evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

from experiments.v4_paper_apps_pyoptix.public_runtime import (
    PublicRuntime,
    _nvrtc_options,
    compile_ptx,
)


SCHEMA = "rtdl.v4.authored_particle.public_pyoptix_ptx_build.v1"
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/v4_authored_particle/pyoptix_device.cu"


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def binding(path: str | Path) -> dict[str, object]:
    value = Path(path).resolve(strict=True)
    return {
        "path": str(value),
        "bytes": value.stat().st_size,
        "sha256": sha256(value),
    }


def git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def write_new(path: Path, value: object) -> None:
    payload = (json.dumps(
        value, sort_keys=True, indent=2, allow_nan=False,
    ) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def compute_capability(value: str) -> tuple[int, int]:
    fields = value.split(".")
    if len(fields) != 2 or any(not field.isdigit() for field in fields):
        raise ValueError("compute capability must be MAJOR.MINOR")
    result = tuple(int(field) for field in fields)
    if not (1 <= result[0] <= 99 and 0 <= result[1] <= 9):
        raise ValueError("compute capability is outside the accepted range")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    if git("status", "--porcelain"):
        raise RuntimeError("authored Particle PTX build requires a clean source tree")
    output = args.output.absolute()
    manifest = args.manifest.absolute()
    if output.exists() or output.is_symlink() \
            or manifest.exists() or manifest.is_symlink():
        raise FileExistsError("authored Particle PTX outputs are create-only")
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    optix_include = args.optix_include.resolve(strict=True)
    cuda_include = args.cuda_include.resolve(strict=True)
    if not (optix_include / "optix_device.h").is_file() \
            or not (cuda_include / "cuda.h").is_file():
        raise FileNotFoundError("OptiX/CUDA headers are incomplete")
    capability = compute_capability(args.compute_capability)
    options = _nvrtc_options(
        optix_include=optix_include,
        cuda_include=cuda_include,
        compute_capability=capability,
    )
    started = time.perf_counter_ns()
    ptx = compile_ptx(
        PublicRuntime(cp=None, optix=None), SOURCE,
        optix_include=optix_include,
        cuda_include=cuda_include,
        compute_capability=capability,
    )
    compile_ns = time.perf_counter_ns() - started
    with output.open("xb") as stream:
        stream.write(ptx)
        stream.flush()
        os.fsync(stream.fileno())
    record = {
        "schema": SCHEMA,
        "status": "PASS__AUTHORED_PARTICLE_PUBLIC_PYOPTIX_PTX_BUILT",
        "source_commit": git("rev-parse", "HEAD"),
        "source_tree": git("rev-parse", "HEAD^{tree}"),
        "source_clean_after_build": not bool(git("status", "--porcelain")),
        "source": binding(SOURCE),
        "ptx": binding(output),
        "compute_capability": list(capability),
        "nvrtc_options": [item.decode("utf-8") for item in options],
        "optix_device_header": binding(optix_include / "optix_device.h"),
        "cuda_header": binding(cuda_include / "cuda.h"),
        "python_executable": str(Path(sys.executable).resolve(strict=True)),
        "python_version": platform.python_version(),
        "cuda_bindings_version": importlib.metadata.version("cuda-bindings"),
        "compile_ns_diagnostic_only": compile_ns,
        "compile_time_in_primary_timer": False,
        "formal_worker_zero_reached": False,
    }
    write_new(manifest, record)
    print(json.dumps({
        "status": record["status"],
        "manifest": str(manifest),
        "ptx": record["ptx"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
