#!/usr/bin/env python3
"""Independent raw-worker recount and phase decomposition for Goal5805.

This post-run tool intentionally imports no Goal5805 experiment module.  It
reconstructs the frozen paired-block statistic directly from the 128 worker
stdout files and separately exposes lifecycle phase ratios for diagnosis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import statistics
from typing import Any


TASKS = ("relation", "triangle")
REGIMES = (
    ("DEPLOYMENT_COLD", "deployment_cold_ns", 1.10),
    ("PREPARE", "prepare_ns", 1.10),
    ("STEADY_E2E", "steady_median_ns", 1.05),
)
PHASES = (
    ("LOAD", "load_ns"),
    ("PREPARE", "prepare_ns"),
    ("FIRST_EXECUTE", "first_execute_ns"),
    ("DEPLOYMENT_COLD", "deployment_cold_ns"),
    ("STEADY_E2E", "steady_median_ns"),
)
WORKER_RE = re.compile(
    r"^(relation|triangle)-b([0-9]{2})-p([0-3])-(rtdl|pyoptix)$")


def canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def percentile(values: list[float], probability: float) -> float:
    return values[int(probability * (len(values) - 1))]


def block_statistic(
        workers: list[dict[str, Any]], *, task: str, metric: str,
        seed: int) -> dict[str, Any]:
    ratios: list[float] = []
    blocks: list[dict[str, Any]] = []
    for block in range(16):
        selected = [row for row in workers
                    if row["task"] == task and row["block"] == block]
        arm_values: dict[str, float] = {}
        for arm in ("RTDL", "PYOPTIX"):
            values = [row["result"][metric] for row in selected
                      if row["arm"] == arm]
            if len(values) != 2 or any(type(value) is not int or value <= 0
                                       for value in values):
                raise RuntimeError(
                    f"raw metric multiplicity/value differs: {task}/{block}/{arm}/{metric}")
            arm_values[arm] = float(statistics.median(values))
        ratio = arm_values["RTDL"] / arm_values["PYOPTIX"]
        ratios.append(ratio)
        blocks.append({"block": block, **arm_values, "ratio": ratio})
    point = float(statistics.median(ratios))
    generator = random.Random(seed)
    draws = sorted(float(statistics.median(
        [ratios[generator.randrange(16)] for _ in range(16)]))
        for _ in range(10_000))
    return {
        "rtdl_over_pyoptix": point,
        "ci95": [percentile(draws, 0.025), percentile(draws, 0.975)],
        "blocks": blocks,
    }


def load_raw(matrix: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    worker_root = matrix / "workers"
    directories = sorted(
        (path for path in worker_root.iterdir() if path.is_dir()),
        key=lambda path: path.name.encode("utf-8"))
    if len(directories) != 128:
        raise RuntimeError(f"raw worker directory count differs: {len(directories)}")
    workers: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []
    pids: set[int] = set()
    for directory in directories:
        match = WORKER_RE.fullmatch(directory.name)
        if match is None:
            raise RuntimeError(f"raw worker name differs: {directory.name}")
        task, block_text, position_text, arm_text = match.groups()
        block = int(block_text); position = int(position_text)
        expected_order = (
            ("RTDL", "PYOPTIX", "PYOPTIX", "RTDL") if block % 2 == 0
            else ("PYOPTIX", "RTDL", "RTDL", "PYOPTIX"))
        arm = arm_text.upper()
        if arm != expected_order[position]:
            raise RuntimeError(f"raw ABBA order differs: {directory.name}")
        stdout_path = directory / "stdout.bin"
        stderr_path = directory / "stderr.bin"
        command_path = directory / "command.json"
        stdout = stdout_path.read_bytes()
        stderr = stderr_path.read_bytes()
        command = command_path.read_bytes()
        if stderr or not stdout or stdout.count(b"\n") != 1:
            raise RuntimeError(f"raw worker stream differs: {directory.name}")
        result = json.loads(stdout)
        if not isinstance(result, dict) \
                or result.get("schema") != "rtdl.goal5805.formal_worker_result.v1" \
                or result.get("status") != "PASS" \
                or result.get("worker_id") != directory.name \
                or result.get("task") != task \
                or result.get("arm") != arm \
                or result.get("formal_worker_count") != 1 \
                or result.get("registered_performance_timing_count") != 66 \
                or not isinstance(result.get("steady_ns"), list) \
                or len(result["steady_ns"]) != 64 \
                or any(type(value) is not int or value <= 0
                       for value in result["steady_ns"]):
            raise RuntimeError(f"raw worker receipt differs: {directory.name}")
        if result["deployment_cold_ns"] != (
                result["load_ns"] + result["prepare_ns"]
                + result["first_execute_ns"]):
            raise RuntimeError(f"raw cold phase sum differs: {directory.name}")
        if result["steady_median_ns"] != int(statistics.median(
                result["steady_ns"])):
            raise RuntimeError(f"raw steady median differs: {directory.name}")
        pid = result.get("pid")
        if type(pid) is not int or pid <= 0 or pid in pids:
            raise RuntimeError(f"raw PID identity differs: {directory.name}")
        pids.add(pid)
        cache_files = sorted(
            path.relative_to(directory).as_posix()
            for path in (directory / "isolated_caches").rglob("*")
            if path.is_file())
        if cache_files:
            raise RuntimeError(f"raw isolated cache populated: {directory.name}")
        workers.append({
            "task": task, "block": block, "position": position,
            "arm": arm, "result": result,
        })
        for role, path, payload in (
                ("command", command_path, command),
                ("stdout", stdout_path, stdout),
                ("stderr", stderr_path, stderr)):
            files.append({
                "worker_id": directory.name, "role": role,
                "path": path.relative_to(matrix).as_posix(),
                "bytes": len(payload), "sha256": sha(payload),
            })
    return workers, files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    matrix = args.matrix.resolve(strict=True)
    evaluation_path = args.evaluation.resolve(strict=True)
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    workers, files = load_raw(matrix)
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    primary_rows: list[dict[str, Any]] = []
    for task_index, task in enumerate(TASKS):
        for regime_index, (regime, metric, threshold) in enumerate(REGIMES):
            row = block_statistic(
                workers, task=task, metric=metric,
                seed=58_050_000 + task_index * 10 + regime_index)
            row.update({
                "task": task, "regime": regime, "threshold": threshold,
                "pass": row["rtdl_over_pyoptix"] <= threshold
                and row["ci95"][1] <= threshold,
            })
            primary_rows.append(row)
    if primary_rows != evaluation.get("rows"):
        raise RuntimeError("independent raw primary rows differ from evaluation")
    phase_rows: list[dict[str, Any]] = []
    for task_index, task in enumerate(TASKS):
        for phase_index, (phase, metric) in enumerate(PHASES):
            row = block_statistic(
                workers, task=task, metric=metric,
                seed=58_059_000 + task_index * 10 + phase_index)
            row.update({"task": task, "phase": phase})
            phase_rows.append(row)
    result: dict[str, Any] = {
        "schema": "rtdl.goal5805.independent_raw_recount.v1",
        "status": "PASS__RAW_WORKERS_RECOUNT_PRIMARY_BYTE_EXACT",
        "primary_evaluation_file_sha256": sha(evaluation_path.read_bytes()),
        "primary_rows": primary_rows,
        "primary_rows_exact_match": True,
        "phase_rows_postresult_diagnostic_only": phase_rows,
        "raw_worker_file_manifest": files,
        "raw_worker_file_count": len(files),
        "raw_worker_payload_bytes": sum(row["bytes"] for row in files),
        "formal_worker_count": len(workers),
        "unique_pid_count": len({row["result"]["pid"] for row in workers}),
        "registered_performance_timing_count": sum(
            row["result"]["registered_performance_timing_count"]
            for row in workers),
        "pass_count": sum(row["pass"] for row in primary_rows),
        "row_count": len(primary_rows),
        "all_six_pass": all(row["pass"] for row in primary_rows),
        "retry_replacement_row_drop": False,
    }
    result["recount_sha256"] = sha(canonical(result))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(
        result, allow_nan=False, indent=2, sort_keys=True,
    ).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": result["status"],
        "formal_worker_count": result["formal_worker_count"],
        "registered_performance_timing_count":
            result["registered_performance_timing_count"],
        "pass_count": result["pass_count"],
        "recount_sha256": result["recount_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
