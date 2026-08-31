"""Create-only same-target controller for the Goal5817 three-arm matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import statistics
import subprocess
import sys
import time
from typing import Any

from experiments.goal5802_premeasurement.workload import RELATION_TASK, TRIANGLE_TASK
from experiments.goal5805_successor.protocol import validate_target_manifest

from .evaluate import evaluate
from .protocol import (
    canonical, schedule, validate_authority, validate_freeze,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Goal5817 JSON root differs: {path}")
    return value


def _validate_preflight(path: Path, *, runtime_manifest_sha256: str) -> dict[str, str]:
    resolved = path.resolve(strict=True)
    if resolved.is_symlink() or not resolved.is_file():
        raise RuntimeError("Goal5817 runtime preflight receipt is not a regular file")
    value = _read(resolved)
    if value.get("schema") != "rtdl.goal5802.formal_runtime_preflight.v1" \
            or value.get("status") != (
                "PASS__LIVE_TARGET_AND_CROSS_ARM_NVRTC_BEFORE_WORKER_ZERO") \
            or value.get("runtime_manifest_file_sha256") != runtime_manifest_sha256:
        raise RuntimeError("Goal5817 runtime preflight result differs")
    for key in (
            "clock_read_count", "registered_performance_timing_count",
            "gpu_kernel_launch_count", "formal_worker_count"):
        if value.get(key) != 0:
            raise RuntimeError(f"Goal5817 preflight zero boundary differs: {key}")
    self_sha = value.get("preflight_sha256")
    if not isinstance(self_sha, str) or len(self_sha) != 64:
        raise RuntimeError("Goal5817 runtime preflight seal differs")
    return {
        "path": str(resolved),
        "file_sha256": _sha(resolved),
        "preflight_sha256": self_sha,
    }


def _direct_command(
        row: dict[str, object], *, direct_binary: Path,
        freeze_sha: str, authority_sha: str, runtime_sha: str,
        target: dict[str, Any]) -> list[str]:
    files = target["files"]
    task = RELATION_TASK if row["task"] == "relation" else TRIANGLE_TASK
    command = [
        str(direct_binary),
        "--worker-id", str(row["worker_id"]),
        "--freeze-sha256", freeze_sha,
        "--authority-sha256", authority_sha,
        "--runtime-manifest-sha256", runtime_sha,
        "--task", task,
        "--regime", str(row["regime"]),
        "--ptx", str(files["matched_ptx"]["path"]),
        "--ptx-sha256", str(files["matched_ptx"]["sha256"]),
    ]
    if row["task"] == "relation":
        command.extend([
            "--compaction-cubin",
            str(files["relation_compaction_cubin"]["path"]),
            "--compaction-cubin-sha256",
            str(files["relation_compaction_cubin"]["sha256"]),
        ])
    return command


def _python_command(
        row: dict[str, object], *, root: Path, freeze: Path,
        target_manifest: Path, authority_sha: str) -> list[str]:
    return [
        sys.executable, "-m", "experiments.goal5817_three_arm.formal_python_worker",
        "--root", str(root),
        "--freeze", str(freeze),
        "--target-manifest", str(target_manifest),
        "--authority-sha256", authority_sha,
        "--arm", str(row["arm"]),
        "--task", str(row["task"]),
        "--regime", str(row["regime"]),
        "--worker-id", str(row["worker_id"]),
    ]


def _capability(
        row: dict[str, object], *, runtime_sha: str,
        preflight: dict[str, str]) -> bytes:
    return canonical({
        "schema": "rtdl.goal5802.live_controller_worker_capability.v1",
        "controller_pid": os.getpid(),
        "worker_id": row["worker_id"],
        "runtime_manifest_sha256": runtime_sha,
        "preflight_receipt_file_sha256": preflight["file_sha256"],
        "preflight_sha256": preflight["preflight_sha256"],
        "nonce": secrets.token_hex(32),
    }) + b"\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--direct-binary", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--runtime-preflight-receipt", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--worker-timeout-seconds", type=int, default=900)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    freeze_path = args.freeze.resolve(strict=True)
    target_path = args.target_manifest.resolve(strict=True)
    direct_binary = args.direct_binary.resolve(strict=True)
    authority_path = args.authority.resolve(strict=True)
    output = args.output_root.absolute()
    if output.exists():
        raise RuntimeError("Goal5817 output root already exists")
    freeze = _read(freeze_path)
    target = _read(target_path)
    authority = _read(authority_path)
    validate_freeze(freeze, rehash=True, root=root)
    validate_target_manifest(target, rehash=True)
    validate_authority(
        authority, freeze_path=freeze_path, target_manifest_path=target_path,
        direct_binary_path=direct_binary)
    runtime_manifest_path = Path(target["files"]["runtime_manifest"]["path"])
    runtime_sha = _sha(runtime_manifest_path)
    preflight = _validate_preflight(
        args.runtime_preflight_receipt, runtime_manifest_sha256=runtime_sha)
    freeze_sha = _sha(freeze_path)
    authority_sha = _sha(authority_path)

    output.mkdir(parents=True)
    worker_root = output / "workers"
    worker_root.mkdir()
    workers: list[dict[str, Any]] = []
    for planned in schedule():
        row = dict(planned)
        worker_dir = worker_root / str(row["worker_id"])
        worker_dir.mkdir()
        cache_root = worker_dir / "isolated_caches"
        cache_paths = {
            "home": worker_dir / "home",
            "tmp": worker_dir / "tmp",
            "xdg": cache_root / "xdg",
            "cuda": cache_root / "cuda",
            "cupy": cache_root / "cupy",
            "optix": cache_root / "optix",
        }
        for path in cache_paths.values():
            path.mkdir(parents=True)
        environment = dict(os.environ)
        environment.update({
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "PYTHONPATH": os.pathsep.join((
                str(root), str((root / "src").resolve(strict=True)))),
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
            "GOAL5802_FORMAL_CONTROLLER_PID": str(os.getpid()),
            "GOAL5802_EXECUTION_AUTHORITY_SHA256": authority_sha,
            "GOAL5802_RUNTIME_MANIFEST_SHA256": runtime_sha,
            "GOAL5802_FREEZE_FILE_SHA256": freeze_sha,
            "GOAL5802_RUNTIME_PREFLIGHT_RECEIPT_PATH": preflight["path"],
            "GOAL5802_RUNTIME_PREFLIGHT_RECEIPT_FILE_SHA256":
                preflight["file_sha256"],
            "GOAL5802_RUNTIME_PREFLIGHT_SHA256": preflight["preflight_sha256"],
        })
        direct = row["arm"] == "DIRECT"
        command = (
            _direct_command(
                row, direct_binary=direct_binary, freeze_sha=freeze_sha,
                authority_sha=authority_sha, runtime_sha=runtime_sha,
                target=target)
            if direct else
            _python_command(
                row, root=root, freeze=freeze_path,
                target_manifest=target_path, authority_sha=authority_sha)
        )
        (worker_dir / "command.json").write_bytes(
            json.dumps(command, sort_keys=True).encode("utf-8") + b"\n")
        environment["GOAL5802_CONTROLLER_ENVELOPE_START_NS"] = str(
            time.perf_counter_ns())
        process = subprocess.Popen(
            command, cwd=root, env=environment,
            stdin=subprocess.PIPE if direct else subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=(os.name == "posix"))
        try:
            stdout, stderr = process.communicate(
                input=_capability(row, runtime_sha=runtime_sha, preflight=preflight)
                if direct else None,
                timeout=args.worker_timeout_seconds)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            (worker_dir / "stdout.bin").write_bytes(stdout)
            (worker_dir / "stderr.bin").write_bytes(stderr)
            raise RuntimeError(f"Goal5817 worker timed out: {row['worker_id']}")
        (worker_dir / "stdout.bin").write_bytes(stdout)
        (worker_dir / "stderr.bin").write_bytes(stderr)
        if process.returncode != 0:
            failure = {
                "schema": "rtdl.goal5817.controller_failure.v1",
                "worker_id": row["worker_id"],
                "exit_code": process.returncode,
                "retry_replacement_row_drop": False,
            }
            (output / "TERMINAL_FAILURE.json").write_bytes(
                json.dumps(failure, indent=2, sort_keys=True).encode("utf-8") + b"\n")
            raise RuntimeError(f"Goal5817 worker failed: {row['worker_id']}")
        parsed = json.loads(stdout)
        if parsed.get("status") != "PASS" \
                or parsed.get("worker_id") != row["worker_id"]:
            raise RuntimeError(f"Goal5817 worker receipt differs: {row['worker_id']}")
        if direct:
            durations = parsed.get("execute_or_regime_durations_ns")
            expected_count = 64 if row["regime"] == "STEADY_E2E" else 1
            if not isinstance(durations, list) or len(durations) != expected_count \
                    or any(type(value) is not int or value <= 0 for value in durations) \
                    or parsed.get("correctness", {}).get("oracle_exact") is not True:
                raise RuntimeError(f"Goal5817 Direct metric differs: {row['worker_id']}")
            metric_ns = int(statistics.median(durations))
            timing_count = len(durations)
        else:
            metric_ns = parsed.get("metric_ns")
            timing_count = parsed.get("registered_performance_timing_count")
            if parsed.get("pid") != process.pid \
                    or type(metric_ns) is not int or metric_ns <= 0:
                raise RuntimeError(f"Goal5817 Python metric differs: {row['worker_id']}")
        cache_files = sorted(
            path.relative_to(cache_root).as_posix()
            for path in cache_root.rglob("*") if path.is_file())
        if cache_files:
            raise RuntimeError(f"Goal5817 worker populated cache: {row['worker_id']}")
        workers.append({
            **row,
            "pid": process.pid,
            "metric_ns": metric_ns,
            "registered_performance_timing_count": timing_count,
            "raw_result": parsed,
            "isolated_cache_files_after": cache_files,
        })

    controller = {
        "schema": "rtdl.goal5817.three_arm_controller_result.v1",
        "status": "COMPLETE__NO_RETRY_REPLACEMENT_OR_ROW_DROP",
        "workers": workers,
        "formal_worker_count": len(workers),
        "registered_performance_timing_count": sum(
            row["registered_performance_timing_count"] for row in workers),
        "freeze_file_sha256": freeze_sha,
        "target_manifest_file_sha256": _sha(target_path),
        "direct_binary_file_sha256": _sha(direct_binary),
        "authority_file_sha256": authority_sha,
        "runtime_preflight_receipt_file_sha256": preflight["file_sha256"],
        "controlled_python_import_roots": [
            str(root), str((root / "src").resolve(strict=True)),
        ],
    }
    controller_path = output / "controller.json"
    controller_path.write_bytes(
        json.dumps(controller, indent=2, allow_nan=False, sort_keys=True).encode("utf-8")
        + b"\n")
    evaluation = evaluate(controller)
    (output / "evaluation.json").write_bytes(
        json.dumps(evaluation, indent=2, allow_nan=False, sort_keys=True).encode("utf-8")
        + b"\n")
    print(json.dumps({
        "status": controller["status"],
        "formal_worker_count": len(workers),
        "registered_performance_timing_count":
            controller["registered_performance_timing_count"],
        "row_count": evaluation["row_count"],
        "gated_pass_count": evaluation["gated_pass_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
