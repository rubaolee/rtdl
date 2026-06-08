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
from scripts.goal4036_partition_component_preview_vs_grouped_stream_timing import _component_size_signature
from scripts.goal4036_partition_component_preview_vs_grouped_stream_timing import _road_points


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4041_partition_device_ambiguous_union_timing_pod.json"


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


def _run_once(cupy, points, summary: dict[str, Any], *, radius: float, cell_factor: float, mode: str):
    cupy.cuda.Stream.null.synchronize()
    start = time.perf_counter()
    result = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d(
        points,
        radius=radius,
        cell_factor=cell_factor,
        partition_summary=summary,
        partition_union_execution="cupy_safe_full",
        ambiguous_union_execution=mode,
        validate_summary_same_contract=False,
    )
    cupy.cuda.Stream.null.synchronize()
    elapsed = time.perf_counter() - start
    if result["metadata"]["status"] != "accept":
        raise RuntimeError(f"component preview failed in {mode}: {result['metadata']}")
    return elapsed, result


def _bench(cupy, name: str, points, *, reps: int) -> dict[str, Any]:
    radius = 0.055
    cell_factor = 0.125
    print("PROFILE_START", name, "points", len(points), flush=True)
    summary = rt.build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
        points,
        radius=radius,
        cell_factor=cell_factor,
        pair_enumeration="device_bounded_offsets",
    )
    _, host_warm = _run_once(cupy, points, summary, radius=radius, cell_factor=cell_factor, mode="host")
    _, device_warm = _run_once(
        cupy,
        points,
        summary,
        radius=radius,
        cell_factor=cell_factor,
        mode="cupy_partition_points",
    )
    host_signature = _component_size_signature(host_warm["columns"]["component_labels"])
    device_signature = _component_size_signature(device_warm["columns"]["component_labels"])
    if host_signature != device_signature:
        raise RuntimeError(f"signature mismatch for {name}")

    host_times: list[float] = []
    device_times: list[float] = []
    for rep in range(int(reps)):
        elapsed, result = _run_once(cupy, points, summary, radius=radius, cell_factor=cell_factor, mode="host")
        if _component_size_signature(result["columns"]["component_labels"]) != host_signature:
            raise RuntimeError(f"host signature mismatch for {name}")
        host_times.append(elapsed)
        print("RUN_HOST_AMBIG", name, rep, f"{elapsed:.6f}", flush=True)
    for rep in range(int(reps)):
        elapsed, result = _run_once(
            cupy,
            points,
            summary,
            radius=radius,
            cell_factor=cell_factor,
            mode="cupy_partition_points",
        )
        if _component_size_signature(result["columns"]["component_labels"]) != host_signature:
            raise RuntimeError(f"device signature mismatch for {name}")
        device_times.append(elapsed)
        print("RUN_DEVICE_AMBIG", name, rep, f"{elapsed:.6f}", flush=True)

    host_summary = _summary(host_times)
    device_summary = _summary(device_times)
    row = {
        "profile": name,
        "point_count": len(points),
        "component_signature_match": True,
        "host_ambiguous_repeated_run": host_summary,
        "device_ambiguous_repeated_run": device_summary,
        "device_over_host_min": host_summary["min_sec"] / device_summary["min_sec"],
        "device_over_host_median": host_summary["median_sec"] / device_summary["median_sec"],
        "summary_metadata": {
            "pair_enumeration": summary["metadata"]["pair_enumeration"],
            "pair_capacity_source": summary["metadata"]["pair_capacity_source"],
            "partition_count": summary["metadata"]["partition_count"],
            "pair_count": summary["metadata"]["pair_count"],
            "status_counts": dict(summary["metadata"]["status_counts"]),
        },
        "device_metadata": {
            "ambiguous_union_execution": device_warm["metadata"]["ambiguous_union_execution"],
            "device_ambiguous_union_used": device_warm["metadata"]["device_ambiguous_union_used"],
            "ambiguous_partition_pairs": device_warm["metadata"]["ambiguous_partition_pairs"],
            "ambiguous_point_comparisons": device_warm["metadata"]["ambiguous_point_comparisons"],
            "ambiguous_positive_edges": device_warm["metadata"]["ambiguous_positive_edges"],
            "ambiguous_union_skipped_reason": device_warm["metadata"].get("ambiguous_union_skipped_reason"),
        },
        "host_metadata": {
            "ambiguous_union_execution": host_warm["metadata"]["ambiguous_union_execution"],
            "device_ambiguous_union_used": host_warm["metadata"]["device_ambiguous_union_used"],
            "ambiguous_partition_pairs": host_warm["metadata"]["ambiguous_partition_pairs"],
            "ambiguous_point_comparisons": host_warm["metadata"]["ambiguous_point_comparisons"],
            "ambiguous_positive_edges": host_warm["metadata"]["ambiguous_positive_edges"],
        },
    }
    print("PROFILE_DONE", name, json.dumps(row, sort_keys=True), flush=True)
    return row


def run(output: pathlib.Path, reps: int) -> dict[str, Any]:
    import cupy

    profiles = [
        ("clustered3d_1024", _clustered_points(1024)),
        ("road3d_1024", _road_points(1024)),
        ("clustered3d_2048", _clustered_points(2048)),
        ("road3d_2048", _road_points(2048)),
        ("clustered3d_4096", _clustered_points(4096)),
        ("road3d_4096", _road_points(4096)),
        ("clustered3d_8192", _clustered_points(8192)),
        ("road3d_8192", _road_points(8192)),
    ]
    rows = [_bench(cupy, name, points, reps=reps) for name, points in profiles]
    payload = {
        "goal": "Goal4041",
        "schema": "rtdl.goal4041.partition_device_ambiguous_union_timing.v1",
        "source_commit": _source_commit(),
        "claim_boundary": (
            "Internal subpath timing for host versus device ambiguous partition-union "
            "continuation. It does not promote partition_convergence_hybrid or authorize "
            "release, public speedup, broad RT-core, whole-app, hidden-dispatch, automatic "
            "partner selection, app-specific engine logic, or true-zero-copy claims."
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
