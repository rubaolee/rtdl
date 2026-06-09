from __future__ import annotations

import argparse
import json
import pathlib
import platform
import statistics
import subprocess
import time
from typing import Any

import rtdsl as rt
from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    make_rt_dbscan_points,
    run_rt_dbscan_benchmark,
)
from scripts.goal4085_partition_summary_build_feasibility import PROFILE_RADII


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4105_direct_status_vs_current_route_pod.json"


def _source_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def _source_tracked_worktree_dirty() -> bool:
    return bool(
        subprocess.check_output(
            ["git", "status", "--short", "--untracked-files=no"],
            cwd=ROOT,
            text=True,
        ).strip()
    )


def _nvidia_smi() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ""


def _summary(values: list[float]) -> dict[str, float]:
    return {
        "min_sec": min(values),
        "median_sec": statistics.median(values),
        "mean_sec": statistics.fmean(values),
        "max_sec": max(values),
    }


def _component_size_signature(signature: dict[str, Any]) -> tuple[int, ...]:
    if "component_sizes" in signature:
        return tuple(sorted(int(value) for value in signature["component_sizes"]))
    cluster_sizes = signature.get("cluster_sizes")
    if isinstance(cluster_sizes, dict):
        return tuple(sorted(int(value) for value in cluster_sizes.values()))
    raise ValueError(f"unsupported signature shape: {signature!r}")


def _timed_direct(points, *, radius: float, cell_factor: float):
    import cupy

    cupy.cuda.Stream.null.synchronize()
    start = time.perf_counter()
    result = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_direct_status_union_preview_3d(
        points,
        radius=radius,
        cell_factor=cell_factor,
        validate_against_materialized_signature=False,
    )
    cupy.cuda.Stream.null.synchronize()
    return time.perf_counter() - start, result


def _run_profile(
    *,
    profile: str,
    point_count: int,
    seed: int,
    cell_factor: float,
    repeat: int,
    warmup: int,
) -> dict[str, Any]:
    radius = PROFILE_RADII[profile]
    points = make_rt_dbscan_points(profile, point_count=point_count, seed=seed)
    samples: list[dict[str, Any]] = []
    for run_index in range(warmup + repeat):
        measured = run_index >= warmup
        label = "MEASURE" if measured else "WARMUP"
        print(f"STRICT_ROUTE_{label}_START {profile} point_count={point_count} run={run_index}", flush=True)

        direct_sec, direct = _timed_direct(points, radius=radius, cell_factor=cell_factor)
        current = run_rt_dbscan_benchmark(
            mode="optix_rt_core_grouped_stream_numba_column_signature_3d",
            dataset=profile,
            point_count=point_count,
            radius=None,
            min_neighbors=None,
            seed=seed,
            partner="numba",
            include_rows=False,
            validate=False,
            repeat=1,
            warmup=0,
        )
        direct_signature = tuple(int(value) for value in direct["columns"]["component_size_signature"])
        current_signature = _component_size_signature(current["signature"])
        if direct_signature != current_signature:
            raise AssertionError(f"{profile} signature mismatch: {direct_signature} != {current_signature}")
        current_sec = float(current["elapsed_sec"])
        direct_metadata = dict(direct["metadata"])
        current_metadata = dict(current["metadata"])
        sample = {
            "run_index": run_index,
            "measured": measured,
            "profile": profile,
            "point_count": point_count,
            "direct_status_union_sec": direct_sec,
            "current_route_sec": current_sec,
            "current_over_direct_speedup": current_sec / direct_sec if direct_sec > 0 else None,
            "direct_component_count": int(direct_metadata["component_count"]),
            "partition_count": int(direct_metadata["partition_count"]),
            "direct_pair_count": int(direct_metadata["pair_count"]),
            "direct_union_iterations": int(direct_metadata["union_iterations"]),
            "current_path": current_metadata.get("path"),
            "current_partner": current_metadata.get("partner"),
            "current_rt_core_accelerated": bool(current_metadata.get("rt_core_accelerated", False)),
            "same_signature": True,
            "direct_partition_summary_materialized": bool(direct_metadata["partition_summary_materialized"]),
            "direct_near_pair_columns_materialized": bool(direct_metadata["near_pair_columns_materialized"]),
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "native_abi_added": False,
        }
        samples.append(sample)
        print(
            "STRICT_ROUTE_SAMPLE "
            + json.dumps(
                {
                    "profile": profile,
                    "run_index": run_index,
                    "measured": measured,
                    "direct_status_union_sec": direct_sec,
                    "current_route_sec": current_sec,
                    "speedup": sample["current_over_direct_speedup"],
                    "partition_count": sample["partition_count"],
                    "pair_count": sample["direct_pair_count"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
    measured_samples = [sample for sample in samples if sample["measured"]]
    direct_values = [float(sample["direct_status_union_sec"]) for sample in measured_samples]
    current_values = [float(sample["current_route_sec"]) for sample in measured_samples]
    reference = measured_samples[-1]
    direct_median = statistics.median(direct_values)
    current_median = statistics.median(current_values)
    return {
        "profile": profile,
        "point_count": point_count,
        "radius": float(radius),
        "cell_factor": float(cell_factor),
        "direct_status_union_sec": _summary(direct_values),
        "current_route_sec": _summary(current_values),
        "current_over_direct_speedup_median": current_median / direct_median if direct_median > 0 else None,
        "direct_is_faster_than_current": direct_median < current_median,
        "partition_count": reference["partition_count"],
        "direct_pair_count": reference["direct_pair_count"],
        "direct_union_iterations": reference["direct_union_iterations"],
        "current_path": reference["current_path"],
        "current_partner": reference["current_partner"],
        "current_rt_core_accelerated": reference["current_rt_core_accelerated"],
        "same_signature": True,
        "direct_partition_summary_materialized": False,
        "direct_near_pair_columns_materialized": False,
        "samples": samples,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "native_abi_added": False,
    }


def run(
    *,
    output: pathlib.Path,
    profiles: tuple[str, ...],
    point_count: int,
    seed: int,
    cell_factor: float,
    repeat: int,
    warmup: int,
) -> dict[str, Any]:
    rows = [
        _run_profile(
            profile=profile,
            point_count=point_count,
            seed=seed,
            cell_factor=cell_factor,
            repeat=repeat,
            warmup=warmup,
        )
        for profile in profiles
    ]
    payload = {
        "schema": "rtdl.goal4105.direct_status_vs_current_route.v1",
        "goal": "Goal4105",
        "source_commit": _source_commit(),
        "source_tracked_worktree_dirty": _source_tracked_worktree_dirty(),
        "platform": platform.platform(),
        "gpu": _nvidia_smi(),
        "point_count": point_count,
        "cell_factor": cell_factor,
        "profiles": list(profiles),
        "repeat": repeat,
        "warmup": warmup,
        "rows": rows,
        "claim_boundary": (
            "Internal current-route comparison evidence only. It does not promote "
            "partition_convergence_hybrid, authorize release, public speedup, broad RT-core, "
            "whole-app, paper-reproduction, hidden-dispatch, automatic partner selection, "
            "app-specific engine logic, native ABI addition, or true-zero-copy claims."
        ),
        "partition_convergence_hybrid_promoted": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "native_abi_added": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE {output}", flush=True)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--profiles", nargs="+", default=["clustered3d", "road3d", "ngsim_dense"])
    parser.add_argument("--point-count", type=int, default=65536)
    parser.add_argument("--seed", type=int, default=20260519)
    parser.add_argument("--cell-factor", type=float, default=0.125)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=1)
    args = parser.parse_args()
    run(
        output=args.output,
        profiles=tuple(str(profile) for profile in args.profiles),
        point_count=int(args.point_count),
        seed=int(args.seed),
        cell_factor=float(args.cell_factor),
        repeat=int(args.repeat),
        warmup=int(args.warmup),
    )


if __name__ == "__main__":
    main()
