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
from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
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


def _run_smoke(*, point_count: int, radius: float, seed: int) -> dict[str, Any]:
    points = make_rt_dbscan_points("clustered3d", point_count=point_count, seed=seed)
    with rt.prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d(
        points,
        radius=radius,
        partner="cupy",
    ) as prepared:
        cp = prepared.cupy
        parent_default = cp.arange(prepared.point_count, dtype=cp.int32)
        default_sec, default_result = _timed(
            cp,
            lambda: prepared.prepared_native.apply_device_grouped_union_all_self(
                radius=prepared.radius,
                parent_out=parent_default,
            ),
        )

        parent_all = cp.arange(prepared.point_count, dtype=cp.int32)
        telemetry_all = cp.zeros((4,), dtype=cp.uint64)
        telemetry_all_sec, telemetry_all_result = _timed(
            cp,
            lambda: prepared.prepared_native.apply_device_grouped_union_all_self(
                radius=prepared.radius,
                parent_out=parent_all,
                telemetry_out=telemetry_all,
            ),
        )

        predicate_flags = cp.zeros((prepared.point_count,), dtype=cp.uint32)
        predicate_flags[::2] = 1
        parent_predicate = cp.arange(prepared.point_count, dtype=cp.int32)
        fallback = cp.full((prepared.point_count,), prepared.point_count, dtype=cp.int32)
        telemetry_predicate = cp.zeros((4,), dtype=cp.uint64)
        predicate_sec, predicate_result = _timed(
            cp,
            lambda: prepared.prepared_native.apply_device_grouped_union_self(
                radius=prepared.radius,
                predicate_flags=predicate_flags,
                parent_out=parent_predicate,
                fallback_candidate_out=fallback,
                telemetry_out=telemetry_predicate,
            ),
        )

        telemetry_all_host = [int(value) for value in telemetry_all.get().tolist()]
        telemetry_predicate_host = [int(value) for value in telemetry_predicate.get().tolist()]

    return {
        "point_count": point_count,
        "radius": radius,
        "seed": seed,
        "default": {
            "elapsed_sec": default_sec,
            "metadata": default_result["metadata"],
        },
        "all_items_telemetry": {
            "elapsed_sec": telemetry_all_sec,
            "telemetry": telemetry_all_host,
            "metadata": telemetry_all_result["metadata"],
            "parent_attempts_positive": telemetry_all_host[0] > 0,
            "parent_successes_positive": telemetry_all_host[1] > 0,
            "fallback_counters_zero": telemetry_all_host[2] == 0 and telemetry_all_host[3] == 0,
        },
        "predicate_telemetry": {
            "elapsed_sec": predicate_sec,
            "telemetry": telemetry_predicate_host,
            "metadata": predicate_result["metadata"],
            "fallback_attempts_positive": telemetry_predicate_host[2] > 0,
        },
        "telemetry_overhead_ratio": telemetry_all_sec / default_sec if default_sec > 0.0 else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Goal2471 OptiX grouped-union telemetry pod smoke."
    )
    parser.add_argument("--point-count", type=int, default=512)
    parser.add_argument(
        "--radius",
        type=float,
        default=0.5,
        help="Smoke radius chosen to exercise both parent-union and fallback-candidate atomics.",
    )
    parser.add_argument("--seed", type=int, default=20260520)
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("docs/reports/goal2471_grouped_union_telemetry_pod_smoke.json"),
    )
    args = parser.parse_args()

    smoke = _run_smoke(point_count=args.point_count, radius=args.radius, seed=args.seed)
    payload = {
        "goal": "Goal2471",
        "status": "pass"
        if (
            smoke["all_items_telemetry"]["parent_attempts_positive"]
            and smoke["all_items_telemetry"]["parent_successes_positive"]
            and smoke["all_items_telemetry"]["fallback_counters_zero"]
            and smoke["predicate_telemetry"]["fallback_attempts_positive"]
        )
        else "fail",
        "source_commit": _git_head(),
        "host": platform.node(),
        "platform": platform.platform(),
        "gpu": _nvidia_smi(),
        "smoke": smoke,
        "claim_boundary": {
            "performance_claim_authorized": False,
            "telemetry_is_instrumentation": True,
            "dbscan_native_abi_added": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
