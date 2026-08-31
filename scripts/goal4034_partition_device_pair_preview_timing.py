from __future__ import annotations

import argparse
import json
import math
import pathlib
import statistics
import time
from typing import Any

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4034_partition_device_pair_preview_timing_pod.json"


def _clustered_points(n: int) -> list[tuple[float, float, float]]:
    points: list[tuple[float, float, float]] = []
    centers = ((0.0, 0.0, 0.0), (3.0, 0.0, 0.0), (0.0, 3.0, 0.0), (3.0, 3.0, 0.0))
    side = max(1, int(round((n / len(centers)) ** (1.0 / 3.0))))
    step = 0.018
    for cx, cy, cz in centers:
        for i in range(side):
            for j in range(side):
                for k in range(side):
                    if len(points) >= n:
                        break
                    points.append((cx + i * step, cy + j * step, cz + k * step))
                if len(points) >= n:
                    break
            if len(points) >= n:
                break
        if len(points) >= n:
            break
    while len(points) < n:
        idx = len(points)
        points.append((6.0 + idx * 0.001, 0.0, 0.0))
    return points


def _road_points(n: int) -> list[tuple[float, float, float]]:
    return [
        (i * 0.006, math.sin(i * 0.025) * 0.04, (i % 17) * 0.002)
        for i in range(n)
    ]


def _summarize(times: list[float]) -> dict[str, float]:
    return {
        "min_sec": min(times),
        "median_sec": statistics.median(times),
        "mean_sec": statistics.fmean(times),
    }


def _time_builder(
    *,
    cupy,
    points: list[tuple[float, float, float]],
    radius: float,
    cell_factor: float,
    mode: str,
    pair_capacity: int | None,
    reps: int,
) -> tuple[dict[str, float], dict[str, Any]]:
    times: list[float] = []
    last_output: dict[str, Any] | None = None
    for rep in range(reps):
        cupy.cuda.Stream.null.synchronize()
        start = time.perf_counter()
        last_output = rt.build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
            points,
            radius=radius,
            cell_factor=cell_factor,
            pair_enumeration=mode,
            pair_capacity=pair_capacity,
        )
        cupy.cuda.Stream.null.synchronize()
        elapsed = time.perf_counter() - start
        validation = rt.validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            points,
            radius=radius,
            cell_factor=cell_factor,
            candidate=last_output,
            float_abs_tol=1.0e-5,
        )
        print(
            "RUN",
            mode,
            "rep",
            rep,
            "sec",
            f"{elapsed:.6f}",
            "status",
            validation["status"],
            flush=True,
        )
        if validation["status"] != "accept":
            raise RuntimeError(f"{mode} validation failed: {validation}")
        times.append(elapsed)
    assert last_output is not None
    return _summarize(times), {
        "pair_count": int(last_output["metadata"]["pair_count"]),
        "partition_count": int(last_output["metadata"]["partition_count"]),
        "status_counts": dict(last_output["metadata"]["status_counts"]),
        "pair_enumeration": last_output["metadata"]["pair_enumeration"],
        "complete_candidate_coverage": bool(last_output["metadata"]["complete_candidate_coverage"]),
    }


def run(output: pathlib.Path, reps: int) -> dict[str, Any]:
    import cupy

    radius = 0.055
    cell_factor = 0.125
    profiles = [
        ("clustered3d_2048", _clustered_points(2048)),
        ("road3d_2048", _road_points(2048)),
        ("clustered3d_4096", _clustered_points(4096)),
        ("road3d_4096", _road_points(4096)),
    ]
    rows: list[dict[str, Any]] = []
    for name, points in profiles:
        print("PROFILE_START", name, "points", len(points), flush=True)
        capacity_reference = rt.build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
            points,
            radius=radius,
            cell_factor=cell_factor,
            pair_enumeration="host",
        )
        pair_capacity = int(capacity_reference["metadata"]["pair_count"])
        print(
            "CAPACITY",
            name,
            "pairs",
            pair_capacity,
            "partitions",
            capacity_reference["metadata"]["partition_count"],
            flush=True,
        )
        # Compile/warm the raw kernel before timing device_bounded_offsets.
        warm = rt.build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
            points,
            radius=radius,
            cell_factor=cell_factor,
            pair_enumeration="device_bounded_offsets",
            pair_capacity=pair_capacity,
        )
        warm_validation = rt.validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            points,
            radius=radius,
            cell_factor=cell_factor,
            candidate=warm,
            float_abs_tol=1.0e-5,
        )
        if warm_validation["status"] != "accept":
            raise RuntimeError(f"warmup validation failed: {warm_validation}")
        host_summary, host_meta = _time_builder(
            cupy=cupy,
            points=points,
            radius=radius,
            cell_factor=cell_factor,
            mode="host",
            pair_capacity=None,
            reps=reps,
        )
        device_summary, device_meta = _time_builder(
            cupy=cupy,
            points=points,
            radius=radius,
            cell_factor=cell_factor,
            mode="device_bounded_offsets",
            pair_capacity=pair_capacity,
            reps=reps,
        )
        row = {
            "profile": name,
            "point_count": len(points),
            "radius": radius,
            "cell_factor": cell_factor,
            "pair_capacity_source": "host_preview_warmup_not_counted",
            "host_pair_enumeration": host_summary,
            "device_bounded_offsets": device_summary,
            "pair_count": pair_capacity,
            "partition_count": host_meta["partition_count"],
            "status_counts": host_meta["status_counts"],
            "same_contract_status": "accept",
            "device_min_vs_host_min_speedup": host_summary["min_sec"] / device_summary["min_sec"],
            "device_median_vs_host_median_speedup": host_summary["median_sec"] / device_summary["median_sec"],
            "device_mode_metadata": device_meta,
        }
        print("PROFILE_DONE", name, json.dumps(row, sort_keys=True), flush=True)
        rows.append(row)

    payload = {
        "goal": "Goal4034",
        "schema": "rtdl.goal4034.partition_device_pair_preview_timing.v1",
        "claim_boundary": (
            "This artifact compares CuPy preview pair-enumeration modes only. "
            "It does not promote partition_convergence_hybrid, authorize release wording, "
            "or authorize public speedup, broad RT-core, whole-app, hidden-dispatch, "
            "automatic-partner-selection, app-specific-engine, or true-zero-copy claims."
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "partition_convergence_hybrid_promoted": False,
        "native_abi_added": False,
        "rows": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print("WROTE", output, flush=True)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--reps", type=int, default=3)
    args = parser.parse_args()
    if args.reps < 1:
        raise SystemExit("--reps must be positive")
    run(args.output, args.reps)


if __name__ == "__main__":
    main()

