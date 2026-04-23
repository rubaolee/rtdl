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

from examples import rtdl_dbscan_clustering_app as dbscan
from examples import rtdl_outlier_detection_app as outlier
from scripts.goal839_baseline_artifact_schema import build_baseline_artifact
from scripts.goal839_baseline_artifact_schema import load_goal835_row
from scripts.goal839_baseline_artifact_schema import write_baseline_artifact
import rtdsl as rt


def _stats(samples: list[float]) -> dict[str, float]:
    if not samples:
        return {"min_sec": 0.0, "median_sec": 0.0, "max_sec": 0.0}
    return {
        "min_sec": min(samples),
        "median_sec": statistics.median(samples),
        "max_sec": max(samples),
    }


def _time_call(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


def _outlier_summary(rows: tuple[dict[str, object], ...]) -> dict[str, Any]:
    outlier_count = sum(1 for row in rows if bool(row["is_outlier"]))
    return {
        "point_count": len(rows),
        "threshold_reached_count": len(rows) - outlier_count,
        "outlier_count": outlier_count,
    }


def _dbscan_summary(rows: tuple[dict[str, object], ...]) -> dict[str, Any]:
    core_count = sum(1 for row in rows if bool(row["is_core"]))
    return {
        "point_count": len(rows),
        "threshold_reached_count": core_count,
        "core_count": core_count,
    }


def _profile_cpu_outlier(copies: int, iterations: int) -> dict[str, Any]:
    case, input_sec = _time_call(lambda: outlier.make_outlier_case(copies=copies))
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    last_rows: tuple[dict[str, object], ...] = ()
    for _ in range(iterations):
        last_rows, query_sec = _time_call(lambda: outlier.expected_tiled_density_rows(copies=copies))
        _, post_sec = _time_call(lambda: _outlier_summary(last_rows))
        query_samples.append(query_sec)
        postprocess_samples.append(post_sec)
    validation = outlier.brute_force_outlier_rows(case["points"])
    parity = tuple(last_rows) == tuple(validation)
    return {
        "summary": _outlier_summary(last_rows),
        "phase_seconds": {
            "point_pack": input_sec,
            "backend_prepare": 0.0,
            "native_threshold_query": _stats(query_samples)["median_sec"],
            "scalar_copyback": 0.0,
            "python_postprocess": _stats(postprocess_samples)["median_sec"],
        },
        "correctness_parity": parity,
        "validation": {
            "method": "compare expected_tiled_density_rows against brute_force_outlier_rows",
            "copies": copies,
            "matches_reference": parity,
        },
        "notes": [
            "CPU scalar oracle uses the exact tiled fixture evaluator for the public outlier case.",
            "No backend prepare phase exists for the CPU oracle path.",
        ],
    }


def _profile_cpu_dbscan(copies: int, iterations: int) -> dict[str, Any]:
    case, input_sec = _time_call(lambda: dbscan.make_dbscan_case(copies=copies))
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    last_rows: tuple[dict[str, object], ...] = ()
    for _ in range(iterations):
        last_rows, query_sec = _time_call(lambda: dbscan.expected_tiled_core_flag_rows(copies=copies))
        _, post_sec = _time_call(lambda: _dbscan_summary(last_rows))
        query_samples.append(query_sec)
        postprocess_samples.append(post_sec)
    validation = dbscan.brute_force_core_flag_rows(case["points"])
    parity = _dbscan_summary(last_rows) == _dbscan_summary(validation)
    return {
        "summary": _dbscan_summary(last_rows),
        "phase_seconds": {
            "point_pack": input_sec,
            "backend_prepare": 0.0,
            "native_threshold_query": _stats(query_samples)["median_sec"],
            "scalar_copyback": 0.0,
            "python_postprocess": _stats(postprocess_samples)["median_sec"],
        },
        "correctness_parity": parity,
        "validation": {
            "method": "compare expected_tiled_core_flag_rows compact summary against brute_force_core_flag_rows compact summary",
            "copies": copies,
            "matches_reference": parity,
        },
        "notes": [
            "CPU scalar oracle uses the exact tiled fixture evaluator for the public DBSCAN case.",
            "No backend prepare phase exists for the CPU oracle path.",
        ],
    }


def _profile_embree_outlier(copies: int, iterations: int) -> dict[str, Any]:
    case, input_sec = _time_call(lambda: outlier.make_outlier_case(copies=copies))
    prepared, prepare_sec = _time_call(lambda: rt.prepare_embree_fixed_radius_count_threshold_2d(case["points"]))
    query_samples: list[float] = []
    copyback_samples: list[float] = []
    postprocess_samples: list[float] = []
    last_rows: tuple[dict[str, object], ...] = ()
    try:
        for _ in range(iterations):
            count_rows, query_sec = _time_call(
                lambda: prepared.run(
                    case["points"],
                    radius=outlier.RADIUS,
                    threshold=outlier.MIN_NEIGHBORS_INCLUDING_SELF,
                )
            )
            last_rows, post_sec = _time_call(lambda: outlier._density_rows_from_count_rows(case["points"], count_rows))
            query_samples.append(query_sec)
            copyback_samples.append(0.0)
            postprocess_samples.append(post_sec)
    finally:
        prepared.close()
    expected = outlier.expected_tiled_density_rows(copies=copies)
    parity = tuple(last_rows) == tuple(expected)
    return {
        "summary": _outlier_summary(last_rows),
        "phase_seconds": {
            "point_pack": input_sec,
            "backend_prepare": prepare_sec,
            "native_threshold_query": _stats(query_samples)["median_sec"],
            "scalar_copyback": _stats(copyback_samples)["median_sec"],
            "python_postprocess": _stats(postprocess_samples)["median_sec"],
        },
        "correctness_parity": parity,
        "validation": {
            "method": "compare Embree prepared summary rows against expected_tiled_density_rows",
            "copies": copies,
            "matches_reference": parity,
        },
        "notes": [
            "Embree baseline uses prepared fixed-radius count-threshold traversal with compact summary reconstruction.",
        ],
    }


def _profile_embree_dbscan(copies: int, iterations: int) -> dict[str, Any]:
    case, input_sec = _time_call(lambda: dbscan.make_dbscan_case(copies=copies))
    prepared, prepare_sec = _time_call(lambda: rt.prepare_embree_fixed_radius_count_threshold_2d(case["points"]))
    query_samples: list[float] = []
    copyback_samples: list[float] = []
    postprocess_samples: list[float] = []
    last_rows: tuple[dict[str, object], ...] = ()
    try:
        for _ in range(iterations):
            count_rows, query_sec = _time_call(
                lambda: prepared.run(
                    case["points"],
                    radius=dbscan.EPSILON,
                    threshold=dbscan.MIN_POINTS,
                )
            )
            last_rows, post_sec = _time_call(lambda: dbscan._core_flag_rows_from_count_rows(case["points"], count_rows))
            query_samples.append(query_sec)
            copyback_samples.append(0.0)
            postprocess_samples.append(post_sec)
    finally:
        prepared.close()
    expected = dbscan.expected_tiled_core_flag_rows(copies=copies)
    parity = _dbscan_summary(last_rows) == _dbscan_summary(expected)
    return {
        "summary": _dbscan_summary(last_rows),
        "phase_seconds": {
            "point_pack": input_sec,
            "backend_prepare": prepare_sec,
            "native_threshold_query": _stats(query_samples)["median_sec"],
            "scalar_copyback": _stats(copyback_samples)["median_sec"],
            "python_postprocess": _stats(postprocess_samples)["median_sec"],
        },
        "correctness_parity": parity,
        "validation": {
            "method": "compare Embree prepared core compact summary against expected_tiled_core_flag_rows compact summary",
            "copies": copies,
            "matches_reference": parity,
        },
        "notes": [
            "Embree baseline uses prepared fixed-radius count-threshold traversal with compact core-flag reconstruction.",
        ],
    }


def build_artifact(*, app_name: str, backend: str, copies: int, iterations: int) -> dict[str, Any]:
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    if copies <= 0:
        raise ValueError("copies must be positive")

    if app_name == "outlier_detection" and backend == "cpu":
        row = load_goal835_row(
            app="outlier_detection",
            path_name="prepared_fixed_radius_density_summary",
            baseline_name="cpu_scalar_threshold_count_oracle",
        )
        prof = _profile_cpu_outlier(copies, iterations)
        return build_baseline_artifact(
            row=row,
            baseline_name="cpu_scalar_threshold_count_oracle",
            source_backend="cpu_oracle",
            benchmark_scale={"copies": copies, "iterations": iterations},
            repeated_runs=iterations,
            correctness_parity=prof["correctness_parity"],
            phase_seconds=prof["phase_seconds"],
            summary=prof["summary"],
            notes=prof["notes"],
            validation=prof["validation"],
        )
    if app_name == "outlier_detection" and backend == "embree":
        row = load_goal835_row(
            app="outlier_detection",
            path_name="prepared_fixed_radius_density_summary",
            baseline_name="embree_scalar_or_summary_path",
        )
        prof = _profile_embree_outlier(copies, iterations)
        return build_baseline_artifact(
            row=row,
            baseline_name="embree_scalar_or_summary_path",
            source_backend="embree",
            benchmark_scale={"copies": copies, "iterations": iterations},
            repeated_runs=iterations,
            correctness_parity=prof["correctness_parity"],
            phase_seconds=prof["phase_seconds"],
            summary=prof["summary"],
            notes=prof["notes"],
            validation=prof["validation"],
        )
    if app_name == "dbscan_clustering" and backend == "cpu":
        row = load_goal835_row(
            app="dbscan_clustering",
            path_name="prepared_fixed_radius_core_flags",
            baseline_name="cpu_scalar_threshold_count_oracle",
        )
        prof = _profile_cpu_dbscan(copies, iterations)
        return build_baseline_artifact(
            row=row,
            baseline_name="cpu_scalar_threshold_count_oracle",
            source_backend="cpu_oracle",
            benchmark_scale={"copies": copies, "iterations": iterations},
            repeated_runs=iterations,
            correctness_parity=prof["correctness_parity"],
            phase_seconds=prof["phase_seconds"],
            summary=prof["summary"],
            notes=prof["notes"],
            validation=prof["validation"],
        )
    if app_name == "dbscan_clustering" and backend == "embree":
        row = load_goal835_row(
            app="dbscan_clustering",
            path_name="prepared_fixed_radius_core_flags",
            baseline_name="embree_scalar_or_summary_path",
        )
        prof = _profile_embree_dbscan(copies, iterations)
        return build_baseline_artifact(
            row=row,
            baseline_name="embree_scalar_or_summary_path",
            source_backend="embree",
            benchmark_scale={"copies": copies, "iterations": iterations},
            repeated_runs=iterations,
            correctness_parity=prof["correctness_parity"],
            phase_seconds=prof["phase_seconds"],
            summary=prof["summary"],
            notes=prof["notes"],
            validation=prof["validation"],
        )
    raise ValueError(f"unsupported app/backend combination: {app_name}/{backend}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write Goal836-valid local fixed-radius baseline artifacts.")
    parser.add_argument("--app", choices=("outlier_detection", "dbscan_clustering"), required=True)
    parser.add_argument("--backend", choices=("cpu", "embree"), required=True)
    parser.add_argument("--copies", type=int, default=20000)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args(argv)
    artifact = build_artifact(
        app_name=args.app,
        backend=args.backend,
        copies=args.copies,
        iterations=args.iterations,
    )
    write_baseline_artifact(args.output_json, artifact)
    print(json.dumps(artifact, indent=2, sort_keys=True))
    return 0 if artifact["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
