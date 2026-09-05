#!/usr/bin/env python3
"""Run fresh-process Goal5848 exact AOT cache-hit probes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

from experiments.goal5848_strong_baseline.contracts import (
    AOT_HIT_ABSOLUTE_LIMIT_NS,
    AOT_HIT_COLD_RATIO_LIMIT_PPM,
    AOT_HIT_REPETITIONS,
    TASKS,
    digest,
    integer_median,
    ratio_ppm,
    require_formal_cache_policy,
    strict_json_loads,
)
from experiments.goal5848_strong_baseline.controller import _new_output_root
from experiments.goal5848_strong_baseline.worker import ROOT, _write_create


def _read_json(path: Path) -> dict[str, object]:
    value = strict_json_loads(
        path.resolve(strict=True).read_text(encoding="utf-8"),
        label="Goal5848 AOT hit",
    )
    if not isinstance(value, dict):
        raise TypeError("Goal5848 AOT hit object required")
    return value


def _validate_worker(
    value: dict[str, object],
    *,
    worker_id: str,
    task: str,
    source_commit: str,
    request_identity: str,
) -> None:
    unsigned = dict(value)
    seal = unsigned.pop("receipt_sha256", None)
    if (
        seal != digest(unsigned)
        or value.get("schema") != "rtdl.goal5848.aot_fresh_process_hit.v1"
        or value.get("status")
        != "PASS__EXACT_VERIFIED_HIT__NO_PRODUCER_NO_COMPILER"
        or value.get("worker_id") != worker_id
        or value.get("task") != task
        or value.get("source_commit") != source_commit
        or value.get("request_identity_sha256") != request_identity
        or type(value.get("pid")) is not int
        or type(value.get("duration_ns")) is not int
        or value["duration_ns"] <= 0
        or value.get("cache_hit") is not True
        or value.get("producer_invoked") is not False
        or value.get("producer_call_count") != 0
        or value.get("compiler_modules_before") != []
        or value.get("compiler_modules_after") != []
        or value.get("nvrtc_mappings_before") != []
        or value.get("nvrtc_mappings_after") != []
        or value.get("public_or_manuscript_claim_authorized") is not False
    ):
        raise RuntimeError("Goal5848 AOT fresh-process hit receipt differs")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--repetitions", type=int, default=AOT_HIT_REPETITIONS)
    parser.add_argument("--worker-timeout-seconds", type=int, default=30)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    require_formal_cache_policy()
    if (
        args.repetitions != AOT_HIT_REPETITIONS
        or args.worker_timeout_seconds <= 0
    ):
        raise ValueError("Goal5848 AOT fresh-process probe count differs")
    output_root = _new_output_root(args.output_root)
    output_root.mkdir(parents=True)
    manifest_path = args.candidate_manifest.resolve(strict=True)
    manifest = _read_json(manifest_path)
    rows = manifest.get("rows")
    if (
        manifest.get("schema") != "rtdl.goal5848.aot_candidates.v1"
        or manifest.get("source_commit") != args.expected_source_commit
        or not isinstance(rows, dict)
    ):
        raise RuntimeError("Goal5848 AOT candidate manifest differs")
    process_rows = []
    worker_rows = []
    stage = "INPUT_VALIDATION"
    try:
        for task in TASKS:
            label = "relation" if task == TASKS[0] else "triangle"
            candidate = rows.get(label)
            if (
                not isinstance(candidate, dict)
                or candidate.get("first_resolution_cache_hit") is not False
                or candidate.get("producer_invocation_count") != 1
                or type(candidate.get("first_resolution_ns")) is not int
                or candidate["first_resolution_ns"] <= 0
            ):
                raise RuntimeError("Goal5848 cold AOT evidence differs")
            for repetition in range(args.repetitions):
                worker_id = f"G5848_AOT_{label}_{repetition:02d}"
                stage = worker_id
                output = output_root / f"{worker_id}.json"
                command = [
                    str(args.python.resolve(strict=True)),
                    "-m",
                    "experiments.goal5848_strong_baseline.aot_hit_worker",
                    "--task",
                    task,
                    "--worker-id",
                    worker_id,
                    "--candidate-manifest",
                    str(manifest_path),
                    "--expected-source-commit",
                    args.expected_source_commit,
                    "--output",
                    str(output),
                ]
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
                if (
                    completed.returncode != 0
                    or completed.stderr
                    or not output.is_file()
                ):
                    raise RuntimeError(f"Goal5848 AOT hit failed: {worker_id}")
                value = _read_json(output)
                expected_stdout = json.dumps(value, sort_keys=True) + "\n"
                if completed.stdout.decode("utf-8") != expected_stdout:
                    raise RuntimeError("Goal5848 AOT worker stdout differs")
                _validate_worker(
                    value,
                    worker_id=worker_id,
                    task=task,
                    source_commit=args.expected_source_commit,
                    request_identity=str(
                        candidate["aot_request_identity_sha256"]
                    ),
                )
                process_rows.append(process)
                worker_rows.append(value)
        if len({row["pid"] for row in worker_rows}) != len(worker_rows):
            raise RuntimeError("Goal5848 AOT hits did not use fresh processes")
        task_results = {}
        for task in TASKS:
            label = "relation" if task == TASKS[0] else "triangle"
            candidate = rows[label]
            durations = [
                int(row["duration_ns"])
                for row in worker_rows
                if row["task"] == task
            ]
            median_ns = integer_median(durations)
            cold_ns = int(candidate["first_resolution_ns"])
            relative_ppm = ratio_ppm(median_ns, cold_ns)
            task_results[task] = {
                "cold_first_resolution_ns": cold_ns,
                "fresh_process_hit_durations_ns": durations,
                "fresh_process_hit_median_ns": median_ns,
                "fresh_process_hit_over_cold_ppm": relative_ppm,
                "absolute_limit_ns": AOT_HIT_ABSOLUTE_LIMIT_NS,
                "relative_limit_ppm": AOT_HIT_COLD_RATIO_LIMIT_PPM,
                "pass": (
                    median_ns <= AOT_HIT_ABSOLUTE_LIMIT_NS
                    and relative_ppm <= AOT_HIT_COLD_RATIO_LIMIT_PPM
                ),
            }
        if not all(row["pass"] for row in task_results.values()):
            raise RuntimeError("Goal5848 AOT hit performance gate fails")
        result = {
            "schema": "rtdl.goal5848.aot_cache_authority.v1",
            "status": "PASS__AC8_EXACT_FRESH_PROCESS_AOT_REUSE",
            "source_commit": args.expected_source_commit,
            "candidate_manifest_path": str(manifest_path),
            "candidate_manifest_sha256": hashlib.sha256(
                manifest_path.read_bytes()
            ).hexdigest(),
            "worker_count": len(worker_rows),
            "process_count": len(process_rows),
            "distinct_pid_count": len({row["pid"] for row in worker_rows}),
            "producer_invocation_count_across_hits": 0,
            "compiler_module_count_across_hits": 0,
            "nvrtc_mapping_count_across_hits": 0,
            "qualification_timing_count": len(worker_rows),
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
            "included_in_formal_estimators": False,
            "prior_in_process_hit_timings_included": False,
            "tasks": task_results,
            "processes": process_rows,
            "worker_receipt_sha256": [
                row["receipt_sha256"] for row in worker_rows
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
            "schema": "rtdl.goal5848.aot_cache_failure.v1",
            "status": "FAIL__NO_RETRY_NO_DISCARD",
            "failed_stage": stage,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "completed_worker_count": len(worker_rows),
            "retry_count": 0,
            "discard_count": 0,
        }
        failure["failure_sha256"] = digest(failure)
        _write_create(output_root / "failure.json", failure)
        raise


if __name__ == "__main__":
    main()
