#!/usr/bin/env python3
"""Deterministic unconditional-result evaluator for Goal5807 formal rows."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
import random
from pathlib import Path
import statistics
import sys
from typing import Any

from scripts.goal5807_provider_ready_formal_controller import (
    CONTROLLER_SCHEMA,
    ROW_SCHEMA,
)
from scripts.goal5807_provider_ready_formal_protocol import (
    ARMS,
    BLOCK_COUNT,
    BOOTSTRAP_DRAWS,
    CI_INDICES,
    PHASES,
    PREFIX_REGIMES,
    REGISTERED_TIMINGS_PER_WORKER,
    SEEDS,
    TASKS,
    THRESHOLDED_REGIMES,
    arm_order,
    canonical,
    create_only,
    expected_worker_coordinates,
    file_sha256,
    read_object,
    validate_contract,
    validate_phase_ledger,
    value_sha256,
    worker_id,
)
from scripts.goal5807_provider_ready_formal_worker import WORKER_SCHEMA


EVALUATION_SCHEMA = "rtdl.goal5807.provider_ready_formal_evaluation.v2"


def _bootstrap_ci(values: list[float], *, seed: int) -> tuple[float, float]:
    generator = random.Random(seed)
    distribution = sorted(
        float(statistics.median(generator.choices(values, k=len(values))))
        for _ in range(BOOTSTRAP_DRAWS)
    )
    return distribution[CI_INDICES[0]], distribution[CI_INDICES[1]]


def _validated_worker(
    row: Mapping[str, Any], *, expected: tuple[str, int, int, str],
    contract_sha256: str, seen_pids: set[int],
) -> tuple[dict[str, int], Mapping[str, Any], int]:
    task, block, position, arm = expected
    identity = worker_id(task, block, position, arm)
    result = row.get("worker_result")
    if not isinstance(result, Mapping):
        raise RuntimeError(f"Goal5807 worker result absent: {identity}")
    result_body = dict(result)
    result_seal = result_body.pop("worker_receipt_sha256", None)
    pid = row.get("pid")
    primary = result.get("primary_app_prepare_plus_first_exact_execute_ns")
    registered = result.get("registered_timing_ns")
    if row.get("schema") != ROW_SCHEMA \
            or row.get("status") != "PASS" \
            or row.get("contract_sha256") != contract_sha256 \
            or row.get("worker_id") != identity \
            or row.get("task") != task or row.get("block") != block \
            or row.get("position") != position or row.get("arm") != arm \
            or row.get("returncode") != 0 \
            or row.get("registered_performance_timing_count") != (
                REGISTERED_TIMINGS_PER_WORKER) \
            or type(pid) is not int or pid in seen_pids \
            or result_seal != value_sha256(result_body) \
            or result.get("schema") != WORKER_SCHEMA \
            or result.get("status") != (
                "PASS__EXACT_ORACLE_AND_PHASE_LEDGER") \
            or result.get("pid") != pid \
            or result.get("worker_id") != identity \
            or result.get("task") != task or result.get("arm") != arm \
            or result.get("contract_sha256") != contract_sha256 \
            or result.get("registered_performance_timing_count") != (
                REGISTERED_TIMINGS_PER_WORKER) \
            or result.get("formal_worker_count") != 1 \
            or result.get("all_phases_preserved_nonprimary") is not True \
            or type(primary) is not int or primary <= 0:
        raise RuntimeError(f"Goal5807 formal row differs: {identity}")
    expected_regimes = {
        "APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE", *PREFIX_REGIMES}
    if not isinstance(registered, Mapping) \
            or set(registered) != expected_regimes \
            or any(type(value) is not int or value <= 0
                   for value in registered.values()) \
            or registered["APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE"] != primary:
        raise RuntimeError(f"Goal5807 registered regimes differ: {identity}")
    pilot = result.get("pilot_receipt")
    if not isinstance(pilot, Mapping):
        raise RuntimeError(f"Goal5807 pilot receipt absent: {identity}")
    pilot_body = dict(pilot)
    pilot_seal = pilot_body.pop("pilot_sha256", None)
    ledger = pilot.get("phase_ledger")
    if pilot_seal != value_sha256(pilot_body) \
            or result.get("pilot_receipt_sha256") != value_sha256(pilot) \
            or not isinstance(ledger, Mapping):
        raise RuntimeError(f"Goal5807 pilot receipt seal differs: {identity}")
    total = validate_phase_ledger(ledger)
    phase_primary = sum(
        int(ledger["phases"][name]["duration_ns"])
        for name in ("app_prepare", "first_exact_execute"))
    if phase_primary != primary \
            or result.get("full_process_total_ns_nonprimary") != total:
        raise RuntimeError(f"Goal5807 timing projection differs: {identity}")
    seen_pids.add(pid)
    return dict(registered), ledger, total


def _regime_results(
    timings: Mapping[tuple[str, int, int, str], Mapping[str, int]], *,
    regime: str, threshold: Mapping[str, Any] | None,
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for task in TASKS:
        block_rows: list[dict[str, Any]] = []
        block_ratios: list[float] = []
        rtdl_values: list[int] = []
        pyoptix_values: list[int] = []
        for block in range(BLOCK_COUNT):
            order = arm_order(block)
            values = {
                arm: [
                    timings[(task, block, position, candidate)][regime]
                    for position, candidate in enumerate(order)
                    if candidate == arm
                ]
                for arm in ARMS
            }
            rtdl_pair = values[ARMS[0]]
            pyoptix_pair = values[ARMS[1]]
            rtdl_values.extend(rtdl_pair)
            pyoptix_values.extend(pyoptix_pair)
            rtdl_block = float(statistics.median(rtdl_pair))
            pyoptix_block = float(statistics.median(pyoptix_pair))
            ratio = rtdl_block / pyoptix_block
            block_ratios.append(ratio)
            block_rows.append({
                "block": block,
                "rtdl_median_ns": rtdl_block,
                "pyoptix_median_ns": pyoptix_block,
                "rtdl_over_pyoptix": ratio,
            })
        median_ratio = float(statistics.median(block_ratios))
        ci_low, ci_high = _bootstrap_ci(block_ratios, seed=SEEDS[task])
        rtdl_median = float(statistics.median(rtdl_values))
        pyoptix_median = float(statistics.median(pyoptix_values))
        positive_gap = max(0.0, rtdl_median - pyoptix_median)
        row: dict[str, Any] = {
            "block_count": len(block_rows),
            "block_rows": block_rows,
            "median_block_ratio_rtdl_over_pyoptix": median_ratio,
            "bootstrap_ci_low": ci_low,
            "bootstrap_ci_high": ci_high,
            "rtdl_arm_median_ns": rtdl_median,
            "pyoptix_arm_median_ns": pyoptix_median,
            "ratio_of_arm_medians": rtdl_median / pyoptix_median,
            "positive_rtdl_minus_pyoptix_arm_median_gap_ns": positive_gap,
            "threshold_applied": threshold is not None,
        }
        if threshold is not None:
            gates = {
                "median_ratio_pass": median_ratio <= threshold[
                    "median_block_ratio_rtdl_over_pyoptix_max"],
                "bootstrap_ci_upper_pass": ci_high <= threshold[
                    "bootstrap_ci_upper_max"],
                "positive_slower_gap_pass": positive_gap <= threshold[
                    "positive_rtdl_minus_pyoptix_arm_median_gap_ns_max"],
            }
            row["gates"] = gates
            row["hypothesis_pass"] = all(gates.values())
        else:
            row["gates"] = None
            row["hypothesis_pass"] = None
        results[task] = row
    return results


def evaluate_rows(
    contract: Mapping[str, Any], rows: Sequence[Mapping[str, Any]], *,
    contract_sha256: str, controller_sha256: str,
) -> dict[str, Any]:
    expected = expected_worker_coordinates()
    if len(rows) != len(expected):
        raise RuntimeError("Goal5807 formal row count differs")
    rows_by_id = {row.get("worker_id"): row for row in rows}
    if len(rows_by_id) != len(expected):
        raise RuntimeError("Goal5807 formal worker ids repeat")
    timings: dict[tuple[str, int, int, str], dict[str, int]] = {}
    full_process: dict[str, dict[str, Any]] = {}
    phase_values: dict[tuple[str, str, str], list[int]] = {}
    full_values: dict[tuple[str, str], list[int]] = {}
    pids: set[int] = set()
    for coordinate in expected:
        task, block, position, arm = coordinate
        identity = worker_id(task, block, position, arm)
        row = rows_by_id.get(identity)
        if not isinstance(row, Mapping):
            raise RuntimeError(f"Goal5807 formal row missing: {identity}")
        registered, ledger, total_ns = _validated_worker(
            row, expected=coordinate, contract_sha256=contract_sha256,
            seen_pids=pids)
        timings[coordinate] = registered
        phase_projection = {
            name: ledger["phases"][name]["duration_ns"] for name in PHASES
        }
        full_process[identity] = {
            "task": task,
            "arm": arm,
            "full_process_total_ns_nonprimary": total_ns,
            "phase_duration_ns_nonprimary": phase_projection,
        }
        full_values.setdefault((task, arm), []).append(total_ns)
        for name, value in phase_projection.items():
            if value is not None:
                phase_values.setdefault((task, arm, name), []).append(value)
    hypotheses = contract["hypotheses"]
    threshold_by_regime = {
        THRESHOLDED_REGIMES[0]: hypotheses["app_boundary"],
        THRESHOLDED_REGIMES[1]: hypotheses["harness_run_entry_prefix"],
    }
    thresholded_results = {
        regime: _regime_results(
            timings, regime=regime, threshold=threshold_by_regime[regime])
        for regime in THRESHOLDED_REGIMES
    }
    unthresholded_results = {
        PREFIX_REGIMES[1]: _regime_results(
            timings, regime=PREFIX_REGIMES[1], threshold=None),
    }
    phase_medians = {
        task: {
            arm: {
                name: (
                    float(statistics.median(phase_values[(task, arm, name)]))
                    if (task, arm, name) in phase_values else None)
                for name in PHASES
            }
            for arm in ARMS
        }
        for task in TASKS
    }
    full_medians = {
        task: {
            arm: float(statistics.median(full_values[(task, arm)]))
            for arm in ARMS
        }
        for task in TASKS
    }
    all_pass = all(
        row["hypothesis_pass"]
        for regime in thresholded_results.values() for row in regime.values())
    evaluation = {
        "schema": EVALUATION_SCHEMA,
        "status": (
            "VALID_RESULT__HYPOTHESES_PASS" if all_pass
            else "VALID_RESULT__HYPOTHESES_FAIL__ACCEPTED_UNCONDITIONALLY"),
        "contract_sha256": contract_sha256,
        "controller_sha256": controller_sha256,
        "worker_count": len(rows),
        "unique_worker_pid_count": len(pids),
        "registered_performance_timing_count": (
            len(rows) * REGISTERED_TIMINGS_PER_WORKER),
        "thresholded_results": thresholded_results,
        "unthresholded_first_class_results": unthresholded_results,
        "all_thresholded_regimes_and_tasks_hypothesis_pass": all_pass,
        "nonprimary_full_process_evidence_by_worker": full_process,
        "nonprimary_full_process_total_medians_ns": full_medians,
        "nonprimary_phase_medians_ns": phase_medians,
        "full_ledger_or_prepared_close_ratio_claim_authorized": False,
        "claim_boundary": contract["claim_boundary"],
        "predecessor_results": contract["predecessor_results"],
        "valid_result_accepted_unconditionally": True,
    }
    return {**evaluation, "evaluation_sha256": value_sha256(evaluation)}


def evaluate_matrix(
    *, root: Path, contract_path: Path, matrix: Path, output: Path,
) -> dict[str, Any]:
    contract = read_object(contract_path)
    validate_contract(contract, root, rehash=True)
    controller_path = matrix / "controller.json"
    controller = read_object(controller_path)
    if controller.get("schema") != CONTROLLER_SCHEMA \
            or controller.get("status") != (
                "COMPLETE__NO_RETRY_RESUME_REPLACEMENT_OR_DROP") \
            or controller.get("contract_sha256") != file_sha256(contract_path) \
            or controller.get("worker_count") != len(
                expected_worker_coordinates()) \
            or controller.get("unique_worker_pid_count") != len(
                expected_worker_coordinates()) \
            or controller.get("registered_performance_timing_count") != (
                len(expected_worker_coordinates())
                * REGISTERED_TIMINGS_PER_WORKER) \
            or any(controller.get(name) != 0 for name in (
                "retry_count", "resume_count", "replacement_count",
                "row_drop_count")):
        raise RuntimeError("Goal5807 controller receipt differs")
    row_paths = sorted((matrix / "rows").glob("*.json"))
    observed_hashes = {path.name: file_sha256(path) for path in row_paths}
    if observed_hashes != controller.get("row_sha256"):
        raise RuntimeError("Goal5807 controller row hash manifest differs")
    rows = [read_object(path) for path in row_paths]
    evaluation = evaluate_rows(
        contract, rows, contract_sha256=file_sha256(contract_path),
        controller_sha256=file_sha256(controller_path))
    create_only(output, evaluation)
    return evaluation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate_matrix(
        root=args.root.resolve(strict=True),
        contract_path=args.contract.resolve(strict=True),
        matrix=args.matrix.resolve(strict=True),
        output=args.output.resolve())
    sys.stdout.buffer.write(canonical(result) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
