from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import subprocess
from typing import Any

from examples.current.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    run_rt_dbscan_benchmark,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4070_rt_dbscan_partition_pair_enumeration_app_timing_pod.json"
APP_MODES = (
    "partner_cupy_partition_convergence_component_signature_3d",
    "partner_cupy_prepared_partition_convergence_component_signature_3d",
)
PROFILES = (
    ("clustered3d_1024", "clustered3d", 1024),
    ("road3d_1024", "road3d", 1024),
    ("clustered3d_4096", "clustered3d", 4096),
    ("road3d_4096", "road3d", 4096),
    ("clustered3d_8192", "clustered3d", 8192),
    ("road3d_8192", "road3d", 8192),
)


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


def _digest(payload: dict[str, Any]) -> dict[str, Any]:
    metadata = payload["metadata"]
    prepared_digest = metadata.get("prepared_partition_summary_digest")
    if not isinstance(prepared_digest, dict):
        prepared_digest = {}
    validation_digest = metadata.get("partition_summary_validation")
    if not isinstance(validation_digest, dict):
        validation_digest = {}
    return {
        "signature": payload["signature"],
        "effective_pair_enumeration": metadata.get("partition_pair_enumeration_effective"),
        "pair_capacity_source": metadata.get("partition_summary_pair_capacity_source"),
        "pair_capacity": prepared_digest.get("pair_capacity", validation_digest.get("pair_capacity")),
        "pair_count": prepared_digest.get("pair_count", validation_digest.get("pair_count")),
        "release_authorized": metadata.get("release_authorized"),
        "public_speedup_claim_authorized": metadata.get("public_speedup_claim_authorized"),
        "partition_convergence_hybrid_promoted": metadata.get("partition_convergence_hybrid_promoted"),
        "full_dbscan_semantics": metadata.get("full_dbscan_semantics"),
        "graph_component_contract_only": metadata.get("graph_component_contract_only"),
    }


def _run_once(app_mode: str, dataset: str, point_count: int, pair_enumeration: str) -> dict[str, Any]:
    return run_rt_dbscan_benchmark(
        mode=app_mode,
        dataset=dataset,
        point_count=point_count,
        radius=None,
        min_neighbors=None,
        seed=20260519,
        partner="cupy",
        include_rows=False,
        validate=False,
        partition_pair_enumeration=pair_enumeration,
    )


def _bench_row(
    app_mode: str,
    profile: str,
    dataset: str,
    point_count: int,
    reps: int,
) -> dict[str, Any]:
    print("PROFILE_START", app_mode, profile, point_count, flush=True)
    warm_default = _run_once(app_mode, dataset, point_count, "mode_default")
    warm_counted = _run_once(app_mode, dataset, point_count, "device_count_then_emit")
    if warm_default["signature"] != warm_counted["signature"]:
        raise RuntimeError(f"signature mismatch for {app_mode} {profile}")

    default_times: list[float] = []
    counted_times: list[float] = []
    for rep in range(int(reps)):
        payload = _run_once(app_mode, dataset, point_count, "mode_default")
        if payload["signature"] != warm_default["signature"]:
            raise RuntimeError(f"default signature drift for {app_mode} {profile}")
        default_times.append(float(payload["elapsed_sec"]))
        print("RUN_DEFAULT", app_mode, profile, rep, f"{float(payload['elapsed_sec']):.6f}", flush=True)
    for rep in range(int(reps)):
        payload = _run_once(app_mode, dataset, point_count, "device_count_then_emit")
        if payload["signature"] != warm_default["signature"]:
            raise RuntimeError(f"count-then-emit signature drift for {app_mode} {profile}")
        counted_times.append(float(payload["elapsed_sec"]))
        print("RUN_COUNT_THEN_EMIT", app_mode, profile, rep, f"{float(payload['elapsed_sec']):.6f}", flush=True)

    default_digest = _digest(warm_default)
    counted_digest = _digest(warm_counted)
    default_capacity = default_digest["pair_capacity"]
    counted_capacity = counted_digest["pair_capacity"]
    capacity_reduction = None
    if default_capacity is not None and counted_capacity is not None:
        capacity_reduction = float(default_capacity) / max(1.0, float(counted_capacity))
    default_summary = _summary(default_times)
    counted_summary = _summary(counted_times)
    row = {
        "app_mode": app_mode,
        "profile": profile,
        "dataset": dataset,
        "point_count": point_count,
        "same_signature": True,
        "default_summary": default_summary,
        "count_then_emit_summary": counted_summary,
        "time_ratio_count_then_emit_over_default_median": (
            counted_summary["median_sec"] / default_summary["median_sec"]
        ),
        "default_digest": default_digest,
        "count_then_emit_digest": counted_digest,
        "pair_capacity_reduction": capacity_reduction,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "partition_convergence_hybrid_promoted": False,
    }
    print("PROFILE_DONE", json.dumps(row, sort_keys=True), flush=True)
    return row


def run(output: pathlib.Path, reps: int) -> dict[str, Any]:
    rows = [
        _bench_row(app_mode, profile, dataset, point_count, reps)
        for app_mode in APP_MODES
        for profile, dataset, point_count in PROFILES
    ]
    payload = {
        "goal": "Goal4070",
        "schema": "rtdl.goal4070.rt_dbscan_partition_pair_enumeration_app_timing.v1",
        "source_commit": _source_commit(),
        "reps": int(reps),
        "claim_boundary": (
            "Internal app-level timing for explicit RT-DBSCAN partition pair-enumeration selection. "
            "It does not promote partition_convergence_hybrid, authorize release, public speedup, "
            "broad RT-core, whole-app, hidden-dispatch, automatic partner selection, app-specific "
            "engine logic, native ABI addition, or true-zero-copy claims."
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
    parser.add_argument("--reps", type=int, default=3)
    args = parser.parse_args()
    payload = run(args.output, args.reps)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
