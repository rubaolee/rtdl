#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
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
from rtdsl.optix_runtime import (
    pack_points,
    _load_optix_library,
    _find_optional_backend_symbol,
    _check_status,
    get_last_phase_timings,
    OptixRowView,
    _RtdlFixedRadiusCountRow
)


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


def _profile_fixed_radius(n_points: int, radius: float, threshold: int) -> dict[str, float]:
    phases: dict[str, float] = {}
    total_start = time.perf_counter()

    # Phase 1: Python Input Construction
    def make_input():
        return [rt.Point(id=i, x=float(i), y=float(i)) for i in range(n_points)]
    
    python_input, elapsed = _time_call(make_input)
    phases["python_input_construction"] = elapsed

    # Phase 2: Packing
    def do_pack():
        return pack_points(records=python_input, dimension=2)
    
    packed_data, elapsed = _time_call(do_pack)
    phases["packing"] = elapsed

    # Phase 3: Launch and Traversal
    def do_launch():
        lib = _load_optix_library()
        symbol = _find_optional_backend_symbol(lib, "rtdl_optix_run_fixed_radius_count_threshold")
        if symbol is None:
            raise RuntimeError("Symbol rtdl_optix_run_fixed_radius_count_threshold not found")
        rows_ptr = ctypes.POINTER(_RtdlFixedRadiusCountRow)()
        row_count = ctypes.c_size_t()
        error = ctypes.create_string_buffer(4096)
        status = symbol(
            packed_data.records,
            packed_data.count,
            packed_data.records,
            packed_data.count,
            ctypes.c_double(radius),
            ctypes.c_size_t(threshold),
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
        _check_status(status, error)
        return OptixRowView(
            library=lib,
            rows_ptr=rows_ptr,
            row_count=row_count.value,
            row_type=_RtdlFixedRadiusCountRow,
            field_names=("query_id", "neighbor_count", "threshold_reached"),
        )

    view, elapsed = _time_call(do_launch)
    phases["backend_call_total"] = elapsed
    timings = get_last_phase_timings()
    if timings:
        phases["c_bvh_build"] = timings["bvh_build"]
        phases["c_optix_launch_and_traversal"] = timings["traversal"]
        phases["c_copy_back"] = timings["copyback"]
        phases["c_ffi_overhead"] = elapsed - sum(timings.values())

    # Phase 4 & 5: Copy-back and Dictionary Materialization
    def do_postprocess():
        return tuple(
            {
                "query_id": int(row["query_id"]),
                "neighbor_count": int(row["neighbor_count"]),
                "threshold_reached": int(row["threshold_reached"]),
            }
            for row in view.to_dict_rows()
        )
    
    result, elapsed = _time_call(do_postprocess)
    phases["python_postprocess"] = elapsed
    
    view.close()

    phases["total"] = time.perf_counter() - total_start
    return phases


def _profile(iterations: int, n_points: int, radius: float, threshold: int) -> dict[str, object]:
    phase_samples: dict[str, list[float]] = {}
    
    for _ in range(iterations):
        phases = _profile_fixed_radius(n_points, radius, threshold)
        for phase, elapsed in phases.items():
            phase_samples.setdefault(phase, []).append(elapsed)

    return {
        "workload": "fixed_radius_count_threshold",
        "iterations": iterations,
        "n_points": n_points,
        "phase_stats": {phase: _stats(samples) for phase, samples in sorted(phase_samples.items())},
        "boundary": "This profiler separates data mapping from OptiX execution. Evidence of RT-core acceleration must come from the isolated 'c_optix_launch_and_traversal' phase on RTX hardware. Do not claim RT-core status based solely on padding optimizations or backend-call totals.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal727 OptiX Fixed Radius Phase-Split Profiler.")
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--points", type=int, default=1000)
    parser.add_argument("--radius", type=float, default=2.0)
    parser.add_argument("--threshold", type=int, default=1)
    args = parser.parse_args(argv)
    if args.iterations < 1:
        raise ValueError("--iterations must be positive")
    print(json.dumps(_profile(args.iterations, args.points, args.radius, args.threshold), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
