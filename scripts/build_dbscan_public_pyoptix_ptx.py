#!/usr/bin/env python3
"""Build and bind the strong public-PyOptiX DBSCAN PTX pair."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from cuda.bindings import nvrtc

from experiments.v4_paper_apps_pyoptix.public_runtime import compile_ptx


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "experiments/v4_paper_apps_pyoptix"
SOURCES = {
    "device": SOURCE_DIR / "dbscan_device.cu",
    "continuation": SOURCE_DIR / "dbscan_continuation.cu",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, check=True, text=True,
        capture_output=True,
    ).stdout.strip()


def _binding(path: Path) -> dict[str, object]:
    path = path.resolve(strict=True)
    return {
        "path": str(path),
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
    }


def _ptx_version(raw: bytes) -> str:
    match = re.search(rb"(?m)^\.version\s+([0-9]+\.[0-9]+)\s*$", raw[:4096])
    if match is None:
        raise RuntimeError("compiled output lacks a canonical PTX version")
    return match.group(1).decode("ascii")


def _gpu_inventory(uuid: str) -> dict[str, str]:
    result = subprocess.run([
        "nvidia-smi", "-i", uuid,
        "--query-gpu=uuid,name,driver_version",
        "--format=csv,noheader",
    ], check=True, text=True, capture_output=True)
    fields = [field.strip() for field in result.stdout.strip().split(",")]
    if len(fields) != 3 or fields[0] != uuid:
        raise RuntimeError("selected target GPU inventory mismatch")
    return {"uuid": fields[0], "name": fields[1], "driver": fields[2]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--gpu-uuid", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    capability = tuple(
        int(value) for value in args.compute_capability.split(","))
    if len(capability) != 2 or capability[0] <= 0 \
            or not 0 <= capability[1] <= 9:
        raise ValueError("compute capability must be an explicit major,minor pair")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    record: dict[str, object] = {
        "schema": "rtdl.nine_app.dbscan.public_pyoptix_build.v1",
        "status": "BUILD_INCOMPLETE",
        "command_argv": sys.argv,
        "source_commit": _git("rev-parse", "HEAD"),
        "source_tree": _git("rev-parse", "HEAD^{tree}"),
        "tracked_source_dirty": bool(_git(
            "status", "--porcelain", "--untracked-files=no")),
        "compute_capability": list(capability),
        "target_gpu": _gpu_inventory(args.gpu_uuid),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "gpu_execution_required_for_build": False,
        "sources": {},
        "outputs": {},
    }
    try:
        if record["tracked_source_dirty"]:
            raise RuntimeError("target PTX build requires a clean tracked source tree")
        nvrtc_status, major, minor = nvrtc.nvrtcVersion()
        if nvrtc_status.value:
            raise RuntimeError(f"NVRTC version query failed: {nvrtc_status.value}")
        record["toolchain"] = {
            "nvrtc_version": f"{major}.{minor}",
            "optix_include": str(args.optix_include.resolve(strict=True)),
            "cuda_include": str(args.cuda_include.resolve(strict=True)),
            "python": sys.version,
        }
        record["sources"] = {
            name: _binding(path) for name, path in SOURCES.items()
        }
        for name, source in SOURCES.items():
            raw = compile_ptx(
                None,
                source,
                optix_include=args.optix_include,
                cuda_include=args.cuda_include,
                compute_capability=capability,
            )
            path = output / f"{name}.ptx"
            path.write_bytes(raw)
            row = _binding(path)
            row["ptx_version"] = _ptx_version(raw)
            record["outputs"][name] = row
        record["status"] = "PASS__TWO_CANONICAL_PTX_ARTIFACTS_BUILT"
    except BaseException as error:
        record.update(
            status="FAILED__TARGET_BUILD",
            error_type=type(error).__name__,
            error=str(error),
        )
        raise
    finally:
        (output / "BUILD.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "status": record["status"],
        "output": str(output),
        "nvrtc": record["toolchain"]["nvrtc_version"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
