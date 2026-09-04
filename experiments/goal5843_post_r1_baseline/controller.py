"""Create-only formal three-arm controller for Goal5843."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
from typing import Any

from experiments.goal5842_causal_admission.tasks import build_task

from .contracts import (
    ARMS,
    BLOCKS,
    BOOTSTRAP_DRAWS,
    BOOTSTRAP_LOWER_INDEX,
    BOOTSTRAP_SEED_BASE,
    BOOTSTRAP_UPPER_INDEX,
    CONTROLLER_SCHEMA,
    DIRECT_ARM,
    FIRST_MODE,
    PHASE_KEYS,
    PYOPTIX_ARM,
    RELATION_TASK,
    RTDL_ARM,
    STEADY_MODE,
    STEADY_REPETITIONS,
    SUBWORKER_SCHEMA,
    TASK_CONTRACTS,
    TASKS,
    TRIANGLE_TASK,
    digest,
    task_contract,
)
from .runtime import (
    create_json,
    create_text,
    git_head,
    load_execution_authority,
    require_bound_path,
    require_idle_bound_gpu,
)


ROOT = Path(__file__).resolve().parents[2]


def integer_median(values: list[int]) -> int:
    if not values or any(type(value) is not int for value in values):
        raise ValueError("median requires nonempty integer vector")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) // 2


def bootstrap_interval(values: list[int], *, seed: int) -> list[int]:
    if len(values) != BLOCKS:
        raise ValueError("bootstrap requires one value per block")
    source = random.Random(seed)
    draws = []
    for _ in range(BOOTSTRAP_DRAWS):
        sample = [values[source.randrange(len(values))] for _ in values]
        draws.append(integer_median(sample))
    draws.sort()
    return [draws[BOOTSTRAP_LOWER_INDEX], draws[BOOTSTRAP_UPPER_INDEX]]


def _direct_command(
    args: argparse.Namespace,
    authority: dict[str, Any],
    row: dict[str, Any],
    mode: str,
) -> tuple[list[str], str]:
    direct_mode = "COLD_FRESH_PROCESS" if mode == FIRST_MODE else "PREPARED_EXECUTION"
    subworker_id = f"{row['worker_id']}__{mode}"
    ticket = hashlib.sha256(
        f"goal5843:{authority['authority_sha256']}:{subworker_id}".encode("ascii")
    ).hexdigest()
    return [
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
        "--measurement-contract",
        "GOAL5842_PUBLIC_OUTPUT_V1",
    ], ticket


def _parse_direct(
    raw: dict[str, Any],
    *,
    row: dict[str, Any],
    mode: str,
    ticket: str,
    authority: dict[str, Any],
    prereg: dict[str, Any],
) -> dict[str, object]:
    subworker_id = f"{row['worker_id']}__{mode}"
    direct_mode = "COLD_FRESH_PROCESS" if mode == FIRST_MODE else "PREPARED_EXECUTION"
    version = [int(part) for part in authority["toolchain"]["optix_sdk"].split(".")]
    version.extend([0] * (3 - len(version)))
    expected_header = version[0] * 10_000 + version[1] * 100 + version[2]
    exact = {
        "schema": "rtdl.goal5842.direct_public_output_raw.v1",
        "status": "PASS",
        "worker_id": subworker_id,
        "task": row["task"],
        "mode": direct_mode,
        "controller_ticket": ticket,
        "freeze_sha256": authority["preregistration_sha256"],
        "optix_header_version": expected_header,
        "measurement_contract": "GOAL5842_PUBLIC_OUTPUT_V1",
        "oracle_validation_outside_execute_durations": True,
    }
    for key, expected in exact.items():
        if raw.get(key) != expected:
            raise RuntimeError(f"Direct inherited transport mismatch: {key}")
    task = build_task(row["task"])
    contract = task_contract(prereg, row["task"])
    if task.input_sha256 != contract["input_sha256"]:
        raise RuntimeError("Direct task input differs from preregistration")
    correctness = raw.get("correctness")
    if not isinstance(correctness, dict) or correctness.get(
        "public_output_oracle_exact"
    ) is not True:
        raise RuntimeError("Direct public correctness payload missing")
    if correctness.get("public_output_contract_id") != contract[
        "public_output_contract_id"
    ]:
        raise RuntimeError("Direct public output contract mismatch")
    if row["task"] == RELATION_TASK:
        output = tuple(
            tuple(int(item) for item in pair) for pair in correctness["canonical_rows"]
        )
        if (
            output != task.expected_output
            or correctness.get("device_status") != 0
            or correctness.get("device_overflow") != 0
        ):
            raise RuntimeError("Direct relation oracle/status mismatch")
        output_sha = digest(output)
        launch_count = 2
    else:
        weighted = int(correctness["weighted_sum"])
        if weighted != task.expected_output["weighted_sum"] or correctness.get(
            "device_status"
        ) != 0:
            raise RuntimeError("Direct triangle oracle/status mismatch")
        output_sha = digest(weighted)
        launch_count = 1
    if output_sha != contract["public_output_sha256"]:
        raise RuntimeError("Direct output digest differs from preregistration")
    durations = raw.get("execute_durations_ns")
    if not isinstance(durations, list) or any(
        type(value) is not int or value < 0 for value in durations
    ):
        raise RuntimeError("Direct durations invalid")
    if len(durations) != (1 if mode == FIRST_MODE else STEADY_REPETITIONS):
        raise RuntimeError("Direct duration count mismatch")
    old = raw.get("phase_durations_ns")
    old_keys = {
        "deterministic_input_materialization",
        "protocol_validation_and_codegen",
        "device_compile",
        "module_program_pipeline_sbt",
        "gas_and_static_prepare",
        "common_preparation_total",
    }
    if not isinstance(old, dict) or set(old) != old_keys:
        raise RuntimeError("Direct phase schema mismatch")
    if old["protocol_validation_and_codegen"] is not None or any(
        type(old[key]) is not int or old[key] < 0
        for key in old_keys - {"protocol_validation_and_codegen"}
    ):
        raise RuntimeError("Direct phase value invalid")
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
        "schema": SUBWORKER_SCHEMA,
        "status": "PASS",
        "schedule_worker_id": row["worker_id"],
        "subworker_id": subworker_id,
        "task": row["task"],
        "arm": row["arm"],
        "block": row["block"],
        "mode": mode,
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "input_sha256": task.input_sha256,
        "output_sha256": output_sha,
        "public_output_contract_id": contract["public_output_contract_id"],
        "public_output_oracle_exact": True,
        "oracle_validation_outside_registered_interval": True,
        "independent_oracle_witness_sha256": authority[
            "independent_oracle_witness"
        ]["witness_sha256"],
        "phases_ns": phases,
        "identity": {
            "direct_binary_sha256": authority["execution_paths"][
                "direct_binary_sha256"
            ],
            "device_source_sha256": authority["execution_paths"][
                "device_source_sha256"
            ],
            "optix_header_version": expected_header,
            "inherited_transport_schema": raw["schema"],
        },
        "latest_execution_boundary": {
            "schema": "rtdl.goal5843.inherited_direct_execution_boundary.v1",
            "static_and_query_inputs_uploaded_during_prepare": True,
            "execute_reuploads_static_or_query_inputs": False,
            "same_prepared_owner_reused_across_steady_samples": mode == STEADY_MODE,
            "gpu_completion_before_timer_stop": True,
            "public_output_scope": contract["public_output_scope"],
            "optix_launch_count": launch_count,
            "source_audit_not_hardware_counter": True,
        },
    }
    receipt["receipt_sha256"] = digest(receipt)
    return receipt


def _python_command(
    args: argparse.Namespace, row: dict[str, Any], mode: str, output: Path
) -> list[str]:
    return [
        args.python,
        "-m",
        "experiments.goal5843_post_r1_baseline.worker",
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


def validate_receipt(
    receipt: dict[str, Any],
    *,
    row: dict[str, Any],
    mode: str,
    authority: dict[str, Any],
    prereg: dict[str, Any],
) -> None:
    observed = receipt.get("receipt_sha256")
    unsealed = dict(receipt)
    unsealed.pop("receipt_sha256", None)
    if not isinstance(observed, str) or digest(unsealed) != observed:
        raise RuntimeError("subworker receipt seal mismatch")
    contract = task_contract(prereg, row["task"])
    exact = {
        "schema": SUBWORKER_SCHEMA,
        "status": "PASS",
        "schedule_worker_id": row["worker_id"],
        "subworker_id": f"{row['worker_id']}__{mode}",
        "task": row["task"],
        "arm": row["arm"],
        "block": row["block"],
        "mode": mode,
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "input_sha256": contract["input_sha256"],
        "output_sha256": contract["public_output_sha256"],
        "public_output_contract_id": contract["public_output_contract_id"],
        "public_output_oracle_exact": True,
        "oracle_validation_outside_registered_interval": True,
        "independent_oracle_witness_sha256": authority[
            "independent_oracle_witness"
        ]["witness_sha256"],
    }
    for key, expected in exact.items():
        if receipt.get(key) != expected:
            raise RuntimeError(f"subworker receipt mismatch: {key}")
    phases = receipt.get("phases_ns")
    if not isinstance(phases, dict) or set(phases) != set(PHASE_KEYS):
        raise RuntimeError("subworker phase schema mismatch")
    for key, value in phases.items():
        if key == "steady_complete_execution":
            if not isinstance(value, list) or any(
                type(item) is not int or item < 0 for item in value
            ):
                raise RuntimeError("steady duration vector invalid")
        elif value is not None and (type(value) is not int or value < 0):
            raise RuntimeError(f"phase duration invalid: {key}")
    if mode == FIRST_MODE:
        if (
            type(phases["first_complete_execution"]) is not int
            or phases["steady_complete_execution"] != []
        ):
            raise RuntimeError("FIRST execution vector invalid")
    elif (
        phases["first_complete_execution"] is not None
        or len(phases["steady_complete_execution"]) != STEADY_REPETITIONS
    ):
        raise RuntimeError("STEADY execution vector invalid")
    if not isinstance(receipt.get("identity"), dict) or not receipt["identity"]:
        raise RuntimeError("subworker identity missing")
    if not isinstance(receipt.get("latest_execution_boundary"), dict):
        raise RuntimeError("subworker execution boundary missing")
    if row["arm"] == RTDL_ARM and row["task"] == TRIANGLE_TASK:
        boundary = receipt["latest_execution_boundary"]
        if boundary.get("prepared_query_input_reused") is not (mode == STEADY_MODE):
            raise RuntimeError("controller rejected RTDL prepared-query reuse")
        gate = prereg["rtdl_triangle_receipt_gate"]
        if boundary.get("execution_path") != gate["execution_path"]:
            raise RuntimeError("controller rejected RTDL scalar execution path")


def _run_subworker(
    args: argparse.Namespace,
    authority: dict[str, Any],
    prereg: dict[str, Any],
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
    for name in (
        "RTDL_V4_FORMAL_LEAF_CACHE",
        "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST",
        "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256",
    ):
        environment.pop(name, None)
    if row["arm"] == DIRECT_ARM:
        command, ticket = _direct_command(args, authority, row, mode)
        environment["GOAL5798_FORMAL_CONTROLLER_PID"] = str(os.getpid())
    else:
        command = _python_command(args, row, mode, output)
        ticket = ""
    create_json(
        directory / "command.json",
        {
            "schema": "rtdl.goal5843.baseline_command.v1",
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
    wall_ns = time.perf_counter_ns() - started
    create_text(directory / "stdout.txt", completed.stdout)
    create_text(directory / "stderr.txt", completed.stderr)
    create_json(
        directory / "controller_observation.json",
        {
            "schema": "rtdl.goal5843.controller_subworker_observation.v1",
            "schedule_worker_id": row["worker_id"],
            "mode": mode,
            "returncode": completed.returncode,
            "process_wall_ns": wall_ns,
        },
    )
    if completed.returncode != 0:
        create_json(
            directory / "failure.json",
            {
                "schema": "rtdl.goal5843.baseline_failure.v1",
                "schedule_worker_id": row["worker_id"],
                "mode": mode,
                "returncode": completed.returncode,
                "retry_permitted": False,
            },
        )
        raise RuntimeError(f"formal subworker failed: {row['worker_id']} {mode}")
    if row["arm"] == DIRECT_ARM:
        receipt = _parse_direct(
            json.loads(completed.stdout),
            row=row,
            mode=mode,
            ticket=ticket,
            authority=authority,
            prereg=prereg,
        )
        create_json(output, receipt)
    else:
        receipt = json.loads(output.read_text(encoding="utf-8"))
    validate_receipt(
        receipt, row=row, mode=mode, authority=authority, prereg=prereg
    )
    return receipt, wall_ns


def combine_subworkers(
    first: dict[str, Any], steady: dict[str, Any], walls: list[int]
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
        "public_output_contract_id",
        "public_output_oracle_exact",
        "oracle_validation_outside_registered_interval",
        "independent_oracle_witness_sha256",
        "identity",
    ):
        if first.get(key) != steady.get(key):
            raise RuntimeError(f"FIRST/STEADY identity mismatch: {key}")
    first_phases = first["phases_ns"]
    steady_values = steady["phases_ns"]["steady_complete_execution"]
    setup_parts = (
        "route_declaration_and_artifact_binding",
        "provider_projection_and_generic_family_admission",
        "runtime_target_and_toolchain_binding",
        "target_materialization",
        "native_prepare",
    )
    return {
        "schedule_worker_id": first["schedule_worker_id"],
        "task": first["task"],
        "arm": first["arm"],
        "block": first["block"],
        "input_sha256": first["input_sha256"],
        "output_sha256": first["output_sha256"],
        "public_output_contract_id": first["public_output_contract_id"],
        "identity": first["identity"],
        "first_execution_boundary": first["latest_execution_boundary"],
        "steady_execution_boundary": steady["latest_execution_boundary"],
        "first_phases_ns": first_phases,
        "steady_phases_ns": steady["phases_ns"],
        "deterministic_input_materialization_ns": first_phases[
            "deterministic_input_materialization"
        ],
        "setup_total_ns": sum(
            int(first_phases[key])
            for key in setup_parts
            if first_phases[key] is not None
        ),
        "first_complete_execution_ns": first_phases["first_complete_execution"],
        "steady_complete_execution_median_ns": integer_median(steady_values),
        "close_ns": first_phases["close"],
        "process_wall_ns": walls,
        "public_output_oracle_exact": True,
        "oracle_validation_outside_registered_interval": True,
        "independent_oracle_witness_sha256": first[
            "independent_oracle_witness_sha256"
        ],
    }


def summarize(composites: list[dict[str, Any]]) -> list[dict[str, object]]:
    metrics = (
        "setup_total_ns",
        "first_complete_execution_ns",
        "steady_complete_execution_median_ns",
    )
    phase_names = tuple(key for key in PHASE_KEYS if "execution" not in key)
    summaries = []
    for task_index, task in enumerate(TASKS):
        rows = [row for row in composites if row["task"] == task]
        arm_medians: dict[str, object] = {}
        for arm in ARMS:
            arm_rows = [row for row in rows if row["arm"] == arm]
            arm_summary: dict[str, object] = {
                metric: integer_median([int(row[metric]) for row in arm_rows])
                for metric in metrics
            }
            arm_summary["first_worker_phase_medians_ns"] = {
                phase: (
                    integer_median(
                        [
                            int(row["first_phases_ns"][phase])
                            for row in arm_rows
                            if row["first_phases_ns"][phase] is not None
                        ]
                    )
                    if any(
                        row["first_phases_ns"][phase] is not None
                        for row in arm_rows
                    )
                    else None
                )
                for phase in phase_names
            }
            arm_summary["worker_count"] = len(arm_rows)
            arm_medians[arm] = arm_summary
        comparisons = []
        for comparison_index, denominator in enumerate((DIRECT_ARM, PYOPTIX_ARM)):
            for metric_index, metric in enumerate(metrics):
                scaled_ratios = []
                for block in range(BLOCKS):
                    numerator_row = next(
                        row
                        for row in rows
                        if row["block"] == block and row["arm"] == RTDL_ARM
                    )
                    denominator_row = next(
                        row
                        for row in rows
                        if row["block"] == block and row["arm"] == denominator
                    )
                    denominator_value = int(denominator_row[metric])
                    if denominator_value <= 0:
                        raise RuntimeError("comparison denominator is not positive")
                    scaled_ratios.append(
                        round(int(numerator_row[metric]) / denominator_value * 1_000_000_000)
                    )
                interval = bootstrap_interval(
                    scaled_ratios,
                    seed=(
                        BOOTSTRAP_SEED_BASE
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
                        "within_block_scaled_ratios_1e9": scaled_ratios,
                        "median_ratio": integer_median(scaled_ratios) / 1_000_000_000,
                        "bootstrap_95_percent_ratio": [
                            interval[0] / 1_000_000_000,
                            interval[1] / 1_000_000_000,
                        ],
                        "registered_gate": None,
                    }
                )
        summaries.append(
            {
                "task": task,
                "task_role": task_contract_from_rows(task)["role"],
                "arm_medians_ns": arm_medians,
                "comparisons": comparisons,
            }
        )
    return summaries


def task_contract_from_rows(task: str) -> dict[str, object]:
    rows = [row for row in TASK_CONTRACTS if row["task"] == task]
    if len(rows) != 1:
        raise RuntimeError("compiled task contract not unique")
    return rows[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--direct-binary", type=Path, required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    args = parser.parse_args()
    prereg, authority = load_execution_authority(
        args.execution_authority,
        preregistration_path=args.preregistration,
        root=ROOT,
        require_clean_repository=True,
    )
    for key, supplied in (
        ("native_library", args.native),
        ("direct_binary", args.direct_binary),
        ("device_source", args.device_source),
        ("optix_include", args.optix_include),
        ("cuda_include", args.cuda_include),
    ):
        require_bound_path(authority, key, supplied)
    if args.optix_sdk != authority["toolchain"]["optix_sdk"]:
        raise RuntimeError("controller OptiX SDK differs from authority")
    if Path(args.python).resolve(strict=True) != Path(
        authority["host"]["python_executable"]
    ).resolve(strict=True):
        raise RuntimeError("controller Python differs from authority")
    require_idle_bound_gpu(authority)
    output_root = args.output_root.absolute()
    output_root.mkdir(parents=True, exist_ok=False)
    create_json(
        output_root / "WORKER_ZERO.json",
        {
            "schema": "rtdl.goal5843.worker_zero.v1",
            "source_commit": git_head(ROOT),
            "preregistration_sha256": prereg["preregistration_sha256"],
            "execution_authority_sha256": authority["authority_sha256"],
            "post_worker_zero_retry_permitted": False,
            "unix_time_ns": time.time_ns(),
        },
    )
    composites = []
    for index, row_value in enumerate(prereg["schedule"]):
        row = dict(row_value)
        print(
            f"Goal5843 {index + 1}/{len(prereg['schedule'])}: {row['worker_id']}",
            file=sys.stderr,
            flush=True,
        )
        directory = output_root / f"{index:03d}_{row['worker_id']}"
        directory.mkdir(parents=False, exist_ok=False)
        first, first_wall = _run_subworker(
            args, authority, prereg, row, FIRST_MODE, directory / "first"
        )
        steady, steady_wall = _run_subworker(
            args, authority, prereg, row, STEADY_MODE, directory / "steady"
        )
        composites.append(
            combine_subworkers(first, steady, [first_wall, steady_wall])
        )
    result: dict[str, object] = {
        "schema": CONTROLLER_SCHEMA,
        "status": "PASS__ALL_PREREGISTERED_ROWS_RETAINED",
        "source_commit": git_head(ROOT),
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "hardware": authority["hardware"],
        "composite_count": len(composites),
        "subworker_receipt_count": len(composites) * len((FIRST_MODE, STEADY_MODE)),
        "composites": composites,
        "task_summaries": summarize(composites),
        "all_adverse_rows_retained": True,
        "registered_performance_success_threshold": None,
        "public_performance_claim_authorized": False,
        "manuscript_performance_claim_authorized": False,
        "external_review_or_consensus_complete": False,
    }
    result["result_sha256"] = digest(result)
    create_json(output_root / "RESULT.json", result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
