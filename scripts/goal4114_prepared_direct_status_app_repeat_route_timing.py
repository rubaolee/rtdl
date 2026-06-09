from __future__ import annotations

import argparse
import json
import pathlib
import platform
import subprocess
from typing import Any

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    run_rt_dbscan_benchmark,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4114_prepared_direct_status_app_repeat_route_timing_pod.json"


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


def _run_profile(
    *,
    profile: str,
    point_count: int,
    seed: int,
    repeat: int,
    warmup: int,
) -> dict[str, Any]:
    print(f"APP_REPEAT_PROFILE_START {profile} point_count={point_count}", flush=True)
    prepared = run_rt_dbscan_benchmark(
        mode="partner_cupy_prepared_direct_status_union_component_signature_3d",
        dataset=profile,
        point_count=point_count,
        radius=None,
        min_neighbors=None,
        seed=seed,
        partner="cupy",
        include_rows=False,
        validate=False,
        repeat=repeat,
        warmup=warmup,
    )
    print(f"APP_REPEAT_PREPARED_DONE {profile} elapsed={prepared['elapsed_sec']}", flush=True)
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
        repeat=repeat,
        warmup=warmup,
    )
    print(f"APP_REPEAT_CURRENT_DONE {profile} elapsed={current['elapsed_sec']}", flush=True)
    prepared_signature = _component_size_signature(prepared["signature"])
    current_signature = _component_size_signature(current["signature"])
    if prepared_signature != current_signature:
        raise AssertionError(f"{profile} signature mismatch: {prepared_signature} != {current_signature}")

    prepared_metadata = dict(prepared["metadata"])
    current_metadata = dict(current["metadata"])
    prepared_protocol = dict(prepared_metadata["prepared_direct_status_repeat_protocol"])
    current_protocol = dict(current_metadata["prepared_query_repeat_protocol"])
    measured = int(prepared_protocol["measured_run_count"])
    prepared_prepare_sec = float(prepared_protocol["prepare_sec"])
    current_prepare_sec = _current_prepare_sec(current_metadata)
    prepared_elapsed_total = float(prepared_protocol["elapsed_sec_total"])
    current_elapsed_total = float(current_protocol["elapsed_sec_total"])
    prepared_amortized_sec = (prepared_prepare_sec + prepared_elapsed_total) / measured
    current_amortized_sec = (current_prepare_sec + current_elapsed_total) / measured
    prepared_replay_sec = float(prepared["elapsed_sec"])
    current_replay_sec = float(current["elapsed_sec"])
    return {
        "profile": profile,
        "point_count": point_count,
        "repeat": repeat,
        "warmup": warmup,
        "same_signature": True,
        "prepared_direct_status_replay_sec": prepared_replay_sec,
        "current_route_replay_sec": current_replay_sec,
        "prepared_direct_status_prepare_sec": prepared_prepare_sec,
        "current_route_prepare_sec": current_prepare_sec,
        "prepared_direct_status_amortized_sec": prepared_amortized_sec,
        "current_route_amortized_sec": current_amortized_sec,
        "prepared_replay_over_current_replay_speedup": current_replay_sec / prepared_replay_sec
        if prepared_replay_sec > 0
        else None,
        "prepared_amortized_over_current_amortized_speedup": current_amortized_sec / prepared_amortized_sec
        if prepared_amortized_sec > 0
        else None,
        "prepared_payload": prepared,
        "current_payload": current,
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
    repeat: int,
    warmup: int,
) -> dict[str, Any]:
    rows = [
        _run_profile(
            profile=profile,
            point_count=point_count,
            seed=seed,
            repeat=repeat,
            warmup=warmup,
        )
        for profile in profiles
    ]
    payload = {
        "schema": "rtdl.goal4114.prepared_direct_status_app_repeat_route_timing.v1",
        "goal": "Goal4114",
        "source_commit": _source_commit(),
        "source_tracked_worktree_dirty": _source_tracked_worktree_dirty(),
        "platform": platform.platform(),
        "gpu": _nvidia_smi(),
        "point_count": point_count,
        "profiles": list(profiles),
        "repeat": repeat,
        "warmup": warmup,
        "rows": rows,
        "claim_boundary": (
            "Internal repeated app-route comparison evidence only. It does not promote "
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
    parser.add_argument("--repeat", type=int, default=4)
    parser.add_argument("--warmup", type=int, default=1)
    args = parser.parse_args()
    run(
        output=args.output,
        profiles=tuple(str(profile) for profile in args.profiles),
        point_count=int(args.point_count),
        seed=int(args.seed),
        repeat=int(args.repeat),
        warmup=int(args.warmup),
    )


if __name__ == "__main__":
    main()
