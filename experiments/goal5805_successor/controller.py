"""Create-only no-retry process controller for Goal5805."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from .evaluate import evaluate_file
from .protocol import (
    BLOCK_COUNT, TASKS, validate_authority, validate_freeze,
    validate_target_manifest,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Goal5805 JSON root differs: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    freeze_path = args.freeze.resolve(strict=True)
    target_path = args.target_manifest.resolve(strict=True)
    authority_path = args.authority.resolve(strict=True)
    output = args.output_root.absolute()
    if output.exists():
        raise RuntimeError("Goal5805 output root already exists")
    validate_freeze(_read(freeze_path), root, rehash=True)
    validate_target_manifest(_read(target_path), rehash=True)
    validate_authority(
        _read(authority_path), freeze_file_sha256=_sha(freeze_path),
        target_manifest_file_sha256=_sha(target_path))
    output.mkdir(parents=True)
    worker_root = output / "workers"
    worker_root.mkdir()
    rows = []
    ordinal = 0
    for task in TASKS:
        for block in range(BLOCK_COUNT):
            order = (("RTDL", "PYOPTIX", "PYOPTIX", "RTDL")
                     if block % 2 == 0 else
                     ("PYOPTIX", "RTDL", "RTDL", "PYOPTIX"))
            for position, arm in enumerate(order):
                worker_id = f"{task}-b{block:02d}-p{position}-{arm.lower()}"
                directory = worker_root / worker_id
                directory.mkdir()
                cache_root = directory / "isolated_caches"
                cache_paths = {
                    "home": directory / "home",
                    "tmp": directory / "tmp",
                    "xdg": cache_root / "xdg",
                    "cuda": cache_root / "cuda",
                    "cupy": cache_root / "cupy",
                    "optix": cache_root / "optix",
                }
                for path in cache_paths.values():
                    path.mkdir(parents=True)
                command = [
                    sys.executable, "-m",
                    "experiments.goal5805_successor.formal_worker",
                    "--root", str(root), "--freeze", str(freeze_path),
                    "--target-manifest", str(target_path),
                    "--authority", str(authority_path),
                    "--arm", arm, "--task", task, "--worker-id", worker_id,
                ]
                environment = dict(os.environ)
                environment.update({
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "HOME": str(cache_paths["home"]),
                    "TMP": str(cache_paths["tmp"]),
                    "TEMP": str(cache_paths["tmp"]),
                    "TMPDIR": str(cache_paths["tmp"]),
                    "XDG_CACHE_HOME": str(cache_paths["xdg"]),
                    "CUDA_CACHE_PATH": str(cache_paths["cuda"]),
                    "CUDA_CACHE_DISABLE": "1",
                    "CUPY_CACHE_DIR": str(cache_paths["cupy"]),
                    "OPTIX_CACHE_PATH": str(cache_paths["optix"]),
                    "OPTIX_CACHE_ENABLED": "0",
                    "OPTIX_CACHE_MAXSIZE": "0",
                    "RTDL_DISABLE_CUBIN_CACHE": "1",
                })
                (directory / "command.json").write_bytes(
                    json.dumps(command, sort_keys=True).encode("utf-8") + b"\n")
                completed = subprocess.run(
                    command, cwd=root, env=environment,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    check=False)
                (directory / "stdout.bin").write_bytes(completed.stdout)
                (directory / "stderr.bin").write_bytes(completed.stderr)
                if completed.returncode != 0:
                    failure = {
                        "schema": "rtdl.goal5805.controller_failure.v1",
                        "worker_id": worker_id, "exit_code": completed.returncode,
                        "retry_replacement_row_drop": False,
                    }
                    (output / "TERMINAL_FAILURE.json").write_bytes(json.dumps(
                        failure, indent=2, sort_keys=True).encode("utf-8") + b"\n")
                    raise RuntimeError(f"Goal5805 worker failed: {worker_id}")
                result = json.loads(completed.stdout)
                if result.get("status") != "PASS" or result.get("worker_id") != worker_id:
                    raise RuntimeError(f"Goal5805 worker receipt differs: {worker_id}")
                cache_files = sorted(
                    path.relative_to(directory).as_posix()
                    for path in cache_root.rglob("*") if path.is_file())
                if cache_files:
                    raise RuntimeError(
                        f"Goal5805 worker populated an isolated cache: {worker_id}")
                rows.append({
                    "ordinal": ordinal, "task": task, "block": block,
                    "position": position, "arm": arm, "result": result,
                    "isolated_cache_files_after": cache_files,
                })
                ordinal += 1
    controller = {
        "schema": "rtdl.goal5805.formal_controller_result.v1",
        "status": "COMPLETE__NO_RETRY_OR_REPLACEMENT",
        "workers": rows,
        "formal_worker_count": len(rows),
        "registered_performance_timing_count": sum(
            row["result"]["registered_performance_timing_count"] for row in rows),
        "freeze_file_sha256": _sha(freeze_path),
        "target_manifest_file_sha256": _sha(target_path),
        "authority_file_sha256": _sha(authority_path),
    }
    controller_path = output / "controller.json"
    controller_path.write_bytes(json.dumps(
        controller, indent=2, allow_nan=False, sort_keys=True).encode("utf-8") + b"\n")
    evaluation = evaluate_file(controller_path, output / "evaluation.json")
    print(json.dumps({
        "status": controller["status"],
        "formal_worker_count": len(rows),
        "registered_performance_timing_count":
            controller["registered_performance_timing_count"],
        "pass_count": evaluation["pass_count"],
        "row_count": evaluation["row_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
