#!/usr/bin/env python3
"""Independently recount one complete Goal5848 generation transaction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path

from experiments.goal5848_strong_baseline.aot_cache_authority import (
    load_aot_cache_authority,
)
from experiments.goal5848_strong_baseline.contracts import (
    ARMS,
    BLOCKS,
    DIRECT_OPTIX_ARM,
    IDIOMATIC_PYOPTIX_ARM,
    INSTRUMENTATION_AUTHORITY_SCHEMA,
    INSTRUMENTATION_AUTHORITY_STATUS,
    INSTRUMENTATION_OVERHEAD_LIMIT_PPM,
    PARTITION_ABSOLUTE_TOLERANCE_NS,
    PARTITION_RELATIVE_TOLERANCE_PPM,
    POST_IMPORT_BLOCK_RATIO_LIMIT_PPM,
    POST_IMPORT_RATIO_LIMIT_PPM,
    PREDECESSOR_RTDL_ARM,
    PREFLIGHT_PASS_STATUS,
    PREFLIGHT_SCHEMA,
    PREREGISTRATION_ARTIFACT_ARGUMENTS,
    PREREGISTRATION_SCHEMA,
    PRIMARY_ARMS,
    PUBLIC_DIRECT_RATIO_LIMIT_PPM,
    RTDL_ARM,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    STRONG_COMPETENCE_RATIO_LIMIT_PPM,
    STRONG_PYOPTIX_ARM,
    SUCCESSOR_PREDECESSOR_RATIO_LIMIT_PPM,
    TASK_CONTRACTS,
    TASKS,
    aot_cache_protocol,
    build_schedule,
    digest,
    evaluate_complete_transaction,
    instrumentation_protocol,
    integer_median,
    ratio_ppm,
    strict_json_loads,
)

ROOT = Path(__file__).resolve().parents[1]
_FORMAL_SANITIZED_ENVIRONMENT = (
    "CFLAGS",
    "CPPFLAGS",
    "CXXFLAGS",
    "LDFLAGS",
    "LIBRARY_PATH",
    "CPATH",
    "CPLUS_INCLUDE_PATH",
    "CUDAFLAGS",
    "NVCC_PREPEND_FLAGS",
    "NVCC_APPEND_FLAGS",
    "CUDA_LAUNCH_BLOCKING",
    "CUDA_DEVICE_MAX_CONNECTIONS",
    "CUDA_CACHE_MAXSIZE",
    "CUDA_CACHE_PATH",
    "CUDA_MODULE_LOADING",
    "CUDA_FORCE_PTX_JIT",
    "CUDA_DISABLE_PTX_JIT",
    "CUDA_INJECTION64_PATH",
    "CUDA_INJECTION32_PATH",
    "CUDA_DEVICE_ORDER",
    "CUDA_AUTO_BOOST",
    "CUPY_ACCELERATORS",
    "CUPY_CACHE_DIR",
    "CUPY_CACHE_IN_MEMORY",
    "NUMBA_CACHE_DIR",
    "NUMBA_ENABLE_CUDASIM",
    "NUMBA_FORCE_CUDA_CC",
    "NUMBA_CUDA_DEFAULT_PTX_CC",
    "XDG_CACHE_HOME",
    "CMAKE_GENERATOR",
    "CMAKE_TOOLCHAIN_FILE",
    "RTDL_GOAL5807_PROFILE_NATIVE",
    "LD_PRELOAD",
    "PYTHONHOME",
    "PYTHONINSPECT",
    "PYTHONSTARTUP",
    "PYTHONHASHSEED",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "BLIS_NUM_THREADS",
)

_INSTRUMENTATION_NATIVE_PHASE = re.compile(
    r"RTDL_GOAL5807_NATIVE_PHASE\|([^|\n]+)\|([^|\n]+)\|([0-9]+)"
)


def _new_output_path(path: Path) -> Path:
    """Create-free canonical output validation without controller imports."""

    absolute = path.expanduser().absolute()
    if absolute.exists() or absolute.is_symlink():
        raise FileExistsError(absolute)
    parent = absolute.parent.resolve(strict=True)
    candidate = parent / absolute.name
    if os.path.commonpath((str(ROOT), str(candidate))) == str(ROOT):
        raise RuntimeError("Goal5848 authority output must be outside source Git")
    return candidate


def _read(path: Path, label: str) -> dict[str, object]:
    if path.is_symlink():
        raise RuntimeError(f"Goal5848 authority rejects symlink: {label}")
    resolved = path.resolve(strict=True)
    if not stat.S_ISREG(resolved.stat().st_mode):
        raise RuntimeError(f"Goal5848 authority requires file: {label}")
    value = strict_json_loads(
        resolved.read_text(encoding="utf-8"),
        label=f"Goal5848 authority {label}",
    )
    if not isinstance(value, dict):
        raise TypeError(f"Goal5848 authority object required: {label}")
    return value


def _sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _validate_seal(
    value: Mapping[str, object],
    field: str,
    label: str,
) -> None:
    unsigned = dict(value)
    seal = unsigned.pop(field, None)
    if seal != digest(unsigned):
        raise RuntimeError(f"Goal5848 authority seal differs: {label}")


def _file_identity(path: Path) -> dict[str, object]:
    if path.is_symlink():
        raise RuntimeError("Goal5848 authority rejects symbolic artifact")
    resolved = path.resolve(strict=True)
    metadata = resolved.stat()
    if not stat.S_ISREG(metadata.st_mode):
        raise RuntimeError("Goal5848 authority artifact is not a file")
    return {
        "path": str(resolved),
        "bytes": metadata.st_size,
        "sha256": _sha256(resolved),
    }


def _git_identity(root: Path) -> dict[str, str]:
    result = {}
    for name, arguments in (
        ("commit", ("rev-parse", "HEAD")),
        ("tree", ("rev-parse", "HEAD^{tree}")),
        ("status", ("status", "--porcelain=v1", "--untracked-files=all")),
    ):
        result[name] = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    return result


def _validate_preregistration(
    value: dict[str, object],
    *,
    source_commit: str,
    predecessor_commit: str,
) -> dict[str, object]:
    _validate_seal(value, "preregistration_sha256", "preregistration")
    artifacts = value.get("artifacts")
    for label, commit_field, tree_field in (
        ("source", "source_commit", "source_tree"),
        ("predecessor", "predecessor_commit", "predecessor_tree"),
        ("pyoptix", "pyoptix_commit", "pyoptix_tree"),
    ):
        identity = value.get(f"{label}_identity")
        if (
            not isinstance(identity, Mapping)
            or set(identity) != {"path", "commit", "tree", "status", "clean"}
            or not isinstance(identity.get("path"), str)
            or not Path(str(identity["path"])).is_absolute()
            or identity.get("commit") != value.get(commit_field)
            or identity.get("tree") != value.get(tree_field)
            or identity.get("status") != ""
            or identity.get("clean") is not True
        ):
            raise RuntimeError(
                f"Goal5848 authority preregistration {label} identity differs"
            )
    expected_keys = {
        "schema", "status", "source_commit", "source_tree",
        "predecessor_commit", "predecessor_tree", "pyoptix_commit",
        "pyoptix_tree", "source_identity", "predecessor_identity",
        "pyoptix_identity", "python", "python_version",
        "expected_optix_sdk", "optix_disk_cache_policy", "artifacts",
        "tasks", "task_contracts", "primary_arms", "all_arms", "blocks",
        "steady_warmups", "steady_repetitions", "schedule",
        "schedule_sha256", "thresholds_ppm", "partition_reconciliation",
        "instrumentation_protocol", "aot_cache_protocol", "endpoint",
        "estimator", "failure_policy", "registered_performance_timing_count",
        "formal_worker_count", "claim_boundary", "retry_count",
        "discard_count", "preregistration_sha256",
    }
    expected_failure_policy = {
        "formal_worker_retry": False,
        "formal_worker_discard": False,
        "prior_rows_authorized_for_pooling": False,
        "repair_requires_new_preregistration": True,
    }
    expected_claim_boundary = {
        "single_generation_only": True,
        "external_review_complete": False,
        "public_or_manuscript_claim_authorized": False,
    }
    if (
        set(value) != expected_keys
        or value.get("schema") != PREREGISTRATION_SCHEMA
        or value.get("status") != "FROZEN__BEFORE_FORMAL_WORKER_ZERO"
        or value.get("source_commit") != source_commit
        or value.get("predecessor_commit") != predecessor_commit
        or not isinstance(value.get("source_tree"), str)
        or len(str(value.get("source_tree"))) != 40
        or not isinstance(value.get("predecessor_tree"), str)
        or len(str(value.get("predecessor_tree"))) != 40
        or not isinstance(value.get("pyoptix_commit"), str)
        or len(str(value.get("pyoptix_commit"))) != 40
        or not isinstance(value.get("pyoptix_tree"), str)
        or len(str(value.get("pyoptix_tree"))) != 40
        or value.get("schedule") != list(build_schedule())
        or value.get("schedule_sha256") != digest(list(build_schedule()))
        or value.get("tasks") != list(TASKS)
        or value.get("task_contracts") != TASK_CONTRACTS
        or value.get("primary_arms") != list(PRIMARY_ARMS)
        or value.get("all_arms") != list(ARMS)
        or value.get("blocks") != BLOCKS
        or value.get("steady_warmups") != STEADY_WARMUPS
        or value.get("steady_repetitions") != STEADY_REPETITIONS
        or value.get("thresholds_ppm") != {
            "post_import_median": POST_IMPORT_RATIO_LIMIT_PPM,
            "post_import_worst_block": POST_IMPORT_BLOCK_RATIO_LIMIT_PPM,
            "public_direct_median": PUBLIC_DIRECT_RATIO_LIMIT_PPM,
            "successor_predecessor_median": (
                SUCCESSOR_PREDECESSOR_RATIO_LIMIT_PPM
            ),
            "strong_competence_median": STRONG_COMPETENCE_RATIO_LIMIT_PPM,
            "instrumentation_overhead": INSTRUMENTATION_OVERHEAD_LIMIT_PPM,
        }
        or value.get("partition_reconciliation") != {
            "absolute_tolerance_ns": PARTITION_ABSOLUTE_TOLERANCE_NS,
            "relative_tolerance_ppm": PARTITION_RELATIVE_TOLERANCE_PPM,
        }
        or value.get("instrumentation_protocol") != instrumentation_protocol()
        or value.get("aot_cache_protocol") != aot_cache_protocol()
        or value.get("endpoint")
        != "implementation_import_end_to_first_exact_public_result"
        or value.get("estimator")
        != "median_of_eight_within_block_integer_ratios"
        or value.get("failure_policy") != expected_failure_policy
        or value.get("claim_boundary") != expected_claim_boundary
        or value.get("optix_disk_cache_policy")
        != "disabled_for_all_primary_arms"
        or not isinstance(value.get("python_version"), str)
        or not value["python_version"]
        or not isinstance(value.get("expected_optix_sdk"), str)
        or not value["expected_optix_sdk"]
        or value.get("registered_performance_timing_count") != 0
        or value.get("formal_worker_count") != 0
        or value.get("retry_count") != 0
        or value.get("discard_count") != 0
        or not isinstance(artifacts, Mapping)
        or set(artifacts) != set(PREREGISTRATION_ARTIFACT_ARGUMENTS)
    ):
        raise RuntimeError("Goal5848 authority preregistration differs")
    rehashed = {}
    for label, row in artifacts.items():
        if not isinstance(row, Mapping) or set(row) != {
            "path", "bytes", "sha256"
        }:
            raise RuntimeError("Goal5848 authority artifact row differs")
        observed = _file_identity(Path(str(row["path"])))
        if observed != row:
            raise RuntimeError(f"Goal5848 authority artifact differs: {label}")
        rehashed[str(label)] = observed
    python_row = value.get("python")
    if (
        not isinstance(python_row, Mapping)
        or set(python_row) != {"path", "bytes", "sha256"}
        or _file_identity(Path(str(python_row["path"]))) != python_row
    ):
        raise RuntimeError("Goal5848 authority Python identity differs")
    return rehashed


def _validate_linked_authority(
    preflight: Mapping[str, object], prefix: str
) -> dict[str, object]:
    path = Path(str(preflight[f"{prefix}_path"]))
    value = _read(path, prefix)
    _validate_seal(value, "authority_sha256", prefix)
    expected_schema, expected_status = {
        "timer_free_witness": (
            "rtdl.goal5848.timer_free_witness_authority.v1",
            "PASS__ALL_EIGHT_PRIMARY_ARM_TASK_WITNESSES",
        ),
        "baseline_competence": (
            "rtdl.goal5848.baseline_competence.v1",
            "PASS__STRONG_PYOPTIX_COMPETENT_FOR_BOTH_TASKS",
        ),
        "instrumentation_overhead": (
            INSTRUMENTATION_AUTHORITY_SCHEMA,
            INSTRUMENTATION_AUTHORITY_STATUS,
        ),
    }[prefix]
    if (
        _sha256(path.resolve(strict=True))
        != preflight[f"{prefix}_file_sha256"]
        or value.get("authority_sha256") != preflight[f"{prefix}_sha256"]
        or value.get("schema") != expected_schema
        or value.get("status") != expected_status
        or (
            prefix == "instrumentation_overhead"
            and (
                value.get("worker_count")
                != instrumentation_protocol()["worker_count"]
                or value.get("process_count")
                != instrumentation_protocol()["worker_count"]
                or value.get("schedule")
                != instrumentation_protocol()["schedule"]
                or value.get("registered_performance_timing_count") != 0
                or value.get("formal_worker_count") != 0
                or value.get("included_in_formal_estimators") is not False
                or value.get("retry_count") != 0
                or value.get("discard_count") != 0
            )
        )
    ):
        raise RuntimeError(f"Goal5848 linked authority differs: {prefix}")
    return value


def _parse_instrumentation_phases(
    stderr: bytes, *, mode: str,
) -> list[dict[str, object]]:
    if mode == "off":
        if stderr:
            raise RuntimeError("Goal5848 plain instrumentation stderr differs")
        return []
    try:
        lines = stderr.decode("ascii").splitlines()
    except UnicodeDecodeError as error:
        raise RuntimeError("Goal5848 instrumentation stderr is not ASCII") from error
    rows = []
    for line in lines:
        match = _INSTRUMENTATION_NATIVE_PHASE.fullmatch(line)
        if match is None:
            raise RuntimeError("Goal5848 instrumentation stderr differs")
        family, phase, duration = match.groups()
        rows.append({
            "family": family,
            "phase": phase,
            "duration_ns": int(duration),
        })
    if not rows:
        raise RuntimeError("Goal5848 instrumented phase evidence is absent")
    return rows


def _validate_instrumentation_evidence(
    value: Mapping[str, object],
    *,
    authority_path: Path,
    preregistration: Mapping[str, object],
) -> None:
    """Independently bind and recount all v2 instrumentation evidence."""

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
    worker_rows = value.get("worker_receipts")
    process_rows = value.get("process_receipts")
    tasks = value.get("tasks")
    if (
        set(value) != expected_authority_keys
        or value.get("source_commit") != preregistration.get("source_commit")
        or value.get("predecessor_commit")
        != preregistration.get("predecessor_commit")
        or value.get("preregistration_sha256")
        != preregistration.get("preregistration_sha256")
        or not isinstance(value.get("hardware"), Mapping)
        or value.get("schedule") != schedule
        or value.get("worker_count") != len(schedule)
        or value.get("process_count") != len(schedule)
        or value.get("registered_performance_timing_count") != 0
        or value.get("formal_worker_count") != 0
        or value.get("included_in_formal_estimators") is not False
        or value.get("retry_count") != 0
        or value.get("discard_count") != 0
        or value.get("public_or_manuscript_claim_authorized") is not False
        or not isinstance(schedule, list)
        or not isinstance(worker_rows, list)
        or not isinstance(process_rows, list)
        or len(worker_rows) != len(schedule)
        or len(process_rows) != len(schedule)
        or not isinstance(tasks, Mapping)
        or set(tasks) != set(TASKS)
    ):
        raise RuntimeError("Goal5848 instrumentation authority rows differ")
    root = authority_path.resolve(strict=True).parent
    workers_root = root / "workers"
    processes_root = root / "processes"
    if (
        authority_path.name != "authority.json"
        or workers_root.is_symlink()
        or processes_root.is_symlink()
        or not workers_root.is_dir()
        or not processes_root.is_dir()
        or {path.name for path in root.iterdir()}
        != {"authority.json", "workers", "processes"}
    ):
        raise RuntimeError("Goal5848 instrumentation root differs")
    expected_worker_names = {
        f"{row['worker_id']}.json" for row in schedule
    }
    expected_process_names = {
        f"{row['worker_id']}.{suffix}"
        for row in schedule
        for suffix in ("json", "stdout", "stderr")
    }
    if (
        {path.name for path in workers_root.iterdir()} != expected_worker_names
        or {path.name for path in processes_root.iterdir()}
        != expected_process_names
    ):
        raise RuntimeError("Goal5848 instrumentation file set differs")

    python_row = preregistration.get("python")
    artifacts = preregistration.get("artifacts")
    if not isinstance(python_row, Mapping) or not isinstance(artifacts, Mapping):
        raise TypeError("Goal5848 instrumentation command inputs differ")
    candidate_manifest = _artifact_path(artifacts, "candidate_manifest")
    expected_source_commit = str(preregistration["source_commit"])
    indexed: dict[tuple[str, int, str], int] = {}
    phases_by_worker: dict[str, list[dict[str, object]]] = {}
    empty_sha256 = hashlib.sha256(b"").hexdigest()

    for scheduled, compact_worker, compact_process in zip(
        schedule, worker_rows, process_rows
    ):
        if not all(
            isinstance(row, Mapping)
            for row in (scheduled, compact_worker, compact_process)
        ):
            raise RuntimeError("Goal5848 instrumentation row type differs")
        worker_id = str(scheduled["worker_id"])
        task = str(scheduled["task"])
        block = int(scheduled["block"])
        mode = str(scheduled["mode"])
        worker_path = workers_root / f"{worker_id}.json"
        process_path = processes_root / f"{worker_id}.json"
        stdout_path = processes_root / f"{worker_id}.stdout"
        stderr_path = processes_root / f"{worker_id}.stderr"
        worker = _read(worker_path, f"instrumentation worker {worker_id}")
        process = _read(process_path, f"instrumentation process {worker_id}")
        _validate_seal(worker, "result_sha256", worker_id)
        _validate_seal(process, "process_sha256", worker_id)
        measurements = worker.get("measurements")
        evidence = (
            measurements.get("evidence")
            if isinstance(measurements, Mapping)
            else None
        )
        partition = (
            measurements.get("endpoint_partition_ns")
            if isinstance(measurements, Mapping)
            else None
        )
        components = (
            measurements.get("component_diagnostics_ns")
            if isinstance(measurements, Mapping)
            else None
        )
        source = worker.get("source")
        endpoint = (
            measurements.get("post_import_to_first_correct_result_ns")
            if isinstance(measurements, Mapping)
            else None
        )
        expected_worker = {
            "worker_id": worker_id,
            "task": task,
            "block": block,
            "mode": mode,
            "endpoint_ns": endpoint,
            "worker_receipt_sha256": worker.get("result_sha256"),
            "worker_file_sha256": _sha256(worker_path),
        }
        if (
            dict(compact_worker) != expected_worker
            or set(worker) != {
                "schema", "status", "arm", "task", "block", "worker_id",
                "classification", "warmups", "repetitions", "python",
                "source", "hardware", "measurements", "claim_boundary",
                "result_sha256",
            }
            or worker.get("schema")
            != "rtdl.goal5848.strong_baseline.worker.v1"
            or worker.get("status") != "PASS__GOAL5848_WORKER"
            or worker.get("arm") != RTDL_ARM
            or worker.get("task") != task
            or worker.get("block") != block
            or worker.get("worker_id") != worker_id
            or worker.get("classification") != "exploration"
            or worker.get("warmups") != 1
            or worker.get("repetitions") != 1
            or not isinstance(source, Mapping)
            or source.get("commit") != expected_source_commit
            or source.get("tree") != preregistration.get("source_tree")
            or source.get("clean") is not True
            or source.get("status") != ""
            or worker.get("hardware") != value.get("hardware")
            or type(endpoint) is not int
            or endpoint <= 0
            or not isinstance(evidence, Mapping)
            or evidence.get("phase_instrumentation") != (mode == "on")
            or evidence.get("output_sha256")
            != TASK_CONTRACTS[task]["public_output_sha256"]
            or not isinstance(partition, Mapping)
            or not isinstance(components, Mapping)
        ):
            raise RuntimeError(
                f"Goal5848 instrumentation worker differs: {worker_id}"
            )
        if mode == "off" and (
            any(
                duration != 0
                for name, duration in partition.items()
                if name != "unattributed_control_plane"
            )
            or partition.get("unattributed_control_plane") != endpoint
            or any(duration is not None for duration in components.values())
            or evidence.get("provider_initialization_phases_ns") != {}
        ):
            raise RuntimeError(
                f"Goal5848 plain instrumentation worker differs: {worker_id}"
            )
        if mode == "on" and not evidence.get(
            "provider_initialization_phases_ns"
        ):
            raise RuntimeError(
                f"Goal5848 instrumented worker phases differ: {worker_id}"
            )
        expected_command = [
            str(python_row["path"]),
            "-m",
            "experiments.goal5848_strong_baseline.worker",
            "--arm",
            RTDL_ARM,
            "--task",
            task,
            "--block",
            str(block),
            "--worker-id",
            worker_id,
            "--classification",
            "exploration",
            "--expected-source-commit",
            expected_source_commit,
            "--candidate-manifest",
            candidate_manifest,
            "--phase-instrumentation",
            mode,
            "--warmups",
            "1",
            "--repetitions",
            "1",
            "--output",
            str(worker_path),
        ]
        if stdout_path.is_symlink() or stderr_path.is_symlink():
            raise RuntimeError("Goal5848 instrumentation stream is a symlink")
        stdout = stdout_path.read_bytes()
        stderr = stderr_path.read_bytes()
        native_phases = _parse_instrumentation_phases(stderr, mode=mode)
        expected_process = {
            "worker_id": worker_id,
            "exit_code": 0,
            "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
            "native_phase_rows": native_phases,
            "process_sha256": process.get("process_sha256"),
            "process_file_sha256": _sha256(process_path),
        }
        if (
            dict(compact_process) != expected_process
            or set(process) != {
                "worker_id", "command", "exit_code", "stdout_sha256",
                "stderr_sha256", "native_phase_rows", "process_sha256",
            }
            or process.get("worker_id") != worker_id
            or process.get("command") != expected_command
            or process.get("exit_code") != 0
            or process.get("stdout_sha256")
            != hashlib.sha256(stdout).hexdigest()
            or process.get("stderr_sha256")
            != hashlib.sha256(stderr).hexdigest()
            or process.get("native_phase_rows") != native_phases
            or stdout != (json.dumps(worker, sort_keys=True) + "\n").encode()
            or (mode == "off" and process.get("stderr_sha256") != empty_sha256)
        ):
            raise RuntimeError(
                f"Goal5848 instrumentation process differs: {worker_id}"
            )
        indexed[(task, block, mode)] = int(endpoint)
        phases_by_worker[worker_id] = native_phases

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
        values: dict[str, list[int]] = defaultdict(list)
        ratios = []
        blocks = []
        for block in range(int(protocol["blocks"])):
            off_ns = indexed[(task, block, "off")]
            on_ns = indexed[(task, block, "on")]
            paired_ratio = ratio_ppm(on_ns, off_ns)
            values["off"].append(off_ns)
            values["on"].append(on_ns)
            ratios.append(paired_ratio)
            blocks.append({
                "block": block,
                "off_ns": off_ns,
                "on_ns": on_ns,
                "signed_difference_ns": on_ns - off_ns,
                "on_over_off_ppm": paired_ratio,
            })
        off_median = integer_median(values["off"])
        on_median = integer_median(values["on"])
        ratio_median = integer_median(ratios)
        overhead_ppm = max(0, ratio_median - 1_000_000)
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
            "measured_instrumentation_overhead_ns": (
                off_median * overhead_ppm + 500_000
            ) // 1_000_000,
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
            raise RuntimeError("Goal5848 instrumentation recount differs")


def _validate_process(
    value: dict[str, object],
    *,
    worker: dict[str, object],
    worker_id: str,
    expected_command: list[str],
    expected_execution_context: dict[str, object],
) -> None:
    _validate_seal(value, "process_sha256", f"process {worker_id}")
    expected_stdout = json.dumps(worker, sort_keys=True) + "\n"
    if (
        set(value) != {
            "schema", "worker_id", "command", "execution_context",
            "exit_code", "wall_ns", "stdout_utf8", "stdout_sha256",
            "stderr_utf8", "stderr_sha256", "process_sha256",
        }
        or value.get("schema") != "rtdl.goal5848.formal_process.v1"
        or value.get("worker_id") != worker_id
        or value.get("exit_code") != 0
        or type(value.get("wall_ns")) is not int
        or value["wall_ns"] <= 0
        or value.get("stdout_utf8") != expected_stdout
        or value.get("stdout_sha256")
        != hashlib.sha256(expected_stdout.encode("utf-8")).hexdigest()
        or value.get("stderr_utf8") != ""
        or value.get("stderr_sha256") != hashlib.sha256(b"").hexdigest()
        or value.get("command") != expected_command
        or value.get("execution_context") != expected_execution_context
    ):
        raise RuntimeError(f"Goal5848 authority process differs: {worker_id}")


def _artifact_path(
    artifacts: Mapping[str, object], label: str,
) -> str:
    row = artifacts.get(label)
    if not isinstance(row, Mapping) or not isinstance(row.get("path"), str):
        raise TypeError(f"Goal5848 command artifact is absent: {label}")
    return str(row["path"])


def _expected_process_command(
    row: Mapping[str, object],
    *,
    preregistration: Mapping[str, object],
    artifacts: Mapping[str, object],
    preregistration_path: Path,
    transaction_root: Path,
) -> list[str]:
    """Independently derive the exact command for one frozen schedule row."""

    python = preregistration.get("python")
    source = preregistration.get("source_identity")
    predecessor = preregistration.get("predecessor_identity")
    pyoptix = preregistration.get("pyoptix_identity")
    if not all(
        isinstance(value, Mapping)
        for value in (python, source, predecessor, pyoptix)
    ):
        raise RuntimeError("Goal5848 command repository identity is absent")
    worker_id = str(row["worker_id"])
    output = transaction_root / "workers" / f"{worker_id}.json"
    common = [
        str(python["path"]),
        "-m",
        "experiments.goal5848_strong_baseline.worker",
        "--arm",
        str(row["arm"]),
        "--task",
        str(row["task"]),
        "--block",
        str(row["block"]),
        "--worker-id",
        worker_id,
        "--classification",
        "formal",
        "--phase-instrumentation",
        "on",
        "--expected-source-commit",
        str(preregistration["source_commit"]),
        "--warmups",
        str(STEADY_WARMUPS),
        "--repetitions",
        str(STEADY_REPETITIONS),
        "--output",
        str(output),
    ]
    arm = row["arm"]
    if arm == RTDL_ARM:
        return [
            *common,
            "--candidate-manifest",
            _artifact_path(artifacts, "candidate_manifest"),
        ]
    if arm in {IDIOMATIC_PYOPTIX_ARM, STRONG_PYOPTIX_ARM}:
        command = [
            *common,
            "--precompiled-ptx",
            _artifact_path(artifacts, "precompiled_ptx"),
            "--pyoptix-source",
            str(pyoptix["path"]),
            "--pyoptix-build-receipt",
            _artifact_path(artifacts, "pyoptix_build_receipt"),
            "--expected-optix-sdk",
            str(preregistration["expected_optix_sdk"]),
        ]
        if arm == STRONG_PYOPTIX_ARM and row["task"] == TASKS[0]:
            command.extend([
                "--compaction-cubin",
                _artifact_path(artifacts, "compaction_cubin"),
            ])
        return command

    module = (
        "experiments.goal5848_strong_baseline.direct_bridge"
        if arm == DIRECT_OPTIX_ARM
        else "experiments.goal5848_strong_baseline.predecessor_worker"
    )
    command = [
        str(python["path"]),
        "-m",
        module,
        "--task",
        str(row["task"]),
        "--block",
        str(row["block"]),
        "--worker-id",
        worker_id,
        "--classification",
        "formal",
        "--output",
        str(output),
    ]
    if arm == PREDECESSOR_RTDL_ARM:
        return [
            *command,
            "--predecessor-root",
            str(predecessor["path"]),
            "--expected-predecessor-commit",
            str(preregistration["predecessor_commit"]),
            "--candidate-manifest",
            _artifact_path(artifacts, "predecessor_candidate_manifest"),
            "--warmups",
            str(STEADY_WARMUPS),
            "--repetitions",
            str(STEADY_REPETITIONS),
        ]
    if arm != DIRECT_OPTIX_ARM:
        raise RuntimeError("Goal5848 command arm differs")
    command.extend([
        "--expected-source-commit",
        str(preregistration["source_commit"]),
        "--direct-worker",
        _artifact_path(artifacts, "direct_worker"),
        "--direct-build-receipt",
        _artifact_path(artifacts, "direct_build_receipt"),
        "--derivation-receipt",
        _artifact_path(artifacts, "derivation_receipt"),
        "--preregistration",
        str(preregistration_path),
        "--precompiled-ptx",
        _artifact_path(artifacts, "precompiled_ptx"),
        "--support-root",
        str(transaction_root / "direct_support"),
    ])
    if row["task"] == TASKS[0]:
        command.extend([
            "--compaction-cubin",
            _artifact_path(artifacts, "compaction_cubin"),
        ])
    return command


def _expected_execution_context(
    preregistration: Mapping[str, object],
) -> dict[str, object]:
    source = preregistration.get("source_identity")
    if not isinstance(source, Mapping) or not isinstance(source.get("path"), str):
        raise TypeError("Goal5848 execution-context source is absent")
    root = Path(str(source["path"]))
    return {
        "cwd": str(root),
        "environment": {
            "PYTHONPATH": f"{root / 'src'}:{root}",
            "CUDA_VISIBLE_DEVICES": "0",
            "CUDA_CACHE_DISABLE": "1",
            "RTDL_OPTIX_DISK_CACHE_POLICY": "disabled",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            **{name: None for name in _FORMAL_SANITIZED_ENVIRONMENT},
        },
    }


def _validate_direct_support(
    transaction_root: Path,
    receipts: list[dict[str, object]],
) -> list[dict[str, object]]:
    direct = [row for row in receipts if row["arm"] == DIRECT_OPTIX_ARM]
    support_root = transaction_root / "direct_support"
    expected_names = {f"{row['worker_id']}.preflight.json" for row in direct}
    if support_root.is_symlink() or {
        path.name for path in support_root.resolve(strict=True).iterdir()
    } != expected_names:
        raise RuntimeError("Goal5848 Direct support file set differs")
    result = []
    for receipt in direct:
        worker_id = str(receipt["worker_id"])
        path = support_root / f"{worker_id}.preflight.json"
        value = _read(path, f"Direct support {worker_id}")
        _validate_seal(value, "preflight_sha256", f"Direct support {worker_id}")
        measurements = receipt["measurements"]
        if not isinstance(measurements, Mapping):
            raise TypeError("Goal5848 Direct measurements are absent")
        evidence = measurements["evidence"]
        if not isinstance(evidence, Mapping):
            raise TypeError("Goal5848 Direct evidence is absent")
        if (
            value.get("schema")
            != "rtdl.goal5802.formal_runtime_preflight.v1"
            or value.get("registered_performance_timing_count") != 0
            or value.get("formal_worker_count") != 0
            or _sha256(path.resolve(strict=True))
            != evidence.get("compatibility_preflight_file_sha256")
            or value.get("preflight_sha256")
            != evidence.get("compatibility_preflight_sha256")
        ):
            raise RuntimeError(
                f"Goal5848 Direct support authority differs: {worker_id}"
            )
        result.append(_file_identity(path))
    return result


def _validate_device_artifacts_independently(
    artifacts: Mapping[str, object],
    *,
    expected_source_commit: str,
    expected_compute_capability: str,
) -> dict[str, object]:
    """Recount the device build without the controller's validator."""

    required = {
        "device_artifact_build_receipt",
        "precompiled_ptx",
        "compaction_cubin",
    }
    if not required.issubset(artifacts):
        raise RuntimeError("Goal5848 device artifact set differs")
    receipt_path = Path(str(
        artifacts["device_artifact_build_receipt"]["path"]
    ))
    receipt = _read(receipt_path, "device artifact build receipt")
    _validate_seal(receipt, "receipt_sha256", "device artifact build receipt")
    outputs = receipt.get("outputs")
    source_identity = receipt.get("source_identity")
    processes = receipt.get("compiler_processes")
    children = receipt.get("compiler_receipts")
    if (
        receipt.get("schema") != "rtdl.goal5848.device_artifact_build.v1"
        or receipt.get("status")
        != "PASS__TWO_FRESH_PROCESS_UNTIMED_NVRTC_PRODUCTS"
        or not isinstance(source_identity, Mapping)
        or source_identity.get("commit") != expected_source_commit
        or source_identity.get("clean") is not True
        or receipt.get("compute_capability") != expected_compute_capability
        or receipt.get("derivation_scope")
        != "SOURCE_AND_PRODUCT_BOUND__NOT_A_HERMETIC_CUDA_HEADER_CLOSURE"
        or receipt.get("public_or_manuscript_claim_authorized") is not False
        or any(
            type(receipt.get(field)) is not int or receipt[field] != 0
            for field in (
                "clock_read_count",
                "registered_performance_timing_count",
                "gpu_kernel_launch_count",
                "formal_worker_count",
                "retry_count",
                "discard_count",
            )
        )
        or not isinstance(outputs, Mapping)
        or set(outputs) != {"precompiled_ptx", "compaction_cubin"}
        or outputs["precompiled_ptx"] != artifacts["precompiled_ptx"]
        or outputs["compaction_cubin"] != artifacts["compaction_cubin"]
        or not isinstance(processes, Mapping)
        or set(processes) != {"ptx", "compaction_cubin"}
        or not isinstance(children, Mapping)
        or set(children) != {"ptx", "compaction_cubin"}
    ):
        raise RuntimeError("Goal5848 independent device receipt differs")
    ptx = Path(str(outputs["precompiled_ptx"]["path"]))
    cubin = Path(str(outputs["compaction_cubin"]["path"]))
    if (
        _file_identity(ptx) != outputs["precompiled_ptx"]
        or _file_identity(cubin) != outputs["compaction_cubin"]
        or b".version" not in ptx.read_bytes()[:4096]
        or cubin.read_bytes()[:4] != b"\x7fELF"
    ):
        raise RuntimeError("Goal5848 independent device product differs")
    loaded_nvrtc = None
    for label, mode, output_label in (
        ("ptx", "ptx", "precompiled_ptx"),
        ("compaction_cubin", "cubin", "compaction_cubin"),
    ):
        child = children[label]
        process = processes[label]
        if not isinstance(child, Mapping) or not isinstance(process, Mapping):
            raise TypeError("Goal5848 independent compiler row differs")
        _validate_seal(child, "receipt_sha256", f"device child {label}")
        child_file = process.get("child_receipt_file")
        if (
            child.get("schema")
            != "rtdl.goal5802.fresh_nvrtc_compile_child.v2"
            or child.get("status")
            != "PASS__FRESH_PROCESS_UNTIMED_NVRTC_COMPILE"
            or child.get("mode") != mode
            or child.get("compute_capability") != expected_compute_capability
            or child.get("product") != outputs[output_label]
            or any(
                type(child.get(field)) is not int or child[field] != 0
                for field in (
                    "clock_read_count",
                    "registered_performance_timing_count",
                    "gpu_kernel_launch_count",
                    "formal_worker_count",
                )
            )
            or process.get("exit_code") != 0
            or process.get("stderr_utf8") != ""
            or process.get("stderr_sha256") != hashlib.sha256(b"").hexdigest()
            or not isinstance(child_file, Mapping)
            or _file_identity(Path(str(child_file["path"]))) != child_file
            or _read(Path(str(child_file["path"])), f"device child {label}")
            != child
        ):
            raise RuntimeError("Goal5848 independent compiler evidence differs")
        current_nvrtc = child.get("loaded_nvrtc")
        if loaded_nvrtc is None:
            loaded_nvrtc = current_nvrtc
        elif current_nvrtc != loaded_nvrtc:
            raise RuntimeError("Goal5848 independent NVRTC identity differs")
        if not isinstance(current_nvrtc, Mapping):
            raise TypeError("Goal5848 independent NVRTC evidence absent")
        for library_label in ("library", "builtins"):
            library = current_nvrtc.get(library_label)
            if (
                not isinstance(library, Mapping)
                or library.get("canonical_regular_file") is not True
                or library.get("symlink") is not False
                or _file_identity(Path(str(library["path"]))) != {
                    "path": library.get("path"),
                    "bytes": library.get("bytes"),
                    "sha256": library.get("sha256"),
                }
            ):
                raise RuntimeError("Goal5848 independent NVRTC bytes differ")
    return _file_identity(receipt_path)


def build_authority(
    *,
    transaction_root: Path,
    preregistration_path: Path,
    preflight_path: Path,
    expected_source_commit: str,
    expected_predecessor_commit: str,
) -> dict[str, object]:
    root = transaction_root.resolve(strict=True)
    if root.is_symlink() or not root.is_dir():
        raise RuntimeError("Goal5848 transaction root differs")
    expected_top = {
        "workers", "processes", "direct_support", "transaction.json"
    }
    if {path.name for path in root.iterdir()} != expected_top:
        raise RuntimeError("Goal5848 transaction top-level file set differs")
    preregistration = _read(preregistration_path, "preregistration")
    artifacts = _validate_preregistration(
        preregistration,
        source_commit=expected_source_commit,
        predecessor_commit=expected_predecessor_commit,
    )
    preflight = _read(preflight_path, "preflight")
    _validate_seal(preflight, "preflight_sha256", "preflight")
    if (
        preflight.get("schema") != PREFLIGHT_SCHEMA
        or preflight.get("status") != PREFLIGHT_PASS_STATUS
        or preflight.get("source_commit") != expected_source_commit
        or preflight.get("predecessor_commit") != expected_predecessor_commit
        or preflight.get("preregistration_file_sha256")
        != _sha256(preregistration_path.resolve(strict=True))
        or preflight.get("preregistration_sha256")
        != preregistration["preregistration_sha256"]
    ):
        raise RuntimeError("Goal5848 authority preflight differs")
    witness = _validate_linked_authority(preflight, "timer_free_witness")
    competence = _validate_linked_authority(preflight, "baseline_competence")
    instrumentation = _validate_linked_authority(
        preflight, "instrumentation_overhead"
    )
    _validate_instrumentation_evidence(
        instrumentation,
        authority_path=Path(str(preflight["instrumentation_overhead_path"])),
        preregistration=preregistration,
    )
    instrumentation_tasks = instrumentation.get("tasks")
    if (
        not isinstance(instrumentation_tasks, Mapping)
        or set(instrumentation_tasks) != set(TASKS)
        or any(
            not isinstance(instrumentation_tasks[task], Mapping)
            or instrumentation_tasks[task].get("pass") is not True
            or instrumentation_tasks[task].get("limit_ppm")
            != INSTRUMENTATION_OVERHEAD_LIMIT_PPM
            or type(instrumentation_tasks[task].get(
                "instrumentation_overhead_ppm"
            )) is not int
            or instrumentation_tasks[task]["instrumentation_overhead_ppm"]
            > INSTRUMENTATION_OVERHEAD_LIMIT_PPM
            for task in TASKS
        )
    ):
        raise RuntimeError("Goal5848 instrumentation gate differs")
    transaction_path = root / "transaction.json"
    transaction = _read(transaction_path, "transaction")
    _validate_seal(transaction, "transaction_sha256", "transaction")
    if (
        transaction.get("schema") != "rtdl.goal5848.formal_transaction.v1"
        or transaction.get("status")
        != "PASS__GOAL5848_SINGLE_GENERATION_FORMAL_TRANSACTION"
        or transaction.get("expected_source_commit") != expected_source_commit
        or transaction.get("expected_predecessor_commit")
        != expected_predecessor_commit
        or transaction.get("preregistration_file_sha256")
        != _sha256(preregistration_path.resolve(strict=True))
        or transaction.get("preflight_file_sha256")
        != _sha256(preflight_path.resolve(strict=True))
        or transaction.get("worker_count") != len(build_schedule())
        or transaction.get("process_count") != len(build_schedule())
        or transaction.get("retry_count") != 0
        or transaction.get("discard_count") != 0
    ):
        raise RuntimeError("Goal5848 authority transaction differs")
    workers_root = root / "workers"
    processes_root = root / "processes"
    expected_names = {
        f"{row['worker_id']}.json" for row in build_schedule()
    }
    if (
        workers_root.is_symlink()
        or processes_root.is_symlink()
        or {path.name for path in workers_root.iterdir()} != expected_names
        or {path.name for path in processes_root.iterdir()} != expected_names
    ):
        raise RuntimeError("Goal5848 authority worker/process file set differs")
    receipts = []
    worker_files = []
    process_files = []
    for row in build_schedule():
        worker_id = str(row["worker_id"])
        worker_path = workers_root / f"{worker_id}.json"
        process_path = processes_root / f"{worker_id}.json"
        worker = _read(worker_path, f"worker {worker_id}")
        process = _read(process_path, f"process {worker_id}")
        _validate_process(
            process,
            worker=worker,
            worker_id=worker_id,
            expected_command=_expected_process_command(
                row,
                preregistration=preregistration,
                artifacts=artifacts,
                preregistration_path=preregistration_path.resolve(strict=True),
                transaction_root=root,
            ),
            expected_execution_context=_expected_execution_context(
                preregistration
            ),
        )
        worker_source = worker.get("source")
        expected_tree = (
            preregistration["predecessor_tree"]
            if row["arm"] == PREDECESSOR_RTDL_ARM
            else preregistration["source_tree"]
        )
        if (
            not isinstance(worker_source, Mapping)
            or worker_source.get("tree") != expected_tree
            or worker.get("python") != preregistration["python_version"]
        ):
            raise RuntimeError(
                f"Goal5848 authority worker source/runtime differs: {worker_id}"
            )
        receipts.append(worker)
        worker_files.append(_file_identity(worker_path))
        process_files.append(_file_identity(process_path))
    recount = evaluate_complete_transaction(
        receipts,
        expected_source_commit=expected_source_commit,
        expected_predecessor_commit=expected_predecessor_commit,
    )
    if (
        recount != transaction.get("recount")
        or recount.get("hardware") != preflight.get("hardware")
        or preflight.get("hardware") != witness.get("hardware")
        or preflight.get("hardware") != competence.get("hardware")
        or preflight.get("hardware") != instrumentation.get("hardware")
    ):
        raise RuntimeError("Goal5848 authority independent recount differs")
    hardware = preflight.get("hardware")
    if not isinstance(hardware, Mapping):
        raise TypeError("Goal5848 authority hardware is absent")
    device_artifact_receipt = _validate_device_artifacts_independently(
        artifacts,
        expected_source_commit=expected_source_commit,
        expected_compute_capability=str(hardware.get("compute_capability")),
    )
    aot_cache_authority = load_aot_cache_authority(
        Path(str(artifacts["aot_cache_authority"]["path"])),
        candidate_manifest=Path(str(artifacts["candidate_manifest"]["path"])),
        expected_source_commit=expected_source_commit,
    )
    direct_support = _validate_direct_support(root, receipts)
    source = _git_identity(Path(str(preregistration["source_identity"]["path"])))
    predecessor = _git_identity(Path(str(
        preregistration["predecessor_identity"]["path"]
    )))
    pyoptix = _git_identity(Path(str(
        preregistration["pyoptix_identity"]["path"]
    )))
    if (
        source["commit"] != expected_source_commit
        or source["tree"] != preregistration["source_tree"]
        or source["status"] != ""
        or predecessor["commit"] != expected_predecessor_commit
        or predecessor["tree"] != preregistration["predecessor_tree"]
        or predecessor["status"] != ""
        or pyoptix["commit"] != preregistration["pyoptix_commit"]
        or pyoptix["tree"] != preregistration["pyoptix_tree"]
        or pyoptix["status"] != ""
    ):
        raise RuntimeError("Goal5848 authority Git identity differs")
    result = {
        "schema": "rtdl.goal5848.single_generation_authority.v1",
        "status": "PASS__INDEPENDENT_BYTE_AND_GATE_RECOUNT",
        "source_commit": expected_source_commit,
        "predecessor_commit": expected_predecessor_commit,
        "transaction": _file_identity(transaction_path),
        "preregistration": _file_identity(preregistration_path),
        "preflight": _file_identity(preflight_path),
        "timer_free_witness": _file_identity(Path(str(
            preflight["timer_free_witness_path"]
        ))),
        "baseline_competence": _file_identity(Path(str(
            preflight["baseline_competence_path"]
        ))),
        "instrumentation_overhead": _file_identity(Path(str(
            preflight["instrumentation_overhead_path"]
        ))),
        "device_artifact_build_receipt": device_artifact_receipt,
        "aot_cache_authority": _file_identity(Path(str(
            artifacts["aot_cache_authority"]["path"]
        ))),
        "aot_cache_authority_sha256": aot_cache_authority[
            "authority_sha256"
        ],
        "artifacts": artifacts,
        "worker_files": worker_files,
        "process_files": process_files,
        "direct_support_files": direct_support,
        "worker_count": len(receipts),
        "process_count": len(process_files),
        "direct_support_count": len(direct_support),
        "retry_count": 0,
        "discard_count": 0,
        "recount": recount,
        "external_review_complete": False,
        "public_or_manuscript_claim_authorized": False,
    }
    result["authority_sha256"] = digest(result)
    return result


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transaction-root", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--expected-predecessor-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_authority(
        transaction_root=args.transaction_root,
        preregistration_path=args.preregistration,
        preflight_path=args.preflight,
        expected_source_commit=args.expected_source_commit,
        expected_predecessor_commit=args.expected_predecessor_commit,
    )
    _write_create(_new_output_path(args.output), result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
