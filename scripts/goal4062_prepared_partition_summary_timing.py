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
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4062_prepared_partition_summary_timing_pod.json"


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


def _run_one_shot_signature(cupy, points, *, radius: float, cell_factor: float) -> tuple[float, dict[str, Any]]:
    cupy.cuda.Stream.null.synchronize()
    start = time.perf_counter()
    result = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
        points,
        radius=radius,
        cell_factor=cell_factor,
        pair_enumeration="device_bounded_offsets",
        validate_summary_same_contract=False,
    )
    cupy.cuda.Stream.null.synchronize()
    elapsed = time.perf_counter() - start
    if result["metadata"]["status"] != "accept":
        raise RuntimeError(f"one-shot signature failed: {result['metadata']}")
    return elapsed, result


def _prepare(cupy, points, *, radius: float, cell_factor: float):
    cupy.cuda.Stream.null.synchronize()
    start = time.perf_counter()
    prepared = rt.prepare_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
        points,
        radius=radius,
        cell_factor=cell_factor,
        pair_enumeration="device_bounded_offsets",
        validate_summary_same_contract=False,
    )
    cupy.cuda.Stream.null.synchronize()
    return time.perf_counter() - start, prepared


def _run_prepared_signature(cupy, prepared) -> tuple[float, dict[str, Any]]:
    cupy.cuda.Stream.null.synchronize()
    start = time.perf_counter()
    result = rt.run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_preview_3d(
        prepared,
        validate_summary_same_contract=False,
    )
    cupy.cuda.Stream.null.synchronize()
    elapsed = time.perf_counter() - start
    if result["metadata"]["status"] != "accept":
        raise RuntimeError(f"prepared signature failed: {result['metadata']}")
    return elapsed, result


def _bench(cupy, name: str, points, *, reps: int) -> dict[str, Any]:
    radius = 0.055
    cell_factor = 0.125
    print("PROFILE_START", name, "points", len(points), flush=True)

    warm_one_shot_sec, warm_one_shot = _run_one_shot_signature(
        cupy,
        points,
        radius=radius,
        cell_factor=cell_factor,
    )
    prepare_sec, prepared = _prepare(cupy, points, radius=radius, cell_factor=cell_factor)
    warm_prepared_sec, warm_prepared = _run_prepared_signature(cupy, prepared)
    expected_signature = tuple(warm_one_shot["columns"]["component_size_signature"])
    if tuple(warm_prepared["columns"]["component_size_signature"]) != expected_signature:
        raise RuntimeError(f"prepared signature mismatch for {name}")

    one_shot_times: list[float] = []
    prepared_times: list[float] = []
    for rep in range(int(reps)):
        elapsed, result = _run_one_shot_signature(cupy, points, radius=radius, cell_factor=cell_factor)
        if tuple(result["columns"]["component_size_signature"]) != expected_signature:
            raise RuntimeError(f"one-shot signature mismatch for {name}")
        one_shot_times.append(elapsed)
        print("RUN_ONE_SHOT_SIGNATURE", name, rep, f"{elapsed:.6f}", flush=True)
    for rep in range(int(reps)):
        elapsed, result = _run_prepared_signature(cupy, prepared)
        if tuple(result["columns"]["component_size_signature"]) != expected_signature:
            raise RuntimeError(f"prepared signature mismatch for {name}")
        prepared_times.append(elapsed)
        print("RUN_PREPARED_SIGNATURE", name, rep, f"{elapsed:.6f}", flush=True)

    one_shot = _summary(one_shot_times)
    prepared_summary = _summary(prepared_times)
    replay_speedup_min = one_shot["min_sec"] / prepared_summary["min_sec"]
    replay_speedup_median = one_shot["median_sec"] / prepared_summary["median_sec"]
    amortized_three_run_speedup = (
        one_shot["median_sec"] * 3.0
    ) / (prepare_sec + prepared_summary["median_sec"] * 3.0)
    row = {
        "profile": name,
        "point_count": len(points),
        "component_signature_match": True,
        "warm_one_shot_sec": warm_one_shot_sec,
        "prepare_sec": prepare_sec,
        "warm_prepared_sec": warm_prepared_sec,
        "one_shot_signature": one_shot,
        "prepared_signature_replay": prepared_summary,
        "prepared_replay_speedup_min": replay_speedup_min,
        "prepared_replay_speedup_median": replay_speedup_median,
        "prepared_three_run_amortized_speedup_median": amortized_three_run_speedup,
        "prepared_handle_metadata": prepared.to_metadata(),
        "prepared_signature_metadata": {
            "prepared_partition_summary_reused": warm_prepared["metadata"]["prepared_partition_summary_reused"],
            "prepared_partition_summary_handle_status": warm_prepared["metadata"][
                "prepared_partition_summary_handle_status"
            ],
            "partition_summary_reused": warm_prepared["metadata"]["partition_summary_reused"],
            "label_materialization": warm_prepared["metadata"]["label_materialization"],
            "component_count": warm_prepared["metadata"]["component_count"],
            "ambiguous_partition_pairs": warm_prepared["metadata"]["ambiguous_partition_pairs"],
            "device_ambiguous_union_used": warm_prepared["metadata"]["device_ambiguous_union_used"],
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
        "goal": "Goal4062",
        "schema": "rtdl.goal4062.prepared_partition_summary_timing.v1",
        "source_commit": _source_commit(),
        "claim_boundary": (
            "Internal preview timing for explicit prepared partition-summary reuse. It does not "
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
