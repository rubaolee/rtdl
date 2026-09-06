"""Single-attempt formal transaction controller for Goal5848."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from collections.abc import Mapping
from pathlib import Path

from .aot_cache_authority import load_aot_cache_authority
from .contracts import (
    ARMS,
    BLOCKS,
    DIRECT_OPTIX_ARM,
    IDIOMATIC_PYOPTIX_ARM,
    IMPLEMENTATION_ENTRY_BLOCK_RATIO_LIMIT_PPM,
    IMPLEMENTATION_ENTRY_RATIO_LIMIT_PPM,
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
    RELATION_TASK,
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
    require_formal_cache_policy,
    strict_json_loads,
)
from .device_artifacts import load_device_artifact_receipt
from .worker import ROOT, _sha256_file, _write_create

PROCESS_SCHEMA = "rtdl.goal5848.formal_process.v2"
TRANSACTION_SCHEMA = "rtdl.goal5848.formal_transaction.v2"
_FORMAL_INHERITED_ENVIRONMENT = {
    "CUDA_VISIBLE_DEVICES": "0",
    "CUDA_CACHE_DISABLE": "1",
    "RTDL_OPTIX_DISK_CACHE_POLICY": "disabled",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONNOUSERSITE": "1",
}
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


def _require_formal_worker_environment() -> None:
    observed = {
        name: os.environ.get(name)
        for name in _FORMAL_INHERITED_ENVIRONMENT
    }
    unexpected = [
        name for name in _FORMAL_SANITIZED_ENVIRONMENT if name in os.environ
    ]
    if observed != _FORMAL_INHERITED_ENVIRONMENT or unexpected:
        raise RuntimeError("Goal5848 formal worker environment differs")


def _read_json(path: Path, label: str) -> dict[str, object]:
    value = strict_json_loads(
        path.resolve(strict=True).read_text(encoding="utf-8"),
        label=f"Goal5848 {label}",
    )
    if not isinstance(value, dict):
        raise TypeError(f"Goal5848 {label} is not an object")
    return value


def _validate_preregistration(
    path: Path,
    *,
    expected_source_commit: str,
    expected_predecessor_commit: str,
    arguments: argparse.Namespace | None = None,
) -> dict[str, object]:
    value = _read_json(path, "preregistration")
    unsigned = dict(value)
    seal = unsigned.pop("preregistration_sha256", None)
    expected_keys = {
        "schema", "status", "source_commit", "source_tree",
        "predecessor_commit", "predecessor_tree", "pyoptix_commit",
        "pyoptix_tree", "source_identity", "predecessor_identity",
        "pyoptix_identity", "python", "python_version",
        "expected_optix_sdk", "optix_disk_cache_policy", "artifacts",
        "tasks", "task_contracts",
        "primary_arms", "all_arms", "blocks", "steady_warmups",
        "steady_repetitions", "schedule", "schedule_sha256",
        "thresholds_ppm", "partition_reconciliation", "endpoint",
        "instrumentation_protocol", "aot_cache_protocol", "estimator",
        "failure_policy",
        "registered_performance_timing_count",
        "formal_worker_count", "claim_boundary", "retry_count",
        "discard_count", "preregistration_sha256",
    }
    schedule = list(build_schedule())
    if (
        set(value) != expected_keys
        or seal != digest(unsigned)
        or value.get("schema") != PREREGISTRATION_SCHEMA
        or value.get("status") != "FROZEN__BEFORE_FORMAL_WORKER_ZERO"
        or value.get("source_commit") != expected_source_commit
        or value.get("predecessor_commit") != expected_predecessor_commit
        or value.get("schedule") != schedule
        or value.get("schedule_sha256") != digest(schedule)
        or value.get("tasks") != list(TASKS)
        or value.get("task_contracts") != TASK_CONTRACTS
        or value.get("primary_arms") != list(PRIMARY_ARMS)
        or value.get("all_arms") != list(ARMS)
        or value.get("blocks") != BLOCKS
        or value.get("steady_warmups") != STEADY_WARMUPS
        or value.get("steady_repetitions") != STEADY_REPETITIONS
        or value.get("thresholds_ppm") != {
            "implementation_entry_median": (
                IMPLEMENTATION_ENTRY_RATIO_LIMIT_PPM
            ),
            "implementation_entry_worst_block": (
                IMPLEMENTATION_ENTRY_BLOCK_RATIO_LIMIT_PPM
            ),
            "post_import_diagnostic_reference_median": (
                POST_IMPORT_RATIO_LIMIT_PPM
            ),
            "post_import_diagnostic_reference_worst_block": (
                POST_IMPORT_BLOCK_RATIO_LIMIT_PPM
            ),
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
        or value.get("registered_performance_timing_count") != 0
        or value.get("formal_worker_count") != 0
        or value.get("retry_count") != 0
        or value.get("discard_count") != 0
        or value.get("optix_disk_cache_policy")
        != "disabled_for_all_primary_arms"
        or value.get("endpoint") != (
            "implementation_entry_to_first_exact_public_result__"
            "post_import_retained_as_state_mismatch_diagnostic"
        )
    ):
        raise RuntimeError("Goal5848 preregistration differs")
    if arguments is not None:
        _validate_preregistered_inputs(value, arguments)
    return value


def _validate_file_identity(path: Path, row: object, label: str) -> None:
    if not isinstance(row, Mapping) or set(row) != {
        "path", "bytes", "sha256"
    }:
        raise RuntimeError(f"Goal5848 preregistered file row differs: {label}")
    absolute = path.expanduser().absolute()
    if absolute.is_symlink():
        raise RuntimeError(f"Goal5848 preregistered file differs: {label}")
    resolved = absolute.resolve(strict=True)
    if (
        row["path"] != str(resolved)
        or row["bytes"] != resolved.stat().st_size
        or row["sha256"] != _sha256_file(resolved)
    ):
        raise RuntimeError(f"Goal5848 preregistered file differs: {label}")


def _validate_preregistered_inputs(
    value: Mapping[str, object],
    arguments: argparse.Namespace,
) -> None:
    artifacts = value.get("artifacts")
    if not isinstance(artifacts, Mapping) or set(artifacts) != set(
        PREREGISTRATION_ARTIFACT_ARGUMENTS
    ):
        raise RuntimeError("Goal5848 preregistered artifacts differ")
    for label, argument in PREREGISTRATION_ARTIFACT_ARGUMENTS.items():
        _validate_file_identity(
            Path(getattr(arguments, argument)), artifacts[label], label
        )
    load_device_artifact_receipt(
        arguments.device_artifact_build_receipt,
        precompiled_ptx=arguments.precompiled_ptx,
        compaction_cubin=arguments.compaction_cubin,
        expected_source_commit=arguments.expected_source_commit,
        expected_optix_sdk=arguments.expected_optix_sdk,
        repository_root=ROOT,
    )
    load_aot_cache_authority(
        arguments.aot_cache_authority,
        candidate_manifest=arguments.candidate_manifest,
        expected_source_commit=arguments.expected_source_commit,
    )
    _validate_file_identity(
        arguments.python.resolve(strict=True), value.get("python"), "python"
    )
    if value.get("expected_optix_sdk") != arguments.expected_optix_sdk:
        raise RuntimeError("Goal5848 preregistered OptiX API differs")
    for label, path, commit, tree in (
        (
            "source",
            ROOT,
            arguments.expected_source_commit,
            value.get("source_tree"),
        ),
        (
            "predecessor",
            arguments.predecessor_root,
            arguments.expected_predecessor_commit,
            value.get("predecessor_tree"),
        ),
        (
            "PyOptix",
            arguments.pyoptix_source,
            arguments.expected_pyoptix_commit,
            arguments.expected_pyoptix_tree,
        ),
    ):
        identity = value.get(f"{label.lower()}_identity")
        resolved = path.resolve(strict=True)
        observed_commit = subprocess.run(
            ["git", "-C", str(resolved), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        observed_tree = subprocess.run(
            ["git", "-C", str(resolved), "rev-parse", "HEAD^{tree}"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        observed_status = subprocess.run(
            [
                "git", "-C", str(resolved), "status", "--porcelain=v1",
                "--untracked-files=all",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if (
            not isinstance(identity, Mapping)
            or identity.get("path") != str(resolved)
            or identity.get("commit") != commit
            or identity.get("tree") != tree
            or identity.get("status") != ""
            or identity.get("clean") is not True
            or observed_commit != commit
            or observed_tree != tree
            or observed_status != ""
        ):
            raise RuntimeError(
                f"Goal5848 preregistered {label} repository differs"
            )
    if (
        value.get("pyoptix_commit") != arguments.expected_pyoptix_commit
        or value.get("pyoptix_tree") != arguments.expected_pyoptix_tree
    ):
        raise RuntimeError("Goal5848 preregistered PyOptix identity differs")


def _new_output_root(path: Path) -> Path:
    absolute = path.expanduser().absolute()
    if absolute.exists() or absolute.is_symlink():
        raise FileExistsError(absolute)
    parent = absolute.parent.resolve(strict=True)
    candidate = parent / absolute.name
    repository = ROOT.resolve(strict=True)
    try:
        inside_repository = os.path.commonpath(
            (str(repository), str(candidate))
        ) == str(repository)
    except ValueError:
        inside_repository = False
    if inside_repository:
        raise RuntimeError("Goal5848 formal output must be outside source Git")
    return candidate


def _validate_preflight(
    path: Path,
    *,
    expected_source_commit: str,
    expected_predecessor_commit: str,
    arguments: argparse.Namespace | None = None,
) -> dict[str, object]:
    value = _read_json(path, "preflight")
    unsigned = dict(value)
    seal = unsigned.pop("preflight_sha256", None)
    if (
        set(value) != {
            "schema", "status", "source_commit", "predecessor_commit",
            "preregistration_path", "preregistration_file_sha256",
            "preregistration_sha256", "timer_free_witness_path",
            "timer_free_witness_file_sha256", "timer_free_witness_sha256",
            "baseline_competence_path", "baseline_competence_file_sha256",
            "baseline_competence_sha256",
            "instrumentation_overhead_path",
            "instrumentation_overhead_file_sha256",
            "instrumentation_overhead_sha256", "hardware",
            "untimed_witness_worker_count",
            "nonformal_competence_worker_count",
            "nonformal_instrumentation_worker_count",
            "registered_performance_timing_count", "formal_worker_count",
            "retry_count", "discard_count",
            "competence_timings_included_in_formal_estimators",
            "instrumentation_timings_included_in_formal_estimators",
            "external_review_complete",
            "public_or_manuscript_claim_authorized", "preflight_sha256",
        }
        or
        seal != digest(unsigned)
        or value.get("schema") != PREFLIGHT_SCHEMA
        or value.get("status") != PREFLIGHT_PASS_STATUS
        or value.get("source_commit") != expected_source_commit
        or value.get("predecessor_commit") != expected_predecessor_commit
        or value.get("registered_performance_timing_count") != 0
        or value.get("formal_worker_count") != 0
        or value.get("untimed_witness_worker_count") != 8
        or value.get("nonformal_competence_worker_count") != 4
        or value.get("nonformal_instrumentation_worker_count")
        != instrumentation_protocol()["worker_count"]
        or value.get("retry_count") != 0
        or value.get("discard_count") != 0
        or value.get("competence_timings_included_in_formal_estimators")
        is not False
        or value.get("instrumentation_timings_included_in_formal_estimators")
        is not False
        or value.get("external_review_complete") is not False
        or value.get("public_or_manuscript_claim_authorized") is not False
    ):
        raise RuntimeError("Goal5848 timer-free preflight differs")
    if arguments is not None:
        preregistration = arguments.preregistration.resolve(strict=True)
        if (
            value.get("preregistration_path") != str(preregistration)
            or value.get("preregistration_file_sha256")
            != _sha256_file(preregistration)
        ):
            raise RuntimeError("Goal5848 preflight preregistration differs")
        for prefix in (
            "timer_free_witness",
            "baseline_competence",
            "instrumentation_overhead",
        ):
            linked = Path(str(value.get(f"{prefix}_path"))).resolve(strict=True)
            linked_value = _read_json(linked, prefix)
            linked_unsigned = dict(linked_value)
            linked_seal = linked_unsigned.pop("authority_sha256", None)
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
                _sha256_file(linked) != value.get(f"{prefix}_file_sha256")
                or linked_seal != digest(linked_unsigned)
                or linked_seal != value.get(f"{prefix}_sha256")
                or linked_value.get("schema") != expected_schema
                or linked_value.get("status") != expected_status
                or linked_value.get("source_commit")
                != expected_source_commit
                or linked_value.get("predecessor_commit")
                != expected_predecessor_commit
                or linked_value.get("registered_performance_timing_count") != 0
                or linked_value.get("formal_worker_count") != 0
                or linked_value.get("retry_count") != 0
                or linked_value.get("discard_count") != 0
                or (
                    prefix == "instrumentation_overhead"
                    and (
                        linked_value.get("worker_count")
                        != instrumentation_protocol()["worker_count"]
                        or linked_value.get("process_count")
                        != instrumentation_protocol()["worker_count"]
                        or linked_value.get("schedule")
                        != instrumentation_protocol()["schedule"]
                        or linked_value.get("included_in_formal_estimators")
                        is not False
                    )
                )
            ):
                raise RuntimeError(f"Goal5848 {prefix} authority differs")
    return value


def _python_worker_command(
    row: Mapping[str, object],
    args: argparse.Namespace,
    output: Path,
) -> list[str]:
    common = [
        str(args.python.resolve(strict=True)),
        "-m",
        "experiments.goal5848_strong_baseline.worker",
        "--arm",
        str(row["arm"]),
        "--task",
        str(row["task"]),
        "--block",
        str(row["block"]),
        "--worker-id",
        str(row["worker_id"]),
        "--classification",
        "formal",
        "--phase-instrumentation",
        "on",
        "--expected-source-commit",
        args.expected_source_commit,
        "--warmups",
        str(STEADY_WARMUPS),
        "--repetitions",
        str(STEADY_REPETITIONS),
        "--output",
        str(output),
    ]
    if row["arm"] == RTDL_ARM:
        return [
            *common,
            "--candidate-manifest",
            str(args.candidate_manifest.resolve(strict=True)),
        ]
    command = [
        *common,
        "--precompiled-ptx",
        str(args.precompiled_ptx.resolve(strict=True)),
        "--pyoptix-source",
        str(args.pyoptix_source.resolve(strict=True)),
        "--pyoptix-build-receipt",
        str(args.pyoptix_build_receipt.resolve(strict=True)),
        "--expected-optix-sdk",
        args.expected_optix_sdk,
    ]
    if row["arm"] == STRONG_PYOPTIX_ARM and row["task"] == RELATION_TASK:
        command.extend([
            "--compaction-cubin",
            str(args.compaction_cubin.resolve(strict=True)),
        ])
    return command


def _command(
    row: Mapping[str, object],
    args: argparse.Namespace,
    output: Path,
    support_root: Path,
) -> list[str]:
    arm = row["arm"]
    if arm in {RTDL_ARM, IDIOMATIC_PYOPTIX_ARM, STRONG_PYOPTIX_ARM}:
        return _python_worker_command(row, args, output)
    common = [
        str(args.python.resolve(strict=True)),
        "-m",
        (
            "experiments.goal5848_strong_baseline.direct_bridge"
            if arm == DIRECT_OPTIX_ARM
            else "experiments.goal5848_strong_baseline.predecessor_worker"
        ),
        "--task",
        str(row["task"]),
        "--block",
        str(row["block"]),
        "--worker-id",
        str(row["worker_id"]),
        "--classification",
        "formal",
        "--output",
        str(output),
    ]
    if arm == PREDECESSOR_RTDL_ARM:
        return [
            *common,
            "--predecessor-root",
            str(args.predecessor_root.resolve(strict=True)),
            "--expected-predecessor-commit",
            args.expected_predecessor_commit,
            "--candidate-manifest",
            str(args.predecessor_candidate_manifest.resolve(strict=True)),
            "--warmups",
            str(STEADY_WARMUPS),
            "--repetitions",
            str(STEADY_REPETITIONS),
        ]
    command = [
        *common,
        "--expected-source-commit",
        args.expected_source_commit,
        "--direct-worker",
        str(args.direct_worker.resolve(strict=True)),
        "--direct-build-receipt",
        str(args.direct_build_receipt.resolve(strict=True)),
        "--derivation-receipt",
        str(args.derivation_receipt.resolve(strict=True)),
        "--preregistration",
        str(args.preregistration.resolve(strict=True)),
        "--precompiled-ptx",
        str(args.precompiled_ptx.resolve(strict=True)),
        "--support-root",
        str(support_root),
    ]
    if row["task"] == RELATION_TASK:
        command.extend([
            "--compaction-cubin",
            str(args.compaction_cubin.resolve(strict=True)),
        ])
    return command


def _worker_execution_context(
    environment: Mapping[str, str],
) -> dict[str, object]:
    return {
        "cwd": str(ROOT.resolve(strict=True)),
        "environment": {
            name: environment.get(name)
            for name in (
                "PYTHONPATH",
                *_FORMAL_INHERITED_ENVIRONMENT,
                *_FORMAL_SANITIZED_ENVIRONMENT,
            )
        },
    }


def _run_once(
    row: Mapping[str, object],
    args: argparse.Namespace,
    *,
    output: Path,
    process_output: Path,
    support_root: Path,
) -> dict[str, object]:
    command = _command(row, args, output, support_root)
    environment = dict(os.environ)
    environment["PYTHONPATH"] = f"{ROOT / 'src'}:{ROOT}"
    execution_context = _worker_execution_context(environment)
    started = time.perf_counter_ns()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        check=False,
        timeout=args.worker_timeout_seconds,
    )
    wall_ns = time.perf_counter_ns() - started
    try:
        stdout = completed.stdout.decode("utf-8")
        stderr = completed.stderr.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RuntimeError("Goal5848 worker output is not UTF-8") from error
    process = {
        "schema": PROCESS_SCHEMA,
        "worker_id": row["worker_id"],
        "command": command,
        "execution_context": execution_context,
        "exit_code": completed.returncode,
        "wall_ns": wall_ns,
        "stdout_utf8": stdout,
        "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
        "stderr_utf8": stderr,
        "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
    }
    process["process_sha256"] = digest(process)
    _write_create(process_output, process)
    if completed.returncode != 0 or stderr or not output.is_file():
        raise RuntimeError(f"Goal5848 worker failed: {row['worker_id']}")
    receipt = _read_json(output, "worker receipt")
    compact_stdout = json.dumps(receipt, sort_keys=True) + "\n"
    if stdout != compact_stdout:
        raise RuntimeError("Goal5848 worker stdout/file receipt differs")
    return receipt


def _write_failure(
    path: Path,
    *,
    stage: str,
    completed_worker_ids: list[str],
    error: BaseException,
) -> None:
    value = {
        "schema": "rtdl.goal5848.formal_transaction_failure.v1",
        "status": "FAIL__TRANSACTION_TERMINATED__NO_RETRY_NO_DISCARD",
        "failed_stage": stage,
        "completed_worker_ids": completed_worker_ids,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "retry_count": 0,
        "discard_count": 0,
        "prior_rows_authorized_for_pooling": False,
    }
    value["failure_sha256"] = digest(value)
    _write_create(path, value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--expected-predecessor-commit", required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
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
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--worker-timeout-seconds", type=int, default=600)
    args = parser.parse_args()
    require_formal_cache_policy()
    _require_formal_worker_environment()
    if args.worker_timeout_seconds <= 0:
        raise ValueError("Goal5848 worker timeout differs")
    output_root = _new_output_root(args.output_root)
    output_root.mkdir(parents=True)
    workers = output_root / "workers"
    processes = output_root / "processes"
    support = output_root / "direct_support"
    workers.mkdir()
    processes.mkdir()
    support.mkdir()
    completed_ids: list[str] = []
    receipts = []
    stage = "PREREGISTRATION"
    try:
        preregistration = _validate_preregistration(
            args.preregistration,
            expected_source_commit=args.expected_source_commit,
            expected_predecessor_commit=args.expected_predecessor_commit,
            arguments=args,
        )
        stage = "TIMER_FREE_PREFLIGHT"
        preflight = _validate_preflight(
            args.preflight,
            expected_source_commit=args.expected_source_commit,
            expected_predecessor_commit=args.expected_predecessor_commit,
            arguments=args,
        )
        if preflight["preregistration_sha256"] != preregistration[
            "preregistration_sha256"
        ]:
            raise RuntimeError("Goal5848 preflight freeze binding differs")
        for row in build_schedule():
            worker_id = str(row["worker_id"])
            stage = worker_id
            receipt = _run_once(
                row,
                args,
                output=workers / f"{worker_id}.json",
                process_output=processes / f"{worker_id}.json",
                support_root=support,
            )
            receipts.append(receipt)
            completed_ids.append(worker_id)
        stage = "INDEPENDENT_RECOUNT"
        recount = evaluate_complete_transaction(
            receipts,
            expected_source_commit=args.expected_source_commit,
            expected_predecessor_commit=args.expected_predecessor_commit,
        )
        if preflight["hardware"] != recount["hardware"]:
            raise RuntimeError("Goal5848 preflight/formal GPU identity differs")
        result = {
            "schema": TRANSACTION_SCHEMA,
            "status": (
                "PASS__GOAL5848_LIFECYCLE_CORRECTED_SINGLE_GENERATION_"
                "FORMAL_TRANSACTION"
            ),
            "expected_source_commit": args.expected_source_commit,
            "expected_predecessor_commit": args.expected_predecessor_commit,
            "preregistration_file_sha256": _sha256_file(
                args.preregistration.resolve(strict=True)
            ),
            "preregistration_sha256": preregistration[
                "preregistration_sha256"
            ],
            "preflight_file_sha256": _sha256_file(
                args.preflight.resolve(strict=True)
            ),
            "preflight_sha256": preflight["preflight_sha256"],
            "worker_count": len(receipts),
            "process_count": len(receipts),
            "retry_count": 0,
            "discard_count": 0,
            "recount": recount,
            "claim_boundary": {
                "single_generation_only": True,
                "external_review_complete": False,
                "public_or_manuscript_claim_authorized": False,
            },
        }
        result["transaction_sha256"] = digest(result)
        _write_create(output_root / "transaction.json", result)
        print(json.dumps(result, sort_keys=True))
    except BaseException as error:
        _write_failure(
            output_root / "failure.json",
            stage=stage,
            completed_worker_ids=completed_ids,
            error=error,
        )
        raise


if __name__ == "__main__":
    main()
