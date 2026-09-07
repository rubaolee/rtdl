#!/usr/bin/env python3
"""Create and bind precompiled PTX for the public-PyOptiX app baselines."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import subprocess
import sys
import time
from pathlib import Path

from experiments.v4_paper_apps_pyoptix.public_runtime import (
    PublicRuntime,
    compile_ptx,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "particle_tracking": ROOT / "experiments/v4_paper_apps_pyoptix/particle_device.cu",
    "triangle_counting": ROOT
    / "experiments/v4_paper_apps_pyoptix/triangle_counting_device.cu",
    "librts": ROOT / "experiments/v4_paper_apps_pyoptix/librts_device.cu",
}


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def _compute_capability(text: str) -> tuple[int, int]:
    parts = text.split(".")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        raise ValueError("compute capability must be MAJOR.MINOR")
    major, minor = (int(part) for part in parts)
    if not (1 <= major <= 99 and 0 <= minor <= 9):
        raise ValueError("compute capability is outside the accepted range")
    return major, minor


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_root.absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    optix_include = args.optix_include.resolve(strict=True)
    cuda_include = args.cuda_include.resolve(strict=True)
    if (
        not (optix_include / "optix.h").is_file()
        or not (optix_include / "optix_device.h").is_file()
    ):
        raise FileNotFoundError("OptiX include directory lacks required headers")
    if not (cuda_include / "cuda.h").is_file():
        raise FileNotFoundError("CUDA include directory lacks cuda.h")
    if _git("status", "--porcelain"):
        raise PermissionError("PTX preparation requires a clean source checkout")
    compute_capability = _compute_capability(args.compute_capability)
    output.mkdir(parents=True)
    runtime = PublicRuntime(cp=None, optix=None)
    programs = {}
    for app, source in SOURCES.items():
        started = time.perf_counter_ns()
        ptx = compile_ptx(
            runtime,
            source,
            optix_include=optix_include,
            cuda_include=cuda_include,
            compute_capability=compute_capability,
        )
        compile_ns = time.perf_counter_ns() - started
        ptx_path = output / f"{app}.ptx"
        with ptx_path.open("xb") as stream:
            stream.write(ptx)
        programs[app] = {
            "source_path": str(source.relative_to(ROOT)),
            "source_sha256": _sha(source),
            "ptx_path": str(ptx_path),
            "ptx_sha256": _sha(ptx_path),
            "ptx_size_bytes": ptx_path.stat().st_size,
            "compile_ns_diagnostic_only": compile_ns,
        }
    manifest = {
        "schema": "rtdl.v4_paper_apps_pyoptix.prebuilt_ptx.v1",
        "status": "PASS__PREBUILT_PTX_READY_FOR_UNTIMED_DRY_RUN",
        "source_commit": _git("rev-parse", "HEAD"),
        "source_tree": _git("rev-parse", "HEAD^{tree}"),
        "source_clean_after_build": not bool(_git("status", "--porcelain")),
        "compute_capability": list(compute_capability),
        "optix_header_sha256": _sha(optix_include / "optix.h"),
        "optix_device_header_sha256": _sha(optix_include / "optix_device.h"),
        "cuda_header_sha256": _sha(cuda_include / "cuda.h"),
        "python_executable": str(Path(sys.executable).resolve(strict=True)),
        "cuda_bindings_version": importlib.metadata.version("cuda-bindings"),
        "programs": programs,
        "formal_worker_zero_reached": False,
        "performance_result_exists": False,
        "compile_time_in_primary_a_c_timer": False,
    }
    manifest_path = output / "PREBUILT_PTX_MANIFEST.json"
    with manifest_path.open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "manifest": str(manifest_path),
                "program_count": len(programs),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
