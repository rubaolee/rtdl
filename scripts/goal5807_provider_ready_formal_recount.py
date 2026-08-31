#!/usr/bin/env python3
"""Independent raw-row recount of Goal5807 provider-ready confirmation."""

from __future__ import annotations

import argparse
import random
from pathlib import Path
import sys
from typing import Any

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


RECOUNT_SCHEMA = "rtdl.goal5807.provider_ready_formal_recount.v2"


def _median(values: list[float | int]) -> float:
    ordered = sorted(float(value) for value in values)
    count = len(ordered)
    if count == 0:
        raise RuntimeError("Goal5807 recount median is empty")
    midpoint = count // 2
    if count % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2.0


def _bootstrap(values: list[float], *, seed: int) -> tuple[float, float]:
    generator = random.Random(seed)
    distribution: list[float] = []
    for _ in range(BOOTSTRAP_DRAWS):
        sample = generator.choices(values, k=len(values))
        distribution.append(_median(sample))
    distribution.sort()
    return distribution[CI_INDICES[0]], distribution[CI_INDICES[1]]


def _regime_results(
    timings: dict[tuple[str, int, int, str], dict[str, int]], *,
    regime: str, threshold: dict[str, Any] | None,
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for task in TASKS:
        ratios: list[float] = []
        rtdl: list[int] = []
        pyoptix: list[int] = []
        block_rows: list[dict[str, Any]] = []
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
            rtdl_block = _median(values[ARMS[0]])
            pyoptix_block = _median(values[ARMS[1]])
            ratio = rtdl_block / pyoptix_block
            rtdl.extend(values[ARMS[0]])
            pyoptix.extend(values[ARMS[1]])
            ratios.append(ratio)
            block_rows.append({
                "block": block,
                "rtdl_median_ns": rtdl_block,
                "pyoptix_median_ns": pyoptix_block,
                "rtdl_over_pyoptix": ratio,
            })
        point = _median(ratios)
        ci_low, ci_high = _bootstrap(ratios, seed=SEEDS[task])
        rtdl_median = _median(rtdl)
        pyoptix_median = _median(pyoptix)
        positive_gap = max(0.0, rtdl_median - pyoptix_median)
        row: dict[str, Any] = {
            "block_count": len(block_rows),
            "block_rows": block_rows,
            "median_block_ratio_rtdl_over_pyoptix": point,
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
                "median_ratio_pass": point <= threshold[
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


def recount(
    *, contract: dict[str, Any], contract_sha256: str,
    controller: dict[str, Any], controller_sha256: str,
    rows: list[dict[str, Any]], evaluation: dict[str, Any],
    evaluation_sha256: str,
) -> dict[str, Any]:
    findings: list[str] = []
    expected = expected_worker_coordinates()
    evaluation_body = dict(evaluation)
    evaluation_seal = evaluation_body.pop("evaluation_sha256", None)
    if evaluation_seal != value_sha256(evaluation_body) \
            or evaluation.get("schema") != (
                "rtdl.goal5807.provider_ready_formal_evaluation.v2") \
            or evaluation.get("contract_sha256") != contract_sha256 \
            or evaluation.get("controller_sha256") != controller_sha256 \
            or evaluation.get("worker_count") != len(expected) \
            or evaluation.get("unique_worker_pid_count") != len(expected) \
            or evaluation.get("registered_performance_timing_count") != (
                len(expected) * REGISTERED_TIMINGS_PER_WORKER):
        findings.append("evaluation_receipt")
    if controller.get("schema") != (
            "rtdl.goal5807.provider_ready_formal_controller.v2") \
            or controller.get("status") != (
                "COMPLETE__NO_RETRY_RESUME_REPLACEMENT_OR_DROP") \
            or controller.get("contract_sha256") != contract_sha256 \
            or controller.get("worker_count") != len(expected) \
            or controller.get("unique_worker_pid_count") != len(expected) \
            or controller.get("registered_performance_timing_count") != len(
                expected) * REGISTERED_TIMINGS_PER_WORKER \
            or any(controller.get(name) != 0 for name in (
                "retry_count", "resume_count", "replacement_count",
                "row_drop_count")):
        findings.append("controller_receipt")
    by_id = {row.get("worker_id"): row for row in rows}
    if len(rows) != len(expected) or len(by_id) != len(expected):
        findings.append("row_universe_or_duplicate_id")
    timings: dict[tuple[str, int, int, str], dict[str, int]] = {}
    full_values: dict[tuple[str, str], list[int]] = {}
    phase_values: dict[tuple[str, str, str], list[int]] = {}
    pids: set[int] = set()
    for coordinate in expected:
        task, block, position, arm = coordinate
        identity = worker_id(task, block, position, arm)
        row = by_id.get(identity)
        if not isinstance(row, dict):
            findings.append(f"missing_row:{identity}")
            continue
        worker = row.get("worker_result")
        if not isinstance(worker, dict):
            findings.append(f"missing_worker_result:{identity}")
            continue
        worker_body = dict(worker)
        worker_seal = worker_body.pop("worker_receipt_sha256", None)
        pilot = worker.get("pilot_receipt")
        if not isinstance(pilot, dict):
            findings.append(f"missing_pilot_receipt:{identity}")
            continue
        pilot_body = dict(pilot)
        pilot_seal = pilot_body.pop("pilot_sha256", None)
        ledger = pilot.get("phase_ledger")
        pid = row.get("pid")
        value = worker.get("primary_app_prepare_plus_first_exact_execute_ns")
        registered = worker.get("registered_timing_ns")
        valid = (
            row.get("schema") == (
                "rtdl.goal5807.provider_ready_formal_row.v2")
            and row.get("status") == "PASS"
            and row.get("contract_sha256") == contract_sha256
            and row.get("worker_id") == identity
            and row.get("task") == task and row.get("block") == block
            and row.get("position") == position and row.get("arm") == arm
            and row.get("returncode") == 0
            and row.get("registered_performance_timing_count") == (
                REGISTERED_TIMINGS_PER_WORKER)
            and type(pid) is int and pid not in pids
            and worker.get("pid") == pid
            and worker.get("schema") == (
                "rtdl.goal5807.provider_ready_formal_worker.v2")
            and worker.get("status") == (
                "PASS__EXACT_ORACLE_AND_PHASE_LEDGER")
            and worker.get("worker_id") == identity
            and worker.get("task") == task and worker.get("arm") == arm
            and worker.get("contract_sha256") == contract_sha256
            and worker.get("registered_performance_timing_count") == (
                REGISTERED_TIMINGS_PER_WORKER)
            and worker.get("formal_worker_count") == 1
            and worker.get("all_phases_preserved_nonprimary") is True
            and worker_seal == value_sha256(worker_body)
            and pilot_seal == value_sha256(pilot_body)
            and worker.get("pilot_receipt_sha256") == value_sha256(pilot)
            and type(value) is int and value > 0
            and isinstance(registered, dict)
            and set(registered) == {
                "APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE", *PREFIX_REGIMES}
            and all(type(item) is int and item > 0
                    for item in registered.values())
            and registered[
                "APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE"] == value
            and isinstance(ledger, dict)
        )
        if not valid:
            findings.append(f"invalid_row:{identity}")
            continue
        try:
            total = validate_phase_ledger(ledger)
        except RuntimeError:
            findings.append(f"phase_ledger:{identity}")
            continue
        phase_primary = sum(
            int(ledger["phases"][name]["duration_ns"])
            for name in ("app_prepare", "first_exact_execute"))
        if phase_primary != value \
                or worker.get("full_process_total_ns_nonprimary") != total:
            findings.append(f"timing_projection:{identity}")
            continue
        pids.add(pid)
        timings[coordinate] = dict(registered)
        full_values.setdefault((task, arm), []).append(total)
        for name in PHASES:
            duration = ledger["phases"][name]["duration_ns"]
            if duration is not None:
                phase_values.setdefault((task, arm, name), []).append(duration)
    thresholded: dict[str, Any] = {}
    unthresholded: dict[str, Any] = {}
    if len(timings) == len(expected):
        hypotheses = contract["hypotheses"]
        thresholded = {
            THRESHOLDED_REGIMES[0]: _regime_results(
                timings, regime=THRESHOLDED_REGIMES[0],
                threshold=hypotheses["app_boundary"]),
            THRESHOLDED_REGIMES[1]: _regime_results(
                timings, regime=THRESHOLDED_REGIMES[1],
                threshold=hypotheses["harness_run_entry_prefix"]),
        }
        unthresholded = {
            PREFIX_REGIMES[1]: _regime_results(
                timings, regime=PREFIX_REGIMES[1], threshold=None),
        }
        if thresholded != evaluation.get("thresholded_results"):
            findings.append("evaluation_thresholded_results_mismatch")
        if unthresholded != evaluation.get(
                "unthresholded_first_class_results"):
            findings.append("evaluation_unthresholded_results_mismatch")
    phase_medians = {
        task: {
            arm: {
                name: (
                    _median(phase_values[(task, arm, name)])
                    if (task, arm, name) in phase_values else None)
                for name in PHASES
            }
            for arm in ARMS
        }
        for task in TASKS
    }
    full_medians = {
        task: {
            arm: _median(full_values[(task, arm)])
            if (task, arm) in full_values else None
            for arm in ARMS
        }
        for task in TASKS
    }
    if phase_medians != evaluation.get("nonprimary_phase_medians_ns"):
        findings.append("evaluation_phase_medians_mismatch")
    if full_medians != evaluation.get(
            "nonprimary_full_process_total_medians_ns"):
        findings.append("evaluation_full_process_medians_mismatch")
    all_pass = bool(thresholded) and all(
        row["hypothesis_pass"]
        for regime in thresholded.values() for row in regime.values())
    if evaluation.get(
            "all_thresholded_regimes_and_tasks_hypothesis_pass") != all_pass:
        findings.append("evaluation_overall_hypothesis_mismatch")
    expected_status = (
        "VALID_RESULT__HYPOTHESES_PASS" if all_pass else
        "VALID_RESULT__HYPOTHESES_FAIL__ACCEPTED_UNCONDITIONALLY")
    if evaluation.get("status") != expected_status:
        findings.append("evaluation_status_mismatch")
    if evaluation.get("valid_result_accepted_unconditionally") is not True:
        findings.append("evaluation_not_unconditionally_accepted")
    result = {
        "schema": RECOUNT_SCHEMA,
        "status": "PASS" if not findings else "FAIL",
        "contract_sha256": contract_sha256,
        "controller_sha256": controller_sha256,
        "evaluation_sha256": evaluation_sha256,
        "worker_count": len(rows),
        "unique_worker_pid_count": len(pids),
        "registered_performance_timing_count": (
            len(timings) * REGISTERED_TIMINGS_PER_WORKER),
        "recomputed_thresholded_results": thresholded,
        "recomputed_unthresholded_first_class_results": unthresholded,
        "recomputed_nonprimary_phase_medians_ns": phase_medians,
        "recomputed_nonprimary_full_process_total_medians_ns": full_medians,
        "finding_count": len(findings),
        "findings": findings,
        "threshold_failure_is_valid_scientific_result": True,
        "predecessor_goal5806_results_replaced": False,
    }
    return {**result, "recount_sha256": value_sha256(result)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    contract_path = args.contract.resolve(strict=True)
    matrix = args.matrix.resolve(strict=True)
    evaluation_path = args.evaluation.resolve(strict=True)
    contract = read_object(contract_path)
    validate_contract(contract, root, rehash=True)
    controller_path = matrix / "controller.json"
    controller = read_object(controller_path)
    row_paths = sorted((matrix / "rows").glob("*.json"))
    observed_hashes = {path.name: file_sha256(path) for path in row_paths}
    if observed_hashes != controller.get("row_sha256"):
        raise RuntimeError("Goal5807 controller row hash manifest differs")
    rows = [read_object(path) for path in row_paths]
    result = recount(
        contract=contract,
        contract_sha256=file_sha256(contract_path),
        controller=controller,
        controller_sha256=file_sha256(controller_path),
        rows=rows,
        evaluation=read_object(evaluation_path),
        evaluation_sha256=file_sha256(evaluation_path))
    create_only(args.output.resolve(), result)
    sys.stdout.buffer.write(canonical(result) + b"\n")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
