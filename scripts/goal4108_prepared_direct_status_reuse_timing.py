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
from examples.benchmark_apps.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    make_rt_dbscan_points,
    run_rt_dbscan_benchmark,
)
from scripts.goal4085_partition_summary_build_feasibility import PROFILE_RADII


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4108_prepared_direct_status_reuse_timing_pod.json"


def _source_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


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


def _sync() -> None:
    import cupy

    cupy.cuda.Stream.null.synchronize()


def _run_profile(
    *,
    profile: str,
    point_count: int,
    seed: int,
    cell_factor: float,
    repeat: int,
    warmup: int,
) -> dict[str, Any]:
    radius = float(PROFILE_RADII[profile])
    print(f"PREP_DIRECT_PROFILE_START {profile} point_count={point_count}", flush=True)

    start = time.perf_counter()
    points = make_rt_dbscan_points(profile, point_count=point_count, seed=seed)
    point_generation_sec = time.perf_counter() - start

    _sync()
    start = time.perf_counter()
    prepared = rt.prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_preview_3d(
        points,
        radius=radius,
        cell_factor=cell_factor,
    )
    _sync()
    prepare_sec = time.perf_counter() - start

    prepared_samples: list[dict[str, Any]] = []
    one_shot_samples: list[dict[str, Any]] = []
    current_samples: list[dict[str, Any]] = []
    for run_index in range(warmup + repeat):
        measured = run_index >= warmup
        label = "MEASURE" if measured else "WARMUP"

        print(f"PREP_DIRECT_{label}_PREPARED {profile} run={run_index}", flush=True)
        _sync()
        start = time.perf_counter()
        prepared_result = rt.run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_direct_status_union_preview_3d(
            prepared,
            validate_against_materialized_signature=False,
        )
        _sync()
        prepared_sec = time.perf_counter() - start

        print(f"PREP_DIRECT_{label}_ONE_SHOT {profile} run={run_index}", flush=True)
        _sync()
        start = time.perf_counter()
        one_shot_result = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_direct_status_union_preview_3d(
            points,
            radius=radius,
            cell_factor=cell_factor,
            validate_against_materialized_signature=False,
        )
        _sync()
        one_shot_sec = time.perf_counter() - start

        print(f"PREP_DIRECT_{label}_CURRENT_ROUTE {profile} run={run_index}", flush=True)
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

        prepared_signature = tuple(int(value) for value in prepared_result["columns"]["component_size_signature"])
        one_shot_signature = tuple(int(value) for value in one_shot_result["columns"]["component_size_signature"])
        current_signature = _component_size_signature(current["signature"])
        if prepared_signature != one_shot_signature or prepared_signature != current_signature:
            raise AssertionError(
                f"{profile} signature mismatch: prepared={prepared_signature} "
                f"one_shot={one_shot_signature} current={current_signature}"
            )

        prepared_samples.append(
            {
                "run_index": run_index,
                "measured": measured,
                "sec": prepared_sec,
                "metadata": prepared_result["metadata"],
            }
        )
        one_shot_samples.append(
            {
                "run_index": run_index,
                "measured": measured,
                "sec": one_shot_sec,
                "metadata": one_shot_result["metadata"],
            }
        )
        current_samples.append(
            {
                "run_index": run_index,
                "measured": measured,
                "sec": float(current["elapsed_sec"]),
                "metadata": current["metadata"],
            }
        )
        print(
            "PREP_DIRECT_SAMPLE "
            + json.dumps(
                {
                    "profile": profile,
                    "run_index": run_index,
                    "measured": measured,
                    "prepared_sec": prepared_sec,
                    "one_shot_sec": one_shot_sec,
                    "current_sec": float(current["elapsed_sec"]),
                },
                sort_keys=True,
            ),
            flush=True,
        )

    prepared.close()
    prepared_values = [float(sample["sec"]) for sample in prepared_samples if sample["measured"]]
    one_shot_values = [float(sample["sec"]) for sample in one_shot_samples if sample["measured"]]
    current_values = [float(sample["sec"]) for sample in current_samples if sample["measured"]]
    prepared_median = statistics.median(prepared_values)
    one_shot_median = statistics.median(one_shot_values)
    current_median = statistics.median(current_values)
    return {
        "profile": profile,
        "point_count": point_count,
        "radius": radius,
        "cell_factor": cell_factor,
        "point_generation_sec": point_generation_sec,
        "prepared_direct_status_prepare_sec": prepare_sec,
        "prepared_direct_status_replay_sec": _summary(prepared_values),
        "one_shot_direct_status_sec": _summary(one_shot_values),
        "current_route_sec": _summary(current_values),
        "prepared_replay_over_one_shot_speedup_median": one_shot_median / prepared_median if prepared_median > 0 else None,
        "prepared_replay_over_current_route_speedup_median": current_median / prepared_median if prepared_median > 0 else None,
        "prepared_three_run_amortized_sec": (prepare_sec + sum(prepared_values)) / len(prepared_values),
        "one_shot_direct_status_median_sec": one_shot_median,
        "current_route_median_sec": current_median,
        "same_signature": True,
        "prepared_handle_metadata": prepared.to_metadata(),
        "prepared_samples": prepared_samples,
        "one_shot_samples": one_shot_samples,
        "current_samples": current_samples,
        "partition_convergence_hybrid_promoted": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
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
        "schema": "rtdl.goal4108.prepared_direct_status_reuse_timing.v1",
        "goal": "Goal4108",
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
            "Internal prepared direct-status reuse evidence only. It does not promote "
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
