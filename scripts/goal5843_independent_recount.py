#!/usr/bin/env python3
"""Stdlib-only independent recount of a Goal5843 baseline transaction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
from typing import Any

from experiments.goal5843_post_r1_baseline.contracts import (
    ARMS,
    BLOCKS,
    BOOTSTRAP_DRAWS,
    BOOTSTRAP_LOWER_INDEX,
    BOOTSTRAP_SEED_BASE,
    BOOTSTRAP_UPPER_INDEX,
    CONTROLLER_SCHEMA,
    DIRECT_ARM,
    EXECUTION_AUTHORITY_SCHEMA,
    FIRST_MODE,
    PHASE_KEYS,
    PYOPTIX_ARM,
    RECOUNT_SCHEMA,
    RELATION_TASK,
    RTDL_ARM,
    STEADY_MODE,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    SUBWORKER_SCHEMA,
    TASKS,
    TRIANGLE_TASK,
    digest,
    load_preregistration,
    sha256_file,
    task_contract,
)
from experiments.goal5843_post_r1_baseline.runtime import create_json


ROOT = Path(__file__).resolve().parents[1]


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
    require(isinstance(observed, str) and digest(unsealed) == observed, f"{label} seal")


def integer_median(values: list[int]) -> int:
    require(bool(values) and all(type(value) is int for value in values), "median vector")
    ordered = sorted(values)
    middle = len(ordered) // 2
    return (
        ordered[middle]
        if len(ordered) % 2
        else (ordered[middle - 1] + ordered[middle]) // 2
    )


def bootstrap_interval(values: list[int], *, seed: int) -> list[int]:
    require(len(values) == BLOCKS, "bootstrap block count")
    source = random.Random(seed)
    draws = []
    for _ in range(BOOTSTRAP_DRAWS):
        sample = [values[source.randrange(len(values))] for _ in values]
        draws.append(integer_median(sample))
    draws.sort()
    return [draws[BOOTSTRAP_LOWER_INDEX], draws[BOOTSTRAP_UPPER_INDEX]]


def validate_receipt(
    receipt: dict[str, Any],
    *,
    scheduled: dict[str, Any],
    mode: str,
    prereg: dict[str, Any],
    authority: dict[str, Any],
) -> None:
    verify_seal(receipt, "receipt_sha256", "subworker receipt")
    contract = task_contract(prereg, scheduled["task"])
    exact = {
        "schema": SUBWORKER_SCHEMA,
        "status": "PASS",
        "schedule_worker_id": scheduled["worker_id"],
        "subworker_id": f"{scheduled['worker_id']}__{mode}",
        "task": scheduled["task"],
        "arm": scheduled["arm"],
        "block": scheduled["block"],
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
        require(receipt.get(key) == expected, f"receipt mismatch: {key}")
    phases = receipt.get("phases_ns")
    require(isinstance(phases, dict) and set(phases) == set(PHASE_KEYS), "phase schema")
    for key, value in phases.items():
        if key == "steady_complete_execution":
            require(
                isinstance(value, list)
                and all(type(item) is int and item >= 0 for item in value),
                "steady vector",
            )
        else:
            require(value is None or (type(value) is int and value >= 0), f"phase {key}")
    if mode == FIRST_MODE:
        require(
            type(phases["first_complete_execution"]) is int
            and phases["steady_complete_execution"] == [],
            "first execution shape",
        )
    else:
        require(
            phases["first_complete_execution"] is None
            and len(phases["steady_complete_execution"]) == STEADY_REPETITIONS,
            "steady execution shape",
        )
    require(isinstance(receipt.get("identity"), dict), "identity missing")
    boundary = receipt.get("latest_execution_boundary")
    require(isinstance(boundary, dict), "execution boundary missing")
    if scheduled["arm"] == RTDL_ARM and scheduled["task"] == TRIANGLE_TASK:
        gate = prereg["rtdl_triangle_receipt_gate"]
        exact_boundary = {
            "schema": "rtdl.v4.triangle_reduction_execution_boundary.v1",
            "execution_path": gate["execution_path"],
            "prepared_query_input_reused": mode == STEADY_MODE,
            "per_ray_u64_materialized_on_host": False,
            "event_rows_materialized_on_host": False,
            "public_output_scalar_bytes": 8,
        }
        for key, expected in exact_boundary.items():
            require(boundary.get(key) == expected, f"RTDL boundary mismatch: {key}")
        fast = boundary.get("fast_operation_receipt")
        require(isinstance(fast, dict), "RTDL fast-operation receipt missing")
        for key in (
            "optix_launch_count",
            "dynamic_accel_build_count",
            "control_d2h_bytes",
            "output_d2h_bytes",
            "role_counters_materialized",
            "total_auxiliary_cuda_kernel_launch_count",
        ):
            require(fast.get(key) == gate[key], f"RTDL fast receipt mismatch: {key}")
        if mode == STEADY_MODE:
            require(
                fast.get("dynamic_device_upload_call_count")
                == gate["steady_dynamic_device_upload_call_count"]
                and fast.get("dynamic_device_upload_bytes")
                == gate["steady_dynamic_device_upload_bytes"],
                "RTDL steady execution repeated query upload",
            )
        else:
            require(
                type(fast.get("dynamic_device_upload_call_count")) is int
                and fast["dynamic_device_upload_call_count"] > 0
                and type(fast.get("dynamic_device_upload_bytes")) is int
                and fast["dynamic_device_upload_bytes"] > 0,
                "RTDL first execution did not expose initial query upload",
            )
        require(
            fast.get("prepared_input_reused") is (mode == STEADY_MODE),
            "RTDL native reuse mismatch",
        )
    elif scheduled["arm"] == RTDL_ARM and scheduled["task"] == RELATION_TASK:
        traversal = boundary.get("traversal_receipt")
        traversal_body = dict(traversal) if isinstance(traversal, dict) else {}
        traversal_sha256 = traversal_body.pop("receipt_sha256", None)
        native_snapshot = (
            traversal.get("native_snapshot") if isinstance(traversal, dict) else None
        )
        expected_count = (
            1 if mode == FIRST_MODE else STEADY_WARMUPS + STEADY_REPETITIONS
        )
        require(
            boundary.get("schema")
            == "rtdl.goal5843.rtdl_relation_execution_boundary.v1",
            "RTDL relation boundary schema",
        )
        require(
            boundary.get("provider_execution_boundary_available") is False
            and boundary.get("evidence_source")
            == "generic_result.traversal_receipt"
            and boundary.get("provider_lifecycle_schema")
            == "rtdl.v4.public_protocol_lifecycle.v1"
            and boundary.get("provider_execution_count") == expected_count,
            "RTDL relation provider lifecycle evidence",
        )
        require(
            boundary.get("physical_executor_classification")
            == "optix_traversal_observed"
            and isinstance(traversal, dict)
            and traversal.get("schema")
            == "rtdl.physical_execution.traversal_receipt.v1"
            and isinstance(traversal_sha256, str)
            and digest(traversal_body) == traversal_sha256
            and traversal.get("physical_executor_classification")
            == "optix_traversal_observed"
            and traversal.get("route_identity")
            == "v4_callback_ir:custom_aabb_bounded_relation_v1"
            and traversal.get("provider_library_sha256")
            == authority["execution_paths"]["native_library_sha256"]
            and traversal.get("output_digest") == contract["public_output_sha256"]
            and traversal.get("expected_program_observed_at_receipt_edge") is True
            and isinstance(native_snapshot, dict)
            and native_snapshot.get("attempted_launch_count") == 2
            and native_snapshot.get("successful_launch_count") == 2
            and native_snapshot.get("complete_context_launch_count") == 2
            and native_snapshot.get("failed_launch_count") == 0
            and native_snapshot.get("raygen_invocation_count") == 8192,
            "RTDL relation traversal evidence",
        )


def combine(
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
        require(first.get(key) == steady.get(key), f"FIRST/STEADY drift: {key}")
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


def summarize(composites: list[dict[str, Any]], prereg: dict[str, Any]) -> list[dict[str, object]]:
    metrics = (
        "setup_total_ns",
        "first_complete_execution_ns",
        "steady_complete_execution_median_ns",
    )
    phase_names = tuple(key for key in PHASE_KEYS if "execution" not in key)
    result = []
    for task_index, task in enumerate(TASKS):
        rows = [row for row in composites if row["task"] == task]
        arms: dict[str, object] = {}
        for arm in ARMS:
            arm_rows = [row for row in rows if row["arm"] == arm]
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
                        row["first_phases_ns"][phase] is not None
                        for row in arm_rows
                    )
                    else None
                )
                for phase in phase_names
            }
            summary["worker_count"] = len(arm_rows)
            arms[arm] = summary
        comparisons = []
        for comparison_index, denominator in enumerate((DIRECT_ARM, PYOPTIX_ARM)):
            for metric_index, metric in enumerate(metrics):
                ratios = []
                for block in range(BLOCKS):
                    numerator = next(
                        row
                        for row in rows
                        if row["block"] == block and row["arm"] == RTDL_ARM
                    )
                    baseline = next(
                        row
                        for row in rows
                        if row["block"] == block and row["arm"] == denominator
                    )
                    require(int(baseline[metric]) > 0, "zero comparison denominator")
                    ratios.append(
                        round(int(numerator[metric]) / int(baseline[metric]) * 1_000_000_000)
                    )
                interval = bootstrap_interval(
                    ratios,
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
                        "within_block_scaled_ratios_1e9": ratios,
                        "median_ratio": integer_median(ratios) / 1_000_000_000,
                        "bootstrap_95_percent_ratio": [
                            interval[0] / 1_000_000_000,
                            interval[1] / 1_000_000_000,
                        ],
                        "registered_gate": None,
                    }
                )
        result.append(
            {
                "task": task,
                "task_role": task_contract(prereg, task)["role"],
                "arm_medians_ns": arms,
                "comparisons": comparisons,
            }
        )
    return result


def evidence_manifest(root: Path) -> list[dict[str, object]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]


def build_recount(
    preregistration: Path, execution_authority: Path, baseline_root: Path
) -> dict[str, object]:
    prereg = load_preregistration(preregistration, ROOT, verify_files=True)
    authority = read_json(execution_authority)
    verify_seal(authority, "authority_sha256", "execution authority")
    require(authority.get("schema") == EXECUTION_AUTHORITY_SCHEMA, "authority schema")
    require(
        authority.get("preregistration_sha256") == prereg["preregistration_sha256"],
        "authority preregistration binding",
    )
    controller = read_json(baseline_root / "RESULT.json")
    verify_seal(controller, "result_sha256", "controller result")
    require(controller.get("schema") == CONTROLLER_SCHEMA, "controller schema")
    worker_zero = read_json(baseline_root / "WORKER_ZERO.json")
    require(worker_zero.get("post_worker_zero_retry_permitted") is False, "worker zero")
    composites = []
    triangle_rtdl_receipts = 0
    for index, scheduled_value in enumerate(prereg["schedule"]):
        scheduled = dict(scheduled_value)
        directory = baseline_root / f"{index:03d}_{scheduled['worker_id']}"
        receipts = {}
        walls = []
        for directory_name, mode in (("first", FIRST_MODE), ("steady", STEADY_MODE)):
            child = directory / directory_name
            require(not (child / "failure.json").exists(), "formal failure record present")
            receipt = read_json(child / "receipt.json")
            validate_receipt(
                receipt,
                scheduled=scheduled,
                mode=mode,
                prereg=prereg,
                authority=authority,
            )
            observation = read_json(child / "controller_observation.json")
            require(
                observation
                == {
                    "schema": "rtdl.goal5843.controller_subworker_observation.v1",
                    "schedule_worker_id": scheduled["worker_id"],
                    "mode": mode,
                    "returncode": 0,
                    "process_wall_ns": observation.get("process_wall_ns"),
                }
                and type(observation["process_wall_ns"]) is int
                and observation["process_wall_ns"] >= 0,
                "controller observation mismatch",
            )
            command = read_json(child / "command.json")
            require(
                command.get("schedule_worker_id") == scheduled["worker_id"]
                and command.get("mode") == mode
                and isinstance(command.get("argv"), list),
                "command custody mismatch",
            )
            receipts[mode] = receipt
            walls.append(observation["process_wall_ns"])
            if scheduled["arm"] == RTDL_ARM and scheduled["task"] == TRIANGLE_TASK:
                triangle_rtdl_receipts += 1
        composites.append(combine(receipts[FIRST_MODE], receipts[STEADY_MODE], walls))
    require(composites == controller.get("composites"), "controller composites differ")
    summaries = summarize(composites, prereg)
    require(summaries == controller.get("task_summaries"), "controller summaries differ")
    require(len(composites) == BLOCKS * len(TASKS) * len(ARMS), "composite count")
    require(triangle_rtdl_receipts == BLOCKS * 2, "RTDL triangle receipt count")
    require(
        controller.get("all_adverse_rows_retained") is True
        and controller.get("registered_performance_success_threshold") is None
        and controller.get("public_performance_claim_authorized") is False
        and controller.get("manuscript_performance_claim_authorized") is False,
        "controller claim boundary widened",
    )
    manifest = evidence_manifest(baseline_root)
    expected_file_count = 2 + len(prereg["schedule"]) * 2 * 5
    require(len(manifest) == expected_file_count, "baseline evidence file count")
    result: dict[str, object] = {
        "schema": RECOUNT_SCHEMA,
        "status": "PASS__INDEPENDENT_STDLIB_RECOUNT_MATCHES_CONTROLLER",
        "source_commit": authority["source_commit"],
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "controller_result_sha256": controller["result_sha256"],
        "hardware": authority["hardware"],
        "composite_count": len(composites),
        "subworker_receipt_count": len(composites) * 2,
        "rtdl_triangle_receipt_gate_pass_count": triangle_rtdl_receipts,
        "task_summaries": summaries,
        "evidence_file_count": len(manifest),
        "evidence_manifest_sha256": digest(manifest),
        "all_adverse_rows_retained": True,
        "registered_performance_success_threshold": None,
        "public_performance_claim_authorized": False,
        "manuscript_performance_claim_authorized": False,
        "external_review_or_consensus_complete": False,
    }
    result["recount_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_recount(
        args.preregistration.resolve(),
        args.execution_authority.resolve(),
        args.baseline_root.resolve(),
    )
    create_json(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
