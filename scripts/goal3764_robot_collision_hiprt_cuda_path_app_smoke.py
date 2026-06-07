#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from examples.v2_0.apps.robotics import rtdl_robot_collision_screening_app as app  # noqa: E402


SCHEMA = "rtdl.goal3764.robot_collision_hiprt_cuda_path_app_smoke.v1"
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal3764_robot_collision_hiprt_cuda_path_app_smoke_a5000.json"
SCOPED_SOURCE_PATHS = (
    "examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py",
    "scripts/goal3764_robot_collision_hiprt_cuda_path_app_smoke.py",
    "tests/goal3764_robot_collision_hiprt_cuda_path_app_smoke_test.py",
)


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "amd_hardware_perf_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "app_specific_native_engine_logic_allowed": False,
    }


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot summarize empty timing list")
    return float(statistics.median(values))


def _run_correctness_case(*, pose_count: int | None, obstacle_count: int | None) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"output_mode": "pose_flags", "skip_validation": False}
    if pose_count is not None:
        kwargs.update({"pose_count": pose_count, "obstacle_count": obstacle_count})
    payload = app.run_app("hiprt", **kwargs)
    return {
        "pose_count": int(payload["pose_count"]),
        "edge_ray_count": int(payload["edge_ray_count"]),
        "obstacle_triangle_count": int(payload["obstacle_triangle_count"]),
        "colliding_pose_count": int(payload["colliding_pose_count"]),
        "matches_oracle": bool(payload["matches_oracle"]),
        "validation_mode": payload["validation_mode"],
        "backend": payload["backend"],
        "claim_boundary": _claim_boundary(),
    }


def _time_hiprt_case(*, pose_count: int, obstacle_count: int, warmup: int, repeat: int) -> dict[str, Any]:
    measured: list[float] = []
    runs: list[dict[str, Any]] = []
    last_payload: dict[str, Any] | None = None
    for iteration in range(warmup + repeat):
        start = time.perf_counter()
        payload = app.run_app(
            "hiprt",
            output_mode="hit_count",
            pose_count=pose_count,
            obstacle_count=obstacle_count,
            skip_validation=True,
        )
        elapsed = time.perf_counter() - start
        is_warmup = iteration < warmup
        last_payload = payload
        print(
            f"[goal3764] hiprt pose_count={pose_count} obstacle_count={obstacle_count} "
            f"{'warmup' if is_warmup else 'repeat'} {iteration + 1}/{warmup + repeat} "
            f"elapsed={elapsed:.6f}s hit_edges={payload['hit_edge_count']}",
            flush=True,
        )
        runs.append(
            {
                "iteration": iteration,
                "is_warmup": is_warmup,
                "elapsed_sec": elapsed,
                "hit_edge_count": int(payload["hit_edge_count"]),
            }
        )
        if not is_warmup:
            measured.append(elapsed)
    assert last_payload is not None
    return {
        "pose_count": pose_count,
        "obstacle_count": obstacle_count,
        "edge_ray_count": int(last_payload["edge_ray_count"]),
        "obstacle_triangle_count": int(last_payload["obstacle_triangle_count"]),
        "hit_edge_count": int(last_payload["hit_edge_count"]),
        "hot_median_sec": _median(measured),
        "hot_min_sec": min(measured),
        "hot_total_sec": float(sum(measured)),
        "repeat": repeat,
        "warmup": warmup,
        "validation_mode": last_payload["validation_mode"],
        "native_continuation_backend": last_payload["native_continuation_backend"],
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    correctness = [
        _run_correctness_case(pose_count=None, obstacle_count=None),
        _run_correctness_case(pose_count=args.correctness_pose_count, obstacle_count=args.correctness_obstacle_count),
    ]
    timings = [
        _time_hiprt_case(
            pose_count=count,
            obstacle_count=count,
            warmup=args.warmup,
            repeat=args.repeat,
        )
        for count in args.timing_pose_counts
    ]
    return {
        "schema": SCHEMA,
        "generated_at_unix": time.time(),
        "source_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "source_commit_short": _command_output(["git", "rev-parse", "--short", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "goal3764_scoped_source_status_short": _command_output(
            ["git", "status", "--short", "--", *SCOPED_SOURCE_PATHS]
        ),
        "goal3764_scoped_source_dirty": bool(
            _command_output(["git", "status", "--short", "--", *SCOPED_SOURCE_PATHS])
        ),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "correctness": correctness,
        "timings": timings,
        "summary": {
            "correctness_case_count": len(correctness),
            "all_correctness_cases_match_oracle": all(bool(row["matches_oracle"]) for row in correctness),
            "timing_case_count": len(timings),
            "max_timing_pose_count": max(row["pose_count"] for row in timings),
        },
        "interpretation": (
            "Robot-collision HIPRT app-route smoke over the CUDA/Orochi path on NVIDIA. "
            "This validates route functionality and bounded timing behavior, not AMD hardware performance."
        ),
        "claim_boundary": _claim_boundary(),
    }


def _parse_counts(value: str) -> tuple[int, ...]:
    counts = tuple(int(part.strip()) for part in value.split(",") if part.strip())
    if not counts:
        raise ValueError("--timing-pose-counts must not be empty")
    if any(count <= 0 for count in counts):
        raise ValueError("--timing-pose-counts values must be positive")
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Goal3764 robot-collision HIPRT CUDA-path app smoke.")
    parser.add_argument("--timing-pose-counts", default="64,128,256,512")
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--correctness-pose-count", type=int, default=128)
    parser.add_argument("--correctness-obstacle-count", type=int, default=128)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.timing_pose_counts = _parse_counts(args.timing_pose_counts)
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3764] wrote {args.output}", flush=True)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
