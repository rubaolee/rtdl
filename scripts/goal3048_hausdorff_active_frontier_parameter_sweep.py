from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path
from typing import Iterable

from examples.benchmark_apps.hausdorff_xhd import rtdl_hausdorff_v2_function as hd
from scripts import goal3046_hausdorff_active_frontier_dataset_diversity as diversity


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
    }


def _same_distance(reference: float, candidate: float, tolerance: float) -> bool:
    return math.isclose(float(reference), float(candidate), rel_tol=tolerance, abs_tol=tolerance)


def _run_config(args: argparse.Namespace, points_a, points_b, reference_distance: float, seed: int, group: int) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for trial in range(args.trials):
        payload = _run_active(points_a, points_b, seed_sample_count=seed, target_points_per_group=group)
        if not _same_distance(reference_distance, float(payload["distance"]), args.tolerance):
            raise RuntimeError(
                f"distance mismatch for seed={seed} group={group} trial={trial + 1}: "
                f"reference={reference_distance} active={payload['distance']}"
            )
        rows.append(payload)
        print(
            f"[goal3048] seed={seed} group={group} trial={trial + 1}/{args.trials} "
            f"active={payload['elapsed_sec']:.9f}s",
            flush=True,
        )
    stats = _timing_stats([float(row["elapsed_sec"]) for row in rows])
    return {
        "seed_sample_count": seed,
        "target_points_per_group": group,
        "active_frontier": stats,
        "all_trials_match_distance": True,
        "direction": rows[0]["direction"],
        "source_index": rows[0]["source_index"],
        "target_index": rows[0]["target_index"],
    }


def _run_case(args: argparse.Namespace, dataset: str, size: int) -> dict[str, object]:
    points_a, points_b = diversity.DATASETS[dataset](size)
    reference = hd.hausdorff_distance_2d(points_a, points_b, method="cupy_grouped_grid_rawkernel", warmup=0)
    print(
        f"[goal3048] dataset={dataset} size={size} reference={reference.distance:.12f} "
        f"cupy={reference.elapsed_sec:.9f}s",
        flush=True,
    )

    for index in range(args.warmup):
        _run_active(
            points_a,
            points_b,
            seed_sample_count=args.seed_sample_counts[0],
            target_points_per_group=args.target_points_per_groups[0],
        )
        print(f"[goal3048] dataset={dataset} size={size} warmup={index + 1}/{args.warmup}", flush=True)

    configs = [
        _run_config(args, points_a, points_b, float(reference.distance), seed, group)
        for seed in args.seed_sample_counts
        for group in args.target_points_per_groups
    ]
    best = min(configs, key=lambda row: float(row["active_frontier"]["median_sec"]))
    current_policy = next(
        row
        for row in configs
        if int(row["seed_sample_count"]) == args.current_seed_sample_count
        and int(row["target_points_per_group"]) == args.current_target_points_per_group
    )
    return {
        "dataset": dataset,
        "points_a": size,
        "points_b": size,
        "reference_method": "cupy_grouped_grid_rawkernel",
        "reference_distance": float(reference.distance),
        "reference_elapsed_sec": float(reference.elapsed_sec),
        "configs": configs,
        "best_config": best,
        "current_policy_config": current_policy,
        "best_vs_current_policy_median_ratio": float(best["active_frontier"]["median_sec"])
        / float(current_policy["active_frontier"]["median_sec"]),
        "best_speedup_vs_reference_median": float(reference.elapsed_sec) / float(best["active_frontier"]["median_sec"]),
        "all_configs_match_distance": all(bool(row["all_trials_match_distance"]) for row in configs),
    }


def run(args: argparse.Namespace) -> dict[str, object]:
    rows = [_run_case(args, dataset, size) for dataset in args.datasets for size in args.sizes]
    best_pairs = [
        (int(row["best_config"]["seed_sample_count"]), int(row["best_config"]["target_points_per_group"]))
        for row in rows
    ]
    pair_counts = {
        f"seed_{seed}_group_{group}": sum(1 for pair in best_pairs if pair == (seed, group))
        for seed in args.seed_sample_counts
        for group in args.target_points_per_groups
    }
    return {
        "goal": "Goal3048",
        "method_under_test": "rtdl_rt_grouped_active_frontier_nearest_witness",
        "datasets": args.datasets,
        "sizes": args.sizes,
        "seed_sample_counts": args.seed_sample_counts,
        "target_points_per_groups": args.target_points_per_groups,
        "current_seed_sample_count": args.current_seed_sample_count,
        "current_target_points_per_group": args.current_target_points_per_group,
        "trials": args.trials,
        "warmup": args.warmup,
        "rows": rows,
        "best_config_frequency": pair_counts,
        "all_rows_match_distance": all(bool(row["all_configs_match_distance"]) for row in rows),
        "min_best_vs_current_policy_median_ratio": min(float(row["best_vs_current_policy_median_ratio"]) for row in rows),
        "median_best_vs_current_policy_median_ratio": statistics.median(
            float(row["best_vs_current_policy_median_ratio"]) for row in rows
        ),
        "v2_6_release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "default_policy_change_authorized": False,
        "claim_boundary": (
            "Internal active-frontier tuning evidence only. A default policy "
            "change needs reviewed multi-dataset evidence and a focused code "
            "change; this artifact alone does not authorize public claims."
        ),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3048 Hausdorff active-frontier seed/group parameter sweep.")
    parser.add_argument("--datasets", choices=sorted(diversity.DATASETS), nargs="+", default=sorted(diversity.DATASETS))
    parser.add_argument("--sizes", type=int, nargs="+", default=[65536, 131072])
    parser.add_argument("--seed-sample-counts", type=int, nargs="+", default=[512, 1024, 2048, 8192])
    parser.add_argument("--target-points-per-groups", type=int, nargs="+", default=[512, 1024, 2048])
    parser.add_argument("--current-seed-sample-count", type=int, default=1024)
    parser.add_argument("--current-target-points-per-group", type=int, default=512)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--tolerance", type=float, default=1.0e-6)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.trials <= 0:
        raise ValueError("trials must be positive")
    if args.warmup < 0:
        raise ValueError("warmup must be non-negative")
    if args.current_seed_sample_count not in args.seed_sample_counts:
        raise ValueError("current-seed-sample-count must be included in seed-sample-counts")
    if args.current_target_points_per_group not in args.target_points_per_groups:
        raise ValueError("current-target-points-per-group must be included in target-points-per-groups")

    payload = run(args)
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
