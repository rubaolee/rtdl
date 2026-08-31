"""Deterministic descriptive paired-block evaluation for Goal5814."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import random
import statistics
from typing import Any, Mapping

from .formal_worker import validate_worker_result
from .measurement_protocol import (
    ARM_B,
    ARM_D,
    BOOTSTRAP_CI_INDICES,
    BOOTSTRAP_DRAWS,
    BOOTSTRAP_SEED_BASE,
    BLOCK_COUNT,
    INVALID_ROW_RULE,
    REGIMES,
    SCHEDULE_SHA256,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    TOTAL_WORKER_COUNT,
    canonical,
    canonical_document,
    schedule,
    schedule_document,
)


CONTROLLER_RESULT_SCHEMA = "rtdl.goal5814.particle_formal_controller_result.v2"
EVALUATION_SCHEMA = "rtdl.goal5814.particle_formal_evaluation.v2"


class EvaluationError(RuntimeError):
    """The complete 144-row evidence is absent or structurally invalid."""


_SUCCESS_LEDGER = {
    "h2d_copy_call_count": 9,
    "h2d_bytes": 140_136,
    "query_h2d_copy_call_count": 7,
    "query_h2d_bytes": 140_000,
    "control_reset_h2d_copy_call_count": 1,
    "control_reset_h2d_bytes": 16,
    "parameter_h2d_copy_call_count": 1,
    "parameter_h2d_bytes": 120,
    "optix_launch_call_count": 1,
    "raygen_invocation_count": 5_000,
    "control_d2h_copy_call_count": 1,
    "control_d2h_bytes": 16,
    "output_d2h_copy_call_count": 1,
    "output_d2h_bytes": 60_000,
    "status_before_output": True,
    "output_d2h_after_status_failure": 0,
    "blocking_boundary_count": 2,
}


def _positive(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) \
            or not math.isfinite(float(value)) or value <= 0:
        raise EvaluationError(f"Goal5814 {label} is not positive finite")
    return float(value)


def _expected_receipt_coordinates(regime: str) -> list[tuple[str, int]]:
    if regime == "DEPLOYMENT_COLD":
        return [("COLD_FIRST_COMPLETE_EXECUTE", 0)]
    if regime == "PREPARE":
        return [("FIRST_COMPLETE_EXECUTE_OUTSIDE_PREPARE_PRIMARY", 0)]
    return [
        *[("STEADY_WARMUP", index) for index in range(STEADY_WARMUPS)],
        *[("STEADY_TIMED", index) for index in range(STEADY_REPETITIONS)],
    ]


def _metric(result: Mapping[str, Any], regime: str) -> int | float:
    measurement = result.get("measurement")
    if not isinstance(measurement, Mapping) or set(measurement) != {
        "regime", "arm", "primary_value_ns", "primary_samples_ns",
        "first_execute_outside_primary_ns", "warmup_execute_count",
        "complete_execute_count", "execution_receipts", "clock",
        "clock_read_count", "registered_performance_timing_count",
        "close_after_all_registered_end_clocks",
    }:
        raise EvaluationError("Goal5814 worker measurement keys differ")
    samples = measurement["primary_samples_ns"]
    receipts = measurement["execution_receipts"]
    if not isinstance(samples, list) or not isinstance(receipts, list) \
            or measurement["clock"] != "time.perf_counter_ns" \
            or measurement["close_after_all_registered_end_clocks"] is not True:
        raise EvaluationError("Goal5814 worker measurement envelope differs")
    for value in samples:
        if type(value) is not int or value <= 0:
            raise EvaluationError("Goal5814 raw timing sample differs")
    if regime == "STEADY_DYNAMIC_E2E":
        expected_registered = STEADY_REPETITIONS
        expected_warmups = STEADY_WARMUPS
        expected_complete = STEADY_WARMUPS + STEADY_REPETITIONS
        expected_clock_reads = STEADY_REPETITIONS * 2
        expected_primary: int | float = statistics.median(samples)
        if len(samples) != STEADY_REPETITIONS \
                or measurement["first_execute_outside_primary_ns"] is not None:
            raise EvaluationError("Goal5814 steady raw sample set differs")
    else:
        expected_registered = 2 if regime == "PREPARE" else 1
        expected_warmups = 0
        expected_complete = 1
        expected_clock_reads = expected_registered * 2
        if len(samples) != 1:
            raise EvaluationError("Goal5814 scalar regime sample differs")
        expected_primary = samples[0]
        auxiliary = measurement["first_execute_outside_primary_ns"]
        if regime == "PREPARE":
            _positive(auxiliary, "prepare first-execute auxiliary")
        elif auxiliary is not None:
            raise EvaluationError("Goal5814 cold auxiliary timing differs")
    if measurement["primary_value_ns"] != expected_primary \
            or measurement["warmup_execute_count"] != expected_warmups \
            or measurement["complete_execute_count"] != expected_complete \
            or measurement["clock_read_count"] != expected_clock_reads \
            or measurement["registered_performance_timing_count"] \
            != expected_registered:
        raise EvaluationError("Goal5814 worker timing accounting differs")
    expected_coordinates = _expected_receipt_coordinates(regime)
    if len(receipts) != len(expected_coordinates):
        raise EvaluationError("Goal5814 execute receipt count differs")
    for receipt, coordinates in zip(receipts, expected_coordinates, strict=True):
        if not isinstance(receipt, Mapping) or set(receipt) != {
            "phase", "repetition", "control", "ledger",
            "exact_worker_check_after_end_clock", "output_borrowed_read_only",
            "output_shape", "output_strides",
        } or (receipt["phase"], receipt["repetition"]) != coordinates \
                or receipt["control"] != [5_000, 0xFFFFFFFF, 0, 0] \
                or receipt["ledger"] != _SUCCESS_LEDGER \
                or receipt["exact_worker_check_after_end_clock"] is not True \
                or receipt["output_borrowed_read_only"] is not True \
                or receipt["output_shape"] != [5_000, 3] \
                or receipt["output_strides"] != [4, 20_000]:
            raise EvaluationError("Goal5814 execute receipt differs")
    _positive(expected_primary, f"{regime} worker metric")
    return expected_primary


def validate_worker_measurement(
        result: Mapping[str, Any], regime: str) -> int | float:
    """Validate one complete raw row before the controller admits it."""

    return _metric(result, regime)


def _validate_controller(controller: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    required = {
        "schema", "status", "preaction_file", "target_manifest_file",
        "execution_request_file", "project_closure_file",
        "schedule_sha256", "schedule", "workers",
        "execution_concurrency", "invalid_row_disposition", "timed",
        "retry_count", "resume_count", "replacement_count", "row_drop_count",
        "formal_worker_count", "unique_worker_pid_count",
        "registered_performance_timing_count",
    }
    if set(controller) != required \
            or controller.get("schema") != CONTROLLER_RESULT_SCHEMA \
            or controller.get("status") \
            != "COMPLETE__144_FRESH_PROCESSES__NO_RETRY_OR_REPLACEMENT" \
            or controller.get("schedule_sha256") != SCHEDULE_SHA256 \
            or controller.get("schedule") != schedule_document() \
            or controller.get("execution_concurrency") \
            != "SEQUENTIAL__ONE_ACTIVE_WORKER" \
            or controller.get("invalid_row_disposition") != INVALID_ROW_RULE \
            or controller.get("timed") is not True \
            or any(controller.get(key) != 0 for key in (
                "retry_count", "resume_count", "replacement_count",
                "row_drop_count")) \
            or controller.get("formal_worker_count") != TOTAL_WORKER_COUNT \
            or controller.get("unique_worker_pid_count") != TOTAL_WORKER_COUNT:
        raise EvaluationError("Goal5814 formal controller envelope differs")
    workers = controller.get("workers")
    if not isinstance(workers, list) or len(workers) != TOTAL_WORKER_COUNT:
        raise EvaluationError("Goal5814 controller does not contain 144 rows")
    expected_rows = schedule()
    results: list[Mapping[str, Any]] = []
    pids: set[int] = set()
    identity_projection: object | None = None
    timing_count = 0
    for row, expected in zip(workers, expected_rows, strict=True):
        if not isinstance(row, Mapping) or set(row) != {
            "ordinal", "regime", "block", "position", "arm", "worker_id",
            "result", "stdout_file", "stderr_file",
            "isolated_cache_files_after",
        } or row["ordinal"] != expected.ordinal \
                or row["regime"] != expected.regime \
                or row["block"] != expected.block \
                or row["position"] != expected.position \
                or row["arm"] != expected.arm \
                or row["worker_id"] != expected.worker_id \
                or row["isolated_cache_files_after"] != []:
            raise EvaluationError("Goal5814 controller row differs")
        result = row["result"]
        if not isinstance(result, Mapping):
            raise EvaluationError("Goal5814 worker result is absent")
        try:
            validate_worker_result(result, expected=expected)
        except Exception as error:
            raise EvaluationError("Goal5814 worker result envelope differs") from error
        _metric(result, expected.regime)
        pids.add(result["pid"])
        timing_count += result["registered_performance_timing_count"]
        projection = {
            "preaction_file": result["preaction_file"],
            "target_manifest_file": result["target_manifest_file"],
            "execution_request_file": result["execution_request_file"],
            "project_closure_file": result["project_closure_file"],
            "target_observation": result["target_observation"],
            "deployment_capability": result["deployment_capability"],
        }
        if identity_projection is None:
            identity_projection = projection
        elif projection != identity_projection:
            raise EvaluationError("Goal5814 worker identity projection differs")
        results.append(result)
    if len(pids) != TOTAL_WORKER_COUNT \
            or controller["registered_performance_timing_count"] != timing_count:
        raise EvaluationError("Goal5814 PID/timing cardinality differs")
    first = results[0]
    if controller["preaction_file"] != first["preaction_file"] \
            or controller["target_manifest_file"] \
            != first["target_manifest_file"] \
            or controller["execution_request_file"] \
            != first["execution_request_file"] \
            or controller["project_closure_file"] \
            != first["project_closure_file"]:
        raise EvaluationError("Goal5814 controller identity differs")
    return results


def _bootstrap(ratios: list[float], row_index: int) -> tuple[float, float]:
    rng = random.Random(BOOTSTRAP_SEED_BASE + row_index)
    draws = sorted(float(statistics.median(
        rng.choices(ratios, k=BLOCK_COUNT))) for _ in range(BOOTSTRAP_DRAWS))
    return draws[BOOTSTRAP_CI_INDICES[0]], draws[BOOTSTRAP_CI_INDICES[1]]


def evaluate(controller: Mapping[str, Any]) -> dict[str, Any]:
    results = _validate_controller(controller)
    rows: list[dict[str, Any]] = []
    raw_workers: list[dict[str, Any]] = []
    for expected, result in zip(schedule(), results, strict=True):
        measurement = result["measurement"]
        raw_workers.append({
            "ordinal": expected.ordinal,
            "regime": expected.regime,
            "block": expected.block,
            "position": expected.position,
            "arm": expected.arm,
            "worker_id": expected.worker_id,
            "pid": result["pid"],
            "primary_value_ns": measurement["primary_value_ns"],
            "primary_samples_ns": measurement["primary_samples_ns"],
            "first_execute_outside_primary_ns": measurement[
                "first_execute_outside_primary_ns"],
            "registered_performance_timing_count": result[
                "registered_performance_timing_count"],
        })
    for row_index, regime in enumerate(REGIMES):
        regime_results = [
            result for result in results if result["regime"] == regime]
        block_rows: list[dict[str, Any]] = []
        ratios: list[float] = []
        absolute: dict[str, list[int | float]] = {ARM_B: [], ARM_D: []}
        for block in range(BLOCK_COUNT):
            selected = [
                result for result in regime_results if result["block"] == block]
            if len(selected) != 2 or {result["arm"] for result in selected} \
                    != {ARM_B, ARM_D}:
                raise EvaluationError("Goal5814 paired block differs")
            by_arm = {result["arm"]: result for result in selected}
            b_value = _metric(by_arm[ARM_B], regime)
            d_value = _metric(by_arm[ARM_D], regime)
            ratio = float(d_value / b_value)
            if not math.isfinite(ratio) or ratio <= 0:
                raise EvaluationError("Goal5814 paired ratio differs")
            absolute[ARM_B].append(b_value)
            absolute[ARM_D].append(d_value)
            ratios.append(ratio)
            block_rows.append({
                "block": block,
                "order": [
                    result["arm"] for result in sorted(
                        selected, key=lambda item: item["position"])],
                "b_pyoptix_ns": b_value,
                "d_rtdl_ns": d_value,
                "rtdl_over_pyoptix": ratio,
            })
        low, high = _bootstrap(ratios, row_index)
        rows.append({
            "zero_based_result_row_index": row_index,
            "regime": regime,
            "b_pyoptix_absolute_median_ns": statistics.median(absolute[ARM_B]),
            "d_rtdl_absolute_median_ns": statistics.median(absolute[ARM_D]),
            "rtdl_over_pyoptix": float(statistics.median(ratios)),
            "rtdl_over_pyoptix_ci95_fixed_indices": [low, high],
            "bootstrap_seed": BOOTSTRAP_SEED_BASE + row_index,
            "bootstrap_draw_count": BOOTSTRAP_DRAWS,
            "bootstrap_ci_indices": list(BOOTSTRAP_CI_INDICES),
            "threshold": None,
            "confirmatory_pass_fail": None,
            "blocks": block_rows,
        })
    value: dict[str, Any] = {
        "schema": EVALUATION_SCHEMA,
        "status": "COMPLETE__DESCRIPTIVE_ONLY__UNCONDITIONAL_RESULT",
        "ratio_orientation": "RTDL_OVER_PYOPTIX",
        "greater_than_one_means_rtdl_slower": True,
        "point_estimator": "MEDIAN_OF_24_PAIRED_BLOCK_RATIOS",
        "threshold_count": 0,
        "confirmatory_noninferiority_claim": False,
        "rows": rows,
        "raw_workers": raw_workers,
        "formal_worker_count": TOTAL_WORKER_COUNT,
        "registered_performance_timing_count": controller[
            "registered_performance_timing_count"],
        "retry_count": 0,
        "resume_count": 0,
        "replacement_count": 0,
        "row_drop_count": 0,
    }
    value["evaluation_sha256"] = hashlib.sha256(canonical(value)).hexdigest()
    return value


def evaluate_file(controller_path: Path, output_path: Path) -> dict[str, Any]:
    controller = json.loads(Path(controller_path).read_text(encoding="utf-8"))
    if not isinstance(controller, dict):
        raise EvaluationError("Goal5814 controller JSON root differs")
    value = evaluate(controller)
    with Path(output_path).open("xb") as stream:
        stream.write(canonical_document(value))
    return value
