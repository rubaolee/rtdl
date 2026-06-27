from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path
from typing import Iterable

from examples.benchmark_apps.hausdorff_xhd import rtdl_hausdorff_v2_function as hd


def _percentile(sorted_values: list[float], fraction: float) -> float:
    if not sorted_values:
        raise ValueError("cannot compute percentile of empty list")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * fraction
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def _timing_stats(values: list[float]) -> dict[str, float | int | list[float]]:
    ordered = sorted(float(value) for value in values)
    q1 = _percentile(ordered, 0.25)
    q3 = _percentile(ordered, 0.75)
    return {
        "samples": values,
        "count": len(values),
        "min_sec": min(values),
        "median_sec": statistics.median(values),
        "max_sec": max(values),
        "q1_sec": q1,
        "q3_sec": q3,
        "iqr_sec": q3 - q1,
    }


def _run_cupy(points_a, points_b) -> dict[str, object]:
    result = hd.hausdorff_distance_2d(
        points_a,
        points_b,
        method="cupy_grouped_grid_rawkernel",
        warmup=0,
    )
    return {
        "distance": result.distance,
        "direction": result.direction,
        "source_index": result.source_index,
        "target_index": result.target_index,
        "elapsed_sec": result.elapsed_sec,
    }


def _run_active(points_a, points_b, *, seed_sample_count: int, target_points_per_group: int) -> dict[str, object]:
    result = hd.hausdorff_distance_2d_rt_grouped_active_frontier_nearest_witness(
        points_a,
        points_b,
        seed_sample_count=seed_sample_count,
        target_points_per_group=target_points_per_group,
    )
    return {
        "distance": result.distance,
        "direction": result.direction,
        "source_index": result.source_index,
        "target_index": result.target_index,
        "elapsed_sec": result.elapsed_sec,
        "rt_core_accelerated": result.rt_core_accelerated,
        "exact_value": result.exact_value,
    }


def _same_distance(left: dict[str, object], right: dict[str, object], tolerance: float) -> bool:
    return math.isclose(float(left["distance"]), float(right["distance"]), rel_tol=tolerance, abs_tol=tolerance)


def _run_size(args, point_count: int) -> dict[str, object]:
    points_a = hd.make_demo_points(point_count, seed=args.seed_a)
    points_b = hd.make_demo_points(point_count, seed=args.seed_b, offset=(args.offset_x, args.offset_y))

    print(f"[goal3045] size={point_count} warmup_start", flush=True)
    for index in range(args.warmup):
        _run_cupy(points_a, points_b)
        _run_active(
            points_a,
            points_b,
            seed_sample_count=args.seed_sample_count,
            target_points_per_group=args.target_points_per_group,
        )
        print(f"[goal3045] size={point_count} warmup={index + 1}/{args.warmup}", flush=True)

    cupy_rows: list[dict[str, object]] = []
    active_rows: list[dict[str, object]] = []
    for trial in range(args.trials):
        if trial % 2 == 0:
            order = ("cupy", "active")
        else:
            order = ("active", "cupy")
        trial_payload: dict[str, dict[str, object]] = {}
        for method in order:
            start = time.perf_counter()
            if method == "cupy":
                payload = _run_cupy(points_a, points_b)
            else:
                payload = _run_active(
                    points_a,
                    points_b,
                    seed_sample_count=args.seed_sample_count,
                    target_points_per_group=args.target_points_per_group,
                )
            payload["outer_elapsed_sec"] = time.perf_counter() - start
            trial_payload[method] = payload
        if not _same_distance(trial_payload["cupy"], trial_payload["active"], args.tolerance):
            raise RuntimeError(
                f"distance mismatch at size={point_count} trial={trial + 1}: "
                f"cupy={trial_payload['cupy']['distance']} active={trial_payload['active']['distance']}"
            )
        cupy_rows.append(trial_payload["cupy"])
        active_rows.append(trial_payload["active"])
        print(
            "[goal3045] "
            f"size={point_count} trial={trial + 1}/{args.trials} "
            f"cupy={trial_payload['cupy']['elapsed_sec']:.9f}s "
            f"active={trial_payload['active']['elapsed_sec']:.9f}s",
            flush=True,
        )

    cupy_samples = [float(row["elapsed_sec"]) for row in cupy_rows]
    active_samples = [float(row["elapsed_sec"]) for row in active_rows]
    cupy_stats = _timing_stats(cupy_samples)
    active_stats = _timing_stats(active_samples)
    return {
        "points_a": point_count,
        "points_b": point_count,
        "seed_sample_count": args.seed_sample_count,
        "target_points_per_group": args.target_points_per_group,
        "cupy_grouped_grid": cupy_stats,
        "active_frontier": active_stats,
        "active_vs_cupy_median_ratio": active_stats["median_sec"] / cupy_stats["median_sec"],
        "active_speedup_vs_cupy_median": cupy_stats["median_sec"] / active_stats["median_sec"],
        "all_trials_match_distance": True,
        "reference_distance": float(cupy_rows[0]["distance"]),
        "reference_direction": cupy_rows[0]["direction"],
        "active_direction": active_rows[0]["direction"],
        "reference_source_index": cupy_rows[0]["source_index"],
        "reference_target_index": cupy_rows[0]["target_index"],
        "active_source_index": active_rows[0]["source_index"],
        "active_target_index": active_rows[0]["target_index"],
    }


def run(args) -> dict[str, object]:
    rows = [_run_size(args, size) for size in args.sizes]
    return {
        "goal": "Goal3045",
        "method_under_test": "rtdl_rt_grouped_active_frontier_nearest_witness",
        "reference_method": "cupy_grouped_grid_rawkernel",
        "sizes": args.sizes,
        "trials": args.trials,
        "warmup": args.warmup,
        "rows": rows,
        "all_rows_match_distance": all(row["all_trials_match_distance"] for row in rows),
        "best_median_speedup_vs_cupy": max(row["active_speedup_vs_cupy_median"] for row in rows),
        "v2_6_release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "claim_boundary": (
            "Internal repeated same-process timing evidence. Public Hausdorff "
            "RT-core speedup wording still needs review, dataset diversity, and "
            "second-GPU confirmation."
        ),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3045 Hausdorff active-frontier repeated timing harness.")
    parser.add_argument("--sizes", type=int, nargs="+", default=[16384, 65536, 131072])
    parser.add_argument("--trials", type=int, default=10)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--seed-sample-count", type=int, default=1024)
    parser.add_argument("--target-points-per-group", type=int, default=512)
    parser.add_argument("--seed-a", type=int, default=11)
    parser.add_argument("--seed-b", type=int, default=29)
    parser.add_argument("--offset-x", type=float, default=0.08)
    parser.add_argument("--offset-y", type=float, default=-0.06)
    parser.add_argument("--tolerance", type=float, default=1.0e-6)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.trials <= 0:
        raise ValueError("trials must be positive")
    if args.warmup < 0:
        raise ValueError("warmup must be non-negative")

    payload = run(args)
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
