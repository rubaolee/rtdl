"""Normalize the audited native Direct OptiX worker for Goal5848."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import subprocess
import time
from collections.abc import Mapping
from pathlib import Path

from experiments.goal5802_premeasurement.workload import (
    RELATION_TASK as DIRECT_RELATION_TASK,
)
from experiments.goal5802_premeasurement.workload import (
    TRIANGLE_TASK as DIRECT_TRIANGLE_TASK,
)

from .contracts import (
    BLOCKS,
    COMPONENT_DIAGNOSTIC_KEYS,
    DIRECT_OPTIX_ARM,
    RELATION_TASK,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    TASK_CONTRACTS,
    TRIANGLE_TASK,
    WORKER_SCHEMA,
    digest,
    strict_json_loads,
)
from .worker import (
    ROOT,
    _git_identity,
    _hardware,
    _sha256_file,
    _summary,
    _write_create,
)
from .workloads import relation_workload, triangle_workload


def _read_json(path: Path, label: str) -> dict[str, object]:
    value = strict_json_loads(
        path.resolve(strict=True).read_text(encoding="utf-8"),
        label=f"Goal5848 {label}",
    )
    if not isinstance(value, dict):
        raise TypeError(f"Goal5848 {label} is not an object")
    return value


def _compatibility_preflight(
    path: Path,
    *,
    runtime_manifest_sha256: str,
) -> tuple[str, str]:
    unsigned = {
        "schema": "rtdl.goal5802.formal_runtime_preflight.v1",
        "status": "PASS__LIVE_TARGET_AND_CROSS_ARM_NVRTC_BEFORE_WORKER_ZERO",
        "runtime_manifest_file_sha256": runtime_manifest_sha256,
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0,
        "unused_compatibility_tail": 0,
    }
    preflight_sha256 = digest(unsigned)
    value = {**unsigned, "preflight_sha256": preflight_sha256}
    _write_create(path, value)
    return _sha256_file(path), preflight_sha256


def _capability_frame(
    *,
    worker_id: str,
    runtime_manifest_sha256: str,
    preflight_file_sha256: str,
    preflight_sha256: str,
) -> bytes:
    value = {
        "controller_pid": os.getpid(),
        "nonce": secrets.token_hex(32),
        "preflight_receipt_file_sha256": preflight_file_sha256,
        "preflight_sha256": preflight_sha256,
        "runtime_manifest_sha256": runtime_manifest_sha256,
        "schema": "rtdl.goal5802.live_controller_worker_capability.v1",
        "worker_id": worker_id,
    }
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def _validate_derivation_and_build(args: argparse.Namespace) -> dict[str, object]:
    derivation = _read_json(args.derivation_receipt, "derivation receipt")
    build = _read_json(args.direct_build_receipt, "Direct build receipt")
    binary = args.direct_worker.resolve(strict=True)
    derivation_unsigned = dict(derivation)
    derivation_seal = derivation_unsigned.pop("receipt_sha256", None)
    build_unsigned = dict(build)
    build_seal = build_unsigned.pop("receipt_sha256", None)
    bundle_root = args.derivation_receipt.resolve(strict=True).parent
    source_candidate = (
        bundle_root / "source/goal5802_premeasurement/direct_worker.cpp"
    )
    dependency_candidate = (
        bundle_root / "source/goal5796_matched/direct_optix.cpp"
    )
    if (
        source_candidate.is_symlink()
        or dependency_candidate.is_symlink()
        or source_candidate.parent.is_symlink()
        or dependency_candidate.parent.is_symlink()
    ):
        raise RuntimeError("Goal5848 Direct source bundle contains a symlink")
    expected_source = source_candidate.resolve(strict=True)
    expected_dependency = dependency_candidate.resolve(strict=True)
    include_dependency = derivation.get("include_dependency")
    expected_include_dependency = {
        "directive_utf8": '#include "../goal5796_matched/direct_optix.cpp"',
        "source_relative_path": (
            "experiments/goal5796_matched/direct_optix.cpp"
        ),
        "bundle_relative_path": (
            "source/goal5796_matched/direct_optix.cpp"
        ),
        "bytes": 25148,
        "sha256": (
            "2533a14152e441f97690e8e427e97f1be5f1747ee8faa0f181cd05b438a01383"
        ),
        "regular_file_required": True,
        "semantic_change": False,
    }
    build_command = build.get("command")
    if (
        derivation_seal != digest(derivation_unsigned)
        or build_seal != digest(build_unsigned)
        or
        derivation.get("schema")
        != "rtdl.goal5848.direct_source_derivation.v2"
        or derivation.get("status")
        != "PASS__PINNED_INCLUDE_BUNDLE_AND_EXACT_TWO_CONSTANT_DERIVATION"
        or derivation.get("optix_cuda_or_output_logic_changed") is not False
        or derivation.get("derived_source_bundle_relative_path")
        != "source/goal5802_premeasurement/direct_worker.cpp"
        or include_dependency != expected_include_dependency
        or not expected_source.is_file()
        or not expected_dependency.is_file()
        or _sha256_file(expected_source) != derivation.get("derived_sha256")
        or expected_dependency.stat().st_size
        != expected_include_dependency["bytes"]
        or _sha256_file(expected_dependency)
        != expected_include_dependency["sha256"]
        or (
            expected_source.parent
            / "../goal5796_matched/direct_optix.cpp"
        ).resolve(strict=True)
        != expected_dependency
        or build.get("schema")
        != "rtdl.goal5802.direct_worker_untimed_build_receipt.v2"
        or build.get("status") != "PASS__SOURCE_TO_DIRECT_WORKER__UNTIMED"
        or build.get("direct_source_sha256") != derivation.get("derived_sha256")
        or not isinstance(build_command, list)
        or build_command.count(str(expected_source)) != 1
        or build.get("output_bytes") != binary.stat().st_size
        or build.get("output_sha256") != _sha256_file(binary)
    ):
        raise RuntimeError("Goal5848 Direct derivation/build identity differs")
    return {
        "binary_path": str(binary),
        "binary_sha256": _sha256_file(binary),
        "build_receipt_sha256": _sha256_file(
            args.direct_build_receipt.resolve(strict=True)
        ),
        "derivation_receipt_sha256": _sha256_file(
            args.derivation_receipt.resolve(strict=True)
        ),
        "derived_source_sha256": derivation["derived_sha256"],
        "parent_source_sha256": derivation["parent_sha256"],
    }


def _validate_direct_receipt(
    value: Mapping[str, object],
    *,
    task: str,
    worker_id: str,
) -> None:
    expected_task = (
        DIRECT_RELATION_TASK if task == RELATION_TASK else DIRECT_TRIANGLE_TASK
    )
    if (
        value.get("schema") != "rtdl.goal5802.direct_scalar.worker.v1"
        or value.get("status") != "PASS"
        or value.get("arm") != "A_DIRECT_CUDA_OPTIX"
        or value.get("worker_id") != worker_id
        or value.get("task") != expected_task
        or value.get("regime") != "STEADY_E2E"
        or value.get("registered_performance_timing_count")
        != STEADY_REPETITIONS
    ):
        raise RuntimeError("Goal5848 Direct worker envelope differs")
    durations = value.get("execute_or_regime_durations_ns")
    if (
        not isinstance(durations, list)
        or len(durations) != STEADY_REPETITIONS
        or any(type(item) is not int or item <= 0 for item in durations)
    ):
        raise RuntimeError("Goal5848 Direct retained samples differ")
    correctness = value.get("correctness")
    ledger = value.get("operation_ledger")
    if not isinstance(correctness, Mapping) or not isinstance(ledger, Mapping):
        raise TypeError("Goal5848 Direct correctness evidence is absent")
    if task == RELATION_TASK:
        expected = [list(row) for row in relation_workload().expected_rows]
        if (
            correctness.get("oracle_exact") is not True
            or correctness.get("canonical_rows") != expected
            or correctness.get("canonical_row_count") != len(expected)
            or correctness.get("raw_event_count") != 2 * len(expected)
            or correctness.get("semantic_unique_count") != len(expected)
            or correctness.get("device_status") != 0
            or correctness.get("device_overflow") != 0
            or ledger.get("optix_launch_count") != 2
            or ledger.get("semantic_compaction_launch_count") != 1
            or ledger.get("application_output_d2h_bytes")
            != TASK_CONTRACTS[task]["public_output_bytes"]
        ):
            raise RuntimeError("Goal5848 Direct relation contract differs")
    else:
        expected = triangle_workload().expected_reduced_u64
        if (
            correctness.get("oracle_exact") is not True
            or correctness.get("reduced_u64") != expected
            or correctness.get("device_status") != 0
            or ledger.get("optix_launch_count") != 1
            or ledger.get("semantic_compaction_launch_count") != 0
            or ledger.get("application_output_d2h_bytes")
            != TASK_CONTRACTS[task]["public_output_bytes"]
        ):
            raise RuntimeError("Goal5848 Direct triangle contract differs")
    if (
        ledger.get("per_ray_d2h_bytes") != 0
        or ledger.get("status_output_commit_blocking_boundary_count") != 2
    ):
        raise RuntimeError("Goal5848 Direct public transport differs")
    lifecycle = value.get("execution_lifecycle_receipts")
    if (
        not isinstance(lifecycle, list)
        or len(lifecycle) != STEADY_WARMUPS + STEADY_REPETITIONS
        or lifecycle[0].get("prepared_input_reused") is not False
        or any(
            row.get("prepared_input_reused") is not True
            for row in lifecycle[1:]
        )
    ):
        raise RuntimeError("Goal5848 Direct prepared-input lifecycle differs")


def _run_direct(args: argparse.Namespace) -> tuple[dict[str, object], dict[str, object]]:
    identity = _validate_derivation_and_build(args)
    preregistration_sha256 = _sha256_file(args.preregistration.resolve(strict=True))
    runtime_manifest_sha256 = identity["build_receipt_sha256"]
    authority_sha256 = identity["derivation_receipt_sha256"]
    preflight_path = args.support_root / f"{args.worker_id}.preflight.json"
    preflight_file_sha256, preflight_sha256 = _compatibility_preflight(
        preflight_path,
        runtime_manifest_sha256=str(runtime_manifest_sha256),
    )
    ptx = args.precompiled_ptx.resolve(strict=True)
    command = [
        str(args.direct_worker.resolve(strict=True)),
        "--worker-id",
        args.worker_id,
        "--freeze-sha256",
        preregistration_sha256,
        "--authority-sha256",
        str(authority_sha256),
        "--runtime-manifest-sha256",
        str(runtime_manifest_sha256),
        "--task",
        DIRECT_RELATION_TASK if args.task == RELATION_TASK else DIRECT_TRIANGLE_TASK,
        "--regime",
        "STEADY_E2E",
        "--ptx",
        str(ptx),
        "--ptx-sha256",
        _sha256_file(ptx),
    ]
    if args.task == RELATION_TASK:
        cubin = args.compaction_cubin.resolve(strict=True)
        command.extend([
            "--compaction-cubin",
            str(cubin),
            "--compaction-cubin-sha256",
            _sha256_file(cubin),
        ])
    environment = dict(os.environ)
    environment.update({
        "GOAL5802_FORMAL_CONTROLLER_PID": str(os.getpid()),
        "GOAL5802_EXECUTION_AUTHORITY_SHA256": str(authority_sha256),
        "GOAL5802_RUNTIME_MANIFEST_SHA256": str(runtime_manifest_sha256),
        "GOAL5802_FREEZE_FILE_SHA256": preregistration_sha256,
        "GOAL5802_RUNTIME_PREFLIGHT_RECEIPT_PATH": str(preflight_path),
        "GOAL5802_RUNTIME_PREFLIGHT_RECEIPT_FILE_SHA256": (
            preflight_file_sha256
        ),
        "GOAL5802_RUNTIME_PREFLIGHT_SHA256": preflight_sha256,
        "GOAL5802_CONTROLLER_ENVELOPE_START_NS": str(time.perf_counter_ns()),
    })
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        input=_capability_frame(
            worker_id=args.worker_id,
            runtime_manifest_sha256=str(runtime_manifest_sha256),
            preflight_file_sha256=preflight_file_sha256,
            preflight_sha256=preflight_sha256,
        ),
        capture_output=True,
        check=False,
    )
    try:
        direct = strict_json_loads(
            completed.stdout,
            label="Goal5848 Direct stdout",
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError("Goal5848 Direct stdout is not JSON") from error
    if completed.returncode != 0 or completed.stderr or not isinstance(direct, dict):
        raise RuntimeError({
            "direct_exit_code": completed.returncode,
            "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
        })
    _validate_direct_receipt(direct, task=args.task, worker_id=args.worker_id)
    correctness = direct["correctness"]
    if not isinstance(correctness, Mapping):
        raise TypeError("Goal5848 Direct correctness evidence is absent")
    evidence = {
        "output_sha256": TASK_CONTRACTS[args.task]["public_output_sha256"],
        "public_output": (
            correctness["canonical_rows"]
            if args.task == RELATION_TASK
            else correctness["reduced_u64"]
        ),
        "source_compilation_inside_endpoint": False,
        "direct_worker_receipt": direct,
        "direct_stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
        "direct_stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
        "compatibility_preflight_file_sha256": preflight_file_sha256,
        "compatibility_preflight_sha256": preflight_sha256,
    }
    return identity, evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=(RELATION_TASK, TRIANGLE_TASK), required=True)
    parser.add_argument("--block", type=int, required=True)
    parser.add_argument("--worker-id", required=True)
    parser.add_argument(
        "--classification",
        choices=("exploration", "formal"),
        default="exploration",
    )
    parser.add_argument("--expected-source-commit")
    parser.add_argument("--direct-worker", type=Path, required=True)
    parser.add_argument("--direct-build-receipt", type=Path, required=True)
    parser.add_argument("--derivation-receipt", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--precompiled-ptx", type=Path, required=True)
    parser.add_argument("--compaction-cubin", type=Path)
    parser.add_argument("--support-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 0 <= args.block < BLOCKS:
        raise ValueError("Goal5848 Direct block differs")
    if args.task == RELATION_TASK and args.compaction_cubin is None:
        raise ValueError("Goal5848 Direct relation requires compaction cubin")
    source = _git_identity()
    if args.classification == "formal" and (
        source["clean"] is not True
        or source["commit"] != args.expected_source_commit
    ):
        raise RuntimeError("Goal5848 Direct formal source identity differs")
    identity, evidence = _run_direct(args)
    direct = evidence["direct_worker_receipt"]
    if not isinstance(direct, Mapping):
        raise TypeError("Goal5848 Direct worker receipt is absent")
    durations = direct["execute_or_regime_durations_ns"]
    if not isinstance(durations, list):
        raise TypeError("Goal5848 Direct duration samples are absent")
    result = {
        "schema": WORKER_SCHEMA,
        "status": "PASS__GOAL5848_WORKER",
        "arm": DIRECT_OPTIX_ARM,
        "task": args.task,
        "block": args.block,
        "worker_id": args.worker_id,
        "classification": args.classification,
        "warmups": STEADY_WARMUPS,
        "repetitions": STEADY_REPETITIONS,
        "python": "none__native_direct_optix",
        "source": source,
        "hardware": _hardware(),
        "measurements": {
            "implementation_import_ns": None,
            "implementation_entry_to_first_correct_result_ns": None,
            "implementation_import_to_endpoint_gap_ns": None,
            "post_import_to_first_correct_result_ns": None,
            "endpoint_partition_ns": None,
            "partition_reconciliation": None,
            "component_diagnostics_ns": {
                name: None for name in COMPONENT_DIAGNOSTIC_KEYS
            },
            "steady_complete_execution": _summary(durations),
            "identity": identity,
            "evidence": evidence,
        },
        "claim_boundary": {
            "exploration_or_formal_classification_owned_by_controller": True,
            "public_or_manuscript_claim_authorized": False,
            "external_review_complete": False,
        },
    }
    result["result_sha256"] = digest(result)
    _write_create(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
