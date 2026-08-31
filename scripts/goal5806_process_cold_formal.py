#!/usr/bin/env python3
"""Create-only formal controller for the Goal5806 process-cold regime."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def _write_create_only(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(_canonical(value) + b"\n")


def _verified_files(contract: dict[str, object]) -> dict[str, Path]:
    files = contract.get("files")
    if not isinstance(files, dict):
        raise ValueError("formal contract lacks files")
    result: dict[str, Path] = {}
    expected_names = {
        "formal_controller", "formal_evaluator", "process_cold_child", "candidate_manifest",
        "trust_root", "trust_head", "trust_package", "native_library",
        "matched_ptx", "relation_compaction_cubin",
    }
    if set(files) != expected_names:
        raise ValueError("formal contract file universe differs")
    for name in sorted(expected_names):
        descriptor = files[name]
        if not isinstance(descriptor, dict) or set(descriptor) != {
                "path", "sha256", "bytes"}:
            raise ValueError(f"formal file descriptor invalid: {name}")
        path = Path(str(descriptor["path"])).resolve(strict=True)
        if path.stat().st_size != descriptor["bytes"] or _sha(path) != descriptor["sha256"]:
            raise ValueError(f"formal file identity differs: {name}")
        result[name] = path
    if result["formal_controller"] != Path(__file__).resolve(strict=True):
        raise ValueError("formal controller path differs")
    return result


def _validate_contract(contract: dict[str, object]) -> None:
    if contract.get("schema") != "rtdl.goal5806.process_cold_formal_contract.v1":
        raise ValueError("formal contract schema differs")
    required = {
        "schema", "goal", "created_after_pilot", "owner_authorized",
        "files", "matrix", "cache_policy", "timer_boundary",
        "expected_output_sha256", "statistics", "claim_boundary",
        "immutable_negative_result",
    }
    if set(contract) != required:
        raise ValueError("formal contract field universe differs")
    if contract["goal"] != "GOAL5806" \
            or contract["created_after_pilot"] is not True \
            or contract["owner_authorized"] is not True:
        raise ValueError("formal contract governance differs")
    matrix = contract["matrix"]
    if matrix != {
            "tasks": ["relation", "triangle"],
            "arms": ["rtdl", "pyoptix"],
            "blocks_per_task": 32,
            "workers_per_block": 2,
            "total_workers": 128,
            "schedule": "ABBA_BY_BLOCK_PARITY",
            "retry_count": 0,
            "replacement_count": 0,
            "row_drop_count": 0,
            "registered_timings_per_worker": 1}:
        raise ValueError("formal matrix differs")
    if contract["cache_policy"] != {
            "CUDA_CACHE_DISABLE": "1",
            "OPTIX_CACHE_ENABLED": "0",
            "OPTIX_CACHE_MAXSIZE": "0",
            "private_cache_root_per_worker": True}:
        raise ValueError("formal cache policy differs")
    if contract["timer_boundary"] != (
            "PARENT_BEFORE_PROCESS_SPAWN_TO_CHILD_FIXED_MARKER_AFTER_"
            "ONE_EXACT_EXECUTE_AND_CLOSE"):
        raise ValueError("formal timer boundary differs")


def _run(args: argparse.Namespace) -> int:
    contract_path = args.contract.resolve(strict=True)
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    _validate_contract(contract)
    files = _verified_files(contract)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    rows_dir = output / "rows"
    rows_dir.mkdir()
    cache_root = output / "worker_caches"
    cache_root.mkdir()
    expected_outputs = contract["expected_output_sha256"]
    rows: list[dict[str, object]] = []
    pids: set[int] = set()
    for task in contract["matrix"]["tasks"]:
        for block in range(contract["matrix"]["blocks_per_task"]):
            order = ("rtdl", "pyoptix") if block % 2 == 0 else ("pyoptix", "rtdl")
            for position, arm in enumerate(order):
                stem = f"{task}_b{block:02d}_p{position}_{arm}"
                cache = cache_root / stem
                for name in ("cuda", "cupy", "optix", "xdg"):
                    (cache / name).mkdir(parents=True, exist_ok=False)
                env = dict(os.environ)
                env.update({
                    "PYTHONHASHSEED": "0",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "CUDA_CACHE_PATH": str(cache / "cuda"),
                    "CUDA_CACHE_DISABLE": "1",
                    "CUPY_CACHE_DIR": str(cache / "cupy"),
                    "OPTIX_CACHE_PATH": str(cache / "optix"),
                    "OPTIX_CACHE_ENABLED": "0",
                    "OPTIX_CACHE_MAXSIZE": "0",
                    "XDG_CACHE_HOME": str(cache / "xdg"),
                })
                command = [
                    sys.executable, str(files["process_cold_child"]), "child",
                    "--arm", arm, "--task", task,
                    "--manifest", str(files["candidate_manifest"]),
                    "--trust-root", str(files["trust_root"]),
                    "--trust-head", str(files["trust_head"]),
                    "--trust-package", str(files["trust_package"]),
                    "--native", str(files["native_library"]),
                    "--ptx", str(files["matched_ptx"]),
                    "--compaction-cubin", str(files["relation_compaction_cubin"]),
                ]
                start = time.perf_counter_ns()
                process = subprocess.Popen(
                    command, env=env, text=True, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, bufsize=1)
                if process.pid in pids:
                    raise RuntimeError("formal worker PID was reused")
                pids.add(process.pid)
                assert process.stdout is not None and process.stderr is not None
                marker = process.stdout.readline()
                primary_ns = time.perf_counter_ns() - start
                stdout_tail = process.stdout.read()
                stderr = process.stderr.read()
                returncode = process.wait()
                child = json.loads(stdout_tail) if stdout_tail.strip() else None
                passed = (
                    returncode == 0
                    and marker == "GOAL5806_BOUNDARY\n"
                    and stderr == ""
                    and isinstance(child, dict)
                    and child.get("schema") == "rtdl.goal5806.process_cold_child.v2"
                    and child.get("task") == task
                    and child.get("arm") == arm
                    and child.get("status_ok") is True
                    and child.get("output_sha256") == expected_outputs[task]
                    and child.get("output_count") == (4096 if task == "relation" else 1)
                )
                row = {
                    "schema": "rtdl.goal5806.process_cold_formal_row.v1",
                    "contract_sha256": _sha(contract_path),
                    "task": task,
                    "block": block,
                    "position": position,
                    "arm": arm,
                    "worker_pid": process.pid,
                    "primary_process_cold_ns": primary_ns,
                    "registered_performance_timing_count": 1,
                    "boundary_marker": marker.rstrip("\n"),
                    "returncode": returncode,
                    "stderr": stderr,
                    "child": child,
                    "status": "PASS" if passed else "FAIL",
                }
                _write_create_only(rows_dir / f"{stem}.json", row)
                rows.append(row)
                if not passed:
                    failure = {
                        "schema": "rtdl.goal5806.process_cold_terminal_failure.v1",
                        "contract_sha256": _sha(contract_path),
                        "failed_row": stem,
                        "completed_worker_count": len(rows),
                        "registered_performance_timing_count": len(rows),
                        "retry_count": 0,
                        "replacement_count": 0,
                    }
                    _write_create_only(output / "TERMINAL_FAILURE.json", failure)
                    raise RuntimeError(f"formal process-cold row failed: {stem}")
            print(f"{task} block {block} complete", flush=True)
    controller = {
        "schema": "rtdl.goal5806.process_cold_formal_controller.v1",
        "status": "COMPLETE",
        "contract_sha256": _sha(contract_path),
        "worker_count": len(rows),
        "unique_worker_pid_count": len(pids),
        "registered_performance_timing_count": len(rows),
        "retry_count": 0,
        "replacement_count": 0,
        "row_drop_count": 0,
        "row_sha256": {
            path.name: _sha(path) for path in sorted(rows_dir.glob("*.json"))},
    }
    _write_create_only(output / "controller.json", controller)
    print(_canonical(controller).decode("ascii"))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return _run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
