#!/usr/bin/env python3
"""Shared, fail-closed Goal5798 worker protocol.

This module is intentionally GPU-free.  All three execution arms use the same
schedule lookup, execution-authority check, output schema, and create-only
receipt writer.  Importing it cannot initialize CUDA or OptiX.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import time
from typing import Any, Callable

from contract_runtime import (
    MEMORY_MODE,
    canonical,
    digest,
    load_freeze,
)


SCHEMA = "rtdl.goal5798.worker_payload_receipt.v1"
AUTHORITY_SCHEMA = "rtdl.goal5798.execution_authority.v1"
RUNTIME_MANIFEST_SCHEMA = "rtdl.goal5798.runtime_manifest.v1"
PREPARED_WARMUPS = 8
PREPARED_REPETITIONS = 64


def sha256_file(path: Path) -> str:
    block = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            block.update(chunk)
    return block.hexdigest()


def now_ns() -> int:
    return time.perf_counter_ns()


def measured(action: Callable[[], Any]) -> tuple[Any, int]:
    start = now_ns()
    value = action()
    return value, now_ns() - start


def median_ns(values: list[int]) -> int:
    if not values or any(type(value) is not int or value < 0 for value in values):
        raise ValueError("duration vector must contain nonnegative integers")
    # Python statistics.median returns float for an even number of ints.  The
    # frozen sample is an integer nanosecond count, so use the exact integer
    # midpoint with floor semantics and disclose the complete vector.
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) // 2


def create_json(path: Path, value: dict[str, Any]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    temporary = path.with_name(
        f".{path.name}.tmp.{os.getpid()}.{time.monotonic_ns()}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(temporary, flags, 0o600)
    try:
        payload = json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        # A hard link publishes a fully written inode without allowing an
        # existing create-only destination to be overwritten.  Consumers can
        # observe either absence or the complete JSON, never an empty prefix.
        os.link(temporary, path)
    finally:
        os.close(descriptor)
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def load_runtime_manifest(path: Path, *, verify_files: bool = True) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != RUNTIME_MANIFEST_SCHEMA:
        raise ValueError("runtime manifest schema mismatch")
    seal = value.get("manifest_sha256")
    unsealed = dict(value)
    unsealed.pop("manifest_sha256", None)
    if not isinstance(seal, str) or digest(unsealed) != seal:
        raise ValueError("runtime manifest seal mismatch")
    files = value.get("files")
    if not isinstance(files, list) or value.get("file_count") != len(files):
        raise ValueError("runtime manifest file count mismatch")
    if len({row.get("path") for row in files if isinstance(row, dict)}) != len(files):
        raise ValueError("runtime manifest duplicate path")
    if value.get("total_bytes") != sum(row.get("bytes", -1) for row in files):
        raise ValueError("runtime manifest byte total mismatch")
    if verify_files:
        root = path.resolve().parents[2]
        for row in files:
            relative = row.get("path")
            if not isinstance(relative, str) or relative.startswith(("/", "\\")) or ".." in Path(relative).parts:
                raise ValueError("unsafe runtime manifest path")
            candidate = root / relative
            if not candidate.is_file():
                raise ValueError(f"runtime file missing: {relative}")
            if candidate.stat().st_size != row.get("bytes") or sha256_file(candidate) != row.get("sha256"):
                raise ValueError(f"runtime file identity mismatch: {relative}")
    return value


def load_execution_authority(
    path: Path,
    *,
    freeze_path: Path,
    freeze: dict[str, Any],
    runtime_manifest: dict[str, Any],
) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != AUTHORITY_SCHEMA:
        raise ValueError("execution authority schema mismatch")
    seal = value.get("authority_sha256")
    unsealed = dict(value)
    unsealed.pop("authority_sha256", None)
    if not isinstance(seal, str) or digest(unsealed) != seal:
        raise ValueError("execution authority seal mismatch")
    if value.get("freeze_file_sha256") != sha256_file(freeze_path):
        raise ValueError("execution authority freeze-file mismatch")
    if value.get("freeze_sha256") != freeze["freeze_sha256"]:
        raise ValueError("execution authority freeze-seal mismatch")
    if value.get("runtime_manifest_sha256") != runtime_manifest["manifest_sha256"]:
        raise ValueError("execution authority runtime-manifest mismatch")
    authorizations = value.get("authorizations")
    exact = {
        "exact_host_bound": True,
        "functional_smoke": True,
        "memory_workers": True,
        "performance_workers": True,
        "worker_zero": True,
    }
    if authorizations != exact:
        raise ValueError("execution authority is not the exact full-run authorization")
    host_binding = value.get("host_binding")
    if not isinstance(host_binding, dict) or value.get("host_binding_sha256") != host_binding.get("binding_sha256"):
        raise ValueError("execution authority host binding missing")
    # The controlling validator owns detailed host semantics.  Import here is
    # safe: contract_runtime is standard-library only.
    from contract_runtime import validate_host_binding

    reasons = validate_host_binding(freeze, host_binding)
    if reasons:
        raise ValueError("execution authority host inadmissible: " + ",".join(reasons))
    return value


def schedule_row(freeze: dict[str, Any], worker_id: str) -> dict[str, Any]:
    rows = freeze["performance_schedule"] + freeze["memory_schedule"]
    matches = [dict(row) for row in rows if row["worker_id"] == worker_id]
    if len(matches) != 1:
        raise ValueError(f"worker id is not unique in frozen schedule: {worker_id}")
    return matches[0]


def parser_for(arm: str | tuple[str, ...]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--runtime-manifest", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path)
    parser.add_argument("--worker-id", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--barrier-dir", type=Path)
    parser.add_argument("--plan-only", action="store_true")
    parser.set_defaults(expected_arm=arm)
    return parser


def admit(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None]:
    freeze_path = args.freeze.resolve()
    freeze = load_freeze(freeze_path)
    # The controller rehashes every runtime file once before the transaction.
    # Repeating 313 filesystem opens inside only the Python arms would pollute
    # the cold comparison with experiment-governance I/O.
    runtime = load_runtime_manifest(args.runtime_manifest.resolve(), verify_files=False)
    row = schedule_row(freeze, args.worker_id)
    expected = args.expected_arm
    if isinstance(expected, tuple):
        arm_matches = row["arm"] in expected
    else:
        arm_matches = row["arm"] == expected
    if not arm_matches:
        raise ValueError(f"worker arm mismatch: {row['arm']} != {expected}")
    if args.plan_only:
        if args.execution_authority is not None:
            raise ValueError("plan-only must not carry execution authority")
        return freeze, row, None
    if args.output is None:
        raise ValueError("execution requires --output")
    if args.execution_authority is None:
        raise ValueError("GPU execution forbidden without --execution-authority")
    authority = load_execution_authority(
        args.execution_authority.resolve(), freeze_path=freeze_path,
        freeze=freeze, runtime_manifest=runtime,
    )
    if row["mode"] == MEMORY_MODE and args.barrier_dir is None:
        raise ValueError("memory worker requires --barrier-dir")
    if row["mode"] != MEMORY_MODE and args.barrier_dir is not None:
        raise ValueError("timed worker must not carry a memory barrier")
    return freeze, row, authority


def plan_result(
    *, freeze: dict[str, Any], row: dict[str, Any], runtime_manifest: dict[str, Any], arm: str,
) -> dict[str, Any]:
    return {
        "schema": "rtdl.goal5798.worker_plan.v1",
        "status": "PLAN_ONLY__GPU_NOT_IMPORTED_OR_EXECUTED",
        "worker_id": row["worker_id"],
        "arm": arm,
        "task": row["task"],
        "mode": row["mode"],
        "freeze_sha256": freeze["freeze_sha256"],
        "runtime_manifest_sha256": runtime_manifest["manifest_sha256"],
    }


def wait_memory_barrier(barrier_dir: Path, payload: dict[str, Any], timeout_seconds: float = 300.0) -> None:
    directory = barrier_dir.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    ready = directory / "prepared.ready.json"
    continuation = directory / "controller.continue"
    create_json(ready, payload)
    deadline = time.monotonic() + timeout_seconds
    while not continuation.is_file():
        if time.monotonic() >= deadline:
            raise TimeoutError("memory controller did not release prepared barrier")
        time.sleep(0.01)
    if continuation.read_bytes() != b"CONTINUE\n":
        raise ValueError("memory continuation token mismatch")


def finish_receipt(
    *,
    freeze: dict[str, Any],
    row: dict[str, Any],
    runtime_manifest: dict[str, Any],
    authority: dict[str, Any],
    phases_ns: dict[str, int | None],
    execute_durations_ns: list[int],
    correctness: dict[str, Any],
    implementation: dict[str, Any],
) -> dict[str, Any]:
    mode = row["mode"]
    timing_eligible = mode != MEMORY_MODE
    if mode == "PREPARED_EXECUTION":
        if len(execute_durations_ns) != PREPARED_REPETITIONS:
            raise ValueError("prepared worker did not produce 64 timed executes")
        primary_sample_ns: int | None = median_ns(execute_durations_ns)
    elif mode == "COLD_FRESH_PROCESS":
        if len(execute_durations_ns) != 1:
            raise ValueError("cold worker must execute exactly once")
        # The controller owns the registered spawn-to-exit primary sample.
        primary_sample_ns = None
    elif mode == MEMORY_MODE:
        if len(execute_durations_ns) != 1:
            raise ValueError("memory worker must execute exactly once after its barrier")
        primary_sample_ns = None
    else:
        raise ValueError(f"unsupported mode: {mode}")
    phase_names = {
        "input_materialization_ns": phases_ns.get("deterministic_input_materialization"),
        "protocol_validation_and_codegen_ns": phases_ns.get("protocol_validation_and_codegen"),
        "device_compile_ns": phases_ns.get("device_compile"),
        "module_program_pipeline_sbt_ns": phases_ns.get("module_program_pipeline_sbt"),
        "gas_and_static_prepare_ns": phases_ns.get("gas_and_static_prepare"),
        "common_preparation_total_ns": phases_ns.get("common_preparation_total"),
        "complete_execute_ns": list(execute_durations_ns),
        "close_ns": phases_ns.get("close"),
        "controller_process_wall_ns": None,
    }
    raw_output_sha256 = correctness.get("raw_output_sha256")
    if not isinstance(raw_output_sha256, str) or len(raw_output_sha256) != 64:
        raise ValueError("correctness lacks raw_output_sha256")
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "PASS",
        "worker_id": row["worker_id"],
        "arm": row["arm"],
        "task": row["task"],
        "mode": mode,
        "row_sample_index": row["row_sample_index"],
        "timing_eligible": timing_eligible,
        "freeze_sha256": freeze["freeze_sha256"],
        "source_manifest_sha256": freeze["source_manifest_sha256"],
        "runtime_manifest_sha256": runtime_manifest["manifest_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "host_binding_sha256": authority["host_binding_sha256"],
        "workload_authority_sha256": freeze["workload_authority"]["authority_sha256"],
        "durations_ns": phase_names,
        "primary_sample_ns": primary_sample_ns,
        "memory": None,
        "raw_output_sha256": raw_output_sha256,
        "correctness": correctness,
        "implementation": implementation,
        "warmup_execute_count": (
            PREPARED_WARMUPS if mode in ("PREPARED_EXECUTION", MEMORY_MODE) else 0),
        "timed_execute_count": len(execute_durations_ns) if timing_eligible else 0,
        "unregistered_memory_execute_count": len(execute_durations_ns) if mode == MEMORY_MODE else 0,
        "unregistered_memory_warmup_count": PREPARED_WARMUPS if mode == MEMORY_MODE else 0,
    }
    result["receipt_sha256"] = digest(result)
    return result
