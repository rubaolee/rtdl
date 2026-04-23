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


def _profile_outlier(copies: int, iterations: int, *, skip_validation: bool) -> dict[str, Any]:
    case = outlier_app.make_outlier_case(copies=copies)
    packed_points, pack_points_sec = _time_call(lambda: rt.pack_points(records=case["points"], dimension=2))
    one_shot_output, one_shot_sec = _time_call(
        lambda: outlier_app.run_app(
            "optix",
            copies=copies,
            optix_summary_mode="rt_count_threshold",
            output_mode="density_summary",
        )
    )
    prepared_obj, prepare_sec = _time_call(
        lambda: rt.prepare_optix_fixed_radius_count_threshold_2d(packed_points, max_radius=outlier_app.RADIUS)
    )
    native_samples: list[float] = []
    postprocess_samples: list[float] = []
    validation_samples: list[float] = []
    last_output: dict[str, Any] | None = None
    try:
        for _ in range(iterations):
            count_rows, elapsed = _time_call(
                lambda: prepared_obj.run(
                    packed_points,
                    radius=outlier_app.RADIUS,
                    threshold=outlier_app.MIN_NEIGHBORS_INCLUDING_SELF,
                )
            )
            native_samples.append(elapsed)
            density_rows, postprocess_sec = _time_call(
                lambda: outlier_app._density_rows_from_count_rows(case["points"], count_rows)
            )
            postprocess_samples.append(postprocess_sec)
            outlier_ids = [int(row["point_id"]) for row in density_rows if bool(row["is_outlier"])]
            oracle_rows: tuple[dict[str, object], ...] = ()
            oracle_outlier_ids: list[int] = []
            validation_sec = 0.0
            if not skip_validation:
                oracle_rows, validation_sec = _time_call(
                    lambda: outlier_app.expected_tiled_density_rows(copies=copies)
                )
                oracle_outlier_ids = [int(row["point_id"]) for row in oracle_rows if bool(row["is_outlier"])]
                validation_samples.append(validation_sec)
            last_output = {
                "matches_oracle": True if skip_validation else outlier_ids == oracle_outlier_ids,
                "point_count": len(case["points"]),
                "density_rows": density_rows,
                "oracle_density_rows": oracle_rows,
                "outlier_count": len(outlier_ids),
            }
    finally:
        _, close_sec = _time_call(prepared_obj.close)

    median = statistics.median(native_samples)
    return {
        "app": "outlier_detection",
        "copies": copies,
        "point_count": len(case["points"]),
        "one_shot_total_sec": one_shot_sec,
        "prepared_optix_pack_points_sec": pack_points_sec,
        "prepared_optix_prepare_sec": prepare_sec,
        "prepared_optix_warm_query_sec": _stats(native_samples),
        "prepared_optix_postprocess_sec": _stats(postprocess_samples),
        "prepared_optix_validation_sec": _stats(validation_samples),
        "prepared_optix_close_sec": close_sec,
        "speedup_one_shot_over_warm_query_median": one_shot_sec / median if median > 0.0 else 0.0,
        "phase_contract": {
            "native_warm_query": "prepared_obj.run only: OptiX traversal, threshold counting, and native row copy-back",
            "postprocess": "Python conversion from count rows to app density rows",
            "validation": "oracle construction/comparison timing; omitted when skip_validation=true",
        },
        "validation_mode": "skipped" if skip_validation else "per_iteration_expected_fixture",
        "one_shot_output": _compact(one_shot_output),
        "prepared_output": _compact(last_output or {}),
    }


def _profile_outlier_threshold_count(copies: int, iterations: int, *, skip_validation: bool) -> dict[str, Any]:
    case = outlier_app.make_outlier_case(copies=copies)
    packed_points, pack_points_sec = _time_call(lambda: rt.pack_points(records=case["points"], dimension=2))
    prepared_obj, prepare_sec = _time_call(
        lambda: rt.prepare_optix_fixed_radius_count_threshold_2d(packed_points, max_radius=outlier_app.RADIUS)
    )
    native_samples: list[float] = []
    validation_samples: list[float] = []
    last_output: dict[str, Any] | None = None
    point_count = len(case["points"])
    try:
        for _ in range(iterations):
            threshold_reached_count, elapsed = _time_call(
                lambda: prepared_obj.count_threshold_reached(
                    packed_points,
                    radius=outlier_app.RADIUS,
                    threshold=outlier_app.MIN_NEIGHBORS_INCLUDING_SELF,
                )
            )
            native_samples.append(elapsed)
            outlier_count = point_count - int(threshold_reached_count)
            oracle_outlier_count: int | None = None
            validation_sec = 0.0
            if not skip_validation:
                oracle_rows, validation_sec = _time_call(
                    lambda: outlier_app.expected_tiled_density_rows(copies=copies)
                )
                oracle_outlier_count = sum(1 for row in oracle_rows if bool(row["is_outlier"]))
                validation_samples.append(validation_sec)
            last_output = {
                "matches_oracle": True if skip_validation else outlier_count == oracle_outlier_count,
                "point_count": point_count,
                "threshold_reached_count": int(threshold_reached_count),
                "outlier_count": outlier_count,
                "oracle_outlier_count": oracle_outlier_count,
            }
    finally:
        _, close_sec = _time_call(prepared_obj.close)

    median = statistics.median(native_samples)
    return {
        "app": "outlier_detection",
        "copies": copies,
        "point_count": point_count,
        "one_shot_total_sec": None,
        "prepared_optix_pack_points_sec": pack_points_sec,
        "prepared_optix_prepare_sec": prepare_sec,
        "prepared_optix_warm_query_sec": _stats(native_samples),
        "prepared_optix_postprocess_sec": _stats([]),
        "prepared_optix_validation_sec": _stats(validation_samples),
        "prepared_optix_close_sec": close_sec,
        "speedup_one_shot_over_warm_query_median": 0.0 if median <= 0.0 else None,
        "phase_contract": {
            "native_warm_query": (
                "prepared_obj.count_threshold_reached only: OptiX traversal, threshold counting, "
                "and scalar count copy-back"
            ),
            "postprocess": "none in scalar-summary mode",
            "validation": "oracle construction/comparison timing; omitted when skip_validation=true",
        },
        "validation_mode": "skipped" if skip_validation else "per_iteration_expected_fixture",
        "result_mode": "threshold_count",
        "prepared_output": _compact(last_output or {}),
    }


def _profile_dbscan(copies: int, iterations: int, *, skip_validation: bool) -> dict[str, Any]:
    case = dbscan_app.make_dbscan_case(copies=copies)
    packed_points, pack_points_sec = _time_call(lambda: rt.pack_points(records=case["points"], dimension=2))
    one_shot_output, one_shot_sec = _time_call(
        lambda: dbscan_app.run_app(
            "optix",
            copies=copies,
            optix_summary_mode="rt_core_flags",
            output_mode="core_flags",
        )
    )
    prepared_obj, prepare_sec = _time_call(
        lambda: rt.prepare_optix_fixed_radius_count_threshold_2d(packed_points, max_radius=dbscan_app.EPSILON)
    )
    native_samples: list[float] = []
    postprocess_samples: list[float] = []
    validation_samples: list[float] = []
    last_output: dict[str, Any] | None = None
    try:
        for _ in range(iterations):
            count_rows, elapsed = _time_call(
                lambda: prepared_obj.run(
                    packed_points,
                    radius=dbscan_app.EPSILON,
                    threshold=dbscan_app.MIN_POINTS,
                )
            )
            native_samples.append(elapsed)
            core_flag_rows, postprocess_sec = _time_call(
                lambda: dbscan_app._core_flag_rows_from_count_rows(case["points"], count_rows)
            )
            postprocess_samples.append(postprocess_sec)
            core_flags = [(int(row["point_id"]), bool(row["is_core"])) for row in core_flag_rows]
            oracle_rows: tuple[dict[str, object], ...] = ()
            oracle_core_flags: list[tuple[int, bool]] = []
            validation_sec = 0.0
            if not skip_validation:
                oracle_rows, validation_sec = _time_call(lambda: dbscan_app.expected_tiled_core_flag_rows(copies=copies))
                oracle_core_flags = [(int(row["point_id"]), bool(row["is_core"])) for row in oracle_rows]
                validation_samples.append(validation_sec)
            last_output = {
                "matches_oracle": True if skip_validation else core_flags == oracle_core_flags,
                "point_count": len(case["points"]),
                "core_flag_rows": core_flag_rows,
                "oracle_core_flag_rows": oracle_rows,
                "core_count": sum(1 for _, is_core in core_flags if is_core),
            }
    finally:
        _, close_sec = _time_call(prepared_obj.close)

    median = statistics.median(native_samples)
    return {
        "app": "dbscan_clustering",
        "copies": copies,
        "point_count": len(case["points"]),
        "one_shot_total_sec": one_shot_sec,
        "prepared_optix_pack_points_sec": pack_points_sec,
        "prepared_optix_prepare_sec": prepare_sec,
        "prepared_optix_warm_query_sec": _stats(native_samples),
        "prepared_optix_postprocess_sec": _stats(postprocess_samples),
        "prepared_optix_validation_sec": _stats(validation_samples),
        "prepared_optix_close_sec": close_sec,
        "speedup_one_shot_over_warm_query_median": one_shot_sec / median if median > 0.0 else 0.0,
        "phase_contract": {
            "native_warm_query": "prepared_obj.run only: OptiX traversal, threshold counting, and native row copy-back",
            "postprocess": "Python conversion from count rows to app DBSCAN core flags",
            "validation": "oracle construction/comparison timing; omitted when skip_validation=true",
            "excluded": "full DBSCAN cluster expansion remains outside this prepared core-flag profiler",
        },
        "validation_mode": "skipped" if skip_validation else "per_iteration_expected_fixture",
        "one_shot_output": _compact(one_shot_output),
        "prepared_output": _compact(last_output or {}),
    }


def _profile_dbscan_threshold_count(copies: int, iterations: int, *, skip_validation: bool) -> dict[str, Any]:
    case = dbscan_app.make_dbscan_case(copies=copies)
    packed_points, pack_points_sec = _time_call(lambda: rt.pack_points(records=case["points"], dimension=2))
    prepared_obj, prepare_sec = _time_call(
        lambda: rt.prepare_optix_fixed_radius_count_threshold_2d(packed_points, max_radius=dbscan_app.EPSILON)
    )
    native_samples: list[float] = []
    validation_samples: list[float] = []
    last_output: dict[str, Any] | None = None
    point_count = len(case["points"])
    try:
        for _ in range(iterations):
            core_count, elapsed = _time_call(
                lambda: prepared_obj.count_threshold_reached(
                    packed_points,
                    radius=dbscan_app.EPSILON,
                    threshold=dbscan_app.MIN_POINTS,
                )
            )
            native_samples.append(elapsed)
            oracle_core_count: int | None = None
            validation_sec = 0.0
            if not skip_validation:
                oracle_rows, validation_sec = _time_call(lambda: dbscan_app.expected_tiled_core_flag_rows(copies=copies))
                oracle_core_count = sum(1 for row in oracle_rows if bool(row["is_core"]))
                validation_samples.append(validation_sec)
            last_output = {
                "matches_oracle": True if skip_validation else int(core_count) == oracle_core_count,
                "point_count": point_count,
                "threshold_reached_count": int(core_count),
                "core_count": int(core_count),
                "oracle_core_count": oracle_core_count,
            }
    finally:
        _, close_sec = _time_call(prepared_obj.close)

    median = statistics.median(native_samples)
    return {
        "app": "dbscan_clustering",
        "copies": copies,
        "point_count": point_count,
        "one_shot_total_sec": None,
        "prepared_optix_pack_points_sec": pack_points_sec,
        "prepared_optix_prepare_sec": prepare_sec,
        "prepared_optix_warm_query_sec": _stats(native_samples),
        "prepared_optix_postprocess_sec": _stats([]),
        "prepared_optix_validation_sec": _stats(validation_samples),
        "prepared_optix_close_sec": close_sec,
        "speedup_one_shot_over_warm_query_median": 0.0 if median <= 0.0 else None,
        "phase_contract": {
            "native_warm_query": (
                "prepared_obj.count_threshold_reached only: OptiX traversal, threshold counting, "
                "and scalar count copy-back"
            ),
            "postprocess": "none in scalar-summary mode; full DBSCAN cluster expansion remains outside this profiler",
            "validation": "oracle construction/comparison timing; omitted when skip_validation=true",
        },
        "validation_mode": "skipped" if skip_validation else "per_iteration_expected_fixture",
        "result_mode": "threshold_count",
        "prepared_output": _compact(last_output or {}),
    }


def run_suite(
    *,
    copies: int,
    iterations: int,
    skip_validation: bool = False,
    result_mode: str = "rows",
) -> dict[str, Any]:
    if copies <= 0:
        raise ValueError("--copies must be positive")
    if iterations <= 0:
        raise ValueError("--iterations must be positive")
    if result_mode not in {"rows", "threshold_count"}:
        raise ValueError("result_mode must be 'rows' or 'threshold_count'")
    profile_outlier = _profile_outlier if result_mode == "rows" else _profile_outlier_threshold_count
    profile_dbscan = _profile_dbscan if result_mode == "rows" else _profile_dbscan_threshold_count
    return {
        "suite": "goal757_optix_fixed_radius_prepared_perf",
        "copies": copies,
        "iterations": iterations,
        "skip_validation": skip_validation,
        "result_mode": result_mode,
        "results": (
            profile_outlier(copies, iterations, skip_validation=skip_validation),
            profile_dbscan(copies, iterations, skip_validation=skip_validation),
        ),
        "boundary": "GTX 1070 evidence validates OptiX prepared-scene behavior only. RTX RT-core speedup claims require RTX-class hardware.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal757 prepared OptiX fixed-radius performance profiler.")
    parser.add_argument("--copies", type=int, default=20000)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--result-mode", choices=("rows", "threshold_count"), default="rows")
    parser.add_argument("--output-json")
    args = parser.parse_args(argv)
    payload = run_suite(
        copies=args.copies,
        iterations=args.iterations,
        skip_validation=args.skip_validation,
        result_mode=args.result_mode,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output_json:
        Path(args.output_json).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
