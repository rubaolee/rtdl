#!/usr/bin/env python3
"""Measure Goal5848 phase-instrumentation overhead in paired fresh processes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path

from experiments.goal5848_strong_baseline.contracts import (
    INSTRUMENTATION_AUTHORITY_SCHEMA,
    INSTRUMENTATION_AUTHORITY_STATUS,
    INSTRUMENTATION_BLOCKS,
    INSTRUMENTATION_OVERHEAD_LIMIT_PPM,
    RELATION_TASK,
    RTDL_ARM,
    TASK_CONTRACTS,
    TASKS,
    WORKER_SCHEMA,
    build_instrumentation_schedule,
    digest,
    integer_median,
    ratio_ppm,
    require_formal_cache_policy,
    strict_json_loads,
)
from experiments.goal5848_strong_baseline.controller import (
    _new_output_root,
    _validate_file_identity,
    _validate_preregistration,
)
from experiments.goal5848_strong_baseline.worker import ROOT, _write_create

_NATIVE_PHASE = re.compile(
    r"RTDL_GOAL5807_NATIVE_PHASE\|([^|\n]+)\|([^|\n]+)\|([0-9]+)"
)


def _read_json(path: Path) -> dict[str, object]:
    value = strict_json_loads(
        path.resolve(strict=True).read_text(encoding="utf-8"),
        label="Goal5848 instrumentation worker receipt",
    )
    if not isinstance(value, dict):
        raise TypeError("Goal5848 instrumentation worker receipt must be an object")
    return value


def _command(
    row: Mapping[str, object], args: argparse.Namespace, output: Path,
) -> list[str]:
    return [
        str(args.python.resolve(strict=True)),
        "-m",
        "experiments.goal5848_strong_baseline.worker",
        "--arm",
        RTDL_ARM,
        "--task",
        str(row["task"]),
        "--block",
        str(row["block"]),
        "--worker-id",
        str(row["worker_id"]),
        "--classification",
        "exploration",
        "--expected-source-commit",
        args.expected_source_commit,
        "--candidate-manifest",
        str(args.candidate_manifest.resolve(strict=True)),
        "--phase-instrumentation",
        str(row["mode"]),
        "--warmups",
        "1",
        "--repetitions",
        "1",
        "--output",
        str(output),
    ]


def _parse_native_phases(stderr: bytes, *, mode: str) -> list[dict[str, object]]:
    if mode == "off":
        if stderr:
            raise RuntimeError("Goal5848 uninstrumented worker wrote stderr")
        return []
    try:
        text = stderr.decode("ascii")
    except UnicodeDecodeError as error:
        raise RuntimeError("Goal5848 native phase trace is not ASCII") from error
    rows = []
    for line in text.splitlines():
        match = _NATIVE_PHASE.fullmatch(line)
        if match is None:
            raise RuntimeError("Goal5848 instrumented worker wrote foreign stderr")
        family, phase, duration = match.groups()
        row = {
            "family": family,
            "phase": phase,
            "duration_ns": int(duration),
        }
        rows.append(row)
    phases = {str(row["phase"]) for row in rows}
    if not rows or "prepare.total" not in phases or "prepare.gas" not in phases:
        raise RuntimeError("Goal5848 native prepare phase trace is incomplete")
    return rows


def _validate_worker(
    value: Mapping[str, object], *, row: Mapping[str, object],
    expected_source_commit: str,
) -> int:
    unsigned = dict(value)
    seal = unsigned.pop("result_sha256", None)
    measurements = value.get("measurements")
    source = value.get("source")
    if (
        seal != digest(unsigned)
        or value.get("schema") != WORKER_SCHEMA
        or value.get("status") != "PASS__GOAL5848_WORKER"
        or value.get("arm") != RTDL_ARM
        or value.get("task") != row["task"]
        or value.get("block") != row["block"]
        or value.get("worker_id") != row["worker_id"]
        or value.get("classification") != "exploration"
        or value.get("warmups") != 1
        or value.get("repetitions") != 1
        or not isinstance(source, Mapping)
        or source.get("commit") != expected_source_commit
        or source.get("clean") is not True
        or source.get("status") != ""
        or not isinstance(measurements, Mapping)
    ):
        raise RuntimeError("Goal5848 instrumentation worker receipt differs")
    evidence = measurements.get("evidence")
    partition = measurements.get("endpoint_partition_ns")
    components = measurements.get("component_diagnostics_ns")
    endpoint = measurements.get("post_import_to_first_correct_result_ns")
    mode_enabled = row["mode"] == "on"
    if (
        type(endpoint) is not int
        or endpoint <= 0
        or not isinstance(evidence, Mapping)
        or evidence.get("phase_instrumentation") is not mode_enabled
        or evidence.get("output_sha256")
        != TASK_CONTRACTS[str(row["task"])]["public_output_sha256"]
        or not isinstance(partition, Mapping)
        or not isinstance(components, Mapping)
    ):
        raise RuntimeError("Goal5848 instrumentation endpoint differs")
    if not mode_enabled and (
        any(
            value != 0
            for name, value in partition.items()
            if name != "unattributed_control_plane"
        )
        or partition.get("unattributed_control_plane") != endpoint
        or any(value is not None for value in components.values())
        or evidence.get("provider_initialization_phases_ns") != {}
    ):
        raise RuntimeError("Goal5848 uninstrumented endpoint contains phase probes")
    if mode_enabled and not evidence.get("provider_initialization_phases_ns"):
        raise RuntimeError("Goal5848 instrumented provider phases are absent")
    return endpoint


def _evaluate(
    receipts: list[dict[str, object]],
    native_phases: Mapping[str, list[dict[str, object]]],
) -> dict[str, object]:
    indexed = {
        (str(row["task"]), int(row["block"]), str(row["mode"])): row
        for row in receipts
    }
    result = {}
    for task in TASKS:
        values = defaultdict(list)
        blocks = []
        for block in range(INSTRUMENTATION_BLOCKS):
            off = indexed[(task, block, "off")]
            on = indexed[(task, block, "on")]
            off_ns = int(off["endpoint_ns"])
            on_ns = int(on["endpoint_ns"])
            values["off"].append(off_ns)
            values["on"].append(on_ns)
            blocks.append({
                "block": block,
                "off_ns": off_ns,
                "on_ns": on_ns,
                "signed_difference_ns": on_ns - off_ns,
            })
        off_median = integer_median(values["off"])
        on_median = integer_median(values["on"])
        overhead = max(0, on_median - off_median)
        overhead_ppm = ratio_ppm(overhead, off_median)
        if overhead_ppm > INSTRUMENTATION_OVERHEAD_LIMIT_PPM:
            raise RuntimeError(
                f"Goal5848 instrumentation overhead exceeds 5%: {task}"
            )
        expected_family = (
            "bounded_relation" if task == RELATION_TASK else "builtin_triangle"
        )
        observed_phase_names = sorted({
            str(phase["phase"])
            for row in receipts
            if row["task"] == task and row["mode"] == "on"
            for phase in native_phases[str(row["worker_id"])]
            if phase["family"] == expected_family
        })
        if "prepare.total" not in observed_phase_names \
                or "prepare.gas" not in observed_phase_names:
            raise RuntimeError("Goal5848 task-native phase coverage differs")
        result[task] = {
            "blocks": blocks,
            "uninstrumented_endpoint_median_ns": off_median,
            "instrumented_endpoint_median_ns": on_median,
            "measured_instrumentation_overhead_ns": overhead,
            "instrumentation_overhead_ppm": overhead_ppm,
            "limit_ppm": INSTRUMENTATION_OVERHEAD_LIMIT_PPM,
            "native_phase_names": observed_phase_names,
            "pass": True,
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--expected-predecessor-commit", required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--worker-timeout-seconds", type=int, default=300)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    require_formal_cache_policy()
    if args.worker_timeout_seconds <= 0:
        raise ValueError("Goal5848 instrumentation timeout differs")
    preregistration = _validate_preregistration(
        args.preregistration,
        expected_source_commit=args.expected_source_commit,
        expected_predecessor_commit=args.expected_predecessor_commit,
    )
    artifacts = preregistration.get("artifacts")
    if not isinstance(artifacts, Mapping):
        raise TypeError("Goal5848 preregistered artifacts are absent")
    _validate_file_identity(
        args.candidate_manifest,
        artifacts.get("candidate_manifest"),
        "candidate_manifest",
    )
    output_root = _new_output_root(args.output_root)
    output_root.mkdir(parents=True)
    workers = output_root / "workers"
    processes = output_root / "processes"
    workers.mkdir()
    processes.mkdir()
    receipts = []
    phase_rows: dict[str, list[dict[str, object]]] = {}
    process_rows = []
    stage = "START"
    try:
        for row in build_instrumentation_schedule():
            worker_id = str(row["worker_id"])
            stage = worker_id
            output = workers / f"{worker_id}.json"
            command = _command(row, args, output)
            environment = dict(os.environ)
            environment["PYTHONPATH"] = f"{ROOT / 'src'}:{ROOT}"
            if row["mode"] == "on":
                environment["RTDL_GOAL5807_PROFILE_NATIVE"] = "1"
            else:
                environment.pop("RTDL_GOAL5807_PROFILE_NATIVE", None)
            completed = subprocess.run(
                command,
                cwd=ROOT,
                env=environment,
                capture_output=True,
                check=False,
                timeout=args.worker_timeout_seconds,
            )
            native = _parse_native_phases(completed.stderr, mode=str(row["mode"]))
            if completed.returncode != 0 or not output.is_file():
                raise RuntimeError(f"Goal5848 instrumentation worker failed: {worker_id}")
            receipt = _read_json(output)
            if completed.stdout.decode("utf-8") != json.dumps(
                receipt, sort_keys=True
            ) + "\n":
                raise RuntimeError("Goal5848 instrumentation stdout differs")
            endpoint = _validate_worker(
                receipt,
                row=row,
                expected_source_commit=args.expected_source_commit,
            )
            compact = {
                "worker_id": worker_id,
                "task": row["task"],
                "block": row["block"],
                "mode": row["mode"],
                "endpoint_ns": endpoint,
                "worker_receipt_sha256": receipt["result_sha256"],
            }
            receipts.append(compact)
            phase_rows[worker_id] = native
            process = {
                "worker_id": worker_id,
                "command": command,
                "exit_code": completed.returncode,
                "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
                "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
                "native_phase_rows": native,
            }
            process["process_sha256"] = digest(process)
            _write_create(processes / f"{worker_id}.json", process)
            process_rows.append(process)
        hardware_rows = {
            json.dumps(_read_json(workers / f"{row['worker_id']}.json")["hardware"],
                       sort_keys=True)
            for row in receipts
        }
        if len(hardware_rows) != 1:
            raise RuntimeError("Goal5848 instrumentation workers span hardware")
        hardware = strict_json_loads(
            next(iter(hardware_rows)),
            label="Goal5848 instrumentation hardware",
        )
        evaluation = _evaluate(receipts, phase_rows)
        value = {
            "schema": INSTRUMENTATION_AUTHORITY_SCHEMA,
            "status": INSTRUMENTATION_AUTHORITY_STATUS,
            "source_commit": args.expected_source_commit,
            "predecessor_commit": args.expected_predecessor_commit,
            "preregistration_sha256": preregistration["preregistration_sha256"],
            "hardware": hardware,
            "schedule": list(build_instrumentation_schedule()),
            "worker_count": len(receipts),
            "process_count": len(process_rows),
            "tasks": evaluation,
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
            "included_in_formal_estimators": False,
            "retry_count": 0,
            "discard_count": 0,
            "public_or_manuscript_claim_authorized": False,
        }
        value["authority_sha256"] = digest(value)
        _write_create(output_root / "authority.json", value)
        print(json.dumps(value, sort_keys=True))
    except BaseException as error:
        failure = {
            "schema": "rtdl.goal5848.instrumentation_overhead_failure.v1",
            "status": "FAIL__NO_RETRY_NO_DISCARD",
            "failed_stage": stage,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "completed_worker_count": len(receipts),
            "retry_count": 0,
            "discard_count": 0,
        }
        failure["failure_sha256"] = digest(failure)
        _write_create(output_root / "failure.json", failure)
        raise


if __name__ == "__main__":
    main()
