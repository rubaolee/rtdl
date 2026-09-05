#!/usr/bin/env python3
"""Run the nonformal Goal5848 strong-PyOptix competence diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from collections.abc import Mapping
from pathlib import Path

from experiments.goal5848_strong_baseline.contracts import (
    IDIOMATIC_PYOPTIX_ARM,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    STRONG_COMPETENCE_RATIO_LIMIT_PPM,
    STRONG_PYOPTIX_ARM,
    TASK_CONTRACTS,
    TASKS,
    WORKER_SCHEMA,
    digest,
    ratio_ppm,
    require_formal_cache_policy,
    strict_json_loads,
)
from experiments.goal5848_strong_baseline.controller import (
    _new_output_root,
    _validate_preregistration,
)
from experiments.goal5848_strong_baseline.worker import ROOT, _write_create
from scripts.goal5848_run_timer_free_preflight import _add_common_arguments


def _read(path: Path) -> dict[str, object]:
    value = strict_json_loads(
        path.resolve(strict=True).read_text(encoding="utf-8"),
        label="Goal5848 competence receipt",
    )
    if not isinstance(value, dict):
        raise TypeError("Goal5848 competence receipt must be an object")
    return value


def _validate_worker(
    value: dict[str, object],
    *,
    arm: str,
    task: str,
    source_commit: str,
) -> int:
    unsigned = dict(value)
    seal = unsigned.pop("result_sha256", None)
    source = value.get("source")
    measurements = value.get("measurements")
    steady = (
        measurements.get("steady_complete_execution")
        if isinstance(measurements, Mapping)
        else None
    )
    evidence = (
        measurements.get("evidence")
        if isinstance(measurements, Mapping)
        else None
    )
    if (
        seal != digest(unsigned)
        or value.get("schema") != WORKER_SCHEMA
        or value.get("status") != "PASS__GOAL5848_WORKER"
        or value.get("arm") != arm
        or value.get("task") != task
        or value.get("classification") != "exploration"
        or value.get("warmups") != STEADY_WARMUPS
        or value.get("repetitions") != STEADY_REPETITIONS
        or not isinstance(source, Mapping)
        or source.get("commit") != source_commit
        or source.get("clean") is not True
        or not isinstance(steady, Mapping)
        or steady.get("sample_count") != STEADY_REPETITIONS
        or not isinstance(steady.get("samples_ns"), list)
        or len(steady["samples_ns"]) != STEADY_REPETITIONS
        or type(steady.get("median_ns")) is not int
        or steady["median_ns"] <= 0
        or not isinstance(evidence, Mapping)
        or evidence.get("output_sha256")
        != TASK_CONTRACTS[task]["public_output_sha256"]
    ):
        raise RuntimeError("Goal5848 baseline competence worker differs")
    return int(steady["median_ns"])


def main() -> None:
    parser = argparse.ArgumentParser()
    _add_common_arguments(parser)
    parser.add_argument("--worker-timeout-seconds", type=int, default=600)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    require_formal_cache_policy()
    if args.worker_timeout_seconds <= 0:
        raise ValueError("Goal5848 competence timeout differs")
    preregistration = _validate_preregistration(
        args.preregistration,
        expected_source_commit=args.expected_source_commit,
        expected_predecessor_commit=args.expected_predecessor_commit,
        arguments=args,
    )
    output_root = _new_output_root(args.output_root)
    output_root.mkdir(parents=True)
    workers = output_root / "workers"
    workers.mkdir()
    process_rows = []
    receipts = []
    stage = "START"
    try:
        for task in TASKS:
            arm_order = (
                (IDIOMATIC_PYOPTIX_ARM, STRONG_PYOPTIX_ARM)
                if task == TASKS[0]
                else (STRONG_PYOPTIX_ARM, IDIOMATIC_PYOPTIX_ARM)
            )
            for arm in arm_order:
                worker_id = f"G5848_COMPETENCE_{task}_{arm}"
                stage = worker_id
                output = workers / f"{worker_id}.json"
                command = [
                    str(args.python.resolve(strict=True)),
                    "-m",
                    "experiments.goal5848_strong_baseline.worker",
                    "--arm",
                    arm,
                    "--task",
                    task,
                    "--block",
                    "0",
                    "--worker-id",
                    worker_id,
                    "--classification",
                    "exploration",
                    "--expected-source-commit",
                    args.expected_source_commit,
                    "--precompiled-ptx",
                    str(args.precompiled_ptx.resolve(strict=True)),
                    "--pyoptix-source",
                    str(args.pyoptix_source.resolve(strict=True)),
                    "--pyoptix-build-receipt",
                    str(args.pyoptix_build_receipt.resolve(strict=True)),
                    "--expected-optix-sdk",
                    args.expected_optix_sdk,
                    "--warmups",
                    str(STEADY_WARMUPS),
                    "--repetitions",
                    str(STEADY_REPETITIONS),
                    "--output",
                    str(output),
                ]
                if arm == STRONG_PYOPTIX_ARM and task == TASKS[0]:
                    command.extend([
                        "--compaction-cubin",
                        str(args.compaction_cubin.resolve(strict=True)),
                    ])
                environment = dict(os.environ)
                environment["PYTHONPATH"] = f"{ROOT / 'src'}:{ROOT}"
                completed = subprocess.run(
                    command,
                    cwd=ROOT,
                    env=environment,
                    capture_output=True,
                    check=False,
                    timeout=args.worker_timeout_seconds,
                )
                process_rows.append({
                    "worker_id": worker_id,
                    "command": command,
                    "exit_code": completed.returncode,
                    "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
                    "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
                })
                if (
                    completed.returncode != 0
                    or completed.stderr
                    or not output.is_file()
                ):
                    raise RuntimeError(
                        f"Goal5848 competence worker failed: {worker_id}"
                    )
                value = _read(output)
                if completed.stdout.decode("utf-8") != (
                    json.dumps(value, sort_keys=True) + "\n"
                ):
                    raise RuntimeError("Goal5848 competence stdout differs")
                _validate_worker(
                    value,
                    arm=arm,
                    task=task,
                    source_commit=args.expected_source_commit,
                )
                receipts.append(value)
        hardware = {
            json.dumps(row["hardware"], sort_keys=True) for row in receipts
        }
        if len(hardware) != 1:
            raise RuntimeError("Goal5848 competence GPU identity differs")
        results = {}
        for task in TASKS:
            medians = {}
            for arm in (IDIOMATIC_PYOPTIX_ARM, STRONG_PYOPTIX_ARM):
                row = next(
                    value
                    for value in receipts
                    if value["task"] == task and value["arm"] == arm
                )
                medians[arm] = _validate_worker(
                    row,
                    arm=arm,
                    task=task,
                    source_commit=args.expected_source_commit,
                )
            observed = ratio_ppm(
                medians[STRONG_PYOPTIX_ARM], medians[IDIOMATIC_PYOPTIX_ARM]
            )
            results[task] = {
                "idiomatic_median_ns": medians[IDIOMATIC_PYOPTIX_ARM],
                "strong_median_ns": medians[STRONG_PYOPTIX_ARM],
                "strong_over_idiomatic_ppm": observed,
                "limit_ppm": STRONG_COMPETENCE_RATIO_LIMIT_PPM,
                "pass": observed <= STRONG_COMPETENCE_RATIO_LIMIT_PPM,
            }
        if not all(row["pass"] for row in results.values()):
            raise RuntimeError("Goal5848 strong baseline competence gate fails")
        result = {
            "schema": "rtdl.goal5848.baseline_competence.v1",
            "status": "PASS__STRONG_PYOPTIX_COMPETENT_FOR_BOTH_TASKS",
            "source_commit": args.expected_source_commit,
            "predecessor_commit": args.expected_predecessor_commit,
            "preregistration_sha256": preregistration[
                "preregistration_sha256"
            ],
            "worker_count": len(receipts),
            "process_count": len(process_rows),
            "engineering_timing_worker_count": len(receipts),
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
            "hardware": receipts[0]["hardware"],
            "tasks": results,
            "processes": process_rows,
            "worker_receipt_sha256": [
                row["result_sha256"] for row in receipts
            ],
            "retry_count": 0,
            "discard_count": 0,
            "included_in_formal_estimators": False,
            "external_review_complete": False,
            "public_or_manuscript_claim_authorized": False,
        }
        result["authority_sha256"] = digest(result)
        _write_create(output_root / "authority.json", result)
        print(json.dumps(result, sort_keys=True))
    except BaseException as error:
        failure = {
            "schema": "rtdl.goal5848.baseline_competence_failure.v1",
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
