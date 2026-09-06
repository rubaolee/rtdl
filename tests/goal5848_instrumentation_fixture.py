from __future__ import annotations

import hashlib
import json
from pathlib import Path

from experiments.goal5848_strong_baseline import contracts
from scripts import goal5848_run_instrumentation_overhead as instrumentation


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_instrumentation_fixture(
    root: Path,
    *,
    source_commit: str,
    predecessor_commit: str,
    preregistration_sha256: str,
    hardware: dict[str, object],
    python_path: Path,
    candidate_manifest: Path,
) -> tuple[Path, dict[str, object]]:
    instrumentation_root = root / "instrumentation"
    workers_root = instrumentation_root / "workers"
    processes_root = instrumentation_root / "processes"
    workers_root.mkdir(parents=True)
    processes_root.mkdir()
    worker_rows = []
    process_rows = []
    phases_by_worker = {}
    for scheduled in contracts.build_instrumentation_schedule():
        worker_id = str(scheduled["worker_id"])
        task = str(scheduled["task"])
        block = int(scheduled["block"])
        mode = str(scheduled["mode"])
        replicate = int(scheduled["replicate"])
        enabled = mode == "on"
        endpoint = 104 if enabled else 100
        partition = {name: 0 for name in contracts.PARTITION_KEYS}
        partition["unattributed_control_plane"] = 0 if enabled else endpoint
        if enabled:
            partition["canonical_input_construction"] = endpoint
        implementation_endpoint = endpoint + 11
        components = {
            name: (1 if enabled and name == "cuda_primary_context" else None)
            for name in contracts.COMPONENT_DIAGNOSTIC_KEYS
        }
        worker = {
            "schema": contracts.WORKER_SCHEMA,
            "status": "PASS__GOAL5848_WORKER",
            "arm": contracts.RTDL_ARM,
            "task": task,
            "block": block,
            "worker_id": worker_id,
            "classification": "exploration",
            "warmups": 1,
            "repetitions": 1,
            "python": "3.12",
            "source": {
                "commit": source_commit,
                "tree": "c" * 40,
                "status": "",
                "clean": True,
            },
            "hardware": hardware,
            "measurements": {
                "implementation_import_ns": 10,
                "implementation_entry_to_first_correct_result_ns": (
                    implementation_endpoint
                ),
                "implementation_import_to_endpoint_gap_ns": 1,
                "post_import_to_first_correct_result_ns": endpoint,
                "endpoint_partition_ns": partition,
                "component_diagnostics_ns": components,
                "evidence": {
                    "phase_instrumentation": enabled,
                    "provider_initialization_phases_ns": (
                        {"native_runtime_warm": 1} if enabled else {}
                    ),
                    "output_sha256": contracts.TASK_CONTRACTS[task][
                        "public_output_sha256"
                    ],
                },
            },
            "claim_boundary": {},
        }
        worker["result_sha256"] = contracts.digest(worker)
        worker_path = workers_root / f"{worker_id}.json"
        _write(worker_path, worker)
        stdout = (json.dumps(worker, sort_keys=True) + "\n").encode()
        family = (
            "bounded_relation"
            if task == contracts.RELATION_TASK
            else "builtin_triangle"
        )
        native_rows = [
            {"family": family, "phase": "prepare.total", "duration_ns": 2},
            {"family": family, "phase": "prepare.gas", "duration_ns": 1},
        ] if enabled else []
        stderr = b"".join(
            (
                "RTDL_GOAL5807_NATIVE_PHASE|"
                f"{row['family']}|{row['phase']}|{row['duration_ns']}\n"
            ).encode("ascii")
            for row in native_rows
        )
        stdout_path = processes_root / f"{worker_id}.stdout"
        stderr_path = processes_root / f"{worker_id}.stderr"
        stdout_path.write_bytes(stdout)
        stderr_path.write_bytes(stderr)
        command = [
            str(python_path),
            "-m",
            "experiments.goal5848_strong_baseline.worker",
            "--arm",
            contracts.RTDL_ARM,
            "--task",
            task,
            "--block",
            str(block),
            "--worker-id",
            worker_id,
            "--classification",
            "exploration",
            "--expected-source-commit",
            source_commit,
            "--candidate-manifest",
            str(candidate_manifest),
            "--phase-instrumentation",
            mode,
            "--warmups",
            "1",
            "--repetitions",
            "1",
            "--output",
            str(worker_path),
        ]
        process = {
            "worker_id": worker_id,
            "command": command,
            "exit_code": 0,
            "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
            "native_phase_rows": native_rows,
        }
        process["process_sha256"] = contracts.digest(process)
        process_path = processes_root / f"{worker_id}.json"
        _write(process_path, process)
        worker_rows.append({
            "worker_id": worker_id,
            "task": task,
            "block": block,
            "mode": mode,
            "replicate": replicate,
            "endpoint_ns": implementation_endpoint,
            "worker_receipt_sha256": worker["result_sha256"],
            "worker_file_sha256": hashlib.sha256(
                worker_path.read_bytes()
            ).hexdigest(),
        })
        process_rows.append({
            "worker_id": worker_id,
            "exit_code": 0,
            "stdout_sha256": process["stdout_sha256"],
            "stderr_sha256": process["stderr_sha256"],
            "native_phase_rows": native_rows,
            "process_sha256": process["process_sha256"],
            "process_file_sha256": hashlib.sha256(
                process_path.read_bytes()
            ).hexdigest(),
        })
        phases_by_worker[worker_id] = native_rows
    value = {
        "schema": contracts.INSTRUMENTATION_AUTHORITY_SCHEMA,
        "status": contracts.INSTRUMENTATION_AUTHORITY_STATUS,
        "source_commit": source_commit,
        "predecessor_commit": predecessor_commit,
        "preregistration_sha256": preregistration_sha256,
        "hardware": hardware,
        "schedule": list(contracts.build_instrumentation_schedule()),
        "worker_count": len(worker_rows),
        "process_count": len(process_rows),
        "worker_receipts": worker_rows,
        "process_receipts": process_rows,
        "tasks": instrumentation._evaluate(worker_rows, phases_by_worker),
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "included_in_formal_estimators": False,
        "retry_count": 0,
        "discard_count": 0,
        "public_or_manuscript_claim_authorized": False,
    }
    value["authority_sha256"] = contracts.digest(value)
    authority_path = instrumentation_root / "authority.json"
    _write(authority_path, value)
    return authority_path, value
