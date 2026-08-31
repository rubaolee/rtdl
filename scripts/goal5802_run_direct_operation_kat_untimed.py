#!/usr/bin/env python3
"""Run the exact Direct first/reuse operation KAT without timing."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from experiments.goal5802_premeasurement.direct_source_audit import (
    audit_direct_source,
)
from experiments.goal5802_premeasurement.runtime_manifest import (
    RELATION_TASK,
    TRIANGLE_TASK,
    digest,
    sha256_file,
    validate_direct_operation_kat,
)
from experiments.goal5802_premeasurement.workload import (
    relation_k_plus_one_workload,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=Path, required=True)
    parser.add_argument("--direct-source", type=Path, required=True)
    parser.add_argument("--ptx", type=Path, required=True)
    parser.add_argument("--compaction-cubin", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    worker = args.worker.resolve(strict=True)
    direct_source = args.direct_source.resolve(strict=True)
    ptx = args.ptx.resolve(strict=True)
    compaction_cubin = args.compaction_cubin.resolve(strict=True)
    files: dict[str, dict[str, object]] = {
        "direct_scalar_worker": {
            "path": str(worker), "sha256": sha256_file(worker)},
        "direct_scalar_source": {
            "path": str(direct_source), "sha256": sha256_file(direct_source)},
        "matched_ptx": {"path": str(ptx), "sha256": sha256_file(ptx)},
        "compaction_cubin": {
            "path": str(compaction_cubin),
            "sha256": sha256_file(compaction_cubin)},
    }
    rows = []
    relation_hostile: dict[str, object] | None = None
    for task in (RELATION_TASK, TRIANGLE_TASK):
        command = [
            str(worker), "--local-untimed-functional", "--task", task,
            "--ptx", str(ptx),
        ]
        if task == RELATION_TASK:
            command.extend(["--compaction-cubin", str(compaction_cubin)])
        completed = subprocess.run(command, capture_output=True, check=False)
        try:
            stdout_utf8 = completed.stdout.decode("utf-8")
            stderr_utf8 = completed.stderr.decode("utf-8")
            receipt = json.loads(stdout_utf8)
        except (UnicodeError, json.JSONDecodeError) as error:
            raise RuntimeError(
                f"Direct untimed operation KAT output is not JSON: {task}") \
                from error
        if task == RELATION_TASK:
            observed = receipt.get("relation_k_plus_one_hostile")
            workload = relation_k_plus_one_workload()
            if not isinstance(observed, dict) \
                    or observed.get("packed_input_sha256") \
                    != workload["packed_input_sha256"]:
                raise RuntimeError(
                    "Direct K+1 worker input/evidence receipt differs")
            relation_hostile = {
                **observed,
                "arm": "A_DIRECT_CUDA_OPTIX",
                "workload_sha256": workload["workload_sha256"],
                "registered_performance_timing_count": 0,
                "formal_worker_count": 0,
            }
        rows.append({
            "task": task,
            "command": command,
            "exit_code": completed.returncode,
            "stdout_utf8": stdout_utf8,
            "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
            "stderr_utf8": stderr_utf8,
            "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
            "worker_receipt": receipt,
        })
    if relation_hostile is None:
        raise RuntimeError("Direct K+1 hostile receipt absent")
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.direct_operation_guard_untimed_kat.v1",
        "status": "PASS__UNTIMED_PREWORKER_ACTUAL_DIRECT_OPERATION_GUARD",
        "rows": rows,
        "task_count": 2,
        "guard_inside_comparative_timer": False,
        "source_audit": audit_direct_source(direct_source),
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "untimed_optix_launch_count": 8,
        "untimed_auxiliary_cuda_kernel_launch_count": 3,
        "untimed_gpu_launch_count": 11,
        "relation_k_plus_one_hostile": relation_hostile,
    }
    value["receipt_sha256"] = digest(value)
    validate_direct_operation_kat(value, files)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": value["status"],
        "receipt_sha256": value["receipt_sha256"],
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "untimed_gpu_launch_count": 11,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
