"""Validate the separate Goal5848 exact-AOT reuse qualification."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from .contracts import (
    AOT_HIT_ABSOLUTE_LIMIT_NS,
    AOT_HIT_COLD_RATIO_LIMIT_PPM,
    AOT_HIT_REPETITIONS,
    TASKS,
    aot_cache_protocol,
    digest,
    integer_median,
    ratio_ppm,
    strict_json_loads,
)

AOT_CACHE_AUTHORITY_SCHEMA = "rtdl.goal5848.aot_cache_authority.v1"
AOT_CACHE_AUTHORITY_STATUS = "PASS__AC8_EXACT_FRESH_PROCESS_AOT_REUSE"
AOT_HIT_WORKER_SCHEMA = "rtdl.goal5848.aot_fresh_process_hit.v1"
AOT_HIT_WORKER_STATUS = "PASS__EXACT_VERIFIED_HIT__NO_PRODUCER_NO_COMPILER"


def _sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _read(path: Path, label: str) -> dict[str, object]:
    if path.is_symlink():
        raise RuntimeError(f"Goal5848 AOT authority rejects symlink: {label}")
    value = strict_json_loads(
        path.resolve(strict=True).read_text(encoding="utf-8"),
        label=f"Goal5848 AOT authority {label}",
    )
    if not isinstance(value, dict):
        raise TypeError(f"Goal5848 AOT authority object required: {label}")
    return value


def _validate_seal(value: Mapping[str, object], field: str, label: str) -> None:
    unsigned = dict(value)
    seal = unsigned.pop(field, None)
    if seal != digest(unsigned):
        raise RuntimeError(f"Goal5848 AOT authority seal differs: {label}")


def _worker_id(task: str, repetition: int) -> str:
    label = "relation" if task == TASKS[0] else "triangle"
    return f"G5848_AOT_{label}_{repetition:02d}"


def _validate_worker(
    value: Mapping[str, object],
    *,
    worker_id: str,
    task: str,
    source_commit: str,
    request_identity: str,
) -> int:
    _validate_seal(value, "receipt_sha256", worker_id)
    if (
        value.get("schema") != AOT_HIT_WORKER_SCHEMA
        or value.get("status") != AOT_HIT_WORKER_STATUS
        or value.get("worker_id") != worker_id
        or value.get("task") != task
        or value.get("source_commit") != source_commit
        or value.get("request_identity_sha256") != request_identity
        or type(value.get("pid")) is not int
        or value["pid"] <= 0
        or type(value.get("duration_ns")) is not int
        or value["duration_ns"] <= 0
        or value.get("cache_hit") is not True
        or value.get("producer_invoked") is not False
        or value.get("producer_call_count") != 0
        or value.get("compiler_modules_before") != []
        or value.get("compiler_modules_after") != []
        or value.get("nvrtc_mappings_before") != []
        or value.get("nvrtc_mappings_after") != []
        or not isinstance(value.get("verification"), Mapping)
        or set(value["verification"]) != {
            "artifact_sha256",
            "authority_sha256",
            "family",
            "deployment_id",
            "executable_identity_sha256",
            "family_executable_identity_sha256",
            "target_sha256",
            "native_library_sha256",
        }
        or any(
            not isinstance(value["verification"].get(field), str)
            or len(value["verification"][field]) != 64
            for field in (
                "artifact_sha256",
                "authority_sha256",
                "executable_identity_sha256",
                "family_executable_identity_sha256",
                "target_sha256",
                "native_library_sha256",
            )
        )
        or value.get("public_or_manuscript_claim_authorized") is not False
    ):
        raise RuntimeError("Goal5848 AOT fresh-process worker differs")
    return int(value["duration_ns"])


def validate_aot_cache_authority(
    value: object,
    *,
    authority_path: Path,
    candidate_manifest: Path,
    expected_source_commit: str,
) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError("Goal5848 AOT cache authority is absent")
    _validate_seal(value, "authority_sha256", "AOT cache authority")
    protocol = aot_cache_protocol()
    tasks = value.get("tasks")
    processes = value.get("processes")
    worker_seals = value.get("worker_receipt_sha256")
    expected_worker_count = int(protocol["worker_count"])
    if (
        value.get("schema") != AOT_CACHE_AUTHORITY_SCHEMA
        or value.get("status") != AOT_CACHE_AUTHORITY_STATUS
        or value.get("source_commit") != expected_source_commit
        or value.get("worker_count") != expected_worker_count
        or value.get("process_count") != expected_worker_count
        or value.get("distinct_pid_count") != expected_worker_count
        or value.get("producer_invocation_count_across_hits") != 0
        or value.get("compiler_module_count_across_hits") != 0
        or value.get("nvrtc_mapping_count_across_hits") != 0
        or value.get("qualification_timing_count") != expected_worker_count
        or value.get("registered_performance_timing_count") != 0
        or value.get("formal_worker_count") != 0
        or value.get("included_in_formal_estimators") is not False
        or value.get("prior_in_process_hit_timings_included") is not False
        or value.get("retry_count") != 0
        or value.get("discard_count") != 0
        or value.get("external_review_complete") is not False
        or value.get("public_or_manuscript_claim_authorized") is not False
        or not isinstance(tasks, Mapping)
        or set(tasks) != set(TASKS)
        or not isinstance(processes, list)
        or len(processes) != expected_worker_count
        or not isinstance(worker_seals, list)
        or len(worker_seals) != expected_worker_count
        or len(set(worker_seals)) != expected_worker_count
    ):
        raise RuntimeError("Goal5848 AOT cache authority contract differs")

    manifest_path = candidate_manifest.resolve(strict=True)
    manifest = _read(manifest_path, "candidate manifest")
    manifest_unsigned = dict(manifest)
    manifest_seal = manifest_unsigned.pop("manifest_sha256", None)
    candidates = manifest.get("rows")
    if (
        value.get("candidate_manifest_path") != str(manifest_path)
        or value.get("candidate_manifest_sha256") != _sha256(manifest_path)
        or manifest_seal != digest(manifest_unsigned)
        or manifest.get("schema") != "rtdl.goal5848.aot_candidates.v1"
        or manifest.get("status")
        != "PASS__EXACT_AOT_CACHE_AND_CANDIDATES_VERIFIED"
        or manifest.get("source_commit") != expected_source_commit
        or not isinstance(candidates, Mapping)
        or set(candidates) != {"relation", "triangle"}
    ):
        raise RuntimeError("Goal5848 AOT cache candidate binding differs")

    process_by_worker = {}
    for process in processes:
        if not isinstance(process, Mapping) or set(process) != {
            "worker_id",
            "command",
            "exit_code",
            "stdout_sha256",
            "stderr_sha256",
        }:
            raise RuntimeError("Goal5848 AOT cache process row differs")
        worker_id = process.get("worker_id")
        if not isinstance(worker_id, str) or worker_id in process_by_worker:
            raise RuntimeError("Goal5848 AOT cache process identity differs")
        if (
            process.get("exit_code") != 0
            or process.get("stderr_sha256") != hashlib.sha256(b"").hexdigest()
            or not isinstance(process.get("command"), list)
        ):
            raise RuntimeError("Goal5848 AOT cache process execution differs")
        process_by_worker[worker_id] = process

    authority_root = authority_path.resolve(strict=True).parent
    expected_files = {"authority.json"}
    observed_pids = set()
    observed_seals = []
    for task in TASKS:
        label = "relation" if task == TASKS[0] else "triangle"
        candidate = candidates[label]
        task_result = tasks[task]
        if not isinstance(candidate, Mapping) or not isinstance(
            task_result, Mapping
        ):
            raise TypeError("Goal5848 AOT cache task row differs")
        request_identity = candidate.get("aot_request_identity_sha256")
        cold_ns = candidate.get("first_resolution_ns")
        if (
            not isinstance(request_identity, str)
            or len(request_identity) != 64
            or candidate.get("first_resolution_cache_hit") is not False
            or candidate.get("producer_invocation_count") != 1
            or type(cold_ns) is not int
            or cold_ns <= 0
        ):
            raise RuntimeError("Goal5848 AOT cold-build evidence differs")
        durations = []
        for repetition in range(AOT_HIT_REPETITIONS):
            worker_id = _worker_id(task, repetition)
            expected_files.add(f"{worker_id}.json")
            worker = _read(authority_root / f"{worker_id}.json", worker_id)
            duration = _validate_worker(
                worker,
                worker_id=worker_id,
                task=task,
                source_commit=expected_source_commit,
                request_identity=request_identity,
            )
            process = process_by_worker.get(worker_id)
            stdout = json.dumps(worker, sort_keys=True) + "\n"
            if (
                process is None
                or process.get("stdout_sha256")
                != hashlib.sha256(stdout.encode("utf-8")).hexdigest()
            ):
                raise RuntimeError("Goal5848 AOT worker/process binding differs")
            durations.append(duration)
            observed_pids.add(worker["pid"])
            observed_seals.append(worker["receipt_sha256"])
        median_ns = integer_median(durations)
        relative_ppm = ratio_ppm(median_ns, int(cold_ns))
        if (
            task_result.get("cold_first_resolution_ns") != cold_ns
            or task_result.get("fresh_process_hit_durations_ns") != durations
            or task_result.get("fresh_process_hit_median_ns") != median_ns
            or task_result.get("fresh_process_hit_over_cold_ppm")
            != relative_ppm
            or task_result.get("absolute_limit_ns")
            != AOT_HIT_ABSOLUTE_LIMIT_NS
            or task_result.get("relative_limit_ppm")
            != AOT_HIT_COLD_RATIO_LIMIT_PPM
            or task_result.get("pass") is not True
            or median_ns > AOT_HIT_ABSOLUTE_LIMIT_NS
            or relative_ppm > AOT_HIT_COLD_RATIO_LIMIT_PPM
        ):
            raise RuntimeError("Goal5848 AOT cache task gate differs")
    if (
        {path.name for path in authority_root.iterdir()} != expected_files
        or len(observed_pids) != expected_worker_count
        or observed_seals != worker_seals
    ):
        raise RuntimeError("Goal5848 AOT cache retained evidence set differs")
    return dict(value)


def load_aot_cache_authority(
    path: Path,
    *,
    candidate_manifest: Path,
    expected_source_commit: str,
) -> dict[str, object]:
    value = _read(path, "AOT cache authority")
    return validate_aot_cache_authority(
        value,
        authority_path=path,
        candidate_manifest=candidate_manifest,
        expected_source_commit=expected_source_commit,
    )


__all__ = [
    "AOT_CACHE_AUTHORITY_SCHEMA",
    "AOT_CACHE_AUTHORITY_STATUS",
    "load_aot_cache_authority",
    "validate_aot_cache_authority",
]
