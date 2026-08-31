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
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4046_partition_component_signature_timing_pod.json"


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


def _run_labels(cupy, points, summary: dict[str, Any], *, radius: float, cell_factor: float):
    cupy.cuda.Stream.null.synchronize()
    start = time.perf_counter()
    result = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d(
        points,
        radius=radius,
        cell_factor=cell_factor,
        partition_summary=summary,
        partition_union_execution="cupy_safe_full",
        ambiguous_union_execution="cupy_partition_points",
        validate_summary_same_contract=False,
    )
    cupy.cuda.Stream.null.synchronize()
    elapsed = time.perf_counter() - start
    if result["metadata"]["status"] != "accept":
        raise RuntimeError(f"label preview failed: {result['metadata']}")
    return elapsed, result


def _run_signature(cupy, points, summary: dict[str, Any], *, radius: float, cell_factor: float):
    cupy.cuda.Stream.null.synchronize()
    start = time.perf_counter()
    result = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
        points,
        radius=radius,
        cell_factor=cell_factor,
        partition_summary=summary,
        ambiguous_union_execution="cupy_partition_points",
        validate_summary_same_contract=False,
    )
    cupy.cuda.Stream.null.synchronize()
    elapsed = time.perf_counter() - start
    if result["metadata"]["status"] != "accept":
        raise RuntimeError(f"signature preview failed: {result['metadata']}")
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
    _, label_warm = _run_labels(cupy, points, summary, radius=radius, cell_factor=cell_factor)
    _, signature_warm = _run_signature(cupy, points, summary, radius=radius, cell_factor=cell_factor)
    label_signature = tuple(_component_size_signature(label_warm["columns"]["component_labels"]))
    if tuple(signature_warm["columns"]["component_size_signature"]) != label_signature:
        raise RuntimeError(f"signature mismatch for {name}")

    label_times: list[float] = []
    signature_times: list[float] = []
    for rep in range(int(reps)):
        elapsed, result = _run_labels(cupy, points, summary, radius=radius, cell_factor=cell_factor)
        if tuple(_component_size_signature(result["columns"]["component_labels"])) != label_signature:
            raise RuntimeError(f"label signature mismatch for {name}")
        label_times.append(elapsed)
        print("RUN_LABELS", name, rep, f"{elapsed:.6f}", flush=True)
    for rep in range(int(reps)):
        elapsed, result = _run_signature(cupy, points, summary, radius=radius, cell_factor=cell_factor)
        if tuple(result["columns"]["component_size_signature"]) != label_signature:
            raise RuntimeError(f"signature mismatch for {name}")
        signature_times.append(elapsed)
        print("RUN_SIGNATURE", name, rep, f"{elapsed:.6f}", flush=True)

    label_summary = _summary(label_times)
    signature_summary = _summary(signature_times)
    row = {
        "profile": name,
        "point_count": len(points),
        "component_signature_match": True,
        "label_repeated_run": label_summary,
        "signature_repeated_run": signature_summary,
        "label_over_signature_min": label_summary["min_sec"] / signature_summary["min_sec"],
        "label_over_signature_median": label_summary["median_sec"] / signature_summary["median_sec"],
        "summary_metadata": {
            "pair_enumeration": summary["metadata"]["pair_enumeration"],
            "pair_capacity_source": summary["metadata"]["pair_capacity_source"],
            "partition_count": summary["metadata"]["partition_count"],
            "pair_count": summary["metadata"]["pair_count"],
            "status_counts": dict(summary["metadata"]["status_counts"]),
        },
        "signature_metadata": {
            "label_materialization": signature_warm["metadata"]["label_materialization"],
            "ambiguous_union_execution": signature_warm["metadata"]["ambiguous_union_execution"],
            "device_ambiguous_union_used": signature_warm["metadata"]["device_ambiguous_union_used"],
            "ambiguous_union_skipped_reason": signature_warm["metadata"]["ambiguous_union_skipped_reason"],
            "component_count": signature_warm["metadata"]["component_count"],
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
        "goal": "Goal4046",
        "schema": "rtdl.goal4046.partition_component_signature_timing.v1",
        "source_commit": _source_commit(),
        "claim_boundary": (
            "Internal subpath timing for component-size signature versus full component-label "
            "materialization over the partition-convergence candidate. It does not promote "
            "partition_convergence_hybrid or authorize release, public speedup, broad RT-core, "
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
