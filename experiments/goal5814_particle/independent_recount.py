"""Separately implemented raw-worker recount for Goal5814.

This module deliberately does not import the primary evaluator or worker
validator. A PASS always reopens every preserved canonical stdout file,
independently validates all 144 worker envelopes, and rebuilds the three
descriptive rows from those raw receipts.
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
import random
import statistics
from typing import Any, Mapping

from .measurement_protocol import (
    ARM_B,
    ARM_D,
    BOOTSTRAP_CI_INDICES,
    BOOTSTRAP_DRAWS,
    BOOTSTRAP_SEED_BASE,
    BLOCK_COUNT,
    EXECUTION_CONCURRENCY_RULE,
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
    strict_json_bytes,
)


RECOUNT_SCHEMA = "rtdl.goal5814.particle_formal_independent_recount.v1"
_CONTROLLER_SCHEMA = "rtdl.goal5814.particle_formal_controller_result.v2"
_WORKER_SCHEMA = "rtdl.goal5814.particle_formal_worker_result.v2"
_EVALUATION_SCHEMA = "rtdl.goal5814.particle_formal_evaluation.v2"

_FILE_IDENTITY_KEYS = {"path", "bytes", "sha256"}
_CONTROLLER_KEYS = {
    "schema", "status", "preaction_file", "target_manifest_file",
    "execution_request_file", "project_closure_file",
    "schedule_sha256", "schedule", "workers",
    "execution_concurrency", "invalid_row_disposition", "timed",
    "retry_count", "resume_count", "replacement_count", "row_drop_count",
    "formal_worker_count", "unique_worker_pid_count",
    "registered_performance_timing_count",
}
_CONTROLLER_ROW_KEYS = {
    "ordinal", "regime", "block", "position", "arm", "worker_id",
    "result", "stdout_file", "stderr_file", "isolated_cache_files_after",
}
_WORKER_KEYS = {
    "schema", "status", "worker_id", "ordinal", "regime", "block",
    "position", "arm", "pid", "parent_pid", "preaction_file",
    "target_manifest_file", "execution_request_file",
    "project_closure_file", "target_observation",
    "deployment_capability", "schedule_sha256", "measurement", "timed",
    "retry_count", "resume_count", "replacement_count", "row_drop_count",
    "formal_worker_count", "registered_performance_timing_count",
}
_MEASUREMENT_KEYS = {
    "regime", "arm", "primary_value_ns", "primary_samples_ns",
    "first_execute_outside_primary_ns", "warmup_execute_count",
    "complete_execute_count", "execution_receipts", "clock",
    "clock_read_count", "registered_performance_timing_count",
    "close_after_all_registered_end_clocks",
}
_RECEIPT_KEYS = {
    "phase", "repetition", "control", "ledger",
    "exact_worker_check_after_end_clock", "output_borrowed_read_only",
    "output_shape", "output_strides",
}
_EVALUATION_KEYS = {
    "schema", "status", "ratio_orientation",
    "greater_than_one_means_rtdl_slower", "point_estimator",
    "threshold_count", "confirmatory_noninferiority_claim", "rows",
    "raw_workers", "formal_worker_count",
    "registered_performance_timing_count", "retry_count", "resume_count",
    "replacement_count", "row_drop_count", "evaluation_sha256",
}
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


class RecountError(RuntimeError):
    """Preserved raw rows do not independently reproduce the evaluation."""


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value)


def _structural_file_identity(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _FILE_IDENTITY_KEYS \
            or not isinstance(value.get("path"), str) \
            or type(value.get("bytes")) is not int or value["bytes"] < 0 \
            or not _is_sha256(value.get("sha256")):
        raise RecountError(f"Goal5814 recount {label} identity differs")
    path = Path(value["path"])
    if not path.is_absolute() and (
            value["path"] != path.as_posix()
            or not path.parts
            or any(part in ("", ".", "..") for part in path.parts)):
        raise RecountError(f"Goal5814 recount {label} relative path differs")
    return dict(value)


def _reopen_raw_identity(
        row: Mapping[str, Any], field: str, label: str,
        raw_root: Path | None,
        ) -> tuple[dict[str, Any], Path, bytes]:
    record = _structural_file_identity(row.get(field), label)
    try:
        recorded = Path(record["path"])
        if recorded.is_absolute():
            path = recorded.resolve(strict=True)
            if record["path"] != str(path):
                raise RecountError(f"Goal5814 recount {label} path differs")
        else:
            if raw_root is None:
                raise RecountError(
                    f"Goal5814 recount {label} relative root is absent")
            root = Path(raw_root).resolve(strict=True)
            path = (root / recorded).resolve(strict=True)
            try:
                path.relative_to(root)
            except ValueError as error:
                raise RecountError(
                    f"Goal5814 recount {label} escaped raw root") from error
        if not path.is_file():
            raise RecountError(f"Goal5814 recount {label} path differs")
        payload = path.read_bytes()
    except RecountError:
        raise
    except Exception as error:
        raise RecountError(
            f"Goal5814 recount {label} file is absent") from error
    if len(payload) != record["bytes"] \
            or hashlib.sha256(payload).hexdigest() != record["sha256"]:
        raise RecountError(f"Goal5814 recount {label} bytes differ")
    return record, path, payload


def _raw_file(
        row: Mapping[str, Any], raw_root: Path | None,
        ) -> tuple[dict[str, Any], dict[str, Any], Path, bytes]:
    record, path, payload = _reopen_raw_identity(
        row, "stdout_file", "stdout", raw_root)
    try:
        value = strict_json_bytes(payload, label="independent worker stdout")
    except Exception as error:
        raise RecountError(
            "Goal5814 recount stdout is not strict JSON") from error
    if payload != canonical_document(value) or value != row.get("result"):
        raise RecountError("Goal5814 recount embedded/raw worker differs")
    return value, record, path, payload


def _expected_receipt_coordinates(regime: str) -> list[tuple[str, int]]:
    if regime == "DEPLOYMENT_COLD":
        return [("COLD_FIRST_COMPLETE_EXECUTE", 0)]
    if regime == "PREPARE":
        return [("FIRST_COMPLETE_EXECUTE_OUTSIDE_PREPARE_PRIMARY", 0)]
    return [
        *[("STEADY_WARMUP", index) for index in range(STEADY_WARMUPS)],
        *[("STEADY_TIMED", index) for index in range(STEADY_REPETITIONS)],
    ]


def _metric(result: Mapping[str, Any], regime: str) -> tuple[int | float, int]:
    measurement = result.get("measurement")
    if not isinstance(measurement, Mapping) \
            or set(measurement) != _MEASUREMENT_KEYS \
            or measurement.get("regime") != regime \
            or measurement.get("arm") != result.get("arm") \
            or measurement.get("clock") != "time.perf_counter_ns" \
            or measurement.get("close_after_all_registered_end_clocks") \
            is not True:
        raise RecountError("Goal5814 recount measurement envelope differs")
    samples = measurement["primary_samples_ns"]
    receipts = measurement["execution_receipts"]
    if not isinstance(samples, list) or any(
            type(item) is not int or item <= 0 for item in samples) \
            or not isinstance(receipts, list):
        raise RecountError("Goal5814 recount samples/receipts differ")
    if regime == "STEADY_DYNAMIC_E2E":
        expected_registered = STEADY_REPETITIONS
        expected_warmups = STEADY_WARMUPS
        expected_complete = STEADY_WARMUPS + STEADY_REPETITIONS
        expected_clock_reads = STEADY_REPETITIONS * 2
        if len(samples) != STEADY_REPETITIONS \
                or measurement["first_execute_outside_primary_ns"] is not None:
            raise RecountError("Goal5814 recount steady cardinality differs")
        expected: int | float = statistics.median(samples)
    else:
        expected_registered = 2 if regime == "PREPARE" else 1
        expected_warmups = 0
        expected_complete = 1
        expected_clock_reads = expected_registered * 2
        if len(samples) != 1:
            raise RecountError("Goal5814 recount scalar cardinality differs")
        expected = samples[0]
        auxiliary = measurement["first_execute_outside_primary_ns"]
        if regime == "PREPARE":
            if type(auxiliary) is not int or auxiliary <= 0:
                raise RecountError(
                    "Goal5814 recount prepare auxiliary timing differs")
        elif auxiliary is not None:
            raise RecountError("Goal5814 recount cold auxiliary timing differs")
    primary = measurement["primary_value_ns"]
    if type(primary) is not type(expected) or primary != expected \
            or not math.isfinite(float(expected)) or expected <= 0 \
            or type(measurement["warmup_execute_count"]) is not int \
            or measurement["warmup_execute_count"] != expected_warmups \
            or type(measurement["complete_execute_count"]) is not int \
            or measurement["complete_execute_count"] != expected_complete \
            or type(measurement["clock_read_count"]) is not int \
            or measurement["clock_read_count"] != expected_clock_reads \
            or type(measurement["registered_performance_timing_count"]) is not int \
            or measurement["registered_performance_timing_count"] \
            != expected_registered:
        raise RecountError("Goal5814 recount worker timing accounting differs")
    coordinates = _expected_receipt_coordinates(regime)
    if len(receipts) != len(coordinates):
        raise RecountError("Goal5814 recount execute receipt count differs")
    for receipt, expected_coordinate in zip(receipts, coordinates, strict=True):
        if not isinstance(receipt, Mapping) or set(receipt) != _RECEIPT_KEYS \
                or (receipt["phase"], receipt["repetition"]) \
                != expected_coordinate \
                or receipt["control"] != [5_000, 0xFFFFFFFF, 0, 0] \
                or receipt["ledger"] != _SUCCESS_LEDGER \
                or receipt["exact_worker_check_after_end_clock"] is not True \
                or receipt["output_borrowed_read_only"] is not True \
                or receipt["output_shape"] != [5_000, 3] \
                or receipt["output_strides"] != [4, 20_000]:
            raise RecountError("Goal5814 recount execute receipt differs")
    return expected, expected_registered


def _validate_worker(
        result: Mapping[str, Any], expected: Any,
        controller: Mapping[str, Any],
        ) -> tuple[int | float, int]:
    if set(result) != _WORKER_KEYS \
            or result.get("schema") != _WORKER_SCHEMA \
            or result.get("status") != "PASS__ONE_FRESH_PROCESS_FORMAL_ROW" \
            or result.get("worker_id") != expected.worker_id \
            or result.get("ordinal") != expected.ordinal \
            or result.get("regime") != expected.regime \
            or result.get("block") != expected.block \
            or result.get("position") != expected.position \
            or result.get("arm") != expected.arm \
            or type(result.get("pid")) is not int or result["pid"] <= 0 \
            or type(result.get("parent_pid")) is not int \
            or result["parent_pid"] <= 0 \
            or result.get("schedule_sha256") != SCHEDULE_SHA256 \
            or result.get("timed") is not True \
            or any(type(result.get(key)) is not int or result[key] != 0
                   for key in ("retry_count", "resume_count",
                               "replacement_count", "row_drop_count")) \
            or type(result.get("formal_worker_count")) is not int \
            or result["formal_worker_count"] != 1 \
            or result.get("preaction_file") != controller["preaction_file"] \
            or result.get("target_manifest_file") \
            != controller["target_manifest_file"] \
            or result.get("execution_request_file") \
            != controller["execution_request_file"] \
            or result.get("project_closure_file") \
            != controller["project_closure_file"] \
            or not isinstance(result.get("target_observation"), Mapping) \
            or not isinstance(result.get("deployment_capability"), Mapping):
        raise RecountError("Goal5814 recount worker envelope differs")
    for field in (
            "preaction_file", "target_manifest_file",
            "execution_request_file", "project_closure_file"):
        _structural_file_identity(result[field], f"worker {field}")
    metric, registered = _metric(result, expected.regime)
    if type(result.get("registered_performance_timing_count")) is not int \
            or result["registered_performance_timing_count"] != registered:
        raise RecountError("Goal5814 recount worker registered timing differs")
    return metric, registered


def _bootstrap(values: list[float], row_index: int) -> list[float]:
    generator = random.Random(BOOTSTRAP_SEED_BASE + row_index)
    ordered: list[float] = []
    for _ in range(BOOTSTRAP_DRAWS):
        resample = generator.choices(values, k=BLOCK_COUNT)
        ordered.append(float(statistics.median(resample)))
    ordered.sort()
    return [
        ordered[BOOTSTRAP_CI_INDICES[0]],
        ordered[BOOTSTRAP_CI_INDICES[1]],
    ]


def _validate_evaluation(
        evaluation: Mapping[str, Any], *, rows: list[dict[str, Any]],
        raw_workers: list[dict[str, Any]], formal_worker_count: int,
        registered_timing_count: int, transaction_counts: Mapping[str, int],
        ) -> None:
    if set(evaluation) != _EVALUATION_KEYS:
        raise RecountError("Goal5814 primary evaluation envelope differs")
    unsigned = dict(evaluation)
    seal = unsigned.pop("evaluation_sha256")
    if not _is_sha256(seal) \
            or seal != hashlib.sha256(canonical(unsigned)).hexdigest() \
            or evaluation["schema"] != _EVALUATION_SCHEMA \
            or evaluation["status"] \
            != "COMPLETE__DESCRIPTIVE_ONLY__UNCONDITIONAL_RESULT" \
            or evaluation["ratio_orientation"] != "RTDL_OVER_PYOPTIX" \
            or evaluation["greater_than_one_means_rtdl_slower"] is not True \
            or evaluation["point_estimator"] \
            != "MEDIAN_OF_24_PAIRED_BLOCK_RATIOS" \
            or evaluation["threshold_count"] != 0 \
            or evaluation["confirmatory_noninferiority_claim"] is not False \
            or evaluation["rows"] != rows \
            or evaluation["raw_workers"] != raw_workers \
            or evaluation["formal_worker_count"] != formal_worker_count \
            or evaluation["registered_performance_timing_count"] \
            != registered_timing_count \
            or any(evaluation[key] != transaction_counts[key] for key in (
                "retry_count", "resume_count", "replacement_count",
                "row_drop_count")):
        raise RecountError(
            "Goal5814 independent raw reconstruction differs from evaluation")


def recount(
        controller: Mapping[str, Any], *,
        evaluation: Mapping[str, Any] | None = None,
        raw_root: Path | None = None,
        reopen_raw_files: bool = True) -> dict[str, Any]:
    """Recount one complete transaction; a PASS always consumes raw files."""

    if reopen_raw_files is not True:
        raise RecountError(
            "Goal5814 PASS recount requires reopening every raw worker file")
    workers = controller.get("workers")
    if set(controller) != _CONTROLLER_KEYS \
            or controller.get("schema") != _CONTROLLER_SCHEMA \
            or controller.get("status") \
            != "COMPLETE__144_FRESH_PROCESSES__NO_RETRY_OR_REPLACEMENT" \
            or controller.get("schedule_sha256") != SCHEDULE_SHA256 \
            or controller.get("schedule") != schedule_document() \
            or controller.get("execution_concurrency") \
            != EXECUTION_CONCURRENCY_RULE \
            or controller.get("invalid_row_disposition") != INVALID_ROW_RULE \
            or controller.get("timed") is not True \
            or any(type(controller.get(key)) is not int or controller[key] != 0
                   for key in ("retry_count", "resume_count",
                               "replacement_count", "row_drop_count")) \
            or type(controller.get("formal_worker_count")) is not int \
            or controller["formal_worker_count"] != TOTAL_WORKER_COUNT \
            or type(controller.get("unique_worker_pid_count")) is not int \
            or controller["unique_worker_pid_count"] != TOTAL_WORKER_COUNT \
            or not isinstance(workers, list) \
            or len(workers) != TOTAL_WORKER_COUNT:
        raise RecountError("Goal5814 recount controller envelope differs")
    for field in (
            "preaction_file", "target_manifest_file",
            "execution_request_file", "project_closure_file"):
        _structural_file_identity(controller[field], f"controller {field}")

    results: list[Mapping[str, Any]] = []
    raw_workers: list[dict[str, Any]] = []
    pids: set[int] = set()
    identity_projection: object | None = None
    seen_raw_paths: set[Path] = set()
    stdout_records: list[dict[str, Any]] = []
    stderr_records: list[dict[str, Any]] = []
    registered_timing_count = 0
    transaction_counts = {
        "retry_count": 0,
        "resume_count": 0,
        "replacement_count": 0,
        "row_drop_count": 0,
    }
    formal_worker_count = 0
    for row, expected in zip(workers, schedule(), strict=True):
        if not isinstance(row, Mapping) or set(row) != _CONTROLLER_ROW_KEYS \
                or row.get("ordinal") != expected.ordinal \
                or row.get("regime") != expected.regime \
                or row.get("block") != expected.block \
                or row.get("position") != expected.position \
                or row.get("arm") != expected.arm \
                or row.get("worker_id") != expected.worker_id \
                or row.get("isolated_cache_files_after") != []:
            raise RecountError("Goal5814 recount schedule row differs")
        result, stdout_record, stdout_path, _ = _raw_file(row, raw_root)
        stderr_record, stderr_path, _ = _reopen_raw_identity(
            row, "stderr_file", "stderr", raw_root)
        if stdout_path in seen_raw_paths or stderr_path in seen_raw_paths \
                or stdout_path == stderr_path:
            raise RecountError("Goal5814 recount raw file path is duplicated")
        seen_raw_paths.update((stdout_path, stderr_path))
        metric, registered = _validate_worker(result, expected, controller)
        if result["pid"] in pids:
            raise RecountError("Goal5814 recount fresh PID cardinality differs")
        pids.add(result["pid"])
        projection = {
            "target_observation": result["target_observation"],
            "deployment_capability": result["deployment_capability"],
        }
        if identity_projection is None:
            identity_projection = projection
        elif projection != identity_projection:
            raise RecountError("Goal5814 recount worker identities differ")
        registered_timing_count += registered
        formal_worker_count += result["formal_worker_count"]
        for key in transaction_counts:
            transaction_counts[key] += result[key]
        stdout_records.append(stdout_record)
        stderr_records.append(stderr_record)
        results.append(result)
        measurement = result["measurement"]
        raw_workers.append({
            "ordinal": expected.ordinal,
            "regime": expected.regime,
            "block": expected.block,
            "position": expected.position,
            "arm": expected.arm,
            "worker_id": expected.worker_id,
            "pid": result["pid"],
            "primary_value_ns": metric,
            "primary_samples_ns": measurement["primary_samples_ns"],
            "first_execute_outside_primary_ns": measurement[
                "first_execute_outside_primary_ns"],
            "registered_performance_timing_count": registered,
        })
    if len(pids) != TOTAL_WORKER_COUNT \
            or formal_worker_count != TOTAL_WORKER_COUNT \
            or controller["formal_worker_count"] != formal_worker_count \
            or controller["unique_worker_pid_count"] != len(pids) \
            or type(controller.get("registered_performance_timing_count")) \
            is not int \
            or controller["registered_performance_timing_count"] \
            != registered_timing_count \
            or any(controller[key] != transaction_counts[key]
                   for key in transaction_counts):
        raise RecountError("Goal5814 recount transaction cardinality differs")

    rebuilt_rows: list[dict[str, Any]] = []
    for row_index, regime in enumerate(REGIMES):
        ratios: list[float] = []
        b_values: list[int | float] = []
        d_values: list[int | float] = []
        block_rows: list[dict[str, Any]] = []
        for block in range(BLOCK_COUNT):
            selected = [
                result for result in results
                if result["regime"] == regime and result["block"] == block]
            if len(selected) != 2 or {item["arm"] for item in selected} \
                    != {ARM_B, ARM_D}:
                raise RecountError("Goal5814 recount paired block differs")
            by_arm = {item["arm"]: item for item in selected}
            b_value, _ = _metric(by_arm[ARM_B], regime)
            d_value, _ = _metric(by_arm[ARM_D], regime)
            ratio = float(d_value / b_value)
            if not math.isfinite(ratio) or ratio <= 0:
                raise RecountError("Goal5814 recount paired ratio differs")
            b_values.append(b_value)
            d_values.append(d_value)
            ratios.append(ratio)
            block_rows.append({
                "block": block,
                "order": [
                    item["arm"] for item in sorted(
                        selected, key=lambda item: item["position"])],
                "b_pyoptix_ns": b_value,
                "d_rtdl_ns": d_value,
                "rtdl_over_pyoptix": ratio,
            })
        rebuilt_rows.append({
            "zero_based_result_row_index": row_index,
            "regime": regime,
            "b_pyoptix_absolute_median_ns": statistics.median(b_values),
            "d_rtdl_absolute_median_ns": statistics.median(d_values),
            "rtdl_over_pyoptix": float(statistics.median(ratios)),
            "rtdl_over_pyoptix_ci95_fixed_indices": _bootstrap(
                ratios, row_index),
            "bootstrap_seed": BOOTSTRAP_SEED_BASE + row_index,
            "bootstrap_draw_count": BOOTSTRAP_DRAWS,
            "bootstrap_ci_indices": list(BOOTSTRAP_CI_INDICES),
            "threshold": None,
            "confirmatory_pass_fail": None,
            "blocks": block_rows,
        })
    if evaluation is not None:
        _validate_evaluation(
            evaluation, rows=rebuilt_rows, raw_workers=raw_workers,
            formal_worker_count=formal_worker_count,
            registered_timing_count=registered_timing_count,
            transaction_counts=transaction_counts)
    value: dict[str, Any] = {
        "schema": RECOUNT_SCHEMA,
        "status": "PASS__INDEPENDENT_RAW_RECOUNT_MATCHES",
        "rows": rebuilt_rows,
        "formal_worker_count": formal_worker_count,
        "unique_worker_pid_count": len(pids),
        "registered_performance_timing_count": registered_timing_count,
        "raw_worker_files_reopened": True,
        "raw_worker_stdout_file_count": len(stdout_records),
        "raw_worker_stdout_bytes": sum(
            record["bytes"] for record in stdout_records),
        "raw_worker_stdout_identities_sha256": hashlib.sha256(
            canonical(stdout_records)).hexdigest(),
        "raw_worker_stderr_file_count": len(stderr_records),
        "raw_worker_stderr_bytes": sum(
            record["bytes"] for record in stderr_records),
        "raw_worker_stderr_identities_sha256": hashlib.sha256(
            canonical(stderr_records)).hexdigest(),
        "primary_evaluation_compared": evaluation is not None,
        "threshold_count": 0,
        **transaction_counts,
    }
    value["recount_sha256"] = hashlib.sha256(canonical(value)).hexdigest()
    return value


def _read_canonical_document(path: Path, label: str) -> dict[str, Any]:
    try:
        resolved = Path(path).resolve(strict=True)
        if not resolved.is_file():
            raise RecountError(f"Goal5814 recount {label} is not a file")
        payload = resolved.read_bytes()
        value = strict_json_bytes(payload, label=label)
    except RecountError:
        raise
    except Exception as error:
        raise RecountError(f"Goal5814 recount {label} is absent") from error
    if payload != canonical_document(value):
        raise RecountError(
            f"Goal5814 recount {label} is not exact canonical JSON")
    return value


def recount_files(
        controller_path: Path, evaluation_path: Path,
        output_path: Path) -> dict[str, Any]:
    controller = _read_canonical_document(controller_path, "controller JSON")
    evaluation = _read_canonical_document(evaluation_path, "evaluation JSON")
    value = recount(
        controller, evaluation=evaluation,
        raw_root=Path(controller_path).resolve(strict=True).parent)
    with Path(output_path).open("xb") as stream:
        stream.write(canonical_document(value))
    return value
