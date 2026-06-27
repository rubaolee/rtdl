from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path
from typing import Callable, Iterable

import numpy as np

from examples.benchmark_apps.hausdorff_xhd import rtdl_hausdorff_v2_function as hd


DatasetFactory = Callable[[int], tuple[np.ndarray, np.ndarray]]


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


def _demo_offset(point_count: int) -> tuple[np.ndarray, np.ndarray]:
    return (
        hd.make_demo_points(point_count, seed=11),
        hd.make_demo_points(point_count, seed=29, offset=(0.08, -0.06)),
    )


def _clustered_shift(point_count: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(3046)
    centers = np.asarray(
        [
            [-0.75, -0.5],
            [-0.2, 0.35],
            [0.45, -0.25],
            [0.7, 0.55],
        ],
        dtype=np.float64,
    )
    groups = np.arange(point_count, dtype=np.int64) % len(centers)
    noise_a = rng.normal(0.0, 0.045, size=(point_count, 2))
    noise_b = rng.normal(0.0, 0.045, size=(point_count, 2))
    points_a = centers[groups] + noise_a
    shifted_centers = centers + np.asarray([0.055, -0.025], dtype=np.float64)
    points_b = shifted_centers[groups] + noise_b
    return points_a.astype(np.float64), points_b.astype(np.float64)


def _ring_vs_spiral(point_count: int) -> tuple[np.ndarray, np.ndarray]:
    index = np.arange(point_count, dtype=np.float64)
    angles = index * (math.pi * (3.0 - math.sqrt(5.0)))
    radius_a = 0.55 + 0.035 * np.sin(index * 0.011)
    radius_b = 0.57 + 0.045 * np.cos(index * 0.009)
    points_a = np.column_stack((radius_a * np.cos(angles), radius_a * np.sin(angles)))
    points_b = np.column_stack(
        (
            1.05 * radius_b * np.cos(angles + 0.021) + 0.035,
            0.92 * radius_b * np.sin(angles + 0.021) - 0.02,
        )
    )
    return points_a.astype(np.float64), points_b.astype(np.float64)


def _adversarial_tail_outlier(point_count: int) -> tuple[np.ndarray, np.ndarray]:
    if point_count < 64:
        raise ValueError("adversarial_tail_outlier needs at least 64 points")
    rng = np.random.default_rng(4063)
    base_count = point_count - 1
    base = rng.uniform(-0.15, 0.15, size=(base_count, 2))
    points_a = np.vstack([base, np.asarray([[1.35, -1.20]], dtype=np.float64)])
    points_b = np.vstack([base + np.asarray([0.012, -0.008], dtype=np.float64), np.asarray([[0.18, -0.16]])])
    return points_a.astype(np.float64), points_b.astype(np.float64)


DATASETS: dict[str, DatasetFactory] = {
    "demo_offset": _demo_offset,
    "clustered_shift": _clustered_shift,
    "ring_vs_spiral": _ring_vs_spiral,
    "adversarial_tail_outlier": _adversarial_tail_outlier,
}


def _run_cupy(points_a: np.ndarray, points_b: np.ndarray) -> dict[str, object]:
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


def _run_active(
    points_a: np.ndarray,
    points_b: np.ndarray,
    *,
    seed_sample_count: int,
    target_points_per_group: int,
) -> dict[str, object]:
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


def _run_case(args: argparse.Namespace, dataset_name: str, point_count: int) -> dict[str, object]:
    points_a, points_b = DATASETS[dataset_name](point_count)

    print(f"[goal3046] dataset={dataset_name} size={point_count} warmup_start", flush=True)
    for index in range(args.warmup):
        _run_cupy(points_a, points_b)
        _run_active(
            points_a,
            points_b,
            seed_sample_count=args.seed_sample_count,
            target_points_per_group=args.target_points_per_group,
        )
        print(f"[goal3046] dataset={dataset_name} size={point_count} warmup={index + 1}/{args.warmup}", flush=True)

    cupy_rows: list[dict[str, object]] = []
    active_rows: list[dict[str, object]] = []
    for trial in range(args.trials):
        order = ("cupy", "active") if trial % 2 == 0 else ("active", "cupy")
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
                f"distance mismatch for dataset={dataset_name} size={point_count} trial={trial + 1}: "
                f"cupy={trial_payload['cupy']['distance']} active={trial_payload['active']['distance']}"
            )
        cupy_rows.append(trial_payload["cupy"])
        active_rows.append(trial_payload["active"])
        print(
            "[goal3046] "
            f"dataset={dataset_name} size={point_count} trial={trial + 1}/{args.trials} "
            f"cupy={trial_payload['cupy']['elapsed_sec']:.9f}s "
            f"active={trial_payload['active']['elapsed_sec']:.9f}s",
            flush=True,
        )

    cupy_stats = _timing_stats([float(row["elapsed_sec"]) for row in cupy_rows])
    active_stats = _timing_stats([float(row["elapsed_sec"]) for row in active_rows])
    return {
        "dataset": dataset_name,
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


def run(args: argparse.Namespace) -> dict[str, object]:
    rows = [_run_case(args, dataset, size) for dataset in args.datasets for size in args.sizes]
    speedups = [float(row["active_speedup_vs_cupy_median"]) for row in rows]
    return {
        "goal": "Goal3046",
        "method_under_test": "rtdl_rt_grouped_active_frontier_nearest_witness",
        "reference_method": "cupy_grouped_grid_rawkernel",
        "datasets": args.datasets,
        "sizes": args.sizes,
        "trials": args.trials,
        "warmup": args.warmup,
        "rows": rows,
        "all_rows_match_distance": all(bool(row["all_trials_match_distance"]) for row in rows),
        "min_median_speedup_vs_cupy": min(speedups),
        "max_median_speedup_vs_cupy": max(speedups),
        "median_of_median_speedups_vs_cupy": statistics.median(speedups),
        "v2_6_release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "claim_boundary": (
            "Internal dataset-diversity timing evidence only. Public Hausdorff "
            "RT-core speedup wording still needs external review, second-GPU "
            "confirmation, and reviewed dataset policy."
        ),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3046 Hausdorff active-frontier dataset-diversity harness.")
    parser.add_argument("--datasets", choices=sorted(DATASETS), nargs="+", default=sorted(DATASETS))
    parser.add_argument("--sizes", type=int, nargs="+", default=[32768, 65536])
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--seed-sample-count", type=int, default=1024)
    parser.add_argument("--target-points-per-group", type=int, default=512)
    parser.add_argument("--tolerance", type=float, default=1.0e-6)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.trials <= 0:
        raise ValueError("trials must be positive")
    if args.warmup < 0:
        raise ValueError("warmup must be non-negative")
    if args.seed_sample_count <= 0:
        raise ValueError("seed-sample-count must be positive")
    if args.target_points_per_group <= 0:
        raise ValueError("target-points-per-group must be positive")

    payload = run(args)
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
