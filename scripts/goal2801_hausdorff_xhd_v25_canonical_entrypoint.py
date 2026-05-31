from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path
from statistics import median
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.hausdorff_xhd import (  # noqa: E402
    rtdl_hausdorff_v2_function as hd,
)


GOAL2801_ENTRYPOINT_VERSION = "rtdl.goal2801.hausdorff_xhd_v2_5_canonical_entrypoint.v1"
DEFAULT_RTDL_METHOD = "rtdl_rt_grouped_adaptive_nearest_witness"
DEFAULT_RTDL_WARMUP = 1
DEFAULT_REPEAT = 3
DEFAULT_ADAPTIVE_GROWTH_FACTOR = 8.0
DEFAULT_ADAPTIVE_TARGET_POINTS_PER_GROUP = 512
CLAIM_BOUNDARY = {
    "canonical_entrypoint": True,
    "public_speedup_claim_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "rtdl_beats_xhd_claim_authorized": False,
    "rtdl_beats_cupy_grid_claim_authorized": False,
    "broad_rt_core_speedup_claim_authorized": False,
    "triton_speedup_claim_authorized": False,
    "paper_reproduction_claim_authorized": False,
    "native_engine_customization": False,
}


def _check_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _run_rtdl_method(a_points, b_points, *, rtdl_method: str):
    if rtdl_method == "rtdl_rt_grouped_adaptive_nearest_witness":
        return hd.hausdorff_distance_2d_rt_grouped_adaptive_nearest_witness(
            a_points,
            b_points,
            growth_factor=DEFAULT_ADAPTIVE_GROWTH_FACTOR,
            target_points_per_group=DEFAULT_ADAPTIVE_TARGET_POINTS_PER_GROUP,
        )
    if rtdl_method == "rtdl_rt_grouped_reduced_nearest_witness":
        return hd.hausdorff_distance_2d_rt_grouped_reduced_nearest_witness(a_points, b_points)
    raise ValueError(
        "rtdl_method must be rtdl_rt_grouped_adaptive_nearest_witness or "
        "rtdl_rt_grouped_reduced_nearest_witness"
    )


def _median_by_elapsed(results):
    ordered = sorted(results, key=lambda item: float(item.elapsed_sec))
    return ordered[len(ordered) // 2]


def run_goal2801_hausdorff_entrypoint(
    *,
    points_a: int,
    points_b: int,
    seed_a: int = 11,
    seed_b: int = 29,
    offset_x: float = 0.08,
    offset_y: float = -0.06,
    rtdl_method: str = DEFAULT_RTDL_METHOD,
    rtdl_warmup: int = DEFAULT_RTDL_WARMUP,
    repeat: int = DEFAULT_REPEAT,
    exact_tolerance: float = 1.0e-9,
) -> dict[str, Any]:
    started = time.perf_counter()
    repeat_count = max(1, int(repeat))
    a_points = hd.make_demo_points(int(points_a), seed=int(seed_a))
    b_points = hd.make_demo_points(int(points_b), seed=int(seed_b), offset=(float(offset_x), float(offset_y)))

    baseline_warmup_started = time.perf_counter()
    hd.hausdorff_distance_2d(
        a_points,
        b_points,
        method="cupy_grouped_grid_rawkernel",
        warmup=1,
    )
    baseline_warmup_elapsed_sec = time.perf_counter() - baseline_warmup_started
    baseline_started = time.perf_counter()
    baseline_runs = tuple(
        hd.hausdorff_distance_2d(
            a_points,
            b_points,
            method="cupy_grouped_grid_rawkernel",
            warmup=0,
        )
        for _ in range(repeat_count)
    )
    baseline = _median_by_elapsed(baseline_runs)
    baseline_elapsed_sec = time.perf_counter() - baseline_started

    rtdl_warmup_elapsed_sec = 0.0
    for _ in range(max(0, int(rtdl_warmup))):
        warmup_started = time.perf_counter()
        _run_rtdl_method(a_points, b_points, rtdl_method=rtdl_method)
        rtdl_warmup_elapsed_sec += time.perf_counter() - warmup_started

    rtdl_started = time.perf_counter()
    rtdl_runs = tuple(_run_rtdl_method(a_points, b_points, rtdl_method=rtdl_method) for _ in range(repeat_count))
    rtdl_result = _median_by_elapsed(rtdl_runs)
    rtdl_elapsed_sec = time.perf_counter() - rtdl_started

    baseline_payload = asdict(baseline)
    rtdl_payload = asdict(rtdl_result)
    distance_error = abs(float(rtdl_result.distance) - float(baseline.distance))
    witness_distance_match = math.isclose(
        float(rtdl_result.distance),
        float(baseline.distance),
        rel_tol=float(exact_tolerance),
        abs_tol=float(exact_tolerance),
    )
    status = "pass" if witness_distance_match else "mismatch"
    return {
        "goal": "Goal2801",
        "entrypoint_version": GOAL2801_ENTRYPOINT_VERSION,
        "status": status,
        "app": "hausdorff_xhd",
        "benchmark_track": "canonical_exact_hausdorff_entrypoint",
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "scenario": {
            "points_a": int(points_a),
            "points_b": int(points_b),
            "seed_a": int(seed_a),
            "seed_b": int(seed_b),
            "offset_x": float(offset_x),
            "offset_y": float(offset_y),
            "exact_tolerance": float(exact_tolerance),
            "rtdl_warmup": int(rtdl_warmup),
            "repeat": repeat_count,
        },
        "baseline": {
            "method": "cupy_grouped_grid_rawkernel",
            "uses_rtdl": False,
            "uses_rt_cores": False,
            "exact_value": True,
            "elapsed_sec": float(baseline.elapsed_sec),
            "elapsed_runs_sec": tuple(float(run.elapsed_sec) for run in baseline_runs),
            "median_elapsed_sec": float(median(float(run.elapsed_sec) for run in baseline_runs)),
            "warmup_elapsed_sec": baseline_warmup_elapsed_sec,
            "wrapper_elapsed_sec": baseline_elapsed_sec,
            "result": baseline_payload,
        },
        "rtdl": {
            "method": rtdl_method,
            "uses_rtdl": True,
            "uses_rt_cores": True,
            "exact_value": True,
            "warmup_elapsed_sec": rtdl_warmup_elapsed_sec,
            "adaptive_growth_factor": DEFAULT_ADAPTIVE_GROWTH_FACTOR
            if rtdl_method == "rtdl_rt_grouped_adaptive_nearest_witness"
            else None,
            "adaptive_target_points_per_group": DEFAULT_ADAPTIVE_TARGET_POINTS_PER_GROUP
            if rtdl_method == "rtdl_rt_grouped_adaptive_nearest_witness"
            else None,
            "elapsed_sec": float(rtdl_result.elapsed_sec),
            "elapsed_runs_sec": tuple(float(run.elapsed_sec) for run in rtdl_runs),
            "median_elapsed_sec": float(median(float(run.elapsed_sec) for run in rtdl_runs)),
            "wrapper_elapsed_sec": rtdl_elapsed_sec,
            "result": rtdl_payload,
        },
        "distance_error": distance_error,
        "matches_exact_baseline": witness_distance_match,
        "rtdl_over_cupy_grid_elapsed_ratio": (
            float(rtdl_result.elapsed_sec) / float(baseline.elapsed_sec)
            if float(baseline.elapsed_sec) > 0.0
            else None
        ),
        "claim_boundary": CLAIM_BOUNDARY,
        "elapsed_sec": time.perf_counter() - started,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal2801 Hausdorff/X-HD v2.5 canonical exact entrypoint.")
    parser.add_argument("--points-a", type=int, default=4096)
    parser.add_argument("--points-b", type=int, default=4096)
    parser.add_argument("--seed-a", type=int, default=11)
    parser.add_argument("--seed-b", type=int, default=29)
    parser.add_argument("--offset-x", type=float, default=0.08)
    parser.add_argument("--offset-y", type=float, default=-0.06)
    parser.add_argument(
        "--rtdl-method",
        choices=("rtdl_rt_grouped_adaptive_nearest_witness", "rtdl_rt_grouped_reduced_nearest_witness"),
        default=DEFAULT_RTDL_METHOD,
    )
    parser.add_argument("--exact-tolerance", type=float, default=1.0e-9)
    parser.add_argument("--rtdl-warmup", type=int, default=DEFAULT_RTDL_WARMUP)
    parser.add_argument("--repeat", type=int, default=DEFAULT_REPEAT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    payload = run_goal2801_hausdorff_entrypoint(
        points_a=args.points_a,
        points_b=args.points_b,
        seed_a=args.seed_a,
        seed_b=args.seed_b,
        offset_x=args.offset_x,
        offset_y=args.offset_y,
        rtdl_method=args.rtdl_method,
        rtdl_warmup=args.rtdl_warmup,
        repeat=args.repeat,
        exact_tolerance=args.exact_tolerance,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
