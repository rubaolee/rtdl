#!/usr/bin/env python3
"""Fail-closed controller for the frozen 240-worker performance matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/v4_long_workload_worker.py"
ARMS = ("old_v4", "new_v4", "pyoptix")
ENDPOINTS = ("complete", "prepared")
BLOCK_ORDERS = (
    ("old_v4", "new_v4", "pyoptix"),
    ("old_v4", "pyoptix", "new_v4"),
    ("new_v4", "old_v4", "pyoptix"),
    ("new_v4", "pyoptix", "old_v4"),
    ("pyoptix", "old_v4", "new_v4"),
    ("pyoptix", "new_v4", "old_v4"),
    ("old_v4", "new_v4", "pyoptix"),
    ("pyoptix", "new_v4", "old_v4"),
)
CONFIG_SCHEMA = "rtdl.v4_long_workload.formal_config.v1"
PREREG_SCHEMA = "rtdl.v4_long_workload.preregistration.v1"
SCHEDULE_SCHEMA = "rtdl.v4_long_workload.schedule.v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root must be an object: {path}")
    return value


def write_create(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def append(path: Path, value: Mapping[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def validate_config(config: Mapping[str, Any]) -> tuple[str, ...]:
    if config.get("schema") != CONFIG_SCHEMA:
        raise ValueError("formal config schema differs")
    units = config.get("units")
    implementations = config.get("implementations")
    common = config.get("common")
    if not isinstance(units, Mapping) or not isinstance(implementations, Mapping) \
            or not isinstance(common, Mapping):
        raise TypeError("formal config mappings are incomplete")
    if tuple(implementations) != ARMS:
        raise ValueError("formal implementation arm order differs")
    unit_ids = tuple(units)
    if len(unit_ids) != 5 or len(set(unit_ids)) != 5:
        raise ValueError("formal config must contain exactly five units")
    expected_apps = {
        "particle_tracking": 1,
        "triangle_counting": 2,
        "librts": 2,
    }
    observed = defaultdict(int)
    for unit_id, row in units.items():
        if not isinstance(row, Mapping) or row.get("unit_id") != unit_id:
            raise ValueError(f"formal unit identity differs: {unit_id}")
        observed[str(row.get("app"))] += 1
        repetitions = row.get("prepared_repetitions")
        if type(repetitions) is not int or repetitions <= 0:
            raise ValueError(f"formal repetitions are invalid: {unit_id}")
    if dict(observed) != expected_apps:
        raise ValueError("formal unit application population differs")
    if common.get("prepared_warmups") != 1:
        raise ValueError("formal prepared warmup count must be one")
    return unit_ids


def build_schedule(config: Mapping[str, Any], *, mode: str) -> list[dict[str, Any]]:
    unit_ids = validate_config(config)
    rows: list[dict[str, Any]] = []
    if mode == "dry-run":
        for unit_id in unit_ids:
            for position, arm in enumerate(ARMS):
                rows.append({
                    "ordinal": len(rows), "unit_id": unit_id,
                    "endpoint": "prepared", "block": None,
                    "position": position, "arm": arm,
                    "repetitions": 1, "warmups": 0,
                })
        return rows
    if mode != "formal":
        raise ValueError(mode)
    for unit_id in unit_ids:
        unit = config["units"][unit_id]
        for endpoint in ENDPOINTS:
            repetitions = (
                1 if endpoint == "complete" else int(unit["prepared_repetitions"])
            )
            warmups = 0 if endpoint == "complete" else 1
            for block, order in enumerate(BLOCK_ORDERS):
                for position, arm in enumerate(order):
                    rows.append({
                        "ordinal": len(rows), "unit_id": unit_id,
                        "endpoint": endpoint, "block": block,
                        "position": position, "arm": arm,
                        "repetitions": repetitions, "warmups": warmups,
                    })
    if len(rows) != 240:
        raise RuntimeError("formal schedule does not contain 240 workers")
    return rows


def _command(
    row: Mapping[str, Any], *, python: Path, config: Path,
    output: Path, journal: Path,
) -> list[str]:
    return [
        str(python), str(WORKER), "--config", str(config),
        "--unit", str(row["unit_id"]), "--arm", str(row["arm"]),
        "--endpoint", str(row["endpoint"]),
        "--repetitions", str(row["repetitions"]),
        "--warmups", str(row["warmups"]),
        "--output", str(output), "--journal", str(journal),
    ]


def _launch(
    command: list[str], *, cwd: Path, stdout_path: Path, stderr_path: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    started = time.perf_counter_ns()
    timed_out = False
    launch_error = None
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        try:
            process = subprocess.Popen(
                command, cwd=cwd, stdout=stdout, stderr=stderr,
                start_new_session=True,
            )
            try:
                return_code = process.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                timed_out = True
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    return_code = process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    return_code = process.wait()
        except OSError as error:
            return_code = 127
            launch_error = f"{type(error).__name__}: {error}"
    return {
        "command": command,
        "return_code": return_code,
        "timeout": timed_out,
        "launch_error": launch_error,
        "wall_ns": time.perf_counter_ns() - started,
        "stdout_relative": None,
        "stderr_relative": None,
    }


def _output_row(
    *, row: Mapping[str, Any], output_root: Path, config_path: Path,
    python: Path, timeout_seconds: int,
) -> dict[str, Any]:
    stem = (
        f"w{int(row['ordinal']):03d}__{row['unit_id']}__{row['endpoint']}__"
        f"b{row['block'] if row['block'] is not None else 'dry'}__"
        f"p{row['position']}__{row['arm']}"
    )
    output = output_root / "workers" / f"{stem}.json"
    journal = output_root / "journals" / f"{stem}.jsonl"
    stdout = output_root / "stdout" / f"{stem}.bin"
    stderr = output_root / "stderr" / f"{stem}.bin"
    launch = _launch(
        _command(row, python=python, config=config_path,
                 output=output, journal=journal),
        cwd=ROOT, stdout_path=stdout, stderr_path=stderr,
        timeout_seconds=timeout_seconds,
    )
    launch["stdout_relative"] = stdout.relative_to(output_root).as_posix()
    launch["stderr_relative"] = stderr.relative_to(output_root).as_posix()
    launch["stdout_sha256"] = sha256(stdout)
    launch["stderr_sha256"] = sha256(stderr)
    launch["output_relative"] = (
        output.relative_to(output_root).as_posix() if output.is_file() else None)
    launch["journal_relative"] = (
        journal.relative_to(output_root).as_posix() if journal.is_file() else None)
    launch["output_sha256"] = sha256(output) if output.is_file() else None
    launch["journal_sha256"] = sha256(journal) if journal.is_file() else None
    worker = None
    parse_error = None
    if output.is_file():
        try:
            worker = read_object(output)
        except (OSError, ValueError, TypeError) as error:
            parse_error = f"{type(error).__name__}: {error}"
    return {
        **dict(row), "launch": launch, "worker": worker,
        "worker_parse_error": parse_error,
    }


def _valid_worker(row: Mapping[str, Any], config_sha256: str) -> bool:
    worker = row.get("worker")
    launch = row.get("launch")
    return bool(
        isinstance(worker, Mapping) and isinstance(launch, Mapping)
        and launch.get("return_code") == 0 and launch.get("timeout") is False
        and worker.get("status") == "PASS"
        and worker.get("unit_id") == row.get("unit_id")
        and worker.get("arm") == row.get("arm")
        and worker.get("endpoint") == row.get("endpoint")
        and worker.get("formal_config_sha256") == config_sha256
        and worker.get("retained_sample_count") == row.get("repetitions")
        and worker.get("warmup_count") == row.get("warmups")
        and worker.get("retry_count") == 0
        and worker.get("discard_count") == 0
    )


def _evaluate(
    rows: list[dict[str, Any]], *, config_sha256: str, formal: bool,
) -> dict[str, Any]:
    groups: dict[tuple[object, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["unit_id"], row["endpoint"],
            row["block"] if formal else "dry",
        )
        groups[key].append(row)
    cells = []
    for key, values in groups.items():
        by_arm = {row["arm"]: row for row in values}
        valid = set(by_arm) == set(ARMS) and all(
            _valid_worker(row, config_sha256) for row in values)
        reason = None
        if valid:
            identities = [row["worker"]["input_identity"] for row in values]
            outputs = [row["worker"]["output_sha256"] for row in values]
            valid = len({digest(item) for item in identities}) == 1 \
                and len(set(outputs)) == 1
            if not valid:
                reason = "input_or_output_parity"
        else:
            reason = "worker_failure_or_population"
        medians = None
        if valid:
            medians = {
                arm: int(statistics.median(
                    by_arm[arm]["worker"]["primary_samples_ns"]))
                for arm in ARMS
            }
        cells.append({
            "unit_id": key[0], "endpoint": key[1], "block": key[2],
            "valid": valid, "reason": reason,
            "medians_ns": medians,
            "new_v4_over_pyoptix": (
                medians["new_v4"] / medians["pyoptix"] if medians else None),
            "old_v4_over_pyoptix": (
                medians["old_v4"] / medians["pyoptix"] if medians else None),
            "new_v4_over_old_v4": (
                medians["new_v4"] / medians["old_v4"] if medians else None),
        })
    evaluations = []
    if formal:
        grouped_cells: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for cell in cells:
            grouped_cells[(cell["unit_id"], cell["endpoint"])].append(cell)
        for key, values in grouped_cells.items():
            ratios = [row["new_v4_over_pyoptix"] for row in values if row["valid"]]
            complete = len(values) == 8 and len(ratios) == 8
            median = statistics.median(ratios) if complete else None
            maximum = max(ratios) if complete else None
            evaluations.append({
                "unit_id": key[0], "endpoint": key[1],
                "valid_block_count": len(ratios),
                "registered_block_count": 8,
                "median_new_v4_over_pyoptix": median,
                "max_new_v4_over_pyoptix": maximum,
                "engineering_target_met": bool(
                    complete and median <= 1.20 and maximum <= 1.35),
            })
    return {"cells": cells, "evaluations": evaluations}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("dry-run", "formal"), required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path)
    parser.add_argument("--dry-run-summary", type=Path)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    args = parser.parse_args()
    if args.output_root.exists():
        raise FileExistsError(args.output_root)
    args.output_root.mkdir(parents=True)
    config_path = args.config.resolve(strict=True)
    config = read_object(config_path)
    schedule = build_schedule(config, mode=args.mode)
    config_sha = sha256(config_path)
    schedule_payload = {
        "schema": SCHEDULE_SCHEMA, "mode": args.mode,
        "config_sha256": config_sha,
        "controller_sha256": sha256(Path(__file__).resolve()),
        "worker_sha256": sha256(WORKER),
        "worker_count": len(schedule), "rows": schedule,
    }
    if args.mode == "formal":
        if args.preregistration is None or args.dry_run_summary is None:
            parser.error("formal mode requires preregistration and dry-run summary")
        prereg_path = args.preregistration.resolve(strict=True)
        prereg = read_object(prereg_path)
        dry_path = args.dry_run_summary.resolve(strict=True)
        dry = read_object(dry_path)
        if (
            prereg.get("schema") != PREREG_SCHEMA
            or prereg.get("formal_config_sha256") != config_sha
            or prereg.get("formal_schedule_sha256") != digest(schedule_payload)
            or prereg.get("controller_sha256") != sha256(Path(__file__).resolve())
            or prereg.get("worker_sha256") != sha256(WORKER)
            or prereg.get("dry_run_summary_sha256") != sha256(dry_path)
            or dry.get("status") != "PASS"
            or dry.get("formal_worker_zero_reached") is not False
        ):
            raise PermissionError("formal preregistration/dry-run authority differs")
    write_create(args.output_root / "SCHEDULE.json", schedule_payload)
    progress = args.output_root / "CONTROLLER_PROGRESS.jsonl"
    progress.touch(exist_ok=False)
    append(progress, {
        "event": "schedule_frozen", "worker_count": len(schedule),
        "schedule_sha256": sha256(args.output_root / "SCHEDULE.json"),
        "formal_worker_zero_reached": False,
    })
    timeout_seconds = int(config["common"]["worker_timeout_seconds"])
    python = args.python.resolve(strict=True)
    rows = []
    for row in schedule:
        observed = _output_row(
            row=row, output_root=args.output_root, config_path=config_path,
            python=python, timeout_seconds=timeout_seconds,
        )
        rows.append(observed)
        append(progress, {
            "event": "worker_complete", "ordinal": row["ordinal"],
            "unit_id": row["unit_id"], "arm": row["arm"],
            "endpoint": row["endpoint"],
            "return_code": observed["launch"]["return_code"],
            "timeout": observed["launch"]["timeout"],
            "output_sha256": observed["launch"]["output_sha256"],
            "journal_sha256": observed["launch"]["journal_sha256"],
        })
    evaluation = _evaluate(
        rows, config_sha256=config_sha, formal=args.mode == "formal")
    if args.mode == "formal":
        passed = len(evaluation["evaluations"]) == 10 and all(
            row["engineering_target_met"] for row in evaluation["evaluations"])
    else:
        passed = len(evaluation["cells"]) == 5 and all(
            row["valid"] for row in evaluation["cells"])
    summary = {
        "schema": f"rtdl.v4_long_workload.{args.mode}_summary.v1",
        "status": "PASS" if passed else "FAIL",
        "formal_worker_zero_reached": args.mode == "formal" and bool(rows),
        "config_sha256": config_sha,
        "controller_sha256": sha256(Path(__file__).resolve()),
        "worker_sha256": sha256(WORKER),
        "schedule_file_sha256": sha256(args.output_root / "SCHEDULE.json"),
        "progress_file_sha256": sha256(progress),
        "retry_count": 0, "discard_count": 0,
        "worker_count": len(rows), "rows": rows,
        **evaluation,
    }
    summary_name = "FORMAL_SUMMARY.json" if args.mode == "formal" \
        else "DRY_RUN_SUMMARY.json"
    write_create(args.output_root / summary_name, summary)
    print(json.dumps({
        "status": summary["status"], "mode": args.mode,
        "worker_count": len(rows),
        "summary": str(args.output_root / summary_name),
    }, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
