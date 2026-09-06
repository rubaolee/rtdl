#!/usr/bin/env python3
"""Combine untimed witnesses and nonformal competence into Goal5848 gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections.abc import Mapping
from pathlib import Path

from experiments.goal5848_strong_baseline.aot_cache_authority import (
    load_aot_cache_authority,
)
from experiments.goal5848_strong_baseline.contracts import (
    INSTRUMENTATION_AUTHORITY_SCHEMA,
    INSTRUMENTATION_AUTHORITY_STATUS,
    INSTRUMENTATION_OVERHEAD_LIMIT_PPM,
    PREFLIGHT_PASS_STATUS,
    PREFLIGHT_SCHEMA,
    PREREGISTRATION_SCHEMA,
    TASKS,
    digest,
    instrumentation_protocol,
    integer_median,
    ratio_ppm,
    strict_json_loads,
)
from experiments.goal5848_strong_baseline.controller import _new_output_root
from experiments.goal5848_strong_baseline.device_artifacts import (
    load_device_artifact_receipt,
)


def _read_sealed(
    path: Path,
    *,
    schema: str,
    status: str,
) -> tuple[dict[str, object], str]:
    resolved = path.resolve(strict=True)
    value = strict_json_loads(
        resolved.read_text(encoding="utf-8"),
        label="Goal5848 preflight input",
    )
    if not isinstance(value, dict):
        raise TypeError("Goal5848 preflight input must be an object")
    unsigned = dict(value)
    seal = unsigned.pop("authority_sha256", None)
    if (
        seal != digest(unsigned)
        or value.get("schema") != schema
        or value.get("status") != status
    ):
        raise RuntimeError("Goal5848 preflight input authority differs")
    return value, hashlib.sha256(resolved.read_bytes()).hexdigest()


def _write_create(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )
    try:
        payload = json.dumps(value, indent=2, sort_keys=True).encode("ascii") + b"\n"
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = -1
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _validate_instrumentation_summary(
    value: Mapping[str, object],
) -> None:
    """Recompute the v2 pair-first estimator from authority-bound rows."""

    expected_authority_keys = {
        "schema", "status", "source_commit", "predecessor_commit",
        "preregistration_sha256", "hardware", "schedule", "worker_count",
        "process_count", "worker_receipts", "process_receipts", "tasks",
        "registered_performance_timing_count", "formal_worker_count",
        "included_in_formal_estimators", "retry_count", "discard_count",
        "public_or_manuscript_claim_authorized", "authority_sha256",
    }
    protocol = instrumentation_protocol()
    schedule = protocol["schedule"]
    workers = value.get("worker_receipts")
    processes = value.get("process_receipts")
    tasks = value.get("tasks")
    if (
        set(value) != expected_authority_keys
        or not isinstance(schedule, list)
        or not isinstance(workers, list)
        or not isinstance(processes, list)
        or len(workers) != len(schedule)
        or len(processes) != len(schedule)
        or not isinstance(tasks, Mapping)
        or set(tasks) != set(TASKS)
    ):
        raise RuntimeError("Goal5848 instrumentation evidence rows differ")

    indexed: dict[tuple[str, int, str], int] = {}
    phases_by_worker: dict[str, list[Mapping[str, object]]] = {}
    for scheduled, worker, process in zip(schedule, workers, processes):
        if (
            not isinstance(scheduled, Mapping)
            or not isinstance(worker, Mapping)
            or set(worker) != {
                "worker_id", "task", "block", "mode", "endpoint_ns",
                "worker_receipt_sha256", "worker_file_sha256",
            }
            or not isinstance(process, Mapping)
            or set(process) != {
                "worker_id", "exit_code", "stdout_sha256", "stderr_sha256",
                "native_phase_rows", "process_sha256",
                "process_file_sha256",
            }
            or worker.get("worker_id") != scheduled.get("worker_id")
            or worker.get("task") != scheduled.get("task")
            or worker.get("block") != scheduled.get("block")
            or worker.get("mode") != scheduled.get("mode")
            or type(worker.get("endpoint_ns")) is not int
            or worker["endpoint_ns"] <= 0
            or not _is_sha256(worker.get("worker_receipt_sha256"))
            or not _is_sha256(worker.get("worker_file_sha256"))
            or process.get("worker_id") != scheduled.get("worker_id")
            or process.get("exit_code") != 0
            or not _is_sha256(process.get("stdout_sha256"))
            or not _is_sha256(process.get("stderr_sha256"))
            or not _is_sha256(process.get("process_sha256"))
            or not _is_sha256(process.get("process_file_sha256"))
            or not isinstance(process.get("native_phase_rows"), list)
        ):
            raise RuntimeError("Goal5848 instrumentation receipt differs")
        native_rows = process["native_phase_rows"]
        if scheduled["mode"] == "off" and (
            native_rows
            or process["stderr_sha256"] != hashlib.sha256(b"").hexdigest()
        ):
            raise RuntimeError("Goal5848 plain instrumentation evidence differs")
        for phase in native_rows:
            if (
                not isinstance(phase, Mapping)
                or set(phase) != {"family", "phase", "duration_ns"}
                or not isinstance(phase.get("family"), str)
                or not isinstance(phase.get("phase"), str)
                or type(phase.get("duration_ns")) is not int
                or phase["duration_ns"] < 0
            ):
                raise RuntimeError("Goal5848 instrumentation phase row differs")
        key = (
            str(scheduled["task"]),
            int(scheduled["block"]),
            str(scheduled["mode"]),
        )
        if key in indexed:
            raise RuntimeError("Goal5848 instrumentation pair is duplicated")
        indexed[key] = int(worker["endpoint_ns"])
        phases_by_worker[str(scheduled["worker_id"])] = native_rows

    expected_task_keys = {
        "blocks", "uninstrumented_endpoint_median_ns",
        "instrumented_endpoint_median_ns",
        "paired_on_over_off_ppm_by_block",
        "paired_on_over_off_median_ppm",
        "measured_instrumentation_overhead_ns",
        "instrumentation_overhead_ppm", "estimator", "limit_ppm",
        "native_phase_names", "pass",
    }
    for task in TASKS:
        off_values = []
        on_values = []
        ratios = []
        blocks = []
        for block in range(int(protocol["blocks"])):
            off_ns = indexed[(task, block, "off")]
            on_ns = indexed[(task, block, "on")]
            paired_ratio = ratio_ppm(on_ns, off_ns)
            off_values.append(off_ns)
            on_values.append(on_ns)
            ratios.append(paired_ratio)
            blocks.append({
                "block": block,
                "off_ns": off_ns,
                "on_ns": on_ns,
                "signed_difference_ns": on_ns - off_ns,
                "on_over_off_ppm": paired_ratio,
            })
        off_median = integer_median(off_values)
        on_median = integer_median(on_values)
        ratio_median = integer_median(ratios)
        overhead_ppm = max(0, ratio_median - 1_000_000)
        overhead_ns = (off_median * overhead_ppm + 500_000) // 1_000_000
        expected_family = (
            "bounded_relation" if task == TASKS[0] else "builtin_triangle"
        )
        phase_names = sorted({
            str(phase["phase"])
            for scheduled in schedule
            if scheduled["task"] == task and scheduled["mode"] == "on"
            for phase in phases_by_worker[str(scheduled["worker_id"])]
            if phase["family"] == expected_family
        })
        expected = {
            "blocks": blocks,
            "uninstrumented_endpoint_median_ns": off_median,
            "instrumented_endpoint_median_ns": on_median,
            "paired_on_over_off_ppm_by_block": ratios,
            "paired_on_over_off_median_ppm": ratio_median,
            "measured_instrumentation_overhead_ns": overhead_ns,
            "instrumentation_overhead_ppm": overhead_ppm,
            "estimator": protocol["estimator"],
            "limit_ppm": protocol["limit_ppm"],
            "native_phase_names": phase_names,
            "pass": overhead_ppm <= int(protocol["limit_ppm"]),
        }
        observed = tasks[task]
        if (
            not isinstance(observed, Mapping)
            or set(observed) != expected_task_keys
            or dict(observed) != expected
            or "prepare.total" not in phase_names
            or "prepare.gas" not in phase_names
            or expected["pass"] is not True
        ):
            raise RuntimeError("Goal5848 instrumentation summary differs")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--expected-predecessor-commit", required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--timer-free-witness", type=Path, required=True)
    parser.add_argument("--baseline-competence", type=Path, required=True)
    parser.add_argument("--instrumentation-overhead", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    preregistration_path = args.preregistration.resolve(strict=True)
    preregistration = strict_json_loads(
        preregistration_path.read_text(encoding="utf-8"),
        label="Goal5848 preregistration",
    )
    if not isinstance(preregistration, dict):
        raise TypeError("Goal5848 preregistration must be an object")
    preregistration_sha256 = preregistration.get("preregistration_sha256")
    preregistration_unsigned = dict(preregistration)
    preregistration_unsigned.pop("preregistration_sha256", None)
    if (
        preregistration_sha256 != digest(preregistration_unsigned)
        or preregistration.get("schema") != PREREGISTRATION_SCHEMA
        or preregistration.get("status")
        != "FROZEN__BEFORE_FORMAL_WORKER_ZERO"
        or preregistration.get("source_commit")
        != args.expected_source_commit
        or preregistration.get("predecessor_commit")
        != args.expected_predecessor_commit
    ):
        raise RuntimeError("Goal5848 preregistration authority differs")
    witness, witness_file_sha256 = _read_sealed(
        args.timer_free_witness,
        schema="rtdl.goal5848.timer_free_witness_authority.v1",
        status="PASS__ALL_EIGHT_PRIMARY_ARM_TASK_WITNESSES",
    )
    competence, competence_file_sha256 = _read_sealed(
        args.baseline_competence,
        schema="rtdl.goal5848.baseline_competence.v1",
        status="PASS__STRONG_PYOPTIX_COMPETENT_FOR_BOTH_TASKS",
    )
    instrumentation, instrumentation_file_sha256 = _read_sealed(
        args.instrumentation_overhead,
        schema=INSTRUMENTATION_AUTHORITY_SCHEMA,
        status=INSTRUMENTATION_AUTHORITY_STATUS,
    )
    competence_tasks = competence.get("tasks")
    instrumentation_tasks = instrumentation.get("tasks")
    protocol = instrumentation_protocol()
    _validate_instrumentation_summary(instrumentation)
    artifacts = preregistration.get("artifacts")
    if not isinstance(artifacts, dict):
        raise TypeError("Goal5848 preregistration artifacts are absent")
    try:
        device_receipt = artifacts["device_artifact_build_receipt"]
        precompiled_ptx = artifacts["precompiled_ptx"]
        compaction_cubin = artifacts["compaction_cubin"]
        aot_cache_authority = artifacts["aot_cache_authority"]
        candidate_manifest = artifacts["candidate_manifest"]
        hardware = witness["hardware"]
        load_device_artifact_receipt(
            Path(str(device_receipt["path"])),
            precompiled_ptx=Path(str(precompiled_ptx["path"])),
            compaction_cubin=Path(str(compaction_cubin["path"])),
            expected_source_commit=args.expected_source_commit,
            expected_optix_sdk=str(preregistration["expected_optix_sdk"]),
            expected_compute_capability=str(hardware["compute_capability"]),
        )
        load_aot_cache_authority(
            Path(str(aot_cache_authority["path"])),
            candidate_manifest=Path(str(candidate_manifest["path"])),
            expected_source_commit=args.expected_source_commit,
        )
    except (KeyError, TypeError) as error:
        raise RuntimeError(
            "Goal5848 device artifact/preflight hardware binding differs"
        ) from error
    if (
        witness.get("source_commit") != args.expected_source_commit
        or competence.get("source_commit") != args.expected_source_commit
        or instrumentation.get("source_commit") != args.expected_source_commit
        or witness.get("predecessor_commit")
        != args.expected_predecessor_commit
        or competence.get("predecessor_commit")
        != args.expected_predecessor_commit
        or instrumentation.get("predecessor_commit")
        != args.expected_predecessor_commit
        or witness.get("preregistration_sha256")
        != preregistration_sha256
        or competence.get("preregistration_sha256")
        != preregistration_sha256
        or instrumentation.get("preregistration_sha256")
        != preregistration_sha256
        or witness.get("hardware") != competence.get("hardware")
        or witness.get("hardware") != instrumentation.get("hardware")
        or witness.get("registered_performance_timing_count") != 0
        or competence.get("registered_performance_timing_count") != 0
        or instrumentation.get("registered_performance_timing_count") != 0
        or witness.get("formal_worker_count") != 0
        or competence.get("formal_worker_count") != 0
        or instrumentation.get("formal_worker_count") != 0
        or witness.get("worker_count") != 8
        or witness.get("process_count") != 8
        or competence.get("worker_count") != 4
        or competence.get("process_count") != 4
        or competence.get("included_in_formal_estimators") is not False
        or witness.get("retry_count") != 0
        or witness.get("discard_count") != 0
        or competence.get("retry_count") != 0
        or competence.get("discard_count") != 0
        or instrumentation.get("worker_count") != protocol["worker_count"]
        or instrumentation.get("process_count") != protocol["worker_count"]
        or instrumentation.get("schedule") != protocol["schedule"]
        or instrumentation.get("retry_count") != 0
        or instrumentation.get("discard_count") != 0
        or instrumentation.get("included_in_formal_estimators") is not False
        or instrumentation.get("public_or_manuscript_claim_authorized")
        is not False
        or not isinstance(competence_tasks, dict)
        or set(competence_tasks) != set(TASKS)
        or not all(
            isinstance(competence_tasks[task], dict)
            and competence_tasks[task].get("pass") is True
            for task in TASKS
        )
        or not isinstance(instrumentation_tasks, dict)
        or set(instrumentation_tasks) != set(TASKS)
        or not all(
            isinstance(instrumentation_tasks[task], dict)
            and instrumentation_tasks[task].get("pass") is True
            and instrumentation_tasks[task].get("limit_ppm")
            == INSTRUMENTATION_OVERHEAD_LIMIT_PPM
            and type(instrumentation_tasks[task].get(
                "instrumentation_overhead_ppm"
            )) is int
            and instrumentation_tasks[task]["instrumentation_overhead_ppm"]
            <= INSTRUMENTATION_OVERHEAD_LIMIT_PPM
            for task in TASKS
        )
    ):
        raise RuntimeError("Goal5848 preflight authorities disagree")
    value = {
        "schema": PREFLIGHT_SCHEMA,
        "status": PREFLIGHT_PASS_STATUS,
        "source_commit": args.expected_source_commit,
        "predecessor_commit": args.expected_predecessor_commit,
        "preregistration_path": str(preregistration_path),
        "preregistration_file_sha256": hashlib.sha256(
            preregistration_path.read_bytes()
        ).hexdigest(),
        "preregistration_sha256": preregistration_sha256,
        "timer_free_witness_path": str(
            args.timer_free_witness.resolve(strict=True)
        ),
        "timer_free_witness_file_sha256": witness_file_sha256,
        "timer_free_witness_sha256": witness["authority_sha256"],
        "baseline_competence_path": str(
            args.baseline_competence.resolve(strict=True)
        ),
        "baseline_competence_file_sha256": competence_file_sha256,
        "baseline_competence_sha256": competence["authority_sha256"],
        "instrumentation_overhead_path": str(
            args.instrumentation_overhead.resolve(strict=True)
        ),
        "instrumentation_overhead_file_sha256": instrumentation_file_sha256,
        "instrumentation_overhead_sha256": instrumentation[
            "authority_sha256"
        ],
        "hardware": witness["hardware"],
        "untimed_witness_worker_count": witness["worker_count"],
        "nonformal_competence_worker_count": competence["worker_count"],
        "nonformal_instrumentation_worker_count": instrumentation[
            "worker_count"
        ],
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "retry_count": 0,
        "discard_count": 0,
        "competence_timings_included_in_formal_estimators": False,
        "instrumentation_timings_included_in_formal_estimators": False,
        "external_review_complete": False,
        "public_or_manuscript_claim_authorized": False,
    }
    value["preflight_sha256"] = digest(value)
    _write_create(_new_output_root(args.output), value)
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
