"""Independent paired-block evaluation for Goal5817."""

from __future__ import annotations

import hashlib
import json
import random
import statistics
from typing import Any, Mapping

from .protocol import (
    ARMS, BLOCK_COUNT, BOOTSTRAP_DRAWS, COMPARISONS, REGIMES,
    RTDL_OVER_PYOPTIX_THRESHOLDS, TASKS, canonical, schedule,
)


def _percentile(sorted_values: list[float], probability: float) -> float:
    return sorted_values[int(probability * (len(sorted_values) - 1))]


def _metric(row: Mapping[str, Any]) -> int:
    value = row.get("metric_ns")
    if type(value) is not int or value <= 0:
        raise RuntimeError("Goal5817 worker metric differs")
    return value


def evaluate(controller: Mapping[str, Any]) -> dict[str, Any]:
    workers = controller.get("workers")
    expected_schedule = schedule()
    if not isinstance(workers, list) or len(workers) != len(expected_schedule):
        raise RuntimeError("Goal5817 worker universe differs")
    observed_projection = [
        {key: row.get(key) for key in (
            "ordinal", "worker_id", "task", "regime", "block", "position", "arm")}
        for row in workers
    ]
    if observed_projection != expected_schedule:
        raise RuntimeError("Goal5817 worker schedule differs")
    if len({row.get("pid") for row in workers}) != len(workers):
        raise RuntimeError("Goal5817 worker PID freshness differs")

    results: list[dict[str, Any]] = []
    comparison_index = {pair: index for index, pair in enumerate(COMPARISONS)}
    for task_index, task in enumerate(TASKS):
        for regime_index, regime in enumerate(REGIMES):
            selected = [row for row in workers
                        if row["task"] == task and row["regime"] == regime]
            for numerator, denominator in COMPARISONS:
                block_rows = []
                ratios: list[float] = []
                for block in range(BLOCK_COUNT):
                    current = [row for row in selected if row["block"] == block]
                    values: dict[str, int] = {}
                    for arm in ARMS:
                        matches = [row for row in current if row["arm"] == arm]
                        if len(matches) != 1:
                            raise RuntimeError("Goal5817 block arm multiplicity differs")
                        values[arm] = _metric(matches[0])
                    ratio = values[numerator] / values[denominator]
                    ratios.append(ratio)
                    block_rows.append({
                        "block": block,
                        **values,
                        "ratio": ratio,
                    })
                point = float(statistics.median(ratios))
                seed = (
                    58_170_000 + task_index * 100 + regime_index * 10
                    + comparison_index[(numerator, denominator)]
                )
                rng = random.Random(seed)
                draws = sorted(float(statistics.median(
                    [ratios[rng.randrange(len(ratios))] for _ in ratios]))
                    for _ in range(BOOTSTRAP_DRAWS))
                low = _percentile(draws, 0.025)
                high = _percentile(draws, 0.975)
                gated = numerator == "RTDL" and denominator == "PYOPTIX"
                threshold = RTDL_OVER_PYOPTIX_THRESHOLDS[regime] if gated else None
                passed = (
                    point <= threshold and high <= threshold
                    if threshold is not None else None
                )
                results.append({
                    "task": task,
                    "regime": regime,
                    "numerator": numerator,
                    "denominator": denominator,
                    "ratio": point,
                    "ci95": [low, high],
                    "bootstrap_seed": seed,
                    "threshold": threshold,
                    "pass": passed,
                    "claim_mode": (
                        "REGISTERED_NONINFERIORITY_GATE" if gated
                        else "DESCRIPTIVE_NO_PASS_FAIL_THRESHOLD"
                    ),
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
            int(row.get("registered_performance_timing_count", 0))
            for row in workers),
        "current_source_direct_arm_present": True,
        "historical_goal5802_values_used": False,
        "prior_goal5805_values_used": False,
    }
    value["evaluation_sha256"] = hashlib.sha256(canonical(value)).hexdigest()
    return value

