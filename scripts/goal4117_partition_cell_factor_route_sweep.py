from __future__ import annotations

import argparse
import json
import pathlib
import platform
import subprocess
from typing import Any

from examples.benchmark_apps.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    DEFAULT_DATASET_CONFIG,
    run_rt_dbscan_benchmark,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4117_partition_cell_factor_route_sweep_pod.json"
DEFAULT_PROFILE_FACTORS = {
    "clustered3d": (0.0625, 0.125, 0.25, 0.5, 1.0),
    "road3d": (0.0625, 0.125, 0.25, 0.5, 1.0),
    "ngsim_dense": (0.0625, 0.125, 0.25, 0.5, 1.0),
}


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


def _component_size_signature(signature: dict[str, Any]) -> tuple[int, ...]:
    if "component_sizes" in signature:
        return tuple(sorted(int(value) for value in signature["component_sizes"]))
    cluster_sizes = signature.get("cluster_sizes")
    if isinstance(cluster_sizes, dict):
        return tuple(sorted(int(value) for value in cluster_sizes.values()))
    raise ValueError(f"unsupported signature shape: {signature!r}")


def _current_prepare_sec(metadata: dict[str, Any]) -> float:
    timing = metadata.get("benchmark_timing_breakdown", {})
    if isinstance(timing, dict):
        host = timing.get("host_observed_sec", {})
        if isinstance(host, dict) and "prepare_sec" in host:
            return float(host["prepare_sec"])
    return 0.0


def _run_current_route(
    *,
    profile: str,
    point_count: int,
    seed: int,
    repeat: int,
    warmup: int,
) -> dict[str, Any]:
    config = DEFAULT_DATASET_CONFIG[profile]
    return run_rt_dbscan_benchmark(
        mode="optix_rt_core_grouped_stream_numba_column_signature_3d",
        dataset=profile,
        point_count=point_count,
        radius=float(config["radius"]),
        min_neighbors=int(config["min_neighbors"]),
        seed=seed,
        partner="numba",
        include_rows=False,
        validate=False,
        repeat=repeat,
        warmup=warmup,
    )


def _run_direct_status(
    *,
    profile: str,
    point_count: int,
    seed: int,
    repeat: int,
    warmup: int,
    partition_cell_factor: float,
) -> dict[str, Any]:
    config = DEFAULT_DATASET_CONFIG[profile]
    return run_rt_dbscan_benchmark(
        mode="partner_cupy_prepared_direct_status_union_component_signature_3d",
        dataset=profile,
        point_count=point_count,
        radius=float(config["radius"]),
        min_neighbors=int(config["min_neighbors"]),
        seed=seed,
        partner="cupy",
        include_rows=False,
        validate=False,
        repeat=repeat,
        warmup=warmup,
        partition_cell_factor=partition_cell_factor,
    )


def _summarize_direct(
    *,
    factor: float,
    payload: dict[str, Any],
    current_signature: tuple[int, ...],
    current_replay_sec: float,
    current_amortized_sec: float,
) -> dict[str, Any]:
    metadata = dict(payload["metadata"])
    protocol = dict(metadata["prepared_direct_status_repeat_protocol"])
    replay_sec = float(payload["elapsed_sec"])
    prepare_sec = float(protocol["prepare_sec"])
    elapsed_total = float(protocol["elapsed_sec_total"])
    measured = int(protocol["measured_run_count"])
    amortized_sec = (prepare_sec + elapsed_total) / measured
    signature = _component_size_signature(payload["signature"])
    handle = dict(metadata["prepared_direct_status_union_handle_metadata"])
    return {
        "partition_cell_factor": float(factor),
        "same_signature": signature == current_signature,
        "replay_sec": replay_sec,
        "prepare_sec": prepare_sec,
        "amortized_sec": amortized_sec,
        "replay_over_current_speedup": current_replay_sec / replay_sec if replay_sec > 0 else None,
        "amortized_over_current_speedup": current_amortized_sec / amortized_sec if amortized_sec > 0 else None,
        "partition_count": int(metadata["partition_count"]),
        "max_neighbor_offset": int(metadata["max_neighbor_offset"]),
        "pair_count": int(metadata["pair_count"]),
        "safe_skip_partition_pairs": int(metadata["safe_skip_partition_pairs"]),
        "safe_full_partition_pairs": int(metadata["safe_full_partition_pairs"]),
        "ambiguous_partition_pairs": int(metadata["ambiguous_partition_pairs"]),
        "ambiguous_point_comparisons": int(metadata["ambiguous_point_comparisons"]),
        "ambiguous_positive_edges": int(metadata["ambiguous_positive_edges"]),
        "union_iterations": int(metadata["union_iterations"]),
        "metadata_cell_factor": float(metadata["cell_factor"]),
        "handle_cell_factor": float(handle["cell_factor"]),
        "claim_boundary": (
            "Internal explicit partition-cell-factor timing evidence only; no route promotion, "
            "release, public speedup, broad RT-core, hidden-dispatch, automatic partner selection, "
            "native ABI, app-specific engine logic, or true-zero-copy claim is authorized."
        ),
        "partition_convergence_hybrid_promoted": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "native_abi_added": False,
        "app_specific_engine_logic_allowed": False,
        "true_zero_copy_claim_authorized": False,
    }


def run(
    *,
    output: pathlib.Path,
    profiles: tuple[str, ...],
    point_count: int,
    seed: int,
    repeat: int,
    warmup: int,
    factors: tuple[float, ...],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    print(
        f"GOAL4117_SWEEP_START point_count={point_count} repeat={repeat} warmup={warmup} factors={factors}",
        flush=True,
    )
    for profile in profiles:
        print(f"PROFILE_START {profile}", flush=True)
        current = _run_current_route(
            profile=profile,
            point_count=point_count,
            seed=seed,
            repeat=repeat,
            warmup=warmup,
        )
        current_metadata = dict(current["metadata"])
        current_protocol = dict(current_metadata["prepared_query_repeat_protocol"])
        current_signature = _component_size_signature(current["signature"])
        current_replay_sec = float(current["elapsed_sec"])
        current_prepare_sec = _current_prepare_sec(current_metadata)
        current_amortized_sec = (
            current_prepare_sec + float(current_protocol["elapsed_sec_total"])
        ) / int(current_protocol["measured_run_count"])
        factor_rows = []
        for factor in factors:
            print(f"FACTOR_START {profile} factor={factor}", flush=True)
            direct = _run_direct_status(
                profile=profile,
                point_count=point_count,
                seed=seed,
                repeat=repeat,
                warmup=warmup,
                partition_cell_factor=float(factor),
            )
            row = _summarize_direct(
                factor=float(factor),
                payload=direct,
                current_signature=current_signature,
                current_replay_sec=current_replay_sec,
                current_amortized_sec=current_amortized_sec,
            )
            factor_rows.append(row)
            print(
                "FACTOR_DONE "
                f"{profile} factor={factor} replay={row['replay_sec']:.6f} "
                f"current={current_replay_sec:.6f} speedup={row['replay_over_current_speedup']:.3f} "
                f"match={row['same_signature']}",
                flush=True,
            )
        best_replay = max(factor_rows, key=lambda row: float(row["replay_over_current_speedup"]))
        best_amortized = max(factor_rows, key=lambda row: float(row["amortized_over_current_speedup"]))
        rows.append(
            {
                "profile": profile,
                "point_count": point_count,
                "radius": float(DEFAULT_DATASET_CONFIG[profile]["radius"]),
                "min_neighbors": int(DEFAULT_DATASET_CONFIG[profile]["min_neighbors"]),
                "current_route_replay_sec": current_replay_sec,
                "current_route_prepare_sec": current_prepare_sec,
                "current_route_amortized_sec": current_amortized_sec,
                "factor_rows": factor_rows,
                "best_replay_partition_cell_factor": best_replay["partition_cell_factor"],
                "best_replay_over_current_speedup": best_replay["replay_over_current_speedup"],
                "best_amortized_partition_cell_factor": best_amortized["partition_cell_factor"],
                "best_amortized_over_current_speedup": best_amortized["amortized_over_current_speedup"],
                "all_factors_match_current_signature": all(bool(row["same_signature"]) for row in factor_rows),
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
            }
        )
        print(
            f"PROFILE_DONE {profile} best_replay_factor={best_replay['partition_cell_factor']} "
            f"best_replay_speedup={best_replay['replay_over_current_speedup']:.3f}",
            flush=True,
        )
    payload = {
        "schema": "rtdl.goal4117.partition_cell_factor_route_sweep.v1",
        "goal": "Goal4117",
        "source_commit": _source_commit(),
        "source_tracked_worktree_dirty": _source_tracked_worktree_dirty(),
        "platform": platform.platform(),
        "gpu": _nvidia_smi(),
        "point_count": point_count,
        "repeat": repeat,
        "warmup": warmup,
        "profiles": list(profiles),
        "partition_cell_factors": list(factors),
        "rows": rows,
        "claim_boundary": (
            "Internal RT-DBSCAN explicit partition-cell-factor route-sweep evidence only. "
            "It does not promote partition_convergence_hybrid or authorize release, public speedup, "
            "broad RT-core, whole-app, paper-reproduction, hidden-dispatch, automatic partner "
            "selection, app-specific engine logic, native ABI addition, AMD performance, or "
            "true-zero-copy claims."
        ),
        "partition_convergence_hybrid_promoted": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "native_abi_added": False,
        "app_specific_engine_logic_allowed": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GOAL4117_SWEEP_DONE wrote={output}", flush=True)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--profiles", nargs="+", default=["clustered3d", "road3d", "ngsim_dense"])
    parser.add_argument("--point-count", type=int, default=65536)
    parser.add_argument("--seed", type=int, default=20260519)
    parser.add_argument("--repeat", type=int, default=4)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--factors", nargs="+", type=float, default=[0.0625, 0.125, 0.25, 0.5, 1.0])
    args = parser.parse_args()
    run(
        output=args.output,
        profiles=tuple(str(profile) for profile in args.profiles),
        point_count=int(args.point_count),
        seed=int(args.seed),
        repeat=int(args.repeat),
        warmup=int(args.warmup),
        factors=tuple(float(factor) for factor in args.factors),
    )


if __name__ == "__main__":
    main()
