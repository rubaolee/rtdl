#!/usr/bin/env python3
"""Timer-free Direct CUDA/OptiX correctness witness for Goal5842."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from experiments.goal5842_causal_admission.contracts import (
    BASELINE_TASKS,
    DIRECT_IDENTITY_WITNESS_SCHEMA,
    RELATION_TASK,
    digest,
)
from experiments.goal5842_causal_admission.runtime import (
    create_json,
    load_execution_authority,
    require_bound_path,
    require_idle_bound_gpu,
)
from experiments.goal5842_causal_admission.tasks import build_task

ROOT = Path(__file__).resolve().parents[1]
RAW_SCHEMA = "rtdl.goal5842.direct_identity_witness_raw.v1"
WITNESS_MODE = "CORRECTNESS_WITNESS_NO_TIMING"
MEASUREMENT_CONTRACT = "GOAL5842_WITNESS_NO_TIMING_V1"


def _contains_duration_field(value: object) -> bool:
    if isinstance(value, dict):
        return any(
            (
                str(key) != "duration_field_count"
                and ("duration" in str(key).lower() or str(key).lower().endswith("_ns"))
            )
            or _contains_duration_field(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_duration_field(item) for item in value)
    return False


def _expected_header_version(version: str) -> int:
    parts = [int(part) for part in version.split(".")]
    parts.extend([0] * (3 - len(parts)))
    return parts[0] * 10_000 + parts[1] * 100 + parts[2]


def _run_task(
    args: argparse.Namespace,
    authority: dict[str, Any],
    task_id: str,
) -> dict[str, object]:
    task = build_task(task_id)
    worker_id = f"DIRECT_WITNESS__{task_id}"
    ticket = hashlib.sha256(
        f"{authority['authority_sha256']}:{worker_id}".encode("ascii")
    ).hexdigest()
    command = [
        str(args.direct_binary.resolve()),
        "--worker-id",
        worker_id,
        "--task",
        task_id,
        "--mode",
        WITNESS_MODE,
        "--device-source",
        str(args.device_source.resolve()),
        "--optix-include",
        str(args.optix_include.resolve()),
        "--cuda-include",
        str(args.cuda_include.resolve()),
        "--freeze-sha256",
        authority["preregistration_sha256"],
        "--controller-ticket",
        ticket,
        "--measurement-contract",
        MEASUREMENT_CONTRACT,
    ]
    environment = os.environ.copy()
    environment["GOAL5798_FORMAL_CONTROLLER_PID"] = str(os.getpid())
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Direct witness failed for {task_id}: {completed.stderr.strip()}"
        )
    raw = json.loads(completed.stdout)
    if (
        raw.get("schema") != RAW_SCHEMA
        or raw.get("status") != "PASS"
        or raw.get("worker_id") != worker_id
        or raw.get("task") != task_id
        or raw.get("mode") != WITNESS_MODE
        or raw.get("freeze_sha256") != authority["preregistration_sha256"]
        or raw.get("controller_ticket") != ticket
        or raw.get("optix_header_version")
        != _expected_header_version(authority["toolchain"]["optix_sdk"])
        or raw.get("clock_api_called_by_witness_path") is not False
        or raw.get("duration_field_count") != 0
        or _contains_duration_field(raw)
    ):
        raise RuntimeError(f"Direct witness identity/timing contract failed: {task_id}")
    correctness = raw.get("correctness")
    if (
        not isinstance(correctness, dict)
        or correctness.get("full_oracle_exact") is not True
    ):
        raise RuntimeError(f"Direct witness oracle marker missing: {task_id}")
    if task_id == RELATION_TASK:
        observed = tuple(
            tuple(int(item) for item in row) for row in correctness["canonical_rows"]
        )
        expected = task.expected_output
        public_output: object = observed
        full_output: object = observed
        if correctness.get("device_overflow") != 0:
            raise RuntimeError("Direct relation witness overflowed")
    else:
        observed_per_ray = tuple(int(item) for item in correctness["per_ray"])
        observed_weighted = int(correctness["weighted_sum"])
        expected = task.expected_output
        public_output = observed_weighted
        full_output = {
            "weighted_sum": observed_weighted,
            "per_ray": observed_per_ray,
        }
    if full_output != expected or correctness.get("device_status") != 0:
        raise RuntimeError(f"Direct witness output mismatch: {task_id}")
    return {
        "task": task_id,
        "input_sha256": task.input_sha256,
        "public_output_sha256": digest(public_output),
        "full_oracle_sha256": digest(full_output),
        "full_oracle_exact": True,
        "gpu_complete_execution_call_count": 1,
        "optix_launch_count": int(raw["optix_launch_count"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--direct-binary", type=Path, required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prereg, authority = load_execution_authority(
        args.execution_authority,
        preregistration_path=args.preregistration,
        root=ROOT,
        require_clean_repository=True,
    )
    for key, supplied in (
        ("direct_binary", args.direct_binary),
        ("device_source", args.device_source),
        ("optix_include", args.optix_include),
        ("cuda_include", args.cuda_include),
    ):
        require_bound_path(authority, key, supplied)
    require_idle_bound_gpu(authority)
    rows = [_run_task(args, authority, task_id) for task_id in BASELINE_TASKS]
    result: dict[str, object] = {
        "schema": DIRECT_IDENTITY_WITNESS_SCHEMA,
        "status": "PASS__DIRECT_FULL_ORACLE_NO_TIMING_OBSERVED",
        "source_commit": authority["source_commit"],
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "hardware": authority["hardware"],
        "direct_binary_sha256": authority["execution_paths"]["direct_binary_sha256"],
        "device_source_sha256": authority["execution_paths"]["device_source_sha256"],
        "tasks": rows,
        "task_count": len(rows),
        "gpu_complete_execution_call_count": sum(
            int(row["gpu_complete_execution_call_count"]) for row in rows
        ),
        "optix_launch_count": sum(int(row["optix_launch_count"]) for row in rows),
        "registered_timing_observation_count": 0,
        "clock_api_called_by_witness_module": False,
        "clock_api_called_by_direct_witness_path": False,
        "duration_field_count": 0,
        "performance_claim_authorized": False,
    }
    result["witness_sha256"] = digest(result)
    create_json(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
