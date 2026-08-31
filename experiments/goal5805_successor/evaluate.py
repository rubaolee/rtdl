"""Independent, deterministic paired-block evaluation for Goal5805."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
import statistics
from typing import Any, Mapping

from .protocol import BOOTSTRAP_DRAWS, REGIMES, TASKS, THRESHOLDS, canonical


def _metric(worker: Mapping[str, Any], regime: str) -> int:
    key = {
        "DEPLOYMENT_COLD": "deployment_cold_ns",
        "PREPARE": "prepare_ns",
        "STEADY_E2E": "steady_median_ns",
    }[regime]
    value = worker.get(key)
    if type(value) is not int or value <= 0:
        raise RuntimeError(f"Goal5805 worker metric differs: {regime}")
    return value


def _percentile(sorted_values: list[float], probability: float) -> float:
    index = int(probability * (len(sorted_values) - 1))
    return sorted_values[index]


def evaluate(controller: Mapping[str, Any]) -> dict[str, Any]:
    workers = controller.get("workers")
    if not isinstance(workers, list) or not workers:
        raise RuntimeError("Goal5805 controller workers absent")
    rows: list[dict[str, Any]] = []
    for task_index, task in enumerate(TASKS):
        for regime_index, regime in enumerate(REGIMES):
            ratios: list[float] = []
            block_rows = []
            block_ids = sorted({worker["block"] for worker in workers
                                if worker["task"] == task})
            for block in block_ids:
                selected = [worker for worker in workers
                            if worker["task"] == task and worker["block"] == block]
                arm_values = {}
                for arm in ("RTDL", "PYOPTIX"):
                    values = [_metric(worker["result"], regime)
                              for worker in selected if worker["arm"] == arm]
                    if len(values) != 2:
                        raise RuntimeError("Goal5805 block arm multiplicity differs")
                    arm_values[arm] = float(statistics.median(values))
                ratio = arm_values["RTDL"] / arm_values["PYOPTIX"]
                ratios.append(ratio)
                block_rows.append({"block": block, **arm_values, "ratio": ratio})
            if len(ratios) != 16:
                raise RuntimeError("Goal5805 paired block count differs")
            point = float(statistics.median(ratios))
            rng = random.Random(58_050_000 + task_index * 10 + regime_index)
            draws = sorted(float(statistics.median(
                [ratios[rng.randrange(len(ratios))] for _ in ratios]))
                for _ in range(BOOTSTRAP_DRAWS))
            low = _percentile(draws, 0.025)
            high = _percentile(draws, 0.975)
            threshold = THRESHOLDS[regime]
            rows.append({
                "task": task, "regime": regime,
                "rtdl_over_pyoptix": point,
                "ci95": [low, high], "threshold": threshold,
                "pass": point <= threshold and high <= threshold,
                "blocks": block_rows,
            })
    value = {
        "schema": "rtdl.goal5805.formal_evaluation.v1",
        "status": "COMPLETE__UNCONDITIONAL_RESULT_ACCEPTANCE",
        "rows": rows,
        "pass_count": sum(row["pass"] for row in rows),
        "row_count": len(rows),
        "all_six_pass": all(row["pass"] for row in rows),
        "registered_performance_timing_count": sum(
            worker["result"]["registered_performance_timing_count"]
            for worker in workers),
        "formal_worker_count": len(workers),
    }
    value["evaluation_sha256"] = hashlib.sha256(canonical(value)).hexdigest()
    return value


def evaluate_file(controller_path: Path, output: Path) -> dict[str, Any]:
    controller = json.loads(controller_path.read_text(encoding="utf-8"))
    value = evaluate(controller)
    output.write_bytes(json.dumps(
        value, indent=2, allow_nan=False, sort_keys=True).encode("utf-8") + b"\n")
    return value

