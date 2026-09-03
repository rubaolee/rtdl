"""Create-only current-system three-arm baseline controller for Goal5842."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from .contracts import (
    BASELINE_ARMS,
    BASELINE_BLOCKS,
    BASELINE_CONTROLLER_SCHEMA,
    BASELINE_SUBWORKER_SCHEMA,
    BASELINE_TASKS,
    BOOTSTRAP_SEED_BASE,
    DIRECT_ARM,
    FIRST_MODE,
    PYOPTIX_ARM,
    RELATION_TASK,
    RTDL_ARM,
    STEADY_MODE,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    digest,
)
from .controller import bootstrap_interval, integer_median
from .runtime import (
    create_json,
    create_text,
    load_execution_authority,
    require_bound_path,
    require_idle_bound_gpu,
)
from .tasks import build_task

ROOT = Path(__file__).resolve().parents[2]
PHASE_KEYS = {
    "deterministic_input_materialization",
    "route_declaration_and_artifact_binding",
    "provider_projection_and_generic_family_admission",
    "runtime_target_and_toolchain_binding",
    "device_compile",
    "module_program_pipeline_sbt",
    "target_materialization",
    "native_prepare",
    "first_complete_execution",
    "steady_complete_execution",
    "close",
}


def validate_subworker_receipt(
    receipt: dict[str, Any],
    *,
    row: dict[str, Any],
    mode: str,
    authority: dict[str, Any],
) -> None:
    seal = receipt.get("receipt_sha256")
    unsealed = dict(receipt)
    unsealed.pop("receipt_sha256", None)
    if not isinstance(seal, str) or digest(unsealed) != seal:
        raise RuntimeError("baseline subworker receipt seal mismatch")
    expected = {
        "schema": BASELINE_SUBWORKER_SCHEMA,
        "status": "PASS",
        "schedule_worker_id": row["worker_id"],
        "subworker_id": f"{row['worker_id']}__{mode}",
        "task": row["task"],
        "arm": row["arm"],
        "block": row["block"],
        "mode": mode,
        "preregistration_sha256": authority["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "oracle_exact": True,
    }
    for key, expected_value in expected.items():
        if receipt.get(key) != expected_value:
            raise RuntimeError(f"baseline subworker receipt mismatch: {key}")
    for key in ("input_sha256", "output_sha256"):
        if not isinstance(receipt.get(key), str) or len(receipt[key]) != 64:
            raise RuntimeError(f"baseline subworker digest invalid: {key}")
    if not isinstance(receipt.get("identity"), dict) or not receipt["identity"]:
        raise RuntimeError("baseline subworker execution identity missing")
    phases = receipt.get("phases_ns")
    if not isinstance(phases, dict) or set(phases) != PHASE_KEYS:
        raise RuntimeError("baseline subworker phase schema mismatch")
    for key, value in phases.items():
        if key == "steady_complete_execution":
            if not isinstance(value, list) or any(
                type(item) is not int or item < 0 for item in value
            ):
                raise RuntimeError("baseline steady duration vector invalid")
        elif value is not None and (type(value) is not int or value < 0):
            raise RuntimeError(f"baseline phase duration invalid: {key}")
    if mode == FIRST_MODE:
        if (
            type(phases["first_complete_execution"]) is not int
            or phases["steady_complete_execution"] != []
        ):
            raise RuntimeError("baseline first-worker execution vector invalid")
    elif (
        phases["first_complete_execution"] is not None
        or len(phases["steady_complete_execution"]) != STEADY_REPETITIONS
    ):
        raise RuntimeError("baseline steady-worker execution vector invalid")
    expected_close = None if row["arm"] == DIRECT_ARM else int
    if expected_close is None:
        if phases["close"] is not None:
            raise RuntimeError("Direct subworker unexpectedly claims close timing")
    elif type(phases["close"]) is not expected_close:
        raise RuntimeError("Python baseline close timing missing")


def direct_command(
    args: argparse.Namespace,
    authority: dict[str, Any],
    row: dict[str, Any],
    mode: str,
) -> tuple[list[str], str]:
    direct_mode = "COLD_FRESH_PROCESS" if mode == FIRST_MODE else "PREPARED_EXECUTION"
    subworker_id = f"{row['worker_id']}__{mode}"
    ticket = hashlib.sha256(
        f"{authority['authority_sha256']}:{subworker_id}".encode("ascii")
    ).hexdigest()
    command = [
        str(args.direct_binary.resolve()),
        "--worker-id",
        subworker_id,
        "--task",
        row["task"],
        "--mode",
        direct_mode,
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
    ]
    return command, ticket


def parse_direct(
    raw: dict[str, Any],
    *,
    row: dict[str, Any],
    mode: str,
    ticket: str,
    authority: dict[str, Any],
) -> dict[str, object]:
    subworker_id = f"{row['worker_id']}__{mode}"
    direct_mode = "COLD_FRESH_PROCESS" if mode == FIRST_MODE else "PREPARED_EXECUTION"
    version_parts = [
        int(part) for part in authority["toolchain"]["optix_sdk"].split(".")
    ]
    version_parts.extend([0] * (3 - len(version_parts)))
    expected_header_version = (
        version_parts[0] * 10_000 + version_parts[1] * 100 + version_parts[2]
    )
    if (
        raw.get("schema") != "rtdl.goal5798.direct_raw_worker.v1"
        or raw.get("status") != "PASS"
        or raw.get("worker_id") != subworker_id
        or raw.get("task") != row["task"]
        or raw.get("mode") != direct_mode
        or raw.get("controller_ticket") != ticket
        or raw.get("freeze_sha256") != authority["preregistration_sha256"]
        or raw.get("optix_header_version") != expected_header_version
    ):
        raise RuntimeError("Direct subworker identity mismatch")
    task = build_task(row["task"])
    correctness = raw.get("correctness")
    if not isinstance(correctness, dict):
        raise TypeError("Direct correctness payload missing")
    if correctness.get("oracle_exact") is not True:
        raise RuntimeError("Direct worker did not report an exact oracle")
    if row["task"] == RELATION_TASK:
        output = tuple(
            tuple(int(item) for item in pair) for pair in correctness["canonical_rows"]
        )
        if output != task.expected_output:
            raise RuntimeError("Direct relation oracle mismatch")
        if (
            correctness.get("device_status") != 0
            or correctness.get("device_overflow") != 0
        ):
            raise RuntimeError("Direct relation device status failure")
        output_sha256 = digest(output)
    else:
        per_ray = tuple(int(item) for item in correctness["per_ray"])
        weighted = int(correctness["weighted_sum"])
        if (
            per_ray != task.expected_output["per_ray"]
            or weighted != task.expected_output["weighted_sum"]
        ):
            raise RuntimeError("Direct triangle oracle mismatch")
        if correctness.get("device_status") != 0:
            raise RuntimeError("Direct triangle device status failure")
        output_sha256 = digest(weighted)
    durations = raw.get("execute_durations_ns")
    if not isinstance(durations, list) or any(
        type(value) is not int or value < 0 for value in durations
    ):
        raise RuntimeError("Direct execution durations invalid")
    expected_count = 1 if mode == FIRST_MODE else STEADY_REPETITIONS
    if len(durations) != expected_count:
        raise RuntimeError("Direct execution duration count mismatch")
    old = raw.get("phase_durations_ns")
    expected_old_phases = {
        "deterministic_input_materialization",
        "protocol_validation_and_codegen",
        "device_compile",
        "module_program_pipeline_sbt",
        "gas_and_static_prepare",
        "common_preparation_total",
    }
    if not isinstance(old, dict) or set(old) != expected_old_phases:
        raise RuntimeError("Direct phase schema mismatch")
    if old["protocol_validation_and_codegen"] is not None or any(
        type(old[key]) is not int or old[key] < 0
        for key in expected_old_phases - {"protocol_validation_and_codegen"}
    ):
        raise RuntimeError("Direct phase duration invalid")
    device_compile = int(old["device_compile"])
    pipeline = int(old["module_program_pipeline_sbt"])
    phases = {
        "deterministic_input_materialization": int(
            old["deterministic_input_materialization"]
        ),
        "route_declaration_and_artifact_binding": None,
        "provider_projection_and_generic_family_admission": None,
        "runtime_target_and_toolchain_binding": None,
        "device_compile": device_compile,
        "module_program_pipeline_sbt": pipeline,
        "target_materialization": device_compile + pipeline,
        "native_prepare": int(old["gas_and_static_prepare"]),
        "first_complete_execution": durations[0] if mode == FIRST_MODE else None,
        "steady_complete_execution": durations if mode == STEADY_MODE else [],
        "close": None,
    }
    receipt: dict[str, object] = {
        "schema": BASELINE_SUBWORKER_SCHEMA,
        "status": "PASS",
        "schedule_worker_id": row["worker_id"],
        "subworker_id": subworker_id,
        "task": row["task"],
        "arm": row["arm"],
        "block": row["block"],
        "mode": mode,
        "preregistration_sha256": authority["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "input_sha256": task.input_sha256,
        "output_sha256": output_sha256,
        "oracle_exact": True,
        "phases_ns": phases,
        "identity": {
            "direct_binary_sha256": authority["execution_paths"][
                "direct_binary_sha256"
            ],
            "device_source_sha256": authority["execution_paths"][
                "device_source_sha256"
            ],
            "optix_header_version": raw["optix_header_version"],
        },
        "direct_close_phase_available": False,
    }
    receipt["receipt_sha256"] = digest(receipt)
    return receipt


def python_command(
    args: argparse.Namespace,
    row: dict[str, Any],
    mode: str,
    output: Path,
) -> list[str]:
    return [
        args.python,
        "-m",
        "experiments.goal5842_causal_admission.baseline_worker",
        "--preregistration",
        str(args.preregistration.resolve()),
        "--execution-authority",
        str(args.execution_authority.resolve()),
        "--schedule-worker-id",
        row["worker_id"],
        "--mode",
        mode,
        "--arm",
        row["arm"],
        "--native",
        str(args.native.resolve()),
        "--optix-include",
        str(args.optix_include.resolve()),
        "--cuda-include",
        str(args.cuda_include.resolve()),
        "--optix-sdk",
        args.optix_sdk,
        "--device-source",
        str(args.device_source.resolve()),
        "--output",
        str(output.resolve()),
    ]


def run_subworker(
    args: argparse.Namespace,
    authority: dict[str, Any],
    row: dict[str, Any],
    mode: str,
    directory: Path,
) -> tuple[dict[str, Any], int]:
    directory.mkdir(parents=False, exist_ok=False)
    output = directory / "receipt.json"
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(ROOT / "src"), str(ROOT), environment.get("PYTHONPATH", ""))
    )
    if row["arm"] == DIRECT_ARM:
        command, ticket = direct_command(args, authority, row, mode)
        environment["GOAL5798_FORMAL_CONTROLLER_PID"] = str(os.getpid())
    else:
        command = python_command(args, row, mode, output)
        ticket = ""
    create_json(
        directory / "command.json",
        {
            "schema": "rtdl.goal5842.baseline_command.v1",
            "schedule_worker_id": row["worker_id"],
            "mode": mode,
            "argv": command,
        },
    )
    started = time.perf_counter_ns()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    process_wall_ns = time.perf_counter_ns() - started
    create_text(directory / "stdout.txt", completed.stdout)
    create_text(directory / "stderr.txt", completed.stderr)
    if completed.returncode != 0:
        create_json(
            directory / "failure.json",
            {
                "schema": "rtdl.goal5842.baseline_failure.v1",
                "schedule_worker_id": row["worker_id"],
                "mode": mode,
                "returncode": completed.returncode,
                "retry_permitted": False,
            },
        )
        raise RuntimeError(
            f"formal baseline subworker failed: {row['worker_id']} {mode}"
        )
    if row["arm"] == DIRECT_ARM:
        raw = json.loads(completed.stdout)
        receipt = parse_direct(
            raw,
            row=row,
            mode=mode,
            ticket=ticket,
            authority=authority,
        )
        create_json(output, receipt)
    else:
        receipt = json.loads(output.read_text(encoding="utf-8"))
    validate_subworker_receipt(
        receipt,
        row=row,
        mode=mode,
        authority=authority,
    )
    return receipt, process_wall_ns


def combine_subworkers(
    first: dict[str, Any], steady: dict[str, Any], process_walls: list[int]
) -> dict[str, object]:
    for key in (
        "schedule_worker_id",
        "task",
        "arm",
        "block",
        "preregistration_sha256",
        "execution_authority_sha256",
        "input_sha256",
        "output_sha256",
        "identity",
    ):
        if first.get(key) != steady.get(key):
            raise RuntimeError(f"FIRST/STEADY baseline identity mismatch: {key}")
    first_phases = first["phases_ns"]
    steady_values = steady["phases_ns"]["steady_complete_execution"]
    if len(steady_values) != STEADY_REPETITIONS:
        raise RuntimeError(
            f"baseline steady vector is not {STEADY_REPETITIONS} samples"
        )
    setup_parts = (
        "route_declaration_and_artifact_binding",
        "provider_projection_and_generic_family_admission",
        "runtime_target_and_toolchain_binding",
        "target_materialization",
        "native_prepare",
    )
    setup_ns = sum(
        int(first_phases[key]) for key in setup_parts if first_phases[key] is not None
    )
    return {
        "schedule_worker_id": first["schedule_worker_id"],
        "task": first["task"],
        "arm": first["arm"],
        "block": first["block"],
        "input_sha256": first["input_sha256"],
        "output_sha256": first["output_sha256"],
        "identity": first["identity"],
        "first_phases_ns": first_phases,
        "steady_phases_ns": steady["phases_ns"],
        "deterministic_input_materialization_ns": first_phases[
            "deterministic_input_materialization"
        ],
        "setup_total_ns": setup_ns,
        "first_complete_execution_ns": first_phases["first_complete_execution"],
        "steady_complete_execution_median_ns": integer_median(steady_values),
        "close_ns": first_phases["close"],
        "process_wall_ns": process_walls,
        "oracle_exact": True,
    }


def summarize(composites: list[dict[str, Any]]) -> list[dict[str, object]]:
    summaries = []
    metrics = (
        "setup_total_ns",
        "first_complete_execution_ns",
        "steady_complete_execution_median_ns",
    )
    phase_names = (
        "deterministic_input_materialization",
        "route_declaration_and_artifact_binding",
        "provider_projection_and_generic_family_admission",
        "runtime_target_and_toolchain_binding",
        "device_compile",
        "module_program_pipeline_sbt",
        "target_materialization",
        "native_prepare",
        "close",
    )
    for task_index, task in enumerate(BASELINE_TASKS):
        task_rows = [row for row in composites if row["task"] == task]
        arms = {}
        for arm in BASELINE_ARMS:
            arm_rows = [row for row in task_rows if row["arm"] == arm]
            arms[arm] = {
                metric: integer_median([int(row[metric]) for row in arm_rows])
                for metric in metrics
            }
            arms[arm]["first_worker_phase_medians_ns"] = {
                phase: (
                    integer_median(
                        [
                            int(row["first_phases_ns"][phase])
                            for row in arm_rows
                            if row["first_phases_ns"][phase] is not None
                        ]
                    )
                    if any(
                        row["first_phases_ns"][phase] is not None for row in arm_rows
                    )
                    else None
                )
                for phase in phase_names
            }
            arms[arm]["worker_count"] = len(arm_rows)
        comparisons = []
        for comparison_index, denominator in enumerate((PYOPTIX_ARM, DIRECT_ARM)):
            for metric_index, metric in enumerate(metrics):
                ratios = []
                for block in range(BASELINE_BLOCKS):
                    numerator_row = next(
                        row
                        for row in task_rows
                        if row["block"] == block and row["arm"] == RTDL_ARM
                    )
                    denominator_row = next(
                        row
                        for row in task_rows
                        if row["block"] == block and row["arm"] == denominator
                    )
                    ratios.append(
                        int(numerator_row[metric]) / int(denominator_row[metric])
                    )
                scaled = [round(value * 1_000_000_000) for value in ratios]
                lower, upper = bootstrap_interval(
                    scaled,
                    seed=(
                        BOOTSTRAP_SEED_BASE
                        + 1000
                        + task_index * 100
                        + comparison_index * 10
                        + metric_index
                    ),
                )
                comparisons.append(
                    {
                        "numerator": RTDL_ARM,
                        "denominator": denominator,
                        "metric": metric,
                        "median_ratio": integer_median(scaled) / 1_000_000_000,
                        "bootstrap_95_percent_ratio": [
                            lower / 1_000_000_000,
                            upper / 1_000_000_000,
                        ],
                        "registered_gate": None,
                    }
                )
        summaries.append(
            {
                "task": task,
                "arm_medians_ns": arms,
                "comparisons": comparisons,
            }
        )
    return summaries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--direct-binary", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--device-source", type=Path, required=True)
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
        ("native_library", args.native),
        ("optix_include", args.optix_include),
        ("cuda_include", args.cuda_include),
    ):
        require_bound_path(authority, key, supplied)
    if args.optix_sdk != authority["toolchain"]["optix_sdk"]:
        raise RuntimeError("OptiX SDK argument differs from execution authority")
    if Path(args.python).resolve(strict=True) != Path(
        authority["host"]["python_executable"]
    ).resolve(strict=True):
        raise RuntimeError("baseline Python executable differs from authority")
    require_idle_bound_gpu(authority)
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=False)
    create_json(
        output_root / "transaction_start.json",
        {
            "schema": "rtdl.goal5842.baseline_transaction_start.v1",
            "status": "WORKER_ZERO_WILL_FOLLOW",
            "source_commit": authority["source_commit"],
            "preregistration_sha256": prereg["preregistration_sha256"],
            "execution_authority_sha256": authority["authority_sha256"],
            "formal_worker_retry": False,
            "formal_worker_drop": False,
        },
    )
    composites = []
    subworker_count = 0
    for index, row in enumerate(prereg["baseline_schedule"]):
        row_dir = output_root / f"{index:03d}_{row['worker_id']}"
        row_dir.mkdir(parents=False, exist_ok=False)
        first, first_wall = run_subworker(
            args, authority, row, FIRST_MODE, row_dir / "first"
        )
        steady, steady_wall = run_subworker(
            args, authority, row, STEADY_MODE, row_dir / "steady"
        )
        composites.append(combine_subworkers(first, steady, [first_wall, steady_wall]))
        subworker_count += 2
    for task in BASELINE_TASKS:
        task_rows = [row for row in composites if row["task"] == task]
        if len({row["input_sha256"] for row in task_rows}) != 1:
            raise RuntimeError(f"cross-arm input contract differs: {task}")
        if len({row["output_sha256"] for row in task_rows}) != 1:
            raise RuntimeError(f"cross-arm output contract differs: {task}")
    summaries = summarize(composites)
    result: dict[str, object] = {
        "schema": BASELINE_CONTROLLER_SCHEMA,
        "status": "PASS__TWO_TASK_THREE_ARM_BASELINE_COMPLETE",
        "source_commit": authority["source_commit"],
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "hardware": authority["hardware"],
        "composite_worker_count": len(composites),
        "subworker_count": subworker_count,
        "registered_subworker_timing_vector_count": subworker_count,
        "registered_execution_sample_count": len(composites) * (1 + STEADY_REPETITIONS),
        "unregistered_warmup_execution_count": len(composites) * STEADY_WARMUPS,
        "gpu_complete_execution_call_count": len(composites)
        * (1 + STEADY_WARMUPS + STEADY_REPETITIONS),
        "task_summaries": summaries,
        "composite_rows": composites,
        "cross_arm_input_output_contract_exact": True,
        "cross_arm_generated_artifact_identity_claimed": False,
        "direct_close_phase_available": False,
        "close_phase_comparable_across_all_arms": False,
        "registered_performance_gate": None,
        "external_review_or_consensus": False,
    }
    result["result_sha256"] = digest(result)
    create_json(output_root / "result.json", result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
