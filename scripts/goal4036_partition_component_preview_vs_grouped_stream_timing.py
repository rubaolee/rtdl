from __future__ import annotations

import argparse
import json
import math
import pathlib
import statistics
import time
from types import SimpleNamespace
from typing import Any

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4036_partition_component_preview_vs_grouped_stream_timing_pod.json"


def _clustered_points(n: int) -> list[SimpleNamespace]:
    points: list[SimpleNamespace] = []
    centers = ((0.0, 0.0, 0.0), (3.0, 0.0, 0.0), (0.0, 3.0, 0.0), (3.0, 3.0, 0.0))
    side = max(1, int(round((n / len(centers)) ** (1.0 / 3.0))))
    step = 0.018
    for cx, cy, cz in centers:
        for i in range(side):
            for j in range(side):
                for k in range(side):
                    if len(points) >= n:
                        break
                    idx = len(points)
                    points.append(SimpleNamespace(id=idx, x=cx + i * step, y=cy + j * step, z=cz + k * step))
                if len(points) >= n:
                    break
            if len(points) >= n:
                break
        if len(points) >= n:
            break
    while len(points) < n:
        idx = len(points)
        points.append(SimpleNamespace(id=idx, x=6.0 + idx * 0.001, y=0.0, z=0.0))
    return points


def _road_points(n: int) -> list[SimpleNamespace]:
    return [
        SimpleNamespace(id=i, x=i * 0.006, y=math.sin(i * 0.025) * 0.04, z=(i % 17) * 0.002)
        for i in range(n)
    ]


def _labels_to_list(labels) -> list[int]:
    if hasattr(labels, "get"):
        labels = labels.get()
    if hasattr(labels, "tolist"):
        labels = labels.tolist()
    return [int(value) for value in labels]


def _component_size_signature(labels) -> list[int]:
    counts: dict[int, int] = {}
    for label in _labels_to_list(labels):
        counts[label] = counts.get(label, 0) + 1
    return sorted(counts.values())


def _summary(times: list[float]) -> dict[str, float]:
    return {
        "min_sec": min(times),
        "median_sec": statistics.median(times),
        "mean_sec": statistics.fmean(times),
    }


def _preview_once(cupy, points, *, radius: float, cell_factor: float) -> tuple[float, dict[str, Any]]:
    cupy.cuda.Stream.null.synchronize()
    start = time.perf_counter()
    result = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d(
        points,
        radius=radius,
        cell_factor=cell_factor,
        partition_union_execution="cupy_safe_full",
        validate_summary_same_contract=False,
    )
    cupy.cuda.Stream.null.synchronize()
    elapsed = time.perf_counter() - start
    if result["metadata"]["status"] != "accept":
        raise RuntimeError(f"preview failed: {result['metadata']}")
    return elapsed, result


def _grouped_prepare_run_once(cupy, points, *, radius: float) -> tuple[float, dict[str, Any]]:
    cupy.cuda.Stream.null.synchronize()
    start = time.perf_counter()
    with rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d(
        points,
        radius=radius,
        component_threshold=1,
        backend="optix",
        partner="cupy",
        strategy="grouped_stream",
    ) as prepared:
        result = rt.fixed_radius_graph_component_labels_3d_v2_8(
            prepared,
            component_threshold=1,
            return_metadata=True,
        )
    cupy.cuda.Stream.null.synchronize()
    elapsed = time.perf_counter() - start
    return elapsed, result


def _bench_profile(cupy, name: str, points: list[SimpleNamespace], *, reps: int) -> dict[str, Any]:
    radius = 0.055
    cell_factor = 0.125
    print("PROFILE_START", name, "points", len(points), flush=True)

    # Warm preview kernels, then time warmed one-shot preview.
    _, warm_preview = _preview_once(cupy, points, radius=radius, cell_factor=cell_factor)
    preview_one_shot_sec, preview_one_shot = _preview_once(cupy, points, radius=radius, cell_factor=cell_factor)
    grouped_one_shot_sec, grouped_one_shot = _grouped_prepare_run_once(cupy, points, radius=radius)

    preview_signature = _component_size_signature(preview_one_shot["columns"]["component_labels"])
    grouped_signature = _component_size_signature(grouped_one_shot["columns"]["component_labels"])
    if preview_signature != grouped_signature:
        raise RuntimeError(f"component signature mismatch for {name}")

    with rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d(
        points,
        radius=radius,
        component_threshold=1,
        backend="optix",
        partner="cupy",
        strategy="grouped_stream",
    ) as prepared:
        grouped_warm = rt.fixed_radius_graph_component_labels_3d_v2_8(
            prepared,
            component_threshold=1,
            return_metadata=True,
        )
        grouped_signature = _component_size_signature(grouped_warm["columns"]["component_labels"])
        reused_summary = rt.build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
            points,
            radius=radius,
            cell_factor=cell_factor,
            pair_enumeration="device_bounded_offsets",
        )
        rt.build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d(
            points,
            radius=radius,
            cell_factor=cell_factor,
            partition_summary=reused_summary,
            partition_union_execution="cupy_safe_full",
            validate_summary_same_contract=False,
        )
        preview_times: list[float] = []
        reuse_times: list[float] = []
        grouped_times: list[float] = []
        for rep in range(reps):
            elapsed, preview = _preview_once(cupy, points, radius=radius, cell_factor=cell_factor)
            preview_times.append(elapsed)
            if _component_size_signature(preview["columns"]["component_labels"]) != grouped_signature:
                raise RuntimeError(f"preview repeated signature mismatch for {name}")
            print("RUN_PREVIEW", name, rep, f"{elapsed:.6f}", flush=True)
        for rep in range(reps):
            cupy.cuda.Stream.null.synchronize()
            start = time.perf_counter()
            reused = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d(
                points,
                radius=radius,
                cell_factor=cell_factor,
                partition_summary=reused_summary,
                partition_union_execution="cupy_safe_full",
                validate_summary_same_contract=False,
            )
            cupy.cuda.Stream.null.synchronize()
            elapsed = time.perf_counter() - start
            reuse_times.append(elapsed)
            if _component_size_signature(reused["columns"]["component_labels"]) != grouped_signature:
                raise RuntimeError(f"reused preview signature mismatch for {name}")
            print("RUN_REUSE", name, rep, f"{elapsed:.6f}", flush=True)
        for rep in range(reps):
            cupy.cuda.Stream.null.synchronize()
            start = time.perf_counter()
            grouped = rt.fixed_radius_graph_component_labels_3d_v2_8(
                prepared,
                component_threshold=1,
                return_metadata=True,
            )
            cupy.cuda.Stream.null.synchronize()
            elapsed = time.perf_counter() - start
            grouped_times.append(elapsed)
            if _component_size_signature(grouped["columns"]["component_labels"]) != grouped_signature:
                raise RuntimeError(f"grouped repeated signature mismatch for {name}")
            print("RUN_GROUPED", name, rep, f"{elapsed:.6f}", flush=True)

    row = {
        "profile": name,
        "point_count": len(points),
        "radius": radius,
        "cell_factor": cell_factor,
        "component_signature_match": True,
        "preview_one_shot_warmed_sec": preview_one_shot_sec,
        "grouped_prepare_run_sec": grouped_one_shot_sec,
        "grouped_prepare_run_over_preview_one_shot": grouped_one_shot_sec / preview_one_shot_sec,
        "preview_repeated_run": _summary(preview_times),
        "partition_summary_reuse_repeated_run": _summary(reuse_times),
        "grouped_prepared_repeated_run": _summary(grouped_times),
        "grouped_prepared_repeated_over_preview_repeated": min(grouped_times) / min(preview_times),
        "grouped_prepared_repeated_over_reuse_repeated": min(grouped_times) / min(reuse_times),
        "preview_metadata": {
            "partition_union_execution": preview_one_shot["metadata"]["partition_union_execution"],
            "partition_summary_pair_enumeration": preview_one_shot["metadata"]["partition_summary_pair_enumeration"],
            "partition_summary_pair_capacity_source": preview_one_shot["metadata"]["partition_summary_pair_capacity_source"],
            "summary_same_contract_validation_enabled": preview_one_shot["metadata"]["summary_same_contract_validation_enabled"],
            "safe_full_partition_union_iterations": preview_one_shot["metadata"]["safe_full_partition_union_iterations"],
            "ambiguous_partition_pairs": preview_one_shot["metadata"]["ambiguous_partition_pairs"],
            "component_count": preview_one_shot["metadata"]["component_count"],
        },
        "grouped_metadata": {
            "rt_core_accelerated": bool(grouped_one_shot["metadata"].get("rt_core_accelerated", False)),
            "front_door": grouped_one_shot["metadata"].get("front_door"),
            "user_selected_partner": grouped_one_shot["metadata"].get("user_selected_partner"),
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
    rows = [_bench_profile(cupy, name, points, reps=reps) for name, points in profiles]
    payload = {
        "goal": "Goal4036",
        "schema": "rtdl.goal4036.partition_component_preview_vs_grouped_stream_timing.v1",
        "claim_boundary": (
            "This artifact compares internal v2.8 candidate routes. It does not promote "
            "partition_convergence_hybrid or authorize release, public speedup, broad RT-core, "
            "whole-app, hidden-dispatch, automatic-partner-selection, app-specific-engine, "
            "or true-zero-copy claims."
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
