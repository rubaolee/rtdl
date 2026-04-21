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
from rtdsl.optix_runtime import pack_points, get_last_phase_timings
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


def _profile_phases(copies: int) -> dict[str, float]:
    phases: dict[str, float] = {}
    total_start = time.perf_counter()

    def make_input():
        return outlier_app.make_outlier_case(copies=copies)["points"]
    
    python_input, elapsed = _time_call(make_input)
    phases["python_input_construction"] = elapsed

    def do_pack():
        return pack_points(records=python_input, dimension=2)
    
    packed_data, elapsed = _time_call(do_pack)
    phases["packing"] = elapsed

    def do_launch():
        return rt.fixed_radius_count_threshold_2d_optix(
            python_input,
            python_input,
            radius=outlier_app.RADIUS,
            threshold=outlier_app.MIN_NEIGHBORS_INCLUDING_SELF,
        )

    count_rows, full_launch_elapsed = _time_call(do_launch)

    timings = get_last_phase_timings()
    if timings:
        phases["c_bvh_build"] = timings["bvh_build"]
        phases["c_optix_launch_and_traversal"] = timings["traversal"]
        phases["c_copy_back"] = timings["copyback"]
        c_total = sum(timings.values())
        phases["c_ffi_overhead"] = full_launch_elapsed - c_total
    else:
        phases["optix_call_total"] = full_launch_elapsed

    def do_postprocess():
        return outlier_app._density_rows_from_count_rows(python_input, count_rows)
    
    result, elapsed = _time_call(do_postprocess)
    phases["scalar_app_postprocess"] = elapsed
    
    phases["total"] = time.perf_counter() - total_start
    return phases


def _profile(iterations: int, copies: int) -> dict[str, object]:
    phase_samples: dict[str, list[float]] = {}
    
    for _ in range(iterations):
        phases = _profile_phases(copies)
        for phase, elapsed in phases.items():
            phase_samples.setdefault(phase, []).append(elapsed)

    # Correctness and Comparison Runs
    cpu_run = outlier_app.run_app(backend="cpu_python_reference", copies=copies)
    optix_rows_run = outlier_app.run_app(backend="optix", copies=copies, optix_summary_mode="rows")
    optix_summary_run = outlier_app.run_app(backend="optix", copies=copies, optix_summary_mode="rt_count_threshold")

    return {
        "workload": "optix_fixed_radius_summary_mode",
        "iterations": iterations,
        "points_per_copy": 8,
        "copies": copies,
        "phase_stats": {phase: _stats(samples) for phase, samples in sorted(phase_samples.items())},
        "comparisons": {
            "cpu_oracle_matched": True, # baseline
            "optix_rows": {
                "matched_oracle": optix_rows_run["matches_oracle"],
                "neighbor_row_count_materialized": optix_rows_run["neighbor_row_count"],
            },
            "optix_summary": {
                "matched_oracle": optix_summary_run["matches_oracle"],
                "neighbor_row_count_materialized": optix_summary_run["neighbor_row_count"],
            }
        },
        "boundary": "Genuine RTX-class evidence must exclusively use the isolated 'c_optix_launch_and_traversal' phase. Any speedups from 'python_input' or 'packing' do not qualify as hardware RT-core acceleration.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal695 OptiX Fixed Radius Phase-Split Profiler.")
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--copies", type=int, default=200)
    args = parser.parse_args(argv)
    if args.iterations < 1:
        raise ValueError("--iterations must be positive")
    print(json.dumps(_profile(args.iterations, args.copies), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
