#!/usr/bin/env python3
"""Independent raw-worker recount for Goal5817; imports no experiment code."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import statistics
from typing import Any


ARMS = ("DIRECT", "PYOPTIX", "RTDL")
TASKS = ("relation", "triangle")
REGIMES = ("DEPLOYMENT_COLD", "PREPARE", "STEADY_E2E")
COMPARISONS = (
    ("RTDL", "PYOPTIX"),
    ("PYOPTIX", "DIRECT"),
    ("RTDL", "DIRECT"),
)
PERMUTATIONS = (
    ("DIRECT", "PYOPTIX", "RTDL"),
    ("DIRECT", "RTDL", "PYOPTIX"),
    ("PYOPTIX", "DIRECT", "RTDL"),
    ("PYOPTIX", "RTDL", "DIRECT"),
    ("RTDL", "DIRECT", "PYOPTIX"),
    ("RTDL", "PYOPTIX", "DIRECT"),
)
THRESHOLDS = {
    "DEPLOYMENT_COLD": 1.10,
    "PREPARE": 1.10,
    "STEADY_E2E": 1.05,
}
BLOCKS = 18
DRAWS = 10_000


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _schedule() -> list[dict[str, object]]:
    rows = []
    ordinal = 0
    for task in TASKS:
        for regime in REGIMES:
            for block in range(BLOCKS):
                for position, arm in enumerate(
                        PERMUTATIONS[block % len(PERMUTATIONS)]):
                    rows.append({
                        "ordinal": ordinal,
                        "worker_id": (
                            f"{task}_{regime.lower()}_b{block:02d}_"
                            f"p{position}_{arm.lower()}"
                        ),
                        "task": task,
                        "regime": regime,
                        "block": block,
                        "position": position,
                        "arm": arm,
                    })
                    ordinal += 1
    return rows


def _percentile(values: list[float], probability: float) -> float:
    return values[int(probability * (len(values) - 1))]


def _read_one_json_line(path: Path) -> tuple[dict[str, Any], bytes]:
    payload = path.read_bytes()
    if not payload.endswith(b"\n") or payload.count(b"\n") != 1:
        raise RuntimeError(f"raw worker is not one JSON line: {path}")
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise RuntimeError(f"raw worker root differs: {path}")
    return value, payload


def _metric(raw: dict[str, Any], row: dict[str, object]) -> tuple[int, int]:
    expected_count = 64 if row["regime"] == "STEADY_E2E" else 1
    if raw.get("status") != "PASS" or raw.get("worker_id") != row["worker_id"] \
            or raw.get("regime") != row["regime"]:
        raise RuntimeError(f"raw worker identity differs: {row['worker_id']}")
    if row["arm"] == "DIRECT":
        expected_task = (
            "CUSTOM_AABB_CLOSED_RELATION_COUNT_V2_MATCHED"
            if row["task"] == "relation"
            else "BUILTIN_TRIANGLE_WEIGHTED_SCALAR_V2_MATCHED"
        )
        durations = raw.get("execute_or_regime_durations_ns")
        if raw.get("arm") != "A_DIRECT_CUDA_OPTIX" \
                or raw.get("task") != expected_task \
                or raw.get("correctness", {}).get("oracle_exact") is not True:
            raise RuntimeError(f"Direct raw correctness differs: {row['worker_id']}")
    else:
        durations = raw.get("durations_ns")
        if raw.get("arm") != row["arm"] or raw.get("task") != row["task"]:
            raise RuntimeError(f"Python raw identity differs: {row['worker_id']}")
    if not isinstance(durations, list) or len(durations) != expected_count \
            or any(type(item) is not int or item <= 0 for item in durations) \
            or raw.get("registered_performance_timing_count") != expected_count:
        raise RuntimeError(f"raw timing boundary differs: {row['worker_id']}")
    metric = int(statistics.median(durations))
    if row["arm"] != "DIRECT" and raw.get("metric_ns") != metric:
        raise RuntimeError(f"Python raw median differs: {row['worker_id']}")
    return metric, expected_count


def _evaluate(workers: list[dict[str, Any]]) -> dict[str, Any]:
    results = []
    comparison_index = {pair: index for index, pair in enumerate(COMPARISONS)}
    for task_index, task in enumerate(TASKS):
        for regime_index, regime in enumerate(REGIMES):
            selected = [row for row in workers
                        if row["task"] == task and row["regime"] == regime]
            for numerator, denominator in COMPARISONS:
                ratios = []
                block_rows = []
                for block in range(BLOCKS):
                    values = {}
                    for arm in ARMS:
                        matches = [row for row in selected
                                   if row["block"] == block and row["arm"] == arm]
                        if len(matches) != 1:
                            raise RuntimeError("independent block multiplicity differs")
                        values[arm] = matches[0]["metric_ns"]
                    ratio = values[numerator] / values[denominator]
                    ratios.append(ratio)
                    block_rows.append({"block": block, **values, "ratio": ratio})
                point = float(statistics.median(ratios))
                seed = (58_170_000 + task_index * 100 + regime_index * 10
                        + comparison_index[(numerator, denominator)])
                rng = random.Random(seed)
                draws = sorted(float(statistics.median(
                    [ratios[rng.randrange(len(ratios))] for _ in ratios]))
                    for _ in range(DRAWS))
                threshold = (THRESHOLDS[regime]
                             if (numerator, denominator) == ("RTDL", "PYOPTIX")
                             else None)
                high = _percentile(draws, 0.975)
                results.append({
                    "task": task,
                    "regime": regime,
                    "numerator": numerator,
                    "denominator": denominator,
                    "ratio": point,
                    "ci95": [_percentile(draws, 0.025), high],
                    "bootstrap_seed": seed,
                    "threshold": threshold,
                    "pass": (point <= threshold and high <= threshold
                             if threshold is not None else None),
                    "claim_mode": (
                        "REGISTERED_NONINFERIORITY_GATE" if threshold is not None
                        else "DESCRIPTIVE_NO_PASS_FAIL_THRESHOLD"),
                    "blocks": block_rows,
                })
    value = {
        "schema": "rtdl.goal5817.three_arm_evaluation.v1",
        "status": "COMPLETE__UNCONDITIONAL_RESULT_ACCEPTANCE",
        "rows": results,
        "row_count": len(results),
        "gated_pass_count": sum(row["pass"] is True for row in results),
        "gated_row_count": sum(row["pass"] is not None for row in results),
        "formal_worker_count": len(workers),
        "registered_performance_timing_count": sum(
            row["registered_performance_timing_count"] for row in workers),
        "current_source_direct_arm_present": True,
        "historical_goal5802_values_used": False,
        "prior_goal5805_values_used": False,
    }
    value["evaluation_sha256"] = hashlib.sha256(_canonical(value)).hexdigest()
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--evidence-archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence_root.resolve(strict=True)
    archive = args.evidence_archive.resolve(strict=True)
    output = args.output.absolute()
    if output.exists():
        raise FileExistsError(output)
    result_root = root / "results/formal_matrix_v1"
    workers_root = result_root / "workers"
    published_controller = json.loads(
        (result_root / "controller.json").read_text(encoding="utf-8"))
    published_evaluation = json.loads(
        (result_root / "evaluation.json").read_text(encoding="utf-8"))
    controller_rows = published_controller.get("workers")
    schedule = _schedule()
    if not isinstance(controller_rows, list) or len(controller_rows) != 324:
        raise RuntimeError("controller worker universe differs")
    controller_by_id = {row.get("worker_id"): row for row in controller_rows}
    if len(controller_by_id) != 324:
        raise RuntimeError("controller worker ids differ")
    if {path.name for path in workers_root.iterdir() if path.is_dir()} \
            != {row["worker_id"] for row in schedule}:
        raise RuntimeError("raw worker directory universe differs")

    recounted = []
    raw_rows = []
    pids = []
    timing_count = 0
    for row in schedule:
        worker_id = str(row["worker_id"])
        directory = workers_root / worker_id
        if (directory / "stderr.bin").read_bytes():
            raise RuntimeError(f"raw worker stderr is nonempty: {worker_id}")
        raw, payload = _read_one_json_line(directory / "stdout.bin")
        metric, count = _metric(raw, row)
        controller_row = controller_by_id[worker_id]
        projection = {key: controller_row.get(key) for key in (
            "ordinal", "worker_id", "task", "regime", "block", "position", "arm")}
        if projection != row or controller_row.get("raw_result") != raw \
                or controller_row.get("metric_ns") != metric \
                or controller_row.get("registered_performance_timing_count") \
                != count or controller_row.get("isolated_cache_files_after") != []:
            raise RuntimeError(f"controller/raw disagreement: {worker_id}")
        pid = controller_row.get("pid")
        if type(pid) is not int or pid <= 0:
            raise RuntimeError(f"worker pid differs: {worker_id}")
        pids.append(pid)
        timing_count += count
        recounted.append({
            **row, "pid": pid, "metric_ns": metric,
            "registered_performance_timing_count": count,
        })
        raw_rows.append({
            "worker_id": worker_id,
            "stdout_bytes": len(payload),
            "stdout_sha256": hashlib.sha256(payload).hexdigest(),
        })
    if len(set(pids)) != 324 or timing_count != 7_128:
        raise RuntimeError("fresh PID or timing total differs")
    independent = _evaluate(recounted)
    if independent != published_evaluation:
        raise RuntimeError("independent evaluation differs from published evaluation")
    receipt = {
        "schema": "rtdl.goal5817.independent_raw_recount.v1",
        "status": "PASS__324_RAW_WORKERS_AND_18_ROWS_EXACT",
        "evidence_archive": {
            "path": str(archive),
            "bytes": archive.stat().st_size,
            "sha256": _sha(archive),
        },
        "controller_file_sha256": _sha(result_root / "controller.json"),
        "published_evaluation_file_sha256": _sha(
            result_root / "evaluation.json"),
        "published_evaluation_internal_sha256": published_evaluation[
            "evaluation_sha256"],
        "raw_worker_count": 324,
        "unique_pid_count": 324,
        "empty_stderr_count": 324,
        "registered_performance_timing_count": timing_count,
        "row_count": independent["row_count"],
        "gated_pass_count": independent["gated_pass_count"],
        "raw_worker_projection_sha256": hashlib.sha256(
            _canonical(raw_rows)).hexdigest(),
        "rows": independent["rows"],
        "controller_raw_result_exact_match_count": 324,
        "retry_replacement_row_drop_count": 0,
    }
    receipt["receipt_sha256"] = hashlib.sha256(_canonical(receipt)).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(json.dumps(
        receipt, indent=2, allow_nan=False, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": receipt["status"],
        "gated_pass_count": receipt["gated_pass_count"],
        "receipt_sha256": receipt["receipt_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
