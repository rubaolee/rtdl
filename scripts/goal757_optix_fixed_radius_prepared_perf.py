#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_dbscan_clustering_app as dbscan_app
from examples import rtdl_outlier_detection_app as outlier_app


def _time_call(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


def _stats(samples: list[float]) -> dict[str, float]:
    if not samples:
        return {"min_sec": 0.0, "median_sec": 0.0, "max_sec": 0.0}
    return {
        "min_sec": min(samples),
        "median_sec": statistics.median(samples),
        "max_sec": max(samples),
    }


def _compact(payload: dict[str, Any]) -> dict[str, Any]:
    compact = dict(payload)
    for key in ("density_rows", "oracle_density_rows", "core_flag_rows", "oracle_core_flag_rows"):
        rows = compact.pop(key, None)
        if isinstance(rows, (list, tuple)):
            compact[f"{key}_count"] = len(rows)
            compact[f"{key}_sample"] = list(rows[:5])
    for key in ("outlier_point_ids", "noise_point_ids"):
        ids = compact.pop(key, None)
        if isinstance(ids, (list, tuple)):
            compact[f"{key}_count"] = len(ids)
            compact[f"{key}_sample"] = list(ids[:10])
    compact.pop("cluster_rows", None)
    compact.pop("oracle_cluster_rows", None)
    return compact


def _profile_outlier(copies: int, iterations: int) -> dict[str, Any]:
    case = outlier_app.make_outlier_case(copies=copies)
    one_shot_output, one_shot_sec = _time_call(
        lambda: outlier_app.run_app(
            "optix",
            copies=copies,
            optix_summary_mode="rt_count_threshold",
            output_mode="density_summary",
        )
    )
    prepared_obj, prepare_sec = _time_call(
        lambda: rt.prepare_optix_fixed_radius_count_threshold_2d(case["points"], max_radius=outlier_app.RADIUS)
    )
    samples: list[float] = []
    last_output: dict[str, Any] | None = None
    try:
        for _ in range(iterations):
            count_rows, elapsed = _time_call(
                lambda: prepared_obj.run(
                    case["points"],
                    radius=outlier_app.RADIUS,
                    threshold=outlier_app.MIN_NEIGHBORS_INCLUDING_SELF,
                )
            )
            density_rows = outlier_app._density_rows_from_count_rows(case["points"], count_rows)
            oracle_rows = outlier_app.expected_tiled_density_rows(copies=copies)
            outlier_ids = [int(row["point_id"]) for row in density_rows if bool(row["is_outlier"])]
            oracle_outlier_ids = [int(row["point_id"]) for row in oracle_rows if bool(row["is_outlier"])]
            last_output = {
                "matches_oracle": outlier_ids == oracle_outlier_ids,
                "point_count": len(case["points"]),
                "density_rows": density_rows,
                "oracle_density_rows": oracle_rows,
                "outlier_count": len(outlier_ids),
            }
            samples.append(elapsed)
    finally:
        _, close_sec = _time_call(prepared_obj.close)

    median = statistics.median(samples)
    return {
        "app": "outlier_detection",
        "copies": copies,
        "point_count": len(case["points"]),
        "one_shot_total_sec": one_shot_sec,
        "prepared_optix_prepare_sec": prepare_sec,
        "prepared_optix_warm_query_sec": _stats(samples),
        "prepared_optix_close_sec": close_sec,
        "speedup_one_shot_over_warm_query_median": one_shot_sec / median if median > 0.0 else 0.0,
        "one_shot_output": _compact(one_shot_output),
        "prepared_output": _compact(last_output or {}),
    }


def _profile_dbscan(copies: int, iterations: int) -> dict[str, Any]:
    case = dbscan_app.make_dbscan_case(copies=copies)
    one_shot_output, one_shot_sec = _time_call(
        lambda: dbscan_app.run_app(
            "optix",
            copies=copies,
            optix_summary_mode="rt_core_flags",
            output_mode="core_flags",
        )
    )
    prepared_obj, prepare_sec = _time_call(
        lambda: rt.prepare_optix_fixed_radius_count_threshold_2d(case["points"], max_radius=dbscan_app.EPSILON)
    )
    samples: list[float] = []
    last_output: dict[str, Any] | None = None
    try:
        for _ in range(iterations):
            count_rows, elapsed = _time_call(
                lambda: prepared_obj.run(
                    case["points"],
                    radius=dbscan_app.EPSILON,
                    threshold=dbscan_app.MIN_POINTS,
                )
            )
            core_flag_rows = dbscan_app._core_flag_rows_from_count_rows(case["points"], count_rows)
            oracle_rows = dbscan_app.expected_tiled_core_flag_rows(copies=copies)
            core_flags = [(int(row["point_id"]), bool(row["is_core"])) for row in core_flag_rows]
            oracle_core_flags = [(int(row["point_id"]), bool(row["is_core"])) for row in oracle_rows]
            last_output = {
                "matches_oracle": core_flags == oracle_core_flags,
                "point_count": len(case["points"]),
                "core_flag_rows": core_flag_rows,
                "oracle_core_flag_rows": oracle_rows,
                "core_count": sum(1 for _, is_core in core_flags if is_core),
            }
            samples.append(elapsed)
    finally:
        _, close_sec = _time_call(prepared_obj.close)

    median = statistics.median(samples)
    return {
        "app": "dbscan_clustering",
        "copies": copies,
        "point_count": len(case["points"]),
        "one_shot_total_sec": one_shot_sec,
        "prepared_optix_prepare_sec": prepare_sec,
        "prepared_optix_warm_query_sec": _stats(samples),
        "prepared_optix_close_sec": close_sec,
        "speedup_one_shot_over_warm_query_median": one_shot_sec / median if median > 0.0 else 0.0,
        "one_shot_output": _compact(one_shot_output),
        "prepared_output": _compact(last_output or {}),
    }


def run_suite(*, copies: int, iterations: int) -> dict[str, Any]:
    if copies <= 0:
        raise ValueError("--copies must be positive")
    if iterations <= 0:
        raise ValueError("--iterations must be positive")
    return {
        "suite": "goal757_optix_fixed_radius_prepared_perf",
        "copies": copies,
        "iterations": iterations,
        "results": (
            _profile_outlier(copies, iterations),
            _profile_dbscan(copies, iterations),
        ),
        "boundary": "GTX 1070 evidence validates OptiX prepared-scene behavior only. RTX RT-core speedup claims require RTX-class hardware.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal757 prepared OptiX fixed-radius performance profiler.")
    parser.add_argument("--copies", type=int, default=20000)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--output-json")
    args = parser.parse_args(argv)
    payload = run_suite(copies=args.copies, iterations=args.iterations)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output_json:
        Path(args.output_json).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
