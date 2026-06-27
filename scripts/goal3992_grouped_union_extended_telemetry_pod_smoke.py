#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import platform
import subprocess
import time
from typing import Any

import rtdsl as rt
from examples.benchmark_apps.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    make_rt_dbscan_points,
)


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=_repo_root(),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ""


def _nvidia_smi() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ""


def _sync(cp: Any) -> None:
    cp.cuda.Stream.null.synchronize()


def _timed(cp: Any, fn) -> tuple[float, Any]:
    _sync(cp)
    start = time.perf_counter()
    result = fn()
    _sync(cp)
    return time.perf_counter() - start, result


def _run_once(*, point_count: int, radius: float, seed: int) -> dict[str, Any]:
    points = make_rt_dbscan_points("clustered3d", point_count=point_count, seed=seed)
    with rt.prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d(
        points,
        radius=radius,
        partner="cupy",
    ) as prepared:
        cp = prepared.cupy

        parent_old = cp.arange(prepared.point_count, dtype=cp.int32)
        telemetry_old = cp.zeros((4,), dtype=cp.uint64)
        old_sec, old_result = _timed(
            cp,
            lambda: prepared.prepared_native.apply_device_grouped_union_all_self(
                radius=prepared.radius,
                parent_out=parent_old,
                telemetry_out=telemetry_old,
            ),
        )

        parent_extended = cp.arange(prepared.point_count, dtype=cp.int32)
        telemetry_extended = cp.zeros((8,), dtype=cp.uint64)
        extended_sec, extended_result = _timed(
            cp,
            lambda: prepared.prepared_native.apply_device_grouped_union_all_self(
                radius=prepared.radius,
                parent_out=parent_extended,
                telemetry_out=telemetry_extended,
            ),
        )

        old_host = [int(value) for value in telemetry_old.get().tolist()]
        extended_host = [int(value) for value in telemetry_extended.get().tolist()]

    return {
        "point_count": point_count,
        "radius": radius,
        "seed": seed,
        "old_four_counter": {
            "elapsed_sec": old_sec,
            "telemetry": old_host,
            "metadata": old_result["metadata"],
        },
        "extended_eight_counter": {
            "elapsed_sec": extended_sec,
            "telemetry": extended_host,
            "metadata": extended_result["metadata"],
        },
        "old_parent_atomic_attempts_positive": old_host[0] > 0,
        "extended_parent_atomic_attempts_positive": extended_host[0] > 0,
        "same_parent_atomic_successes": old_host[1] == extended_host[1],
        "extended_radius_candidate_hits_positive": extended_host[4] > 0,
        "extended_reported_intersection_candidates_positive": extended_host[7] > 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Goal3992 grouped-union extended telemetry pod smoke."
    )
    parser.add_argument("--point-count", type=int, default=4096)
    parser.add_argument("--radius", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=20260608)
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("docs/reports/goal3992_grouped_union_extended_telemetry_pod_smoke.json"),
    )
    args = parser.parse_args()

    smoke = _run_once(point_count=args.point_count, radius=args.radius, seed=args.seed)
    old_meta = smoke["old_four_counter"]["metadata"]
    ext_meta = smoke["extended_eight_counter"]["metadata"]
    status = (
        old_meta.get("grouped_union_extended_telemetry_enabled") is False
        and old_meta.get("grouped_union_telemetry_counter_count") == 4
        and ext_meta.get("grouped_union_extended_telemetry_enabled") is True
        and ext_meta.get("grouped_union_telemetry_counter_count") == 8
        and smoke["old_parent_atomic_attempts_positive"]
        and smoke["extended_parent_atomic_attempts_positive"]
        and smoke["same_parent_atomic_successes"]
        and smoke["extended_radius_candidate_hits_positive"]
        and smoke["extended_reported_intersection_candidates_positive"]
    )
    payload = {
        "goal": "Goal3992",
        "status": "pass" if status else "fail",
        "source_commit": _git_head(),
        "host": platform.node(),
        "platform": platform.platform(),
        "gpu": _nvidia_smi(),
        "smoke": smoke,
        "claim_boundary": {
            "performance_claim_authorized": False,
            "telemetry_is_instrumentation": True,
            "dbscan_native_abi_added": False,
            "release_authorized": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if status else 1


if __name__ == "__main__":
    raise SystemExit(main())
