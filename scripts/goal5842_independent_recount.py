#!/usr/bin/env python3
"""Independently recount one Goal5842 hardware-generation transaction."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from experiments.goal5842_causal_admission.contracts import (
    ADMISSION_TASKS,
    BASELINE_ARMS,
    BASELINE_BLOCKS,
    BASELINE_CONTROLLER_SCHEMA,
    BASELINE_SUBWORKER_SCHEMA,
    BASELINE_TASKS,
    BOOTSTRAP_DRAWS,
    BOOTSTRAP_LOWER_INDEX,
    BOOTSTRAP_SEED_BASE,
    BOOTSTRAP_UPPER_INDEX,
    CAUSAL_BLOCKS,
    CHECK_OFF,
    CHECK_ON,
    CONTROLLER_RESULT_SCHEMA,
    DIRECT_ARM,
    EXECUTION_AUTHORITY_SCHEMA,
    FIRST_MODE,
    GPU_IDENTITY_WITNESS_SCHEMA,
    INDEPENDENT_RECOUNT_SCHEMA,
    PYOPTIX_ARM,
    RTDL_ARM,
    STEADY_MODE,
    STEADY_REPETITIONS,
    WORKER_RECEIPT_SCHEMA,
    digest,
    load_preregistration,
    sha256_file,
)

ROOT = Path(__file__).resolve().parents[1]
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
ROUTE_PHASE = "route_declaration_and_artifact_binding"
CAUSAL_PHASE = "provider_projection_and_public_admission_or_unchecked_construction"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON object required: {path}")
    return value


def verify_seal(value: dict[str, Any], field: str, label: str) -> None:
    observed = value.get(field)
    unsealed = dict(value)
    unsealed.pop(field, None)
    require(
        isinstance(observed, str) and digest(unsealed) == observed,
        f"{label} seal mismatch",
    )


def integer_median(values: list[int]) -> int:
    require(
        bool(values) and all(type(value) is int for value in values),
        "invalid median vector",
    )
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) // 2


def bootstrap(values: list[int], seed: int) -> list[int]:
    require(len(values) == CAUSAL_BLOCKS, "bootstrap block count mismatch")
    source = random.Random(seed)
    draws = []
    for _ in range(BOOTSTRAP_DRAWS):
        sample = [values[source.randrange(len(values))] for _ in values]
        draws.append(integer_median(sample))
    draws.sort()
    return [draws[BOOTSTRAP_LOWER_INDEX], draws[BOOTSTRAP_UPPER_INDEX]]


def evidence_manifest(root: Path) -> list[dict[str, object]]:
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rows.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    require(bool(rows), f"empty evidence root: {root}")
    return rows


def validate_authority(
    authority: dict[str, Any], prereg: dict[str, Any], prereg_path: Path
) -> None:
    verify_seal(authority, "authority_sha256", "execution authority")
    require(
        authority.get("schema") == EXECUTION_AUTHORITY_SCHEMA,
        "authority schema mismatch",
    )
    require(
        authority.get("status") == "AUTHORIZED_FOR_FORMAL_WORKER_ZERO",
        "authority status mismatch",
    )
    require(
        authority.get("preregistration_sha256") == prereg["preregistration_sha256"],
        "authority/preregistration mismatch",
    )
    require(
        authority.get("repository_status_short") == [], "authority repository was dirty"
    )
    require(
        isinstance(authority.get("source_commit"), str)
        and len(authority["source_commit"]) == 40,
        "authority source commit invalid",
    )
    require(
        authority.get("registered_timing_observation_count") == 0,
        "authority observed timing",
    )
    require(authority.get("gpu_execution_count") == 0, "authority executed GPU work")
    require(
        authority.get("preregistration_file_sha256") == sha256_file(prereg_path),
        "authority preregistration file identity mismatch",
    )


def causal_summary(receipts: list[dict[str, Any]]) -> list[dict[str, object]]:
    summaries = []
    for task_index, task in enumerate(ADMISSION_TASKS):
        task_rows = [row for row in receipts if row["task"] == task]
        blocks = []
        for block in range(CAUSAL_BLOCKS):
            rows = [row for row in task_rows if row["block"] == block]
            on_rows = [row for row in rows if row["arm"] == CHECK_ON]
            off_rows = [row for row in rows if row["arm"] == CHECK_OFF]
            require(
                len(on_rows) == 2 and len(off_rows) == 2,
                f"incomplete causal block {task}/{block}",
            )
            on_causal = integer_median(
                [int(row["phases_ns"][CAUSAL_PHASE]) for row in on_rows]
            )
            off_causal = integer_median(
                [int(row["phases_ns"][CAUSAL_PHASE]) for row in off_rows]
            )
            on_route = integer_median(
                [int(row["phases_ns"][ROUTE_PHASE]) for row in on_rows]
            )
            off_route = integer_median(
                [int(row["phases_ns"][ROUTE_PHASE]) for row in off_rows]
            )
            on_total = integer_median(
                [int(row["registered_admission_total_ns"]) for row in on_rows]
            )
            off_total = integer_median(
                [int(row["registered_admission_total_ns"]) for row in off_rows]
            )
            blocks.append(
                {
                    "block": block,
                    "check_on_causal_phase_median_ns": on_causal,
                    "check_off_causal_phase_median_ns": off_causal,
                    "causal_phase_on_minus_off_ns": on_causal - off_causal,
                    "route_declaration_on_minus_off_ns": on_route - off_route,
                    "total_capability_on_minus_off_ns": on_total - off_total,
                }
            )
        causal_deltas = [int(row["causal_phase_on_minus_off_ns"]) for row in blocks]
        total_deltas = [int(row["total_capability_on_minus_off_ns"]) for row in blocks]
        summaries.append(
            {
                "task": task,
                "worker_count": len(task_rows),
                "block_count": len(blocks),
                "check_on_causal_phase_median_ns": integer_median(
                    [
                        int(row["phases_ns"][CAUSAL_PHASE])
                        for row in task_rows
                        if row["arm"] == CHECK_ON
                    ]
                ),
                "check_off_causal_phase_median_ns": integer_median(
                    [
                        int(row["phases_ns"][CAUSAL_PHASE])
                        for row in task_rows
                        if row["arm"] == CHECK_OFF
                    ]
                ),
                "primary_causal_phase_delta_median_ns": integer_median(causal_deltas),
                "primary_causal_phase_delta_bootstrap_95_percent_ns": bootstrap(
                    causal_deltas, BOOTSTRAP_SEED_BASE + task_index
                ),
                "route_declaration_negative_control_delta_median_ns": integer_median(
                    [int(row["route_declaration_on_minus_off_ns"]) for row in blocks]
                ),
                "secondary_total_capability_delta_median_ns": integer_median(
                    total_deltas
                ),
                "secondary_total_capability_delta_bootstrap_95_percent_ns": bootstrap(
                    total_deltas, BOOTSTRAP_SEED_BASE + 100 + task_index
                ),
                "block_rows": blocks,
                "ratio_to_check_off_reported": False,
            }
        )
    return summaries


def recount_causal(
    root: Path, prereg: dict[str, Any], authority: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    result = read_json(root / "result.json")
    verify_seal(result, "result_sha256", "causal controller result")
    require(
        result.get("schema") == CONTROLLER_RESULT_SCHEMA,
        "causal result schema mismatch",
    )
    require(
        result.get("status") == "PASS__CAUSAL_ADMISSION_COHORT_COMPLETE",
        "causal result status mismatch",
    )
    require(
        result.get("source_commit") == authority["source_commit"],
        "causal source commit mismatch",
    )
    require(
        result.get("preregistration_sha256") == prereg["preregistration_sha256"],
        "causal result preregistration mismatch",
    )
    require(
        result.get("execution_authority_sha256") == authority["authority_sha256"],
        "causal result authority mismatch",
    )
    require(
        result.get("hardware") == authority["hardware"],
        "causal result hardware mismatch",
    )
    require(
        result.get("normal_reference_admission_after_estimand") is True,
        "causal result timing boundary missing",
    )
    receipts = []
    frozen_tasks = {row["task"]: row for row in prereg["task_contracts"]}
    task_signatures: dict[str, object] = {}
    task_inputs: dict[str, str] = {}
    for index, scheduled in enumerate(prereg["causal_schedule"]):
        path = root / f"{index:03d}_{scheduled['worker_id']}" / "receipt.json"
        receipt = read_json(path)
        verify_seal(
            receipt, "receipt_sha256", f"causal receipt {scheduled['worker_id']}"
        )
        require(
            receipt.get("schema") == WORKER_RECEIPT_SCHEMA,
            "causal receipt schema mismatch",
        )
        for key in (
            "worker_id",
            "task",
            "arm",
            "block",
            "position",
            "arm_sample_index",
        ):
            require(
                receipt.get(key) == scheduled[key], f"causal schedule mismatch: {key}"
            )
        require(
            receipt.get("preregistration_sha256") == prereg["preregistration_sha256"],
            "causal preregistration mismatch",
        )
        require(
            receipt.get("execution_authority_sha256") == authority["authority_sha256"],
            "causal authority mismatch",
        )
        phases = receipt.get("phases_ns")
        require(
            isinstance(phases, dict)
            and set(phases)
            == {
                "route_declaration_and_artifact_binding",
                "provider_projection_and_public_admission_or_unchecked_construction",
            },
            "causal phase schema mismatch",
        )
        require(
            all(type(value) is int and value >= 0 for value in phases.values()),
            "causal phase value invalid",
        )
        require(
            receipt.get("registered_admission_total_ns") == sum(phases.values()),
            "causal total mismatch",
        )
        require(
            receipt.get("program_signature")
            == receipt.get("post_estimand_public_admission_signature"),
            "causal program identity mismatch",
        )
        require(
            receipt.get("normal_reference_admission_after_estimand") is True,
            "causal reference admission timing boundary missing",
        )
        require(
            receipt.get("garbage_collector_disabled_during_registered_phases") is True,
            "causal garbage-collector boundary missing",
        )
        require(receipt.get("clock") == "time.perf_counter_ns", "causal clock mismatch")
        require(
            receipt.get("gpu_imported_or_executed") is False, "causal worker used GPU"
        )
        task = str(receipt["task"])
        signature = receipt["program_signature"]
        input_sha = receipt.get("input_sha256")
        require(isinstance(input_sha, str), "causal input digest missing")
        require(
            input_sha == frozen_tasks[task]["input_sha256"],
            "causal input differs from preregistered task",
        )
        if task in task_signatures:
            require(
                task_signatures[task] == signature, "causal cross-worker program drift"
            )
            require(task_inputs[task] == input_sha, "causal cross-worker input drift")
        else:
            task_signatures[task] = signature
            task_inputs[task] = input_sha
        receipts.append(receipt)
    recomputed = causal_summary(receipts)
    require(
        result.get("task_summaries") == recomputed,
        "causal controller summary differs from recount",
    )
    require(
        result.get("worker_count") == len(prereg["causal_schedule"]),
        "causal worker count mismatch",
    )
    return result, receipts


def validate_baseline_receipt(
    receipt: dict[str, Any],
    scheduled: dict[str, Any],
    mode: str,
    prereg: dict[str, Any],
    authority: dict[str, Any],
) -> None:
    verify_seal(
        receipt, "receipt_sha256", f"baseline receipt {scheduled['worker_id']}/{mode}"
    )
    require(
        receipt.get("schema") == BASELINE_SUBWORKER_SCHEMA,
        "baseline receipt schema mismatch",
    )
    for key in ("task", "arm", "block"):
        require(
            receipt.get(key) == scheduled[key], f"baseline schedule mismatch: {key}"
        )
    require(
        receipt.get("schedule_worker_id") == scheduled["worker_id"],
        "baseline worker id mismatch",
    )
    require(
        receipt.get("subworker_id") == f"{scheduled['worker_id']}__{mode}",
        "baseline subworker id mismatch",
    )
    require(receipt.get("mode") == mode, "baseline mode mismatch")
    require(
        receipt.get("preregistration_sha256") == prereg["preregistration_sha256"],
        "baseline preregistration mismatch",
    )
    require(
        receipt.get("execution_authority_sha256") == authority["authority_sha256"],
        "baseline authority mismatch",
    )
    require(receipt.get("oracle_exact") is True, "baseline oracle did not pass")
    frozen_task = next(
        row for row in prereg["task_contracts"] if row["task"] == scheduled["task"]
    )
    require(
        receipt.get("input_sha256") == frozen_task["input_sha256"],
        "baseline input differs from preregistered task",
    )
    require(
        receipt.get("output_sha256") == frozen_task["public_output_sha256"],
        "baseline output differs from preregistered task",
    )
    phases = receipt.get("phases_ns")
    require(
        isinstance(phases, dict) and set(phases) == PHASE_KEYS,
        "baseline phase schema mismatch",
    )
    for key, value in phases.items():
        if key == "steady_complete_execution":
            require(
                isinstance(value, list)
                and all(type(item) is int and item >= 0 for item in value),
                "baseline steady vector invalid",
            )
        else:
            require(
                value is None or (type(value) is int and value >= 0),
                f"baseline phase invalid: {key}",
            )
    if mode == FIRST_MODE:
        require(
            type(phases["first_complete_execution"]) is int,
            "baseline first sample missing",
        )
        require(
            phases["steady_complete_execution"] == [],
            "first worker contains steady samples",
        )
    else:
        require(
            phases["first_complete_execution"] is None,
            "steady worker contains first sample",
        )
        require(
            len(phases["steady_complete_execution"]) == STEADY_REPETITIONS,
            "steady sample count mismatch",
        )
    if scheduled["arm"] == DIRECT_ARM:
        require(phases["close"] is None, "Direct unexpectedly claims a close phase")
    else:
        require(type(phases["close"]) is int, "Python arm close phase missing")


def combine_baseline(
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
        require(
            first.get(key) == steady.get(key), f"baseline FIRST/STEADY drift: {key}"
        )
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
        "identity": first["identity"],
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
        "process_wall_ns": process_walls,
        "oracle_exact": True,
    }


def baseline_summary(composites: list[dict[str, Any]]) -> list[dict[str, object]]:
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
        arms: dict[str, object] = {}
        for arm in BASELINE_ARMS:
            arm_rows = [row for row in task_rows if row["arm"] == arm]
            summary: dict[str, object] = {
                metric: integer_median([int(row[metric]) for row in arm_rows])
                for metric in metrics
            }
            summary["first_worker_phase_medians_ns"] = {
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
            summary["worker_count"] = len(arm_rows)
            arms[arm] = summary
        comparisons = []
        for comparison_index, denominator in enumerate((PYOPTIX_ARM, DIRECT_ARM)):
            for metric_index, metric in enumerate(metrics):
                ratios = []
                for block in range(BASELINE_BLOCKS):
                    numerator = next(
                        row
                        for row in task_rows
                        if row["block"] == block and row["arm"] == RTDL_ARM
                    )
                    baseline = next(
                        row
                        for row in task_rows
                        if row["block"] == block and row["arm"] == denominator
                    )
                    require(int(baseline[metric]) > 0, "zero baseline denominator")
                    ratios.append(
                        round(
                            int(numerator[metric])
                            / int(baseline[metric])
                            * 1_000_000_000
                        )
                    )
                interval = bootstrap(
                    ratios,
                    BOOTSTRAP_SEED_BASE
                    + 1000
                    + task_index * 100
                    + comparison_index * 10
                    + metric_index,
                )
                comparisons.append(
                    {
                        "numerator": RTDL_ARM,
                        "denominator": denominator,
                        "metric": metric,
                        "median_ratio": integer_median(ratios) / 1_000_000_000,
                        "bootstrap_95_percent_ratio": [
                            value / 1_000_000_000 for value in interval
                        ],
                        "registered_gate": None,
                    }
                )
        summaries.append(
            {"task": task, "arm_medians_ns": arms, "comparisons": comparisons}
        )
    return summaries


def recount_baseline(
    root: Path, prereg: dict[str, Any], authority: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    result = read_json(root / "result.json")
    verify_seal(result, "result_sha256", "baseline controller result")
    require(
        result.get("schema") == BASELINE_CONTROLLER_SCHEMA,
        "baseline result schema mismatch",
    )
    require(
        result.get("status") == "PASS__TWO_TASK_THREE_ARM_BASELINE_COMPLETE",
        "baseline result status mismatch",
    )
    require(
        result.get("source_commit") == authority["source_commit"],
        "baseline source commit mismatch",
    )
    require(
        result.get("preregistration_sha256") == prereg["preregistration_sha256"],
        "baseline result preregistration mismatch",
    )
    require(
        result.get("execution_authority_sha256") == authority["authority_sha256"],
        "baseline result authority mismatch",
    )
    require(
        result.get("hardware") == authority["hardware"],
        "baseline result hardware mismatch",
    )
    published = result.get("composite_rows")
    require(isinstance(published, list), "baseline composite rows missing")
    composites = []
    task_contracts: dict[str, tuple[str, str]] = {}
    for index, scheduled in enumerate(prereg["baseline_schedule"]):
        directory = root / f"{index:03d}_{scheduled['worker_id']}"
        first = read_json(directory / "first" / "receipt.json")
        steady = read_json(directory / "steady" / "receipt.json")
        validate_baseline_receipt(first, scheduled, FIRST_MODE, prereg, authority)
        validate_baseline_receipt(steady, scheduled, STEADY_MODE, prereg, authority)
        published_row = published[index]
        walls = published_row.get("process_wall_ns")
        require(
            isinstance(walls, list)
            and len(walls) == 2
            and all(type(value) is int and value >= 0 for value in walls),
            "baseline process-wall vector invalid",
        )
        recomputed = combine_baseline(first, steady, walls)
        require(
            recomputed == published_row, "baseline composite differs from raw receipts"
        )
        task = str(first["task"])
        contract = (str(first["input_sha256"]), str(first["output_sha256"]))
        if task in task_contracts:
            require(
                task_contracts[task] == contract,
                "cross-arm input/output contract drift",
            )
        else:
            task_contracts[task] = contract
        composites.append(recomputed)
    summaries = baseline_summary(composites)
    require(
        result.get("task_summaries") == summaries,
        "baseline controller summary differs from recount",
    )
    require(
        result.get("composite_worker_count") == len(composites),
        "baseline composite count mismatch",
    )
    require(
        result.get("subworker_count") == 2 * len(composites),
        "baseline subworker count mismatch",
    )
    return result, composites


def validate_identity_witness(
    witness: dict[str, Any], prereg: dict[str, Any], authority: dict[str, Any]
) -> None:
    verify_seal(witness, "witness_sha256", "GPU identity witness")
    require(
        witness.get("schema") == GPU_IDENTITY_WITNESS_SCHEMA,
        "identity witness schema mismatch",
    )
    require(
        witness.get("status") == "PASS__NO_TIMING_OBSERVED",
        "identity witness status mismatch",
    )
    require(
        witness.get("source_commit") == authority["source_commit"],
        "identity source commit mismatch",
    )
    require(
        witness.get("preregistration_sha256") == prereg["preregistration_sha256"],
        "identity preregistration mismatch",
    )
    require(
        witness.get("execution_authority_sha256") == authority["authority_sha256"],
        "identity authority mismatch",
    )
    require(
        witness.get("hardware") == authority["hardware"], "identity hardware mismatch"
    )
    rows = witness.get("tasks")
    require(
        isinstance(rows, list)
        and [row.get("task") for row in rows] == list(ADMISSION_TASKS),
        "identity task cohort mismatch",
    )
    for row in rows:
        frozen_task = next(
            task for task in prereg["task_contracts"] if task["task"] == row["task"]
        )
        require(
            row.get("input_sha256") == frozen_task["input_sha256"],
            "identity witness input differs from preregistration",
        )
        require(
            row.get("exact_identity_equal") is True,
            "on/off executable identity mismatch",
        )
        require(
            row.get("on", {}).get("output_sha256")
            == row.get("off", {}).get("output_sha256"),
            "on/off output mismatch",
        )
        require(
            row.get("on", {}).get("output_sha256")
            == frozen_task["public_output_sha256"],
            "identity witness output differs from preregistration",
        )
        require(
            row.get("on", {}).get("physical_executor_classification")
            == "optix_traversal_observed",
            "on arm lacks OptiX traversal",
        )
        require(
            row.get("off", {}).get("physical_executor_classification")
            == "optix_traversal_observed",
            "off arm lacks OptiX traversal",
        )
    require(
        witness.get("registered_timing_observation_count") == 0,
        "identity witness contains timing",
    )
    require(
        witness.get("performance_claim_authorized") is False,
        "identity witness overclaims performance",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--identity-witness", type=Path, required=True)
    parser.add_argument("--causal-root", type=Path, required=True)
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prereg_path = args.preregistration.resolve()
    authority_path = args.execution_authority.resolve()
    witness_path = args.identity_witness.resolve()
    causal_root = args.causal_root.resolve()
    baseline_root = args.baseline_root.resolve()
    prereg = load_preregistration(prereg_path, ROOT, verify_files=True)
    authority = read_json(authority_path)
    validate_authority(authority, prereg, prereg_path)
    witness = read_json(witness_path)
    validate_identity_witness(witness, prereg, authority)
    causal, causal_receipts = recount_causal(causal_root, prereg, authority)
    baseline, composites = recount_baseline(baseline_root, prereg, authority)
    require(causal.get("hardware") == authority["hardware"], "causal hardware mismatch")
    require(
        baseline.get("hardware") == authority["hardware"], "baseline hardware mismatch"
    )
    witness_rows = {row["task"]: row for row in witness["tasks"]}
    for task in ADMISSION_TASKS:
        causal_rows = [row for row in causal_receipts if row["task"] == task]
        require(bool(causal_rows), f"causal task missing: {task}")
        require(
            all(
                row["input_sha256"] == witness_rows[task]["input_sha256"]
                for row in causal_rows
            ),
            f"causal/identity input mismatch: {task}",
        )
        require(
            all(
                row["program_signature"] == witness_rows[task]["program_signature"]
                for row in causal_rows
            ),
            f"causal/identity program mismatch: {task}",
        )
    for task in BASELINE_TASKS:
        baseline_rows = [row for row in composites if row["task"] == task]
        require(
            all(
                row["input_sha256"] == witness_rows[task]["input_sha256"]
                for row in baseline_rows
            ),
            f"baseline/identity input mismatch: {task}",
        )
        require(
            all(
                row["output_sha256"] == witness_rows[task]["on"]["output_sha256"]
                for row in baseline_rows
            ),
            f"baseline/identity output mismatch: {task}",
        )
    causal_manifest = evidence_manifest(causal_root)
    baseline_manifest = evidence_manifest(baseline_root)
    result: dict[str, object] = {
        "schema": INDEPENDENT_RECOUNT_SCHEMA,
        "status": "PASS__ONE_GPU_GENERATION_RECOUNT_COMPLETE",
        "source_commit": authority["source_commit"],
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "hardware": authority["hardware"],
        "architecture_generation": authority["hardware"]["architecture_generation"],
        "identity_witness_sha256": witness["witness_sha256"],
        "causal_result_sha256": causal["result_sha256"],
        "baseline_result_sha256": baseline["result_sha256"],
        "causal_receipt_count": len(causal_receipts),
        "baseline_composite_count": len(composites),
        "causal_evidence_file_count": len(causal_manifest),
        "causal_evidence_manifest_sha256": digest(causal_manifest),
        "baseline_evidence_file_count": len(baseline_manifest),
        "baseline_evidence_manifest_sha256": digest(baseline_manifest),
        "causal_summaries": causal["task_summaries"],
        "baseline_summaries": baseline["task_summaries"],
        "distinct_gpu_architecture_generation_count": 1,
        "required_gpu_architecture_generation_count": 2,
        "cross_generation_gate_passed": False,
        "external_review_or_consensus": False,
        "public_performance_claim_authorized": False,
    }
    result["recount_sha256"] = digest(result)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="ascii") as stream:
        json.dump(
            result, stream, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False
        )
        stream.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
