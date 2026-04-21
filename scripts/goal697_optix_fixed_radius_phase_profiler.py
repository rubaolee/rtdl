#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_dbscan_clustering_app as dbscan
from examples import rtdl_outlier_detection_app as outlier


GOAL = "Goal697 OptiX fixed-radius app-level phase profiler"
DATE = "2026-04-21"


def _time_call(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


def _stats(samples: Iterable[float]) -> dict[str, float]:
    values = list(samples)
    if not values:
        return {"min_sec": 0.0, "median_sec": 0.0, "max_sec": 0.0}
    return {
        "min_sec": min(values),
        "median_sec": statistics.median(values),
        "max_sec": max(values),
    }


def _append_sample(samples: dict[str, list[float]], phase: str, value: float) -> None:
    samples.setdefault(phase, []).append(value)


def _fixed_radius_count_rows(
    points: tuple[rt.Point, ...],
    *,
    radius: float,
    threshold: int,
) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for query in points:
        count = 0
        threshold_reached = 0
        for candidate in points:
            if math.hypot(query.x - candidate.x, query.y - candidate.y) <= radius:
                count += 1
                if count >= threshold:
                    threshold_reached = 1
                    break
        rows.append(
            {
                "query_id": query.id,
                "neighbor_count": min(count, threshold),
                "threshold_reached": threshold_reached,
            }
        )
    return tuple(rows)


def _run_fixed_radius_summary(
    mode: str,
    points: tuple[rt.Point, ...],
    *,
    radius: float,
    threshold: int,
) -> tuple[dict[str, object], ...]:
    if mode == "optix":
        return tuple(
            rt.fixed_radius_count_threshold_2d_optix(
                points,
                points,
                radius=radius,
                threshold=threshold,
            )
        )
    if mode == "dry-run":
        return _fixed_radius_count_rows(points, radius=radius, threshold=threshold)
    raise ValueError(f"unsupported mode `{mode}`")


def _profile_outlier_once(
    *,
    mode: str,
    copies: int,
    path: str,
) -> tuple[dict[str, float], dict[str, object]]:
    phases: dict[str, float] = {}
    total_start = time.perf_counter()
    case, elapsed = _time_call(lambda: outlier.make_outlier_case(copies=copies))
    phases["python_input_construction"] = elapsed
    points = case["points"]

    if path == "rows":
        backend = "optix" if mode == "optix" else "cpu_python_reference"
        neighbor_rows, elapsed = _time_call(lambda: outlier._run_rows(backend, case))
        phases["backend_execute_or_materialize_rows"] = elapsed
        density_rows, elapsed = _time_call(lambda: outlier.density_rows_from_neighbor_rows(points, neighbor_rows))
        phases["python_postprocess"] = elapsed
        native_summary_row_count = 0
        result_rows = density_rows
        comparison_kind = "full_density_rows"
    elif path == "rt_count_threshold":
        count_rows, elapsed = _time_call(
            lambda: _run_fixed_radius_summary(
                mode,
                points,
                radius=outlier.RADIUS,
                threshold=outlier.MIN_NEIGHBORS_INCLUDING_SELF,
            )
        )
        phases["backend_execute_or_materialize_rows"] = elapsed
        result_rows, elapsed = _time_call(lambda: outlier._density_rows_from_count_rows(points, count_rows))
        phases["python_postprocess"] = elapsed
        neighbor_rows = ()
        native_summary_row_count = len(count_rows)
        comparison_kind = "outlier_flags_only"
    else:
        raise ValueError(f"unsupported outlier path `{path}`")

    oracle_rows, elapsed = _time_call(lambda: outlier.brute_force_outlier_rows(points))
    phases["oracle_validate"] = elapsed
    if comparison_kind == "outlier_flags_only":
        observed = [int(row["point_id"]) for row in result_rows if bool(row["is_outlier"])]
        expected = [int(row["point_id"]) for row in oracle_rows if bool(row["is_outlier"])]
        matches_oracle = observed == expected
    else:
        matches_oracle = result_rows == oracle_rows
    phases["total"] = time.perf_counter() - total_start

    return phases, {
        "app": "outlier_detection",
        "path": path,
        "copies": copies,
        "point_count": len(points),
        "neighbor_row_count": len(neighbor_rows),
        "native_summary_row_count": native_summary_row_count,
        "matches_oracle": matches_oracle,
        "comparison_kind": comparison_kind,
    }


def _profile_dbscan_once(
    *,
    mode: str,
    copies: int,
    path: str,
) -> tuple[dict[str, float], dict[str, object]]:
    phases: dict[str, float] = {}
    total_start = time.perf_counter()
    case, elapsed = _time_call(lambda: dbscan.make_dbscan_case(copies=copies))
    phases["python_input_construction"] = elapsed
    points = case["points"]

    if path == "rows":
        backend = "optix" if mode == "optix" else "cpu_python_reference"
        neighbor_rows, elapsed = _time_call(lambda: dbscan._run_rows(backend, case))
        phases["backend_execute_or_materialize_rows"] = elapsed
        cluster_rows, elapsed = _time_call(lambda: dbscan.cluster_from_neighbor_rows(points, neighbor_rows))
        phases["python_postprocess"] = elapsed
        core_flag_rows = ()
        comparison_kind = "full_cluster_rows"
    elif path == "rt_core_flags":
        count_rows, elapsed = _time_call(
            lambda: _run_fixed_radius_summary(
                mode,
                points,
                radius=dbscan.EPSILON,
                threshold=dbscan.MIN_POINTS,
            )
        )
        phases["backend_execute_or_materialize_rows"] = elapsed
        core_flag_rows, elapsed = _time_call(lambda: dbscan._core_flag_rows_from_count_rows(points, count_rows))
        phases["python_postprocess"] = elapsed
        neighbor_rows = ()
        cluster_rows = ()
        comparison_kind = "core_flags_only"
    else:
        raise ValueError(f"unsupported dbscan path `{path}`")

    oracle_rows, elapsed = _time_call(lambda: dbscan.brute_force_dbscan(points))
    phases["oracle_validate"] = elapsed
    if comparison_kind == "core_flags_only":
        oracle_core_flag_rows, elapsed = _time_call(lambda: dbscan.brute_force_core_flag_rows(points))
        phases["oracle_core_flag_validate"] = elapsed
        observed = [(int(row["point_id"]), bool(row["is_core"])) for row in core_flag_rows]
        expected = [(int(row["point_id"]), bool(row["is_core"])) for row in oracle_core_flag_rows]
        matches_oracle = observed == expected
    else:
        matches_oracle = cluster_rows == oracle_rows
    phases["total"] = time.perf_counter() - total_start

    return phases, {
        "app": "dbscan_clustering",
        "path": path,
        "copies": copies,
        "point_count": len(points),
        "neighbor_row_count": len(neighbor_rows),
        "native_summary_row_count": len(core_flag_rows),
        "cluster_row_count": len(cluster_rows),
        "matches_oracle": matches_oracle,
        "comparison_kind": comparison_kind,
    }


def _profile_case(
    *,
    mode: str,
    app: str,
    path: str,
    copies: int,
    iterations: int,
) -> dict[str, object]:
    phase_samples: dict[str, list[float]] = {}
    last_output: dict[str, object] = {}
    for _ in range(iterations):
        if app == "outlier_detection":
            phases, output = _profile_outlier_once(mode=mode, copies=copies, path=path)
        elif app == "dbscan_clustering":
            phases, output = _profile_dbscan_once(mode=mode, copies=copies, path=path)
        else:
            raise ValueError(f"unsupported app `{app}`")
        for phase, elapsed in phases.items():
            _append_sample(phase_samples, phase, elapsed)
        last_output = output

    return {
        "app": app,
        "path": path,
        "mode": mode,
        "iterations": iterations,
        "phase_stats": {phase: _stats(samples) for phase, samples in sorted(phase_samples.items())},
        "last_output": last_output,
    }


def run_profile(*, mode: str, copies: int, iterations: int) -> dict[str, object]:
    if copies < 1:
        raise ValueError("--copies must be positive")
    if iterations < 1:
        raise ValueError("--iterations must be positive")

    cases = (
        ("outlier_detection", "rows"),
        ("outlier_detection", "rt_count_threshold"),
        ("dbscan_clustering", "rows"),
        ("dbscan_clustering", "rt_core_flags"),
    )
    return {
        "goal": GOAL,
        "date": DATE,
        "backend": "optix" if mode == "optix" else "cpu_python_reference_dry_run",
        "mode": mode,
        "copies": copies,
        "iterations": iterations,
        "hardware_boundary": (
            "This is RTX-ready app-level phase instrumentation. A dry run uses CPU oracle paths; "
            "an OptiX run requires a built RTDL OptiX library and suitable NVIDIA hardware. "
            "GTX 1070 timing is not RT-core timing."
        ),
        "classification_change": False,
        "rtx_speedup_claim": False,
        "native_subphase_boundary": (
            "The current native fixed-radius ABI returns whole-call results only. Packing/BVH build, "
            "OptiX launch, and copy-back are not separately timed until the native API exposes counters."
        ),
        "cases": [
            _profile_case(mode=mode, app=app, path=path, copies=copies, iterations=iterations)
            for app, path in cases
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal697 OptiX fixed-radius app-level phase profiler.")
    parser.add_argument("--mode", choices=("dry-run", "optix"), default="dry-run")
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    payload = run_profile(mode=args.mode, copies=args.copies, iterations=args.iterations)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
