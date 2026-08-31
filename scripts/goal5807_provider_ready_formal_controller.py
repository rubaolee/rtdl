#!/usr/bin/env python3
"""Create-only, no-recovery controller for Goal5807 confirmatory workers."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from scripts.goal5807_provider_ready_formal_protocol import (
    TOTAL_WORKERS,
    REGISTERED_TIMINGS_PER_WORKER,
    TOTAL_REGISTERED_TIMINGS,
    arm_order,
    canonical,
    create_only,
    expected_worker_coordinates,
    file_sha256,
    read_object,
    validate_contract,
    value_sha256,
    worker_id,
)
from scripts.goal5807_provider_ready_formal_worker import WORKER_SCHEMA


ROW_SCHEMA = "rtdl.goal5807.provider_ready_formal_row.v2"
CONTROLLER_SCHEMA = "rtdl.goal5807.provider_ready_formal_controller.v2"
EXECUTION_TOKEN = "GOAL5807_OWNER_AUTHORIZED_EXACT_FROZEN_CONTRACT"


def _write_bytes_create_only(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(value)


def _subprocess_launcher(
    *, root: Path, contract_path: Path, task: str, block: int,
    position: int, arm: str, directory: Path,
) -> dict[str, Any]:
    identity = worker_id(task, block, position, arm)
    cache_root = directory / "isolated_caches"
    cache_paths = {
        name: cache_root / name
        for name in ("cuda", "cupy", "optix", "xdg", "tmp")
    }
    for path in cache_paths.values():
        path.mkdir(parents=True, exist_ok=False)
    command = [
        sys.executable,
        "-m",
        "scripts.goal5807_provider_ready_formal_worker",
        "--root",
        str(root),
        "--contract",
        str(contract_path),
        "--arm",
        arm,
        "--task",
        task,
        "--worker-id",
        identity,
    ]
    environment = dict(os.environ)
    existing_pythonpath = environment.get("PYTHONPATH", "")
    pythonpath = os.pathsep.join(
        item for item in (str(root), str(root / "src"), existing_pythonpath)
        if item)
    environment.update({
        "PYTHONPATH": pythonpath,
        "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
        "CUDA_CACHE_PATH": str(cache_paths["cuda"]),
        "CUDA_CACHE_DISABLE": "1",
        "CUPY_CACHE_DIR": str(cache_paths["cupy"]),
        "OPTIX_CACHE_PATH": str(cache_paths["optix"]),
        "OPTIX_CACHE_ENABLED": "0",
        "OPTIX_CACHE_MAXSIZE": "0",
        "RTDL_DISABLE_CUBIN_CACHE": "1",
        "XDG_CACHE_HOME": str(cache_paths["xdg"]),
        "TMPDIR": str(cache_paths["tmp"]),
    })
    process = subprocess.Popen(
        command,
        cwd=root,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    return {
        "command": command,
        "pid": process.pid,
        "returncode": process.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "cache_files_after": sorted(
            path.relative_to(directory).as_posix()
            for path in cache_root.rglob("*") if path.is_file()),
    }


def _valid_worker_result(
    result: object, *, expected_id: str, task: str, arm: str,
    pid: int, contract_sha256: str,
) -> bool:
    if not isinstance(result, Mapping):
        return False
    body = dict(result)
    seal = body.pop("worker_receipt_sha256", None)
    primary = result.get(
        "primary_app_prepare_plus_first_exact_execute_ns")
    return (
        seal == value_sha256(body)
        and result.get("schema") == WORKER_SCHEMA
        and result.get("status") == "PASS__EXACT_ORACLE_AND_PHASE_LEDGER"
        and result.get("worker_id") == expected_id
        and result.get("task") == task
        and result.get("arm") == arm
        and result.get("pid") == pid
        and result.get("contract_sha256") == contract_sha256
        and type(primary) is int and primary > 0
        and result.get("registered_performance_timing_count") == (
            REGISTERED_TIMINGS_PER_WORKER)
        and isinstance(result.get("registered_timing_ns"), Mapping)
        and result.get("formal_worker_count") == 1
        and isinstance(result.get("pilot_receipt"), Mapping)
    )


def execute_schedule(
    *, root: Path, contract_path: Path, output: Path,
    launcher: Callable[..., dict[str, Any]] = _subprocess_launcher,
) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("Goal5807 formal output root already exists")
    output.mkdir(parents=True)
    rows_root = output / "rows"
    workers_root = output / "workers"
    rows_root.mkdir()
    workers_root.mkdir()
    contract_sha = file_sha256(contract_path)
    row_hashes: dict[str, str] = {}
    pids: set[int] = set()
    completed = 0
    for task, block, position, arm in expected_worker_coordinates():
        identity = worker_id(task, block, position, arm)
        directory = workers_root / identity
        directory.mkdir()
        launched = launcher(
            root=root, contract_path=contract_path, task=task, block=block,
            position=position, arm=arm, directory=directory)
        command = launched.get("command")
        stdout = launched.get("stdout")
        stderr = launched.get("stderr")
        pid = launched.get("pid")
        returncode = launched.get("returncode")
        if not isinstance(command, list) \
                or not isinstance(stdout, bytes) \
                or not isinstance(stderr, bytes) \
                or type(pid) is not int or type(returncode) is not int:
            raise RuntimeError("Goal5807 launcher result shape differs")
        create_only(directory / "command.json", command)
        _write_bytes_create_only(directory / "stdout.bin", stdout)
        _write_bytes_create_only(directory / "stderr.bin", stderr)
        result: object = None
        try:
            result = json.loads(stdout) if stdout.strip() else None
        except (UnicodeDecodeError, json.JSONDecodeError):
            result = None
        observed_registered_timing_count = (
            result.get("registered_performance_timing_count", 0)
            if isinstance(result, Mapping) else 0)
        if type(observed_registered_timing_count) is not int \
                or observed_registered_timing_count < 0:
            observed_registered_timing_count = 0
        passed = (
            returncode == 0
            and stderr == b""
            and pid not in pids
            and _valid_worker_result(
                result, expected_id=identity, task=task, arm=arm, pid=pid,
                contract_sha256=contract_sha))
        row = {
            "schema": ROW_SCHEMA,
            "status": "PASS" if passed else "FAIL",
            "contract_sha256": contract_sha,
            "worker_id": identity,
            "task": task,
            "block": block,
            "position": position,
            "arm": arm,
            "pid": pid,
            "returncode": returncode,
            "stdout_sha256": file_sha256(directory / "stdout.bin"),
            "stderr_sha256": file_sha256(directory / "stderr.bin"),
            "cache_files_after": launched.get("cache_files_after", []),
            "worker_result": result,
            "registered_performance_timing_count": (
                observed_registered_timing_count),
        }
        row_path = rows_root / f"{identity}.json"
        create_only(row_path, row)
        row_hashes[row_path.name] = file_sha256(row_path)
        if not passed:
            failure = {
                "schema": "rtdl.goal5807.provider_ready_terminal_failure.v1",
                "status": "TERMINAL__NO_RETRY_RESUME_REPLACEMENT_OR_DROP",
                "contract_sha256": contract_sha,
                "failed_worker_id": identity,
                "completed_pass_worker_count": completed,
                "failed_worker_registered_timing_count": (
                    observed_registered_timing_count),
                "preserved_observed_registered_timing_count": (
                    completed * REGISTERED_TIMINGS_PER_WORKER
                    + observed_registered_timing_count),
                "partial_result_reuse_authorized": False,
                "retry_count": 0,
                "resume_count": 0,
                "replacement_count": 0,
                "row_drop_count": 0,
            }
            create_only(output / "TERMINAL_FAILURE.json", failure)
            raise RuntimeError(f"Goal5807 formal worker failed: {identity}")
        pids.add(pid)
        completed += 1
        print(f"{task} block {block} position {position} complete", flush=True)
    if completed != TOTAL_WORKERS or len(pids) != TOTAL_WORKERS:
        raise RuntimeError("Goal5807 formal worker/PID universe differs")
    controller = {
        "schema": CONTROLLER_SCHEMA,
        "status": "COMPLETE__NO_RETRY_RESUME_REPLACEMENT_OR_DROP",
        "contract_sha256": contract_sha,
        "worker_count": completed,
        "unique_worker_pid_count": len(pids),
        "registered_performance_timing_count": TOTAL_REGISTERED_TIMINGS,
        "retry_count": 0,
        "resume_count": 0,
        "replacement_count": 0,
        "row_drop_count": 0,
        "row_sha256": dict(sorted(row_hashes.items())),
    }
    create_only(output / "controller.json", controller)
    return controller


def run_controller(args: argparse.Namespace) -> dict[str, Any]:
    if args.execute_token != EXECUTION_TOKEN:
        raise RuntimeError("Goal5807 explicit owner execution token is absent")
    root = args.root.resolve(strict=True)
    contract_path = args.contract.resolve(strict=True)
    contract = read_object(contract_path)
    files = validate_contract(contract, root, rehash=True)
    if files["formal_controller"] != Path(__file__).resolve(strict=True):
        raise RuntimeError("Goal5807 formal controller path differs")
    return execute_schedule(
        root=root, contract_path=contract_path, output=args.output.resolve())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute-token", required=True)
    result = run_controller(parser.parse_args())
    sys.stdout.buffer.write(canonical(result) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
