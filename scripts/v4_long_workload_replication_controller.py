#!/usr/bin/env python3
"""Create-only controller for the cit-Patents long-row replication."""

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
from collections.abc import Mapping
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/v4_long_workload_worker.py"
CONFIG_SCHEMA = "rtdl.v4_long_workload.formal_config.v1"
PREREG_SCHEMA = "rtdl.v4_long_workload.replication_preregistration.v1"
SCHEDULE_SCHEMA = "rtdl.v4_long_workload.replication_schedule.v1"
SUMMARY_SCHEMA = "rtdl.v4_long_workload.replication_summary.v1"
UNIT_ID = "triangle_counting__cit_patents__rt_2a1__4m"
ENDPOINT = "prepared"
ARMS = ("new_v4", "pyoptix")
BLOCK_ORDERS = (
    ("new_v4", "pyoptix"),
    ("pyoptix", "new_v4"),
    ("new_v4", "pyoptix"),
    ("pyoptix", "new_v4"),
    ("new_v4", "pyoptix"),
    ("pyoptix", "new_v4"),
    ("new_v4", "pyoptix"),
    ("pyoptix", "new_v4"),
)
EXPECTED_UNIT = {
    "app": "triangle_counting",
    "operation": None,
    "dataset": "cit-Patents",
    "expected_triangle_count": 7_515_023,
    "max_relation_rows": 4_000_000,
    "prepared_repetitions": 3,
}
THRESHOLDS = {
    "median_new_v4_over_pyoptix_max": 1.20,
    "every_block_new_v4_over_pyoptix_max": 1.35,
}
PRIOR_REGISTERED_GPU = {
    "name": "NVIDIA RTX A4500",
    "uuid": "GPU-5dbda20d-af85-650e-7250-10b265a77143",
    "driver": "550.127.05",
    "compute_capability": "8.6",
}
REPLICATION_SCOPES = ("same_host_temporal", "cross_gpu_reproducibility")


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def replication_scope_matches(
    scope: object, registered_machine: object,
) -> bool:
    if scope not in REPLICATION_SCOPES or not isinstance(
            registered_machine, Mapping):
        return False
    gpu = registered_machine.get("gpu")
    if not isinstance(gpu, Mapping):
        return False
    if scope == "same_host_temporal":
        return dict(gpu) == PRIOR_REGISTERED_GPU
    return gpu.get("uuid") != PRIOR_REGISTERED_GPU["uuid"]


def validate_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
    if config.get("schema") != CONFIG_SCHEMA:
        raise ValueError("formal config schema differs")
    common = config.get("common")
    implementations = config.get("implementations")
    units = config.get("units")
    if not isinstance(common, Mapping) \
            or not isinstance(implementations, Mapping) \
            or not isinstance(units, Mapping):
        raise TypeError("formal config mappings are incomplete")
    if any(not isinstance(implementations.get(arm), Mapping) for arm in ARMS):
        raise ValueError("replication implementation arms are incomplete")
    unit = units.get(UNIT_ID)
    if not isinstance(unit, Mapping) or unit.get("unit_id") != UNIT_ID:
        raise ValueError("replication unit is missing")
    for key, expected in EXPECTED_UNIT.items():
        if unit.get(key) != expected:
            raise ValueError(f"replication unit field differs: {key}")
    if common.get("prepared_warmups") != 1:
        raise ValueError("replication prepared warmup count must be one")
    if common.get("retry_allowed") is not False \
            or common.get("discard_allowed") is not False:
        raise ValueError("replication forbids retry and discard")
    timeout = common.get("worker_timeout_seconds")
    if type(timeout) is not int or timeout < 120:
        raise ValueError("replication worker timeout is invalid")
    affinity = common.get("cpu_affinity")
    if not isinstance(affinity, Mapping) or set(affinity) != {"cpu_ids"}:
        raise ValueError("replication requires an exact CPU-affinity contract")
    cpu_ids = affinity.get("cpu_ids")
    if not isinstance(cpu_ids, list) or len(cpu_ids) != 1 \
            or type(cpu_ids[0]) is not int or cpu_ids[0] < 0:
        raise ValueError("replication requires one logical CPU")
    registered = common.get("registered_machine")
    if not isinstance(registered, Mapping):
        raise ValueError("replication registered machine is missing")
    for arm in ARMS:
        row = implementations[arm]
        for key in (
            "source_root", "source_commit", "source_tree",
            "native_library_path", "native_library_sha256",
        ):
            if not row.get(key):
                raise ValueError(f"replication arm field is missing: {arm}:{key}")
    return unit


def build_schedule(config: Mapping[str, Any], *, mode: str) -> list[dict[str, Any]]:
    unit = validate_config(config)
    repetitions = int(unit["prepared_repetitions"])
    rows: list[dict[str, Any]] = []
    if mode == "dry-run":
        orders = (ARMS,)
        repetitions = 1
        warmups = 0
    elif mode == "formal":
        orders = BLOCK_ORDERS
        warmups = 1
    else:
        raise ValueError(mode)
    for block, order in enumerate(orders):
        for position, arm in enumerate(order):
            rows.append({
                "ordinal": len(rows),
                "unit_id": UNIT_ID,
                "endpoint": ENDPOINT,
                "block": None if mode == "dry-run" else block,
                "position": position,
                "arm": arm,
                "repetitions": repetitions,
                "warmups": warmups,
            })
    expected = 2 if mode == "dry-run" else 16
    if len(rows) != expected:
        raise RuntimeError("replication schedule population differs")
    return rows


def schedule_payload(
    config_path: Path, config: Mapping[str, Any], *, mode: str,
) -> dict[str, Any]:
    rows = build_schedule(config, mode=mode)
    return {
        "schema": SCHEDULE_SCHEMA,
        "mode": mode,
        "config_sha256": sha256(config_path),
        "controller_sha256": sha256(Path(__file__).resolve()),
        "worker_sha256": sha256(WORKER),
        "worker_count": len(rows),
        "rows": rows,
    }


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
    }


def _run_worker(
    row: Mapping[str, Any], *, output_root: Path, config_path: Path,
    python: Path, timeout_seconds: int,
) -> dict[str, Any]:
    block = row["block"] if row["block"] is not None else "dry"
    stem = (
        f"w{int(row['ordinal']):03d}__{row['unit_id']}__{row['endpoint']}__"
        f"b{block}__p{row['position']}__{row['arm']}"
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
    paths = {
        "stdout": stdout,
        "stderr": stderr,
        "output": output if output.is_file() else None,
        "journal": journal if journal.is_file() else None,
    }
    for name, path in paths.items():
        launch[f"{name}_relative"] = (
            path.relative_to(output_root).as_posix() if path is not None else None
        )
        launch[f"{name}_sha256"] = sha256(path) if path is not None else None
    worker = None
    parse_error = None
    if output.is_file():
        try:
            worker = read_object(output)
        except (OSError, ValueError, TypeError) as error:
            parse_error = f"{type(error).__name__}: {error}"
    return {
        **dict(row),
        "launch": launch,
        "worker": worker,
        "worker_parse_error": parse_error,
    }


def _valid_worker(row: Mapping[str, Any], *, config_sha256: str) -> bool:
    launch = row.get("launch")
    worker = row.get("worker")
    return bool(
        isinstance(launch, Mapping)
        and isinstance(worker, Mapping)
        and launch.get("return_code") == 0
        and launch.get("timeout") is False
        and worker.get("status") == "PASS"
        and worker.get("unit_id") == UNIT_ID
        and worker.get("arm") == row.get("arm")
        and worker.get("endpoint") == ENDPOINT
        and worker.get("formal_config_sha256") == config_sha256
        and worker.get("retained_sample_count") == row.get("repetitions")
        and worker.get("warmup_count") == row.get("warmups")
        and worker.get("retry_count") == 0
        and worker.get("discard_count") == 0
    )


def evaluate(
    rows: list[dict[str, Any]], *, config_sha256: str, formal: bool,
) -> dict[str, Any]:
    expected_blocks = 8 if formal else 1
    cells = []
    for block in range(expected_blocks):
        key = block if formal else None
        selected = [row for row in rows if row.get("block") == key]
        by_arm = {str(row["arm"]): row for row in selected}
        valid = set(by_arm) == set(ARMS) and all(
            _valid_worker(row, config_sha256=config_sha256)
            for row in selected
        )
        reason = None
        medians = None
        if valid:
            inputs = [by_arm[arm]["worker"]["input_identity"] for arm in ARMS]
            outputs = [by_arm[arm]["worker"]["output_sha256"] for arm in ARMS]
            valid = len({digest(value) for value in inputs}) == 1 \
                and len(set(outputs)) == 1
            if not valid:
                reason = "input_or_output_parity"
            else:
                medians = {
                    arm: int(statistics.median(
                        by_arm[arm]["worker"]["primary_samples_ns"]
                    ))
                    for arm in ARMS
                }
        else:
            reason = "worker_failure_or_population"
        cells.append({
            "unit_id": UNIT_ID,
            "endpoint": ENDPOINT,
            "block": key,
            "valid": valid,
            "reason": reason,
            "medians_ns": medians,
            "new_v4_over_pyoptix": (
                medians["new_v4"] / medians["pyoptix"] if medians else None
            ),
        })
    ratios = [row["new_v4_over_pyoptix"] for row in cells if row["valid"]]
    method_complete = len(cells) == expected_blocks and len(ratios) == expected_blocks
    median_ratio = statistics.median(ratios) if method_complete else None
    maximum_ratio = max(ratios) if method_complete else None
    target_met = bool(
        formal
        and method_complete
        and median_ratio <= THRESHOLDS["median_new_v4_over_pyoptix_max"]
        and maximum_ratio <= THRESHOLDS["every_block_new_v4_over_pyoptix_max"]
    )
    return {
        "cells": cells,
        "valid_block_count": len(ratios),
        "registered_block_count": expected_blocks,
        "method_complete": method_complete,
        "median_new_v4_over_pyoptix": median_ratio,
        "max_new_v4_over_pyoptix": maximum_ratio,
        "engineering_target_met": target_met,
    }


def _validate_formal_authority(
    *, config_path: Path, config: Mapping[str, Any], prereg_path: Path,
    dry_path: Path,
) -> None:
    prereg = read_object(prereg_path)
    dry = read_object(dry_path)
    expected_schedule = schedule_payload(config_path, config, mode="formal")
    dry_rows = dry.get("rows")
    dry_identity = None
    dry_output = None
    dry_parity = False
    if isinstance(dry_rows, list) and len(dry_rows) == 2:
        workers = [row.get("worker") for row in dry_rows]
        if all(isinstance(worker, Mapping) for worker in workers):
            identities = [worker.get("input_identity") for worker in workers]
            outputs = [worker.get("output_sha256") for worker in workers]
            dry_parity = len({digest(value) for value in identities}) == 1 \
                and len(set(outputs)) == 1
            if dry_parity:
                dry_identity = identities[0]
                dry_output = outputs[0]
    prior = prereg.get("prior_transaction")
    checks = (
        prereg.get("schema") == PREREG_SCHEMA,
        prereg.get("status") == "FROZEN_BEFORE_REPLICATION_WORKER_ZERO",
        prereg.get("formal_worker_zero_reached") is False,
        prereg.get("formal_config_sha256") == sha256(config_path),
        prereg.get("dry_run_summary_sha256") == sha256(dry_path),
        prereg.get("controller_sha256") == sha256(Path(__file__).resolve()),
        prereg.get("worker_sha256") == sha256(WORKER),
        prereg.get("formal_schedule_sha256") == digest(expected_schedule),
        prereg.get("formal_worker_count") == 16,
        prereg.get("unit_id") == UNIT_ID,
        prereg.get("endpoint") == ENDPOINT,
        prereg.get("arms") == list(ARMS),
        prereg.get("paired_blocks") == 8,
        prereg.get("block_orders") == [list(row) for row in BLOCK_ORDERS],
        prereg.get("prepared_repetitions_per_worker") == 3,
        prereg.get("prepared_warmups_per_worker") == 1,
        prereg.get("engineering_thresholds") == THRESHOLDS,
        prereg.get("retry_allowed") is False,
        prereg.get("discard_allowed") is False,
        prereg.get("all_adverse_rows_retained") is True,
        prereg.get("cpu_affinity") == config["common"].get("cpu_affinity"),
        prereg.get("registered_machine") == config["common"].get(
            "registered_machine"),
        prereg.get("unit") == config["units"][UNIT_ID],
        prereg.get("implementations") == {
            arm: config["implementations"][arm] for arm in ARMS
        },
        isinstance(prior, Mapping),
        isinstance(prior, Mapping)
            and prior.get("archive_sha256")
            == "ef2ca7890c9d415dc1edbe71966aabc512209c9d8608d4eaf460c7c1fddf8bdc",
        isinstance(prior, Mapping)
            and prior.get("formal_summary_sha256")
            == "74c8196f6e6f8e3fc13f1d4bce312087950d1e38571909042815ff6470d0672d",
        isinstance(prior, Mapping)
            and prior.get("pooled_into_this_replication") is False,
        isinstance(prior, Mapping)
            and prior.get("registered_gpu") == PRIOR_REGISTERED_GPU,
        replication_scope_matches(
            prereg.get("replication_scope"),
            config["common"].get("registered_machine"),
        ),
        dry.get("schema") == SUMMARY_SCHEMA,
        dry.get("mode") == "dry-run",
        dry.get("status") == "COMPLETE__DRY_RUN_PARITY_PASS",
        dry.get("formal_worker_zero_reached") is False,
        dry.get("worker_count") == 2,
        dry.get("config_sha256") == sha256(config_path),
        dry.get("controller_sha256") == sha256(Path(__file__).resolve()),
        dry.get("worker_sha256") == sha256(WORKER),
        dry.get("retry_count") == 0,
        dry.get("discard_count") == 0,
        dry_parity,
        prereg.get("input_identity") == dry_identity,
        prereg.get("input_identity_sha256") == digest(dry_identity),
        prereg.get("expected_output_sha256") == dry_output,
    )
    if not all(checks):
        raise PermissionError("replication preregistration/dry-run authority differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("dry-run", "formal"), required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path)
    parser.add_argument("--dry-run-summary", type=Path)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    args = parser.parse_args()
    if args.output_root.exists():
        raise FileExistsError(args.output_root)
    config_path = args.config.resolve(strict=True)
    config = read_object(config_path)
    validate_config(config)
    if args.mode == "formal":
        if args.preregistration is None or args.dry_run_summary is None:
            parser.error("formal mode requires preregistration and dry-run summary")
        _validate_formal_authority(
            config_path=config_path,
            config=config,
            prereg_path=args.preregistration.resolve(strict=True),
            dry_path=args.dry_run_summary.resolve(strict=True),
        )

    args.output_root.mkdir(parents=True)
    payload = schedule_payload(config_path, config, mode=args.mode)
    write_create(args.output_root / "SCHEDULE.json", payload)
    progress = args.output_root / "CONTROLLER_PROGRESS.jsonl"
    progress.touch(exist_ok=False)
    append(progress, {
        "event": "schedule_frozen",
        "worker_count": payload["worker_count"],
        "schedule_sha256": sha256(args.output_root / "SCHEDULE.json"),
        "formal_worker_zero_reached": False,
    })
    timeout = int(config["common"]["worker_timeout_seconds"])
    python = args.python.resolve(strict=True)
    rows = []
    for row in payload["rows"]:
        observed = _run_worker(
            row,
            output_root=args.output_root,
            config_path=config_path,
            python=python,
            timeout_seconds=timeout,
        )
        rows.append(observed)
        append(progress, {
            "event": "worker_complete",
            "ordinal": row["ordinal"],
            "unit_id": row["unit_id"],
            "arm": row["arm"],
            "endpoint": row["endpoint"],
            "return_code": observed["launch"]["return_code"],
            "timeout": observed["launch"]["timeout"],
            "output_sha256": observed["launch"]["output_sha256"],
            "journal_sha256": observed["launch"]["journal_sha256"],
        })
    result = evaluate(
        rows,
        config_sha256=sha256(config_path),
        formal=args.mode == "formal",
    )
    if args.mode == "dry-run":
        status = "COMPLETE__DRY_RUN_PARITY_PASS" \
            if result["method_complete"] else "FAIL__DRY_RUN_METHOD"
    elif not result["method_complete"]:
        status = "FAIL__REPLICATION_METHOD"
    elif result["engineering_target_met"]:
        status = "COMPLETE__REPLICATION_TARGET_MET"
    else:
        status = "COMPLETE__REPLICATION_TARGET_NOT_MET"
    summary = {
        "schema": SUMMARY_SCHEMA,
        "mode": args.mode,
        "status": status,
        "formal_worker_zero_reached": args.mode == "formal" and bool(rows),
        "config_sha256": sha256(config_path),
        "controller_sha256": sha256(Path(__file__).resolve()),
        "worker_sha256": sha256(WORKER),
        "schedule_file_sha256": sha256(args.output_root / "SCHEDULE.json"),
        "progress_file_sha256": sha256(progress),
        "worker_count": len(rows),
        "retry_count": 0,
        "discard_count": 0,
        "rows": rows,
        **result,
    }
    write_create(args.output_root / "SUMMARY.json", summary)
    print(json.dumps({
        "status": status,
        "mode": args.mode,
        "worker_count": len(rows),
        "summary": str(args.output_root / "SUMMARY.json"),
    }, sort_keys=True))
    return 0 if result["method_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
