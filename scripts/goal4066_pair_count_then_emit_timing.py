from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import statistics
import time
from typing import Any

import rtdsl as rt

from scripts.goal4036_partition_component_preview_vs_grouped_stream_timing import _clustered_points
from scripts.goal4036_partition_component_preview_vs_grouped_stream_timing import _road_points


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4066_pair_count_then_emit_timing_pod.json"


def _source_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def _summary(times: list[float]) -> dict[str, float]:
    return {
        "min_sec": min(times),
        "median_sec": statistics.median(times),
        "mean_sec": statistics.fmean(times),
    }


def _run_summary(cupy, points, *, pair_enumeration: str) -> tuple[float, dict[str, Any]]:
    cupy.cuda.Stream.null.synchronize()
    start = time.perf_counter()
    result = rt.build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
        points,
        radius=0.055,
        cell_factor=0.125,
        pair_enumeration=pair_enumeration,
    )
    cupy.cuda.Stream.null.synchronize()
    elapsed = time.perf_counter() - start
    return elapsed, result


def _bench(cupy, name: str, points, *, reps: int) -> dict[str, Any]:
    print("PROFILE_START", name, "points", len(points), flush=True)
    _, warm_bounded = _run_summary(cupy, points, pair_enumeration="device_bounded_offsets")
    _, warm_counted = _run_summary(cupy, points, pair_enumeration="device_count_then_emit")
    if warm_bounded["metadata"]["status_counts"] != warm_counted["metadata"]["status_counts"]:
        raise RuntimeError(f"status-count mismatch for {name}")
    if int(warm_bounded["metadata"]["pair_count"]) != int(warm_counted["metadata"]["pair_count"]):
        raise RuntimeError(f"pair-count mismatch for {name}")

    bounded_times: list[float] = []
    counted_times: list[float] = []
    for rep in range(int(reps)):
        elapsed, result = _run_summary(cupy, points, pair_enumeration="device_bounded_offsets")
        bounded_times.append(elapsed)
        print("RUN_BOUNDED", name, rep, f"{elapsed:.6f}", flush=True)
        if result["metadata"]["status_counts"] != warm_bounded["metadata"]["status_counts"]:
            raise RuntimeError(f"bounded status-count mismatch for {name}")
    for rep in range(int(reps)):
        elapsed, result = _run_summary(cupy, points, pair_enumeration="device_count_then_emit")
        counted_times.append(elapsed)
        print("RUN_COUNT_THEN_EMIT", name, rep, f"{elapsed:.6f}", flush=True)
        if result["metadata"]["status_counts"] != warm_bounded["metadata"]["status_counts"]:
            raise RuntimeError(f"count-then-emit status-count mismatch for {name}")

    bounded = _summary(bounded_times)
    counted = _summary(counted_times)
    bounded_capacity = int(warm_bounded["metadata"]["pair_capacity"])
    counted_capacity = int(warm_counted["metadata"]["pair_capacity"])
    row = {
        "profile": name,
        "point_count": len(points),
        "same_contract": True,
        "bounded_summary": bounded,
        "count_then_emit_summary": counted,
        "time_ratio_count_then_emit_over_bounded_median": counted["median_sec"] / bounded["median_sec"],
        "bounded_pair_capacity": bounded_capacity,
        "count_then_emit_pair_capacity": counted_capacity,
        "pair_capacity_reduction": bounded_capacity / max(1, counted_capacity),
        "pair_count": int(warm_counted["metadata"]["pair_count"]),
        "status_counts": dict(warm_counted["metadata"]["status_counts"]),
        "count_then_emit_metadata": {
            "pair_enumeration": warm_counted["metadata"]["pair_enumeration"],
            "pair_capacity_source": warm_counted["metadata"]["pair_capacity_source"],
            "device_pair_count_probe_used": warm_counted["metadata"]["device_pair_count_probe_used"],
            "device_pair_enumeration_used": warm_counted["metadata"]["device_pair_enumeration_used"],
            "overflow": warm_counted["metadata"]["overflow"],
        },
    }
    print("PROFILE_DONE", name, json.dumps(row, sort_keys=True), flush=True)
    return row


def run(output: pathlib.Path, reps: int) -> dict[str, Any]:
    import cupy

    profiles = [
        ("clustered3d_1024", _clustered_points(1024)),
        ("road3d_1024", _road_points(1024)),
        ("clustered3d_4096", _clustered_points(4096)),
        ("road3d_4096", _road_points(4096)),
        ("clustered3d_8192", _clustered_points(8192)),
        ("road3d_8192", _road_points(8192)),
    ]
    rows = [_bench(cupy, name, points, reps=reps) for name, points in profiles]
    payload = {
        "goal": "Goal4066",
        "schema": "rtdl.goal4066.pair_count_then_emit_timing.v1",
        "source_commit": _source_commit(),
        "claim_boundary": (
            "Internal preview timing for exact-capacity device pair enumeration. It does not "
            "promote partition_convergence_hybrid, authorize release, public speedup, broad RT-core, "
            "whole-app, hidden-dispatch, automatic partner selection, app-specific engine logic, "
            "native ABI addition, or true-zero-copy claims."
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
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--reps", type=int, default=5)
    args = parser.parse_args()
    payload = run(args.output, args.reps)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
