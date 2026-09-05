#!/usr/bin/env python3
"""Run all eight Goal5848 primary arm/task witnesses without registered timing."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

from experiments.goal5848_strong_baseline.contracts import (
    DIRECT_OPTIX_ARM,
    IDIOMATIC_PYOPTIX_ARM,
    PRIMARY_ARMS,
    RELATION_TASK,
    RTDL_ARM,
    STRONG_PYOPTIX_ARM,
    TASK_CONTRACTS,
    TASKS,
    digest,
    require_formal_cache_policy,
    strict_json_loads,
)
from experiments.goal5848_strong_baseline.controller import (
    _new_output_root,
    _validate_preregistration,
)
from experiments.goal5848_strong_baseline.worker import ROOT, _write_create


def _read_json(path: Path) -> dict[str, object]:
    value = strict_json_loads(
        path.resolve(strict=True).read_text(encoding="utf-8"),
        label="Goal5848 preflight worker",
    )
    if not isinstance(value, dict):
        raise TypeError("Goal5848 preflight worker object required")
    return value


def _command(
    arm: str,
    task: str,
    args: argparse.Namespace,
    output: Path,
) -> list[str]:
    command = [
        str(args.python.resolve(strict=True)),
        "-m",
        "experiments.goal5848_strong_baseline.preflight_worker",
        "--arm",
        arm,
        "--task",
        task,
        "--output",
        str(output),
    ]
    if arm == RTDL_ARM:
        return [
            *command,
            "--candidate-manifest",
            str(args.candidate_manifest.resolve(strict=True)),
        ]
    command.extend([
        "--precompiled-ptx",
        str(args.precompiled_ptx.resolve(strict=True)),
    ])
    if arm in {IDIOMATIC_PYOPTIX_ARM, STRONG_PYOPTIX_ARM}:
        command.extend([
            "--pyoptix-source",
            str(args.pyoptix_source.resolve(strict=True)),
            "--pyoptix-build-receipt",
            str(args.pyoptix_build_receipt.resolve(strict=True)),
            "--expected-optix-sdk",
            args.expected_optix_sdk,
        ])
    if arm == DIRECT_OPTIX_ARM:
        command.extend([
            "--direct-worker",
            str(args.direct_worker.resolve(strict=True)),
        ])
    if task == RELATION_TASK and arm in {
        STRONG_PYOPTIX_ARM,
        DIRECT_OPTIX_ARM,
    }:
        command.extend([
            "--compaction-cubin",
            str(args.compaction_cubin.resolve(strict=True)),
        ])
    return command


def _validate_worker(value: dict[str, object], *, arm: str, task: str) -> None:
    unsigned = dict(value)
    seal = unsigned.pop("receipt_sha256", None)
    details = value.get("details")
    if (
        seal != digest(unsigned)
        or value.get("schema")
        != "rtdl.goal5848.timer_free_preflight_worker.v1"
        or value.get("status") != "PASS__UNTIMED_EXACT_PHYSICAL_WITNESS"
        or value.get("arm") != arm
        or value.get("task") != task
        or not isinstance(details, dict)
        or details.get("output_sha256")
        != TASK_CONTRACTS[task]["public_output_sha256"]
        or type(details.get("execution_count")) is not int
        or details["execution_count"] < 2
        or value.get("clock_read_count") != 0
        or value.get("registered_performance_timing_count") != 0
        or value.get("formal_worker_count") != 0
        or value.get("external_review_complete") is not False
        or value.get("public_or_manuscript_claim_authorized") is not False
    ):
        raise RuntimeError("Goal5848 timer-free preflight worker differs")


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--expected-predecessor-commit", required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--predecessor-root", type=Path, required=True)
    parser.add_argument("--predecessor-candidate-manifest", type=Path, required=True)
    parser.add_argument("--precompiled-ptx", type=Path, required=True)
    parser.add_argument("--compaction-cubin", type=Path, required=True)
    parser.add_argument(
        "--device-artifact-build-receipt", type=Path, required=True
    )
    parser.add_argument("--pyoptix-source", type=Path, required=True)
    parser.add_argument("--expected-pyoptix-commit", required=True)
    parser.add_argument("--expected-pyoptix-tree", required=True)
    parser.add_argument("--pyoptix-build-receipt", type=Path, required=True)
    parser.add_argument("--expected-optix-sdk", required=True)
    parser.add_argument("--direct-worker", type=Path, required=True)
    parser.add_argument("--direct-build-receipt", type=Path, required=True)
    parser.add_argument("--derivation-receipt", type=Path, required=True)
    parser.add_argument("--aot-cache-authority", type=Path, required=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    _add_common_arguments(parser)
    parser.add_argument("--worker-timeout-seconds", type=int, default=300)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    require_formal_cache_policy()
    if args.worker_timeout_seconds <= 0:
        raise ValueError("Goal5848 preflight timeout differs")
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
    processes = []
    receipts = []
    stage = "START"
    try:
        for task in TASKS:
            for arm in PRIMARY_ARMS:
                worker_id = f"G5848_PREFLIGHT_{task}_{arm}"
                stage = worker_id
                output = workers / f"{worker_id}.json"
                command = _command(arm, task, args, output)
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
                process = {
                    "worker_id": worker_id,
                    "command": command,
                    "exit_code": completed.returncode,
                    "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
                    "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
                }
                processes.append(process)
                if (
                    completed.returncode != 0
                    or completed.stderr
                    or not output.is_file()
                ):
                    raise RuntimeError(
                        f"Goal5848 timer-free preflight failed: {worker_id}"
                    )
                value = _read_json(output)
                if completed.stdout.decode("utf-8") != (
                    json.dumps(value, sort_keys=True) + "\n"
                ):
                    raise RuntimeError("Goal5848 preflight stdout differs")
                _validate_worker(value, arm=arm, task=task)
                receipts.append(value)
        hardware = {
            json.dumps(row["hardware"], sort_keys=True) for row in receipts
        }
        if len(hardware) != 1:
            raise RuntimeError("Goal5848 preflight GPU identity differs")
        result = {
            "schema": "rtdl.goal5848.timer_free_witness_authority.v1",
            "status": "PASS__ALL_EIGHT_PRIMARY_ARM_TASK_WITNESSES",
            "source_commit": args.expected_source_commit,
            "predecessor_commit": args.expected_predecessor_commit,
            "preregistration_sha256": preregistration[
                "preregistration_sha256"
            ],
            "preregistration_file_sha256": hashlib.sha256(
                args.preregistration.resolve(strict=True).read_bytes()
            ).hexdigest(),
            "worker_count": len(receipts),
            "process_count": len(processes),
            "clock_read_count": 0,
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
            "hardware": receipts[0]["hardware"],
            "processes": processes,
            "worker_receipt_sha256": [
                row["receipt_sha256"] for row in receipts
            ],
            "retry_count": 0,
            "discard_count": 0,
            "external_review_complete": False,
            "public_or_manuscript_claim_authorized": False,
        }
        result["authority_sha256"] = digest(result)
        _write_create(output_root / "authority.json", result)
        print(json.dumps(result, sort_keys=True))
    except BaseException as error:
        failure = {
            "schema": "rtdl.goal5848.timer_free_witness_failure.v1",
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
